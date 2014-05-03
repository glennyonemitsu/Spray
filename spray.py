#! /usr/bin/env python

from __future__ import print_function
import argparse
import mimetypes
import os.path
import sys

from flask import Flask, render_template, Response
import yaml


yaml_file = os.path.abspath('spray.yaml')
if not os.path.exists(yaml_file):
    print('spray.yaml file not found in current directory')
    sys.exit(1)
    
with open(yaml_file) as fh:
    conf = yaml.load(fh)


app = Flask(__name__)
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')

for route, meta in conf.iteritems():
    if type(meta) is dict:
        template = meta['template']
        name = meta['name'] if 'name' in meta else route
    else:
        template = meta
        name = route
    app.add_url_rule(route, name, lambda: render_template(template))

def catchall_route(path):
    static_file = os.path.abspath(os.path.join('static', path))
    if not os.path.exists(static_file):
        return '404'
    return app.send_static_file(path)

app.add_url_rule('/<path:path>', 'catchall', catchall_route)


app.run(debug=True, host='0.0.0.0')
