# Staged-JSON contract

The machine-readable interface between this repo's research output and any apply-side
tooling (Baird's manual paste workflow today; the goig-ggit-data-ops repo tomorrow).
**Treat this document as the contract** — if a field changes, version-note it here.

Two files, both living in the per-scope staging dir
(`batches/<scope>/staging/<run>/`, committed as the audit trail):

- `staged_resolutions.json` — Country Sweeps (any preset: refs-only, deep, in-dev).
- `staged_new.json` — discovery candidates.

Handoff packets additionally write two **sidecars** next to them (workbook-render
inputs only, never apply targets, so they stay outside this contract's apply
semantics): `qc_flags.json` (mechanical-check flags incl. the `Existence_support`
ref-thinness check; `staged_note` marks prior coverage) and `staged_actions.json`
(see below). Both are produced by `scripts/build_qc_staging.py`; after the Leg-3
merge, regenerate them only with `--sidecars-only` (a full re-run would clobber the
merged records in `staged_resolutions.json` — the script guards against this).
An assembled packet's `staged_resolutions.json` carries `meta.mode: "handoff"`
(older packets say `"qc"`; both mark the dir as assembled, so
`staged_store.discover_staging_dirs` never re-imports it as prior work).

### Review-app sidecars (`review_log.jsonl`, `review_decisions.json`)

Written by `review_app/` (`store.py`) into each staging dir it reviews, committed with the batch;
they hold decisions ABOUT staged records and never change `staged_*.json`. A record is keyed
`<dir label>::<pid>|<sheet_row>|<colid>` (`dir` label = path relative to the repo root).

- `review_log.jsonl` — append-only truth, one JSON record per click, never edited. **Latest record
  per `key` wins.** An undo appends a record with `undecided: true`. A torn last line is skipped.
  - Line record (`ref`, `fill`, `status`, `oo`, `route`, `new_row`): `{key, dir, pid, sheet_row,
    ref_col, kind, decision, suggested_value, note, reviewer, ts, undecided}`; `decision` is
    `accept | hold | reject | suggest` (`suggest` needs a `suggested_value` or a `note`).
  - Item record (`concern`, `wikidiff`, `routeqc`, `route_suggestion`, `monitor`, `flag`,
    `escalation`, `unresolved`, `confirmed`, `other`): `{key, dir, pid, kind, call, note, reviewer,
    ts, undecided}`; `call` is `confirmed | dismissed | needs_research` for `concern`,
    `noted | todo | dismissed` for the rest. Items never write a cell. Any call on a concern
    releases its contested-column lock; accepting a line whose proposed value equals a contested
    value also writes a `dismissed` item record ("resolved by accepted <col> fill").
  - `reviewer` and `ts` (ISO-8601, America/New_York) are stamped server-side. Machine reviewers
    (`MACHINE_REVIEWERS` = `backend sync`, `push`) are honest records of what wrote them but are
    not a click: a line whose latest record is one, or an undo, counts as NOT reviewed, and
    consumers that want "clicked accepts only" check for that.
- `review_decisions.json` — derived: `{"generated": ts, "decisions": {key: latest record}}`,
  regenerated atomically from the whole log after every append (log rolled back if it fails).
  Consumers read it (and the log) through `review_app/decisions.py`, which matches a staged
  record by `(pid, colid)` with `sheet_row` breaking ties, because sheet rows drift.

### `staged_actions.json` (sidecar — render input, NOT an apply target)

The full carried-in staged-work join: EVERY pending action from the scope's prior
staging dirs (auto-discovered by country+commodity), so nothing staged stays buried
in an earlier packet's workbook. It **duplicates** records whose canonical home is
the source dirs' `staged_resolutions.json`/`staged_new.json` — apply from those,
never from this sidecar. Shape:

```json
{ "meta": { "mode": "handoff_actions", "country", "commodity", "csv",
            "staged_dirs": [...], "counts": {...} },
  "concerns": [...], "status_changes": [...], "fills": [...],
  "ref_work": [...], "routes": [...], "new_rows": [...] }
```

Records are the source dirs' records (trimmed to the fields the workbook renders)
plus, on every record: `source_dir` (provenance — which staging dir holds the full
canonical record) and a `sheet_row` re-resolved against THIS packet's snapshot
(the original kept as `source_sheet_row` when it differed). Carried concerns also
get `also_flagged` (this packet's own wiki/mechanical flags on the same
(project_id, concern-type) — cross-reference, not duplication). `concerns` carries
ALL concern types; `status_changes` only verdicts ≠ `confirm` (confirms are
counted in `meta.counts.status_verdicts`); `ref_work` only actionable classes
(`REFS_ADDED`/`DEAD_LINK`/`REF_BLOCKED`/`REF_UNSUPPORTED`/`UNRESOLVED`; `REVERIFIED` is counts-only);
`new_rows` all discovery classes. Version note (2026-07): `staged_actions.json`
replaces the retired `existence_carryover.json` (which carried only
existence/duplicate concerns); the workbook builder still renders a legacy
`existence_carryover.json` through the same Concerns tab if no
`staged_actions.json` is present.

Nothing in either file is ever auto-applied. Every URL has passed
`scripts/url_verifier.py` (HTTP 200 + value present) and the blocklist
(no gem.wiki / globalenergymonitor / theodora / wikidot / abarrelfull).

---

## `staged_resolutions.json`

```json
{ "meta": { ... }, "resolutions": [ { ... }, ... ] }
```

**meta** (all optional but conventional): `commodity` (`"oil"|"gas"`), `scope`
(`{tracker, country, csv, statuses?}` — `csv` is the snapshot basename in `data/`),
`generated`, `n_units`, `class_out_counts`, `class_in_counts`, `n_validity_flags`,
`n_fills`, `n_status_reviews`, `verdict_counts`, `concern_counts`,
`status_verdict_counts`, `counts` (added by the workbook builder).

**Common record core** (every resolution):

| field | type | meaning |
|---|---|---|
| `project_id` | str | GEM ProjectID (`P####`) |
| `sheet_row` | int | live-sheet row (`CSV index + 4`) |
| `pipeline_name`, `segment_name` | str | identity, from the snapshot |
| `ref_col` | str | the `[ref]` column this record targets; sentinels `__VALIDITY__` / `__REDUNDANCY__` / `__STATUS__` / `__ROUTE__` / `__WIKIDIFF__` / `__ROUTEQC__` mark non-ref records |
| `value_cols` | [str] | the value columns the ref cluster governs |
| `primary_value_col`, `primary_value` | str | the headline value |
| `values` | {col: value} | exact column→value payload (for FILL/STATUS: the proposed edits) |
| `current_ref` | str | the `[ref]` cell content before this batch |
| `class_in` | str | `HAS_REF` \| `MISSING_REF` \| `FILL` \| `VALIDITY` \| `STATUS` |
| `class_out` | str | see per-type tables below |
| `proposed_refs` | [url] | verified URLs to paste (never fabricated; may be empty) |
| `verifications` | [{url, ok, contains_value}] | url_verifier results |
| `tier` | str | `high` (≥1 validated ref; status change ≥2 independent) \| `medium` \| `low` |
| `independent` | bool | ≥2 independent sources reached |
| `source_language` | str | e.g. `"en"`, `"ar"` |
| `researcher_notes` | str | rationale; `[QC]`-prefixed notes were added at merge |
| `tab` | str? | `"operators_owners"` = targets the ProjectID-keyed operators/owners tab (GID 1489950650), not the tracker |
| `wiki` | str? | gem.wiki page visited (never cited) |

Every `MISSING_REF` unit in a run's `worklist.json` is owed one of these records — sources
that agree with the value already on the sheet produce a `REFS_ADDED` carrying that same
value, which is the leg's product, not a no-op (standing rule 4e). A seeded `MISSING_REF`
record left `UNRESOLVED` with no refs and no `researcher_notes` is a silent skip, flagged by
`sweep_gates.py` gate L and by `scripts/check_shard_coverage.py` before the shard is written.

**Ref records** (`class_in` `HAS_REF` / `MISSING_REF`): `class_out` ∈ `REFS_ADDED` /
`REVERIFIED` / `DEAD_LINK` (every link 404/410) / `REF_BLOCKED` (could not fetch) / `REF_UNSUPPORTED` (loads, screen missed the value) / `UNRESOLVED`. Apply = paste `proposed_refs` into the
`ref_col` cell of `sheet_row` (or, when `tab="operators_owners"`, into that ProjectID's
row on the operators/owners tab).

**Fill records** (`class_in="FILL"`): a previously blank value researched. Apply = write
`values` into their columns AND `proposed_refs` into `ref_col` — never one without the
other (no orphan values/refs). `class_out` `REFS_ADDED` = corroborated;
`UNRESOLVED` = not corroborated, do not apply.

A few researchable columns have **no paired `[ref]` column in the schema** —
`OtherEnglishNames` is the one this batch hit (US gas P0257, 2026-09-04). Such a fill
carries `ref_col: ""` and empty `proposed_refs`, and states its corroboration in
`researcher_notes` instead; the "never one without the other" rule is about orphan `[ref]`
*cells*, and there is no cell to orphan. It still classes `REFS_ADDED` when corroborated,
because that value means *corroborated* and the vocabulary has no other word for it —
inventing a `FILL` class instead makes the record invisible to `staged_summary.py` (which
counts `class_in=FILL` + `class_out=REFS_ADDED`) and drops it from the handoff's
`AllFillsBackend` paste surface, which filters on the same pair.

**Validity records** (`ref_col="__VALIDITY__"`): read-and-flag only, never an edit.
Extra fields: `verdict` (`"confirmed (caveat)"` \| `"concern"`), `concern_type`
(`existence`/`duplicate`/`classification`/`attribution`/`spec`/`none`),
`recommendation` (short human next step), and — on a `concern` — **`contested`**:
`{backend column: candidate value}`, the cells the finding disputes, with the candidate
replacement where the evidence supports naming one and `""` where it only says the
current value is wrong. `class_out` is always `UNRESOLVED`.

`contested` is what puts a concern on the **paste surface**. A validity record proposes no
edit, so it is filtered out of the `<Cmdty>_Backend` mirror; `contested` lets the builder
tint the disputed CURRENT value **orange** there (deliberately outside the green/yellow/
red/blue tier palette — those mean "paste this", orange means "stop, adjudicate"), with the
finding, candidate and sources in the cell comment. A concern naming no column still tints
the row's `SheetRow` locator. Omit it and the finding is visible only on the `_Validity`
tab — which is exactly how P0271/Transco's Capacity, contradicted by its own cited ref,
read as an ordinary untouched cell in the US-gas TX batch (2026-09-04). Backfill records
staged before the field existed with `scripts/backfill_contested.py`.

**`__REDUNDANCY__` is a shard-only sentinel, not a stored `ref_col`.** Research subagents
emit it when answering "is this row a double-count?", but it has no baseline record, so
`merge_ref_shards.py` drops it with a WARN. `harvest_sentinel_findings.py` re-appends each
one **as a `__VALIDITY__` record** (marked `harvested_from_shard: true`, `class_out:
UNRESOLVED`), which is the only shape that reaches a store or a workbook. So: expect
`__REDUNDANCY__` in `shards/`/`ref_shards/`, never in a merged `staged_resolutions.json`.
The cluster-level redundancy pass (`staging/redundancy/`) likewise stages plain
`__VALIDITY__` records — one per implicated row, carrying the cluster's ruling.

**Status records** (`ref_col="__STATUS__"`, annual-update mode): one per in-dev segment
row. Extra fields: `current_status`, `verdict` (`confirm`/`change`/`stale`/`unclear`),
`proposed_status`, `evidence_date` (YYYY-MM of the newest independent evidence),
`staleness_rule` (`""` \| `"2y->shelved"` \| `"4y->cancelled"`). `class_out` mapping:

| verdict | class_out | apply semantics |
|---|---|---|
| `confirm` | `CONFIRMED` | no edit; evidence date recorded |
| `change` | `CHANGE_PROPOSED` | write `values` (Status + date cols) + paste `proposed_refs` into `Status [ref]` |
| `stale` | `STALE` | write `values` (includes `ShelvedCancelledType=inferred`); **no ref by design** — it is an inference |
| `unclear` | `UNRESOLVED` | no edit; see notes |

Merge-time QC guarantees (enforced by `scripts/merge_deepsweep_shards.py`): no
`proposed_ref` without a passing `ok && contains_value` verification; a `change` with
zero verified refs is downgraded to `unclear`; a `stale` shelved/cancelled inference
always carries `ShelvedCancelledType=inferred`.

**GOTCHA — re-running the merge is destructive when a leg was enriched after its first
merge.** `merge_deepsweep_shards.py` regenerates every FILL/VALIDITY/STATUS/ROUTE record
from `rows/<PID>.json`, so any *post-merge* edit made directly to
`staged_resolutions.json` — most importantly a harvest/verification step that upgrades a
fill's `class_out` from `UNRESOLVED` to `REFS_ADDED` — is silently reverted to the
shard's pre-harvest state. Record counts stay identical, which is why it is easy to miss;
compare the `class_out` distribution against `git show HEAD:<path>` after any re-merge.
(Hit on 2026-07-28: re-merging `batches/iraq-gas/staging/ref-sweep-operating/` to amend
two records knocked `REFS_ADDED` 120 → 52 and `UNRESOLVED` 225 → 288.) To amend a record
in an already-harvested leg, **edit both** the shard (provenance, so a future re-merge
carries the text) **and** `staged_resolutions.json` in place — do not re-merge.

**Wiki-diff records** (`ref_col="__WIKIDIFF__"`, `class_in="WIKIDIFF"`; the §6
handoff packet, `scripts/wiki_alignment.py`): one per (pipeline, field) sheet↔wiki mismatch;
read-and-flag, never an edit. Extra fields: `field` (sheet column), `wiki_key` (label
as displayed on the page), `sheet_value`/`sheet_value_norm`, `wiki_value`/
`wiki_value_norm`, `staged_value`/`staged_source` (when the sheet cell has a staged
pending correction), `staged_note` ("known — staged (...)" when a prior packet's
concern covers the field), `action` (human next step), `severity` (`flag`/`info`).
`class_out` ∈ `WIKI_UPDATE` (edit the wiki page) / `SHEET_SUSPECT` (verify
independently, then fix the sheet) / `WIKI_STALE_VS_STAGED` (apply the staged packet
first) / `UNPARSED` (no Wiki URL or unparseable page). The common-core ref fields are
present but empty so merge/apply tooling passes these records through untouched.

**Route-QC records** (`ref_col="__ROUTEQC__"`, `class_in="ROUTEQC"`,
`class_out="ROUTE_FLAG"`; `scripts/route_integrity.py`): one per (pipeline, failed
check); read-and-flag, never an edit — a route is never auto-replaced. Extra fields:
`check` (`length_ratio`/`countries`/`null_geometry`/`degenerate`/`endpoint_country`),
`measured` (from the drawn GeoJSON), `expected` (from the sheet), `detail`,
`severity`, `route_accuracy`, `staged_note`. Distinct from `__ROUTE__` records
(route *suggestions* staged by a sweep's `routes` leg — see the Sweep SOP "Schema
extensions"); a `__ROUTE__` suggestion for the same PID annotates the `__ROUTEQC__`
flag as "known — staged".

**Route-candidate records** (`ref_col="__ROUTE__"`, `class_in="ROUTE"`,
`class_out="ROUTE_CANDIDATE"`; the §8 Route-creation workflow, `build_route_candidate.py`;
added 2026-07-22): one per PID — drawn geometry staged as a routes-repo-valid
`candidate_routes/<PID>.geojson`, destined for a **human branch+PR against the routes
repo** (or the per-batch-authorized agent apply, `workflows.md` §8 step 6 —
`suggested_route_accuracy`, the `researcher_notes`, and `proposed_refs` are exactly
what `scripts/apply_route_candidates.py` writes to the sheet's route columns).
The `method` is a *field*, not a family of class_outs (one
`class_out` for all rungs). Extra fields:

| field | meaning |
|---|---|
| `method` | `gulfpub_sidecar` \| `arcgis` \| `osm` \| `digitized` \| `endpoints_greatcircle` |
| `geometry_file` | path to the candidate geojson (relative to the staging dir) |
| `source` | `{name, url, ref_id?, license, odbl, fetched_utc, layer_meta?}` |
| `georef` | `{order, n_gcps, rmse_km, loo_rmse_km, pass}` (rung-3 only) |
| `endpoints` | `{start{name,lon,lat,ref,anchor?}, end{…}, snapped}` |
| `length_km`, `sheet_length_km`, `length_ratio` | measured vs sheet, and their ratio |
| `current_route_accuracy`, `suggested_route_accuracy` | current vs the rung's cap |
| `replacement` | true when an existing GEM route is being replaced (yellow fill) |
| `geometry_signals` | IoU / endpoint / Hausdorff / g_score vs any existing GEM route |
| `qc_passed`, `qc` | gate verdict + `{errors, warnings, checks}` (FAIL ⇒ red QC cell, listed not dropped) |
| `facility_anchors` | `[{gem_id, name, source, role, dist_km, citable:false}]` — GOGET/GOGPT usage, **audit only, never a citation** |

The common-core ref fields (`values` empty, `proposed_refs`, `verifications`, `tier`,
`independent`) are present so merge/apply tooling passes these records through
untouched; the downstream carry predicate (`class_in=="ROUTE" or ref_col=="__ROUTE__"`)
is `class_out`-agnostic, so a §6 handoff auto-carries them. `build_ref_workbook.py`
renders the `<Cmdty>_RouteCandidates` tab.

---

## `staged_new.json`

```json
{ "meta": { "scope": {tracker, country, csv}, "class_counts": {...}, "n_candidates": n },
  "candidates": [ { ... }, ... ] }
```

Per candidate:

| field | type | meaning |
|---|---|---|
| `slug` | str | filesystem-safe id (empty for consolidator-level matches) |
| `class` | str | `new_row` \| `monitor` \| `matched_existing` |
| `name` | str | best project name |
| `matched_project_id` | str | the existing `P####` when `matched_existing` |
| `values` | {GEM col: value} | exact tracker column names, controlled vocab respected |
| `refs` | {`X [ref]` col: [url]} | verified URLs per ref column; every filled value has one, and vice versa |
| `verifications`, `tier`, `independent`, `source_language`, `researcher_notes` | | as above |
| `monitor_reason` | str | for `monitor`: which add-threshold leg failed |

Apply semantics: `new_row` = a candidate new tracker row (green in the workbook) that
cleared the add-threshold (sponsor + geography + concrete step); `monitor` = watch, do
not add; `matched_existing` = add `name` to the matched row's `OtherEnglishNames`, no
new row. Merge-time QC (`scripts/merge_discovery_shards.py`): blocklist strip, no orphan
values/refs, a `new_row` left with zero verified refs is downgraded to `monitor`.
