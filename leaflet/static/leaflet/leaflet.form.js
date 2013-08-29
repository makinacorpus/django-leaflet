L.FieldStore = L.Class.extend({
    initialize: function (id, options) {
        this.formfield = document.getElementById(id);
        L.setOptions(this, options);

        this.prefix = 'SRID=' + this.options.srid + ';';
    },

    load: function () {
        var wkt = new Wkt.Wkt();
        try {
            var value = (this.formfield.value || '').replace(this.prefix, '');
            if (value) {
                wkt.read(value);
                return wkt.toObject(this.options.defaults);
            }
        } catch (e) {  // Ignore empty or malformed WKT strings
        }
        return null;
    },

    save: function (layer) {
        var items = layer.getLayers(),
            is_empty = items.length === 0,
            is_multi = this.options.is_collection || items.length > 1,
            wkt = new Wkt.Wkt();

        if (!is_empty) {
            wkt.fromObject((is_multi ? layer : items[0]));
            this.formfield.value = this.prefix + wkt.write();
        }
        else {
            this.formfield.value = '';
        }
    }
});


L.GeometryField = L.Class.extend({
    statics: {
        unsavedText: 'Map geometry is unsaved'
    },

    options: {
        field_store_class: L.FieldStore
    },

    initialize: function (options) {
        L.setOptions(this, options);

        this._unsavedChanges = false;

        // Warn if leaving with unsaved changes
        var _beforeunload = window.onbeforeunload;
        window.onbeforeunload = L.Util.bind(function(e) {
            if (this._unsavedChanges)
                return L.GeometryField.unsavedText;
            if (typeof(_beforeunload) == 'function')
                return _beforeunload();
            return null;
        }, this);
    },

    addTo: function (map) {
        this._map = map;

        var store_opts = L.Util.extend(this.options, {defaults: map.defaults});
        this.store = new this.options.field_store_class(this.options.id, store_opts);

        this.drawnItems = new L.FeatureGroup();
        map.addLayer(this.drawnItems);

        // Initialize the draw control and pass it the FeatureGroup of editable layers
        var drawControl = new L.Control.Draw({
            edit: {
                featureGroup: this.drawnItems
            },
            draw: {
                polyline: this.options.is_linestring,
                polygon: this.options.is_polygon,
                circle: false, // Turns off this drawing tool
                rectangle: this.options.is_polygon,
                marker: this.options.is_point,
            }
        });

        if (this.options.modifiable) {
            map.addControl(drawControl);

            map.on('draw:created', this.onCreated, this);
            map.on('draw:edited', this.onEdited, this);
            map.on('draw:deleted', this.onDeleted, this);

            // Flag for unsaved changes
            map.on('draw:drawstart draw:editstart', function () {
                this._unsavedChanges = true;
            }, this);
            map.on('draw:drawstop draw:editstop', function () {
                this._unsavedChanges = false;
            }, this);
        }

        this.load();
    },

    load: function () {
        var geometry = this.store.load();
        if (geometry) {
            // Add initial geometry to the map
            geometry.addTo(this._map);
            this.drawnItems.addLayer(geometry);

            // And fit view extent.
            if (typeof(geometry.getBounds) == 'function') {
                this._map.fitBounds(geometry.getBounds());
            }
            else {
                this._map.panTo(geometry.getLatLng());
                this._map.setZoom(module.default_zoom);
            }
        }
    },

    onCreated: function (e) {
        var layer = e.layer;
        this._map.addLayer(layer);
        this.drawnItems.addLayer(layer);
        this.store.save(this.drawnItems);
    },

    onEdited: function (e) {
        this.store.save(this.drawnItems);
    },

    onDeleted: function (e) {
        var layer = e.layer;
        this.drawnItems.removeLayer(layer);
        this.store.save(this.drawnItems);
    }
});
