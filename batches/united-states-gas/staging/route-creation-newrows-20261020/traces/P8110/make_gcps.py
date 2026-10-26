"""Build gcps.json. lonlat = Census 2023 cartographic-boundary (500k) county vertex; pixel = corner/junction of the map's gray parish outline located by eye on 6x zoom tiles (tiles.py), as an offset from the preview alignment pixel (icp_A, preview only)."""
import json
C={('c%d'%c['id']):c for c in json.load(open('corner_candidates.json'))}
T={('t%d'%t['id']):t for t in json.load(open('tri_refined.json'))}
picks=[ # id, dx, dy, description
('c4',1,-0.5,'Franklin Parish and Catahoula Parish boundary corner (northeast corner of the notch south of Franklin Parish)'),
('c0',2,-2,'Catahoula Parish, LaSalle Parish corner on the straight western line'),
('c11',0,0,'Franklin Parish and Tensas Parish boundary corner on the eastern edge'),
('t158',0,-1.3,'Catahoula, LaSalle and Rapides Parish junction on the Avoyelles Parish north line'),
('t186',-1.5,-1,'junction of the Avoyelles and St. Landry parish line and neighboring parish lines'),
('t208',0.8,-0.3,'St. Landry, Lafayette and Iberia area parish corner west of Lafayette'),
('t201',1.7,1.3,'Iberville and Pointe Coupee parish junction'),
('t225',0,1,'Iberville, Assumption and Ascension area parish corner'),
('t224',2,0.3,'Iberville, Assumption and Ascension parish junction near milepost 200'),
('t232',6.3,2,'Assumption, Lafourche and St. James parish junction'),
('t240',8,0.3,'Assumption, Lafourche and Terrebonne parish junction near Morgan City'),
('t239',15,2,'Jefferson, Lafourche and St. Charles parish junction'),
('t233',16,0,'Jefferson, Orleans and Plaquemines parish junction'),
]
out=[]
for i,dx,dy,desc in picks:
    o=C.get(i) or T[i]; x,y=o['px1']
    ll=o['lonlat']
    ctys=o.get('cty') or [o['name']+','+o['st']]
    out.append({'px':[round(round(x)+dx,1),round(round(y)+dy,1)],'lonlat':[round(ll[0],6),round(ll[1],6)],'name':desc,
     'source_ref':'US Census Bureau 2023 cartographic boundary file cb_2023_us_county_500k (https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_county_500k.zip), vertex shared by '+'; '.join(ctys)+' (script corners.py/tri.py)' if i.startswith('t') else 'US Census Bureau 2023 cartographic boundary file cb_2023_us_county_500k (https://www2.census.gov/geo/tiger/GENZ2023/shp/cb_2023_us_county_500k.zip), county boundary corner of '+o['name']+' Parish (script corners.py)','cand':i})
json.dump(out,open('gcps.json','w'),indent=1)
for g in out: print(g['cand'],g['px'],g['lonlat'])
