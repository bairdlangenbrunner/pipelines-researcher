"""Build country-discovery args for the five US gas data center slices, no length floor (run from repo root).

Plan: docs/plans/2026-10-16_us-gas-datacenter-subfloor.md. Each slice: scripts/build_discovery_context.py (full
national roster + discovery_context.json), then this adds the data center scope rule, the vet rule (rulings 1 to 3
plus the 10-02 rules (e) to (h)), data center search strategies, and the slice's seeds from seeds_by_region.json
(sorted eia, lead, plant so each seed chunk holds one source). minKm 0; priorStaging = the slice's 10-02 run.
Models are chosen at dispatch: pass them on the command line as --model-search/--model-vet/--model-consolidate.
"""
import argparse, json, os, subprocess, sys
ST = 'batches/united-states-gas/staging'
D = f'{ST}/discovery-datacenter-seeds-20261016'
SEEDS = json.load(open(f'{D}/seeds_by_region.json'))['seeds']
DATE = '20261016'
ORDER = {'eia': 0, 'lead': 1, 'plant': 2}
SLICES = {
 'tx-permian': ('Texas + New Mexico',
   'Oracle and OpenAI Stargate at Abilene (Energy Transfer Hugh Brinson laterals, VoltaGrid), Fermi America HyperGrid at Amarillo, Google / Intersect Power at Deaf Smith County (NGPL Amarillo Expansion), Kinder Morgan Creekside, Permian behind-the-meter data center power (Pacifico, Stargate Milam County, Shackelford County), New Mexico Project Jupiter (Dona Ana County, Green Chile)',
   [('dc-intrastate', 'Texas INTRASTATE laterals to data center campuses and their gas plants, which never appear in FERC: Texas Railroad Commission T-4 permits and the RRC public GIS viewer (search the operator and county of each data center campus in Texas), TCEQ air permits for the plant that name the gas supplier, intrastate operators (Energy Transfer, Enterprise, Kinder Morgan Texas, ONEOK/EnLink, Targa, WhiteWater, Atmos Pipeline-Texas). FERC silence is not an existence concern.')]),
 'gulf': ('Louisiana, Mississippi, Alabama, Florida and the Gulf of Mexico offshore',
   'Meta Hyperion at Richland Parish (Entergy Louisiana gas plants, the Tiger lateral and its expansion), Kosciusko Junction and Mississippi data centers (Amazon Madison County, xAI Southaven), Alabama and Florida utility plants built for data center load',
   [('dc-intrastate', 'Louisiana and Mississippi intrastate laterals to data center plants: Louisiana Office of Conservation pipeline permits, LDNR coastal use permits, Louisiana PSC Entergy dockets that name the gas supply, Mississippi PSC. FERC silence is not an existence concern.')]),
 'appalachian-se': ('Pennsylvania, Ohio, West Virginia, Virginia, Maryland, Delaware, Kentucky, Tennessee, Georgia, South Carolina, North Carolina',
   'Homer City and Shippingport in Pennsylvania, Ohio behind-the-meter data center plants (DT Midstream NEXUS interconnect, Williams Socrates for Meta in New Albany), Transco Southeast Supply Enhancement and Central Virginia Capacity in the Virginia data center belt, MVP Boost and Southgate, Georgia Power and Duke data center load, xAI Memphis (Tennessee)',
   [('dc-intrastate', 'State-regulated laterals to data center plants: Pennsylvania PUC, Ohio Power Siting Board certificates (the board lists gas pipelines with their end user), West Virginia PSC, Virginia SCC, Tennessee and Georgia PSC dockets. Utility distribution mains are out of scope; a dedicated transmission lateral is in. FERC silence is not an existence concern.')]),
 'midcon-north': ('Oklahoma, Kansas, Nebraska, Iowa, Missouri, Arkansas, Illinois, Indiana, Michigan, Wisconsin, Minnesota, North Dakota, South Dakota',
   'Ameren Big Hollow, Indiana and Ohio-border laterals (Dearborn County), North Dakota data center power (Line Section 32, Applied Digital), Wisconsin and Michigan utility plants for Microsoft and Meta campuses, Oklahoma and Arkansas data center plants',
   [('dc-intrastate', 'State-regulated laterals to data center plants: Oklahoma Corporation Commission, Kansas KCC, Iowa Utilities Commission permits, Minnesota PUC, North Dakota PSC siting, Wisconsin PSC, Michigan PSC Act 9 certificates, Indiana IURC, Illinois Commerce Commission. FERC silence is not an existence concern.')]),
 'west-ne-ak': ('the West (California, Nevada, Utah, Arizona, Colorado, Wyoming, Montana, Idaho, Oregon, Washington), Alaska, and the Northeast (New York, New Jersey, Connecticut, Massachusetts, Rhode Island, New Hampshire, Vermont, Maine)',
   'Tallgrass Cheyenne Power Hub and Wyoming data center power (Naughton conversion, Prometheus Hyperscale), Utah behind-the-meter campuses (Delta / Millard County, Joule), Arizona and Nevada data center gas plants, Pacific Northwest data center load (Kelso-Beaver), New York and New Jersey data center plants',
   [('dc-intrastate', 'State-regulated laterals to data center plants: Wyoming Industrial Siting, Utah PSC, Arizona Corporation Commission line siting, Nevada PUCN, Colorado PUC, Oregon EFSC, Washington EFSEC, New York PSC Article VII. FERC silence is not an existence concern.')]),
}
SCOPE = ("Natural gas pipelines tied to the US data center buildout, at ANY length (Baird 2026-10-16, no floor): a "
         "transmission line, lateral, loop or expansion whose sourced purpose is to supply a data center, a data "
         "center campus, or a gas power plant built for one. Compression-only expansions tied to data centers count "
         "(LengthKnown 0). OUT: pipe inside the plant fence, local utility distribution mains, field gathering, and "
         "power-plant laterals with no data center tie (those are monitor when under 25 km; 25 km or more was covered "
         "by the 2026-10-02 discovery). Crude, NGL and refined-product lines are out of scope. If you cannot establish "
         "a length, still emit it and say 'length unknown'.")
