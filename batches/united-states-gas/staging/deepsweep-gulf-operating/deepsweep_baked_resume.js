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
const A = {
  "repo": "/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher",
  "staging": "batches/united-states-gas/staging/deepsweep-gulf-operating",
  "commodity": "gas",
  "country": "United States",
  "pids": [
    "P0249",
    "P0251",
    "P0263",
    "P0269",
    "P0283",
    "P0294",
    "P2497",
    "P2500",
    "P2529",
    "P2544",
    "P2594",
    "P2606",
    "P2607",
    "P2627",
    "P2733",
    "P2738",
    "P3283",
    "P4028",
    "P4029",
    "P4030",
    "P4031",
    "P4032",
    "P4033",
    "P4034",
    "P4035",
    "P4036",
    "P4037",
    "P4038",
    "P4039",
    "P4040",
    "P4050",
    "P4060",
    "P5401",
    "P5709",
    "P5823",
    "P5849",
    "P6005"
  ],
  "roster": [
    "P0143 | Acadian Gas Pipeline System | Haynesville shale field->Louisiana | len=1000.0 dia=? cap=1000.00 | status=operating | updated=2023-08-18",
    "P0159 | Bridgeline Gas Pipeline | Larose->Louisiana | len=1585.0 dia=? cap=920.00 | status=operating | updated=2023-08-22",
    "P0164 | Southeast Supply Header | Perryville Hub->Alabama | len=462.0 dia=36, 42 cap=1140.00 | status=operating | updated=2023-08-23",
    "P0165 | Chandeleur Gas Pipeline | offshore Gulf of Mexico->Mississippi | len=346.0 dia=? cap=330.00 | status=operating | updated=2023-08-23",
    "P0175 | Destin Gas Pipeline | Gulf of Mexico->Mississippi | len=385.0 dia=24, 36 cap=1200.00 | status=operating | updated=2023-08-23",
    "P0187 | Midla Natchez Pipeline | Winnsboro->Mississippi | len=52.0 dia=12.00 cap=48.00 | status=operating | updated=2023-08-24",
    "P0192 | Garden Banks Gas Pipeline | Gulf of Mexico->Gulf of Mexico | len=84.0 dia=30.00 cap=1000.00 | status=operating | updated=2023-08-24",
    "P0199 | Gulfstream Natural Gas Pipeline | Mobile County->Florida | len=1199.0 dia=? cap=1310.00 | status=operating | updated=2022-10-11",
    "P0204 | Independence Trail Natural Gas Pipeline | West Delta Block 68->Gulf of Mexico | len=138.0 dia=24 cap=1000.00 | status=operating | updated=2023-08-25",
    "P0210 | Louisiana Intrastate Gas (LIG) Pipeline | Cotton Valley->Louisiana | len=2000.0 dia=? cap=700.00 | status=operating | updated=2023-08-25",
    "P0217 | Mississippi Canyon Gas Pipeline | Mississippi Canyon->Louisiana | len=44.5 dia=30.00 cap=800.00 | status=operating | updated=2023-08-26",
    "P0223 | Nautilus Gas Pipeline | Ship Shoal Block 207, Green Canyon Corridor->Louisiana | len=154.0 dia=30.00 cap=600.00 | status=operating | updated=2023-08-28",
    "P0244 | Regency Intrastate Gas (RIGS) Pipeline | Caddo Parish->Louisiana | len=200.0 dia=12, 16, 20, 24 cap=200.00 | status=operating | updated=2023-08-29",
    "P0249 | Sabal Trail Gas Transmission Pipeline | Alexander City->Florida | len=516.0 dia=24, 36 cap=830.00 | status=operating | updated=2023-08-11",
    "P0251 | Sea Robin Gas Pipeline | Gulf of Mexico->Louisiana | len=438.0 dia=? cap=1260.00 | status=operating | updated=2023-08-30",
    "P0263 | Texas Gas Transmission Pipeline | ?->Indiana, Illinois, Ohio | len=5975.0 dia=? cap=6100.00 | status=operating | updated=2023-08-10",
    "P0269 | TransCameron Pipeline | Grand Chenier->Louisiana | len=24.0 dia=42.00 cap=1900.00 | status=operating | updated=2023-07-26",
    "P0283 | Creole Trail Pipeline | Beauregard Parish->Louisiana | len=94.0 dia=? cap=1500.00 | status=operating | updated=2023-08-10",
    "P0294 | Magnolia Intrastate Pipeline | ?->Mississippi | len=118.0 dia=6 to 24 cap=122.00 | status=operating | updated=2023-09-01",
    "P2497 | Tennessee Gas Pipeline | ?->? | len=0.0 dia=? cap=894.00 | status=operating | updated=2023-08-03",
    "P2500 | AlaTenn Gas Pipeline | ?->Alabama | len=0.0 dia=? cap=39.00 | status=operating | updated=2023-08-24",
    "P2529 | Florida Gas Transmission Pipeline | ?->Louisiana | len=0.0 dia=24 cap=75.00 | status=operating | updated=2022-10-11",
    "P2544 | Transcontinental Gas Pipeline | ?->Alabama | len=17.7 dia=42.00 cap=206.00 | status=operating | updated=2022-10-14",
    "P2594 | Florida Gas Transmission Pipeline | ?->Florida | len=30.3 dia=30.00 cap=169.00 | status=operating | updated=2022-10-11",
    "P2606 | Sabal Trail Gas Transmission Pipeline | ?->Florida | len=0.0 dia=? cap=170.00 | status=operating | updated=2023-08-11",
    "P2607 | Transcontinental Gas Pipeline | ?->Louisiana | len=? dia=36.00 cap=400.00 | status=operating | updated=2022-10-14",
    "P2627 | Florida Gas Transmission Pipeline | ?->Alabama | len=8.9 dia=24 cap=343.00 | status=operating | updated=2022-10-11",
    "P2733 | Transcontinental Gas Pipeline | ?->Alabama | len=35.41 dia=? cap=818.00 | status=operating | updated=2022-10-14",
    "P2738 | Florida Gas Transmission Pipeline | ?->Alabama | len=0.0 dia=? cap=60.00 | status=operating | updated=2022-10-11",
    "P3283 | Acadian Gas Pipeline System | ?->Louisiana | len=83.0 dia=? cap=1000.00 | status=operating | updated=2023-07-07",
    "P4028 | Florida Gas Transmission Pipeline | ?->? | len=1.0 dia=8, 36 cap=69.00 | status=operating | updated=2022-10-11",
    "P4029 | Florida Gas Transmission Pipeline | ?->? | len=483.0 dia=24, 30, 36, 42 cap=820.00 | status=operating | updated=2022-10-11",
    "P4030 | Florida Gas Transmission Pipeline | ?->? | len=9.0 dia=20, 30 cap=50000.00 | status=operating | updated=2022-10-11",
    "P4031 | Florida Gas Transmission Pipeline | ?->? | len=7.0 dia=30 cap=10.00 | status=operating | updated=2022-10-11",
    "P4032 | Florida Gas Transmission Pipeline | ?->? | len=17.3 dia=36 cap=95.00 | status=operating | updated=2022-10-11",
    "P4033 | Florida Gas Transmission Pipeline | ?->? | len=0.3 dia=24 cap=100.00 | status=operating | updated=2022-10-11",
    "P4034 | Florida Gas Transmission Pipeline | ?->? | len=33.0 dia=36 cap=121.00 | status=operating | updated=2022-10-11",
    "P4035 | Florida Gas Transmission Pipeline | ?->? | len=136.0 dia=16, 24, 36 cap=130.00 | status=operating | updated=2022-10-11",
    "P4036 | Florida Gas Transmission Pipeline | ?->? | len=15.0 dia=24 cap=180.00 | status=operating | updated=2022-10-11",
    "P4037 | Florida Gas Transmission Pipeline | ?->? | len=64.0 dia=16, 24, 36 cap=298.00 | status=operating | updated=2022-10-11",
    "P4038 | Florida Gas Transmission Pipeline | ?->? | len=0.0 dia=30, 36 cap=80.00 | status=operating | updated=2022-10-11",
    "P4039 | Florida Gas Transmission Pipeline | ?->? | len=139.0 dia=30, 36 cap=200.00 | status=operating | updated=2022-10-11",
    "P4040 | Florida Gas Transmission Pipeline | ?->? | len=1.0 dia=12 cap=62.00 | status=operating | updated=2022-10-11",
    "P4050 | Florida Gas Transmission Pipeline | ?->? | len=0.4 dia=20 cap=36.00 | status=operating | updated=2022-10-11",
    "P4060 | Florida Gas Transmission Pipeline | ?->Alabama | len=0.0 dia=? cap=100.00 | status=operating | updated=2022-10-11",
    "P5401 | Acadian Gas Pipeline System | ?->? | len=0.0 dia=? cap=400.00 | status=operating | updated=2023-07-07",
    "P5709 | Acadian Gas Pipeline System | ?->Louisiana | len=270.0 dia=30, 36, 42 cap=1800.00 | status=operating | updated=2023-08-18",
    "P5823 | Regency Intrastate Gas (RIGS) Pipeline | ?->Louisiana | len=120.0 dia=30, 42 cap=600.00 | status=operating | updated=2023-08-29",
    "P5849 | Tiger Gas Pipeline | ?->Louisiana | len=21.0 dia=42 cap=400.00 | status=operating | updated=2023-08-30",
    "P6005 | Kinetica Energy Express | Plaquemines->Louisiana | len=1139.0 dia=36 cap=? | status=operating | updated=2023-09-13"
  ],
  "model": "sonnet",
  "extra_brief": "SCOPE: US GULF COAST (Louisiana / Mississippi / Alabama / Florida / offshore Gulf of Mexico)\nOPERATING gas pipelines, LastUpdated <= 2023. 50 rows = batch 2 of the US stale-operating\ncohort (batch 1 was Texas). The slice was cut by ROUTE GEOMETRY, not by the sheet's\nStartState/Province column, because that column is blank or not-a-state on 19 of these 50 rows.\n\nCALIBRATION \u2014 a blank means NOBODY LOOKED, not that nothing exists.\nThis cohort's citation base is 25 filled `[ref]` cells against 715 owed\n(3.5%), and the owner/operator tab carries ZERO refs for these 50 rows. Read that the way\nIndia/Ukraine were read, NOT the way Pakistan was: an `UNRESOLVED` here is UNFINISHED, not the\ncorrect outcome. Every one of these lines is FERC-, BOEM- or state-regulated and has a public\ndocket; if you cannot source an operating line's diameter or in-service year, you have not\nreached the right register yet.\n\nTHE GULF COAST SOURCE LADDER (use it in this order):\n1. **FERC** \u2014 `elibrary.ferc.gov` and the CP-numbered certificate dockets for INTERSTATE gas.\n   Most of this batch is interstate: Florida Gas Transmission, Transco, Tennessee Gas,\n   Southeast Supply Header, Gulfstream, Sabal Trail, Texas Gas Transmission, Destin, Midla,\n   Chandeleur, Sea Robin, Garden Banks, Nautilus, Mississippi Canyon, Independence Trail,\n   Tiger, Kinetica, Creole Trail, TransCameron, AlaTenn. A FERC ORDER states capacity,\n   diameter, mileage, compression, cost estimate and the in-service date explicitly, and\n   the Commission's own findings are ONE origin distinct from the applicant's website.\n   `ferc.gov/industries-data/natural-gas` for project pages; FERC Form 2 for operator data.\n2. **BOEM / BSEE** \u2014 `data.boem.gov` (Pipeline Permits / Pipeline Segments queries) for any\n   line on the Outer Continental Shelf: Garden Banks, Nautilus, Mississippi Canyon,\n   Independence Trail, Sea Robin, Chandeleur, Destin, Southeast Supply Header's offshore\n   leg. The BOEM segment record gives segment number, diameter, length, product, status\n   (ACT / ABN / OUT), approval and abandonment dates \u2014 a regulator register independent of\n   the operator. **A BOEM status of abandoned / out-of-service on the row's main segments is\n   a status finding: file it as a validity `spec` concern with the date, do NOT change the\n   Status value.** Gathering lines on the OCS are BOEM-, not FERC-jurisdictional, so FERC\n   silence on an offshore line is expected.\n3. **State regulators for INTRASTATE lines** \u2014 FERC silence is NOT an existence concern for:\n   Louisiana intrastate (Acadian, Bridgeline, Louisiana Intrastate Gas, Regency Intrastate\n   Gas / RIGS, Tiger's intrastate portion) -> Louisiana DNR Office of Conservation, SONRIS,\n   the LA Public Service Commission; Alabama intrastate (Magnolia Intrastate) -> Alabama\n   PSC; Mississippi -> Mississippi PSC. Florida Gas Transmission's in-state work also\n   surfaces in Florida PSC / Florida DEP dockets and the Florida Siting Board.\n4. **PHMSA / NPMS** \u2014 `npms.phmsa.dot.gov` for routes and operator identity; PHMSA annual\n   report mileage/diameter by operator ID.\n5. **EIA** \u2014 the Natural Gas Pipeline Projects table and `eia.gov` state / infrastructure\n   pages; independent of the operator, good for in-service dates and capacity.\n6. **Operator disclosures** \u2014 SEC 10-K / S-1, investor decks, tariffs and system maps\n   (Kinder Morgan for FGT + Southeast Supply Header + TGP + Sabal Trail; Energy Transfer for\n   FGT + Tiger + Gulf coast intrastates; Williams for Transco + Gulfstream; Boardwalk for\n   Texas Gas; Enbridge for Nautilus / Garden Banks / Mississippi Canyon / Sabal Trail /\n   Gulfstream; Enterprise for Acadian + Independence Trail; EnLink for Bridgeline; Genesis\n   Energy for Sea Robin; Cheniere for Creole Trail; Venture Global for TransCameron;\n   Kinetica Partners; Boardwalk / Midla). One operator is ONE origin across all its pages.\n7. Trade press (Pipeline & Gas Journal, Natural Gas Intelligence, S&P Global, Reuters,\n   Offshore Magazine's annual GoM map for subsea lines).\n\nINDEPENDENCE, precisely. FERC + the applicant's own filing IN that FERC docket are ONE\norigin \u2014 the docket contains the company's numbers. FERC's ORDER vs the company's website\nIS two. BOEM's segment record vs the operator's page IS two. The same wire story republished\nis one. Anything citing GEM is disqualified.\n\nTHE FLORIDA GAS TRANSMISSION CLUSTER \u2014 17 of the 50 rows are FGT rows, 14 of them expansion\nphases (Phase IV, V Stages 1-2 / 3 / 4, VI, VII Phase 1, VIII, East Leg, Western Division,\nJacksonville, Sanford, Putnam, Turkey Point Lateral, Alabama Power Lateral, AE Cooperative\nUpgrade, Mobile Bay Lateral, East Louisiana, South Alabama, Southwest Alabama). Each phase\nhas its own FERC certificate proceeding \u2014 find THAT docket and its order; the order gives\nthe miles of loop/lateral by county, the added compression, the added capacity and the\nin-service date. Rules that bite: an expansion with NO new physical pipe (compression only)\ngets `LengthKnown = 0` and blank `Diameter`; a phase whose numbers are only ever stated as\npart of a later phase's total is a duplicate/relabel candidate \u2014 check the roster and NAME\nthe sibling PID; a SYSTEM figure (FGT's 5,000+ miles, its total capacity) is never a ref\nfor a phase row. The same logic applies to the Acadian family (P0143 system / P3283 Gillis\nLateral / P5709 Haynesville Extension / P5401 its capacity expansion) and the Transco\nHillabee Phase 1 / Phase 2 pair.\n\nSTATE COLUMNS ARE PART OF THIS BATCH. The sheet's `StartState/Province` / `EndState/Province`\nare blank on 19 rows here (all 14 FGT expansion phases, P2497 TGP Acadiana Expansion, P5401\nAcadian Haynesville capacity expansion, P0251 Sea Robin's start) and not-a-state on others\n(P0192 Garden Banks and P0204 Independence Trail read `Gulf of Mexico`; P0223 Nautilus reads\n`offshore Louisiana`; P0263 Texas Gas reads `Louisana`). Route geometry also disagrees with\nthe sheet on P0294 Magnolia (sheet ends Mississippi, route ends Alabama), P0175 Destin\n(sheet starts Mississippi, route starts offshore Louisiana), P0199 Gulfstream (sheet starts\nAlabama, route starts Mississippi), P0159 Bridgeline and P0244 RIGS (sheet Louisiana, route\nfirst vertex Texas). For YOUR row: if either state cell is blank or not a US state /\nMexican or Canadian province, emit a fills[] object with `ref_col: \"Location [ref]\"`,\n`value_cols: [\"StartState/Province\", \"EndState/Province\"]`, the sourced state names as\nvalues, and a verified ref that places the termini (a FERC order's county list, a BOEM\nsegment record's landfall, the operator's system map). If the cell is filled but your\nsources disagree with it, file a validity `attribution` concern naming the source and the\nstate it supports \u2014 never silently pass it. The column holds individual STATES (or\nMexican/Canadian provinces); for offshore lines use the landfall state.\n\nRULES THAT BITE HERE:\n- **Never cite GEM.** No gem.wiki / globalenergymonitor.org in any `[ref]`. Visit the wiki\n  page for its OUTBOUND citations only.\n- **Wikipedia IS citable** as ONE secondary source: two language editions of one article\n  are ONE source, and an article whose own footnote is GEM cannot corroborate.\n- **abarrelfull is BANNED** (`abarrelfull.wikidot.com`, `.co.uk`) and so is theodora.com \u2014\n  never, not even alongside corroboration.\n- **Never fabricate a URL.** Every URL goes through `scripts/url_verifier.py --name`.\n- **A blocked fetch is not a deletion.** 403 / Cloudflare / timeout / geo-block = access\n  failure; only a confirmed 404/410 may retire a ref. A blocked origin gets its Wayback\n  snapshot ADDED alongside, never swapped in. FERC eLibrary and data.boem.gov are slow and\n  sometimes stall \u2014 retry, use `curl -sL` with a browser User-Agent, and cite the document's\n  own accession / stable URL, never the search page.\n- **Cite the ARTICLE, never a navigation surface.** A site root, a search-results page, an\n  eLibrary query URL, a paginated index, or a bare host is a MUTABLE surface and fails\n  validation.\n- **SegmentCost: half of batch 1's researched cost values did not survive primary sources.**\n  A cost is `REFS_ADDED` only when a primary source (FERC order estimate, 10-K capitalized\n  cost, dated financing) states THAT figure for THAT project scope. A total-project or\n  system figure restated on a segment row is a `spec` concern, not a ref. Never derive a\n  segment cost from a system total.\n\nEXISTENCE / DUPLICATE FLAGS \u2014 the bar is high. Before you recommend that a row be retired,\nfolded into another, or called a phantom:\n  (a) NAME THE DOCUMENT you tested and say what it does and does not contain. \"The report\n      does not mention it\" is only evidence if that report would necessarily list it.\n  (b) An intrastate line's absence from FERC, and an OCS gathering line's absence from FERC,\n      are EXPECTED and are NOT existence concerns. Check the state regulator / BOEM first.\n  (c) Read MAPS, not just full text. A system map or an operator schematic often names a\n      segment the prose never does.\n  (d) Segment-vs-network granularity: GEM tracks segments and project phases; a source\n      describing the whole system is not evidence a phase is duplicated. An aggregate\n      figure restated on a phase row is a defect worth flagging, but the PHASE still exists.\n  (e) Decommissioned is not non-existent. A GoM line abandoned after a hurricane or idled\n      by its operator EXISTED and is a status finding (see the BOEM rule above), never an\n      existence concern.\nState your evidence so a reviewer can check it.\n\nMEASURED CONDITIONS (2026-09-04) \u2014 do not burn budget re-testing these:\n  - www.ferc.gov ROOT answers 403 to scripted clients, but document paths under\n    `www.ferc.gov/sites/default/files/...pdf` return 200 and pass url_verifier. elibrary.ferc.gov\n    returns 200; cite the accession-number document URL, never the search page.\n  - www.eia.gov returns 200 but takes ~10 s per fetch \u2014 batch your EIA reads; the\n    `naturalgas/data.php#pipelines` navigation page cited on 22 of this batch's cells is a\n    navigation page, not a ref for any value: name the specific EIA table/workbook instead.\n  - data.boem.gov returns 200 (~6.5 s). Enbridge offshore factsheet PDFs (8+ MB) and\n    Kinetica's system map PDF return 200 \u2014 download with curl and read with pdftotext.\n  - sermessenger.energytransfer.com (Sea Robin / Trunkline informational postings) returns 200.\n  - `hienergyebb.azurewebsites.net` (old Gulf South/Hi-Energy EBB) does NOT resolve \u2014 NXDOMAIN\n    is a dead host, so a Wayback capture is the only route to anything hosted there.\n  - Existing refs on these rows: 12 units all-live, 13 with dead links, 9 live but the page\n    never names the pipeline (`name_found` false) \u2014 those 9 are attribution work, not\n    re-verification.\n\nTHE HARVESTED CITATION POOL IS A WORKLIST, NOT A LOOKUP TABLE. 542 citations were\nharvested across these 50 wiki pages. Do not stop at the first sufficient source and leave\nthe rest of your row's pool unopened. In `researcher_notes`, report HOW MANY of your row's\nharvested citations you actually opened, and flag any you could not read and why.\n\nVALUE CONVENTIONS: `*CostUnits` is a BARE currency code (`USD`), never \"USD millions\".\nControlled vocab is lowercase except `FIDStatus` (`Pre-FID`/`FID`). Capacity is stated in the\nsheet's units \u2014 check the worklist unit's column header before writing a number. An\nexpansion with no new physical pipe gets `LengthKnown = 0` and blank `Diameter`. Never fill\na `[ref]` without a paired value, or leave a researched value without a `[ref]`.\nNo recon legs run for US gas and you never propose route geometry; a route-vs-sheet\ndisagreement is a validity note, nothing more.\n"
}
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
if you found nothing wrong, summarizing what you confirmed).${STATUS_REVIEW ? ' In annual-update mode also emit\nat least one status_reviews object per segment row (shaped as specified above).' : ''} validity[].proposed_refs and all
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
