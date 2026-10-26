import json
from shapely.geometry import shape, LineString, Point
from pyproj import Geod
geo=Geod(ellps='WGS84')
R='../../'
line=shape(json.load(open(R+'fetched_layers/P8324_traced.geojson'))['features'][0]['geometry'])
if line.geom_type=='MultiLineString': line=max(line.geoms,key=lambda g:g.length)
L=geo.geometry_length(line);print('length km %.2f mi %.2f'%(L/1000,L/1609.344),'(FERC says 13.24 mi, sheet 12 mi)')
print('start',line.coords[0],'end',line.coords[-1])
par=shape(json.load(open('richland_county.json'))['features'][0]['geometry'])
print('inside Richland Parish:',par.contains(line))
for f,name in (('roads2.json','I-20'),('roads3.json','US 80')):
    for ft in json.load(open(f))['features']:
        g=shape(ft['geometry']);x=line.intersection(g)
        print(name,'crossing',x.wkt[:80], 'dist along line from south end km %.2f'%(geo.geometry_length(LineString([line.coords[0],*[c for c in []]]))/1000 if False else line.project(x if x.geom_type=='Point' else x.centroid)*111.2*0.84))
