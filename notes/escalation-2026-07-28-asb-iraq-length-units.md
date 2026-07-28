# Escalation — 19 Iraq gas lengths carry a spurious miles→km conversion

**Date:** 2026-07-28 · **Scope:** GGIT, Iraq, gas · **Ruling needed from Baird**
**Staged:** `batches/iraq-gas/staging/asb-length-units/staged_resolutions.json`
(19 `__VALIDITY__` records, `concern_type: spec`)

## The claim

OPEC's *Annual Statistical Bulletin* gas-pipeline table (Table 4.10 in ASB2012,
Table 9.9 in ASB2017) heads its length column **"(miles)"**. **The Iraq block is
tabulated in kilometres.** GEM's ingest converted anyway, so **19 Iraq gas rows are
1.609344× too long**.

This is the same defect already documented for Libya
(`notes/escalation-2026-07-28-asb-libya-length-units.md`) — but see **Correction**
below, because that memo used Iraq as a *control proving the ingest correct*. That
control is wrong, and Iraq is worse than Libya: OPEC fixed Libya in ASB2013 and
**never fixed Iraq**.

## Evidence

**1. Arithmetic, not resemblance.** All 19 rows resolve to `ASB raw × 1.609344`
kilometres. Two distinct sub-families, and they got there by **different mechanisms** —
which matters because it means they need different fixes:

| family | rows | how the sheet holds it | signature |
|---|---|---|---|
| `P18xx`/`P22xx` (13) | ASB2012-era | `LengthKnown` = the **converted** figure, `LengthKnownUnits` = `km` | product **rounded to whole km** (431, 211, 56, 39, 72, 37, 77, 216, 470, 145, 34, 438, 87) |
| `P40xx` (6) | ASB2017-era | `LengthKnown` = the **raw ASB integer**, `LengthKnownUnits` = **`mi`** | the sheet's own formula emits 40.23, 119.09, 80.47, 46.67, 117.48, 61.16 |

For the 13, someone multiplied on the way in and stored kilometres.

For the 6, **nobody converted anything** — the ingest wrote the ASB integer verbatim
and simply believed the column header, tagging it `mi`. `LengthKnownKm` is a computed
column (`LengthKnown` converted per `LengthKnownUnits`), so the sheet's own formula
produced 40.23 from `25 mi`. Those decimals are the spreadsheet's arithmetic, not an
ingest artefact.

> **CORRECTED 2026-07-28.** This item originally read the `P40xx` decimals as evidence
> of "a second, decimal-retaining ingest pass" and concluded "two separate ingest
> passes, years apart, both applied it." That is wrong: only one pass ever applied a
> multiplication. The `P40xx` rows are a **unit-label** error, and their stored numbers
> are already correct. The staged records were re-targeted accordingly — see
> **Which rows are staged** below.

**2. Diameter corroborates the row match.** Every one of the 19 matches its ASB row on
diameter as well as on the length quotient — an independent attribute from the same
table row. This is what separates the real hits from coincidence: four rows whose
length quotient landed near an ASB value were **rejected** because neither diameter nor
name agreed (`P5856` Gharraf 76 km/20″, `P6824` Shouibah 46 km/8-10″, `P7435` Khor
Al-Zubair-Shatt Al Arab 40 km/42″, `P7457` Semel-Duhok 40 km/36″ — 40.00 km is simply a
round number).

**3. Drawn routes arbitrate, 6–0.** Of the 19, seven have drawn geometry. Six agree with
the **raw** value and **none** with the sheet value:

| PID | sheet km | ASB raw | drawn km | drawn/sheet | drawn/raw |
|---|---|---|---|---|---|
| P1841 | 431.0 | 268 | 224.9 | 0.52 | 0.84 |
| P1842 | 211.0 | 131 | 108.1 | 0.51 | 0.83 |
| P1845 | 56.0 | 35 | 33.7 | 0.60 | **0.96** |
| P1850 | 77.0 | 48 | 51.2 | 0.66 | **1.07** |
| P1851 | 216.0 | 134 | 141.9 | 0.66 | **1.06** |
| P4067 | 117.5 | 73 | 66.9 | 0.57 | **0.92** |
| P2234 | 87.0 | 54 | 33.1 | 0.38 | 0.61 |

