# Egypt — country notes

MENA deep-coverage country (GGIT gas focus so far). Gas packet legs:

- **In-dev status sweep (Leg A)** — delivered `pipelines_batch_20260709_0724_ET_egypt-gas_annual-indev.xlsx` (7 in-dev rows).
- **Operating deep sweep (Leg C)** — delivered `pipelines_batch_20260713_1319_ET_egypt-gas_deepsweep.xlsx` (50 operating rows). Fan-out ran on Sonnet.
- **Discovery (Leg B)** — NOT yet delivered: 6 vetted candidates staged under `batches/staging/annual-gas-egypt/discovery/vetted/` (ain-sokhna-sonker-fsru, egypt-israeli-import-nitzana, gaza-marine-el-arish-offshore, libya-egypt-gas-pipeline, shukeir-hurghada, taba-sharm-el-sheikh); workbook not built.

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
- **142 blank value cells filled** (best-effort, paired verified ref) → `Gas_Fills`.
- **50 route suggestions** for weak-`RouteAccuracy` rows → `Gas_RouteSuggestions`
  (corridor + sourced named endpoints; candidates for a human routes-repo branch, never
  auto-applied).
- GulfPub/PE World Map cross-comparison (95 Egypt features) → `Gas_GulfPub`; treat dataset
  "additions" as likely mislabels until endpoints/country verified; `Capacity_mmcfd`=300 is
  a placeholder, never a capacity source.
