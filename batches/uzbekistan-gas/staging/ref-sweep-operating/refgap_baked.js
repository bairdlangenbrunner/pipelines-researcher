export const meta = {
  name: 'uz-gas-refgap-sweep',
  description: 'Ref-gap research fan-out for the Uzbekistan gas operating leg: one researcher per ProjectID brief, sourcing recorded sheet values against Russian-language Uzbek state, legal and Soviet technical material; writes ref_shards/<PID>.json',
  phases: [
    { title: 'Research', detail: 'one subagent per ProjectID brief' },
  ],
}

const A = {"repo": "/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher", "staging": "batches/uzbekistan-gas/staging/ref-sweep-operating", "model": "sonnet", "briefs": [{"pid": "P2030", "name": "Central Asia–China Gas Pipeline", "n_units": 4}, {"pid": "P2290", "name": "Gazli-Kagan Gas Pipeline", "n_units": 4}, {"pid": "P2698", "name": "Shurtan-Sherabad Gas Pipeline", "n_units": 2}, {"pid": "P3983", "name": "Gazli-Kagan Gas Pipeline", "n_units": 6}, {"pid": "P3984", "name": "Gazli-Kagan Gas Pipeline", "n_units": 4}, {"pid": "P4071", "name": "Ahangaran-Pungan Gas Pipeline", "n_units": 3}, {"pid": "P4072", "name": "Ahangaran-Pungan Gas Pipeline", "n_units": 8}, {"pid": "P4073", "name": "Gazli-Nukus Gas Pipeline", "n_units": 3}, {"pid": "P5870", "name": "Gazli-Sarymay Gas Pipeline", "n_units": 9}, {"pid": "P6933", "name": "Bukhara-Tashkent-Bishkek-Almaty Gas Pipeline", "n_units": 2}, {"pid": "P6934", "name": "Bukhara-Tashkent-Bishkek-Almaty Gas Pipeline", "n_units": 4}, {"pid": "P6935", "name": "Bukhara-Tashkent-Bishkek-Almaty Gas Pipeline", "n_units": 2}, {"pid": "P6936", "name": "Kelif-Mubarek Gas Pipeline", "n_units": 3}, {"pid": "P6937", "name": "Kelif-Dushanbe Gas Pipeline", "n_units": 6}, {"pid": "P6963", "name": "Yangiyer-Ahangaran Gas Pipeline", "n_units": 1}, {"pid": "P6964", "name": "Yangiyer-Ahangaran Gas Pipeline", "n_units": 3}, {"pid": "P6966", "name": "Mubarek-Kagan Gas Pipeline", "n_units": 2}]}
const MODEL = A.model || 'sonnet'
const REPO = A.repo
const STG = A.staging

