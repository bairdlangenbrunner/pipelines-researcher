# INGL/TMNG transmission-map — legend interpretation & digitization scheme

Source raster: `maps/ingl_big_map_fullres.jpg` (INGL national natural-gas
transmission map, "big-map.jpg", ingl.co.il; base map © Survey of Israel 2018).
Georeference: `georef_params.json` (ITM EPSG:2039 comb fit, ~92.5 m/px).

**Read the legend before tracing.** This file transcribes the map's own key
(מקרא, bottom-left) and records how each symbol maps onto the digitization — in
particular which symbols are **point-anchors** the traced routes must pass
*dead-through*, and which band-color decodes to the bright-fill mask the
centerline recentering targets. Hebrew is transcribed verbatim from the raster;
English is a working translation.

## Standing caveat (from the map's own disclaimer box)

> "הצגת כלל המערכות במפה הינה סכמטית ונועדה להתרשמות בלבד…" — the presentation of
> all systems is **schematic**, intended for general impression only; depiction is
> based on information supplied to the company.

→ Any geometry traced from this map is capped at **`RouteAccuracy = medium`**
(route-creation SOP "traced" rung). The ~2018 snapshot informs status/coverage
but never overrides current sources.

## Line types (band symbols)

Each transmission line is drawn as a colored **band** (a colored centerline fill
flanked by darker blue edges). The band *fill color* is the classifier:

| Hebrew | English (working) | Band fill | Digitization note |
|---|---|---|---|
| קו פעיל / בהקמה | active / under construction | **yellow** center (blue-yellow-blue) | onshore trunk; the INGL grid P3658 |
| קו מוכפל, פעיל / בהקמה | twinned, active / under construction | yellow w/ dark ticks | twinned segment |
| קו פעיל המיועד להכפלה | active, marked for twinning | **red/orange** center | — |
| **קו מספקי גז, פעיל / בהקמה** | **gas-suppliers line, active / u.c.** | **white/light** center (blue-white-blue) | **the offshore field→shore bands** — Leviathan (P7602/P7603) and Karish/Tanin (P8003). This is the band the bright-fill mask `r>180 & g>205 & b>200` targets for centerline recentering. |
| קו גז במדינות שכנות | gas line in neighboring countries | dark-blue **dashed** | the P0480 Israel–Jordan style symbol; dashed on a topo basemap → NOT amenable to the white-fill recenter (kept a human-review candidate) |
| קו בתכנון סטטוטורי | line in statutory planning | solid medium-blue | planning corridor (status ground-truth only) |
| קו מאושר בתכנית סטטוטורית | approved in statutory plan | blue-cyan-blue (light) | planning corridor |

## Point symbols — the digitization ANCHORS

These are discrete facility markers. Where a traced line begins/ends/passes at
one, the trace is routed **through the exact center of the symbol** (detected by
point-symmetry: the true center minimizes the mean abs difference between a patch
and its 180°-rotation). This is the "connect directly to legend points" scheme.

| Hebrew | English (working) | Symbol | Used as anchor for |
|---|---|---|---|
| **מיקום הקידוח** | **well location** | **⊕** (circle enclosing a 4-point diamond/star) | **Tanin** ⊕ and **Karish** ⊕ well-markers — P8003 passes dead-through both centers |
| תחנת קבלה ימית | marine receiving station | cyan **circle-R** (○R) | **Dor / INGL OOAT** terminus of P8003 (labeled "תחנת קבלה ימית אופציונלית", optional) |
| סעפת תת ימית… וליצוא עתידי | subsea manifold (small-reservoir tie-in & future export) | cyan rounded **OOAT** box | the OOAT facility annotation near the Dor terminus |
| אסדה | platform | derrick/tower icon | **Leviathan** platform (P7602/P7603 landfall corridor) |
| תחנת קבלה | receiving station (onshore) | cyan **R** box | onshore reception |
| תחנת הפחתת לחץ ומדידה (PRMS) | pressure-reduction & metering station | yellow **P** box | onshore grid node |
| תחנת הגפה | valve / block station | solid yellow box | — |
| תחנת PRMS לתחנת כח ולחלוקה | PRMS for power + distribution | **DP** box | — |
| תחנת CNG | CNG station | **C** box | — |
| תחנת PRMS לחלוקה | PRMS for distribution | **D** box | — |
| תחנת כוח | power station | red factory icon | demand node |
| אתר התפלה | desalination site | blue droplet | demand node |
| גבול ישראל | Israel border | dashed rectangle | — |
| גבול רשיון / זיכיון לקידוח | drilling license / concession boundary | thin solid-blue rectangle | field-block boundaries |

(Planned/statutory variants of the station symbols use light-green = statutorily
approved, light-blue = planned.)

## Tracing rules distilled from the map (apply to every line)

1. **Follow the band CENTERLINE, not the dark outline edge.** The near-white BFS
   mask walks the dark band *edge* (~4 px / ~415 m off). Recenter every point onto
   the bright-fill midpoint along the local perpendicular (`recenter_traces.py` /
   the `recenter()` in `retrace_karish_tanin.py`).
2. **Pass dead-through every point-anchor.** Detect the symbol center by
   point-symmetry (±7 px search, radius 10) and pin the trace endpoint / junction
   to it. Do not sit offset on the band near the marker.
3. **Stay straight at crossings.** Where two lines cross they *look* like they run
   over/under one another; the trace must continue straight through. Enforced by
   rejecting fill runs wider than `MAX_RUN_PX` (a merge = a crossing → keep the
   straight guide point, offset 0) and capping any single shift at `MAX_OFFSET_PX`.
4. **Don't cut corners on turns.** Densify before recentering so bends are sampled
   finely enough to track the band around a turn.
5. **Onshore dashed/topo-basemap lines are not white-band traces.** The
   neighboring-countries dashed symbol (P0480) can't use the white-fill recenter;
   trace it by hand and keep it a human-review candidate.

## Legend crops (committed for audit)

`overlays/legend_key.png` is a crop of the map's legend box (raster px
≈ x[40–360], y[2300–3260], bottom-left of `maps/ingl_big_map_fullres.jpg`) kept for
audit. Route-anchor QC overlays: `overlays/zoom2_{tanin,karish,dor}.png` (each marker
hit dead-centre) and `overlays/retrace_karish.png` (full Tanin→Karish→Dor line).
