import json,sys,collections
from PIL import Image,ImageDraw
from prelim_roads import px
R=json.load(open('tiger_roads.json'))
cnt=collections.defaultdict(set)
for L in R:
    for nm,mt,paths in R[L]:
        for p in paths:
            for q in (p[0],p[-1]):cnt[(round(q[0],5),round(q[1],5))].add((nm,mt))
nodes=[(k,v) for k,v in cnt.items() if len({n for n,_ in v if n})>=2 and any(m in('S1100','S1200','S1400') for _,m in v)]
nodes.sort()
json.dump([[k[0],k[1],sorted(([a or "",b] for a,b in v))] for k,v in nodes],open('nodes.json','w'))
print(len(nodes))
if len(sys.argv)>5:
    im=Image.open('../../maps/P8321/appxA-usgs-p4-04.png').convert('RGB');d=ImageDraw.Draw(im)
    for i,(k,v) in enumerate(nodes):
        x,y=px(*k);d.ellipse([x-4,y-4,x+4,y+4],outline=(255,0,255),width=2);d.text((x+6,y-6),str(i),fill=(255,0,0))
    im.crop(tuple(map(int,sys.argv[1:5]))).save(sys.argv[5])
