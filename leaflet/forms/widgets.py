from django import forms
from django.contrib.gis.forms.widgets import BaseGeometryWidget
from django.core import validators
from django.template.defaultfilters import slugify

from leaflet import app_settings, PLUGINS, PLUGIN_FORMS


class LeafletWidget(BaseGeometryWidget):
    template_name = 'leaflet/widget.html'
    map_srid = 4326
    map_width = None
    map_height = None
    modifiable = True
    supports_3d = False
    include_media = False
    settings_overrides = {}

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

    def _get_attrs(self, name, attrs=None):
        assert self.map_srid == 4326, 'Leaflet vectors should be decimal degrees.'

        # Retrieve params from Field init (if any)
        self.geom_type = self.attrs.get('geom_type', self.geom_type)
        self.settings_overrides = self.attrs.get('settings_overrides', self.settings_overrides)

        # Setting 'loadevent' added in the widget constructor
        loadevent = self.attrs.get('loadevent', app_settings.get('LOADEVENT'))

        attrs = attrs or {}

        # In BaseGeometryWidget, geom_type is set using gdal, and fails with generic.
        # See https://code.djangoproject.com/ticket/21021
        if self.geom_type == 'GEOMETRY':
            attrs['geom_type'] = 'Geometry'

        map_id_css = slugify(attrs.get('id', name))  # id need to have - for the inline formset to replace the prefix
        map_id = map_id_css.replace('-', '_')  # JS-safe
        attrs.update(id=map_id,
                     id_css=map_id_css,
                     module='geodjango_%s' % map_id,
                     id_map=map_id_css + '-map',
                     id_map_callback=map_id + '_map_callback',
                     loadevent=loadevent,
                     modifiable=self.modifiable,
                     target_map=attrs.get('target_map', getattr(self, 'target_map', None)),
                     settings_overrides=attrs.get('settings_overrides', getattr(self, 'settings_overrides', None)),
                     geometry_field_class=attrs.get('geometry_field_class', getattr(self, 'geometry_field_class', 'L.GeometryField')),
                     field_store_class=attrs.get('field_store_class', getattr(self, 'field_store_class', 'L.FieldStore')))
        return attrs

    def get_context(self, name, value, attrs):
        value = None if value in validators.EMPTY_VALUES else value
        context = super().get_context(name, value, attrs)
        context.update(self._get_attrs(name, attrs))
        return context
