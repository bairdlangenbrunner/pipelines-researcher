# GOIT/GGIT Project — Setup & Context

This document orients a fresh Claude session (in the migrated workspace project) to the
GOIT/GGIT pipeline-research work. Read this first.

---

## 1. What this project is

Maintaining and improving Global Energy Monitor's open-access pipeline databases:
- **GOIT** — Global Oil Infrastructure Tracker (crude oil + NGL pipelines, worldwide)
- **GGIT** — Global Gas Infrastructure Tracker (gas pipelines)
- Related trackers: LNG terminals, LNG carrier vessels

Work spans: pipeline infrastructure research (global, with depth in MENA, US, Iran, Iraq,
Saudi Arabia), GIS/geospatial processing, database QC, and agentic AI research/reconciliation
workflows. Output goal: a clean, well-sourced, publication-ready database with accurate
statuses, geometries, and metadata.

Researcher initials in the tracker: **CB**.

---

## 2. STANDING RESEARCH RULE (do not violate)

**Never use GEM, gem.wiki, Global Energy Monitor, or globalenergymonitor.org as a source or
citation unless explicitly requested.** The point is to surface what *other*, independent
sources exist.

---

## 3. Live data access

The live backend Google Sheet is set to "Anyone with link can view" permanently.

**Sheet ID:** `1foPLE6K-uqFlaYgLPAUxzeXfDO5wOOqE7tibNHeqTek`

Pull individual tabs via bash + curl using the CSV export URL:

```bash
curl -sL "https://docs.google.com/spreadsheets/d/1foPLE6K-uqFlaYgLPAUxzeXfDO5wOOqE7tibNHeqTek/export?format=csv&gid={GID}" -o tab.csv
```

**Tab GIDs:**
- oil/NGL = `456134080` (107 cols)
- gas = `1020144097` (~140–143 cols)

**Header is at CSV row index 2** for both tabs (rows 0–1 are metadata). Read with
`pd.read_csv(file, header=2, low_memory=False)`.

Each tab is well under 10 MB.

