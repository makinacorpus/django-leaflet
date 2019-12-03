# Copyright (c) Django Software Foundation and individual contributors.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     1. Redistributions of source code must retain the above copyright notice,
#        this list of conditions and the following disclaimer.
#
#     2. Redistributions in binary form must reproduce the above copyright
#        notice, this list of conditions and the following disclaimer in the
#        documentation and/or other materials provided with the distribution.
#
#     3. Neither the name of Django nor the names of its contributors may be
#        used to endorse or promote products derived from this software without
#        specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from __future__ import unicode_literals

import logging
import warnings
import json

from distutils.version import LooseVersion
from django import get_version
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.forms.widgets import Widget
from django.template import loader

try:
    import six
except ImportError:
    from django.utils import six

from django.utils import translation
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core import validators

try:
    from django.contrib.gis.geos import GEOSGeometry
except (ImportError, ImproperlyConfigured):
    from .nogeos import GEOSGeometry

try:
    from django.contrib.gis.geos import GEOSException
except (ImportError, ImproperlyConfigured):
    from .nogeos import GEOSException

try:
    from django.contrib.gis.gdal import OGRException
except (ImportError, ImproperlyConfigured):
    from .nogeos import OGRException

try:
    from django.contrib.gis.gdal import OGRGeomType
except (ImportError, ImproperlyConfigured):
    class OGRGeomType:
        """
        Encapsulate OGR Geometry Types.
        Taken from Django GitHub repository:
        https://github.com/django/django/commit/5411821e3b8d1427ee63a5914aed1088c04cc1ed
        """

        wkb25bit = -2147483648

        # Dictionary of acceptable OGRwkbGeometryType s and their string names.
        _types = {0: 'Unknown',
                  1: 'Point',
                  2: 'LineString',
                  3: 'Polygon',
                  4: 'MultiPoint',
                  5: 'MultiLineString',
                  6: 'MultiPolygon',
                  7: 'GeometryCollection',
                  100: 'None',
                  101: 'LinearRing',
                  102: 'PointZ',
                  1 + wkb25bit: 'Point25D',
                  2 + wkb25bit: 'LineString25D',
                  3 + wkb25bit: 'Polygon25D',
                  4 + wkb25bit: 'MultiPoint25D',
                  5 + wkb25bit: 'MultiLineString25D',
                  6 + wkb25bit: 'MultiPolygon25D',
                  7 + wkb25bit: 'GeometryCollection25D',
                  }
        # Reverse type dictionary, keyed by lower-case of the name.
        _str_types = {v.lower(): k for k, v in _types.items()}

        def __init__(self, type_input):
            "Figure out the correct OGR Type based upon the input."
            if isinstance(type_input, OGRGeomType):
                num = type_input.num
            elif isinstance(type_input, str):
                type_input = type_input.lower()
                if type_input == 'geometry':
                    type_input = 'unknown'
                num = self._str_types.get(type_input)
                if num is None:
                    raise GEOSException('Invalid OGR String Type "%s"' % type_input)
            elif isinstance(type_input, int):
                if type_input not in self._types:
                    raise GEOSException('Invalid OGR Integer Type: %d' % type_input)
                num = type_input
            else:
                raise TypeError('Invalid OGR input type given.')

                # Setting the OGR geometry type number.
            self.num = num

        def __str__(self):
            "Return the value of the name property."
            return self.name

        def __eq__(self, other):
            """
            Do an equivalence test on the OGR type with the given
            other OGRGeomType, the short-hand string, or the integer.
            """
            if isinstance(other, OGRGeomType):
                return self.num == other.num
            elif isinstance(other, str):
                return self.name.lower() == other.lower()
            elif isinstance(other, int):
                return self.num == other
            else:
                return False

        @property
        def name(self):
            "Return a short-hand string form of the OGR Geometry type."
            return self._types[self.num]

        @property
        def django(self):
            "Return the Django GeometryField for this OGR Type."
            s = self.name.replace('25D', '')
            if s in ('LinearRing', 'None'):
                return None
            elif s == 'Unknown':
                s = 'Geometry'
            elif s == 'PointZ':
                s = 'Point'
            return s + 'Field'

        def to_multi(self):
            """
            Transform Point, LineString, Polygon, and their 25D equivalents
            to their Multi... counterpart.
            """
            if self.name.startswith(('Point', 'LineString', 'Polygon')):
                self.num += 3

logger = logging.getLogger('django.contrib.gis')


