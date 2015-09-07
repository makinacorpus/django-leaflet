var assert = chai.assert;


describe('Test Leaflet Extras', function() {

    describe('L.Control.ResetView', function() {

        var map,
            control,
            button;

        before(function() {
            map = L.map('map').fitWorld();

            control = new L.Control.ResetView(L.latLngBounds([[1, 1], [3, 3]]));
            control.addTo(map);

            button = control._container.getElementsByTagName('a')[0];
        });

        after(function() {
            map.removeControl(control);
            map.remove();
        });

        it("should reset view on button click", function(done) {
            var callback = sinon.spy();
            map.on('viewreset', callback);
            happen.click(button);
            assert.isTrue(callback.called);
            done();
        });

    });


    describe('L.Map.DjangoMap', function() {

        it("should not fail with minimal options", function(done) {
            var map = new L.Map.DjangoMap('map', {djoptions: {layers: []}});
            map.remove();
            done();
        });

    });
});
