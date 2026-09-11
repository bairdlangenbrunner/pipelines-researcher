SCOPE: US gas SLICE 2, batch A7 of 7 — WEST, ROCKIES, UPPER MIDWEST, NEW MEXICO AND CROSS-BORDER. 42
rows: Northwest Pipeline (system row + expansions), Northern Natural's Minnesota/Wisconsin
expansions (Northern Lights 2017-2025, Rochester, the Sioux Falls A-line replacement), MountainWest
(Main Line, Overthrust, Westbound Compression), Great Basin (system + four expansions), Kern River
Delta Lateral, GTN Xpress, ANR Wisconsin Reliability, REX's Colorado project, the California
utility systems (SoCalGas, PG&E, SDG&E Line 1600), the North Dakota proposals (Intensity, Tioga to
Emerson), New Mexico Permian laterals (Double E Red Hills, Agua Blanca Red Hills Interconnect, Targa
Forza, Steady Eddy), the Centra line crossing Minnesota, and cancelled western export/border
projects (Pacific Connector, WEST Header, Paso Norte, Ehrenberg-San Luis Río Colorado, Trail
West/N-MAX, Kalama Lateral). Baird chose 2026-09-10 to deep-sweep these rows with status review ON
instead of a separate in-dev pass later, so this is the ONLY pass these rows get this cycle: do the
status work and the data work together.

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
- **Operating rows:** confirm still operating (not idled, abandoned, sold, converted). A current
  tariff, PHMSA annual report or operator page dated within ~2 years is enough. A sale or rename is
  a `verdict: "change"` on the owner/name cells, not status.
- **Construction rows (P7772 NNG Northern Lights 2025, P7785 MountainWest Westbound Compression,
  P7823 Spring Creek):** in service yet? Source the date (FERC notice of commencement of service,
  operator release). Built -> `operating` + StartYear1.
- **Proposed rows:** confirm with a dated source NEWER than LastUpdated, or find the change
  (FID/construction start -> `construction` + `ConstructionYear` + `FIDStatus = FID`; built ->
  `operating`; suspended -> `shelved`; withdrawn -> `cancelled` + `ShelvedCancelledType =
  confirmed`). Past-due targets: **P2553 SDG&E Line 1600 Replacement (2024), P4455 Crow Creek (2025),
  P5727 Double E Red Hills Lateral (2023), P7857 Great Basin 2024 Expansion (no year)**. Newer
  proposals to confirm: P7782/P7783 Intensity Phases I/II, P7790 Northwest Kelso-Beaver, P7812
  Northwest Wild Trail, P7850 Targa Forza, P7858/P7859/P7860 Great Basin, P7863 REX Critical Energy
  Reliability Link.
- **Shelved row P2625 Tioga to Emerson** (`confirmed`, 2025 target): dormancy rules (shelved >= 4y with
  no news -> `stale` / `4y->cancelled`, `ShelvedCancelledType = inferred`); test for revival first.
- **Cancelled rows (P0237 Pacific Connector, P0304 WEST Header, P0382 Paso Norte, P0404
  Ehrenberg-San Luis Río Colorado, P1299 Steady Eddy, P2626 Trail West/N-MAX, P5101 Kalama Lateral,
  P7830 Double E original proposal):** is the cancellation RIGHT and SOURCED? Find the dated
  withdrawal (FERC order vacating the certificate / accepting withdrawal, sponsor announcement).
  P1299 reads `inferred` -> `confirmed` on a dated source. **P0382, P0404 and P1299 have no
  CancelledYear; P0382 and P0404 have no type** — supply them. A cancelled project REVIVED is the
  most valuable finding in the batch.

ROUTE-VS-SHEET MISMATCHES — RESEARCH THE PIPELINE, ROUTE FIRST (Baird 2026-09-10).
Where the sheet's start/end states disagree with the routes-repo geometry, do not flag and move on,
and do not assume either side is right. The route is at
`../GOIT-GGIT-pipeline-routes/data/individual-routes/gas-pipelines/<PID>.geojson` (read it:
coordinates, feature count, any properties naming a digitizing source). In order:
1. **Judge the ROUTE first.** Is it an accurate trace of THIS pipeline: right corridor, right
   termini, the right project (not the parent system, a sibling phase, or a different pipeline)?
   Check it against sourced maps (FERC/BLM alignment sheets, state siting maps, the operator's
   project map). Give the geometry's first and last coordinates in plain words in researcher_notes.
   **A multi-feature route's "first" and "last" points are in FEATURE ORDER, not flow order** — read
   the whole extent before concluding anything from the endpoints.
2. **Then decide the cells.** If the route is right and the cell is wrong -> a fills[] record on
   `Location [ref]` with `value_cols: ["StartState/Province", "EndState/Province"]` and the sourced
   states, plus an `attribution` concern with `contested: {"EndState/Province": "<state>"}`. If the
   route is wrong or stops short -> a validity concern `contested: {"RouteAccuracy": "<your
   grade>"}`, the recommendation "route candidate for §8" with the sourced termini, and the cells
   stay as sourced. Both can be wrong. Never edit a state cell to match a bad route, and never
   propose coordinates.
