try:
    from django.contrib.gis.forms.fields import GeometryField
except ImportError:
    from django.forms import Field as GeometryField

from .widgets import LeafletWidget


class LeafletGeometryField(GeometryField):
    widget = LeafletWidget
    geom_type = 'GEOMETRY'


class GeometryCollectionField(LeafletGeometryField):
    geom_type = 'GEOMETRYCOLLECTION'


class PointField(LeafletGeometryField):
    geom_type = 'POINT'


class MultiPointField(LeafletGeometryField):
    geom_type = 'MULTIPOINT'


class LineStringField(LeafletGeometryField):
    geom_type = 'LINESTRING'


class MultiLineStringField(LeafletGeometryField):
    geom_type = 'MULTILINESTRING'


class PolygonField(LeafletGeometryField):
    geom_type = 'POLYGON'


class MultiPolygonField(LeafletGeometryField):
    geom_type = 'MULTIPOLYGON'
