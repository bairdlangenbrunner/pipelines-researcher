"""Sanity check: geodesic length vs stated 24 mi, county containment of the line, endpoints, and distance of the line from TIGER SR 161 near its west section.
Usage: python3 -I check_route.py <counties.gpkg> <roads.gpkg> <traced.geojson>"""
import sys, json, geopandas as gpd
from shapely.geometry import shape
from pyproj import Geod
cnt=gpd.read_file(sys.argv[1]); roads=gpd.read_file(sys.argv[2]); f=json.load(open(sys.argv[3]))['features'][0]
g=shape(f['geometry']); geod=Geod(ellps='WGS84')
km=geod.geometry_length(g)/1000; print('length km %.2f mi %.2f ratio to 24 mi %.2f'%(km,km/1.609344,km/1.609344/24))
print('start',g.coords[0],'end',g.coords[-1])
for _,c in cnt.iterrows():
    inter=g.intersection(c.geometry)
    if not inter.is_empty: print(c.NAME,'county share %.1f%%'%(100*geod.geometry_length(inter)/geod.geometry_length(g)))
sr=roads[roads.FULLNAME=='State Rte 161'].unary_union
import numpy as np
from shapely.geometry import Point
# distance of the Phase 1 west section (first 25 vertices) to SR 161
pts=list(g.coords)[:40]
d=[ (Point(p).distance(sr))*85000 for p in pts]
print('min distance of first 40 vertices to SR 161, m: %.0f'%min(d))
