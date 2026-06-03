# pipelines-researcher

Research, QC, and **reconciliation** scaffolding for Global Energy Monitor's
open-access pipeline databases — the Global Oil Infrastructure Tracker (GOIT,
crude oil + NGL) and Global Gas Infrastructure Tracker (GGIT, gas).

It mirrors the governance model of the sibling LNG-terminals researcher (modular
SOPs, reference docs, "surface candidates, never auto-apply"), and adds a
**pluggable, geometry-aware reconciliation engine**: scraped pipeline route
databases (GulfPub today, more later) register via a declarative manifest and get
diffed against GEM by name, attributes, and route geometry — producing a reviewable
Excel deliverable, never a live edit.

## Quick start

```bash
pip install -r requirements.txt              # deps (pandas, geopandas, rapidfuzz, …)
./scripts/refresh_csvs.sh                     # pull fresh GOIT + GGIT CSV snapshots
python3 -c "import pandas as pd; print(pd.read_csv('data/GOIT_oil_ngl.csv', header=2, low_memory=False).shape)"

# Reconcile a registered dataset against GEM (the engine):
python scripts/ingest.py    --source gulfpub --commodity both --out batches/staging/recon/<run>/
python scripts/reconcile.py --source gulfpub --country "Saudi Arabia" --commodity both --staging batches/staging/recon/<run>/
python scripts/build_recon_workbook.py --staging batches/staging/recon/<run>/ --output batches/pipelines_batch_<stamp>_<scope>_reconciliation.xlsx
```

## Documentation

- **[CLAUDE.md](CLAUDE.md)** — operational guide + workflow router. Read first.
- **[docs/workflows.md](docs/workflows.md)** — command recipes per workflow.
- **[docs/sops/](docs/sops/)** — reconciliation, update, discovery, triage, qc.
- **[docs/reference/](docs/reference/)** — schema, controlled vocab, confidence
  tiers, workbook conventions, route conventions, source roster.
- **[docs/GOIT_Pipeline_Research_Workflow.md](docs/GOIT_Pipeline_Research_Workflow.md)**
  — the authoritative 4-phase research methodology.
- **[sources/README.md](sources/README.md)** — how to register a new reference dataset.

## Layout

```
.
├── CLAUDE.md / README.md / requirements.txt / .env.example
├── docs/            sops/ + reference/ + country_notes/ + the research methodology
├── sources/         reference-dataset registry (manifest + optional adapter); gulfpub/
├── scripts/         engine (ingest, match, route_compare, reconcile, build_*) + helpers
├── data/            date-stamped CSV snapshots of the live tabs
├── batches/         deliverables (gitignored) + staging/ (committed JSON audit trail)
└── working_files/   active workbooks (incl. the Saudi GulfPub golden reference)
```

## Standing rules

- **Never cite GEM** (gem.wiki, globalenergymonitor.org) as a source unless approved.
- **Corroborate with 2+ independent sources**; a scraped dataset is one source,
  never authoritative on its own.
- The agent **never writes** to the live Sheet or the routes repo — every batch is a
  reviewable file the user applies manually.
