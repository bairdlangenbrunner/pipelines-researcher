# Tagging, backend organization and maps for generated pipeline pages

Draft 2026-11-06. A working note for the three questions Baird raised when the template draft went into the Google Doc: how to organize the backend so a row has one primary page and any number of secondary network or relational links, how the template fits the way pipeline pages are organized today, and how a single map per page can carry every route. Nothing here is decided. The decisions it needs are listed at the end and mirrored in `README.md`.

## 1. What the backend holds today

Four columns describe how rows relate to pages and to each other, and they overlap.

| Column | Tab | Filled | What it means in practice |
|---|---|---|---|
| `PipelineName` | oil, gas | all rows | The pipeline the row belongs to. On a multi-row page it is usually the page name, but not always. |
| `SegmentName` | oil, gas | some rows | The row's label inside its pipeline. |
| `Wiki` | oil, gas | most rows | The page the row appears on. 487 rows have none. The page name differs from `PipelineName` on 257 rows (34 of them because the page is named after the segment). |
| `PipelineNetworkGrouping` | oil, gas | oil 421 rows, 39 values; gas 1,260 rows, 124 values | A network the row belongs to. Oil values are English page-like names (Shandong Oil Pipeline Network). Gas values are mostly Chinese (山东输气管网). |
| `AltPipelineNetworkGrouping` (oil), `PipelineNetworkGroupingAlt` (gas) | oil, gas | oil 0; gas 18 rows (MGS I/II, Vertical Gas Corridor) | A second network. Named differently on the two tabs. |
| `AlternateRouteProjectIDs` | oil | 2 rows | Other ProjectIDs that are competing route variants of this one. |
| `PipelineNetworkContainer` | operators/owners | 1,675 rows, 163 values | The ownership team's system label (Bakken Pipeline System, Express-Platte Pipeline System). A fourth grouping notion, kept on a different tab. |

China shows how the overlap plays out.

- Gas, 985 rows, 120 pages, 82 `PipelineName` values, 72 groupings. 14 `PipelineName` values are spread over several pages: the 66 rows named `Shandong Gas Pipeline Network` sit on the network page and on segment pages such as `Laishan-Penglai-Longkou Gas Pipeline`; `West-East Gas Pipeline 2` rows sit on the trunk page and on branch pages. 6 pages hold several `PipelineName` values, some of which are only spelling variants (`Hebei Gas Pipeline Network` and `Hebei Gas pipeline Network`). Grouping values are Chinese, so they cannot be page names as they stand.
- Oil, 362 rows, 143 pages, 233 names, 23 groupings. Here `PipelineNetworkGrouping` is already an English network name, but there is no page for most networks: `Shandong Oil Pipeline Network` covers 118 rows on 54 pages with 66 names.
- No oil row and 18 gas rows have `LengthKnown = 0`. All 18 are expansion projects (Rover Phase 2, Columbia Central Virginia Connector, ANR Wisconsin Access) that already sit on their parent pipeline's page, and none has a route.

So today a row's page is set by the `Wiki` URL, its pipeline by `PipelineName`, and its network by a free-text grouping, and the three can disagree. The generator needs one rule.

## 2. Proposed model: one primary page, any number of secondary tags

Two tags per row, both on the tracker tab, both holding page names rather than URLs.

**Primary tag: the page the row's details live on.** The rule is that `PipelineName` is the page name, full stop, and the `Wiki` URL is derived from it (`https://www.gem.wiki/` plus the name with spaces as underscores). A row appears in exactly one place with its tables and references. `SegmentName` labels the row on that page and gives the row its anchor, so a row can still be linked as `Page#Segment`. The 257 rows where page and name disagree are the step 3 renames list, and each is settled one of two ways: the page moves to the `PipelineName`, or the `PipelineName` changes to the page (which is what the 34 segment-named pages want, with the old name moving to `SegmentName` or to the secondary tag).

**Secondary tags: the networks and related pipelines the row also belongs to.** One column, `NetworkTags`, holding zero or more page names separated by semicolons, the same convention `OtherEnglishNames` uses. Each value is the primary name of another page. Two uses, one mechanism:

