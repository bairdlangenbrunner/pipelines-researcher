# Egypt (oil + gas): 106 `[ref]` cells cite a mutable navigation surface, not a document

**Date:** 2026-08-27
**Scope:** Egypt, both trackers. Found during the 2026-08-27 oil ref sweep +
gas deep sweep (`batches/egypt-oil/staging/ref-sweep-all`,
`batches/egypt-gas/staging/deepsweep-20260827`).
**Status:** diagnosed, remedy staged, **sheet write NOT authorized and NOT performed.**

---

## 1. The defect

106 `[ref]` cells across 20 Egypt rows cite an `egyptoil-gas.com` **navigation
surface** instead of the article the value came from:

| tracker | URL cited | cells | rows |
|---|---|---:|---:|
| GGIT gas | `https://egyptoil-gas.com/?s=Gas+Pipelines+Egypt` | 65 | 14 |
| GOIT oil | `https://egyptoil-gas.com/reports_category/monthly/page/7/` (+ `/page/2/`) | 41 | 6 |
| | **total** | **106** | **20** |

Both are mutable. The first is a **site search-results page** — its content is
whatever the search engine returns today. The second is **page 7 of a paginated
category index**; every new monthly issue pushes the target article one slot
further down, so the cited page has already stopped containing the report it was
meant to point at. Neither is a document, neither is citable, and neither can be
re-checked by a future researcher.

`scripts/url_verifier.py` already catches this class and says so:

> *search/index page, not a document — cite the underlying article or report, not a mutable navigation surface.*

`scripts/ref_gap_worklist.py`, run independently over both staging dirs after the
fold, classifies **every single one** of its `NON_CITATION` gaps as one of these
two URLs (36 gas units, 31 oil units in the scoped worklists) plus the gem.wiki
self-citations noted in §5. No other URL contributes to that bucket.

**This is a citation-form defect, not a research gap.** The underlying document
exists, is live, is verifier-clean, and supports the values.

## 2. The document

**Egypt Oil & Gas Newspaper, September 2020, Issue 165 —
"Gulf of Suez, Eastern Desert and Sinai: Egypt's Crude Oil Squad"**, 4 pp.

`https://egyptoil-gas.com/reports/gulf-of-suez-eastern-desert-and-sinai-egypts-crude-oil-squad/`
→ `url_verifier`: `ok=True, status=200`.

It carries two tables that between them account for most of the values on the
affected rows — "Crude Oil Infrastructure in the Gulf of Suez/Sinai" (7 lines)
and "Natural Gas Infrastructure in the Gulf of Suez/Sinai" (7 lines), each giving
from / to / km / inches / capacity.

**The correct citation form is already in use on the same tab:** 69 gas cells
across 21 Egypt rows cite proper `egyptoil-gas.com/reports/<slug>` article URLs.
On P8013 the two forms sit **on one row** — its `Diameter [ref]` already carries
the article URL while its other five cells carry the search URL. So this is not a
convention that was never established; it is one that lapsed on a subset of rows.

## 3. What the document settled

Folded into staging this pass — **26 oil ref units + 15 gas ref units to
`REFS_ADDED`, plus 14 fills** (9 oil, 5 gas). Highlights:

- **Nine pre-existing orphan `[ref]` cells** on P7975–P7979 (StartLocation /
  EndLocation refs stapled to blank value cells) closed properly — re-staged as
  value+ref **fills**, not perpetuated as orphans.
- **P8084 `Diameter` = 10 in** — a value the sheet leaves blank entirely.
- **P8013 naming** — the source calls it **"Trans Gulf Gas"**, never "Trans
  Sinai". Staged as an `OtherEnglishNames` alias rather than a rename, because
  "Trans Sinai Gas Pipeline I" is a segment-numbered GEM family name shared with
  sibling rows.
- **Two existence concerns REFUTED** — see §4, the serious half of this note.

## 4. The reason this matters more than a URL cleanup: cross-leg agent blindness

In **seven** places, an agent in this run asked for precisely the document
another agent in the same run was already reading. Verbatim from their own notes:

| row | leg | what it asked for |
|---|---|---|
| P7975 | validity | *"chase an EGPC/PPC annual report or a specific egyptoil-gas.com article that actually names 'Ras Shukheir-El-Hafair'"* — the crude table names it |
| P7976/77/78 | refs | returned **all-UNRESOLVED** while the *validity* leg on the same rows had already found the article and recommended the swap |
| P7979 | validity | filed an **existence** concern — while the *refs* leg on the same row had already found and cited the article (the inverse direction) |
| P7341 | validity | *"the actual September 2020 egyptoil-gas.com report it originally pointed to (via a fixed article/PDF URL, not the paginated index)"* |
| P8084 | validity | *"find a document that actually names a 'Suez-Cairo ring'"* — the gas table lists `Suez-Cairo Ring, Suez → Cairo Ring, 150 km, 10 in` |
| P8018 | validity | three tests for a named "Suez-Port Said" line — the gas table lists `Suez-Port Said, Suez → Port Said, 160 km, 16 in` |

