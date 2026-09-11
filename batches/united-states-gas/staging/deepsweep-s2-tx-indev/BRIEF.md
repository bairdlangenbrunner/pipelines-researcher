SCOPE: US gas SLICE 2, batch A3 of 7 — TEXAS IN-DEVELOPMENT. 40 rows: 23 proposed, 8 construction,
9 cancelled. The Permian-to-Gulf egress buildout (Hugh Brinson, Blackcomb, Eiger Express, Traverse,
Trident, Apex, DeLa Express, Saguaro, the Targa extensions), the LNG feed lines (Rio Bravo for Rio
Grande LNG, CP Express for CP2, Port Arthur's Texas and Louisiana Connectors, Sabine Crossing, ADCC,
Freeport LNG), and a set of cancelled Permian projects (Pecos Trail, Permian Global Access, Bluebonnet,
Permian Pass, Gemini Gulf Coast, Roadrunner Phase 3). Baird chose 2026-09-10 to deep-sweep these rows
with status review ON instead of a separate in-dev pass later, so this is the ONLY pass these rows get
this cycle: do the status work and the data work together.

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
- **Construction rows (P2643, P3589, P3885, P3886, P4453, P7828, P7853, P7854):** the question is
  whether each is NOW IN SERVICE. **P2643 Delaware Link** (LastUpdated 2023-08, 2023 target) and
  **P4453 Oasis Modernization** (2022-10, 2022 target) are very likely operating — source the date.
  The rest have 2026-2028 targets: confirm construction is underway, or find the early start-up or
  the delay. An in-service announcement, a Texas RRC T-4 permit/completion, or the EIA project
  workbook's in-service date -> verdict `change` to `operating` with `StartYear1`.
- **Proposed rows:** confirm with a dated source NEWER than LastUpdated, or find the change
  (FID/construction start -> `construction` + `ConstructionYear` + `FIDStatus = FID`; suspended ->
  `shelved`; withdrawn -> `cancelled` with `ShelvedCancelledType = confirmed`). Stale rows: P3682
  Whistler Midland Lateral Extension (2022-10), P4379 ADCC (2023-07), P3666 Freeport LNG Terminal
  Pipeline (2023-08), P3667 / P3969 Valley Crossing (2023-08). **P4379 ADCC** fed Corpus Christi
  Stage 3 — lead: it may be built; source it. Several 2025-10 rows are fresh; still confirm them.
  **LNG-feed pipelines follow their terminal** (Rio Grande, CP2, Port Arthur, Sabine Pass, Freeport,
  Texas LNG): a terminal's FID or cancellation is strong evidence, but it is the TERMINAL's evidence.
  State in researcher_notes whether the source speaks to the pipeline itself.
- **Cancelled rows (P0289, P0320, P0327, P1317, P2582, P2602, P3160, P3294):** the question is
  whether the cancellation is RIGHT and SOURCED, not whether it is dormant. Find the dated
  withdrawal (sponsor announcement, a 10-K dropping it, press): that is the `Cancelled [ref]`.
  Check CancelledYear against it. Rows reading `inferred` (P0289, P0327, P2582, P2602) become
  `confirmed` on a dated, sourced cancellation (verdict `change` with proposed_changes
  `{"ShelvedCancelledType": "confirmed", "CancelledYear": "<yyyy>"}`). P1317 Gemini Gulf Coast and
  P3160 Concho-Progreso have NO CancelledYear or type — supply both. A "cancelled" project that was
  actually BUILT (or revived under a new name — Permian egress projects were often re-scoped and
  re-announced) is the most valuable finding here: name the successor and its GEM PID if it has one.
  A cancelled row still needs its specs sourced AS PROPOSED.

ROUTE-VS-SHEET MISMATCHES — RESEARCH THE PIPELINE, ROUTE FIRST (Baird 2026-09-10).
Where the sheet's start/end states disagree with the routes-repo geometry, do not flag and move on,
and do not assume either side is right. The route is at
`../GOIT-GGIT-pipeline-routes/data/individual-routes/gas-pipelines/<PID>.geojson` (read it:
coordinates, feature count, any properties naming a digitizing source). In order:
1. **Judge the ROUTE first.** Is it an accurate trace of THIS pipeline: right corridor, right
   termini, the right project (not the parent system, a sibling segment, or a different pipeline)?
   Check it against sourced maps (FERC EIS/EA alignment sheets and county lists, the operator's
   project map, Texas RRC permit maps). Give the geometry's first and last coordinates in plain
   words in researcher_notes.
