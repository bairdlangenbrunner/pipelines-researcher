# Escalation — Egypt gas, ten new `NA` rows (P8050–P8059): citation + length defects

**Date:** 2026-08-07
**Scope:** GGIT gas, Egypt, ProjectIDs P8050–P8059 (SheetRows 4311–4322), researcher
code **`NA`** — read from col J of `data/GGIT_gas_snapshot_20260807.csv`, not inferred.
**Raised by:** the §8 route-creation pass
(`batches/egypt-gas/archive/staging/route-creation-20260807/`), which required endpoint research
on every row and surfaced these as a side effect.
**Routing:** these are **Update-workflow** findings (source + value fixes). §8 detects,
Update fixes — nothing here was corrected on the sheet.

## Why this is an escalation and not ten separate notes

Two standing thresholds are met:

- ~~*"A whole class of GEM values looks systematically wrong."* Seven of the ten rows cite
  the **EGAS Annual Report 2018** and the report contains no line item for the pipeline in
  question, so the rows are effectively unsourced.~~ **WITHDRAWN 2026-08-10 — this finding
  was wrong.** See Finding 0. The citations are to the report's **GASCO national-grid map**
  (printed p.35), which the text-search approach could not see. The map carries per-segment
  `NN" NN km` annotations, and most of the cited rows transcribe theirs exactly. What
  survives is **one** value defect (P8051's bore) and one duplicate-check (P8050 vs
  P7567) — not a class-wide sourcing failure.
- *"A QC spot-check shows >10% of sampled cells unsupported."* Comfortably exceeded.

~~The pattern is not that the pipelines are fake — most are plausibly real — but that the
citations do not support the values attached to them, so the rows are effectively
unsourced.~~ **Withdrawn — see Finding 0.**

## Finding 0 — where EGAS 2018 is cited, and why the first read of it was wrong

