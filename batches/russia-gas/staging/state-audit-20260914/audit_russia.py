"""State audit + batch plan for the Russia gas campaign (port of the US slice-2 audit).

Read-only. Takes the scoped worklist (252 rows: Russia gas minus the 33 carried PIDs),
then audits:
  - status / LastUpdated counts and ref-unit counts by status x class
  - StartState/Province + EndState/Province: federal-subject vocabulary (typos, `X region`
    vs `X Oblast`, `Republic of X` vs `X Republic`, bare names), blanks, multi-subject
    cells, and a spatial join of each row's routes-repo geometry against Natural Earth
    admin-1 (projected to EPSG:3576 for the offshore nearest-subject fallback)
  - Russia-specific rules: Tyumen Oblast contains KhMAO + YaNAO, Arkhangelsk contains NAO
    (vocabulary, not a mismatch); sheet start == geometry end and vice versa is a direction
    swap (`OK_REVERSED`), not an error; a foreign terminus is a cross-border flag only
  - a `derived` slicing subject -> real federal district (8 districts, post-2018; NE's
    `region` column is coarser and stale for Buryatia/Zabaykalsky) -> batch (R1..R7)
  - duplicate-looking name pairs (in-scope vs in-scope and in-scope vs carried)
  - oil-looking rows on the gas tab
Writes region_audit.csv, duplicate_candidates.csv, batch_plan.csv and, per batch,
batches/<batch>/include_pids.txt + exclude_pids.txt (complement of the Russia roster +
the carried PIDs — the union rule means a slice is cut with --exclude-pids, never
--include-pids alone).
Usage: python audit_russia.py <worklist.json> <outdir>
"""
import json, os, re, sys, difflib
import pandas as pd, geopandas as gpd
from shapely.geometry import Point, shape
from shapely.ops import unary_union

sys.path.insert(0, 'scripts')
from normalize import split_countries  # noqa: E402

WL, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
wl = json.load(open(WL))
CSV = 'data/' + wl['scope']['csv']
ROUTES = '../GOIT-GGIT-pipeline-routes/data/individual-routes/gas-pipelines'
NE = os.path.expanduser('~/Dropbox/_gis-data/_natural_earth_data/ne_10m_admin_1_states_provinces/'
                        'ne_10m_admin_1_states_provinces.shp')
CARRIED = [l.split('#')[0].strip() for l in open('batches/russia-gas/carried_from_others.txt')
           if l.split('#')[0].strip()]

df = pd.read_csv(CSV, header=2, low_memory=False, keep_default_na=False, na_values=[])
df['sheet_row'] = df.index + 4
IN = sorted({u['project_id'] for u in wl['units']})
inrows = {(u['project_id'], u['sheet_row']) for u in wl['units']}
ru = df[df['CountriesOrAreas'].map(lambda s: 'russia' in split_countries(s))]
scope = ru[ru.apply(lambda r: (r['ProjectID'], r['sheet_row']) in inrows, axis=1)].copy()
carried = ru[ru['ProjectID'].isin(CARRIED)]
print(f'Russia gas rows: {len(ru)}; in scope: {len(scope)} rows / {scope.ProjectID.nunique()} PIDs; '
      f'carried: {len(carried)}; N/A: {int((ru.Status.str.strip().str.upper() == "N/A").sum())}')

scope['lu_year'] = scope['LastUpdated'].astype(str).str[:4]
print('\nstatus counts:\n' + scope['Status'].value_counts().to_string())
print('\nstatus x LastUpdated year:\n' + pd.crosstab(scope['Status'], scope['lu_year']).to_string())
u = pd.DataFrame(wl['units'])
print('\nunits by status x class:\n' + pd.crosstab(u['status'], u['class'], margins=True).to_string())

