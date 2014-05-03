#! /usr/bin/env python

from __future__ import print_function
import argparse
import hashlib
import logging
import mimetypes
import os
import os.path
import sys

from flask import abort, Flask, make_response, render_template, request
from gunicorn.app.base import Application
from gunicorn.arbiter import Arbiter
from gunicorn.config import Config
import yaml


parser = argparse.ArgumentParser()
parser.add_argument('-d', '--debug', help='debugging output', action='store_true')
subparsers = parser.add_subparsers(help='subcommands')

args_server = subparsers.add_parser('run_server', help='run server')
args_server.add_argument('-b', '--bind', default='localhost:8080', help='bind ip:port')
args_server.add_argument('-m', '--mode', default='developer', choices=['developer', 'production'], help='developer or production mode')
args_server.add_argument('-p', '--path', help='spray path', default=os.getcwd())
args_server.set_defaults(action='run_server')

args_create = subparsers.add_parser('create_project', help='create a project')
args_create.add_argument('-n', '--name', required=True, help='project name')
args_create.set_defaults(action='create_project')

args = parser.parse_args()

log_format = '%(levelname)s: %(message)s'
logging.basicConfig(format=log_format, level=logging.DEBUG if args.debug else logging.ERROR)

def run_server():
    try:
        yaml_file = os.path.abspath('spray.yaml')
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
    app = Flask(__name__)
    app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')

    @app.errorhandler(404)
    def not_found(error):
        logging.debug('Handling 404 error')
        for tmpl in ('404.jade', '404.html'):
            not_found_template = os.path.abspath(os.path.join('templates', tmpl))
            if os.path.exists(not_found_template):
                logging.debug('Using ' + tmpl + ' to serve 404 page')
                return make_response(render_template(tmpl), 404)
        else:
            logging.debug('Using default 404 string to serve 404 page')
            return '404 Not Found', 404

    @app.before_request
    def cache_checker():
        hasher = hashlib.new('sha1')
        hasher.update(request.path)
        cache_key = hasher.hexdigest()
        cache_file = os.path.abspath(os.path.join('cache', cache_key))
        logging.debug('Checking for cache key "{key}" for request path "{path}"'.format(key=cache_key, path=request.path))
        if os.path.exists(cache_file):
            logging.debug('Found cache key "{key}"'.format(key=cache_key))
            data = app.send_static_file(cache_file)
            return make_response(data, 200)
        else:
            logging.debug('Did not find cache key "{key}"'.format(key=cache_key))

    @app.after_request
    def cache_recorder(response):
        return response
        hasher = hashlib.new('sha1')
        hasher.update(request.path)
        cache_key = hasher.hexdigest()
        cache_file = os.path.abspath(os.path.join('cache', cache_key))
        if not os.path.exists(cache_file):
            with open(cache_file, 'w') as fh:
                fh.write(response.get_data())
        return response


    for route, meta in conf.iteritems():
        if type(meta) is dict:
            template = meta['template']
            name = meta['name'] if 'name' in meta else route
        else:
            template = meta
            name = route
        logging.debug('Registering route {route} named {name}'.format(route=route, name=name))
        app.add_url_rule(route, name, lambda: render_template(template))


    def catchall_view(path):
        logging.debug('Serving request with the catchall_view')
        static_file = os.path.abspath(os.path.join('static', path))
        if not os.path.exists(static_file):
            logging.debug('Did not find static file {filename}'.format(filename=static_file))
            return abort(404)
        logging.debug('Found static file {filename}'.format(filename=static_file))
        data = app.send_static_file(path)
        return make_response(data, 200)

    app.add_url_rule('/<path:path>', 'catchall', catchall_view)

    host = ''.join(args.bind.split(':')[:-1])
    port = int(args.bind.split(':')[-1])
    if args.mode == 'developer':
        app.run(debug=args.debug, host=host, port=port)
    elif args.mode == 'production':
        app.run(debug=args.debug, host=host, port=port)


def create_project():
    dest = os.path.abspath(args.name)
    if os.path.exists(dest):
        logging.error('Project destination {dest} already exists'.format(dest=dest))
        sys.exit(1)
    logging.info('Creating new project at {dest}'.format(dest=dest))
    os.mkdir(dest)
    logging.info('Creating spray.yaml file')
    with open(os.path.join(dest, 'spray.yaml'), 'w') as fh:
        fh.write('')
    logging.info('Creating templates directory')
    os.mkdir(os.path.join(dest, 'templates'))
    logging.info('Creating static directory')
    os.mkdir(os.path.join(dest, 'static'))
    logging.info('Creating cache directory')
    os.mkdir(os.path.join(dest, 'cache'))

if args.action == 'run_server':
    run_server()
elif args.action == 'create_project':
    create_project()
