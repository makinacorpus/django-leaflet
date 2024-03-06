(function () {
    let djoptions = JSON.parse(document.getElementById("leaflet-djoptions").textContent);
    let globals = !JSON.parse(document.getElementById("leaflet-no-globals").textContent);
    let callback = JSON.parse(document.getElementById("leaflet-callback").textContent);
    let name = JSON.parse(document.getElementById("leaflet-name").textContent);

    function loadmap() {
        if (callback === null) {
            callback = "null";
        }
        options = {
            djoptions: djoptions,
            initfunc: loadmap,
            globals: globals, callback: callback
        },
        map = L.Map.djangoMap(name, options);
        if (globals) {
            window[`leafletmap${name}`] = map;
        }
    }
    let loadevents = JSON.parse(document.getElementById("leaflet-loadevents").textContent);
    if (loadevents.length === 0) loadmap();
    else if (window.addEventListener) for (var i=0; i<loadevents.length; i++) window.addEventListener(loadevents[i], loadmap, false);
    else if (window.jQuery) jQuery(window).on(loadevents.join(' '), loadmap);
    if (globals) {
        // Put initialization function in global scope (like django-leaflet < 0.7)
        window[`loadmap${name}`] = loadmap;
    }
})();
