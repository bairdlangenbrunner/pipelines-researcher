export const meta = {
  name: 'critical-deep-sweep',
  description: 'Critical re-audit of an in-scope pipeline set: confirm each data point against independent sources and flag phantom / duplicate / misclassified / mis-attributed entries (existence+classification first). One skeptical subagent per pipeline; read-and-stage only, never auto-applies.',
  phases: [
    { title: 'Audit', detail: 'one subagent per pipeline — existence+classification, then attribution+spec' },
  ],
}

// args (from `python scripts/build_deepsweep_args.py --staging <dir>`):
//   { repo, staging, commodity, country, pids:[...], roster:[...], status_review?: true }
// status_review: true = annual-update mode — each subagent ALSO stages a per-segment-row
// status verdict (confirm / change / stale / unclear) as `status_reviews` in its shard.
// tolerate a JSON-encoded string (some invocation paths stringify `args`)
const A = {"repo": "/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher", "staging": "batches/united-states-gas/staging/deepsweep-appalachian-operating", "commodity": "gas", "country": "United States", "pids": ["P0145", "P0149", "P0150", "P0153", "P0154", "P0156", "P0169", "P0172", "P0176", "P0182", "P0205", "P0209", "P0216", "P0221", "P0225", "P0279", "P0288", "P0291", "P0297", "P0307", "P0310", "P0312", "P0313", "P0325", "P0370", "P0375", "P0377", "P0387", "P0392", "P2003", "P2040", "P2438", "P2502", "P2505", "P2516", "P2531", "P2551", "P2604", "P2630", "P2635", "P3202", "P3220", "P5829", "P5830", "P5831", "P6003"], "roster": ["P0145 | Access South Gas Pipeline | Uniontown->Mississippi | len=1287.0 dia=? cap=320.00 | status=operating | updated=2023-08-21", "P0149 | Algonquin Gas Transmission Pipeline | Lambertville->Massachusetts | len=1131.0 dia=? cap=3120.00 | status=operating | updated=2023-08-21", "P0150 | Algonquin Gas Transmission Pipeline | Rockland County->New York | len=37.0 dia=42 cap=342.00 | status=operating | updated=2023-08-21", "P0153 | Appalachian Connector Pipeline | ?->Chatham | len=52.0 dia=? cap=2000.00 | status=operating | updated=2022-10-14", "P0154 | Atlantic Bridge Gas Project | ?->Maine | len=? dia=? cap=40.00 | status=operating | updated=2023-08-16", "P0156 | Atlantic Sunrise Gas Pipeline | ?->Susquehanna County | len=197.5 dia=? cap=1700.00 | status=operating | updated=2023-08-22", "P0169 | Columbia Gas Transmission | Midwest->New York | len=19312.0 dia=? cap=3000.00 | status=operating | updated=2022-10-06", "P0172 | Crossroads Gas Pipeline | Schererville->Ohio | len=202.0 dia=? cap=300.00 | status=operating | updated=2023-08-23", "P0176 | Dominion Gas Pipeline | Dominion LNG in Maryland, gas from Ohio and Virginia->New United Kingdom | len=6059.0 dia=? cap=7200.00 | status=operating | updated=2023-08-11", "P0182 | Eastern Shore Gas Pipeline | ?->Delaware | len=732.0 dia=? cap=100.00 | status=operating | updated=2023-08-23", "P0205 | Iroquois Gas Pipeline | Waddington->New York | len=669.0 dia=? cap=500.00 | status=operating | updated=2022-10-11", "P0209 | Leach XPress Gas Pipeline | ?->Ohio | len=160.0 dia=30, 36 cap=1530.00 | status=operating | updated=2023-08-25", "P0216 | Millennium Gas Pipeline | Lake Erie->New York | len=182.0 dia=14, 24, 30 cap=500.00 | status=operating | updated=2023-08-25", "P0221 | Mountaineer XPress Gas Pipeline | ?->West Virginia | len=171.0 dia=29, 36 cap=2700.00 | status=operating | updated=2023-08-10", "P0225 | NEXUS Gas Transmission (NGT) Pipeline | Kensington->Michigan | len=255.0 dia=36.00 cap=1500.00 | status=operating | updated=2023-08-28", "P0279 | WB Xpress Gas Pipeline | ?->West Virginia | len=29.0 dia=? cap=1300.00 | status=operating | updated=2023-08-31", "P0288 | Empire Pipeline | Chippawa->Pennsylvania | len=269.0 dia=? cap=300.00 | status=operating | updated=2023-09-14", "P0291 | Sunbury Pipeline | Lycoming->Pennsylvania | len=35.0 dia=20 cap=200.00 | status=operating | updated=2023-09-01", "P0297 | Central Corridor Pipeline | ?->Ohio | len=12.0 dia=20 cap=1.03 | status=operating | updated=2023-08-04", "P0307 | Mountaineer Gas Pipeline | Berkley->West Virginia | len=44.3 dia=? cap=? | status=operating | updated=2022-10-06", "P0310 | DeRuyter Pipeline | Norwich->New York | len=40.2 dia=? cap=1.45 | status=operating | updated=2023-08-09", "P0312 | Risberg Line Pipeline | ?->Ohio | len=28.0 dia=12.00 cap=55.00 | status=operating | updated=2023-09-01", "P0313 | Marquette Connector Pipeline | Arnold->Michigan | len=42.0 dia=10, 20 cap=144.00 | status=operating | updated=2023-09-01", "P0325 | Buckeye Xpress Pipeline | ?->West Virginia | len=64.0 dia=20, 24, 36 cap=275.00 | status=operating | updated=2023-09-01", "P0370 | Birdsboro Pipeline | Oley->Pennsylvania | len=13.2 dia=12.00 cap=79.00 | status=operating | updated=2023-09-03", "P0375 | Saginaw Trail Pipeline | ?->Michigan | len=94.0 dia=24 cap=200.00 | status=operating | updated=2023-09-03", "P0377 | Revolution Pipeline | ?->Pennsylvania | len=120.0 dia=24, 30 cap=440.00 | status=operating | updated=2023-09-03", "P0387 | Gulf Xpress Pipeline | ?->Mississippi | len=0.0 dia=? cap=875.00 | status=operating | updated=2023-09-04", "P0392 | Rover Pipeline | ?->Michigan | len=711.0 dia=42 cap=1700.00 | status=operating | updated=2023-08-05", "P2003 | Eastern Shore Gas Pipeline | ?->Maryland, Delaware | len=40.0 dia=10, 16, 24 cap=61.00 | status=operating | updated=2023-08-23", "P2040 | Mountaineer Gas Pipeline | Charlestown->West Virginia | len=39.4 dia=? cap=? | status=operating | updated=2022-10-06", "P2438 | Rover Pipeline | ?->Michigan | len=0.0 dia=? cap=1550.00 | status=operating | updated=2023-08-05", "P2502 | Appalachian Gateway Pipeline | ?->Pennsylvania | len=110.0 dia=20, 24, 36 cap=484.26 | status=operating | updated=2023-09-05", "P2505 | Vector Gas Pipeline | ?->Michigan | len=1.25 dia=24.00 cap=180.00 | status=operating | updated=2023-08-03", "P2516 | Columbia Gas Transmission | ?->Virginia | len=0.0 dia=? cap=45.00 | status=operating | updated=2022-10-06", "P2531 | Empire Pipeline | ?->Ontario | len=40.2 dia=26.00 cap=300.00 | status=operating | updated=2023-09-14", "P2551 | Leidy South Pipeline | ?->Delaware | len=12.2 dia=36, 42 cap=580.00 | status=operating | updated=2023-08-11", "P2604 | Rover Pipeline | ?->Michigan | len=0.0 dia=? cap=175.00 | status=operating | updated=2023-08-05", "P2630 | Dominion Gas Pipeline | ?->Ohio | len=5.1 dia=36.00 cap=150.00 | status=operating | updated=2023-08-11", "P2635 | Rover Pipeline | ?->West Virginia | len=0.0 dia=? cap=300.00 | status=operating | updated=2023-08-05", "P3202 | Vector Gas Pipeline | ?->Wisconsin | len=0.0 dia=? cap=380.00 | status=operating | updated=2023-08-03", "P3220 | Eastern Gas Transmission and Storage System (EGTS) | ?->Virginia | len=6437.38 dia=? cap=9500.00 | status=operating | updated=2022-10-07", "P5829 | Rockies Express Gas Pipeline | ?->Ohio | len=14.0 dia=24 cap=600.00 | status=operating | updated=2023-08-30", "P5830 | Rockies Express Gas Pipeline | ?->Illinois | len=? dia=? cap=1800.00 | status=operating | updated=2023-08-30", "P5831 | Rockies Express Gas Pipeline | ?->Missouri | len=? dia=? cap=800.00 | status=operating | updated=2023-08-30", "P6003 | Eastern Shore Gas Pipeline | ?->Maryland | len=20.0 dia=8,10,16 cap=14.00 | status=operating | updated=2023-09-13"], "extra_brief": "SCOPE: US APPALACHIAN BASIN + MID-ATLANTIC (Ohio / Pennsylvania / West Virginia / New York /\nMichigan / New Jersey / Maryland / Delaware / Virginia / Indiana, plus two rows whose route\ncrosses into Ontario). OPERATING gas pipelines, LastUpdated <= 2023. 46 rows = batch 3 of the\nUS stale-operating cohort (batch 1 Texas, batch 2 Gulf Coast). The slice was cut by the\nDERIVED state from the 2026-09-04 route-geometry audit, not by the sheet's StartState/Province\ncolumn, which is blank or wrong on a meaningful share of the cohort.\n\nCALIBRATION \u2014 a blank means NOBODY LOOKED, not that nothing exists.\nThis cohort's citation base is **11 filled `[ref]` cells against 663 owed (1.7%)** \u2014 thinner\nthan the Gulf Coast batch's 3.5%. Read it the way India and Ukraine were read, NOT the way\nPakistan was: `UNRESOLVED` here is UNFINISHED, not the correct outcome. Nearly every line in\nthis batch is a FERC-certificated interstate pipeline with a public docket, an EIA entry and\nyears of trade coverage. If you cannot source an operating Appalachian line's diameter,\ncapacity or in-service year, you have not reached the right register yet.\n\nTHE SOURCE LADDER (use it in this order):\n1. **FERC** \u2014 `elibrary.ferc.gov` and the CP-numbered certificate docket. Almost all of this\n   batch is interstate and FERC-jurisdictional: Rover (CP15-93), NEXUS (CP16-22), Leach XPress\n   and Mountaineer XPress (Columbia/TC Energy), Rockies Express, Atlantic Sunrise (Transco),\n   Leidy South, Access South, Millennium, Algonquin/AIM, Empire, Iroquois, Vector, Eastern Gas\n   Transmission & Storage (EGTS, ex-Dominion Transmission), Columbia Gas Transmission,\n   Appalachian Gateway, WB Xpress, Gulf Xpress, Buckeye Xpress, Central Corridor, Sunbury.\n   A FERC ORDER states mileage by county, diameter, horsepower, added capacity, the cost\n   estimate and the in-service date explicitly. The Commission's FINDINGS are one origin\n   distinct from the applicant's own filing in the same docket.\n2. **STATE regulators for intrastate lines and for siting** \u2014 FERC silence is not an existence\n   concern for an intrastate line. Ohio Power Siting Board (`opsb.ohio.gov`) for Ohio gas\n   transmission siting; PA PUC (`puc.pa.gov`) + PA DEP chapter 105/102 permits for\n   Pennsylvania (Revolution, Birdsboro, Sunbury are PA-jurisdictional in whole or part);\n   WV PSC (`psc.state.wv.us`) for Mountaineer Gas Company's Phase I/II (an intrastate LDC\n   project, NOT a FERC project); NY DPS (`documents.dps.ny.gov/public/`, the DMM docket\n   system) for Article VII certificates; Michigan PSC (`michigan.gov/mpsc`); NJ BPU\n   (`nj.gov/bpu`); Virginia SCC (`scc.virginia.gov`).\n3. **PHMSA / NPMS** \u2014 `npms.phmsa.dot.gov` for route and operator identity; PHMSA annual\n   report mileage by operator ID.\n4. **EIA** \u2014 the Natural Gas Pipeline Projects workbook and state/infrastructure pages;\n   independent of the operator and good for in-service dates and added capacity.\n5. **Operator disclosures** \u2014 SEC 10-K/S-1, investor decks, tariffs and system maps.\n   TC Energy/Columbia (Columbia Gas Transmission, Leach XPress, Mountaineer XPress, WB Xpress,\n   Gulf Xpress, Buckeye Xpress, Central Corridor); Energy Transfer (Rover); Enbridge (Algonquin,\n   Texas Eastern, Vector, NEXUS co-owner); DT Midstream (NEXUS co-owner, Millennium);\n   Williams (Atlantic Sunrise, Leidy South); Tallgrass (Rockies Express); National Fuel Gas\n   (Empire); Berkshire/Eastern Gas Transmission & Storage (EGTS, ex-Dominion); Chesapeake\n   Utilities (Eastern Shore); Mountaineer Gas Company (WV LDC); Iroquois Gas Transmission.\n   One operator is ONE origin across all of its pages and microsites.\n6. Trade press (Natural Gas Intelligence, S&P Global, Reuters, Pipeline & Gas Journal,\n   Marcellus Drilling News, Kallanish). Local Ohio/PA/WV newspapers are useful for\n   construction milestones and are independent of the operator.\n\nINDEPENDENCE, precisely. FERC's ORDER vs the applicant's own filing IN that docket are ONE\norigin \u2014 the docket contains the company's numbers. FERC's order vs the company's website IS\ntwo. A state PUC's order vs FERC's order IS two. `roverpipelinefacts.com` is Energy Transfer's\nown microsite and is ONE origin with Energy Transfer; `esng.com` is ONE origin with Chesapeake\nUtilities. The same wire story republished is one. Anything citing GEM is disqualified.\n\nTHE NAME-COLLISION AND PHASE CLUSTERS \u2014 this batch is a duplicate/granularity minefield and\nthat is deliberate. Get these right before touching anything else:\n- **Rover, 4 rows.** P0392 Phase 1 (711 mi, 42 in, 1700 MMcf/d), P2438 Phase 2 (len 0,\n  1550 MMcf/d), P2604 Rover Expansion (len 0, 175), P2635 Wick Meter Station Expansion (len 0,\n  300, WV->WV). Phases 1 and 2 are ADDITIVE halves of one ~3.25 Bcf/d system \u2014 Rover's system\n  total is NEVER a ref for a phase row, and finding \"3.25 Bcf/d\" does not make either phase\n  wrong. The three len-0 rows are compression/meter-station scopes: `LengthKnown = 0` and blank\n  `Diameter` is CORRECT for them (expansion with no new physical pipe), so do not \"fix\" it.\n  P2635 is a meter station in West Virginia while the mainline runs Ohio->Michigan; that is a\n  real difference of scope, not a state error.\n- **Rockies Express, 3 rows.** P5829 Seneca Lateral (14 mi, 24 in), P5830 Zone 3 East-to-West\n  (blank length, 1800), P5831 Zone 3 Capacity Enhancement (blank length, 800). Zone 3\n  East-to-West is a FLOW REVERSAL on existing pipe \u2014 if the FERC order confirms no new mainline\n  pipe, the owed length is `0`, not a number scraped off the system. Both blanks are owed.\n- **Eastern Shore, 3 rows.** P0182 (732 mi, 100 MMcf/d, 1959), P2003 2017 Expansion (40 mi),\n  P6003 Del-Mar Energy Pathway (20 mi). **P0182's 732 mi is the number to test hardest** \u2014\n  Eastern Shore Natural Gas is commonly described as a system of a few hundred miles, so either\n  732 is wrong or it counts something the description does not. Name the document either way.\n- **Mountaineer \u2014 a NAME COLLISION, not a duplicate.** P0221 Mountaineer XPress (171 mi,\n  2700 MMcf/d) is TC Energy/Columbia Gas Transmission's FERC project. P0307 Phase I and P2040\n  Phase II \"Mountaineer Gas Pipeline\" belong to **Mountaineer Gas Company**, a West Virginia\n  LDC, and are state-regulated (WV PSC), not FERC. Different companies, different projects.\n  Do not merge them and do not cite one for the other.\n- **Empire, 2 rows.** P0288 Main Line (269 mi, Ontario->Pennsylvania, 300 MMcf/d) and P2531\n  North Expansion (40.2 mi, Pennsylvania->Ontario, 300 MMcf/d). The identical 300 and the\n  reversed endpoints are both suspicious: check whether the expansion's capacity is the SYSTEM\n  figure restated on a segment row (that is a `spec` concern) and which direction each actually\n  flows after the North Expansion.\n- **Vector, 2 rows.** P2505 Blue Water Energy Center lateral (1.25 mi, 24 in) and P3202 Blue\n  Water Compressor (len 0, recorded Michigan->Wisconsin). Verify P3202's endpoints \u2014 a\n  compressor project ending in Wisconsin on a Michigan lateral needs an explanation or is an\n  attribution concern.\n- **Algonquin, 2 rows.** P0149 Main Line (1131 mi) and P0150 Algonquin Incremental Market /\n  AIM (37 mi, 42 in). AIM's numbers are not the main line's.\n- **Columbia Gas Transmission, 2 rows.** P0169 carries SegmentName `SYSTEM/NETWORK INFO`,\n  19,312 mi and a blank start state \u2014 it is a NETWORK row, not a segment, so a system figure IS\n  the right kind of ref for it and a segment figure is not. P2516 Central Virginia Connector\n  (len 0) is a discrete project.\n- **Dominion / EGTS, 2 rows.** P0176 (6,059 mi) and P2630 West Loop Expansion (5.1 mi). See the\n  next paragraph about P0176's end state.\n\nSTATE COLUMNS ARE PART OF THIS BATCH.\n- **P0176 carries `New United Kingdom` in `EndState/Province`. This is a find-and-replace scar\n  (\"New England\" -> \"New United Kingdom\") and it is NOT a mechanical fix.** The column holds\n  individual STATES everywhere else in the tracker, and `New England` appears ZERO times in\n  either tracker, so restoring it would introduce an unprecedented value. Research the row's\n  real terminus state and propose THAT, with a ref. Same treatment if you meet it elsewhere.\n- **P0169 and P0176 have a blank `StartState/Province`**; P2551 and P2531 and P0288 have an\n  end-state the route geometry disputes; P0156 (Atlantic Sunrise) and P2502 (Appalachian\n  Gateway) have a start-state the geometry disputes.\n- For YOUR row: if either state cell is blank or is not a US state / Canadian province, emit a\n  fills[] object with `ref_col: \"Location [ref]\"`, `value_cols: [\"StartState/Province\",\n  \"EndState/Province\"]`, the sourced state names as values, and a verified ref that places the\n  termini (a FERC order's county list, a state siting order, the operator's system map). If the\n  cell is filled but your sources disagree with it, file a validity `attribution` concern naming\n  the source and the state it supports \u2014 never silently pass it.\n\nRULES THAT BITE HERE:\n- **Never cite GEM.** No gem.wiki / globalenergymonitor.org in any `[ref]`. Visit the wiki page\n  for its OUTBOUND citations only.\n- **Wikipedia IS citable** as ONE secondary source; an article whose own footnote is GEM cannot\n  corroborate.\n- **abarrelfull is BANNED** (`abarrelfull.wikidot.com`, `.co.uk`) and so is theodora.com.\n- **Never fabricate a URL.** Every URL goes through `scripts/url_verifier.py --name`.\n- **A blocked fetch is not a deletion.** 403 / Cloudflare / timeout = access failure; only a\n  confirmed 404/410 may retire a ref. A blocked origin gets its Wayback snapshot ADDED\n  alongside, never swapped in.\n- **Cite the ARTICLE, never a navigation surface.** A site root, a search-results page, an\n  eLibrary query URL or a bare host is a MUTABLE surface and fails validation. Cite the\n  accession-numbered FERC document, not the search that found it.\n- **SegmentCost: half of batch 1's researched cost values did not survive primary sources.**\n  A cost is `REFS_ADDED` only when a primary source (FERC order estimate, 10-K capitalized cost,\n  dated financing) states THAT figure for THAT project scope. A total-project or system figure\n  restated on a segment row is a `spec` concern, not a ref.\n- **Expansion with no new physical pipe -> `LengthKnown = 0`, `Diameter` blank.** Several rows\n  here are already correct on this; confirm rather than \"fix\".\n- **Two orphan `[ref]` cells on blank values: P0149 and P0150 `Pressure [ref]`.** A ref with no\n  value is a defect \u2014 either source the pressure value to pair with it, or flag the ref.\n\nEXISTENCE / DUPLICATE FLAGS \u2014 the bar is high. Before you recommend a row be retired, folded or\ncalled a phantom:\n  (a) NAME THE DOCUMENT you tested and say what it does and does not contain. \"The report does\n      not mention it\" is only evidence if that report would necessarily list it.\n  (b) An intrastate line's absence from FERC is EXPECTED and is NOT an existence concern.\n      Check the state regulator first (this bites on Mountaineer Gas, Revolution, Birdsboro,\n      Sunbury, Risberg, DeRuyter, Marquette Connector, Saginaw Trail).\n  (c) Read MAPS, not just full text. A system map or tariff schematic often names a segment the\n      prose never does.\n  (d) Segment-vs-network granularity: GEM tracks segments and project phases. A source\n      describing the whole system is not evidence a phase is duplicated. An aggregate figure\n      restated on a phase row is a defect worth flagging, but the PHASE still exists.\n  (e) A line idled, converted or partially abandoned EXISTED and is a status finding, never an\n      existence concern.\nState your evidence so a reviewer can check it.\n\nMEASURED CONDITIONS (2026-09-08) \u2014 do not burn budget re-testing these:\n  - `elibrary.ferc.gov` returns 200 fast (~0.15 s). `www.ferc.gov` ROOT answers 403 to scripted\n    clients, but document paths under `www.ferc.gov/sites/default/files/...pdf` return 200 and\n    pass url_verifier.\n  - `dps.ny.gov` ROOT answers 403, but `documents.dps.ny.gov/public/` (the DMM docket system)\n    returns 200 \u2014 go straight there for New York.\n  - `dis.puc.pa.gov` does NOT resolve (NXDOMAIN). Use `www.puc.pa.gov` (200) and find the\n    docket path from there.\n  - 200 and usable: `opsb.ohio.gov` (~1.1 s), `psc.state.wv.us`, `michigan.gov/mpsc`,\n    `nj.gov/bpu`, `scc.virginia.gov`, `roverpipelinefacts.com`, `esng.com`.\n  - `www.eia.gov` returns 200 but takes ~10 s per fetch, and the pipeline-projects workbook is\n    an .xlsx \u2014 download with curl and read it, do not fetch it as a page. Batch your EIA reads.\n  - **The 18 distinct `bit.ly` links in this batch's harvested pool all redirect to\n    en.wikipedia.org.** They are ONE secondary source each, not 18 sources \u2014 resolve a shortener\n    before citing it, and cite the resolved target, never the `bit.ly` form.\n  - Existing refs on these rows: 6 units all-live, 5 with dead links, 4 live but the page never\n    names the pipeline (`name_found` false) \u2014 those 4 are attribution work, not re-verification.\n\nTHE HARVESTED CITATION POOL IS A WORKLIST, NOT A LOOKUP TABLE. 570 citations were harvested\nacross these 46 wiki pages. Do not stop at the first sufficient source and leave the rest of\nyour row's pool unopened. In `researcher_notes`, report HOW MANY of your row's harvested\ncitations you actually opened, and flag any you could not read and why.\n\nVALUE CONVENTIONS: `*CostUnits` is a BARE currency code (`USD`), never \"USD millions\".\nControlled vocab is lowercase except `FIDStatus` (`Pre-FID`/`FID`). Capacity is stated in the\nsheet's units \u2014 check the worklist unit's column header before writing a number. Never fill a\n`[ref]` without a paired value, or leave a researched value without a `[ref]`.\nNo recon legs run for US gas and you never propose route geometry; a route-vs-sheet\ndisagreement is a validity note, nothing more.\n", "model": "sonnet"}
if (!Array.isArray(A.pids) || !A.pids.length) {
  throw new Error("critical-deep-sweep needs args.pids — run scripts/build_deepsweep_args.py and pass its JSON as `args`.")
}
// Model is chosen by the orchestrator at dispatch time (standing rule: cheapest model
// genuinely good enough for this run) and passed via args.model; 'sonnet' is only the
// fallback when no choice is passed, not a pin.
const MODEL = A.model || 'sonnet'
const REPO = A.repo
const STAGING = A.staging
const COMMODITY = A.commodity || 'gas'
const COUNTRY = A.country || ''
const PIDS = A.pids
const ROSTER = (A.roster || []).join("\n")
const STATUS_REVIEW = !!A.status_review
// optional scope-specific guidance (e.g. China: research in Chinese, geo-blocked-site
// workarounds) appended verbatim to every subagent contract
const EXTRA = A.extra_brief ? `\n\n## Scope-specific guidance (from the orchestrator)\n${A.extra_brief}` : ''

