export const meta = {
  name: 'guangxi-refgap-sweep',
  description: 'Ref-gap research fan-out for the Guangxi pilot: one researcher per ProjectID brief, sourcing recorded values in Chinese and routing around geo-blocked hosts; writes ref_shards/<PID>.json',
  phases: [
    { title: 'Research', detail: 'one subagent per ProjectID brief' },
  ],
}

// args: { repo, staging, model?, briefs: [{pid, name, n_units}] }
const A = (typeof args === 'string') ? JSON.parse(args) : (args || {})
if (!Array.isArray(A.briefs) || !A.briefs.length) throw new Error('need args.briefs')
const MODEL = A.model || 'sonnet'
const REPO = A.repo
const STG = A.staging

const contract = (b) => `You are a GEM pipeline ref-sweep researcher. Target: ProjectID ${b.pid} (${b.name}), a China gas pipeline row in the Guangxi provincial grid.

cd ${REPO} first. STG=${STG}

## Inputs (read them)
- Your brief: \`${STG}/ref_shards/_briefs/${b.pid}.json\` — lists your ${b.n_units} gap units (ref cells that are MISSING (class UNRESOLVED) or whose existing link is dead/failing (DEAD_LINK)). Each unit: ref_col, sheet_row, segment_name, value_cols, values, primary_value, current_ref.
- Chinese search keys: \`${STG}/chinese_names.json\` → your PID's entry (zh_pipeline_name / zh_segment_name / zh_alt_names).
- Seed leads: \`${STG}/wiki_citations.json\` (may have none for your PID).
- The deep-sweep audit shard \`${STG}/rows/${b.pid}.json\` — read it: its researcher already found sources for this row; reuse/verify those leads before fresh searching.

## Scope-specific guidance
This pipeline is part of China's Guangxi (广西) provincial gas grid:
- **Research primarily IN CHINESE.** The zh names are your PRIMARY search keys (the English name is a translation nobody in China uses). Combine with 天然气管道 / 输气管道 / 支线 / 投产 / 开工 / 核准 / 竣工. Set source_language "zh" on Chinese-sourced items.
- **Known-blocked hosts (geo-blocking, pre-checked):** fgw.gxzf.gov.cn (the Guangxi DRC — most dead current_refs live there), fgw.liuzhou.gov.cn, fgw.nanning.gov.cn, gig.cn. A ConnectTimeout there means GEO-BLOCKED, not dead: go straight to a web.archive.org snapshot of that URL (the snapshot must pass url_verifier like any URL) and record the original URL in researcher_notes. Quick snapshot check: \`curl -s "https://archive.org/wayback/available?url=<orig>"\`. Don't waste time retrying the origin; many fgw pages have NO snapshot — that's a legitimate UNRESOLVED.
- **Hosts confirmed reachable:** ndrc.gov.cn, pipechina.com.cn, cnpc.com.cn, sinopec.com, news.bjx.com.cn, gx.chinanews.com.cn, gx.xinhuanet.com, wsbs.liuzhou.gov.cn, sasac.gov.cn. Official announcements are widely republished (新华网, 人民网, sohu, sina, 澎湃, 北极星) — but republications of ONE original story count as ONE source for the ≥2-independent rule.

## Standing rules (NON-NEGOTIABLE)
1. NEVER cite gem.wiki / globalenergymonitor.org, theodora.com, abarrelfull / any wikidot.com page. Read for leads only.
2. NEVER fabricate a URL. Nothing found → class_out "UNRESOLVED" + researcher_notes explaining what you searched.
3. Run EVERY url through the verifier before citing: \`python scripts/url_verifier.py "<url>" "<expected substring>" ["<more>"]\` — cite only on OK/200 AND token present. Use distinctive tokens (Chinese pipeline name fragments, numbers, place names).
4. Corroborate with ≥2 INDEPENDENT sources where possible. tier: high = ≥2 independent working+value-present; medium = 1 strong; low = 1 weak/partial.

## Task, per unit in your brief
Find independent sources that SUPPORT the RECORDED value(s) (\`values\` / \`primary_value\`) for that ref_col. For DEAD_LINK units, first try a web.archive.org snapshot of \`current_ref\` (it was the original support), then fresh Chinese-language search. NEVER propose refs for a DIFFERENT value — if what you find disagrees with the recorded value, set class_out "UNRESOLVED" and put the disagreement in researcher_notes (value changes route to a different workflow). Work ALL ${b.n_units} units; it's fine for several units to share the same verified source when it genuinely supports each value.

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
      "source_language": "zh",
      "researcher_notes": "<what supports the value; for archive snapshots note the original URL; if unresolved, what you searched>" }
  ]
}
One resolution per brief unit (all ${b.n_units}, including UNRESOLVED ones). Every proposed_ref must have a passing verification entry. Before finishing run \`python -c "import json; json.load(open('${STG}/ref_shards/${b.pid}.json'))"\`. Return ONLY a 2-line summary: units REFS_ADDED vs UNRESOLVED, and any surprises. The shard file is the deliverable.`

phase('Research')
log(`Ref-gap research: ${A.briefs.length} ProjectID briefs, one subagent each.`)
const results = await parallel(A.briefs.map(b => () =>
  agent(contract(b), { label: `refgap:${b.pid}`, phase: 'Research', agentType: 'general-purpose', model: MODEL })
))
const done = results.filter(Boolean).length
log(`Ref-gap research complete: ${done}/${A.briefs.length} returned. Shards in ${STG}/ref_shards/`)
return { researched: done, total: A.briefs.length }
