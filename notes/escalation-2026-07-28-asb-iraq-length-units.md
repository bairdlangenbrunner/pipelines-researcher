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

> **All four rejections were later independently vindicated** (Leg-3 research,
> 2026-07-28) — worth recording, because a rejection is the easiest thing in an
> arithmetic match to get silently wrong. `P5856`: Al-Jibawi gives "76 km" verbatim, so
> the sheet value is *correct as it stands*. `P7435`: Al-Jibawi gives "40 km", likewise
> correct. `P6824`: turned out to be a **diesel** line that does not belong in GGIT at
> all (`escalation-2026-07-28-iraq-gasoil-misfiled.md`) — a second, stronger reason to
> exclude it. `P7457`: the sheet's 40.00 km **is** wrong, but not from this defect — KRG
> MNR states the pipeline is 30 km, and 40 km is what DNO and OGJ give as the *distance
> from field to plant*. So the "just a round number" instinct was right and the cause was
> something else entirely; see the length-provenance escalation in
> `batches/iraq-gas/staging/qc/`. **Zero of the four rejections was a false negative.**

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

**7. An independent Iraqi-government aggregate lands where the correction puts GEM.**
Recovered during the ref-gap re-pass: a 2013 JCCP seminar presentation by **Nihad A.
Moosa, Director General of the Iraqi Ministry of Oil's Oil Pipelines Company** — i.e.
the official responsible for the network — states Iraq's gas pipeline length as
`L.P.G = 1219 km And dry gas = 1088`, **≈ 2,307 km total**.

Compare GEM's matching cohort (Iraq, `Status = operating`, `StartYear1 ≤ 2013` or blank —
30 rows, 19 of them ASB-derived):

| GEM state | total | vs. the DG's 2,307 km |
|---|---|---|
| as the sheet stands today | 3,832 km | **+66%** |
| with this memo's 19-row length correction applied | 2,780 km | **+21%** |
| …and minus P4061's 600 km cluster-C double count | 2,180 km | **−6%** |

**Two independent escalations each move GEM toward a figure neither was derived from.**
The length correction closes two-thirds of the gap; removing the P4061 aggregate/segment
double count (`batches/iraq-gas/staging/redundancy/`, cluster C) closes almost all of the
rest. Neither fix was tuned to this number — the length fix comes from arithmetic and
route arbitration, the P4061 question from name/diameter overlap — so their landing
together on an official total is genuine convergent evidence.

> **Three caveats, stated rather than buried, because this is corroboration and not proof:**
> (a) the slide text is garbled and internally inconsistent in places (it is extracted
> from a presentation, and "L.P.G" vs "dry gas" is not a clean split of what GGIT models
> as gas transmission — see the P1853 note about that row being a *system* carrying both);
> (b) the cohort filter is approximate — treating blank `StartYear1` as pre-2013 and
> `operating` as the DG's in-service definition are both judgement calls, and a handful of
> rows could reasonably move either way; (c) ±6% agreement on a soft, round aggregate is
> not a precision match. What it does establish is **direction and magnitude**: GEM's Iraq
> gas network is currently ~66% too long, and the two staged corrections account for
> essentially all of it.
>
> Source: `http://web.archive.org/web/20231114092911/https://www.jccp.or.jp/international/conference/docs/s2-3_simminar_oil_final1_130307.pdf`
> (origin now 404s; Wayback snapshot 2023-11-14, 7.9 MB, read with `pdftotext` — another
> row of `url_verifier.py`'s large-PDF blind spot). The same deck independently sources
> P4061's own length: *"National dry gas 42\`\` is the main gas pipe line is length about
> 600km"* — note **"about"**, which is exactly why the trunk-vs-segment reading in
> cluster C matters. It also names a planned **52″ × 600 km "2nd National Gas P/L from
> North Rumail(a)"** that has no GGIT row — logged as a discovery lead in
> `docs/country_notes/iraq.md`.

**8. Named short hops arbitrate geographically, and they arbitrate for kilometres.**
The route-arbitration table above covers only the 7 of 19 rows that have drawn geometry.
For rows with no route, the ASB entry's own *place names* give an independent test:
where both endpoints are identifiable towns or plants, the real-world separation can be
compared with the raw integer and with the converted figure. Every case tested favours
the raw figure, and the short hops are the most decisive because a 1.609× error on a
40 km line is geographically absurd rather than merely wrong:

| ASB gas entry (Table 9.9, Iraq block) | raw | as miles → km | real-world separation | reads as |
|---|---|---|---|---|
| `Kirkuk/Baiji` | 90 | 144.8 | ~90 km | **km** |
| `Mishraq cross road/Mousil PWR St` (= P4067's sibling P4068) | 38 | 61.2 | ~38 km | **km** |
| `North Rumaila/Khor Al-Zubair gas dis station` | 54 | 86.9 | ~55 km | **km** |

A cross-table control in the same publication points the same way: ASB2017 **Table 6.9
(crude)** carries `(K3) Station/Iraqi-Syrian border  2 x 98`, and K3/Haditha to the
Syrian border is ~98 km, not ~158 km. So the kilometre reading is a property of **OPEC's
Iraq data**, not of the gas table alone — which is why a re-ingest of *either* table
would reintroduce the defect.

**Direct textual corroboration on one staged row.** `P4067` (Al-Ahdab→Al-Zubaydia,
ASB raw 73) is independently reported by Al-Jibawi at **76 km**. That agrees with the raw
integer to 4% and refutes the sheet's computed 117.48 km outright — the first of the 19
rows to be confirmed by a *source statement* rather than by arithmetic or geometry.

> Read this together with the P4067 classification note in `batches/iraq-gas/staging/qc/`:
> Al-Jibawi's 76 km line is described as **crude oil**, and OPEC lists the Ahdab corridor's
> crude and gas lines as separate rows in Tables 6.9 and 9.9. Whether the 76 km belongs to
> the same physical line as ASB's 73 km gas entry is unresolved and flagged there. For the
> *length* question it does not matter: either way the corridor is ~73–76 km, so 117.48 km
> is wrong on this row.

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

## Companion finding: the ASB *capacity* ingest is fine in Iraq (one row excepted)

> **SUPERSEDED IN PART, 2026-07-28.** This section is still correct about the **ASB**
> capacity ingest — Iraq's did not drop the `(1,000 scm/yr)` multiplier the way Libya's
> did. But its framing of P1841 as a lone exception no longer holds: the ref-gap re-pass
> found two more Iraq rows carrying a correct number under a wrong `CapacityUnits` label
> (P7477 ~98× high, P4041 ~35× high, both non-ASB rows), making this a **three-row class**
> with errors in *both* directions — so there is no blanket capacity fix either. Full
> analysis, including a tracker-wide screen that finds a worse non-Iraqi row:
> `notes/escalation-2026-07-28-iraq-capacity-units.md`.

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
