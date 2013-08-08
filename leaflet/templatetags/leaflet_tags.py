import json

from django import template
from django.template import Context
from django.conf import settings

from leaflet import app_settings, SPATIAL_EXTENT, SRID, PLUGINS, PLUGINS_DEFAULT


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
        "PLUGINS_JS": _get_all_resources_for_plugins(plugin_names, 'js'),
    }


@register.inclusion_tag('leaflet/map_fragment.html')
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

    tiles = app_settings.get('TILES')

    extent = None
    if SPATIAL_EXTENT is not None:
        xmin, ymin, xmax, ymax = SPATIAL_EXTENT
        extent = (ymin, xmin, ymax, xmax)

    djoptions = dict(
        srid=SRID,
        extent=list(extent),
        fitextent=fitextent,
        center=app_settings['DEFAULT_CENTER'],
        zoom=app_settings['DEFAULT_ZOOM'],
        layers=tiles,
        scale=app_settings.get('SCALE'),
        minimap=app_settings.get('MINIMAP'),
        resetview=app_settings.get('RESET_VIEW'),
        tilesextent=list(app_settings.get('TILES_EXTENT', []))
    )

    return {
        'name': name,
        'creatediv': creatediv,
        'callback': callback,
        'GLOBAL_LOADMAP': app_settings.get('GLOBAL_LOADMAP'),
        'djoptions': json.dumps(djoptions)
    }


@register.simple_tag
def leaflet_json_config():
    settings_as_json = app_settings.copy()

    if SPATIAL_EXTENT is not None:
        xmin, ymin, xmax, ymax = settings_as_json.pop('SPATIAL_EXTENT')
        settings_as_json['SPATIAL_EXTENT'] = {'xmin': xmin, 'ymin': ymin,
                                              'xmax': xmax, 'ymax': ymax}

    return json.dumps(settings_as_json)


def _get_plugin_names(plugin_names_from_tag_parameter):
    """
    Returns a list of plugin names, specified in the parameter.
    Used by tags to determine which plugins to include
    :param pluging_names_parameter:
    :return:
    """
    if isinstance(plugin_names_from_tag_parameter, (str, unicode)):
        names = plugin_names_from_tag_parameter.split(',')
        return [n.strip() for n in names]
    else:
        return [PLUGINS_DEFAULT]


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
