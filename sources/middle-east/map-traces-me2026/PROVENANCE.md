# Energy Infrastructure Map of the Middle East, 2026 — vector trace + georeference

## Deliverable

- `me2026_pipelines.geojson` — **339 LineStrings, 8,742 vertices, 83,069 km**, EPSG:4326.
  Every feature carries the full genealogy block (source map, page, publisher,
  georeferencing method and residuals, accuracy tier) plus per-feature
  `commodity`, `status_class`, `legend_class`, `stroke_rgb`, `dashed`, `name`,
  `name_dist_pt`, `name_confidence`, `name_ambiguous`, `commodity_conflict`,
  `other_names`, `diameter_in`, `length_km`, `n_vertices`.
  Every property is a **flat scalar** — no nested objects, no arrays
  (`other_names` is `;`-joined, matching the sheet's `OtherEnglishNames`;
  `drawn_feature_offset_median_km` is the feature's own commodity's value).
  QGIS reads a nested value as a `QVariantMap`/`QVariantList` and the OGR
  GeoJSON writer then refuses to write the feature, so a route traced off this
  layer could not be exported. Keep new properties flat.
- `me2026_gas_pipelines.geojson` — **190 routes, 49,791 km** (29 named), for GGIT.
- `me2026_oil_pipelines.geojson` — **149 routes, 33,278 km** (21 named), for GOIT.
  The two commodity files are a `commodity` filter over the combined one —
  identical features and properties, disjoint, and together exactly the 339.
  `assemble.py` writes all three in one pass.
- `me2026_labels.geojson` — 905 georeferenced label points (67 pipeline names,
  208 places, 22 countries, 15 capitals, 593 other), kind-tagged by source font.

Breakdown:

| legend class | routes | km |
|---|---:|---:|
| gas, in service | 152 | 39,590 |
| gas, under construction / planned / proposed | 38 | 10,201 |
| oil, in service | 143 | 31,289 |
| oil, under construction / planned / proposed | 6 | 1,988 |

50 routes carry a name (29 high / 8 medium / 13 low confidence); 85 carry a
diameter parsed from the caption's `[NN]` tag.

## Source

`../energy-map-of-the-middle-east-2026-peregrine-bush.pdf` — *Energy
Infrastructure Map of the Middle East, 2026 edition*, published by Petroleum
Economist / World Oil / Gulf Energy Information / Global Energy Infrastructure.
One page, 2525.67 × 2394.31 pt, **no raster images** — the map is entirely
vector, 3,511 drawing paths, 13 embedded CFF Type1 subset fonts. Neatline
bbox `[42, 44, 2483, 2354]`.

The map's own source roster (its "Sources" block): Petroleum Economist, Global
Energy Infrastructure, World Oil, ADNOC, Aramco, BAPCO, Botas, bp, Cedigaz,
CNOOC, Crescent Petroleum, Dana Gas, ExxonMobil, KNPC, NIOC, Oman LNG, OPEC,
Penspen, PDO, QatarEnergy, Shell, TotalEnergies, Turkish Petroleum and others.

> **Copyright, verbatim from the map:** *"No reproduction whatsoever of this map
> or any part thereof is permitted without prior consent of the copyright
> owners."* This is a commercial wall map. The traces here are a derived
> extraction held internally for research; treat any redistribution — including
> publishing the geometry — as needing the publisher's consent. Nothing from
> this directory has been pushed to the routes repo, the tracker, or anywhere
> public.

## Legend decoding

Stroke colour maps to commodity **the opposite way round from intuition**:

| stroke | dash | class |
|---|---|---|
| red `(0.844, 0.098, 0.126)` | solid | **gas**, in service |
| red | `[2 2]` | **gas**, under construction / planned / proposed |
| green `(0.0, 0.573, 0.28)` | solid | **oil**, in service |
| green | `[2 2]` | **oil**, under construction / planned / proposed |
| green + black dotted overlay | — | oil pipeline **mothballed** (see *Not done*) |

Verified four independent ways before anything downstream depended on it:

