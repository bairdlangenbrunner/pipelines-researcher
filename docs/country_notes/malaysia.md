# Malaysia

**5 gas rows (GGIT) and 5 oil rows (GOIT).** Gas was swept in full on **2026-08-12** — a §2
reconciliation against **three** sources (a first: GulfPub, OSM, and the newly registered
Malaysian Gas Map), a §3 deep sweep of all 5 rows, and the §6 handoff packet. **Oil has not
been swept.**

Staged, not applied. Counts regenerate via
`python scripts/staged_summary.py --country Malaysia --commodity gas` — never hand-edit them.

**FIVE files to work** — the packet does **not** subsume the recons (`recon_actions = 0`), and
with three sources the recon surface is the larger half of the batch:

- `pipelines_batch_20260812_1344_ET_malaysia-gas_handoff-actions.xlsx` (+ its `-evidence`
  twin) — 8 open decisions, 0 status changes, 15 backend paste units, 2 operators/owners
  units, 6 wiki updates, 21 open flags; evidence side 5 confirmed audits, 5 fill-detail and
  31 ref-detail rows.
- `pipelines_batch_20260812_1343_ET_malaysia-gas_reconciliation-gulfpub.xlsx`
- `pipelines_batch_20260812_1343_ET_malaysia-gas_reconciliation-osm.xlsx`
- `pipelines_batch_20260812_1343_ET_malaysia-gas_reconciliation-malaysian-gas-map.xlsx`
- `pipelines_batch_20260812_1344_ET_malaysia-gas_deepsweep.xlsx` (the per-leg sweep workbook;
  its decisions are carried into the actions file — work the actions file)

**Read the escalation memos before working any of it:**
`notes/escalation-2026-08-12-malaysia-gas-recon-scope.md` (the scope ruling, the GulfPub
status conflicts, P7105, and the OSM-independence retraction) and
`notes/escalation-2026-08-12-length-ratio-band-vs-route-accuracy.md` (our own Leg-2 defect,
fixed the same day).

Row profile — all five are `Fuel = Gas`, all researcher **WA**, and four of five were last
touched in **2023**:

| PID | name | status | LengthKnownKm | RouteAccuracy | LastUpdated |
|---|---|---|---|---|---|
| P1065 | Peninsular Gas Utilization Pipeline | operating | 2,623 | very high (within meters) | 2023-08-31 |
| P1066 | Sabah–Sarawak Gas Pipeline (SSGP) | operating | 512 | very high (within meters) | 2023-08-31 |
| P1067 | Trans Sabah Gas Pipeline | cancelled | 662 | low | 2025-08-19 |
| P1068 | Trans Thailand–Malaysia Gas Pipeline (TTM) | operating | 267 | very low (straight line/schematic) | 2023-08-10 |
| P7105 | Malaysia Singapore Gas Pipeline | operating | 70 | **no route** | 2024-10-01 |

## What defines Malaysia: under-coverage, and GOIT already maps the oil half

Malaysia's defining fact is not a data defect inside the rows — it is **how few rows there
are**. Five GGIT gas rows against Indonesia 50, Australia 151, Thailand 34, Vietnam 15,
Philippines 13, Myanmar 9. Three independent sources describe roughly 150 Malaysian gas
pipelines between them, and all three tripped the >30-additions escalation gate in a country
with five rows: GulfPub 51 additions (41 discovery candidates), Malaysian Gas Map 67 (65),
OSM 29 (8).

The sharpest evidence that this is under-coverage rather than a matcher artifact is
**cross-tracker**: GOIT carries five Malaysian *oil* rows — P7908–P7912, all `operating`, all
`high` accuracy, all added by **IM in February 2026** — on the very offshore corridors GulfPub
proposes on the gas side (P7912 Erb West–Labuan 143 km vs GulfPub's `Erb West - Labuan`
136.8 km; P7908 Gumusut Kakap–Kimanis 200 km vs `Limbayong - Kimanis` 169.0 km). Excluding the
gas feeders while GOIT maps the oil ones leaves GEM tracking half of one physical bundle.

**This is a ruling, not a task.** Nothing is staged as a discovery addition. Either the
offshore field-to-shore gas feeders are in GGIT scope — in which case Malaysia is a Discovery
campaign of ~30–65 candidates, not a handoff item — or they are not, in which case the
exclusion belongs in this file as a stated inclusion rule so no future sweep re-litigates it.

## Gotchas

- **OSM is NOT an independent check on P1065/P1066.** Both rows' `Route [ref]` cells cite
  `openinframap.org`, which renders OSM data, so GEM's geometry was traced from the thing that
  is being used to confirm it. The 92% containment the OSM run reported is the correct
  *diagnosis of a null run* (the geometry is already in GEM, so nothing was left to match) but
  carries **no corroborative weight** and must never be counted toward the 2-independent
  target. General rule this batch established: **read the `Route [ref]` cell before crediting
  any geometry source as independent.**
