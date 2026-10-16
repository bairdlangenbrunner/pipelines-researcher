"""US gas data center discovery seeds, no length floor (run from repo root).

Plan: docs/plans/2026-10-16_us-gas-datacenter-subfloor.md (Baird rulings 2026-10-16). Three seed sources, each
seed labeled by source in its seed_id prefix and name_hint:
  A. eia:    EIA Natural Gas Pipeline Projects on a 2024-or-later current sheet (or in service 2024+), with no
             STRONG GEM match on the fresh crosswalk (eia_crosswalk_20261016.json), any length, whose demand
             served / notes / name mention data centers or power. Reversals and abandonments dropped. A weak
             crosswalk hit (related / possible / docket) is passed as a hint, not a match: an expansion of a GEM
             system with no row of its own is still a candidate. Plus Nueva Era Dos and PLUSS by name (strong-
             matched to their parent system, under-floor power-demand pipe Baird named).
  B. lead:   the named leads from the gem-desk web survey (grants/beyond-carbon/2026-10-16-...-research-plan.md).
  C. plant:  GOGPT US gas plants tagged `Captive industry type` = data center, plus a notes search (labeled
             'gogpt-notes', GOGPT does not tag them captive), status announced / pre-construction / construction
             or operating with a 2024+ start. One seed per plant (GEM location ID) with coordinates, owner, MW,
             status and the nearest GGIT US routes (EPSG:5070) from goit-ggit-pipeline-routes-normalized.
Inputs: data/GGIT_gas_snapshot_20261016.csv, work/gogpt_20261016.csv (gem-db-ops/gogpt/pull.py --out),
sources/eia_pipeline_projects/data/eia_projects_{latest,long}.csv.
"""
import json, re, glob, os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

D = 'batches/united-states-gas/staging/discovery-datacenter-seeds-20261016'
ROUTES = '../goit-ggit-pipeline-routes-normalized/data/individual-routes/gas-pipelines'
REGION = {
 'tx-permian': 'TX NM',
 'gulf': 'LA MS AL FL GM',
 'appalachian-se': 'PA OH WV VA MD DE DC KY TN GA SC NC',
 'midcon-north': 'OK KS NE IA MO AR IL IN MI WI MN ND SD',
 'west-ne-ak': 'CA NV UT AZ CO WY MT ID OR WA AK NY NJ CT MA RI NH VT ME',
}
ST2R = {s: r for r, ss in REGION.items() for s in ss.split()}
STATE_ABBR = {'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA', 'Colorado': 'CO',
 'Connecticut': 'CT', 'Delaware': 'DE', 'District of Columbia': 'DC', 'Florida': 'FL', 'Georgia': 'GA', 'Idaho': 'ID',
 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME',
 'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM',
 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR',
 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN',
 'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV',
 'Wisconsin': 'WI', 'Wyoming': 'WY'}
DC = re.compile(r'data.?cent|hyperscal|\bAI\b|artificial intel|Stargate|Jupiter|\bMeta\b|Google|Oracle|Amazon|AWS|Microsoft', re.I)
PW = re.compile(r'power|electric|generat|\bplant\b', re.I)
slug = lambda s: re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')[:60].strip('-')

# ---- A. EIA ---------------------------------------------------------------------------------------------
X = json.load(open(f'{D}/eia_crosswalk_20261016.json'))
hits = {}
for pid, r in X['rows'].items():
    for c in r['candidates']:
        hits.setdefault(c['project_key'], []).append((pid, c.get('tier')))
long = pd.read_csv('sources/eia_pipeline_projects/data/eia_projects_long.csv', dtype=str, low_memory=False).fillna('')
e = pd.read_csv('sources/eia_pipeline_projects/data/eia_projects_latest.csv', dtype=str, low_memory=False).fillna('')
current = set(long[(long.sheet_kind == 'current') & (long.release >= '2024-01')].project_key)
yr = pd.to_numeric(e.year_in_service_date.str[:4], errors='coerce')
u = e[e.project_key.isin(current) | (yr >= 2024)].copy()
alltext = long.groupby('project_key')[['demand_served', 'notes', 'project_notes']].agg(lambda s: ' '.join(dict.fromkeys(s)))
u['text'] = u.project_key.map(alltext.apply(' '.join, axis=1)).fillna('') + ' ' + u.project_name
u['dc'] = u.text.str.contains(DC)
u['pw'] = u.text.str.contains(PW)
u['strong'] = u.project_key.map(lambda k: [p for p, t in hits.get(k, []) if t == 'strong'])
u['weak'] = u.project_key.map(lambda k: [f'{p} ({t})' for p, t in hits.get(k, []) if t != 'strong'])
NAMED = re.compile(r'nueva era dos|pluss', re.I)
pick = (u.dc | u.pw) & ~u.project_type.isin(['Reversal', 'Abandonment']) & (
    (u.strong.str.len() == 0) | u.project_name.str.contains(NAMED))
s = u[pick].copy()
s['nkey'] = s.project_name.str.lower().str.replace(r'[^a-z0-9]+', ' ', regex=True).str.strip()

