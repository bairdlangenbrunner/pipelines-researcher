"""Audit StartState/Province + EndState/Province for the US gas stale-operating cohort
against route geometry (routes repo) joined to Natural Earth 10m admin-1 polygons."""
import json, os, glob, sys, collections
import pandas as pd, geopandas as gpd
from shapely.geometry import Point, shape, LineString, MultiLineString

CSV='data/GGIT_gas_snapshot_20260904.csv'
ROUTES='../GOIT-GGIT-pipeline-routes/data/individual-routes/gas-pipelines'
NE=os.path.expanduser('~/Dropbox/_gis-data/_natural_earth_data/ne_10m_admin_1_states_provinces/ne_10m_admin_1_states_provinces.shp')
DONE=set(os.path.basename(p)[:-5] for p in glob.glob('batches/united-states-gas/staging/deepsweep-tx-operating/rows/*.json'))

df=pd.read_csv(CSV,header=2,low_memory=False)
us=df[(df['StartCountryOrArea'].astype(str).str.contains('United States',na=False))|(df['EndCountryOrArea'].astype(str).str.contains('United States',na=False))]
op=us[us['Status'].astype(str).str.strip().str.lower()=='operating']
lu=pd.to_numeric(op['LastUpdated'].astype(str).str[:4],errors='coerce')
cohort=op[lu<=2023].copy()
cohort['sheet_row']=cohort.index+4
cohort['batch1']=cohort['ProjectID'].isin(DONE)

adm=gpd.read_file(NE)
adm=adm[adm['iso_a2'].isin(['US','MX','CA'])][['name','iso_a2','geometry']].to_crs(4326)
sidx=adm.sindex

def state_at(pt):
    cands=adm.iloc[list(sidx.query(pt,predicate='intersects'))]
    if len(cands): return f"{cands.iloc[0]['name']} ({cands.iloc[0]['iso_a2']})"
    # nearest within ~0.3 deg (offshore/coastal)
    d=adm.distance(pt); i=d.idxmin()
    return f"{adm.loc[i,'name']} ({adm.loc[i,'iso_a2']})~{d[i]:.2f}" if d[i]<0.5 else None

def endpoints(geom):
    lines=[]
    if geom.geom_type=='LineString': lines=[geom]
    elif geom.geom_type=='MultiLineString': lines=list(geom.geoms)
    if not lines: return None,None
    # first vertex of the first part, last vertex of the last part
    return Point(lines[0].coords[0]), Point(lines[-1].coords[-1])

def split_states(v):
    if pd.isna(v) or not str(v).strip(): return []
    return [s.strip() for s in str(v).replace(';',',').split(',') if s.strip()]

rows=[]
for _,r in cohort.iterrows():
    pid=r['ProjectID']; fp=f"{ROUTES}/{pid}.geojson"
    rec=dict(pid=pid,sheet_row=r['sheet_row'],batch1=r['batch1'],name=r['PipelineName'],seg=r['SegmentName'],
             start_state=r['StartState/Province'],end_state=r['EndState/Province'],
             start_loc=r['StartLocation'],start_dist=r['StartPrefecture/District'],end_loc=r['EndLocation'],end_dist=r['EndPrefecture/District'],
             route_type=r['RouteType'],route_acc=r['RouteAccuracy'])
    geo_a=geo_b=None; traversed=[]
    if os.path.exists(fp):
        try:
            gj=json.load(open(fp)); feats=gj.get('features',[])
            geoms=[shape(f['geometry']) for f in feats if f.get('geometry')]
            geoms=[g for g in geoms if not g.is_empty]
            if geoms:
                from shapely.ops import unary_union
                g=unary_union(geoms) if len(geoms)>1 else geoms[0]
                a,b=endpoints(g if g.geom_type in ('LineString','MultiLineString') else geoms[0])
                if a is not None:
                    geo_a=state_at(a); geo_b=state_at(b)
                    hits=adm.iloc[list(sidx.query(g,predicate='intersects'))]
                    traversed=sorted(set(hits['name']))
        except Exception as e:
            rec['geo_err']=str(e)[:80]
    rec.update(geo_first=geo_a,geo_last=geo_b,traversed=traversed)
    ss=split_states(rec['start_state']); es=split_states(rec['end_state'])
    def base(s): return s.split(' (')[0] if s else None
    ends={base(geo_a),base(geo_b)}-{None}
    if geo_a is None:
        verdict='NO_ROUTE'
    elif not ss and not es:
        verdict='BLANK_BOTH'
    elif not ss:
        verdict='BLANK_START'
    else:
        start_ok=any(s in ends for s in ss)
        start_strict=base(geo_a) in ss or base(geo_b) in ss
        end_ok=(not es) or any(s in ends for s in es) or any(s in traversed for s in es)
        start_trav=any(s in traversed for s in ss)
        if start_ok and end_ok: verdict='OK'
        elif start_trav and end_ok: verdict='OK_INTERIOR'   # start state is on the line but not at a terminus
        elif start_trav or start_ok: verdict='END_MISMATCH'
        else: verdict='START_MISMATCH'
    rec['verdict']=verdict; rows.append(rec)

out=pd.DataFrame(rows)
out['traversed']=out['traversed'].apply(lambda x: ', '.join(x))
out.to_csv(sys.argv[1] if len(sys.argv)>1 else 'audit.csv',index=False)
print('cohort',len(out),'batch1',out['batch1'].sum())
print(out.groupby(['batch1','verdict']).size().to_string())
