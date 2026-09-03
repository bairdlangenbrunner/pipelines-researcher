# PPIS "Energy Infrastructure Map - 2025" — a vector-PDF digitization

Page 6 of the **Investment Brochure 2025** published by Pakistan's **Directorate General
of Petroleum Concessions (DGPC)** through the **Pakistan Petroleum Information Service
(PPIS)** / LMK Resources. Source PDF is tracked in this directory; origin
`https://ppisonline.com/Brochure/Investment%20Brochure%202025.pdf` (28 pp, A4, retrieved
2026-08-26).

Rebuild the output with:

```bash
python sources/pakistan/prepare.py     # -> data/ppis-pipelines.geojson
python sources/pakistan/qc_render.py   # -> extraction/qc_{page_overlay,georeferenced}.png
```

Deterministic — same PDF in, byte-identical geometry out. `data/` is derived;
`extraction/` holds the tracked inputs and QC renders. The QC renders are derived too:
`qc_render.py` re-draws both from the current extraction (the overlay in page space
straight off `prepare.build_paths`, the map from the geojson), so a change to the
class dictionary or the dash logic is visible without a hand-made figure.

---

## What this is, and what it is not

The map is **vector art, not a raster**. `pdfimages -list` shows no image on the page
that carries the network, so the pipelines are recovered as the publisher's own drawn
coordinates — no raster tracing, no interpolation, no fabricated vertices. Every
coordinate in the output traces to a `get_drawings()` path item.

What that buys is *shape* fidelity, not *survey* fidelity. The drawing is a
publication schematic: it is topologically faithful (the right lines connect the right
places in the right order) and it is dimensionally close (see the validation table),
but individual vertices are draughtsman's approximations. Treat it as **corridor-level
evidence**, the same standing GulfPub, OSM and the Malaysian Gas Map have — a
Tier-3 reference that corroborates *where a line runs*, never a survey trace.

## Georeferencing

Lambert Conformal Conic, fitted to **57 city symbols at known real-world coordinates**
(`extraction/gcps.py`).

| | |
|---|---|
| median residual | **3.28 km** |
| mean residual | 5.93 km |
| p90 | 14.68 km |
| max | 21.80 km (Layyah) |
| bias | 0.00 km — none in either axis |

**The drawn graticule is NOT the control, and this matters.** The map carries a 1°
graticule (top 60–79°E, bottom 61–77°E, sides 20–36°N). Its labels are converted to
outlines and the bottom row is covered by the footer bar, so the tick values were
recovered analytically: only the hypothesis "bottom = 61→77°E" makes a top tick and a
bottom tick coincide, which pins the central meridian at 68°E. But fitting the
projection to those ticks leaves a **systematic +12.3 km north bias across the whole
map** (mean error 14.2 km), because the drawn left and right tick ladders disagree by
~1.6 pt in a way that contradicts conic parallel curvature. The graticule is decorative,
drawn to the neat-line rather than to the projection.

Fitting to city symbols instead removes the bias entirely — and then independently
recovers **λ₀ = 68.08°E and n = 0.437** against the graticule's own **68°E and 0.439**.
The two controls agree once the bias is out, which is what makes the fit trustworthy;
it is not merely the better-scoring option.

Model choice was leave-one-out cross-validated over affine / poly2 / poly3 / LCC /
equidistant-conic / Albers. LCC won (LOO mean 6.90 km vs affine 9.98). The remaining
residual is **not** a model deficiency — it is scattered, not structured, and at
1 pt ≈ 3.9 km on this page a 3.3 km median *is* sub-pixel symbol placement. A rubber-sheet
fit would only be interpolating the draughtsman's hand-placement noise.

One GCP is excluded: the **Skardu** square sits 2.3 pt from `SKARDU` but 3.2 pt from
`SATPARA`, and including it dragged n from 0.437 to 0.506 on its own. If you re-add it,
expect the graticule agreement above to disappear.

## Validation against published figures

Lengths were never fitted to anything — they fall out of the geometry, so the agreement
is a genuine external check on the georeference:

| Route | Extracted | Published | Δ |
|---|---|---|---|
| Iran–Pakistan (Pak. section) | 796 km | 781 km | +2% |
| TAPI (Pak. section) | 814 km | 774 km | +5% |
| Pakistan Stream / North-South | 1,089 km | ~1,100 km | −1% |
| PARCO crude Karachi→Mahmud Kot | 804 km | 864 km | −7% |
| White oil (WOP + MFM) | 1,131 km | ~1,179 km | −4% |
| SNGPL transmission network | 10,608 km | ~9,000–13,000 km | in range |
| SSGCL transmission network | 5,373 km | ~4,300–5,000 km | +7–25% |

