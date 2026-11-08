# Plan: primary and secondary page tags in the pipelines backend

Drafted 2026-11-06 with Baird. Background and the argument for the model: `wiki/design_tagging_and_maps.md`. This file is the implementation plan: what changes in the sheet, in what order, with which scripts, and what Baird decides at each gate. Nothing below is started.

**Superseded in part 2026-11-08 by `docs/plans/2026-11-08_network-pages.md`:** Baird chose new columns after all (`PrimaryNetwork`, `PrimaryNetworkLocalLanguage`, `SecondaryNetworks` with `;`), a primary/secondary network model, and a China-only scope with Guangxi as the pilot. The invariants and the audit tooling below still apply; the "no new column" ruling and D3/D6 do not. The China registry lives at `wiki/data/networks.json`.

## The model, restated after the blast-radius check

The design note proposed a new `NetworkTags` column. Checking who reads the existing columns changes that: `PipelineNetworkGrouping` is addressed by name in `gem-db-ops/gem_colmap.py` (`network_grouping`), used as a single value by `scripts/match.py` (synthetic network rows for reconciliation), `scripts/build_qc_workbook.py` (segment-name uniqueness within a network), `scripts/build_ref_worklist.py` (`--exclude-network-regex`, the China provincial-grid idiom) and `scripts/ref_pairs.py`, and it is a column in the public release summary sheets (`goit-ggit-data-ops/releases/summary-sheets/*`). A semicolon list in it would quietly break the matcher's network synthesis and change a public column. So: no new column, no list values, and the existing columns take the roles.

