import numpy as np
from PIL import Image
M='../../maps/P8317/pagwis-fig1-%d.png'
def g(i): return np.asarray(Image.open(M%i).convert('L'),dtype=np.float32)
a,b=g(1),g(2)
best=[]
t=b[80:560,60:1250]   # top of sheet 2 (orig px)
for dy in range(1500,1800,4):
  for dx in range(-400,100,4):
    ya,xa=80+dy,60+dx
    p=a[ya:ya+480,xa:xa+1190]
    if p.shape!=t.shape or xa<0: continue
    c=np.corrcoef(p[::4,::4].ravel(),t[::4,::4].ravel())[0,1]
    best.append((c,dx,dy))
best.sort(reverse=True); print(best[:5])