Endpoints land where they should: IP begins at the Iran border at Gabd (61.62, 25.39);
TAPI enters at Chaman (66.48, 30.89) and exits toward Fazilka (73.88, 30.34); the white
oil line terminates at **Machike (74.028, 31.725)** against a real 74.02, 31.72.

SSGCL runs long because the map draws parts of its distribution system, not only
transmission — treat its network total as an upper bound.

## The class dictionary

Ten pipeline classes, named from the legend text, matched by the colour used **on the
map**. Legend swatches and map strokes drift slightly and consistently (legend crude
`(1.0,.6,.204)` vs map `(1.0,.522,.039)`; legend refined `(0,.659,.349)` vs map
`(.216,.839,.043)`), so: **legend text is the authority for the name, map colour for the
match.**

Solid lines are strokes. **No dashed line in this PDF carries a dash array** — every
drawing reports `dashes '[] 0'`, so a dashed line exists only as many separate
primitives, and there are **two** such encodings:

- **filled polygons** (~0.33 pt each) — the three import/trunk corridors, the legend
  swatches and the inset-scale dashes;
- **hairline strokes** (width 0.035 pt, ~0.46 pt long, period ~0.7 pt) — how every
  dashed line in the **map body** is drawn.

Both are reassembled into one LineString per dashed **run**, so no dashed pipeline is
emitted as a string of tiny fragments. The filled-polygon corridors reduce each dash to
its centroid and run a minimum spanning tree over the k-NN graph — MST rather than a
nearest-neighbour walk, because the corridors have spurs and a greedy walk hops across
them. The hairline marks are stitched end-to-end by union-find on their endpoints,
shortest link first, with a 60° collinearity gate against each mark's own axis and a
1.6 pt maximum gap (run counts are flat across 1.2–1.6 pt, so the threshold sits on a
plateau rather than on a cliff).

| class | features | km | source |
|---|---|---|---|
| `sngpl_gas_existing` | 278 | 10,608 | solid stroke `(1.0, 0.0, 0.008)` |
| `ssgcl_gas_existing` | 95 | 5,373 | solid stroke `(0.008, 0.2, 0.8)` |
| `sngpl_gas_planned` | 8 | 179 | 77 hairline dash marks, same colour |
| `ssgcl_gas_planned` | 13 | 352 | 149 hairline dash marks, same colour |
| `iran_pakistan_gas_planned` | 1 | 796 | 757 dash fills `(1.0, 0.0, 1.0)` |
| `tapi_gas_planned` | 2 | 814 | 670 dash fills `(0.0, 0.8, 1.0)` |
| `pakistan_stream_gas_planned` | 1 | 1,089 | 1,004 dash fills `(0.4, 0.2, 1.0)` |
| `crude_oil_existing` | 1 | 873 | solid stroke `(1.0, 0.522, 0.039)` |
| `refined_oil_existing` | 1 | 1,131 | solid stroke `(0.216, 0.839, 0.043)` |
| `oil_planned_uc` | 12 | 244 | stroke `(0.016, 1.0, 0.008)` — 10 solid + 2 stitched |

412 features, 21,460 km. Every feature carries `drawn_as` (`solid` | `dashed`) and, when
stitched from hairlines, `dash_marks_stitched`; the per-class mark/run/drop counts are in
the output's `ppis_extraction.dashed_lines` block.

