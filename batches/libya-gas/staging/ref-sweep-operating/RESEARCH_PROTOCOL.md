# Ref-research protocol — Libya gas operating rows

Identical to the contract used for the first 15 shards (see
`libya-operating-ref-research.js`), so shards are directly comparable.

Working dir: `/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher`
Staging: `batches/libya-gas/staging/ref-sweep-operating` (referred to below as `$S`)

Read your brief: `$S/ref_shards/_briefs/<PID>.json` — it lists `units` (each a ref
cell needing a working ref that supports the stated value) and `seed_citations`
(gem.wiki outbound cites, as *leads only* — verify them, never cite gem.wiki).

For EACH unit: find a source that supports its `values`, and produce a working,
verified ref.

## Standing rules (non-negotiable)

1. **NEVER cite** gem.wiki / globalenergymonitor.org / theodora.com / A Barrel Full /
   any wikidot.com page. Read for leads only.
2. **NEVER fabricate a URL.** If none verifies, mark the unit `UNRESOLVED`.
3. **Verify EVERY url before citing:**
   `python scripts/url_verifier.py "<url>" "<expected substring>"` — cite only if
   OK/200 AND it contains the expected token (a distinctive number/place/name;
   Arabic forms welcome). Try Wayback (`https://web.archive.org/web/2023/<url>`)
   for dead originals.
4. **Corroborate with ≥2 INDEPENDENT sources** where possible (separate origins; not
   one wire reprinted; nothing tracing to GEM). `tier`: `high` = ≥2 independent
   working + value-present; `medium` = 1 strong; `low` = 1 weak/partial/conflicting.
5. **Search Arabic + regional/trade sources:** Libya Herald, The Libya Observer,
   Libya Update, Al Wasat / alwasat.ly, Attaqa / attaqa.net, Ean Libya, official
   National Oil Corporation pages (noc.ly), Mellitah Oil & Gas, Sirte Oil Company,
   Zueitina Oil Company, Waha Oil Company, OPEC Annual Statistical Bulletin, MEED,
   Zawya, Pipeline & Gas Journal, Oil & Gas Journal, EIA, Offshore Technology,
   NS Energy, World Bank / AfDB reports.
6. **KNOWN GOTCHA in this scope:** many Sirte-Basin rows cite OPEC ASB 2012
   Table 4.10 whose live opec.org PDF link is DEAD (redirects to the homepage). The
   table IS recoverable via Wayback snapshots of the ASB PDF + `pdftotext` — a
   recovered Wayback ASB URL that names the pipeline and its specs is a valid ref.
   Other agents in this batch already did this successfully; prefer a Wayback ASB URL
   over UNRESOLVED for those rows, and add a second independent non-OPEC source where
   one exists.

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

One resolution object per unit in the brief. `sheet_row` comes from the brief.
Before finishing, run
`python -c "import json; json.load(open('$S/ref_shards/<PID>.json'))"`
to confirm it parses.

## Additionally: the redundancy question

This batch is also critically evaluating whether some GEM Libya gas rows are
double-counts of each other. If your brief's pipeline is flagged below, spend a
little extra search effort on it and put your evidence in a final resolution object
with `"ref_col": "__REDUNDANCY__"` (no refs required if you find nothing; set
`class_out: "UNRESOLVED"` and explain in `researcher_notes`).

Answer only what sources actually say — "no evidence either way" is a valid and
useful answer. Do not speculate.

Return ONLY a 2–3 line summary (units REFS_ADDED vs UNRESOLVED, any value
contradictions, and your redundancy read if flagged). The shard file is the
deliverable.
