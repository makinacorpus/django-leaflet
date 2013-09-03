import django

if django.VERSION >= (1, 6, 0):
    from django.contrib.gis.forms.fields import GeometryField
else:
    from django.contrib.gis.forms.fields import GeometryField as BaseField

    class GeometryField(BaseField):
        geom_type = 'GEOMETRY'

        def __init__(self, *args, **kwargs):
            kwargs['geom_type'] = self.geom_type
            super(GeometryField, self).__init__(*args, **kwargs)
            self.widget.attrs['geom_type'] = self.geom_type


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