**Do NOT:**
- Use Drive MCP `download_file_content` (returns only the first tab)
- Use Drive MCP `read_file_content` (lossy summary, truncates rows)
- Use `web_fetch` on the export URL (won't accept URLs not literally provided in-turn)

The `data/` folder in this bundle contains dated CSV snapshots of both tabs so the project has
offline data immediately. Re-pull with the curl commands above to refresh.

---

## 4. Pipeline routes (GeoJSON)

Public GitHub repo: `https://github.com/GlobalEnergyMonitor/GOIT-GGIT-pipeline-routes`
- Fetch individual files via `raw.githubusercontent.com`
- List folder contents / locate files by ProjectID via the GitHub API:
  `https://api.github.com/repos/GlobalEnergyMonitor/GOIT-GGIT-pipeline-routes/contents/{path}`

Local mirror (on Baird's machine, not in this bundle):
`/Users/baird/Dropbox/_git_ALL/_github-repos-gem/GOIT-GGIT-pipeline-routes`

EPSG:4326 is the standard projection.

---

## 5. Column / schema notes

- **Column order:** Always ask Baird to paste the header row rather than inferring from the
  data dictionary — the dictionary's `OilOrderInSheet` column is unreliable.
- Several oil-sheet columns are absent from the data dictionary, e.g.: `Disrupted`, `RMI`,
  `QCCOwner2025Update`, `OwnerEntityIDs`, `AlternateRouteProjectIDs`.
- Cost columns are named `Cost`, `CostUnits`, `Cost [ref]` — NOT `ProjectLevelCost`.
- `OtherEnglishNames`: semicolon-separated.
- `SheetRow` = CSV index + 4.
- **Buffer rows:** ~104 rows with reserved ProjectIDs should be excluded from QC.

### Owner field conventions
- `--` is a valid sentinel for unknown ownership.
- Separator characters (commas, ampersands, slashes) inside Owner strings are legitimate
  (they appear inside real company names) — do not flag them.

---

## 6. Controlled-vocabulary casing (locked)

- **lowercase:** Status, RouteAccuracy, PipelineType
- **Title Case (exceptions):** DelayType, ShelvedCancelledType, FIDStatus, Delayed, Opposition
- `very high (within meters)` is a valid RouteAccuracy value.
- Lowercase is the de facto sheet convention even where older standing rules say otherwise.
- When in doubt, pull a real row and match exact casing/spelling.

(Full vocabularies are in `GOIT_Pipeline_Research_Workflow.md`.)

---

## 7. Key principles & learnings

- **Expansion vs. new construction:** Always verify whether new physical pipe is being built.
  If not → length = 0, diameter = blank.
- **URL verification:** Never fabricate source URLs. If a URL can't be confirmed, describe the
  source precisely or flag as inferred/presumed. Inferred status changes →
  ShelvedCancelledType = Presumed, no fabricated URL.
- **Diameter flags** are review items, not auto-rejections.
- **WKT/route-format checks** are permanently dropped from the QC workbook.
- **Web search strategy:** Decompose pipeline IDs into component parts (trunk line, KP
  reference, commodity, receiving facility) when exact-string queries fail. Adding
  contract/procurement keywords (year ranges, "tender," "construction") beats route-based
  queries alone.

---

## 8. Approach & patterns

- Stepwise, one-sheet-at-a-time for QC workbook builds (avoids token/message limits, allows
  review between steps).
- Iterative pushback expected and welcome — Baird challenges data points, source URLs, and
  methodology. Don't defend wrong findings; revise on evidence.
- Resume bundles (zip with scripts, cache, README) packaged at session close for continuity.
- Country-level research → multi-tab Excel workbooks (Summary, Existing Entries, Discovery,
  Context, Search Log).
- Excel outputs: red highlight for changes (`FFCCCC` fill, `CC0000` font), green for new
  (`E2EFDA`), blue headers (`4472C4`) white bold, freeze panes at row 2.

---

## 9. Active workstreams (as of migration)

1. **GulfPub ↔ GEM Saudi Arabia comparison** (`GOIT_SaudiArabia_Gulfpub_Comparison.xlsx`):
   confidence-check logic (green/yellow/red) for matched records. In progress: when a matched
   GEM pipeline has low/medium route accuracy, compare GEM route to GulfPub route for spatial
   consistency and factor into confidence scoring (GulfPub routes treated as more accurate for
   low/medium GEM entries; human review step). Route GeoJSONs via the public GitHub repo.
2. **GOIT oil/NGL QC workbook** (`GOIT_oil_ngl_QC.xlsx`): Sheets 1–8 (Status, RouteAccuracy,
   OtherVocab, Owner format, WikiLink Health, Geo Consistency, Name Uniqueness, Date Logic)
   plus Sheet 9 (Diameter_OutOfRange) and Sheet 11 (BroadSweep_Misc). Sheet 10 (route/WKT)
   permanently dropped. Clean rebuild of Sheets 1–8 against latest CSV was pending.
   NOTE: this workbook is NOT in this bundle — re-locate or rebuild from the resume bundle zip.
3. **Country-level research:** 80+ countries covered in a prior global sweep; Iraq, Iran,
   Saudi Arabia have had deep dives.

### Pending country items
- **Iran:** P6074 (Goureh–Persian Gulf Coast) needs verification before any duplicate/removal
  decision. P5367 (Golpa–Moghanak) reclassification as a Neka–Ray segment rather than
  standalone entry.
- **Iraq:** Grand Faw Port third offshore pipeline (Esta/Micoperi, contracted April 2025)
  entered as a single new row. Basra–Haditha (P0544) status may need review (listed as
  "construction" but appeared still in pre-construction/tender phase as of early 2026).
- **LNG carrier tracker:** quarterly reconciliation workflow designed and partially executed
  against SFOC partner data; methodology in `instructions.md` (not in this bundle).

---

## 10. Tools & resources

- **GEM Project Database MCP server:** TypeScript MCP server around
  `gem-project-db.herokuapp.com`; auth via Django `sessionid` cookie (`GEM_SESSION_COOKIE`
  env var); ~10 tools (`list_projects`, `get_project`, `list_units`, `get_unit`,
  `list_entities`, etc.); session cookie expires ~every 2 weeks.
- **SFOC Google Sheet** (LNG carrier reconciliation): ID
  `1LwgbR4jnMrzaTIyhWeuOf0Z4Foj0lOMGEABBd58eIhY`; accessible ONLY via Drive MCP
  `read_file_content` (pipe-delimited markdown); direct CSV export returns HTTP 401.
- **GEM LNG tracker:** Sheet ID `1FjjeQD8AlQ_kQAMrohA3jAV3yZy7Lb61djt25D-4Fh8`,
  GID `243795339`; accessible via direct CSV export; header at row index 1.
- **Asana:** country-assignment tracking lives here (not in Google Drive).
- **Python stack:** pandas, openpyxl, geopandas, shapely, fiona.
- **GIS tools:** QGIS, Python/GeoPandas, GeoJSON, GeoPackage, Shapefile; EPSG:4326.

### Key external sources for pipeline research
OGJ, Rigzone, MEED, ATF Projects, S&P Global, Kpler, Shana, Tehran Times, Pipeline Technology
Journal, Offshore Technology, KS Al-Hajri, Samsung E&A, Saudipedia, AramcoLife, Mehr News
Agency, Interfax, IEA, EIA.

---

## 11. Post-migration setup checklist

In the new workspace Claude Project:
- [ ] Upload the files in this bundle (see MIGRATION_README.md).
- [ ] Link/connect the GEM Shared Drive to the new project.
- [ ] Re-connect MCP connectors as needed (GEM Project Database, Google Drive, etc.).
- [ ] Refresh the `GEM_SESSION_COOKIE` for the GEM Project Database MCP if expired.
- [ ] Re-locate or rebuild `GOIT_oil_ngl_QC.xlsx` and the LNG carrier `instructions.md`
      (these live in a separate resume bundle, not included here).
- [ ] Verify the curl CSV pull works from the new environment.