- A national or provincial network: a Shandong segment on its own page carries `NetworkTags = Shandong Gas Pipeline Network`. The network page is generated from every row that tags it.
- A relational link to a different pipeline: a branch on its own page carries `NetworkTags = West-East Gas Pipeline 2`, and the trunk page lists it under related pipelines. A row can carry both a network and a trunk, so `NetworkTags = Shandong Gas Pipeline Network; West-East Gas Pipeline 2` is valid.

**What a network page is.** A page with no rows of its own: an introduction, one map of every member route, a members table (segment, status, length, start year, owner, link to the member page), and references. No pipeline-details tables, because every detail lives on exactly one member page. This is the main change from the current China layout, where the network page holds a `===Segment===` subsection with every detail for all 66 rows. The alternative, keeping the details on the network page, means a row appears twice (its own page and the network page) and the generator has to decide which copy is canonical. Recommendation: details on the primary page only, network pages are rosters plus a map. For a network whose segments have no page of their own (Shanxi, 66 rows all named `Shanxi Natural Gas Pipeline Network`), nothing changes: the network page is their primary page and holds the tables, one row per segment, as the draft template already does for multi-row pages.

**The existing columns under this model.**

- `PipelineNetworkGrouping` becomes the first `NetworkTags` value once its values are page names. Oil values mostly are already. Gas values need the Chinese network name translated to the English page name (山东输气管网 becomes `Shandong Gas Pipeline Network`), and the Chinese name goes to that network page's `OtherLanguageAlternativePipelineNames`.
- `AltPipelineNetworkGrouping` and `PipelineNetworkGroupingAlt` fold into `NetworkTags` as a second value, and the two differently named columns go away.
- `AlternateRouteProjectIDs` stays separate. It means competing proposals for the same corridor, not membership, and renders as an "Alternative routes" line on both pages.
- `PipelineNetworkContainer` on the operators/owners tab is the ownership team's label and is left alone. Whether its 163 systems should also become network tags is a decision for later; many of them (Express-Platte, Bakken) would make good relational pages.

**How a page type is decided.** A page name that is some row's `PipelineName` is a pipeline page. A page name that appears only in `NetworkTags` is a network page. A name that appears in both is a pipeline page with a related-pipelines section added. No new column is needed to mark the type.

## 3. Cleaning up China first

The gas tab is the messy one and the one that needs this first. The work is mechanical enough to script a proposal and review it as a workbook before anything touches the sheet.

1. Translate each Chinese `PipelineNetworkGrouping` to its English network page name. 72 values; most already have a network page whose name is the obvious translation.
2. For each row whose `Wiki` page is not its `PipelineName` (the 14 names spread over several pages): set `PipelineName` to the page name, move the old name to `NetworkTags`, and keep `SegmentName` as it is. Shandong's 66 rows become rows on their segment pages with `NetworkTags = Shandong Gas Pipeline Network`, except the ones whose page is the network page itself, which stay.
3. Merge spelling variants on one page (`Hebei Gas pipeline Network`) into the page name.
4. Fill `Wiki` for the 30 gas and 100 oil China rows without a page from `PipelineName`, which creates those pages at generation time.
5. Oil: `PipelineNetworkGrouping` is already English, so it only moves into `NetworkTags`, and 23 network pages get generated.

A script in `wiki/scripts/` (not written yet) would read the snapshot, propose these edits row by row, and write a review workbook with the current and proposed `PipelineName`, `SegmentName`, `Wiki`, and `NetworkTags`. Applying the accepted rows goes through the usual authorized sheet write, never automatically.

## 4. The template against the current page organization

Current pipeline pages come in two layouts. Hand-written single-pipeline pages (most of the tracker) have Background, Project details as a bullet list, Ownership, a map, and references. Chinese network pages, written by the earlier generation run, have `==Network location==` (one map), `==Background==`, `==Network details==` with one `===Segment===` subsection per row, and `==Articles and resources==`.

The draft in the Google Doc keeps the table layout the other trackers use and reconciles the two like this.

