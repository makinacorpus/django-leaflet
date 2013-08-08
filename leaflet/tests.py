from django.test import SimpleTestCase

from leaflet import PLUGINS, _normalize_plugins_config
from leaflet.templatetags import leaflet_tags


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