VET = ("(d) DATA CENTER RULES (Baird 2026-10-16, docs/plans/2026-10-16_us-gas-datacenter-subfloor.md). 1 (loosened later on 2026-10-16): "
       "DataCenter = yes with a validated ref that names THIS pipeline and mentions data centers at all as a demand driver "
       "or a reason for the project (the filing, the developer, the shipper, EIA, or press). One of several named drivers "
       "counts; so does a shipper whose demand for this project the source ties to data centers. Data center talk that is "
       "company-wide and not about this project, comes only from opponents, or concerns another row leaves DataCenter "
       "blank with a note in researcher_notes. 2: a compression-only expansion tied to data centers is a new_row with LengthKnown = 0, "
       "LengthKnownUnits = mi (or km as the source states), Diameter blank, RouteType 'Capacity expansion only', "
       "RouteAccuracy 'no route', in the parent-system / SegmentName shape of (e); the parent row is not tagged for it. "
       "3: no length floor for a pipeline tied to data centers; in-fence plant piping and utility distribution mains are "
       "out. A sourced line with no data center tie and under 25 km -> class monitor, monitor_reason 'no data center tie'. "
       "(e) EXPANSION ROWS: GEM tracks US expansion projects as their own rows, with PipelineName = the parent system's GEM "
       "PipelineName exactly as the roster spells it and SegmentName = the project (e.g. P2544 'Transcontinental Gas "
       "Pipeline' / 'Hillabee Expansion Project, Phase 2'). An expansion with no row of its own is a new_row in that shape, "
       "not a match to the parent system's row. A project that IS an existing row under another name is matched_existing. "
       "(f) EIA (sources/eia_pipeline_projects/NOTES.md): cite the DATED release that states the value as "
       "https://www.eia.gov/naturalgas/pipelines/<file> (newest is EIA-NaturalGasPipelineProjectsAug2026.xlsx; never the "
       "undated twin), sheet + Excel row in the note, url_verifier with --name set to the EIA project name. Local copies "
       "are in sources/eia_pipeline_projects/raw/. Pair EIA with a FERC order/filing, a state regulator document or an "
       "operator release when cheap. EIA 'Cost (millions)' -> stage the full number (450 -> 450000000, USD). EIA miles -> "
       "LengthKnown in mi, never converted. EIA 'Additional Capacity' is INCREMENTAL MMcf/d for an expansion. Status: "
       "Announced/Pre-filing/Applied/Approved -> proposed, Construction -> construction, Completed -> operating, On Hold -> "
       "shelved, Cancelled/Denied -> cancelled. Month cells are integers 1-12. (g) Country = United States; Puerto Rico is "
       "out of scope. Intrastate lines never appear in FERC: FERC silence is not an existence concern; check the state "
       "regulator (Texas RRC T-4 etc.). (h) Owner names in the ownership team's style: run scripts/entity_lookup.py and "
       "scripts/entity_style.py, adopt the team's spelling on an exact/alias hit only. Notes are plain language for a "
       "person: short sentences, sources named by what they are, no repo jargon, no em-dashes or arrows.")
