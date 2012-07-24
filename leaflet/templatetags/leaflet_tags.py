from django import template
from django.conf import settings

from . import SPATIAL_EXTENT


register = template.Library()

@register.simple_tag
def leaflet_css():
    return """<link rel="stylesheet" type="text/css" href="%(static)sleaflet.css">
    <!--[if lte IE 8]>
    <link rel="stylesheet" type="text/css" href="%(static)sleaflet.ie.css" />
    <![endif]-->
    """ % {'static': settings.STATIC_URL}

@register.simple_tag
def leaflet_js():
    leafletjs = 'leaflet.min.js'
    if settings.TEMPLATE_DEBUG:
        leafletjs = 'leaflet.js'
    return '<script src="%s%s" type="text/javascript"></script>' % (settings.STATIC_URL, leafletjs)

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

    return """
    <div id="%(name)s"></div>
    <script type="text/javascript">
        var loadmap%(name)s = function () {
            var map = new L.Map('%(name)s');
            %(extent)s
            %(callback)s(map, bounds);
        };
        window.addEventListener("load", loadmap%(name)s);
    </script>
    """ % {'name': name, 'callback': callback, 'extent': conf_extent}