**4. Physical sanity.** Baiji→Al-Qaim (P1841) is ~225 km great-circle. The raw 268 km
is a normal routing allowance over that; the converted 431 km would be 1.9× the
great-circle, implausible for a straight desert trunk. The drawn route measures 224.9 km.

**5. GEM's own wiki pages state the misreading outright.** The wiki-alignment leg
(Leg 1) found that all 13 ASB2012-family pages render the length as a dual value whose
"miles" half is *exactly the ASB integer*:

```
P1841  sheet 431.0   wiki "431 km / 268 miles"
P1842  sheet 211.0   wiki "211 km / 131 miles"
P2233  sheet 438.0   wiki "438 km / 272 miles"
P1852  sheet 470.0   wiki "470 km / 292 miles"      (…13 of 13)
```

So the ingest's interpretation is not inferred — it is written down: the ASB figure was
taken as miles and converted. (The wiki is *visited* for this diff and never cited as a
source; this is internal-provenance evidence about a GEM ingest, not a reference.) The
six `P40xx` rows carry no such dual rendering, which is consistent with them coming
from the later, decimal-retaining pass.

**6. OPEC never corrected Iraq.** ASB2017 Table 9.9 still prints the Iraq block as
`131 / 268 / 90 / 21 / 48 / 272 / 54 / 134 / 23 / 45 / 24 / 35 / 29 / 74 / 50` —
byte-identical integers to ASB2012 — while the **Libya** block in the same table now
carries genuine-mile decimals (Brega/Al Khums 399.9, Brega/Benghazi 152.52,
Intisar/Zueitina 136.4). OPEC converted Libya and left Iraq alone. **Any future
re-ingest of the Iraq block will reintroduce this.**

## Proven scope, and the controls that prove it

The defect is **per-country in the source**, not a blanket ingest bug. Tested both
directions:

| block | reading | evidence | verdict |
|---|---|---|---|
| **Iraq** | **kilometres** | 19 rows, 6–0 route arbitration | ✗ **defect** |
| **Libya** (ASB2012) | **kilometres** | 14 rows — the Libya memo | ✗ defect |
| **Qatar** | genuine miles | Dolphin 230 → 370 km; real ~364 km | ✓ ingest correct |
| **Saudi Arabia** | genuine miles | Abqaiq/Yanbu 741 → 1193 km; real ~1200 km | ✓ ingest correct |
| **UAE** | genuine miles | Habshan/Maqta 81 → 130 km; real ~125 km | ✓ ingest correct |
| Iran, Algeria, Nigeria | genuine miles | printed with 2–4 decimals (685.4042, 24.24, 27.83872) = OPEC's own km→mi conversion | ✓ ingest correct |

**A blanket fix would corrupt Qatar, Saudi and UAE.** Fix Iraq and Libya only.

Note the tempting-but-invalid shortcut: *"integer values mean kilometres."* It fails —
Qatar, Saudi and UAE blocks are also plain integers and are genuinely miles. The test
has to be empirical per country (route/independent length), not typographic.

## Which rows are staged, and which are memo-only

**All 19 are staged** — nothing here is memo-only. They are staged as
`__VALIDITY__` / `concern_type: spec` records, **not** as fills, because each targets a
*populated, published* value; per the standing rule a reference value is never
auto-applied. Each record carries the exact proposed value and a one-line
`recommendation`, so applying is one step once you rule.

**Apply the right cell — the two families differ, and only one of them needs the number
changed:**

| family | edit | leave alone |
|---|---|---|
| 13 rows `P18xx`/`P22xx` | `LengthKnown` → the ASB figure | `LengthKnownUnits` (already `km`) |
| 6 rows `P40xx` | `LengthKnownUnits` `mi` → **`km`** | `LengthKnown` — **already correct** |

`LengthKnownKm` and `LengthMergedKm` are **computed columns — never paste over them.**
Both fixes above correct `LengthKnownKm` automatically.

