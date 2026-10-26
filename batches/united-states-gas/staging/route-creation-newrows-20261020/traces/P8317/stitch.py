# Place the five sheets in one pixel frame. The sheets tile the route edge to edge (frames abut, no real overlap):
# the pipeline leaves one sheet's frame edge and enters the next sheet's frame edge, so the shift between sheets is
# fixed by the point where the orange line crosses the shared edge, extrapolated to the frame edge.
import json, numpy as np
T=json.load(open('orange_by_sheet.json'))
X0,X1,Y0,Y1=38,1619,70,2285   # map frame of every sheet (px)
def edge_cross(poly,which):
    p=np.array(poly)
    if which=='bottom': sel=p[p[:,1]>Y1-120]; fit=np.polyfit(sel[:,1],sel[:,0],1); return float(np.polyval(fit,Y1))
    if which=='top': sel=p[p[:,1]<Y0+120]; fit=np.polyfit(sel[:,1],sel[:,0],1); return float(np.polyval(fit,Y0))
    if which=='left': sel=p[p[:,0]<X0+120]; fit=np.polyfit(sel[:,0],sel[:,1],1); return float(np.polyval(fit,X0))
    if which=='right': sel=p[p[:,0]>X1-120]; fit=np.polyfit(sel[:,0],sel[:,1],1); return float(np.polyval(fit,X1))
P={k:T[str(k)][0] for k in range(1,6)}
off={1:(0.0,0.0)}   # global = sheet px + off
# 1->2 : bottom of 1 meets top of 2
x1=edge_cross(P[1],'bottom'); x2=edge_cross(P[2],'top'); off[2]=(off[1][0]+x1-x2, off[1][1]+Y1-Y0)
x2=edge_cross(P[2],'bottom'); x3=edge_cross(P[3],'top'); off[3]=(off[2][0]+x2-x3, off[2][1]+Y1-Y0)
# 3->4 : left edge of 3 meets right edge of 4 (sheet 4 lies west of 3)
y3=edge_cross(P[3],'left'); y4=edge_cross(P[4],'right'); off[4]=(off[3][0]+X0-X1, off[3][1]+y3-y4)
x4=edge_cross(P[4],'bottom'); x5=edge_cross(P[5],'top'); off[5]=(off[4][0]+x4-x5, off[4][1]+Y1-Y0)
off={k:[round(v[0],1),round(v[1],1)] for k,v in off.items()}
print(off); json.dump(off,open('sheet_offsets_stitch.json','w'))
