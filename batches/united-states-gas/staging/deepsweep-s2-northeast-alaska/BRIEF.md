SCOPE: US gas SLICE 2, batch A6 of 7 — NORTHEAST / APPALACHIAN OPERATING + ALASKA. 42 rows in two very
different halves:
- **Lower 48 (22 rows):** Texas Eastern segments (OPEN, TEAM 2012/2014/2021, TEAL, Middlesex),
  Equitrans segments, National Fuel, Mountain Valley, Algonquin (Access Northeast, Atlantic Bridge,
  Project Maple), Maritimes & Northeast, Mountaineer, ANR Alberta Xpress, Adelphia, NJNG Southern
  Reliability Link, Western Massachusetts.
- **Alaska (20 rows):** the North Slope export and in-state proposals (AKLNG, ASAP, Alaska Pipeline
  Project, Denali, Arctic Fox, Point Thomson, Donlin Gold) and the operating Cook Inlet / North Slope
  systems (Kenai-Beluga, Tyonek, Kenai-Anchorage, Anchorage system, Nuiqsut, Northstar, the Kuparuk
  fuel-gas line).
Baird chose 2026-09-10 to deep-sweep these rows with status review ON instead of a separate in-dev
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
    segment row, a navigation page, a terminus page) -> the cell is effectively UNCITED: find the
    document that does state it and stage it as REFS_ADDED; if nothing states it, UNRESOLVED
    saying so. Keep the old ref in `researcher_notes`, never silently dropped.
  - Confirmed 404/410 -> `class_out: "DEAD_LINK"` with the Wayback capture if one exists, plus a
    replacement source. A 403/timeout/WAF is NOT dead — never retire a ref over an access failure.
  - The source DISAGREES with the recorded value -> stage the sourced value AND a `spec` concern.
- Where one document re-verifies several HAS_REF cells, say so once and stage it on each.

STATUS REVIEW IS ON FOR EVERY ROW (one status_reviews object per row).
- **Operating rows:** confirm the row is still operating (not idled, abandoned, sold to a new
  operator, or converted). A current tariff, PHMSA annual report or operator page dated within ~2
  years is enough. A sale or rename is a `verdict: "change"` on the owner/name cells, not status.
- **Proposed rows (P0147 AKLNG, P2526 Donlin Gold, P5545 Western Massachusetts, P6011 Project Maple,
  P6534 Point Thomson):** confirm with a dated source NEWER than LastUpdated, or find the change.
  Leads to verify, not answers: Glenfarne took over AKLNG in 2025 and split it into phases (an
  in-state pipeline first, the LNG plant later) — look for a phase-1 FID and what scope it covers;
  the Donlin Gold row's 2024 target is past; Project Maple is an Enbridge (Algonquin + Maritimes)
  2025 proposal.
- **Shelved row P0293 Alaska Stand Alone Pipeline (ASAP)** — reads shelved `confirmed` with a 2025
  target. Lead: ASAP's in-state line and AKLNG's pipeline converged (same corridor, AGDC as sponsor).
  If ASAP has been folded into AKLNG's phase 1, say so with the document — that is a `duplicate`
  / `validity` question between P0293 and P0147, not a status tweak.
- **Cancelled rows (P0144 Access Northeast, P0146 Alaska Pipeline Project, P0174 Denali, P0300 Arctic
  Fox):** is the cancellation RIGHT and SOURCED? Find the dated withdrawal (FERC notice of
  withdrawal of pre-filing, sponsor announcement). P0300 reads `inferred` -> `confirmed` on a dated
  source. Check each CancelledYear against its document; supply it where blank. A cancelled project
  REVIVED is the most valuable finding: test whether **P6011 Project Maple** re-scopes **P0144 Access
  Northeast** (both Algonquin expansions into New England) — if it does, name the relationship; the
  cancelled row stays cancelled unless the same project was revived.

