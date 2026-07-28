# Research protocol — Libya gas CANCELLED rows (status-review + validity)

Two rows carry `Status = cancelled` and were never covered by the operating
ref-sweep or the in-dev sweep. This pass asks three questions per row:
**is `cancelled` still the right status, are the row's values credible, and can
each ref cell be sourced?**

Working dir: `/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher`
Staging: `batches/libya-gas/staging/cancelled-review` (below: `$S`)

## Standing rules (non-negotiable — identical to the operating sweep)

1. **NEVER cite** gem.wiki / globalenergymonitor.org / theodora.com / A Barrel Full /
   any wikidot.com page. Read for leads only.
2. **NEVER fabricate a URL.** If none verifies, mark the unit `UNRESOLVED`.
3. **Verify EVERY url before citing:**
   `python scripts/url_verifier.py "<url>" "<expected substring>"` — cite only if
   OK/200 AND it contains the expected token (a distinctive number/place/name;
   Arabic forms welcome). Try Wayback (`https://web.archive.org/web/2015/<url>`)
   for dead originals. Arabic sources are expected here — both rows' existing
   notes cite Arabic outlets.
4. **Corroborate with ≥2 INDEPENDENT sources** where possible. `tier`: `high` =
   ≥2 independent working + value-present; `medium` = 1 strong; `low` = 1
   weak/partial/conflicting.
5. **Search Arabic + regional/trade sources:** Libya Herald, The Libya Observer,
   Al Wasat / alwasat.ly, Attaqa / attaqa.net, Ean Libya, akhbarlibya24.net,
   KUNA, Al Bayan (albayan.ae), noc.ly, Mellitah Oil & Gas, Eni, Tunisian ETAP /
   STEG, MEED, Zawya, Pipeline & Gas Journal, Oil & Gas Journal, OPEC ASB.
6. **A cancelled status is a claim like any other.** These rows are old and quiet.
   *Absence of news is NOT evidence of cancellation* — but it also is not evidence
   against it. If you find no source that says the project was cancelled, say so
   plainly and keep `ShelvedCancelledType = Presumed` / `inferred` rather than
   inventing a cancellation event. Equally, if you find the project was **revived**
   or was never really a distinct project, that is a major finding — report it.

## Deliverable

Write `$S/ref_shards/<PID>.json` = a single JSON object EXACTLY:

```json
{
 "project_id": "<PID>",
 "pipeline_name": "<name>",
 "resolutions": [
   { "ref_col": "<e.g. Status [ref]>", "sheet_row": 0,
     "class_out": "REFS_ADDED|REVERIFIED|DEAD_LINK|UNRESOLVED",
     "proposed_refs": ["https://...verified..."],
     "verifications": [{"url":"https://...","ok":true,"contains_value":true}],
     "tier": "high|medium|low", "independent": true, "source_language": "en|ar",
     "researcher_notes": "<what you searched, the value's support vs sources, any contradiction to flag>" }
 ]
}
```

One resolution object per unit in your brief (`$S/ref_shards/_briefs/<PID>.json`).
`sheet_row` comes from the brief. Before finishing, run
`python -c "import json; json.load(open('$S/ref_shards/<PID>.json'))"`.

## Additionally: the validity question (REQUIRED for both rows)

Add a final resolution object with `"ref_col": "__VALIDITY__"`, `class_out`
`UNRESOLVED`, and your evidence in `researcher_notes`. Your brief names the
specific concern. Answer only what sources actually say — **"no evidence either
way" is a valid and useful answer.** Do not speculate, and do not resolve a
concern by asserting the tracker is right.

Return ONLY a 3–4 line summary (units REFS_ADDED vs UNRESOLVED, your status
verdict, your validity verdict). The shard file is the deliverable.