# ---- Natural Earth: canonical subject = NE name_en (RU) ---------------------------------
adm = gpd.read_file(NE)[['name', 'name_en', 'iso_a2', 'type_en', 'geometry']].to_crs(4326)
adm.loc[(adm.iso_a2 == 'RU') & (adm.name == 'Altay'), 'name_en'] = 'Altai Krai'   # NE mislabels the krai
adm.loc[(adm.iso_a2 == 'RU') & (adm.name == 'Chita'), 'name_en'] = 'Zabaykalsky Krai'
adm['name_en'] = adm['name_en'].fillna(adm['name'])
adm = adm[adm['name_en'].notna()].copy()
adm['canon'] = adm.apply(lambda r: r['name_en'] if r['iso_a2'] == 'RU' else f"{r['name_en']} ({r['iso_a2']})", axis=1)
RU_SUBJECTS = set(adm[adm.iso_a2 == 'RU']['canon'])
sidx = adm.sindex
NEIGHBOURS = ['RU', 'NO', 'FI', 'SE', 'DK', 'EE', 'LV', 'LT', 'PL', 'DE', 'BY', 'UA', 'GE', 'AZ', 'AM', 'TR',
              'BG', 'RO', 'KZ', 'UZ', 'TM', 'IR', 'MN', 'CN', 'KP', 'KR', 'JP']
adm_p = adm[adm.iso_a2.isin(NEIGHBOURS)].to_crs(3576).reset_index(drop=True)  # North Pole LAEA Russia — metres;
sidx_p = adm_p.sindex                                                           # neighbours only (Antarctica explodes in 3576)

DISTRICT = {}
for d, names in {
    'Central': ['Belgorod', 'Bryansk', 'Vladimir', 'Voronezh', 'Ivanovo', 'Kaluga', 'Kostroma', 'Kursk',
                'Lipetsk', 'Moscow Oblast', 'Moscow', 'Oryol', 'Ryazan', 'Smolensk', 'Tambov', 'Tver', 'Tula',
                'Yaroslavl'],
    'Northwestern': ['Arkhangelsk', 'Vologda', 'Kaliningrad', 'Republic of Karelia', 'Komi', 'Leningrad',
                     'Murmansk', 'Nenets', 'Novgorod', 'Pskov', 'Saint Petersburg'],
    'Southern': ['Republic of Adygea', 'Astrakhan', 'Volgograd', 'Republic of Kalmykia', 'Krasnodar',
                 'Rostov', 'Autonomous Republic of Crimea', 'Sevastopol'],
    'North Caucasian': ['Republic of Dagestan', 'Republic of Ingushetia', 'Kabardino-Balkar',
                        'Karachay-Cherkess', 'Republic of North Ossetia-Alania', 'Chechen', 'Stavropol'],
    'Volga': ['Republic of Bashkortostan', 'Kirov', 'Mari El', 'Republic of Mordovia', 'Nizhny Novgorod',
              'Orenburg', 'Penza', 'Perm', 'Samara', 'Saratov', 'Republic of Tatarstan', 'Udmurt',
              'Ulyanovsk', 'Chuvash'],
    'Ural': ['Kurgan', 'Sverdlovsk', 'Tyumen', 'Khanty-Mansi', 'Chelyabinsk', 'Yamalo-Nenets'],
    'Siberian': ['Altai Republic', 'Altai Krai', 'Irkutsk', 'Kemerovo', 'Krasnoyarsk', 'Novosibirsk', 'Omsk',
                 'Tomsk', 'Tuva', 'Republic of Khakassia'],
    'Far Eastern': ['Amur', 'Republic of Buryatia', 'Jewish', 'Zabaykalsky', 'Kamchatka', 'Magadan',
                    'Primorsky', 'Sakha', 'Sakhalin', 'Khabarovsk', 'Chukotka'],
}.items():
    for n in names:
        hits = [c for c in RU_SUBJECTS if c == n or c.startswith(n + ' ') or c.startswith(n + '-')]
        if n == 'Moscow': hits = ['Moscow']
        for h in hits: DISTRICT[h] = d
unmapped = RU_SUBJECTS - set(DISTRICT)
assert not unmapped, f'subjects without a district: {unmapped}'

