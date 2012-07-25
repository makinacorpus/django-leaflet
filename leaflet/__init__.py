from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.translation import ugettext_lazy as _


app_settings = dict({
    'LEAFLET_VERSION': "",
    'TILES_URL': None,
    'SPATIAL_EXTENT': None,
}, **getattr(settings, 'LEAFLET_CONFIG', {}))


SPATIAL_EXTENT = app_settings.get("SPATIAL_EXTENT")
if SPATIAL_EXTENT is None:
    SPATIAL_EXTENT = getattr(settings, 'SPATIAL_EXTENT')
if SPATIAL_EXTENT is not None:
    if not isinstance(SPATIAL_EXTENT, tuple) or len(SPATIAL_EXTENT) != 4:
        raise ImproperlyConfigured(_("Spatial extent should be a tuple (minx, miny, maxx, maxy)"))
