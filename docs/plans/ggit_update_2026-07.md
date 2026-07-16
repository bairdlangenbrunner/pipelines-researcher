# GGIT gas update — program plan (RETIRED 2026-07-15)

> **Retired.** Superseded by the campaign annual-packet mechanism
> (`campaigns/ggit-2026` + `docs/workflows.md §7`); see
> `docs/research_backlog.md §1`. The Process-B tooling below was never built.
> Kept for the row-count scale reference; section refs and SOP names predate the
> 2026-07-15 workflow consolidation (e.g. `ref_sweep.md` is now `sweep.md`).

Plan of record for the mid-2026 gas-tracker update. Numbers from the
`GGIT_gas_snapshot_20260610.csv` pull (4,269 rows). Decisions locked with Baird
2026-06-10: **in-dev first** · stale handled in **tiers** (tier 1 = `LastUpdated`
< 2024) · stale-operating depth = **key fields only** · **global, country-batched**.

**Routes are out of scope for the whole program** (standing exclusion: `Route [ref]`
is dropped by the pair model; `RouteAccuracy`/geometry go through the routes repo).
But **Start/EndLocation backfill is IN scope and prioritized** — it is the stated
prerequisite for the future route-work program (999 / 1,070 rows blank today).

---

## The two processes (reusable, complementary)

### Process R — Ref Sweep (exists; gains modes)
SOP: `docs/sops/ref_sweep.md`. Operates on ref cells; never changes values.
New `--mode` for `build_ref_worklist.py` (worklist filter, same unit model):