> **CORRECTED 2026-07-28.** The staged records originally proposed a value for
> `LengthKnownKm` on all 19 rows. That named a formula cell, and for the six `P40xx`
> rows it would have been actively wrong: `LengthKnown` would still have held the ASB
> integer tagged `mi`, so the sheet would have re-derived the inflated figure on the
> next recalc and the fix would have silently reverted. Re-targeted by
> `batches/iraq-gas/staging/asb-length-units/retarget_editable_cells.py` (idempotent).

| | rows |
|---|---|
| Staged, route-confirmed | P1841, P1842, P1845, P1850, P1851, P4067 |
| Staged, arithmetic + diameter only (no drawn route) | P1846, P1847, P1848, P1852, P2231, P2232, P2233, P4062, P4064, P4065, P4066, P4068 |
| Staged, but **neither** value fits its route — needs a look | P2234 |

Two per-row caveats, flagged rather than buried:

- **P2234** (North Rumela/Khor Al-Zubair): drawn route 33.1 km fits neither 54 nor 87.
  Most likely a partial route. The unit correction still stands on arithmetic +
  diameter (42″ matches exactly); the route is a separate problem.
- **P2231** (North Gas/Baiji): raw 90 km is slightly *under* the ~101 km Kirkuk–Baiji
  great-circle, which would be impossible if the endpoints are the two cities. The
  ASB2012 row is named "North Gas/Baiji" (a plant, not Kirkuk city) and ASB2017
  renamed it "Kirkuk/Baiji", so the endpoint is probably the North Gas Company plant.
  Confirm the origin before applying this one.

## Correction to the Libya memo

`notes/escalation-2026-07-28-asb-libya-length-units.md` asserts *"Same for Iraq
(Baiji→Al-Qaim 268 → 431 km, right for that route; 268 km would be far too short)."*
**That is refuted.** Baiji→Al-Qaim is ~225 km great-circle and P1841's own drawn route
measures 224.9 km, so 268 km is right and 431 km is far too long. The Libya memo's
Qatar and Saudi controls are unaffected and still hold. That memo has been corrected
in place.

## Companion finding: the capacity column is *fine* in Iraq (one row excepted)

Worth stating because it isolates the defect to length. Libya's ASB capacity ingest
dropped the `(1,000 scm/yr)` multiplier; **Iraq's did not** — 11 of 13 ASB2012 rows
carry the correct bcm/y (P2231 0.89, P2232 5.26, P1845 2.00, P1846 0.67, P1847 0.70,
P1848 2.10, P2234 10.00, P1850 4.80, P1851 10.42, P1852 11.03). Exceptions:

- **P1841 — unit mislabel.** `Capacity = 2.41` tagged `MMcf/d`; ASB gives 2,410,000
  (1,000 scm/yr) = **2.41 bcm/y**. The number is right, the unit is wrong, so the
  computed `CapacityBcm/y` reads **0.02** instead of 2.41 — ~120× low. Fix
  `CapacityUnits` to `bcm/y`; do not touch the value.
- **P1842 (160 MMcf/d → 1.64) and P2233 (150 MMcf/d → 1.53)** disagree with ASB (7.4
  and 3.087 bcm/y). Both carry an `iraqenergy.org` capacity ref — they were
  deliberately re-sourced, so this is an ordinary two-source value conflict, not a
  unit bug. Left to normal Update triage.

## Sources

- ASB2012 (Table 4.10, Iraq block, p. 75) —
  `http://web.archive.org/web/20250110032615/https://opec.org/opec_web/static_files_project/media/downloads/publications/ASB2012.pdf`
- ASB2017 (Table 9.9, Iraq block) —
  `http://web.archive.org/web/20250206233526/https://www.opec.org/opec_web/static_files_project/media/downloads/publications/ASB2017_13062017.pdf`

Both return HTTP 206 `application/pdf` on a ranged fetch. **`url_verifier.py` cannot
validate either** — they exceed its large-PDF limit (already noted for ASB2012); the
table text was extracted locally with `pdftotext` and read directly.
