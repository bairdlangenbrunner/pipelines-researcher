SCOPE: US gas SLICE 2, batch A4 of 7 — TEXAS + MIDCONTINENT, OPERATING (plus the Midcontinent's
in-dev and cancelled rows). 41 rows: 27 operating, 1 construction (P0287 Gulf Coast Southbound Phase
III), 8 proposed, 5 cancelled. Two kinds of row live here and they need different work:
- **Big interstate SYSTEM rows** — P0152 ANR Main Line, P0262 TETCO Main Line, P0274 Trunkline Main
  Line, P2579 Northern Natural Main Line, P0197 Gulf South system, P0163 EOIT, P0277 Vector. System
  length / capacity / diameter belong HERE and nowhere else; they are the rows most likely to be cited
  to a stale system page. Source them from the operator's current 10-K system description, FERC Form
  2 or tariff, and a second origin (EIA's pipeline data, PHMSA annual report data, a state PSC).
- **Permian takeaway lines and their expansions** — Permian Highway (+ expansion), Gulf Coast Express,
  Whistler (mainline, Midland Lateral, capacity expansion), Matterhorn Express, Agua Blanca,
  Roadrunner Phases 1-2, the Targa Buffalo Run / Bull Run lines, Producers Midstream Residue Header —
  plus Midwest projects on ANR, NNG, Alliance, Southern Star, MoGas and Transco.
Baird chose 2026-09-10 to deep-sweep these rows with status review ON instead of a separate status
pass later, so this is the ONLY pass these rows get this cycle: do the status work and the data work
together.

CALIBRATION — __CALIBRATION__

EVERY WORKLIST UNIT IS OWED A RECORD — INCLUDING THE ALREADY-CITED ONES. This slice is unlike slice 1:
most values here already carry a `[ref]` (class `HAS_REF`). `check_shard_coverage.py` lists a HAS_REF
unit with no record exactly like a skipped blank. For each HAS_REF unit:
- Open the cited URL(s) (the worklist's `current_ref`, and `existing_ref_checks` where the builder
  already HTTP-checked them). Does it resolve, NAME this pipeline/segment, and STATE the value?
  - Yes -> `class_out: "REVERIFIED"`, `values` = the recorded value, `proposed_refs` = the existing
    ref(s) you re-verified PLUS the second independent source if you found one (the second source
    is still owed — rule 4d), `verifications` for each.
  - Resolves but does not state the value, or does not name the pipeline (a system page on a
    project row, a navigation page, a terminus page) -> the cell is effectively UNCITED: find the
    document that does state it and stage it as REFS_ADDED; if nothing states it, UNRESOLVED
    saying so. Keep the old ref in `researcher_notes`, never silently dropped.
  - Confirmed 404/410 -> `class_out: "DEAD_LINK"` with the Wayback capture if one exists, plus a
    replacement source. A 403/timeout/WAF is NOT dead — never retire a ref over an access failure.
  - The source DISAGREES with the recorded value -> stage the sourced value AND a `spec` concern.
- Where one document re-verifies several HAS_REF cells, say so once and stage it on each.

STATUS REVIEW IS ON FOR EVERY ROW (one status_reviews object per row).
- **Operating rows (27):** is each STILL operating, and is StartYear1 right? Look for abandonment
  (FERC `CP` abandonment orders), idling, sale/rename, or conversion. A clean "still operating"
  verdict needs a dated source newer than LastUpdated (a current tariff, a 10-K, an EIA/PHMSA
  listing) — say which. For system rows, StartYear1 is the system's first year of service.
- **Construction row P0287 Gulf Coast Southbound Phase III** (2026 target) — confirm construction is
  underway, or find the in-service date or delay.
- **Proposed rows (P2530 ANR Elwood, P2566 MoGas Expansion, P3187 ANR Wisconsin Access, P4380 ANR
  Skunk River Replacement, P7793 ANR Heartland, P7814 Transco Decatur Lateral, P7826 Southern Star
  Cedar Vale):** confirm with a dated source NEWER than LastUpdated, or find the change. **P2530
  (StartYear1 2022) and P3187 (2022) and P4380 (2024)** have in-service targets in the past: each is
  either built (-> operating + StartYear1), delayed, or withdrawn. FERC's eLibrary docket for each
  project will say which.
- **Cancelled rows (P0318 Arkoma Residue Capacity, P0371 Blue Mountain Delivery, P2564 Southern Star
  Midwest Market Access, P3184 Alliance Capacity Expansion):** is the cancellation RIGHT and SOURCED?
  Find the dated withdrawal (FERC order granting withdrawal / vacating, sponsor announcement): that is
  the `Cancelled [ref]`. Rows reading `inferred` (P0318, P0371, P3184) become `confirmed` on a dated,
  sourced cancellation (verdict `change`, proposed_changes `{"ShelvedCancelledType": "confirmed",
  "CancelledYear": "<yyyy>"}`). P2564 has CancelledYear 2023 but no type. **P3184 reads CancelledYear
  2018 but StartYear1 2021** — one of them is wrong; source both. A cancelled row still needs its
  specs sourced AS PROPOSED.

ROUTE-VS-SHEET MISMATCHES — RESEARCH THE PIPELINE, ROUTE FIRST (Baird 2026-09-10).
Where the sheet's start/end states disagree with the routes-repo geometry, do not flag and move on,
and do not assume either side is right. The route is at
`../GOIT-GGIT-pipeline-routes/data/individual-routes/gas-pipelines/<PID>.geojson` (read it:
coordinates, feature count, feature properties, which often name the digitizing source and specs).
In order:
1. **Judge the ROUTE first.** Is it an accurate trace of THIS pipeline: right corridor, right
   termini, the right project (not the parent system, a sibling segment, or a different pipeline)?
   Check it against sourced maps (FERC EIS/EA alignment sheets and county lists, the operator's
   system map, Texas RRC permit data). Give the geometry's first and last coordinates in plain words
   in researcher_notes.
2. **Then decide the cells.** If the route is right and the cell is wrong -> a fills[] record on
   `Location [ref]` with `value_cols: ["StartState/Province", "EndState/Province"]` and the sourced
   states, plus an `attribution` concern with `contested: {"StartState/Province": "<state>"}`. If the
   route is wrong -> a validity concern `contested: {"RouteAccuracy": "<your grade>"}`, the
   recommendation "route candidate for §8" with the sourced termini, and the cells stay as sourced.
   Both can be wrong. Never edit a state cell to match a bad route, and never propose coordinates.
3. A multi-feature route's first/last coordinates are in feature order, not flow order. For a system
   row, judge the route by its EXTENT and corridor, not by which feature comes first.
This batch's cases:
- **P0262 TETCO Main Line** — sheet Texas -> New York. The route is 470 OSM ways whose extent runs
  from south Texas (26.1°N) to the New Jersey / New York area (41.4°N, 74.2°W), so the audit's
  Tennessee/Kentucky "termini" are feature-order artifacts. Still grade it: does the OSM assembly
  include laterals or other operators' lines, and does it reach the system's true northern terminus?
- **P3683 Whistler Midland Lateral** — BOTH states blank. The route (16 features, from the operator's
  own data: properties `DATASOURCE: WWM`, `PIPESPEC: 16"...`, per-feature `LENGTHMI`) runs about
  31.2-32.3°N, 101.7-102.3°W (Midland / Martin County area). **The sheet reads 50 mi, Diameter `30,
  42`, 2,000 MMcf/d — the MAINLINE's diameter and capacity (P0319 reads `30, 42`, 2,000).** The route
  properties say 16-inch. Decide whether the route is the Midland Lateral, then whether the sheet's
  length/diameter/capacity are the lateral's or copied from the mainline (a `spec` concern if copied).
- **P6900 Cimarron River Gas Pipeline** — every cell blank except status. The route (9 features,
  properties `Operator: Cimarron River Pipeline`, `TYPEPIPE: Interstate`) runs from the Texas
  Panhandle (35.8°N, 102.0°W) through the Oklahoma Panhandle to southwest Kansas (37.1-37.6°N). Grade
  it, then source the termini states, length, diameter, capacity, owner, and StartYear1.
- **P2547 Gulf South Index 99 Expansion** — BOTH states blank; the route is a 3-point line in deep
  East Texas (31.3-31.6°N, about 94.0°W, San Augustine / Shelby County area). Grade it and source the
  states.
- **P0287 Gulf Coast Southbound Phase III** — sheet start Chicago, Illinois; end `Agua Dulce Hub`,
  **Louisiana**. Agua Dulce is in Nueces County, TEXAS. No route. Source the true termini (lead: the
  "Gulf Coast Southbound" projects are NGPL/Kinder Morgan reversal expansions — verify) and stage the
  corrected state with a Location fill.
- **Whitespace:** P7851 and P7852 read EndState `"Texas "` (trailing space) — stage trimmed `Texas`.
- **Name typo:** P0163 reads PipelineName `Enable Oklahoma Instrastate Transmission (EOIT)` —
  "Instrastate". Say so in a `spec` concern with the correctly spelled name from the operator's
  own document (lead: Enable was merged into Energy Transfer in 2021 — the current name may differ).

DUPLICATES AND FAMILIES — get these right before anything else:
- **Whistler: P0319 Mainline, P3683 Midland Lateral, P3887 Mainline Capacity Expansion** here; P3682
  Midland Lateral EXTENSION (proposed) is in batch A3 — a different scope from P3683.
- **Roadrunner: P0286 Phase 1 (200 mi) and P2601 Phase 2 (0 km but Diameter 30)** here; Phase 3
  (P2602) is in A3. A 0-length row with a diameter is internally inconsistent: if Phase 2 was
  compression, Diameter should be blank; if pipe, the length is wrong.
- **Permian Highway: P0302 mainline and P3884 Capacity Expansion (15 mi — compression plus some
  looping?)**; **Gulf Coast Express: P0378 mainline** (P3886 expansion in A3). Mainline figures are
  not refs for expansion rows.
- **Matterhorn Express P3882** — the row A3 is testing as possibly misfiled is **P5905 "Matterhorn
  Express | Blackfin Pipeline"**; if your sources say Blackfin is a separate project, put it in
  `cross_row_leads`.
- **Targa: P7851 Buffalo Run Gas Pipeline and P7852 Bull Run Gas Pipeline** (operating, every spec
  blank) here; their EXTENSIONS P7853/P7854 (construction) are in A3 and P7850 is in A7. Source what
  the originals are (length, diameter, capacity, StartYear1) without borrowing the extensions'
  figures.
- **Gulf South: P0197 SYSTEM row + P0198 Coastal Bend Header, P2547 Index 99, P2637 Willis Lateral**
  here; 11 operating expansions are in A2 and 4 proposed rows in A1. P0197's end cell holds four
  states — the sheet's multi-state convention for system rows; leave the form alone unless a state is
  wrong.
- **ANR: P0152 Main Line + P2530, P3187, P4380, P7793** here; other ANR rows are in A1/A2/A6/A7.
  **Northern Natural: P2579 Main Line + P4458, P4459, P4460 (Iowa replacement projects, each Capacity
  `0.00`)**; a replacement may add no capacity, but `0` needs a source stating no incremental
  capacity — otherwise UNRESOLVED on the value. **Southern Star: P2564, P7826** (system P0253 swept in
  slice 1). **Alliance: P3184, P3185** (system P0151 swept). **Transco: P5520 Texas to Louisiana
  Energy Pathway, P7814 Decatur Lateral.** **Trunkline P0274** (P3664 in A1). **Vector P0277**
  (sibling rows swept in slice 1). **Agua Blanca P2498** (P2499 swept, P7109 in A7). **MoGas P2566**
  (P2565 swept). **Producers Midstream P7861** (P7862 in A3).
- System rows vs segment rows: a system figure restated on a project row is a `spec` defect on the
  project row; a project figure is never a ref for the system row.

LENGTHS AND UNITS. Mixed mi/km — system rows here are in km (P0163, P0197, P0262, P0274) and mi
(P0152, P2579); read YOUR row's `LengthKnownUnits` before writing a number. Rows with `LengthKnown = 0`
(P0287, P2530, P2564, P2566, P2601, P3184, P3187, P3887, P5520, P7826) are compression/reversal
scopes: expansion with no new physical pipe -> `LengthKnown = 0`, Diameter blank is the RULE — confirm
the scope, don't "fix".

OWNERSHIP. Leads to verify, not answers: TC Energy (ANR), Enbridge (TETCO, Vector), Energy Transfer
(Trunkline, EOIT/Enable), Berkshire Hathaway Energy (Northern Natural), Boardwalk (Gulf South),
Kinder Morgan (Permian Highway, Gulf Coast Express, NGPL), WhiteWater with partners (Whistler, Agua
Blanca, Matterhorn Express), Pembina / Enbridge (Alliance — it changed hands), Southern Star
(privately held — source the owners), Targa, Williams (Transco). A disputed CURRENT owner is an
`attribution` concern with `contested` naming `Owner1` / `Owner2%` / `Operator`; owner/operator work
stages onto the `Gas_OperatorsOwners` tab.

THE SOURCE LADDER (in this order):
1. **FERC** — `elibrary.ferc.gov` and the CP docket for INTERSTATE lines (ANR, TETCO, Trunkline, NNG,
   Gulf South, Vector, Alliance, Southern Star, MoGas, Transco, Cimarron River): certificate orders
   state mileage by county, diameter, capacity, cost, in-service requirement; notices of commencement
   of service date StartYear; abandonment orders date retirements; Form 2 and tariffs give system
   figures. The applicant's filing and FERC's order restating it are ONE origin.
2. **Texas Railroad Commission / Oklahoma Corporation Commission / Kansas Corporation Commission** —
   intrastate lines (Permian Highway, GCX, Whistler, Agua Blanca, Roadrunner's Texas side, Targa,
   EOIT) are not FERC-certificated, so FERC silence is EXPECTED. RRC T-4 permits and RRC pipeline data;
   cite a specific permit or document page, never a search form.
3. **PHMSA / NPMS** — `www.npms.phmsa.dot.gov` (200); PHMSA annual report data for system mileage.
4. **EIA** — the Natural Gas Pipeline Projects workbook
   — **every release from May 2018 on is already on disk** in
   `sources/eia_pipeline_projects/raw/` (`raw/vintages.csv` gives each file's origin URL;
   `sources/eia_pipeline_projects/NOTES.md` the quirks). Read the local workbooks — do NOT
   re-download, and never cite the undated `EIA-NaturalGasPipelineProjects.xlsx`, which changes
   every quarter. Cite the DATED release
   URL that states the value, with the sheet and Excel row in `note`. EIA's `data.php` is a navigation page — never cite it.
5. **Operator disclosures** — SEC 10-K / 8-K (system descriptions state mileage and capacity), investor
   decks, tariffs, project pages. **SEC EDGAR answers 200 only to a DECLARED User-Agent** (`-A "Baird
   Langenbrunner research langenbrunner@gmail.com"`). One operator is ONE origin across all its pages
   and press releases.
6. **Trade and regional press** — NGI, S&P Global, Reuters, RBN, P&GJ, OGJ, Hart Energy, Midland
   Reporter-Telegram, The Oklahoman, Des Moines Register, Milwaukee Journal Sentinel.

INDEPENDENCE, precisely. FERC's order vs the company website = TWO origins. An RRC permit vs the
company = TWO. A Federal Register notice of an application restates the APPLICANT's numbers. The same
wire story reposted (businesswire / prnewswire / globenewswire / seekingalpha) is the operator's
origin. Anything citing GEM is disqualified.

EXISTENCE / DUPLICATE FLAGS — the bar is high. (a) Name the document you tested and what it does
and does not contain. (b) An intrastate line's absence from FERC is expected. (c) Read maps, not
just text. (d) Segment-vs-network: an aggregate restated on a segment row is a `spec` defect, but the
segment exists. (e) A proposed project "exists" if it was genuinely proposed: a filing, an open
season, an announcement.

RULES THAT BITE:
- Never cite GEM. abarrelfull, theodora and yingdodo are BANNED (url_verifier rejects them).
  Resolve every `bit.ly` / shortener before opening it and cite the resolved target; if it resolves
  to a banned host, the value is UNSOURCED — chase the footnote.
- Never fabricate a URL. Every URL goes through `scripts/url_verifier.py --name`.
- A blocked fetch is not a deletion; only a confirmed 404/410 retires a ref. Add Wayback captures.
- Cite the ARTICLE, never a navigation surface (site root, search results, eLibrary query URL,
  interactive map, EIA data.php, the RRC search form).
- SegmentCost: REFS_ADDED only when a primary source states THAT figure for THAT scope.
- Pressure: a FERC order or tariff states MAOP for many lines; look, don't force.
- Never fill a `[ref]` without a paired value.

TIMEOUTS. Put a hard timeout on every fetch (`curl --max-time 30`, the verifier's own timeout);
never let one slow host stall the row. **Write your shard EARLY** (after the first few units) and
update it as you go, so an interrupted run leaves partial work on disk.

MEASURED CONDITIONS (2026-09-10): `elibrary.ferc.gov` 200 fast; `www.ferc.gov` root 403s scripted
clients but `www.ferc.gov/sites/default/files/...pdf` paths return 200. `www.eia.gov` 503 to HEAD,
200 to GET. SEC EDGAR 200 with the declared UA, 403 with a browser UA. `web.archive.org` 200.

THE HARVESTED CITATION POOL (`wiki_citations.json`) IS A WORKLIST, NOT A LOOKUP TABLE. Report in
researcher_notes how many of your row's harvested citations you opened, and which you could not read.

VALUE CONVENTIONS: `*CostUnits` = bare currency code (`USD`). Controlled vocab lowercase except
`FIDStatus` (`Pre-FID` / `FID`); `ShelvedCancelledType` = `inferred` / `confirmed`. Capacity and
length in the sheet's units for your row. Canadian provinces as the sheet spells them (`Ontario`).
No recon legs run for US gas.
