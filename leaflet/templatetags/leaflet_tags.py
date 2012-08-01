import os
from django import template
from django.conf import settings

from leaflet import app_settings, SPATIAL_EXTENT


register = template.Library()


def base_url():
    version = app_settings.get('LEAFLET_VERSION')
    return os.path.join(settings.STATIC_URL, "leaflet", version)


@register.simple_tag
def leaflet_css():
    return """<link rel="stylesheet" type="text/css" href="%(static)s/leaflet.css">
    <!--[if lte IE 8]>
    <link rel="stylesheet" type="text/css" href="%(static)s/leaflet.ie.css" />
    <![endif]-->
    """ % {'static': base_url()}


@register.simple_tag
def leaflet_js():
    leafletjs = 'leaflet.min.js'
    if settings.TEMPLATE_DEBUG:
        leafletjs = 'leaflet.js'
    return '<script src="%s/%s" type="text/javascript"></script>' % (base_url(), leafletjs)


@register.simple_tag
def leaflet_map(name, callback=None):
    if callback is None:
        callback = "%sInit" % name

    conf_extent = """
        var bounds = null;
    """
    if SPATIAL_EXTENT is not None:
        xmin, ymin, xmax, ymax = SPATIAL_EXTENT
        conf_extent = """
        var southWest = new L.LatLng(%s, %s),
            northEast = new L.LatLng(%s, %s),
            bounds = new L.LatLngBounds(southWest, northEast);
        // Restrict to bounds
        map.setMaxBounds(bounds);
        // Fit bounds
        map.fitBounds(bounds);
        """ % (ymin, xmin, ymax, xmax)

    conf_tileslayer = ""
    tilesurl = app_settings.get('TILES_URL')
    if tilesurl:
        conf_tileslayer = """
            var tilesLayer = new L.TileLayer("%s");
            map.addLayer(tilesLayer);
        """ % tilesurl

    return """
    <div id="%(name)s"></div>
    <script type="text/javascript">
        var loadmap%(name)s = function () {
            var map = new L.Map('%(name)s');
            %(extent)s
            %(tiles)s
            if(typeof %(callback)s == 'function') {
                %(callback)s(map, bounds);
            }
        };
        window.addEventListener("load", loadmap%(name)s);
    </script>
    """ % {'name': name, 'callback': callback, 
           'extent': conf_extent,
           'tiles': conf_tileslayer}