const statusInstr = STATUS_REVIEW ? `

## STATUS REVIEW (annual-update mode — REQUIRED, one object per segment row)
This is an in-development row being checked for the annual update. Beyond the audit above,
determine the pipeline's CURRENT true status. Hunt for dated evidence NEWER than the sheet's
(the roster line shows updated=LastUpdated). A status change is a claim like any other:
>=2 independent sources, every URL through url_verifier. Verdict vocabulary:
- "confirm" — the recorded Status is still right; say what confirms it, with the evidence date.
- "change"  — evidence-based status change. Set proposed_status and proposed_changes as
  {column: value} pairs — Status (controlled vocab, lowercase) plus the matching date columns
  (e.g. now operating -> StartYear1; construction began -> ConstructionYear; newly shelved ->
  ShelvedYear). A change without a verified ref will be downgraded at merge — source it.
- "stale"   — NO independent news found. Apply the dormancy rules: proposed with no progress
  >=2y -> shelved; shelved >=4y -> cancelled. proposed_changes MUST include
  ShelvedCancelledType="inferred" (lowercase — that is the live column's vocabulary, NOT
  "Presumed") and the inference gets NO fabricated ref (standing rule 2);
  set staleness_rule to "2y->shelved" or "4y->cancelled". If dormant but under the threshold,
  use "confirm" and note the last-evidence date.
- "unclear" — genuinely cannot tell; explain what you tried in researcher_notes.
evidence_date = date of the MOST RECENT independent evidence found (YYYY-MM where possible).
Add to the shard: "status_reviews": [
  { "segment_name": "<or empty>", "sheet_row": <int from worklist>,
    "current_status": "<from the sheet>", "verdict": "confirm|change|stale|unclear",
    "proposed_status": "<or empty>", "proposed_changes": {"Status": "...", "...": "..."},
    "evidence_date": "YYYY-MM", "staleness_rule": "" ,
    "proposed_refs": ["https://...verified..."],
    "verifications": [{"url":"https://...","ok":true,"contains_value":true}],
    "tier": "high|medium|low", "independent": true, "source_language": "en",
    "researcher_notes": "<what you searched, the newest dated evidence, your reasoning>" }
]` : ''

