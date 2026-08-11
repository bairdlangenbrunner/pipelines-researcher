export const meta = {
  name: 'india-gas-refgap-sweep',
  description: 'Ref-gap research fan-out for the India gas operating leg: one researcher per ProjectID brief, sourcing the values already recorded on the sheet against PNGRB and Indian company/regulator disclosures; writes ref_shards/<PID>.json',
  phases: [
    { title: 'Research', detail: 'one subagent per ProjectID brief' },
  ],
}

const A = {"repo": "/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher", "staging": "batches/india-gas/staging/ref-sweep-operating", "model": "sonnet", "briefs": [{"pid": "P0904", "name": "Agartala Regional Gas Network", "n_units": 9}, {"pid": "P0906", "name": "Assam Regional Gas Network", "n_units": 3}, {"pid": "P0907", "name": "Barauni-Guwahati Gas Pipeline", "n_units": 5}, {"pid": "P0911", "name": "Cauvery Basin Gas Network", "n_units": 9}, {"pid": "P0912", "name": "Chainsa-Jhajjar-Hissar Gas Pipeline", "n_units": 8}, {"pid": "P0916", "name": "Dadri-Bawana-Nangal Gas Pipeline", "n_units": 3}, {"pid": "P0919", "name": "Dahej-Vijaipur Gas Pipeline (DVPL-I)", "n_units": 8}, {"pid": "P0920", "name": "East West Gas Pipeline (India)", "n_units": 1}, {"pid": "P0923", "name": "Gujarat Regional Gas Network", "n_units": 7}, {"pid": "P0924", "name": "Hazira-Ankleshwar Gas Pipeline", "n_units": 8}, {"pid": "P0925", "name": "Hazira-Vijaipur-Jagdishpur (HVJ) Gas Pipeline", "n_units": 8}, {"pid": "P0926", "name": "Heera-Uran Trunk Line (HUT)", "n_units": 8}, {"pid": "P0927", "name": "High Pressure Gujarat Gas Grid Network", "n_units": 6}, {"pid": "P0930", "name": "Jaigarh-Dabhol Gas Pipeline", "n_units": 9}, {"pid": "P0933", "name": "KG Basin Gas Pipeline", "n_units": 7}, {"pid": "P0934", "name": "Kochi-Koottanad-Bangalore-Mangalore Gas Pipeline", "n_units": 8}, {"pid": "P0937", "name": "Low Pressure Gujarat Gas Grid Network", "n_units": 1}, {"pid": "P0938", "name": "Mallavaram-Bhopal-Bhilwara-Vijaipur Gas Pipeline", "n_units": 9}, {"pid": "P0941", "name": "Mehsana-Bhatinda Gas Pipeline", "n_units": 9}, {"pid": "P0943", "name": "Mumbai Regional Natural Gas Pipeline Network", "n_units": 7}, {"pid": "P0944", "name": "Mumbai-Uran Trunk Line (MUT)", "n_units": 3}, {"pid": "P0953", "name": "Shahdol-Phulpur Gas Pipeline", "n_units": 9}, {"pid": "P0957", "name": "Vijaipur-Auraiya-Pulphur Gas Pipeline", "n_units": 3}, {"pid": "P1436", "name": "Rajasthan Gas Pipeline (Focus)", "n_units": 2}, {"pid": "P2210", "name": "Dahej-Koyali Refinery Gas Pipeline", "n_units": 1}, {"pid": "P2212", "name": "Dahej-Uran-Panvel-Dhabhol Gas Pipeline", "n_units": 8}, {"pid": "P3297", "name": "Vijaipur-Dadri Gas Pipeline (GREP-I)", "n_units": 9}, {"pid": "P3298", "name": "Dahej-Vijaipur Pipeline (DVPL-II)", "n_units": 9}, {"pid": "P3299", "name": "Vijaipur-Dadri Gas Pipeline (GREP-II)", "n_units": 9}, {"pid": "P3310", "name": "Duliajan-Numaligarh Gas Pipeline", "n_units": 1}, {"pid": "P3905", "name": "Dandewala-Gamnewala-RSEB Ramgarh Gas Pipeline", "n_units": 3}, {"pid": "P3906", "name": "Haridwar-Rishikesh-Dehradun Gas Pipeline", "n_units": 1}, {"pid": "P5533", "name": "Bhatinda-Gurdaspur Gas Pipeline", "n_units": 1}]}
const MODEL = A.model || 'sonnet'
const REPO = A.repo
const STG = A.staging

