"""Check one LNG tag shard (shards/lng-<chunk>.json) against the brief; run from repo root. Exit 1 on findings.

    python batches/united-states-gas/staging/update-lng-tags-20261117/check_shard.py a1
"""
import json, re, sys
from pathlib import Path

D = Path('batches/united-states-gas/staging/update-lng-tags-20261117')
sys.path.insert(0, 'scripts')
from url_verifier import BLOCKLIST_HOSTS  # noqa: E402

chunk = sys.argv[1]
want = set(json.load(open(D / 'chunks.json'))[chunk])
wl = {r['project_id']: r for r in json.load(open(D / 'worklist.json'))['rows']}
s = json.load(open(D / 'shards' / f'lng-{chunk}.json'))
OUT = {'yes', 'terminal_only', 'confirmed_existing', 'existing_unsupported', 'blank_noted', 'unfinished'}
COLS = ['AssociatedWithUSLNGExports', 'AssociatedLNGTerminal', 'AssociatedLNGNotes']
bad = []
led = {x['project_id']: x for x in s.get('ledger', [])}
if set(led) != want:
    bad.append(f'ledger rows missing {sorted(want - set(led))} / stray {sorted(set(led) - want)}')
for p, x in led.items():
    if x.get('outcome') not in OUT:
        bad.append(f'{p}: outcome {x.get("outcome")!r}')
    if not str(x.get('note', '')).strip():
        bad.append(f'{p}: ledger note empty')
for r in s.get('records', []):
    p = r.get('project_id'); v = r.get('values', {})
    if p not in want:
        bad.append(f'{p}: record not in this chunk'); continue
    if led.get(p, {}).get('outcome') not in ('yes', 'terminal_only', 'confirmed_existing'):
        bad.append(f'{p}: record but ledger outcome {led.get(p, {}).get("outcome")!r}')
    if sorted(v) != sorted(COLS) or r.get('value_cols') != COLS or r.get('ref_col') != 'AssociatedLNG [ref]':
        bad.append(f'{p}: values / value_cols / ref_col must be the three columns and AssociatedLNG [ref]')
    flag, term = str(v.get(COLS[0], '')).strip(), str(v.get(COLS[1], '')).strip()
    if flag not in ('yes', ''):
        bad.append(f'{p}: flag {flag!r} (yes or blank)')
    if not flag and not term:
        bad.append(f'{p}: record with neither the flag nor a terminal')
    if term.lower() in ('yes', 'no') or 'http' in term:
        bad.append(f'{p}: terminal {term!r}')
    if not str(v.get(COLS[2], '')).strip():
        bad.append(f'{p}: AssociatedLNGNotes empty')
    cur = wl[p]['current']
    if cur['AssociatedWithUSLNGExports'] == 'yes' and flag != 'yes':
        bad.append(f'{p}: clears the existing yes')
    old_t = cur['AssociatedLNGTerminal'].strip()
    if old_t and 'http' not in old_t and old_t.lower() != 'yes' and not term:
        bad.append(f'{p}: clears the existing terminal {old_t!r}')
    refs = r.get('proposed_refs') or []
    if not refs:
        bad.append(f'{p}: no proposed_refs')
    for u in refs:
        if not re.match(r'https?://', u) or any(h in u for h in ('gem.wiki', 'globalenergymonitor.org')) or any(h in u for h in BLOCKLIST_HOSTS):
            bad.append(f'{p}: ref {u!r} not allowed')
    if r.get('tier') not in ('high', 'medium', 'low'):
        bad.append(f'{p}: tier {r.get("tier")!r}')
    for t in (v.get(COLS[2], ''), r.get('researcher_notes', '')):
        if '—' in t or '->' in t or '→' in t:
            bad.append(f'{p}: notes use an em-dash or arrow')
print('\n'.join(bad) or f'{chunk}: ok ({len(s.get("records", []))} records, {len(led)} ledger rows)')
sys.exit(1 if bad else 0)