const contract = (b) => `You are a GEM pipeline ref-sweep researcher. Target: ProjectID ${b.pid} (${b.name}), an Uzbekistan gas pipeline row.

cd ${REPO} first. STG=${STG}

## Inputs (read them, in this order)
- Your brief: \`${STG}/ref_shards/_briefs/${b.pid}.json\` — your ${b.n_units} gap units (ref cells MISSING/UNRESOLVED, or whose existing link is dead). Each unit: ref_col, sheet_row, segment_name, value_cols, values, primary_value, current_ref, class_out. Some units carry a \`note\` from the orchestrator — obey it.
- The deep-sweep audit shard \`${STG}/rows/${b.pid}.json\` — a researcher already audited this row and found sources. REUSE and re-verify those leads before searching fresh; its \`validity\` and \`fills\` entries name real, verified URLs.
- \`seed_citations\` in your brief, and \`${STG}/wiki_citations.json\` — leads ONLY, never a citation, and read the wiki-citation trap below before trusting one.

## Scope-specific guidance — Uzbekistan

**Russian is the primary research language here, not a fallback (Baird directive, 2026-08-26).** Uzbekistan's gas grid is Soviet-built and its documentary record is Russian-language. Search Russian FIRST; Uzbek (Latin script) counts too. An \`UNRESOLVED\` that only reflects an English-language search is not an acceptable outcome on this batch. Set \`source_language\` to \`ru\` or \`uz\` and put an English gloss of the supporting sentence in researcher_notes so the finding is reviewable.

**Where the material lives.** Operator/state: \`uzbekneftegaz.uz\`, \`utg.uz\` (Uzbektransgaz), \`minenergy.uz\`, \`gov.uz\`, \`stat.uz\`. Legal/regulatory — these name pipelines, lengths and diameters inside investment programmes and decrees, and are the single most productive vein for this country: \`lex.uz\`, \`norma.uz\`. Press: \`uzdaily.uz\` (has a Russian edition), \`gazeta.uz\`, \`kun.uz\`, \`podrobno.uz\`, \`review.uz\`, \`xabar.uz\`, plus \`interfax.ru\`, \`neftegaz.ru\`, \`oilcapital.ru\`, \`trend.az\`, \`centralasia.news\`. For the trunks that touch Turkmenistan/Tajikistan/Kyrgyzstan, Gazprom and CNPC material. **Soviet-era technical literature is legitimate and often the ONLY place a string's own diameter and length are itemised** — VNIIgaz / VNIPItransgaz tables, \`Газовая промышленность\`, ministry handbooks. Ukraine's entire unlock on comparable rows was one VNIPItransgaz table, recovered from a Wayback capture of a dead page.

**A dead link is a lead, not a loss.** 39 of this country's 78 filled ref cells are already dead. For every \`DEAD_LINK\` unit, try \`web.archive.org\` on the \`current_ref\` BEFORE searching fresh — that page was the original support and the capture usually still carries the value. Cite the Wayback URL and name the original in researcher_notes.

**Access failure ≠ deletion (hard rule).** Only a confirmed HTTP 404 or 410 may cause a ref to drop. A 403, WAF block, geo-block, TLS failure or timeout means inaccessible-to-us, which is not evidence the page is gone: keep it, say so, and ADD a Wayback snapshot alongside rather than swapping it in. If \`url_verifier\` fails on TLS but \`curl -sI\` returns 200, the page is LIVE — say so in notes (Kazakhstan's \`adilet.zan.kz\` made 51 of 105 cells look dead with zero real 404s). Note also that \`web.archive.org\` content serving was unreachable from this machine on 2026-08-26 while \`archive.org\`'s API answered normally; if that persists for you it is a network condition that tells you nothing about the source, and you must not cite a capture you could not actually read.

**Calibrate UNRESOLVED honestly — this country sits between India and Kazakhstan.** Don't reach for \`UNRESOLVED\` before searching in Russian; but don't manufacture a citation either. These are domestic strings run by a state monopoly that does not publish line-wise specs, so after a genuine Russian-language search an honest \`UNRESOLVED\` on a per-string diameter or capacity is often the CORRECT answer. Say what you searched, in which language, so the verdict is auditable.

**The wiki-citation trap — a harvested URL earns ONE cell, not a row.** 18 rows map to only 11 gem.wiki pages, so many seed leads were harvested from a page about a PARENT trunk or a SIBLING string. A URL earns a \`[ref]\` cell only when the page names YOUR segment's own value. Sharpest case: **P6933/P6934/P6935** (\`Mubarek-Zirabulak I/II/III\`) hang off the Bukhara–Tashkent–Bishkek–Almaty page whose own parent rows are excluded from this batch, so its citations are about the parent trunk and do NOT support a string's length or diameter. Same shape for the \`Gazli-Kagan\`, \`Yangiyer-Ahangaran\` and \`Mubarek-Kagan\` families. A generic or aggregate citation that never names your segment supports nothing.

**Descriptive units are still sourceable.** A Russian-language source describing the line as a natural-gas transmission pipeline in operation supports \`Fuel\`, \`PipelineType\` and \`Status\` at once — cite the passage rather than inventing a source per column. But an authorisation, decree or programme date is NOT a commissioning year; never support a \`StartYear\` from one.

**Support the RECORDED value, never a different one.** If what you find disagrees with the sheet's value, set \`class_out = "UNRESOLVED"\` and put the disagreement in researcher_notes — value changes route to a different workflow, not to this shard.

**Two questions are ALREADY SETTLED — do not re-litigate them.** The deep sweep that ran before you answered both, by sourcing: (1) P6933/P6934/P6935's diameters of 1020/1021/1022 mm are a **sheet defect** — the row's own cited uzreport.news source gives Ø1020×12 mm for all three threads, so 1021/1022 look like a segment index leaking into the value; the correction is already staged, so do NOT propose refs for 1021 or 1022. (2) P2698's capacity of **1.00 is CORRECT** (~1 bcm/y, per an Interfax wire quoting an Uzbekneftegaz source, 2003-09-04, republished on mineral.ru, corroborated by cabar.asia 2016) — it is not a units error, so treat 1.00 as the value to support.

**Banned and unusable sources — this bit us on this very batch.** Never propose: gem.wiki / globalenergymonitor.org (standing rule 1), abarrelfull or ANY wikidot.com page, theodora.com, **Wikipedia in any language** (\`source_roster.md\`: never cite directly — use it to REACH an original source, then cite that), and **studfile.net** or comparable student-upload / document re-host sites, which are tertiary re-uploads in the same class as the blocklisted hosts. Three units in the deep sweep had to be downgraded for exactly this. For a place's administrative region, cite **GeoNames** (this repo's established substitute) or the Uzbek statistics committee, not an encyclopaedia infobox.

## Standing rules (NON-NEGOTIABLE)
1. NEVER cite gem.wiki / globalenergymonitor.org, theodora.com, abarrelfull / any wikidot.com page, Wikipedia in any language, or studfile.net-style document re-hosts. Read for leads only.
2. NEVER fabricate a URL. Nothing found → class_out "UNRESOLVED" + researcher_notes saying what you searched, IN WHICH LANGUAGES.
3. Run EVERY url through the verifier before citing: \`python scripts/url_verifier.py "<url>" "<expected substring>" ["<more>"]\` — cite only on OK/200 AND token present. Use distinctive tokens (numbers, place names, the operator's name). Verifier false negatives are real: prose and equivalent units count ("введён в 2004 году" supports StartYear1 = 2004). If a URL fails on SSL/TLS but \`curl -sI\` returns 200, it is LIVE — say so. BEWARE the inverse too: a token can match JS telemetry or inline CSS rather than article text (a Facebook page "passed" on "1020" in this batch purely from \`-1020px\`), so on a script-heavy page confirm the value is in the VISIBLE text.
4. Corroborate with ≥2 INDEPENDENT sources where possible. tier: high = ≥2 independent working+value-present; medium = 1 strong; low = 1 weak/partial. The same wire story republished is ONE source.

## Task, per unit in your brief
Find independent sources that SUPPORT the RECORDED value(s) (\`values\` / \`primary_value\`) for that ref_col. For \`DEAD_LINK\` units, FIRST try a web.archive.org snapshot of \`current_ref\` — that page was the original support. Work ALL ${b.n_units} units; several units may share one verified source when it genuinely supports each value.

## Output — write the shard, then a 2-line summary
Write \`${STG}/ref_shards/${b.pid}.json\` EXACTLY shaped:
{
  "project_id": "${b.pid}",
  "pipeline_name": "<from brief>",
  "resolutions": [
    { "ref_col": "<from unit>", "sheet_row": <int from unit>,
      "class_out": "REFS_ADDED|UNRESOLVED",
      "proposed_refs": ["https://...verified..."],
      "verifications": [{"url":"https://...","ok":true,"contains_value":true}],
      "tier": "high|medium|low", "independent": true,
      "source_language": "ru",
      "researcher_notes": "<what supports the value, with an English gloss of the supporting sentence if it is not English; for archive snapshots name the original URL; if unresolved, what you searched and in which languages>" }
  ]
}
One resolution per brief unit (all ${b.n_units}, including UNRESOLVED ones). Every proposed_ref must have a passing verification entry. Before finishing run \`python -c "import json; json.load(open('${STG}/ref_shards/${b.pid}.json'))"\`. Return ONLY a 2-line summary: units REFS_ADDED vs UNRESOLVED, and any surprises. The shard file is the deliverable.`

phase('Research')
log(`Uzbekistan ref-gap research: ${A.briefs.length} ProjectID briefs, one subagent each.`)
const results = await parallel(A.briefs.map(b => () =>
  agent(contract(b), { label: `refgap:${b.pid}`, phase: 'Research', agentType: 'general-purpose', model: MODEL })
))
const done = results.filter(Boolean).length
log(`Ref-gap research complete: ${done}/${A.briefs.length} returned. Shards in ${STG}/ref_shards/`)
return { researched: done, total: A.briefs.length }
