# Escalation — 14 Libya gas lengths carry a spurious miles→km conversion

**Date:** 2026-07-28 (ET) · **Tracker:** GGIT (gas) · **Scope:** Libya only, 14 rows
**Origin:** Libya gas deep sweep, `batches/libya-gas/staging/qc/` (Leg-3 research fan-out)
**Decision owner:** Baird · **Engine never auto-applies — this is a flag, not an edit.**

Companion memo: `notes/escalation-2026-07-28-scm-capacity-units.md`. Both defects come
out of the **same table** — OPEC ASB2012 Table 4.10 — and the same ingest, one in the
length column and one in the capacity column. They are written up separately because
they need different fixes and have different scope.

## The finding

OPEC ASB2012 Table 4.10 heads its length column **"(miles)"**. GEM's ingest took the
header at face value and multiplied by 1.609344 on the way in. That is correct for every
OPEC member in the table **except Libya**, whose block is tabulated in **kilometres**.
The result is 14 Libya gas rows whose `LengthKnownKm` is 1.609× the real length.

| PID | Pipeline | ASB2012 raw | ×1.609344 | GEM sheet | drawn route | route ÷ ASB | route ÷ sheet |
|---|---|---|---|---|---|---|---|
| P1856 | Intesar-Brega | 207 | 333.1 | **333.00** | 223.0 | 1.08 | 0.67 |
| P1857 | 103D-103A | 26 | 41.8 | **41.00** | – | – | – |
| P1859 | Bouri-Bahr Assalam | 20 | 32.2 | **32.00** | – | – | – |
| P1860 | Waha-Nasser | 110 | 177.0 | **177.00** | 69.9 | 0.64 | 0.39 |
| P1861 | Farigh-Intesar | 110 | 177.0 | **177.00** | 13.3 (stub) | – | – |
| P1862 | Brega-Benghazi | 246 | 395.9 | **396.00** | 225.9 | 0.92 | 0.57 |
| P1864 | Khoms-Tripoli | 125 | 201.2 | **201.00** | 105.2 | 0.84 | 0.52 |
| P1865 | Tripoli-Mellitah | 98 | 157.7 | **158.00** | 116.6 | 1.19 | 0.74 |
| P1866 | Nasser-Brega | 172 | 276.8 | **277.00** | 174.0 | 1.01 | 0.63 |
| P1867 | Attahaddy-km-91.5 | 25 | 40.2 | **40.00** | – | – | – |
| P1868 | Km-81.5-Brega | 82 | 132.0 | **132.00** | – | – | – |
| P1869 | Raguba-Km-110 | 88 | 141.6 | **142.00** | – | – | – |
| P1870 | Intesar-Sahel | 80 | 128.7 | **129.00** | – | – | – |
| P1871 | Sahel-km-81.5 | 49 | 78.9 | **79.00** | – | – | – |

Every one of the 14 matches `raw × 1.609344` to within 1 km. That is arithmetic, not
resemblance.

## Why the Libya block is kilometres and the rest of the table is miles

Four independent checks, two of which are controls from *outside* Libya:

1. **Qatar is the control that proves the header is normally honest.** ASB2012 lists the
   Dolphin line Ras Laffan→Abu Dhabi at 230. GEM converted it to 364.00 km — and 364 km
   is the well-documented real length of Dolphin. So for Qatar the tabulated figure
   genuinely *is* miles and GEM's conversion is *correct*. Same for Iraq (Baiji→Al-Qaim
   268 → 431 km, right for that route; 268 km would be far too short) and Saudi Arabia
   (Abqaiq→Yanbu 741 mi ≈ 1,193 km, the known East-West figure). **The ingest is not
   broken. One country's block in the source is.**
2. **Greenstream is the control inside Libya.** ASB2012 lists Mellitah/Gela at 540. The
   real Greenstream is ~520 km. 540 miles would be 869 km, which is impossible for a
   Mellitah→Gela crossing. So the Libya block's numbers are kilometres. GEM's P0439
   carries 520.00 km from another source and therefore escaped the defect — which is
   why the pattern went unnoticed.
3. **ASB2013 fixed it.** The same Greenstream row is listed at **334.8** in ASB2013 —
   334.8 × 1.609 = 538.7 ≈ the 540 that ASB2012 printed. OPEC converted the Libya block
   to genuine miles between editions. (Found by the `sirte-east` research agent; the
   ASB2012 side is verified directly from the Wayback PDF.)
4. **The drawn routes agree with the raw figures, not the sheet.** Of the 7 affected rows
   with usable geometry, 6 fall inside the 0.75–1.33 route-integrity band against the
   *unconverted* value and only 1 does against the sheet value. The sharpest case:
   P1864 + P1865 unconverted = 223 km, their drawn routes total 221.8 km, and World
   Bank / Tractebel give the combined Khoms→Mellitah run as 222 km.

## What this explains that was previously mis-diagnosed

- **P1860 / P1861 sharing `LengthKnownKm = 177.00` is not a GEM copy-paste.** ASB2012
  lists *both* Waha/Nasser and Faregh/Intesar at 110, so both converted to 177.0. The
  duplication is in the source. (I staged the copy-paste theory earlier in this batch;
  the `sirte-east` agent refuted it from the primary table and is right.)
