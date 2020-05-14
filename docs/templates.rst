Use in templates
================

Use Leaflet API
---------------

You can use the *Leaflet* API as usual. There are two ways to
grab a reference on the just initialized map and options.


**Using Javascript callback function**

The easy way :

::

    <script>
        function map_init_basic (map, options) {
            ...
            L.marker([50.5, 30.5]).addTo(map);
            ...
        }
    </script>

    {% leaflet_map "yourmap" callback="window.map_init_basic" %}


**Using events**

If you don't want to expose global callbacks :

::

    <script>
        window.addEventListener("map:init", function (e) {
            var detail = e.detail;
            ...
            L.marker([50.5, 30.5]).addTo(detail.map);
            ...
        }, false);
    </script>

Event object has two properties : ``map`` and ``options`` (initialization).

For Internet Explorer support, we fallback on jQuery if available ::

    $(window).on('map:init', function (e) {
        var detail = e.originalEvent ?
                     e.originalEvent.detail : e.detail;
        ...
        L.marker([50.5, 30.5]).addTo(detail.map);
        ...
    });


Customize map size
------------------

CSS is your friend:

::

    <style>

        .leaflet-container {  /* all maps */
            width:  600px;
            height: 400px;
        }

        #specialbigmap {
            height: 800px;
        }

        /* Resize the "display_raw" textbox */
        .django-leaflet-raw-textarea {
            width: 100%;
        }

    </style>



Configuration
-------------

In order to configure *django-leaflet*, just add a new section in your
settings::

    LEAFLET_CONFIG = {
        # conf here
    }

And add some of the following entries.


Spatial extent
~~~~~~~~~~~~~~

You can configure a global spatial extent for your maps, that will
automatically center your maps, restrict panning and add reset view and scale
controls. (*See advanced usage to tweak that.*)::

    'SPATIAL_EXTENT': (5.0, 44.0, 7.5, 46)


Initial map center and zoom level
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In addition to limiting your maps with ``SPATIAL_EXTENT``, you can also specify
initial map center, default, min and max zoom level::

    'DEFAULT_CENTER': (6.0, 45.0),
    'DEFAULT_ZOOM': 16,
    'MIN_ZOOM': 3,
    'MAX_ZOOM': 18,

The tuple/list must contain (lat,lng) coords.


Default tiles layer
~~~~~~~~~~~~~~~~~~~

To globally add a tiles layer to your maps::

    'TILES': 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'

This setting can also be a list of tuples ``(name, url, options)``.
The python dict ``options`` accepts all the Leaflet tileLayers options.

If it contains several layers, a layer switcher will then be added automatically.

::

    'TILES': [('Satellite', 'http://server/a/...', {'attribution': '&copy; Big eye', 'maxZoom': 16}),
              ('Streets', 'http://server/b/...', {'attribution': '&copy; Contributors'})]


If you omit this setting, a default OpenSTreetMap layer will be created for your convenience. If you do not want
a default layers (perhaps to add them in your own JavaScript code on map initialization), set the value to an empty
list, as shown below.

::

    'TILES': []

Note that this will also prevent any overlays defined in settings from being displayed.

.. _overlays:
Overlay layers
~~~~~~~~~~~~~~

To globally add an overlay layer, use the same syntax as tiles::

    'OVERLAYS': [('Cadastral', 'http://server/a/{z}/{x}/{y}.png', {'attribution': '&copy; IGN'})]

Currently, overlay layers from settings are limited to tiles. For vectorial overlays, you
will have to add them via JavaScript (see also events).

.. new section: worked example on including WMS overlays
To add layers other than the tiles supported by the global config, e.g. WMS layers,
insert a script block, get a reference to the map's ``layerscontrol``, and add any layer supported by Leaflet
as overlays to that layerscontrol object.


In a template:

::

    {% block content %}
    {% leaflet_map "detailmap" callback="window.map_init" %}
    {% endblock %}


    {% block javascript %}
    {{ block.super }}
    <script>
    function map_init(map, options) {
        {% include 'shared/overlays.html' %}
    }
    </script>
    {% endblock %}

In a snippet, here called ``shared/overlays.html``, the overlays are configured.
Doing so in a snippet allows the same set of overlays to be re-used across other maps in your Django project.

``shared/overlays.html``:

::

    var lc = map.layerscontrol;

    // An example from the Atlas of Living Australia https://www.ala.org.au/
    lc.addOverlay(
        L.tileLayer.wms(
        'https://spatial-beta.ala.org.au/geoserver/ALA/wms',
        {layers: 'ALA:aus2', format: 'image/png', transparent: true}),
        'Australia'
    );

    // add lc.addOverlay() layers as needed

For an overview of available layer types and options, see the
[Leaflet docs on tile layers](https://leafletjs.com/examples/wms/wms.html).

Attribution prefix
~~~~~~~~~~~~~~~~~~

To globally add an attribution prefix on maps (most likely an empty string) ::

    'ATTRIBUTION_PREFIX': 'Powered by django-leaflet'

Default is ``None``, which leaves the value to `Leaflet's default <http://leafletjs.com/reference.html#control-attribution>`_.


Scale control
~~~~~~~~~~~~~

Scale control may be set to show 'metric' (m/km), or 'imperial' (mi/ft) scale
lines, or 'both'.  Default is 'metric'.

Enable metric and imperial scale control::

    'SCALE': 'both'

Disable scale control::

    'SCALE': None


Minimap control
~~~~~~~~~~~~~~~

Shows a small map in the corner which shows the same as the main map with a
set zoom offset::

    'MINIMAP': True

By default it shows the tiles of the first layer in the list.

(`More info... <https://github.com/Norkart/Leaflet-MiniMap>`_)

Reset view button
~~~~~~~~~~~~~~~~~

By default, a button appears below the zoom controls and, when clicked, shows the entire map.
To remove this button, set::

    'RESET_VIEW': False


Global initialization functions and ``window.maps``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since 0.7.0, the ``leaflet_map`` template tag no longer registers initialization functions in global scope,
and no longer adds map objects into ``window.maps`` array by default. To restore these features, use::

    'NO_GLOBALS' = False

Force Leaflet image path
~~~~~~~~~~~~~~~~~~~~~~~~

If you are using staticfiles compression libraries such as django_compressor,
which can do any of compressing, concatenating or renaming javascript files,
this may break Leaflet's own ability to determine its installed path, and in
turn break the method ``L.Icon.Default.imagePath()``.

To use Django's own knowledge of its static files to force this value
explicitly, use::

    'FORCE_IMAGE_PATH': True

Plugins
~~~~~~~

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

  * absolute URL - will be included as-is; **example**: ``http://absolute-url.example.com/path/to/script.js``
  * a URL beginning from the root - will be included as-is;  **example**: ``/root/path/to/stylesheet.css``
  * a relative URL - settings.STATIC_URL will be prepended; **example**: ``relative/path/to/stylesheet.css`` will be included as **/static/relative/path/to/stylesheet.css** (depending on your setting for STATIC_URL)

Now, use ``leaflet_js`` and ``leaflet_css`` tags to load CSS and JS resources of
configured Leaflet plugins.

By default only plugins with ``'auto-include'`` as True will be included.

To include specific plugins in the page, specify plugin names, comma separated::

    {% load leaflet_tags %}

    <head>
        ...
        {% leaflet_js  plugins="bouncemarker,draw" %}
        {% leaflet_css plugins="bouncemarker,draw" %}
    </head>

To include all plugins configured in ``LEAFLET_CONFIG['PLUGINS']``, use::

    {% leaflet_js plugins="ALL" %}
    {% leaflet_css plugins="ALL" %}
