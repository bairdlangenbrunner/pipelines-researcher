# pipelines-researcher

Research, QC, and **reconciliation** scaffolding for Global Energy Monitor's
open-access pipeline databases — the Global Oil Infrastructure Tracker (GOIT,
crude oil + NGL) and Global Gas Infrastructure Tracker (GGIT, gas).

It mirrors the governance model of the sibling LNG-terminals researcher (modular
SOPs, reference docs, "surface candidates, never auto-apply"), and adds a
**pluggable, geometry-aware reconciliation engine**: scraped pipeline route
databases (GulfPub today, more later) register via a declarative manifest and get
diffed against GEM by name, attributes, and route geometry — producing a reviewable
Excel deliverable, never a live edit. Around the engine sit the research workflows
(routed from CLAUDE.md): country sweeps, discovery, targeted updates, QC/handoff
packets, annual-update campaigns, and route creation (candidate route GeoJSON
staged for a human PR against the routes repo).

## Quick start

```bash
pip install -r requirements.txt              # deps (pandas, geopandas, rapidfuzz, …)
./scripts/refresh_csvs.sh                     # dated GOIT + GGIT + operators/owners snapshots → data/
python3 -c "import pandas as pd; print(pd.read_csv('data/GOIT_oil_ngl_snapshot_<date>.csv', header=2, low_memory=False).shape)"

# Reconcile a registered dataset against GEM (the engine):
python scripts/ingest.py    --source gulfpub --commodity both --out batches/<scope>/staging/recon-gulfpub-<date>/
python scripts/reconcile.py --source gulfpub --country "Saudi Arabia" --commodity both --staging batches/<scope>/staging/recon-gulfpub-<date>/
python scripts/build_recon_workbook.py --staging batches/<scope>/staging/recon-gulfpub-<date>/ --output batches/<scope>/deliverables/pipelines_batch_<stamp>_<scope>_reconciliation.xlsx
```

## Documentation

- **[CLAUDE.md](CLAUDE.md)** — operational guide + workflow router. Read first.
- **[docs/workflows.md](docs/workflows.md)** — command recipes per workflow.
- **[docs/sops/](docs/sops/)** — triage, reconciliation, sweep, discovery, update,
  qc/handoff, annual update, route creation.
- **[docs/reference/](docs/reference/)** — schema, controlled vocab, confidence
  tiers, workbook conventions, route conventions, source roster, staged-JSON schema.
- **[docs/GOIT_Pipeline_Research_Workflow.md](docs/GOIT_Pipeline_Research_Workflow.md)**
  — the authoritative 4-phase research methodology.
- **[sources/README.md](sources/README.md)** — how to register a new reference dataset.

## Layout

```
.
├── CLAUDE.md / README.md / requirements.txt / .env.example
├── docs/            workflows.md + sops/ + reference/ + country_notes/ + the methodology
├── sources/         reference-dataset registry (manifest + optional adapter); gulfpub/
├── scripts/         engine (ingest, match, route_compare, reconcile, build_*) + helpers
├── data/            date-stamped CSV snapshots of the live tabs
├── batches/         scope-first: <country>-<commodity>/{staging,deliverables,archive}; INDEX.md
├── campaigns/       annual-update campaign rosters (e.g. ggit-update-2026-07)
├── notes/           session memos (triage memos, escalation writeups)
└── working_files/   active workbooks (incl. the Saudi GulfPub golden reference)
```

## Batches: what "staging" means

The agent never writes to the systems of record (the live Google Sheet and the
`GOIT-GGIT-pipeline-routes` repo), so **everything this repo produces is pending
until a human applies it**. The `batches/` tree makes that lifecycle literal.
Everything for one country+commodity lives under
`batches/<country-slug>-<commodity>/` (e.g. `batches/egypt-gas/`):

- **`staging/<mode[-qualifier]>/`** — one dir per run (`annual`, `ref-sweep-operating`,
  `qc`, `route-creation-p3620-p3657`, …). *Staging ≠ scratch*: it is **finished
  work awaiting application** — the canonical, committed, machine-readable record
  (staged JSON, candidate route GeoJSON, audit trail). Each run dir's store file
  carries `meta.scope` (country + commodity), which is how later handoff packets
  auto-discover and carry it. Reconciliation inputs (`staging/recon-<source>-<date>/`)
  are the one exception: no store file, deliberately invisible to discovery.
- **`deliverables/`** — the human-facing **views**: xlsx workbooks rendered from
  staging (gitignored, regenerable at any time; new timestamp every rebuild).
  For route creation the deliverable you act on is the staged
  `candidate_routes/<PID>.geojson` itself — the workbook is just its review surface.
- **`archive/`** — lifecycle is **by move**: when a batch is applied to the sheet
  (or a routes-repo PR merges, or a workbook is superseded), its staging dir /
  old xlsx moves here. So anything still under `staging/` + `deliverables/` is
  live pending work, by definition.

`batches/INDEX.md` is the whole-tree lookup (per-scope runs with pending counts,
deliverables, archive) — regenerate with `python scripts/staged_summary.py --index`,
never hand-edit.

## Standing rules

- **Never cite GEM** (gem.wiki, globalenergymonitor.org) as a source unless approved.
- **Corroborate with 2+ independent sources**; a scraped dataset is one source,
  never authoritative on its own.
- The agent **never writes** to the live Sheet or the routes repo — every batch is a
  reviewable file the user applies manually.