ROUTE-VS-SHEET MISMATCHES — RESEARCH THE PIPELINE, ROUTE FIRST (Baird 2026-09-10).
Where the sheet's start/end states disagree with the routes-repo geometry, do not flag and move on,
and do not assume either side is right. The route is at
`../GOIT-GGIT-pipeline-routes/data/individual-routes/gas-pipelines/<PID>.geojson` (read it:
coordinates, feature count, any properties naming a digitizing source). In order:
1. **Judge the ROUTE first.** Is it an accurate trace of THIS pipeline: right corridor, right
   termini, the right project (not the parent system, a sibling phase, or a different pipeline)?
   Check it against sourced maps (FERC EA alignment sheets and county/milepost lists, the operator's
   project map). Give the geometry's first and last coordinates in plain words in researcher_notes.
   **A multi-feature route's "first" and "last" points are in FEATURE ORDER, not flow order** — read
   the whole extent before concluding anything from the endpoints.
2. **Then decide the cells.** If the route is right and the cell is wrong -> a fills[] record on
   `Location [ref]` with `value_cols: ["StartState/Province", "EndState/Province"]` and the sourced
   states, plus an `attribution` concern with `contested: {"StartState/Province": "<state>"}`. If
   the route is wrong -> a validity concern `contested: {"RouteAccuracy": "<your grade>"}`, the
   recommendation "route candidate for §8" with the sourced termini, and the cells stay as sourced.
   Both can be wrong. Never edit a state cell to match a bad route, and never propose coordinates.
3. **Expansion projects are mostly loops and compressor stations scattered along a mainline.** The
   state cells record where THIS project's facilities are, from the FERC order. A route that traces
   the mainline between the first and last facility overstates the project.
This batch's cases:
- **P0260 TETCO TEAM 2014** — sheet Uniontown PA -> Lambertville NJ, 34 mi, 36-inch. The route is 28
  OSM features, 2,867 points, spanning 84.4°W to 75.0°W and 38.3-40.5°N — far wider than 34 mi of
  loop; it looks like a stretch of the TETCO mainline system, not the TEAM 2014 loops. First feature
  starts in the West Virginia panhandle (39.85°N, 80.81°W), last ends in southwestern Pennsylvania
  (39.93°N, 79.67°W). Grade it against TEAM 2014's certificated loops (lead: several Pennsylvania
  loops plus compression, with Lambertville NJ a compressor/meter location — verify). The sheet's end
  state NJ is right only if a TEAM 2014 facility is there.
- **P5832 TETCO TEAM 2012** — sheet West Virginia -> Pennsylvania, 17.3 mi, 36-inch; the route (7
  OSM features) lies entirely in Pennsylvania, 39.88-39.98°N from the southwestern corner (80.52°W) to
  south-central PA (77.0°W). Source where TEAM 2012's loops were and whether any facility was in West
  Virginia.
- **P4454 Equitrans Ohio Valley Connector Expansion (OVCX)** — sheet Ohio -> Ohio, 6 mi, "12, 24";
  the route (1 feature, properties name "Ohio Valley Connector Expansion", State "PA, WV, OH") lies
  entirely in Wetzel County, West Virginia (39.54-39.56°N, about 80.50-80.54°W) — right where the
  **P6897 Ohio Valley Connector** route ends. Source what OVCX built (pipe vs compression) and where;
  both the route and the Ohio/Ohio cells are in question.
- **P6878 NFG Supply Main Line, P6895 Equitrans Mainline, P6897 Ohio Valley Connector** — BOTH
  states blank. Routes: P6878 140 features across Pennsylvania into New York (to 43.2°N); P6895 West
  Virginia (39.56°N, 80.55°W) to Pennsylvania (40.30°N, 79.91°W), extent to 38.9°N; P6897 Ohio (39.82°N,
  80.88°W) to West Virginia (39.56°N, 80.55°W). Source the states; for the two system rows, record
  the extent (states crossed) in researcher_notes too.

DUPLICATES, FAMILIES, AND SYSTEM-ON-SEGMENT CAPACITY — get these right before anything else:
- **Equitrans P6895 Mainline, P6896 "Allenghy" Valley Connector, P6897 Ohio Valley Connector** all read
  **4,400 MMcf/d** — the same number on three segments of different sizes is almost certainly one
  system figure copied onto each. Source each segment's own capacity; a system aggregate on a
  segment row is a `spec` concern. **P6878 NFG Main Line also reads 4,400 MMcf/d and 1,800 mi** —
  check it isn't the same copied number, and source NFG Supply's own mileage/capacity. P6896's name
  is misspelled: `Allegheny`.
