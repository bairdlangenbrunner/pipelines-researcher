# independent checks: (1) overlay TIGER roads on the map using the fitted affine, (2) geodesic length, (3) endpoints
import json,numpy as np,sys
from PIL import Image,ImageDraw
from pyproj import Geod
G=json.load(open('gcps.json'))
P=np.array([g['px'] for g in G]);L=np.array([g['lonlat'] for g in G])
A=np.c_[P,np.ones(len(P))]
cx,_,_,_=np.linalg.lstsq(A,L,rcond=None)    # px -> lonlat
ix,_,_,_=np.linalg.lstsq(np.c_[L,np.ones(len(L))],P,rcond=None)  # lonlat -> px
topx=lambda lon,lat:np.array([lon,lat,1])@ix
fc=json.load(open('../../fetched_layers/P8321_traced.geojson'))
geom=fc['features'][0]['geometry'];lines=[geom['coordinates']] if geom['type']=='LineString' else geom['coordinates']
geod=Geod(ellps='WGS84');tot=sum(geod.line_length([c[0] for c in l],[c[1] for c in l]) for l in lines)
print('length km %.2f mi %.2f stated 7.26 mi ratio %.3f'%(tot/1000,tot/1609.344,tot/1609.344/7.26))
print('start',lines[0][0],'end',lines[-1][-1])
# independent junction test: predicted pixel of TIGER junctions vs unseen map features is done visually via overlay
im=Image.open('../../maps/P8321/appxA-usgs-p4-04.png').convert('RGB');d=ImageDraw.Draw(im)
R=json.load(open('tiger_roads.json'))
for Lr in R:
    for nm,mt,paths in R[Lr]:
        for p in paths:d.line([tuple(topx(*q)) for q in p],fill=(255,0,255),width=1)
for l in lines:d.line([tuple(topx(*q)) for q in l],fill=(255,0,0),width=2)
im.save(sys.argv[1] if len(sys.argv)>1 else 'check_overlay.png')
