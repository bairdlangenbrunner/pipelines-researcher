import numpy as np
from PIL import Image
im=np.array(Image.open('p31-031.png').convert('RGB')).astype(int)
blk=(im.max(axis=2)<70)
def ys_xs(x0,x1,y0,y1):
    ys,xs=np.nonzero(blk[y0:y1,x0:x1]);return xs+x0,ys+y0
# vertical A-C segment
xs,ys=ys_xs(1760,1800,345,650);print('vert AC x mean',xs.mean(),xs.min(),xs.max())
# horizontal top A-B (y near 328)
xs,ys=ys_xs(1670,1770,310,345);print('top AB y mean',ys.mean(),ys.min(),ys.max(), 'x range',xs.min(),xs.max())
# horizontal C-east (y~668)
xs,ys=ys_xs(1790,1950,650,685);print('C east y mean',ys.mean(),ys.min(),ys.max())
# horizontal D-E (y ~ 1350)
xs,ys=ys_xs(1700,2100,1335,1375);print('DE y mean',ys.mean(),ys.min(),ys.max(),xs.min(),xs.max())
xs,ys=ys_xs(1760,1800,345,650)
p=np.polyfit(ys,xs,1);print('AC fit slope',p,'x at 329.5',np.polyval(p,329.5),'x at 666.4',np.polyval(p,666.4))
# DE and east flat: fit line to black pixels in clean sections
for name,(x0,x1,y0,y1) in {'DE_west':(1700,1850,1345,1375),'DE_mid':(1850,2000,1345,1375),'DE_east':(2000,2140,1335,1365)}.items():
    xs,ys=ys_xs(x0,x1,y0,y1);print(name,xs.mean(),ys.mean(),len(xs))
