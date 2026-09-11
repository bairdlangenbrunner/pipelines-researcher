SCOPE: US gas SLICE 2, batch A1 of 7 — GULF COAST IN-DEVELOPMENT. 44 rows: 41 proposed /
construction / shelved and 3 cancelled (P0285 Haynesville Global Access, P2522 Creole Trail
Reversal, P3192 FGT Big Bend). Louisiana-heavy: the LNG feed-gas buildout (Plaquemines, Driftwood /
Louisiana LNG, Port Arthur, Golden Pass, Commonwealth, Delfin, CP2, Lake Charles) and the
Haynesville-to-Gulf egress corridor, plus Mississippi / Alabama / Florida projects. Baird chose
2026-09-10 to deep-sweep these rows with status review ON instead of a separate in-dev pass later, so
this is the ONLY pass these rows get this cycle: do the status work and the data work together.

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
- **Construction rows (P0193, P2539, P2542, P3186, P3282, P3664, P5115, P6843, P7805, P7831):** the
  question is whether each is NOW IN SERVICE. Several had in-service targets in 2022-2025. An
  in-service announcement, a FERC in-service notice/letter (the `CP` docket's "notice of
  commencement of service"), or the EIA project workbook's in-service date -> verdict `change` to
  `operating` with `StartYear1`. **P2542 Gulfstream Phase VI** was last updated 2022-10 with a 2022
  in-service target — it is very likely operating; source the date.
- **Proposed rows:** confirm with a dated source NEWER than LastUpdated, or find the change
  (FID/construction start -> `construction` + `ConstructionYear` + `FIDStatus = FID`;
  suspended -> `shelved`; withdrawn -> `cancelled` with `ShelvedCancelledType = confirmed`).
  Rows last touched 2022-2023, most likely to be stale: P3663 Commonwealth LNG pipeline (2022-07),
  P4457 Lowman (2022-10), P2559 Magnolia (2023-07), P5509 Sabine Pass Stage 5 pipeline (2023-07),
  P5516 CE FLNG pipelines (2023-07), P3665 West Delta LNG pipeline (2023-08).
  **LNG-feed pipelines follow their terminal:** a terminal's FID, suspension, or cancellation is
  strong evidence for the pipeline's status, but it is the TERMINAL's evidence. State in
  researcher_notes whether the source speaks to the pipeline itself.
- **Shelved rows (P2523, P2737, P3590, P5881):** apply the dormancy rules (shelved >= 4y with no
  news -> `stale` / `4y->cancelled`, `ShelvedCancelledType = inferred`, no ref). P5881 Magnolia
  Extension was shelved 2019 and P2523 Delhi Connector 2021 — test each for revival first (a
  re-scoped project under a new name is not dead; name it and its GEM PID if it has one).
- **Cancelled rows (P0285, P2522, P3192):** the question is whether the cancellation is RIGHT and
  SOURCED, not whether it is dormant. Find the dated withdrawal (FERC order vacating the
  certificate / granting withdrawal, sponsor announcement, press): that is the `Cancelled [ref]`.
  Check CancelledYear against it. P2522 reads `inferred` — a dated, sourced cancellation makes it
  `confirmed` (verdict `change` with proposed_changes
  `{"ShelvedCancelledType": "confirmed", "CancelledYear": "<yyyy>"}`). A "cancelled" project that
  was actually BUILT is a status change to operating — the most valuable finding this half can make.
  A cancelled row still needs its specs sourced AS PROPOSED; proposal-era documents are the right ones.

ROUTE-VS-SHEET MISMATCHES — RESEARCH THE PIPELINE, ROUTE FIRST (Baird 2026-09-10).
Where the sheet's start/end states disagree with the routes-repo geometry, do not flag and move on,
and do not assume either side is right. The route is at
`../GOIT-GGIT-pipeline-routes/data/individual-routes/gas-pipelines/<PID>.geojson` (read it:
coordinates, feature count, any properties such as a digitizing source). In order:
1. **Judge the ROUTE first.** Is it an accurate trace of THIS pipeline: right corridor, right
   termini, the right project (not the parent system, a sibling phase, or a different pipeline)?
   Check it against sourced maps (FERC EIS/EA alignment sheets and county lists, the operator's
   project map, a state siting order). Give the geometry's first and last coordinates in plain
   words ("near Meridian MS", "Augusta GA area") in researcher_notes.
2. **Then decide the cells.** If the route is right and the cell is wrong -> a fills[] record on
   `Location [ref]` with `value_cols: ["StartState/Province", "EndState/Province"]` and the sourced
   states, plus an `attribution` concern with `contested: {"StartState/Province": "<state>"}`. If
   the route is wrong -> a validity concern `contested: {"RouteAccuracy": "<your grade>"}`, the
   recommendation "route candidate for §8" with the sourced termini, and the cells stay as sourced.
   Both can be wrong. Never edit a state cell to match a bad route, and never propose coordinates.
3. A compression-only or multi-state project can legitimately touch states the new pipe does not.
   Say which facilities are where.
This batch's cases:
- **P3664 Trunkline Pipeline Modifications (Lake Charles LNG)** — sheet start `Mississippi`, end
  Louisiana; the route (21 pts, digitized from the 2015 FERC FEIS, 17.9 mi) lies entirely in
  Calcasieu/Cameron area, Louisiana. Its properties list `AffectedSt: LA, MS, AR`, so the project
  may include compression or modifications upstream in MS/AR. Settle which states the facilities
  are in and whether `Mississippi` is a real terminus. Also: the row reads status `construction`
  with StartYear1 2031 — check the Lake Charles LNG project's current status and what it means
  for this row.
- **P7855 SNG South System Expansion 4** — sheet MS -> South Carolina; the route (14 features,
  1,038 pts) runs from about the MS/AL line east of Meridian to the Augusta, Georgia area. Settle
  the true termini from the FERC application/order (lead: check whether any facilities sit in SC
  across the river from Augusta) and whether the route covers the project or only part of it.
- **P2542 Gulfstream Phase VI** — BOTH state cells blank; the route is a 2-point straight line in
  the Tampa Bay area, Florida (`very low` accuracy). Source the state(s), and grade the route.
- **P0173 Delfin Offshore** — route is 6 pts / ~0.5 km at the Cameron LA coast; the sheet says Gulf
  of Mexico (start/end are the UTOS and HIOS pipelines, length 0.21 km). The state mismatch is an
  offshore snapping artifact; still check the route against the project's own description.
- Blank states, no route: P3663, P5509, P7833 (both blank). Source them.

DUPLICATES AND FAMILIES — get these right before anything else:
- **P7802 "Tennessee Gas Pipeline | Mississippi Crossing (MSX)" and P7841 "Mississippi Crossing
  Project"** carry identical values (Greenville MS -> Butler AL, 208 mi, 2,100 MMcf/d, 2028). Very
  likely the SAME PROJECT filed twice. Test it; if so, file `duplicate` on BOTH, naming the other
  PID and saying which row should survive (and why — owner/attribution, completeness).
- **Driftwood LNG Pipeline, 4 rows: P0177 Mainline (99.3 mi, 4,000 MMcf/d) and P3282 / P7770 /
  P7769 Line 200 & Line 300 Expansion Phases 1/2/3.** The terminal has changed hands and name
  since the rows were written (lead: Woodside acquired Tellurian in 2024 and renamed the terminal
  Louisiana LNG — verify). Decide what each row physically is; a mainline figure is not a ref
  for a phase row, and phase figures are not refs for the mainline.
- **Port Arthur family:** P3197 Louisiana Connector Amendment and P3590 Louisiana Connector
  Extension (shelved) are here; **P0241 Louisiana Connector and P3198 Texas Connector are in batch
  A3** (swept in parallel). Put facts about them in `cross_row_leads`.
- **Haynesville egress corridor:** P5115 Louisiana Energy Gateway (LEG), P6843 LEAP Expansion
  Phase 4 (Phases 1-3 are in batch A2), P0285 Haynesville Global Access (cancelled), P2523 Delhi
  Connector (shelved), P7807 Gillis Access Extension (Main Line P5416 in A2), P7808 Transco Gillis
  West, P7831 Pelican, P7832 NGPL Texas-Louisiana Expansion, P2737 Delta Express (shelved), P2559
  Magnolia. Many share termini (Gillis hub, Haynesville, Carlyss). Interconnects are not
  duplicates, but a renamed or merged project can be.
- **P2737 Delta Express (Venture Global) and P6531 DeLa Express (batch A3)** are distinct
  projects with similar names. Do not cross-cite.
- **P0193 Gator Express Phase I** (construction) and **P5519 TETCO Venice Extension** (proposed)
  both feed Plaquemines LNG; Gator Express Phase 2 (P3193) is in batch A2.
- **Gulf South (Boardwalk), 4 proposed rows here:** P7780 PLUSS, P7784 Eunice Reliability & Lake
  Charles Supply, P7810 Kosci Junction, P7815 Southeast CURE. The system row P0197 is in A4 and
  about a dozen operating expansions are in A2. A system figure is never a ref for a project row.
- Singletons on systems swept in slice 1 (context, not refs): P2545 Transco Hillabee Phase 3
  (Phases 1-2 swept, batch 2); P2605 Sabal Trail Phase III (Phases I-II swept); P3192 FGT Big Bend
  and P7824 FGT South Central Louisiana (FGT swept; P5548 FGT South Louisiana is in A2 — a
  different project with a similar name); P2522 / P7797 Creole Trail (main line P0283 swept);
  P5881 Magnolia Extension (P0294 swept); P7855 SNG and P7802 TGP (system rows swept).
- **Rows with almost nothing on them — existence first:** P4457 Lowman Pipeline (every spec
  blank), P5509 Sabine Pass LNG Stage 5 Expansion Pipeline, P5516 CE FLNG Terminal Pipelines
  (proposal 2012), P7833 South Mississippi Project. A cancelled or never-proposed project is a
  status or existence finding; say which with the document.

LENGTHS AND UNITS. Mixed mi/km; read YOUR row's `LengthKnownUnits` before writing a number. Twelve
rows carry `LengthKnown = 0` (compression/meter/modification scopes: P2605, P3186, P3197, P6843,
P7769, P7784, P7797, P7805, P7808, P7815, P7824, P7832): expansion with no new physical pipe ->
`LengthKnown = 0`, Diameter blank is the RULE — confirm the scope, don't "fix". **P7832 NGPL
TX-LA Expansion reads Capacity 300,000 Dth/d** — keep the sheet's units; note the MMcf/d equivalent
in researcher_notes.

OWNERSHIP. Leads to verify, not answers: Venture Global (Gator Express, Delta Express), Woodside
(Driftwood / Louisiana LNG), Sempra (Port Arthur), Cheniere (Creole Trail, Sabine Pass), Energy
Transfer (Trunkline, Lake Charles; FGT via Citrus), Kinder Morgan (TGP, SNG, NGPL), Williams
(Transco, LEG, Gulfstream co-owner), Boardwalk (Gulf South), Enbridge (TETCO; LEAP), TC Energy (ANR).
Owner/operator work is staged onto the `Gas_OperatorsOwners` tab; a disputed CURRENT owner is an
`attribution` concern with `contested` naming `Owner1` / `Owner2%` / `Operator`.

THE SOURCE LADDER (in this order):
1. **FERC** — `elibrary.ferc.gov` and the CP docket. LNG feed pipelines are usually certificated
   with the terminal (NGA section 3 + 7): the ORDER states mileage by parish/county, diameter,
   capacity, cost, in-service requirement; notices of commencement of service date StartYear;
   orders vacating / granting withdrawal date cancellations. The applicant's filing and FERC's
   order restating the applicant's numbers are ONE origin; say which document you cite.
2. **State regulators** — FERC silence is EXPECTED for an intrastate line (LEG, LEAP, Magnolia,
   Pelican and several Haynesville egress lines are intrastate). Louisiana DNR / Office of
   Conservation and SONRIS; Louisiana PSC; Mississippi PSC; Alabama PSC; Florida PSC.
3. **PHMSA / NPMS** — `www.npms.phmsa.dot.gov` (200).
4. **EIA** — the Natural Gas Pipeline Projects workbook
   — **every release from May 2018 on is already on disk** in
   `sources/eia_pipeline_projects/raw/` (`raw/vintages.csv` gives each file's origin URL;
   `sources/eia_pipeline_projects/NOTES.md` the quirks). Read the local workbooks — do NOT
   re-download, and never cite the undated `EIA-NaturalGasPipelineProjects.xlsx`, which changes
   every quarter. It is the
   likely answer for in-service years, capacities and costs on most project rows here. Cite the DATED release
   URL that states the value, with the sheet and Excel row in `note`. EIA's `data.php` is a navigation page — never cite it.
5. **Operator disclosures** — SEC 10-K / 8-K / investor decks, tariffs, project pages. **SEC EDGAR
   answers 200 only to a DECLARED User-Agent** (`-A "Baird Langenbrunner research
   langenbrunner@gmail.com"`). One operator is ONE origin across all its pages and press releases.
6. **Trade and regional press** — NGI, S&P Global, Reuters, RBN, P&GJ, OGJ, LNG Prime, Natural Gas
   Intel, The Advocate / Lafourche Gazette / American Press (Lake Charles), NOLA.com, Mississippi
   Today, AL.com, Tampa Bay Times.

INDEPENDENCE, precisely. FERC's order vs the company website = TWO origins. A state order vs FERC =
TWO. A Federal Register notice of an application restates the APPLICANT's numbers. The same wire
story reposted (businesswire / prnewswire / globenewswire / seekingalpha) is the operator's origin.
Anything citing GEM is disqualified.

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
