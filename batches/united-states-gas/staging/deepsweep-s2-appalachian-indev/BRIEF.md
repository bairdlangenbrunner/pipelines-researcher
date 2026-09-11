SCOPE: US gas SLICE 2, batch A5 of 7 — APPALACHIAN / NORTHEAST / MID-ATLANTIC IN-DEVELOPMENT. 46 rows:
18 proposed, 1 construction (P2538 Transco Gateway), 5 shelved, 22 cancelled. This is the region of
the contested-and-cancelled Northeast projects (Atlantic Coast, PennEast, Constitution-era Transco
projects, Northeast Energy Direct, Northern Access 2016, North Brooklyn, NESE) and the newer
Appalachian expansions (MVP Southgate and Interconnect, Transco Southeast Supply Enhancement / Power
Express, Iroquois ExC, TETCO Appalachia to Market III, Columbia, EGTS, National Fuel, Texas Gas
Borealis, Rover). Baird chose 2026-09-10 to deep-sweep these rows with status review ON instead of a
separate in-dev pass later, so this is the ONLY pass these rows get this cycle: do the status work and
the data work together.

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
- **Construction row P2538 Transco Gateway Expansion** (LastUpdated 2022-10, 2022 target) — very
  likely in service; source the date (FERC notice of commencement of service, Williams release).
- **Proposed rows:** confirm with a dated source NEWER than LastUpdated, or find the change
  (FID/construction start -> `construction` + `ConstructionYear` + `FIDStatus = FID`; built ->
  `operating` + StartYear1; suspended -> `shelved`; withdrawn -> `cancelled` with
  `ShelvedCancelledType = confirmed`). Stale rows with past in-service targets: **P2600 Transco
  Regional Energy Access (2023-08; lead: REAP went into service in phases in 2023-2024), P3201 Transco
  Southeastern Trail (2022-10; lead: in service by 2021-2022), P4446 Columbia Virginia Electrification
  (2022-10), P4449 / P4450 / P4451 DTE Michigan Lateral rows (2022-10)**. Verify each lead; do not
  assume.
- **Shelved rows (P0296 Delmarva, P0323 Greater Philadelphia Expansion, P3189 Columbia Marysville
  Connector, P4447 Columbia Northern Loop, P6004 Chickahominy):** apply the dormancy rules (shelved
  >= 4y with no news -> `stale` / `4y->cancelled`, `ShelvedCancelledType = inferred`, no ref). Test
  each for revival first; a re-scoped project under a new name is not dead — name it and its GEM PID
  if it has one.
- **Cancelled rows (22):** is the cancellation RIGHT and SOURCED? Find the dated withdrawal (FERC
  order vacating the certificate / granting withdrawal, sponsor announcement, court decision): that
  is the `Cancelled [ref]`. Check CancelledYear against it. Rows reading `inferred` (P1926, P2524,
  P2616, P2628, P2651, P3199) become `confirmed` on a dated, sourced cancellation (verdict `change`
  with proposed_changes `{"ShelvedCancelledType": "confirmed", "CancelledYear": "<yyyy>"}`). Rows
  with no type at all (P0374, P3169, P4452, P5601) — supply it. **A cancelled project REVIVED is the
  most valuable finding in this batch.** Lead to verify: **P2574 Transco Northeast Supply Enhancement
  (NESE)** reads cancelled 2024, but Williams publicly moved to restart NESE in 2025 — if the revival
  is documented (FERC certificate reinstatement/extension, New York or New Jersey permits), the
  verdict is `change` to the current status with the dated source. Check **P4070 / P5405 North
  Brooklyn** and **P2575 / P6008 Northern Access 2016** for the same. A cancelled row still needs its
  specs sourced AS PROPOSED; proposal-era documents are the right ones.

