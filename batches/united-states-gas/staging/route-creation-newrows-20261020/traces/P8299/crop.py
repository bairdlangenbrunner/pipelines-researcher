import sys
from PIL import Image, ImageDraw
x0,y0,x1,y1,out=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]),sys.argv[5]
sc=float(sys.argv[6]) if len(sys.argv)>6 else 2
im=Image.open('pg-19.png').convert('RGB').crop((x0,y0,x1,y1))
im=im.resize((int((x1-x0)*sc),int((y1-y0)*sc)),Image.LANCZOS)
d=ImageDraw.Draw(im)
for x in range((x0//50+1)*50,x1,50):
    X=(x-x0)*sc; d.line([(X,0),(X,im.size[1])],fill=(0,0,255) if x%100==0 else (150,150,255),width=1); 
    if x%100==0: d.text((X+2,2),str(x),fill=(255,0,0))
for y in range((y0//50+1)*50,y1,50):
    Y=(y-y0)*sc; d.line([(0,Y),(im.size[0],Y)],fill=(0,0,255) if y%100==0 else (150,150,255),width=1)
    if y%100==0: d.text((2,Y+2),str(y),fill=(255,0,0))
im.save(out)
