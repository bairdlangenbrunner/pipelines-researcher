import numpy as np
from pyproj import Geod
P=[('Beaufort',(1448.8,1583.4),(-88.18766,46.53766)),('King',(-45.5,1704.4),(-88.4088,46.5198)),('Vermilac',(-622,1488),(-88.4947,46.5413)),
('junction',(-464,1064),(-88.472259,46.585275)),('houghton',(-902,-1549),(-88.55194,46.8518))]
A=np.array([[p[0],p[1],1] for _,p,_ in P]);L=np.array([l for *_,l in P])
co,*_=np.linalg.lstsq(A,L,rcond=None)
print(co)
g=Geod(ellps='WGS84')
for n,p,l in P:
    f=np.array([*p,1])@co; print(n,f.round(5),round(g.inv(f[0],f[1],*l)[2]))
