Spray
=====

Simple static site framework


Specify flask style routes and template files in `spray.yaml`

    /:
        name:       home
        template:   home.jade
    /contact:
        name:       contact
        template:   contact.jade
    /bio:
        name:       bio
        template:   biography.jade

Since names are provided you can use them with Flask's `url_for` function.

You can also use shorthand or mix both styles:

    /:              home.jade
    /contact:       contact.jade
    /bio:       
        name:       bio
        template:   biography.jade

The `url_for` parameter will then become the full route string if shorthand is
used.

For jinja2 support, just use the `.html` extension.

All templates should be in the `templates/` directory relative to the 
`spray.yaml` file.

All static files should be in the `static/` directory relative to the 
`spray.yaml` file. This `static/` directory is mapped to the root of your 
website domain. As an example, the file `static/robots.txt` would be accessible
at `http://example.com/robots.txt`.


## Features

Flask powered

Templating via jade and jinja2 support

Static files

Caching and E-tag


## Quick Start

To install (hopefully sometime soon)

    $ pip install spray 

Start a project
    
    $ spray create_project mysite
    $ ls mysite/

        mysite/spray.yaml
        mysite/templates/
        mysite/static/
        mysite/cache/

Work in development or production mode

    $ spray run_server \
            --mode={development,production} \
            --bind=0.0.0.0:8080



