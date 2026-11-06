import sys,json; sys.path.insert(0,'.')
from mpcut import interp, sub, master, stpt
import l101
from pyproj import Geod
Gd=Geod(ellps='WGS84')
def mi(ls): return sum(Gd.inv(a[0],a[1],b[0],b[1])[2] for a,b in zip(ls,ls[1:]))/1609.344
out={}
# leidy
M=json.load(open('leidy_master.json')); P=[tuple(p) for p in M['path']]; C=M['cum']; ch=M['ch']; k=M['k']
lc=lambda mp: ch[0]+(mp-0.11)*k
L=lambda a,b: sub(P,C,lc(a),lc(b))
# mainline (Skillman) from north_master_a
N=json.load(open('north_master_a.json')); NP=[tuple(p) for p in N['path']]; NC=N['cum']; c165=N['c165']
nm=lambda mp: c165+mp-1413.0
# feature 101 two-anchor calibration: MP 1793.92 at chain 27.95 (Somerset/Morris line at 27.975), MP 1825.8 at chain 59.99 (Essex/Bergen line at 59.975)
k1=(59.99-27.95)/(1825.8-1793.92); f1=lambda mp: 27.95+(mp-1793.92)*k1
out['P8281']=[('Skillman Loop',1776.8,1783.0,sub(NP,NC,nm(1776.8),nm(1783.0))),
              ('Pleasant Run Loop',0.1,6.9,L(0.1,6.9)),
              ('Franklin Loop',57.5,69.0,L(57.5,69.0)),
              ('Dorrance Loop (Leidy Loop Line MP from Station 515)',17.7,23.0,L(68.95+17.7,68.95+23.0))]
out['P8280']=[('Haneyville Loop',178.49,183.13,L(178.49,183.13)),('Williamsport Loop',134.57,138.30,L(134.57,138.30)),
              ('Benton Loop (Leidy Loop Line MP from Station 515)',33.19,39.28,L(68.95+33.19,68.95+39.28)),
              ('Allentown Loop',30.29,36.56,L(30.29,36.56)),('Clinton Loop',13.62,18.25,L(13.62,18.25)),
              ('Stirling Loop',1789.60,1793.92,l101.sub(f1(1789.60),f1(1793.92)))]
out['P3199']=[('Bergen Loop',1825.80,1826.41,l101.sub(f1(1825.80),f1(1826.41)))]
for pid,ls in out.items():
    fc={'type':'FeatureCollection','features':[{'type':'Feature','properties':{'name':n,'mp_start':a,'mp_end':b,'cut_mi':round(mi(g),2)},'geometry':{'type':'LineString','coordinates':g}} for n,a,b,g in ls]}
    json.dump(fc,open(f'cuts/{pid}_loops.geojson','w'))
    print(pid,[(n.split(' (')[0],round(mi(g),2),round(abs(b-a),2)) for n,a,b,g in ls],'sum',round(sum(mi(g) for *_,g in ls),2))
# re-append P8287 North Georgia Extension loop
p,cum,_,_=master([stpt(125),(-83.96338,34.01211)])
g=sub(p,cum,0,19.01)
fc=json.load(open('cuts/P8287_loops.geojson'))
fc['features']=[f for f in fc['features'] if f['properties']['name']!='North Georgia Extension Loop']
fc['features'].append({'type':'Feature','properties':{'name':'North Georgia Extension Loop','mp_start':None,'mp_end':None,'cut_mi':round(mi(g),2)},'geometry':{'type':'LineString','coordinates':g}})
json.dump(fc,open('cuts/P8287_loops.geojson','w'))
print('P8287',[(f['properties']['name'],round(mi(f['geometry']['coordinates']),2)) for f in fc['features']])
