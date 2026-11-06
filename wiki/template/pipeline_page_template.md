# Template for GEM wiki page layout: pipelines (GOIT and GGIT)

Draft 2026-11-06, for the data team's "Templates for GEM Wiki Page Layout" folder. The section layout follows the LNG terminals and GOGPT templates. Pipelines are not in GEM's database. The input is the two tracker tabs plus the "Pipeline operators/owners" tab, all joined on `ProjectID`.

## How to read this template

- `«ColumnName»` is a value from the tracker file, using its exact column header. In the Google Doc these are highlighted.
- `[ref: «Column [ref]»]` means the cell gets citations from that ref column. A ref cell can hold several URLs separated by new lines or semicolons. Each URL is one citation, and a URL already cited on the page is reused as a named ref.
- Lines starting with **Logic:** are conditional rules. In the Google Doc they become comments.
- Everything else is fixed text.
- Inputs: the oil tab ("Oil/NGL", 107 columns) and the gas tab ("Gas", 134 columns) have their header on row 3. The operators/owners tab has its header on row 2. Skip any row whose `ProjectID` does not start with `P` (these are buffer rows) and any row with `Status = N/A` (an exclusion marker, not a status).

## Page grouping

**Logic:** One wiki page per distinct `«Wiki»` URL. All tracker rows that share a `«Wiki»` URL are the **segments** of that page, like LNG's units. Rows are ordered by `«StartYear1»`, then `«ProjectID»`. A row with a blank `«Wiki»` gets a new page named `«PipelineName»`. Two pages appear on both the oil and gas tabs; those combine their rows and show both navbars.

**Logic:** The page name is the page in the `«Wiki»` URL, decoded (`%E2%80%93` becomes `–`, underscores become spaces), not `«PipelineName»`. This keeps every existing page and its history where it is. Whether to move pages so they match `«PipelineName»` is open decision 1.

**Logic:** The segment label in every table is `«SegmentName»` when it is filled. Otherwise it is `«PipelineName»`. If two segments end up with the same label, add `(«ProjectID»)`.

Counts from the 2026-11-06 snapshot: oil has 2,093 rows on 1,250 pages, with 305 rows that have no page yet. Gas has 4,621 rows on 2,630 pages, with 182 rows that have no page yet. About 80% of pages have a single segment.

---

## Page markup

```
«page name»

<!--- COMMENT 1 (generated-page warning, standard GEMwiki text) -->
{{Navbar-Global Oil Infrastructure Tracker}}      (oil tab)
{{Navbar-Global Gas Infrastructure Tracker}}      (gas tab)
```

### Introduction (generated)

**Single segment:**

> '''«page name»''', also known as '''«OtherEnglishNames»''' (local name: '''«OtherLanguagePrimaryPipelineName»'''), is {a/an} {status phrase} {fuel phrase} pipeline {location phrase}.[ref: «Status [ref]»]

**Multiple segments:**

> '''«page name»''', also known as ..., is a {fuel phrase} pipeline {location phrase} with segments that are {comma list of distinct status phrases}.

**Logic:**
- **Also known as:** List `«OtherEnglishNames»`, then `«OtherLanguageAlternativePipelineNames»`, split on commas and semicolons, each in bold. Leave out any name equal to the page name. Leave the clause out when the list is empty. The local name is `«OtherLanguagePrimaryPipelineName»` and is left out when blank.
- **Status phrase:** taken from `«Status»`. `construction` becomes "under construction". `operating`, `proposed`, `shelved`, `cancelled`, `retired`, `mothballed` and `idled` stay as they are. Use "an" before a vowel sound.
- **Fuel phrase:** On the gas tab, `gas` becomes "gas" and `gas and hydrogen` becomes "gas and hydrogen". On the oil tab, `oil` becomes "crude oil", `NGL` becomes "natural gas liquids (NGL)", `oil products (only)` becomes "oil products", `LPG` becomes "liquefied petroleum gas (LPG)", `CO2` becomes "carbon dioxide", and `condensate` and `naphtha (only)` become "condensate" and "naphtha". A combined value such as `oil, NGL` becomes "crude oil and NGL". Define an abbreviation only the first time it appears.
- **Location phrase:** If every segment's `«CountriesOrAreas»` is one country, use "in «StartState/Province», «Country»". Drop the province when the start and end provinces differ, or when it is blank. If there are several countries, use "running from «StartCountryOrArea» to «EndCountryOrArea»". If the countries in between are known, add "through «middle countries»".
- **Dormancy sentence:** For a segment with `«ShelvedCancelledType» = inferred`, add this after the intro: "No development on «segment label» has been reported since «year of the newest Status ref», and it is considered {shelved/cancelled}." This replaces the 2021 template's "As of MONTH YEAR, no development ... for over 2[4] years" wording. A sentence that stays true needs no "as of" date to go stale.

