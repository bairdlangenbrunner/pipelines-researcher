"""Step 0 seed list for the Russia gas discovery pass (run from the repo root).

Inputs : OSM §2 recon (recon-osm-20260930) DISCOVERY_CANDIDATE additions, GulfPub recon 20260914
         (DISCOVERY_CANDIDATE + FRAGMENT_OF_EXISTING), the 20260930 GGIT snapshot, the routes-repo mirror,
         and hand-curated leads from the R1-R7 validity stores (store_leads.json).
Method : OSM — named features only, stubs merged by normalized name, total length >= 25 km -> candidate,
         < 25 km -> monitor; match-to-existing first (geometry coverage by the roster's drawn routes,
         name similarity to every roster name variant); district = largest share of length by federal
         district (district_join.py, the state-audit's Natural Earth join).
Output : seeds_by_district.{csv,json}
Usage  : python batches/russia-gas/staging/discovery-seeds-20260930/build_seeds.py
"""
import json, os, sys, re, collections
import pandas as pd
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
import geopandas as gpd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, 'scripts')
import district_join as DJ                      # noqa: E402
import normalize as N                           # noqa: E402
import route_compare as RC                      # noqa: E402
from rapidfuzz import fuzz                      # noqa: E402

ST = 'batches/russia-gas/staging'
OSM = f'{ST}/recon-osm-20260930'
GP = f'{ST}/recon-gulfpub-20260914'
MIN_KM = 25.0
COVER_BUF_KM = 1.5

# ---- roster (285 Russia rows) --------------------------------------------------------------
df = pd.read_csv('data/GGIT_gas_snapshot_20260930.csv', header=2, low_memory=False, keep_default_na=False, na_values=[])
ru = df[df['CountriesOrAreas'].map(lambda s: 'russia' in N.split_countries(s))]
NAMECOLS = ['PipelineName', 'OtherEnglishNames', 'OtherLanguagePrimaryPipelineName', 'OtherLanguageAlternativePipelineNames']
roster_names = []                               # (pid, normalized variant)
for _, r in ru.iterrows():
    for c in NAMECOLS:
        for part in re.split(r'[;|/]', str(r[c])):
            n = N.normalize_name(part, drop_stopwords=True)
            if n:
                roster_names.append((r['ProjectID'], n))
print(f'roster rows {len(ru)}; name variants {len(roster_names)}')

# drawn-route coverage layer (metric, EPSG:3576)
geoms = []
for pid in ru['ProjectID'].unique():
    g = RC.load_gem_route(pid, 'gas')
    if g:
        geoms.append((pid, shape(g)))
routes = gpd.GeoDataFrame({'pid': [p for p, _ in geoms]}, geometry=[g for _, g in geoms], crs=4326).to_crs(3576)
routes_union = unary_union(routes.geometry.buffer(COVER_BUF_KM * 1000).values)
print(f'roster routes drawn: {len(geoms)}')


def best_name(n):
    best = (None, 0)
    for pid, v in roster_names:
        s = fuzz.token_set_ratio(n, v)
        if s > best[1]:
            best = (pid, s)
    return best


def metric(geom):
    return gpd.GeoSeries([geom], crs=4326).to_crs(3576).iloc[0]


def km_of(g_m):
    return g_m.length / 1000


def components_km(g_m):
    """lengths (km) of the ~0.5 km-connected components of a line set."""
    b = g_m.buffer(500)
    comps = list(b.geoms) if b.geom_type == 'MultiPolygon' else [b]
    out = []
    for c in comps:
        part = g_m.intersection(c)
        out.append(part.length / 1000)
    return sorted(out, reverse=True)


# ---- OSM: named discovery candidates, merged by name ---------------------------------------
md = json.load(open(f'{OSM}/match_diff.json'))
side = json.load(open(f'{OSM}/geometry_sidecar.json'))
dc = [a for a in md['additions'] if a['disposition'] == 'DISCOVERY_CANDIDATE']
stats = {'osm_dc': len(dc), 'osm_dc_named': sum(1 for a in dc if a['ref']['name']),
         'osm_dc_km_total': round(sum(a['ref']['geodesic_km'] or 0 for a in dc), 1),
         'osm_dc_unnamed_km': round(sum(a['ref']['geodesic_km'] or 0 for a in dc if not a['ref']['name']), 1),
         'osm_dc_unnamed_ge25': sum(1 for a in dc if not a['ref']['name'] and (a['ref']['geodesic_km'] or 0) >= MIN_KM)}