2. **Then decide the cells.** If the route is right and the cell is wrong -> a fills[] record on
   `Location [ref]` with `value_cols: ["StartState/Province", "EndState/Province"]` (and the
   Start/EndLocation cells where they are wrong too) with the sourced values, plus an `attribution`
   concern with `contested: {"EndState/Province": "<state>"}`. If the route is wrong -> a validity
   concern `contested: {"RouteAccuracy": "<your grade>"}`, the recommendation "route candidate for
   §8" with the sourced termini, and the cells stay as sourced. Both can be wrong. Never edit a
   state cell to match a bad route, and never propose coordinates.
This batch's cases:
- **P3198 Port Arthur Pipeline — Texas Connector** — sheet Jefferson County TX -> St Landry Parish
  LA (31 mi). The route (30 pts) lies entirely in the Jefferson/Orange County, Texas area, from about
  30.08°N to the Port Arthur terminal near 29.80°N. **P0241 Louisiana Connector (72 mi) carries the
  IDENTICAL start/end cells**, so the likeliest story is that the system's end-to-end termini were
  copied onto both segment rows. Settle each segment's own termini from the FERC order (CP docket
  for Port Arthur Pipeline) and stage per-segment Location fills if the cells are wrong. P0241 has no
  route mismatch in the audit, but its cells need the same check — do both rows together (one
  subagent's findings go in the other's `cross_row_leads`).
- **Mustang Express P7834 Mainline / P7835 Cougar Lateral / P7836 Golden Triangle-Spindletop Storage
  Lateral, and P7837 Eiger Express** — all four have BOTH state cells blank and no start/end
  locations. Routes: P7834 from about Katy (29.81°N, 95.88°W) east to the Port Arthur area (29.79°N,
  93.95°W); P7835 from Wharton/Colorado County (29.47°N, 96.63°W) to the P7834 start near Katy; P7836 a
  3-point, ~4 mi line near Beaumont/Spindletop (30.03°N, 94.1°W); P7837 from the Pecos/Reeves County
  area (31.26°N, 103.09°W) to about Katy. Grade each route against the sponsor's announced route,
  then source the locations and states.
- Blank states, no route: P3666, P3667, P3682, P3969 (both blank); P2582, P2602, P2643, P3589, P4453,
  P5664, P5905, P7771, P7798, P7811, P7840, P7853, P7854, P7862 (start or end location blank). Source
  what the documents give you; states are the owed unit, locations when stated.
- **Whitespace:** P7853 and P7854 both read EndState `"Texas "` (trailing space). Stage the trimmed
  `Texas` in the Location fill with the source that places the terminus.

DUPLICATES AND FAMILIES — get these right before anything else:
- **Port Arthur (Sempra): P0241 Louisiana Connector and P3198 Texas Connector here;** P3197
  Louisiana Connector Amendment and P3590 Louisiana Connector Extension (shelved) are in batch A1.
  Four rows, one project family. Decide what each physically is; a system figure (2,000 MMcf/d,
  42-inch) is a ref for a segment row only if the source says it applies to that segment.
- **Saguaro Connector: P5664 Main Line (155 mi, 2,800 MMcf/d) and P7822 Lateral (0.10 mi, 2,800
  MMcf/d, ending in Chihuahua).** A 0.1-mile lateral carrying the mainline's full capacity is
  suspect: check whether P7822 is really the border crossing, what its own capacity is, and whether
  the Mexican side is someone else's pipeline. Mainline figures are not refs for the lateral.
- **Mustang Express, 3 rows (P7834/P7835/P7836)** — mainline figures are not refs for laterals.
- **P5905 "Matterhorn Express | Blackfin Pipeline"** — lead: Blackfin may be its OWN project (a
  separate Permian-to-Gulf line, possibly by a different sponsor group) filed under Matterhorn's
  PipelineName. If so, file an `attribution` concern naming the correct pipeline name and owners.
  Matterhorn Express itself (P3882) is in batch A4.
- **Valley Crossing: P3667 Capacity Expansion (0 mi, 720 MMcf/d) and P3969 Texas LNG Lateral
  Extension (10 mi, capacity blank but units `MMcf/d`)** — two proposed rows on Enbridge's Valley
  Crossing (system row P0276 swept in slice 1). Test whether they are the same Texas LNG feed
  project described twice. P3969's orphan `CapacityUnits` needs a value or a note.
- **Targa: P7853 Buffalo Run Extension and P7854 Bull Run Extension (construction)** here; P7851 /
  P7852 are in batch A4 and P7850 in A7.
- **DeLa Express (P6531, Moss Bluff LA) is NOT Delta Express (P2737, batch A1, Venture Global).**
  Do not cross-cite.
