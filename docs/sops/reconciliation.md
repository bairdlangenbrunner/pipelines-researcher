# SOP — Reconciliation (GEM ↔ a scraped reference dataset)

Diff a registered external pipeline dataset (GulfPub and OpenStreetMap today; more
later — the registry table is in `docs/reference/source_roster.md`) against the
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
2. **Sources with no global extract need a pre-fetch first.** GulfPub ships one global
   file; OSM does not — pull the scoped extract into `sources/osm/data/` and add its
   `datasets[]` entry before ingesting
   (`fetch_overpass.py --iso <ISO2> --substance <c> --include-lifecycle`; both flags are
   mandatory — see `sources/osm/NOTES.md` and the roster).
3. `scripts/ingest.py --source <name> --commodity <c>` runs the source's manifest
   (via the declarative loader, or its `adapter.py` if present) → `canonical_records.json`
   + a geometry sidecar. The canonical schema (`sources/_schema/canonical_record.md`)
   is GEM-aligned: status mapped to GEM lowercase vocab, diameter parsed to an
   inch-set, length converted to km, **geodesic km computed from geometry** (never
   from an embedded projected shape-length field), source cited by non-URL
   `report_citation`.
4. Sanity-check record counts against the raw file before proceeding.

### 3. Match (hybrid: attributes + geometry)
`scripts/match.py` + `scripts/route_compare.py`, orchestrated by `reconcile.py`.
Reference records match against GEM rows of the **same commodity sheet**:

- **Blocking** by `(country, commodity)`. Reference `country` ↔ GEM
  `CountriesOrAreas` *any-of* (GEM rows can be multi-country).
- **Attribute signals** (each ∈ [0,1]): name (rapidfuzz `token_set_ratio` over
  `PipelineName`/`SegmentName`/`OtherEnglishNames`/`PipelineNetworkGrouping`),
  endpoints (best-orientation fuzzy + geocoded distance), diameter (multi-value
  **set subset/Jaccard**, never equality), length ratio (prefer geodesic).
  Boilerplate tokens (`gas`, `oil`, `pipeline`, `line`, `system`, … —
  `match.GENERIC_NAME_TOKENS`) are **stripped before name scoring**: `token_set_ratio`
  scores on the token intersection, so two unrelated names sharing only that
  boilerplate scored ~0.7 and let one GEM row act as a magnet for every reference.
- **Geometry signals** (only when both routes exist): buffer-IoU, **containment**
  (intersection ÷ smaller buffer — the signal that survives a *partial* reference,
  which IoU cannot: a 97 km fragment lying exactly on a 520 km route scores IoU 0.02),
  endpoint distance, Hausdorff, length ratio — computed in a metric CRS.
- **Absent geometry is "untested", not "passed".** When the reference has a route and
  the GEM row does not, `g_score` is set to `geometry_untested_score` (0.15) rather
  than dropped. Dropping it renormalized the weights and scored that candidate as if
  it had *passed* the geometry test — so routeless GEM rows structurally outranked
  correctly-matched rows whose real geometry scored anything below perfect.
- **`buffer_km_for_overlap` is per-source, and 2 km is an onshore-survey default.**
  Coarse or offshore geometry needs more (OSM uses 10 km); too tight reads the same
  pipeline as no match.
- **Admin-area signal** (`scripts/geo_signals.py`, `s_geoarea`) — the signal that survives
  when name, endpoints, diameter, length *and* route are all blank. It resolves the
  reference trace's vertices against Natural Earth admin-0/admin-1 and scores that
  footprint against the GEM row's declared `Start`/`End CountryOrArea` +
  `State/Province` + `Prefecture/District`, which GEM fills far more often than
  `Start`/`EndLocation`. **`geoarea_weight` defaults to 0.0 (OFF)**, so enabling it moves
  no already-committed composite; a dataset opts in via its manifest `matching:` block.
  It is **excluded from `PHYSICAL_SIGNALS`**: province-coarse evidence routes a finding to
  a human, it never unlocks green on its own.
- **Geometry candidates = attribute top-K ∪ physically closest rows** (`spatial_candidates`,
  default 8). The costly geometry pass used to go to the attribute leaders only — a
  meaningless ranking when the reference is unnamed, so the true match was never tested.
- **Weights layer: engine defaults ← source `matching` ← dataset `matching`.** Tune one
  country's extract at the **dataset** level; source weights are global, so retuning them
  to fix one country silently rewrites every already-committed run of that source.
- **Dual-level granularity:** score against individual GEM segment rows **and**
  synthetic network rows (grouped by `PipelineNetworkGrouping`, merged geometry /
  summed length / union diameter). Emit the better of the two; record the matched
  `GEM segments` list. Detect the reverse (one GEM ↔ several reference rows).