ROUTE-VS-SHEET MISMATCHES — RESEARCH THE PIPELINE, ROUTE FIRST (Baird 2026-09-10).
Where the sheet's start/end states disagree with the routes-repo geometry, do not flag and move on,
and do not assume either side is right. The route is at
`../GOIT-GGIT-pipeline-routes/data/individual-routes/gas-pipelines/<PID>.geojson` (read it:
coordinates, feature count, any properties naming a digitizing source). In order:
1. **Judge the ROUTE first.** Is it an accurate trace of THIS pipeline: right corridor, right
   termini, the right project (not the parent system, a sibling phase, or a different pipeline)?
   Check it against sourced maps (FERC EIS/EA alignment sheets and county lists, the operator's
   project map, a state siting order). Give the geometry's first and last coordinates in plain
   words in researcher_notes.
2. **Then decide the cells.** If the route is right and the cell is wrong -> a fills[] record on
   `Location [ref]` with `value_cols: ["StartState/Province", "EndState/Province"]` and the sourced
   states, plus an `attribution` concern with `contested: {"EndState/Province": "<state>"}`. If the
   route is wrong or covers only part of the project -> a validity concern `contested:
   {"RouteAccuracy": "<your grade>"}`, the recommendation "route candidate for §8" with the sourced
   termini, and the cells stay as sourced. Both can be wrong. Never edit a state cell to match a bad
   route, and never propose coordinates.
3. **A market is not a terminus.** Many Northeast projects were "to serve New York / New Jersey
   markets" while the new pipe sat entirely in Pennsylvania, with compression elsewhere. The state
   cells record where the PHYSICAL facilities start and end. Say which facilities are where
   (pipeline loops vs compressor stations vs meter stations) from the FERC order.
This batch's cases:
- **P2524 Transco Diamond East (cancelled)** — sheet Pennsylvania -> New York, 50 mi; the route (7
  pts) lies entirely in northeastern Pennsylvania (about 41.1-41.35°N, 75.6-76.5°W, the Luzerne /
  Wyoming County area). Settle from the project's FERC pre-filing/application whether any facility
  was in New York; if not, the end state is a market, not a terminus.
- **P2574 Transco NESE** — sheet Lancaster County PA -> New York, 60 km. The route (5 pts) covers only
  the Raritan Bay corridor: from the Rockaway transfer point in New York waters (40.52°N, 73.87°W) to
  Middlesex County NJ (40.44°N, 74.31°W). NESE's FERC order lists several facilities (lead: a
  Pennsylvania loop in Lancaster County, a New Jersey loop, the offshore Raritan Bay Loop, and a new
  New Jersey compressor station — verify). So the route is PARTIAL: grade it, recommend a §8 route
  covering the certificated loops, and keep the cells as sourced (start Lancaster County PA is
  plausibly right).
- **P2600 Transco Regional Energy Access** — sheet Pennsylvania -> New Jersey; the route (22 pts)
  lies entirely in Pennsylvania (Luzerne County 41.37°N to the Monroe/Northampton area 40.91°N). Same
  test as NESE: are the New Jersey facilities compression/meter only? Grade the route against the
  certificated loops.
- **P2622 ACP Supply Header Project** — BOTH states blank; the route (9 pts) runs from Westmoreland
  County PA (40.46°N, 79.64°W) to north-central West Virginia (39.17°N, 80.56°W). Source the states.
- **P3669 Transco Appalachian Connector (cancelled 2017)** — BOTH states and every spec blank; the
  route (12 pts) runs from the northern West Virginia panhandle (39.99°N, 80.75°W) to southern Virginia
  (36.91°N, 79.37°W, the Pittsylvania County / Transco Station 165 area). Establish what this project
  was (existence first), then grade the route and source the states and specs as proposed.

DUPLICATES AND FAMILIES — get these right before anything else:
- **North Brooklyn: P4070 "North Brooklyn Pipeline" (cancelled 2023 confirmed, 250 MMcf/d, 2022) and
  P5405 "North Brooklyn Gas Pipeline" (cancelled, no year/type)** — identical termini (Brownsville ->
  Greenpoint), 7 mi, 30-inch. Very likely the SAME PROJECT filed twice (and lead: it was largely BUILT
  before the final phase was dropped — check whether what was built makes one row `operating`). If
  duplicate, file `duplicate` on BOTH, naming the other PID and saying which row should survive and why.
