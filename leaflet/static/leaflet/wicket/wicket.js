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
var Wkt=function(){var beginsWith,endsWith;beginsWith=function(str,sub){return str.substring(0,sub.length)===sub};endsWith=function(str,sub){return str.substring(str.length-sub.length)===sub};return{delimiter:" ",isArray:function(obj){return!!(obj&&obj.constructor===Array)},trim:function(str,sub){sub=sub||" ";while(beginsWith(str,sub))str=str.substring(1);while(endsWith(str,sub))str=str.substring(0,str.length-1);return str},Wkt:function(initializer){this.delimiter=Wkt.delimiter;this.wrapVertices=
true;this.regExes={"typeStr":/^\s*(\w+)\s*\(\s*(.*)\s*\)\s*$/,"spaces":/\s+|\+/,"numeric":/-*\d+(\.*\d+)?/,"comma":/\s*,\s*/,"parenComma":/\)\s*,\s*\(/,"coord":/-*\d+\.*\d+ -*\d+\.*\d+/,"doubleParenComma":/\)\s*\)\s*,\s*\(\s*\(/,"trimParens":/^\s*\(?(.*?)\)?\s*$/};this.components=undefined;if(initializer&&typeof initializer==="string")this.read(initializer);else if(this.fromGeometry)this.fromGeometry(initializer)}}}();
Wkt.Wkt.prototype.isCollection=function(){switch(this.type.slice(0,5)){case "multi":return true;case "polyg":return true;default:return false}};Wkt.Wkt.prototype.sameCoords=function(a,b){return a.x===b.x&&a.y===b.y};Wkt.Wkt.prototype.fromObject=function(obj){var result=this.deconstruct.call(this,obj);this.components=result.components;this.isRectangle=result.isRectangle||false;this.type=result.type;return this};
Wkt.Wkt.prototype.toObject=function(config){return this.construct[this.type].call(this,config)};Wkt.Wkt.prototype.merge=function(wkt){if(this.type!==wkt.type)throw TypeError("The input geometry types must agree");this.components.concat(wkt.components);this.type="multi"+this.type};
Wkt.Wkt.prototype.read=function(wkt){var matches;matches=this.regExes.typeStr.exec(wkt);if(matches){this.type=matches[1].toLowerCase();this.base=matches[2];if(this.ingest[this.type])this.components=this.ingest[this.type].apply(this,[this.base])}else{console.log("Invalid WKT string provided to read()");throw{name:"WKTError",message:"Invalid WKT string provided to read()"};}return this.components};
Wkt.Wkt.prototype.write=function(components){var i,pieces,data;components=components||this.components;pieces=[];pieces.push(this.type.toUpperCase()+"(");for(i=0;i<components.length;i+=1){if(this.isCollection()&&i>0)pieces.push(",");if(!this.extract[this.type])return null;data=this.extract[this.type].apply(this,[components[i]]);if(this.isCollection()&&this.type!=="multipoint")pieces.push("("+data+")");else{pieces.push(data);if(i!==components.length-1&&this.type!=="multipoint")pieces.push(",")}}pieces.push(")");
return pieces.join("")};
Wkt.Wkt.prototype.extract={point:function(point){return point.x+this.delimiter+point.y},multipoint:function(multipoint){var i,parts=[],s;for(i=0;i<multipoint.length;i+=1){s=this.extract.point.apply(this,[multipoint[i]]);if(this.wrapVertices)s="("+s+")";parts.push(s)}return parts.join(",")},linestring:function(linestring){return this.extract.point.apply(this,[linestring])},multilinestring:function(multilinestring){var i,parts=[];for(i=0;i<multilinestring.length;i+=1)parts.push(this.extract.linestring.apply(this,[multilinestring[i]]));
return parts.join(",")},polygon:function(polygon){return this.extract.multilinestring.apply(this,[polygon])},multipolygon:function(multipolygon){var i,parts=[];for(i=0;i<multipolygon.length;i+=1)parts.push("("+this.extract.polygon.apply(this,[multipolygon[i]])+")");return parts.join(",")},geometrycollection:function(str){console.log("The geometrycollection WKT type is not yet supported.")}};
Wkt.Wkt.prototype.ingest={point:function(str){var coords=Wkt.trim(str).split(this.regExes.spaces);return[{x:parseFloat(this.regExes.numeric.exec(coords[0])[0]),y:parseFloat(this.regExes.numeric.exec(coords[1])[0])}]},multipoint:function(str){var i,components,points;components=[];points=Wkt.trim(str).split(this.regExes.comma);for(i=0;i<points.length;i+=1)components.push(this.ingest.point.apply(this,[points[i]]));return components},linestring:function(str){var i,multipoints,components;multipoints=this.ingest.multipoint.apply(this,
[str]);components=[];for(i=0;i<multipoints.length;i+=1)components=components.concat(multipoints[i]);return components},multilinestring:function(str){var i,components,line,lines;components=[];lines=Wkt.trim(str).split(this.regExes.doubleParenComma);if(lines.length===1)lines=Wkt.trim(str).split(this.regExes.parenComma);for(i=0;i<lines.length;i+=1){line=lines[i].replace(this.regExes.trimParens,"$1");components.push(this.ingest.linestring.apply(this,[line]))}return components},polygon:function(str){var i,
j,components,subcomponents,ring,rings;rings=Wkt.trim(str).split(this.regExes.parenComma);components=[];for(i=0;i<rings.length;i+=1){ring=rings[i].replace(this.regExes.trimParens,"$1").split(this.regExes.comma);subcomponents=[];for(j=0;j<ring.length;j+=1)subcomponents.push({x:parseFloat(ring[j].split(this.regExes.spaces)[0]),y:parseFloat(ring[j].split(this.regExes.spaces)[1])});components.push(subcomponents)}return components},multipolygon:function(str){var i,components,polygon,polygons;components=
[];polygons=Wkt.trim(str).split(this.regExes.doubleParenComma);for(i=0;i<polygons.length;i+=1){polygon=polygons[i].replace(this.regExes.trimParens,"$1");components.push(this.ingest.polygon.apply(this,[polygon]))}return components},geometrycollection:function(str){console.log("The geometrycollection WKT type is not yet supported.")}};
