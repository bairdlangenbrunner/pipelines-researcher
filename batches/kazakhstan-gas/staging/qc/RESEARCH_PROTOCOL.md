# Leg-3 research protocol — Kazakhstan gas handoff QC

You are resolving flagged disagreements on a set of GEM gas-pipeline rows that share a
**source ladder**. Your brief (`rows/_briefs/<key>.json`) carries 2–6 rows, each with its
current sheet values, its flags verbatim, and the geometry measured in Leg 2.

Read the brief's `source_ladder` field first — it names the documents most likely to
answer YOUR rows, and it records what the earlier legs already settled, so you do not
re-derive a closed point or contradict a staged verdict.

`$S` below = `batches/kazakhstan-gas/staging/qc`.

## READ THIS FIRST — the sourcing situation in Kazakhstan

Kazakhstan is neither India nor Pakistan. Its rows are real and mostly well-drawn (48 of
52 are mapped, 30 at `high` accuracy) and about half the ref cells already carry a
citation. What the country lacks is a **line-wise register**:

> **There is no public line-wise register of Kazakh trunk gas pipelines.** Surveyed
> 2026-08-11; full writeup in `docs/reference/source_roster.md`.

The best line-wise source, the KazMunayGas Annual Report's "Gas Transportation and
Marketing" table, itemises only the **8 major systems** — i.e. it publishes exactly the
system-level aggregates that are this country's characteristic defect, never the
individual strings. QazaqGaz's Integrated Annual Report 2024 lists 25 Intergas Central
Asia lines by **name only**.

**So the calibration here is:**

