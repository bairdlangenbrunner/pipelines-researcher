# Escalation — Egypt gas, ten new `NA` rows (P8050–P8059): citation + length defects

**Date:** 2026-08-07
**Scope:** GGIT gas, Egypt, ProjectIDs P8050–P8059 (SheetRows 4311–4322), researcher
code **`NA`** — read from col J of `data/GGIT_gas_snapshot_20260807.csv`, not inferred.
**Raised by:** the §8 route-creation pass
(`batches/egypt-gas/staging/route-creation-20260807/`), which required endpoint research
on every row and surfaced these as a side effect.
**Routing:** these are **Update-workflow** findings (source + value fixes). §8 detects,
Update fixes — nothing here was corrected on the sheet.

## Why this is an escalation and not ten separate notes

Two standing thresholds are met:

- *"A whole class of GEM values looks systematically wrong."* **Seven of the ten rows**
  cite the **EGAS Annual Report 2018** across **36 `[ref]` cells**, and for **six of those
  seven** the report contains **no line item for the pipeline in question** — see the
  citation map below. Three independent subagents reached this separately, each using
  `pdftotext -layout` over both the live file and its Wayback snapshot, searching the
  report's own "COMPLETED DURING 2017/2018" and "UNDER CONSTRUCTION" grid tables;
  re-verified 2026-08-10 by rendering the pages and reading them visually.
- *"A QC spot-check shows >10% of sampled cells unsupported."* Comfortably exceeded.

The pattern is not that the pipelines are fake — most are plausibly real — but that
the **citations do not support the values attached to them**, so the rows are
effectively unsourced.

## Finding 0 — citation map: exactly where EGAS 2018 is cited

URL in every case:
`https://egyptoil-gas.com/wp-content/uploads/2019/01/EGAS-Annual-Report-2018-EN.pdf`

SheetRows are as of the **2026-08-10** snapshot — the gas tab was re-sorted between
08-07 and 08-10 and P8051 moved 4322 → 4313, so 08-07 locators are stale.

| PID | SheetRow | Cells | Which | Supported by the report? |
|---|---|---|---|---|
| P8050 | 4312 | 1 | Location | **No** — no Rosetta line item (its other 5 refs are a Dec-2019 ministry page, not EGAS) |
| P8051 | 4313 | 5 | Status, Fuel, PipelineType, Diameter, Location | **No** (`Length [ref]` is World Bank RP1184, not EGAS — hence 5, not 6) |
| P8052 | 4314 | 6 | Status, Fuel, PipelineType, Length, Diameter, Location | **No** — no North Sinai line item at all |
| P8053 | 4315 | 6 | " | **No** — same |
| P8054 | 4316 | 6 | " | **YES** — see below |
| P8057 | 4319 | 6 | " | **No** — no Mostorod / El Tebbin anywhere |
| P8059 | 4321 | 6 | " | **No** — no Ameriya / Sidi Krir / InterGen anywhere |
| P8055, P8056, P8058 | — | 0 | — | (do not cite it) |

**P8054 is legitimately sourced and must come off the unsupported list.** Printed p.37:
*"Dahshur / AlWaste pipeline 68.5 km - 36"*, under construction 2017/2018, target
September 2018, cost 277.5 million L.E + 13.4 million US$. Diameter matches exactly;
68.5 km vs the row's 65 km, which petro-news.com independently gives as 65.

**Correction to an earlier search result.** The first pass reported "no Abu Hummus in
the report"; that was a **false negative** — the token list was
`Hummus/Homos/Hommos/Humus` and the report spells it **"Houmas"**. Printed p.37 does
carry *"Ezdwaj Edku / Abu Houmas pipeline 30 km - 42"*. That item matches existing GEM
row **P7567 "Idku-Abu Hummus Gas Pipeline" (30 km, 42 in)** exactly — not P8050
(Rosetta→Abu Hummus, 29 km, 30 in) nor P8051 (Abu Hummus→Nubaria, 65 km, 32 in), so the
unsupported verdict on those two stands. But `Ezdwaj` = ازدواج = *duplication*, and 30 km
vs P8050's 29 km is close: **P8050 needs a duplicate-check against P7567** before it is
treated as a distinct line.

### What the report does contain

The entire grid-pipeline content is 15 line items on printed pp.35 and 37 (PDF pages
19–20), verified visually as well as by extraction — the blank-extracting PDF page 18 is
a photographic section-title spread, not lost table rows.

- *Completed 2017/2018:* New Capital/Dahshur 70 km–32" · West Assiout PS 1.4 km–24" ·
  South Helwan 1.2 km–30" · 6 October 0.4 km–20" · Al Suez 3.5 km–16" ·
  Algameel/Damietta 50 km–42"
- *Under construction 2017/2018:* Dahshur/AlWaste 68.5 km–36" ·
  Ezdwaj Edku/Abu Houmas 30 km–42" · AlWaste/Beni Suef 60 km–36" ·
  Tina/Abu Sultan 92 km–42" (Ph1) · Abu Sultan/New Capital 73 km–42" (Ph2) ·
  Fayoum/Giza 27 km–24" · ELSLAAM/Matrouh 90 km–10" · Trans-Sinai 196 km–36" ·
  West of Cairo 16 km–30"

The only element that could loosely justify a `Location [ref]` for an unlisted Delta line
is the GASCO national-grid **map** on p.35 — it is not row-specific and does not carry
length, diameter, status or type.

## Finding 1 — length conflicts with the row's own endpoints

Straight-line (great-circle) distance between the two endpoints each row names, versus
`LengthKnownKm` on that row. A real route can never be **shorter** than its own chord,
so a ratio > 1.0 is not "a bit off" — it is impossible as stated.

| PID | Named endpoints | Chord km | Sheet km | Ratio | Verdict |
|---|---|---|---|---|---|
| P8057 | Mostorod → El Tebbin | 40.8 | 25 | **1.63** | impossible as stated |
| P8052 | Sheikh Zuweid → Sinai Cement (El Hassana) | 63.0 | 45 | **1.40** | impossible as stated |
| P8059 | Al Amreya → Sidi Krir 3&4 (InterGen) | 14.1 | 75 | 0.19 (**5.3× overshoot**) | length or endpoints wrong |
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

**Not done — deliberately:** nothing was written to the live sheet or the routes repo.
No length, name, or citation was corrected. **P8057, P8059 and P8052 should not have
their route applied until their length question is settled** — applying them would move
`RouteAccuracy` off `no route` for rows whose geometry is known to contradict their own
`LengthKnownKm`, which is how a defect gets laundered into a "mapped" row.