### ==Location== (generated)

> The pipeline {runs / is proposed to run / was proposed to run / ran} from «StartLocation», «StartState/Province», «StartCountryOrArea» to «EndLocation», «EndState/Province», «EndCountryOrArea».[ref: «StartLocation [ref]», «EndLocation [ref]» (oil) / «Location [ref]» (gas)]

**Logic:**
- **Verb:** use "runs" for `operating`, `idled` and `mothballed`; "is proposed to run" for `proposed` and `construction`; "was proposed to run" for `shelved` and `cancelled`; "ran" for `retired`.
- **Place names:** blank parts are dropped, and repeated parts collapse ("Novorossiysk, Krasnodar Krai, Russia").
- **Single segment:** one sentence.
- **Multiple segments:** Table 1 instead of the sentence.
- **Ten or more segments (Baird 2026-11-06):** no Table 1 here. The overview sentence points to the segment table under Project Details, which replaces Tables 1 to 5 with one tabbed table (see "Pages with ten or more segments" below).

**Table 1: Route details** (multiple segments only)

| Segment | Start location | End location | Countries | Length |
|---|---|---|---|---|
| segment label | «StartLocation», «StartState/Province», «StartCountryOrArea» [ref] | «EndLocation», ... [ref] | «CountriesOrAreas» | «LengthKnown» «LengthKnownUnits» [ref: «Length [ref]»] |

**Map** (generated):

> The map below shows {the exact route / the approximate route / a sketch of the route} of the pipeline.

> `{{#display_map: |lines=<route coordinates>~~~~«segment label» ...}}`

**Logic:**
- **Geometry:** It comes from the routes repo (`GlobalEnergyMonitor/GOIT-GGIT-pipeline-routes`, one `<ProjectID>.geojson` per segment). It is not in the tracker sheet, so the data team needs a way in. GEMwiki already has `make_map_w_wkt_geometry()`, so we would send WKT per ProjectID as an extra column or file (open decision 5). Thin each line to about 60 to 100 points so the page stays light.
- **Caption:** taken from `«RouteAccuracy»`. `very high (within meters)` and `high` give "the exact route". `medium` and `low` give "the approximate route". `very low (straight line/schematic)` gives "a sketch of the route".
- **No route:** If `«RouteType»` is not `Mapped route (at any accuracy)`, show no map and write "The route of this pipeline has not been mapped."

### ==Project Details== (generated)

**Table 2: Pipeline details**

| Segment | Status | Fuel | Capacity | Length | Diameter |
|---|---|---|---|---|---|
| segment label | «Status» [ref: «Status [ref]»] | «Fuel» [ref: «Fuel [ref]»] | «Capacity» «CapacityUnits» [ref: «Capacity [ref]»] | «LengthKnown» «LengthKnownUnits» [ref: «Length [ref]»] | «Diameter» «DiameterUnits» [ref: «Diameter [ref]»] |

Caption under the table: list each unit abbreviation used on the page, for example "bcm/y = billion cubic meters per year; MMcf/d = million cubic feet per day; bpd = barrels per day; mtpa = million tonnes per year".

**Logic:**
- **Original units, always:** Values appear exactly as the source states them. Never use the computed columns (`LengthKnownKm`, `LengthMergedKm`, `CapacityBcm/y`, `CapacityBOEd`, `DiameterInMm`). Numbers get thousands separators.
- **Diameter:** a diameter cell can hold several values ("500, 530, 1220"); show it as written.
- **Length:** if `«LengthKnown»` is `0`, show "0 (expansion with no new pipe)".
- **Gas pressure:** on the gas tab, add a "Pressure" column (`«Pressure» «PressureUnits»` [ref]) only when some segment has a value.
- **Empty columns:** a column with no value in any segment is left out (GEMwiki `exclude_empty_columns=True`).

