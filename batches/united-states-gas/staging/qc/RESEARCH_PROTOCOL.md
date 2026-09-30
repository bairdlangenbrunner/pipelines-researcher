# Leg-3 research protocol — United States gas handoff QC (2026-09-16)

You are resolving flagged disagreements on a set of GEM gas-pipeline rows that share a
**source ladder**. Your brief (`rows/_briefs/<key>.json`) carries 2–8 rows, each with its
current sheet values, its flags verbatim, and the geometry measured in Leg 2.

Read the brief's `source_ladder` field first — it names the documents most likely to answer
YOUR rows and records what earlier legs already settled, so you do not re-derive a closed
point or contradict a staged verdict.

`$S` below = `batches/united-states-gas/staging/qc`.

## READ THIS FIRST — the sourcing situation in the United States

The US is the **inverse of Kazakhstan and the inverse of Pakistan**. For a FERC-jurisdictional
interstate pipeline there IS a line-wise public register, and it is unusually rich:

> **FERC eLibrary publishes the application, the environmental assessment and the certificate
> order for every NGA §7 interstate project** — and the EA's facility tables state each loop's
> and lateral's **length in miles and pipe diameter in inches, segment by segment.**

So the calibration here is:

- On an **interstate** row, `UNRESOLVED` for a diameter or a length is almost always "nobody
  looked", not "the number is not public". Find the docket. The EA facility table is the
  single highest-yield document in this entire packet.
- On an **intrastate or gathering** row, the opposite holds — and roughly half the rows in
  this cut are intrastate. **These pipelines are not in FERC eLibrary at all**, by statute,
  not by omission. An eLibrary miss on a Texas intrastate is evidence of nothing. Go to the
  Texas Railroad Commission T-4 permit record and the RRC public GIS pipeline viewer, the
  Louisiana DNR/LDEQ permits, the Alaska RCA, the state PUC. A documented `UNRESOLVED` on a
  gathering line's diameter is a legitimate outcome; an `UNRESOLVED` reached by searching only
  eLibrary is not.

Which is which is in your brief's `source_ladder`, and it says so explicitly where it matters
(`energy-transfer-tx`, `permian-gathering`, `lng-feeders`, `alaska`, `leap`).

### US-specific gotchas that will cost you hours, or cost you a wrong finding

