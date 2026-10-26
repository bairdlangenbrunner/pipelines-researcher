"""Chain skeleton pieces (between milepost circles) into one pixel polyline, north to south."""
import json, numpy as np, networkx as nx
from scipy import ndimage as ndi
pts = np.load('skel.npy'); S = {tuple(p) for p in pts}
mask = np.zeros((2750,2125),bool)
for x,y in S: mask[y,x]=True
lab,n = ndi.label(mask, structure=np.ones((3,3)))
pieces=[]
for i in range(1,n+1):
    ys,xs = np.nonzero(lab==i)
    if len(xs)<8: continue
    G = nx.Graph()
    P = set(zip(xs,ys))
    for (x,y) in P:
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                if (dx or dy) and (x+dx,y+dy) in P: G.add_edge((x,y),(x+dx,y+dy),weight=(dx*dx+dy*dy)**.5)
    a = next(iter(G.nodes))
    d = nx.single_source_dijkstra_path_length(G,a); u=max(d,key=d.get)
    d = nx.single_source_dijkstra_path_length(G,u); v=max(d,key=d.get)
    path = nx.dijkstra_path(G,u,v)
    pieces.append(path)
print(len(pieces),'pieces')
# chain: start with piece whose endpoint has smallest y
def ends(p): return p[0],p[-1]
best=None
for k,p in enumerate(pieces):
    for e in ends(p):
        if best is None or e[1]<best[0]: best=(e[1],k,e)
_,k,e = best
chain = pieces[k] if pieces[k][0]==e else pieces[k][::-1]
rest = [p for j,p in enumerate(pieces) if j!=k]
gaps=[]
while rest:
    tail = chain[-1]
    bj=None
    for j,p in enumerate(rest):
        for rev in (0,1):
            q = p[::-1] if rev else p
            dd = np.hypot(q[0][0]-tail[0], q[0][1]-tail[1])
            if bj is None or dd<bj[0]: bj=(dd,j,rev)
    dd,j,rev = bj; gaps.append((round(float(dd),1),tuple(int(v) for v in tail)))
    q = rest.pop(j); q = q[::-1] if rev else q
    chain += q
print('gaps px',gaps)
# simplify with Douglas-Peucker (~1 px at 250 dpi)
from shapely.geometry import LineString
ls = LineString(chain).simplify(1.0)
pl = [[round(x,1),round(y,1)] for x,y in ls.coords]
print(len(pl),'pts')
json.dump({"image":"map250.png","polylines":[pl],"notes":"Red Cloud Connector route extracted by color mask from the 250 dpi render of page 54, skeletonized, pieces between milepost circles chained nearest-end from the north. Milepost circle gaps are bridged straight (about 20 px)."},open('trace.json','w'))
