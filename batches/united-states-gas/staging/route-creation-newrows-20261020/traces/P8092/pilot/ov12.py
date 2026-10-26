import json,numpy as np,sys
from PIL import Image,ImageDraw
from pyproj import Transformer
M='/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher/batches/united-states-gas/staging/route-creation-newrows-20261020/maps/P8092/map-12.png'
t=Transformer.from_crs(4326,32606,always_xy=True)
# preview-only affine from grid labels: orig px = 150+(488000-E)*.24 ; y = 371+(N-6866000)*.24 (rotated 180: N increases downward)
tx,ty,s=float(sys.argv[1]),float(sys.argv[2]),float(sys.argv[3])
def px(E,N): return 150+tx+(488000-E)*s, 371+ty+(N-6866000)*s
o=Image.open(M).convert('RGB'); d=ImageDraw.Draw(o)
def draw(fn,col,w=3):
    for f in json.load(open(fn))['features']:
        g=f['geometry']; 
        if g['type']=='Polygon': rings=g['coordinates']
        elif g['type']=='MultiPolygon': rings=[r for p in g['coordinates'] for r in p]
        elif g['type']=='LineString': rings=[g['coordinates']]
        elif g['type']=='MultiLineString': rings=g['coordinates']
        else: continue
        for r in rings:
            p=[px(*t.transform(*c)) for c in r]
            d.line(p,fill=col,width=w)
draw('w12.json',(255,0,0)); draw('r2.json',(255,0,255),4); draw('f12.json',(0,0,255),1)
o.crop((90,60,2450,830)).save('ov12.png')
