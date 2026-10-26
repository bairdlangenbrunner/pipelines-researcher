"""Build the 2026-10-19 re-vet run: the 26 monitor leads marked for re-check plus the new 2026-10-18 survey leads (run from repo root).

Rulings 6 to 8 (Baird 2026-10-18, docs/plans/2026-10-16_us-gas-datacenter-subfloor.md): a tie through a power plant counts,
big interstate expansions with an indirect tie are in, and endpoints are not needed for a data center pipeline row (sponsor
plus a named project). One national seedsOnly run with seedRetry, the comprehensive budget, and every earlier data center run
as priorStaging so nothing is staged twice. Models are chosen at dispatch on the command line.
"""
import argparse, csv, glob, json, os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(__file__))
from build_slice_args import ST, D, SCOPE, VET  # noqa: E402

DATE = '20261019'
MONITOR = 'batches/united-states-gas/deliverables/US_gas_datacenter_monitor_2026-10-18_watch.csv'
SURVEY = f'{D}/survey-2026-10-18'

RULES_1018 = (
    " (i) RULINGS 6 TO 8 (Baird 2026-10-18) AND 10 (2026-10-19), on top of (d). 6: a tie THROUGH A POWER PLANT counts. A pipeline, lateral or "
    "expansion that supplies a gas plant is DataCenter = yes when the plant's own filings, its developer, or the utility tie "
    "THAT PLANT to data center load. A named campus or customer is high specificity; data center load named among the plant's "
    "reasons is medium. Company-wide resource-plan talk about data centers, not about this plant, stays blank. The ref for the "
    "tag must name the pipeline; a second ref may carry the plant's data center tie, and DataCenterNotes says how the two "
    "connect (pipeline serves plant X; plant X is tied to data center Y by source Z). Tag the expansion or lateral serving "
    "the plant, never a legacy mainline it hangs off. 7: big interstate expansions with such an indirect tie are included. "
    "8 AS LOOSENED BY 10 (Baird 2026-10-19): for a pipeline tied to data centers, the ONLY add-threshold is a real "
    "pipeline project that serves a data center or the energy supply to one: a source (announcement, filing, permit or "
    "credible press) describes the pipeline project and ties it to a data center, directly or through the plant it "
    "supplies (ruling 6). Endpoints, the state, length and route are NOT needed; a project with no disclosed location is "
    "still new_row, never monitor for that reason. Fill StartState/Province when it can be inferred (the sponsor's other "
    "assets, the plant it serves) and say in researcher_notes that it is inferred and why. StartLocation, EndLocation, "
    "LengthKnown and the route stay blank until a source gives them (RouteAccuracy 'no route'). A tie guessed from a "
    "line's name is not a tie. This loosening applies to data center rows only.")
VET_1019 = VET + RULES_1018
SCOPE_1019 = SCOPE.replace("or a gas power plant built for one.",
                           "or a gas power plant built for one or tied to data center load by its owner, developer or "
                           "utility (ruling 6, 2026-10-18).")

INTRO = (
    "Seeds come from two sources, named by the seed_id prefix.\n"
    "recheck: a lead an earlier data center pass left on the monitor list, now marked for re-check because rulings 6 to 8 "
    "(2026-10-18) may turn it into a row or a tag: a tie through a power plant now counts, and endpoints are not needed. "
    "The hint carries the last researcher's reason and the run it came from. It is a starting point, never a conclusion: "
    "re-research the tie under the new rulings, and when the sponsor and project are named, stage the row even without "
    "endpoints or length. When the pipeline turns out to be an existing roster row, it is 'matched' (a DataCenter tag lead "
    "for that row) with the ref that ties it to data centers in evidence.\n"
    "survey: a new lead from the 2026-10-18 web survey of gathering, utility and Texas permit infrastructure. The hint "
    "carries what the survey found and the URLs it read; verify everything yourself. Several Texas leads come from Texas "
    "Railroad Commission new construction reports (Form PS-48 PDFs); a report is a valid ref for the line's operator, "
    "county, length, diameter and start date, but a data center tie guessed from a line's NAME is not a tie: find a source "
    "that says what the line serves. Check the roster first: some survey leads may already be rows (Hugh Brinson P8318 "
    "Abilene Laterals, Licking County Pipeline P8320, Prosperity Line P8234, Transwestern Green Chile P8290).\n"
    "Outcome codes for the ledger reason (start with one): NEW_ROW, EXISTING_ROW (matched, tag lead), ONSITE_NO_PIPE, "
    "NOT_FOUND, NO_DC_TIE (pipeline real, no data center tie even under ruling 6), OUT_OF_SCOPE.")