- **Route-integrity `length_ratio` flags on these rows are mostly false positives** —
  they were firing because the *length* is wrong, not the route. That inverts the
  standing Libya reading that most `length_ratio` flags mean a schematic route. P1858
  and P1861 remain genuine route problems; the 14 above are length problems.
- **P1866's "wrong 277 km against a sourced ~172 km"** (redundancy cluster F) is this
  defect, not an independent error.

## Not covered by this explanation — do not fix these the same way

- **P1872 Km-91.5-Brega** (sheet 184, ASB 92) and **P1873 Jakhira-Intesar** (sheet 160,
  ASB 80) are each **exactly 2.00×** the ASB figure, not 1.609×. Different mechanism,
  unknown origin. Flagged, not diagnosed.
  - The `sirte-grid` agent proposed that both are dual-diameter rows (`36, 16` and
    `20, 8`) and may be summing two parallel pipes of the ASB length. Attractive, but
    **P1867 is also dual-diameter (`30, 12`) and shows the ordinary ×1.609**, so
    "parallel pipe" does not by itself separate the two groups. Left open.
- **P0484 Wafa-Mellitah** at 5246.00 is `raw × 10` — the separate decimal-shift error
  already on record.
- **P1855 / P1858 / P1863 / P6705 / P6709 / P6713 / P6714** carry the ASB figure
  *unconverted* and are fine on this axis. Whatever ingested them read the column
  correctly, which suggests the 14 and the 7 came in on different passes.
- **P1858's 131.96** deserves one look: it is exactly 82 × 1.609344, and 82 is
  *another row's* ASB figure (Km-81.5/Brega). ASB2012 gives Bu-Attifel/Intesar as 133.
  The practical difference is ~1 km, so this is a curiosity rather than a correction,
  but it hints the converting pass also mis-aligned a row.

## The citable source

    https://web.archive.org/web/20120722013100/http://www.opec.org:80/opec_web/static_files_project/media/downloads/publications/ASB2012.pdf

Verified: HTTP 200, and the file it serves is **md5-identical** (`0f45d36b…`, 7,711,852
bytes) to the PDF I extracted the table from. Table 4.10, Libya block, pp. 75–76. Use
this in place of the dead `opec.org` link currently sitting in these rows' `[ref]` cells.

Caveat for whoever re-verifies it: `scripts/url_verifier.py` returns OK on a generic
token ("OPEC") but FAILS on "Jakhira" — it does not read that deep into a 7.7 MB PDF.
That is a verifier limit, not a bad citation; confirm with `pdftotext -layout`. Noted in
the verifier's own docstring.

## What is already staged vs. what this memo is the only record of

Three separate research agents hit this pattern independently, from different corridors
and without being told about each other's findings — which is the main reason I am
confident it is real and not a coincidence of arithmetic.

**Seven are staged as ordinary fills** with their own verified refs in
`batches/libya-gas/staging/qc/rows/`. They appear in the handoff actions workbook and
can simply be applied:

| PID | staged value | ASB raw | tier | note |
|---|---|---|---|---|
| P1856 | 215 | 207 | high | agent found 215 from its own two sources, not the ASB figure |
| P1860 | 110 | 110 | high | |
| P1861 | 110 | 110 | high | |
| P1862 | 246 | 246 | high | |
| P1864 | 125 | 125 | medium | |
| P1865 | 98 | 98 | medium | |
| P1866 | 172 | 172 | medium | also corroborated by ASB's *oil* table 4.9, same corridor |

That six of seven landed on the ASB raw figure *from independent sources* is itself
corroboration that the raw figure is the real length.

**Six more are recorded only as `spec` validity concerns** — P1857 (from the
`sirte-east` agent), P1867, P1868, P1869, P1870, P1871 (from `sirte-grid`). Length was
not their assigned flag, so the agents correctly declined to stage a fill and filed a
"human should review this against the ASB figure" concern instead. They surface in the
handoff **evidence** workbook as open issues, not in the actions workbook as
paste-ready values. If the class ruling goes the obvious way, these are the rows that
still need converting into actual edits. The two ×2.00 outliers, **P1872 and P1873**,
are filed the same way and need the same conversion — but only after their different
mechanism is understood.

**P1859 Bouri-Bahr Assalam (32.00 vs ASB 20) is recorded nowhere.** It carried no QC
flag, so it was never in the Leg-3 worklist at all and no agent looked at it. This memo
is its only record.

## Recommended disposition

1. **Correct the 14 `LengthKnownKm` values to the ASB2012 raw figures** in the table
   above, and re-cite them to a verifiable Wayback ASB URL rather than the dead
   opec.org link currently on the rows.
2. **Re-run route integrity for Libya afterwards.** Most of the 12 flagged rows should
   clear, which changes the country's route-quality picture materially — do not
   downgrade `RouteAccuracy` on these rows before the lengths are fixed.
3. **Check the same 14 rows' capacity values** against the companion `scm` memo — same
   table, same ingest, and P1858 sits in both lists.
4. **Do not sweep other countries for this.** The Qatar/Iraq/Saudi controls show their
   conversions are correct; a blanket "un-convert ASB lengths" pass would introduce 
   errors where none exist. If another country is ever suspected, the test is the one
   used here: pick a row whose real length is independently well known and see which
   reading it matches.
5. Worth asking whether the ingest can record *which* ASB edition a value came from.
   ASB2012 and ASB2013 disagree on the units of the same Libya rows, so "OPEC ASB" alone
   is not a reproducible citation.
