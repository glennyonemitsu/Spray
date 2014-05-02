Spray
=====

Simple static site framework


Specify flask routes and template files in `spray.yaml`

    /:
        name:       home
        template:   home.jade
    /contact:
        name:       contact
        template:   contact.jade
    /bio:
        name:       bio
        template:   biography.jade

Since names are provided you can use them with Flask's url_for function.

You can also use shorthand:

    /:          home.jade
    /contact:   contact.jade
    /bio:       biography.jade

The url_for parameter will then become the full route string.

For jinja2 support, just use the `.html` extension.

All templates should be in the templates/ directory relative to the spray.yaml 
file.
