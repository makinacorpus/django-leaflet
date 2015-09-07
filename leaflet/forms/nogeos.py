# -*- coding: utf-8 -*-


class GEOSGeometry(object):
    """
    A simple mock of django.contrib.gis.geos.GEOSGeometry to make
    django-leaflet work with only django-geojson (without libgeos)
    """
    def __init__(self, geo_input, srid=None):
        self.srid = srid
        self.geojson = geo_input
        return


class GEOSException(Exception):
    pass
