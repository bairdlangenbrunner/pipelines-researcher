# Review app intake: every deliverable lands in one accumulating review surface

Status: PLAN, 2026-10-02. Nothing below is built. Companion to
`docs/plans/2026-09-30_review-app.md` (the app itself) and `review_app/README.md`.

## Goal (Baird 2026-10-02)

Whenever a new country (or a new batch for an included country) is researched, its deliverable
is ADDED to the previous ones and shows up in the review app without rework. The app is the one
accumulating review surface; the handoff workbook is a derived view of the same staged work
(`build_ref_workbook.py --decisions`), not the primary deliverable.

Most of the machinery exists: `batches/review-app/manifest.json` lists included countries,
`review_data.build` discovers each included country's staging dirs fresh on every build, and
`publish.py` ships one `review-app-<commodity>` scope over all of them. What is missing is an
**intake contract** that every batch type satisfies, and three gaps the 2026-10-02 audit found:

1. Reconciliation output never reaches the app (1 of 36 recon dirs holds a store file).
2. Severity trusts the staging: a record whose `values` drift from the sheet reads as a major
   change even when the researcher meant "confirmed as recorded".
3. One-off scripts count only when they write the canonical store files; a dir without one is
   invisible, and nothing says so at delivery time.

All three are the same defect from different angles: staged work that is not readable by
`review_data.py`, or readable with the wrong meaning.

## Measurements behind the plan (2026-10-02 dataset, Russia + US gas, 7,795 lines)

| What | Count |
|---|---|
| fill / oo lines carrying a `change` op | 347 |
| changed cells on those lines | 900 |
| changed cells whose `researcher_notes` never mention the old value | 46 |
| change lines with fewer than 2 proposed refs | 131 |
| change lines tiered `high` (default accept) | 331 |
| line-level changes that are only casing / whitespace | 2 |
| numeric formatting-only changes (`150.00` vs `150.0`) | 0 (`_same` already equates them) |
| recon staging dirs / with a store file | 36 / 1 (Iraq `recon-gulfpub-followup`) |
| update-store dirs (`staged_updates.json`) the app cannot read | 4 (2 US oil, Israel validation, owners-style) |

So caveat 2 is not a formatting problem. It is that a value change is staged with the same
shape, tier and default as a ref-only fill, and the gates never ask a change to justify itself.

---

## Phase A: the intake contract (small; do first)

**A1. Define "in the app".** A staging dir contributes to the review app iff it holds a store
file whose `meta` names the scope: `staged_resolutions.json`, `staged_new.json`,
`staged_updates.json`, or (Phase C) `match_diff.json`, with `meta.scope.country` (or
`meta.country`) and a commodity. Everything else in `staging/` is working material. Write this
in `review_app/README.md` (new section "Intake") and in the Update SOP step for one-off
batches: *a one-off script that does not write a conformant store file has not delivered*.

**A2. Intake check, run at every delivery.** New `review_app/intake.py check <dir> [...]`:
builds the dir alone through `review_data.build` (snapshot = newest), and reports
lines / items by kind, records that fell to kind `other` (with their `class_in`/`class_out`),
missing columns against the snapshot, records with no `project_id`, and whether `scopes.py
check` would ask. Exit 2 when the dir is unreadable (no store file / no scope meta), exit 1 on
`other` records or missing columns. Add it as the last step before the review-app ask in
`docs/workflows.md` §2 to §8 (one line each) and to the QC SOP pre-delivery checks.

**A3. Make the invisible visible.** `review_data.build` already computes `country_status`;
add `unreadable_dirs` per country: children of the scope dir (`batches/<slug>-<commodity>/staging/*`)
with no store file, minus known working-material kinds (`route-creation*` with only `_tmp_*.json`,
`discovery-*` with only `work/`, `state-audit-*`, `scoping-*`, `eia-crosswalk-*`,
`recon-*` until Phase C). The page shows them in the "all decided, hidden" strip as
"N dirs not readable"; `scopes.py list` prints them. `staged_summary.py --index` already labels
these "no store, invisible to discovery": keep the label, link it to this contract.

