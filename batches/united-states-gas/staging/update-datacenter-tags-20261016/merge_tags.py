"""Merge the DataCenter tag shards (shards/tags-*.json, shards/followup-*.json) into staged_resolutions.json (run from repo root).

Only DataCenter = yes rows become records. Every worklist row also keeps a ledger line in meta (yes, blank_noted with the
reason a tie was not accepted, or blank), so a reviewer can see what was checked. A later shard for the same ProjectID
replaces an earlier one (the follow-up chunk re-checks rows with a lead from the 2026-10-16 discovery runs).
Each yes record also carries DataCenterNotes, the plain notes on the related data center from dc_notes/notes-*.json.
"""
import glob, json

D = 'batches/united-states-gas/staging/update-datacenter-tags-20261016'
recs, led = {}, {}
for f in sorted(glob.glob(f'{D}/shards/tags-*.json')) + sorted(glob.glob(f'{D}/shards/followup-*.json')):
    d = json.load(open(f))
    for x in d.get('ledger', []):
        led[x['project_id']] = x
        if x['outcome'] != 'yes':
            recs.pop(x['project_id'], None)
    for r in d.get('records', []):
        r.setdefault('action', 'change')
        r.setdefault('current_ref', '')
        recs[r['project_id']] = r
notes = {}
for f in sorted(glob.glob(f'{D}/dc_notes/notes-*.json')):
    notes.update(json.load(open(f)))
for pid, r in recs.items():
    n = notes.get(pid, {}).get('note', '').strip()
    if n:
        r['value_cols'] = ['DataCenter', 'DataCenterNotes']
        r['values']['DataCenterNotes'] = n
missing = sorted(p for p in recs if 'DataCenterNotes' not in recs[p]['values'])
if missing:
    print('no DataCenterNotes for', missing)
pids = sorted(led)
meta = {'commodity': 'gas', 'mode': 'update',
        'scope': {'csv': 'GGIT_gas_snapshot_20261016.csv', 'country': 'United States', 'include_pids': pids,
                  'rows': len(pids), 'project_ids': len(pids)},
        'n_units': len(recs), 'created': '2026-10-16', 'requested_by': 'BL',
        'purpose': 'DataCenter tags, 16 October 2026: US gas rows in development, operating rows starting 2023 or later, '
                   'rows matched to EIA projects that name power or data center demand, and rows the data center '
                   'discovery runs pointed at. DataCenter = yes only where a validated ref names the pipeline and ties it '
                   'to a data center (plan docs/plans/2026-10-16_us-gas-datacenter-subfloor.md, ruling 1).',
        'ledger': [led[p] for p in pids]}
json.dump({'meta': meta, 'resolutions': [recs[p] for p in sorted(recs)]}, open(f'{D}/staged_resolutions.json', 'w'),
          indent=1, ensure_ascii=False)
from collections import Counter
print(len(recs), 'records;', dict(Counter(x['outcome'] for x in led.values())))
