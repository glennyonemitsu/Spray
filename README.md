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