**A4. Read the update store.** `review_data._load_dir` opens only four files; `staged_updates.json`
(Update SOP step 6 shape: `rows[pid] = {pipeline, sheet_row, changes, research}`) is not one of
them, so every Update-mode batch, including the US oil one-offs, is invisible even when scoped.
Add a reader: each `changes` entry becomes a `fill` / `status` / `oo` line with the same key
shape (`<dir>::<pid>|<sheet_row>|<colid>`), `class_in="FILL"`, `class_out="REFS_ADDED"`,
tier from the record (default `medium`); each `research` entry becomes a `concern` item.
`update_seed.py` already emits this shape, so the reader doubles as its consumer.
(`store.sync_backend`, `push.py` and `basis` need no change: they work on built lines.)

**A5. Tracker-wide batches.** The owners-style batch is unscoped on purpose
(`meta.country = ""`). Give the manifest a `tracker-wide` entry (country `*`, commodity `both`)
that the batch build includes when answered yes, rendered under its own country checkbox and
never merged into a country's view. Optional; decide with Baird (question 4 below).

Docs touched: `review_app/README.md`, `docs/workflows.md` (review-app batch block + one line per
section), `docs/sops/update.md`, `docs/sops/qc.md` pre-delivery list, CLAUDE.md "Routing notes".

---

## Phase B: severity that cannot be gamed by sloppy staging

Severity itself is right: what a line does to the cells. The fix is upstream (a change must
justify itself at staging) plus two signals in the app so an unjustified change is visible and
is never a default accept.

**B1. Staging gate (blocking, per shard).** `scripts/check_shard_coverage.py` already blocks an
`UNRESOLVED` record whose `values` move a sheet cell (line ~207). Extend the same block to
`REFS_ADDED` / `REVERIFIED` records: for each `values[c]` where the sheet cell is non-empty and
`not merge_qc._same(cell, value)` (reuse `review_data._same` semantics: numeric equality after
comma strip), require BOTH (i) the old value appears in `researcher_notes`, and (ii) at least two
proposed refs (rule 4, precise value over rounding). Failing (i) or (ii): BLOCK with
"value change without stated basis: set `values` to the sheet's (ref-only) or record the old
value and a second ref". A casing / whitespace-only difference is allowed with (i) alone.

**B2. Delivery gate (per store).** Same test as a new `sweep_gates.py` gate (call it gate N),
report mode first so existing batches can be measured; blocking for new batches once the
backlog is reported.

**B3. Tier.** `merge_qc` treats a value change like a status change: a single-publisher change
caps at `medium` (parallel to `STATUS_CHANGE_MIN_PUBLISHERS`), so the app's default is `hold`.
Today 331 of 347 change lines are `high` and default to accept.

**B4. App signals.** `review_data._line` adds `change_basis`: `[]` when fine, else any of
`unexplained` (notes lack the old value), `single_source` (fewer than 2 refs),
`restyle` (casing / whitespace only). `default` is `hold` whenever `change_basis` is non-empty,
whatever the tier. The chip reads `major · change (single source)`; a `basis` facet filters on
it; the "accept all minor changes" bulk button is unaffected (these are major). `summary()`
counts them so the publish log and the session summary show the backlog.

**B5. Backfill report.** Run B2 in report mode over every dir in the included scopes and attach
the offender list to the country notes (`docs/country_notes/russia.md`, `united-states.md`).
Repairs are per batch (re-stage the record), never edits to the app.

---

## Phase C: reconciliation intake

Standing rules kept: a scraped dataset is one source in a conflict, never authoritative; a
reference value is never auto-applied; a Tier-2 source never reaches green alone. So recon
output becomes **items** (a call plus a note), never lines, and a `todo` call is the handoff to
Update, which turns it into a resolution record the normal way. The standalone §2 workbook stays
as the detailed view; the app carries the decisions.

**C1. Recognize the dir.** Add `match_diff.json` to `staged_store._STORE_FILES` with its own
meta reader (`meta.country`, `meta.commodity`, `meta.source`; mode `recon`). Check the three
consumers of `_STORE_FILES` (`discover_staging_dirs`, `scopes.researched`, `staged_summary`)
and `load_staged_context` (must tolerate a dir with no resolutions). `build_ref_workbook.py`
must not start carrying recon dirs as "prior staged packets" without the crosswalk step; guard
by mode.