This batch's cases:
- **P1299 Steady Eddy Pipeline (cancelled)** — sheet start "Loving", New Mexico -> Texas, 23 mi, 24-inch.
  The route (1 feature, 8 points) runs due south along about 104.13°W from 32.27°N to 32.03°N — all in
  Eddy County, New Mexico, stopping about 3 km short of the Texas line (32.00°N). Note the name trap:
  Loving is a town in Eddy County NM AND the name of Loving County TX. Establish the project's
  termini from its filing or announcement, then decide whether the route stops short (a partial
  trace) or the end state is wrong.
- **P6898 MountainWest Main Line** — BOTH states blank, every length/diameter blank except 1,868 mi and
  2,600 MMcf/d. The route (91 features, 2,016 points) spans 111.98°W to 107.52°W and 39.1-42.0°N —
  Utah, Wyoming and Colorado; feature order runs Ogden UT (41.14°N) to central Utah (39.69°N,
  110.62°W). Source the system's states (lead: Utah, Wyoming, Colorado) and put the extent in notes.

DUPLICATES, FAMILIES, AND SYSTEM-ON-SEGMENT CAPACITY — get these right before anything else:
- **MountainWest: P6898 Main Line (2,600 MMcf/d), P6899 Overthrust (261 mi, 2,800 MMcf/d), P7785
  Westbound Compression (0 mi, 325 MMcf/d).** A segment reading MORE capacity than the mainline is
  possible (Overthrust is its own pipeline) but check each figure names its own scope. Lead:
  Williams acquired MountainWest (formerly Dominion Energy Questar Pipeline) from Southwest Gas in
  2024 — verify and stage the owner/operator.
- **Northern Natural: P2578 Northern Lights 2019, P2603 Rochester, P2734 Northern Lights 2017 (5 km),
  P3942 NL 2021, P3943 NL 2023 (Minnesota -> Wisconsin, 9 mi, five diameters), P4461 South Sioux City
  to Sioux Falls A-line Replacement (84 mi, capacity 0), P7772 NL 2025** — system row P2579 and
  P4458-P4460 are in batch A4; P7771 in A3. Each expansion's specs are its own FERC order's. A
  replacement project may add no capacity, so P4461's `0` could be right or a blank written as zero
  — source which. P2578 reads 101.41 MMcf/d: check whether that is a Dth/d figure converted.
- **Northwest Pipeline: P0230 system row, P2626 Trail West/N-MAX, P5101 Kalama Lateral, P7790
  Kelso-Beaver, P7812 Wild Trail.** P7790 and P7812 read `LengthKnown = 0` — lead: Kelso-Beaver
  replaces/adds pipe in SW Washington (verify); if new physical pipe is certificated, 0 is wrong.
- **Great Basin: P7856 Main Line (900 mi, no capacity), P7857 2024 Expansion, P7858 Gabbs Lateral NASF
  Relocation, P7859 2026 Expansion (8.13 MMcf/d), P7860 2028 Expansion (0 mi, 1,250 MMcf/d).** 1,250
  MMcf/d on a system whose mainline has no stated capacity is implausible — lead: a Dth/d figure, or
  the 2028 expansion's number is misread. Source it with units. Owner: lead is Southwest Gas
  Holdings' pipeline subsidiary — verify.
- **Double E: P5727 Red Hills Lateral here; P0061 mainline swept in slice 1; P7830 "Original Proposal
  (Oil Pipeline)" (cancelled 2011).** P7830 is a GAS-tracker row describing an oil proposal: decide
  its place IN THE GAS TRACKER (is it a genuine earlier gas-line proposal, a precursor that belongs
  in notes on P0061, or not a gas pipeline at all -> `validity` concern). **Do NOT research, stage or
  propose anything for the oil tracker** — oil is out of scope this cycle.
- **Targa Red Hills cluster: P7109 Agua Blanca "Targa Red Hills Interconnect" (EVERY spec blank) and
  P7850 Targa Forza (from the Red Hills plant, NM -> Texas, 36 mi, 36-inch).** Agua Blanca's other
  rows are P2498 (A4) and P2499 (slice 1); Targa's P7851/P7852 (A4) and P7853/P7854 (A3). Establish
  what P7109 physically is before sourcing specs, and whether any of these describe the same pipe.
- **P3856 Kern River Delta Lateral** (system row P0207 swept). **P3171 GTN Xpress** (system P0231
  swept): compression-only 0 km — confirm. **P5547 ANR Wisconsin Reliability** (ANR rows across
  batches). **P7863 REX CERL** (REX rows swept in slice 1). **P2553 Line 1600 Replacement** (P2552
  Line 1600 swept in slice 1) — reads 0 km with Diameter 36: internally inconsistent; source which.
- **P7782 / P7783 Intensity Phase I and Phase II** — each phase's specs are its own.

CELLS THAT LOOK WRONG — check each with a source, don't just "fix":
- **Whitespace:** P6233 StartState `California ` and P6250 StartState `California ` (trailing space);
  P6250 PipelineName `Pacific Gas & Electric Pipeline ` (trailing space). Stage the trimmed value as a
  `validity` concern with `contested` naming the column; cite nothing new for a whitespace fix.
