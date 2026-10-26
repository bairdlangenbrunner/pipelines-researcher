"""Build the 2026-10-19 utility gas plant run: plants of 300 MW or more in development, grouped by parent owner (run from repo root).

Step 2 of the 2026-10-19 status note (gem-desk grants/beyond-carbon). Ruling 6 (2026-10-18): a pipeline that supplies a gas
plant is a data center row when the plant's filings, developer, or utility tie THAT plant to data center load. The earlier
plant seeds covered only plants GOGPT tags captive for a data center; this run covers the utility plants. Plants: US GOGPT
units with gas in Fuel, status announced, pre-construction or construction, summed by GEM location ID to 300 MW or more,
minus plants already seeded (seeds_by_region.json) and plants GOGPT flags for a data center. One seed per parent owner (split
into seeds of five plants for big fleets), owners ranked by the MW of their new-site and coal-to-gas conversion plants; replacements at coal sites ride along as
lower priority. --part a = owners 1 to 20, --part b = owners 21 to 40. Writes args.json, roster.txt, and args_wf.json (the
roster replaced by a pointer to roster.txt, small enough to pass to the workflow). Models are chosen on the command line.
"""
import argparse, glob, json, os, re, sys
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from build_slice_args import ST, D, SEEDS  # noqa: E402
from build_recheck_args import VET_1019, SCOPE_1019  # noqa: E402
import subprocess

DATE = '20261019'
GOGPT = f'{D}/work/gogpt_{DATE}.csv'
DCX = re.compile(r'data.?cent|hyperscal|artificial intel|Stargate', re.I)
SHARE = re.compile(r'\s*\[[^\]]*\]\s*')
PER_SEED = 5
ALIAS = {'Blackstone Group Inc': 'Blackstone Inc'}  # one company under two GEM spellings

INTRO = (
    "Each seed is one utility or power company (the parent owner in GEM's plant tracker) and its gas plants of 300 MW or more "
    "in development. For EACH plant in the hint, answer two questions. (A) How does the gas arrive: a new lateral, a loop or "
    "expansion of an interstate or intrastate line, a utility-built line, or an existing line already at the site (coal "
    "conversions often need a new lateral). Name the pipeline sponsor and project when a source does. (B) Is THAT plant tied "
    "to data center load by its own filings (certificate or siting case, air permit, integrated resource plan section on the "
    "plant), its developer, or the utility (a large-load contract, a named hyperscaler, data center load named among the "
    "plant's reasons). Company-wide data center talk not about this plant is not a tie. Only a pipeline whose plant is tied "
    "is a candidate. A tied plant with a named supply project and sponsor is NEW_ROW even without endpoints or length "
    "(ruling 8). A tied plant served by a pipeline that is already a roster row is EXISTING_ROW (a tag lead, the ref for the "
    "plant tie in evidence). A plant with no tie gets one line in the ledger reason and no candidate. A plant served by an "
    "existing line with no new pipe is ONSITE_NO_PIPE. The ledger reason covers every plant in the seed, one short line "
    "each, starting with its outcome code: NEW_ROW, EXISTING_ROW, ONSITE_NO_PIPE, NOT_FOUND, NO_DC_TIE, OUT_OF_SCOPE.")
SEARCH = (
    "Per plant: search the plant name with 'data center', the utility's certificate or resource plan docket for the plant, "
    "and the plant name with 'pipeline' or 'lateral' or 'gas supply'. Then FERC and Federal Register for a CP docket or "
    "blanket prior notice naming the plant, the state regulator or siting board, the pipeline sponsor's project page and "
    "earnings materials, and trade press (Utility Dive, Pipeline and Gas Journal, Natural Gas Intelligence, Data Center "
    "Dynamics). A blocked page is not a dead end: run python scripts/fetch.py <url> --head 4000, then the Wayback copy. GOGPT "
    "and gem.wiki are leads only, never refs.")
