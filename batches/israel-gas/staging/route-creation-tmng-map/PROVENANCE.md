# Route genealogy — Israel gas / INGL-map batch

Every geojson this batch produces is traceable, end to end, back to a named
source. Two forms carry that lineage:

- **`route_provenance.json`** — machine-readable ledger for the whole batch.
- **`provenance` property on each feature** inside `candidate_routes/<PID>.geojson`
  — travels *with* the geometry into any routes-repo PR, so the lineage is never
  separated from the file. (Re)generate both with `python stamp_provenance.py`.

## Where the source artifacts live (all committed)

| Folder | Contents | Role |
|---|---|---|
| `maps/` | `ingl_big_map_fullres.jpg` | the source raster everything is traced from |
| `traces/` | `trace_*.geojson`, `extract_*.geojson` | digitized/extracted intermediate geometry |
| `candidate_routes/` | `<PID>.geojson` | the delivered candidate routes (provenance-stamped) |
| `overlays/` | `*.png` | visual QC (route drawn on the georeferenced map) |
| `georef_params.json` | ITM fit | pixel → EPSG:2039 → WGS84 transform |

> These were moved out of the gitignored `fetched_layers/` so the map + traces
> commit as provenance. `fetched_layers/` remains only for truly re-fetchable
> scratch.

## The two genealogy roots

```
ROOT A — INGL transmission raster map
  maps/ingl_big_map_fullres.jpg
    ( https://www.ingl.co.il/wp-content/uploads/2024/04/big-map.jpg
      via https://www.ingl.co.il/en/holancha/ , fetched 2026-07-23,
      base map © Survey of Israel 2018; map is schematic → cap medium )
        │  georef_params.json  (comb-fit ITM EPSG:2039, ~92.5 m/px)
        │  extract_offshore_lines.py  (color-mask → BFS path → simplify → WGS84)
        ▼
     traces/trace_leviathan.geojson ──▶ build_route_candidate.py ─▶ candidate_routes/P7602.geojson, P7603.geojson
     traces/trace_p0480.geojson      ──▶ build_route_candidate.py ─▶ candidate_routes/P0480.geojson  (replacement)
     traces/trace_karish.geojson     ──▶ build_route_candidate.py ─▶ candidate_routes/P8003.geojson  (NEW discovery row)
     traces/trace_tamar.geojson      ──▶ (reference only — NOT promoted; see note)
     traces/trace_marib.geojson      ──▶ (reference only — NOT promoted; see note)

ROOT B — existing high-accuracy GEM geometry (routes repo)
  GOIT-GGIT-pipeline-routes : data/individual-routes/gas-pipelines/P3658.geojson  (RouteAccuracy high)
        │  extraction of the Elyakim↔Ramle eastern trunk the network already contains
        │  (map used only to CONFIRM the corridor, not to trace)
        ▼
     traces/extract_p2197.geojson    ──▶ build_route_candidate.py ─▶ candidate_routes/P2197.geojson  (replacement)
```

## Per-route lineage

| PID | Root | Immediate parent | Method | Cap | QC gate |
|---|---|---|---|---|---|
| P7602 Leviathan I | map | `traces/trace_leviathan.geojson` | map trace | medium | PASS |
| P7603 Leviathan II | map | `traces/trace_leviathan.geojson` (shares I corridor) | map trace | medium | PASS |
| P0480 Israel–Jordan | map | `traces/trace_p0480.geojson` | map trace, replaces prior chord | low | PASS |
| P8003 Karish–Dor (NEW) | map | `traces/trace_karish.geojson` | map trace, new discovery row | medium | PASS |
| P2197 Ramle–Elyakim | GEM geom | `P3658.geojson` → `traces/extract_p2197.geojson` | extracted, replaces 2-pt chord | medium | FAIL* |

**Traces kept as reference but deliberately NOT promoted to candidates:**
`trace_tamar.geojson` (186 km, Tamar platform→Ashdod) and `trace_marib.geojson`
(23 km, →Ashkelon) back the discovery finding for P8001 (Tamar/Mari-B→Ashdod export
line) but are not staged as route geometry: the northern תמר map label is
schematically displaced, the two traces disagree on the landfall (Ashdod vs
Ashkelon), and the real export-line length (~42 km Mari-B→Ashdod) is unverified.
Per both discovery agents, P8001's route needs a GIS-level source before geometry is
drawn — so the row is staged without a route. See `docs/country_notes/israel.md`.

\* P2197's gate FAIL is a **documented, non-blocking** Natural-Earth coarse-boundary
artifact (16.2 km "Palestine" landfall where the trunk hugs the Green Line) —
**identical** to its accepted parent P3658, which is classed Israel-only/high. Not a
defect in the extraction; full reasoning in `staged_resolutions.json` and the feature's
`provenance.researcher_notes`.

## Reproducing any route from scratch

1. `python georef_ingl_map.py` → rebuilds `georef_params.json` from `maps/…jpg`.
2. `python extract_offshore_lines.py <key> x0 y0 x1 y1 [dilate]` → re-traces a line into `traces/`.
3. `python /…/scripts/build_route_candidate.py --method traced --geom traces/<file>.geojson …` → candidate.
4. `python stamp_provenance.py` → re-stamps provenance onto the geojsons + ledger.
