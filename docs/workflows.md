# Workflow recipes

Step-by-step command sequences for the workflows routed from `CLAUDE.md`. The
research methodology (`docs/GOIT_Pipeline_Research_Workflow.md`) is authoritative
for *what* to research; the SOPs (`docs/sops/`) are the operational rules; this file
is the glue — which commands, in which order. Read the section for the workflow
you're running, plus its SOP.

**Fresh-pull shorthand:** `./scripts/refresh_csvs.sh` → dated GOIT + GGIT snapshots
in `data/` (`header=2`). Re-derive the column→index map each run; the schema drifts.

**How they fit together:** Triage (memo) → Reconciliation / Update / Discovery
(xlsx) → QC (xlsx, detects → routes fixes back to Update). Reconciliation and QC
both *surface* work; Update/Discovery *do* it.

**Batch artifacts:** staging JSON under `batches/staging/` — `recon/<source>_<scope>_<date>/`
for reconciliation, `<scope-slug>/` for ad-hoc. Deliverables are
`batches/pipelines_batch_<YYYYMMDD>_<HHMM>_ET[_<scope>]_<mode>.xlsx`
(stamp via `TZ=America/New_York date "+%Y%m%d_%H%M_ET"`; never overwrite).

---

## §1 Reconcile against a scraped dataset (the engine)

The pluggable core. `<source>` is any folder under `sources/` (GulfPub today). See
the Reconciliation SOP for phase detail.

1. Confirm parameters (SOP §1): `--source`, `--commodity oil|gas|both`, `--country`,
   lifecycle states, geometry pass on (default). Note the source's `scraped_date`.
2. Fresh pull (shorthand).
3. **Ingest** the reference → canonical records:
   ```bash
   python scripts/ingest.py --source gulfpub --commodity both \
     --out batches/staging/recon/gulfpub_saudi-arabia_<DATE>/
   ```
   Reads `sources/gulfpub/manifest.yml` (+ `adapter.py` if present). Spot-check 5
   records vs the raw GeoJSON (status mapped, diameter set, length→km, geodesic
   computed, geometry sidecar present).
4. **Reconcile** (match + geometry + diff + score):
   ```bash
   python scripts/reconcile.py --source gulfpub --country "Saudi Arabia" \
     --commodity both --gem-oil data/GOIT_oil_ngl_snapshot_<DATE>.csv \
     --gem-gas data/GGIT_gas_snapshot_<DATE>.csv \
     --staging batches/staging/recon/gulfpub_saudi-arabia_<DATE>/
   ```
   → `match_diff.json` + `route_metrics.json`. Pulls GEM routes from the local
   mirror (else `fetch_route.sh`) for geometry signals.
5. **Route findings (SOP §4):** Additions → Discovery (match-to-existing FIRST);
   value/status disagreements → Update; GEM-only → log. **Do not auto-apply.**
   Author `staged_*.json` resolutions in the run folder as you review.
6. **Build:**
   ```bash
   python scripts/build_recon_workbook.py \
     --staging batches/staging/recon/gulfpub_saudi-arabia_<DATE>/ \
     --output batches/pipelines_batch_<stamp>_gulfpub-saudi-arabia_reconciliation.xlsx
   python scripts/recalc.py batches/pipelines_batch_<stamp>_gulfpub-saudi-arabia_reconciliation.xlsx
   ```
   Then present. **Adding a new dataset later = a new `sources/<name>/` manifest; the
   §1 commands are unchanged** (`--source <name>`).

---

## §2 Update existing pipelines
1. Fresh pull. 2. Confirm scope + tier (Update SOP). 3. Derive worklist (in-dev rows
∪ blank-ref fills ∪ stale ∪ recon disagreements). 4. Research per methodology Phase 2
→ stage `batches/staging/<scope>/staged_updates.json`. 5. `url_verifier.py` every URL;
`entity_lookup.py` every new owner. 6. Build `…_<scope>_update.xlsx` (changed cells
red); `recalc.py`; present.

## §3 Discover new pipelines
1. Fresh pull + dedup index. 2. Search per methodology Phase 3 + route research
(`route_conventions.md`). 3. Apply the add-threshold; below → `monitor_list`. 4.
`url_verifier.py` / `entity_lookup.py`. 5. Build `…_<scope>_discovery.xlsx` (new rows
green); `recalc.py`; present. Reconciliation Additions feed here — match-to-existing first.

## §4 Triage (memo)
1. Fresh pull. 2. Gap analysis (methodology Phase 1) + staleness flags + recon
backlog. 3. Write `batches/triage_<stamp>_ET.md` with options (workflow + scope +
tier). Present; stop and ask.

## §5 Quality control (xlsx)
1. Fresh pull. 2. `python scripts/build_qc_workbook.py --tracker oil --country <C>
--output batches/pipelines_batch_<stamp>_<scope>_qc.xlsx` — one sheet at a time
for large scopes (QC SOP sheet list; route/WKT sheet dropped). 3. `recalc.py`;
present; route fixes to a follow-on Update batch.

---

## §6 Reference sweep (fill & re-verify every `[ref]`)

Crawl every ref-bearing data point in scope and reach **≥2 working, independent links
that contain the precise value** — fill blank `[ref]`s, re-verify filled ones. One
tracker per batch. See the Ref Sweep SOP for the pair model, tiers, and standing rules.
Distinct from §5 QC: **QC detects orphan refs; Ref Sweep researches & stages refs.**
**Route/geometry `[ref]` cells are OUT OF SCOPE** (geometry is reconciled against the
routes repo, not media URLs) — `discover_ref_pairs` drops them automatically.
**Owner/operator refs** don't live on the tracker tab — the worklist joins the separate
**"Pipeline operators/owners" tab** (GID 1489950650, ProjectID-keyed) and stages
`Operator [ref]` / `Owner [ref]` units onto a dedicated `<Cmdty>_OperatorsOwners` tab.

