# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json

import django
from django.contrib.staticfiles.storage import StaticFilesStorage, staticfiles_storage
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.test import SimpleTestCase
from django.contrib.admin import ModelAdmin, StackedInline
from django.contrib.admin.options import BaseModelAdmin, InlineModelAdmin
from django.contrib.gis.db import models as gismodels

from .. import PLUGINS, PLUGIN_FORMS, _normalize_plugins_config, JSONLazyTranslationEncoder
from django.utils import six
from django.utils.translation import ugettext_lazy
from ..templatetags import leaflet_tags
from ..admin import LeafletGeoAdmin, LeafletGeoAdminMixin
from ..forms.widgets import LeafletWidget
from ..forms import fields


class DummyStaticFilesStorage(StaticFilesStorage):

    def url(self, name):
        raise ValueError


class AppLoadingTest(SimpleTestCase):

    def test_init_with_non_default_staticfiles_storage(self):
        """
        Non-default STATICFILES_STORAGE (ex. django.contrib.staticfiles.storage.ManifestStaticFilesStorage)
        might raise ValueError when file could not be found by this storage and DEBUG is set to False.

        Ensure that _normalize_plugins_config calls `static` lazily, in order to let the `collectstatic` command to run.

        """

        try:
            with self.settings(STATICFILES_STORAGE='leaflet.tests.tests.DummyStaticFilesStorage',
                               STATIC_ROOT="/", DEBUG=False):
                staticfiles_storage._setup()  # reset already initialized (and memoized) default STATICFILES_STORAGE

                with self.assertRaises(ValueError):
                    # Ensure that our DummyStaticFilesStorage is unable to process `static` calls right now
                    static("a")

                PLUGINS.update({
                    'a': {'css': 'a'},
                })

                PLUGINS.pop('__is_normalized__')
                # This would raise if `static` calls are not lazy
                _normalize_plugins_config()
        finally:
            # Reset the STATICFILES_STORAGE to a default one
            staticfiles_storage._setup()
            _normalize_plugins_config()


class PluginListingTest(SimpleTestCase):

    def test_default_resources(self):
        PLUGINS.update({
            'a': {'css': 'a'},
            'b': {'css': 'b', 'auto-include': True},
            'c': {'css': 'c'},
        })
        PLUGINS.pop('__is_normalized__')
        _normalize_plugins_config()

        names = leaflet_tags._get_plugin_names(None)
        resources = leaflet_tags._get_all_resources_for_plugins(names, 'css')
        self.assertEquals(['/static/b'], resources)

    def test_all_resources(self):
        PLUGINS.update({
            'a': {'css': 'a'},
            'b': {'css': 'b'},
            'c': {'css': 'c'},
        })
        PLUGINS.pop('ALL')
        PLUGINS.pop(PLUGIN_FORMS)
        PLUGINS.pop('__is_normalized__')
        _normalize_plugins_config()

        names = leaflet_tags._get_plugin_names('ALL')
        resources = leaflet_tags._get_all_resources_for_plugins(names, 'css')
        self.assertEquals(['/static/a', '/static/b', '/static/c'],
                          sorted(resources))

    def test_explicit_resources(self):
        PLUGINS.update({
            'a': {'css': 'a'},
            'b': {'css': 'b'},
            'c': {'css': 'c'},
        })
        PLUGINS.pop('__is_normalized__')
        _normalize_plugins_config()

        names = leaflet_tags._get_plugin_names('a,c')
        resources = leaflet_tags._get_all_resources_for_plugins(names, 'css')
        self.assertEquals(['/static/a', '/static/c'], sorted(resources))


class TemplateTagTest(SimpleTestCase):

    def test_default_layer_in_leaflet_map(self):
        context = leaflet_tags.leaflet_map('map')
        self.assertEquals('map', context['name'])
        self.assertTrue('"OSM", "//{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"' in
                        context['djoptions'])


