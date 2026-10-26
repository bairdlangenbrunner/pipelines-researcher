import json, numpy as np
from gcp_raw import G
T=json.load(open('orange_by_sheet.json')); off=json.load(open('sheet_offsets_stitch.json'))
X0,X1,Y0,Y1=38,1619,70,2285
def orient(k,p):
    p=[list(q) for q in p]
    first_is_start = (p[0][1]<p[-1][1]) if k in (1,2,5) else (p[0][0]>p[-1][0])
    return p if first_is_start else p[::-1]
line=[]
for k in range(1,6):
    p=orient(k,T[str(k)][0]); ox,oy=off[str(k)]
    line+= [[x+ox,y+oy] for x,y in p]
json.dump({"image":"mosaic of pagwis-fig1-1..5.png in one pixel frame (sheet offsets in sheet_offsets_stitch.json: global = sheet px + offset)",
 "polylines":[line],"notes":"Orange PROPOSED PIPELINE line extracted by color mask, skeleton and chain per sheet (trace_orange.py), sheets placed edge to edge by where the line crosses each shared frame edge (stitch.py), oriented north to south."},open('trace.json','w'))
EXC={'Mine Rd x Mahan School Rd'}
gc=[]
for s,n,x,y,lo,la,ref in G:
    if n in EXC: continue
    ox,oy=off[str(s)]
    gc.append({"px":[x+ox,y+oy],"lonlat":[lo,la],"name":n+f" (sheet 1{'ABCDE'[s-1]})","source_ref":ref,"sheet_px":[x,y],"sheet":s})
json.dump(gc,open('gcps.json','w'),indent=1)
print(len(gc),'gcps',len(line),'trace pts')
