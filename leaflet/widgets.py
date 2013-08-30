from django.contrib.gis.forms.widgets import BaseGeometryWidget


class LeafletWidget(BaseGeometryWidget):
    template_name = 'leaflet/widget.html'
    map_width = '100%'
    map_height = 400
    modifiable = True

    class Media:
        js = ('leaflet/leaflet.js',
              'leaflet/draw/leaflet.draw.js',
              'leaflet/leaflet.extras.js',
              'leaflet/leaflet.form.js',
              'leaflet/wicket/wicket.js',
              'leaflet/wicket/wicket-leaflet.js')

        css = ('leaflet/leaflet.css',
               'leaflet/draw/leaflet.draw.css')

    def render(self, name, value, attrs=None):
        attrs = attrs or {}
        attrs.update(id_map=attrs.get('id', '') + '_map',
                     id_map_callback = attrs.get('id', '') + '_map_callback',
                     modifiable=self.modifiable,
                     map_srid=self.map_srid,
                     map_width=self.map_width,
                     map_height=self.map_height,
                     geometry_field_class=attrs.get('geometry_field_class', 'L.GeometryField'),
                     field_store_class=attrs.get('field_store_class', 'L.FieldStore'))
        return super(LeafletWidget, self).render(name, value, attrs)