class LeafletWidgetRenderingTest(SimpleTestCase):
    def test_default_media(self):
        widget = LeafletWidget()
        media = widget.media
        self.assertEquals([], media.render_js())
        self.assertEquals([], list(media.render_css()))

    def test_included_media(self):
        class LeafletWidgetMedia(LeafletWidget):
            include_media = True

        widget = LeafletWidgetMedia()
        media = widget.media
        media_js = "".join(media.render_js())
        media_css = "".join(media.render_css())
        self.assertIn('leaflet/leaflet.js', media_js)
        self.assertIn('leaflet/leaflet.extras.js', media_js)
        self.assertIn('leaflet/leaflet.forms.js', media_js)
        self.assertIn('leaflet/draw/leaflet.draw.js', media_js)

        self.assertIn('leaflet/leaflet.css', media_css)
        self.assertIn('leaflet/draw/leaflet.draw.css', media_css)

    def test_widget_geometry_is_empty_string(self):
        widget = LeafletWidget()
        widget.render('geom', '', {'id': 'geom'})
        self.assertTrue(True, 'We should\'t accept blank geometry in value.')


class LeafletFieldsWidgetsTest(SimpleTestCase):
    def test_default_widget(self):
        for typ in ['Geometry', 'Point', 'MultiPoint', 'LineString', 'Polygon',
                    'MultiLineString', 'MultiPolygon', 'GeometryCollection']:
            f = getattr(fields, typ + 'Field')()
            self.assertTrue(isinstance(f.widget, LeafletWidget))
            self.assertEquals(f.widget.geom_type, typ.upper())


class DummyAdminSite(object):
    """
    Mock adminsite, which is required by InlineModelAdmin.__init__
    """

    def is_registered(self, model):
        return True


class DummyModel(gismodels.Model):
    geom = gismodels.PointField()

    class Meta:
        app_label = "leaflet"


class DummyInlineModel(gismodels.Model):
    geom = gismodels.PointField()

    class Meta:
        app_label = "leaflet"


class BaseLeafletGeoAdminTest(object):
    modeladmin_class = None  # type: BaseModelAdmin
    leafletgeoadmin_class = None  # type: LeafletGeoAdmin

    def setUp(self):
        self.modeladmin = self.leafletgeoadmin_class(DummyModel, DummyAdminSite())
        self.geomfield = DummyModel._meta.get_field('geom')
        self.formfield = self.modeladmin.formfield_for_dbfield(self.geomfield)

    def test_widget_for_field(self):
        widget = self.formfield.widget
        self.assertTrue(issubclass(widget.__class__, LeafletWidget))

    def test_widget_parameters(self):
        widget = self.formfield.widget
        self.assertEquals(widget.geom_type, 'POINT')
        self.assertEquals(widget.settings_overrides, {'DEFAULT_CENTER': (8.0, 3.15), })
        self.assertFalse(widget.map_height is None)
        self.assertFalse(widget.map_width is None)
        self.assertTrue(widget.modifiable)

    def test_widget_media(self):
        widget = self.formfield.widget
        media = widget.media
        media_js = "".join(media.render_js())
        media_css = "".join(media.render_css())
        self.assertIn('leaflet/leaflet.js', media_js)
        self.assertIn('leaflet/leaflet.extras.js', media_js)
        self.assertIn('leaflet/leaflet.forms.js', media_js)
        self.assertIn('leaflet/draw/leaflet.draw.js', media_js)

        self.assertIn('leaflet/leaflet.css', media_css)
        self.assertIn('leaflet/draw/leaflet.draw.css', media_css)

    def test_is_subclass_of_modeladmin(self):
        self.assertTrue(issubclass(self.leafletgeoadmin_class, self.modeladmin_class))


class DummyAdminSettingsOverridesMixin(object):
    settings_overrides = {
        'DEFAULT_CENTER': (8.0, 3.15),
    }


class DummyMixinModelAdmin(DummyAdminSettingsOverridesMixin, LeafletGeoAdminMixin, ModelAdmin):
    pass


class LeafletGeoAdminMixinTest(BaseLeafletGeoAdminTest, SimpleTestCase):
    modeladmin_class = ModelAdmin
    leafletgeoadmin_class = DummyMixinModelAdmin

    def test_is_not_subclass_of_modeladmin(self):
        self.assertFalse(issubclass(LeafletGeoAdminMixin, BaseModelAdmin))


class DummyModelAdmin(DummyAdminSettingsOverridesMixin, LeafletGeoAdmin):
    pass


