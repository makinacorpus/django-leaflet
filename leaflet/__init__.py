import urlparse
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext as _


DEFAULT_TILES_URL = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'

app_settings = dict({
    'TILES_URL': DEFAULT_TILES_URL,
    'SPATIAL_EXTENT': None,
    'DEFAULT_ZOOM': None,
    'DEFAULT_CENTER': None,
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

DEFAULT_CENTER = app_settings.get('DEFAULT_CENTER', None)
if DEFAULT_CENTER is not None and not (isinstance(DEFAULT_CENTER, (list,tuple)) and len(DEFAULT_CENTER) == 2):
    raise ImproperlyConfigured("LEAFLET_CONFIG['DEFAULT_CENTER'] must be an list/tuple with two elements - (lon, lat)")

DEFAULT_ZOOM = app_settings.get("DEFAULT_ZOOM", None)
if DEFAULT_ZOOM is not None and not (isinstance(DEFAULT_ZOOM, int) and (1 <= DEFAULT_ZOOM <= 24)):
    raise ImproperlyConfigured("LEAFLET_CONFIG['DEFAULT_ZOOM'] must be an int between 1 and 24.")


PLUGINS = app_settings.get("PLUGINS", None)
if PLUGINS is not None and not (isinstance(PLUGINS, dict) and all(map(lambda el: isinstance(el, dict), PLUGINS.itervalues()))):
    raise ImproperlyConfigured("LEAFLET_CONFIG['PLUGINS'] must be dict of dicts in the format { '[plugin_name]': { 'js': '[path-to-js]', 'css': '[path-to-css]' } } .")

PLUGIN_ALL = 'ALL'

# -----------------------

def _normalize_plugins_config():
    """
    Normalizes the PLUGINS setting:
        * ensures the 'css' and 'js' are arrays of URLs
        * ensures all URLs are transformed as follows:
            ** if the URL is absolute - leave it as-is
            ** if the URL is a root URL - starts with a / - leave it as-is
            ** the the URL is not a root URL - does not start with / - prepend settings.STATIC_URL
    Also, adds a special key - ALL - that includes 'css' and 'js' for all plugins listed
    """
    if '__is_normalized__' in PLUGINS: # already normalized
        return

    RESOURCE_TYPE_KEYS = ['css', 'js']
    PLUGINS[PLUGIN_ALL] = dict( (k, []) for k in RESOURCE_TYPE_KEYS)

    for plugin_dict in PLUGINS.itervalues():
        for resource_type in RESOURCE_TYPE_KEYS:
            # normalize the resource URLs
            urls = plugin_dict.get(resource_type, None)
            if isinstance(urls, (str, unicode)):
                urls = [urls]
            elif isinstance(urls, tuple): # force to list
                urls = list(urls)
            elif isinstance(urls, list): # already a list
                pass
            else: # css/js has not been specified or the wrong type
                urls = []

            # normalize the URLs - see the docstring for details
            for i, url in enumerate(urls):
                url_parts = urlparse.urlparse(url)
                if url_parts.scheme or url_parts.path.startswith('/'):
                    # absolute URL or a URL starting at root
                    pass
                else:
                    urls[i] = urlparse.urljoin(settings.STATIC_URL, url)

            plugin_dict[resource_type] = urls

            # also append it to the ALL pseudo-plugin;
            # PLUGINS[PLUGIN_ALL][resource_type] is known to be a list form the initialization above
            PLUGINS[PLUGIN_ALL][resource_type].extend(urls)

    PLUGINS['__is_normalized__'] = True

_normalize_plugins_config()

