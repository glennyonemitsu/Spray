#! /usr/bin/env python

from __future__ import print_function
import os.path
import sys

from flask import Flask, render_template
import yaml


yaml_file = os.path.abspath('spray.yaml')
if not os.path.exists(yaml_file):
    print('spray.yaml file not found in current directory')
    sys.exit(1)
    
with open(yaml_file) as fh:
    conf = yaml.load(fh)


def create_view(template):
    def view():
        return render_template(template)
    return view


app = Flask(__name__)
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
for route, meta in conf.iteritems():
    if type(meta) is dict:
        template = meta['template']
        name = meta['name'] if 'name' in meta else route
    else:
        template = meta
        name = route
    view = create_view(template)
    app.add_url_rule(route, name, view)


app.run(debug=True, host='0.0.0.0')