def eia_region(r):
    for st in re.split(r'[^A-Z]+', (r.beg_state + ',' + r.state_s).upper()):
        if st in ST2R:
            return ST2R[st]
    return 'unassigned'

seeds = []
for nkey, g in s.groupby('nkey', sort=False):
    r = g.sort_values('last_release').iloc[-1]
    ops = '; '.join(dict.fromkeys(g.pipeline_operator_name))
    gem = (['strong crosswalk match ' + ', '.join(r.strong)] if r.strong else []) + (
        ['weak crosswalk hints ' + ', '.join(r.weak)] if r.weak else [])
    hint = ['SOURCE A: EIA', f"EIA {r.project_type}", f"EIA status {r.status}" + (f" ({r.status_history})" if r.status_history else ''),
            f"in service {r.year_in_service_date or '?'}", f"states {r.state_s}", f"diameter {r.pipeline_diameter_inches or '?'} in",
            f"capacity +{r.additional_capacity_mmcf_d or '?'} MMcf/d", r.pipeline_type,
            f"demand served: {r.demand_served}" if r.demand_served else '',
            'EIA text names a data center or hyperscaler' if r.dc else 'EIA text names power demand only',
            f"docket {r.docket_number}" if r.docket_number else '', *gem,
            f"EIA cite: {r.last_file} sheet '{r.last_sheet}' row {r.last_excel_row}",
            f"EIA notes: {r.notes_latest[:220]}" if r.notes_latest else '']
    seeds.append({'seed_id': 'eia:' + slug(nkey), 'name': r.project_name, 'length': f"EIA: {r.miles or 'blank'} mi",
                  'operator': ops, 'kind': r.project_type, 'name_hint': ' | '.join(h for h in hint if h),
                  'region': eia_region(r), 'source': 'eia'})

# ---- B. named web-survey leads ----------------------------------------------------------------------------
LEADS = [
 ('abilene-lateral', 'Abilene lateral (Hugh Brinson, Oracle / Stargate campus)', 'Energy Transfer', 'tx-permian', 'EIA-free lead: 14 mi',
  'Texas intrastate lateral off the Hugh Brinson system to the Oracle and OpenAI Stargate campus at Abilene, complete Q2 2026 per Energy Transfer Q2 2026 earnings release (SEC Exhibit 99.1, https://www.sec.gov/Archives/edgar/data/0001276187/000127618726000033/ex991eterq22026.htm). Check overlap with the EIA seed "Oracle Data Center Laterals (Hugh Brinson / North Texas)" and GEM P3885'),
 ('creekside-lateral', 'Creekside lateral', 'Kinder Morgan', 'tx-permian', 'lead: 11.2 mi',
  'Texas, in service Q4 2026, serves power generation, industrial and data center demand per Kinder Morgan Q1 2026 release (SEC, https://www.sec.gov/Archives/edgar/data/0001506307/000150630726000033/kmi2026q18-kex991.htm)'),
 ('amarillo-expansion', 'Amarillo Expansion (NGPL, CP26-581)', 'Natural Gas Pipeline Co of America (Kinder Morgan)', 'tx-permian', 'lead: length unknown',
  'FERC CP26-581 filed September 2026, 550,000 Dth/d, application says gas generates power for a data center in Deaf Smith County, Texas; shipper an Intersect Power affiliate; NGI ties it to Google Project Roman (https://naturalgasintel.com/news/google-data-center-anchors-550000-dthd-ngpl-natural-gas-expansion-in-texas/)'),
 ('dtm-nexus-interconnect', 'DT Midstream NEXUS interconnect for an Ohio data center', 'DT Midstream', 'appalachian-se', 'lead: length unknown',
  '250 MMcf/d interconnect off NEXUS (GEM P0225) serving a behind-the-meter plant for an unnamed Ohio data center, and the MIST open season of up to 1.5 Bcf/d with data center developers among shippers, per DT Midstream Q1 2026 earnings call. May be no new pipe; a lateral of its own is a new row'),
 ('homer-city-supply', 'Homer City gas supply laterals', 'EQT / Texas Eastern / Eastern Gas Transmission', 'appalachian-se', 'lead: length unknown',
  'Homer City Energy Campus, Pennsylvania, 4.4 GW gas plant for a data center campus, up to 665,000 MMBtu/d from EQT via Texas Eastern and Eastern Gas Transmission from 2027 (RBC Capital Markets May 2026). Lateral details unverified: find whether new pipe is built and by whom'),
 ('cheyenne-power-hub', 'Cheyenne Power Hub supply (Rockies Express)', 'Tallgrass Energy', 'west-ne-ak', 'lead: length unknown',
  'Tallgrass Cheyenne Power Hub, Wyoming, gas power for data centers, fed by Rockies Express (GEM P2517 Cheyenne Hub Enhancement is a different, older project). Find the supply lateral, if any'),
 ('kosciusko-junction', 'Kosciusko Junction Pipeline Project (Gulf South)', 'Boardwalk Pipelines (Gulf South Pipeline)', 'gulf', 'lead: about 111 mi',
  'Mississippi, 1.16 Bcf/d, 2028; Boardwalk project page says it supports electric generation, data centers and industrial growth, no customer named (https://bwpipelines.com/project/kosciusko-junction-pipeline-project). Likely GEM P7810 "Kosci Junction Project": confirm, and whether a ref ties it to a data center'),
]
for sid, name, op, reg, length, hint in LEADS:
    seeds.append({'seed_id': f'lead:{sid}', 'name': name, 'length': length, 'operator': op, 'kind': 'web-survey lead',
                  'name_hint': 'SOURCE B: gem-desk web survey 2026-10-16 | ' + hint, 'region': reg, 'source': 'lead'})

