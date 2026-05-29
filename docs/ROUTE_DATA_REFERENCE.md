# Pipeline Route Data — Reference

Routes are GeoJSON, not stored in the main Google Sheet. This file points to where they live
and how to fetch them. (No route files are bundled here — they're pulled on demand.)

## Source of truth: public GitHub repo

`https://github.com/GlobalEnergyMonitor/GOIT-GGIT-pipeline-routes`

### Fetch a single route file (raw)
```bash
curl -sL "https://raw.githubusercontent.com/GlobalEnergyMonitor/GOIT-GGIT-pipeline-routes/main/{path-to-file}" -o route.geojson
```

### List folder contents / find a file by ProjectID (GitHub API)
```bash
curl -sL "https://api.github.com/repos/GlobalEnergyMonitor/GOIT-GGIT-pipeline-routes/contents/{path}"
```
Returns JSON listing of files in the folder; match on ProjectID (e.g., `P5367`) to locate the
right GeoJSON, then fetch via the raw URL above.

## Local mirror (Baird's machine — not in this bundle)
`/Users/baird/Dropbox/_git_ALL/_github-repos-gem/GOIT-GGIT-pipeline-routes`

## Conventions
- Projection: **EPSG:4326** (WGS84 lon/lat).
- Geometry: LineString / MultiLineString for routes.
- RouteAccuracy values: high, medium, low, no route, `very high (within meters)`.
- WKT/route-format QC checks are permanently dropped — do not rebuild route-format QC.

## In-sheet route columns
- `RouteType` — dropdown (match exact sheet strings).
- `RouteLocation` — "Folder" if GeoJSON uploaded; blank if not yet created.
- `RouteAccuracy` — see values above.
- `RouteNotes` — map source, endpoint coords, link to visual map.
- `Route [ref]` — URL to best available map source.

## Saudi Arabia / GulfPub note
The GulfPub comparison work treats GulfPub routes as more accurate than low/medium-accuracy GEM
routes. Spatial-consistency comparison (GEM route vs. GulfPub route) feeds the confidence score,
with a human-review step before any GEM route is replaced. GulfPub route WKT is captured in the
`Gulfpub_Routes_WKT` sheet of `GOIT_SaudiArabia_Gulfpub_Comparison.xlsx`.
