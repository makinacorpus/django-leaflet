import json

from django import template
from django.template import Context
from django.conf import settings

from leaflet import app_settings, SPATIAL_EXTENT, SRID
from leaflet import MAP_CENTER, MAP_ZOOM, PLUGINS_CSS, PLUGINS_JS


register = template.Library()

@register.inclusion_tag('leaflet/css.html')
def leaflet_css(only_plugins=None, exclude_plugins=None):
    """

    :param only_plugins:
    :param exclude_plugins:
    :return:
    """
    return {
        "MINIMAP": app_settings.get('MINIMAP'),
        "PLUGINS_CSS": PLUGINS_CSS,
    }


@register.inclusion_tag('leaflet/js.html')
def leaflet_js(only_plugins=None, exclude_plugins=None):
    """

    :param only_plugins:
    :param exclude_plugins:
    :return:
    """
    return {
        "DEBUG": settings.TEMPLATE_DEBUG,
        "SRID": SRID,
        "MINIMAP": app_settings.get('MINIMAP'),
        "PLUGINS_JS": PLUGINS_JS,
    }


@register.simple_tag
def leaflet_map(name, callback=None, fitextent=True, creatediv=True):
    """

    :param name:
    :param callback:
    :param fitextent:
    :param creatediv:
    :return:
    """
    if callback is None:
        callback = "%sInit" % name

    tilesurl = app_settings.get('TILES_URL')
    if tilesurl and isinstance(tilesurl, basestring):
        tilesurl = (('background', tilesurl),)

    extent = None
    if SPATIAL_EXTENT is not None:
        xmin, ymin, xmax, ymax = SPATIAL_EXTENT
        extent = (ymin, xmin, ymax, xmax)

    t = template.loader.get_template("leaflet/map_fragment.html")
    return t.render(Context(dict(name=name,
                                 creatediv=creatediv,
                                 srid=SRID,
                                 extent=list(extent),
                                 map_center=MAP_CENTER,
                                 map_zoom=MAP_ZOOM,
                                 fitextent=fitextent,
                                 tilesurl=[list(url) for url in tilesurl],
                                 callback=callback,
                                 scale=app_settings.get('SCALE'),
                                 minimap=app_settings.get('MINIMAP'),
                                 tilesextent=list(app_settings.get('TILES_EXTENT', [])),
                                )))

@register.simple_tag
def leaflet_json_config():
    settings_as_json = app_settings.copy()

    if SPATIAL_EXTENT is not None:
        xmin, ymin, xmax, ymax = settings_as_json.pop('SPATIAL_EXTENT')
        settings_as_json['SPATIAL_EXTENT'] = { 'xmin': xmin, 'ymin': ymin, 'xmax': xmax, 'ymax': ymax }

    return json.dumps(settings_as_json)
