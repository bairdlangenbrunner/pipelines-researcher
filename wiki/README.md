# Pipeline wiki page automation

Prep work for getting GOIT (oil and NGL) and GGIT (gas) pipeline pages on gem.wiki generated automatically, the way most other GEM trackers already are.

## How GEM does this

The data team generates and uploads every tracker's pages from one shared repo, [`GlobalEnergyMonitor/GEMwiki`](https://github.com/GlobalEnergyMonitor/GEMwiki). It is maintained by Hannah Howell. It is not Baird's repo, so it is read-only from here: a local clone with a local `baird` branch sits at `../GEMwiki`, set so it cannot push. Pipelines are not in it yet. The closest existing module is LNG terminals (`MainTrackers/LNG/`), which has one page per terminal and one table row per unit. Pipelines would follow the same pattern, with one page per pipeline and one table row per segment.

A run of that repo looks like this: `python launcher.py generate <tracker> --input_file <csv>` writes one `.txt` of wiki markup per page, then `python launcher.py upload <tracker> --wikisource-directory <dir>` posts them. The generator rewrites only its own sections. Anything a person wrote between the "COMMENT 2" and "COMMENT 3" markers, such as Background, is kept on every run. The ownership tree is a separate insert the data team adds (`generate_insert ... --section "ownership tree"`).

## The data team's prep steps, applied to pipelines

The steps come from the data team's doc "Steps for Readying Information for Wiki Page Generation" (updated 23 Apr 2024, Google Doc `19lsxh3ZRTlELVKaA2O8iL61vFrmGwX9S07yHrhpts-M`).

| Step | What the data team asks for | Pipelines status | Where |
|---|---|---|---|
| 1 | A page template in the shared "Templates for GEM Wiki Page Layout" folder, with tracker column names highlighted and conditional wording in comments | Draft written here and pushed into the Google Doc "Wiki page template - gas pipelines (draft)" (`13QZ-mOGYlNqgwfKbK8cxh4z1nZ5iXdzqSEB8DuzCIeI`, Templates folder) on 2026-11-06; being edited there | [`template/pipeline_page_template.md`](template/pipeline_page_template.md), `scripts/md_to_gdoc.py` |
| 2 | The template plus an example tracker sheet, sent in an Asana task | Example sheet builder written; Asana task not opened | `scripts/build_example_tracker.py` → `out/` |
| 3 | A list of projects whose names changed since the last release, so the data team can move pages | Readiness report lists every row whose wiki page name differs from `PipelineName` | `scripts/readiness_report.py` → `out/` |
| 4 | Data team writes the code and sends sample pages | Not started | |
| 5 | Final tracker data sent to the data team | Not started | |
| 6 | Zip of generated `.txt` pages to review; sample pages on the wiki | Not started | |
| 7 | Data team uploads (300 pages per minute) | Not started | |
| 8 | Search the uploaded pages for bugs and report them | Not started | |

Pipelines are not in GEM's database, so the "fully in the database" shortcuts in steps 2, 3 and 5 do not apply. The tracker data goes to the data team as a file.

The doc warns that the turnaround stretches by about a week each for a thin template, an unclear page layout, unsettled column headers, or uncleaned data. That is why the template is detailed and why the readiness report lists data gaps as well as renames.

## Running

```bash
./scripts/refresh_csvs.sh                       # fresh snapshots first
python wiki/scripts/readiness_report.py         # renames, new pages, data gaps
python wiki/scripts/build_example_tracker.py    # example tracker xlsx for the data team
python wiki/scripts/md_to_gdoc.py wiki/template/pipeline_page_template.md <docId> --dry-run   # push the template into a Google Doc (drop --dry-run to write; needs gws-gem-write and Baird's OK)
```

The first two scripts read the newest `data/*_snapshot_*.csv` files and write to `wiki/out/`, which is gitignored because the outputs copy tracker rows. Before anything is sent to the data team, the example sheet drops the `ResearcherNotes` and `ESJNotes` columns.

## Relationship to the existing wiki tooling

`scripts/build_wiki_pages.py` and `docs/sops/wiki_pages.md` hand-build draft pages for new pipelines and post them after review. That remains the route until the data team's generator covers pipelines. Its Project Details is a bullet list. The template here switches to the numbered tables the other trackers use, so the hand-built drafts should move to the same layout once Baird approves the template. Then a hand-built page and a generated page will look the same.

## Decided

- **Five or more segments: one tabbed table (Baird 2026-11-06; threshold lowered from ten the same day).** `scripts/generate_pages.py` replaces Tables 1 to 5 with one sortable table under Project Details and a Route / Details / Timeline / Cost / Ownership / All columns tab strip, CSS only, styled by `Template:Segment table/styles.css` (pushed with `--push-styles`). Smaller pages keep the five tables. The route map's click popup is tightened by `Template:Pipeline map/styles.css` (also pushed with `--push-styles`) and shows a status-colored dot. The row label is "Segment" on every table. Live on Transcontinental Gas Pipeline; mockup at https://claude.ai/artifact/Cs1KMu8zBctA2uRdap3crR.
- **Parent column next to Owner (Baird 2026-11-06).** Filled from the gas tab's Parent cell as the backend has it; parents stay the ownership team's research. Maps are `width=100%` so pages fit a phone screen.
- **Map colors match GEM's website tracker maps; headings are sentence case (Baird 2026-11-06).** Lines and route-shape pictures are colored by status from the website map config, with a legend line under the map on pages with several segments. Headings read "Project details", "Articles and resources".

## Open decisions

Tabled on 2026-11-06; Baird wants to work through them later. Items 1 to 4 are listed in the template too, where each one applies. Items 5 to 11 come from [`design_tagging_and_maps.md`](design_tagging_and_maps.md), which argues each one; the backend side is planned in [`docs/plans/2026-11-06_wiki-tagging-backend.md`](../docs/plans/2026-11-06_wiki-tagging-backend.md) (decisions D1 to D6 there gate phase 1).

1. Page names: keep each page at its current `Wiki` URL, or move pages so they match `PipelineName`? The readiness report counts both sides. The design note recommends `PipelineName` is the page name and `Wiki` is derived from it.
2. Parent companies: decided 2026-11-06, see Decided.
3. Oil's `Background` column: use it to seed Background on new pages only, or ignore it?
4. Status categories: decided 2026-11-08, no categories on generated pages.
5. Page type rule: row details only on the primary page, with network pages generated as a roster plus one map (recommended), or keep per-segment details on network pages as the China pages have now.
6. Tracker columns: the implementation plan (`docs/plans/2026-11-06_wiki-tagging-backend.md`) drops the new `NetworkTags` column after a blast-radius check (`match.py`, `build_qc_workbook.py`, `gem-db-ops` colmap and the public release sheets all read `PipelineNetworkGrouping` as one value). Instead `PipelineNetworkGrouping` is secondary tag 1 and the Alt column is secondary tag 2, both single page names; whether to unify the two Alt headers is open.
7. Whether the owners tab's `PipelineNetworkContainer` systems also become network tags.
8. China gas: translating the 72 Chinese `PipelineNetworkGrouping` values to English network page names, and who checks the translation.
9. Map coloring: decided 2026-11-06, by status in the website map's colors with a legend (see Decided). Names show on click, not hover (Maps 13 limit).
10. Whether to test Maps' `geojson=` input on the test wiki before building the `lines=` generator.
11. Row anchors on multi-row pages: `SegmentName` or `ProjectID`.
12. The Google Doc is titled for gas pipelines while the template covers both trackers: one doc for both, or split it.