class BaseGeometryWidget(Widget):
    """
    The base class for rich geometry widgets.
    Render a map using the WKT of the geometry.
    Adapted from:
    https://github.com/django/django/commit/a7975260b50282b934c78c8e51846d103636ba04
    """
    geom_type = 'GEOMETRY'
    map_srid = 4326
    map_width = 600
    map_height = 400
    display_raw = False

    supports_3d = False
    template_name = ''  # set on subclasses

    def __init__(self, attrs=None):
        self.attrs = {}
        for key in ('geom_type', 'map_srid', 'map_width', 'map_height', 'display_raw'):
            self.attrs[key] = getattr(self, key)
        if attrs:
            self.attrs.update(attrs)

    def serialize(self, value):
        return value.wkt if value else ''

    def deserialize(self, value):
        try:
            # To allow older versions of django-leaflet to work,
            # self.map_srid is also returned (unlike the imported Django class)
            return GEOSGeometry(value, self.map_srid)
        except (GEOSException, ValueError) as err:
            logger.error("Error creating geometry from value '%s' (%s)", value, err)
        return None

    if LooseVersion(get_version()) >= LooseVersion('1.11'):
        def get_context(self, name, value, attrs):
            context = super().get_context(name, value, attrs)
            # If a string reaches here (via a validation error on another
            # field) then just reconstruct the Geometry.
            if value and isinstance(value, str):
                value = self.deserialize(value)

            if value:
                # Check that srid of value and map match
                if value.srid and value.srid != self.map_srid:
                    try:
                        ogr = value.ogr
                        ogr.transform(self.map_srid)
                        value = ogr
                    except OGRException as err:
                        logger.error(
                            "Error transforming geometry from srid '%s' to srid '%s' (%s)",
                            value.srid, self.map_srid, err
                        )

            if attrs is None:
                attrs = {}

            build_attrs_kwargs = {
                'name': name,
                'module': 'geodjango_%s' % name.replace('-', '_'),  # JS-safe
                'serialized': self.serialize(value),
                'geom_type': OGRGeomType(self.attrs['geom_type']),
                'STATIC_URL': settings.STATIC_URL,
                'LANGUAGE_BIDI': translation.get_language_bidi(),
            }
            build_attrs_kwargs.update(attrs)
            context.update(self.build_attrs(self.attrs, build_attrs_kwargs))
            return context
    else:
        def render(self, name, value, attrs=None):
            # If a string reaches here (via a validation error on another
            # field) then just reconstruct the Geometry.
            if isinstance(value, six.string_types):
                value = self.deserialize(value)

            if isinstance(value, dict):
                value = GEOSGeometry(json.dumps(value), srid=self.map_srid)

            if value:
                # Check that srid of value and map match
                if value.srid != self.map_srid:
                    try:
                        ogr = value.ogr
                        ogr.transform(self.map_srid)
                        value = ogr
                    except OGRException as err:
                        logger.error(
                            "Error transforming geometry from srid '%s' to srid "
                            "'%s' (%s)" % (value.srid, self.map_srid, err)
                        )

            context = self.build_attrs(
                attrs,
                name=name,
                module='geodjango_%s' % name.replace('-', '_'),  # JS-safe
                serialized=self.serialize(value),
                geom_type=OGRGeomType(self.attrs['geom_type']),
                STATIC_URL=settings.STATIC_URL,
                LANGUAGE_BIDI=translation.get_language_bidi(),
            )
            return loader.render_to_string(self.template_name, context)


class GeometryField(forms.Field):
    """
    This is the basic form field for a Geometry.  Any textual input that is
    accepted by GEOSGeometry is accepted by this form.  By default,
    this includes WKT, HEXEWKB, WKB (in a buffer), and GeoJSON.
    """
    geom_type = 'GEOMETRY'

    default_error_messages = {
        'required': _('No geometry value provided.'),
        'invalid_geom': _('Invalid geometry value.'),
        'invalid_geom_type': _('Invalid geometry type.'),
        'transform_error': _('An error occurred when transforming the geometry '
                             'to the SRID of the geometry form field.'),
    }

    def __init__(self, **kwargs):
        # Pop out attributes from the database field, or use sensible
        # defaults (e.g., allow None).
        self.srid = kwargs.pop('srid', None)
        self.geom_type = kwargs.pop('geom_type', self.geom_type)
        if 'null' in kwargs:
            kwargs.pop('null', True)
            warnings.warn("Passing 'null' keyword argument to GeometryField is"
                          "deprecated.", DeprecationWarning, stacklevel=2)
        super(GeometryField, self).__init__(**kwargs)
        self.widget.attrs['geom_type'] = self.geom_type

    def to_python(self, value):
        """
        Transforms the value to a Geometry object.
        """
        if value in validators.EMPTY_VALUES:
            return None

        if not isinstance(value, GEOSGeometry):
            try:
                value = GEOSGeometry(value)
            except (GEOSException, ValueError, TypeError):
                raise forms.ValidationError(self.error_messages['invalid_geom'], code='invalid_geom')

        # Try to set the srid
        if not value.srid:
            try:
                value.srid = self.widget.map_srid
            except AttributeError:
                if self.srid:
                    value.srid = self.srid
        return value

    def clean(self, value):
        """
        Validates that the input value can be converted to a Geometry
        object (which is returned).  A ValidationError is raised if
        the value cannot be instantiated as a Geometry.
        """
        geom = super(GeometryField, self).clean(value)
        if geom is None:
            return geom

        # Ensuring that the geometry is of the correct type (indicated
        # using the OGC string label).
        if str(geom.geom_type).upper() != self.geom_type and not self.geom_type == 'GEOMETRY':
            raise forms.ValidationError(self.error_messages['invalid_geom_type'], code='invalid_geom_type')

        # Transforming the geometry if the SRID was set.
        if self.srid and self.srid != -1 and self.srid != geom.srid:
            try:
                geom.transform(self.srid)
            except (GEOSException, ValueError, TypeError):
                raise forms.ValidationError(
                    self.error_messages['transform_error'], code='transform_error')

        return geom

    def _has_changed(self, initial, data):
        """ Compare geographic value of data with its initial value. """

        try:
            data = self.to_python(data)
            initial = self.to_python(initial)
        except forms.ValidationError:
            return True

        # Only do a geographic comparison if both values are available
        if initial and data:
            data.transform(initial.srid)
            # If the initial value was not added by the browser, the geometry
            # provided may be slightly different, the first time it is saved.
            # The comparison is done with a very low tolerance.
            return not initial.equals_exact(data, tolerance=0.000001)
        else:
            # Check for change of state of existence
            return bool(initial) != bool(data)
