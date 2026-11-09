# Plan: network pages with primary and secondary networks (China first)

Drafted 2026-11-08 with Baird. Supersedes the column decisions in `docs/plans/2026-11-06_wiki-tagging-backend.md` (that plan's audit invariants still hold; its "no new column" ruling does not). Background: `wiki/design_tagging_and_maps.md`. Registry: `wiki/data/networks.json`. Nothing on the wiki or the sheet is changed by this plan until each gate below is passed.

## Scope

China gas only. Networks outside China are on hold (Baird 2026-11-08): the registry does not list them, the generator's network mode refuses a network with no registry entry, and the non-China grouping values (owner groups, market zones, trunk labels) are not touched. Oil is out of scope.

## The three levels

| Level | Sheet field | Wiki surface |
|---|---|---|
| Network | `PrimaryNetwork` (one value per row, same on every row of a PipelineName) | A network page: rollups, a Pipelines table, a map of every segment, the segment table of its direct segments, Background with one subsection per pipeline |
| Pipeline | `PipelineName` | A pipeline page as today (`wiki/scripts/generate_pages.py`), plus an "It is classified as part of the [[X]]." line in the lead and the network's name in the infobox-style Pipelines table |
| Segment | `SegmentName` (anchor `row-<PID>`) | A row on its pipeline's page, never a page of its own |

Researchers' `PipelineName`s are never renamed to fit a page (gem_schema, 2026-11-07). The network organizes; the names stay.

## Primary and secondary networks

- A pipeline has at most one primary network and any number of secondary networks. Both behave like tags.
- The primary is where the pipeline is counted: the network page's length total, status mix and segment count include it, and its segments draw at full weight on the network map.
- A secondary is navigation only: the pipeline is listed under "Connected pipelines" on that network's page and drawn lighter on its map (opacity 0.45, weight 2), and it is never in that network's totals. The pipeline page says "Also connected to Y".
- Invariant: every row of one PipelineName carries the same primary. The audit flags a split (P7668 was one until it moved, 2026-11-08).
- A one-row pipeline that is not a network of anything still has a primary when it belongs to a grid (the Beijing case: one row, one network, no network page).

## Sheet columns

Added to the Gas tab by Baird on 2026-11-08, ahead of the pilot: `PrimaryNetwork` (col A, renamed from `PipelineNetworkGrouping`), `PrimaryNetworkWiki` (col B, new) and `SecondaryNetworks` (col C, renamed from `PipelineNetworkGroupingAlt`). The oil tab keeps the old names.

- `PrimaryNetwork`: English, one value, the network's `NetworkName` on the networks tab. The China values were swapped from Chinese to English the same day (986 rows, backup `notes/sheet-backup-2026-11-08-gas-primary-network-english.csv`); the Chinese name lives only on the networks tab.
- `PrimaryNetworkWiki`: the network page URL, filled for China; blank where the network page does not exist yet (Sichuan-Chongqing) and for every network outside China.
- `SecondaryNetworks`: one or more `NetworkName`s. Multi-select chips write them separated by `, ` (comma and space), so that is the separator; no network name may contain a comma.
- Both network columns carry a strict dropdown from `'Gas pipeline networks'!B3:B` (2026-11-08); `SecondaryNetworks` allows multiple selections, which is switched on in the Sheets UI because the API has no field for it. A network is added to the tab before a row can use it.
- Readers that addressed the old name now read `PrimaryNetwork` first and fall back to `PipelineNetworkGrouping` (oil): `scripts/match.py`, `build_qc_workbook.py`, `build_leg3_briefs.py`, `build_ref_worklist.py` (its `--exclude-network-regex` is tried against both the English name and the registry's local name, so the Chinese China idiom still works), `ref_pairs.py`, and `gem-db-ops/gem_colmap.py` (`network_grouping` is per tab now). `SecondaryNetworks` is a list and is never read as one value. The public release summary sheets still name the old column; the next release needs a note.

**Networks tab (created 2026-11-08, Baird's request):** the backend's `Gas pipeline networks` tab (gid 132857322) holds one row per network, header in row 2, written from the registry: `NetworkID` (N0001.., stable key), `NetworkName` (English; the value the Gas tab's `PrimaryNetwork` and `SecondaryNetworks` carry), `NetworkNameLocalLanguage`, `Countries`, `NetworkType`, `Pipelines` (member PipelineNames, `;`), `PipelineCount`, `SegmentCount`, `LengthKnownKm`, `Wiki`, `WikiPageKind`, `Notes`, `Researcher`, `LastUpdated`. `SegmentCount` and `LengthKnownKm` are snapshot values from the creation date, not formulas; a refresh rewrites them from a fresh pull. The registry (`networks_tab` key) and the tab are kept in step: edit the registry, rewrite the tab, never hand-edit one without the other. Backup: `notes/sheet-backup-2026-11-08-gas-pipeline-networks-tab.csv`. The 57 networks outside China (N0073-N0129: the other PrimaryNetwork values as written, plus four used only as secondaries) were added the same day so the dropdowns cover every value in use; they sit in the registry's `networks_outside_china` list, unreviewed, with wiki work on hold, and the generator never reads that list. Backup: `notes/sheet-backup-2026-11-08-gas-networks-outside-china-and-dropdowns.csv`.

## Network names (2026-11-08: applied to the sheet; network pages not built yet)

Baird 2026-11-08: the network label must read differently from the pipeline that shares its name, and every Chinese pipeline should belong to a network that has a page. PipelineNames stay as they are; only the network side changes.

Why: on the live sheet (2026-11-08, 985 China gas rows) every row but one has a `PrimaryNetwork`, but 42 of the 72 networks hold a single pipeline (West-East Gas Pipeline 1, Sino-Myanmar, Zhongwei-Guiyang), so "network" and "pipeline" were the same thing and those networks could only ever be redirects. `SecondaryNetworks` was empty on every row.

The scheme follows the 2024 reorganization doc ("Chinese gas pipelines - 2024 reorganization", Google Doc `1GONZpFFWlEExd2G2CbUaiPZW-3DZkB5PBpi5BisMco4`), which sorted every Chinese pipeline into I (international), P (provincial network: within one province or autonomous region), N (national) and T (trans-province), with a `ChineseNetworkPrimary` label deciding its wiki page. The doc's columns (`ChinesePipelineType`, `ChineseNetworkPrimary`, `ChineseNetworkSecondary`, `ChineseClassificationNotes`) are no longer on the Gas tab; `PrimaryNetwork` and `SecondaryNetworks` replaced the network two. About 33 networks replace the 72:

| Type | Network | Holds today | Rows |
|---|---|---|---|
| P | `<Place> Provincial Gas Network` (provinces and autonomous regions; "Provincial" because Guangxi, Xinjiang, Inner Mongolia and Ningxia are autonomous regions) | the 26 provincial networks, Sichuan-Chongqing becoming Sichuan's | about 700 |
| P | `<Place> Municipal Gas Network` (Beijing, Chongqing, Shanghai, Tianjin) | the 4 municipal networks | 55 |
| N | China National Gas Pipelines | the 23 trunk-line networks (West-East 1-5, Shaan-Jing, Sichuan-Shanghai and its parallel, China-Russia East, China-Russia Far East, the Tibet line and the rest) | 171 |
| I | China International Gas Pipelines | the 10 import and 1 export networks, the Guangdong-Macao link, and P6787 Sarybulak-Zimunay (the one row with no network) | about 29 |
| T | China Interprovincial Gas Pipelines ("interprovincial": one word, the standard English form; the 2024 doc's "trans-province" names the same type) | the connecting-line and coal-to-gas networks except Guangdong-Macao | about 26 |

- Tibet gets no provincial network: its one row (P5100, cancelled) runs from Qinghai into Tibet, so it is N. A Tibet network is added the day an in-region line is tracked.
- `PrimaryNetworkLocalLanguage` keeps the Chinese name for the provincial networks; the three national groupings get one each (to draft).
- Sichuan-Chongqing becomes Sichuan Provincial Gas Network (Baird 2026-11-08: Sichuan had no network of its own). 27 of its 28 rows run within Sichuan. The 28th, P4568 (CNPC Sichuan & Chongqing Gas Pipeline Network, Sichuan to Chongqing), stays in it with Chongqing Municipal Gas Network as a secondary. Chongqing already has its own network (38 rows), which is unchanged apart from the rename.

Secondaries: every N, I and T pipeline takes as `SecondaryNetworks` the provincial and municipal networks of the divisions its route crosses, derived from route geometry (mechanical, not research). A provincial page then lists its own pipelines and the national lines passing through, and its map shows everything in the division.

Provincial renames:

| ID | Current | Proposed | Pipelines | Rows |
|---|---|---|---|---|
| N0001 | Anhui Gas Pipeline Network | Anhui Provincial Gas Network | 1 | 52 |
| N0002 | Beijing Gas Pipeline Network | Beijing Municipal Gas Network | 1 | 1 |
| N0011 | Chongqing Gas Pipeline Network | Chongqing Municipal Gas Network | 1 | 38 |
| N0015 | Fujian Gas Pipeline Network | Fujian Provincial Gas Network | 1 | 10 |
| N0016 | Gansu Gas Pipeline Network | Gansu Provincial Gas Network | 1 | 10 |
| N0017 | Guangdong Gas Pipeline Network | Guangdong Provincial Gas Network | 6 | 44 |
| N0019 | Guangxi Gas Pipeline Network | Guangxi Provincial Gas Network | 3 | 43 |
| N0020 | Guizhou Gas Pipeline Network | Guizhou Provincial Gas Network | 1 | 48 |
| N0021 | Hainan Gas Pipeline Network | Hainan Provincial Gas Network | 1 | 6 |
| N0023 | Hebei Gas Pipeline Network | Hebei Provincial Gas Network | 1 | 27 |
| N0025 | Heilongjiang Natural Gas Pipeline Network | Heilongjiang Provincial Gas Network | 1 | 9 |
| N0026 | Henan Gas Pipeline Network | Henan Provincial Gas Network | 1 | 23 |
| N0028 | Hubei Gas Pipeline Network | Hubei Provincial Gas Network | 1 | 18 |
| N0029 | Hunan Gas Pipeline Network | Hunan Provincial Gas Network | 1 | 30 |
| N0030 | Inner Mongolia Gas Pipeline Network | Inner Mongolia Provincial Gas Network | 1 | 43 |
| N0031 | Jiangsu Coastal Gas Pipeline | Jiangsu Provincial Gas Network | 1 | 22 |
| N0033 | Jiangxi Natural Gas Pipeline Network | Jiangxi Provincial Gas Network | 1 | 28 |
| N0034 | Jilin Gas Pipeline Network | Jilin Provincial Gas Network | 1 | 14 |
| N0035 | Liaoning Gas Pipeline Network | Liaoning Provincial Gas Network | 1 | 19 |
| N0037 | Ningxia Gas Pipeline Network | Ningxia Provincial Gas Network | 1 | 6 |
| N0042 | Qinghai Gas Pipeline Network | Qinghai Provincial Gas Network | 1 | 8 |
| N0047 | Shaanxi Gas Pipeline Network | Shaanxi Provincial Gas Network | 1 | 23 |
| N0048 | Shandong Gas Pipeline Network | Shandong Provincial Gas Network | 1 | 36 |
| N0049 | Shanghai Gas Pipeline Network | Shanghai Municipal Gas Network | 1 | 8 |
| N0050 | Shanxi Gas Pipeline Network | Shanxi Provincial Gas Network | 1 | 66 |
| N0052 | Sichuan-Chongqing Gas Pipeline Network | Sichuan Provincial Gas Network | 2 | 28 |
| N0057 | Tianjin Gas Pipeline Network | Tianjin Municipal Gas Network | 1 | 8 |
| N0066 | Xinjiang Gas Pipeline Network | Xinjiang Provincial Gas Network | 2 | 29 |
| N0069 | Yunnan Gas Pipeline Network | Yunnan Provincial Gas Network | 1 | 24 |
| N0070 | Zhejiang Natural Gas Pipeline Network | Zhejiang Provincial Gas Network | 1 | 38 |

None of the proposed titles exists on gem.wiki yet. Jiangsu Coastal Gas Pipeline is the one network whose current name is not a "Gas Pipeline Network" name; it becomes Jiangsu Provincial Gas Network like the rest.

Pages after the change:

- Every network gets its own page (case 3 in "Network page rules"; case 2 goes away), holding the Pipelines table (primary members, then pipelines passing through as secondaries), Connected pipelines, the network map and network-wide Background. No redirects.
- A pipeline that shared the old network name (Guangxi Gas Pipeline Network) keeps its page as an ordinary pipeline page with its own segments, and its lead says "It is classified as part of the [[Guangxi Provincial Gas Network]]." In 24 divisions all rows share one PipelineName (Shanxi's 66 rows are all Shanxi Gas Pipeline Network), so the network page and the pipeline page overlap; the network page carries the pass-through lines and the map, the pipeline page the segment detail.
- The trunk lines' own pages (West-East Gas Pipeline 1 and the rest) are unchanged; their leads say which grouping they are in.

Apply steps:

1. Done 2026-11-08. Registry: `networks` holds the 33; a renamed network keeps its NetworkID with `former_name`; the three groupings are N0130-N0132 with `former_networks`; the 42 absorbed networks are in `networks_retired` with `merged_into`.
2. Done 2026-11-08. Networks tab: rewritten from the registry, 33 China rows then the 57 outside China (90 rows, A3:N92; rows 93-131 cleared). The groupings' local-language names are blank until drafted.
3. Done 2026-11-08. Gas tab: `PrimaryNetwork` on 986 rows, `SecondaryNetworks` on 282, `LastUpdated` stamped on all 986 (`Researcher` left as it was, as in the first `PrimaryNetwork` write: classification, not research). Crossings counted from the routes repo at 10 km or 10% of the route; 28 rows with no route used their start and end provinces. Baird kept the five provincial rows whose route lies in a neighboring division (P5983, P4994, P4678, P5053, P5096) in their own network, with the crossed division as a secondary. P5100 (cancelled, Qinghai to Tibet) is in China National Gas Pipelines with Qinghai as a secondary; Tibet has no network. `PrimaryNetworkWiki` is unchanged until the network pages exist (step 5). Backups: `notes/sheet-backup-2026-11-08-china-network-scheme-gas.csv` and `-networks-tab.csv`.
4. Wiki: create Guangxi Provincial Gas Network from the network parts of the current page and return Guangxi Gas Pipeline Network to a pipeline page, then the other networks as each is reached.
5. `PrimaryNetworkWiki` points at each network's page.

## Network page rules

Which page a network gets, from the registry's `page_case`:

1. The network has one PipelineName: no extra page. The pipeline page is the network page and its lead names the network (66 of 72 Chinese networks today).
2. Several PipelineNames and one of them equals the network's English name: that page becomes the network page. Its own rows are the direct segments; the other names are listed in a Pipelines table and link to their own pages (Guangdong, Guangxi, Xinjiang, Sebei-Xining-Lanzhou, and West-East Gas Pipeline 2 until P7668 moves).
3. Several PipelineNames and none matches: a new page at the registry's English name (today only 川渝输气管网, proposed as Sichuan-Chongqing Gas Pipeline Network; Baird decides the name).

**Network page lead (Baird 2026-11-08, shortened the same day):** "<Network> (<local name>) groups the gas pipelines in <place>, China. It is a [[Chinese Gas Pipeline Networks|Chinese pipeline grouping by Global Energy Monitor (GEM)]], not an official Chinese network." (GEM spelled out, Baird 2026-11-09.) The three groupings say what they hold instead of a place (`GROUPING_SCOPE` in `network_pages.py`). [[Chinese Gas Pipeline Networks]] (built by `wiki/scripts/china_networks_page.py`, saved 2026-11-08) explains the five kinds of network and lists all 33 with counts; rerun it after each network page is built so its table links the page. A member pipeline's page that has its own page (Guangxi LNG Terminal Transport Pipeline) says "It is classified as part of the [[<Network>]]." in its lead (Baird 2026-11-08: "classified as part of", never a bare "part of", since the network is an organizing label rather than an official system), and the network page links to it from its Pipelines table rather than repeating its segments.

Sections of a network page, in order (Baird 2026-11-08, revised): lead; Location (map count line and a map of the network's own segments only, no connected pipelines, no province sentence); Pipelines (table: pipeline, local name, segments, length, status mix, link; no Total row); Articles and resources. No Background, no References, no Connected pipelines section, no segment table. A network page holds no background: that prose lives on the member pipeline pages (the Guangxi network text moved to Guangxi Gas Pipeline Network 2026-11-08). The overview page's Networks table has no local-name column, since the registry's names are mechanical. The lead's "also known as" list is built from the network's own rows only, never from a segment's local name.

Folding standalone segment pages: a page whose title is a SegmentName is folded onto its pipeline's page by default. Its Background prose moves onto the pipeline page under the segment's subheader, or into the segment background table when the page uses the tabbed layout. Its citations are carried through the generator's refs ledger (`audit_refs`: a lost citation blocks the save). The old title is left as a redirect; this account cannot delete pages.

Categories: on hold (Baird 2026-11-08). No network category, no per-network category, until the pilot has been looked at.

## Pilot: Guangxi

Network 广西输气管网 / Guangxi Gas Pipeline Network, case 2. 43 rows since P7668 moved over from West-East Gas Pipeline 2 (2026-11-08). Members: Guangxi Gas Pipeline Network (33 direct segments, 2,021 km), Guangxi LNG Terminal Transport Pipeline (8 segments, 1,620 km, Guangxi and Yunnan), Nanning-Pingxiang Gas Pipeline (2 segments, 225 km). Every row's Wiki cell already points at the Guangxi page, so the pilot changes the page's shape and not its row set. Secondary candidates for its Connected pipelines list are in the registry's `secondary_proposals`; Baird picks.

Steps:

1. Mockup (done 2026-11-08): hand-built wikitext of the pilot page from the live text, for approval. No save.
2. Generator `--network <English name>` mode in `generate_pages.py`: rows = every row whose registry-mapped primary is the network; direct segments = rows whose PipelineName equals the page name; the sections above. Pipeline pages gain the two lead lines. Preserved sections (COMMENT2 to COMMENT3) are carried as today.
3. Dry run to `wiki/out/samples/`, compare with the mockup, render through action=parse, check the refs ledger (nothing lost).
4. Save through `scripts/wiki_save.py` from the work profile, one page, after Baird's OK. Then the member pipelines' pages, only when Baird wants one. Done for Guangxi LNG Terminal Transport Pipeline 2026-11-08: its page was built from its 8 rows (the generator selects by `Wiki`, which still points at the network page, so a wrapper passed the rows), the legacy Guangxi LNG Supporting Line page folded in and redirects to it, and the network page's Pipelines table links to it while its 8 segments left the network page's segment table (their 17 citations moved with them). The map still draws them. The LNG-specific Background paragraph and its 12 sources then moved from the network page to the LNG page, and the network page's subsection for the pipeline became a short explainer of what that page holds. Nanning-Pingxiang Gas Pipeline got its own page the same way (new page, 2 rows, P7668 still grouped under West-East Gas Pipeline 2 on the sheet). Rule from this: a member pipeline with its own page keeps all of its own Background and sources there; the network page keeps only network-wide history and one linked explainer per member pipeline. The explainer is one sentence saying what the pipeline is, then "Its page has more details." (Baird 2026-11-08); it does not list the segments or say what the page holds.

Generator gap found on that page: `intro()` falls back to the first row's `OtherLanguageAlternativePipelineNames` on a multi-segment page with no system row, so a segment's local name (柳州支线) lands in the lead as the pipeline's alias. Network mode must take the pipeline's local name from `OtherLanguagePrimaryPipelineName` (the majority value) and skip segment aliases.
5. Audit: `python wiki/scripts/network_audit.py` (to write) checks the invariants: one primary per PipelineName, every primary in the registry, every registry page exists or is a PipelineName, no secondary equal to the primary, no grouping value equal to the row's own PipelineName.

## Gates (Baird decides)

1. The mockup's shape (this turn).
2. Adding the sheet columns: done by Baird 2026-11-08 (see Sheet columns).
3. P7668's move to Guangxi Gas Pipeline Network (done 2026-11-08: `PrimaryNetwork` and `PrimaryNetworkWiki`, backup `notes/sheet-backup-2026-11-08-gas-p7668-primary-network.csv`), and the other grouping fixes already on the list (P4553, P3894, P8037). Each is a sheet write under the hard requirements: FORMULA pre-read, backup CSV in `notes/`, RAW cell-scoped write, re-read, `Researcher` = CB and `LastUpdated` stamped.
4. The name for 川渝输气管网 and whether the four Central Asia–China line groupings merge into one network.
5. Which secondary proposals become `SecondaryNetworks` values for the Guangxi pilot.
6. Extending past Guangxi: Guangdong and Xinjiang next (case 2, no new page), then Sichuan-Chongqing (case 3), then the one-pipeline networks, which only gain the lead line.

## Out of scope here

Non-China networks (on hold), oil, wiki categories, deleting the 15 leftover redirects from the 2026-11-08 moves (admin), updating the 132 Wiki link cells to the moved titles (separate authorized write).
