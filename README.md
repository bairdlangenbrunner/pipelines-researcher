# pipelines-researcher

Working repo for Global Energy Monitor (GEM) pipeline-database research and QC
work. Covers the Global Oil Infrastructure Tracker (GOIT), Global Gas
Infrastructure Tracker (GGIT), and related LNG trackers.

## Quick start

```bash
# 1. Install Python deps
pip install -r requirements.txt

# 2. Pull fresh CSV snapshots from the live backend Google Sheet
./scripts/refresh_csvs.sh

# 3. Load in Python (header is at CSV row index 2)
python3 -c "
import pandas as pd
df = pd.read_csv('data/GOIT_oil_ngl.csv', header=2, low_memory=False)
print(df.shape)  # ~(2199, 107)
"
```

## Documentation

- **[CLAUDE.md](CLAUDE.md)** — operational guide for Claude Code sessions
  (rules, access methods, schema gotchas, active workstreams). Read this first
  if you're using Claude Code in this repo.
- **[docs/PROJECT_SETUP_AND_CONTEXT.md](docs/PROJECT_SETUP_AND_CONTEXT.md)** —
  fuller project context, pending country items, tools inventory.
- **[docs/GOIT_Pipeline_Research_Workflow.md](docs/GOIT_Pipeline_Research_Workflow.md)** —
  the four-phase deep-research workflow with controlled vocabulary and country
  notes.
- **[docs/ROUTE_DATA_REFERENCE.md](docs/ROUTE_DATA_REFERENCE.md)** — where and
  how to fetch pipeline route GeoJSONs.

## Layout

```
.
├── CLAUDE.md                  # operational guide for Claude Code
├── README.md                  # this file
├── requirements.txt           # Python deps
├── data/                      # date-stamped CSV snapshots of live tabs
├── docs/                      # full reference documentation
├── scripts/                   # bash helpers (refresh, route fetch)
└── working_files/             # active research workbooks
```

## Standing rules

- **Never cite GEM** (gem.wiki, globalenergymonitor.org, Global Energy Monitor)
  as a source in research outputs unless explicitly approved. The goal of this
  work is to surface what *other*, independent sources exist.
- **Corroborate with 2+ independent sources.** For every material data point, try
  to find at least two independent sources that agree rather than relying on one.
  2+ corroborating sources → high confidence; a single source → medium/low.
  Republished wire copy or anything that circles back to GEM is not independent
  corroboration. See `CLAUDE.md` and `docs/GOIT_Pipeline_Research_Workflow.md`.