1. The legend swatches' own page coordinates sit under the decoded headings
   `Gas pipelines` and `Oil pipelines`.
2. A 13-pipeline self-check against captions that name their own commodity:
   13 correct, 1 mismatched, **0 mismatches at medium or high name confidence**.
3. Unambiguous anchors: Tapline (crude) is green, Dolphin (gas) is red.
4. A 7× crop of the IGAT 5/6 leader lines, read by eye.

The text layer is obfuscated (subset fonts with `/MT<codepoint>` glyph names in
`/Differences`), so it was decoded from the font `/Encoding` rather than by OCR,
with cp1252 handling for 0x80–0x9F. Independently proven by cross-checking the
`/Widths` arrays against known Arial and Arial Bold advance widths: **117/117
exact matches, 0 mismatches**.

## Georeferencing

The map carries **no graticule** — there is nothing to read control points off.
Instead the map's own **cyan coastline layer** was registered to Natural Earth
10m coastline + lakes by coarse equirectangular grid search followed by trimmed
ICP (60% quantile), and a page → (lon, lat) polynomial was fitted to the
correspondences. The Strait of Hormuz inset and everything outside the neatline
are excluded from the fit.

| | order 1 (affine) | **order 2 (quadratic, shipped)** |
|---|---:|---:|
| in-sample, cyan coastline (n=12,000) | 2.90 km median / 4.91 RMSE | **0.87 / 0.97** |
| held-out, grey borders (n=7,200) | 3.31 / 4.73 | **1.45 / 1.60** |

The held-out number is the honest one: `register.py` fits the **cyan** layer
only, and `validate_georef.py` scores the map's **grey country-border** strokes
— never seen by the fit — against `ne_10m_admin_0_countries`. It is also
conservative, since it charges us for genuine Natural-Earth-vs-publisher border
disagreement. `georef/fit_order2.npy` is what `assemble.py` applies.

## What the numbers do and do not mean

There are **two distinct error terms**, and only the second one limits how the
geometry can be used:

1. **Georeferencing residual — 1.45 km median / 1.60 km RMSE.** How well the
   fitted transform reproduces the map's own projection. This is a property of
   the registration, not of the pipelines.
2. **Drawn-feature offset — gas 3.06 km, oil 2.39 km median.** How faithfully
   the cartographer drew the pipe in the first place. Measured by
   `qc_vs_gem.py` against GEM routes already carrying `RouteAccuracy` *high* or
   *very high*: 97 Middle East routes, **71 inside the sheet's footprint** and
   scored (26 excluded because they run outside the sheet — Iran–Pakistan–India,
   Dauletabad, Egypt west of ~34°E — where scoring would measure the map's
   coverage, not its accuracy). 59% of gas and 73% of oil routes land within
   5 km. Distances are measured **GEM → ours**, because chaining splits our
   polylines at junctions and the reverse direction would charge us for pipe
   GEM has not drawn.

So the geometry is good to roughly **2–3 km**, dominated by the drawing, not the
registration. That is a `RouteAccuracy` judgement for the researcher to make,
not one made here — nothing in this directory sets or proposes a RouteAccuracy
value. These routes are **candidate geometry**: a wall map is a single
secondary source, so a route from here still needs the normal §8 treatment
(corroboration, `qc_routes.py`, human PR) before it goes anywhere near the
routes repo or the sheet.

## Caption attachment, and where it is weakest

Captions do not sit on the line they describe. The map uses **black leader
lines**, and following them is what makes attachment correct: `extract_leaders.py`
pulls 709 short black strokes, and `assemble.py` anchors a caption at the far
endpoint of the longest leader touching its bounding box. 31 of 67 pipeline-name
captions are anchored this way. Before leader-following, `IGAT 6 [56]` attached
at high confidence to a *green* line 0.7 pt away while its actual red trunk sat
19.2 pt off; afterwards IGAT 4, 6 and 9 all moved to gas at high confidence,
commodity conflicts fell 6 → 2 and ambiguous names 19 → 13.