# ---- sheet vocabulary normaliser --------------------------------------------------------
ALIAS = {
    'yakutia': 'Sakha Republic', 'republic of sakha': 'Sakha Republic',
    'republic of sakha (yakutia)': 'Sakha Republic', 'respublic of sakha (yakutia)': 'Sakha Republic',
    'sakha republic': 'Sakha Republic',
    'north ossetia': 'Republic of North Ossetia-Alania',
    'republic of north ossetia': 'Republic of North Ossetia-Alania',
    'republic of udmurtia': 'Udmurt Republic', 'republic of chuvashia': 'Chuvash Republic',
    'nizhgorod oblast': 'Nizhny Novgorod Oblast',
    'yamalo-nenets oblast': 'Yamalo-Nenets Autonomous Okrug',
    'chukotka autonomus district': 'Chukotka Autonomous Okrug',
    'chukotka autonomous district': 'Chukotka Autonomous Okrug',
    'altai territory': 'Altai Krai', 'republic of altai': 'Altai Republic',
    'moscow region': 'Moscow Oblast', 'moscow oblast': 'Moscow Oblast',
    'st. petersburg': 'Saint Petersburg', 'saint petersburg': 'Saint Petersburg', 'st petersburg': 'Saint Petersburg',
    'komi republic': 'Komi Republic', 'republic of komi': 'Komi Republic',
    'republic of karelia': 'Republic of Karelia', 'karelia': 'Republic of Karelia',
}
FOREIGN = {  # sheet tokens that are not Russian subjects — country of the foreign terminus
    'estonia': 'EE', 'latvia': 'LV', 'lithuania': 'LT', 'finland': 'FI', 'belarus': 'BY', 'ukraine': 'UA',
    'mecklenburg-vorpommern': 'DE', 'kırklareli': 'TR', 'ankara': 'TR', 'hokkaido': 'JP',
    'heilongjiang': 'CN', 'jilin': 'CN', 'xinjiang': 'CN', 'shanghai': 'CN', 'kyakhta': 'RU:Republic of Buryatia',
    'udine and lower austria': 'IT/AT', 'republic of south ossetia': 'GE', 'selenge province': 'MN',
    'georgia': 'GE', 'azerbaijan': 'AZ', 'kazakhstan': 'KZ', 'uzbekistan': 'UZ', 'turkmenistan': 'TM',
    'iran': 'IR', 'mongolia': 'MN', 'china': 'CN', 'turkey': 'TR', 'türkiye': 'TR', 'germany': 'DE',
}
CANON_LOWER = {c.lower(): c for c in RU_SUBJECTS}

def split_states(v):
    v = str(v).strip()
    return [s.strip() for s in re.split(r'[;/]| and ', v) if s.strip()] if v else []

def canon_subject(s):
    """-> (canonical, kind) kind in {ok, typo, foreign, unknown}."""
    raw = s; k = s.strip().lower()
    if k in ALIAS: return ALIAS[k], ('ok' if ALIAS[k].lower() == k else 'typo')
    if k in FOREIGN:
        f = FOREIGN[k]
        if f.startswith('RU:'): return f[3:], 'typo'   # a town used as a subject
        return f'{raw} ({f})', 'foreign'
    k2 = re.sub(r'\bautonomus\b', 'autonomous', k)
    k2 = re.sub(r'\b(respublic|reublic|repulic)\b', 'republic', k2)
    k2 = re.sub(r'\boblas\b', 'oblast', k2)
    k2 = re.sub(r'\bregion\b', 'oblast', k2)
    k2 = re.sub(r'\bterritory\b', 'krai', k2)
    k2 = re.sub(r'\bautonomous district\b', 'autonomous okrug', k2)
    if k2 in CANON_LOWER: return CANON_LOWER[k2], ('ok' if k2 == k else 'typo')
    # Republic of X <-> X Republic
    m = re.match(r'republic of (.+)', k2)
    for cand in ([f'{m.group(1)} republic', k2] if m else [f'republic of {k2}', f'{k2} republic']):
        if cand in CANON_LOWER: return CANON_LOWER[cand], 'typo'
    # bare name -> Oblast / Krai / Republic
    for suf in (' oblast', ' krai', ' republic'):
        if k2 + suf in CANON_LOWER: return CANON_LOWER[k2 + suf], 'typo'
    mm = difflib.get_close_matches(k2, list(CANON_LOWER), n=1, cutoff=0.85)
    if mm: return CANON_LOWER[mm[0]], 'typo'
    return raw, 'unknown'

