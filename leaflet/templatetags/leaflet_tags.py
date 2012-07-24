from django import template
from django.conf import settings

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

    return """
    <div id="%(name)s"></div>
    <script type="text/javascript">
        var loadmap%(name)s = function () {
            var map = new L.Map('%(name)s');
            %(callback)s(map);
        };
        window.addEventListener("load", loadmap%(name)s);
    </script>
    """ % {'name': name, 'callback': callback}
