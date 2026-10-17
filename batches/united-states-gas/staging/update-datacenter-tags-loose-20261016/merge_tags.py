"""Merge the loosened-rule DataCenter re-tag shards (shards/tags-*.json) into staged_resolutions.json (run from repo root).

The 56 rows are the 51 the 2026-10-16 tag store left blank with a note, plus P8314 and P8323, plus three tag leads
from the discovery retries (P0246, P0225, P8195; shards/tags-8.json). Ruling 1 was loosened the same
day: DataCenter = yes when a validated ref names the pipeline and mentions data centers at all as a reason for it. Only yes
rows become records (each carries DataCenterNotes in its values); every row keeps a ledger line in meta. Kept as its own
store so the first store's decisions and applied markers stay untouched.
"""
import glob, json

D = 'batches/united-states-gas/staging/update-datacenter-tags-loose-20261016'
recs, led = {}, {}
for f in sorted(glob.glob(f'{D}/shards/tags-*.json')):
    d = json.load(open(f))
    for x in d.get('ledger', []):
        led[x['project_id']] = x
        if x['outcome'] != 'yes':
            recs.pop(x['project_id'], None)
    for r in d.get('records', []):
        r.setdefault('action', 'change')
        r.setdefault('current_ref', '')
        recs[r['project_id']] = r
missing = sorted(p for p in recs if not recs[p]['values'].get('DataCenterNotes'))
if missing:
    print('no DataCenterNotes for', missing)
want = {r['project_id'] for r in json.load(open(f'{D}/worklist.json'))['rows']}
assert want == set(led), (sorted(want - set(led)), sorted(set(led) - want))
pids = sorted(led)
meta = {'commodity': 'gas', 'mode': 'update',
        'scope': {'csv': 'GGIT_gas_snapshot_20261016.csv', 'country': 'United States', 'include_pids': pids,
                  'rows': len(pids), 'project_ids': len(pids)},
        'n_units': len(recs), 'created': '2026-10-16', 'requested_by': 'BL',
        'purpose': 'DataCenter re-tag, 16 October 2026, under the loosened ruling 1: DataCenter = yes when a validated ref '
                   'names the pipeline and mentions data centers at all as a demand driver or a reason for the project. '
                   'Covers the 51 rows the first tag store left blank with a note, plus P8314 and P8323, and three tag leads from the '
                   'discovery retries (P0246, P0225, P8195) '
                   '(plan docs/plans/2026-10-16_us-gas-datacenter-subfloor.md).',
        'ledger': [led[p] for p in pids]}
json.dump({'meta': meta, 'resolutions': [recs[p] for p in sorted(recs)]}, open(f'{D}/staged_resolutions.json', 'w'),
          indent=1, ensure_ascii=False)
from collections import Counter
print(len(recs), 'records;', dict(Counter(x['outcome'] for x in led.values())))
