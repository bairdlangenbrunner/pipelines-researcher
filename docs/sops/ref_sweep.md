# SOP — Reference sweep (fill & re-verify every `[ref]`)

Crawl every row and every ref-bearing data point in a country+tracker scope and, for
each one, reach the target: **≥2 links that both WORK (HTTP 200, no error) AND
corroborate each other AND contain the precise data point** being referenced.

- **Blank `[ref]` + filled value** → research and add corroborating source URLs.
- **Filled `[ref]`** → re-check the URLs still resolve *and* still contain the value.

Distinct from QC's link-rot detection: **QC *detects*, Ref Sweep *researches & stages*.**
QC's BroadSweep flags orphan refs (ref filled, value blank); the Ref Sweep fixes the
inverse (value present, ref blank) and re-verifies live refs. Both share the one ref-pair
model in `scripts/ref_pairs.py`.

The deep-research rules (source hierarchy, corroboration, independence) live in
`docs/GOIT_Pipeline_Research_Workflow.md` Phase 2 and `docs/reference/confidence_tiers.md`;
this SOP is the operational sequence.

## Inputs
- Scope: country + tracker (oil / gas). One tracker per batch.
- Optional `--status` filter (default: **all** statuses, incl. operating).
- Decision for the current program: **upgrade single-source data points to ≥2
  corroborating links** (a lone working source still needs a second, independent one).

## The ref-pair model (group-walk)
`scripts/ref_pairs.py::discover_ref_pairs` re-derives, from the **fresh header every
batch**, which value columns each `X [ref]` sources. A `[ref]` governs the run of value
columns since the previous `[ref]`, minus identity/derived/no-ref columns; when the ref's
name matches a column (exact/prefix) the cluster starts there. Known irregulars (flagged
`irregular:true` for reviewer sanity):
- gas `Location [ref]` sources **both** start and end endpoint blocks (one ref, 8 cols).
- gas `H2RepurposedKmOr% [ref]` → the H2 km/% cols.
- `Owner`/`Parent` have **no** `[ref]` column on the tracker tab (emitted as a synthetic
  `kind:'owner'` unit, class `MISSING_REF_NO_COLUMN`). **Owner/operator source URLs live in a
  separate backend tab, "Pipeline operators/owners"** (GID `1489950650`, header at CSV row
  index 1) — *not* in a tracker-row `[ref]` cell or `ResearcherNotes`. That tab is
  **ProjectID-keyed** (same `ProjectID`s as the trackers), with `Owner [ref]` / `Operator [ref]`
  columns whose `[ref]` **precedes** its values (opposite of the trackers). The sweep surfaces an
  owner-ref candidate **per pipeline row** labeled `Owner (→ Pipeline operators/owners tab)`;
  Baird pastes it onto that ProjectID's row of the operators/owners tab. Because the tab is
  ProjectID-keyed (not entity-keyed), the ref is per-pipeline — no entity-level de-dup. See
  `docs/reference/gem_schema.md` for the full column layout.
- **Route/geometry is OUT OF SCOPE.** `RouteType`/`RouteAccuracy`/`RouteNotes` → `Route [ref]`
  is dropped by `discover_ref_pairs` (`SKIP_REF_COLS`); **never research, fill, or re-verify a
  `Route [ref]`.** Pipeline geometry is reconciled against the `GOIT-GGIT-pipeline-routes` repo
  (a separate human branch + PR), not corroborated from media `[ref]` URLs.

## Output (what Baird works from)
The deliverable leads with **`<Cmdty>_Backend`** — a paste-ready mirror of the live-sheet
layout: one row per pipeline segment, each touched data point shown as its **value column
immediately followed by its `[ref]` column** carrying the proposed ref(s), the `[ref]` cell
**color-coded by corroboration tier** (green/yellow/red/blue, below). This is the tab Baird
works from. The `<Cmdty>_Refs_Added / _Reverified / _DeadLinks / _Unresolved` bucket tabs
remain as supporting detail (full verifications, current-ref, notes) but are not the primary view.