- **Cancelled Permian projects vs successors:** Permian Global Access (P0320, Waha -> Gillis) and
  Permian Pass (P2582, TX -> LA) and Bluebonnet (P0327, Waha -> Katy) have near-identical corridors
  to live projects in this batch (DeLa Express, Eiger Express, Trident, Apex). A re-announcement
  under a new name is a `duplicate`/`status` finding only with a document saying so; similar
  corridors alone are not.
- Singletons on systems in other batches (context, not refs): P3886 GCX Capacity Expansion (GCX
  mainline P0378 in A4), P3682 Whistler Midland Lateral (Whistler rows in A4), P2602 Roadrunner
  Phase 3 (Phases 1-2 in A4), P4453 Oasis Modernization (Oasis P0234 swept in slice 1), P7771 NNG
  Tarzan Compressor (NNG rows in A4/A7), P7840 Transwestern Desert Southwest (Transwestern P0273
  swept in slice 1), P7862 Producers Midstream Palo Duro (P7861 in A4).

LENGTHS AND UNITS. Mixed mi/km; read YOUR row's `LengthKnownUnits` before writing a number. Rows with
`LengthKnown = 0` (P2602, P3667, P3886, P4453, P7771) are compression/modernization scopes: expansion
with no new physical pipe -> `LengthKnown = 0`, Diameter blank is the RULE — confirm the scope, don't
"fix". P2602 Roadrunner Phase 3 reads 0 km but Diameter 30 — check whether Phase 3 was compression
(then Diameter should be blank) or pipe (then the length is wrong).

OWNERSHIP. Leads to verify, not answers: Energy Transfer (Hugh Brinson, Mustang Express?, Gemini Gulf
Coast?, Transwestern — check each), Enbridge (Rio Bravo, Valley Crossing), Kinder Morgan (GCX,
Trident, Permian Pass), WhiteWater with partners (Matterhorn, Blackcomb, Traverse, Eiger Express —
verify each), Venture Global (CP Express), Sempra (Port Arthur), Targa, Northern Natural (Berkshire
Hathaway Energy), ONEOK/EnLink or Williams (verify for each Permian row). Where a lead above carries a
`?`, it is a guess — source it or leave it out. A disputed CURRENT owner is an `attribution` concern
with `contested` naming `Owner1` / `Owner2%` / `Operator`; owner/operator work stages onto the
`Gas_OperatorsOwners` tab.

THE SOURCE LADDER (in this order):
1. **FERC** — `elibrary.ferc.gov` and the CP docket, for INTERSTATE or LNG-certificated lines only
   (Rio Bravo, CP Express, Port Arthur connectors, Sabine Crossing, Transwestern, NNG). The ORDER
   states mileage by county, diameter, capacity, cost, in-service requirement. The applicant's filing
   and FERC's order restating the applicant's numbers are ONE origin; say which document you cite.
2. **Texas Railroad Commission** — most rows here are INTRASTATE, so FERC silence is EXPECTED. RRC
   T-4 permits (pipeline permit number, operator, size), the RRC pipeline GIS/public viewer data, and
   RRC press. Cite a specific permit or document page, never the search form.
3. **PHMSA / NPMS** — `www.npms.phmsa.dot.gov` (200).
4. **EIA** — the Natural Gas Pipeline Projects workbook
   — **every release from May 2018 on is already on disk** in
   `sources/eia_pipeline_projects/raw/` (`raw/vintages.csv` gives each file's origin URL;
   `sources/eia_pipeline_projects/NOTES.md` the quirks). Read the local workbooks — do NOT
   re-download, and never cite the undated `EIA-NaturalGasPipelineProjects.xlsx`, which changes
   every quarter. It is the
   likely answer for in-service years, capacities and costs on most project rows here. Cite the DATED release
   URL that states the value, with the sheet and Excel row in `note`. EIA's `data.php` is a navigation page — never cite it.
5. **Operator disclosures** — SEC 10-K / 8-K / investor decks, FID and open-season announcements,
   project pages. **SEC EDGAR answers 200 only to a DECLARED User-Agent** (`-A "Baird Langenbrunner
   research langenbrunner@gmail.com"`). One operator is ONE origin across all its pages and press
   releases; a JV partner's own release is a SEPARATE origin only if it states the figure itself.
6. **Trade and regional press** — NGI, S&P Global, Reuters, RBN, P&GJ, OGJ, Hart Energy, Midland
   Reporter-Telegram, Houston Chronicle, San Antonio Express-News, Beaumont Enterprise, Corpus
   Christi Caller-Times.

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
length in the sheet's units for your row. Mexican states are spelled as the sheet spells them
(`Nuevo León`, `Chihuahua`). No recon legs run for US gas.