- For a **per-string SPEC** (this string's own length, diameter, capacity) an honest
  `UNRESOLVED` is often the *correct* outcome — the number may not exist publicly. What is
  never acceptable is copying a system figure onto a string without saying that is what
  you did.
- For **`Operator`** the opposite holds. Operatorship *is* documented: QazaqGaz IGO 2024
  naming a line in Intergas Central Asia's asset list is an operatorship statement even
  though it carries no specs. Dig before you give up on an operator.

### Kazakhstan-specific gotchas that will cost you hours if you miss them

1. **`adilet.zan.kz` serves an INCOMPLETE TLS certificate chain.** `url_verifier.py`
   retries with verification off and returns `ok=true` with `insecure_tls: True`. **That
   verdict means the page IS LIVE — never call an adilet URL dead.** Fetching by hand
   needs `curl -sk` with a browser User-Agent.
2. **The tracker's dominant Kazakh ref is a planning document whose evidence is in MAPS.**
   About half of this country's `[ref]` cells cite Order of the Minister of Energy №350
   (29.09.2023, "General Gasification Scheme 2023–2030",
   `adilet.zan.kz/rus/docs/G23JVM00350`), usually with anchor `#z250`. That anchor lands in
   **Appendices 5–7, which are графические схемы — maps.** A full-text search that fails to
   find a length or a capacity is therefore **not** evidence the ref fails. Say "text only,
   maps not read" rather than asserting the ref is unsupported.
3. **Two vintages of one publisher are ONE origin.** KMG's AR2019/AR2020 and AR2021
   disagree materially on the same systems (Central Asia–Centre 5,306 → 4,149.2 km;
   Bukhara–Ural 2,382 → 1,567.8; BTBA + Gazli–Shymkent 2,462 → 1,903.4; Soyuz +
   Orenburg–Novopskov 1,147 → 805). That is a scope redefinition, not a correction. A row
   matching AR2020 is **dated, not corroborated**, and picking whichever vintage agrees
   with the sheet is not verification. KMG stopped publishing the table after AR2021 (the
   gas arm was carved out to Samruk-Kazyna in November 2021 and renamed QazaqGaz).
4. **Research in Russian and Kazakh.** Ministry orders, QazaqGaz/Intergas material, akimat
   (regional government) gasification programmes and regional news are overwhelmingly
   Russian-language; English coverage is thin and often derivative. Set `source_language`
   to `ru` or `kk` accordingly — a Russian-language source is a first-class citation here,
   not a fallback.
5. **What does NOT exist — do not spend time re-hunting it.** Government decrees №463 and
   2022 №488 are **forward-looking project tables**, not inventories of existing pipe; the
   KASE/KazTransGas 2023 bond prospectus carries aggregates only; Order 182-Н/Қ
   (29.04.2025) is a single embedded JPEG map. Confirmed dead hosts: `gurk.kz`,
   `kazazot.kz` (both real 404s).

## Standing rules (non-negotiable)

1. **NEVER cite** gem.wiki / globalenergymonitor.org / A Barrel Full / any `wikidot.com`
   page / theodora.com. The gem.wiki infobox is what RAISED most of your flags — read it
   for leads, never as a `[ref]`.
2. **NEVER fabricate a URL.** If nothing verifies, mark `UNRESOLVED` and say what you
   tried. An invented citation is the one unrecoverable error.
3. **Verify EVERY url before citing:**
   `python scripts/url_verifier.py "<url>" "<expected substring>"` — cite only if OK/200
   AND it contains the expected token (a distinctive number, place or name). Try Wayback
   (`https://web.archive.org/web/2023/<url>`) for dead originals. **Verifier false
   negatives are real:** prose and equivalent units count ("введён в эксплуатацию в 1974
   году" supports `StartYear1 = 1974`; "6 млрд м³ в год" supports 6 bcm/y). Never declare
   a source unsupported off a substring miss without reading the passage and quoting it.
   `insecure_tls: True` means LIVE (see gotcha 1). A large PDF the substring check cannot
   see inside is a documented false negative — download it, read it with
   `pdftotext -layout`, and say in `researcher_notes` that you confirmed the value locally.
4. **Corroborate with ≥2 INDEPENDENT sources** where possible (separate origins; not one
   wire story reprinted; nothing tracing back to GEM; not two vintages of one publisher).
   `tier`: `high` = ≥2 independent working + value-present; `medium` = 1 strong; `low` =
   1 weak/partial/conflicting.
5. **No orphan refs, no orphan values.** Never propose a `[ref]` without the value it
   supports, and never propose a value without a ref.
6. **A flagged disagreement is a question, not a verdict.** Decide which side is wrong,
   with evidence, and say which you decided.
7. **Do not re-litigate what your brief says is settled.** A per-row deep sweep, an
   in-development status review, a cancelled-status review, an eleven-cluster redundancy
   adjudication and two reconciliations (GulfPub, OSM) already ran over these rows. Their
   findings are staged elsewhere and re-researching them produces conflicting verdicts.
   The class-level findings are written up in
   `notes/escalation-2026-08-11-kazakhstan-system-level-values-on-strings.md` — read it
   if your brief touches a multi-string system.

## The flag types you will see

- **`Operator` blank while the wiki names one (21 rows — the big one).** The sheet's
  `Operator` cell lives on the separate ProjectID-keyed operators/owners tab, and it is
  blank while gem.wiki names an operator. **This is one question per COMPANY, not per
  row:** whoever operates the Bukhara-Ural trunk operates all of its strings — answer once
  and apply it across your brief, saying explicitly in each shard that you did. Owner and
  operator are different facts: for Kazakhstan's transit corridors they genuinely differ by
  section (Gazprom entities on the Russian side, Intergas Central Asia on the Kazakh side),
  so **name the entity that operates the KAZAKH section** and cite a source that says so
  rather than one that merely names the system's participants.
- **Multi-segment wiki union (`Diameter`, `Owner`, `Parent`, `Operator`).** The gem.wiki
  page covers the WHOLE multi-string or multi-country system while the GEM row is ONE
  string, so the "union" the flag reports is the system's set of values. **Usually this is
  not a per-row defect.** Decide, once per system, whether the row should carry the
  system's set or its own value, and say which — that judgement is the deliverable, and it
  belongs in `validity[]`, not in a fill. Only propose a fill if you can source THIS
  string's own value.
- **`length_ratio` (10 rows).** The drawn route's geodesic length disagrees with
  `LengthKnownKm` by more than ±33%, scattering both ways (7 under, 3 over). Kazakhstan's
  routes are not overwhelmingly schematic, so do not assume the route is the wrong side.
  Three patterns to consider before proposing anything:
  - a **whole-system length on a Kazakh-portion route** — the commonest shape here (CAC,
    Bukhara–Ural, Gazli–Shymkent). The length may be right and the ratio meaningless; say
    what the length counts.
  - a **phased or segment row** whose geojson covers the whole corridor — a granularity
    artifact, not an error; do not "fix" the length to match.
  - a genuinely wrong number, which does happen: P3955's 155.8 km against a 600 km drawn
    route is a 3.85× gap that no scope difference explains comfortably.
- **`endpoint_country`** — a transnational route's first or last endpoint lands in a
  country that is neither `StartCountryOrArea` nor `EndCountryOrArea`. For a transit
  pipeline a route that stops at the Kazakh border may be a correctly-drawn PARTIAL route
  rather than an error. Decide which and say so. **Do not propose new coordinates.**
- **`countries`** — the route makes landfall in a country the sheet never lists. For the
  northern Kostanay/Aktobe corridor, check whether this is the Russian border and whether a
  Natural Earth boundary artifact explains it before treating it as a data defect.
- **`Date_logic`** — `Status = operating` with no `StartYear1`. Find the commissioning
  year. A gas FIELD's first-production year is NOT the pipeline's commissioning year — if a
  field date is all you can find, say so and mark it `low`, or leave it `UNRESOLVED`.
- **`Capacity` / `Diameter` blank while the wiki shows one** — a candidate fill. Source it
  independently or leave it `UNRESOLVED`; never carry the wiki's number across.

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
     "values": {"Operator": "Intergas Central Asia JSC"},
     "primary_value_col": "Operator",
     "primary_value": "Intergas Central Asia JSC",
     "class_out": "REFS_ADDED|UNRESOLVED",
     "tab": "operators_owners",
     "proposed_refs": ["https://...verified..."],
     "verifications": [{"url":"https://...","ok":true,"contains_value":true}],
     "tier": "high|medium|low", "independent": true, "source_language": "ru|kk|en",
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
- Use `validity[]` for a judgement with no single cell to fill — which is where most of the
  multi-segment-union answers belong ("the 2,600 km is the whole CAC system while the
  geojson draws the Kazakh portion, so neither value is wrong; state what it counts").
- Omit either array if empty. **Write the file even if everything came back `UNRESOLVED`**
  — a documented dead end is a result, and a missing shard is not.
- Before finishing, run
  `python -c "import json; json.load(open('$S/rows/<PID>.json'))"` to confirm it parses.
