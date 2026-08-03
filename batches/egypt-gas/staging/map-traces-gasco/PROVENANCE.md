# GASCO 2007 Egypt gas network — map traces

Traced geometry for every gas line drawn on the GASCO **"Natural Gas Network,
Nov. 2007"** map, delivered as WGS84 GeoJSON. **Traces only** — no pipeline names, no
ProjectID matching, no research, no `[ref]` work. Nothing here has been written to
`GOIT-GGIT-pipeline-routes` or to the live GEM sheet, and this directory deliberately
sits outside the §8 route-creation lifecycle (no `candidates.json`, no
`staged_resolutions.json`, no workbook) so it is not misfiled as pending route-apply
work.

## Deliverable

`gasco2007_gas_network.geojson` — 224 LineStrings, 773 vertices, 6 dp, EPSG:4326.

| legend class | features |
|---|---|
| `existing_pl` (Existing P/L, solid green) | 161 |
| `under_study_pl` (Under Study P/L, dashed blue) | 52 |
| `under_construction_pl` (Under Cons. P/L, dashed red) | 11 |

219 features fall inside Egypt; 5 do not (the map extends into Israel/Jordan). They
are tagged `inside_egypt`, not dropped.

## Source

| | |
|---|---|
| file | `maps/source_mashreq_gas_initiative_2008.pdf` (committed here) |
| page | 15 |
| title on the sheet | GASCO, *Natural Gas Network*, Nov. 2007 |
| nature | **PDF vector art**, not a picture |

The page's pipelines are stroked PDF/SVG paths, so the geometry is *extracted*, not
raster-traced: `pdftocairo -svg` → parse each `<path>` → resolve its `transform`
matrix → keep the strokes whose colour matches a pipeline class. No skeletonization,
no judgement about where a line runs.

## Legend decoding

Colour→class was **read off the printed legend swatches in the art itself**, not
eyeballed — the swatches are vector strokes like the pipelines are, so their stroke
colours bind the classes directly:

| swatch | class |
|---|---|
| `#019901` solid | Existing P/L |
| `#3333FF` / `#0000FF` / `#333399` dashed | Under Cons. P/L |
| `#FF0000` dashed | Under Study P/L |

Excluded as not-pipe: the 204 short orange strokes (label leader lines), the green
map-frame rectangle, and the black/grey border work.

## Georeferencing

**The map prints its own 1° graticule.** That is the registration source — 70
graticule intersections, each of which has an exact lon/lat by construction, spread
over the whole sheet. No coordinate was read off the map and no lon/lat was invented.

- Fit: `scripts/georef.py`, **order 2 (quadratic)**, condition 4.05
- In-sample RMSE **1.91 km**, max residual 4.74 km
- **Leave-one-out RMSE 2.15 km** — the honest number, and it passes the SOP's
  `≤ max(5 km, 2% of length)` registration gate
- Order 1 (affine) was tested and is worse: LOO 6.63 km

Report: `georef/georef_report_gasco2007.json`. GCPs: `gcps/gcps_gasco2007.json`.

### What the 2.15 km does and does not mean

It measures how well the transform reproduces **the map's own projection**. It does
*not* mean a traced line lands within 2 km of the real pipe, because GASCO drew the
geography schematically. Measured independently against 23 OSM-geocoded settlements
that were **not** used in the fit (`gcps/validation_places_gasco2007.json`):

> **median drawn-feature offset 14 km**, RMSE 21 km, worst 48 km (Asyut).

That is the number to use when judging these traces. Every feature carries it as
`drawn_feature_offset_median_km`, plus `accuracy_tier: "low"`. **These are not
surveyed geometry** and must not be treated as such.

Rubber-sheeting toward the place markers was tried (affine, quadratic and thin-plate
spline on the places; graticule + TPS place correction) and **did not generalize** —
best place-based LOO was 17.9–19.0 km against the graticule fit's 2.15 km. So the
drawing is reproduced *as drawn*, under the map's own projection, and the schematic
error is reported rather than smeared around. `scripts/georef.py` was **not**
modified; the TPS experiment lived in scratch only.

## QC

- `overlays/qc_gasco2007_on_source.png` — traces redrawn on the rendered source page.
  Falsifiability check: a trace not sitting on a drawn line is not pipe.
- `overlays/qc_gasco2007_traces_only.png` — geometry alone.
- `overlays/qc_gasco2007_vs_gem_routes.png` — traces against GEM's existing
  high/medium-accuracy Egypt gas routes. The Nile valley trunk, the Suez corridor, the
  Western Desert lines and the delta all track GEM's routes; this is an independent
  corroboration of the registration, not an input to it.

Total traced length 9,299 km. The map self-reports "Total Length 16.5 Thousand Km",
which includes distribution mains that are not drawn — a loose upper bound only, not a
pass/fail gate.

## Scripts

| script | does |
|---|---|
| `extract_gasco2007.py` | SVG path extraction → `traces/gasco2007_paths.json` (page space) |
| `emit_gasco2007.py` | georeference + emit the GeoJSON + the georef report |
| `qc_overlay.py` | trace-on-source overlays |
| `qc_vs_gem.py` | overlay vs GEM reference routes |

## Not done

The **GASCO 2018 "National Gas Grid"** map (EGAS Annual Report 2017/18 p.19,
persisted here as `maps/gasco2018_p19.png`) was **not traced** — Baird's call
2026-08-02, on the grounds that it depicts the same network. It is raster-only (a
single 1811×2001 CMYK JPEG over a false-colour satellite basemap), so it would have
required colour masking and skeletonization rather than exact vector extraction.
