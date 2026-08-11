# Leg-3 research protocol — India gas handoff QC

You are resolving flagged disagreements on a set of GEM gas-pipeline rows that share a
**source ladder**. Your brief (`rows/_briefs/<key>.json`) carries 3–7 rows, each with
its current sheet values, its flags verbatim, and the geometry measured in Leg 2.

Read the brief's `source_ladder` field first — it names the documents most likely to
answer YOUR rows, and often records what the prior legs already established, so you do
not re-derive a settled point.

`$S` below = `batches/india-gas/staging/qc`.

## READ THIS FIRST — the sourcing situation in India

India is the **inverse of Pakistan**. Pakistan's rows came from a bulk map load with no
text behind them, so research had nothing to grip. India's rows are actively maintained,
coherent and real — what they lack is **citations**. Refs sit on roughly 9% of ref cells
(149 of 1,650), and 34 of 35 operating rows carry no PNGRB reference at all even though
PNGRB is demonstrably where their numbers came from.

**So your default expectation is that a source EXISTS and has simply never been cited.**
An `UNRESOLVED` here is a weaker result than it was in Pakistan. Dig before you give up.

**The unlock is the PNGRB NGPL MIS register:**

> `https://pngrb.gov.in/data-bank/20260531-NGPL-MIS-Report.pdf`

A monthly line-wise register of every authorised common-carrier gas pipeline, in three
sections — OPERATIONAL, PARTIALLY COMMISSIONED, UNDER CONSTRUCTION — with authorised /
operating / under-construction length, authorised and design capacity in MMSCMD,
authorisation date, target completion and states traversed. It is already parsed at
`scripts/parse_pngrb_ngpl_mis.py`, and a crosswalk of it against the GEM rows is staged
at `batches/india-gas/staging/register-crosswalk/staged_resolutions.json` — **read that
crosswalk for your PIDs before searching**, so you build on it instead of repeating it.

Three things about the register that will save you time:

1. **It is a TIME SERIES, and diffing editions is dispositive.** Older editions live at
   `https://www.pngrb.gov.in/data-bank/NGPL-<DDMMYYYY>.pdf` and `.../NGPL-<YYYYMMDD>.pdf`
   (e.g. `NGPL-25062021.pdf`, `NGPL-20240626.pdf`). Authorisation number, sponsor and
   authorisation date stay FIXED across editions while the project NAME changes — so two
   differently-named GEM rows sharing an authorisation number are one authorisation, and
   that beats any argument from name similarity.
2. **It names the AUTHORISATION HOLDER, which is the owner** — often, but not always,
   also the operator. When you cite it for an operator, say which one it establishes.
3. **`url_verifier` FAILs on it** — it is a large PDF and the substring check cannot see
   inside. That is a documented false negative, not a dead link. Download it and read it
   with `pdftotext -layout`, then say in `researcher_notes` that you confirmed the value
   locally. The same applies to PNGRB amendment letters, which are frequently image-only
   scans with **no text layer at all** — render those to PNG and read them rather than
   concluding the document does not support the value.

Other PNGRB surfaces worth knowing: per-project authorisation and amendment letters under
`/pdf/ngp/Govt-Authorization/`, bid route maps at
`/pdf/ngp/bid/bid<N>/Map-<CODE>-Bidding.pdf` (the maps carry a text layer giving endpoints
and intermediate towns), and ERDMP audit reports under `/pdf/ngp-audit-report/`.

## Standing rules (non-negotiable)

1. **NEVER cite** gem.wiki / globalenergymonitor.org / A Barrel Full / any
   `wikidot.com` page. The gem.wiki infobox is what RAISED most of your Operator flags —
   read it for leads, never as a `[ref]`.
2. **NEVER fabricate a URL.** If nothing verifies, mark `UNRESOLVED` and say what you
   tried. An invented citation is the one unrecoverable error.
3. **Verify EVERY url before citing:**
   `python scripts/url_verifier.py "<url>" "<expected substring>"` — cite only if
   OK/200 AND it contains the expected token (a distinctive number, place or name).
   Try Wayback (`https://web.archive.org/web/2023/<url>`) for dead originals.
   **Verifier false negatives are real:** prose and equivalent units count ("commissioned
   in 1998" supports `StartYear1 = 1998`; "6 BCM annually" supports 6 bcm/y). Never
   declare a source unsupported off a substring miss without reading the passage and
   quoting it. If a URL fails on SSL/TLS but `curl -sI` returns 200, it is LIVE — say so.
4. **Corroborate with ≥2 INDEPENDENT sources** where possible (separate origins; not one
   wire story reprinted; nothing tracing back to GEM). `tier`: `high` = ≥2 independent
   working + value-present; `medium` = 1 strong; `low` = 1 weak/partial/conflicting.
   Note that PNGRB is the de facto ORIGIN of many GEM numbers, so a PNGRB citation plus a
   company report repeating the same authorised figure may be one origin, not two — say
   so rather than claiming `high` on a shared lineage.
5. **No orphan refs, no orphan values.** Never propose a `[ref]` without the value it
   supports, and never propose a value without a ref.
6. **Search Indian sources, not just English majors.** Company **annual reports** are the
   most productive family here, and Indian listed companies publish detailed ones: GAIL
   (gailonline.com), GSPL (gspcgroup.com / gspl.co.in), IOCL, ONGC, Petronet LNG,
   Pipeline Infrastructure Ltd, Gujarat Gas, IGGL, Assam Gas. Then the regulator and
   ministry: PNGRB (pngrb.gov.in), MoPNG and its Indian Petroleum & Natural Gas Statistics
   (mopng.gov.in), PPAC (ppac.gov.in), and the **Comptroller & Auditor General**
   (cag.gov.in) — CAG performance audits contain operational detail no press release does,
   and one already settled the HUT/MUT question in this pass. Then trade and business
   press: Business Standard, The Hindu BusinessLine, Economic Times Energy, Mint,
   Financial Express, Moneycontrol, Pipeline & Gas Journal, Oil & Gas Journal, S&P Global.
   Hindi and regional-language state-government sources are fair game and count as
   independent — set `source_language` accordingly.
7. **A flagged disagreement is a question, not a verdict.** Decide which side is wrong,
   with evidence, and say which you decided.

## The flag types you will see

- **`Operator` (39 rows — the big one).** The sheet's `Operator` cell (on the separate
  ProjectID-keyed operators/owners tab) is blank while gem.wiki names one. India records
  an operator on exactly ONE of its 75 gas rows, against 794 of 4,356 (18.2%) across the
  GGIT gas tab — so this is a genuine India gap, not the tracker norm, and it is worth
  real effort. **This is one question per COMPANY, not per row:** whoever operates GAIL's
  HVJ system operates all five of its segments, so answer once and apply it across your
  brief, saying explicitly that you did. Owner and operator are different facts —
  a joint venture's shareholders are not necessarily its operator, and an SPV
  (Pipeline Infrastructure Ltd, Reliance Gas Pipelines Ltd, Hooghly Pipelines) is not its
  parent. Name the entity that actually operates the pipe, and cite a source that says so
  rather than one that merely names the owner.