1. Fresh pull.
2. **Worklist** (scope scan + classify; `--verify-existing` HTTP-checks existing refs up
   front, deterministically — no agent tokens):
   ```bash
   python scripts/build_ref_worklist.py --tracker oil --country "Saudi Arabia" \
     [--status proposed,construction] --verify-existing \
     --out batches/staging/ref-sweep-saudi-arabia/worklist.json
   ```
3. **Harvest** the gem.wiki outbound citations (start research there; never cite gem.wiki):
   ```bash
   python scripts/harvest_wiki_citations.py \
     --worklist batches/staging/ref-sweep-saudi-arabia/worklist.json \
     --out batches/staging/ref-sweep-saudi-arabia/wiki_citations.json
   ```
4. **Research loop (per ProjectID, SOP §Sequence-4):** verify candidates with
   `url_verifier` (search in-country languages where needed); reach ≥2 independent working
   sources; assign tier. Stage `staged_resolutions.json` (`class_out` ∈ REFS_ADDED /
   REVERIFIED / DEAD_LINK / UNRESOLVED). **Never auto-apply; no fabricated URLs.**
5. **Build:**
   ```bash
   python scripts/build_ref_workbook.py \
     --staging batches/staging/ref-sweep-saudi-arabia/ \
     --output batches/pipelines_batch_<stamp>_saudi-arabia_refsweep.xlsx
   python scripts/recalc.py batches/pipelines_batch_<stamp>_saudi-arabia_refsweep.xlsx
   ```
   Leads with two paste-ready tabs: **`<Cmdty>_Backend`** (mirror of the tracker layout —
   each touched value next to its `[ref]`, colored by tier) and **`<Cmdty>_OperatorsOwners`**
   (mirror of the operators/owners tab — ProjectID-keyed, `[ref]` precedes its values; paste
   back onto that tab by ProjectID). Work from those; the `*_Refs_*` bucket tabs are supporting
   detail. Then present. Scale country-by-country on Baird's sign-off.

### §6b Deep sweep (ref sweep + deep-fill + validity check, one pass)

The combined "go deep on a whole country+tracker" mode. Same engine and deliverable as
§6, but each in-scope row gets **three things at once**:
1. **Ref sweep + critical confirmation** — re-verify live `[ref]`s and fill blank `[ref]`s
   to the ≥2-independent target (the standard §6 job), AND actively confirm the *value*
   each ref supports: check that independent sources **agree with the GEM number**, not
   just that a live page mentions the pipeline. Material disagreement → a validity concern,
   not a silent re-verify.
2. **Deep-fill** of blank *value* fields — research the missing data point, fill it, and
   stage a paired `[ref]` (best-effort on weak fields like Capacity — don't force a
   number). Staged as `class_in="FILL"` records → dedicated `<Cmdty>_Fills` tab.
3. **Validity / existence check** — skeptically judge whether the pipeline is real,
   correctly classified (transmission line? right commodity?), correctly attributed, and
   not a duplicate/relabel; flag concerns as `__VALIDITY__` records (with structured
   `verdict` / `concern_type` / `recommendation`) → dedicated `<Cmdty>_Validity` tab.
   Read-and-flag: never proposes an edit.

This is the ref-sweep analogue of Update's `exhaustive` tier, extended with fills and
existence-checking. It is **read-and-stage only** — still never auto-applies, still
honours every standing rule. Schema extensions (`class_in="FILL"`, `__VALIDITY__` + its
structured fields), how to run it at scale via subagent fan-out, and the merge-time QC
normalization are in the **Ref Sweep SOP → "Deep sweep variant" + "At scale"**. The
deliverable adds `<Cmdty>_Validity` and `<Cmdty>_Fills` tabs to the §6 layout.

**Repeatable runner — the `critical-deep-sweep` workflow.** The validity/existence pass
is packaged as a saved workflow (`.claude/workflows/critical-deep-sweep.js`) that fans out
**one skeptical subagent per pipeline** — each starts from the sources the sheet already
cites, then critically confirms existence → classification → duplicate → attribution →
spec, and writes a shard. Always begin research from the row's existing `[ref]`s +
gem.wiki citations before open-web search. Full sequence:

```bash
# 1. fresh pull + worklist + wiki citations (the standard §6 steps 1–3), into the staging dir, e.g.:
STG=batches/staging/ref-sweep-gas-saudi-arabia
python scripts/build_ref_worklist.py --tracker gas --country "Saudi Arabia" --verify-existing --out $STG/worklist.json
python scripts/harvest_wiki_citations.py --worklist $STG/worklist.json --out $STG/wiki_citations.json
# 2. derive the workflow args (in-scope PIDs + duplicate-detection roster) from the worklist:
python scripts/build_deepsweep_args.py --staging $STG/         # prints JSON → pass as the Workflow `args`
```
3. Invoke the workflow with that JSON as `args` (it has no FS access, so PIDs/roster must be
   passed in): `Workflow({ name: 'critical-deep-sweep', args: <the JSON> })`. One subagent per
   PID writes `$STG/rows/<PID>.json`.
4. Merge shards onto the preserved ref work + apply merge-time QC:
   `python scripts/merge_deepsweep_shards.py --staging $STG/` (snapshots the ref-sweep output to
   `staged_resolutions.prior.json` on first run, then rebuilds `staged_resolutions.json`).
5. Build + recalc as in §6 step 5 (`_deepsweep.xlsx`); the `<Cmdty>_Validity` /
   `<Cmdty>_Fills` tabs render the findings. Present; escalate systemic blocks (a whole
   class tracing to one non-pipeline source) rather than patching row-by-row.
