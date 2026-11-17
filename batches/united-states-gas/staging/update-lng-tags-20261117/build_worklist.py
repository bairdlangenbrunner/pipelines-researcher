"""LNG tag worklist, US gas, 2026-11-17 (run from repo root).

Every US row (Status not N/A) in the 2026-11-17 snapshot, plus the three Mexico Rosarito rows that already carry an LNG
terminal cell. Each row carries its current AssociatedWithUSLNGExports / AssociatedLNGTerminal values, its existing refs,
and the EIA pipeline-projects candidates from eia/eia_crosswalk.json with EIA's notes and demand-served text, so agents
start from what EIA says. Group A (likely LNG ties: already tagged, EIA text naming LNG or export, LNG words in the name or
notes, Texas or Louisiana or Alaska rows built since 2010 or in development) goes to sonnet in small chunks; group B (the
rest) goes to haiku in larger chunks. Terminal names come from GEM's LNG terminal tracker (gem-db-ops lng/gem_export.csv) so
agents write a terminal the way that tracker names it.
"""
import json, re
import pandas as pd

D = 'batches/united-states-gas/staging/update-lng-tags-20261117'
SNAP = 'data/GGIT_gas_snapshot_20261117.csv'
EXTRA = ['P0427', 'P1264', 'P2247']
LNG_RE = re.compile(r'\bLNG\b|liquef|export|feed ?gas|terminal', re.I)
NAME_RE = re.compile(r'\bLNG\b|Sabine|Cameron|Calcasieu|Plaquemines|Golden Pass|Freeport|Corpus Christi|Port Arthur|Rio Grande|'
                     r'Driftwood|Delfin|Cove Point|Elba|Commonwealth|Magnolia|Lake Charles|Gulf Coast|Permian|Haynesville|'
                     r'Express|Access|Connector|Header|Gateway|Pathway|Global|Coastal|Matterhorn|Whistler|Saguaro|Baja', re.I)

g = pd.read_csv(SNAP, header=2, low_memory=False, keep_default_na=False, na_values=[])
g['SheetRow'] = g.index + 4
rows_df = g[(g.CountriesOrAreas.str.contains('United States') & (g.Status != 'N/A')) | g.ProjectID.isin(EXTRA)]
xw = json.load(open(f'{D}/eia/eia_crosswalk.json'))['rows']
lg = pd.read_csv('sources/eia_pipeline_projects/data/eia_projects_long.csv', low_memory=False, keep_default_na=False, na_values=[])
lg = lg.sort_values('release').groupby('project_key').tail(1).set_index('project_key')
lt = pd.read_csv('../gem-db-ops/lng/gem_export.csv', low_memory=False, keep_default_na=False, na_values=[])
lt = lt[lt['Country/Area'].isin(['United States', 'Mexico', 'Canada'])]
terms = (lt.groupby('TerminalName').agg(country=('Country/Area', 'first'), type=('FacilityType', lambda s: '/'.join(sorted(set(s) - {''}))),
                                        status=('Status', lambda s: '/'.join(sorted(set(s) - {''})))).reset_index())
json.dump(terms.to_dict('records'), open(f'{D}/lng_terminals.json', 'w'), indent=1, ensure_ascii=False)
refcols = [c for c in g.columns if c.endswith('[ref]')]
out = []
for _, r in rows_df.iterrows():
    cands = []
    for c in (xw.get(r.ProjectID) or {}).get('candidates', [])[:6]:
        e = lg.loc[c['project_key']] if c['project_key'] in lg.index else None
        cands.append({k: c.get(k) for k in ('tier', 'project_name', 'operator', 'project_type', 'status', 'year_in_service',
                                             'states', 'miles', 'capacity_mmcfd', 'docket', 'cite_url', 'notes')}
                     | {'demand_served': '' if e is None else e['demand_served'], 'project_notes': '' if e is None else e['project_notes'],
                        'press_names': '' if e is None else e['name_of_the_projects_as_appeared_on_press_releases_or_government_applications']})
    eia_txt = ' '.join(f"{c['project_name']} {c['notes']} {c['demand_served']} {c['project_notes']}" for c in cands)
    tagged = r.AssociatedWithUSLNGExports.strip() != '' or r.AssociatedLNGTerminal.strip() != ''
    gulf = any(s in f"{r['StartState/Province']} {r['EndState/Province']}" for s in ('Texas', 'Louisiana', 'Alaska'))
    yr = pd.to_numeric(r.StartYear1, errors='coerce')
    recent = r.Status in ('proposed', 'construction', 'shelved', 'cancelled') or (yr == yr and yr >= 2010)
    why = [w for w, ok in [('tagged', tagged), ('eia_lng_text', bool(LNG_RE.search(eia_txt))),
                           ('name_or_notes', bool(LNG_RE.search(f'{r.PipelineName} {r.SegmentName} {r.ResearcherNotes}') or NAME_RE.search(f'{r.PipelineName} {r.SegmentName} {r.OtherEnglishNames}'))),
                           ('tx_la_ak_recent', gulf and recent)] if ok]
    refs = sorted({u for c in refcols for u in re.findall(r'https?://[^\s,]+', str(r[c]))})
    out.append({'project_id': r.ProjectID, 'sheet_row': int(r.SheetRow), 'group': 'A' if why else 'B', 'why_group_a': why,
                'pipeline_name': r.PipelineName, 'segment_name': r.SegmentName, 'other_names': r.OtherEnglishNames,
                'status': r.Status, 'start_year': r.StartYear1, 'owner': r.Owner, 'countries': r.CountriesOrAreas,
                'start': f"{r.StartLocation}, {r['StartState/Province']}", 'end': f"{r.EndLocation}, {r['EndState/Province']}",
                'length': f"{r.LengthKnown} {r.LengthKnownUnits}".strip(), 'diameter': f"{r.Diameter} {r.DiameterUnits}".strip(),
                'capacity': f"{r.Capacity} {r.CapacityUnits}".strip(),
                'current': {'AssociatedWithUSLNGExports': r.AssociatedWithUSLNGExports, 'AssociatedLNGTerminal': r.AssociatedLNGTerminal,
                            'AssociatedLNG [ref]': r['AssociatedLNG [ref]'], 'AssociatedLNGNotes': r.AssociatedLNGNotes},
                'researcher_notes': r.ResearcherNotes[:600], 'existing_refs': refs[:20], 'eia': cands})
out.sort(key=lambda x: (x['group'], x['pipeline_name'], x['segment_name']))
json.dump({'snapshot': SNAP, 'rows': out}, open(f'{D}/worklist.json', 'w'), indent=1, ensure_ascii=False)
A = [x['project_id'] for x in out if x['group'] == 'A']; B = [x['project_id'] for x in out if x['group'] == 'B']
chunks = {f'a{i // 8 + 1}': A[i:i + 8] for i in range(0, len(A), 8)} | {f'b{i // 20 + 1}': B[i:i + 20] for i in range(0, len(B), 20)}
json.dump(chunks, open(f'{D}/chunks.json', 'w'), indent=1)
print(len(out), 'rows;', len(A), 'group A in', sum(k[0] == 'a' for k in chunks), 'chunks;', len(B), 'group B in', sum(k[0] == 'b' for k in chunks), 'chunks;', len(terms), 'terminals')
