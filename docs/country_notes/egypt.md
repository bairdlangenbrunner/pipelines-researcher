# Egypt — country notes

MENA deep-coverage country (GGIT gas focus so far). Gas packet legs:

- **In-dev status sweep (Leg A)** — delivered `pipelines_batch_20260709_0724_ET_egypt-gas_annual-indev.xlsx` (7 in-dev rows).
- **Operating deep sweep (Leg C)** — delivered `pipelines_batch_20260713_1319_ET_egypt-gas_deepsweep.xlsx` (50 operating rows). Fan-out ran on Sonnet.
- **Discovery (Leg B)** — delivered `pipelines_batch_20260715_1552_ET_egypt-gas_discovery.xlsx`
  (7-candidate queue fully vetted → 4 new rows / 3 monitor; the 07-09 shards were
  independently re-vetted at delivery, one downgraded). See "Discovery (Leg B)" below.
- **Sheet↔wiki↔route QC legs (handoff-packet pilot, researcher onboarding; workflows.md §6)** — delivered
  `pipelines_batch_20260715_1442_ET_egypt-gas_qc.xlsx` (57 rows; staging
  `batches/egypt-gas/staging/qc/`): 12-row `Gas_Existence` tracking review (5 existence
  + 7 duplicate concerns carried from the prior staged packets — read first), 152 wiki
  diffs (77 WIKI_UPDATE / 67 SHEET_SUSPECT / 7 stale-vs-staged / 1 UNPARSED = P7864, no
  Wiki URL), 13 route length-ratio flags (11 already staged-annotated), 63 mechanical
  flags (incl. 38 `Existence_support` thin-ref flags, ALL covered by the prior
  existence audit), 14-row Leg-3 research → 21 validity + 10 fills.
  See "Open items — QC packet" below.
- **Handoff packet (regenerated 2026-07-16 as the two-file split; rebuilt same day
  to drop the `SheetRow` locator from `Gas_AllFillsBackend` so all columns paste
  1:1; rebuilt again 2026-07-28 against `GGIT_gas_snapshot_20260728.csv` to fix 43
  stale `SheetRow` locators — 33 `Gas_Decisions` + 10 `Gas_ConfirmedAudit`)** — delivered
  `pipelines_batch_20260728_1731_ET_egypt-gas_handoff-actions.xlsx` +
  `…-evidence.xlsx` (same staging dir, `staged_actions.json` sidecar; supersedes
  the 2359 pair, now in `archive/`). Counts below are from the 07-28 rebuild;
  the fresher snapshot also refreshed the prefilled current values (57 newly
  populated + 118 changed cells on `Gas_AllFillsBackend`, incl. 27 `LastUpdated`),
  and **16 of 284 staged ref units are already live in their target `[ref]` cell**
  (26 more partially) — check the cell before pasting. **THE
  researcher deliverable** — supersedes working from the four workbooks above (and the
  earlier single-file 0959 handoff). The ACTIONS file holds only suggested changes +
  open issues: 79 open decisions (`Gas_Decisions`, high-concern first), 1 status change
  (P3657→shelved), 387 tracker paste units on `Gas_AllFillsBackend` (fills + paste-ready
  refs unified) + 42 operators/owners units, 4 new rows, 49 wiki updates, 50 route
  suggestions, 27 open flags. The EVIDENCE file holds the audit trail: 31 confirmed
  audits, 145 fill-detail + 302 ref-detail rows (201 REVERIFIED counts-only), 102
  wiki-context diffs, 56 covered mechanical flags, 12 covered route flags, 3 monitor.
  Counts derive from
  `python scripts/staged_summary.py --country Egypt --commodity gas` — regenerate, don't
  hand-edit.

Oil (GOIT) not yet swept.

## Live-sheet review — NA's P8004–P8019 additions (2026-07-28)

16 new Egypt gas rows were entered directly on the live sheet 2026-07-27/28
(SheetRows 4277–4292), sourced mainly to the Ministry of Petroleum's house magazine
*مجلة البترول* (petro-mag.org) and, for P8013–P8019, to an egyptoil-gas.com **search
URL** that carries no data. Full parse of both magazine issues, row-by-row verdicts,
and the reusable source-assessment rules:
**`notes/review-2026-07-28-na-egypt-gas-additions.md`**.

Attribution is **NA** (`Researcher` col J, read 2026-07-29) — *not* NF, a different
researcher. Col J was blank in the 07-28 snapshot, so read it rather than inferring.

