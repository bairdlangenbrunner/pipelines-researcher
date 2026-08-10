# Leg-3 research protocol — Pakistan gas handoff QC

Working dir: `/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher`
Staging: `batches/pakistan-gas/staging/qc` (referred to below as `$S`)

Your brief is `$S/rows/_briefs/<CLUSTER>.json`. It lists the rows assigned to you
and, per row, the SPECIFIC flag(s) Legs 1/2 raised. **Resolve the flagged question,
not the whole row** — a 63-agent deep sweep, a cancelled-status review and two
reconciliations (GulfPub, OSM) already ran over these rows and their findings are
staged elsewhere. Widening scope duplicates work and produces conflicting verdicts.

## READ THIS FIRST — the sourcing situation in Pakistan

**51 of GEM's 70 Pakistan gas rows are one July-2023 bulk load off two MAP files**
(`sngpl.com.pk/images/transmission/TransmissionMap042022L.jpg` and
`pepl.com.pk/assets/images/downloads/Energy-MapA4-2020.pdf`), plus 8 more off the
SSGC equivalent. Both are cartographic. That means the lengths, diameters and
endpoints on those rows were **digitized or inferred from a map**, and there is
usually no text anywhere naming the individual segment. Full analysis:
`notes/escalation-2026-08-07-pakistan-sngpl-map-bulk-load.md`.

Two consequences for your work:

1. **`UNRESOLVED` is a common and correct outcome here.** Do not stretch to fit a
   weak source onto a row just to avoid an empty result. A documented dead end —
   naming what you searched and what does not exist — is genuinely useful.
2. **The highest-value find in this whole leg is a text-searchable SNGPL or SSGC
   asset register**: an annual report with a province-wise / line-wise transmission
   breakdown, an OGRA licence document, a PPIB or HDIP publication, or an SNGPL
   tender/engineering document naming segments with lengths and commissioning dates.
   One such document would resolve rows across every cluster. **If you find one, say
   so loudly in `researcher_notes` and give the exact URL** — even for rows it does
   not directly answer.

Also note **gem.wiki is returning HTTP 403** to all automated fetches right now, so
the usual harvested-lead starting point is unavailable and `wiki` URLs in your brief
will not load. That is an access failure, not evidence of anything.

## Standing rules (non-negotiable)

1. **NEVER cite** gem.wiki / globalenergymonitor.org / theodora.com / A Barrel Full /
   any `wikidot.com` page. Read for leads only — never a `[ref]`.
2. **NEVER fabricate a URL.** If nothing verifies, mark `UNRESOLVED` and say what you
   tried. An invented citation is the one unrecoverable error.
3. **Verify EVERY url before citing:**
   `python scripts/url_verifier.py "<url>" "<expected substring>"` — cite only if
   OK/200 AND it contains the expected token (a distinctive number, place or name).
   Try Wayback (`https://web.archive.org/web/2023/<url>`) for dead originals.
   **Verifier false negatives are real:** prose and equivalent units count ("commissioned
   in 1998" supports `StartYear1 = 1998`; "56 miles" supports 90 km). Never declare a
   source unsupported off a substring miss without reading the passage and quoting it.
   If a URL fails on SSL/TLS but `curl -sI` returns 200, it is LIVE — say so.
4. **Corroborate with ≥2 INDEPENDENT sources** where possible (separate origins; not
   one wire story reprinted; nothing tracing back to GEM). `tier`: `high` = ≥2
   independent working + value-present; `medium` = 1 strong; `low` = 1
   weak/partial/conflicting.
5. **No orphan refs, no orphan values.** Never propose a `[ref]` without the value it
   supports, and never propose a value without a ref.
6. **Search Urdu and Pakistani/regional sources**, not just English majors: SNGPL
   (sngpl.com.pk), SSGC (ssgc.com.pk), OGRA (ogra.org.pk), PPIB, HDIP, Mari Energies
   / Mari Petroleum, OGDCL, PPL (ppl.com.pk), Interstate Gas Systems (isgs.com.pk),
   Pakistan Petroleum Information Service, Business Recorder (brecorder.com), Dawn
   Business, The News / thenews.com.pk, Profit/Pakistan Today, The Express Tribune,
   Pakistan Economic Survey, Pipeline & Gas Journal, Oil & Gas Journal, MEED, Zawya.
   Company **annual reports** are the single most productive family here.
7. **A flagged disagreement is a question, not a verdict.** "The drawn route is shorter
   than the stated length" may mean the LENGTH is wrong, or that the ROUTE is a
   partial/straight-line schematic. Decide which, with evidence, and say which you
   decided. Pakistan's routes are overwhelmingly `RouteAccuracy = very low
   (straight line/schematic)`, so **the route being wrong is the more likely default** —
   do not "correct" a sourced length to match a schematic line.

## The three flag types you will see

- **`Date_logic`** — `Status = operating` with no `StartYear1`. Find the commissioning
  year. A gas FIELD's first-production year is NOT automatically the pipeline's
  commissioning year — if a field date is all you can find, say so explicitly and mark
  it `low`, or leave it `UNRESOLVED`. An SNGPL/SSGC annual report that says a line was
  "completed/commissioned during FY20XX" is the ideal source.
- **`length_ratio`** — the drawn route's geodesic length disagrees with `LengthKnown`.
  Find the SOURCED length. Report which of the two the evidence supports. Where the
  route is longer than the stated length, consider that the row may be one SEGMENT of
  a longer line whose geojson covers the whole thing — that is a granularity artifact,
  not an error, and must not be "fixed".
- **`endpoint_country`** — a transnational route's endpoint lands in a country that is
  neither the row's `StartCountryOrArea` nor `EndCountryOrArea`. Decide whether the
  geometry is drawn wrong or the start/end columns are wrong; for a multi-country
  project the answer is often that GEM's row covers a different extent than the drawn
  line. Do not propose new coordinates.

## Deliverable

Write ONE file per row: `$S/rows/<PID>.json`, a single JSON object EXACTLY:

```json
{
 "project_id": "<PID>",
 "pipeline_name": "<name>",
 "sheet_row": <int from the brief>,
 "wiki": "<wiki url from the brief>",
 "fills": [
   { "ref_col": "StartYear1 [ref]",
     "value_cols": ["StartYear1"],
     "values": {"StartYear1": "1998"},
     "primary_value_col": "StartYear1",
     "primary_value": "1998",
     "class_out": "REFS_ADDED|UNRESOLVED",
     "proposed_refs": ["https://...verified..."],
     "verifications": [{"url":"https://...","ok":true,"contains_value":true}],
     "tier": "high|medium|low", "independent": true, "source_language": "en|ur",
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

- Use `fills[]` for a proposed value + its ref (start year, corrected length).
- Use `validity[]` for a judgement with no single cell to fill (e.g. "the drawn route
  is a straight-line schematic, so the ROUTE is the error, not the 76.67 km length").
- Omit either array if empty. **Write the file even if everything came back
  `UNRESOLVED`** — a documented dead end is a result, and a missing shard is not.
- Before finishing, run
  `python -c "import json; json.load(open('$S/rows/<PID>.json'))"` to confirm it parses.
