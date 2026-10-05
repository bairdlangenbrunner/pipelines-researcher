# Leg-3 research protocol — Ukraine gas handoff QC

You are resolving flagged disagreements on a set of GEM gas-pipeline rows that share a
**source ladder**. Your brief (`rows/_briefs/<key>.json`) carries 2–10 rows, each with its
current sheet values, its flags verbatim, and the geometry measured in Leg 2.

Read the brief's `source_ladder` field first — it names the documents most likely to
answer YOUR rows, and it records what the earlier legs already settled, so you do not
re-derive a closed point or contradict a staged verdict.

`$S` below = `batches/ukraine-gas/staging/qc`.

## READ THIS FIRST — the sourcing situation in Ukraine

Ukraine is neither India nor Kazakhstan. Its 47 gas rows are **among the worst-cited
scopes in the tracker**: 34 of 1,034 `[ref]` cells are filled, **3.29%**, against 18.49%
tracker-wide — 2nd lowest of the 52 country scopes with 20+ gas rows, behind the
Netherlands at 3.03% and effectively tied with Bangladesh at 3.30%. Of the 22 refs that do
sit on operating rows, 17 are dead links. `Length [ref]` and `Capacity [ref]` are each
filled on exactly **one** of the 47 rows — and length and capacity are precisely what this
pass found wrong.

That cuts two ways and you must hold both:

- **A blank cell here is not evidence that the fact is unpublished.** It is far more often
  evidence that nobody has looked. So `UNRESOLVED` is a WEAK result in Ukraine, not the
  correct outcome it frequently is in Kazakhstan. Dig before you give up.
- **But the pipe is mostly Soviet-era**, built 1967–1985, and per-string specs from that
  era genuinely may not exist in any reachable public source. An honest `UNRESOLVED` that
  says exactly what you searched is still far better than a system figure copied onto a
  string, or a plausible number with no origin.

**The one question that is definitely answerable is `Operator`**, which is 22 of the 30
worklist rows. Since 1 January 2020 the transmission system operator for
government-controlled Ukraine is **Gas TSO of Ukraine LLC (ТОВ «Оператор ГТС України»,
GTSOU)**, unbundled from Naftogaz/Ukrtransgaz under Energy Community requirements. Get the
exact legal name GEM should carry, cite it properly, and apply it across your brief — but
note it does **not** extend to the occupied-southeast rows or the Russian-side lines, which
have their own briefs and their own answers.

### Ukraine-specific gotchas that will cost you hours if you miss them

1. **The two operator sites 403 behind a WAF — and a 403 is NOT a deletion.**
   `utg.ua` (Ukrtransgaz, including the historical chronology that would settle two
   clusters) and `tsoua.com` (GTSOU) both returned HTTP 403 to `url_verifier` on
   2026-08-15. Under the standing rules a blocked origin is never treated as a dead link.
   Read them through Wayback (`https://web.archive.org/web/2023/<url>`) and cite the
   snapshot. Never drop a working ref because the live origin blocked you.
2. **`moldovatransgaz.md` fails TLS.** SSL and connection errors on 2026-08-15 both with
   and without certificate verification. The **`mtg.md` mirror** serves the same content
   and verifies 200 — use it and say you did.
3. **Ukrainian routes are 2–5 vertex SCHEMATICS.** A drawn span is therefore a LOWER BOUND
   on corridor extent, nothing more. A drawn length shorter than the stated length is
   **not** evidence against the stated length. Only a drawn span that far EXCEEDS the
   stated length is evidence — and there are exactly two such rows in the country
   (P0784 at 759.1 km drawn against 164.00 stated, and P1481 whose 333.00 km cannot span a
   corridor that is ~424 km great-circle). Do not "fix" a length to match a schematic.
4. **Two motifs of defect run through this country and both are already escalated —
   recognise them, don't re-derive them.**
   - **Gazprom attributed ownership of Ukrainian pipe** (P1485, P0783, P0775 at 48.6%,
     P0776 at "Gazprom 100%"). Gazprom owns no Ukrainian section; the post-2019 unbundling
     put the GTS under GTSOU. If you see this shape again, note it — do not restate it.
   - **System/aggregate capacity restated as a line's own** (P0784's 24.00 bcm/y, 29.00 on
     both Ivatsevychi rows). Same shape India and Kazakhstan carry.
5. **A source that is GEM's own origin is not corroboration.** Gazprom's capacity table
   (65 vs 45 Mm³/day → 23.725 / 16.425 bcm/y) matches P0775/P0776 almost exactly, which
   makes it the likely ORIGIN of those cells. Matching the sheet to its own source is not
   verification.
6. **Research in Ukrainian and Russian.** Operator material, ministry orders
   (zakon.rada.gov.ua), NEURC/НКРЕКП decisions, ProZorro tenders and regional press are
   overwhelmingly Ukrainian- or Russian-language; English coverage is thin and derivative.
   Set `source_language` to `uk` or `ru` accordingly — a Ukrainian-language source is a
   first-class citation here, not a fallback.
7. **Occupied-territory sourcing.** For anything east or south of the 2022 line, Russian
   state and occupation media all trace back to single official directives — five outlets
   repeating one announcement is **one origin**, so cap the tier at `medium` and say why.
   Never present an occupation authority as the legitimate operator without labelling it
   as such.

## Standing rules (non-negotiable)