1. **UNITS. This is the single largest false-negative source in this country.** Every US
   source is **miles and inches**; the tracker is `LengthKnownKm` in kilometres and
   `Diameter` in **millimetres** (read the row's own `DiameterUnits` — do not assume).
   A 42-inch pipe is 1067 mm; 30-inch is 762 mm; 24-inch is 610 mm. 51.97 miles is 83.6 km.
   **Convert before you call anything a mismatch**, and per standing rule 4(e) a source
   agreeing within rounding **IS a ref** — cite it at medium/high with the discrepancy noted.
   `UNRESOLVED` means nothing was found, never that something slightly different was found.
2. **A FERC order and the applicant's own filing in the same docket are ONE origin.** The
   certificate order recites the applicant's numbers; the press release repeats them. That is
   one publisher three times, so it is `tier: medium`, `independent: false`. A genuine second
   source is the EIA Natural Gas Pipeline Projects table, a state agency with its own record
   (RRC, a state DEQ/PUC), or trade press reporting its own reporting. Two EIA releases are
   also one origin, and two SEC filings by one registrant are one origin (`audit_shard.py`
   enforces both).
3. **An "expansion" with no new pipe SHOULD have a blank `Diameter` — the flag is then
   correctly resolved as a confirmation, not a fill.** Many of the 37 `Diameter` flags in this
   cut sit on compressor-station and capacity expansions (`McComb Compressor Station`,
   `Mobile Compressor Expansion`, `Zone 3 Capacity Expansion`, `Mainline Capacity Expansion`).
   The gem.wiki page describes the whole SYSTEM, so its diameter is the mainline's, and
   carrying it onto a compression-only row would be a fabricated attribute. Standing rule:
   **expansion with no new physical pipe → `LengthKnown = 0`, `Diameter = blank`.** Establish
   from the EA or the project description whether the project lays pipe. If it does not, write
   a `validity[]` record saying the blank is correct and why — that is the answer.
4. **`Operator` is 33 of the 104 flags, and it is one question per COMPANY, not per row.**
   These cells live on the separate ProjectID-keyed operators/owners tab. Establish who
   operates a system once and apply it to every row of that system in your brief, saying
   explicitly in each shard that you did. Beware the US merger churn that IS most of this
   flag: Energy Transfer absorbed Enable (2021), ONEOK absorbed Magellan (2023), Williams
   acquired MountainWest (2023), Berkshire took majority of Dominion's gas transmission
   (EGTS). Name the operator **as of now**, cite a source that says so, and note the
   predecessor in `researcher_notes`.
5. **The `Northwest Pipeline Co` → `Northwest Pipeline LLC` rename is already adjudicated**
   slice-wide and ships as a `Gas_Decisions` ruling. Do not re-research it. If a source you
   read states one spelling or the other, record which — that is useful — but do not stage a
   fill for the rename itself.
6. **The EIA URL convention.** Cite the EIA *page* or the dated release, never a bare
   `EIA-NaturalGasPipelineProjects.xlsx` or a `data.php` link — `audit_shard.py` rejects both.
7. **`Status = N/A` rows are out of scope** and have already been dropped from this packet
   (P3162). If you meet one, it is not a research target.

## Standing rules (non-negotiable)

1. **NEVER cite** gem.wiki / globalenergymonitor.org / A Barrel Full (`abarrelfull.wikidot.com`,
   `abarrelfull.co.uk`) / theodora.com / yingdodo.com. The gem.wiki infobox is what RAISED most
   of your flags — read it for leads, never as a `[ref]`.
2. **NEVER fabricate a URL.** If nothing verifies, mark `UNRESOLVED` and say what you tried.
   An invented citation is the one unrecoverable error.
3. **Verify EVERY url before citing:**
   `python scripts/url_verifier.py "<url>" "<expected substring>"` — cite only if OK/200 AND it
   contains the expected token (a distinctive number, place or name). Try Wayback
   (`https://web.archive.org/web/2023/<url>`) for dead originals. **Verifier false negatives are
   real:** prose and equivalent units count ("a 42-inch, 25.6-mile loop" supports
   `Diameter = 1067` and `LengthKnownKm = 41.2`; "placed in service in November 2021" supports
   `StartYear1 = 2021`). Never declare a source unsupported off a substring miss without reading
   the passage and quoting it. **A large PDF the substring check cannot see inside is a
   documented false negative** — and FERC EAs are large PDFs. Download it (`curl -o`), read it
   with `pdftotext -layout`, and say in `researcher_notes` that you confirmed the value locally.
4. **Corroborate with ≥2 INDEPENDENT sources** where possible (separate origins; not one wire
   story reprinted; nothing tracing back to GEM; not two releases of one publisher; not the
   order plus the application — see gotcha 2). `tier`: `high` = ≥2 independent working +
   value-present; `medium` = 1 strong; `low` = 1 weak/partial/conflicting. **`tier: "high"` or
   `independent: true` on a `validity[]` record with an empty `proposed_refs` is a
   self-contradiction and `audit_shard.py` will fail you for it.**
5. **An uncited value is owed a ref exactly as a blank is owed a value** (standing rule 4(e)).
   Confirming a recorded value IS an output: emit `class_out: "REFS_ADDED"` carrying the SAME
   value with the ref that states it. "Confirmed as recorded" in your summary and nowhere
   machine-readable is the same as never having checked it.
6. **No orphan refs, no orphan values.** Never propose a `[ref]` without the value it supports,
   and never propose a value without a ref.
7. **A flagged disagreement is a question, not a verdict.** Decide which side is wrong, with
   evidence, and say which you decided.
8. **Never write to the live Google Sheet or the routes repo.** Never propose coordinates.
9. **Do not re-litigate what is settled.** Twelve prior deep-sweep batches ran over these rows
   — 764 concerns, 1,547 corroborated fills, ~3,900 ref records and 1,252 validity verdicts are
   already staged. Re-researching them produces conflicting verdicts.

## The flag types you will see (104 flags / 91 rows)

- **`Diameter` (37)** — blank on the sheet while the wiki shows one. Before proposing a fill,
  settle gotcha 3: does this project lay new pipe? If not, the blank is correct and the answer
  is a `validity[]` record. If it does, the EA facility table gives the diameter in inches —
  convert to mm and check the row's `DiameterUnits`.
- **`Operator` (33)** — blank or stale on the operators/owners tab. One question per company;
  see gotcha 4. Every such record MUST carry `"tab": "operators_owners"`.
- **`Date_logic` (14)** — `Status = operating` with no `StartYear1`, or years out of order
  (ProposalYear ≤ ConstructionYear ≤ StartYear1). For an interstate, the in-service date is in
  the docket or the company's in-service notice; for a Permian gathering line it is usually the
  RRC T-4 permit/commissioning record; for Alaska it is an RCA or DNR right-of-way record and
  may pre-date the digital era. **A gas FIELD's first-production year is NOT the pipeline's
  commissioning year** — if a field date is all you can find, say so and mark it `low`.
- **`StartYear1` (4)** — as above, as an explicit candidate fill.
- **`countries` (6) / `endpoint_country` (5)** — the drawn route makes landfall in, or ends in,
  a country the sheet does not list. In this cut these are **US–Mexico and US–Canada border
  crossings**. A route that stops at the border on a pipeline whose sheet row spans both may be
  a correctly-drawn PARTIAL route rather than an error, and a Natural Earth 1:50m boundary
  artifact can put a near-border vertex on the wrong side. Decide which it is and say so in a
  `validity[]` record. **Do not propose new coordinates** — geometry fixes go to the routes
  repo via a human PR.
- **`LengthKnownKm` (3)** — blank while a length is knowable. Miles → km (gotcha 1).
- **`Capacity` (2)** — blank while the wiki shows one. Source it independently or leave it
  `UNRESOLVED`; never carry the wiki's number across. US capacities are usually MMcf/d or
  Bcf/d — record `CapacityUnits` to match what you cite, and note that the tracker's own
  capacity column may be in a different unit than your source.

## Deliverable

Write ONE file per row — `$S/rows/<PID>.json`, one JSON object EXACTLY:

```json
{
 "project_id": "<PID>",
 "pipeline_name": "<name>",
 "sheet_row": <int from the brief>,
 "wiki": "<wiki url from the brief>",
 "fills": [
   { "ref_col": "Diameter [ref]",
     "value_cols": ["Diameter"],
     "values": {"Diameter": "1067"},
     "primary_value_col": "Diameter",
     "primary_value": "1067",
     "class_out": "REFS_ADDED|UNRESOLVED|DEAD_LINK|REVERIFIED",
     "proposed_refs": ["https://...verified..."],
     "verifications": [{"url":"https://...","ok":true,"contains_value":true}],
     "tier": "high|medium|low", "independent": true, "source_language": "en",
     "researcher_notes": "<what you searched; how the source supports the value; the unit conversion you did; any contradiction>" }
 ],
 "validity": [
   { "verdict": "concern|confirmed (caveat)",
     "concern_type": "spec|attribution|existence|duplicate|classification",
     "fields": ["Diameter"],
     "recommendation": "<what a human should DO — an action, not a summary>",
     "researcher_notes": "<the evidence>",
     "proposed_refs": [], "verifications": [], "tier": "", "independent": false }
 ]
}
```

- **`fields` on a `validity[]` record is REQUIRED** and names which flagged field(s) that
  judgement answers. It is how `check_flag_coverage.py` sees that you addressed the flag; the
  merge drops the key, so it never reaches the deliverable.
- **`Operator` and `Owner` fills MUST carry `"tab": "operators_owners"`.** Everything else
  omits `tab`.
- Use `fills[]` for a proposed or confirmed value + its ref. Use `validity[]` for a judgement
  with no single cell to fill — the compression-only blank diameter, the partial-route
  endpoint call, a granularity ruling.
- Omit either array if empty. **Write the file even if everything came back `UNRESOLVED`** — a
  documented dead end is a result, and a missing shard is not.

## Before you finish — both gates must be clean

```bash
python3 -c "import json; json.load(open('$S/rows/<PID>.json'))"      # parses
python3 $S/check_flag_coverage.py --pid <PID>                        # every flag reported
python3 scripts/audit_shard.py $S/rows/<PID>.json                    # true to its own evidence
```

Run all three for EVERY row in your brief. A non-zero exit is a defect to fix in place, not a
result to report.
