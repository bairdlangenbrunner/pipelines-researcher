# Egypt — country notes

MENA deep-coverage country (GGIT gas focus so far). Gas packet legs:

- **In-dev status sweep (Leg A)** — delivered `pipelines_batch_20260709_0724_ET_egypt-gas_annual-indev.xlsx` (7 in-dev rows).
- **Operating deep sweep (Leg C)** — delivered `pipelines_batch_20260713_1319_ET_egypt-gas_deepsweep.xlsx` (50 operating rows). Fan-out ran on Sonnet.
- **Discovery (Leg B)** — delivered `pipelines_batch_20260715_1552_ET_egypt-gas_discovery.xlsx`
  (7-candidate queue fully vetted → 4 new rows / 3 monitor; the 07-09 shards were
  independently re-vetted at delivery, one downgraded). See "Discovery (Leg B)" below.
- **Sheet↔wiki↔route QC legs (handoff-packet pilot, researcher onboarding; workflows.md §6)** — delivered
  `pipelines_batch_20260715_1442_ET_egypt-gas_qc.xlsx` (57 rows; staging
  `batches/staging/qc-gas-egypt/`): 12-row `Gas_Existence` tracking review (5 existence
  + 7 duplicate concerns carried from the prior staged packets — read first), 152 wiki
  diffs (77 WIKI_UPDATE / 67 SHEET_SUSPECT / 7 stale-vs-staged / 1 UNPARSED = P7864, no
  Wiki URL), 13 route length-ratio flags (11 already staged-annotated), 63 mechanical
  flags (incl. 38 `Existence_support` thin-ref flags, ALL covered by the prior
  existence audit), 14-row Leg-3 research → 21 validity + 10 fills.
  See "Open items — QC packet" below.
- **Handoff packet (regenerated 2026-07-16 as the two-file split)** — delivered
  `pipelines_batch_20260716_1156_ET_egypt-gas_handoff-actions.xlsx` +
  `…-evidence.xlsx` (same staging dir, `staged_actions.json` sidecar): **THE
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
  a placeholder, never a capacity source.

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
