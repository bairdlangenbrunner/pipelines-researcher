"""Sanity check: geodesic length vs stated 300 mi, and the order of Louisiana parishes crossed (Census 2023 500k)."""
import json, geopandas as gpd
from shapely.geometry import shape, Point
from pyproj import Geod
f=json.load(open('../../fetched_layers/P8110_traced.geojson'))['features'][0]['geometry']
lines=f['coordinates'] if f['type']=='MultiLineString' else [f['coordinates']]
g=Geod(ellps='WGS84'); L=sum(g.line_length([p[0] for p in l],[p[1] for p in l]) for l in lines)/1000
print('length km %.1f mi %.1f ratio to 300 mi %.2f'%(L,L/1.609344,L/1.609344/300))
cty=gpd.read_file('/private/tmp/claude-501/census_dl/county/cb_2023_us_county_500k.shp').to_crs(4326); cty=cty[cty.STATEFP=='22']
seq=[]
for l in lines:
    for x,y in l:
        for _,r in cty.iterrows():
            if r.geometry.contains(Point(x,y)):
                if not seq or seq[-1]!=r.NAME: seq.append(r.NAME)
                break
print(' > '.join(seq)); print('start',lines[0][0],'end',lines[-1][-1], 'parts',len(lines))
