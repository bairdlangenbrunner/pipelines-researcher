"""Build the sixth seedsOnly retry run (2026-10-17). Run from the repo root.

The fifth retry ran Texas-Permian in four parts, about an hour apart, so the session-wide web search cap could refill
between them. Part 2 still hit the cap and most of its seeds ran only 2 to 5 searches. This round re-runs every retry5
seed (all parts, every region) that reported fewer than 6 searches and was not queued or matched, with the same
comprehensive budget. Launch it only once the search budget has refilled (about 10 seeds per hour).
"""
import argparse, glob, json, os, re, sys

sys.path.insert(0, os.path.dirname(__file__))
from build_slice_args import ST, DATE  # noqa: E402

MIN_SEARCHES = 6


def pool(key):
    out, src = [], []
    for r5 in sorted(glob.glob(f'{ST}/discovery-datacenter-{key}-retry5*-{DATE}')):
        seeds = {s['seed_id']: s for s in json.load(open(f'{r5}/args.json'))['seeds']}
        done = {}
        for f in glob.glob(f'{r5}/discovery/found_seeds-*.json'):
            for e in json.load(open(f)).get('seed_ledger', []):
                m = re.search(r'Searches run:\s*(\d+)', e.get('reason', ''))
                done[e['seed_id']] = (e['disposition'], int(m.group(1)) if m else 0, e.get('reason', ''))
        low = [dict(s, name_hint=(s.get('name_hint', '') + f" | FIFTH PASS ({done[sid][0]}, {done[sid][1]} searches): "
                                  f"{done[sid][2]}").strip(' |') if sid in done else s.get('name_hint', ''))
               for sid, s in seeds.items()
               if not (done.get(sid, ('', 0, ''))[1] >= MIN_SEARCHES or done.get(sid, ('', 0, ''))[0] in ('queued', 'matched'))]
        if low:
            out += low
            src.append(r5)
    return out, src


def build(key, models, chunk):
    out, src = pool(key)
    if not out:
        print(key, 'nothing to retry')
        return None
    stg = f'{ST}/discovery-datacenter-{key}-retry6-{DATE}'
    os.makedirs(stg, exist_ok=True)
    a = json.load(open(f'{src[0]}/args.json'))
    prior = a['priorStaging'] + [d for d in sorted(glob.glob(f'{ST}/discovery-datacenter-{key}-retry5*-{DATE}'))]
    a.update(staging=stg, seeds=out, seedChunk=chunk, priorStaging=prior, **models)
    a['extra'] = re.sub(r'These \d+ seeds', f'These {len(out)} seeds', a['extra'].replace('FIFTH RETRY', 'SIXTH RETRY')).replace(
        'and the fourth pass ran out of web searches before reaching them',
        'and the fourth and fifth passes ran out of web searches before finishing them')
    json.dump(a, open(f'{stg}/args.json', 'w'), ensure_ascii=False)
    print(key, len(out), 'seeds from', ', '.join(os.path.basename(s) for s in src))
    return stg


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('slices', nargs='*')
    p.add_argument('--model-search', required=True)
    p.add_argument('--model-vet', required=True)
    p.add_argument('--model-consolidate', required=True)
    p.add_argument('--chunk', type=int, default=3)
    o = p.parse_args()
    m = {'model': o.model_search, 'modelSearch': o.model_search, 'modelVet': o.model_vet, 'modelConsolidate': o.model_consolidate}
    for k in (o.slices or ['tx-permian', 'appalachian-se']):
        build(k, m, o.chunk)
