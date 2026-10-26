"""Sanity check for P8212: length, counties, NM/TX split. Needs TIGER 2023 county file path as argv[1]."""
import json,sys,geopandas as gpd
from shapely.geometry import shape
from pyproj import Geod
geod=Geod(ellps='WGS84')
f=json.load(open('fetched_layers/P8212_traced.geojson'))['features'][0]
g=shape(f['geometry'])
print('km',geod.geometry_length(g)/1000,'mi',geod.geometry_length(g)/1609.344)
c=gpd.read_file(sys.argv[1])
for st,co in [('35','025'),('48','165')]:
    poly=c[(c.STATEFP==st)&(c.COUNTYFP==co)].geometry.iloc[0]
    part=g.intersection(poly)
    print(st,co,c[(c.STATEFP==st)&(c.COUNTYFP==co)].NAME.iloc[0],'mi in county',geod.geometry_length(part)/1609.344)
coords=list(g.geoms[0].coords) if g.geom_type=='MultiLineString' else list(g.coords)
print('start',coords[0],'end',coords[-1])