Status is derived from the class name: `_existing` → `operating`, `_planned` → `proposed`.
**`oil_planned_uc` gets a BLANK status**, because its legend entry ("OIL PIPELINE UNDER
CONST./PLANNED") conflates two GEM statuses and the map offers nothing to break the tie.
A blank is the honest reading and means this source raises no `Status_Conflicts` for that
class — do not resolve it to one value to make the column look complete. `ingest.py`
reports it as `UNMAPPED status (12)`; that warning is expected, not a defect.

A network class is one feature **per branch between junctions**, which is why SNGPL is
278 features rather than one — that is the graph, not fragmentation. A **dashed** line is
the exception: it is one feature per dashed *run*, stitched whole.

### The operators' dashed lines are PLANNED, and stroke width is the only tell

The hairline dash marks sit in the **same colour and the same drawing type** as the
operators' solid EXISTING lines, so a colour-only classifier reads them as operating pipe.
The legend settles what they are: SNGPL and SSGCL each get a *solid* EXISTING entry and a
*dashed* PLANNED entry **in the identical colour** — solid-vs-dashed is the only
discriminator the map offers. So the stitched runs are emitted as `sngpl_gas_planned` /
`ssgcl_gas_planned` at `status = proposed`, not as `_existing`/`operating`.

What separates them mechanically is **stroke width**: dash marks are drawn at 0.035 pt,
every solid line at 0.141–0.493 pt. That is a clean two-order gap, but note the caveat —
the map body draws these dashes ~9× lighter than the legend's own dashed swatch, so the
assignment rests on *colour + dashedness*, not on matching the swatch's weight. Every
reclassified feature says so in its `description`.

Two marks-only leftovers, both recorded in `dashed_lines`, neither a coverage claim:

- **86 `ssgcl_gas_planned` filled marks** all fall inside the **HYDERABAD-BADIN inset**,
  which is at its own larger scale — dropped rather than reprojected through the
  main-map transform.
- **11 hairline marks** (4 SNGPL, 7 SSGCL) chain to fewer than 3 marks or under 1.5 pt.
  Emitting them would manufacture ~1.5 km phantom pipelines, so they are dropped and
  counted in `marks_dropped_unstitched`.

### The trap: field ellipses in pipeline colours

`(0.929, 0.196, 0.216)` fills (n=257) and `(0.341, 0.725, 0.325)` fills (n=152) are
**GAS FIELD and OIL FIELD symbols**, not dashed pipelines — and the first of those is
byte-identical to the legend's *SNGPL planned* swatch colour, so a colour-only match
puts 620 pt of field symbols into the gas network. They separate cleanly on **shape**:
field ellipses run aspect ≈ 2.0 at ≈ 1.0 pt, true dash marks aspect ≈ 1.3–1.5 at
≈ 0.33 pt. Their distribution is also diagnostic — they cluster on the Sindh field belt
and inside the Hyderabad-Badin inset, not along corridors.

Other non-pipeline classes in the same neighbourhood, recorded so they are not
rediscovered: `(0.137,0.588,0.929)`s rivers, `(1.0,0.0,0.0)`s power stations,
`(0.023,0.0,1.0)`s plant icon linework, `(0.929,0.18,0.22)`f the LoC / disputed-boundary
dotted line.

## Map annotations

155 on-map annotations carrying diameter and/or length were harvested
(`extraction/map_annotations.json`), e.g. `24"x132 KM, KADANWARI-N.SHAH`,
`16"x558 KM, INDUS LEFT BANK`, `26" PAPCO WHITE OIL PIPELINE`. Each feature gets the
nearest one within 6 pt as `nearest_text` / `label_diameter_in` / `label_length_km`,
with the gap in `label_gap_pt`.

**These are label-proximity artifacts and are unverified** — same standing as the
Malaysian Gas Map's labels. On a dense network a label sits near several branches, and
the nearest one is not necessarily its referent. Use them as a lead for a targeted
lookup, never as a sourced diameter or length. The annotation is genuine published
content; the *assignment* is ours and is a guess.

## Scope

- The **Karachi** and **Hyderabad-Badin** insets are excluded wholesale. Both are at
  larger scales; anything inside them needs its own fit.
- The statistics, legend, installed-capacity and energy-reserves panels are excluded.
- Coverage is Pakistan only — the map's Afghan, Iranian and Indian margins carry no
  network.
- **`oil_planned_uc` is the weakest class.** Its 12 features sit at Karachi, Mahmud Kot
  (PARCO) and Morgah (ARL) — all refinery locations, which is consistent with the legend
  name but also with short refinery-area connectors. Its legend swatch is *dashed* while
  10 of the 12 map features are *solid* (the other 2 are stitched from 9 hairline marks),
  so the class assignment itself is medium confidence.

## Standing-rule notes

The DGPC/PPIS brochure is an independent government-agency source — citing it does not
touch the never-cite-GEM rule. But it is **one source**: under the 2+-independent
corroboration rule, it reaches medium alone, and a GEM row it disagrees with routes to
Update's normal source search rather than being overwritten. As a reference route it is
presumptively **real pipe**: an unmatched trace here is either geometry GEM is missing or
a pipeline GEM is missing, and gets triaged by `disposition` like any other.
