from django.contrib.gis.admin import OSMGeoAdmin

from .widgets import LeafletWidget


class LeafletGeoAdmin(OSMGeoAdmin):
    widget = LeafletWidget
    map_template = 'leaflet/admin/leaflet.html'
    openlayers_url = 'leaflet/leaflet.js'
    leaflet_extras_url = 'leaflet/leaflet.extras.js'
    leaflet_css = 'leaflet/leaflet.css'

    @property
    def media(self):
        media = super(LeafletGeoAdmin, self).media
        media.add_js([self.leaflet_extras_url])
        media.add_css({'screen': (self.leaflet_css,)})
        return media