- **VNG Interconnect: P3200 "Transco | VNG Interconnect" (10 km, 245 MMcf/d, cancelled 2021 confirmed)
  and P5990 "VNG Interconnect" (24 mi, 30-inch, cancelled 2021 confirmed)** — the same name and
  cancellation year. Test whether they are one project (Transco facilities for Virginia Natural Gas's
  Header Improvement Project) or two distinct scopes (Transco's piece vs VNG's own pipe). If one,
  `duplicate` on both.
- **DTE Michigan Lateral: P4449 (parent row, every spec blank) + P4450 Rogers City Connector + P4451
  Norwalk Manistee Connector.** Decide what P4449 physically is. A parent row with no scope of its
  own restating its children is a `validity` / `duplicate` question — say which with the document.
- **PennEast: P0240 Phase I and P3196 Phase II**, both cancelled 2021. Each phase's specs are its
  own; the project total (e.g. 1,107 MMcf/d) is a ref for a phase only if the source applies it.
- **Atlantic Coast: P0155 mainline and P2622 Supply Header** — both cancelled 2020 confirmed.
- **Empire Northern Access 2016: P2575 (NY to Ontario) and P6008 (PA to NY)** — two scopes of one
  project; don't cross-cite specs.
- **Mountain Valley: P2567 Southgate Expansion and P7829 Interconnect Expansion (0 mi, 350 MMcf/d)**
  here; the MVP mainline P0220 and **P4456** are in batch A6. Test whether P7829 and P4456 describe
  the same scope (MVP's post-in-service capacity additions); if so, `duplicate` naming both.
- **EGTS: P3169 Mid-Atlantic Chiller, P4452 Morgantown Connector, P7825 Capital Area** (system row
  P3220 swept in slice 1). **Columbia: P3189, P4446, P4447, P7999** (P7999 Appalachia Supply Project
  has EVERY cell blank — existence and specs from scratch). **Iroquois: P2651, P3279** (system P0205
  swept). **Transco: P2524, P2538, P2574, P2600, P3199, P3200, P3201, P3669, P7108, P7800.**
- Singletons on systems in other batches (context, not refs): P5601 TGP Northeast Energy Direct
  (TGP rows swept in slice 1), P7794 Texas Gas Borealis (Texas Gas swept), P7801 Rover Bulger and
  Harmon Creek (Rover swept), P7813 TETCO Appalachia to Market III (TETCO rows in A4/A6), P7827
  National Fuel Tioga Pathway (NFG rows in A6), P1926 DeRuyter Expansion (P0310 swept).

CELLS THAT LOOK WRONG — check each with a source, don't just "fix":
- **Typos:** P2567 end `North Caolina`; P2628 end `West Virgina`. Stage the corrected spelling in a
  `Location [ref]` fill with a source that places the terminus.
- **P3169 EGTS Mid-Atlantic Chiller** reads end location `Chicago`, state `Virginia` — no such
  terminus is plausible for an EGTS project; source the true facility location.
- **P3201 Transco Southeastern Trail** reads Virginia -> **Louisiana**; lead: its facilities were in
  Virginia and the Carolinas/Georgia. Source the states.
- **P7813 TETCO Appalachia to Market III** reads start state **Delaware**; check it.
- **P1926 DeRuyter Expansion** reads capacity `0.55 bcm/y` — keep the sheet's units; note the
  MMcf/d equivalent in researcher_notes.

LENGTHS AND UNITS. Mixed mi/km; read YOUR row's `LengthKnownUnits` before writing a number. Rows with
`LengthKnown = 0` (P2538, P2651, P3169, P3279, P4446, P7800, P7801, P7813, P7825, P7829) are
compression/meter scopes: expansion with no new physical pipe -> `LengthKnown = 0`, Diameter blank is
the RULE — confirm the scope, don't "fix". **P7813 reads 0 mi with Diameter 36** — internally
inconsistent; source which is right.

OWNERSHIP. Leads to verify, not answers: Williams (Transco; NESE; Northeast Supply), Dominion / Duke
(Atlantic Coast), UGI / Enbridge / NJR / SJI / Southern Co (PennEast partners — verify), Equitrans
(now EQT) and partners (MVP), TC Energy (Columbia, Iroquois partner), Berkshire Hathaway Energy (EGTS
— formerly Dominion Energy Transmission), National Fuel (Empire, NFG Supply), Enbridge (TETCO), Kinder
Morgan (TGP), Boardwalk (Texas Gas), Energy Transfer (Rover), National Grid (North Brooklyn), DTE,
Chesapeake Utilities (Delmarva, Aspire Energy Express). A disputed CURRENT owner is an `attribution`
concern with `contested` naming `Owner1` / `Owner2%` / `Operator`; owner/operator work stages onto the
`Gas_OperatorsOwners` tab.

THE SOURCE LADDER (in this order):
1. **FERC** — `elibrary.ferc.gov` and the CP docket: the ORDER states mileage by county, diameter,
   capacity, cost, in-service requirement; notices of commencement of service date StartYear; orders
   vacating / granting withdrawal date cancellations. The applicant's filing and FERC's order
   restating the applicant's numbers are ONE origin; say which document you cite.
2. **State regulators and courts** — NY DEC and NY PSC (water quality certificates, North Brooklyn's
   rate case), NJ DEP and NJ BPU, PA DEP, VA SCC, WV PSC, Ohio Power Siting Board, Michigan PSC,
   Maryland PSC, Delaware PSC; federal appeals-court decisions (ACP, PennEast, MVP). A court opinion
   is its own origin.
3. **PHMSA / NPMS** — `www.npms.phmsa.dot.gov` (200).
4. **EIA** — the Natural Gas Pipeline Projects workbook
   — **every release from May 2018 on is already on disk** in
   `sources/eia_pipeline_projects/raw/` (`raw/vintages.csv` gives each file's origin URL;
   `sources/eia_pipeline_projects/NOTES.md` the quirks). Read the local workbooks — do NOT
   re-download, and never cite the undated `EIA-NaturalGasPipelineProjects.xlsx`, which changes
   every quarter. Cite the DATED release
   URL that states the value, with the sheet and Excel row in `note`. EIA's `data.php` is a navigation page — never cite it.
5. **Operator disclosures** — SEC 10-K / 8-K / investor decks, project pages. **SEC EDGAR answers 200
   only to a DECLARED User-Agent** (`-A "Baird Langenbrunner research langenbrunner@gmail.com"`). One
   operator is ONE origin across all its pages and press releases.
6. **Trade and regional press** — NGI, S&P Global, Reuters, RBN, P&GJ, E&E News, Utility Dive,
   Pittsburgh Post-Gazette, Times Leader (Wilkes-Barre), Morning Call, NJ.com, Gothic/THE CITY (New
   York), Richmond Times-Dispatch, Cardinal News, Charleston Gazette-Mail, Columbus Dispatch.

INDEPENDENCE, precisely. FERC's order vs the company website = TWO origins. A state order vs FERC =
TWO. A court opinion vs FERC = TWO. A Federal Register notice of an application restates the
APPLICANT's numbers. The same wire story reposted (businesswire / prnewswire / globenewswire /
seekingalpha) is the operator's origin. Advocacy groups' pages restating FERC figures are FERC's
origin. Anything citing GEM is disqualified.

EXISTENCE / DUPLICATE FLAGS — the bar is high. (a) Name the document you tested and what it does
and does not contain. (b) Read maps, not just text. (c) Segment-vs-network: an aggregate restated on
a phase row is a `spec` defect, but the phase exists. (d) A proposed project "exists" if it was
genuinely proposed: a filing, an open season, an announcement.

RULES THAT BITE:
- Never cite GEM. abarrelfull, theodora and yingdodo are BANNED (url_verifier rejects them).
  Resolve every `bit.ly` / shortener before opening it and cite the resolved target; if it resolves
  to a banned host, the value is UNSOURCED — chase the footnote.
- Never fabricate a URL. Every URL goes through `scripts/url_verifier.py --name`.
- A blocked fetch is not a deletion; only a confirmed 404/410 retires a ref. Add Wayback captures.
- Cite the ARTICLE, never a navigation surface (site root, search results, eLibrary query URL,
  interactive map, EIA data.php).
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
length in the sheet's units for your row. No recon legs run for US gas.
