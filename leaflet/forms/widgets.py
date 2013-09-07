from django import forms
try:
    from django.contrib.gis.forms.widgets import BaseGeometryWidget
except ImportError:
    from django.forms.widgets import Textarea

    class BaseGeometryWidget(Textarea):
        geom_type = 'GEOMETRY'
        display_raw = False

from .. import PLUGINS, PLUGIN_FORMS


class LeafletWidget(BaseGeometryWidget):
    template_name = 'leaflet/widget.html'
    map_srid = 4326
    map_width = None
    map_height = None
    modifiable = True
    supports_3d = False
    include_media = False

    @property
    def media(self):
        if not self.include_media:
            return forms.Media()

        js = PLUGINS[PLUGIN_FORMS]['js']
        css = PLUGINS[PLUGIN_FORMS]['css']
        return forms.Media(js=js, css={'screen': css})

    def serialize(self, value):
        return value.geojson if value else ''

    def render(self, name, value, attrs=None):
        assert self.map_srid == 4326, 'Leaflet vectors should be decimal degrees.'

        # Retrieve params from Field init (if any)
        self.geom_type = self.attrs.get('geom_type', self.geom_type)

        attrs = attrs or {}

        # In BaseGeometryWidget, geom_type is set using gdal, and fails with generic.
        # See https://code.djangoproject.com/ticket/21021
        if self.geom_type == 'GEOMETRY':
            attrs['geom_type'] = 'Geometry'

        attrs.update(id_map=attrs.get('id', name) + '_map',
                     id_map_callback=attrs.get('id', name) + '_map_callback',
                     modifiable=self.modifiable,
                     geometry_field_class=attrs.get('geometry_field_class', 'L.GeometryField'),
                     field_store_class=attrs.get('field_store_class', 'L.FieldStore'))
        return super(LeafletWidget, self).render(name, value, attrs)
