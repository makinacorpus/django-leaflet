import json

from django import template
from django.template import Context
from django.conf import settings

from leaflet import app_settings, SPATIAL_EXTENT, SRID
from leaflet import PLUGINS


register = template.Library()

@register.inclusion_tag('leaflet/css.html')
def leaflet_css(plugins=None):
    """

    :param only_plugins:
    :param exclude_plugins:
    :return:
    """
    plugin_names = _get_plugin_names(plugins)
    return {
        "MINIMAP": app_settings.get('MINIMAP'),
        "PLUGINS_CSS": _get_all_resources_for_plugins(plugin_names, 'css'),
    }


@register.inclusion_tag('leaflet/js.html')
def leaflet_js(plugins=None):
    """

    :param only_plugins:
    :param exclude_plugins:
    :return:
    """
    plugin_names = _get_plugin_names(plugins)
    return {
        "DEBUG": settings.TEMPLATE_DEBUG,
        "SRID": SRID,
        "MINIMAP": app_settings.get('MINIMAP'),
        "PLUGINS_JS":  _get_all_resources_for_plugins(plugin_names, 'js'),
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
                                 center=app_settings['DEFAULT_CENTER'],
                                 zoom=app_settings['DEFAULT_ZOOM'],
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




def _get_plugin_names(plugin_names_from_tag_parameter):
    """
    Returns a list of plugin names, specified in the parameter.
    Used by tags to determine which plugins to include
    :param pluging_names_parameter:
    :return:
    """
    if isinstance(plugin_names_from_tag_parameter, (str,unicode)):
        names = plugin_names_from_tag_parameter.split(',')
        return map(lambda n: n.strip(), names)
    else:
        return []



def _get_all_resources_for_plugins(plugin_names, resource_type):
    """
    Returns a list of URLs for the plugins with the specified resource type (js, css, ...)
    :param plugin_names:
    :param resource_type:
    :return:
    """
    result = []
    for plugin_name in plugin_names:
        if plugin_name in PLUGINS:
            result.extend(PLUGINS[plugin_name].get(resource_type, []))

    return result

