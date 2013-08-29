from django.contrib.gis.admin import OSMGeoAdmin

from .widgets import LeafletWidget


class LeafletGeoAdmin(OSMGeoAdmin):
    widget = LeafletWidget
    map_template = 'leaflet/admin/leaflet.html'
    openlayers_url = 'leaflet/leaflet-src.js'

    @property
    def media(self):
        media = super(LeafletGeoAdmin, self).media
        media.add_js(['leaflet/draw/leaflet.draw.js',
                      'leaflet/leaflet.extras.js',
                      'leaflet/leaflet.form.js',
                      'leaflet/wicket/wicket.js',
                      'leaflet/wicket/wicket-leaflet.js'])
        media.add_css({'screen': ('leaflet/leaflet.css',
                                  'leaflet/draw/leaflet.draw.css')})
        return media