const contract = (b) => `You are a GEM pipeline ref-sweep researcher. Target: ProjectID ${b.pid} (${b.name}), an India gas pipeline row with Status = operating.

cd ${REPO} first. STG=${STG}

## Inputs (read them, in this order)
- Your brief: \`${STG}/ref_shards/_briefs/${b.pid}.json\` — your ${b.n_units} gap units (ref cells that are MISSING/UNRESOLVED, or whose existing link is dead). Each unit: ref_col, sheet_row, segment_name, value_cols, values, primary_value, current_ref.
- \`batches/india-gas/staging/register-crosswalk/staged_resolutions.json\` — the PNGRB register crosswalk ALREADY staged refs for many India rows. Read your PID's entries FIRST so you do not redo settled work, and so you know which of your units the register can answer.
- The deep-sweep audit shard \`${STG}/rows/${b.pid}.json\` — its researcher already found sources for this row; reuse and verify those leads before searching fresh.
- Seed leads: \`${STG}/wiki_citations.json\` (may have none for your PID) — leads ONLY, never a citation.

## Scope-specific guidance — India

**The sources exist; they were simply never cited.** India is the inverse of a thin-source country: these are real, well-documented, mostly GAIL/GSPL/ONGC-operated trunk lines. Treat UNRESOLVED as a last resort, not a default.

**Start with the regulator's own line-wise register.** PNGRB publishes a MONTHLY inventory of authorised natural-gas pipelines at \`https://pngrb.gov.in/data-bank/20260531-NGPL-MIS-Report.pdf\` (printed p.2, "PHYSICAL PROGRESS REPORT OF NATURAL GAS PIPELINE"). Per pipeline it gives entity, authorisation date, authorised length, authorised + design capacity (MMSCMD), operating length, under-construction length, target completion and states traversed — so it directly supports Length, Capacity, Status and often Owner. Fetch it with curl and read it with \`pdftotext -layout\`; url_verifier returns HTTP 200 + "value not found" on it (documented large-PDF false negative), so confirm the value locally and SAY SO in researcher_notes. Older editions for a dated claim: \`https://www.pngrb.gov.in/data-bank/NGPL-25062021.pdf\`, \`.../NGPL-20240626.pdf\`.

**Caveat: the register covers COMMON-CARRIER pipelines only.** Dedicated/tie-in lines (ONGC trunk lines, Duliajan-Numaligarh, refinery feeders, regional networks) sit inside its totals but are NOT itemised. Absence from the table is NOT evidence of anything.

**Independence caveat.** GEM's India numbers appear to DERIVE from PNGRB, and company reports often restate the same authorised figure. A PNGRB citation plus a company report repeating it may be ONE origin, not two — say so rather than claiming \`high\` on a shared lineage.

**Other productive sources:** GAIL (gailonline.com), GSPL/GSPC (gspcgroup.com), IOCL, ONGC, Petronet LNG, Pipeline Infrastructure Ltd, Gujarat Gas, IGGL, Assam Gas annual reports and investor presentations; PNGRB public notices and bid documents (\`pngrb.gov.in/pdf/public-notice/...\`, \`.../bid/...\`); PPAC (ppac.gov.in); MoPNG annual report and Indian Petroleum & Natural Gas Statistics (mopng.gov.in); the Comptroller & Auditor General (cag.gov.in) — CAG performance audits carry operational detail no press release does. Then Business Standard, The Hindu BusinessLine, Economic Times Energy, Mint, Moneycontrol, Pipeline & Gas Journal, Oil & Gas Journal. English coverage is good; Hindi/regional sources are fair game and count as independent (set source_language accordingly).

**Descriptive units (Fuel, PipelineType, Status) are still sourceable.** A source that describes the line as a natural-gas TRANSMISSION pipeline in operation supports \`Fuel = Gas\`, \`PipelineType = transmission\` and \`Status = operating\` at once. Cite the passage; do not invent a separate source per column.

**Authorisation date is NOT a commissioning year** — never support a StartYear from one.

## Standing rules (NON-NEGOTIABLE)
1. NEVER cite gem.wiki / globalenergymonitor.org, theodora.com, abarrelfull / any wikidot.com page. Read for leads only.
2. NEVER fabricate a URL. Nothing found → class_out "UNRESOLVED" + researcher_notes explaining what you searched.
3. Run EVERY url through the verifier before citing: \`python scripts/url_verifier.py "<url>" "<expected substring>" ["<more>"]\` — cite only on OK/200 AND token present. Use distinctive tokens (numbers, place names, the operator's name). Verifier false negatives are real: prose and equivalent units count ("commissioned in 2019" supports StartYear1 = 2019). If a URL fails on SSL/TLS but \`curl -sI\` returns 200, it is LIVE — say so.
4. Corroborate with ≥2 INDEPENDENT sources where possible. tier: high = ≥2 independent working+value-present; medium = 1 strong; low = 1 weak/partial.

## Task, per unit in your brief
Find independent sources that SUPPORT the RECORDED value(s) (\`values\` / \`primary_value\`) for that ref_col. For dead-link units, first try a web.archive.org snapshot of \`current_ref\` (it was the original support), then search fresh. NEVER propose refs for a DIFFERENT value — if what you find disagrees with the recorded value, set class_out "UNRESOLVED" and put the disagreement in researcher_notes (value changes route to a different workflow). Work ALL ${b.n_units} units; it is fine for several units to share one verified source when it genuinely supports each value.

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
      "source_language": "en",
      "researcher_notes": "<what supports the value; for archive snapshots note the original URL; for PNGRB note that you confirmed it locally with pdftotext; if unresolved, what you searched>" }
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