# containment: sheet says the parent, geometry lands in the enclave (vocabulary, not mismatch)
CONTAINS = {'Tyumen Oblast': {'Khanty-Mansi Autonomous Okrug', 'Yamalo-Nenets Autonomous Okrug'},
            'Arkhangelsk Oblast': {'Nenets Autonomous Okrug'},
            'Moscow Oblast': {'Moscow'}, 'Leningrad Oblast': {'Saint Petersburg'}}
def same(a, b):
    return a == b or b in CONTAINS.get(a, ()) or a in CONTAINS.get(b, ())

def subject_at(pt):
    c = adm.iloc[list(sidx.query(pt, predicate='intersects'))]
    if len(c): return c.iloc[0]['canon']
    ptp = gpd.GeoSeries([pt], crs=4326).to_crs(3576).iloc[0]
    near = list(sidx_p.nearest(ptp, return_all=False)[1])
    if near:
        d = adm_p.iloc[near[0]].geometry.distance(ptp)
        if d < 60_000: return f"{adm_p.iloc[near[0]]['canon']}~offshore"
    return None

def district_of(canon):
    if not canon: return ''
    base = canon.split('~')[0]
    return DISTRICT.get(base, 'FOREIGN' if base not in RU_SUBJECTS else '')

rows = []
for _, r in scope.iterrows():
    pid = r['ProjectID']
    ss, es = split_states(r['StartState/Province']), split_states(r['EndState/Province'])
    ssf = [canon_subject(s) for s in ss]; esf = [canon_subject(s) for s in es]
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
                    geo_a, geo_b = subject_at(Point(lines[0].coords[0])), subject_at(Point(lines[-1].coords[-1]))
                trav = sorted(set(adm.iloc[list(sidx.query(g, predicate='intersects'))]['canon']))
        except Exception as e:
            geo_a = f'ERR {str(e)[:40]}'
    base = lambda s: s.split('~')[0] if s else None
    ga, gb = base(geo_a), base(geo_b)
    ends = {ga, gb} - {None}
    def hit(names, cands): return any(same(n, c) for n in names for c in cands)
    if geo_a is None: verdict = 'NO_ROUTE'
    elif not ssn and not esn: verdict = 'BLANK_BOTH'
    elif not ssn: verdict = 'BLANK_START'
    else:
        s_end = hit(ssn, ends); s_tr = hit(ssn, trav)
        e_ok = (not esn) or hit(esn, ends) or hit(esn, trav)
        reversed_ = bool(ga and gb and hit(ssn, [gb]) and esn and hit(esn, [ga]) and not hit(ssn, [ga]))
        verdict = ('OK_REVERSED' if reversed_ else 'OK' if s_end and e_ok else 'OK_INTERIOR' if s_tr and e_ok
                   else 'END_MISMATCH' if (s_end or s_tr) else 'START_MISMATCH')
    # derived slicing subject: the RUSSIAN terminus (start unless foreign), sheet unless geometry contradicts
    def first_ru(names): return next((n for n in names if n in RU_SUBJECTS), None)
    if verdict in ('OK', 'OK_INTERIOR', 'END_MISMATCH', 'OK_REVERSED') or (verdict == 'NO_ROUTE' and ssn):
        derived = first_ru(ssn) or first_ru(esn) or (ssn[0] if ssn else '')
    elif verdict == 'START_MISMATCH' or verdict.startswith('BLANK'):
        derived = (ga if ga in RU_SUBJECTS else None) or first_ru(ssn) or first_ru(esn) \
                  or (gb if gb in RU_SUBJECTS else None) or ga or (esn[0] if esn else '')
    else:
        derived = first_ru(esn) or (esn[0] if esn else '')
    derived = derived or ''
    cross = sorted({n for n in ssn + esn + list(ends) if n and n not in RU_SUBJECTS})
    rows.append(dict(pid=pid, sheet_row=r['sheet_row'], status=r['Status'], lu=r['LastUpdated'],
                     name=r['PipelineName'], seg=r['SegmentName'], fuel=r['Fuel'], ptype=r['PipelineType'],
                     start_state=r['StartState/Province'], end_state=r['EndState/Province'],
                     start_country=r['StartCountryOrArea'], end_country=r['EndCountryOrArea'],
                     countries=r['CountriesOrAreas'], route_type=r['RouteType'],
                     route_acc=r['RouteAccuracy'], geo_first=geo_a, geo_last=geo_b,
                     traversed=', '.join(trav), verdict=verdict, typos='; '.join(typos),
                     unknown='; '.join(unknown), multi_cell=len(ss) > 1 or len(es) > 1,
                     cross_border='; '.join(cross), derived=derived, district=district_of(derived)))