SEARCH = (
    "COMPREHENSIVE SEARCH, focused on the two questions the new rulings open: (A) is there a source tying this pipeline, or "
    "the power plant it feeds, to data center load (the plant's air permit or siting case, the utility's certificate or "
    "rate case for THIS plant, the developer's or hyperscaler's release, the large-load or electric service agreement "
    "docket); (B) who sponsors the pipeline and what is it called (FERC eLibrary and Federal Register for CP dockets and "
    "blanket prior notices, the state regulator or siting board, the Texas Railroad Commission new construction reports "
    "and T-4 permits, midstream earnings releases and call transcripts, trade press). Search with several name variants "
    "(project, plant, campus, developer, county). A blocked page is not a dead end: run python scripts/fetch.py <url> "
    "--head 4000, then the Wayback copy. For EIA seeds, cite the dated release URL https://www.eia.gov/naturalgas/"
    "pipelines/<file>. GOGPT and gem.wiki stay leads only, never refs.")

BUDGET = (
    "Budget: at least 6 distinct web searches per seed, more when a lead appears; read the most promising pages in full "
    "(python scripts/fetch.py <url>). Pace searches a few seconds apart; if a search fails, wait and retry before giving up. "
    "End each ledger reason with 'Searches run: N.' and a plain list of the sources checked and what each showed.")


def monitor_seeds():
    out = []
    for r in csv.DictReader(open(MONITOR)):
        if not r['Re-check under new rulings']:
            continue
        sid = 'recheck:' + re.sub(r'[^a-z0-9]+', '-', r['Lead ID'].split(':', 1)[1].lower()).strip('-')
        hint = ' | '.join(x for x in [
            f"SOURCE recheck: {r['Kind']}", r['State'] and f"state {r['State']}",
            r['Developer or owner'] and f"developer/owner {r['Developer or owner']}",
            r['Plant MW'] and f"plant {r['Plant MW']} MW, {r['Plant status (GOGPT)']}, start {r['Plant start year']}",
            r['Nearest GGIT pipelines'] and f"nearest GGIT routes: {r['Nearest GGIT pipelines']}",
            f"on the list because: {r['Why it is on the list']}",
            f"LAST CHECK ({r['Last checked']}, {r['Staging run']}): {r['Researcher reason (last check)']}",
            r['Links the researcher cited (not re-checked)'] and f"links cited then: {r['Links the researcher cited (not re-checked)']}",
        ] if x)
        out.append({'seed_id': sid, 'name': r['Lead'], 'length': r['Length (if known)'] or 'length unknown',
                    'kind': 'monitor lead, re-check', 'name_hint': hint})
    return out


def survey_seeds():
    """The survey leads section 5 of the gem-desk status note lists as new and qualifying, not yet in GGIT."""
    gath = {p['name']: p for p in json.load(open(f'{SURVEY}/survey_gathering.json'))['projects']}
    ldc = {p['name']: p for p in json.load(open(f'{SURVEY}/survey_ldc.json'))['projects']}
    rrc = {p['name']: p for p in json.load(open(f'{SURVEY}/survey_rrc_taps.json'))['rrc']['data_center_permits']}

    def hint(p):
        urls = '; '.join(f"{u['url']} ({u.get('what', '')})" for u in p.get('urls', []) if u.get('verified'))
        bits = [f"{k}: {p[k]}" for k in ('builder_or_supplier', 'utility_or_builder', 'operator', 'state', 'county', 'serves',
                                         'length_km', 'diameter_in', 'status', 'evidence') if p.get(k) not in (None, '')]
        return 'SOURCE survey 2026-10-18 | ' + ' | '.join(bits) + (f' | survey URLs: {urls}' if urls else '')

    picks = [
        (gath, 'Woodway dedicated pipeline for hyperscale data center', 'survey:woodway-hyperscale-line'),
        (gath, 'Monarch Compute Campus gas line (Hope Gas)', 'survey:monarch-campus-line-hope-gas'),
        (gath, 'AEP fuel cell data center pipeline (Hope Utilities / NEO)', 'survey:hope-utilities-aep-fuel-cell-line'),
        (ldc, 'PowerConneX New Albany 3 pipeline', 'survey:powerconnex-iii-supply-line'),
        (gath, 'Kinetik residue connections to power plants (Pecos Power, Basin Ranch)', 'survey:kinetik-residue-pecos-basin-ranch'),
        (rrc, 'Stargate Pipeline, 24in', 'survey:rrc-stargate-pipeline-24in'),
        (rrc, 'Abilene 2.0 and Abilene 3.0', 'survey:rrc-abilene-2-and-3'),
        (rrc, 'Bolt Shackelford Datacenter Interconnect', 'survey:rrc-bolt-shackelford-interconnect'),
        (rrc, 'Chevron Power Lateral', 'survey:rrc-whitewater-chevron-power-lateral'),
        (rrc, 'Abilene DC 1, LLC', 'survey:rrc-abilene-dc1-taylor'),
        (rrc, 'Abilene DC 1, LLC (Goodnight gas pipeline)', 'survey:rrc-abilene-dc1-armstrong-goodnight'),
        (rrc, 'Duroc Power Plant lateral', 'survey:rrc-duroc-power-plant-lateral'),
    ]
    out = []
    for src, name, sid in picks:
        p = src[name]
        km = p.get('length_km')
        out.append({'seed_id': sid, 'name': name, 'length': f'survey: ~{km} km' if km else 'length unknown',
                    'kind': 'survey lead', 'operator': p.get('operator') or p.get('builder_or_supplier') or p.get('utility_or_builder') or '',
                    'name_hint': hint(p)})
    return out


