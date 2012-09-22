from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext as _


DEFAULT_TILES_URL = 'http://{s}.tiles.mapbox.com/v3/mapbox.mapbox-streets/{z}/{x}/{y}.png'

app_settings = dict({
    'LEAFLET_VERSION': "",
    'TILES_URL': DEFAULT_TILES_URL,
    'SPATIAL_EXTENT': None,
    'SRID': None,
    'SCALE': True,
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