- **The GulfPub run was rebuilt at `1343_ET` after a same-day engine fix; the `1256_ET`
  workbooks were deleted.** The reference-side country filter tested plain equality against one
  normalized country, so every record whose country field names more than one country
  (`Thailand / Malaysia`) was silently dropped. Malaysia went **50 → 55** GulfPub refs and
  **46 → 51** additions. The one that matters: `gulfpub:gas:2006` **is P1068** (Trans
  Thailand–Malaysia, 254.3 km, operating, JDA→Kangar) — before the fix P1068 sat in `gem_only`
  with no reference support at all. It lands as a `NEAR_MISS` at composite 0.4207, 0.03 under
  threshold, purely because P1068's schematic straight-line route scores near-zero IoU against
  a real trace. **Do not lower the threshold.** Two consequences: P1068 **is** corroborated
  (254.3 vs 267 km is a 5% delta, agreeing on status and the Kangar landfall), and GulfPub's
  trace is a **route-improvement candidate** for it.
- **Two of the three recon runs are `MATCH_QUALITY` null runs** (OSM and Malaysian Gas Map:
  0 matched rows each). A null run is a claim about the matcher until its health line is read —
  neither is a discovery set, and neither should be "fixed" by lowering a threshold.
- **P1065 is a NETWORK row, not a segment row.** Its `LengthKnownKm = 2,623` is PGB's own
  published figure for the whole PGU system (mainline + Loop 1 + Loop 2 + laterals, confirmed
  by OGJ); the drawn route is the ~1,214 km mainline. The 0.46 length ratio is
  segment-vs-network granularity, **not** a length defect — it was researched and closed with
  no value change.
- **P1067's route is drawn wrong but its length is right.** 662 km is confirmed by three
  independent sources (Sinar Project/Politikus, AidData's China Eximbank loan record,
  Malaysiakini); the drawn 380 km LineString simply omits the Sandakan detour. That is a
  **routes-repo follow-up**, not a length change, and `RouteAccuracy` stays `low`.
- **A blank `Operator` here is the tracker norm, not a Malaysia defect** — the column is filled
  on 22.53% of rows tracker-wide and 18.44% of gas rows. Do not import India's reading, where a
  blank `Operator` *was* a genuine gap.
- **The Malaysian Gas Map is the registry's first digitized document** (vector wall map,
  Malaysian Gas Association 2022 ed.) — its per-segment labels are provably unreliable, so it
  corroborates *corridors*, never attributes. Quirks in
  `sources/malaysian_gas_map/NOTES.md`; the as-delivered artifacts are tracked in
  `sources/malaysian_gas_map/extraction/` and `prepare.py` re-derives the ingest input.

## Open items

1. **The scope ruling** (above) — blocks any Discovery work. Nothing else in the batch depends
   on it.
2. **P1066 status.** GulfPub splits the 512 km line into a 386.2 km *closed* section
   (Lawas→MLNG Bintulu) and a 112.7 km *operating* section (Kimanis→Lawas); the two sum to
   498.9 km against GEM's 512, so the segmentation reconciles to GEM's own length. GEM's row is
   wholly `operating` with **no `Status [ref]`** and `LastUpdated 2023-08-31`. A tier-2 dataset
   never settles a status alone → verify against Petronas / Malaysian press, then Update.
3. **P7105 existence/duplicate.** The one row **no source corroborates**. Its 70 km cannot be
   spanned by its own stated endpoints: P1065's drawn route ends at the Johor Bahru Causeway
   (1.4578 N, 103.7680 E), from which the Attap Valley ORF is 5.8 km and Pasir Gudang 8.9 km.
   Do **not** treat this as a length fix — the unspannable length is evidence about what the
   row *is*. Either it describes something other than its endpoints, or it restates PGU
   capacity already carried on P1065.
4. **P1066 `Operator`** — the batch's only staged value change (blank → `PETRONAS Carigali Sdn
   Bhd`, operators/owners tab, **medium**). Two other readings are defensible and are stated in
   the row's notes: the 2017 O&M agreement appears on *PGB's own* milestone timeline, whose
   natural reading makes **PGB** the operator and PCSB the asset-owning counterparty; or leave
   it blank. Reviewer's call.
5. **P1067's route** — redraw via Sandakan (routes-repo branch + PR; not authorized here).
6. **P1068's route** — GulfPub's real trace against GEM's `very low` straight line. A
   route-improvement candidate, same handling as P1067's: routes-repo branch + PR, never an
   auto-replacement.
7. **Oil (5 rows, P7908–P7912) has never been swept.** They are recent (IM, Feb 2026) and
   `high` accuracy, so they are the low-priority half — but they are also the rows that make
   the gas scope question concrete.
