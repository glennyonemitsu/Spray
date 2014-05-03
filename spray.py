#! /usr/bin/env python

from __future__ import print_function
import argparse
import hashlib
import logging
import mimetypes
import os.path
import sys

from flask import abort, Flask, make_response, render_template, request
import yaml


log_format = '%(levelname)s: %(message)s'
logging.basicConfig(format=log_format, level=logging.DEBUG)

try:
    yaml_file = os.path.abspath('spray.yaml')
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

app.run(debug=True, host='0.0.0.0')
