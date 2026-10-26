"""zoom.py cx cy half scale out.png : crop mosaic around frame point (cx,cy), grid lines every 10 frame px, labeled every 20."""
import sys
from PIL import Image, ImageDraw
cx,cy,h,s=map(int,sys.argv[1:5]); out=sys.argv[5]; ox,oy=-1800,-2000
M=Image.open('mosaic.png').convert('RGB')
c=M.crop((cx-h-ox,cy-h-oy,cx+h-ox,cy+h-oy)).resize((2*h*s,2*h*s),Image.LANCZOS); d=ImageDraw.Draw(c)
for v in range(-h,h+1,10):
    col=(255,255,0) if v%20==0 else (120,120,120)
    if (cx+v)%10==0 or True:
        pass
for X in range((cx-h)//10*10,cx+h+1,10):
    x=(X-(cx-h))*s; d.line([(x,0),(x,c.size[1])],fill=(255,255,255) if X%50==0 else (90,90,90),width=1)
    if X%20==0: d.text((x+2,2),str(X),fill=(255,255,0))
for Y in range((cy-h)//10*10,cy+h+1,10):
    y=(Y-(cy-h))*s; d.line([(0,y),(c.size[0],y)],fill=(255,255,255) if Y%50==0 else (90,90,90),width=1)
    if Y%20==0: d.text((2,y+2),str(Y),fill=(255,255,0))
c.save(out)