BUDGET = (
    "Budget: about 3 web searches per plant, at most 14 per seed; spend more on the plants with a data center lead. Pace "
    "searches a few seconds apart; if a search fails, wait and retry before giving up. End each ledger reason with "
    "'Searches run: N.' and a plain list of the sources checked and what each showed.")


def plants():
    g = pd.read_csv(GOGPT, low_memory=False, keep_default_na=False, na_values=[])
    u = g[(g['Country/Area'] == 'United States') & g.Fuel.str.contains('gas', case=False)
          & g.Status.isin(['announced', 'pre-construction', 'construction'])].copy()
    u['mw'] = pd.to_numeric(u['Capacity (MW)'], errors='coerce').fillna(0)
    seeded = {m.group(1) for s in SEEDS for m in [re.search(r'GEM location (L\d+)', s.get('name_hint', ''))] if m}
    out = []
    for loc, p in u.groupby('GEM location ID'):
        mw = p.mw.sum()
        if mw < 300 or loc in seeded:
            continue
        if p['Captive industry type'].str.contains('data cent', case=False).any() or p.Notes.str.contains(DCX).any():
            continue
        r = p.iloc[0]
        conv = ' '.join(dict.fromkeys(x for x in p['Conversion/replacement?'] if x))
        frm = ' '.join(dict.fromkeys(x for x in p['Conversion from/replacement of (fuel)'] if x))
        coal = 'coal' in frm
        kind = ('coal conversion' if 'conversion' in conv and coal else 'coal replacement' if coal
                else conv + (f' of {frm}' if frm else '') if conv else 'new site')
        parent = SHARE.split((r['Parent(s)'] or r['Owner(s)']).split(';')[0])[0].strip() or 'unknown'
        parent = ALIAS.get(parent, parent)
        out.append({'loc': loc, 'name': r['Plant name'], 'parent': parent, 'owner': r['Owner(s)'], 'mw': round(mw),
                    'status': '/'.join(sorted(set(p.Status))), 'start': '/'.join(sorted({str(x) for x in p['Start year'] if x})),
                    'place': ', '.join(x for x in [r.City, r['Local area (taluk, county)'], r['State/Province']] if x),
                    'latlon': f"{r.Latitude}, {r.Longitude}", 'kind': kind, 'priority': kind in ('new site', 'coal conversion')})
    return out


def owner_seeds(ps, part):
    df = pd.DataFrame(ps)
    rank = df[df.priority & (df.parent != 'unknown')].groupby('parent').mw.sum().sort_values(ascending=False)  # no owner group to search
    owners = list(rank.index[:20] if part == 'a' else rank.index[20:40])
    seeds = []
    for o in owners:
        sub = df[df.parent == o].sort_values(['priority', 'mw'], ascending=[False, False])
        lines = [f"{x['name']} (GEM location {x['loc']}): {x['mw']} MW, {x['status']}, start {x['start'] or 'unknown'}, "
                 f"{x['kind']}{'' if x['priority'] else ' (lower priority)'}, {x['place']} ({x['latlon']}), owner {x['owner']}"
                 for _, x in sub.iterrows()]
        base = 'utility:' + re.sub(r'[^a-z0-9]+', '-', o.lower()).strip('-')[:50]
        parts = [lines[i:i + PER_SEED] for i in range(0, len(lines), PER_SEED)]  # big fleets split so each seed stays searchable
        for k, ls in enumerate(parts, 1):
            tag = f' (group {k} of {len(parts)})' if len(parts) > 1 else ''
            seeds.append({'seed_id': base + (f'-{k}' if len(parts) > 1 else ''), 'kind': 'utility plant owner', 'operator': o,
                          'name': f'{o}: gas supply to its plants in development{tag}', 'length': 'length unknown',
                          'name_hint': f"SOURCE GOGPT utility plants (leads only, never refs) | parent {o}{tag} | "
                                       f"{len(ls)} of its {len(sub)} plant(s), {int(sub.mw.sum())} MW in all | PLANTS: "
                                       + ' || '.join(ls)})
    return seeds, rank


