import json,sys
from PIL import Image,ImageDraw
from prelim_roads import px
J=json.load(open('junctions.json'))
im=Image.open('../../maps/P8321/appxA-usgs-p4-04.png').convert('RGB');d=ImageDraw.Draw(im)
x0,y0,x1,y1=map(int,sys.argv[1:5])
for i,j in enumerate(J):
    x,y=px(j['lon'],j['lat'])
    if x0<=x<=x1 and y0<=y<=y1:
        d.ellipse([x-3,y-3,x+3,y+3],outline=(255,0,255),width=1);d.text((x+5,y-5),str(i),fill=(255,0,0))
im.crop((x0,y0,x1,y1)).resize(((x1-x0)*2,(y1-y0)*2),Image.LANCZOS).save(sys.argv[5])
