"""Scoping audit for US gas SLICE 2 (every US gas row not staged in batches 1-5).

Read-only. Re-derives the roster from the scoping worklist, then audits:
  - status / LastUpdated counts and ref-unit counts by status x class
  - StartState/Province + EndState/Province: vocabulary typos, blanks, multi-state cells,
    and a spatial join of each row's routes-repo geometry against Natural Earth admin-1
    (same method as ../state-audit-20260904/audit_states.py)
  - a `derived` slicing state + region, and batch sizing
  - duplicate-looking name pairs (slice 2 internal and slice 2 vs slice 1)
  - oil-looking rows on the gas tab
Usage: python audit_slice2.py <worklist.json> <outdir>
"""
import json, os, re, sys, glob, difflib, collections
import pandas as pd, geopandas as gpd
from shapely.geometry import Point, shape
from shapely.ops import unary_union

WL, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
wl = json.load(open(WL))
CSV = 'data/' + wl['scope']['csv']
ROUTES = '../GOIT-GGIT-pipeline-routes/data/individual-routes/gas-pipelines'
NE = os.path.expanduser('~/Dropbox/_gis-data/_natural_earth_data/ne_10m_admin_1_states_provinces/'
                        'ne_10m_admin_1_states_provinces.shp')

df = pd.read_csv(CSV, header=2, low_memory=False, keep_default_na=False, na_values=[])
df['sheet_row'] = df.index + 4
S2 = sorted({u['project_id'] for u in wl['units']})
s2rows = {(u['project_id'], u['sheet_row']) for u in wl['units']}
us = df[df['CountriesOrAreas'].str.contains('United States', na=False)]
slice2 = us[us.apply(lambda r: (r['ProjectID'], r['sheet_row']) in s2rows, axis=1)].copy()
slice1 = us[~us['ProjectID'].isin(S2) & (us['Status'].str.strip().str.upper() != 'N/A')]
print(f'US gas rows: {len(us)}; slice 2: {len(slice2)} rows / {slice2.ProjectID.nunique()} PIDs; '
      f'slice 1: {len(slice1)}')

# ---- N/A + status + LastUpdated ------------------------------------------------------
na = us[us['Status'].str.strip().str.upper() == 'N/A']
print('\nStatus = N/A (US gas):', na[['ProjectID', 'sheet_row', 'PipelineName', 'SegmentName']].to_dict('records'))
slice2['lu_year'] = slice2['LastUpdated'].astype(str).str[:4]
print('\nstatus counts:\n' + slice2['Status'].value_counts().to_string())
print('\nstatus x LastUpdated year:\n' + pd.crosstab(slice2['Status'], slice2['lu_year']).to_string())

# ---- units by status x class ---------------------------------------------------------
u = pd.DataFrame(wl['units'])
print('\nunits by status x class:\n' + pd.crosstab(u['status'], u['class'], margins=True).to_string())

# ---- state vocabulary ----------------------------------------------------------------
adm = gpd.read_file(NE)
adm = adm[adm['iso_a2'].isin(['US', 'MX', 'CA'])][['name', 'iso_a2', 'geometry']].to_crs(4326)
VALID = set(adm['name'].dropna()) | {'Gulf of Mexico', 'Gulf of America', 'Offshore', 'Federal Offshore'}
sidx = adm.sindex

def split_states(v):
    v = str(v).strip()
    return [s.strip() for s in re.split(r'[;,/]| and ', v) if s.strip()] if v else []

def fix(s):
    if s in VALID: return s, None
    m = difflib.get_close_matches(s, sorted(VALID), n=1, cutoff=0.8)
    return (m[0], 'typo') if m else (s, 'unknown')

def state_at(pt):
    c = adm.iloc[list(sidx.query(pt, predicate='intersects'))]
    if len(c): return c.iloc[0]['name']
    d = adm.distance(pt); i = d.idxmin()
    return f"{adm.loc[i, 'name']}~offshore" if d[i] < 0.5 else None

