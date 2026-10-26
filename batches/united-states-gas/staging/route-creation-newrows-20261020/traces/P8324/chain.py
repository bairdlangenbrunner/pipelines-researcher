import json, numpy as np, networkx as nx
from PIL import Image, ImageDraw
pts=np.load('skel.npy'); S={(int(x),int(y)) for x,y in pts}
G=nx.Graph()
for (x,y) in S:
    for dx in(-1,0,1):
        for dy in(-1,0,1):
            if (dx or dy) and (x+dx,y+dy) in S: G.add_edge((x,y),(x+dx,y+dy),weight=(dx*dx+dy*dy)**.5)
ends=[n for n in G if G.degree(n)==1]; print(sorted(ends,key=lambda p:p[1]))
path=nx.shortest_path(G,(1592,1315),(1660,877),weight='weight')
from shapely.geometry import LineString
ls=LineString(path).simplify(1.0)
pl=[[round(x,1),round(y,1)] for x,y in ls.coords]
print(len(path),len(pl),'px len',LineString(path).length, 'm@28.4',LineString(path).length*0.0254/300*336000)
json.dump({"image":"p31-031.png (page 31 of PUBLIC-Volume_I_07_01_26.pdf rendered at 300 dpi)","polylines":[pl],"notes":"Centerline skeleton of the yellow project boundary line, main run only; the short west spur near US 80 and the northwest spur near LA 852 are left out. Pixel x,y, origin top-left."},open('trace.json','w'))
im=Image.open('p31-031.png').convert('RGB').crop((1300,780,1800,1400)).resize((1000,1240))
d=ImageDraw.Draw(im)
d.line([((x-1300)*2,(y-780)*2) for x,y in pl],fill=(255,0,0),width=2)
im.save('overlay.png')