def build(models, chunk):
    stg = f'{ST}/discovery-datacenter-recheck-{DATE}'
    os.makedirs(stg, exist_ok=True)
    subprocess.run([sys.executable, 'scripts/build_discovery_context.py', '--tracker', 'gas', '--country', 'United States',
                    '--staging', stg, '--out', f'{stg}/args.json'], capture_output=True, text=True, check=True)
    a = json.load(open(f'{stg}/args.json'))
    seeds = monitor_seeds() + survey_seeds()
    assert len({s['seed_id'] for s in seeds}) == len(seeds)
    prior = sorted(d for d in glob.glob(f'{ST}/discovery-datacenter-*-20261016') if 'seeds' not in d)
    a.update(staging=stg, scopeRule=SCOPE_1019, vetRule=VET_1019, strategies=[], seeds=seeds, seedsOnly=True, seedRetry=True,
             seedIntro=INTRO, seedSearch=SEARCH, seedBudget=BUDGET, seedChunk=chunk, minKm=0, priorStaging=prior, **models)
    a['extra'] = '\n'.join([
        '## This run: United States gas DATA CENTER re-vet, 2026-10-19, seeds only, national.',
        f'{len(seeds)} seeds: leads an earlier pass left on the monitor list that the 2026-10-18 rulings may turn into rows '
        'or tags, and new leads from the 2026-10-18 infrastructure survey. Rulings 6 to 8 (in the vet rule): a tie through a '
        'power plant counts, big interstate expansions with an indirect tie are in, and a data center pipeline needs only a '
        'sponsor and a named project, not endpoints.',
        'Read the priorStaging runs only to learn which new rows and matches they already staged, so you never stage the '
        'same line twice. A seed they left monitor or dropped is re-researched in full.',
        'The roster below is the FULL national roster (pulled 2026-10-19, including the rows appended 2026-10-16 and 10-17): '
        'match against all of it. A matched_existing / EXISTING_ROW finding is a DataCenter tag lead for that row: put the ref '
        'that ties the row to a data center in its evidence. Do not suggest a plant or campus name as an OtherEnglishNames.',
        'GOGPT (GEM plant tracker) and gem.wiki are leads only, never refs. Crude, NGL and refined-product lines are out of '
        'scope. Puerto Rico and everything outside the US are out of scope.',
    ])
    json.dump(a, open(f'{stg}/args.json', 'w'), ensure_ascii=False)
    print(stg, len(seeds), 'seeds', len(a['roster']), 'roster', len(prior), 'prior runs', len(json.dumps(a, ensure_ascii=False)), 'bytes')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--model-search', required=True)
    p.add_argument('--model-vet', required=True)
    p.add_argument('--model-consolidate', required=True)
    p.add_argument('--chunk', type=int, default=4)
    o = p.parse_args()
    build({'model': o.model_search, 'modelSearch': o.model_search, 'modelVet': o.model_vet,
           'modelConsolidate': o.model_consolidate}, o.chunk)
