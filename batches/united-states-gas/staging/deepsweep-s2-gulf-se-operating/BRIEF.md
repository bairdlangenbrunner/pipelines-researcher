SCOPE: US gas SLICE 2, batch A2 of 7 — GULF COAST + SOUTHEAST, OPERATING / IDLE (plus the region's
few non-Gulf in-dev rows). 41 rows: 32 operating, 2 idle (P0188 UTOS, P6584 ANR Offshore Grand
Chenier), 3 construction (P0311 Buncombe County, P2556 Columbia Louisiana XPress, P5627 East Tennessee
Ridgeline), 3 proposed (P4420 Carolina Gas Moore–Dorchester, P4448 Columbia Mainline 100/200
Replacement, P7106 Cumberland), and 3 cancelled (P0355 T-030, P2518 Texas Gas Clarksville
Interconnection, P5600 TGP NGL Conversion). Louisiana-heavy: the offshore gathering/transmission
systems (HIOS, UTOS, Stingray, Columbia Gulf), the Haynesville egress lines that are now built (LEAP,
Gulf Run, NG3, Gillis Access), Plaquemines feed lines (Gator Express, Evangeline Pass, Columbia East
Lateral Xpress), and about a dozen Gulf South (Boardwalk) expansions. Baird chose 2026-09-10 to
deep-sweep these rows with status review ON instead of a separate status pass later, so this is the
ONLY pass these rows get this cycle: do the status work and the data work together.

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
- **Operating rows (32):** the question is whether each is STILL operating, and whether StartYear1 is
  right. Look for abandonment (a FERC `CP` abandonment order, a BSEE/BOEM relinquishment for an
  offshore line), idling, sale/rename, or conversion. A clean "still operating" verdict needs a dated
  source newer than LastUpdated (a current tariff, a 10-K system description, an EIA/PHMSA listing) —
  say which. The offshore rows (P0200 HIOS, P0256 Stingray, P6533 Columbia Gulf's offshore laterals)
  are the likeliest to have partial abandonments.
- **Idle rows (P0188 UTOS, P6584 ANR Offshore Grand Chenier):** both read `ShelvedCancelledType =
  confirmed`. Is the line still idle, abandoned in place, removed, or back in service? A FERC
  abandonment authorization or a BSEE decommissioning record is the document. Idle -> retired is a
  status change; state the year.
- **Construction rows:** P2556 Columbia Louisiana XPress (LastUpdated 2022-10, in-service target
  2022) is very likely operating — source the in-service date. P0311 Buncombe County Pipeline (2023
  target) — same question. P5627 East Tennessee Ridgeline (2026 target) — confirm construction is
  underway (FERC notice to proceed, construction start) or find the delay.
- **Proposed rows:** confirm with a dated source NEWER than LastUpdated, or find the change.
  P4420 Moore–Dorchester (2022-09) and P4448 Columbia Mainline 100/200 Replacement (2022-10) are
  stale; either may now be built (-> operating + StartYear1) or withdrawn. P7106 Cumberland Gas
  Pipeline (2024-10) — lead: a TGP lateral to TVA's Cumberland plant in Tennessee; verify, and note
  the row has no start/end states and no specs besides length.
- **Cancelled rows (P0355, P2518, P5600):** the question is whether the cancellation is RIGHT and
  SOURCED. Find the dated withdrawal (FERC order vacating the certificate / granting withdrawal,
  sponsor announcement): that is the `Cancelled [ref]`. Check CancelledYear against it. A
  "cancelled" project that was actually BUILT is a status change to operating. A cancelled row still
  needs its specs sourced AS PROPOSED. **P5600 TGP NGL Conversion Expansion** (964 mi, no states)
  concerned converting part of TGP to NGL service. Research it as the GAS-TRACKER row it is (status,
  cancellation, specs as proposed); do NOT open any oil/NGL-tracker work — oil is out of scope this
  cycle. If it should not be in the gas tracker at all, say so as a `validity` concern, nothing more.

ROUTE-VS-SHEET MISMATCHES — RESEARCH THE PIPELINE, ROUTE FIRST (Baird 2026-09-10).
Where the sheet's start/end states disagree with the routes-repo geometry, do not flag and move on,
and do not assume either side is right. The route is at
`../GOIT-GGIT-pipeline-routes/data/individual-routes/gas-pipelines/<PID>.geojson` (read it:
coordinates, feature count, feature properties, which often name the digitizing source). In order:
1. **Judge the ROUTE first.** Is it an accurate trace of THIS pipeline: right corridor, right
   termini, the right project (not the parent system, a sibling phase, or a different pipeline)?
   Check it against sourced maps (FERC EIS/EA alignment sheets and county lists, the operator's
   system map, BOEM/BSEE pipeline records for offshore lines, a state siting order). Give the
   geometry's first and last coordinates in plain words in researcher_notes.
2. **Then decide the cells.** If the route is right and the cell is wrong -> a fills[] record on
   `Location [ref]` with `value_cols: ["StartState/Province", "EndState/Province"]` and the sourced
   states, plus an `attribution` concern with `contested: {"StartState/Province": "<state>"}`. If
   the route is wrong -> a validity concern `contested: {"RouteAccuracy": "<your grade>"}`, the
   recommendation "route candidate for §8" with the sourced termini, and the cells stay as sourced.
   Both can be wrong. Never edit a state cell to match a bad route, and never propose coordinates.
3. Offshore: `Gulf of Mexico` is the sheet's convention for an offshore terminus. A route point a
   few miles off the coast is an offshore terminus, not a Louisiana one. A route digitized in the
   reverse direction (onshore first) is not a mismatch — say so and move on.
This batch's cases:
- **P0256 Stingray Gas Pipeline** — start state BLANK, end Louisiana; 325 mi, 36-inch, operating.
  The route is 45 BOEM pipeline-segment features (properties `SEGMENT_NU`, `ROW_NUMBER`,
  `STATUS_COD`, `PPL_SIZE_C`), from about 27.3°N far offshore to the Cameron coast (29.8°N). **About
  30 of the 45 segments are coded `ABN` (abandoned) or `REM` (removed), and sizes run 4-36 inch,
  some gas/condensate (`G/C`).** Judge whether this trace is Stingray at all, or Stingray plus other
  operators' abandoned laterals: the BOEM ROW numbers identify the right-of-way holder — check them
  against BOEM's pipeline data for Stingray. If much of the system is abandoned, that also bears on
  the length (325 mi) and the status. Source the start (offshore -> `Gulf of Mexico`).
- **P0188 UTOS** — sheet Gulf of Mexico -> Johnson's Bayou LA; route 5 pts, 29 mi, from about 25 mi
  off the Cameron coast (where it meets HIOS P0200's last point) to Johnson's Bayou. The audit's
  "Louisiana" start is a coastal-buffer artifact. Confirm the offshore terminus (HIOS platform
  block) and grade a 5-point `high` route.
- **P6584 ANR Offshore Grand Chenier System** — sheet West Cameron Block 167 (Gulf of Mexico) ->
  Grand Chenier LA; route digitized onshore-first (Grand Chenier -> about 29.1°N offshore). Likely a
  direction artifact; confirm the block and the onshore facility.
- **P3193 Gator Express Phase 2** — start BLANK, end Plaquemines LNG; route 2 parts, 9 pts, 12 mi
  in Plaquemines Parish (about 29.60°N to 29.43°N along the river). Source the start (which
  interconnect) and check the route reaches the terminal site.
- **P6533 Columbia Gulf Transmission (system row)** — BOTH states and nearly every spec blank; the
  route is 184 OSM ways from offshore Louisiana (29.1°N) to eastern Kentucky (38.4°N, the Leach
  area). Source the termini states (lead: Louisiana to Kentucky via Mississippi and Tennessee —
  verify), and check whether the OSM assembly includes non-Columbia Gulf lines. System-level specs
  (length, diameter, capacity) belong on this row; do not put them on project rows.
- Straight-line routes (`very low`): P5926 GS Southeast Expansion and P5932 GS Texas to Mississippi
  Expansion are 2-point lines. The grade is already honest; note the sourced termini so a §8 route
  can be drawn later, but do not file a concern just for `very low`.

DUPLICATES AND FAMILIES — get these right before anything else:
- **LEAP (Enbridge), 4 rows here: P5113 mainline (150 mi, 1,000 MMcf/d) and P5114 / P6773 / P6842
  Expansion Phases 1/2/3** (all LengthKnown 0 — compression). Phase 4 (P6843) is in batch A1. A
  mainline figure is never a ref for a phase row, and phase capacities are not the mainline's.
- **Gulf South (Boardwalk), 9 operating expansion rows here** (P2561, P3194, P5926, P5932, P5939,
  P5967, P5968, P5969, P5974, P5975, P5976). The system row P0197 and P0198/P2547/P2637 are in batch
  A4; four proposed rows are in A1. A system figure is never a ref for a project row. Gulf South's
  own project pages and FERC orders per project are the sources.
- **Gator Express (Venture Global): P3193 Phase 2 and P5415 Meter Project (Line 40 Connection)**
  here; Phase I (P0193) is in A1. Plaquemines is the terminal for P2536 Evangeline Pass and P3188
  Columbia East Lateral Xpress too — interconnects, not duplicates.
- **Gillis hub cluster:** P5416 Gillis Access Main Line, P5417 NG3, P1294 Gulf Run, P5113 LEAP all
  end at or near Gillis/Starks LA. Interconnects are not duplicates, but check that no two rows
  describe the same pipe under different names (P5416 vs P5417 in particular — both Haynesville to
  Gillis, 2024-2025).
- **Florida Gas Transmission: P4059 Mobile County Project and P5548 South Louisiana Project** are
  here; P7824 FGT South Central Louisiana (proposed) is in A1 — a different project with a similar
  name. Do not cross-cite. The FGT system and ~20 other FGT rows were swept in slice 1.
- **Columbia Gas Transmission: P2556 Louisiana XPress, P3188 East Lateral Xpress, P4448 Mainline
  100/200 Replacement** here; P3189/P4446/P4447/P7999 are in A5. LXP is a Columbia GULF expansion in
  practice (Kentucky to Louisiana compression) — confirm which system the project belongs to; the
  row's PipelineName may be wrong.
- **HIOS P0200 and UTOS P0188** connect (HIOS's end cell reads "Gulf of Mexico, UTOS Gas Pipeline").
  Both read 2,000 MMcf/d and 42-inch, 1978 — check that each figure is that line's own, not the
  other's.
- **East Tennessee: P5627 Ridgeline and P7809 System Alignment Project.** P7809 reads Capacity
  `0.00` MMcf/d — a replacement/realignment may legitimately add no capacity, but `0` is a value
  that needs a source; if no source states zero incremental capacity, UNRESOLVED on the value.
- Singletons on systems swept in slice 1 (context, not refs): P2509 TETCO Cameron Expansion (0.32 km),
  P2518 Texas Gas Clarksville, P4420 Carolina Gas Moore–Dorchester, P5600 TGP, P7792 Transco
  Southeast Energy Connector.

TYPOS IN STATE CELLS: P0311 end `North Carolna`, P2518 start `Kentuky` and end `Tennesse`. Stage the
corrected spelling as a `Location [ref]` fill with a source that places the termini (the spelling is
mechanical; the ref is still owed).

LENGTHS AND UNITS. Mixed mi/km; read YOUR row's `LengthKnownUnits` before writing a number. Rows with
`LengthKnown = 0` (P2556, P2561, P4059, P4420, P5114, P5548, P5968, P5974, P6773, P6842) are
compression/meter scopes: expansion with no new physical pipe -> `LengthKnown = 0`, Diameter blank is
the RULE — confirm the scope, don't "fix". P4420 and P4448 read length 0 / 0.5 mi with a proposal
year of 2022; confirm what physical work each involves.

OWNERSHIP. Leads to verify, not answers: Venture Global (Gator Express), Kinder Morgan (TGP,
Evangeline Pass), Enbridge (LEAP, TETCO, UTOS, East Tennessee), Williams (Transco), Momentum Midstream
(NG3), Boardwalk (Gulf South, Texas Gas), TC Energy (Columbia Gas, Columbia Gulf, ANR), Energy
Transfer / Kinder Morgan (FGT via Citrus), Berkshire Hathaway Energy or Dominion (Carolina Gas —
it changed hands), Stingray (owner unknown to us — source it). A disputed CURRENT owner is an `attribution` concern with `contested` naming `Owner1` /
`Owner2%` / `Operator`; owner/operator work stages onto the `Gas_OperatorsOwners` tab.

THE SOURCE LADDER (in this order):
1. **FERC** — `elibrary.ferc.gov` and the CP docket: the ORDER states mileage by parish/county,
   diameter, capacity, cost, in-service requirement; notices of commencement of service date
   StartYear; abandonment orders date retirements. The applicant's filing and FERC's order
   restating the applicant's numbers are ONE origin; say which document you cite.
2. **BOEM / BSEE** for offshore lines — BOEM's pipeline data (ROW numbers, segment status, size) and
   BSEE decommissioning records. Cite a specific document or data page, never a map viewer.
3. **State regulators** — FERC silence is EXPECTED for an intrastate line (LEAP, NG3, Gillis Access
   and several Haynesville lines are intrastate). Louisiana DNR / Office of Conservation and SONRIS;
   Louisiana PSC; Mississippi, Alabama, Tennessee, Kentucky, North and South Carolina PSCs/PUCs.
4. **PHMSA / NPMS** — `www.npms.phmsa.dot.gov` (200).
5. **EIA** — the Natural Gas Pipeline Projects workbook
   — **every release from May 2018 on is already on disk** in
   `sources/eia_pipeline_projects/raw/` (`raw/vintages.csv` gives each file's origin URL;
   `sources/eia_pipeline_projects/NOTES.md` the quirks). Read the local workbooks — do NOT
   re-download, and never cite the undated `EIA-NaturalGasPipelineProjects.xlsx`, which changes
   every quarter. It is the
   likely answer for in-service years, capacities and costs on most project rows here. Cite the DATED release
   URL that states the value, with the sheet and Excel row in `note`. EIA's `data.php` is a navigation page — never cite it.
6. **Operator disclosures** — SEC 10-K / 8-K / investor decks, tariffs, project pages. **SEC EDGAR
   answers 200 only to a DECLARED User-Agent** (`-A "Baird Langenbrunner research
   langenbrunner@gmail.com"`). One operator is ONE origin across all its pages and press releases.
7. **Trade and regional press** — NGI, S&P Global, Reuters, RBN, P&GJ, OGJ, LNG Prime, The Advocate,
   American Press (Lake Charles), NOLA.com, Mississippi Today, AL.com, Tennessean, Asheville
   Citizen-Times.

INDEPENDENCE, precisely. FERC's order vs the company website = TWO origins. A state order vs FERC =
TWO. BOEM's data vs FERC = TWO. A Federal Register notice of an application restates the APPLICANT's
numbers. The same wire story reposted (businesswire / prnewswire / globenewswire / seekingalpha) is
the operator's origin. Anything citing GEM is disqualified.

EXISTENCE / DUPLICATE FLAGS — the bar is high. (a) Name the document you tested and what it does
and does not contain. (b) An intrastate line's absence from FERC is expected. (c) Read maps, not
just text. (d) Segment-vs-network: an aggregate restated on a phase row is a `spec` defect, but the
phase exists. (e) A proposed project "exists" if it was genuinely proposed: a filing, an open
season, an announcement.

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
