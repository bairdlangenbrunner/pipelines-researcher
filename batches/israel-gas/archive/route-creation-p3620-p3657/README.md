# Route creation — Ashdod–Ashkelon Gas Pipeline (P3620 onshore, P3657 offshore)

§8 route-creation run, 2026-07-22/23. Israel, gas (GGIT).

**APPLIED to the routes repo 2026-07-23** (Baird-directed): after Baird's manual
edit bridging the Ashdod HDD bore in P3620 (now 2.1 km, ending at the marine
tie-in 31.8543N/34.6590E = P3657's start), both geojsons were committed to
`GOIT-GGIT-pipeline-routes` main (merge `72d29de1`, pushed to origin).
Sheet edits APPLIED 2026-07-23 (Baird-directed, via Sheets API): both rows
(1036/1063) RouteAccuracy high→medium, RouteNotes filled, Route [ref] replaced
with the TAMA/NtM/INGL map sources.

Sheet context: both rows claim `RouteAccuracy = high` / "Mapped route", but both
routes-repo geojsons are **empty placeholders** — these candidates fill missing
geometry (`replacement: false`).

## Candidates

- **`candidate_routes/P3657.geojson`** — offshore segment, 41.6 km (sheet 42, ratio
  0.99), **gate PASS**, suggested accuracy **medium** (downgraded from the gis
  method's default: it's a corridor midline, not an as-built survey). Two official
  vector sources spliced at 31.8747N/34.5828E (66 m seam agreement):
  1. TAMA 37/A/2/7 statutory blueprint strip midline for the Ashdod ~9.2 km
     (±~175 m; starts at the HDD shore-crossing compound = true landfall);
  2. NtM 113/2024 works-corridor midline for the remaining ~32 km (±~500 m —
     half the ~1.0 km corridor width).
- **`candidate_routes/P3620.geojson`** — onshore segment, **PARTIAL**: the
  Ashdod ~1.5 km strip midline (±~20 m) plus the ~0.6 km HDD bore bridge added
  by Baird 2026-07-23 (total 2.1 km, connecting to P3657's start). Gate **FAIL
  on length ratio 0.52 — expected and explained**: the Ashkelon-side ~2.4 km
  onshore run has no public vector source (OSM empty; blueprint sheets cover
  Ashdod only), and we don't fabricate. Gap is logged in
  `docs/research_backlog.md`.

## Derivation (fully reproducible, no hand-drawn coordinates)

- `derive_p3657_midline.py` — NtM 113/2024 23-point DMS corridor polygon
  (transcribed verbatim) → 1:1 vertex-pair midpoints + Ashdod tail →
  `fetched_layers/ntm113_corridor.geojson`, `p3657_ntm_midline.geojson`.
- `derive_tama_strips.py` — TAMA 37/A/2/7 GIS bundle
  (`fetched_layers/tama_37a27_1053432_gis.zip`, JPG + JGW world file EPSG:2039) →
  color-segmented green pipeline strip (רצועת צנרת) → centroid midlines →
  `p3620_ashdod_strip_midline.geojson`, `p3657_combined_midline.geojson`.
- Candidates then built with
  `scripts/build_route_candidate.py --method gis --accuracy medium` (validation
  gate + provenance + staging upsert).

## Sources (all url_verifier-passed)

- NtM 113/2024, Israel Ports & Shipping Authority (רספ"ן), 02 Dec 2024 — mirror:
  `https://kachol.com/wp-content/uploads/2024/12/הודעה-למשיטים-1132024-פרויקט-הנחת-צינור-גז.pdf`
- TAMA 37/A/2/7 (plan 1053432) GIS bundle:
  `https://apps.land.gov.il/IturTabotData/download/jerus/1053432.zip`
  (+ regulations PDF, proposed-state sheet PDF under the same store)
- INGL project page: `https://www.ingl.co.il/en/sea-line-project-ashdod-ashkelon/`
  (prose: 36″, ~42 km marine + ~4 km beach lines); INGL national transmission map
  `big-map-scaled.jpg` — schematic disclaimer, corroborator only.

Both endpoints registered in `sources/gis_endpoints.yml`
(`israel_itur_tabot`) + `docs/reference/source_roster.md`.