- Pipeline page: Introduction, Location (map plus a route table when there are several rows), Project details (pipeline details, timeline, cost, one row per segment), Ownership, preserved hand-written sections, Articles and Resources, categories. This replaces the bullet list on hand-written pages and the per-segment subsections on network pages.
- Network page: Introduction, Location (one map of all members), Network members (one table), Related pipelines when any row tags it as a trunk, Articles and Resources. Generated from the tags, so it never goes stale as rows move.
- Hand-written Background text survives on both page types through the preserved-section markers (`COMMENT2` and `COMMENT3`), the same way the other trackers keep their Background sections. The old `===Segment===` subsections on network pages do not survive; their content is the tracker data, which the tables now show.
- Row anchors: every row on a multi-row page gets an anchor named after its segment, so a `Wiki` URL can carry `#Segment` and a network page's members table can link straight to the row.

## 5. One map per page

The ask is one map per page with every route on it, the segment name on hover, or colors with a small legend. What the wiki can do today, checked against the Maps 13.1.2 source (`resources/GoogleMaps/jquery.googlemap.js`, `addLine`):

- One `{{#display_map: |lines=...}}` takes any number of lines. Each line is `lat, lon:lat, lon:...~title~text~strokeColor~strokeOpacity~strokeWeight`, lines separated by semicolons. The Chinese network pages already use multi-line maps this way (without the `~` fields).
- The title and text open in a popup on click, not on hover. The Google service attaches a click listener to each polyline and nothing for mouseover. Hover would need a change to the extension, so the realistic design is click for the name and color for the legend.
- Stroke color, opacity and weight are per line, so a legend is possible: a small wikitext table beside the map with a colored cell per entry. Maps has no built-in legend.
- `geojson=` is an alternative input (a wiki page or file holding GeoJSON, several allowed since Maps 14.1, which gem.wiki does not have yet). It would keep the wikitext short on pages like Shanxi (66 routes) and could carry the name in feature properties, but it needs a page per route uploaded to the wiki and I have not tested how its popups behave. Worth one test on the test wiki before choosing.

Recommended design for the generator:

- Color by `Status`, with a fixed palette (operating, construction, proposed, shelved or cancelled, retired or idled or mothballed), and the legend showing only the statuses present. This scales from a two-segment page to a 66-row network page and reads the same on every page. The click popup shows the segment name, status, and a link to the row's anchor or member page.
- On a pipeline page with few routed rows (up to about eight) the route table doubles as the legend: a colored swatch column in the route table, one color per segment, and the status palette only above that count. This is the "colored differently with a small legend" option and it is a page-level switch in the generator, not a data change.
- Rows with no route draw nothing and say so in the route table ("route not mapped"). Rows with `LengthKnown = 0` are expansions with no new pipe: no line, and the route table says "no new pipe, expansion of the existing route". All 18 such rows already share a page with the pipe they expand, so the map still shows the physical route.
- Geometry comes from the routes repo `<PID>.geojson`, which the generator converts to the `lat, lon` strings, simplifying long routes so a 66-route page stays well under the wikitext size limit. The GEMwiki helper `make_map_w_wkt_geometry` already does the WKT half of this for other trackers.
- Center and zoom are computed from the union of all drawn routes, so a network page frames the whole province and a short lateral frames itself.

## 6. Decisions this needs

1. Page type rule: details only on the primary page, network pages as roster plus map (recommended), or keep per-segment details on network pages too.
2. Column changes on the tracker: add `NetworkTags`; retire `AltPipelineNetworkGrouping` and `PipelineNetworkGroupingAlt`; make `Wiki` derived from `PipelineName` or keep it hand-set.
3. Whether `PipelineNetworkContainer` systems on the owners tab become network tags.
4. China gas translation of the 72 Chinese groupings to English page names, and who checks it.
5. Map coloring: by status with a legend (recommended), by segment on small pages, or both as a page-level switch.
6. Whether to test `geojson=` input on the test wiki before building the lines generator.
7. Row anchors: `SegmentName` as the anchor, or `ProjectID`.