def build(models, part, chunk):
    stg = f'{ST}/discovery-datacenter-utility-{part}-{DATE}'
    os.makedirs(stg, exist_ok=True)
    subprocess.run([sys.executable, 'scripts/build_discovery_context.py', '--tracker', 'gas', '--country', 'United States',
                    '--staging', stg, '--out', f'{stg}/args.json'], capture_output=True, text=True, check=True)
    a = json.load(open(f'{stg}/args.json'))
    ps = plants()
    seeds, rank = owner_seeds(ps, part)
    prior = sorted(d for d in glob.glob(f'{ST}/discovery-datacenter-*') if 'seeds' not in d and not d.startswith(stg)
                   and 'utility' not in d)
    a.update(staging=stg, scopeRule=SCOPE_1019, vetRule=VET_1019, strategies=[], seeds=seeds, seedsOnly=True, seedRetry=True,
             seedIntro=INTRO, seedSearch=SEARCH, seedBudget=BUDGET, seedChunk=chunk, minKm=0, priorStaging=prior, **models)
    a['extra'] = '\n'.join([
        f'## This run: United States gas DATA CENTER pass over utility gas plants, part {part}, {DATE}, seeds only, national.',
        f'{len(seeds)} seeds, one per parent owner, covering {sum(1 for p in ps if p["parent"] in set(rank.index[:40]))} '
        'plants in the first 40 owners overall. Ruling 6 (in the vet rule): a pipeline that supplies a plant tied to data '
        'center load is a data center row. Ruling 8: a sponsor and a named project are enough; endpoints are not needed.',
        'Read the priorStaging runs only to learn which new rows and matches they already staged, so you never stage the '
        'same line twice.',
        'The roster is the FULL national roster (pulled 2026-10-19): match against all of it. A matched_existing / '
        'EXISTING_ROW finding is a DataCenter tag lead for that row: put the ref that ties the row to a data center in its '
        'evidence. Do not suggest a plant name as an OtherEnglishNames.',
        'GOGPT (GEM plant tracker) and gem.wiki are leads only, never refs. Crude, NGL and refined-product lines are out of '
        'scope. Puerto Rico and everything outside the US are out of scope.'])
    json.dump(a, open(f'{stg}/args.json', 'w'), ensure_ascii=False)
    open(f'{stg}/roster.txt', 'w').write('\n'.join(a['roster']) + '\n')
    slim = dict(a, roster=[f"THE FULL ROSTER IS IN A FILE, not inline: {stg}/roster.txt ({len(a['roster'])} rows, one per "
                           "line, ALL statuses, format \"PID | PipelineName / SegmentName aka=OtherNames | Start->End | "
                           "status | len dia cap\"). Before deciding any match, grep it for every name variant, operator, "
                           "state and town of your lead (grep -i), and read the hits. Treat every row in that file as if it "
                           "were listed here."])
    json.dump(slim, open(f'{stg}/args_wf.json', 'w'), ensure_ascii=False)
    pd.DataFrame(ps).to_csv(f'{stg}/utility_plants.csv', index=False)
    print(stg, len(seeds), 'seeds;', len(ps), 'plants', len({p['parent'] for p in ps}), 'parents;',
          len(json.dumps(slim, ensure_ascii=False)), 'bytes slim')
    print('owners:', '; '.join(f'{o} {int(m)} MW' for o, m in (rank.iloc[:20] if part == 'a' else rank.iloc[20:40]).items()))


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--part', choices=['a', 'b'], required=True)
    p.add_argument('--model-search', required=True)
    p.add_argument('--model-vet', required=True)
    p.add_argument('--model-consolidate', required=True)
    p.add_argument('--chunk', type=int, default=2)
    o = p.parse_args()
    build({'model': o.model_search, 'modelSearch': o.model_search, 'modelVet': o.model_vet,
           'modelConsolidate': o.model_consolidate}, o.part, o.chunk)