rows = []
for _, r in slice2.iterrows():
    pid = r['ProjectID']
    ss, es = split_states(r['StartState/Province']), split_states(r['EndState/Province'])
    ssf = [fix(s) for s in ss]; esf = [fix(s) for s in es]
    typos = [f'{a}->{b}' for a, (b, k) in zip(ss + es, ssf + esf) if k == 'typo']
    unknown = [a for a, (b, k) in zip(ss + es, ssf + esf) if k == 'unknown']
    ssn = [b for b, _ in ssf]; esn = [b for b, _ in esf]
    geo_a = geo_b = None; trav = []
    fp = f'{ROUTES}/{pid}.geojson'
    if os.path.exists(fp):
        try:
            gs = [shape(f['geometry']) for f in json.load(open(fp)).get('features', []) if f.get('geometry')]
            gs = [g for g in gs if not g.is_empty]
            if gs:
                g = unary_union(gs) if len(gs) > 1 else gs[0]
                lines = [g] if g.geom_type == 'LineString' else list(getattr(g, 'geoms', []))
                lines = [l for l in lines if l.geom_type == 'LineString']
                if lines:
                    geo_a, geo_b = state_at(Point(lines[0].coords[0])), state_at(Point(lines[-1].coords[-1]))
                trav = sorted(set(adm.iloc[list(sidx.query(g, predicate='intersects'))]['name']))
        except Exception as e:
            geo_a = f'ERR {str(e)[:40]}'
    base = lambda s: s.split('~')[0] if s else None
    ends = {base(geo_a), base(geo_b)} - {None}
    if geo_a is None: verdict = 'NO_ROUTE'
    elif not ssn and not esn: verdict = 'BLANK_BOTH'
    elif not ssn: verdict = 'BLANK_START'
    else:
        s_end = any(s in ends for s in ssn); s_tr = any(s in trav for s in ssn)
        e_ok = (not esn) or any(s in ends or s in trav for s in esn)
        verdict = ('OK' if s_end and e_ok else 'OK_INTERIOR' if s_tr and e_ok
                   else 'END_MISMATCH' if (s_end or s_tr) else 'START_MISMATCH')
    # derived slicing state: sheet start (typo-fixed) unless geometry contradicts it
    if verdict in ('OK', 'OK_INTERIOR', 'END_MISMATCH') or (verdict == 'NO_ROUTE' and ssn):
        derived = ssn[0]
    elif verdict == 'START_MISMATCH' or verdict.startswith('BLANK'):
        derived = base(geo_a) or (esn[0] if esn else '')
    else:
        derived = esn[0] if esn else ''
    states_all = sorted(set(ssn + esn) | set(trav))
    rows.append(dict(pid=pid, sheet_row=r['sheet_row'], status=r['Status'], lu=r['LastUpdated'],
                     name=r['PipelineName'], seg=r['SegmentName'], fuel=r['Fuel'],
                     start_state=r['StartState/Province'], end_state=r['EndState/Province'],
                     start_country=r['StartCountryOrArea'], end_country=r['EndCountryOrArea'],
                     countries=r['CountriesOrAreas'], route_type=r['RouteType'],
                     route_acc=r['RouteAccuracy'], geo_first=geo_a, geo_last=geo_b,
                     traversed=', '.join(trav), verdict=verdict, typos='; '.join(typos),
                     unknown='; '.join(unknown), multi_cell=len(ss) > 1 or len(es) > 1,
                     n_states=len(states_all), derived=derived))
a = pd.DataFrame(rows)

REG = {
 'Texas': 'TX',
 'Louisiana': 'Gulf', 'Mississippi': 'Gulf', 'Alabama': 'Gulf', 'Florida': 'Gulf',
 'Gulf of Mexico': 'Gulf', 'Gulf of America': 'Gulf',
 'Ohio': 'Appalachian', 'Pennsylvania': 'Appalachian', 'West Virginia': 'Appalachian',
 'New York': 'Appalachian', 'New Jersey': 'Appalachian', 'Maryland': 'Appalachian',
 'Delaware': 'Appalachian', 'Virginia': 'Appalachian', 'Michigan': 'Appalachian',
 'Indiana': 'Appalachian', 'District of Columbia': 'Appalachian',
 'Kentucky': 'Southeast', 'Tennessee': 'Southeast', 'North Carolina': 'Southeast',
 'South Carolina': 'Southeast', 'Georgia': 'Southeast',
 'Massachusetts': 'NewEngland', 'Connecticut': 'NewEngland', 'Rhode Island': 'NewEngland',
 'New Hampshire': 'NewEngland', 'Vermont': 'NewEngland', 'Maine': 'NewEngland',
 'Oklahoma': 'Midcontinent', 'Kansas': 'Midcontinent', 'Arkansas': 'Midcontinent',
 'Missouri': 'Midcontinent', 'Illinois': 'Midcontinent', 'Iowa': 'Midcontinent',
 'Nebraska': 'Midcontinent',
 'Alaska': 'Alaska',
}
a['derived'] = a['derived'].str.replace('~offshore', '', regex=False)
a['region'] = a['derived'].map(lambda s: REG.get(s, 'West' if s else 'UNKNOWN'))
a.loc[a['derived'].isin(adm[adm.iso_a2 != 'US']['name']), 'region'] = 'CrossBorder'
a['group'] = a['status'].map(lambda s: 'op/idle' if s in ('operating', 'idle') else
                             'cancelled' if s == 'cancelled' else 'in-dev')
