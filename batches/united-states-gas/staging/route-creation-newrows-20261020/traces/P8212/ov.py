import json,sys
from PIL import Image, ImageDraw
IMG='/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher/batches/united-states-gas/staging/route-creation-newrows-20261020/maps/P8212/notice-of-scoping-image1.png'
im=Image.open(IMG).convert('RGB')
t=json.load(open(sys.argv[1]))
pl=t['polylines'] if 'polylines' in t else list(t.values())
x0,y0,x1,y1,s=map(int,sys.argv[2:7])
c=im.crop((x0,y0,x1,y1)).resize(((x1-x0)*s,(y1-y0)*s),Image.LANCZOS)
d=ImageDraw.Draw(c)
for p in pl:
    q=[((x-x0)*s,(y-y0)*s) for x,y in p]
    d.line(q,fill=(0,200,0),width=1)
    for a in q[::4]: d.ellipse([a[0]-2,a[1]-2,a[0]+2,a[1]+2],outline=(0,0,0))
c.save(sys.argv[7])
