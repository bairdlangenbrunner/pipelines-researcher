import sys
from PIL import Image, ImageDraw
im=Image.open('/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher/batches/united-states-gas/staging/route-creation-newrows-20261020/maps/P8212/notice-of-scoping-image1.png').convert('RGB')
x0,y0,x1,y1,s=map(int,sys.argv[1:6])
c=im.crop((x0,y0,x1,y1)).resize(((x1-x0)*s,(y1-y0)*s),Image.LANCZOS)
d=ImageDraw.Draw(c)
for x in range((x0//10+1)*10,x1,10):
    d.line([((x-x0)*s,0),((x-x0)*s,c.height)],fill=(0,0,0) if x%50==0 else (170,170,170),width=1)
    if x%50==0: d.text(((x-x0)*s+2,2),str(x),fill=(0,0,200))
for y in range((y0//10+1)*10,y1,10):
    d.line([(0,(y-y0)*s),(c.width,(y-y0)*s)],fill=(0,0,0) if y%50==0 else (170,170,170),width=1)
    if y%50==0: d.text((2,(y-y0)*s+2),str(y),fill=(0,0,200))
c.save(sys.argv[6])
