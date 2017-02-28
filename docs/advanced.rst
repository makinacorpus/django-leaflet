Advanced usage
==============


``{% leaflet_map %}`` tag parameters
------------------------------------

* ``callback``: javascript function name for initialization callback.
  (Default: None).

* ``fitextent``: control if map initial view shoud be set to extent setting.
  (Default: ``True``). Setting fixextent to ``False`` will prevent view reset
  and scale controls to be added.

* ``creatediv``: control if the leaflet map tags creates a new div or not.
  (Default: ``True``).
  Useful to put the javascript code in the header or footer instead of the
  body of the html document. If used, do not forget to create the div manually.

* ``loadevent``: One or more space-separated *window* events that trigger map initialization.
  (Default: ``load``, i.e. all page resources loaded).
  If empty values is provided, then map initialization is immediate.
  And with a wrong value, the map is never initialized. :)

* ``settings_overrides``: Map with overrides to the default LEAFLET_CONFIG settings.
  (Default: {}).

Config overrides
----------------

It is possible to dynamically override settings in ``LeafletWidget`` init:

::

    from leaflet.forms.widgets import LeafletWidget


    class WeatherStationForm(forms.ModelForm):

        class Meta:
            model = WeatherStation
            fields = ('name', 'geom')
            widgets = {'geom': LeafletWidget(attrs={
                'settings_overrides': {
                    'DEFAULT_CENTER': (6.0, 45.0),
                }
            })}

For overriding the settings in ``LeafletGeoAdmin``, use set the appropriate property:

::

    class WeatherStationAdminAdmin(LeafletGeoAdmin):
        settings_overrides = {
           'DEFAULT_CENTER': (6.0, 45.0),
        }


Projection
----------

It is possible to setup the map spatial reference in ``LEAFLET_CONFIG``::

    'SRID': 2154  # See http://spatialreference.org

Additional parameter is required to compute scale levels : the tiles extent in
local projection::

    'TILES_EXTENT': [924861,6375196,985649,6448688],

For more information, `have a look at this example <http://blog.mathieu-leplatre.info/leaflet-tiles-in-lambert-93-projection-2154.html>`_.

Example of TileCache configuration compatible with Leaflet:

::

    [scan-portrait]
    type=WMSLayer
    layers=scan100,scan25
    url=http://server/wms?
    extension=jpg
    tms_type=google
    srs=EPSG:2154
    bbox=924861,6375196,985649,6448688

    [cache]
    type=GoogleDisk
    expire=2592000
    base=/tmp/tiles


By default, *django-leaflet* will try to load the spatial reference from your static
files at "proj4js/{{ srid }}.js". If it fails, it will eventually rely on
`<spatialreference.org>`_.