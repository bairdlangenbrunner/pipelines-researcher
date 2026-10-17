"""Build the fifth seedsOnly retry runs (2026-10-16). Run from the repo root.

The fourth retry ran with the fixed search budget, but partway through Texas-Permian the session-wide web search cap
(600 calls, refilling about 100 per hour) ran out, so many seed agents ran no searches at all. This round re-runs every
retry4 seed that reported fewer than 6 searches and was not queued or matched, with the same comprehensive budget.
Launch it only once the search budget has refilled (about 8 searches per seed).
"""
import argparse, glob, json, os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(__file__))
from build_slice_args import SLICES, ST, DATE  # noqa: E402

MIN_SEARCHES = 6


def pool(key):
    r4 = f'{ST}/discovery-datacenter-{key}-retry4-{DATE}'
    seeds = {s['seed_id']: s for s in json.load(open(f'{r4}/args.json'))['seeds']}
    done = {}
    for f in glob.glob(f'{r4}/discovery/found_seeds-*.json'):
        for e in json.load(open(f)).get('seed_ledger', []):
            m = re.search(r'Searches run:\s*(\d+)', e.get('reason', ''))
            done[e['seed_id']] = (e['disposition'], int(m.group(1)) if m else 0)
    return [s for sid, s in seeds.items()
            if not (done.get(sid, ('', 0))[1] >= MIN_SEARCHES or done.get(sid, ('', 0))[0] in ('queued', 'matched'))]


def build(key, models, chunk):
    out = pool(key)
    if not out:
        print(key, 'nothing to retry')
        return
    r4 = f'{ST}/discovery-datacenter-{key}-retry4-{DATE}'
    stg = f'{ST}/discovery-datacenter-{key}-retry5-{DATE}'
    os.makedirs(stg, exist_ok=True)
    a = json.load(open(f'{r4}/args.json'))
    a.update(staging=stg, seeds=out, seedChunk=chunk, priorStaging=a['priorStaging'] + [r4], **models)
    a['extra'] = a['extra'].replace('FOURTH RETRY', 'FIFTH RETRY').replace(
        'were left monitor or dropped by earlier passes that ran only about one search each',
        'were left monitor or dropped by earlier passes that ran only about one search each, and the fourth pass ran out '
        'of web searches before reaching them')
    json.dump(a, open(f'{stg}/args.json', 'w'), ensure_ascii=False)
    subprocess.run([sys.executable, 'scripts/build_discovery_context.py', '--tracker', 'gas', '--country', 'United States',
                    '--staging', stg, '--out', f'{stg}/_ctx.json'], capture_output=True, text=True)
    print(key, len(out), 'seeds')


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