a = pd.DataFrame(rows)
a['group'] = a['status'].map(lambda s: 'op/idle' if s in ('operating', 'idle', 'mothballed', 'retired') else
                             'cancelled' if s == 'cancelled' else 'in-dev')
ucount = u.groupby('project_id').size()
a['units'] = a['pid'].map(ucount).fillna(0).astype(int)

BATCH = {'Far Eastern': 'r1-fareast', 'Volga': 'r5-volga', 'Siberian': 'r6-siberia',
         'Central': 'r7-central-south', 'Southern': 'r7-central-south', 'North Caucasian': 'r7-central-south'}
def batch_of(r):
    if r['district'] == 'Northwestern':
        return 'r2-nw-operating' if r['group'] == 'op/idle' else 'r3-nw-indev'
    if r['district'] == 'Ural':   # 53 rows / 798 units whole — split YaNAO (30) from the southern subjects (23)
        return 'r4a-urals-yanao' if r['derived'] == 'Yamalo-Nenets Autonomous Okrug' else 'r4b-urals-south'
    return BATCH.get(r['district'], 'UNASSIGNED')
a['batch'] = a.apply(batch_of, axis=1)
# manual placements for rows with no Russian terminus in sheet or geometry (reason in region_audit `manual`)
MANUAL = {
    'P1472': ('r7-central-south', 'North Caucasus–Transcaucasus trunk (Mozdok–Tbilisi–Yerevan): Russian leg is Stavropol/N. Ossetia'),
    'P2227': ('r7-central-south', 'Blue Stream onshore Turkish leg — researched with the Blue Stream family (Stavropol)'),
    'P4559': ('r1-fareast', 'Sakhalin–China (Jilin) proposal — Far Eastern export family'),
    'P5409': ('r1-fareast', 'Soyuz Vostok / Power of Siberia 2 family (Buryatia start per sheet)'),
    'P5656': ('r7-central-south', 'Petrovsk (Saratov Obl.)–Elets (Lipetsk Obl.), no geometry; Central terminus'),
}
a['manual'] = a['pid'].map(lambda p: MANUAL.get(p, ('', ''))[1])
a.loc[a['pid'].isin(MANUAL), 'batch'] = a.loc[a['pid'].isin(MANUAL), 'pid'].map(lambda p: MANUAL[p][0])
a.to_csv(f'{OUT}/region_audit.csv', index=False)

print('\nverdict counts:\n' + a['verdict'].value_counts().to_string())
pd.set_option('display.width', 250); pd.set_option('display.max_colwidth', 60)
print('\ntypos (sheet -> canonical):\n' + a[a.typos != ''][['pid', 'sheet_row', 'status', 'typos']].to_string(index=False))
print('\nunknown subject tokens:\n' + a[a.unknown != ''][['pid', 'sheet_row', 'unknown']].to_string(index=False))
print('\nmismatch/blank rows:\n' + a[a.verdict.isin(['START_MISMATCH', 'END_MISMATCH', 'BLANK_START', 'BLANK_BOTH'])]
      [['pid', 'sheet_row', 'status', 'start_state', 'end_state', 'geo_first', 'geo_last', 'verdict']].to_string(index=False))