**Table 3: Project timeline**

| Segment | Status | Proposal year | FID | Construction year | Start year | Inactive year |
|---|---|---|---|---|---|---|
| segment label | «Status» | «ProposalYear» [ref: «Proposal [ref]»] | «FIDYear» («FIDStatus») [ref: «FID [ref]»] | «ConstructionYear» [ref: «Construction [ref]»] | «StartYear1» [ref: «Start [ref]»] | {year} ({status}) [ref] |

Caption under the table: "FID = final investment decision, used by some developers to indicate a project will move forward".

**Logic:**
- **Start year:** For `proposed` and `construction`, the header note reads "planned". If `«Delayed» = yes`, add " (delayed)" after the start year, with the ref from `«Delay [ref]»`. Later phases (`«StartYear2»`, `«StartYear3»`) are added as "2027, 2029 (phase 2)".
- **Inactive year:** For `shelved`, use `«ShelvedYear»` [ref: «Shelved [ref]»]. For `cancelled`, use `«CancelledYear»` [ref: «Cancelled [ref]»]. For `retired`, `mothballed` and `idled`, use `«StopYear»` [ref: «Stop [ref]»]. Add "(inferred)" when `«ShelvedCancelledType» = inferred`. Leave the cell blank for any other status.
- **FID:** The FID column is left out when every segment's `«FIDStatus»` is blank (most oil rows).

**Table 4: Cost**

| Segment | Cost | Project-level cost (gas only) |
|---|---|---|
| segment label | «Cost» «CostUnits» (US$«CostUSD») [ref: «Cost [ref]»]; on the gas tab «SegmentCost» «SegmentCostUnits» [ref: «SegmentCost [ref]»] | «ProjectLevelCost» «ProjectLevelCostUnits» [ref: «ProjectLevelCost [ref]»] |

**Logic:**
- **Currency format:** Costs are stored as full numbers. Show them as "US$5.1 billion" or "EGP 300 million" and keep the original currency. Add the US dollar figure in brackets only when the currency is not USD.
- **Project-level cost:** It repeats on every segment of a project, so show it once, in the first row, like LNG's "Total terminal capacity".
- **No cost data:** If every cost cell is blank, replace the table with "====Cost==== No cost data available.", the same way LNG handles financing.

### Pages with ten or more segments (Baird 2026-11-06)

A page with ten or more segments gets ONE sortable table under Project Details instead of Tables 1 to 5, with a row per segment and a tab strip above it: Route, Details, Timeline, Cost, Ownership, All columns. Each tab shows that table's columns (Route = Segment, Route shape, Start/end, Countries/areas, Length; Details = Segment, Status, Fuel, Capacity, Length, Diameter, Pressure; Timeline = Segment, Status, Proposal year, FID, Construction year, Start year, Inactive year; Cost; Ownership). Status and Length appear on two tabs. Column rules above still apply: a column empty in every row is left out, and a tab with no columns left is not offered. There is no Ownership section on such a page; the old heading anchors (`Table_1:_Route_details` ... `Ownership`) stay as empty spans so existing links land on the table. The tabs are CSS only (`:target` on empty anchor divs, no JavaScript); the stylesheet lives on `Template:Segment table/styles.css` (content model sanitized-css, loaded with `<templatestyles>`), and `wiki/scripts/generate_pages.py --push-styles` keeps it equal to the text in the script. Without the stylesheet every column shows. First page: Transcontinental Gas Pipeline (32 segments, 2026-11-06). Threshold `SEG_TABLE_MIN = 10` in the script.

### ==Ownership== (generated)

**Table 5: Ownership**

| Segment | Owner | Operator |
|---|---|---|
| segment label | «Owner1» («Owner1%»); «Owner2» («Owner2%»); ... [ref: «Owner [ref]»] | «Operator» [ref: «Operator [ref]»] |

