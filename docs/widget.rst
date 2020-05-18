Leaflet map forms widgets
=========================

A Leaflet widget is provided to edit geometry fields.
It embeds *Leaflet.draw* in version *0.4.0*.


.. image :: https://f.cloud.github.com/assets/546692/1048836/78b6ad94-1094-11e3-86d8-c3e88626a31d.png

.. _admin:
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


To modify the map widget used in the Django admin,
override a custom ``admin/change_form.html``:

::

    {% extends "admin/change_form.html" %}
    {% load i18n admin_urls static leaflet_tags %}

    {% block stylesheets %}
    {{ block.super }}
    {% leaflet_css plugins="ALL" %}
    <style>
    /* Force leaflet controls underneath header (z-index 1000) and
       above leaflet tiles (z-index 400)*/
    .leaflet-top{z-index:999;}
    </style>
    {% endblock %}

    {% block javascripts %}
    {{ block.super }}
    {% leaflet_js plugins="ALL" %}
    {% include 'shared/leaflet_widget_overlays.js' %}
    {% endblock %}

In this way, both CSS and JS can be modified for all admin leaflet widgets.

As an example of modifying the CSS, here the leaflet map widget controls
are forced underneath a bootstrap4 navbar.

As an example of modifying the JS, a custom snippet called
``shared/leaflet_widget_overlays.js`` uses the map init event to add
some custom (non-tile) overlays.

::

    <script>
      window.addEventListener("map:init", function (event) {
        var map = event.detail.map; // Get reference to map
        {% include 'shared/overlays.html' %}

        // Other modifications, e.g. fullscreen control:
        map.addControl(new L.Control.Fullscreen());
        // Note, this requires the Leaflet fullscreen CSS, JS,
        // and image assets to be present as static files,
        // and configured in LEAFLET_SETTINGS
    });
    </script>

Again, the actual overlays here are factored out into a separate snippet.
In this example, we re-use ``shared/overlays.html`` as also shown in :ref:`overlays`.

To show a textarea input for the raw GeoJSON geometry, override admin ``form_fields``:

::

    from django.contrib.gis.db import models as geo_models

    LEAFLET_WIDGET_ATTRS = {
        'map_height': '500px',
        'map_width': '100%',
        'display_raw': 'true',
        'map_srid': 4326,
    }

    LEAFLET_FIELD_OPTIONS = {'widget': LeafletWidget(attrs=LEAFLET_WIDGET_ATTRS)}

    FORMFIELD_OVERRIDES = {
        geo_models.PointField: LEAFLET_FIELD_OPTIONS,
        geo_models.MultiPointField: LEAFLET_FIELD_OPTIONS,
        geo_models.LineStringField: LEAFLET_FIELD_OPTIONS,
        geo_models.MultiLineStringField: LEAFLET_FIELD_OPTIONS,
        geo_models.PolygonField: LEAFLET_FIELD_OPTIONS,
        geo_models.MultiPolygonField: LEAFLET_FIELD_OPTIONS,
    }

    class MyAdmin(admin.ModelAdmin):

        formfield_overrides = FORMFIELD_OVERRIDES


The widget attribute `display_raw` toggles the textarea input.
The textarea can be resized by overriding its CSS class ``.django-leaflet-raw-textarea``.


In forms
--------

::

    from django import forms

    from leaflet.forms.widgets import LeafletWidget


    class WeatherStationForm(forms.ModelForm):

        class Meta:
            model = WeatherStation
            fields = ('name', 'geom')
            widgets = {'geom': LeafletWidget()}

Again, the LeafletWidget can be intialized with custom attributes,
e.g. ``LeafletWidget(attrs=LEAFLET_WIDGET_ATTRS)`` as shown above.

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

Programmatically appended maps
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you are adding a map to the DOM programmatically, as for example by jQuery, the 
default events driven mechanism will not work, and a viable workaround is to specify 
an empty ``loadevent`` attribute in your ``Meta.widgets`` definiton :

::

    class Meta:
        ...
        widgets = {
            'geometry': LeafletWidget(attrs={'loadevent': ''}),
        }
        
You will also need to refresh the map by invoking ``invalidateSize`` on it, and to do
so you need to instruct django-leaflet to expose the map globally, by setting the 
``NO_GLOBALS`` to False, in ``LEAFLET_CONFIG``.  The map will be accessible via a field
added to the global ``window`` object: if ``xyzt`` is the name of your field, your 
corresponding leaflet map will be at ``window['leafletmapid_xyzt-map']``.

Custom Forms
~~~~~~~~~~~~

If you need a reusable customization of widgets maps, first override the JavaScript
field behavior by extending ``L.GeometryField``, then in *Django* subclass the
``LeafletWidget`` to specify the custom ``geometry_field_class``.

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


To customise individual forms, you can either extend the geometry field as shown above,
or inject a script into the form template.

In this example, a custom set of overlays is added as shown for both :ref:`overlays`
and :ref:`admin` widgets, insert an extra script into the form template
in the same way as shown in :ref:`admin`.

::

    {% extends "base.html" %}
    {% load static leaflet_tags geojson_tags crispy_forms_tags bootstrap4  %}

    <!-- The form -->
    {% block content %}
    <div class="container">
      <div class="row">
        <div class="col-12">
          {% crispy form form.helper %}
        </div><!-- .col -->
      </div><!-- .row -->
    </div><!-- .container -->
    {% endblock %}

    {% block extrastyle %}
    {% leaflet_css plugins="ALL" %}
    {{ form.media.css }}
    {% endblock %}

    {% block extrajs %}
    {% leaflet_js plugins="ALL" %}
    {{ form.media.js }}
    {% include 'shared/leaflet_widget_overlays.js' %}
    {% endblock extrajs %}



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