print('\nreversed (direction, not error):\n' + a[a.verdict == 'OK_REVERSED'][['pid', 'sheet_row', 'start_state', 'end_state', 'geo_first', 'geo_last']].to_string(index=False))
print(f"\nmulti-subject cells: {int(a.multi_cell.sum())}; cross-border rows: {int((a.cross_border != '').sum())}")
print('\nno-route rows:\n' + a[a.verdict == 'NO_ROUTE'][['pid', 'sheet_row', 'status', 'start_state', 'end_state', 'name']].to_string(index=False))
print('\nunassigned:\n' + a[a.batch == 'UNASSIGNED'][['pid', 'sheet_row', 'status', 'start_state', 'end_state', 'geo_first', 'geo_last', 'derived', 'verdict']].to_string(index=False))
print('\ndistrict x group:\n' + pd.crosstab(a['district'], a['group'], margins=True).to_string())
print('\nbatch x group (rows):\n' + pd.crosstab(a['batch'], a['group'], margins=True).to_string())
print('\nbatch units:\n' + a.groupby('batch')['units'].agg(['count', 'sum']).to_string())
plan = a.groupby('batch').agg(rows=('pid', 'count'), pids=('pid', 'nunique'), units=('units', 'sum'),
                              in_dev=('group', lambda s: int((s == 'in-dev').sum())),
                              op=('group', lambda s: int((s == 'op/idle').sum())),
                              cancelled=('group', lambda s: int((s == 'cancelled').sum()))).reset_index()
plan.to_csv(f'{OUT}/batch_plan.csv', index=False)

# ---- per-batch include / exclude files ---------------------------------------------------
ALL_RU = sorted(set(ru['ProjectID']))
for b, grp in a.groupby('batch'):
    if b == 'UNASSIGNED': continue
    d = f'{OUT}/batches/{b}'; os.makedirs(d, exist_ok=True)
    inc = sorted(set(grp['pid']))
    exc = sorted((set(ALL_RU) - set(inc)) | set(CARRIED))
    open(f'{d}/include_pids.txt', 'w').write('\n'.join(inc) + '\n')
    open(f'{d}/exclude_pids.txt', 'w').write('\n'.join(exc) + '\n')
    assert not set(inc) & set(exc)

# ---- duplicates ----------------------------------------------------------------------
def norm(s):
    s = re.sub(r'\b(pipeline|pipe line|gas|natural|project|system|expansion|lateral|llc|company|trunk|trunkline|main)\b',
               ' ', str(s).lower())
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()
def key(r): return norm(f"{r['PipelineName']} {r['SegmentName']}")
s2 = scope.assign(k=scope.apply(key, axis=1)); s1 = carried.assign(k=carried.apply(key, axis=1))
pairs = []
for i, x in enumerate(s2.itertuples()):
    for y in list(s2.itertuples())[i + 1:] + list(s1.itertuples()):
        if x.ProjectID == y.ProjectID: continue
        rt = difflib.SequenceMatcher(None, x.k, y.k).ratio()
        if rt >= 0.9 or (x.k and x.k == y.k):
            pairs.append(dict(a=x.ProjectID, a_status=x.Status, a_name=f'{x.PipelineName} | {x.SegmentName}',
                              b=y.ProjectID, b_status=y.Status, b_name=f'{y.PipelineName} | {y.SegmentName}',
                              b_carried=y.ProjectID in CARRIED, ratio=round(rt, 3)))
dp = pd.DataFrame(pairs).sort_values('ratio', ascending=False) if pairs else pd.DataFrame()
dp.to_csv(f'{OUT}/duplicate_candidates.csv', index=False)
print(f'\nduplicate-looking pairs ({len(dp)}):\n' + (dp.to_string(index=False) if len(dp) else 'none'))
multi = scope.groupby('ProjectID').size(); print('multi-segment PIDs in scope:', multi[multi > 1].to_dict())

# ---- oil-looking -----------------------------------------------------------------------
OILRX = r'\b(crude|oil|ngl|condensate|products?|propane|ethane|butane|refined|co2|carbon dioxide|hydrogen|water|helium)\b'
oil = scope[(scope['Fuel'].str.strip() != 'Gas') |
            scope.apply(lambda r: bool(re.search(OILRX, f"{r['PipelineName']} {r['SegmentName']} {r['OtherEnglishNames']}".lower())), axis=1)]
print('\noil-looking / non-Gas fuel:\n' + oil[['ProjectID', 'sheet_row', 'Status', 'Fuel', 'PipelineName', 'SegmentName']].to_string(index=False))
print('\nPipelineType counts:\n' + scope['PipelineType'].value_counts(dropna=False).to_string())
