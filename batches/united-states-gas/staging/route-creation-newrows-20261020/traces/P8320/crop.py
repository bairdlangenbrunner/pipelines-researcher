import sys
from PIL import Image,ImageDraw
# usage: crop.py cx cy out  (native coords); 400x400 crop upscaled 2x with tick labels every 50px
cx,cy,out=int(sys.argv[1]),int(sys.argv[2]),sys.argv[3]
h=int(sys.argv[4]) if len(sys.argv)>4 else 200
im=Image.open('img-000.png').convert('RGB').crop((cx-h,cy-h,cx+h,cy+h)).resize((h*4,h*4),Image.LANCZOS)
d=ImageDraw.Draw(im)
for k in range(0,2*h,50):
    d.line([(k*2,0),(k*2,12)],fill=(255,0,0));d.text((k*2+2,12),str(cx-h+k),fill=(255,0,0))
    d.line([(0,k*2),(12,k*2)],fill=(255,0,0));d.text((14,k*2),str(cy-h+k),fill=(255,0,0))
im.save(out)
