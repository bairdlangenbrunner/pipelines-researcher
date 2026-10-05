"""Build country-discovery args for the five US gas regional slices (run from repo root).

Each slice: python scripts/build_discovery_context.py (full national roster + discovery_context.json in
the slice dir), then this adds the US scope rule, vet rule, region strategies and the slice's EIA seeds.
"""
import json, os, subprocess, sys
ST = 'batches/united-states-gas/staging'
D = f'{ST}/discovery-seeds-20261002'
SEEDS = json.load(open(f'{D}/seeds_by_region.json'))['seeds']
DATE = '20261002'
SLICES = {
 'tx-permian': ('Texas + New Mexico (incl. the Permian Basin both sides)',
   'Permian takeaway (Waha-to-Gulf Coast, Katy, Agua Dulce, Corpus Christi), Haynesville/East Texas lines into the Gulf LNG belt, LNG feed-gas headers (Port Arthur, Rio Grande, Corpus Christi Stage 3, Freeport, Golden Pass), data-center and power-plant laterals, San Juan Basin NM',
   ('crossborder', 'US-Mexico export lines starting in Texas or New Mexico (Agua Dulce/Nueces/El Paso/Presidio/Del Rio/Roma/McAllen border crossings; SENER/CENAGAS and IEnova/Sempra Infraestructura, TC Energy Mexico project lists) - the US segment is in scope; Mexico-only segments are out of slice.'),
   ('intrastate', 'Texas INTRASTATE pipelines, which never appear in FERC: Texas Railroad Commission T-4 permits and the RRC public GIS viewer, Texas Pipeline Association, intrastate operators (Enterprise, Energy Transfer intrastate, Kinder Morgan Texas, ONEOK/EnLink, Targa, WhiteWater, Atmos Pipeline-Texas, Enbridge Texas). FERC silence is not an existence concern.')),
 'gulf': ('Louisiana, Mississippi, Alabama, Florida and the Gulf of Mexico offshore',
   'Louisiana LNG feed lines (Plaquemines, Calcasieu Pass, CP2, Venture Global Gator Express, Driftwood/Woodside Louisiana Line 200/300, Commonwealth, Delfin), Haynesville-to-Gulf takeaway (LEG, NG3, Gulf Run), Florida supply (Sabal Trail, Florida Southeast Connection, Gulfstream), Mississippi/Alabama storage-hub connectors',
   ('offshore', 'Gulf of Mexico OCS gas pipelines: BOEM pipeline permits and the data.boem.gov pipeline dataset, BSEE, Offshore Magazine Gulf of Mexico maps; large export/trunk lines from deepwater hubs to shore (Discovery, Nautilus, Manta Ray, Destin, Okeanos, Cleopatra, Mardi Gras system) - skip infield flowlines.'),
   ('intrastate', 'Louisiana and Mississippi intrastate pipelines: Louisiana Office of Conservation pipeline division, LDNR coastal use permits, Mississippi PSC, Louisiana intrastate operators (EnLink LIG, Energy Transfer Louisiana Intrastate, Acadian Gas, Bridgeline). FERC silence is not an existence concern.')),
 'appalachian-se': ('Pennsylvania, Ohio, West Virginia, Virginia, Maryland, Delaware, Kentucky, Tennessee, Georgia, South Carolina, North Carolina',
   'Marcellus/Utica takeaway (Rover, NEXUS, Mountaineer XPress, Leach XPress, Atlantic Sunrise, Mariner), MVP Southgate and Boost, Transco Southeast Supply Enhancement, data-center laterals in Virginia/Ohio/Georgia, Columbia Gas/TC Energy KY-VA expansions, utility-owned transmission (Dominion, Piedmont, Atlanta Gas Light, Southern Company Gas)',
   ('intrastate', 'State-regulated transmission: Pennsylvania PUC, Ohio Power Siting Board certificates, West Virginia PSC, Virginia SCC, Georgia/NC/SC PSC dockets, utility transmission lines (Washington Gas, Columbia Gas of Ohio, Piedmont, Dominion Energy Ohio) of 25 km or more.')),
 'midcon-north': ('Oklahoma, Kansas, Nebraska, Iowa, Missouri, Arkansas, Illinois, Indiana, Michigan, Wisconsin, Minnesota, North Dakota, South Dakota',
   'SCOOP/STACK and Anadarko takeaway, Bakken residue-gas lines (WBI Bakken East, Northern Border expansions, Alliance), Midwest power-plant and data-center laterals, Northern Natural Gas and ANR expansions, Rockies Express / Midcontinent Express / Gulf Crossing',
   ('crossborder', 'US-Canada lines entering North Dakota, Minnesota, Michigan (Alliance, Viking, Great Lakes, Vector, Northern Border), and their expansions - the US segment is in scope.'),
   ('intrastate', 'State-regulated transmission: Oklahoma Corporation Commission, Kansas KCC, Iowa Utilities Commission permits, Minnesota PUC route permits, North Dakota PSC siting, Michigan PSC Act 9 certificates, Illinois Commerce Commission. FERC silence is not an existence concern for intrastate lines.')),
 'west-ne-ak': ('the West (California, Nevada, Utah, Arizona, Colorado, Wyoming, Montana, Idaho, Oregon, Washington), Alaska, and the Northeast (New York, New Jersey, Connecticut, Massachusetts, Rhode Island, New Hampshire, Vermont, Maine)',
   'Arizona/Nevada supply (Transwestern, El Paso Northern Arizona expansions, Kern River, Southwest Gas Greenlink-era laterals), Rockies (Wyoming Interstate, Colorado Interstate, TransColorado), Pacific Northwest (GTN Xpress, Northwest Pipeline), Alaska (Alaska LNG / Alaska Gasline Development Corp, Cook Inlet and North Slope lines), Northeast (Constitution, NESE, Iroquois, Algonquin, Maritimes, Tennessee 300-line work)',
   ('crossborder', 'US-Mexico export lines starting in Arizona or California (Sierrita, North Baja, Costa Azul feed) and US-Canada lines in the Northwest and Northeast (GTN, Iroquois, Maritimes & Northeast, PNGTS, Champlain/Vermont) - the US segment is in scope.'),
   ('intrastate', 'Alaska state lines (Alaska DNR State Pipeline Coordinator, AGDC), California CPUC and utility transmission (SoCalGas, PG&E backbone lines of 25 km or more), Wyoming and Colorado state siting. FERC silence is not an existence concern for intrastate lines.')),
}
SCOPE = ("Natural gas pipelines adding >= 25 km (15.5 mi) of NEW pipe: interstate and intrastate transmission trunks, "
         "laterals, and the loops/new pipe of an expansion project. Skip field gathering systems, processing-plant "
         "spurs inside a field, and local distribution networks. Compression-only expansions (no new pipe) and lines "
         "under 25 km go to the monitor list, not new rows. If you cannot establish a length, still emit it and say "
         "'length unknown'. Crude, NGL and refined-product lines are OUT OF SCOPE this cycle - drop them.")
