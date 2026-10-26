import sys
from PIL import Image, ImageDraw
sheet,cx,cy,half=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4])
im=Image.open('../../maps/P8317/pagwis-fig1-%d.png'%sheet).convert('RGB')
x0,y0=max(0,cx-half),max(0,cy-half)
c=im.crop((x0,y0,x0+2*half,y0+2*half)); z=900/(2*half)
c=c.resize((900,900),Image.LANCZOS); d=ImageDraw.Draw(c)
step=50 if half<=200 else 100
for v in range((x0//step+1)*step,x0+2*half,step):
    X=(v-x0)*z; d.line([(X,0),(X,900)],fill=(255,255,0),width=1); d.text((X+2,2),str(v),fill=(255,255,255))
for v in range((y0//step+1)*step,y0+2*half,step):
    Y=(v-y0)*z; d.line([(0,Y),(900,Y)],fill=(255,255,0),width=1); d.text((2,Y+2),str(v),fill=(255,255,255))
c.save('/private/tmp/claude-501/crop.png')