**Correction (2026-08-10, on Baird's steer).** The researcher was reading the report's
**map**, not its prose tables: printed p.35 carries GASCO's *National Gas Grid* map, on
which each segment is drawn and most are annotated `NN" NN km`. Pipelines were identified
**visually off that map**. Every "the report does not contain this pipeline" conclusion in
the original memo came from `pdftotext` full-text search, which cannot read a raster map —
so it was answering the wrong question. The map is a legitimate source for `Location`,
and — because the legend distinguishes EXISTING / UNDER CONS. / UNDER STUDY p/l and the
annotations give bore and length — for `Status`, `PipelineType`, `Fuel`, `Diameter` and
`Length` too. Citing all six cells to it is defensible practice, not a defect.

Map evidence is committed alongside this batch at
`batches/egypt-gas/archive/staging/route-creation-20260807/maps/` (full p.35 render plus the four
region crops the table below rests on).

### Citation map

URL in every case:
`https://egyptoil-gas.com/wp-content/uploads/2019/01/EGAS-Annual-Report-2018-EN.pdf`

SheetRows are as of the **2026-08-10** snapshot — the gas tab was re-sorted between
08-07 and 08-10 and P8051 moved 4322 → 4313, so 08-07 locators are stale.

| PID | Row | Cells | Sheet | Map label (p.35) | Verdict |
|---|---|---|---|---|---|
| P8052 | 4314 | 6 | 45 km, 24" | `24" - 45 km`, Sinai Cement & Ind. Area | **exact — supported** |
| P8053 | 4315 | 6 | 16 km, 16" | `16" - 16 km`, Military Cement & Ind. Area | **exact — supported** |
| P8057 | 4319 | 6 | 25 km, 24" | `24" 25 k.m`, Mostorud→Tebbin corridor | **exact — supported** |
| P8054 | 4316 | 6 | 65 km, 36" | text p.37 *Dahshur / AlWaste 68.5 km - 36"*; map `24"/20" 65 km` near Dahshour | **supported** (also in the prose table) |
| P8050 | 4312 | 1 (`Location` only) | 29 km, 30" | `30" 27 k.m` at the Idku landfall | bore exact, 27 vs 29 km — but length/bore cite a Dec-2019 ministry page, not EGAS, so no conflict |
| P8051 | 4313 | 5 (no `Length`) | 65 km, 32" | `42" 65km` inside the stacked Abu Homos label bundle | length exact, **bore 42 ≠ 32** — probable mis-pairing across stacked labels |
| P8059 | 4321 | 6 | 75 km, 24" | `24" 75 km`, leader-lined from *Natgas* at Sidi Krir / Intergen P.S | **exact — supported** (see the decimal note below) |
| P8055, P8056, P8058 | — | 0 | — | — | do not cite it |

Six of the seven carry a map label whose **diameter matches the sheet exactly**, and four
match on length too — itself strong evidence that these cells were transcribed off the map
rather than invented.

**Decimal-point note (P8059, corrected 2026-08-10).** An earlier read of this label as
`24" 7.5 k.m` — and the consequent claim that the sheet's 75 km was a decimal misread — is
**withdrawn**. It came from a 600 dpi render of PDF page 19, but `pdfimages -list` shows the
map is an embedded raster of only **1811 × 2001 px at 200 ppi**, so that render upsampled
~3× and turned the black outline seam between two adjacent digits into a dot-like blob.
Re-cut from the native image (label at native px ≈ x 414–470, y 592–606) and compared
against a *known* decimal elsewhere on the same map, the reading does not hold: in
`12" 14.5km` the decimal is a **light** dot sitting in a gap about one digit-width wide,
whereas the mark between the 7 and the 5 is a **dark**, full-height seam identical to the
one between the 1 and the 5 of the neighbouring `24" 15km`. The label reads **75 km** and
therefore *agrees* with the sheet. Evidence committed as `maps/z_decimal_calibration.png`
(side-by-side) and `maps/z_sidikrir_natgas_label.png` (context).

### What actually survives

1. **P8051 diameter** — sheet 32", the 65 km map label reads 42". The Abu Homos bundle
   stacks six labels (`24" 45km`, `24" 45km`, `18/16" 13km`, `12" 14.5km`, `24" 15km`,
   `42" 65km`) over a shared corridor, so mis-pairing bore to length is an easy slip.
   Nearby 32" labels are `32" 200 k.m` and `32" 105 km` — neither is 65 km.
2. **P8050 vs P7567** — the prose table's *"Ezdwaj Edku / Abu Houmas pipeline 30 km - 42"*
   matches existing **P7567 "Idku-Abu Hummus Gas Pipeline" (30 km, 42 in)** exactly, and on
   the map "Rosetta" is an **offshore field** whose tie-back lands at Idku, not the Delta
   town of Rashid. So P8050's Rosetta→Abu Hummus may be the same physical line as P7567
   under a field-name reading of its origin. **Duplicate-check required.**

Also corrected: an earlier search reported "no Abu Hummus in the report". That was a
**false negative** — the token list was `Hummus/Homos/Hommos/Humus`; the report spells it
**"Houmas"** in prose and **"Abu Homos"** on the map.

### What the prose tables contain (for completeness)

15 line items on printed pp.35 and 37, verified visually as well as by extraction — the
blank-extracting PDF page 18 is a photographic section-title spread, not lost table rows.

- *Completed 2017/2018:* New Capital/Dahshur 70 km–32" · West Assiout PS 1.4 km–24" ·
  South Helwan 1.2 km–30" · 6 October 0.4 km–20" · Al Suez 3.5 km–16" ·
  Algameel/Damietta 50 km–42"
- *Under construction 2017/2018:* Dahshur/AlWaste 68.5 km–36" ·
  Ezdwaj Edku/Abu Houmas 30 km–42" · AlWaste/Beni Suef 60 km–36" ·
  Tina/Abu Sultan 92 km–42" (Ph1) · Abu Sultan/New Capital 73 km–42" (Ph2) ·
  Fayoum/Giza 27 km–24" · ELSLAAM/Matrouh 90 km–10" · Trans-Sinai 196 km–36" ·
  West of Cairo 16 km–30"

The prose tables cover only the two fiscal years' new-build and rehabilitation programme,
so a long-operating segment being absent from them says nothing about whether it exists —
another reason the original text-search inference did not hold.

## Finding 0b — WITHDRAWN 2026-08-10 (same day it was raised): the cement anchor was right

> **This finding is withdrawn in full.** It asserted that our §8 research had resolved
> "Sinia Cement Industrial Area" to the wrong plant — that the real one sits on the El
> Arish corridor while we had anchored to Sinai White Cement at El Hassana in central
> Sinai. Two independent checks say otherwise, and both point at the anchor we already
> used:
>
> 1. **OSM, Egypt-wide.** A name sweep returns exactly two Sinai cement works, and they
>    are neighbours in the Jabal Lubna quarry district, ~50 km inland: *Sinai White
>    Cement Factory* (33.7683, 30.7240) and *Al Arish Cement* (33.8487, 30.7008), with
>    industrial polygon way 97684492 (33.7765, 30.7242) between them. There is no cement
>    works at or beside El Arish town.
> 2. **The GASCO sheet's own captions.** Georeferencing the printed place labels off the
>    same Nov-2007 grid map (order-2 graticule fit) puts `Sinai` at (33.821, 30.759) and
>    `Cement` at (33.824, 30.705) — within 2–5 km of the OSM plants, and ~55 km south of
>    El Arish. The map agrees with OSM, not with this finding.
>
> The "El Arish town + offset south" arithmetic in the withdrawn table was reverse-derived
> from the 45 km length to make the ratio work; it was not evidence.
>
> **P8053 comes off the do-not-apply list.** Its 7.4 km plant-to-plant chord against a
> 16 km sheet length is ordinary winding for a quarry-district tie line.
>
> **What survives for P8052** is only the length ratio, and it is a smaller problem than
> stated: 63.0 km from Sheikh Zuweid *town* against 45 km on both the sheet and the map.
> The likely reading is that the take-off is a tie-in on the coastal/AGP trunk rather than
> the town centre — the map's own inland branch (trace g07-0088) leaves the coast at
> (33.949, 31.067) and runs 41.6 km to Sinai White Cement, which is what its `24" - 45
> k.m` label says. So P8052's *start* wants narrowing by ~20 km along the coast; its end
> is correct and its corridor is correct.
>
> Standing lesson, same as Finding 0's: check the map before ruling on a map-derived row.

## Finding 1 — length conflicts with the row's own endpoints

> **Revised 2026-08-10 (twice — read this, not the table).** Two entries below are artefacts
> of our own endpoint research, not sheet defects.
>
> - **P8052** — the ratio stands but the diagnosis in the first revision does not. Finding 0b
>   (wrong cement plant) is withdrawn; the end anchor is right and the *start* is the loose
>   one: the tap is a tie-in on the coastal trunk ~20 km west of Sheikh Zuweid town, which is
>   what the map's own inland branch shows. Corridor correct, length still unreconciled.
> - **P8053** — no length problem at all. Off the do-not-apply list.
> - **P8059** — our endpoints are wrong, not the length. No `7.5 km` label exists anywhere on
>   the georeferenced sheet (all 46 extracted labels checked), so 75 km stands, and a 14.1 km
>   Amreya → Sidi Krir chord is 5.3× too short for it.
> - **P8057** — 25 km is faithfully transcribed off the map, so this is the source disagreeing
>   with the geography rather than a transcription defect.
>
> **Do-not-apply is therefore obsolete as a blanket list.** Baird's 2026-08-10 instruction is
> that every Egypt row should carry at least a `very low (straight line/schematic)` route, and
> at that tier a schematic line whose *corridor* is right is exactly what the tier means. All
> four are re-staged in `route-creation-20260810` with the open question written into
> `ResearcherNotes`; **P8052/P8053 are now clean to apply**, and **P8057/P8059 apply only if a
> schematic placeholder ahead of the real corridor is wanted** — that is Baird's call, not a
> block.

Straight-line (great-circle) distance between the two endpoints each row names, versus
`LengthKnownKm` on that row. A real route can never be **shorter** than its own chord,
so a ratio > 1.0 is not "a bit off" — it is impossible as stated.

| PID | Named endpoints | Chord km | Sheet km | Ratio | Verdict |
|---|---|---|---|---|---|
| P8057 | Mostorod → El Tebbin | 40.8 | 25 | **1.63** | impossible as stated |
| P8052 | Sheikh Zuweid → Sinai Cement (Jabal Lubna) | 63.0 | 45 | **1.40** | start anchor too far east — see revision |
| P8059 | Al Amreya → Sidi Krir 3&4 (InterGen) | 14.1 | 75 | 0.19 (**5.3× overshoot**) | **endpoints** wrong — 75 km is map-confirmed |
| P8053 | Sinai Cement → Military Cement (Jabal Lubna) | 7.4 | 16 | 0.46 (2.17×) | high but possible |
| P8056 | Abu Qurqas → Asyut | 89.9 | 135 | 0.67 (1.50×) | see note |
| P8054 | Dahshur → El Wasta | 46.1 | 65 | 0.71 (1.41×) | see note |

Notes on the last two: P8056's stated overshoot (1.50×) is closely matched by its own
already-operating twin **P6700** (150 km vs the same ~90 km chord = 1.67×), and P8054's
length + diameter are independently corroborated twice (EGAS 2018 at 68.5 km, and
petro-news.com at exactly 65 km / 36 in). Both therefore read as **genuinely circuitous
Nile-valley corridors**, not wrong endpoints — flagged for awareness only.

P8057, P8052 and P8059 are the real problems and each has two possible fixes that we
cannot adjudicate from available sources: either the length is wrong, or the named
endpoint denotes a *tie-in/metering point* rather than the settlement/facility of that
name. Both need a source, not a guess.

## Finding 2 — P8057 `EndPrefecture/District` repeats `StartLocation`

P8057's end cell reads `Mostorud`, identical to its start. The row's Arabic
`OtherLanguagePrimaryPipelineName` (`خط غاز مستطرد-- التبين`) names **El Tebbin** as the
terminus. This is a copy-paste error, and it is the reason the row's length looked
self-consistent until the endpoints were resolved.

Separately: the row's cited ministry release
(`petroleum.gov.eg/.../mop_02052022_01.aspx`) was fetched and text-searched during this
pass — it contains **4** occurrences of ازدواج (duplication) and names دهشور / العاصمة /
أبوقرقاص / أسيوط, but **zero** occurrences of مسطرد (Mostorod) or التبين (El Tebbin). It
was therefore removed from P8057's proposed `Route [ref]` rather than carried as an
unsupported citation. P8057 has **no route-informing source** beyond its two endpoint
anchors, and no source at all establishing that the line exists.

## Finding 3 — P8058 is probably filed under the wrong pipeline family

`PipelineName` = "Dahshour-Cairo Gas Pipeline II", which reads as the sequel to existing
**P8040** "Dahshour-Cairo Gas Pipeline". But the row's **own Arabic name** and the seed
press release both put العاصمة (Capital) *before* دهشور — the word order of existing
**P3930** "New Administrative Capital–Dahshur Gas Pipeline", not P8040's. Geometry
agrees: against the stated 67 km, the New-Administrative-Capital reading gives a 55.7 km
chord (1.20×, normal), while the P8040-corridor reading gives 33.7 km (1.99×, worse than
P8040's own mapped winding factor of 1.73×).

So P8058 is most likely the **second line of the P3930 corridor**, mis-named as a sequel
to P8040. Needs human adjudication and probably a rename **before** any route is applied
— the staged candidate uses the NAC reading and says so. `Diameter` is also blank on
P8058, unlike P8040 (24, 20 in) and P3930 (32 in).

**Resolved on the sheet 2026-08-10:** `PipelineName` now reads "New Administrative
Capital–Dahshur Gas Pipeline II", i.e. the NAC reading the staged candidate assumed. The
staged geometry is therefore consistent with the row as it now stands. `Diameter` is
still blank.

## Finding 4 — P8055's name asserts a lineage the sources don't support

GASCO's own grid-expansion deck names this project **"Duplication of the Trans-Sinai
pipeline"** (28 km, 36 in, cost $13 M — the cost matches the row exactly). GEM's
`PipelineName` "Trans-Sinai Gas pipeline II" / `OtherEnglishNames` "Trans Gulf Gas
PipelineII" adds two claims the source does not make:

- **"Trans Gulf"** appears nowhere in the source, and no evidence was found of a
  Gulf-of-Suez or Suez Canal crossing. It looks like a mistranslation or an invention.
- **The "I"/"II" lineage is false.** GEM's existing **P8013** "Trans Sinia Gas Pipeline I"
  is a *different* pipeline: 12 in (vs 36 in), Petreco Plant → Ras Baker Transmission
  Station, Gulf of Suez — oilfield infrastructure, not a national-grid trunk. P8055
  should not be treated as its second phase.
- `EndState/Province` = "Suez" conflicts with GASCO's own location field, which reads
  "Sinai" only.

P8055 is the one row of the ten with **no route candidate** — it stays `ROUTE_PARTIAL`,
because the source gives no named endpoints for the 28 km duplicated stretch and
fabricating a pair was not an option.

## Finding 5 — P8052 and P8053 share one identical `PipelineName`

Both read "El Sheikhh Zowayed-Sinia Cement Gas Pipeline" while being different segments
(24 in / 45 km vs 16 in / 16 km, different endpoints). Functionally this is one
multi-leg line: Sheikh Zuweid → Sinai Cement → Military Cement. Either that is intentional
segment-per-PID granularity (fine) or they should share a `PipelineName` with distinct
`SegmentName`s under a network parent, as GEM does elsewhere. A data-model call, not a
research finding.

Note the row names are also transliteration-garbled — "Sheikhh", "Zowayed", "Sinia",
"Roseta" (P8050), "Mostorud" (P8057), "Ameriya-Intergen P.S " with a trailing double
space (P8059). Worth a normalization pass alongside the source fixes.

## Finding 6 — pre-existing anomalies in *neighbouring* rows (not `NA`'s)

Surfaced incidentally; out of scope for this batch, logged so they aren't lost:

- **P3929** "El Wasta–Beni Suef Gas Pipeline" carries `LengthKnownKm = 68.50`, which is
  exactly the EGAS-2018 figure for the **Dahshur–El Wasta** segment (i.e. P8054's line).
  The same report gives Al Wasta–Beni Suef as 60 km / 36 in. This reads as a length-value
  swap between adjacent segments. **Confirmed first-party 2026-08-10** by reading printed
  p.37 directly (`"AlWaste / Beni Suef pipeline 60 km - 36"`) — no longer second-hand.
- **P7567** "Idku-Abu Hummus Gas Pipeline" (30 km, 42 in, operating, `medium`) is the row
  the report's *"Ezdwaj Edku / Abu Houmas 30 km - 42"* item matches. Check **P8050**
  (Rosetta→Abu Hummus, 29 km, 30 in) against it for duplication before treating P8050 as
  a distinct line.
- **P6699** "Beni Suef–Abu Qurqas" and **P6700** "Abu Qurqas–Asyut" both carry exactly
  `150.00` km — an identical value for two differently-named segments.
- **P8056 vs P6700**: legitimately separate rows (P8056 is the announced twin/duplication
  of the operating P6700), but they should cross-reference each other, e.g. in RouteNotes.
- **P8057 vs P8021**: P8021 "Kuraimat–Al Tebbin Gas Pipeline" (87 km, operating) already
  terminates at El Tebbin from the south. Not a duplicate of P8057 (different origin and
  corridor), but worth a human cross-check that both lines are real and distinct.

## What was done, and what wasn't

**Done:** 9 candidate geometries + 1 `ROUTE_PARTIAL` staged in
`batches/egypt-gas/staging/route-creation-20260807/`, delivered as
`batches/egypt-gas/deliverables/pipelines_batch_20260807_1712_ET_egypt-gas_route-creation.xlsx`.
Every candidate's notes carry its own flags in full.

**Superseded 2026-08-10.** All ten rows were re-staged, with these corrections folded into
their notes, in `batches/egypt-gas/staging/route-creation-20260810/` →
`pipelines_batch_20260810_1800_ET_egypt-gas_route-creation.xlsx`, which covers all 34
routeless Egypt gas rows rather than these ten. The 08-07 staging dir and workbook are in
`batches/egypt-gas/archive/`.

**Not done — deliberately:** nothing was written to the live sheet or the routes repo.
No length, name, or citation was corrected.

**Apply guidance (final, 2026-08-10)** — the earlier blanket "do not apply" list is retired,
because Baird's floor for Egypt is now "at least a very low resolution route" and a schematic
line with the right corridor satisfies it:

- **P8052, P8053** — clear to apply. Finding 0b is withdrawn; the cement anchors were right.
  P8052 keeps a note that its coastal-trunk tap sits ~20 km west of Sheikh Zuweid town.
- **P8057, P8059** — apply only if a placeholder ahead of the real corridor is wanted. Both
  have a live unresolved fact (P8057: 25 km vs a 40.8 km chord, both defensible; P8059: 75 km
  map-confirmed against a 14.1 km chord, so the west-Alexandria end is wrong). Applying moves
  `RouteAccuracy` off `no route` for a row whose length is still in question — acceptable at
  `very low` if that trade is made knowingly, which is why it is stated here rather than
  decided here.
- **P8050, P8051, P8054, P8056, P8058** — unaffected by the 2026-08-10 corrections.

The **value** findings below (2–6) are untouched by any of this and still route to §5 Update.
