# Leg-3 research protocol — Libya gas handoff QC

Working dir: `/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher`
Staging: `batches/libya-gas/staging/qc` (referred to below as `$S`)

Your brief is `$S/rows/_briefs/<CLUSTER>.json`. It lists the rows assigned to you
and, per row, the SPECIFIC flag(s) Leg 1/2 raised. **Resolve the flagged question,
not the whole row** — the ref sweep, the redundancy pass and the reconciliations
already ran over these rows and their findings are staged elsewhere. Widening scope
duplicates work and produces conflicting verdicts.

## Standing rules (non-negotiable)

1. **NEVER cite** gem.wiki / globalenergymonitor.org / theodora.com / A Barrel Full /
   any `wikidot.com` page. gem.wiki is READ for leads only — never a `[ref]`.
2. **NEVER fabricate a URL.** If nothing verifies, say so and mark `UNRESOLVED`. An
   unresolved flag is a fine outcome; an invented citation is not.
3. **Verify EVERY url before citing:**
   `python scripts/url_verifier.py "<url>" "<expected substring>"` — cite only if
   OK/200 AND it contains the expected token (a distinctive number, place or name;
   Arabic forms welcome). Try Wayback (`https://web.archive.org/web/2023/<url>`)
   for dead originals.
4. **Corroborate with ≥2 INDEPENDENT sources** where possible (separate origins; not
   one wire story reprinted; nothing tracing back to GEM). `tier`: `high` = ≥2
   independent working + value-present; `medium` = 1 strong; `low` = 1
   weak/partial/conflicting.
5. **No orphan refs, no orphan values.** Never propose a `[ref]` without the value it
   supports, and never propose a value without a ref.
6. **Search Arabic + regional/trade sources**, not just English majors: Libya Herald,
   The Libya Observer, Libya Update, Al Wasat / alwasat.ly, Attaqa / attaqa.net, Ean
   Libya, National Oil Corporation (noc.ly), Mellitah Oil & Gas, Sirte Oil Company
   (sirteoil.com.ly), Zueitina Oil Company, Waha Oil Company, OPEC Annual Statistical
   Bulletin, MEED, Zawya, Pipeline & Gas Journal, Oil & Gas Journal, EIA, Offshore
   Technology, NS Energy.
7. **KNOWN GOTCHA in this scope:** many Sirte-Basin rows cite OPEC ASB Table 4.10,
   whose live opec.org PDF link is DEAD (redirects to the homepage). The table IS
   recoverable from Wayback snapshots of the ASB PDF via `pdftotext`; other agents in
   this batch did this successfully. Prefer a recovered Wayback ASB URL that actually
   names the pipeline over `UNRESOLVED`. Note its capacity column header reads
   **"(1,000 scm/yr)"** — the tabulated number is thousands of scm/yr.
8. **A flagged disagreement is a question, not a verdict.** "The wiki says X" is a
   lead. "The drawn route is shorter than the stated length" may mean the LENGTH is
   wrong, or the ROUTE is a partial/schematic line — decide which, with evidence, and
   say which one you decided.

## The three flag types you will see

- **`Operator`** — the operators/owners tab has a blank (or unreferenced) `Operator`.
  Find who physically operates the line. In Libya the operator is normally one of the
  NOC joint-venture operating companies (Sirte Oil, Waha Oil, Zueitina Oil, Mellitah
  Oil & Gas, Akakus, Harouge), NOT "National Oil Corporation" itself — NOC is the
  owner. Use the exact company name a source uses. **Every Libya gas row currently
  has a blank `Operator [ref]`, including the 11 rows where Operator is filled**, so
  a ref for an already-correct operator value is still useful work.
- **`Date_logic`** — `Status=operating` with no `StartYear1`. Find the commissioning
  year. A field's first-production year is NOT automatically its pipeline's
  commissioning year — say so if that is all you can find, and mark it `low`.
- **`length_ratio`** — the drawn route's geodesic length disagrees with
  `LengthKnownKm`. Your job is to find the SOURCED length. Report which of the two
  the evidence supports; if the evidence supports the route, the length value is the
  error and vice versa.

## Deliverable

Write ONE file per row: `$S/rows/<PID>.json`, a single JSON object EXACTLY:

```json
{
 "project_id": "<PID>",
 "pipeline_name": "<name>",
 "sheet_row": <int from the brief>,
 "wiki": "<wiki url from the brief>",
 "fills": [
   { "ref_col": "<e.g. StartYear1 [ref]>",
     "value_cols": ["StartYear1"],
     "values": {"StartYear1": "1970"},
     "class_out": "REFS_ADDED|UNRESOLVED",
     "proposed_refs": ["https://...verified..."],
     "verifications": [{"url":"https://...","ok":true,"contains_value":true}],
     "tier": "high|medium|low", "independent": true, "source_language": "en|ar",
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

- Use `fills[]` for a proposed value + its ref (operator, start year, corrected length).
- Use `validity[]` for a judgement with no single cell to fill (e.g. "the route is a
  straight-line schematic, not the length value, so downgrade `RouteAccuracy`").
- Omit either array if empty. Write the file even if everything came back
  `UNRESOLVED` — a documented dead end is a result.
- **Operator fills:** use `ref_col: "Operator [ref]"` and `value_cols: ["Operator"]`.
  These land on the separate operators/owners tab, which is expected.
