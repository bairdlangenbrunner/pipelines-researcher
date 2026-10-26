from PIL import Image; import numpy as np
im=np.array(Image.open('../../maps/P8329/RochesterLateralMap-1.png').convert('RGB')).astype(int)
def m(c,t=60): return (np.abs(im-np.array(c)).sum(2)<t)
mag=m((255,0,197)); org=m((230,152,0)); blu=m((0,112,255))
out=np.full(im.shape,255,np.uint8)
out[mag]=(255,0,197); out[org]=(230,152,0); out[blu]=(0,112,255)
Image.fromarray(out).save('masks.png')
np.save('mag.npy',mag); np.save('org.npy',org); np.save('blu.npy',blu)
print(mag.sum(),org.sum(),blu.sum())