| Role | Column | Rule |
|---|---|---|
| Primary tag (the page the row's details live on) | `PipelineName` + `Wiki` | `PipelineName` is the page name. `Wiki` is `https://www.gem.wiki/` + the name with spaces as underscores, plus `#SegmentName` on a multi-row page. Exactly one page per row. |
| Row label and anchor inside the page | `SegmentName` | Unchanged. Blank on a single-row page. |
| Secondary tag 1 (network) | `PipelineNetworkGrouping` | One value, the English page name of the network page (`Shandong Gas Pipeline Network`). Stays single-valued. |
| Secondary tag 2 (second network, or the trunk a branch belongs to) | `AltPipelineNetworkGrouping` (oil) / `PipelineNetworkGroupingAlt` (gas) | One value, a page name. The two headers do the same job; whether to unify the header is decision D3. |
| Competing route variants | `AlternateRouteProjectIDs` | Unchanged; it is a relation between proposals, not membership. |
| Ownership team's system label | `PipelineNetworkContainer` (owners tab) | Untouched by this plan. |

Page type at generation time: a name that is some row's `PipelineName` is a pipeline page; a name that appears only in a grouping column is a network page, generated as roster plus map from the rows that tag it. A name in both is a pipeline page with a related-pipelines section.

Invariants the audit enforces, tracker-wide:

1. `page_name(Wiki) == PipelineName` for every row with a `Wiki` value (257 rows fail today, 34 of them because the page is named after the segment).
2. `Wiki` is filled (487 rows fail today). Whether the sheet column is filled or the generator derives it is decision D2.
3. Every grouping value is a page name: it exists on the wiki, or it is some row's `PipelineName`, or it is on the list of network pages the generator will create. Chinese grouping values on the gas tab fail this (72 values for China; 65 have a single derivable English page, 7 are ambiguous, see `wiki/out/china_gas_grouping_candidates.csv`).
4. One `PipelineName` per page (6 China gas pages fail, mostly spelling variants).
5. A grouping value never equals the row's own `PipelineName` (a network row tagging itself).

## Phases

### Phase 0: decisions (gate before any tooling)

- D1. Page-name rule: `PipelineName` is the page name, full stop. For the 257 rows where they differ today, the default resolution is that the row keeps its page and `PipelineName` takes the page name; the old `PipelineName` goes to the grouping column when it is a network or trunk name (the Shandong case), otherwise to `OtherEnglishNames`. The reverse (move the page to match the name) is the exception, chosen by hand when the page name is plainly wrong. Baird confirms this direction.
- D2. `Wiki` column: filled in the sheet for every row (recommended: it is what researchers and the release use) or left blank and derived by the generator.
- D3. Alt header: unify to one header on both tabs (touches `ref_pairs.py`, the colmap note, and the release notebooks' column lists) or keep both and have the generator read either. Recommended: keep both for now, unify at the next release.
- D4. Details live only on the primary page; network pages are generated rosters. (Design note recommendation.)
- D5. Stamping: a tag normalization is a spelling-level edit with no research behind it, so the lines carry `style_only` and the push stamps `LastUpdated` only, as the owner-style batch does. Or stamp `Researcher = CB` too.
- D6. China gas translation: accept the derived English page names for the 65 single-candidate groupings as the proposal, with the 7 ambiguous ones (`广东输气管网` spans four Guangdong network pages, `内蒙古输气管网` spans Inner Mongolia and Liaoning, `西气东输二线` and `中缅输气管道中国段` are trunks not networks) decided by hand.

### Phase 1: audit and proposal tooling (this repo, read-only)

- `wiki/scripts/tag_audit.py`: runs the five invariants over the newest snapshots, tracker-wide, with `--country` and `--commodity` filters; writes `wiki/out/tag_audit_<date>.xlsx` with one tab per invariant and a summary. Folds the rename logic from `readiness_report.py` so the step 3 renames list and invariant 1 are one computation.
- `wiki/scripts/propose_tags.py --country China --commodity gas`: proposes the edits that make each failing row pass, one line per cell: `PipelineName`, `SegmentName`, `Wiki`, `PipelineNetworkGrouping`, the Alt column, `OtherEnglishNames`, `OtherLanguageAlternativePipelineNames`. Each line carries a reason (`page named after segment`, `grouping translated from 山东输气管网`, `spelling variant merged`, `Wiki derived from PipelineName`) and a confidence (high when mechanical, medium when the translation came from a single candidate, low when a person must choose). Output is staged JSON in the review-app shape under `batches/wiki-tags/staging/update-wiki-tags-<date>/` with `meta.style_only = true` when D5 says so, plus a review workbook with current and proposed values side by side (`scripts/build_owner_style_workbook.py` is the pattern).
- Translation table: `wiki/data/network_page_names.json`, grouping value to English page name, seeded from the derived candidates and edited by hand for the ambiguous ones. The generator and `propose_tags.py` both read it.
- Both scripts: read with `keep_default_na=False`, drop non-`P` rows and `Status = N/A`, never write the sheet.

### Phase 2: China gas pilot (the messy case)

1. Fresh snapshot, run the audit and the proposal for China gas (985 rows, 120 pages). Expect roughly: 66 Shandong rows plus the rest of the 14 spread names get `PipelineName = page name` with the old name moving to the grouping column; 72 grouping values translated; 6 pages' spelling variants merged; 30 rows get a `Wiki` value.
2. Baird reviews in the review app (`scopes.py set` the batch; tag lines are column-only kinds so `clean_accepts.py --column-only` can auto-accept the high ones, holds the medium and low) or in the workbook.
3. Push accepted cells with `review_app/push.py` (plan, ask, `--apply`), backup CSV in `notes/`, stamps per D5. Re-run the audit on a fresh pull to confirm the China gas invariants pass.
4. Record the 7 hand decisions in `wiki/data/network_page_names.json` and in `docs/country_notes/china.md`.

Checks to do before step 3: `push.py` has no column whitelist that I found, but it has not written `PipelineName` or `Wiki` before; dry-run the plan on two rows first and confirm the cell text and the backup look right. `Wiki` cells may be formulas on some rows; the FORMULA pre-read aborts on those and they get handled by hand.

### Phase 3: China oil and the other grouped countries

China oil needs no renames (0 names spread over pages, 2 pages with name variants) and its 23 grouping values are already English page names; 22 have no page yet, which the generator will create. So the China oil pass is: fill `Wiki` for 100 rows, fix the 2 variant pages, confirm invariant 5. Then run the audit tracker-wide and work the remaining failures country by country: 257 renames in total, 487 blank `Wiki`, and the gas tab's 124 grouping values outside China (the Russia campaign and Kazakhstan passes already touched some of these; their country notes say which).

### Phase 4: hand-off and generator

- Update the template (`wiki/template/pipeline_page_template.md` and the Google Doc) so the page-grouping section says "one page per `PipelineName`" and adds the network-page variant (introduction, one map, members table, related pipelines, references). Add the anchor rule (D7 in the README list: `SegmentName` or `ProjectID`).
- Example tracker (`build_example_tracker.py`) adds a network-page example: a grouping value with its member rows across several pages.
- Readiness report's renames tab becomes the step 3 list the data team asked for, after the pilot.
- Map generation follows `wiki/design_tagging_and_maps.md` section 5 and is a separate plan once the data team's module exists.

## What this plan does not do

- No new tracker column, no header rename until D3 is decided.
- No sheet write outside `push.py`, no routes-repo change, no wiki page edit. Network pages are created by the generator, not by hand.
- `PipelineNetworkContainer` on the owners tab stays as it is.
- Does not touch the hand-built page route in `scripts/build_wiki_pages.py`; that gets the table layout when the template is approved (`wiki/README.md`).

## Effort

Phase 1 is a day of scripting. Phase 2 is a half day of Baird's review time for the China gas lines plus a push. Phase 3 scales with the rename count per country and is best done inside each country's next batch. Phase 4 waits on the data team.
