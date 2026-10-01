# SOP — Discover new pipelines

Find pipeline projects **not** in GOIT/GGIT and stage them as candidate new rows.
Reconciliation `Additions` (reference-only rows) feed directly into this SOP —
**but first try to match each one to an existing GEM pipeline under a different
name** (capture as `OtherEnglishNames`); only genuine misses become discoveries.

The search strategies and the route-research ladder are below (this SOP is their one
home; the original 4-phase methodology doc is archived in `docs/archive/`). Commands
(incl. the `country-discovery` workflow runner): `docs/workflows.md §4`.

## Inputs
- Region/country scope; whether to include early-stage proposals.

## Sequence
1. `scripts/refresh_csvs.sh`; build a dedup index of existing rows for the scope.
2. **Search strategies** (see "Search strategies" below): operator project pages;
   regulators (FERC/PHMSA/MARAD/BOEM/Texas RRC or national equivalents); EIA /
   government data; industry news (`"<country>" new oil pipeline <year>`);
   offshore/subsea FIDs; cross-border projects.
3. **"Sufficient information to add" threshold** — a candidate qualifies only with
   (a) an identified sponsor, (b) at least country + region/endpoint, and (c) a
   concrete step (MOU, FEED award, permit applied, tender). Below threshold → a
   `monitor_list` sheet, not a new row.
4. **Route / map research** (see "Route / map research" below; ladder values in
   `docs/reference/route_conventions.md`): official GIS first; else digitized visual
   maps; assign `RouteAccuracy` on the ladder; fill `RouteType`/`RouteNotes`/`Route
   [ref]`. (Capacity expansion, no new pipe → `no route`.)
5. Collect all GEM columns with verified `[ref]` URLs for each discovery.
6. `scripts/url_verifier.py` on all URLs; `scripts/entity_lookup.py` on every new
   owner/operator/parent.
7. Stage `batches/<scope>/staging/<run>/staged_new.json`; build
   `…_<scope>_discovery.xlsx` (new rows green-tinted); `recalc.py`; present.

**Owner/operator refs on a new row have no tab home.** Owner/operator `[ref]`s live on the
ProjectID-keyed operators/owners tab, which doesn't yet have a row for a not-created discovery.
So a staged `Owner [ref]` is **dropped from the `<Cmdty>_NewRows` mirror but preserved in
`staged_new.json`** — Baird adds it to the operators/owners tab after the new row gets a ProjectID.

## Search strategies

One pass per angle; the `country-discovery` workflow runs them as parallel agents.

**Seed leads are owed a disposition each.** Unmatched reference-dataset features (OSM/GulfPub
recon `DISCOVERY_CANDIDATE`s) are a list of named leads, not a search angle: a search agent handed
the list reports the seeds it can cite and silently skips the rest (Russia D2/D4/D5 2026-09-30 —
most seeds never surfaced). Pass them as the workflow's `args.seeds`; every one must end in the
seed ledger as `queued`, `matched` (PID), `monitor`, `dropped` (with why) or `already_handled`,
and the workbook's `<Cmdty>_SeedLedger` tab shows it. A seed with no disposition is unfinished work.

1. **Company project pages** — the major operators' sites for pipeline projects under
   development.
2. **Regulatory filings** — FERC, PHMSA, MARAD (US) or the national equivalent, for new
   pipeline applications.
3. **EIA / government data** — the EIA petroleum pipeline projects database or the national
   equivalent.
4. **Industry news** — `"<country>" new oil pipeline <year>` and `"<country>" NGL pipeline
   construction` (and the gas equivalents), in-country languages included.
5. **Deepwater / offshore** — new subsea pipeline FIDs tied to field developments.
6. **Cross-border** — new crude/NGL/gas lines touching the country in either direction.

For each discovery collect every GEM column where data is available, with a verified
`[ref]` for every data point. **Aliases:** a pipeline known under several names (e.g.
Pacific Pipeline = Lines 901/903 = CA-324/CA-325 = Las Flores Pipeline System = Santa Ynez
Pipeline System) lists them all in `OtherEnglishNames`, semicolon-separated
(`gem_schema.md`).

## Route / map research

For every new pipeline, a dedicated route search, in this order:

1. **Official GIS / geometry first** — developer project sites (e.g.
   `westerngatewaypipeline.com/project-details`), regulator GIS portals (Texas RRC Public GIS
   Viewer, BOEM OCS pipeline data, PHMSA National Pipeline Mapping System), Oil and Gas
   Watch (`oilandgaswatch.org`, digitized interactive routes), ArcGIS Online public datasets.
2. **No GIS file → visual route maps** — company press releases and investor presentations
   (schematic maps), trade-press articles (Offshore Magazine, OGJ, Pipeline & Gas Journal
   embed company maps), EIS/DEIS documents (detailed route maps, often PDF appendices),
   Federal Register notices with map references.
3. **Offshore / deepwater** — BOEM pipeline data (`data.boem.gov`), BSEE pipeline permits,
   Offshore Magazine's annual Gulf of Mexico map, the Enbridge interactive map
   (`enbridge.com/map`) for GoM assets; known platform/block coordinates (e.g. Green Canyon
   19 ≈ 27.88°N, 89.17°W) give low-accuracy endpoints.
4. **Conversions of existing pipelines** (e.g. Double H → Hiland Express) — the existing
   route is already in PHMSA / company databases and GEM may already hold the geometry; say
   "conversion" in `RouteNotes`.
5. **Assign `RouteAccuracy`** on the ladder in `docs/reference/route_conventions.md`
   (`high` traced/shapefile, `medium` digitized from a map, `low` A-to-B endpoints,
   `no route`; `high`/`very high` only for built pipe) and fill `RouteType`, `RouteNotes`
   (map source, endpoint coordinates, link to the visual map) and `Route [ref]` (the best
   map source URL).

## Escalate
If discovery surfaces more than ~5 candidate clusters in one country (a systematic
gap), pause and discuss scope before generating many new records.