VET = ("(d) LENGTH RULE (Baird 2026-10-02, US gas discovery): a qualifying new_row must add >= 25 km (15.5 mi) of new pipe "
       "with a SOURCED length. Under 25 km, compression-only (no new pipe), or uncertain/unsourced length -> class monitor, "
       "monitor_reason 'length'. (e) EXPANSION ROWS: GEM tracks US expansion projects as their own rows, with PipelineName "
       "= the parent system's GEM PipelineName exactly as the roster spells it and SegmentName = the project (e.g. P2544 "
       "'Transcontinental Gas Pipeline' / 'Hillabee Expansion Project, Phase 2'). An expansion that adds >= 25 km of new "
       "pipe and has no row of its own is a new_row in that shape, not a match to the parent system's row. A project that "
       "IS an existing row under another name is matched_existing. (f) EIA (sources/eia_pipeline_projects/NOTES.md): cite "
       "the DATED release that states the value as https://www.eia.gov/naturalgas/pipelines/<file> (never the undated "
       "EIA-NaturalGasPipelineProjects.xlsx; its twin is ...ProjectsAug2026.xlsx), sheet + Excel row in the note, "
       "url_verifier with --name set to the EIA project name. Local copies are in sources/eia_pipeline_projects/raw/. "
       "Every release is ONE origin: pair EIA with a FERC order/filing, a Federal Register notice, a state regulator "
       "document or an operator release when cheap. EIA 'Cost (millions)' -> stage the full number (450 -> 450000000, "
       "USD). EIA miles -> LengthKnown in mi, never converted. EIA 'Additional Capacity' is INCREMENTAL MMcf/d for an "
       "expansion. Status: Announced/Pre-filing/Applied/Approved -> proposed, Construction -> construction, Completed -> "
       "operating, On Hold -> shelved, Cancelled/Denied -> cancelled. (g) Country = United States; Puerto Rico is its own "
       "GEM area and out of scope. Intrastate lines never appear in FERC: FERC silence is not an existence concern; check "
       "the state regulator (Texas RRC T-4 etc.). (h) Owner names in the ownership team's style: run scripts/entity_lookup.py "
       "and scripts/entity_style.py, adopt the team's spelling on an exact/alias hit only.")
