*django-leaflet* allows you to use `Leaflet <http://leaflet.cloudmade.com>`_
in your `Django <https://www.djangoproject.com>`_ projects.


=======
INSTALL
=======

::

    pip install django-leaflet

=====
USAGE
=====

* Add ``leaflet`` to your ``INSTALLED_APPS``

* Add the HTML header :

::

    {% load leaflet_tags %}
    
    <head>
        ...
        {% leaflet_js %}
        {% leaflet_css %}
    </head>


* Add the map in your page, providing a name :
::
    
    ...
    <body>
        ...
        {% leaflet_map "yourmap" %}
        ...
    </body>


* Use the *Leaflet* API as usual in the map initialization callback (*can be
  facultative depending on settings*) :

::

    <script type="text/javascript">
        function yourmapInit(yourmap, bounds) {
            ...
            // Add background layer from MapBox
            yourmap.addLayer(new L.TileLayer('http://{s}.tiles.mapbox.com/v3/mapbox.mapbox-light/{z}/{x}/{y}.png'));
            ...
        }
    </script>



* Give your maps a size (``height`` is **mandatory**) :

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

In order to configure *django-leaflet*, just add a new section in your settings :

::

    LEAFLET_CONFIG = {
        # conf here
    }


Spatial extent
--------------

You can configure a global spatial extent for your maps, that will automatically
center your maps, restrict panning and add reset view and scale controls.
(*See advanced usage to tweak that.*)

    'SPATIAL_EXTENT' : (5.0, 44.0, 7.5, 46)

Default tiles layer
-------------------

To globally add a tiles layer to your maps :

    'TILES_URL' : 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'

This setting can also be a list of tuples (name, url) ! A layer switcher
will then be added automatically.

Leaflet version
---------------

By default, it runs the last stable version (*0.4.4*) of Leaflet. But it is possible 
to run the ``legacy`` version (*0.3.1*) or the ``unstable`` under development (*master*).

    'LEAFLET_VERSION' : 'legacy'

Scale control
-------------

Automatically add a scale control with km and miles :

    'SCALE' : False


Advanced usage
==============

{% leaflet_map %} tag parameters
--------------------------------

    callback

        A Javascript function name for initialization callback. (Default:``name + Init``)
        
        ``{% leaflet_map "yourmap" callback="window.customMap" %}``

    fixextent

        Control if map initial view shoud be set to extent setting. (Default: ``True``).
        Setting fixextent to ``False`` will prevent view reset and scale controls
        to be added.


Projection
----------

It is possible to setup the map spatial reference in ``LEAFLET_CONFIG`` :

    'SRID' : 2154   # See http://spatialreference.org

Additional parameters are then required to compute scale levels :

    'MAX_RESOLUTION' : 1142.7383,
    'TILES_EXTENT' : [700000,6325197,1060000,6617738],

For more information, `have a look at this example <http://blog.mathieu-leplatre.info/leaflet-tiles-in-lambert-93-projection-2154.html>`_.

=======
AUTHORS
=======

    * Mathieu Leplatre <mathieu.leplatre@makina-corpus.com>

|makinacom|_

.. |makinacom| image:: http://depot.makina-corpus.org/public/logo.gif
.. _makinacom:  http://www.makina-corpus.com

=======
LICENSE
=======

    * Lesser GNU Public License
    * Leaflet Copyright - 2010-2011 CloudMade, Vladimir Agafonkin
