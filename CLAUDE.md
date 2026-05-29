# CLAUDE.md

Operational guide for Claude Code sessions in this repo. Read this first; the
files in `docs/` go deeper on each topic.

---

## What this repo is

Working repo for maintaining and improving Global Energy Monitor's open-access
pipeline databases:

- **GOIT** — Global Oil Infrastructure Tracker (crude oil + NGL pipelines, worldwide)
- **GGIT** — Global Gas Infrastructure Tracker (gas pipelines)
- Related trackers: LNG terminals, LNG carrier vessels

Work spans: pipeline infrastructure research (global; deeper coverage in MENA,
US, Iran, Iraq, Saudi Arabia), GIS/geospatial processing, database QC, and
agentic AI research/reconciliation workflows.

Researcher initials in the tracker: **CB**.

---

## STANDING RULES — do not violate

1. **Never cite GEM as a source.** Do not use gem.wiki, globalenergymonitor.org,
   or any Global Energy Monitor surface as a citation in `[ref]` columns or
   research outputs unless Baird explicitly says to. The goal is to surface
   what *other*, independent sources exist.
2. **Never fabricate source URLs.** If a URL can't be verified, describe the
   source precisely in `ResearcherNotes` and flag as inferred/presumed.
   Inferred status changes → `ShelvedCancelledType = Presumed`, no fabricated URL.
3. **Don't defend wrong findings.** Baird challenges data points actively.
   Acknowledge errors, revise on evidence, regenerate outputs.
4. **Corroborate with 2+ independent sources (near-requirement).** When
   researching any pipeline data point (status, capacity, length, diameter,
   ownership, FID, dates, locations, route), TRY to find at least two
   *independent* sources that agree, not just one. Confidence follows
   corroboration: **2+ independent corroborating sources → high**; **a single
   source → medium/low**; **no verifiable source → inferred/presumed** (see
   rule 2). The same wire story republished across sites, multiple sources that
   all trace back to one original report, and anything that itself cites GEM
   (see rule 1 — circular) do NOT count as independent corroboration. Record the
   confidence tier and the corroborating sources in `ResearcherNotes`.

---

## Live data access (the only correct way)

The backend Google Sheet (`1foPLE6K-uqFlaYgLPAUxzeXfDO5wOOqE7tibNHeqTek`) is set
to "Anyone with link can view" permanently. Pull tabs via bash + curl:

```bash
# Oil/NGL tab (107 cols)
curl -sL "https://docs.google.com/spreadsheets/d/1foPLE6K-uqFlaYgLPAUxzeXfDO5wOOqE7tibNHeqTek/export?format=csv&gid=456134080" -o data/GOIT_oil_ngl.csv

# Gas tab (~140 cols)
curl -sL "https://docs.google.com/spreadsheets/d/1foPLE6K-uqFlaYgLPAUxzeXfDO5wOOqE7tibNHeqTek/export?format=csv&gid=1020144097" -o data/GGIT_gas.csv
```

Or use the helper: `./scripts/refresh_csvs.sh`

**Header is at CSV row index 2** for both tabs. Always load with:
```python
df = pd.read_csv(path, header=2, low_memory=False)
```

### Don't do these
- ❌ Drive MCP `download_file_content` — returns only the first tab
- ❌ Drive MCP `read_file_content` — lossy, truncates rows
- ❌ `web_fetch` on the export URL — won't accept URLs not literally provided in-turn

---

## Repo layout

```
pipelines-researcher/
├── CLAUDE.md                              # this file
├── README.md                              # human-facing repo readme
├── requirements.txt                       # Python deps
├── .gitignore
├── docs/
│   ├── PROJECT_SETUP_AND_CONTEXT.md       # full project context, pending items, tools list
│   ├── GOIT_Pipeline_Research_Workflow.md # the deep-research agentic workflow
│   └── ROUTE_DATA_REFERENCE.md            # how to fetch pipeline route GeoJSONs
├── data/
│   ├── GOIT_oil_ngl_snapshot_YYYYMMDD.csv # date-stamped snapshots
│   └── GGIT_gas_snapshot_YYYYMMDD.csv
├── working_files/
│   └── GOIT_SaudiArabia_Gulfpub_Comparison.xlsx
└── scripts/
    ├── refresh_csvs.sh                    # pull latest CSV snapshots
    └── fetch_route.sh                     # fetch a route GeoJSON by ProjectID
```

---

## Schema gotchas (oil sheet)

- Column order: **ask Baird to paste the header row** — the data dictionary's
  `OilOrderInSheet` is unreliable.
- Several oil-sheet columns are absent from the data dictionary:
  `Disrupted`, `RMI`, `QCCOwner2025Update`, `OwnerEntityIDs`,
  `AlternateRouteProjectIDs`.
- Cost columns: `Cost`, `CostUnits`, `Cost [ref]` (NOT `ProjectLevelCost`).
- `OtherEnglishNames`: semicolon-separated.
- `SheetRow` = CSV index + 4.
- Buffer rows (~104 reserved ProjectIDs) should be excluded from QC.
- `Owner` field: `--` is a valid sentinel for unknown ownership; commas/
  ampersands/slashes inside Owner strings are legitimate company-name
  separators — do not flag them.

---

## Controlled-vocabulary casing (locked)

- **lowercase:** `Status`, `RouteAccuracy`, `PipelineType`
- **Title Case (exceptions):** `DelayType`, `ShelvedCancelledType`, `FIDStatus`,
  `Delayed`, `Opposition`
- `very high (within meters)` is a valid `RouteAccuracy` value.
- When in doubt, pull a real row from the sheet and match exact casing.

