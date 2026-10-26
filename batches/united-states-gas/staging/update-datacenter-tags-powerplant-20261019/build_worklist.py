"""DataCenter re-tag worklist under ruling 6, US gas (plan step 3 of the 2026-10-19 status doc; run from repo root).

Rows: every US row in development (proposed, construction) whose DataCenter is blank in the 2026-10-19 snapshot. Ruling 6
(2026-10-18): a tie through a power plant counts, so rows the 2026-10-16 tag stores left blank are re-judged. Group A is
the 16 big interstate expansions serving utility or power load (ruling 7), researched first; group B is everything else.
Each row carries the notes the two earlier tag stores left for it, so the agent starts from what was already checked.
"""
import json, re
import pandas as pd

D = 'batches/united-states-gas/staging/update-datacenter-tags-powerplant-20261019'
SNAP = 'data/GGIT_gas_snapshot_20261019.csv'
PRIOR = ['batches/united-states-gas/staging/update-datacenter-tags-20261016',
         'batches/united-states-gas/staging/update-datacenter-tags-loose-20261016']
GROUP_A = ['P7855', 'P2567', 'P2574', 'P2605', 'P5664', 'P8174', 'P8210', 'P7793', 'P5627', 'P7809', 'P8146', 'P8122',
           'P8124', 'P8125', 'P7863', 'P8171']

g = pd.read_csv(SNAP, header=2, low_memory=False, keep_default_na=False, na_values=[])
g['SheetRow'] = g.index + 4
us = g[g.CountriesOrAreas.str.contains('United States', na=False)]
b = us[us.Status.isin(['proposed', 'construction']) & (us.DataCenter.str.strip() == '')]
prior, staged_yes = {}, set()
for d in PRIOR:
    s = json.load(open(f'{d}/staged_resolutions.json'))
    for x in s['meta'].get('ledger', []):
        prior.setdefault(x['project_id'], []).append(f"{d.rsplit('/', 1)[1]}: {x['outcome']}: {x.get('note', '')}")
    staged_yes |= {r['project_id'] for r in s['resolutions']}
refcols = [c for c in us.columns if c.endswith('[ref]')]
rows = []
for _, r in b.iterrows():
    if r.ProjectID in staged_yes:
        continue  # a yes already staged and awaiting review
    refs = sorted({u for c in refcols for u in re.findall(r'https?://\S+', str(r[c]))})
    rows.append({'project_id': r.ProjectID, 'sheet_row': int(r.SheetRow), 'group': 'A' if r.ProjectID in GROUP_A else 'B',
                 'pipeline_name': r.PipelineName, 'segment_name': r.SegmentName, 'status': r.Status,
                 'start_year': r.StartYear1, 'owner': r.Owner, 'start': f"{r.StartLocation}, {r['StartState/Province']}",
                 'end': f"{r.EndLocation}, {r['EndState/Province']}", 'length': f"{r.LengthKnown} {r.LengthKnownUnits}".strip(),
                 'prior_notes': prior.get(r.ProjectID, []), 'existing_refs': refs[:25]})
rows.sort(key=lambda x: (x['group'], GROUP_A.index(x['project_id']) if x['group'] == 'A' else 0, x['pipeline_name'], x['segment_name']))
json.dump({'snapshot': SNAP, 'rows': rows}, open(f'{D}/worklist.json', 'w'), indent=1, ensure_ascii=False)
print(len(rows), 'rows;', sum(x['group'] == 'A' for x in rows), 'in group A;', len(b) - len(rows), 'skipped as already staged yes')