SEED_INTRO = (
 "Seeds come from three sources, named by the seed_id prefix and the 'SOURCE' label in each hint.\n"
 "eia: a project from EIA's Natural Gas Pipeline Projects workbook (2024 or later release, or in service 2024+) whose "
 "demand served or notes name data centers or power, with NO strong GEM match on the fresh crosswalk. 'weak crosswalk "
 "hints' list PIDs that may be the parent system or the same project under another name: check those first. An "
 "expansion of a GEM system with no row of its own is a candidate in the parent-system / SegmentName shape. A "
 "'strong crosswalk match' seed (Nueva Era Dos, PLUSS) is in the list because it is short power-demand pipe Baird "
 "named: decide whether the match is right or the project deserves its own row. Power demand alone, no data center "
 "tie, under 25 km -> monitor 'no data center tie'.\n"
 "lead: a named lead from a web survey of data center pipelines. The hint carries what the survey found and its "
 "sources; verify everything yourself.\n"
 "plant: a GOGPT gas power plant built for a data center (GEM's own plant tracker, so it is a LEAD, never a ref). Your "
 "job is to find HOW THE PLANT GETS ITS GAS. The hint lists the nearest GGIT routes with distances. Each plant seed "
 "ends in one of four outcomes; start the ledger reason with the outcome code:\n"
 "  NEW_LATERAL: a dedicated new lateral or pipeline (any length) that GEM lacks -> candidate + 'queued'.\n"
 "  EXISTING_ROW: it is supplied directly by an existing roster row (a tap on that line, or a lateral that already has "
 "a row) -> 'matched' with matched_project_id and the evidence URL naming both the pipeline and the plant. This is a "
 "DataCenter tag lead for that row, NOT an alias: never suggest the plant name as an OtherEnglishNames.\n"
 "  ONSITE_NO_PIPE: supplied by an on-site, in-fence or behind-the-meter tap with no new pipe, or by a utility "
 "distribution main -> 'monitor' with what you found.\n"
 "  NOT_FOUND: no source says how it gets gas -> 'monitor' saying what you searched. A 'gogpt-notes' plant that is "
 "not actually built for a data center (the notes only mention utility load or say it is not for a data center) -> "
 "'dropped' with why.\n"
 "Several seeds may be one project (an EIA lateral, a lead and the plant it feeds): give them the same candidate and "
 "say so.")