# ---- C. GOGPT data center plants ------------------------------------------------------------------------
g = pd.read_csv(f'{D}/work/gogpt_20261016.csv', dtype=str, low_memory=False).fillna('')
g = g[(g['Country/Area'] == 'United States') & g.Fuel.str.contains('fossil gas')]
tag = g['Captive industry type'].str.contains('data cent', case=False)
notes = g.Notes.str.contains(r'data.?cent|hyperscal|artificial intel|Stargate', case=False, regex=True)
sy = pd.to_numeric(g['Start year'], errors='coerce')
live = g.Status.isin(['announced', 'pre-construction', 'construction']) | ((g.Status == 'operating') & (sy >= 2024))
g = g[(tag | notes) & live].assign(tagged=tag)
gem = pd.read_csv(sorted(glob.glob('data/GGIT_gas_snapshot_2026*.csv'))[-1], header=2, low_memory=False,
                  keep_default_na=False, na_values=[])
us = gem[gem.CountriesOrAreas.str.contains('United States', na=False)]
geoms = []
for _, r in us.iterrows():
    f = f'{ROUTES}/{r.ProjectID}.geojson'
    if os.path.exists(f) and os.path.getsize(f) > 0:
        try:
            gg = gpd.read_file(f)
        except Exception:
            continue
        if len(gg) and gg.geometry.notna().any():
            geoms.append({'pid': r.ProjectID, 'label': f"{r.PipelineName}" + (f" / {r.SegmentName}" if r.SegmentName else ''),
                          'status': r.Status, 'geometry': gg.geometry.union_all()})
R = gpd.GeoDataFrame(geoms, crs='EPSG:4326').to_crs('EPSG:5070')
print(len(R), 'US gas routes loaded')
plants = []
for loc, p in g.groupby('GEM location ID', sort=False):
    r = p.iloc[0]
    try:
        pt = gpd.GeoSeries([Point(float(r.Longitude), float(r.Latitude))], crs='EPSG:4326').to_crs('EPSG:5070').iloc[0]
    except ValueError:
        pt = None
    near = []
    if pt is not None:
        d = R.distance(pt) / 1000
        for i in d.nsmallest(3).index:
            if d[i] <= 30:
                near.append(f"{R.pid[i]} {R.label[i]} ({R.status[i]}) {d[i]:.1f} km")
    mw = pd.to_numeric(p['Capacity (MW)'], errors='coerce').sum()
    st = STATE_ABBR.get(r['State/Province'], '')
    statuses = '/'.join(dict.fromkeys(p.Status))
    hint = ['SOURCE C: GOGPT data center plant' + ('' if p.tagged.any() else ' (gogpt-notes: GOGPT does NOT tag it captive for a data center; its notes only mention data centers)'),
            f"GEM location {loc}", f"{len(p)} unit(s), {mw:.0f} MW, status {statuses}",
            f"start {'/'.join(dict.fromkeys(x for x in p['Start year'] if x)) or '?'}",
            f"owner {r['Owner(s)'] or '?'}", f"operator {r['Operator(s)']}" if r['Operator(s)'] else '',
            f"location {r.City + ', ' if r.City else ''}{r['Local area (taluk, county)'] + ', ' if r['Local area (taluk, county)'] else ''}{r['State/Province']} ({r.Latitude}, {r.Longitude}, {r['Location accuracy'] or 'accuracy ?'})",
            'nearest GGIT routes: ' + ('; '.join(near) if near else 'none within 30 km'),
            'GOGPT notes: ' + ' '.join(r.Notes.split())[:260] if r.Notes else '']
    plants.append({'seed_id': f"plant:{loc.lower()}-{slug(r['Plant name'])[:40]}", 'name': f"{r['Plant name']} (gas supply)",
                   'length': 'plant seed: find the supply pipe', 'operator': r['Owner(s)'], 'kind': 'data center gas plant',
                   'name_hint': ' | '.join(h for h in hint if h), 'region': ST2R.get(st, 'unassigned'), 'source': 'plant',
                   'state': st, 'tagged': bool(p.tagged.any())})
seeds += plants

ids = [x['seed_id'] for x in seeds]
assert len(ids) == len(set(ids)), [i for i in ids if ids.count(i) > 1]
json.dump({'seeds': seeds}, open(f'{D}/seeds_by_region.json', 'w'), indent=1, ensure_ascii=False)
df = pd.DataFrame(seeds)
print(len(seeds), 'seeds'); print(pd.crosstab(df.region, df.source, margins=True))
