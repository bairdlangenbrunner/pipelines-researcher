#!/usr/bin/env python3
"""Fill empty Background bodies on live gem.wiki pages from drafted prose.

python scripts/patch_wiki_backgrounds.py DRAFTED.json MANIFEST.json OUTDIR [--post]

DRAFTED.json: {"drafts": {PID: text with {k}}, "refs": {k: {url,title,site}}} (merged drafter output).
Only PIDs in DRAFTED are touched. A Background body is filled only when it is empty or holds just the
dormancy sentence; the dormancy sentence stays after the new text. Dry run writes before/after files.
With --post: re-reads the live page, skips on any change since planning, saves, purges, parse-checks the map.
"""
import json, re, sys, time, os
sys.path.insert(0, 'scripts'); sys.path.insert(0, '../goit-ggit-data-ops/gem-wiki')
import pandas as pd
import build_wiki_pages as B
import gemwiki as g
from wiki_save import save as wiki_save_save  # same scripts/ path build_wiki_pages comes from

drafted_path, man_path, outdir = sys.argv[1:4]
POST = '--post' in sys.argv
D = json.load(open(drafted_path)); man = json.load(open(man_path))
os.makedirs(outdir, exist_ok=True)
snap = pd.read_csv(B.SNAP, header=2, low_memory=False, keep_default_na=False)
rows = {r['ProjectID']: r.to_dict() for _, r in snap.iterrows()}

def retry(fn, n=20):
    for i in range(n):
        try: return fn()
        except Exception as e:
            print('retry', i, type(e).__name__, flush=True); time.sleep(15)
    raise SystemExit('wiki unreachable')

def resolve(txt):
    txt = re.sub(r'[ \t]+(?=\{[A-Za-z0-9_]+\})', '', txt)
    for k, v in D['refs'].items():
        txt = txt.replace('{' + k + '}', B.cite(v['url'], B.pdf_title(v['url']) or v['title'], v['site']))
    return txt

def section(text, head, level):
    """(start of body, end of body) of a heading at this level, or None."""
    eq = '=' * level
    m = re.search(r'\n' + eq + r'\s*' + re.escape(head) + r'\s*' + eq + r'[ \t]*\n', text)
    if not m: return None
    nxt = re.search(r'\n={2,%d}[^=\n]' % level, text[m.end():])
    return m.end(), (m.end() + nxt.start() + 1 if nxt else len(text))

def fill(text, pids, single_page):
    bg = section(text, 'Background', 2)
    if not bg: return text, ['no Background section']
    notes = []
    names = set(re.findall(r'<ref name="(r[0-9a-f]{6})">', text))
    for pid in pids:
        r = rows[pid]
        bg = section(text, 'Background', 2)
        if single_page: s, e = bg
        else:
            sub = section(text[bg[0] - 1:bg[1]], B.seg_title(r), 3)
            if not sub: notes.append(pid + ': segment heading not in Background'); continue
            s, e = sub[0] + bg[0] - 1, sub[1] + bg[0] - 1
        body = text[s:e].strip('\n')
        if body and not ('no development on' in body and '\n\n' not in body):
            notes.append(pid + ': body not empty, left alone'); continue
        new = resolve(D['drafts'][pid]).strip()
        if not new: notes.append(pid + ': empty draft'); continue
        new = B.dedupe_refs(new, names)
        out = new + (('\n\n' + body) if body else '')
        text = text[:s] + out + '\n\n' + text[e:].lstrip('\n')
    return text, notes

s = retry(lambda: g.session(login=True)) if POST else retry(lambda: g.session())
log = []
for m in man:
    pids = [p for p in m['pids'] if p in D['drafts'] and D['drafts'][p].strip()]
    if not pids: continue
    t = m['title']
    live = retry(lambda: g.page_text(s, t))
    single = len(m['pids']) == 1 and m['kind'] == 'new'
    new, notes = fill(live, pids, single)
    rec = {'title': t, 'pids': pids, 'notes': notes, 'changed': new != live}
    safe = re.sub(r'[^A-Za-z0-9]+', '_', t)
    open(f'{outdir}/{safe}.before', 'w').write(live); open(f'{outdir}/{safe}.after', 'w').write(new)
    if POST and new != live:
        again = retry(lambda: g.page_text(s, t))
        if again != live: rec['result'] = 'LIVE CHANGED, skipped'
        else:
            r = retry(lambda: wiki_save_save(s, t, text=new, summary='add background'))  # edit + purge + map check
            rec['rev'] = r.get('newrevid'); rec['result'] = 'saved'; rec['map'] = r['map']
    log.append(rec); print(t, rec.get('result', 'dry'), rec['notes'], rec.get('map'), flush=True)
    json.dump(log, open(f'{outdir}/log.json', 'w'), indent=1)
