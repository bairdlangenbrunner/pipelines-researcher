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
