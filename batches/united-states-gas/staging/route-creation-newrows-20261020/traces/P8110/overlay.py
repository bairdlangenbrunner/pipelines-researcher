import json,sys
from PIL import Image, ImageDraw
t=json.load(open('trace.json')); im=Image.open('map250.png').convert('RGB'); d=ImageDraw.Draw(im)
for pl in t['polylines']:
    d.line([tuple(p) for p in pl],fill=(0,255,0),width=3)
    for i,p in enumerate(pl): d.ellipse([p[0]-4,p[1]-4,p[0]+4,p[1]+4],outline=(0,0,255))
im.save('overlay_full.png')
im.crop((0,1900,2125,2400)).save('ov_south.png'); im.crop((200,1300,1000,2000)).save('ov_mid.png')
