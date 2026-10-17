"""Build the fourth seedsOnly retry runs (2026-10-16). Run from the repo root.

The second and third retries were not comprehensive: the country-discovery seed prompt carried a fixed budget line
("about one focused search per seed") that overrode the COMPREHENSIVE SEARCH checklist, so the seed agents ran about
one search per seed. The workflow now takes args.seedBudget and args.seedRetry. This round re-runs every seed the
second retry (or, where it ran, the third) left monitor or dropped, with a budget of at least eight searches per seed.
"""
import argparse, json, os, subprocess, sys

sys.path.insert(0, os.path.dirname(__file__))
from build_slice_args import SLICES, SCOPE, VET, SEED_INTRO, ST, DATE  # noqa: E402
from build_retry2_args import CHECKLIST, INTRO_EXTRA  # noqa: E402
from build_retry3_args import REJUDGE  # noqa: E402

BUDGET = ("Budget: this is a COMPREHENSIVE retry. Earlier passes ran about one search per seed, so treat every seed as "
          "unsearched. Run at least 8 distinct web searches per seed, more when a lead appears, and read the most "
          "promising pages in full (python scripts/fetch.py <url>, not just search snippets). Follow every lead a result "
          "gives: a hyperscaler or developer filing, a county agenda, an air permit number, a utility docket, a news story "
          "about the same site. Never stop early because an earlier pass found nothing. End each ledger reason with "
          "'Searches run: N.' and a plain list of the sources checked and what each showed.")


def pool(key):
    out = []
    a = json.load(open(f'{ST}/discovery-datacenter-{key}-retry2-{DATE}/args.json'))
    seeds = {s['seed_id']: s for s in a['seeds']}
    led = {e['seed_id']: e for e in json.load(open(f'{ST}/discovery-datacenter-{key}-retry2-{DATE}/staged_new.json'))
           ['meta']['seed_ledger']}
    r3 = f'{ST}/discovery-datacenter-{key}-retry3-{DATE}/staged_new.json'
    if os.path.exists(r3):
        led.update({e['seed_id']: e for e in json.load(open(r3))['meta']['seed_ledger']})
    for sid, s in seeds.items():
        e = led.get(sid)
        if e is None or e['disposition'] not in ('monitor', 'dropped'):
            continue
        s = dict(s)
        hint = f" | LATEST PASS ({e['disposition']}, thin, about one search): {e.get('reason', '')}"
        if sid in REJUDGE:
            hint += f" | RE-JUDGE: {REJUDGE[sid]}"
        s['name_hint'] = (s.get('name_hint', '') + hint).strip(' |')
        out.append(s)
    return out


def build(key, models):
    out = pool(key)
    if not out:
        print(key, 'nothing to retry')
        return
    stg = f'{ST}/discovery-datacenter-{key}-retry4-{DATE}'
    os.makedirs(stg, exist_ok=True)
    subprocess.run([sys.executable, 'scripts/build_discovery_context.py', '--tracker', 'gas', '--country', 'United States',
                    '--staging', stg, '--out', f'{stg}/args.json'], capture_output=True, text=True, check=True)
    a = json.load(open(f'{stg}/args.json'))
    scope, leads, extra = SLICES[key]
    prior = [p for p in [f'{ST}/discovery-{key}-20261002', f'{ST}/discovery-datacenter-{key}-{DATE}'] +
             [f'{ST}/discovery-datacenter-{key}-{r}-{DATE}' for r in ('retry', 'retry2', 'retry3')] if os.path.exists(p)]
    a.update(staging=stg, scopeRule=SCOPE, vetRule=VET, strategies=[], seeds=out, seedsOnly=True, seedRetry=True,
             seedIntro=SEED_INTRO + INTRO_EXTRA, seedSearch=CHECKLIST, seedBudget=BUDGET, seedChunk=3, minKm=0,
             priorStaging=prior, **models)
    a['extra'] = '\n'.join([
        f'## This run: United States gas DATA CENTER discovery, region {key} = {scope}. FOURTH RETRY, seeds only, COMPREHENSIVE.',
        f'These {len(out)} seeds were left monitor or dropped by earlier passes that ran only about one search each. '
        'Research each in full under the COMPREHENSIVE SEARCH checklist and the budget below. The earlier-pass text in '
        'each hint is a starting point, never a conclusion. Read the priorStaging runs first only to learn which new '
        'rows and matches they already staged, so you never stage the same line twice.',
        'Pace searches a few seconds apart. If a search fails, wait and retry it before giving up; only then say in the '
        'reason that the search failed.',
        'The roster below is the FULL national roster: match against all of it. A line that only passes through this '
        'region: report it with "out_of_slice": true in why_maybe_new.',
        'No length floor: any sourced length, 0 for compression-only, as long as the pipeline is tied to a data center. '
        'A matched_existing / EXISTING_ROW finding is a DataCenter tag lead for that row: put the ref that ties the row '
        'to a data center in its evidence. Do not suggest a plant or campus name as an OtherEnglishNames.',
        'GOGPT (GEM plant tracker) and gem.wiki are leads only, never refs. Crude, NGL and refined-product lines are out '
        'of scope. Puerto Rico is out of scope.',
    ])
    json.dump(a, open(f'{stg}/args.json', 'w'), ensure_ascii=False)
    print(key, len(out), 'seeds')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('slices', nargs='*')
    p.add_argument('--model-search', required=True)
    p.add_argument('--model-vet', required=True)
    p.add_argument('--model-consolidate', required=True)
    o = p.parse_args()
    m = {'model': o.model_search, 'modelSearch': o.model_search, 'modelVet': o.model_vet, 'modelConsolidate': o.model_consolidate}
    for k in (o.slices or SLICES):
        build(k, m)
