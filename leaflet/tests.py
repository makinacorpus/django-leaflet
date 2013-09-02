from django.test import SimpleTestCase

from . import PLUGINS, PLUGIN_FORMS, _normalize_plugins_config
from .templatetags import leaflet_tags
from .forms.widgets import LeafletWidget
from .forms import fields


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
        self.assertEquals(['b'], resources)

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
        self.assertEquals(['a', 'b', 'c'], sorted(resources))

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
        self.assertEquals(['a', 'c'], sorted(resources))


class LeafletWidgetRenderingTest(SimpleTestCase):
    def test_default_media(self):
        widget = LeafletWidget()
        media = widget.media
        self.assertEquals([], media.render_js())
        self.assertEquals([], list(media.render_css()))

    def test_admin_media(self):
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


class LeafletFieldsWidgetsTest(SimpleTestCase):
    def test_default_widget(self):
        for typ in ['Geometry', 'Point', 'MultiPoint', 'LineString', 'Polygon', 
                    'MultiLineString', 'MultiPolygon']:
            f = getattr(fields, typ + 'Field')()
        self.assertEquals(f.widget.attrs['geom_type'], typ.upper())
