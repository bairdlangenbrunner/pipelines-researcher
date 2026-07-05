# Staged-JSON contract

The machine-readable interface between this repo's research output and any apply-side
tooling (Baird's manual paste workflow today; the goig-ggit-data-ops repo tomorrow).
**Treat this document as the contract** — if a field changes, version-note it here.

Two files, both living in the per-scope staging dir
(`batches/staging/<scope-slug>/`, committed as the audit trail):

- `staged_resolutions.json` — ref sweeps, deep sweeps, annual-update in-dev sweeps.
- `staged_new.json` — discovery candidates.

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
| `ref_col` | str | the `[ref]` column this record targets; sentinels `__VALIDITY__` / `__STATUS__` mark non-ref records |
| `value_cols` | [str] | the value columns the ref cluster governs |
| `primary_value_col`, `primary_value` | str | the headline value |
| `values` | {col: value} | exact column→value payload (for FILL/STATUS: the proposed edits) |
| `current_ref` | str | the `[ref]` cell content before this batch |
| `class_in` | str | `HAS_REF` \| `MISSING_REF` \| `FILL` \| `VALIDITY` \| `STATUS` |
| `class_out` | str | see per-type tables below |
| `proposed_refs` | [url] | verified URLs to paste (never fabricated; may be empty) |
| `verifications` | [{url, ok, contains_value}] | url_verifier results |
| `tier` | str | `high` (≥2 independent) \| `medium` \| `low` |
| `independent` | bool | ≥2 independent sources reached |
| `source_language` | str | e.g. `"en"`, `"ar"` |
| `researcher_notes` | str | rationale; `[QC]`-prefixed notes were added at merge |
| `tab` | str? | `"operators_owners"` = targets the ProjectID-keyed operators/owners tab (GID 1489950650), not the tracker |
| `wiki` | str? | gem.wiki page visited (never cited) |

**Ref records** (`class_in` `HAS_REF` / `MISSING_REF`): `class_out` ∈ `REFS_ADDED` /
`REVERIFIED` / `DEAD_LINK` / `UNRESOLVED`. Apply = paste `proposed_refs` into the
`ref_col` cell of `sheet_row` (or, when `tab="operators_owners"`, into that ProjectID's
row on the operators/owners tab).

**Fill records** (`class_in="FILL"`): a previously blank value researched. Apply = write
`values` into their columns AND `proposed_refs` into `ref_col` — never one without the
other (no orphan values/refs). `class_out` `REFS_ADDED` = corroborated;
`UNRESOLVED` = not corroborated, do not apply.

**Validity records** (`ref_col="__VALIDITY__"`): read-and-flag only, never an edit.
Extra fields: `verdict` (`"confirmed (caveat)"` \| `"concern"`), `concern_type`
(`existence`/`duplicate`/`classification`/`attribution`/`spec`/`none`),
`recommendation` (short human next step). `class_out` is always `UNRESOLVED`.

**Status records** (`ref_col="__STATUS__"`, annual-update mode): one per in-dev segment
row. Extra fields: `current_status`, `verdict` (`confirm`/`change`/`stale`/`unclear`),
`proposed_status`, `evidence_date` (YYYY-MM of the newest independent evidence),
`staleness_rule` (`""` \| `"2y->shelved"` \| `"4y->cancelled"`). `class_out` mapping:

| verdict | class_out | apply semantics |
|---|---|---|
| `confirm` | `CONFIRMED` | no edit; evidence date recorded |
| `change` | `CHANGE_PROPOSED` | write `values` (Status + date cols) + paste `proposed_refs` into `Status [ref]` |
| `stale` | `STALE` | write `values` (includes `ShelvedCancelledType=Presumed`); **no ref by design** — it is an inference |
| `unclear` | `UNRESOLVED` | no edit; see notes |

Merge-time QC guarantees (enforced by `scripts/merge_deepsweep_shards.py`): no
`proposed_ref` without a passing `ok && contains_value` verification; a `change` with
zero verified refs is downgraded to `unclear`; a `stale` shelved/cancelled inference
always carries `ShelvedCancelledType=Presumed`.

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
