*django-leaflet* allows you to use `Leaflet <http://leaflet.cloudmade.com>`_
in your `Django <https://www.djangoproject.com>`_ projects.

It embeds Leaflet in version *0.6.4*.

.. image:: https://travis-ci.org/makinacorpus/django-leaflet.png
    :target: https://travis-ci.org/makinacorpus/django-leaflet

.. image:: https://coveralls.io/repos/makinacorpus/django-leaflet/badge.png
    :target: https://coveralls.io/r/makinacorpus/django-leaflet


=======
INSTALL
=======

::

    pip install django-leaflet

=====
USAGE
=====

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

* Your maps shows up!


Use Leaflet API
---------------

You can use the *Leaflet* API as usual. There are two ways to
grab a reference on the just initialized map and options.


**Using Javascript callback function**

Simple brutish way :

    <script type="text/javascript">
        function map_init_basic (map, options) {
            ...
            L.marker([50.5, 30.5]).addTo(e.map);
            ...
        }
    </script>

    {% leaflet_map "yourmap" callback="window.map_init_basic" %}


**Using events**

More refined and flexible :

::

    <script type="text/javascript">
        window.addEventListener("map:init", function (e) {
            ...
            L.marker([50.5, 30.5]).addTo(e.map);
            ...
        }, false);
    </script>

Event object has two properties : ``map`` and ``options`` (initialization).

For Internet Explorer 6,7,8 support, we fallback on jQuery if available ::

    $(window).on('map:init', function (e) { ... });

If you want to support archaic browsers **and** still avoid jQuery,
*django-leaflet* comes with a minimalist polyfill for events.
Add it in ``<head>`` this way ::

    <!--[if IE 8]><script src="{% static "leaflet/eventlister.ie8.js" %}"></script><!--<![endif]-->
    <!--[if lt IE 8]><script src="{% static "leaflet/eventlister.ie6-7.js" %}"></script><!--<![endif]-->


Customize map size
------------------

::

    <style>
    
        .leaflet-container {  /* all maps */
            width:  600px;
            height: 400px;
        }
        
        #specialbigmap {
            height: 800px;
        }
        
    </style>



Configuration
=============

In order to configure *django-leaflet*, just add a new section in your
settings::

    LEAFLET_CONFIG = {
        # conf here
    }


Spatial extent
--------------

You can configure a global spatial extent for your maps, that will
automatically center your maps, restrict panning and add reset view and scale
controls. (*See advanced usage to tweak that.*)::

    'SPATIAL_EXTENT': (5.0, 44.0, 7.5, 46)


Initial map center and zoom level
---------------------------------

In addition to limiting your maps with ``SPATIAL_EXTENT``, you can also specify
initial map center and zoom level::

    'DEFAULT_CENTER': (6.0, 45.0),
    'DEFAULT_ZOOM': 16,

The tuple/list must contain (lat,lng) coords.


Default tiles layer
-------------------

To globally add a tiles layer to your maps::

    'TILES': 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'

This setting can also be a list of tuples ``(name, url, attributions)``.

If it contains several layers, a layer switcher will then be added automatically.

::

    'TILES': [('Satellite', 'http://server/a/...', '© Big eye'),
              ('Streets', 'http://server/b/...', '© Contributors')]


Attribution prefix
------------------

To globally add an attribution prefix on maps (most likely an empty string) ::

    'ATTRIBUTION_PREFIX': 'Powered by django-leaflet'

Default is ``None``, which leaves the value to `Leaflet's default <http://leafletjs.com/reference.html#control-attribution>`_.


Scale control
-------------

Disable scale control with km and miles::

    'SCALE': False

Minimap control
---------------

Shows a small map in the corner which shows the same as the main map with a 
set zoom offset::

    'MINIMAP': True

By default it shows the tiles of the first layer in the list.

(`More info... <https://github.com/Norkart/Leaflet-MiniMap>`_)


Plugins
-------

To ease the usage of plugins, django-leaflet allows specifying a set of plugins, that can
later be referred to from the template tags by name::

    'PLUGINS': {
        'name-of-plugin': {
            'css': ['relative/path/to/stylesheet.css', '/root/path/to/stylesheet.css'],
            'js': 'http://absolute-url.example.com/path/to/script.js',
            'auto-include': True,
        },
        . . .
    }

Both 'css' and 'js' support identical features for specifying resource URLs:

    * can be either a plain string or a list of URLs
    * each string can be:

        - absolute URL - will be included as-is; **example**: ``http://absolute-url.example.com/path/to/script.js``
        - a URL beginning from the root - will be included as-is;  **example**: ``/root/path/to/stylesheet.css``
        - a relative URL - settings.STATIC_URL will be prepended; **example**: ``relative/path/to/stylesheet.css`` will be included as **/static/relative/path/to/stylesheet.css** (depending on your setting for STATIC_URL)

Now, use ``leaflet_js`` and ``leaflet_css`` tags to load CSS and JS resources of 
configured Leaflet plugins.

By default only plugins with ``'auto-include'`` as True will be included.

To include specific plugins in the page, specify plugin names, comma separated::

    {% load leaflet_tags %}

    <head>
        ...
        {% leaflet_js  plugins="bouncemarker, draw" %}
        {% leaflet_css plugins="bouncemarker, draw"%}
    </head>

To include all plugins configured in ``LEAFLET_CONFIG['PLUGINS']``, use::

    {% leaflet_js plugins="ALL" %}
    {% leaflet_css plugins="ALL" %}


Advanced usage
==============

``{% leaflet_map %}`` tag parameters
------------------------------------

* ``callback``: javascript function name for initialization callback.
  (Default: None).

* ``fixextent``: control if map initial view shoud be set to extent setting.
  (Default: ``True``). Setting fixextent to ``False`` will prevent view reset
  and scale controls to be added.

* ``creatediv``: control if the leaflet map tags creates a new div or not.
  (Default: ``True``).
  Useful to put the javascript code in the header or footer instead of the
  body of the html document. If used, do not forget to create the div manually.

* ``loadevent``: One or more space-separated *window* events that trigger map initialization.
  (Default: ``load``, i.e. all page resources loaded).
  If empty values is provided, then map initialization is immediate.
  And with a wrong value, the map is never initialized. :)


Projection
----------

It is possible to setup the map spatial reference in ``LEAFLET_CONFIG``::

    'SRID': 2154  # See http://spatialreference.org

Additional parameter is required to compute scale levels : the tiles extent in
local projection::

    'TILES_EXTENT': [700000, 6325197, 1060000, 6617738],

For more information, `have a look at this example <http://blog.mathieu-leplatre.info/leaflet-tiles-in-lambert-93-projection-2154.html>`_.

By default, Django will try to load the spatial reference from your static
files at "proj4js/{{ srid }}.js". If it fails, it will eventually rely on
`<spatialreference.org>`_.

=======
AUTHORS
=======

* Mathieu Leplatre <mathieu.leplatre@makina-corpus.com>
* Ariel Núñez <http://ingenieroariel.com>
* Boris Chervenkov <https://github.com/boris-chervenkov>

|makinacom|_

.. |makinacom| image:: http://depot.makina-corpus.org/public/logo.gif
.. _makinacom:  http://www.makina-corpus.com

=======
LICENSE
=======

* Lesser GNU Public License
* Leaflet Copyright - 2010-2011 CloudMade, Vladimir Agafonkin