**Logic:**
- **Source tab:** Owner and operator come from the operators/owners tab, joined on `ProjectID`. Percentages are stored as fractions (0.75) and shown as "75%". A blank percentage shows the name only.
- **Fallback:** If the operators/owners tab has no row for the ProjectID, use the tracker tab's `«Owner»` cell as written.
- **Parent:** There is no Parent column. Parent companies belong to the ownership team, and the data team's ownership tree insert covers them (open decision 2). Put the "ownership tree" insert point right after this table, the way the other GEOT-covered trackers do.

### Preserved sections (human-written, never overwritten)

```
<!--- COMMENT 2 (standard GEMwiki text) -->
==Background==
...whatever is on the live page now: Background, Opposition, Expansion Projects, Financing, and so on...
<!--- COMMENT 3 (standard GEMwiki text) -->
```

**Logic:**
- **Copied as-is:** Every section of the live page whose heading is not a generated heading is copied as it stands (GEMwiki `get_existing_wiki_text`). Old generated-like headings such as "Project details", "Pipeline details" and "Location" are replaced, so they must be on the generated list in every spelling seen live: "Project details", "Project Details", "Pipeline details", "Location", "Articles and resources", "Articles and Resources", "Resources and articles".
- **Old Expansion Projects sections:** On older pages these hold bullet-list details for each segment, which duplicate Table 2. Treat them as human text for now, and flag them for a person to fold into Background (open decision 6).
- **New pages:** A new page with nothing to preserve gets an empty `==Background==` only if oil's `«Background»` column has text (open decision 3). Otherwise it gets no Background section.
- **Named refs:** A preserved section can reuse a named ref (`<ref name=":0" />`) whose definition sat in a generated section that is now replaced. That breaks the citation. The LNG run hit this. The generator should log every named ref used in preserved text but defined nowhere, so a person can fix those pages before upload.

### ==Articles and Resources== (generated)

```
==Articles and Resources==
===Additional data===
To access additional data, including an interactive map of {oil and NGL / gas} pipelines, a downloadable dataset, and summary data, please visit the [https://globalenergymonitor.org/projects/global-oil-infrastructure-tracker/ Global Oil Infrastructure Tracker] on the Global Energy Monitor website.
   (gas tab: [https://globalenergymonitor.org/projects/global-gas-infrastructure-tracker/ Global Gas Infrastructure Tracker])
===References===
<references />
```

### Categories (generated)

```
[[Category:Global Oil Infrastructure Tracker]]   or   [[Category:Global Gas Infrastructure Tracker]]
[[Category:Oil and NGL Pipelines]]               or   [[Category:Gas and Hydrogen Pipelines]]
[[Category:{Status} pipelines in «country»]]     one per country in «CountriesOrAreas», per distinct status
```

**Logic:**
- **Live categories:** The first two lines match what live pages carry now, judging from a sample of 50 pages taken 2026-11-06.
- **Status categories:** Live pages mix "Existing pipelines in X", "Existing oil pipelines in X", "Proposed pipelines in X" and "Operating pipelines in X" (open decision 4). The draft proposes `Operating`, `Proposed`, `Under construction`, `Shelved`, `Cancelled`, `Retired`, `Idled` and `Mothballed` + "pipelines in «country»". Old status categories that are not on the generated list stay on the page only if they sit inside a preserved section.
- **Table of contents:** Add `__NOTOC__` when the page has no preserved sections, as GEMwiki does for the other trackers.

---

## Open decisions for Baird (before this goes to the data team)

1. **Page names.** Keep each page at its current `«Wiki»` URL (the draft does this), or move pages to match `«PipelineName»`? The readiness report lists the mismatches. Most are dash or spacing differences (`-` vs `–`), and some are real renames. Real renames go to the data team as the step 3 list.
2. **Parent companies.** Leave the column out and rely on the ownership tree insert (the draft does this), or add a Parent column like LNG?
3. **Oil `Background` column.** Seed Background on new pages from it, or leave it out?
4. **Status categories.** Which scheme should the pages use?
5. **Route geometry.** Send WKT per ProjectID as an extra column in the tracker file, or as a separate file the generator joins?
6. **Old Expansion Projects sections.** Leave them as preserved text, or fold them into Background in a cleanup pass before the first generated upload?
7. **Gas `«PipelineType»`.** It is blank on 1,648 gas rows, so the draft keeps it out of the intro. It could be added later as "a gas transmission pipeline" once filled.
