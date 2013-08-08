L.Control.ResetView = L.Control.extend({
    statics: {
        ICON: 'url(images/reset-view.png)',
        TITLE: "Reset view",
    },

    options: {
        position: 'topleft'
    },

    initialize: function (bounds, options) {
        // Accept function as argument to bounds
        this.getBounds = typeof(bounds) == 'function' ? bounds :
                                                        function() { return bounds; };

        L.Util.setOptions(this, options);
    },

    onAdd: function (map) {
        if (map.resetviewControl) {
            map.removeControl(map.resetviewControl);
        }
        map.resetviewControl = this;

        var container = L.DomUtil.create('div', 'leaflet-control-zoom');
        var link = L.DomUtil.create('a', 'leaflet-control-zoom-out leaflet-bar leaflet-bar-part', container);
        link.href = '#';
        link.title = L.Control.ResetView.TITLE;
        link.style.backgroundImage = L.Control.ResetView.ICON;

        L.DomEvent.addListener(link, 'click', L.DomEvent.stopPropagation)
                  .addListener(link, 'click', L.DomEvent.preventDefault)
                  .addListener(link, 'click', L.Util.bind(function() {
                      map.fitBounds(this.getBounds());
                   }, this));
        return container;
    }
});


L.Map.DjangoMap = L.Map.extend({

    initialize: function (id, options) {
        // Merge compatible options
        // (can be undefined)
        var djoptions = options.djoptions;
        options.zoom = djoptions.zoom;
        options.center = djoptions.center;
        options.maxBounds = djoptions.extent;

        // Translate SRID to native options
        options = L.Util.extend(options,
                                this._projectionOptions(djoptions));

        L.Map.prototype.initialize.apply(this, arguments);

        this._addLayers();
        this._addControls();

        if (djoptions.fitextent && djoptions.extent &&
            !(djoptions.center || djoptions.zoom)) {
            map.fitBounds(djoptions.extent);
        }
    },

    _projectionOptions: function (djoptions) {
        if (!djoptions.srid)
            return {};

        var projopts = {};

        var bbox = djoptions.tileextent,
            width = bbox[2] - bbox[0],
            height = bbox[3] - bbox[1],
            maxResolution = (djoptions.maxResolution || width / 256);

        var scale = function(zoom) {
            return 1 / (maxResolution / Math.pow(2, zoom));
        };
        var transformation = new L.Transformation(1, -bbox[0], -1, bbox[3]);
        var crs = L.Proj.CRS('EPSG:' + djoptions.srid,
                             Proj4js.defs[''+ djoptions.srid], transformation);
        crs.scale = scale;

        return {
            crs: crs,
            scale: scale,
            continuousWorld: true
        };
    },

    _addLayers: function (djoptions) {
        var layers = this.options.djoptions.layers;

        if (layers.length == 1) {
            var layer = l2d(layers[0]),
            L.tileLayer(layer.url, layer.options).addTo(map);
            return;
        }

        map.layerscontrol = L.control.layers().addTo(map);
        for (var i = 0, n = layers.length; i < n; i++) {
            var layer = l2d(layers[i])
                l = L.tileLayer(layer.url, layer.options);
            map.layerscontrol.addBaseLayer(l, layer.name);
            // Show first one as default
            if (i === 0) l.addTo(map);
        }

        function l2d(l) {
            var name = layer[0],
                url = layer[1],
                attribution = layer[2],
                options = {'attribution': attribution,
                           'continuousWorld': this.options.continuousWorld};
            return {name: name, url: url, options: options};
        }
    },

    _addControls: function () {
        // Scale control ?
        if (this.options.djoptions.scale) {
            map.whenReady(function () {
                new L.Control.Scale({imperial: false}).addTo(map);
            });
        }

        // Minimap control ?
        if (this.options.djoptions.minimap) {
            for (var firstLayer in this._layers) break;
            var url = this._layers[firstLayer]._url;
            var layer = L.tileLayer(url);
            map.whenReady(function () {
                map.minimapcontrol = new L.Control.MiniMap(layer,
                                                           {toggleDisplay: true}).addTo(map);
            });
        }

        // ResetView control ?
        if (this.options.djoptions.resetview) {
            var bounds = this.options.djoptions.extent;
            if (bounds) {
                // Add reset view control
                map.whenReady(function () {
                    new L.Control.ResetView(bounds).addTo(map);
                });
            }
        }
    }

});


L.Map.djangoMap = function () { return new L.Map.DjangoMap(arguments); };