- **Mountain Valley: P0220 mainline and P4456 Greene Interconnect Project (0 mi, 1,000 MMcf/d, every
  location blank)** here; **P2567 Southgate and P7829 Interconnect Expansion (0 mi, 350 MMcf/d)** are
  in batch A5. Establish what P4456 physically is (an interconnect at MVP's Greene County PA/WV end?)
  and whether P4456 and P7829 describe the same scope; if so, `duplicate` naming both.
- **Texas Eastern segments: P0235 OPEN, P0260 TEAM 2014, P0261 TEAL, P2562 Middlesex, P5832 TEAM 2012,
  P5835 TEAM 2021** (system row P0262 in A4; P7813 TEAM III in A5). Each project's specs are its own;
  never cite the system's capacity on a segment. P0261 TEAL reads 5 mi but 950 MMcf/d and "30, 36" —
  TEAL was an Ohio lateral plus loop (lead); check both. P5835 TEAM 2021 reads 1 mi, 30-inch, 18 MMcf/d.
- **Algonquin: P0144 Access Northeast, P6011 Project Maple (every location blank), P7820 Atlantic
  Bridge Phase I (6 mi, 40 MMcf/d), P7821 Phase II (0 mi, 93 MMcf/d)** — system rows P0149/P0150 were
  swept in slice 1. Atlantic Bridge's two phases: lead is ~132 MMcf/d total with the Weymouth MA
  compressor the late piece. Source the split.
- **NFG: P2537 FM100, P6878 Main Line** (P7827 Tioga Pathway in A5).
- **Mountaineer: P2009 Phase III (Eastern Panhandle Expansion)** — reads **4,750 MMcf/d on 3.4 mi of
  8-inch**: impossible as written. Lead: the figure is in Dth/d or Mcf/d. Source the capacity and its
  unit; the start state "Maryland, Pennsylvania" also needs a source (lead: the TransCanada/Columbia
  Eastern Panhandle Expansion tapped Columbia's line near the MD/PA border — verify).
- **Alaska name collisions — rows that may be the same pipe:** P7450 "Kenai Beluga Pipeline | Beluga
  Pipeline" (Beluga -> Old Tyonek, 16.2 mi) vs **P7458 "Beluga Pipeline"** (Beluga -> Anchorage, 101.4
  mi, 20-inch, 1984); P7453 "Kenai Nikiski Pipeline" vs **P7461 Tyonek Gas Pipeline** (Nikiski ->
  Beluga, 50.7 mi, 1968) and **P7455 Cook Inlet Gas Gathering System** (Tyonek area -> Nikiski area);
  P7454 Kenai Kachemak vs P7456 Kenai-Anchorage. Map each row to one physical pipeline from the
  Alaska DNR State Pipeline Coordinator's right-of-way list or the RCA tariff before sourcing specs;
  a real overlap is a `duplicate` on both PIDs.
- **P7465 "Trans-Alaska Gas Pipeline"** (Kuparuk Operations Center -> TAPS Pump Station 4, 149 mi,
  "8, 10", 1977) — lead: this is the fuel-gas line feeding the TAPS pump stations, not the proposed
  1970s-80s Alaska gas export line of a similar name. Confirm what it is and whether it still runs
  (TAPS pump stations have been shut down over time).
- **AKLNG family: P0147 AKLNG, P0293 ASAP, P6534 Point Thomson Unit Gas Transmission Pipeline (63 mi,
  32-inch — lead: this was AKLNG's PTU gas transmission line in the FERC application).** Sort out
  which rows are components of which; a component row filed separately is fine, a row restating
  the whole is not.
- **P0146 Alaska Pipeline Project (TransCanada/ExxonMobil) and P0174 Denali (BP/ConocoPhillips)** — two
  distinct competing Alaska Highway projects; the shared 4,500 MMcf/d is fine if each source states it.

CELLS THAT LOOK WRONG — check each with a source, don't just "fix":
- **P7463 Northstar Gas Pipeline** reads Diameter `10.15` — lead: two diameters ("10, 15") or a
  decimal-comma artifact. Source it.
- **P0212 Maritimes & Northeast** reads start Goldboro, Nova Scotia; lead: since Sable/Deep Panuke
  production ended, flow is supplied from New England/Canada differently — the physical start is
  unchanged, so don't move it, but record current flow direction in researcher_notes if sourced.
- **P2501 ANR Alberta Xpress** reads Michigan -> Louisiana at 0 km: a compression-only scope, so 0
  is right if sourced — confirm, and source the states (ANR's Southeast mainline facilities).
- **P0174 Denali** reads StartYear1 2020 and CancelledYear 2011 — planned-vs-cancelled, fine if
  sourced. **P0146** — check its CancelledYear against the dated end of the project.

LENGTHS AND UNITS. Mixed mi/km; read YOUR row's `LengthKnownUnits` before writing a number. Rows
with `LengthKnown = 0` (P2501, P4456, P7821) are compression/meter scopes: expansion with no new
physical pipe -> `LengthKnown = 0`, Diameter blank is the RULE — confirm the scope, don't "fix".

OWNERSHIP. Leads to verify, not answers: Enbridge (Texas Eastern, Algonquin, Maritimes & Northeast
with partners), EQT (acquired Equitrans in 2024 — Equitrans rows and MVP's operator), MVP's
partners (NextEra, Con Edison, AltaGas/WGL, RGC), National Fuel, TC Energy (ANR, Columbia),
Mountaineer Gas (UGI sold it — verify to whom), Adelphia Gateway (New Jersey Resources), NJNG, the
Western Massachusetts project's utility, Glenfarne and AGDC (AKLNG, ASAP), Hilcorp and Harvest
Alaska (Cook Inlet and North Slope lines), ENSTAR (Kenai-Anchorage, Anchorage system). A disputed
CURRENT owner is an `attribution` concern with `contested` naming `Owner1` / `Owner2%` / `Operator`;
owner/operator work stages onto the `Gas_OperatorsOwners` tab.

THE SOURCE LADDER (in this order):
1. **FERC** — `elibrary.ferc.gov` and the CP docket: the ORDER states mileage by county, diameter,
   capacity, cost, in-service requirement; notices of commencement of service date StartYear.
   AKLNG is FERC docket CP17-178 (EIS, order 2020); ASAP had a US Army Corps SEIS. The applicant's
   filing and FERC's order restating the applicant's numbers are ONE origin; say which you cite.
2. **Alaska agencies** — the Regulatory Commission of Alaska (tariffs, certificates for Cook Inlet
   and North Slope carriers), the Alaska DNR **State Pipeline Coordinator's Section** (right-of-way
   leases and pipeline lists with length/diameter), AGDC board materials and reports, the Alaska
   Legislature's gasline analyses (Legislative Budget & Audit, Legislative Research). **Northeast
   agencies** — Massachusetts EFSB and DPU, NJ BPU and DEP, PA PUC and DEP, NY PSC, WV PSC, Ohio
   Power Siting Board.
3. **PHMSA / NPMS** — `www.npms.phmsa.dot.gov` (200); PHMSA annual report data for operator mileage.
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
6. **Trade and regional press** — NGI, S&P Global, Reuters, RBN, P&GJ, E&E News, Utility Dive; Alaska:
   Anchorage Daily News, Alaska Journal of Commerce, Alaska Beacon, Petroleum News (`petroleumnews.com`),
   KTOO/Alaska Public Media; Northeast: Boston Globe, CommonWealth Beacon, Pittsburgh Post-Gazette,
   NJ Spotlight, Charleston Gazette-Mail.

INDEPENDENCE, precisely. FERC's order vs the company website = TWO origins. An Alaska DNR lease vs
the operator's RCA tariff = TWO. AGDC and the State of Alaska are ONE origin for AKLNG/ASAP (AGDC is
a state corporation); Glenfarne is a separate origin. A Federal Register notice of an application
restates the APPLICANT's numbers. The same wire story reposted is the operator's origin. Anything
citing GEM is disqualified.

EXISTENCE / DUPLICATE FLAGS — the bar is high. (a) Name the document you tested and what it does
and does not contain. (b) Read maps, not just text. (c) Segment-vs-network: an aggregate restated on
a segment row is a `spec` defect, but the segment exists. (d) A proposed project "exists" if it was
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
- Pressure: a FERC order, RCA tariff or DNR lease states MAOP for many lines; look, don't force.
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
