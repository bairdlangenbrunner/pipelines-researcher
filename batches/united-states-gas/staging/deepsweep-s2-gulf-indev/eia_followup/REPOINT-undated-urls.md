# Delta pass: repoint EVERY undated-EIA-workbook citation in ONE shard

You are given one `<PID>`. Work **only** on
`batches/united-states-gas/staging/deepsweep-s2-gulf-indev/rows/<PID>.json`.
Do NOT redo the row's research. Do NOT touch any other file.

## The defect

These shards were researched before the EIA archive landed. Their citations point at

    https://www.eia.gov/naturalgas/pipelines/EIA-NaturalGasPipelineProjects.xlsx

the **undated** workbook. EIA replaces that file every quarter, so a citation to it does
not durably state anything, and it must never appear in a `[ref]`. Every occurrence has
to become a **dated release URL** that actually states the value.

It appears in up to five places — fix all of them:
- `fills[].proposed_refs[].url`
- `fills[].verifications[].url`
- `validity[].proposed_refs[].url`
- `status_reviews[].proposed_refs[].url`
- `cross_row_leads[].url`

## Procedure

1. `grep -n 'EIA-NaturalGasPipelineProjects\.xlsx' <file>`. A URL that already carries a
   month/year (`…ProjectsAug2026.xlsx`, `…Projects_May2026.xlsx`, `…Projects_July2019.xlsx`)
   is fine — leave it. Only the bare undated one is in scope.
2. Identify the EIA project row this shard is about, once, up front:
   - `sources/eia_pipeline_projects/data/eia_projects_long.csv` — one line per
     release x sheet x project. Filter on the project name / operator / FERC docket.
     (If `data/` is missing: `python sources/eia_pipeline_projects/prepare.py`.)
   - `sources/eia_pipeline_projects/raw/vintages.csv` — file -> origin URL. Take the URL
     from this table **verbatim**; never construct one.
3. For each occurrence, work out which **value** it is cited for (the enclosing record's
   `ref_col` / `primary_value`, or the validity/status_review claim), then find the dated
   release that states that value:
   - Default to the **newest** release that states it.
   - If the note is about when a value first appeared or changed, cite the release that
     marks the transition instead.
   - Confirm the value in the release itself
     (`sources/eia_pipeline_projects/raw/<file>.xlsx`) and record the **sheet name and the
     Excel row**. The header is the row containing `Project Name`, found by scanning.
4. Replace the URL, and make the accompanying `note` / `researcher_notes` state the sheet
   and Excel row. Re-run each new URL through
   `python scripts/url_verifier.py --name "<EIA project name>" <url>` and update the
   matching `verifications` entry with the real result. Do not leave a stale verification
   pointing at the old URL.
5. If **no** dated release states the value — EIA is blank for that field in every release
   carrying the project — then the citation was wrong, not merely undated. Drop that ref
   and its verification; if the unit has no ref left, set `class_out` to `UNRESOLVED` and
   say in `researcher_notes` that EIA was checked across every release carrying the project
   and the field is blank in all of them.

## Rules that still apply

- **All EIA releases are ONE origin.** Two releases agreeing is one source. `independent`
  stays `false` on a unit whose only origin is EIA — fix it if you find `true` there.
- Never cite GEM. Never invent a URL. Never drop a once-working non-EIA ref.
- Keep every record this pass does not change. Do not reorder or renumber anything.
- Append one line to `summary` saying how many citations you repointed and to which releases.

## Gate (blocking, before you finish)

```
python scripts/check_shard_coverage.py --staging batches/united-states-gas/staging/deepsweep-s2-gulf-indev --pid <PID>
grep -c 'pipelines/EIA-NaturalGasPipelineProjects\.xlsx' batches/united-states-gas/staging/deepsweep-s2-gulf-indev/rows/<PID>.json
```
The coverage gate must print OK and the grep must print `0`. Both are required.

Report: how many citations you repointed, which releases you cited, and any unit that fell
back to UNRESOLVED.
