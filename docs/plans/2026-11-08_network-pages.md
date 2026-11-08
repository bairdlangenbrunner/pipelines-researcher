# Plan: network pages with primary and secondary networks (China first)

Drafted 2026-11-08 with Baird. Supersedes the column decisions in `docs/plans/2026-11-06_wiki-tagging-backend.md` (that plan's audit invariants still hold; its "no new column" ruling does not). Background: `wiki/design_tagging_and_maps.md`. Registry: `wiki/data/networks.json`. Nothing on the wiki or the sheet is changed by this plan until each gate below is passed.

## Scope

China gas only. Networks outside China are on hold (Baird 2026-11-08): the registry does not list them, the generator's network mode refuses a network with no registry entry, and the non-China grouping values (owner groups, market zones, trunk labels) are not touched. Oil is out of scope.

## The three levels

| Level | Sheet field | Wiki surface |
|---|---|---|
| Network | `PrimaryNetwork` (one value per row, same on every row of a PipelineName) | A network page: rollups, a Pipelines table, a map of every segment, the segment table of its direct segments, Background with one subsection per pipeline |
| Pipeline | `PipelineName` | A pipeline page as today (`wiki/scripts/generate_pages.py`), plus a "Part of the X network" line in the lead and the network's name in the infobox-style Pipelines table |
| Segment | `SegmentName` (anchor `row-<PID>`) | A row on its pipeline's page, never a page of its own |

Researchers' `PipelineName`s are never renamed to fit a page (gem_schema, 2026-11-07). The network organizes; the names stay.

## Primary and secondary networks

- A pipeline has at most one primary network and any number of secondary networks. Both behave like tags.
- The primary is where the pipeline is counted: the network page's length total, status mix and segment count include it, and its segments draw at full weight on the network map.
- A secondary is navigation only: the pipeline is listed under "Connected pipelines" on that network's page and drawn lighter on its map (opacity 0.45, weight 2), and it is never in that network's totals. The pipeline page says "Also connected to Y".
- Invariant: every row of one PipelineName carries the same primary. The audit flags a split (P7668 today).
- A one-row pipeline that is not a network of anything still has a primary when it belongs to a grid (the Beijing case: one row, one network, no network page).

## Sheet columns

New columns on the Gas tab, added when Baird decides (gate 2): `PrimaryNetwork`, `PrimaryNetworkLocalLanguage`, `SecondaryNetworks`.

- `PrimaryNetwork`: English, one value, the network page title. For China it is the registry's English name for the row's current `PipelineNetworkGrouping`.
- `PrimaryNetworkLocalLanguage`: the local-language name; for China the Chinese characters that sit in `PipelineNetworkGrouping` today.
- `SecondaryNetworks`: English names separated by `;`. A checkbox-style tag picker can replace the free text once a networks tab exists; the separator is the contract until then.
- `PipelineNetworkGrouping` and `PipelineNetworkGroupingAlt` are left in place for now. `gem-db-ops/gem_colmap.py` (`network_grouping`), `scripts/match.py` (synthetic network rows), `scripts/build_qc_workbook.py`, `scripts/build_ref_worklist.py --exclude-network-regex`, `scripts/ref_pairs.py` and the public release summary sheets all read the grouping column by name. Because `PrimaryNetwork` is single-valued it can replace `PipelineNetworkGrouping` later with a colmap alias and one release-notes line; `SecondaryNetworks` is a list and must never be pointed at by those readers. Whether the grouping column is eventually renamed or retired is a later decision, not part of this plan.
- The generator reads `PrimaryNetwork` when the column exists and otherwise maps `PipelineNetworkGrouping` through the registry, so the wiki work does not wait on the sheet columns.

**Networks tab (created 2026-11-08, Baird's request):** the backend's `Gas pipeline networks` tab (gid 132857322) holds one row per network, header in row 1, written from the registry: `NetworkID` (N0001.., stable key), `NetworkName` (English; the value the Gas tab's `PrimaryNetwork` and `SecondaryNetworks` carry), `NetworkNameLocalLanguage`, `Countries`, `NetworkType`, `Pipelines` (member PipelineNames, `;`), `PipelineCount`, `SegmentCount`, `LengthKnownKm`, `Wiki`, `WikiPageKind`, `Notes`, `Researcher`, `LastUpdated`. `SegmentCount` and `LengthKnownKm` are snapshot values from the creation date, not formulas; a refresh rewrites them from a fresh pull. The registry (`networks_tab` key) and the tab are kept in step: edit the registry, rewrite the tab, never hand-edit one without the other. Backup: `notes/sheet-backup-2026-11-08-gas-pipeline-networks-tab.csv`.

## Network page rules

Which page a network gets, from the registry's `page_case`:

1. The network has one PipelineName: no extra page. The pipeline page is the network page and its lead names the network (66 of 72 Chinese networks today).
2. Several PipelineNames and one of them equals the network's English name: that page becomes the network page. Its own rows are the direct segments; the other names are listed in a Pipelines table and link to their own pages (Guangdong, Guangxi, Xinjiang, Sebei-Xining-Lanzhou, and West-East Gas Pipeline 2 until P7668 moves).
3. Several PipelineNames and none matches: a new page at the registry's English name (today only 川渝输气管网, proposed as Sichuan-Chongqing Gas Pipeline Network; Baird decides the name).

Sections of a network page, in order: lead; Location with the map of every primary segment at full weight and every secondary pipeline lighter; Pipelines (table: pipeline, local name, segments, length, status mix, link), then Connected pipelines (the secondaries, same columns, no totals); Project details with the tabbed segment table gaining a Pipeline column (direct segments and member pipelines' segments together, sortable by pipeline); Background with a Network background subsection first and then one subsection per pipeline holding that pipeline's segment background table; Articles and resources as today. The lead's "also known as" list is built from the network's own rows only, never from a segment's local name (the live Guangxi lead leaks 中缅管道钦州支线（南宁-钦州）, a segment alias).

Folding standalone segment pages: a page whose title is a SegmentName is folded onto its pipeline's page by default. Its Background prose moves onto the pipeline page under the segment's subheader, or into the segment background table when the page uses the tabbed layout. Its citations are carried through the generator's refs ledger (`audit_refs`: a lost citation blocks the save). The old title is left as a redirect; this account cannot delete pages.

Categories: on hold (Baird 2026-11-08). No network category, no per-network category, until the pilot has been looked at.

## Pilot: Guangxi

Network 广西输气管网 / Guangxi Gas Pipeline Network, case 2. 42 rows today, 43 once P7668 moves. Members: Guangxi Gas Pipeline Network (33 direct segments, 2,021 km), Guangxi LNG Terminal Transport Pipeline (8 segments, 1,620 km, Guangxi and Yunnan), Nanning-Pingxiang Gas Pipeline (2 segments, 225 km). Every row's Wiki cell already points at the Guangxi page, so the pilot changes the page's shape and not its row set. Secondary candidates for its Connected pipelines list are in the registry's `secondary_proposals`; Baird picks.

Steps:

1. Mockup (done 2026-11-08): hand-built wikitext of the pilot page from the live text, for approval. No save.
2. Generator `--network <English name>` mode in `generate_pages.py`: rows = every row whose registry-mapped primary is the network; direct segments = rows whose PipelineName equals the page name; the sections above. Pipeline pages gain the two lead lines. Preserved sections (COMMENT2 to COMMENT3) are carried as today.
3. Dry run to `wiki/out/samples/`, compare with the mockup, render through action=parse, check the refs ledger (nothing lost).
4. Save through `scripts/wiki_save.py` from the work profile, one page, after Baird's OK. Then the member pipelines' pages (none exist standalone for Guangxi today; the two member names have no page of their own and get none until Baird wants them).
5. Audit: `python wiki/scripts/network_audit.py` (to write) checks the invariants: one primary per PipelineName, every primary in the registry, every registry page exists or is a PipelineName, no secondary equal to the primary, no grouping value equal to the row's own PipelineName.

## Gates (Baird decides)

1. The mockup's shape (this turn).
2. Adding the three sheet columns, and when: before the generator mode (so it reads the sheet) or after the pilot (so the registry stands in). Recommended: after the pilot.
3. P7668's grouping move to 广西输气管网, and the other grouping fixes already on the list (P4553, P3894, P8037). Each is a sheet write under the hard requirements: FORMULA pre-read, backup CSV in `notes/`, RAW cell-scoped write, re-read, `Researcher` = CB and `LastUpdated` stamped.
4. The name for 川渝输气管网 and whether the four Central Asia–China line groupings merge into one network.
5. Which secondary proposals become `SecondaryNetworks` values for the Guangxi pilot.
6. Extending past Guangxi: Guangdong and Xinjiang next (case 2, no new page), then Sichuan-Chongqing (case 3), then the one-pipeline networks, which only gain the lead line.

## Out of scope here

Non-China networks (on hold), oil, wiki categories, deleting the 15 leftover redirects from the 2026-11-08 moves (admin), updating the 132 Wiki link cells to the moved titles (separate authorized write).