## Sequence
1. `scripts/refresh_csvs.sh` → fresh snapshot (don't sweep a stale CSV).
2. **Worklist** — `scripts/build_ref_worklist.py --tracker <t> --country <C>
   [--status …] --verify-existing --out batches/staging/ref-sweep-<scope>/worklist.json`.
   Classifies each row×pair ref cell: `SKIP` (all values blank), `MISSING_REF` (value
   filled, ref blank), `HAS_REF` (ref filled → re-verify), `MISSING_REF_NO_COLUMN` (owner).
   `--verify-existing` HTTP-checks every existing ref URL up front (deterministic, **no
   agent tokens**) so most `HAS_REF` units pre-classify live vs dead before research.
3. **Harvest** — `scripts/harvest_wiki_citations.py --worklist … --out …/wiki_citations.json`.
   Start research from the row's gem.wiki page: harvest its **outbound** external citations
   (once per ProjectID). We *visit* gem.wiki but **never cite it** — only the underlying
   URLs (gem.wiki/globalenergymonitor/theodora are filtered out here and at the verifier).
   Expect many harvested links to be dead — verify each before use.
4. **Research loop (per ProjectID):**
   - **HAS_REF:** if `--verify-existing` shows all URLs live AND containing the value AND
     there are ≥2 independent → **Re-verified (blue)**, done. A single live source still
     needs a 2nd independent corroborating link.
   - **MISSING_REF / degraded HAS_REF:** rank harvested candidates (link text/context vs
     the value + source tier in `source_roster.md`), `url_verifier.verify_url(url,
     any_of=surface_forms(value))` each, keep the live + value-present ones. If gem.wiki
     citations are insufficient, web-search down the source hierarchy — those URLs also
     pass `url_verifier`.
   - **Search in the country's language(s), not just English.** Seed from the row's
     `OtherLanguage*` name columns and transliterations (Saudi → Arabic: Aramco Arabic
     press, Argaam, SPA). Foreign pages still pass `url_verifier`; the "contains the value"
     check leans on language-agnostic tokens (numbers, years, diameters). Record the source
     language in `ResearcherNotes`.
   - **Corroboration & tier:** seek ≥2 working, **independent** links (independence per
     `confidence_tiers.md`: separate origins; NOT the same wire story / GEM-citing). Assign
     tier → 2+ independent = **high/green**; single strong = **medium/yellow**; single weak
     / partial conflict = **low/red**; none verifiable = **Unresolved + ResearcherNotes**
     (no fabricated URL — standing rule 2).
5. Stage one resolution per unit (`class_out` ∈ `REFS_ADDED` / `REVERIFIED` / `DEAD_LINK` /
   `UNRESOLVED`, `proposed_refs`, `verifications`, `tier`, `independent`, `source_language`,
   `researcher_notes`, `harvested_from_wiki`) into
   `batches/staging/ref-sweep-<scope>/staged_resolutions.json`.
6. **Build** — `scripts/build_ref_workbook.py --staging batches/staging/ref-sweep-<scope>/
   --output batches/pipelines_batch_<stamp>_<scope>_refsweep.xlsx`; then `recalc.py`;
   present. Leads with the `<Cmdty>_Backend` paste-ready tab (see **Output** above), bucket
   tabs follow. `<stamp>` from `TZ=America/New_York date "+%Y%m%d_%H%M_ET"`; never overwrite.

## Tier → color
Applied to each `[ref]` cell on the `<Cmdty>_Backend` tab (and the tier cell on the bucket tabs):
green = ≥2 independent working sources · yellow = single source · red = low/none ·
**blue = re-verified existing ref (no action)** · red Current-ref cell (DeadLinks tab) = dead/value-missing.

## Standing rules (echoed)
Visit-but-**never-cite** gem.wiki/globalenergymonitor (rule 1) · **never theodora** ·
every URL through `url_verifier` (even ones that worked last batch) · no orphan refs ·
**no fabricated URLs** (rule 2) · nothing auto-applied — the xlsx is a candidate set Baird
pastes manually.

## Pre-delivery checks
README present; every `Proposed ref(s)` cell verified (HTTP 200 + value present) and free
of GEM/theodora; tier colors correct; no orphan refs; Unresolved units have a
`ResearcherNotes` reason and no fabricated URL. Full checklist: `docs/sops/qc.md`.

## Escalation gates
Stop and report rather than mass-producing low-value rows if: a large fraction of
MISSING_REF units end **Unresolved**, or the harvester hit-rate is very low, or a whole
class of values looks systematically unsupported (likely a schema misread, not a finding).

## Iterate
Expect Baird to challenge specific refs. Acknowledge, re-search with verified sources,
regenerate — **do not defend** wrong findings (standing rule 3).
