"""Merge the LNG tag shards (shards/lng-*.json) into staged_resolutions.json (run from repo root).

Rows: every US gas row (plus three Mexico Rosarito rows) in the 2026-11-17 snapshot (worklist.json). Records carry
AssociatedWithLNGExports, AssociatedLNGTerminal and AssociatedLNGNotes with the shared AssociatedLNG [ref] (columns
added 2026-11-17). Every row keeps a ledger line in meta. Pass --partial to merge before every chunk is in.
"""
import glob, json, sys
from collections import Counter

D = 'batches/united-states-gas/staging/update-lng-tags-20261117'
recs, led = {}, {}
for f in sorted(glob.glob(f'{D}/shards/lng-*.json')):
    d = json.load(open(f))
    for x in d.get('ledger', []):
        led[x['project_id']] = x
        if x['outcome'] not in ('yes', 'terminal_only', 'confirmed_existing'):
            recs.pop(x['project_id'], None)
    for r in d.get('records', []):
        r.setdefault('action', 'change')
        recs[r['project_id']] = r
wl = {r['project_id']: r for r in json.load(open(f'{D}/worklist.json'))['rows']}
for p, r in recs.items():  # sheet row, names and the current ref come from the snapshot, not the agent
    w = wl[p]
    r.update(sheet_row=w['sheet_row'], pipeline_name=w['pipeline_name'], segment_name=w['segment_name'],
             current_ref=w['current']['AssociatedLNG [ref]'], primary_value=r['values'].get('AssociatedWithLNGExports', ''))
stray = sorted(set(led) - set(wl))
assert not stray, stray
if '--partial' not in sys.argv:
    assert set(wl) == set(led), sorted(set(wl) - set(led))
pids = sorted(led)
meta = {'commodity': 'gas', 'mode': 'update',
        'scope': {'csv': 'GGIT_gas_snapshot_20261117.csv', 'country': 'United States', 'include_pids': pids,
                  'rows': len(pids), 'project_ids': len(pids)},
        'n_units': len(recs), 'created': '2026-11-17', 'requested_by': 'BL',
        'purpose': 'LNG terminal tags, 17 November 2026: AssociatedWithLNGExports (yes when a validated source ties this '
                   'pipeline or expansion to LNG export, directly or as feedgas supply), AssociatedLNGTerminal (terminal names '
                   'as GEM\'s LNG tracker writes them), and AssociatedLNGNotes, with the new shared AssociatedLNG [ref]. '
                   'Covers every US gas row (brief: BRIEF.md in this folder).',
        'ledger': [led[p] for p in pids]}
json.dump({'meta': meta, 'resolutions': [recs[p] for p in sorted(recs)]}, open(f'{D}/staged_resolutions.json', 'w'),
          indent=1, ensure_ascii=False)
print(len(recs), 'records;', len(led), 'of', len(wl), 'rows judged;', dict(Counter(x['outcome'] for x in led.values())))