| Mode | What gets researched | Cost |
|---|---|---|
| `verify` | HTTP-check existing refs (deterministic); research **replacements for dead/value-missing links only** | cheapest |
| `corroborate` | `verify` + upgrade single-source cells to ≥2 independent | medium |
| `fill` | `corroborate` + research every blank `[ref]` with a filled value | full (today's behavior) |

Plus filters: `--stale-before YYYY-MM-DD` (LastUpdated cutoff), `--ids P…,P…`,
`--fields <list>` (restrict to a key-field subset — the stage-B lever).

**Key fields** (the `--fields key` preset): Status, Capacity, Length, Diameter,
Start (dates), StartLocation/EndLocation (the gas `Location [ref]` 8-col cluster),
Fuel, FuelSource, FID, plus Operator/Owner via the operators/owners tab join.
Excluded from the preset: Background, Proposal, Construction, Delay, Pressure,
SegmentCost, ProjectLevelCost, H2 — researched only in `fill` mode.

### Process B — Backfill (new; research-heavy)
The inverse gap: **value blank** (with or without a ref). New
`build_backfill_worklist.py` emits `MISSING_VALUE` units for the key fields,
same unit schema as Process R (ProjectID, ref_col cluster, sheet_row, OO join).
Research loop per ProjectID (same AGENT_BRIEF pattern, wiki-harvest seed,
`url_verifier` on every URL, in-country languages):

- found + ≥2 independent verified → `class_out:"VALUE_FILLED"`, `proposed_value`
  (controlled vocab respected) + `proposed_refs`, tier high.
- found, single source → `VALUE_FILLED`, tier medium.
- genuinely not determinable → `UNRESOLVED` + ResearcherNotes (no fabricated
  value, no fabricated URL — a blank may be correct, e.g. proposed lines without
  a diameter; say so).
- **No orphan halves ever**: a proposed value always ships with its verified
  ref(s) in the same unit (standing rule).

Deliverable mirrors the ref-sweep workbook: paste-ready `<Cmdty>_Backend` +
`<Cmdty>_OperatorsOwners` tabs — proposed **values** styled as changed cells
(red, per `workbook_conventions.md`), their `[ref]` cells colored by tier.
`build_ref_workbook.py` learns the `VALUE_FILLED` class (value cell gets the
proposed value; today it only writes ref cells).

**How they compose in one batch:** one country batch = one staging dir; run R
worklist + B worklist against the same snapshot, research per-ProjectID once
(an agent sees both its ref units and its value units), stage one combined
`staged_resolutions.json`, build one workbook. Update-SOP checks apply on top
for in-dev rows (status logic 2y→shelved / 4y→cancelled, expansion rule,
divestiture sweep, `entity_lookup.py` for any new owner).

### The ledger (how nothing falls through)
`batches/staging/ggit-update-2026-07/ledger.json` — per ProjectID: which process
× mode × batch covered it, counts by class_out, UNRESOLVED carry-overs. Every
batch build appends. Stage C's worklist = (rows in no batch) ∪ (UNRESOLVED units).

---

## Stages

### Stage A — in-dev (Baird's #2, runs FIRST) — 998 rows
`--status proposed,construction,shelved`, global, country-batched.
Treatment: Process R `fill` (full) + Process B (all key fields; 862/998 rows
have ≥1 key value blank) + Update-SOP validation (status flips, FID, dates).
Queue (rows): China 326 · US 131 · Russia 70 · Brazil 28 · India 24 ·
Saudi Arabia 21 · Australia 20 · Germany 18 · Colombia 18 · Iraq 15 · …
(137 countries; top 25 ≈ 811 rows). China and the US split into ~4 and ~2
sub-batches; the long tail groups into regional batches (e.g. "EU small",
"Latin America", "SE Asia") to keep batches ~30–60 rows.

### Stage B — stale tier 1 (Baird's #1) — 1,854 rows (`LastUpdated` < 2024)
Mostly operating (1,693). Treatment: Process R `verify` on everything +
`corroborate`/`fill` restricted to `--fields key` + Process B key fields
(1,451/1,854 rows key-incomplete). Queue: China 288 · US 256 · Russia 127 ·
Italy 126 · Australia 84 · Pakistan 63 · Germany 56 · Spain 53 · Qatar 48 ·
Bangladesh 48 · … (127 countries). The deterministic `--verify-existing` pass
runs first and is free of agent tokens — it sizes the real research load before
we commit batches. **Stale tier 2** (`LastUpdated` in 2024, 491 rows) is queued
for after the July release, same treatment.

### Stage C — sweep-up (Baird's #3) — ~1,495 rows + carry-overs
Whatever A and B didn't touch: recently-updated operating rows, retired/
cancelled, plus the 9 broken-status rows (8 blank Status, 1 "mixed status" —
fix these early, they're data bugs). Treatment: Process R `verify` (link-rot
pass) + ledger-driven retry of UNRESOLVED units from A/B + final QC workbook
(`build_qc_workbook.py --tracker gas`) as the release gate.

---

## Tooling to build before batches start (~1–2 days)
1. `build_ref_worklist.py`: `--mode`, `--stale-before`, `--ids`, `--fields`
   (with the `key` preset).
2. `build_backfill_worklist.py` (MISSING_VALUE units) — shares `ref_pairs` +
   the OO join; likely a sibling entry point, not a fork.
3. `build_ref_workbook.py`: `VALUE_FILLED` class → write proposed value into
   the Backend value cell (changed-cell red), keep tier colors on refs.
4. Ledger append + stage-C "leftover" worklist generator.
5. Batch-queue generator (country/region grouping from the live snapshot) so
   each batch kickoff is one command.
6. SOP updates: ref_sweep.md gains the mode table; new `docs/sops/backfill.md`;
   workflows.md §7.

## Throughput & timeline (working back from ~July 3)
Saudi 10-row pilot ≈ 108 units, ~6 parallel agents, well under an hour of
research wall-time. Assume 150–250 rows/day sustained with parallel batches and
the deterministic pre-pass shrinking HAS_REF work.

- **Jun 10–12** — tooling above + a 20–30-row combined pilot (R `fill` + B) on a
  mid-size country (e.g. Iraq 15 or Saudi 21 in-dev rows) to calibrate cost.
- **Jun 12–22** — Stage A (998 rows, ~20 batches). Baird pastes as batches land.
- **Jun 18–29** — Stage B (1,854 rows), overlapping once A is flowing; verify
  pass first, research second.
- **Jun 29–Jul 3** — Stage C sweep-up + QC workbook + escalations memo.
- Safety valve: the ledger makes any unfinished tail a ranked carry-over queue,
  not silent gaps; stale tier 2 follows post-release.

## Standing rules (unchanged, echoed)
Never cite GEM/theodora/abarrelfull/wikidot · never fabricate URLs **or values** ·
≥2 independent corroboration target · every URL through `url_verifier` · nothing
auto-applied (xlsx + staged JSON only; Baird pastes) · no orphan ref/value halves ·
escalation gates per CLAUDE.md (plus: a country whose verify pass shows >30% dead
links, or a backfill batch ending >40% UNRESOLVED, stops for review).