- **P6233 SoCalGas** (3,640 mi, 3,725 MMcf/d, Diameter 36) and **P6250 PG&E** (7,000 mi, Diameter 30) are
  SYSTEM rows: a single diameter on a utility system is the largest line at best. Source the system
  mileage (CPUC, PHMSA annual reports) and say what the diameter represents.
- **P7125 Centra Pipeline** — Spruce Siding, Manitoba -> Fort Frances, Ontario, 270 km, capacity
  `65000 Mcf/d`. It is in the US slice because the line crosses northern Minnesota (lead: the US
  segment is "Centra Pipelines Minnesota"). Keep the sheet's units; note MMcf/d in researcher_notes.
- **P0382 Paso Norte** (NM -> Chihuahua) and **P0404 Ehrenberg-San Luis Río Colorado** (AZ -> Sonora):
  cross-border. The US border crossing needs a FERC Section 3 authorization / Presidential Permit —
  a good dated source for both existence and cancellation.

LENGTHS AND UNITS. Mixed mi/km; read YOUR row's `LengthKnownUnits` before writing a number. Rows with
`LengthKnown = 0` (P2553, P3171, P7785, P7790, P7812, P7860) are compression/meter scopes if the
source says so: expansion with no new physical pipe -> `LengthKnown = 0`, Diameter blank is the RULE
— confirm the scope, don't "fix". Where a 0-length row carries a diameter (P2553), one of them is wrong.

OWNERSHIP. Leads to verify, not answers: Williams (Northwest Pipeline, MountainWest), Berkshire
Hathaway Energy (Northern Natural, Kern River), TC Energy (GTN, ANR), Tallgrass (REX — verify
current ownership), Southwest Gas (Great Basin; Spring Creek), SoCalGas / SDG&E (Sempra), PG&E,
WhiteWater and partners (Double E, Agua Blanca), Targa, Intensity Infrastructure Partners, Centra
Gas Manitoba (Manitoba Hydro), Pembina / Veresen (Pacific Connector), Northwest Innovation Works
(Kalama). A disputed CURRENT owner is an `attribution` concern with `contested` naming `Owner1` /
`Owner2%` / `Operator`; owner/operator work stages onto the `Gas_OperatorsOwners` tab.

THE SOURCE LADDER (in this order):
1. **FERC** — `elibrary.ferc.gov` and the CP docket: the ORDER states mileage by county, diameter,
   capacity, cost, in-service requirement; notices of commencement of service date StartYear;
   orders vacating / accepting withdrawal date cancellations. The applicant's filing and FERC's order
   restating the applicant's numbers are ONE origin; say which document you cite.
2. **State regulators and land agencies** — California PUC (SoCalGas/SDG&E/PG&E system facts, Line
   1600 decisions), Public Utilities Commission of Nevada, Utah PSC, Wyoming PSC, Colorado PUC,
   Washington UTC and EFSEC, Oregon PUC and DEQ, Minnesota PUC, North Dakota PSC (Intensity and
   Tioga-Emerson siting), New Mexico PRC and Oil Conservation Division, Texas RRC (for the Texas ends
   of the Permian laterals); **BLM** NEPA documents for rights-of-way on federal land (ePlanning).
3. **PHMSA / NPMS** — `www.npms.phmsa.dot.gov` (200); PHMSA annual report data for operator mileage.
4. **EIA** — the Natural Gas Pipeline Projects workbook
   — **every release from May 2018 on is already on disk** in
   `sources/eia_pipeline_projects/raw/` (`raw/vintages.csv` gives each file's origin URL;
   `sources/eia_pipeline_projects/NOTES.md` the quirks). Read the local workbooks — do NOT
   re-download, and never cite the undated `EIA-NaturalGasPipelineProjects.xlsx`, which changes
   every quarter. Cite the DATED release
   URL that states the value, with the sheet and Excel row in `note`. EIA's `data.php` is a navigation page — never cite it.
   Canada's **Canada Energy Regulator** covers the Canadian side of P7125 and P2625.
5. **Operator disclosures** — SEC 10-K / 8-K / investor decks, project pages. **SEC EDGAR answers 200
   only to a DECLARED User-Agent** (`-A "Baird Langenbrunner research langenbrunner@gmail.com"`). One
   operator is ONE origin across all its pages and press releases.
6. **Trade and regional press** — NGI, S&P Global, Reuters, RBN, P&GJ, E&E News, Utility Dive, Natural
   Gas Intel; regional: Oregonian / OPB, Bismarck Tribune, Star Tribune, Salt Lake Tribune, Nevada
   Independent, Carlsbad Current-Argus, Albuquerque Journal, San Diego Union-Tribune.

INDEPENDENCE, precisely. FERC's order vs the company website = TWO origins. A state order vs FERC =
TWO. A BLM decision vs FERC = TWO (separate agencies, separate records). A Federal Register notice of
an application restates the APPLICANT's numbers. The same wire story reposted is the operator's
origin. Anything citing GEM is disqualified.

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
