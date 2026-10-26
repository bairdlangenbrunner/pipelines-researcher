# Intersections of named TIGER/Line 2023 road centerlines (US Census Bureau, Indiana County PA, tl_2023_42063_roads)
import geopandas as gpd, itertools, sys
from shapely.ops import unary_union
g=gpd.read_file('/private/tmp/claude-501/tiger63/tl_2023_42063_roads.shp')
names=['Coal Rd','Bruner Rd','Power Plant Rd','Mine Rd','Dickey Rd','Mahan School Rd','Black Lick Rd','McConnell Rd','Dunlap Dr','Ash Rd','Muddy Run Rd','Thompson Rd','Falling Run Rd','Campbells Mill Rd','Pine Ln','Country Lane Rd','Grafton Rd','Rome St']
print(sorted(set(g.FULLNAME.dropna()) & set(names)))
sel={n:unary_union(g[g.FULLNAME==n].geometry.tolist()) for n in names if (g.FULLNAME==n).any()}
for a,b in itertools.combinations(sel,2):
    i=sel[a].intersection(sel[b])
    if not i.is_empty: print(a,'x',b,i.wkt[:120])
