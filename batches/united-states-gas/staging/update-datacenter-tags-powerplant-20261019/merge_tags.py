"""Merge the ruling-6 DataCenter re-tag shards (shards/tags-*.json) into staged_resolutions.json (run from repo root).

The rows are the US gas rows in development whose DataCenter was blank in the 2026-10-19 snapshot (worklist.json). Ruling 6
(2026-10-18): a tie through a power plant counts. Only yes rows become records (each carries DataCenterNotes in its values);
every row keeps a ledger line in meta. Kept as its own store so the 2026-10-16 stores' decisions stay untouched.
Pass --partial to merge before every chunk is in.
"""
import glob, json, sys
from collections import Counter

D = 'batches/united-states-gas/staging/update-datacenter-tags-powerplant-20261019'
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
wl = {r['project_id']: r for r in json.load(open(f'{D}/worklist.json'))['rows']}
for p, r in recs.items():  # sheet row and names come from the snapshot, not the agent
    r.update(sheet_row=wl[p]['sheet_row'], pipeline_name=wl[p]['pipeline_name'], segment_name=wl[p]['segment_name'])
missing = sorted(p for p in recs if not recs[p]['values'].get('DataCenterNotes'))
if missing:
    print('no DataCenterNotes for', missing)
stray = sorted(set(led) - set(wl))
assert not stray, stray
if '--partial' not in sys.argv:
    assert set(wl) == set(led), sorted(set(wl) - set(led))
pids = sorted(led)
meta = {'commodity': 'gas', 'mode': 'update',
        'scope': {'csv': 'GGIT_gas_snapshot_20261019.csv', 'country': 'United States', 'include_pids': pids,
                  'rows': len(pids), 'project_ids': len(pids)},
        'n_units': len(recs), 'created': '2026-10-19', 'requested_by': 'BL',
        'purpose': 'DataCenter re-tag, 19 October 2026, under ruling 6 of 18 October: a tie through a power plant counts when '
                   'the plant\'s filings, developer, or utility tie that plant to data center load. Covers the US gas rows in '
                   'development whose DataCenter was blank, the 16 big interstate expansions first '
                   '(plan docs/plans/2026-10-16_us-gas-datacenter-subfloor.md).',
        'ledger': [led[p] for p in pids]}
json.dump({'meta': meta, 'resolutions': [recs[p] for p in sorted(recs)]}, open(f'{D}/staged_resolutions.json', 'w'),
          indent=1, ensure_ascii=False)
print(len(recs), 'records;', len(led), 'of', len(wl), 'rows judged;', dict(Counter(x['outcome'] for x in led.values())))
