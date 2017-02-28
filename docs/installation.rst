Installation
============

Last stable version:

::

    pip install django-leaflet


Last development version (master branch):

::

    pip install -e git+https://github.com/makinacorpus/django-leaflet.git#egg=django-leaflet


Configuration
-------------

* Add ``leaflet`` to your ``INSTALLED_APPS``

* Add the HTML header::

    {% load leaflet_tags %}

    <head>
        ...
        {% leaflet_js %}
        {% leaflet_css %}
    </head>

* Add the map in your page, providing a name::

    ...
    <body>
        ...
        {% leaflet_map "yourmap" %}
        ...
    </body>

* Your map shows up!

Example
-------

Check out the `example project <https://github.com/makinacorpus/django-leaflet/tree/master/example>`_
for a complete integration!