Headlines: the pipe is largely real but P8005 "SUMED Gas Pipeline" is a mis-named
FSRU send-out line (BL's flag confirmed); P8007 length is 8 km not 7; P8008 is 15 km
not 15.5 and is a Sinai *loop*, not a new line; P8013–P8019 are unsourced as entered.
Systemic: refs pasted into `LengthDoubleCounting` instead of `Length [ref]`
(**45 gas rows tracker-wide, not only NA** — includes our own P3620/P3657; **fixed on
the live sheet 2026-07-28**, backup in `notes/2026-07-28-lengthdoublecounting-fix-backup.csv`),
and **P8001/P8003 collide with the IDs reserved by the Israel gas batch**, which must
be re-numbered before it is applied. `Researcher` was blank on all 16 at review time
and now reads `NA`. Remaining fixes belong in a §5 Update batch, not in-place edits.

## Open items — gas (staged, NOT applied — candidates for review)

**No escalation gate tripped.** Unlike Saudi (P1897–P1925 GIS/km-post family) and Iran
(class-wide NIOC→NIGC), Egypt shows **no class-wide existence gap** and no single
class-wide overwrite — the 4 existence concerns are all row-specific, and attribution is
row-by-row nuance, not one systemic relabel.

### In-dev status sweep (Leg A, 7 rows → 1 status change, ~14% < 30% gate)
- **P3657 Israel–Egypt Offshore Gas Pipeline** → proposed→`shelved` (stale): all traces
  cluster on a defunct proposal; superseded by the operating EMG reverse-flow imports.
- P0473 (Cyprus–Egypt), P3620 (Israel–Egypt onshore), P6685 (Solaimaneyah–North Giza),
  P6686 (New Fayoum), P7597 (Cronos–Port Said), P7864 (Nitzana): status confirmed /
  confirmed-caveat; segment-level spec/attribution caveats flagged on the workbook, not
  applied. Detail in the annual-indev workbook's `Gas_StatusReview` tab.

### Operating deep sweep (Leg C, 50 rows → 109 validity records: 53 confirmed-caveat / 56 concern)
Concerns by type: **attribution 37, spec 31, existence 4, duplicate 4.**

- **Attribution (dominant theme, 37)** — recurring **GASCO (Egyptian Natural Gas Company,
  the transmission *operator*) vs EGAS (Egyptian Natural Gas Holding Co, the *owner*)**
  confusion on domestic trunk rows (e.g. P0477, P3346, P3366): several rows carry EGAS
  where the transmission operator is GASCO. This is row-specific nuance (each needs the
  operator/owner split checked), **not** a single class-wide swap. Also: **P0462
  Arish–Ashkelon** FuelSource `Egypt`→`Israel` (post-2020 reverse-flow import of Tamar +
  Leviathan gas); **P3659** youm7 URL sits in the FuelSource *value* cell — move it to
  `FuelSource [ref]` (data-entry fix).
- **Duplicate / segmentation (4 human de-dup decisions):**
  - **P0477** (Dahshour→Aswan whole-line network, 930 km) vs the six segment rows
    **P6697–P6702** — keep the network row OR the segments, never both in any length total.
    **P6698 (Al Kurimat–Beni Suef)** is one of those segments folded into P0477.
  - **P6687 / P0474 / P3934** — three ProjectIDs for ONE physical trunk (Western Desert
    Gas Project North Line / Obaiyed feeder).
  - **P7574** vs **P3930** (New Administrative Capital–Dahshur, 70 km/32 in) — compare
    before treating both as final; evidence leans toward overlap.
- **Existence (4, all row-specific — keep-but-reref unless noted):**
  - **P3938 Badr El Din Spur (2)** — the 16-in/130/Abu Sennan spec traces to a **PROPOSED
    CO2-EOR transport concept, not a built gas transmission line**. Do not treat as
    operating gas; reclassify/remove.
  - **P6687 Obaiyed Spurline** — sole cited source does not name a distinct 41.5 km/26 in
    line; verify it exists as its own segment before keeping (ties into the P6687/P0474/
    P3934 de-dup above).
  - **P0476 (Salam→Abu Gharadig)**, **P6693** — real lines, but the sole GEM-adjacent
    citation is effectively unsupported; existence rests on independent GulfPub + OGJ /
    Offshore-Technology. Replace the ref, keep the row.
- **Spec (31)** — assorted endpoint/province, length, diameter, capacity, cost corrections
  flagged per row on `Gas_Validity` (e.g. P0436 SegmentCost 207.55M USD unsupported vs
  ~220M cited; P3928 start province Alexandria→Beheira). Read-and-flag; none auto-applied.

### Refs & fills (Leg C)
- Ref pass: **240 REFS_ADDED / 182 REVERIFIED / 17 UNRESOLVED**. Unresolved are mostly
  value disagreements (no independent source supports the current GEM number), not merely
  unsearched — route to review.
- **142 blank-value fill records** (119 corroborated + 23 not corroborated/dropped,
  each corroborated fill with a paired verified ref) → `Gas_Fills`.
- **50 route suggestions** for weak-`RouteAccuracy` rows → `Gas_RouteSuggestions`
  (corridor + sourced named endpoints; candidates for a human routes-repo branch, never
  auto-applied).
- GulfPub/PE World Map cross-comparison (95 Egypt features) → `Gas_GulfPub`; treat dataset
  "additions" as likely mislabels until endpoints/country verified; `Capacity_mmcfd`=300 is
  a placeholder, never a capacity source. **Superseded as the recon surface** by the two
  standalone §2 workbooks below — the 07-28 handoff rebuild carries `gulfpub_crosscompare=0`,
  so no recon content reaches the actions file.

### Reconciliation (§2, 2026-07-29 — TWO standalone workbooks, NOT in the handoff)

> **GulfPub half RE-RUN 2026-08-12 — work
> `pipelines_batch_20260812_1359_ET_egypt-gas_reconciliation-gulfpub.xlsx`; the `0941_ET`
> workbook and its staging dir are in `archive/`.** The reference-side country filter
> compared GulfPub's country string with `==`, dropping every multi-country record
> (Egypt gas 92 → 95 refs). Engine defect, fixed same day:
> `notes/escalation-2026-08-12-multicountry-reference-filter-dropped-transit-trunks.md`.
> **Retraction: 4 of the 43 `gem_only` "no reference counterpart" findings were artifacts.**
> The re-run also picks up matcher fixes landed since 07-29, so it moves further than the
> filter alone: **72 overlaps / 23 additions / 69 gem_only / 5 status conflicts** (was 52 /
> 40 / 43 / 3). Additions fell below the >30 gate; the GEM tab has also grown 78 → 117 rows
> since 07-29, which is why `gem_only` rises. **Read it as a fresh run, not a delta.**
> The OSM half is unaffected (ISO-scoped extract, single-country by construction).

Run to give Egypt the same recon coverage Libya has. Both are **separate review surfaces**:
nothing here is folded into `…_handoff-actions.xlsx`, and nothing is staged as an edit.
Deliverables: `pipelines_batch_20260729_0941_ET_egypt-gas_reconciliation-gulfpub.xlsx`
(rebuilt from the `0910_ET` version after the length-units fix below — work the `0941` file;
`0910` is in `archive/`) and `pipelines_batch_20260729_0910_ET_egypt-gas_reconciliation-osm.xlsx`
(OSM has no length attribute, unaffected). Inputs in `staging/recon-{gulfpub,osm}-20260729/`.

- **GulfPub** (92 Egypt gas features): **52 overlaps** (45 yellow / 7 green), **40 additions —
  all `NEAR_MISS`**, 43 GEM-only, 3 status conflicts, 12 ambiguous clusters, 1 route-replacement
  candidate. 40 reference-only additions is **over the >30 escalation gate** — but every one
  bucketed `NEAR_MISS` rather than `DISCOVERY_CANDIDATE`, i.e. the engine thinks each is close
  to an existing row. Adjudicate by hand before any is treated as a discovery.
- **`Ref Length (km)` was MILES, ~38% short — FIXED, and this workbook was rebuilt.** Found by
  the required ingest spot-check on this run: a dataset-wide manifest defect, not Egypt-specific.
  The manifest now reads `length_units: mi` with a `Canada: km` per-country override, and the
  `0941_ET` rebuild carries corrected lengths — GEM agreement went 2/52 → 15/52 within ±10%.
  Matching was never affected (`match.py` scores length on `geodesic_km`): the re-run against
  the same snapshot changed `s_length` on 0 pairs and left all counts identical.
  `notes/escalation-2026-07-29-gulfpub-gas-length-miles.md`.
- **OSM** (21 features / 476.6 km, first Egypt OSM run): **0 overlaps**, both `MATCH_QUALITY`
  escalations raised — 0 of 21 features named and 62 of 78 GEM rows `no route`/`very low`, so
  name and geometry are both dead and only the admin-area signal (52.4% of records, via the
  documented `geoarea_weight: 0.30`) was live. Top composite 0.4094 vs the 0.45 threshold.
  **The threshold was not lowered.** Triage by disposition instead: **9 `ROUTE_FOR_EXISTING`**
  (candidate geometry for routeless rows → human routes-repo PR; the run's real value), 2
  `FRAGMENT_OF_EXISTING`, 10 `DISCOVERY_CANDIDATE` (match each to an existing row under
  another name first). Do NOT read the 0 overlaps as "GEM is missing all 21".

### Discovery (Leg B, 2026-07-15: 7 candidates → 4 new rows / 3 monitor)

Queue surfaced 7 candidate clusters (over the >5 escalation gate; surfaced at delivery —
all 7 fully vetted, nothing pending). New rows on `Gas_NewRows` (paste-ready; owner refs
on `Gas_OperatorsOwners`, applied once rows have ProjectIDs):

- **Shukeir–Hurghada** (127 km / 24 in, GASCO, operating 2006) — tier HIGH: OGJ 2007 +
  independent GulfPub record + archived GASCO site. Upstream of P6034 (Hurghada–Safaga),
  distinct physical segment.
- **El Sadat–El Fayoum (Dahshour)** (76 km / 32 in, EIB Gas Grid Reinforcement) — tier
  medium: EIB EIA PDF + EIB project page. Status `operating` is INFERRED (both sources
  predate completion) — flagged in ResearcherNotes.
- **Egypt Israeli Gas Import Pipeline (Nitzana, Egyptian side)** (~$400M, GASCO,
  proposed 2025) — distinct from the Israeli-side rows P3620/P7864.
- **Ain Sokhna FSRU Gas Import Pipeline (Sonker)** (17 km / 36 in, operating) —
  StartYear1 left blank; grid injection began summer 2025 per the Status refs (reviewer
  may set 2025 from those same refs).

Monitor (below add-threshold): **Gaza Marine–El Arish** (development option halted by the
Gaza war), **Libya–Egypt** (Jan 2026 Petrojet–NOC MoU is feasibility-study-only, no
endpoints), **Taba–Sharm El-Sheikh** (the 2026-07-15 re-vet DOWNGRADED the 07-09 new_row
shard: its corroborating URLs didn't actually confirm the line on close read — single
2007 OGJ source tracing to GASCO, and 2016–2022 reporting frames Sharm El-Sheikh gas as
newly arriving).

**Nitzana is represented three ways — apply as ONE linked decision:** existing rows
P3620 (Israel–Egypt onshore) and P7864 (Nitzana, in-dev; flagged as a possible duplicate
pair in the staged concerns) plus the discovery new-row *Egypt Israeli Gas Import
Pipeline (Nitzana, Egyptian side)* covering the Egyptian section. Settle the
P3620↔P7864 de-dup and the new row together so the corridor doesn't end up with
overlapping rows.

## Open items — §8 route creation (2026-07-30; 40 candidates APPLIED, 15 partials open)

All 55 gas rows with `RouteAccuracy = no route` covered in
`batches/egypt-gas/staging/route-creation/`; workbook
`…_20260730_1239_ET_egypt-gas_route-creation.xlsx`. **37 candidate geojsons**
(15 GulfPub sidecar, 3 gis split/merge — Tarek-junction split of the WDGP-N trunk for
P3934/P6687, four Denise traces merged for P7447 — and 19 endpoints great-circle at
`very low (straight line/schematic)`) + **18 corridor-only ROUTE_PARTIAL rows** (an
endpoint couldn't be publicly coordinated — no fabricated coords).

**APPLIED 2026-07-30 (Baird-authorized):** the 37 candidates replaced their null
placeholders in `GOIT-GGIT-pipeline-routes` (merge `0c8c01f4`, via its `qc_routes.py`:
24 PASS / 13 length-WARN `--include`d / 0 FAIL), and the sheet's route columns were
written for those 37 rows (111 cells, batch verified on readback; backup
`notes/sheet-write-2026-07-30-egypt-gas-route-columns.csv`): `RouteNotes` += CB method
stamp + the full researcher notes, `RouteCreator` += `CB`, `Route [ref]` += informing
URLs — all appends, nothing overwritten. **RouteAccuracy also written same day**
(37 cells: 19 `very low (straight line/schematic)` / 15 `high` / 3 `medium`, backup
`notes/sheet-write-2026-07-30-egypt-gas-route-accuracy.csv`); Baird flipped the six
South Valley `RouteType` cells to `Mapped route (at any accuracy)` himself, settling
the per-segment decision. (`RouteLocation` no longer exists as a sheet column.) The
18 ROUTE_PARTIAL rows keep `no route`.

- **5 intentional gate FAILs, each a sheet-length question, not a geometry defect:**
  P6697 (ratio 0.685), P6687 (2.303 — Obaiyed→Tarek portion vs 41.5 km sheet), P7447
  (0.446 — Denise system scope), **P3937/P3938 (both sheet lengths = 130 km, almost
  certainly a garbled echo of an OGJ 130-mile CO2-EOR figure; real corridors 26.8 km
  BED-2→BED-3 and 70 km BED→Alam El Shawish per corroborated GulfPub traces).**
- **Sheet endpoint corrections surfaced by the research** (flag columns on the
  workbook): P6704 start is NOT Rashid (intra-Amreya spur, WDGC→butane plant);
  P7597 Cronos ends at Zohr infrastructure, NOT Port Said; P6035 "Veunsa" = West
  Damietta power plant (Kafr Saad); P7572 "Qarun" is actually the offshore
  Karawan/DEKA sealine into El Gamil (misfiled name); **P8008/P8009 "Sinia" = GASCO's
  transliteration of Sinai** (Trans-Sinai duplication lines, mis-scoped as Upper
  Egypt); P8002's 73 km looks like the Abu Sultan→NAC portion of the 165 km El
  Tina–Abu Sultan–NAC trunk (double-count check).
- **South Valley segments P6697–P6702** (`RouteType = Included in other ProjectID`,
  parent P0477 already mapped): accepting the per-segment candidates implies a
  RouteType decision — Baird's call, linked to the P0477-vs-segments de-dup above.
**RETRY PASS same day (Baird-directed, post-quota-reset): 3 of the 18 partials
resolved and APPLIED** — routes-repo merge `241ef5aa` (qc 2 PASS / 1 length-WARN
`--include`d), sheet write of all four route columns on the 3 rows (12 cells,
readback-verified; backup `notes/sheet-write-2026-07-30-egypt-gas-retry-routes.csv`);
workbook `…_20260730_1415_ET_egypt-gas_route-creation-retry.xlsx`; results in
`retry_results_*.json` + `assemble_retry_candidates.py` in the staging dir.

- **P8013 Trans Gulf**: "Petreco Plant" = Petrobel's Petreco Oil Centre at Abu Rudeis
  (Eni 2016 Egypt report + Egypt Oil & Gas), crossing the Gulf of Suez to Ras Bakr
  Transmission Station — sheet `EndLocation` is blank, suggest that name.
- **P8021 Korimat–Al Tebbin**: World Bank ICR (Loans 3103/3441-EGT) names the 95 km
  22-inch El Tebbin (Dahsour)–Kureimat gas line, completed ~Sep 1996 — distinct from
  the same-named 2016 electricity line.
- **P8014 Zaafarana–Korimat**: resolved by main-session adjudication — the SAME WB ICR
  names the 162 km Zafarana–Kureimat line (completed Nov 1995; as-designed 18-inch,
  changed from 20) vs sheet 163 km; the Sadat City→Dahshur 75 km line is a second,
  later Kureimat supply, not a competing identity. StartYear1 candidate: 1995. (WB PDF
  is a 3.9MB scan — url_verifier large-PDF substring false-negative, confirmed via
  pdftotext.)

**The 15 remaining ROUTE_PARTIAL rows keep `no route`**; their staged records now
carry the second-pass findings. Notables: P8020's corridor corroborated by the Egypt
Oil & Gas 2017 transmission-map (Greater Cairo→El Tina→Port Said) but no named
endpoint facilities; P8005 gained an OSM-sourced start (SUMED Pipelines Terminal
polygon, Ain Sokhna) but "the national grid" end stays unnamed; P8003's identity
nailed to EGAS Annual Report 2018 p.20 (24"/27 km Fayoum–Giza rehabilitation,
governorate-level only); P7588's Kom Ombo tie-in candidate RULED OUT on distance
(~57 km > the 37 km pipe); P8009 localized to North Sinai Governorate (2025-11-18 EIA
consultation); Abu Madi (P8022/P8023 start) has NO citable coordinate in
Nominatim/Overpass/GeoNames/Wikidata — checked independently in the main session.

## Open items — §8 route creation 2026-08-04 (ENTSOG pass; ALL 23 candidates APPLIED, partials open)

**Single review surface for everything route-pending (both passes):**
`…_20260805_1701_ET_egypt-gas_route-creation-pending.xlsx` — **partials only
now** (README + `Gas_RouteSuggestions`, 17 rows; July + August unioned, July
P8022/P8023 superseded by the August re-research). Zero pending candidates
since the 2026-08-05 apply, so the workbook has no `Gas_RouteCandidates` tab.
Rebuild anytime with `route-creation-20260804/build_merged_pending_workbook.py`
(it now filters on each record's `applied` stamp); the two staging dirs stay
canonical.

Baird-directed second §8 pass: replacement routes for the 35 `very low` + 3 `low`
rows off the new ENTSOG/GIE SYSCAP 2026 vector layer (`sources/entsog/`; measured
Egypt accuracy median 4.2 km / p90 13 km → `medium` cap), plus a fresh run at all
30 `no route` rows. **23 candidates + 4 partials staged** in
`batches/egypt-gas/staging/route-creation-20260804/` (its README has the full
adjudication); workbook `…_20260804_1656_ET_egypt-gas_route-creation.xlsx`
(the `_1431_ET` build is superseded/archived — P0436 withdrawn same day after
Baird re-graded its row to `medium` on the sheet).

- Replacements (10) **APPLIED 2026-08-04 (authorized)**: 7 ENTSOG-traced `medium`
  (P7567 P8019 P8024 P8010 P0462 P3928 P3936) + 3 GulfPub sidecar `high` (P3935 —
  fixes a south endpoint ~400 km off; P6034; P6037). Routes merge `752ab5d3`
  (QC 6 pass + 4 WARN included with documented rationale: P0462 Gaza-waters
  vertices, P3936/P6034 length flags = the staged gate FAILs, P3935 geocoder
  matching the same wrong southern "Salam" the old route used); sheet half via
  `apply_route_candidates.py --replace` (NEW mode this batch — 50 cells verified,
  RouteCreator SET to `CB`, backup
  `notes/sheet-write-2026-08-04-egypt-gas-route-replacements.csv`);
  `audit_route_sync.py` Egypt gas clean. 25+ rejects keep their existing geometry;
  P6033 HOLD (start identity), P7482 skipped (18 km subsea hop); P0436 withdrawn
  (row now `medium`, a medium ENTSOG trace can't improve it).
- No-route rows (13) **APPLIED 2026-08-05 (authorized)**: P8034 sidecar `high`;
  P8041 P8044 P8045 P8033 P8036 P8038 P8042 P8027 P8040 P8032 ENTSOG-traced
  `medium`; P8031 P8039 endpoints `very low`. Routes merge `a2fa41c8` (QC 11 pass
  + 2 WARN included: P8031 −40% is a great-circle straight line, P8041 −37% is the
  suspect sheet length; P8042's internal-gate FAIL passed the routes-repo gate at
  −27%); sheet half via `apply_route_candidates.py` (65 cells verified —
  RouteType/RouteAccuracy/RouteNotes/RouteCreator/Route [ref]; backup
  `notes/sheet-write-2026-08-05-egypt-gas-route-columns.csv`);
  `audit_route_sync.py` Egypt gas A/B/C = 0. Finding D flags P8051–P8053 — new
  sheet rows with blank RouteType/RouteAccuracy, unrelated to this pass, worth a
  look when someone next touches those rows.
- 4 documented gate FAILs applied deliberately — P3936 (1.343, corridor review) and
  three suspected sheet-length defects: P6034 (38.5 km vs 57 km coastal geometry),
  P8041 (55 km vs EIA chainage 33 km), P8042 (215 km vs ~162 km canal corridor).
- Still partial (the only pending route work left): P8026 (no start), P8022/P8023
  (Abu Madi governorate conflict, sources ~80 km apart), **P8035 = duplicate of
  applied P8013** (merge/retire, don't draw). P8040 name flag: `PipelineName` says "Damanhur", sheet's own
  StartLocation + Arabic name say **Dahshour** — rename recommended.

## Open items — §8 route creation 2026-08-07 (NA's newest rows P8050–P8059; staged NOT applied)

Baird-directed: research the pipelines `NA` recently added to the backend and draw
candidate routes where they read `no route`. Scope is the **ten newest `NA` gas rows**
— P8050–P8059, SheetRows 4311–4322, all `no route`, none previously worked (the 17
July/August partials in `…_20260805_1701_ET_…route-creation-pending.xlsx` are a
disjoint set). Staging `batches/egypt-gas/staging/route-creation-20260807/`; workbook
`…_20260807_1712_ET_egypt-gas_route-creation.xlsx`.

**Recency was determined by walking the daily `data/GGIT_gas_snapshot_*.csv` files for
the first date each row's `PipelineName` went non-blank — NOT by ProjectID.** P8000–P8099
were pre-allocated as blank placeholder rows on 2026-07-15, so PID order says nothing
about when a row was actually filled. Researcher code read from **col J**, never inferred.
Gotcha worth remembering: the literal code `NA` is in pandas' default `na_values`, so a
plain `read_csv` silently blanks all 423 of `NA`'s gas rows — use
`keep_default_na=False, na_values=[]`.

- **9 candidates + 1 `ROUTE_PARTIAL` staged.** Rung mix: 2 ENTSOG-traced `medium`
  (P8057, P8059), 7 endpoints great-circle `very low` (P8050 P8051 P8052 P8053 P8054
  P8056 P8058), 1 partial (P8055). Internal gate 7 PASS / 2 FAIL; the routes-repo's own
  `qc_routes.py` gives **4 pass / 5 warn / 0 fail** — every WARN is a length flag, and in
  each case the *sheet length* is the suspect value, not the geometry.
- **ENTSOG was adjudicated per PID against the overlay PNGs, not accepted wholesale.**
  Accept only where BOTH endpoint snaps fall inside ENTSOG's measured Egypt error
  (median 4.2 km / p90 13 km): P8057 (2.9/1.4 km) and P8059 (0.0/2.0 km). Rejected for
  P8051 (14.1 km), P8054 (14.4 km), P8056 (18.6 km) — the network path stops short of the
  real terminus, so a chord beats it; for P8050 the path is 1.9× the sheet length and
  swings well west; for P8058 the path fits but the *endpoint identity* is contested, so a
  `medium` grade would overstate the evidence. North Sinai (P8052/P8053) has no ENTSOG
  coverage at all.
- **The do-not-apply list is RETIRED (2026-08-10, second revision).** All ten rows were
  re-staged in the 08-10 pass below, and the blocks resolved as follows:
  - **P8052/P8053 — clear to apply. The "wrong cement plant" finding is WITHDRAWN.** An
    Egypt-wide OSM name sweep returns exactly two Sinai cement works and they are
    neighbours in the **Jabal Lubna** quarry district (*Sinai White Cement* 33.7683,30.7240;
    *Al Arish Cement* 33.8487,30.7008) — there is no cement works beside El Arish town.
    Independently, georeferencing the GASCO sheet's own printed captions puts `Sinai` at
    (33.821,30.759) and `Cement` at (33.824,30.705), i.e. on the OSM plants. The original
    anchor was right; the withdrawn "El Arish + offset" arithmetic was reverse-derived from
    the 45 km to make the ratio work. What survives is only P8052's 1.40 ratio, best read as
    the tap being a coastal-trunk tie-in ~20 km west of Sheikh Zuweid town (the map's own
    inland branch g07-0088 leaves the coast at 33.949,31.067 and runs 41.6 km to the plant,
    matching its `24" - 45 k.m` label).
  - **P8057, P8059** — apply only if a schematic placeholder ahead of the real corridor is
    wanted; that trade is Baird's call, not a block. Both keep a live length question
    (P8057: map-sourced 25 km vs a 40.8 km chord; P8059: map-confirmed 75 km vs a 14.1 km
    chord, so the west-Alexandria end is the wrong facility).
- **Data-quality escalation covering all ten rows:**
  `notes/escalation-2026-08-07-egypt-gas-new-rows-citations.md`. **The headline citation
  finding was WITHDRAWN 2026-08-10** — `NA` was identifying these pipelines **visually off
  the GASCO national-grid map on printed p.35**, not from the report's prose tables, so the
  original `pdftotext` full-text search was answering the wrong question. The map draws each
  segment and annotates most `NN" NN km`; citing Status/Fuel/Type/Length/Diameter/Location
  to it is defensible. 7 rows cite the report across 36 `[ref]` cells, and against the map
  **P8052 (`24" - 45 km`), P8053 (`16" - 16 km`), P8057 (`24" 25 k.m`) and P8059
  (`24" 75 km`) match exactly**;
  P8054 is corroborated by the prose table too. Six of the seven have a map label whose
  **diameter matches the sheet exactly**. What survives is narrow: **P8051's 32" conflicts
  with the 65 km label's 42"**
  (probable mis-pairing inside the stacked six-label Abu Homos bundle); and **P8050 needs a
  duplicate-check against P7567** — the report's "Ezdwaj Edku / Abu Houmas 30 km - 42""
  matches P7567 exactly, and on the map "Rosetta" is an *offshore field* landing at Idku,
  not the Delta town. Map evidence committed at
  `batches/egypt-gas/archive/staging/route-creation-20260807/maps/` — including
  `z_decimal_calibration.png`, which is why the earlier "P8059 = 7.5 km decimal misread"
  claim was retracted: the map raster is only 200 ppi, the 600 dpi page render upsampled
  ~3×, and at native scale the mark between the 7 and the 5 is a dark inter-glyph seam, not
  the light baseline dot a real decimal makes (cf. `12" 14.5km` on the same map). Six rows
  have lengths that conflict with their own endpoints (P8057 and P8052 impossibly so — the
  chord exceeds the stated pipe length; P8059 overshoots 5.3×); P8057's `EndPrefecture`
  wrongly repeats its `StartLocation`; **P8058 is probably the second line of the P3930
  New-Administrative-Capital corridor, not a sequel to P8040** (its own Arabic name and
  the seed press release both say so, and the geometry agrees) — adjudicate and probably
  rename before applying; P8055's "Trans Gulf … II" name asserts a false lineage to P8013
  (a 12″ Gulf-of-Suez oilfield line) when GASCO calls it "Duplication of the Trans-Sinai
  pipeline". These route to **Update**, not §8.
- P8057's cited ministry release was fetched and text-searched here: 4 hits for ازدواج,
  zero for مسطرد/التبين — **removed** from its proposed `Route [ref]` rather than carried
  as an unsupported citation.
- Incidental pre-existing anomalies (not `NA`'s rows, logged in the escalation): **P3929**
  carries 68.5 km, which is EGAS-2018's figure for the *Dahshur–El Wasta* segment (P8054's
  line) — **confirmed first-party 2026-08-10**, printed p.37 gives Al Wasta/Beni Suef as
  60 km / 36"; **P6699 and P6700** both carry exactly 150.00 km.
- **Sheet moved 2026-08-10** — 08-07 locators are stale: the gas tab was re-sorted
  (P8051 4322 → 4313, the ten rows now contiguous at 4312–4321) and three edits landed —
  **P8058 renamed to "New Administrative Capital–Dahshur Gas Pipeline II"** (i.e. the
  escalation's Finding 3 was acted on, and the staged geometry already assumed that
  reading), P8055's name tidied, and P8051's `?utm_source=chatgpt.com` stripped.

## §8 route creation 2026-08-10 (ALL 34 routeless gas rows; 24 candidates APPLIED, 10 partials open)

Baird's instruction reset the bar: **"ideally, I want every single Egypt pipeline to have at
least a very low resolution route."** That relaxes *precision*, not *sourcing* — at
`very low (straight line/schematic)` a settlement- or facility-level anchor pair is exactly
what the tier describes, so three passes' worth of rows that had been held back as
`ROUTE_PARTIAL` for imprecision are now drawable. The sourcing rule is unchanged: every
coordinate comes from OSM, GeoNames, a published facility record, or (flagged as such) a
point read off GEM's own applied geometry as an internal tie-in.

Staging `batches/egypt-gas/staging/route-creation-20260810/`; workbook
`…_20260810_1800_ET_egypt-gas_route-creation.xlsx`. **This pass supersedes the 08-05
pending workbook and the whole 08-07 pass** — both, plus the July `route-creation` and
`route-creation-20260804` staging dirs, moved to `batches/egypt-gas/archive/`. Their pending
remainder was entirely re-staged here, so Egypt gas now has **one** open route surface.

- **Scope is exhaustive, not a selection.** Egypt has 115 gas rows; 34 are routeless (33
  `no route` + P8067 blank). **24 are now candidates, 10 stay `ROUTE_PARTIAL`** — nothing is
  silently absent, each partial carries its reason in `ResearcherNotes`.
- **APPLIED 2026-08-10 (authorized, both halves).** Routes repo: all 24 merged, `d0d8ba77`
  (7 of them replaced pre-existing `geometry: null` placeholders, so no real route was
  overwritten); the 7 WARN PIDs went in via explicit `--include`. Sheet: **120 cells** across
  the 24 rows, `RouteCreator` `CB`, backup `notes/sheet-write-2026-08-10-egypt-gas-route-columns.csv`.
  `audit_route_sync.py` A/B/C = 0. **P0477 was applied too** — "all candidates" resolved the
  convention question in favour of routing the parent network row (`high`, merged from its own
  six segments); everything else is `very low (straight line/schematic)`.
  **P8063, P8065 and P8066 carry an empty `Route [ref]` by design** — their anchors are points
  read off GEM's own applied geometry, which standing rule 1 forbids citing, so the provenance
  lives in `RouteNotes` instead.
- **Two rows `NA` added after this batch was scoped were routed and APPLIED 2026-08-11**
  (`batches/egypt-gas/staging/route-creation-20260811/`, both `very low`, both QC PASS,
  5 sheet cells each, `RouteCreator` `CB`, backup `notes/sheet-write-2026-08-11-…csv`):
  **P8068** El Noubareya–Qusina (routes merge `1a2c64b5`; the Nubaria CCPP anchor reused from
  P8051 → OSM Quwaysna town node, 47.9 km chord vs 40 km; the GASCO 2007 map carries **no**
  24″/40 km label within 35 km of this corridor, so it rests on the two named endpoints alone)
  and **P8069** Bader3–Ameriya (routes merge `950df475`; OSM *Bed-3 Camp* node in Abu Gharadig,
  corroborated 0.4 km away by the separate OSM *Badr El Din* junction node → WDGC, read as the
  processing destination for Western Desert field gas, 223 km chord vs 253 km).
  **Both arrived with a blank `RouteAccuracy`, and blank means `no route`** — a new row whose
  cell hasn't been filled in yet is routed and applied like any other (Baird 2026-08-11,
  `route_conventions.md`), not held back.
- **Egypt gas now stands at 117 rows: 107 routed, 10 unrouted — and the 10 are exactly the
  partials listed below.** `audit_route_sync.py` A/B/C/D all 0. (One of the 10, **P7589**,
  was resolved 2026-08-11 and is staged not applied — see below; applying it takes Egypt gas
  to 108 routed / 9 unrouted.)
- Internal gate 24 PASS / 0 FAIL; routes-repo `qc_routes.py` **17 pass / 7 warn / 0 fail**
  (WARNs P6704 P8020 P8052 P8053 P8056 P8057 P8059 — all length ratios, expected for
  great-circle candidates).
- **Anchors newly resolved this pass** (the reason the long-standing partials moved):
  **Abu Madi = 31.3667, 31.4133** (GeoNames *Ḩaql Ghāz Abū Māḑī* gasfield, corroborated
  within 1.3 km by unnamed OSM industrial way 690415406) unblocked P8022/P8023/P8049; the
  **two distinct "Ameriya" nodes** GEM already uses — Amreya oil & gas plant (29.8648,
  31.0948, end of the applied P0474) and WDGC (29.8429, 31.0094, start of P3934/P8032),
  10.2 km apart — unblocked P8065/P8066; the **OSM El-Tina station** node (32.3075, 31.0425)
  unblocked P8026 and P8035.
- **P8035 correction:** the July pass had resolved it to P8013's Petreco/Ras Bakr endpoints
  and called it a duplicate of P8013. Withdrawn — P8035 is the Port Said **UGDC–El Tina**
  line, re-anchored to El Gamil → El-Tina station (28.7 km vs 40 km).
- **P0477 South Valley is a convention question, not research.** The 930 km parent
  network row is staged as a merge of its own six applied segment routes (P6697–P6702,
  929 km summed). 15 network rows tracker-wide already carry routes, so it is not
  unprecedented — whether GEM wants parent rows routed was Baird's call, and **the 08-10
  "add all candidates" authorization made it: applied.** Reversible by deleting
  `P0477.geojson` and clearing the four route cells.
- **Two rows carry a length question the geometry can't settle** — P8020 (186 km chord vs
  130 km sheet, so either the length is wrong or "Cairo Ring" means a different node than
  P8017's) and P8035. Corridors are right; both apply-at-your-discretion like P8057/P8059.
- **The 9 remaining partials, with why:** P8005/P8006/P8007 (Ain Sokhna terminal spurs —
  the terminal end is anchored, the grid-side end is unnamed in every source), P8008/P8009
  ("Sinia Gas Pipeline 1/2" — no endpoint named anywhere; "Sinia" is the governorate),
  P8001 (Abu Gharadig anchored, no geocodable NORPETCO facility), P8003 (EGAS 2018 names
  the project but no endpoints; Fayoum→Giza is ~80 km against a 27 km row), P7605 (Wanda:
  nothing geocodable), P8055 (Trans-Sinai II duplication: GASCO gives length/bore/cost but
  no endpoints). Each needs a *source*, not another geocoding attempt.
- **P7589 (Faramid) came OFF the partials list 2026-08-11** — staged as a candidate in
  `staging/route-creation-20260811-p7589/`, routes-repo QC **PASS**, 36.9 km vs 38.0 km
  (−3%), not yet applied. Both ends moved:
  - **Start.** Faramid is a named *development lease* (map code 94) inside the **East
    Obaiyed** concession on the EGPC/EGAS/GANOPE concession map (`eug.petroleum.gov.eg`),
    bbox 26.9497–27.0666 E / 30.9999–31.0997 N (~50 km²), five graded wellpads inside the
    traced polygon on imagery. The old start guess (30.9659, 26.8891, "30 km NW of
    Meleiha") is ~13 km off and falls **outside** the lease — superseded.
  - **End.** The "159 km away" rejection is **withdrawn**. Egypt Oil & Gas has Agiba
    "extending another line from the Faramid field to **Badr El Din Company** to process
    24 mcf/d" — and "Badr El Din Company" is **BAPETCO**, the operator (post-Cheiron, per
    SPE/JPT + Capricorn), not the BED *field*. The processing point is the **BAPETCO
    Obaiyed gas plant** (31.0996, 26.6142), 35 km west. Sheet capacity 25.00 MMcf/d matches
    the "24 mcf/d" in the same sentence. **Lesson: a name-match to a field can be a match to
    the operating company** — check what the name denotes before rejecting on distance.
  - **Geometry** follows the existing Obaiyed export right-of-way (OSM way/545729460), a
    multi-lane graded corridor visible continuously in imagery and passing 1.07 km from the
    pads. The straight-line alternative is 35.2 km and never deviates >2.4 km, so
    `low (within kilometers)` holds either way. No Faramid-specific trench is
    distinguishable from the trunk, and OSM carries no Faramid line — shared ROW is
    inferred from co-location, not observed.
- **Egypt oil is effectively complete**: 46 rows, 45 with mapped geometry. P7326 already
  carries a deliberate `geometry: null` placeholder in the routes repo and is correctly
  `Unavailable`/`no route`. One defect: **P7338** (Dekhela–Wadi Al Qamar LPG) has real
  3-point geometry in the routes repo but `RouteType = Unavailable (cannot find route)`
  against `RouteAccuracy = low` — a three-way-sync violation needing a one-cell RouteType
  fix, repairable with `apply_route_candidates.py --backfill-route-type --pids P7338`.

## ProjectID recycling — P8017 / P8020 → P8084 (APPLIED 2026-08-27)

**A cleared row's ProjectID can be reused for another country's pipeline, and the routes
repo goes on serving the old geometry under it.** `NA`'s two Egypt rows P8017
(*Suez-Cairo Ring*, 150 km, 90 MMcf/d) and P8020 (*Cairo Ring–Port Said*, 130 km,
230.30 MMcf/d) were wiped from the gas tab on 2026-08-14 19:26 UTC (backend revision
`345949`) with **no entry on the `Removed oil/NGL/gas pipelines` tab**, and both PIDs were
then reused by `AL` for Iraq *Baiji-Mosul Gas Pipeline* segments (2026-08-24). The wipe was a
range clear of `C:CF`, so `ProjectID` and the route block `DC:DG` survived — which is exactly
why the two rows kept reading `Mapped route`/`high` while `P8017.geojson` and `P8020.geojson`
still held Nile-Delta coordinates for Iraqi pipe.

Resolved 2026-08-27 (authorized; both halves in one batch):

- **P8017 restored as `P8084`** — the next free pre-allocated PID (SheetRow 4344). 26
  hand-entered cells recovered verbatim from revision `345873` and re-entered;
  `Researcher`/`LastUpdated` preserved as `NA`/2026-07-28, restore provenance in
  `ResearcherNotes`. Geometry moved with the row: `P8017.geojson` → `P8084.geojson`
  (routes merge `1ccf6cfa`, `qc_routes.py` PASS, 136 km vs 150 km, Egypt→Egypt).
- **The two Iraq rows reset to `Not mapped (but could be …)`/`no route`**, with
  null-geometry placeholders in the routes repo. **`AL` has not uploaded replacement
  geojsons** — a freshly re-synced `drive-uploads/` mirror holds one file in her folder (`P2232`),
  and nothing on any branch touches these PIDs — so both rows stay routeless pending her
  files. `RouteCreator = AL` and her `Route [ref]` are deliberately left in place as
  provenance for the routes she intends to deliver.
- **P8020's Egypt row was NOT restored** (not in scope). Its 27 recovered cells sit in
  `notes/recovered-2026-08-27-p8017-p8020-cleared-row-values.md` — **Drive keeps revisions
  ~14 days, so that file is the only copy after roughly 2026-08-28.**
- GulfPub `gulfpub:gas:424` (*Suez - Dahshour Pipeline*) matched the old P8017 at route
  IoU 1.0, so with P8084 carrying the same geometry the §2 overlap is preserved — the
  "424 re-buckets as an unmatched addition" consequence noted in the 08-26 triage memo
  no longer applies.
- Sheet backup: `notes/backup-2026-08-27-p8084-restore-p8017-p8020-route-reset.csv` (32
  cells, before/after). `audit_route_sync.py` lists none of the three PIDs.

**This class of defect is invisible to `audit_route_sync.py`** — its four findings are all
per-row consistency checks, so a row with geometry and `Mapped`/`high` reads as in sync no
matter which continent the geometry is on. A **finding E** (geometry centroid outside the
row's own `CountriesOrAreas`) would catch it; still an open call in the 08-26 triage memo.

## Open items — QC packet (2026-07-15, staged NOT applied)

Wiki-parser spot check 5/5, route geodesic recompute matched, recalc clean.

- **P0473 Cyprus–Egypt length is wrong: 240 km, not 310.** The sheet's 310 km reflects
  the older Aphrodite→Damietta concept; the current project is ~240 km (3 verified refs,
  tier high). The 215 km drawn route then sits inside the ratio band (0.90) — the length
  value was the error, not the geometry.
- **P6699 wiki refuted:** the wiki page suggests Nile Valley Gas Company as operator;
  independent sources say **GASCO** (2 refs). Fix the WIKI here, not the sheet.
- **StartYear1 fills (5):** P0474=1999 (Apache FY1999 10-K + OGJ), P6037=2021,
  P6687=2000, P6692=2007 (single-source, medium), P7574=2018 (medium). P3938 StartYear1
  genuinely unfindable — consistent with its CO2-EOR-concept existence concern.
- **Operator fills (4, → operators/owners tab, `Target tab` column on Gas_Fills):**
  P6033=GASCO, P6699=GASCO, P6701=Nile Valley Gas Company (1 live ref, downgraded
  medium), P6704=Egyptian Natural Gas Co.
- **P0436 Arab Gas Pipeline union flags resolved:** sheet correct — the multi-segment
  wiki page unions values; segment-level sheet values stand.
- **Wiki-editing worklist for the researcher:** 77 WIKI_UPDATE rows on `Gas_WikiAlignment`
  (sheet newer than wiki); 7 WIKI_STALE_VS_STAGED wait on the staged deep-sweep packet
  being applied first.
