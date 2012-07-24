*django-leaflet* allows you to use `Leaflet <http://leaflet.cloudmade.com>`_ (*version 0.3*)
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


* Use the *Leaflet* API as usual in the map initialization callback :

::

    <script type="text/javascript">
        function yourmapInit(yourmap, bounds) {
            ...
            // Add background layer from MapBox
            yourmap.addLayer(new L.TileLayer('http://{s}.tiles.mapbox.com/v3/mapbox.mapbox-light/{z}/{x}/{y}.png'));
            ...
        }
    </script>

:notes:

    A Javascript function name for initialization callback can be provided
    with ``{% leaflet_map "yourmap" "window.customMap" %}``. Default is ``name + Init``.


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

You can configure a global spatial extent for your maps, that will automatically
center your maps and restrict panning. Just add in your project settings :

::

    LEAFLET_CONFIG = {
        'SPATIAL_EXTENT' : (5.0, 44.0, 7.5, 46)
    }


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
