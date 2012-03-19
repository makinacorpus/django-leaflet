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


* Add the map in your page :

::
    
    ...
    <body>
        ...
        {% leaflet_map "yourmap" %}
        ...        
    </body>

* Use the *Leaflet* API as usual on the resulting ``yourmap`` object :

::

    <script type="text/javascript">
        ...
        // Add background layer from MapBox
        yourmap.addLayer(new L.TileLayer('http://{s}.tiles.mapbox.com/v3/mapbox.mapbox-light/{z}/{x}/{y}.png'));
        ...
    </script>

* Give your maps a size (**mandatory**) :

::

    <style>
    
        .leaflet-container {
            width:  600px;
            height: 400px;
        }
        
        #specialbigmap {
            height: 800px;
        }
        
    </style>

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