SEED_INTRO = ("Each seed below is a project from EIA's Natural Gas Pipeline Projects workbook (releases May 2018 to Aug 2026; "
  "the historical sheet reaches back to 1996) that scripts/eia_crosswalk.py matched to NO GEM row. EIA is a citable "
  "US government source, but a single origin. Being unmatched by the crosswalk is NOT proof the line is missing: the "
  "crosswalk matches on name + operator + state, so for older projects the most likely outcome is an existing roster "
  "row under another name (a renamed project, a phase of a row, the parent system's row when the project built no "
  "separate segment). Match-to-existing first. But GEM tracks expansion projects as their own rows (PipelineName = "
  "parent system, SegmentName = project, e.g. P2544 Transcontinental Gas Pipeline / Hillabee Expansion Project, "
  "Phase 2), so an expansion that added >= 25 km of new pipe and has no row of its own is a candidate, not a match "
  "to the parent system row. The seed's length is EIA's miles of new pipe.")
SEED_SEARCH = ("EIA's own row first - the local workbooks in sources/eia_pipeline_projects/raw/ and "
  "sources/eia_pipeline_projects/data/eia_projects_latest.csv (cite the dated release URL "
  "https://www.eia.gov/naturalgas/pipelines/<file>); then the FERC docket in the seed hint (FERC orders, Federal "
  "Register notices), the operator's project page, 10-K or press release, and for intrastate lines the state "
  "regulator. A sourced length >= 25 km is 15.5 mi")
def strategies(scope, leads, extra):
    base = [
     ('news', f'Industry and business news for {scope}: natural gas pipeline announcements, open seasons, binding precedent agreements, FIDs, in-service announcements. Thematic leads: {leads}. Cover the last ~5 years closely, then sweep older coverage (Pipeline & Gas Journal, OGJ, NGI, RBN, S&P Global, Reuters) for built lines.'),
     ('regulators', f'FERC paper trail for {scope}: certificate dockets (CP), Federal Register notices of applications and orders, FERC approved-major-projects lists, environmental assessments/EIS documents; plus PHMSA. Look for certificated pipelines of >= 25 km with no roster row, all years.'),
     ('operators', f'Operator project pages, 10-K / annual reports and investor decks for the midstream companies active in {scope} (interstate pipeline companies, intrastate operators, LNG developers, utilities): every gas pipeline project, current and past, of >= 25 km.'),
     ('maps', f'The MISSING-pipeline stance for {scope}: OPERATING interstate and intrastate gas transmission SYSTEMS that GEM never captured, any build year - the EIA list of interstate and intrastate natural gas pipeline companies and the EIA US Energy Atlas natural gas pipeline layer, PHMSA annual-report operator lists (data/PHMSA_pipeline_operators_opids_20260508.csv is local), company system maps. A named system with no roster match is exactly what this strategy exists to find. Report each as one candidate per system or distinct segment.'),
    ]
    return [{'key': k, 'brief': b} for k, b in base + list(extra)]
def build(key):
    scope, leads, *extra = SLICES[key]
    slug = f'discovery-{key}-{DATE}'
    stg = f'{ST}/{slug}'
    os.makedirs(stg, exist_ok=True)
    out = subprocess.run([sys.executable, 'scripts/build_discovery_context.py', '--tracker', 'gas', '--country', 'United States',
                          '--staging', stg, '--out', f'{stg}/args.json'], capture_output=True, text=True, check=True)
    a = json.load(open(f'{stg}/args.json'))
    seeds = [{k: v for k, v in s.items() if k != 'region'} for s in SEEDS if s['region'] == key]
    a.update(staging=stg, scopeRule=SCOPE, vetRule=VET, strategies=strategies(scope, leads, extra), seeds=seeds,
             seedIntro=SEED_INTRO, seedSearch=SEED_SEARCH, seedChunk=8,
             modelSearch='sonnet', modelVet='sonnet', modelConsolidate='opus')
    a['extra'] = '\n'.join([
        f'## This run: United States gas discovery, region {key} = {scope}',
        'Search ONLY this region. A multi-state line is in this slice when it STARTS here; a line that only passes through '
        'or ends here: report it with "out_of_slice": true in why_maybe_new. The roster below is the FULL national roster - match against all of it.',
        'Window (Baird 2026-10-02): ALL HISTORY - operating lines GEM never captured, whatever their build year, PLUS cancelled, '
        'shelved and in-development projects.',
        'Length rule: >= 25 km (15.5 mi) of new pipe; uncertain length -> say so.',
        'Unmatched EIA projects of 25 km or more for this region are already handed to dedicated seed agents; EIA projects under '
        'the floor are listed in batches/united-states-gas/staging/discovery-seeds-20261002/below_floor.csv - do not report those.',
        'Crude, NGL and refined-product lines are out of scope this cycle. Puerto Rico is its own GEM area and out of scope.',
    ])
    json.dump(a, open(f'{stg}/args.json', 'w'), ensure_ascii=False)
    print(key, len(seeds), 'seeds', len(a['roster']), 'roster', len(a['strategies']), 'strategies', len(json.dumps(a, ensure_ascii=False)), 'bytes')
if __name__ == '__main__':
    for k in (sys.argv[1:] or SLICES):
        build(k)
