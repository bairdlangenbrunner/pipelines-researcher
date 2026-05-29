# GOIT Pipeline Research Workflow — Deep Research Agentic Instructions

## Overview

This document defines a structured, multi-phase research workflow for updating country-level crude oil and NGL pipeline data in the Global Oil Infrastructure Tracker (GOIT), maintained by Global Energy Monitor (GEM). The workflow is designed to be run inside Claude chat, using web search and deep research tools, and producing Excel outputs that map directly to the GOIT spreadsheet column structure.

**Critical rule:** Never use GEM, gem.wiki, Global Energy Monitor, or globalenergymonitor.org as a source or citation unless Baird explicitly says to. The goal is to find what other sources exist independently.

---

## Inputs

Before starting research on a country, gather:

1. **CSV export of the GOIT sheet** — filtered to the target country and commodity (Oil, NGL, or both). The CSV has a 2-row header (rows 0–1 are metadata; row 2 is the column names). Read with `pd.read_csv(file, header=2)`.
2. **The data dictionary** — defines all ~112 columns and their expected values/formats.
3. **Country and commodity scope** — e.g., "USA, crude oil and NGL pipelines only" or "Nigeria, all oil/NGL."

---

## Phase 1: Data Inventory & Gap Analysis

**Goal:** Understand what's already tracked and where the gaps are.

### Steps:
1. Load the CSV with `header=2` and filter to the target country via `CountriesOrAreas`.
2. Filter to the specified fuel types (e.g., Oil, NGL).
3. Categorize pipelines by status: operating, proposed, construction, shelved, cancelled, idle, mothballed, retired.
4. For each pipeline (especially proposed/construction/shelved), identify missing values across key columns:
   - Status [ref], Owner, Parent
   - ProposalYear, Proposal [ref], ConstructionYear, Construction [ref]
   - StartYear1, Start [ref]
   - Capacity, CapacityUnits, Capacity [ref]
   - LengthKnown, LengthKnownUnits, Length [ref]
   - Diameter, DiameterUnits, Diameter [ref]
   - StartLocation, StartState/Province, StartCountryOrArea, StartLocation [ref]
   - EndLocation, EndState/Province, EndCountryOrArea, EndLocation [ref]
   - Cost, CostUnits, Cost [ref]
   - FIDStatus, FIDYear, FID [ref]
   - Opposition, Opposition [ref]
   - Background, Background [ref]
5. Print a structured gap analysis for each in-development pipeline.

---

## Phase 2: Deep Research — Status Updates & Data Enrichment

**Goal:** For each in-development pipeline (proposed, construction, shelved), search for the latest information to fill gaps and check for status changes.

### Research priorities (in order):
1. **Status changes** — Has the pipeline moved from proposed → construction, construction → operating, proposed → shelved/cancelled, etc.?
2. **Missing [ref] URLs** — Every data point must have a source URL in the corresponding [ref] column.
3. **Key data fields** — Capacity, length, diameter, cost, ownership, start/end locations, FID status, opposition.

### Source hierarchy (prefer in this order):
1. Company investor relations pages, SEC filings (10-K, 10-Q, 8-K), press releases
2. Regulatory filings (FERC, PHMSA, MARAD, state agencies like Texas RRC, Alaska DNR)
3. Industry publications (Oil & Gas Journal, Offshore Magazine, Pipeline & Gas Journal, S&P Global/Platts, Argus Media, Hart Energy)
4. Specialist analytics (East Daley Analytics, RBN Energy, Wood Mackenzie)
5. Wire services (Reuters, BusinessWire, PRNewswire, Bloomberg)
6. Government data (EIA petroleum data, BOEM, BLM)
7. Environmental/opposition groups (Earthjustice, Sierra Club, Earthworks — for opposition data)
8. Quality news outlets (for the target country)

### URL Verification Rules — CRITICAL

**Every URL in a [ref] column MUST be verified.** This means:
- The URL must resolve to a real page (not a 404, not a redirect to an unrelated page).
- The page must actually contain the specific data point being cited.
- Do NOT guess URL paths, query parameters, or page IDs.
- Do NOT fabricate URLs that look plausible but haven't been verified.
- If you find information but cannot locate the exact URL, write in ResearcherNotes: "Source: [Company] press release dated [date], titled '[title]' — URL not verified" so the researcher can look it up manually.
- After building the Excel file, spot-check a sample of URLs by fetching them to confirm they contain what's claimed.

### Expansion vs. New Construction Rule

For any pipeline entry that is a **capacity expansion** (pump station additions, DRA injection, terminal upgrades, looping of existing pipe):
- Check carefully whether any **new physical pipeline** is being built.
- If NO new pipe is being laid: `LengthKnown = 0`, `Diameter = blank`.
- If YES new pipe (e.g., a looping project adds parallel pipe): record the new pipe's length and diameter, not the existing system's.
- Note in ResearcherNotes what type of expansion it is.

### Ownership Divestiture Checks

