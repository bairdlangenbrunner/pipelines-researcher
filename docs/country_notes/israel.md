# Israel

Gas only (no GOIT crude/NGL rows). Small, dense, well-documented transmission grid
plus a cluster of offshore field-to-shore export lines (Tamar, Leviathan, Karish) and
several cross-border/paper lines (EMG, Israel–Jordan, Israel–Cyprus, EastMed, Gas for
Gaza). GEM had 22 gas rows at the 2026-07-23 snapshot.

## Regulators / official data
- **Israel Natural Gas Lines (INGL / נתג"ז)** — owns/operates the national transmission
  grid; publishes the TMNG system map. `ingl.co.il`.
- **Ministry of Energy (Petroleum Commissioner)** — licences, field development plans.
- **Survey of Israel** — base mapping; the INGL map is drawn on the Israeli TM grid
  (ITM, EPSG:2039), gridlines every 20 km.

## Key operators / owners
- **INGL** — national transmission grid; also owns the nearshore (~10 km) + onshore
  Dor receiving facilities for Karish (title transferred from Energean under a 2019
  agreement, ~$102m).
- **Chevron (formerly Noble Energy)** — Tamar operator; Leviathan operator.
- **Energean plc** (via Energean Israel Ltd, 100%) — Karish/Tanin FPSO and its export line.
- **EMG / East Gas Company** — El Arish–Ashkelon line; see the P0462 ownership flag below.

## Routing / GIS tips
- The **INGL/TMNG raster map** (`batches/israel-gas/staging/route-creation-tmng-map/maps/ingl_big_map_fullres.jpg`)
  is georeferenced to ITM (EPSG:2039), ~92.5 m/px; the georef params + provenance live in
  that staging dir (`georef_params.json`, `route_provenance.json`, `PROVENANCE.md`). The
  map's own disclaimer calls it **schematic**, so anything traced from it caps at
  `RouteAccuracy = medium` (route-creation SOP "traced" rung). It is a ~2018 snapshot —
  informs status/coverage but never overrides current sources.
- Route genealogy for produced geojson has two roots: (1) the INGL raster trace, and
  (2) extraction from existing high-accuracy GEM geometry (P3658). Every candidate
  feature carries a `provenance` block; see `PROVENANCE.md`.

## Gotchas
- **Ashdod vs Ashkelon landfall (P8001).** The INGL map suggests an Ashkelon landfall for
  the Mari-B/Yam Tethys export line, but the 2002 transmission licence and all engineering
  sources say **Ashdod** (Ashkelon on the map = the offshore field position + a separate
  INGL station). P8001 geometry is deferred until this is resolved.
- **One physical pipe, two map lines.** The map's "Tamar→Ashdod" and "Mari-B→Ashkelon"
  lines are the *same* 30-inch Mari-B/Yam Tethys export pipe (built 2004; Tamar hot-tapped
  into it in 2013). Collapsed into one row (P8001), not two.
- **Karish nearshore/onshore is INGL, not Energean** — the offshore export line (P8003) is
  Energean's; the last ~10 km + Dor station are INGL's.
- Possible pre-existing gem.wiki page "Karish and Tanin Fields Gas Sales Pipeline" — check
  before publishing P8003 to avoid a duplicate.

## What this batch staged (INGL/TMNG ground-truth, 2026-07-23 — NOT applied)

Staging under `batches/israel-gas/staging/`; deliverables under `.../deliverables/`
(`pipelines_batch_20260723_1105_ET_israel-gas_route-creation.xlsx`,
`pipelines_batch_20260723_1606_ET_israel-gas_discovery.xlsx` + P8001/P8003 wiki texts).

- **Discovery — 2 new rows** (`staging/discovery-tmng-map/staged_new.json`):
  - **P8001 Mari-B–Ashdod Gas Pipeline** — operating, 30 in, ~6 bcm/y, start 2004; owner/parent
    open item; geometry deferred (Ashdod-vs-Ashkelon).
  - **P8003 Karish–Tanin FPSO Gas Export Pipeline** — operating, first gas 26 Oct 2022,
    90.3 km, dual 30/24 in, 8 bcm/y, Energean 100%; route candidate staged.
- **Validation — 5 candidate edits** (`staging/validation-tmng-map/staged_edits.json`;
  all candidates for Update, none auto-applied): **P7604** Leviathan III status
  construction→operating; **P7606** Leviathan IV no-change (pre-FID) + flag; **P0479**
  Israel–Cyprus EndLocation FPSO→Vassiliko + capacity re-verify flag; **P5276** Gas for Gaza
  no-change (war-suspended) + do-not-auto-replace route flag; **P0462** EMG ownership relabel
  (Egyptian Natural Gas Co→East Gas Company; Chevron 33.54%→9.75%) + diameter 26 in (needs
  1 more source) + ResearcherNotes cleanup.
- **Route candidates — 5** (`staging/route-creation-tmng-map/candidate_routes/`, medium,
  never auto-replaced): P7602 & P7603 Leviathan Subsea I/II (119.3 km, QC pass), P0480
  Israel–Jordan (54.1 km, pass), P8003 Karish (87.5 km, pass, ends ~9.7 km short of Dor),
  **P2197 Ramle–Elyakim (90.0 km, QC FAIL — documented, not delivered as replacement)**.

## Open items
- **P8001** — owner/parent (original Yam Tethys partners) and length (~42 km, single-lineage,
  unverified) still open; geometry deferred pending the Ashdod-vs-Ashkelon landfall question.
- **P8003** — confirm no existing gem.wiki "Karish and Tanin Fields Gas Sales Pipeline" row
  before publishing; route candidate ends ~9.7 km short of Dor (nearshore/onshore is INGL).
- **P3620 Ashdod–Ashkelon** — routes/sheet applied 2026-07-23 but geometry still partial
  (2.1 of ~4 km); the Ashkelon-side ~2.4 km onshore run has no public vector yet (see
  `docs/research_backlog.md`). P3657 complete.
- **P0462** — diameter 26 in needs a second independent source; ownership relabel routed to Update.
- **P2197 Ramle–Elyakim** — route candidate failed QC; needs a better source than the schematic map.
- **Separate Ashdod–Ashkelon feeder** seen on the map is a possible future discovery row
  (distinct from P3620/P3657 and from P8001).
- **Oil/NGL** — Israel not yet swept on the GOIT side (no crude rows expected, but unconfirmed).
