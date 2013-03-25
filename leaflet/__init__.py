import urlparse
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext as _


DEFAULT_TILES_URL = 'http://{s}.tiles.mapbox.com/v3/mapbox.mapbox-streets/{z}/{x}/{y}.png'

app_settings = dict({
    'TILES_URL': DEFAULT_TILES_URL,
    'SPATIAL_EXTENT': None,
    'MAP_ZOOM': None,
    'MAP_CENTER': None,
    'SRID': None,
    'SCALE': True,
    'TILES_EXTENT': [],
    'MINIMAP': False,
    'PLUGINS': {},
}, **getattr(settings, 'LEAFLET_CONFIG', {}))


SPATIAL_EXTENT = app_settings.get("SPATIAL_EXTENT")
if SPATIAL_EXTENT is None:
    SPATIAL_EXTENT = getattr(settings, 'SPATIAL_EXTENT', (-180, -90, 180, 90))
if SPATIAL_EXTENT is not None:
    if not isinstance(SPATIAL_EXTENT, (tuple, list)) or len(SPATIAL_EXTENT) != 4:
        raise ImproperlyConfigured(_("Spatial extent should be a tuple (minx, miny, maxx, maxy)"))

SRID = app_settings.get("SRID") 
if SRID is None:
    SRID = getattr(settings, 'MAP_SRID', getattr(settings, 'SRID', 3857))
if SRID == 3857:  # Leaflet's default, do not setup custom projection machinery
    SRID = None

MAP_CENTER = app_settings.get('MAP_CENTER', None)
if MAP_CENTER is not None and not (isinstance(MAP_CENTER, (list,tuple)) and len(MAP_CENTER) == 2):
    raise ImproperlyConfigured("LEAFLET_CONFIG['MAP_CENTER'] must be an list/tuple with two elements - (lon, lat)")

MAP_ZOOM = app_settings.get("MAP_ZOOM", None)
if MAP_ZOOM is not None and not (isinstance(MAP_ZOOM, int) and (1 <= MAP_ZOOM <= 24)):
    raise ImproperlyConfigured("LEAFLET_CONFIG['MAP_ZOOM'] must be an int between 1 and 24.")


PLUGINS = app_settings.get("PLUGINS", None)
if PLUGINS is not None and not (isinstance(PLUGINS, dict) and all(map(lambda el: isinstance(el, dict), PLUGINS.itervalues()))):
    raise ImproperlyConfigured("LEAFLET_CONFIG['PLUGINS'] must be dict of dicts in the format { '[plugin_name]': { 'js': '[path-to-js]', 'css': '[path-to-css]' } } .")

PLUGINS_CSS = []
PLUGINS_JS = []

# -----------------------

def _flat_list_from_plugin_config(key):
    """
    Flattens a list of lists to produce a single-level list:
        [1,[2,3], 4] => [1,2,3,4]
    :param key:
    :param config:
    :return:
    """
    result = []
    for plugin_dict in PLUGINS.itervalues():
        e = plugin_dict.get(key)
        if isinstance(e, (str, unicode)):
            result.append(e)
        elif isinstance(e, (list, tuple)):
            result += list(e)
    return result


def ensure_full_url(url):
    """
    """
    u = urlparse.urlparse(url)
    if u.scheme or u.path.startswith('/'):
        # absolute URL or a URL starting at root
        return url
    else:
        return urlparse.urljoin('/static/', url)


PLUGINS_CSS = _flat_list_from_plugin_config('css')
PLUGINS_CSS = map(ensure_full_url, PLUGINS_CSS)

PLUGINS_JS  = _flat_list_from_plugin_config('js')
PLUGINS_JS  = map(ensure_full_url, PLUGINS_JS)