**C2. Newest run per source wins.** For one scope and source, only the newest
`recon-<source>-<date>` dir contributes; older ones are listed as superseded in
`country_status`. One-time cleanup: move the superseded dirs (Egypt gulfpub 0708 / 0812, Iraq
gulfpub 0705 and oil 0603, Egypt osm 0729) to `archive/` so the lifecycle stays "by move".

**C3. What becomes an item** (new kind `recon`, calls `noted / todo / dismissed`):

| Bucket | Item | Attached to |
|---|---|---|
| `status_conflicts` | "source says X, GEM says Y; verify, never auto-flip" | each GEM pid |
| `overlaps` with a disagreement (`s_diameter < 1`, `s_length` below the manifest threshold, or `route_replacement_candidate`) and `coverage != partial` | ref vs GEM values side by side | each `gem_segments` pid |
| `additions`: `ROUTE_FOR_EXISTING`, `NEAR_MISS` | candidate geometry / possible match | `best_guess` pid |
| `additions`: `DISCOVERY_CANDIDATE` | one scope-level item each | scope card |
| `additions`: `FRAGMENT_OF_EXISTING`; `gem_only`; agreeing overlaps | not items (SOP: log only / corroboration); counted in summary | |
| `ambiguous` | skipped in v1, counted (Russia has 225) | |
| run with a `MATCH_QUALITY` escalation or a coverage verdict `not_reconciliation_grade` | ONE scope-level item, nothing else from the run (Libya OSM) | scope card |

Key: `<dir>::<pid>|<sheet_row>|__RECON__:<source>:<bucket>:<ref_id>`. Item body shows the
source tier and license line (OSM is ODbL, geometry reuse is Baird's call).

**C4. Re-runs carry decisions.** A re-run is a new dir, so `publish.carry_forward` (which
matches on dir + pid + column) would orphan every recon decision. Extend it: when the superseded
dir (C2) holds a decision whose `ref_id` and pid match an item of the new run, copy it under the
new key with `rekeyed_from`. GulfPub `oid` and OSM ids are stable (OSM id fix 2026-08-26).

**C5. Volume gate.** Build with `--recon` off by default until measured: Russia GulfPub alone is
113 status conflicts + ~190 near misses + 2 discovery candidates + the disagreeing overlaps.
Measure across the included countries, then decide the default and whether near misses need a
composite floor.

**C6. The two one-offs.** Iraq `recon-gulfpub-followup` already conforms. Libya
`recon-osm-20260728/staged_recon_verdicts.json` is nonstandard: write its coverage verdict as
`escalations.json` in that dir (one entry) so the app shows it; leave the file as the memo.

**C7. Follow-on.** `update_seed.py` reads recon items with call `todo` as seeds, so the
Update batch starts from the clicks.

Docs touched: Reconciliation SOP §5 (the app route beside the crosswalk route), QC SOP handoff
contract (the xlsx is still not carried; the app is), CLAUDE.md "Recons standalone" pointers and
the routing note on `disposition`.

---

## Phase D: scale, once more countries are included

- **Per-country parts.** `publish.py` splits parts by size; with 10+ countries the page loads
  everything to show one. Split parts by country instead, keep `index.json` whole, and load the
  ticked countries' parts (`gas.js`). The dataset is 38 MB for two countries today.
- **Oil scope.** No oil country is included; the manifest and publish already support
  `--commodity oil`. Nothing to build, but the first oil batch exercises A2 to A4.
- **Country notes.** Replace "N files to work" with "in the review app since <date>" once a
  country is included; `staged_summary.py` already prints decided counts.

## Decisions for Baird

1. Recon in the app as items (Phase C), or keep the §2 workbook as the only recon surface?
2. Phase C v1 skips `ambiguous`; agree?
3. A value change with one source or no stated old value defaults to `hold` even at tier high (B4), and caps at `medium` (B3). Agree?
4. A `tracker-wide` manifest entry for the owners-style batch (A5), or leave it outside the app?
5. Archive the superseded recon dirs by move (C2)?

## Order and size

A (contract, intake check, update-store reader): small, one session. B (gates + tier + app
signals + backfill report): medium, one session plus the backfill run. C (recon): medium to
large, measure first. D: as needed. A and B do not depend on each other; C depends on A1 and A3.