Full vocabularies: see `docs/GOIT_Pipeline_Research_Workflow.md`.

---

## Operational principles

- **Expansion vs. new construction:** Always verify whether new physical pipe is
  being built. If not → `LengthKnown = 0`, `Diameter = blank`.
- **Diameter flags** are review items, not auto-rejections.
- **WKT/route-format QC checks** are permanently dropped — do not rebuild them.
- **Web search strategy:** When exact-string queries fail on pipeline IDs,
  decompose into components (trunk line, KP reference, commodity, receiving
  facility). Adding contract/procurement keywords (year ranges, "tender,"
  "construction") beats route-based queries alone.
- **Stepwise builds:** For multi-sheet QC workbooks, build one sheet at a time
  to avoid token/message limits and allow review between steps.

---

## Output conventions for Excel deliverables

- Headers: blue fill `4472C4`, white bold, center-aligned, wrap text.
- Changed cells: red fill `FFCCCC`, red font `CC0000`.
- New rows (discovery): green fill `E2EFDA`.
- Freeze panes at row 2 (below headers).
- Multiple URLs in `[ref]` columns: separated by `, ` (comma + space).
- Key columns widened: `PipelineName` (45), `SegmentName` (50),
  `Status [ref]` (55), `Owner` (55), `ResearcherNotes` (55).

---

## Active workstreams (as of repo creation)

1. **Saudi Arabia GulfPub ↔ GEM comparison**
   (`working_files/GOIT_SaudiArabia_Gulfpub_Comparison.xlsx`):
   confidence-check logic (green/yellow/red) for matched records. In progress:
   when a matched GEM pipeline has low/medium route accuracy, compare GEM route
   to GulfPub route for spatial consistency and factor into confidence scoring.
   GulfPub routes treated as more accurate for low/medium GEM entries; human
   review step before any GEM route is replaced.
2. **GOIT oil/NGL QC workbook** (`GOIT_oil_ngl_QC.xlsx`, NOT in this repo —
   re-locate from separate resume bundle): Sheets 1–8 (Status, RouteAccuracy,
   OtherVocab, Owner format, WikiLink Health, Geo Consistency, Name Uniqueness,
   Date Logic) plus Sheet 9 (Diameter_OutOfRange) and Sheet 11 (BroadSweep_Misc).
   Sheet 10 (route/WKT) permanently dropped. Clean rebuild of Sheets 1–8
   against latest CSV was pending.
3. **Country-level research:** 80+ countries covered in a prior global sweep;
   Iraq, Iran, Saudi Arabia have had deep dives.

### Pending country items
- **Iran:** P6074 (Goureh–Persian Gulf Coast) needs verification before any
  duplicate/removal decision. P5367 (Golpa–Moghanak) reclassification as a
  Neka–Ray segment rather than standalone entry.
- **Iraq:** Grand Faw Port third offshore pipeline (Esta/Micoperi, contracted
  April 2025) entered as a single new row. Basra–Haditha (P0544) status may
  need review (listed as "construction" but appeared still in pre-construction/
  tender phase as of early 2026).

---

## External tools & resources

- **Pipeline routes (GeoJSON):**
  `https://github.com/GlobalEnergyMonitor/GOIT-GGIT-pipeline-routes` — fetch via
  raw URL or GitHub Contents API. See `docs/ROUTE_DATA_REFERENCE.md` and
  `scripts/fetch_route.sh`.
- **GEM Project Database MCP server:** wraps `gem-project-db.herokuapp.com`;
  auth via `GEM_SESSION_COOKIE` env var (Django sessionid; rotates ~every 2
  weeks).
- **SFOC sheet** (LNG carrier reconciliation): ID
  `1LwgbR4jnMrzaTIyhWeuOf0Z4Foj0lOMGEABBd58eIhY`; accessible ONLY via Drive MCP
  `read_file_content` (pipe-delimited markdown); direct CSV export returns 401.
- **GEM LNG tracker:** Sheet ID `1FjjeQD8AlQ_kQAMrohA3jAV3yZy7Lb61djt25D-4Fh8`,
  GID `243795339`; CSV export works; header at row index 1.
- **Python stack:** see `requirements.txt`.
- **GIS:** QGIS, GeoPandas, GeoJSON/GeoPackage/Shapefile; EPSG:4326 standard.

### Preferred external sources for pipeline research
OGJ, Rigzone, MEED, ATF Projects, S&P Global, Kpler, Shana, Tehran Times,
Pipeline Technology Journal, Offshore Technology, KS Al-Hajri, Samsung E&A,
Saudipedia, AramcoLife, Mehr News Agency, Interfax, IEA, EIA. Plus regulatory
filings (FERC, PHMSA, MARAD, Texas RRC, Alaska DNR) for US work.

---

## Common commands

```bash
# Refresh both CSV snapshots from the live sheet
./scripts/refresh_csvs.sh

# Fetch a pipeline route by ProjectID (e.g., P5367)
./scripts/fetch_route.sh P5367

# Install Python deps
pip install -r requirements.txt
```

---

## When starting a new task

1. Confirm the country + commodity scope.
2. Refresh CSVs (`./scripts/refresh_csvs.sh`) — don't work from stale snapshots
   for live research.
3. Load with `pd.read_csv(path, header=2, low_memory=False)`.
4. Follow the four-phase workflow in `docs/GOIT_Pipeline_Research_Workflow.md`:
   inventory → research → discovery → structured Excel output.
5. Run the quality checks listed at the end of the workflow doc before
   delivering.
