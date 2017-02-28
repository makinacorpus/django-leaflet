Leaflet map forms widgets
=========================

A Leaflet widget is provided to edit geometry fields.
It embeds *Leaflet.draw* in version *0.4.0*.


.. image :: https://f.cloud.github.com/assets/546692/1048836/78b6ad94-1094-11e3-86d8-c3e88626a31d.png


In Adminsite
------------

::

    from django.contrib import admin
    from leaflet.admin import LeafletGeoAdmin

    from .models import WeatherStation


    admin.site.register(WeatherStation, LeafletGeoAdmin)


A mixin is also available for inline forms:

::

    from django.contrib import admin
    from leaflet.admin import LeafletGeoAdminMixin

    class PoiLocationInline(LeafletGeoAdminMixin, admin.StackedInline):
        model = PoiLocation


In forms
--------

With *Django* >= 1.6:

::

    from django import forms

    from leaflet.forms.widgets import LeafletWidget


    class WeatherStationForm(forms.ModelForm):

        class Meta:
            model = WeatherStation
            fields = ('name', 'geom')
            widgets = {'geom': LeafletWidget()}

With all *Django* versions:

::

    from django import forms

    from leaflet.forms.fields import PointField


    class WeatherStationForm(forms.ModelForm):
        geom = PointField()

        class Meta:
            model = WeatherStation
            fields = ('name', 'geom')

The related template would look like this:

::

    {% load leaflet_tags %}
    <html>
      <head>
       {% leaflet_js plugins="forms" %}
       {% leaflet_css plugins="forms" %}
      </head>
      <body>
        <h1>Edit {{ object }}</h1>
        <form action="POST">
            {{ form }}
            <input type="submit"/>
        </form>
      </body>
    </html>


Every map field will trigger an event you can use to add your custom machinery :

::

    map.on('map:loadfield', function (e) {
        ...
        // Customize map for field
        console.log(e.field, e.fieldid);
        ...
    });


If you need a reusable customization of widgets maps, first override the JavaScript field behaviour by extending ``L.GeometryField``, then in Django subclass the ``LeafletWidget`` to specify the custom ``geometry_field_class``.

::

    YourGeometryField = L.GeometryField.extend({
        addTo: function (map) {
            L.GeometryField.prototype.addTo.call(this, map);
            // Customize map for field
            console.log(this);
        },
        // See GeometryField source (static/leaflet/leaflet.forms.js) to override more stuff...
    });

::

    class YourMapWidget(LeafletWidget):
        geometry_field_class = 'YourGeometryField'

    class YourForm(forms.ModelForm):
        class Meta:
            model = YourModel
            fields = ('name', 'geom')
            widgets = {'geom': YourMapWidget()}

Plugins
-------

It's possible to add extras JS/CSS or auto-include *forms* plugins
everywhere: ::

    LEAFLET_CONFIG = {
        'PLUGINS': {
            'forms': {
                'auto-include': True
            }
        }
    }

( *It will be merged over default minimal set required for edition* )


Details
-------

* It relies on global settings for map initialization.
* It works with local map projections. But SRID is specified globally
  through ``LEAFLET_CONFIG['SRID']`` as described below.
* Javascript component for de/serializing fields value is pluggable.
* Javascript component for Leaflet.draw behaviour initialization is pluggable.