a.to_csv(f'{OUT}/slice2_state_audit.csv', index=False)

print('\nverdict counts:\n' + a['verdict'].value_counts().to_string())
print('\ntypos:\n' + a[a.typos != ''][['pid', 'sheet_row', 'status', 'typos']].to_string(index=False))
print('\nunknown state tokens:\n' + a[a.unknown != ''][['pid', 'sheet_row', 'unknown']].to_string(index=False))
print('\nmismatch/blank rows:\n' + a[a.verdict.isin(['START_MISMATCH', 'END_MISMATCH', 'BLANK_START', 'BLANK_BOTH'])]
      [['pid', 'sheet_row', 'status', 'start_state', 'end_state', 'geo_first', 'geo_last', 'verdict']].to_string(index=False))
print(f"\nmulti-state: {int(a.multi_cell.sum())} rows with >1 state in a cell; "
      f"{int((a.n_states > 1).sum())} rows touching >1 state (cells + route)")
print('\nno-route rows with blank start state:\n' + a[(a.verdict == 'NO_ROUTE') & (a.start_state.str.strip() == '')]
      [['pid', 'sheet_row', 'status', 'end_state', 'name']].to_string(index=False))
print('\nregion x group:\n' + pd.crosstab(a['region'], a['group'], margins=True).to_string())
ucount = u.groupby('project_id').size()
a['units'] = a['pid'].map(ucount)
print('\nunits region x group:\n' + a.pivot_table(index='region', columns='group', values='units',
                                                    aggfunc='sum', margins=True, fill_value=0).to_string())

# ---- duplicates ----------------------------------------------------------------------
def norm(s):
    s = re.sub(r'\b(pipeline|pipe line|gas|natural|project|system|expansion|lateral|llc|company)\b',
               ' ', str(s).lower())
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()
def key(r): return norm(f"{r['PipelineName']} {r['SegmentName']}")
s2 = slice2.assign(k=slice2.apply(key, axis=1)); s1 = slice1.assign(k=slice1.apply(key, axis=1))
pairs = []
for i, x in enumerate(s2.itertuples()):
    for y in list(s2.itertuples())[i + 1:] + list(s1.itertuples()):
        if x.ProjectID == y.ProjectID: continue
        rt = difflib.SequenceMatcher(None, x.k, y.k).ratio()
        if rt >= 0.9 or (x.k and x.k == y.k):
            pairs.append(dict(a=x.ProjectID, a_status=x.Status, a_name=f'{x.PipelineName} | {x.SegmentName}',
                              b=y.ProjectID, b_status=y.Status, b_name=f'{y.PipelineName} | {y.SegmentName}',
                              b_slice=2 if y.ProjectID in S2 else 1, ratio=round(rt, 3)))
dp = pd.DataFrame(pairs).sort_values('ratio', ascending=False) if pairs else pd.DataFrame()
dp.to_csv(f'{OUT}/slice2_duplicate_candidates.csv', index=False)
pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 70)
print(f'\nduplicate-looking pairs ({len(dp)}):\n' + (dp.to_string(index=False) if len(dp) else 'none'))
multi = slice2.groupby('ProjectID').size(); print('multi-segment PIDs in slice 2:', multi[multi > 1].to_dict())

# ---- oil-looking -----------------------------------------------------------------------
OILRX = r'\b(crude|oil|ngl|condensate|products?|propane|ethane|butane|refined|co2|carbon dioxide|hydrogen|water)\b'
oil = slice2[(slice2['Fuel'].str.strip() != 'Gas') |
             slice2.apply(lambda r: bool(re.search(OILRX, f"{r['PipelineName']} {r['SegmentName']} {r['OtherEnglishNames']}".lower())), axis=1)]
print('\noil-looking / non-Gas fuel:\n' + oil[['ProjectID', 'sheet_row', 'Status', 'Fuel', 'PipelineName', 'SegmentName']].to_string(index=False))