groups = collections.defaultdict(list)
for a in dc:
    nm = a['ref']['name'].strip()
    if nm:
        groups[N.normalize_name(nm) or nm.lower()].append(a)
stats['osm_name_groups'] = len(groups)

rows = []
for key, items in groups.items():
    refs = [i['ref'] for i in items]
    lines = [shape(side[r['ref_id']]) for r in refs if r['ref_id'] in side]
    if not lines:
        continue
    gm = metric(unary_union(lines))
    tot = km_of(gm)
    comps = components_km(gm)
    cov = gm.intersection(routes_union).length / gm.length if gm.length else 0
    nn = N.normalize_name(refs[0]['name'], drop_stopwords=True)
    pid, sc = best_name(nn)
    sh = DJ.district_shares(mapping(unary_union(lines)))
    ops = sorted({r['operator'] for r in refs if r['operator']})
    dias = sorted({str(r['diameter']) for r in refs if r['diameter']})
    rows.append(dict(
        source='osm', seed_id=f'osm:{key.replace(" ", "-")[:60]}', name=refs[0]['name'],
        names_variants='; '.join(sorted({r['name'] for r in refs})[:4]), n_features=len(refs),
        total_km=round(tot, 1), largest_component_km=round(comps[0], 1), n_components=len(comps),
        diameter_mm='; '.join(dias[:4]), operator='; '.join(ops[:3]),
        start_year='; '.join(sorted({str(r['start_year']) for r in refs if r['start_year']})),
        coverage_by_roster_routes=round(cov, 2), nearest_name_pid=pid, nearest_name_score=int(sc), name_tokens=len(nn.split()),
        nearest_geom_pid='; '.join(items[0]['best_guess']['project_ids']) if items[0].get('best_guess') else '',
        district_shares='; '.join(f'{k} {v:.0f}km' for k, v in sorted(sh.items(), key=lambda kv: -kv[1])),
        district=max((k for k in sh if k != 'OUTSIDE'), key=lambda k: sh[k], default='UNASSIGNED'),
        ref_ids=[r['ref_id'] for r in refs][:30]))

# ---- GulfPub: 2 DC + 1 FRAGMENT ------------------------------------------------------------
gmd = json.load(open(f'{GP}/match_diff.json'))
gside = json.load(open(f'{GP}/geometry_sidecar.json'))
for a in gmd['additions']:
    if a['disposition'] not in ('DISCOVERY_CANDIDATE', 'FRAGMENT_OF_EXISTING'):
        continue
    if a['disposition'] == 'FRAGMENT_OF_EXISTING' and 'P0756' not in json.dumps(a.get('best_guess', {})):
        continue
    r = a['ref']
    g = gside.get(r['ref_id'])
    sh = DJ.district_shares(g) if g else {}
    gm = metric(shape(g)) if g else None
    cov = gm.intersection(routes_union).length / gm.length if gm is not None and gm.length else 0
    pid, sc = best_name(N.normalize_name(r['name'], drop_stopwords=True))
    rows.append(dict(
        source='gulfpub', seed_id=f"gulfpub:{r['ref_id']}", name=r['name'], names_variants=r['name'], n_features=1,
        total_km=round(km_of(gm), 1) if gm is not None else r.get('length_km'),
        largest_component_km=round(km_of(gm), 1) if gm is not None else None, n_components=1,
        diameter_mm=str(r.get('diameter') or ''), operator=r.get('operator') or '', start_year=str(r.get('start_year') or ''),
        coverage_by_roster_routes=round(cov, 2), nearest_name_pid=pid, nearest_name_score=int(sc),
        name_tokens=len(N.normalize_name(r['name'], drop_stopwords=True).split()),
        nearest_geom_pid='; '.join((a.get('best_guess') or {}).get('project_ids', [])),
        district_shares='; '.join(f'{k} {v:.0f}km' for k, v in sorted(sh.items(), key=lambda kv: -kv[1])),
        district=max((k for k in sh if k != 'OUTSIDE'), key=lambda k: sh[k], default='UNASSIGNED'),
        ref_ids=[r['ref_id']], gulfpub_disposition=a['disposition']))