**Open question — the IGAT numbering.** Eleven near-parallel Iranian trunks run
within a few km of each other, and caption→line assignment is least reliable
there. The evidence says the *geometry* is fine and the *numbering* is not:

| GEM route | distance to the line we labelled with that name | distance to the nearest line in our gas network |
|---|---:|---:|
| P0442 IGAT 2 | 8.30 km | 2.22 km |
| P0443 IGAT 3 | 39.15 km | 4.08 km |
| P0446 IGAT 7 | 74.02 km | 17.45 km |
| P0444 IGAT 4 | 93.56 km | **56.17 km** |

The first three are a labelling mismatch, not a drawing error — the map draws
pipe where GEM says pipe is, we just hung the wrong number on it. P0444 is
different: 56 km from *any* gas line we extracted, which is a genuine open
question (either the map omits IGAT 4, draws it very differently, or GEM's route
is wrong). Recorded, not smoothed over. Do not trust an `IGAT n` name from this
extraction without checking it.

**Two remaining commodity conflicts**, both flagged in `commodity_conflict` and
both low name-confidence: `ME2026-0038` "Arab Gas Pipeline" (drawn green) and
`ME2026-0323` "Southern Oman Gas Line (SOGL)" (drawn green). The colour is the
stronger evidence — captions attach by proximity, colour is read off the stroke
itself — but neither has been resolved.

## QC

- `overlays/qc_me2026_on_source.png` — extracted strokes redrawn over the
  rendered page. Inspected across the Gulf, Iran, Iraq, Kuwait, Qatar and the
  UAE: every drawn pipeline is covered and no trace floats off-line.
- `overlays/qc_me2026_georeferenced.png` — routes plotted against the Natural
  Earth coastline.
- `georef/validation_report.json` — the held-out border validation.
- `georef/qc_vs_gem_pairs.csv`, `georef/qc_vs_gem_network.csv` — the
  drawn-feature offset, per named pair and network-wide. GEM routes are used
  here as a **yardstick for our geometry only**; GEM is never cited as a source
  and nothing was written back.

## Scripts (run in this order, from this directory)

| script | does |
|---|---|
| `extract_paths.py` | red/green strokes → `traces/pipelines_pagespace.json` (339 chained polylines; drops furniture boxes and sub-0.6 pt symbol strokes) |
| `extract_leaders.py` | short black strokes → `traces/leaders.json` (709) |
| `extract_basemap.py` | cyan coastline + grey borders → `traces/basemap_lines.json` (~12 MB, gitignored) |
| `decode_text.py` | font-`/Encoding` de-obfuscation → `traces/labels.json` (1,155 lines) |
| `register.py` | grid search + trimmed ICP → `georef/fit_order{1,2}.npy`, `fit_report.json` |
| `validate_georef.py` | held-out grey-border score → `georef/validation_report.json` |
| `assemble.py` | applies the order-2 fit, attaches captions via leaders, stamps genealogy → both GeoJSONs |
| `qc_overlay.py` | the two QC PNGs |
| `qc_vs_gem.py` | drawn-feature offset vs GEM high-accuracy routes |

The whole chain was re-run end to end in this directory to confirm it
reproduces; the stamped genealogy numbers are the reproduced fit's, not an
earlier run's.

## Not done

- **Mothballed oil is not separated.** The legend documents a green + black
  dotted "oil pipeline mothballed" style; the extractor does not detect the
  black dotted overlay, so those lines land in `oil_in_service`. Tapline is
  correctly marked only because its own caption says "mothballed".
- **No matching to GEM ProjectIDs.** Nothing here is reconciled against GOIT or
  GGIT rows; the seven pairs in `qc_vs_gem.py` are hand-verified QC anchors, not
  a crosswalk.
- **Nothing written to the routes repo or the backend sheet.** These are staged
  traces in this repo only.
- Non-pipeline map content (fields, refineries, plants, terminals) is decoded in
  `traces/labels.json` and georeferenced in `me2026_labels.geojson`, but no
  point-symbol geometry was extracted for it.
