# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
try:
    from django.contrib.gis.forms.widgets import BaseGeometryWidget
except ImportError:
    from .backport import BaseGeometryWidget

from leaflet import PLUGINS, PLUGIN_FORMS


class LeafletWidget(BaseGeometryWidget):
    template_name = 'leaflet/widget.html'
    map_srid = 4326
    map_width = None
    map_height = None
    modifiable = True
    supports_3d = False
    include_media = False
    geometry_field_class = 'L.GeometryField'
    field_store_class = 'L.FieldStore'
    target_map = None

    @property
    def media(self):
        if not self.include_media:
            return forms.Media()

        # We assume that including media for widget means there is
        # no Leaflet at all in the page.
        js = ['leaflet/leaflet.js'] + PLUGINS[PLUGIN_FORMS]['js']
        css = ['leaflet/leaflet.css'] + PLUGINS[PLUGIN_FORMS]['css']
        return forms.Media(js=js, css={'screen': css})

    def serialize(self, value):
        return value.geojson if value else ''

    def render(self, name, value, attrs=None):
        context = self.build_attrs(attrs)

        id_map = context.get('id', name).replace('-', '_')
        context.setdefault('id_map', id_map + '_map')  # JS-safe
        context.setdefault('id_map_callback', id_map + '_map_callback')

        override_at_class = ['geom_type', 'modifiable', 'map_srid', 'target_map',
                             'geometry_field_class', 'field_store_class']
        for key in override_at_class:
            context.setdefault(key, getattr(self, key))

        assert context['map_srid'] == 4326, 'Leaflet vectors should be decimal degrees.'

        # In BaseGeometryWidget, geom_type is set using gdal, and fails with generic.
        # https://github.com/django/django/blob/1.6.5/django/contrib/gis/forms/widgets.py#L73
        # See https://code.djangoproject.com/ticket/21021
        if context['geom_type'] == 'GEOMETRY':
            context['geom_type'] = 'Geometry'
        self.attrs['geom_type'] = context['geom_type']

        return super(LeafletWidget, self).render(name, value, context)
