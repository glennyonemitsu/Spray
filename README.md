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

Flask powered. Gevent powered for production mode.

Templating via jade and jinja2 support

Static files

Caching and (soon) E-tag


## Quick Start

To install

    $ pip install spray 

Start a project
    
    $ spray create_project mysite
    $ ls mysite/

        mysite/spray.yaml
        mysite/templates/
        mysite/static/
        mysite/cache/

Work in development or production mode

    $ spray run \
            --mode={development,production} \
            --bind=0.0.0.0:8080

More info available with the `--help` flag

    $ spray --help


## Serving And Caching Under The Hood

Requests are served by looking for the matching flask route, then as a file in
`static/` if the route does not exist. Content-Type headers are determined by 
an extension: mime type dictionary. Though by default all route based requests
will be served the `text/html` Content-Type header.

In development mode the server will never use caching. Perhaps in the future it
will constantly watch the `templates/` and `static/` directories.

In production, each request will be cached in `cache/`. The cache key will 
simply be the request path. Even if the template or static file is updated in
the file system, the cache will not be invalidated and updated. In this case the
server must be restart.

