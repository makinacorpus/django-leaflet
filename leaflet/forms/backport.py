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

from django.conf import settings
from django.contrib.gis import gdal
from django.forms.widgets import Widget
from django.template import loader
from django.utils import six
from django.utils import translation
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.core import validators

try:
    from django.contrib.gis.geos import GEOSGeometry
except ImportError:
    from .nogeos import GEOSGeometry

try:
    from django.contrib.gis.geos import GEOSException
except ImportError:
    from .nogeos import GEOSException

logger = logging.getLogger('django.contrib.gis')


class BaseGeometryWidget(Widget):
    """
    The base class for rich geometry widgets.
    Renders a map using the WKT of the geometry.
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
            return GEOSGeometry(value, self.map_srid)
        except (GEOSException, ValueError) as err:
            logger.error(
                "Error creating geometry from value '%s' (%s)" % (value, err)
            )
        return None

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
                except gdal.OGRException as err:
                    logger.error(
                        "Error transforming geometry from srid '%s' to srid "
                        "'%s' (%s)" % (value.srid, self.map_srid, err)
                    )

        context = self.build_attrs(
            attrs,
            name=name,
            module='geodjango_%s' % name.replace('-', '_'),  # JS-safe
            serialized=self.serialize(value),
            geom_type=gdal.OGRGeomType(self.attrs['geom_type']),
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
            except:
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
