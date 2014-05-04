#! /usr/bin/env python

from __future__ import print_function
import argparse
import hashlib
import logging
import mimetypes
import os
import os.path
import shutil
import sys

from flask import abort, Flask, make_response, render_template, request, send_file
import yaml


__version__ = '0.1'


parser = argparse.ArgumentParser()
parser.add_argument('-d', '--debug', help='debugging output', action='store_true')
subparsers = parser.add_subparsers(help='Spray command actions')

args_server = subparsers.add_parser('run', help='Run the web server')
args_server.add_argument('-b', '--bind', default='localhost:8080', help='Bind server to ip:port')
args_server.add_argument('-m', '--mode', default='development', choices=['development', 'production'], help='Deployment mode development or production mode')
args_server.add_argument('-p', '--path', help='Spray path', default=os.getcwd())
args_server.add_argument('-c', '--cache', help='Use cache for development mode. This is always on for production mode', default=False, action='store_true')
args_server.set_defaults(action='run')

args_create = subparsers.add_parser('create', help='Create a new Spray project')
args_create.add_argument('-n', '--name', required=True, help='Project name')
args_create.set_defaults(action='create')

args = parser.parse_args()

log_format = '%(levelname)s: %(message)s'
logging.basicConfig(format=log_format, level=logging.DEBUG if args.debug else logging.ERROR)

# set of routes that returned a 404, so a cache file does not get created and muck up the file system
missing = set()
missing_output = None

def create_app(args):
    try:
        serve_path = os.path.abspath(args.path)
        yaml_file = os.path.join(serve_path, 'spray.yaml')
        logging.debug('Loading yaml file {filename}'.format(filename=yaml_file))
        with open(yaml_file) as fh:
            conf = yaml.load(fh)
    except IOError:
        logging.error('spray.yaml not found')
        sys.exit(1)
    except yaml.scanner.ScannerError as e:
        logging.error('spray.yaml not proper YAML syntax')
        sys.exit(1)

    mimetypes.init()
    app = Flask(__name__, instance_path=serve_path, template_folder=os.path.join(serve_path, 'templates'))
    app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')

    @app.errorhandler(404)
    def not_found(error):
        global missing
        global missing_output
        logging.debug('Handling 404 error')
        missing.add(request.path)
        if missing_output is None:
            logging.debug('Rendering the 404 error page for the first time')
            for tmpl in ('404.jade', '404.html'):
                not_found_template = os.path.abspath(os.path.join(serve_path, 'templates', tmpl))
                if os.path.exists(not_found_template):
                    logging.debug('Using "{tmpl}" to serve 404 page'.format(tmpl=not_found_template))
                    missing_output = render_template(tmpl)
            if missing_output is None:
                logging.debug('Using default 404 string to serve 404 page')
                missing_output = '404 Not Found'
        else:
            logging.debug('Serving previously rendered 404 page')
        return missing_output, 404
        res = make_response(missing_output, 404)
        res.headers['Content-Type'] = 'text/html'
        logging.debug(res)
        return res

    @app.before_request
    def missing_checker():
        global missing
        logging.debug('Checking if the request path "{path}" was already determined to be a 404'.format(path=request.path))
        if request.path in missing:
            logging.debug('The request path "{path}" was determined to be a 404'.format(path=request.path))
            abort(404)

    @app.before_request
    def cache_checker():
        if args.cache and request.path not in missing:
            hasher = hashlib.new('sha1')
            hasher.update(request.path)
            cache_key = hasher.hexdigest()
            cache_file = os.path.abspath(os.path.join(serve_path, 'cache', cache_key))
            logging.debug('Checking for cache key "{key}" for request path "{path}"'.format(key=cache_key, path=request.path))
            if os.path.exists(cache_file):
                logging.debug('Found cache file "{key}"'.format(key=cache_file))
                return send_file(cache_file, mimetype=mimetypes.guess_type(request.path)[0])
            else:
                logging.debug('Did not find cache key "{key}"'.format(key=cache_key))
        else:
            logging.debug('Not checking for cache')

    @app.after_request
    def cache_recorder(response):
        if response.status_code != 404:
            if args.cache:
                hasher = hashlib.new('sha1')
                hasher.update(request.path)
                cache_key = hasher.hexdigest()
                cache_file = os.path.abspath(os.path.join(serve_path, 'cache', cache_key))
                if not os.path.exists(cache_file):
                    response.direct_passthrough = False
                    with open(cache_file, 'w') as fh:
                        fh.write(response.get_data())
            else:
                logging.debug('Not saving output for cache')
        return response


    for route, meta in conf.iteritems():
        if type(meta) is dict:
            template = meta['template']
            name = meta['name'] if 'name' in meta else route
        else:
            template = meta
            name = route
        def view():
            logging.debug('Serving request "{path}" with template "{template}"'.format(path=request.path, template=template))
            return render_template(template)
        logging.debug('Registering route {route} named {name}'.format(route=route, name=name))
        app.add_url_rule(route, name, view)


    def catchall_view(path):
        logging.debug('Serving request with the catchall_view')
        static_file = os.path.abspath(os.path.join(serve_path, 'static', path))
        if not os.path.exists(static_file):
            logging.debug('Did not find static file {filename}'.format(filename=static_file))
            return abort(404)
        logging.debug('Found static file {filename}'.format(filename=static_file))
        return send_file(static_file, mimetype=mimetypes.guess_type(request.path)[0])

    app.add_url_rule('/<path:path>', 'catchall', catchall_view)
    return app


def create_file(*args):
    path = os.path.join(*args[:-1])
    logging.info('Creating file {filename}'.format(filename=path))
    with open(path, 'w') as fh:
        fh.write(args[-1])


def create_directory(*args):
    directory = os.path.join(*args)
    logging.info('Creating directory {path}'.format(path=directory))
    os.mkdir(directory)
    

def create_project():
    dest = os.path.abspath(args.name)
    if os.path.exists(dest):
        logging.error('Project destination {dest} already exists'.format(dest=dest))
        sys.exit(1)
    create_directory(dest)
    create_file(dest, 'spray.yaml', '/:\n    template: home.jade\n    name: home')
    for path in ('templates', 'static', 'cache'):
        create_directory(dest, path)
    create_file(dest, 'templates', 'home.jade', 'h1 Hello, World!')
    create_file(dest, 'templates', '404.jade', 'h1 404 Not Found')


def main():
    if args.action == 'run':
        host = ''.join(args.bind.split(':')[:-1])
        port = int(args.bind.split(':')[-1])
        if args.mode == 'development':
            app = create_app(args)
            logging.debug('Launching server in development mode')
            app.run(debug=args.debug, host=host, port=port)
        elif args.mode == 'production':
            from gevent.wsgi import WSGIServer

            args.cache = True
            cache_path = os.path.abspath(os.path.join(args.path, 'cache'))
            logging.debug('Clearing cache directory {path}'.format(path=cache_path))
            if os.path.exists(cache_path):
                shutil.rmtree(cache_path)
            create_directory(cache_path)
            app = create_app(args)
            logging.debug('Launching server in production mode')
            server = WSGIServer((host, port), app, log=None)
            server.serve_forever()
    elif args.action == 'create':
        create_project()

if __name__ == '__main__':
    main()