1. **NEVER cite** gem.wiki / globalenergymonitor.org / A Barrel Full / any `wikidot.com`
   page / theodora.com. The gem.wiki infobox is what RAISED most of your flags — read it
   for leads, never as a `[ref]`.
2. **NEVER fabricate a URL.** If nothing verifies, mark `UNRESOLVED` and say what you
   tried. An invented citation is the one unrecoverable error.
3. **Verify EVERY url before citing:**
   `python scripts/url_verifier.py "<url>" "<expected substring>"` — cite only if OK/200
   AND it contains the expected token (a distinctive number, place or name). Try Wayback
   for dead or blocked originals. **Verifier false negatives are real:** prose and
   equivalent units count ("введений в експлуатацію у 1974 році" supports
   `StartYear1 = 1974`; "6 млрд м³ на рік" supports 6 bcm/y). Never declare a source
   unsupported off a substring miss without reading the passage and quoting it. A large PDF
   the substring check cannot see inside is a documented false negative — download it, read
   it with `pdftotext -layout`, and say in `researcher_notes` that you confirmed the value
   locally.
4. **Corroborate with ≥2 INDEPENDENT sources** where possible (separate origins; not one
   wire story reprinted; nothing tracing back to GEM; not two vintages of one publisher;
   not five outlets relaying one directive). `tier`: `high` = ≥2 independent working +
   value-present; `medium` = 1 strong; `low` = 1 weak/partial/conflicting.
5. **No orphan refs, no orphan values.** Never propose a `[ref]` without the value it
   supports, and never propose a value without a ref.
6. **A flagged disagreement is a question, not a verdict.** Decide which side is wrong,
   with evidence, and say which you decided.
7. **Do not re-litigate what your brief says is settled.** A per-row deep sweep, an
   in-development status review, a cancelled-status review, an eight-cluster redundancy
   adjudication and two reconciliations (GulfPub, OSM) already ran over these rows. Their
   findings are staged elsewhere and re-researching them produces conflicting verdicts.

## The flag types you will see

- **`Operator` blank while the wiki names one (22 rows — the big one).** The sheet's
  `Operator` cell lives on the separate ProjectID-keyed operators/owners tab, so a fill
  MUST carry `"tab": "operators_owners"`. This is one question per COMPANY, not per row —
  answer once and apply it across your brief, saying explicitly in each shard that you did.
  Owner and operator are different facts, and in Ukraine they diverge sharply by section:
  GTSOU operates government-controlled trunk pipe, Gazprom transgaz subsidiaries operate
  the Russian sections, and occupied-territory assets are contested. **Name the entity that
  operates the section this ROW describes**, and cite a source that says so rather than one
  that merely names the system.
- **`length_ratio` (14 rows).** The drawn route's geodesic length disagrees with
  `LengthKnownKm` by more than the accuracy band allows. Read gotcha 3 before doing
  anything. Three patterns to consider:
  - a **schematic route** understating a real corridor — the commonest shape here and NOT
    a finding;
  - a **whole-system or whole-corridor length on a partial route**, or the reverse (a row
    scoped to the Ukrainian section against a route drawn for the whole international
    line). Say what the length counts;
  - a genuinely wrong number, which does happen — but it needs a drawn span EXCEEDING the
    stated length, or an independent source, not just a ratio.
- **`endpoint_country`** — a transnational route's first or last endpoint lands in a
  country that is neither `StartCountryOrArea` nor `EndCountryOrArea`. For a transit
  pipeline a route that stops at the border may be a correctly-drawn PARTIAL route rather
  than an error. Decide which and say so. **Do not propose new coordinates.**
- **`countries`** — the route makes landfall in a country the sheet never lists. Check
  whether a Natural Earth boundary artifact or a legitimately transnational corridor
  explains it before treating it as a data defect.
- **Multi-segment wiki union (`Owner`, `Parent`, `Operator`).** The gem.wiki page covers
  the WHOLE multi-string or multi-country system while the GEM row is ONE string, so the
  "union" the flag reports is the system's value set. **Usually this is not a per-row
  defect.** Decide, once per system, whether the row should carry the system's set or its
  own value, and say which — that judgement is the deliverable and it belongs in
  `validity[]`, not in a fill. Only propose a fill if you can source THIS string's own
  value.
- **`Date_logic`** — `Status = operating` with no `StartYear1`. Find the commissioning
  year. A gas FIELD's first-production year is NOT the pipeline's commissioning year — if a
  field date is all you can find, say so and mark it `low`, or leave it `UNRESOLVED`.

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
     "values": {"Operator": "Gas TSO of Ukraine LLC"},
     "primary_value_col": "Operator",
     "primary_value": "Gas TSO of Ukraine LLC",
     "class_out": "REFS_ADDED|UNRESOLVED",
     "tab": "operators_owners",
     "proposed_refs": ["https://...verified..."],
     "verifications": [{"url":"https://...","ok":true,"contains_value":true}],
     "tier": "high|medium|low", "independent": true, "source_language": "uk|ru|en",
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
  length_ratio and multi-segment-union answers belong ("the 164 km counts the Ukrainian
  section while the geojson draws the whole corridor, so neither value is wrong; state what
  it counts").
- Omit either array if empty. **Write the file even if everything came back `UNRESOLVED`**
  — a documented dead end is a result, and a missing shard is not.
- Before finishing, run
  `python -c "import json; json.load(open('$S/rows/<PID>.json'))"` to confirm it parses.
