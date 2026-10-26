import sys
from PIL import Image,ImageDraw
im=Image.open('../../maps/P8321/appxA-usgs-p4-04.png').convert('RGB')
cx,cy,half,out=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]),sys.argv[4]
c=im.crop((cx-half,cy-half,cx+half,cy+half)).resize((half*8,half*8),Image.LANCZOS)
d=ImageDraw.Draw(c)
# grid ticks every 10 px
for k in range(0,2*half,10):
    d.line([(k*4,0),(k*4,8)],fill=(255,0,0));d.line([(0,k*4),(8,k*4)],fill=(255,0,0))
    if k%20==0:d.text((k*4+2,10),str(cx-half+k),fill=(255,0,0));d.text((10,k*4),str(cy-half+k),fill=(255,0,0))
c.save(out)
