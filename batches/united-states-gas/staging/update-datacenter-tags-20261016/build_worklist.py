"""DataCenter tag worklist, US gas (plan step 3, docs/plans/2026-10-16_us-gas-datacenter-subfloor.md; run from repo root).

Rows: every US row in development (proposed, construction), operating rows with StartYear1 2023 or later, and every
row the fresh EIA crosswalk matches STRONG to an EIA project whose text names data centers or power. The rows the
2026-10-16 data center discovery runs point at are added later with --add-pids (a follow-up chunk). Each row
carries its EIA hint (project, demand served, notes) and its existing refs so the agent starts from what exists.
"""
import argparse, json, re
import pandas as pd

D = 'batches/united-states-gas/staging/update-datacenter-tags-20261016'
SNAP = 'data/GGIT_gas_snapshot_20261016.csv'
DC = re.compile(r'data.?cent|hyperscal|\bAI\b|artificial intel|Stargate|Jupiter|\bMeta\b|Google|Oracle|Amazon|AWS|Microsoft', re.I)
PW = re.compile(r'power|electric|generat|\bplant\b', re.I)
p = argparse.ArgumentParser(); p.add_argument('--add-pids', default=''); p.add_argument('--out', default=f'{D}/worklist.json')
o = p.parse_args()

g = pd.read_csv(SNAP, header=2, low_memory=False, keep_default_na=False, na_values=[])
g['SheetRow'] = g.index + 4
us = g[g.CountriesOrAreas.str.contains('United States', na=False)]
X = json.load(open('batches/united-states-gas/staging/discovery-datacenter-seeds-20261016/eia_crosswalk_20261016.json'))
long = pd.read_csv('sources/eia_pipeline_projects/data/eia_projects_long.csv', dtype=str, low_memory=False).fillna('')
txt = long.groupby('project_key')[['demand_served', 'notes', 'project_notes']].agg(lambda s: ' '.join(dict.fromkeys(x for x in s if x)))
eia = {}
for pid, r in X['rows'].items():
    for c in r['candidates']:
        if c.get('tier') != 'strong':
            continue
        t = ' '.join(txt.loc[c['project_key']]) if c['project_key'] in txt.index else ''
        t = (t + ' ' + c['project_name']).strip()
        eia.setdefault(pid, []).append({'eia_project': c['project_name'], 'operator': c['operator'], 'status': c['status'],
            'in_service': c['year_in_service'], 'cite_url': c['cite_url'], 'sheet': c['sheet'], 'excel_row': c['excel_row'],
            'text': t[:500], 'dc': bool(DC.search(t)), 'power': bool(PW.search(t))})
sy = pd.to_numeric(us.StartYear1, errors='coerce')
why = {}
for pid in us[us.Status.isin(['proposed', 'construction'])].ProjectID: why.setdefault(pid, []).append('in development')
for pid in us[(us.Status == 'operating') & (sy >= 2023)].ProjectID: why.setdefault(pid, []).append('operating, start 2023 or later')
for pid, es in eia.items():
    if pid in set(us.ProjectID) and any(e['dc'] or e['power'] for e in es):
        why.setdefault(pid, []).append('EIA project names data centers' if any(e['dc'] for e in es) else 'EIA project names power demand')
for pid in filter(None, o.add_pids.split(',')): why.setdefault(pid.strip(), []).append('data center discovery points at it')
refcols = [c for c in us.columns if c.endswith('[ref]')]
rows = []
for _, r in us[us.ProjectID.isin(why)].iterrows():
    refs = sorted({u for c in refcols for u in re.findall(r'https?://\S+', str(r[c]))})
    rows.append({'project_id': r.ProjectID, 'sheet_row': int(r.SheetRow), 'pipeline_name': r.PipelineName,
                 'segment_name': r.SegmentName, 'status': r.Status, 'start_year': r.StartYear1, 'owner': r.Owner,
                 'start': f"{r.StartLocation}, {r['StartState/Province']}", 'end': f"{r.EndLocation}, {r['EndState/Province']}",
                 'length': f"{r.LengthKnown} {r.LengthKnownUnits}".strip(), 'why_listed': why[r.ProjectID],
                 'eia': eia.get(r.ProjectID, []), 'existing_refs': refs[:25], 'current_datacenter': r.DataCenter})
rows.sort(key=lambda x: (0 if any(e['dc'] for e in x['eia']) else 1, x['pipeline_name'], x['segment_name']))
json.dump({'snapshot': SNAP, 'rows': rows}, open(o.out, 'w'), indent=1, ensure_ascii=False)
print(len(rows), 'rows;', sum(any(e['dc'] for e in x['eia']) for x in rows), 'with an EIA data center mention')
