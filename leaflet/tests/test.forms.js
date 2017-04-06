var assert = chai.assert;


describe('Test Leaflet Forms', function() {

    describe('L.FieldStore', function() {

        afterEach(function () {
            document.getElementById('formfield').value = '';
        });

        it("should serialize and store", function () {
            var store = new L.FieldStore("formfield", {
                collection_type: "featureGroup"
            });
            store.save(L.polyline([[1, 2], [3, 4]]));
            assert.equal(store.formfield.value, '{"type":"LineString","coordinates":[[2,1],[4,3]]}');
        });
    });


    describe('L.GeometryField', function() {

        it("should detect geometry type", function (done) {
            var field = new L.GeometryField({geom_type: 'GEOMETRY'});
            assert.isTrue(field.options.is_generic);
            field = new L.GeometryField({geom_type: 'POLYGON'});
            assert.isTrue(field.options.is_polygon);
            field = new L.GeometryField({geom_type: 'LINESTRING'});
            assert.isTrue(field.options.is_linestring);
            field = new L.GeometryField({geom_type: 'POINT'});
            assert.isTrue(field.options.is_point);
            done();
        });

        describe('Events', function () {

            var map;

            beforeEach(function () {
                map = L.map('map').fitWorld();
            });

            afterEach(function () {
                map.remove();
            });

            it("should emit event when field is loaded", function (done) {
                var field = new L.GeometryField({
                    geom_type: 'GEOMETRY',
                    modifiable: true,
                    fieldid: 'formfield'
                });
                map.on('map:loadfield', function (e) {
                    assert.equal(e.target, map);
                    assert.equal(e.field, field);
                    assert.equal(e.fieldid, 'formfield');
                    assert.isDefined(map.drawControlformfield);
                    done();
                });
                field.addTo(map);
            });
        });
    });
});
