/*


  Copyright (C) 2012 K. Arthur Endsley (kaendsle@mtu.edu)
  Michigan Tech Research Institute (MTRI)
  3600 Green Court, Suite 100, Ann Arbor, MI, 48105

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.

*/
Wkt.Wkt.prototype.isRectangle=false;Wkt.Wkt.prototype.trunc=function(coords){var i,verts=[];for(i=0;i<coords.length;i+=1)if(Wkt.isArray(coords[i]))verts.push(this.trunc(coords[i]));else if(i===0||!this.sameCoords(coords[0],coords[i]))verts.push(coords[i]);return verts};
Wkt.Wkt.prototype.construct={point:function(config,component){var coord=component||this.components;if(coord instanceof Array)coord=coord[0];return L.marker(this.coordsToLatLng(coord),config)},multipoint:function(config){var i,layers=[],coords=this.components;for(i=0;i<coords.length;i+=1)layers.push(this.construct.point.call(this,config,coords[i]));return L.featureGroup(layers,config)},linestring:function(config,component){var coords=component||this.components,latlngs=this.coordsToLatLngs(coords);
return L.polyline(latlngs,config)},multilinestring:function(config){var coords=this.components,latlngs=this.coordsToLatLngs(coords,1);return L.multiPolyline(latlngs,config)},polygon:function(config){var coords=this.trunc(this.components),latlngs=this.coordsToLatLngs(coords,1);return L.polygon(latlngs,config)},multipolygon:function(config){var coords=this.trunc(this.components),latlngs=this.coordsToLatLngs(coords,2);return L.multiPolygon(latlngs,config)},geometrycollection:function(config){var comps,
i,layers;comps=this.trunc(this.components);layers=[];for(i=0;i<this.components.length;i+=1)layers.push(this.construct[comps[i].type].call(this,comps[i]));return L.featureGroup(layers,config)}};L.Util.extend(Wkt.Wkt.prototype,{coordsToLatLngs:L.GeoJSON.coordsToLatLngs,coordsToLatLng:function(coords,reverse){var lat=reverse?coords.x:coords.y,lng=reverse?coords.y:coords.x;return L.latLng(lat,lng,true)}});
Wkt.Wkt.prototype.deconstruct=function(obj){var attr,coordsFromLatLngs,features,i,verts,rings,tmp;coordsFromLatLngs=function(arr){var i,coords;coords=[];for(i=0;i<arr.length;i+=1)if(Wkt.isArray(arr[i]))coords.push(coordsFromLatLngs(arr[i]));else coords.push({x:arr[i].lng,y:arr[i].lat});return coords};if(obj.constructor===L.Marker||obj.constructor===L.marker)return{type:"point",components:[{x:obj.getLatLng().lng,y:obj.getLatLng().lat}]};if(obj.constructor===L.Rectangle||obj.constructor===L.rectangle){tmp=
obj.getBounds();return{type:"polygon",isRectangle:true,components:[[{x:tmp.getSouthWest().lng,y:tmp.getNorthEast().lat},{x:tmp.getNorthEast().lng,y:tmp.getNorthEast().lat},{x:tmp.getNorthEast().lng,y:tmp.getSouthWest().lat},{x:tmp.getSouthWest().lng,y:tmp.getSouthWest().lat},{x:tmp.getSouthWest().lng,y:tmp.getNorthEast().lat}]]}}if(obj.constructor===L.Polyline||obj.constructor===L.polyline){verts=[];tmp=obj.getLatLngs();if(!tmp[0].equals(tmp[tmp.length-1])){for(i=0;i<tmp.length;i+=1)verts.push({x:tmp[i].lng,
y:tmp[i].lat});return{type:"linestring",components:verts}}}if(obj.constructor===L.Polygon||obj.constructor===L.polygon){rings=[];verts=[];tmp=obj.getLatLngs();for(i=0;i<obj._latlngs.length;i+=1)verts.push({x:tmp[i].lng,y:tmp[i].lat});verts.push({x:tmp[0].lng,y:tmp[0].lat});rings.push(verts);if(obj._holes&&obj._holes.length>0){verts=coordsFromLatLngs(obj._holes)[0];verts.push(verts[0]);rings.push(verts)}return{type:"polygon",components:rings}}if(obj.constructor===L.MultiPolyline||obj.constructor===
L.MultiPolygon||obj.constructor===L.LayerGroup||obj.constructor===L.FeatureGroup){features=[];tmp=obj._layers;for(attr in tmp)if(tmp.hasOwnProperty(attr))if(tmp[attr].getLatLngs||tmp[attr].getLatLng)features.push(this.deconstruct(tmp[attr]));return{type:function(){switch(obj.constructor){case L.MultiPolyline:return"multilinestring";case L.MultiPolygon:return"multipolygon";case L.FeatureGroup:return function(){var i,mpgon,mpline,mpoint;mpgon=true;mpline=true;mpoint=true;for(i in obj._layers)if(obj._layers.hasOwnProperty(i)){if(obj._layers[i].constructor!==
L.Marker)mpoint=false;if(obj._layers[i].constructor!==L.Polyline)mpline=false;if(obj._layers[i].constructor!==L.Polygon)mpgon=false}if(mpoint)return"multipoint";if(mpline)return"multilinestring";if(mpgon)return"multipolygon";return"geometrycollection"}();default:return"geometrycollection"}}(),components:function(){var i,comps;comps=[];for(i=0;i<features.length;i+=1)if(features[i].components)comps.push(features[i].components);return comps}()}}if(obj.constructor===L.Rectangle||obj.constructor===L.rectangle)console.log("Deconstruction of L.Circle objects is not yet supported");
else console.log("The passed object does not have any recognizable properties.")};
