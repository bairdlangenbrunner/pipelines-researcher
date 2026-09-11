# EIA Natural Gas Pipeline Projects (US)

EIA's project-level tracker of US interstate and intrastate natural gas pipeline projects. It covers
new lines, expansions, laterals and compression. Each project row carries:

- operator, project type and status
- in-service year and completed date
- states, and beginning/end state
- cost ($ millions), miles, **additional** capacity (MMcf/d) and diameter (inches)
- regulating authority and FERC docket
- notes, demand served and website

Each release has a current-projects sheet and a historical-projects sheet. In every release the
header is the row containing `Project Name`, found by scanning, never by a fixed offset.

This is a **reference source for US gas research, not a reconciliation dataset.** It has no
geometry, so it has no `manifest.yml`, and `reconcile.py` does not run on it. It feeds
`scripts/eia_crosswalk.py`, which pre-matches GEM rows to EIA projects for sweep prompts.

## Files

- `raw/*.xlsx` (tracked): every release, May 2018 → Aug 2026. That is 28 dated files plus the
  undated `EIA-NaturalGasPipelineProjects.xlsx`, which is byte-identical to the newest dated
  release (`prepare.py` reports the twin).
- `raw/vintages.csv` (tracked): the file → release → origin URL → bytes → sha256 table.
- `prepare.py` → `data/` (gitignored, regenerate in ~30 s):
  - `eia_projects_long.csv`: one line per release × sheet × project row, keyed by
    `project_key = normalized name|operator`.
  - `eia_projects_latest.csv`: one line per project, with its latest values and a
    `<field>_history` column for status, in-service year, cost, miles, capacity and diameter
    (e.g. `Applied@2018-05 > Completed@2020-01`).

## Getting a new release

EIA posts a new file roughly quarterly at `https://www.eia.gov/naturalgas/pipelines/<file>`.

**File names are irregular.** Check EIA's pipelines page for the real link rather than guessing:
- most follow `EIA-NaturalGasPipelineProjects_<Mon><YYYY>.xlsx`
- `_July2019` and `_March2020` spell the month out
- `…ProjectsAug2026.xlsx` has no underscore, while `…Projects_May2026.xlsx` does

To fetch a file:
- Use a full GET with a browser User-Agent (`curl -sL -A 'Mozilla/5.0 …'`).
- Range requests and the directory listing return 403. HEAD returns 503.
- A 404 comes back as `text/html`, so check the content type before saving.

After downloading, re-run `python sources/eia_pipeline_projects/prepare.py`.

## How to use it in research

- **One origin.** Every release is EIA. Two releases agreeing is not two sources: pair EIA with a
  FERC filing or an operator/regulator document for rule 4's second source.
- **Cite the dated release that states the value.** Use a specific file URL, not the undated
  one (it changes every quarter). Put the sheet and Excel row in `note`, and pass `--name` with
  the EIA project name to `url_verifier` (it reads xlsx cell text).
- **History is the point.**
  - The first release showing `Completed` or `Cancelled` bounds the in-service or cancellation
    year.
  - A project that drops out of the current sheet without reaching `Completed` is a stale lead,
    not a cancellation, until a docket or operator source says so.
- **Capacity is incremental.** `Additional Capacity` for an expansion is the added MMcf/d, not the
  line's total. EIA `Miles = 0` usually means compression-only, which is GEM's
  expansion-with-no-new-pipe case (`LengthKnown = 0`, Diameter blank).
- EIA status words map loosely to GEM:
  - Announced / Pre-filing / Applied / Approved → proposed
  - Construction → construction
  - Completed → operating
  - On Hold → shelved
  - Cancelled / Denied → cancelled
  - `Part Completed` is a per-segment read.
