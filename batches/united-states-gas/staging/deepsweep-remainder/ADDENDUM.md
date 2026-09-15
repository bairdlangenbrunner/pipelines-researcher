# Batch-5 addendum — rules this batch's rebuild established

Written 2026-09-15 during the batch-5 rebuild. Everything here is a defect that reached a
delivered workbook (`20260910_1526_ET`) and had to be repaired afterwards, so it belongs in
the dispatch brief of every later US-gas batch.

## Cite the EIA release, never the undated workbook — and pin the Excel row

`https://www.eia.gov/naturalgas/pipelines/EIA-NaturalGasPipelineProjects.xlsx` (no date) and
`https://www.eia.gov/naturalgas/data.php` are both banned as refs: the first is a moving
target that will not say tomorrow what it says today, the second states no value at all. The
citable form is the dated release:

```
https://www.eia.gov/naturalgas/pipelines/EIA-NaturalGasPipelineProjects_<Mon><Year>.xlsx
```

— underscore before the month on every release **except Aug 2026**, which is the lone
un-underscored `EIA-NaturalGasPipelineProjectsAug2026.xlsx`. 165 records in this batch cited
the undated file and were re-grounded onto Aug2026; the verification note now ends with a
`[file / sheet '<name>' / Excel row <n> / project '<name>']` citation so a reader can land on
the exact cell. Write that citation when you stage the ref, not afterwards.

The 29 dated workbooks are cached under `sources/eia_pipeline_projects/raw/`, and
`sources/eia_pipeline_projects/data/eia_projects_long.csv` is every row of every release in
one long table (`release, file, sheet, excel_row, project_name, …`) — use it to find the row
rather than opening the xlsx.

## EIA carries the same project TWICE in one release — check before you cite a row

`Columbia to Eastover Pipeline` sits at **row 833** (`Completed`, completed 2016-11-01, last
updated 2018-01-24) **and row 838** (`Construction`, blank completion, last updated
2016-08-30) of every workbook since 2018. The second is a stale pre-completion copy EIA never
removed. Taking "the newest release's row for this name" without disambiguating picks whichever
the reader emits last — which would have made two researchers' notes ("Status = Completed,
Completed Date = 2016-11-01") cite a row that says neither.

So: when a project name resolves to more than one row in the release you are citing, say which
one you mean by Excel row number and by the field values you read out of it. If they disagree,
the one whose `Last Updated Date` is later is the live record — but cite it explicitly, never
implicitly.

Corollary for notes: an explicit `row <n>` in your own prose is the most specific thing you can
write, and it is what disambiguates you later. Two of this batch's records
(`TETCO TEAM 2012 Expansion` at row 731 vs `TETCO TEAM 2014 Expansion` at row 785) were only
separable because their notes named the row.

## `contested` is `{backend column: candidate value}` — a value, not a sentence

The candidate renders in the workbook's cell comment as `Candidate value(s): <col> = <val>`,
directly under the record's own `recommendation`. So prose in the value slot is duplication at
best and an un-pasteable suggestion at worst. Twelve records here carried sentences
(`"unclear -- see notes"`, `"53.10 km is ~1.8% below TEAM 2014's confirmed 33.5-33.6 mi ..."`).

- Proposing a replacement → the bare value: `{"Owner1": "BlackRock"}`.
- Disputing the current value with no replacement → the **empty string**: `{"StartYear1": ""}`.
  The cell still tints and still carries the whole comment; it just stops implying a candidate
  that does not exist.
- The reasoning goes in `recommendation` and `researcher_notes`, which is where a human reads it.
- A candidate must be a value the live column actually accepts. `CapacityUnits: "MDth/d"` is
  not — the column holds `bcm/y, MMcf/d, MMSCMD, TJ/d, mill.Sm3/day, GWh/d, Mcf/d, m3/d, mtpa`
  — so convert, and flag the conversion in the recommendation.

## UNRESOLVED proposes nothing

`class_out: "UNRESOLVED"` means **nothing was found**. It therefore carries
`proposed_refs: []`, `tier: "low"`, `independent: false`, and no verification marked
`ok + contains_value`. Six records here were UNRESOLVED while staging 1–3 refs, which would have
written an orphan `[ref]` with no paired value. The pages you searched still belong in
`verifications` with `contains_value: false` — that is the search record, and it is what makes
the negative finding credible.

Two shapes that look like exceptions and are not:

- **A page that proves your recorded value is wrong** is evidence for a negative finding, not a
  ref for the value. It states no value for your unit → `contains_value: false`.
- **A blank that is the CORRECT value** (an expansion with no new pipe → `Diameter` blank) is
  still UNRESOLVED with no refs, because a `[ref]` cell with no paired value is barred outright.
  Say in the notes that blank is correct and why.

And the inverse, which cost this batch a record: **a source that states your recorded value IS a
ref.** Confirming a recorded value is `REFS_ADDED` with the same value — an output, not a no-op
(Rule 4(e)). A later-era disagreement is a *separate* finding that goes to a `validity` record
with `contested`; it does not turn a sourced confirmation into "nothing found".

## A status verdict that no URL can ever back is not a status verdict

`check_shard_coverage.py` rejects `verdict: "change"` (or `"stale"`) with no `proposed_refs`,
because merge QC rewrites it to `unclear` and the recommendation silently dies. That gate is
right, and the fix is usually to stage the URLs the notes name.

But one shape here can never satisfy it: `ShelvedCancelledType: confirmed → inferred` inferred
from **absence** (no cancellation document exists anywhere). Standing rule 2 forbids
manufacturing a URL for it, so as a status verdict it is unmergeable by construction. Re-key it:
the status review says what it actually found (`confirm` — the recorded Status stands), and the
recommendation moves to a `validity` record with `contested: {"ShelvedCancelledType":
"inferred"}`, where an empty `proposed_refs` list is the correct shape and the finding still
reaches the paste surface. Re-key, do not re-research.

## Tier is arithmetic, not emphasis

Unchanged from the slice-2 brief and repeated because 103 records here needed it: `tier: "high"`
and `independent: true` require **2+ distinct publishing origins** among the refs that actually
verified. All EIA releases together are ONE origin; so are multiple filings by one EDGAR
registrant, multiple notices in one FERC docket, and multiple Wayback captures of one site. A
trade-press article restating a company's own press release is one origin, not two. Run
`python3 scripts/audit_shard.py <shard>` — it does this arithmetic for you and exits non-zero.