class LeafletGeoAdminTest(BaseLeafletGeoAdminTest, SimpleTestCase):
    modeladmin_class = ModelAdmin
    leafletgeoadmin_class = DummyModelAdmin


class DummyMixinStackedInline(DummyAdminSettingsOverridesMixin, LeafletGeoAdminMixin, StackedInline):
    model = DummyInlineModel


class LeafletGeoAdminStackedInlineTest(BaseLeafletGeoAdminTest, SimpleTestCase):
    modeladmin_class = InlineModelAdmin
    leafletgeoadmin_class = DummyMixinStackedInline


class LeafletWidgetMapTest(SimpleTestCase):

    def test_default_parameters(self):
        widget = LeafletWidget()
        output = widget.render('geom', '', {'id': 'geom'})
        self.assertIn(".fieldid = 'geom'", output)
        self.assertIn(".srid = 4326", output)
        self.assertIn(".geom_type = 'Geometry'", output)
        self.assertIn('#geom { display: none; }', output)
        self.assertIn('function geom_map_callback(map, options)', output)

    def test_overriden_parameters(self):
        class PolygonWidget(LeafletWidget):
            geom_type = 'POLYGON'
        widget = PolygonWidget()
        output = widget.render('geometry', '', {'id': 'geometry'})
        self.assertIn(".fieldid = 'geometry'", output)
        self.assertIn(".geom_type = 'Polygon'", output)
        self.assertIn('#geometry { display: none; }', output)
        self.assertIn('function geometry_map_callback(map, options)', output)

    def test_javascript_safe_callback_name(self):
        widget = LeafletWidget()
        output = widget.render('prefix-geom', '')
        self.assertIn('function prefix_geom_map_callback(map, options)', output)
        output = widget.render('geom', '', {'id': 'prefix-geom'})
        self.assertIn('function prefix_geom_map_callback(map, options)', output)


class SettingsOverridesTest(SimpleTestCase):

    def test_settings_overrides(self):
        widget = LeafletWidget(attrs={
            'settings_overrides': {
                'DEFAULT_CENTER': (8.0, 3.14),
            }
        })
        output = widget.render('geom', '', {'id': 'geom'})
        self.assertIn('"center": [8.0, 3.14]', output)

    def test_spatial_extent_settings_overrides(self):
        widget = LeafletWidget(attrs={
            'settings_overrides': {
                'SPATIAL_EXTENT': (
                    3.812255859375,
                    50.387507803003146,
                    4.0869140625,
                    50.523904629228625,
                ),
                'DEFAULT_ZOOM': None,
                'DEFAULT_CENTER': None,
            }
        })
        output = widget.render('geom', '', {'id': 'geom'})
        self.assertIn('"extent": [[50.387507803003146, 3.812255859375], [50.523904629228625, 4.0869140625]]', output)
        self.assertIn('"center": null', output)
        self.assertIn('"zoom": null', output)


class LeafletModelFormTest(SimpleTestCase):

    def test_modelform_field_conformity(self):
        class DummyForm(django.forms.ModelForm):
            geom = fields.PointField()

            class Meta:
                model = DummyModel
                fields = ['geom']

        form = DummyForm()
        output = form.as_p()
        self.assertIn(".geom_type = 'Point'", output)

    if django.VERSION >= (1, 6, 0):
        def test_modelform_widget_conformity(self):
            class DummyForm(django.forms.ModelForm):
                class Meta:
                    model = DummyModel
                    fields = ['geom']
                    widgets = {'geom': LeafletWidget()}
            form = DummyForm()
            output = form.as_p()
            self.assertIn(".geom_type = 'Point'", output)


class LeafletGeoAdminMapTest(LeafletGeoAdminTest):

    def test_widget_template_overriden(self):
        widget = self.formfield.widget
        output = widget.render('geom', '', {'id': 'geom'})
        self.assertIn(".module .leaflet-draw ul", output)
        self.assertIn('<div id="geom-div-map">', output)


class JSONLazyTranslationEncoderTest(SimpleTestCase):

    def test_lazy_translation_encoding(self):
        text = ugettext_lazy('text')
        ret = json.dumps(text, cls=JSONLazyTranslationEncoder)
        self.assertIsInstance(ret, six.string_types)
        self.assertEqual(ret, '"text"')