**Two of these produced recommendations to destroy real rows:**

- **P8084** — *"(b) drop/relabel the row as an unverified/GEM-only entry."*
  The source names the line and its 150 km matches the sheet **exactly**.
- **P8018** — *"downgrade to inferred/unsourced… or retire the row"*, or fold it
  into P8002's El-Tina/Abu Sultan family. The source names it and matches on
  name, both endpoints **and** diameter.

Both recommendations are now **WITHDRAWN** in staging, with the original text
preserved under `SUPERSEDED WITHIN THIS BATCH` so the reasoning stays auditable.

Neither agent was careless — both ran genuinely thorough searches (P8084 read
both GASCO wall maps pixel-by-pixel; P8018 applied all three of the tests this
cohort calls for, including the map test at native raster resolution). Both
simply tested the **wrong document**: the EGAS Annual Report 2018, which really
does not describe these lines. The finding they needed was sitting in a sibling
agent's context.

**This is the Uzbekistan lesson recurring** — *"the harvested pool is a worklist,
not a lookup table."* The new part is the failure mode: **findings do not
propagate across a fan-out**, so a document recovered by one agent is invisible
to every other agent in the same run, and an existence concern can be filed
against a row whose source is already in the batch's hands.

**Rule to adopt:** an `existence` verdict must be checked against the batch's own
accumulated sources before it is staged — a fan-out needs a reconciliation step,
not just a merge step. Concretely: no `existence` concern ships without first
grepping the run's other shards for the row's name and endpoints.

## 5. Two adjacent defects the same measurement exposed

- **Rule 1 is clean here — checked, not assumed.** Scanning every `[ref]` cell on
  all 173 Egypt rows across both tabs for `gem.wiki` / `globalenergymonitor.org`
  returns **0 cells**. (The gem.wiki URLs that appear beside these units in
  `gap_worklist.json` are each row's own `wiki` column, a legitimate GEM-internal
  field, not a citation. Worth stating explicitly because a URL tally across all
  of a unit's fields reads as if those pages were being cited — they are not.)
  All 31 oil `NON_CITATION` units are the paginated index URL, on the six rows
  P7341 and P7975–P7979.
- **A length pattern, not four separate errors.** This one document disagrees
  with four Egypt rows on length, and **in every case the sheet is longer**:

  | row | sheet | EOG | Δ | corroboration of identity |
  |---|---:|---:|---:|---|
  | P7341 Ras Shukeir–Asyut (oil) | 340 km | 280 km | −60 | diameter "20,22" exact |
  | P8016 Ras Shukheir–Suez | 256 km | 245 km | −11 | dia 16 **and** cap 160 exact |
  | P8018 Suez–Port Said | 165 km | 160 km | −5 | name, both endpoints, dia 16 exact |
  | P3659 Port Said–Arish *(out of scope)* | 235 km | 185 km | −50 | dia "36, 42" ↔ "36/42" |

  A consistent direction across four independent rows points at a **measurement
  convention** difference (EOG quoting point-to-point trunk length; GEM including
  spurs/laterals or as-built slack) rather than four unrelated mistakes. P7341's
  340 km is separately backed by a live Youm7 article of 2019-05-26 stating
  *"تم الانتهاء من تنفيذ خط من شقير حتى أسيوط بطول 340 كم"*, so at least that row
  is a genuine two-source conflict, not a transcription slip. **No length was
  changed.** Flag the delta, defer the recommendation — and settle it once for
  the family rather than row by row.

  Also unreconciled: SUMED system capacity 2,400,000 bbl/d in the source vs GEM's
  two segments summing 2,500,000 bbl/d; and P7979's 97,000 bpd, which the source
  leaves as "-" and nothing else corroborates.

## 6. One thing the document does NOT say

The ownership sentence reads: *"The SUMED has the biggest length (320 km),
diameter (42 inches) and capacity (2.4 mmbbl/d) among other crude oil pipelines,
**operated by the Petroleum Pipeline Company (PPC)**."*

The participial clause attaches to **SUMED alone**, not to the eight-line set.
It was deliberately **not** extended to the other rows, and no `Operator` /
`Owner [ref]` was staged from it. Recorded here because the sentence reads, at a
glance, like a blanket attribution for the whole table — and would be wrong.

## 7. Remedy — what is staged vs what needs authorization

**Staged (this repo, reviewable, no live writes):** all 41 ref-unit upgrades, the
14 fills, the two withdrawn existence concerns, the two new length concerns.

**Authorization-gated, NOT performed** — a live-sheet write of the 106 URL
corrections, swapping each navigation-surface URL for the article URL. It meets
the "mechanical and pre-verified" bar (one string replaced by one verified string,
no research judgment applied live), so it is a candidate for the authorized-write
path in CLAUDE.md — but it has not been asked for and has not been done.

Also still gated from earlier in this pass: P7338 (Oil/NGL **CV1210**), P5596
(Gas **F3114**), P3931's misplaced URL (**BQ1941**), and the 8 GASCO URL
corrections (P8055 ×7 + P6685).
