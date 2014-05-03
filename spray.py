#! /usr/bin/env python

from __future__ import print_function
import argparse
import mimetypes
import os.path
import sys

from flask import abort, Flask, render_template, Response, make_response
import yaml


yaml_file = os.path.abspath('spray.yaml')
if not os.path.exists(yaml_file):
    print('spray.yaml file not found in current directory')
    sys.exit(1)
    
with open(yaml_file) as fh:
    conf = yaml.load(fh)


app = Flask(__name__)
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
mimetypes.init()

for route, meta in conf.iteritems():
    if type(meta) is dict:
        template = meta['template']
        name = meta['name'] if 'name' in meta else route
    else:
        template = meta
        name = route
    app.add_url_rule(route, name, lambda: render_template(template))

@app.errorhandler(404)
def not_found(error):
    for tmpl in ('404.jade', '404.html'):
        not_found_template = os.path.abspath(os.path.join('templates', tmpl))
        if os.path.exists(not_found_template):
            return make_response(render_template(not_found_template), 404)
    else:
        return '404 Not Found', 404

def catchall_route(path):
    static_file = os.path.abspath(os.path.join('static', path))
    if not os.path.exists(static_file):
        for tmpl in ('404.jade', '404.html'):
            not_found_template = os.path.abspath(os.path.join('templates', tmpl))
            if os.path.exists(not_found_template):
                return make_response(render_template(not_found_template), 404)
        else:
            return abort(404)
    data = app.send_static_file(path)
    return make_response(data, 200)

app.add_url_rule('/<path:path>', 'catchall', catchall_route)


app.run(debug=True, host='0.0.0.0')