SEED_SEARCH = (
 "for eia: seeds, EIA's own row first (sources/eia_pipeline_projects/raw/ and data/eia_projects_latest.csv; cite the "
 "dated release URL https://www.eia.gov/naturalgas/pipelines/<file>), then the FERC docket, the operator's project page "
 "or earnings release, the state regulator. For plant: seeds, the plant's state air permit (TCEQ, Ohio EPA, and the "
 "like) or siting application often names the gas supplier and the lateral; then the developer's and the midstream "
 "company's releases and earnings calls, Texas RRC T-4 permits in that county for Texas plants, FERC for interstate "
 "taps, local news on the campus")
def strategies(scope, leads, extra):
    base = [
     ('dc-news', f'News, earnings releases and earnings-call transcripts for {scope}: natural gas pipelines, laterals and expansions built or proposed to serve data centers or the gas plants that power them (2023 to now). Thematic leads: {leads}. Midstream companies now name data center laterals in quarterly releases (Energy Transfer, Kinder Morgan, Williams, DT Midstream, Boardwalk, Enbridge, TC Energy, EQT, Tallgrass); read them in full. Any length counts.'),
     ('dc-regulators', f'Regulatory paper trail for {scope}: FERC certificate and prior-notice filings (CP dockets, blanket certificate prior notices for short laterals) and Federal Register notices whose shipper or end user is a data center or a plant built for one; state siting dockets for gas laterals to data center campuses. Any length counts.'),
    ]
    return [{'key': k, 'brief': b} for k, b in base + list(extra)]
def build(key, models):
    scope, leads, extra = SLICES[key]
    stg = f'{ST}/discovery-datacenter-{key}-{DATE}'
    os.makedirs(stg, exist_ok=True)
    subprocess.run([sys.executable, 'scripts/build_discovery_context.py', '--tracker', 'gas', '--country', 'United States',
                    '--staging', stg, '--out', f'{stg}/args.json'], capture_output=True, text=True, check=True)
    a = json.load(open(f'{stg}/args.json'))
    seeds = sorted((s for s in SEEDS if s['region'] == key), key=lambda s: ORDER[s['source']])
    seeds = [{k: v for k, v in s.items() if k in ('seed_id', 'name', 'length', 'kind', 'operator', 'name_hint')} for s in seeds]
    a.update(staging=stg, scopeRule=SCOPE, vetRule=VET, strategies=strategies(scope, leads, extra), seeds=seeds,
             seedIntro=SEED_INTRO, seedSearch=SEED_SEARCH, seedChunk=8, minKm=0,
             priorStaging=[f'{ST}/discovery-{key}-20261002'], **models)
    a['extra'] = '\n'.join([
        f'## This run: United States gas DATA CENTER discovery, region {key} = {scope}',
        'Search ONLY this region. A multi-state line is in this slice when it STARTS here; a line that only passes through '
        'or ends here: report it with "out_of_slice": true in why_maybe_new. The roster below is the FULL national roster - match against all of it.',
        'Window: pipelines built or proposed for data center demand, 2023 to now.',
        'No length floor (Baird 2026-10-16): any sourced length, 0 for compression-only, as long as the pipeline is tied to '
        'a data center. A matched_existing / EXISTING_ROW finding is a DataCenter tag lead for that row: put the ref that '
        'ties the row to a data center in its evidence. Do not suggest a plant or campus name as an OtherEnglishNames.',
        'The 2026-10-02 discovery for this region (priorStaging) already covered lines of 25 km or more of any purpose; '
        'do not re-report its candidates.',
        'GOGPT (GEM plant tracker) and gem.wiki are leads only, never refs. Crude, NGL and refined-product lines are out of '
        'scope. Puerto Rico is out of scope.',
    ])
    json.dump(a, open(f'{stg}/args.json', 'w'), ensure_ascii=False)
    print(key, len(seeds), 'seeds', len(a['roster']), 'roster', len(a['strategies']), 'strategies', len(json.dumps(a, ensure_ascii=False)), 'bytes')
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
