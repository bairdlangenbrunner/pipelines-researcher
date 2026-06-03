# SOP — Reconciliation (GEM ↔ a scraped reference dataset)

Diff a registered external pipeline dataset (GulfPub today; more later) against the
live GOIT/GGIT trackers, and produce a reviewable workbook of candidates. **This SOP
surfaces work; it does not perform it** — fixes go through the Update and Discovery
SOPs. Reconciliation **never edits** the Google Sheet or the routes repo.

Unlike the LNG terminals project (which diffs one canonical PDF, GIIGNL), pipelines
have **no canonical reference**. Every dataset is plugged in via the registry in
`sources/` (a declarative `manifest.yml` + optional Python adapter), normalized into
one canonical schema, then run through the **same** generic match → diff → score →
workbook pipeline. Adding a dataset is config, not code.

## When to run

- The user asks to reconcile a named source for a scope: "reconcile GulfPub for
  Saudi Arabia", "gulfpub diff for Iraq oil", "compare GEM to <dataset>".
- A fresh scrape of a registered source lands.
- Triage flags an unprocessed reconciliation backlog.

## Phases

### 1. Parameter confirmation
Confirm: which `--source` (must exist under `sources/`), which `--commodity`
(`oil` / `gas` / `both`), the `--country`/scope, which GEM lifecycle states to
include, and whether the route-geometry pass + route-replacement flagging are on
(default **yes**). Note the source's `scraped_date` and OID-stability caveat from
its manifest. These go in the workbook README sheet.

### 2. Ingest + normalize the reference
1. Fresh GEM pull: `scripts/refresh_csvs.sh` (don't reconcile against a stale
   snapshot). Re-derive the column→index map from the fresh header.
2. `scripts/ingest.py --source <name> --commodity <c>` runs the source's manifest
   (via the declarative loader, or its `adapter.py` if present) → `canonical_records.json`
   + a geometry sidecar. The canonical schema (`sources/_schema/canonical_record.md`)
   is GEM-aligned: status mapped to GEM lowercase vocab, diameter parsed to an
   inch-set, length converted to km, **geodesic km computed from geometry** (never
   from an embedded projected shape-length field), source cited by non-URL
   `report_citation`.
3. Sanity-check record counts against the raw file before proceeding.

### 3. Match (hybrid: attributes + geometry)
`scripts/match.py` + `scripts/route_compare.py`, orchestrated by `reconcile.py`.
Reference records match against GEM rows of the **same commodity sheet**:

- **Blocking** by `(country, commodity)`. Reference `country` ↔ GEM
  `CountriesOrAreas` *any-of* (GEM rows can be multi-country).
- **Attribute signals** (each ∈ [0,1]): name (rapidfuzz `token_set_ratio` over
  `PipelineName`/`SegmentName`/`OtherEnglishNames`/`PipelineNetworkGrouping`),
  endpoints (best-orientation fuzzy + geocoded distance), diameter (multi-value
  **set subset/Jaccard**, never equality), length ratio (prefer geodesic).
- **Geometry signals** (only when both routes exist): buffer-IoU (primary),
  endpoint distance, Hausdorff, length ratio — computed in a metric CRS.
- **Dual-level granularity:** score against individual GEM segment rows **and**
  synthetic network rows (grouped by `PipelineNetworkGrouping`, merged geometry /
  summed length / union diameter). Emit the better of the two; record the matched
  `GEM segments` list. Detect the reverse (one GEM ↔ several reference rows).
- **Confidence** = composite over present signals → green/yellow/red per
  `docs/reference/confidence_tiers.md`; a single Tier-2 source caps at yellow.
  Top-2 candidates within 10% → **ambiguous** (red), list both, never auto-resolve.

### 4. Diff + score → classify
`reconcile.py` writes `match_diff.json` + `route_metrics.json` and classifies:

| Class | → routes to | Workbook sheet |
|---|---|---|
| **Overlap** (matched) | confidence bump / Update if a value disagrees | `<Cmdty>_Overlaps` |
| **Addition** (reference-only) | **Discovery** (try to match to an existing GEM pipeline under another name FIRST) | `<Cmdty>_Additions` |
| **GEM-only** | usually log only (the source has gaps) | `<Cmdty>_GEM_only` |
| **Status conflict** | verify true status (Update) — never auto-flip | `Status_Conflicts` |
| **Ambiguous** | manual review | `Ambiguous_Clusters` |

### 5. Build the workbook
`scripts/build_recon_workbook.py` → the per-commodity `Oil_`/`Gas_` sheets +
`Routes_WKT` + README (sheet defs + counts). `scripts/recalc.py` to confirm no
formula errors. Present the file. Layout + colors: `docs/reference/workbook_conventions.md`.

## Route reconciliation specifics

When a reference route exists and the matched GEM `RouteAccuracy` is
`low`/`medium`/`no route`, and geometry is corroborated (buffer-IoU ≥ 0.5 **or**
endpoint score ≥ 0.7), set `route_replacement_candidate = True`. It surfaces as a
yellow column on `Overlaps`, in `Routes_WKT` (with IoU + current accuracy), and a
pre-filled `staged_route_replacements.json` for human confirmation. **No GeoJSON is
written** — replacing a route is a separate manual branch+PR against
`GOIT-GGIT-pipeline-routes`. If GEM is already `high`/`very high` and geometries
disagree badly → `Route_Conflicts`, not a replacement.

## Hard rules

- **Never auto-apply** a reference value. Every disagreement is a *candidate* routed
  through Update's normal source-search + confidence-labeling.
- A `ResearcherNotes` cell may document a **deliberate** GEM divergence — flag the
  delta but defer the recommendation (verify, don't overwrite).
- Honor standing rules: never cite GEM, never fabricate URLs, corroborate (the
  reference is one source — a single Tier-2 dataset never reaches green alone).

## Audit trail (`batches/staging/recon/<source>_<scope>_<YYYYMMDD>/`)

Committed (agent-authored): `staged_recon_verdicts.json`,
`staged_report_only_resolutions.json` (a reference-only row confirmed as an existing
GEM pipeline under another name → "add to `OtherEnglishNames`"),
`staged_status_conflicts.json`, `staged_route_replacements.json`. Gitignored
(derived, re-derivable): `canonical_records.json`, `geometry_sidecar.json`,
`match_diff.json`, `route_metrics.json`.

## Escalate to the user when
- A reference disagrees on >10% of matched rows (material conflicts, not raw count).
- A source produces >30 reference-only Additions in one country (scope/coverage gap).
- Record counts diverge wildly from the raw file (adapter/manifest bug).
- An OID-unstable source was re-scraped (cross-scrape identity needs a decision).
