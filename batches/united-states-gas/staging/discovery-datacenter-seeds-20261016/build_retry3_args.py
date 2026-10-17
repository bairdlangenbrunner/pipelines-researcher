"""Build the third seedsOnly retry runs (2026-10-16). Run from the repo root.

The second retry hit a usage limit partway through the Appalachian-Southeast run, so 17 of its seeds ran no new searches,
and one Texas-Permian seed was searched only once. This round re-runs those seeds under the same COMPREHENSIVE SEARCH
checklist, plus any seed the second retry turned down under the old strict data center rule (listed in REJUDGE).
With --not-checked, the round instead takes the seeds whose second-retry reason says some checklist sources were not
checked (a state air permit, Railroad Commission T-4 file, FERC docket), written to a retry3b dir.
"""
import argparse, json, os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(__file__))
from build_slice_args import SLICES, SCOPE, VET, SEED_INTRO, ST, DATE  # noqa: E402
from build_retry2_args import CHECKLIST, INTRO_EXTRA  # noqa: E402

INCOMPLETE = re.compile(r'session limit|could not run|not completed|incomplete|not done|no new search|fewer than eight|'
                        r'in one retry search', re.I)
REJUDGE = {'eia:commonwealth-energy-connector-project':
           'The second retry turned this down because sources cite Virginia data center growth only as general context. '
           'That is the old strict rule. Under the loosened ruling 1, a validated ref that names this project and gives '
           'data center growth as a reason for it is enough, and there is no length floor once the tie holds.'}


NOT_CHECKED = re.compile(r'not (yet )?checked[^.]*', re.I)


def pool(key, not_checked=False):
    base = f'{ST}/discovery-datacenter-{key}-retry2-{DATE}'
    a = json.load(open(f'{base}/args.json'))
    d = json.load(open(f'{base}/staged_new.json'))
    seeds = {s['seed_id']: s for s in a['seeds']}
    out = []
    for led in d['meta']['seed_ledger']:
        sid, why = led['seed_id'], led.get('reason', '')
        if not_checked:
            m = NOT_CHECKED.search(why)
            if not m or INCOMPLETE.search(why) or sid in REJUDGE:
                continue
            extra = (f" | SECOND PASS ({led['disposition']}): {why} | GAP: the second retry says '{m.group(0)}'. Search "
                     "those sources first and in full: look up the plant's air permit by its number or name in the state "
                     "permit database and read the application, which usually names the gas supplier and the lateral; "
                     "read the Railroad Commission T-4 permits and pipeline GIS viewer for the county; search FERC "
                     "eLibrary for the plant, developer and county.")
        elif sid in REJUDGE:
            extra = f" | SECOND PASS ({led['disposition']}): {why} | RE-JUDGE: {REJUDGE[sid]}"
        elif INCOMPLETE.search(why):
            extra = (f" | SECOND PASS ({led['disposition']}, searches did not run or were cut short, so treat it as "
                     f"unsearched): {why}")
        else:
            continue
        s = dict(seeds[sid])
        s['name_hint'] = (s.get('name_hint', '') + extra).strip(' |')
        out.append(s)
    return out


def build(key, models, not_checked=False):
    out = pool(key, not_checked)
    if not out:
        print(key, 'nothing to retry')
        return
    stg = f'{ST}/discovery-datacenter-{key}-retry3{"b" if not_checked else ""}-{DATE}'
    os.makedirs(stg, exist_ok=True)
    subprocess.run([sys.executable, 'scripts/build_discovery_context.py', '--tracker', 'gas', '--country', 'United States',
                    '--staging', stg, '--out', f'{stg}/args.json'], capture_output=True, text=True, check=True)
    a = json.load(open(f'{stg}/args.json'))
    scope, leads, extra = SLICES[key]
    prior = [p for p in (f'{ST}/discovery-{key}-20261002', f'{ST}/discovery-datacenter-{key}-{DATE}',
                         f'{ST}/discovery-datacenter-{key}-retry-{DATE}', f'{ST}/discovery-datacenter-{key}-retry2-{DATE}',
                         f'{ST}/discovery-datacenter-{key}-retry3-{DATE}')
             if os.path.exists(p)]
    a.update(staging=stg, scopeRule=SCOPE, vetRule=VET, strategies=[], seeds=out, seedsOnly=True,
             seedIntro=SEED_INTRO + INTRO_EXTRA, seedSearch=CHECKLIST, seedChunk=3, minKm=0, priorStaging=prior, **models)
    a['extra'] = '\n'.join([
        f'## This run: United States gas DATA CENTER discovery, region {key} = {scope}. THIRD RETRY, seeds only.',
        (f'These {len(out)} seeds left some checklist sources unsearched in the second retry (each hint names the gap). '
         'Search the gap sources first and in full, then the rest of the COMPREHENSIVE SEARCH checklist. '
         'Read the priorStaging runs first only to learn which new rows and matches they already staged, so you never '
         'stage the same line twice.') if not_checked else
        f'These {len(out)} seeds were cut short in the second retry (a usage limit stopped the web searches) or were '
        'judged there under the old strict data center rule. Treat each as unsearched and research it in full under the '
        'COMPREHENSIVE SEARCH checklist. The FIRST PASS and SECOND PASS text in each hint is a starting point, never a '
        'conclusion. Read the priorStaging runs first only to learn which new rows and matches they already staged, so '
        'you never stage the same line twice.',
        'Pace searches a few seconds apart. If a search fails, retry it before giving up; only then say in the reason '
        'that the search failed.',
        'The roster below is the FULL national roster: match against all of it. A line that only passes through this '
        'region: report it with "out_of_slice": true in why_maybe_new.',
        'No length floor: any sourced length, 0 for compression-only, as long as the pipeline is tied to a data center. '
        'A matched_existing / EXISTING_ROW finding is a DataCenter tag lead for that row: put the ref that ties the row '
        'to a data center in its evidence. Do not suggest a plant or campus name as an OtherEnglishNames.',
        'GOGPT (GEM plant tracker) and gem.wiki are leads only, never refs. Crude, NGL and refined-product lines are out '
        'of scope. Puerto Rico is out of scope.',
    ])
    json.dump(a, open(f'{stg}/args.json', 'w'), ensure_ascii=False)
    print(key, len(out), 'seeds', len(a['roster']), 'roster')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('slices', nargs='*')
    p.add_argument('--model-search', required=True)
    p.add_argument('--model-vet', required=True)
    p.add_argument('--model-consolidate', required=True)
    p.add_argument('--not-checked', action='store_true')
    o = p.parse_args()
    m = {'model': o.model_search, 'modelSearch': o.model_search, 'modelVet': o.model_vet, 'modelConsolidate': o.model_consolidate}
    for k in (o.slices or ['gulf', 'tx-permian', 'appalachian-se', 'midcon-north', 'west-ne-ak']):
        if os.path.exists(f'{ST}/discovery-datacenter-{k}-retry2-{DATE}/staged_new.json'):
            build(k, m, o.not_checked)