For countries with recent major divestitures (e.g., Nigeria's Shell→Renaissance, Eni→Oando, ExxonMobil→Seplat transfers in 2024–2025), systematically check:
- Which pipelines were included in each divestiture package.
- What the new JV ownership structure is (operator %, NNPC %, etc.).
- Update ALL affected pipeline rows, not just the ones that come up in search results.

---

## Phase 3: Discovery — New/Missing Pipelines

**Goal:** Identify pipeline projects in the target country that are NOT in the existing tracker.

### Search strategies:
1. **Company project pages** — Check the websites of major operators in the country for pipeline projects under development.
2. **Regulatory filings** — Search FERC, PHMSA, MARAD (for US), or equivalent agencies for new pipeline applications.
3. **EIA / government data** — Check the EIA's petroleum pipeline projects database, or equivalent national data sources.
4. **Industry news** — Search for "[Country] new oil pipeline 2024 2025 2026" and "[Country] NGL pipeline construction."
5. **Deepwater/offshore** — For countries with offshore production, search for new subsea pipeline FIDs associated with field developments.
6. **Cross-border** — Search for any new cross-border crude or NGL pipelines.

### For each new pipeline discovered, collect:
All GOIT columns where data is available, with verified source URLs for every data point.

### Route / Map Research for New Pipelines

For every newly discovered pipeline, conduct a dedicated route search:

1. **First, look for official GIS/geometry data:**
   - Developer/operator project websites (e.g., `westerngatewaypipeline.com/project-details`)
   - Regulatory agency GIS portals (e.g., Texas RRC Public GIS Viewer, BOEM OCS pipeline data, PHMSA National Pipeline Mapping System)
   - Oil and Gas Watch (`oilandgaswatch.org`) — may have digitized routes with interactive maps
   - ArcGIS Online public datasets

2. **If no GIS file exists, look for visual route maps:**
   - Company press releases and investor presentations (often include schematic maps)
   - Industry publication articles (Offshore Magazine, OGJ, Pipeline & Gas Journal — often embed maps from company sources)
   - EIS/DEIS documents (contain detailed route maps, often as PDF appendices)
   - Federal Register notices with map references

3. **For offshore/deepwater pipelines:**
   - BOEM pipeline data at `data.boem.gov`
   - BSEE pipeline permits
   - Offshore Magazine's annual Gulf of Mexico map
   - Enbridge interactive map (`enbridge.com/map`) for Gulf of Mexico assets
   - Known platform/block coordinates (e.g., Green Canyon 19 = ~27.88°N, 89.17°W) can provide low-accuracy endpoints

4. **For conversions of existing pipelines** (e.g., Double H → Hiland Express):
   - The existing pipeline route should already be in databases (PHMSA, company websites)
   - Check if GEM already has a wiki page with the route geometry
   - Note in RouteNotes that this is a conversion of an existing pipeline

5. **Assign RouteAccuracy per GOIT conventions:**
   - `high` — Route has been digitally traced in GIS software or shapefile obtained from reliable source
   - `medium` — Route is not a straight line but hasn't been precisely traced (e.g., digitized from a press release map)
   - `low` — Basic point A to point B connection from known endpoints
   - `no route` — No route information available, or it's a capacity expansion with no new pipe

6. **Record in the spreadsheet:**
   - `RouteType`: Type of route (mapped, estimated, etc.)
   - `RouteLocation`: Where the GeoJSON is stored ("Folder" if uploaded, blank if not yet created)
   - `RouteAccuracy`: high / medium / low / no route
   - `RouteNotes`: Description of map source, endpoint coordinates if known, link to visual map image
   - `Route [ref]`: URL to the best available map source

---

## Phase 4: Structured Output — Excel File

**Goal:** Produce an Excel workbook with three sheets matching the GOIT column structure.

### Sheet 1: Updated Existing Pipelines
- One row per pipeline that has changes or new data.
- Carry forward all existing data from the CSV for unchanged columns.
- **Highlight changed/new cells in red** (red fill `FFCCCC` + red font `CC0000`) so the researcher can see what's been modified.
- Unchanged cells retain their original values with no highlighting.

### Sheet 2: New Pipelines (Discovery)
- One row per newly discovered pipeline, using the same column structure.
- **Highlight all populated cells in green** (`E2EFDA`) to distinguish from existing data.
- Include all available data with verified [ref] URLs.

### Sheet 3: Status Changes Summary
- Quick-reference table with columns: Pipeline Name, Segment, Current GOIT Status, Recommended Status, Key Evidence, Source URL.
- Highlight the "Recommended Status" column in red for changes.
- Include ownership corrections, fuel type corrections, and data corrections (e.g., length fixes) alongside status changes.

### Column formatting rules:
- Headers: Blue fill (`4472C4`), white bold font, center-aligned, wrap text.
- Freeze panes at row 2 (below headers).
- Key columns widened: PipelineName (45), SegmentName (50), Status [ref] (55), Owner (55), ResearcherNotes (55).
- Multiple URLs in [ref] columns separated by `, ` (comma + space), per GOIT convention.

### OtherEnglishNames column:
- When a pipeline is known by multiple names (e.g., Pacific Pipeline = Lines 901/903 = CA-324/CA-325 = Las Flores Pipeline System = Santa Ynez Pipeline System), list all alternative English names in the `OtherEnglishNames` column, separated by semicolons (`;`).

---

## Quality Checks — Before Delivering

Before presenting the Excel file, verify:

1. **URL spot-check:** Fetch 3–5 of the [ref] URLs to confirm they resolve correctly and contain the claimed data.
2. **Expansion length check:** For every expansion/capacity project, confirm whether new pipe is being built. If not: length = 0, diameter = blank.
3. **Ownership consistency:** If a divestiture affected multiple pipelines, confirm ALL affected rows have been updated (not just the ones that surfaced in individual searches).
4. **Status logic:** Verify that status changes follow GOIT conventions:
   - If no development updates for 2 years post-proposal → Shelved
   - If no development updates for 4+ years post-proposal → Cancelled
   - If confirmed cancelled by owner/news → Cancelled with ShelvedCancelledType = "Confirmed"
   - If presumed by GEM rule → ShelvedCancelledType = "Presumed"
5. **Date consistency:** If status = Operating, there should be a StartYear. If status = Cancelled, there should be a CancelledYear (or StopYear = "presumed" for 4-year rule).
6. **ResearcherNotes:** Every row with changes should have a ResearcherNotes entry explaining what changed, why, and any caveats (e.g., "Cost is total project, not pipeline-specific" or "Length is existing system total, not new construction").
7. **No GEM self-citation:** Confirm that no [ref] URLs point to gem.wiki or globalenergymonitor.org unless Baird explicitly approved it.

---

## Iterative Refinement

After delivering the initial Excel file, expect Baird to:
1. Review individual pipeline entries and challenge specific data points.
2. Ask for URL verification on specific [ref] cells.
3. Request deeper research on pipelines where findings seem thin or uncertain.
4. Flag corrections (e.g., expansion length issues, ownership nuances).

When corrections are identified:
- Acknowledge the error directly.
- Search for the correct information with verified sources.
- Update the relevant cells and regenerate the Excel file.
- Do NOT defend initial findings that turn out to be wrong — revise based on evidence.

---

## Controlled-Vocabulary Field Casing

ALL values must be lowercase, exactly as follows:

- **Status:** operating, proposed, construction, shelved, cancelled, idle, mothballed, retired
- **RouteAccuracy:** high, medium, low, no route (note: `very high (within meters)` is also a valid value)
- **PipelineType:** transmission, gathering, distribution
- **DelayType:** Presumed, Confirmed (exception: these two are title case)
- **ShelvedCancelledType:** Presumed, Confirmed (same exception — title case)
- **FIDStatus:** Pre-FID, FID (title case, only populated when Status = proposed)
- **Delayed:** Yes (title case; leave blank if not delayed — do not enter No)
- **Opposition:** Yes, No (title case)
- **RouteType:** match the exact dropdown strings from the sheet (e.g., Not mapped (but could be — route or endpoints are known), Mapped route (at any accuracy), Unavailable (cannot find route))

**General rule:** When in doubt about any controlled-vocabulary field, pull a real row from the GOIT database and match the exact casing and spelling before populating. Never assume Title Case or ALL CAPS for dropdown fields.

---

## Country-Specific Notes

### United States
- **Key regulatory sources:** FERC (gas/LNG), PHMSA (safety), MARAD (deepwater ports), EIA (project tracking), Texas RRC (Texas pipelines), Alaska DNR State Pipeline Coordinator
- **Deepwater export terminals:** Four competing projects (SPOT, Texas GulfLink, Blue Marlin, Bluewater Texas) — track MARAD license status, EPA CAA permits, and FID status separately
- **Gulf of Mexico deepwater:** New wave of pipeline FIDs in 2024 (Canyon Oil, Rome, Oceanus) — these are subsea pipelines with limited route data; use OCS block coordinates for low-accuracy routing

### Nigeria
- **Three major 2024–2025 divestitures** reshape ownership across the entire dataset:
  - Shell/SPDC → Renaissance Africa Energy (March 2025, $2.4B)
  - Eni/NAOC → Oando PLC (August 2024, $783M)
  - ExxonMobil/MPNU → Seplat Energy (December 2024, $800M)
- **PPMC/NPSC network:** Most segments are effectively idle due to vandalism — verify operational status before accepting "operating" at face value
- **Niger Delta pipelines:** Chronic sabotage, oil theft, and force majeure declarations mean "operating" status requires nuance — flag disruption history in ResearcherNotes and set Disrupted = TRUE where applicable

---

## Workflow Summary

```
1. Receive country + commodity scope + CSV data
2. Phase 1: Load data → filter → gap analysis
3. Phase 2: Deep research per pipeline (status + enrichment + verified URLs)
4. Phase 3: Discovery search for missing pipelines (+ route/map research)
5. Phase 4: Build Excel (3 sheets, red highlights for changes, green for new)
6. Quality checks (URL verification, expansion lengths, ownership consistency)
7. Deliver file + summary of key findings
8. Iterate based on Baird's review
```
