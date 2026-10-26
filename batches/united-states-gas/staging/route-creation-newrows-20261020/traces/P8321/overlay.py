import json,sys
from PIL import Image,ImageDraw
im=Image.open('../../maps/P8321/appxA-usgs-p4-04.png').convert('RGB')
d=ImageDraw.Draw(im)
t=json.load(open('trace.json'))
for pl in t['polylines']:d.line([tuple(p) for p in pl],fill=(255,0,0),width=2)
try:
    for g in json.load(open('gcps.json')):
        x,y=g['px'];d.ellipse([x-9,y-9,x+9,y+9],outline=(255,255,0),width=3);d.text((x+12,y-6),g['name'],fill=(0,0,0))
except Exception:pass
im.crop(tuple(map(int,sys.argv[1:5]))).save(sys.argv[5])
