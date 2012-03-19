from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def leaflet_css():
    return '<link rel="stylesheet" type="text/css" href="%sleaflet.css">' % settings.STATIC_URL

@register.simple_tag
def leaflet_js():
    leafletjs = 'leaflet.min.js'
    if settings.TEMPLATE_DEBUG:
        leafletjs = 'leaflet.js'
    return '<script src="%s%s" type="text/javascript"></script>' % (settings.STATIC_URL, leafletjs)

@register.simple_tag
def leaflet_map(name):
    return """
    <div id="%(name)s"></div>
    <script type="text/javascript">
        var %(name)s = new L.Map('%(name)s');
    </script>
    """ % {'name': name}

