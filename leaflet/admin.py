from django.contrib.admin import ModelAdmin
from django.core.exceptions import ImproperlyConfigured

try:
    from djgeojson.fields import GeoJSONField
except ImportError:
    GeoJSONField = type(object)
try:
    from django.contrib.gis.db.models import GeometryField
except (ImportError, ImproperlyConfigured):
    # When GEOS is not installed
    GeometryField = type(object)

from .forms.widgets import LeafletWidget


class LeafletGeoAdminMixin:
    widget = LeafletWidget
    map_template = 'leaflet/admin/widget.html'
    modifiable = True
    map_width = 'min(calc(100vw - 30px), 720px)'
    map_height = '400px'
    display_raw = False
    settings_overrides = {}

    def formfield_for_dbfield(self, db_field, request=None, **kwargs):
        """
        Overloaded from ModelAdmin to set Leaflet widget
        in form field init params.
        """
        is_geometry = isinstance(db_field, (GeometryField, GeoJSONField))
        is_editable = is_geometry and (db_field.dim < 3 or
                                       self.widget.supports_3d)

        if is_editable:
            # Setting the widget with the newly defined widget.
            widget = self.widget
            if 'widget' in kwargs and issubclass(kwargs['widget'], LeafletWidget):
                # If the widget is already a LeafletWidget of some kind
                # Then use it rather than a blank one.
                widget = kwargs['widget']

            kwargs['widget'] = self._get_map_widget(db_field, widget)
            return db_field.formfield(**kwargs)
        else:
            return super().formfield_for_dbfield(db_field, request, **kwargs)

    def _get_map_widget(self, db_field, widget):
        """
        Overriden LeafletWidget with LeafletGeoAdmin params.
        """
        class LeafletMap(widget):
            template_name = self.map_template
            include_media = True
            geom_type = db_field.geom_type
            modifiable = self.modifiable
            map_width = self.map_width
            map_height = self.map_height
            display_raw = self.display_raw
            settings_overrides = self.settings_overrides
        return LeafletMap


class LeafletGeoAdmin(LeafletGeoAdminMixin, ModelAdmin):
    pass
