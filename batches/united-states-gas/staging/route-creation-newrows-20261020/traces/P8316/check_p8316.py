"""Sanity checks for P8316: geodesic length, endpoints in El Paso County TX, crossing of Stan Roberts Sr Ave and the TIGER county polygon."""
import json, geopandas as gpd
from pyproj import Geod
from shapely.geometry import shape, Point
D='/private/tmp/claude-501/-Users-baird-Dropbox--git-ALL--github-repos-gem-pipelines-researcher/b8a48c22-afac-4a01-8a7d-67c80be12078/scratchpad/tiger8316/'
R='batches/united-states-gas/staging/route-creation-newrows-20261020/'
f=json.load(open(R+'fetched_layers/P8316_traced.geojson'))['features'][0]
g=shape(f['geometry']); G=Geod(ellps='WGS84')
L=sum(G.geometry_length(x) for x in (g.geoms if hasattr(g,'geoms') else [g]))/1000
print('length km %.3f mi %.3f stated 5.8 mi ratio %.3f'%(L,L/1.609344,L/1.609344/5.8))
c=gpd.read_file(D+'tl_2023_us_county.zip'); c=c[c.GEOID=='48141'].geometry.iloc[0]
ln=g if g.geom_type=='LineString' else g.geoms[0]
for n,pt in [('start',Point(ln.coords[0])),('end',Point(ln.coords[-1]))]: print(n,pt.coords[0],'in El Paso County TX:',c.contains(pt))
print('all in county:',c.buffer(0.0005).contains(g))
import pandas as pd
r=gpd.read_file(D+'tl_2023_48141_roads.zip',bbox=(-106.42,31.95,-106.33,32.01))
sr=r[r.FULLNAME=='Stan Roberts Sr Ave'].geometry.unary_union
x=g.intersection(sr.buffer(0.0002)); print('crosses Stan Roberts Sr Ave near:',x.centroid.coords[0] if not x.is_empty else None)
print('state-line distance of northern leg: min lat',min(p[1] for p in ln.coords),'max lat',max(p[1] for p in ln.coords))
