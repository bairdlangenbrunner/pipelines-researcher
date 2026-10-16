"""Build the second seedsOnly retry runs (Baird 2026-10-16: "retry everything that was not retried, make sure your search is
COMPREHENSIVE"). Run from the repo root.

Per region, the pool is every seed the 10-16 slice run left as monitor or dropped that the first retry did not cover, plus
every candidate the slice run vetted to monitor (re-entered as a seed carrying what the first pass found). Each goes to
discovery-datacenter-<region>-retry2-20261016 with a required search checklist, and every monitor reason must list what
was searched.
"""
import argparse, json, os, subprocess, sys

sys.path.insert(0, os.path.dirname(__file__))
from build_slice_args import SLICES, SCOPE, VET, SEED_INTRO, ST, DATE  # noqa: E402

CHECKLIST = (
 "COMPREHENSIVE SEARCH (required for every seed; a seed that ends monitor must list in its reason each source below that "
 "was checked and what it showed, in plain words): (1) EIA's Natural Gas Pipeline Projects workbook, newest release "
 "(sources/eia_pipeline_projects/raw/, data/eia_projects_latest.csv), by operator, county and plant name; (2) FERC: "
 "eLibrary and Federal Register searches for the plant, campus, developer and county, including CP dockets and blanket "
 "certificate prior notices (short laterals and taps are usually prior notices); (3) the state regulator: the public "
 "utility commission or siting board docket (Ohio Power Siting Board, Virginia SCC, Kentucky PSC, Georgia PSC, Indiana "
 "IURC, Wisconsin PSC, Louisiana PSC and the like), and for Texas the Railroad Commission T-4 permits and its pipeline "
 "GIS viewer for the county; (4) the state air permit or its public notice (TCEQ, Ohio EPA, Pennsylvania DEP and the "
 "like), which often names the gas supplier and the lateral; (5) the utility's integrated resource plan or rate case if a "
 "utility builds the plant; (6) county and city records and local news: zoning and planning agendas, commission minutes, "
 "road-crossing or easement notices; (7) the developer's, the hyperscaler's and the midstream company's releases, project "
 "pages, investor decks and earnings-call transcripts (Energy Transfer, Kinder Morgan, Williams, Enbridge, TC Energy, "
 "Boardwalk, DT Midstream, EQT, Atmos, ONEOK, Targa, Tallgrass, Southwest Gas, local distribution companies); (8) trade "
 "press (Pipeline and Gas Journal, Natural Gas Intelligence, RBN, Data Center Dynamics, Utility Dive, E&E News). Search "
 "each in English with several name variants (plant, campus, code name, developer, county, nearest town). Do at least "
 "eight distinct searches per seed before NOT_FOUND. A blocked page is not a dead end: run python scripts/fetch.py <url> "
 "--head 4000, then the Wayback copy, before giving up on it. GOGPT and gem.wiki stay leads only, never refs. "
 "For eia: seeds, start from EIA's own row and cite the dated release URL https://www.eia.gov/naturalgas/pipelines/<file>.")

INTRO_EXTRA = (
 "\nmonitor: a candidate the 10-16 slice run vetted to monitor (an existing lead with its own slug). The hint carries the "
 "values and the reason it was held. Re-research it from scratch: find endpoints, length and a concrete step, and test "
 "the data center tie against the loosened ruling 1 (data centers mentioned at all as a reason for the project count). "
 "If it now qualifies, it is a candidate + 'queued'; otherwise 'monitor' with what was searched.\n"
 "dropped: a seed the slice run dropped. Check the drop reason again; reverse it only on a source.")


def pool(key):
    base = f'{ST}/discovery-datacenter-{key}-{DATE}'
    a = json.load(open(f'{base}/args.json'))
    d = json.load(open(f'{base}/staged_new.json'))
    seeds = {s['seed_id']: s for s in a['seeds']}
    retried = set()
    r1 = f'{ST}/discovery-datacenter-{key}-retry-{DATE}/args.json'
    if os.path.exists(r1):
        retried = {s['seed_id'] for s in json.load(open(r1))['seeds']}
    out = []
    for led in d['meta']['seed_ledger']:
        if led['disposition'] in ('monitor', 'dropped') and led['seed_id'] not in retried:
            s = dict(seeds[led['seed_id']])
            s['name_hint'] = (s.get('name_hint', '') + f" | FIRST PASS ({led['disposition']}): {led.get('reason', '')}").strip(' |')
            out.append({k: v for k, v in s.items() if k in ('seed_id', 'name', 'length', 'kind', 'operator', 'name_hint')})
    for c in d['candidates']:
        if c['class'] == 'monitor' and c.get('slug'):
            urls = [x['url'] for x in c.get('verifications', []) if x.get('url')][:5]
            out.append({'seed_id': f"monitor:{c['slug']}", 'name': c.get('name') or c['slug'],
                        'length': 'unknown', 'kind': 'monitor candidate', 'operator': '',
                        'name_hint': f"SOURCE: 10-16 slice candidate held as monitor | pages read: {', '.join(urls)} | "
                                     f"notes: {c.get('researcher_notes', '')} | FIRST PASS (monitor): {c.get('monitor_reason', '')}"})
    return out


def build(key, models):
    out = pool(key)
    if not out:
        print(key, 'nothing to retry')
        return
    stg = f'{ST}/discovery-datacenter-{key}-retry2-{DATE}'
    os.makedirs(stg, exist_ok=True)
    subprocess.run([sys.executable, 'scripts/build_discovery_context.py', '--tracker', 'gas', '--country', 'United States',
                    '--staging', stg, '--out', f'{stg}/args.json'], capture_output=True, text=True, check=True)
    a = json.load(open(f'{stg}/args.json'))
    scope, leads, extra = SLICES[key]
    prior = [f'{ST}/discovery-{key}-20261002', f'{ST}/discovery-datacenter-{key}-{DATE}']
    if os.path.exists(f'{ST}/discovery-datacenter-{key}-retry-{DATE}'):
        prior.append(f'{ST}/discovery-datacenter-{key}-retry-{DATE}')
    a.update(staging=stg, scopeRule=SCOPE, vetRule=VET, strategies=[], seeds=out, seedsOnly=True,
             seedIntro=SEED_INTRO + INTRO_EXTRA, seedSearch=CHECKLIST, seedChunk=3, minKm=0, priorStaging=prior, **models)
    a['extra'] = '\n'.join([
        f'## This run: United States gas DATA CENTER discovery, region {key} = {scope}. SECOND RETRY, seeds only.',
        f'These {len(out)} seeds were left monitor or dropped by {prior[1]} and never retried. Treat each as fresh and '
        'research it in full under the COMPREHENSIVE SEARCH checklist. The FIRST PASS text in each hint is what the '
        'earlier pass found; it is a starting point, never a conclusion. Read the priorStaging runs first only to learn '
        'which new rows and matches they already staged, so you never stage the same line twice.',
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
    print(key, len(out), 'seeds', len(a['roster']), 'roster', len(json.dumps(a, ensure_ascii=False)), 'bytes')


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
