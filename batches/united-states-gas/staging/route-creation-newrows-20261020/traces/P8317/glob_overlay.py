import numpy as np, json
from pyproj import Transformer
from gcp_raw import G
from PIL import Image, ImageDraw
S=1.006
tr=Transformer.from_crs(4326,32617,always_xy=True)
EXC={'Mine Rd x Mahan School Rd'}
off={}
for k in range(1,6):
    v=[]
    for s,n,x,y,lo,la,ref in G:
        if s!=k or n in EXC: continue
        E,N=tr.transform(lo,la); v.append((E/S-x,-N/S-y))
    off[k]=np.mean(v,axis=0)
json.dump({k:list(map(float,v)) for k,v in off.items()},open('sheet_offsets_gcp.json','w'))
tr_by=json.load(open('orange_by_sheet.json'))
cols=[(255,0,0),(0,160,0),(0,0,255),(200,0,200),(0,160,160)]
base=np.min([off[k] for k in off],axis=0)
W=int(max(off[k][0] for k in off)+1700-base[0]); H=int(max(off[k][1] for k in off)+2300-base[1])
print(W,H)
im=Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im)
for k in range(1,6):
    ox,oy=off[k]-base
    d.rectangle([ox+38,oy+70,ox+1619,oy+2285],outline=cols[k-1])
    for poly in tr_by[str(k)]:
        d.line([(x+ox,y+oy) for x,y in poly],fill=cols[k-1],width=4)
im.resize((W//4,H//4)).save('/private/tmp/claude-501/glob.png'); print(im.size)