- **`length_ratio` (37 rows).** The drawn route's geodesic length disagrees with
  `LengthKnownKm` by more than ±33%. **Do NOT carry over the Pakistan heuristic that the
  route is probably wrong.** India's routes are not overwhelmingly schematic — 29 rows are
  `medium`, 10 `high`, against 26 `very low (straight line/schematic)` — and the ratios
  scatter both ways (24 under, 13 over, median 0.69). Work out which side the evidence
  supports, per row. Three specific patterns to consider before proposing anything:
  - a **network/aggregate row** (regional grids, basin networks) states a total network
    length while its geojson draws only a trunk — the length may be right and the ratio
    meaningless. Say what the length counts.
  - a **phased row** whose geojson covers the whole line, not its phase — a granularity
    artifact, not an error; do not "fix" the length to match.
  - a genuinely **understated length**, which is real here: P0934's 44 km is contradicted
    by the register (675 km operating), OSM (306 km mapped) and its own drawn route (375
    km) all at once.
- **`Date_logic`** — `Status = operating` with no `StartYear1`. Find the commissioning
  year. A gas FIELD's first-production year is NOT the pipeline's commissioning year — if
  a field date is all you can find, say so and mark it `low`, or leave it `UNRESOLVED`.
- **`endpoint_country`** — a transnational route's last endpoint lands in a country that
  is neither `StartCountryOrArea` nor `EndCountryOrArea`. For a transit pipeline (IPI,
  TAPI) a route that stops in Pakistan or Afghanistan may be a correctly-drawn PARTIAL
  route rather than an error. Decide which and say so. Do not propose new coordinates.
- **`countries`** — the route makes landfall in a country the sheet never lists. For
  P5413 (Gurdaspur–Jammu) check whether this is a Natural Earth boundary artifact around
  Jammu & Kashmir before treating it as a data defect.
- **`Diameter_OutOfRange` / `Capacity`** — a number outside a plausible range. P0906's
  350 "inches" is almost certainly 350 mm. **Confirm the intended figure from a source;
  do not convert blind** — a plausible-looking unit conversion applied without evidence
  is exactly the kind of change this workflow exists to prevent.
- **`Existence_support`** — the row's refs are too thin to establish that the project
  exists as described. Answer the existence question first; everything else is moot if
  the row is a phantom. Never propose deleting a row on thin refs alone.

## Deliverable

Write ONE file per row — `$S/rows/<PID>.json`, one JSON object EXACTLY:

```json
{
 "project_id": "<PID>",
 "pipeline_name": "<name>",
 "sheet_row": <int from the brief>,
 "wiki": "<wiki url from the brief>",
 "fills": [
   { "ref_col": "Operator [ref]",
     "value_cols": ["Operator"],
     "values": {"Operator": "GAIL (India) Ltd"},
     "primary_value_col": "Operator",
     "primary_value": "GAIL (India) Ltd",
     "class_out": "REFS_ADDED|UNRESOLVED",
     "tab": "operators_owners",
     "proposed_refs": ["https://...verified..."],
     "verifications": [{"url":"https://...","ok":true,"contains_value":true}],
     "tier": "high|medium|low", "independent": true, "source_language": "en|hi",
     "researcher_notes": "<what you searched; how the source supports the value; any contradiction>" }
 ],
 "validity": [
   { "verdict": "concern|confirmed (caveat)",
     "concern_type": "spec|attribution|existence|duplicate|classification",
     "recommendation": "<what a human should DO — an action, not a summary>",
     "researcher_notes": "<the evidence>",
     "proposed_refs": [], "verifications": [], "tier": "", "independent": false }
 ]
}
```

- `Operator` and `Owner` fills MUST carry `"tab": "operators_owners"` — those two columns
  live on the operators/owners tab (GID 1489950650), not the gas tab. Everything else
  omits `tab`.
- Use `fills[]` for a proposed value + its ref (operator, corrected length, start year).
- Use `validity[]` for a judgement with no single cell to fill (e.g. "the 608.82 km is a
  network total and the geojson draws only the trunk, so neither value is wrong").
- Omit either array if empty. **Write the file even if everything came back
  `UNRESOLVED`** — a documented dead end is a result, and a missing shard is not.
- Before finishing, run
  `python -c "import json; json.load(open('$S/rows/<PID>.json'))"` to confirm it parses.
