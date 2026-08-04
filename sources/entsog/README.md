# ENTSOG/GIE System Capacity Map 2026 — extracted pipeline vectors

Source: **ENTSOG/GIE System Capacity Map 2026** (January 2026 edition), the
official ENTSOG transmission-capacity wall map. PDF committed alongside:
`ENTSOG_GIE_SYSCAP_2026_1600x1200_FULL_016_FLAT.pdf`, downloaded 2026-08 from
<https://www.entsog.eu/sites/default/files/2026-01/ENTSOG_GIE_SYSCAP_2026_1600x1200_FULL_016_FLAT.pdf>.

This is a **map-trace layer, not a registered reconciliation dataset** — there is
no `manifest.yml`; it is used as a §8 route-creation source (traced → `medium`
accuracy cap) and as corroboration, in the same spirit as `maps/` + `traces/`
layers elsewhere.

## Files

- `ENTSOG_GIE_SYSCAP_2026_pipelines_operational_wgs84.geojson` — solid strokes
  (operational), with the map's three line-weight classes in `properties.layer`
  (DN900+, DN600–900, <DN600).
- `ENTSOG_GIE_SYSCAP_2026_pipelines_project_wgs84.geojson` — even-dash strokes
  (projects / FID-pending as drawn by ENTSOG).
- `ENTSOG_GIE_SYSCAP_2026_pipelines_not_operational_wgs84.geojson` — dash-dot-dot
  strokes (built, not operational).
- `build_entsog.py` — the extractor (run inside this directory): PyMuPDF vector
  extraction from page 0, Béziers flattened at 8 steps, strokes classified by the
  PDF layer (OCG) name and dash pattern per the map legend.
- `affine_icp.npz` — the georeferencing transform (`W`, `v`: page-points →
  EPSG:3857 affine), fit by ICP of the map's coastline layer against the Natural
  Earth coastline; median residual ≈ 1 m in projected space (the fitting session's
  script was not retained — the transform itself is the reproducible artifact).

## Accuracy (measured, Egypt window)

Cartographic accuracy is far coarser than the georef residual: against 24
high/medium-accuracy GEM Egypt gas routes (2026-08-04 pass), median lateral
offset **4.2 km**, p90 **13 km**. Hence traced ENTSOG geometry is capped at
`RouteAccuracy = medium` and is never used to overrule a `high` route.

First used: Egypt gas §8 route-creation pass 2026-08-04
(`batches/egypt-gas/staging/route-creation-20260804/` — network matcher
`entsog_match.py` there builds a routable graph from these strokes).
