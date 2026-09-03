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
  **GEM diameters are per-row unit-tagged** — read them ONLY through
  `normalize.gem_diameter_set(row)`, which honours the row's own `DiameterUnits`
  (GGIT gas: 1,499 rows `mm` / 1,669 `in`; GOIT oil: 400 / 1,062). A bare
  `parse_diameter_set(row['Diameter'])` defaults to inches and reads 530 mm as
  530 inches. **That defect was live in `match.py` and `build_qc_workbook.py`
  until 2026-08-11**, so the diameter signal was dead on ~45% of gas rows (42 of
  44 Kazakhstan gas rows are `mm`) and `Diameter_OutOfRange` flagged every
  mm-tagged row — 1,497 false findings where 1 was real. **Blast radius:** any
  recon run or QC workbook built before 2026-08-11 scored diameter on the `in`
  rows only; re-read its diameter findings, and where a decision turned on a
  weak composite score, re-run `reconcile.py` (Kazakhstan's GulfPub re-run went
  0 → 2 green overlaps, status conflicts 7 → 4, discovery candidates 3 → 1).
  Do **not** substitute the sheet's `DiameterInMm` column: it is a formula that
  emits `--` on exactly the multi-value rows the parser exists for.
  A second, independent defect in the same parser was fixed the same day: a comma
  is BOTH GEM's multi-value delimiter (`700, 720, 820`) and prose's thousands
  separator, so **source text `1,020 mm` parsed as `[1, 20]` → `[0.04, 0.79]` in**,
  and a value restated in two units (`820 mm / 32.28 inches`) read the restatement
  as a second mm value (1.27 in). `parse_diameter_set` now collapses the
  unambiguous thousands case only and lets a token's OWN unit beat the caller's
  default. **Blast radius is source/prose strings, not the trackers** — verified 0
  of 4,327 gas and 0 of 2,096 oil rows change — so what it corrupted is
  wiki-alignment and reference-side diameter comparisons: the worst Kazakhstan case
  (P2291/P2292) actually AGREED with the sheet and was reported `SHEET_SUSPECT`.
  Re-run `wiki_alignment.py` for any country whose packet predates 2026-08-11
  before trusting its Diameter records.
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

**A `best_guess` PID is only a location claim when a locational axis was alive.** With an
unnamed reference (`s_name` 0), a **routeless** guessed row (`g_untested`) and no province
score (`s_geoarea` 0), the sole live signal is *length* — so the "nearest" row is whichever
one is a similar number of kilometres, anywhere in the country. Kazakhstan OSM 2026-08-11
put 18 unnamed traces spread from lon 51 to lon 78 all "nearest" to routeless P5776
(17.8 km), some 1,500 km from its corridor. Since 2026-08-11 `disposition()` detects that
case and prints "read {PID} as arithmetic, not geography" instead of "Nearest was {PID}";
four older OSM runs still carry the misleading phrasing — see `docs/research_backlog.md` §2.
This is an OSM-only failure mode (GulfPub features are named), and the fix is reporting only:
no threshold, weight or match result changed.

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

## Engine invariants the bugs taught

Each of these was a shipped defect first; the ledger (A/B counts, re-runs, archived
workbooks) lives in the named note — this list is the rule only.

- **A country scope is a JOIN, never a bare `==`.** A multi-country reference record
  (a cross-border transit trunk) must match every country it names; `ingest.py`,
  `reconcile.py` and `adapter_base.py` all go through `normalize.country_matches()`.
  Until 2026-08-12 the reference side compared strings with `==` and silently dropped
  every transit trunk (Ukraine gas 111 → 158 refs, Kazakhstan 32 → 63); the falsified
  bucket is `gem_only`. All committed GulfPub recons were re-run that day.
  `notes/escalation-2026-08-12-multicountry-reference-filter-dropped-transit-trunks.md`.
- **A thin recon is a claim about the pipeline until the input count is checked.**
  `MATCH_QUALITY` covers a dead matcher, never records that never arrived — reconcile the
  ingested count against the raw extract before reading any bucket.
- **A diagnostic must report the MATCHER's view of the data, never the data's own.**
  The health line counts `name_norm`, not the raw name: until 2026-08-14 a Cyrillic-only
  name normalized to the empty string while the line still reported it as "named", so
  Ukraine OSM read "9.2% of refs named" on a run where the matcher saw none and
  `MATCH_QUALITY` stayed silent through a 0.1% overlap rate. Fixed via
  `normalize.translit_cyrillic()` + the transliterated-boilerplate stoplist in
  `match.GENERIC_NAME_TOKENS`; both Cyrillic extracts (Ukraine, Kazakhstan) re-run with no
  bucket count moved — a corrected "closest GEM" attribution is the expected gain when a
  manifest weights `name` 0.10 against geometry 0.45, and is NOT a reason to retune.
  `notes/escalation-2026-08-14-cyrillic-names-invisible-to-matcher.md`.
- **`MATCH_QUALITY` is fixed with a per-dataset `geoarea_weight` override, never by
  lowering a threshold and never by retuning a shared source-level block** (that moves
  committed runs in other countries). And only when the dead-axes condition actually
  holds — measure first; where GEM rows are mostly routed, the warning on the name axis
  alone is a true report (Uzbekistan, India, Kazakhstan all refused an override on evidence).
- **A unit declared in a manifest is a claim to verify, not a given.** GulfPub gas
  `length_units` sat wrong (`km`, actually miles) through a scrape repoint and four
  countries' workbooks; check `geodesic_km ÷ length_km` on the ingest (≈ 1.609 means the
  declared unit is miles). `units.length_units_by_country` handles a block that differs
  (GulfPub gas: Canada km, everything else miles). Fixed 2026-07-29; any gas recon workbook
  stamped before `20260729_0941_ET` has `Ref Length (km)` ~38% short.
  `notes/escalation-2026-07-29-gulfpub-gas-length-miles.md`.
- **An OID field is identity, not geometry — verify it is unique before trusting it across
  scrapes.** OSM's `osm_id_key` collided on disjoint parts of one way group until
  2026-08-26 (62 features across 10 extracts; `ingest.py`'s `#2`/`#3` suffixing lost no
  geometry, so no committed finding is falsified, but the suffix is order-dependent).
  `_disambiguate_keys()` now appends a geometry-derived discriminator to colliding keys
  only, so a re-fetch moves nothing but unstable ids and owes no re-run. `sources/osm/NOTES.md`.

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
