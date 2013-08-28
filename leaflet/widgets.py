from django.contrib.gis.admin.widgets import OpenLayersWidget


LEAFLET_DATA_SRID = 4326


class LeafletWidget(OpenLayersWidget):
    def render(self, name, value, attrs=None):
        attrs = attrs or {}
        attrs.update(id_map=attrs.get('id', '') + '_map',
                     id_map_callback = attrs.get('id', '') + '_map_callback',
                     srid=LEAFLET_DATA_SRID)
        return super(LeafletWidget, self).render(name, value, attrs)

    def map_options(self):
        return {}