- **Confidence** = composite over present signals → green/yellow/red per
  `docs/reference/confidence_tiers.md`; a single Tier-2 source caps at yellow.
  Top-2 candidates within 10% → **ambiguous** (red), list both, never auto-resolve.
  **Green additionally requires a physical signal** — endpoints, diameter, or a
  *tested* geometry score (`reconcile.PHYSICAL_SIGNALS`). Name + length alone cannot
  reach green however high the composite: names share boilerplate and length is a
  bare ratio two unrelated lines match by coincidence. Such a match is capped at
  yellow and the reason carries `capped at yellow — no physical signal`.

### 4. Diff + score → classify
`reconcile.py` writes `match_diff.json` + `route_metrics.json` and classifies:

| Class | → routes to | Workbook sheet |
|---|---|---|
| **Overlap** (matched) | confidence bump / Update if a value disagrees | `<Cmdty>_Overlaps` |
| **Addition** (reference-only) | **by disposition**, see below — never one undifferentiated pile | `<Cmdty>_Additions` |
| **GEM-only** | usually log only (the source has gaps) | `<Cmdty>_GEM_only` |
| **Status conflict** | verify true status (Update) — never auto-flip | `Status_Conflicts` |
| **Ambiguous** | manual review | `Ambiguous_Clusters` |

**An unmatched reference record is dispositioned, not dumped.** A route in a reference
dataset is presumptively *real pipe* — the open question is only which kind of finding it
is, and a single "Addition" bucket let 52 Iraq OSM traces be filed as one untriaged pile.
`reconcile.disposition()` labels each one (most specific first):

| Disposition | Meaning | Action |
|---|---|---|
| `FRAGMENT_OF_EXISTING` | ≥ `route_containment_threshold` (0.60) of the trace lies inside a drawn GEM route | partial trace of a tracked line — log, don't discover |
| `ROUTE_FOR_EXISTING` | nearest GEM row has **no route** and its declared geography matches the trace | candidate **geometry** for that row → §8 / a human routes-repo PR |
| `NEAR_MISS` | composite within `near_miss_delta` (0.10) below the yellow threshold | adjudicate by hand — **a false Addition hides a real one** |
| `DISCOVERY_CANDIDATE` | no plausible GEM row | Discovery — but match to an existing row under another name FIRST (→ `OtherEnglishNames`) |

Two guards ride alongside. **`coverage`** flags an overlap as `partial` when the reference
covers < 25% of the GEM row, so a 0.1 km OSM stub is never read as corroborating a 105 km
pipeline (and can never nominate itself as a route replacement). And `meta.diagnostics`
records whether the matcher had anything to work with — % of reference records named, % of
GEM rows routed, the composite distribution — because a zero-overlap run is otherwise
ambiguous between "GEM is missing all of this" and "every signal was blank". It raises a
`MATCH_QUALITY` escalation when both the name and geometry axes are mostly dead, or when a
run of ≥5 records returns zero overlaps. **Never read a null run as a discovery set.**

### 5. Build the workbook
`scripts/build_recon_workbook.py` → the per-commodity `Oil_`/`Gas_` sheets +
`Routes_WKT` + README (sheet defs + counts). `scripts/recalc.py` to confirm no
formula errors. Present the file. Layout + colors: `docs/reference/workbook_conventions.md`.

The README carries the matcher health with the findings: a **`Signal`** row (the per-axis
percentages above) plus one red-tinted row per `meta.diagnostics.escalations` entry. Until
2026-07-29 `reconcile.py` only printed these to stdout, so the person who most needed
them — whoever opens the workbook — never saw them. Read the `Signal` row before trusting
any single match.

To surface the same diff **inside a sweep/handoff workbook** instead, flatten it with
`scripts/build_recon_crosswalk.py` (source-agnostic — it replaces the GulfPub-only
`build_gulfpub_crosswalk.py`, now a deprecated shim):

```bash
python scripts/build_recon_crosswalk.py --match-diff $RECON/match_diff.json --sweep-dir $STG/
```

`build_ref_workbook.py` globs `recon_*_crosswalk.json` out of the staging dir, so dropping
the file in is the whole wiring step — one `<Cmdty>_<Source>` tab per reconciled dataset
(`Gas_GulfPub`, `Gas_OSM`, …). A legacy `gulfpub_crosswalk.json` still reads. Skipping this
step is why a reconciliation can run clean and still never reach a reviewer.

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

## Audit trail (`batches/<scope>/staging/recon-<source>-<YYYYMMDD>/`)

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