# ---- store leads (hand-curated from the R1-R7 validity stores) ----------------------------
leads = json.load(open(f'{HERE}/store_leads.json'))
for L in leads:
    rows.append(dict(source='store', seed_id=L['seed_id'], name=L['name'], names_variants=L.get('ru_name', ''),
                     n_features=0, total_km=L.get('km'), largest_component_km=L.get('km'), n_components=0,
                     diameter_mm=L.get('diameter', ''), operator=L.get('operator', ''), start_year=L.get('year', ''),
                     coverage_by_roster_routes=None, nearest_name_pid='', nearest_name_score=0, name_tokens=0,
                     nearest_geom_pid=L.get('related_pids', ''), district_shares='', district=L['district'],
                     note=L['note'], evidence=L['evidence'], ref_ids=[]))

# ---- classify ------------------------------------------------------------------------------
for r in rows:
    km = r['total_km']
    cov = r['coverage_by_roster_routes'] or 0
    if r['source'] == 'store':
        r['bucket'] = 'seed' if (km or 0) >= MIN_KM else ('monitor' if km else 'seed_length_unknown')
    elif cov >= 0.6 or (r['nearest_name_score'] >= 90 and cov >= 0.25 and r['name_tokens'] >= 2):
        r['bucket'] = 'matched_existing'; r['match_basis'] = 'geometry' if cov >= 0.6 else 'name+geometry'
    elif r['nearest_name_score'] >= 95 and r['name_tokens'] >= 2:
        r['bucket'] = 'matched_existing'; r['match_basis'] = 'name'
    elif r.get('gulfpub_disposition') == 'FRAGMENT_OF_EXISTING':
        r['bucket'] = 'matched_existing'
    elif (km or 0) >= MIN_KM:
        r['bucket'] = 'seed'
    else:
        r['bucket'] = 'monitor'
    r['match_basis'] = r.get('match_basis', '')
    nm = r['name'].lower()
    r['kind_hint'] = ('distribution' if re.search(r'межпосел|газификац|распредел|поселк|посёлк', nm) else
                      'field/gathering' if re.search(r'укпг|нгкм|гкм|месторожд|подключение|кс-|куст', nm) else
                      'spur (otvod/GRS)' if re.search(r'отвод|грс|агрс|тэц|грэс', nm) else 'trunk/other')
    r['name_hint'] = (f"name ~ {r['nearest_name_pid']} ({r['nearest_name_score']})"
                      if r['nearest_name_score'] >= 80 else '')

SLICE = {'Far Eastern': 'D1', 'Siberian': 'D2', 'Ural': 'D3', 'Northwestern': 'D4', 'Volga': 'D5', 'Central': 'D5',
         'Southern': 'D6', 'North Caucasian': 'D6'}
for r in rows:
    r['slice'] = SLICE.get(r['district'], 'UNASSIGNED')
out = pd.DataFrame(rows)
out['ref_ids'] = out['ref_ids'].map(lambda x: '; '.join(x[:5]) + (f' (+{len(x)-5})' if len(x) > 5 else ''))
cols = ['slice', 'bucket', 'district', 'source', 'seed_id', 'name', 'names_variants', 'n_features', 'total_km', 'largest_component_km',
        'n_components', 'diameter_mm', 'operator', 'start_year', 'coverage_by_roster_routes', 'nearest_name_pid',
        'nearest_name_score', 'name_hint', 'match_basis', 'kind_hint', 'nearest_geom_pid', 'district_shares', 'note', 'evidence', 'gulfpub_disposition', 'ref_ids']
out = out.reindex(columns=cols)
out = out.sort_values(['slice', 'bucket', 'total_km'], ascending=[True, True, False])
out.to_csv(f'{HERE}/seeds_by_district.csv', index=False)
js = {'meta': {'built': '2026-09-30', 'min_km': MIN_KM, 'cover_buffer_km': COVER_BUF_KM, 'stats': stats,
               'note': 'bucket: seed = goes to the district discovery run; monitor = <25 km; matched_existing = already tracked '
                       '(geometry coverage or name) - not a seed; seed_length_unknown = store lead without a length (goes to vetting, '
                       'length rule applies there).'},
      'seeds': json.loads(out.to_json(orient='records', force_ascii=False))}
json.dump(js, open(f'{HERE}/seeds_by_district.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps(stats))
print(pd.crosstab(out['slice'], out['bucket'], margins=True).to_string())
print(pd.crosstab(out['district'], out['source']).to_string())