const contract = (pid) => `You are a meticulous, skeptical GEM pipeline researcher. Critically RE-AUDIT one ${COUNTRY}
${COMMODITY} pipeline: ProjectID ${pid}. This is a deep-sweep validity pass — your job is to CONFIRM the
existing data and EXPOSE anything wrong, not to rubber-stamp it. Baird expects some of this data to
be wrong, some pipelines to not exist, and some to be duplicates or misclassified. Find those.

cd ${REPO} first.

## Inputs (read them — ALWAYS START FROM THE SOURCES THE SHEET ALREADY CITES)
- Your pipeline's current GEM values + existing refs: \`${STAGING}/worklist.json\` → load it and
  filter \`units\` to \`project_id == "${pid}"\`. Each unit has ref_col, value_cols, values,
  primary_value, current_ref, sheet_row, segment_name, pipeline_name, wiki.
- Source leads harvested from this row's gem.wiki page: \`${STAGING}/wiki_citations.json\`
  (your STARTING POINT — engage what the sheet itself cites BEFORE open-web search; verify each
  live, since many rot; READ gem.wiki for leads but NEVER cite it). A row whose only support is a
  generic/aggregate citation that does not actually name this pipeline is itself an existence flag.
- Roster of ALL ${PIDS.length} in-scope pipelines (for duplicate/relabel detection — does ${pid} look
  like the same physical pipe as another row under a different name?):
${ROSTER}

## Standing rules (NON-NEGOTIABLE)
1. NEVER cite gem.wiki / globalenergymonitor.org, theodora.com, or A Barrel Full /
   abarrelfull.wikidot.com / any wikidot.com page. Read for leads only. url_verifier rejects them.
2. NEVER fabricate a URL. If you cannot verify, say so in researcher_notes — no invented links.
3. Run EVERY url through the verifier before you cite it, WITH THE PIPELINE NAME:
   \`python scripts/url_verifier.py "<url>" "<expected substring>" ["<more>"] --name "<pipeline name>"\`
   (or \`verify_url(url, any_of=surface_forms(value), name=<pipeline_name>)\`) → cite only if it
   prints OK/200 AND contains the expected token(s) AND names the pipeline. Use distinctive tokens
   (numbers, place names). Every verification object you write carries "name_found": true|false.
   RELEVANCE: a page about terminus A, or about terminus B, or about the parent trunk, is NOT a ref
   for the "A-B" segment row unless it names that segment (its FULL name, or its local-language
   name from the worklist's OtherLanguage* columns). If the name is in another script and the
   verifier misses it, read the page and encode the hand-confirmed match as name_found=true with
   the matched string in "note". A ref whose page never names the pipeline is capped at low at
   merge and listed by the pre-delivery gates -- do not stage it as if it were support.
4. Corroborate with >=2 INDEPENDENT sources (separate origins; not one wire story reprinted, not two
   pages both tracing to GEM). tier: high = >=2 independent working+value-present; medium = 1 strong;
   low = 1 weak/partial/conflicting. TWO REFS PER DATA POINT IS THE TARGET FOR EVERY UNIT: after the
   first source lands, the second search is owed -- a different publisher and a different document
   class (regulator approval / operator disclosure / press / EIA or acceptance notice). A single-
   source unit is fillable at medium, but its researcher_notes must say what you searched for the
   second source and why none was found. Search in the country's languages too where English is thin.
5. Read every document you open TO EXHAUSTION, for every column and every sibling row. A source
   found for one cell is a source for every fact on its page: if the approval notice you found for
   Status also states length, diameter, investment, construction start and commissioning date, stage
   it onto Length / Diameter / SegmentCost / Construction / Start [ref] too (REFS_ADDED where the
   value is on the sheet, a fill where the cell is blank). Then check the roster: a page about the
   trunk names its branches, and a page about segment I states segment II's numbers -- write those
   into your researcher_notes naming the other PID, so the orchestrator can route them (findings do
   not propagate across a fan-out by themselves). Limit: a SYSTEM figure is never a ref for a
   SEGMENT cell (aggregate-vs-segment rule) -- note it and file a validity concern instead.

## What to do, IN THIS PRIORITY ORDER (existence + classification FIRST)
1. EXISTENCE — Is this pipeline real? Find independent evidence it physically exists/is being built.
   If the ONLY traces are GEM-derived, or the sheet's cited source does not actually name this
   pipeline, or you cannot find independent confirmation, flag verdict="concern",
   concern_type="existence" (possible hallucination / GEM-only entity).
2. CLASSIFICATION — Is it correctly classified as recorded (right commodity; a transmission trunk vs
   a gathering/process/feeder line)? Wrong → concern_type="classification".
3. DUPLICATE — Compare against the roster. If ${pid} is very likely the same physical pipe as another
   ProjectID (relabel / segment double-count), flag concern_type="duplicate" and NAME the other PID.
4. ATTRIBUTION — owner/operator, FuelSource, province, endpoints. Wrong → concern_type="attribution".
5. SPEC — length, diameter, capacity, dates. CRITICALLY confirm each against >=2 independent sources.
   It is NOT enough that a page mentions the pipeline — the source must AGREE with the GEM number.
   Material disagreement → concern_type="spec", verdict="concern" (never silently pass it).
6. FILLS ARE OWED, NOT OPPORTUNISTIC. Every worklist unit for ${pid} with class == "MISSING_VALUE"
   is a blank the sheet owes a value for (Length, Capacity, Diameter, StartYear, ConstructionYear,
   SegmentCost, Pressure, FuelSource, Operator, Owner …). For EACH ONE emit a fills[] object: a
   sourced value with a paired verified ref when you find one, otherwise class_out="UNRESOLVED" with
   researcher_notes saying what you searched. Never force a number (a weak Capacity stays blank rather
   than fabricated); never skip a blank silently. Blank cells on OPERATING rows come first -- they are
   what the researchers notice.${statusInstr}${EXTRA}

A pipeline that is real and correctly classified but has a lesser caveat → verdict="confirmed (caveat)".
Only open existence/duplicate/classification doubt → verdict="concern".

## Output — write a shard, then return a summary
Write \`${STAGING}/rows/${pid}.json\` = a single JSON object EXACTLY shaped like:
{
  "project_id": "${pid}",
  "pipeline_name": "<from worklist>",
  "sheet_row": <int from worklist>,
  "wiki": "<gem.wiki url from worklist>",
  "validity": [
    { "segment_name": "<or empty>", "verdict": "confirmed (caveat)|concern",
      "concern_type": "existence|duplicate|classification|attribution|spec|none",
      "recommendation": "<short human next step, e.g. 'reclassify as NGL' / 'merge into P####' / 'verify endpoint'>",
      "contested": {"<backend column the finding disputes>": "<candidate value, or \"\" if the evidence only says the current value is wrong>"},
      "researcher_notes": "<the full finding — what you checked, what the sheet's own sources say, what independent sources say vs GEM, your reasoning>",
      "proposed_refs": ["https://...verified..."], "tier": "high|medium|low",
      "independent": true, "source_language": "en" }
  ],
  "fills": [
    { "segment_name": "<or empty>", "sheet_row": <int>, "ref_col": "Capacity [ref]",
      "value_cols": ["Capacity"], "primary_value_col": "Capacity", "values": {"Capacity": "<val>"},
      "primary_value": "<val>", "proposed_refs": ["https://...verified..."],
      "verifications": [{"url":"https://...","ok":true,"contains_value":true,"name_found":true,
                          "note":"<the phrase on the page that states the value and names the line>"}],
      "class_out": "REFS_ADDED|UNRESOLVED", "tier": "high|medium|low", "independent": true,
      "source_language": "en", "researcher_notes": "<why this value / source; what you searched for a 2nd source>" }
  ],
  "cross_row_leads": [
    { "project_id": "<other PID from the roster>", "url": "https://...verified...",
      "facts": "<what the page states about THAT row, e.g. '825 km, 3.1 bn RMB, construction Oct 2008'>" }
  ],
  "summary": "<one line>"
}
Emit at least one validity object per pipeline (use verdict="confirmed (caveat)", concern_type="none"
if you found nothing wrong, summarizing what you confirmed). ON EVERY verdict="concern", fill
\`contested\` — it is the ONLY thing that puts your finding on the paste surface. A validity record
proposes no edit, so it is filtered off the _Backend mirror; \`contested\` is what tints the disputed
CURRENT value orange there with your finding attached. Omit it and a researcher pastes straight over
the cell you flagged. Name the EXACT backend column ("LengthKnownUnits", not "units"), give the
candidate value where your evidence names one, and "" where it only establishes the current value is
wrong. A concern about the row as a whole (existence/duplicate) may leave it {}.${STATUS_REVIEW ? ' In annual-update mode also emit\nat least one status_reviews object per segment row (shaped as specified above).' : ''} validity[].proposed_refs and all
fills[].proposed_refs must have passed url_verifier (with --name). One fills[] object per
MISSING_VALUE unit in your worklist slice (sourced or UNRESOLVED) -- an owed blank with no object
is a defect the pre-delivery gates list. Before finishing, run
\`python -c "import json; json.load(open('${STAGING}/rows/${pid}.json'))"\` to confirm it parses.
Return ONLY a 2-line summary: the verdict/concern_types you staged, and any UNRESOLVED. Your shard
file is the deliverable, not your message.`

phase('Audit')
log(`Critically auditing ${PIDS.length} ${COUNTRY} ${COMMODITY} pipelines (existence+classification first), one subagent each.`)
const results = await parallel(PIDS.map(pid => () =>
  agent(contract(pid), { label: `audit:${pid}`, phase: 'Audit', agentType: 'general-purpose', model: MODEL })
))
const done = results.filter(Boolean).length
log(`Audit complete: ${done}/${PIDS.length} subagents returned. Shards in ${STAGING}/rows/`)
return { audited: done, total: PIDS.length }
