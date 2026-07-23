export const meta = {
  name: 'egypt-gas-qc-research',
  description: 'Leg 3 of the Egypt gas QC packet: targeted research on rows where the sheet itself is suspect (sheet\u2194wiki disagreements, route-vs-length conflicts, missing start years). One skeptical subagent per flagged row; confirms or refutes the SPECIFIC flagged disagreement with >=2 independent sources. Read-and-stage only, never auto-applies.',
  phases: [
    { title: 'Research', detail: 'one subagent per flagged row \u2014 resolve the specific flagged disagreement' },
  ],
}

// args baked from batches/staging/qc-gas-egypt/worklist.json (mode qc_research).
// Each row carries the specific flags (source: wiki_alignment SHEET_SUSPECT /
// route_integrity / mechanical) that targeted research must confirm or refute.
const A = {
 "repo": "/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher",
 "staging": "batches/staging/qc-gas-egypt",
 "commodity": "gas",
 "country": "Egypt",
 "csv": "data/GGIT_gas_snapshot_20260715.csv",
 "owners_csv": "data/GEM_operators_owners_snapshot_20260715.csv",
 "rows": [
  {
   "project_id": "P0436",
   "sheet_row": 1236,
   "pipeline_name": "Arab Gas Pipeline",
   "segment_name": "Arish-Taba Gas Pipeline",
   "status": "operating",
   "wiki": "https://www.gem.wiki/Arab_Gas_Pipeline",
   "flags": [
    {
     "source": "wiki_alignment",
     "field": "Diameter",
     "detail": "multi-segment wiki page unions 'diameter' to 24, 26, 36 in; sheet has 36 in — verify whether the sheet row should carry every segment's value (never cite the wiki)",
     "sheet_value": "36",
     "wiki_value": "24 inches; 26 inches; 36 inches"
    },
    {
     "source": "wiki_alignment",
     "field": "Operator",
     "detail": "multi-segment wiki page unions 'operator' to egyptian natural gas; jordanian egyptian fajr natural gas; syrian petroleum; sheet has egyptian natural gas — verify whether the sheet row should carry every segment's value (never cite the wiki)",
     "sheet_value": "Egyptian Natural Gas Co",
     "wiki_value": "Egyptian Natural Gas Company (GASCO); Jordanian Egyptian Fajr Natural Gas Company; Syrian Petroleum Company"
    },
    {
     "source": "wiki_alignment",
     "field": "Owner",
     "detail": "multi-segment wiki page unions 'owner' to egyptian natural gas holding; jordanian egyptian fajr natural gas; syrian petroleum; sheet has egyptian natural gas holding — verify whether the sheet row should carry every segment's value (never cite the wiki)",
     "sheet_value": "Egyptian Natural Gas Holding Co [100.%]",
     "wiki_value": "Egyptian Natural Gas Holding Company; Jordanian Egyptian Fajr Natural Gas Company; Syrian Petroleum Company"
    }
   ]
  },
  {
   "project_id": "P0473",
   "sheet_row": 1107,
   "pipeline_name": "Cyprus–Egypt Gas Pipeline",
   "segment_name": "",
   "status": "proposed",
   "wiki": "https://www.gem.wiki/Cyprus%E2%80%93Egypt_Gas_Pipeline",
   "flags": [
    {
     "source": "route_integrity",
     "field": "length_ratio",
     "detail": "drawn route is 215 km but the sheet says 310 km (ratio 0.69, allowed 0.75–1.33) — wrong route, wrong length value, or a partial segment drawn",
     "measured": "geodesic 215 km (ratio 0.69)",
     "expected": "LengthKnownKm = 310 km"
    }
   ]
  },
  {
   "project_id": "P0474",
   "sheet_row": 2252,
   "pipeline_name": "Obaiyed-Amreya Northern Gas Pipeline",
   "segment_name": "Obaiyed-Tarek Gas Pipeline",
   "status": "operating",
   "wiki": "https://www.gem.wiki/Obaiyed-Amreya_Northern_Gas_Pipeline",
   "flags": [
    {
     "source": "wiki_alignment",
     "field": "Diameter",
     "detail": "multi-segment wiki page unions 'diameter' to 26, 32, 34 in; sheet has 32 in — verify whether the sheet row should carry every segment's value (never cite the wiki)",
     "sheet_value": "32",
     "wiki_value": "26 in; 32 in; 34 in"
    },
    {
     "source": "mechanical",
     "field": "Date_logic",
     "detail": "Status=operating but no StartYear1"
    }
   ]
  },
  {
   "project_id": "P3938",
   "sheet_row": 1899,
   "pipeline_name": "Badr El Din Spur Gas Pipelines",
   "segment_name": "Badr El Din Spur (2)",
   "status": "operating",
   "wiki": "https://www.gem.wiki/Badr_El_Din_Spur_Gas_Pipelines",
   "flags": [
    {
     "source": "wiki_alignment",
     "field": "Diameter",
     "detail": "multi-segment wiki page unions 'diameter' to 16, 20 in; sheet has 16 in — verify whether the sheet row should carry every segment's value (never cite the wiki)",
     "sheet_value": "16.00",
     "wiki_value": "16 in; 20 in"
    },
    {
     "source": "mechanical",
     "field": "Date_logic",
     "detail": "Status=operating but no StartYear1"
    }
   ]
  },
  {
   "project_id": "P6033",
   "sheet_row": 3880,
   "pipeline_name": "Damietta–SEGAS Pipeline",
   "segment_name": "",
   "status": "operating",
   "wiki": "https://www.gem.wiki/Damietta%E2%80%93SEGAS_Pipeline",
   "flags": [
    {
     "source": "wiki_alignment",
     "field": "Operator",
     "detail": "sheet Operator is blank but wiki shows 'Egyptian Natural Gas Company (GASCO)' — candidate sheet fill; verify independently (never cite the wiki)",
     "sheet_value": "",
     "wiki_value": "Egyptian Natural Gas Company (GASCO)"
    }
   ]
  },
  {
   "project_id": "P6037",
   "sheet_row": 2298,
   "pipeline_name": "Al Gamil–Damietta Gas Pipeline",
   "segment_name": "",
   "status": "operating",
   "wiki": "https://www.gem.wiki/Al_Gamil%E2%80%93Damietta_Gas_Pipeline",
   "flags": [
    {
     "source": "mechanical",
     "field": "Date_logic",
     "detail": "Status=operating but no StartYear1"
    }
   ]
  },
  {
   "project_id": "P6687",
   "sheet_row": 2199,
   "pipeline_name": "Obaiyed-Amreya Northern Gas Pipeline",
   "segment_name": "Obaiyed Spurline",
   "status": "operating",
   "wiki": "https://www.gem.wiki/Obaiyed-Amreya_Northern_Gas_Pipeline",
   "flags": [
    {
     "source": "wiki_alignment",
     "field": "Diameter",
     "detail": "multi-segment wiki page unions 'diameter' to 26, 32, 34 in; sheet has 26 in — verify whether the sheet row should carry every segment's value (never cite the wiki)",
     "sheet_value": "26",
     "wiki_value": "26 in; 32 in; 34 in"
    },
    {
     "source": "mechanical",
     "field": "Date_logic",
     "detail": "Status=operating but no StartYear1"
    }
   ]
  },
  {
   "project_id": "P6692",
   "sheet_row": 2126,
   "pipeline_name": "Qasr-Shams Gas Pipeline ",
   "segment_name": "",
   "status": "operating",
   "wiki": "https://www.gem.wiki/Qasr-Shams_Gas_Pipeline",
   "flags": [
    {
     "source": "mechanical",
     "field": "Date_logic",
     "detail": "Status=operating but no StartYear1"
    }
   ]
  },
  {
   "project_id": "P6697",
   "sheet_row": 3979,
   "pipeline_name": "South Valley Gas Pipeline",
   "segment_name": "Dahshour-Al Kurimat Gas Pipeline",
   "status": "operating",
   "wiki": "https://www.gem.wiki/South_Valley_Gas_Pipeline",
   "flags": [
    {
     "source": "wiki_alignment",
     "field": "Capacity",
     "detail": "sheet Capacity is blank but wiki shows '12 billion cubic meters per year' — candidate sheet fill; verify independently (never cite the wiki)",
     "sheet_value": "",
     "wiki_value": "12 billion cubic meters per year"
    },
    {
     "source": "wiki_alignment",
     "field": "Diameter",
     "detail": "multi-segment wiki page unions 'diameter' to 30, 32, 36 in; sheet has 36 in — verify whether the sheet row should carry every segment's value (never cite the wiki)",
     "sheet_value": "36",
     "wiki_value": "32; 36; 36,32,32,32,32,30 inches"
    }
   ]
  },
  {
   "project_id": "P6699",
   "sheet_row": 3981,
   "pipeline_name": "South Valley Gas Pipeline",
   "segment_name": "Beni Suef-Abu qurqas Gas pipeline",
   "status": "operating",
   "wiki": "https://www.gem.wiki/South_Valley_Gas_Pipeline",
   "flags": [
    {
     "source": "wiki_alignment",
     "field": "Operator",
     "detail": "sheet Operator is blank but wiki shows 'Nile Valley Gas Company' — candidate sheet fill; verify independently (never cite the wiki)",
     "sheet_value": "",
     "wiki_value": "Nile Valley Gas Company"
    }
   ]
  },
  {
   "project_id": "P6700",
   "sheet_row": 3982,
   "pipeline_name": "South Valley Gas Pipeline",
   "segment_name": "Abu qurqas-Asyut Gas pipeline",
   "status": "operating",
   "wiki": "https://www.gem.wiki/South_Valley_Gas_Pipeline",
   "flags": [
    {
     "source": "wiki_alignment",
     "field": "Capacity",
     "detail": "sheet Capacity is blank but wiki shows '12 billion cubic meters per year' — candidate sheet fill; verify independently (never cite the wiki)",
     "sheet_value": "",
     "wiki_value": "12 billion cubic meters per year"
    },
    {
     "source": "wiki_alignment",
     "field": "Diameter",
     "detail": "multi-segment wiki page unions 'diameter' to 30, 32, 36 in; sheet has 32 in — verify whether the sheet row should carry every segment's value (never cite the wiki)",
     "sheet_value": "32",
     "wiki_value": "32; 36; 36,32,32,32,32,30 inches"
    }
   ]
  },
  {
   "project_id": "P6701",
   "sheet_row": 3983,
   "pipeline_name": "South Valley Gas Pipeline",
   "segment_name": "Asyut-Girga Gas pipeline",
   "status": "operating",
   "wiki": "https://www.gem.wiki/South_Valley_Gas_Pipeline",
   "flags": [
    {
     "source": "wiki_alignment",
     "field": "Operator",
     "detail": "sheet Operator is blank but wiki shows 'Nile Valley Gas Company' — candidate sheet fill; verify independently (never cite the wiki)",
     "sheet_value": "",
     "wiki_value": "Nile Valley Gas Company"
    }
   ]
  },
  {
   "project_id": "P6704",
   "sheet_row": 3985,
   "pipeline_name": "Raven-Al Ameryia Gas Pipeline",
   "segment_name": "",
   "status": "operating",
   "wiki": "https://www.gem.wiki/Raven-Al_Ameryia_Gas_Pipeline",
   "flags": [
    {
     "source": "wiki_alignment",
     "field": "Operator",
     "detail": "sheet Operator is blank but wiki shows 'Egyptian Natural Gas Company (GASCO)' — candidate sheet fill; verify independently (never cite the wiki)",
     "sheet_value": "",
     "wiki_value": "Egyptian Natural Gas Company (GASCO)"
    }
   ]
  },
  {
   "project_id": "P7574",
   "sheet_row": 4167,
   "pipeline_name": "New Administration Capital PS Gas Pipeline",
   "segment_name": "",
   "status": "operating",
   "wiki": "https://www.gem.wiki/New_Administration_Capital_PS_Gas_Pipeline",
   "flags": [
    {
     "source": "mechanical",
     "field": "Date_logic",
     "detail": "Status=operating but no StartYear1"
    }
   ]
  }
 ]
}

const REPO = A.repo
const STAGING = A.staging
const COMMODITY = A.commodity || 'gas'
const COUNTRY = A.country || ''
const MODEL = A.model || 'sonnet'   // dispatch-time choice, never pinned
const ROWS = A.rows
if (!Array.isArray(ROWS) || !ROWS.length) throw new Error('qc-research needs args.rows from worklist.json')

const contract = (row) => `You are a meticulous, skeptical GEM pipeline researcher. Resolve the SPECIFIC QC
flags below for one ${COUNTRY} ${COMMODITY} pipeline row: ProjectID ${row.project_id}
(${row.pipeline_name}${row.segment_name ? ' / ' + row.segment_name : ''}, status=${row.status}, sheet row ${row.sheet_row}).
This is NOT a full re-audit \u2014 the row was already deep-swept. Each flag is a concrete suspected error
in the GEM sheet. Your job: decide, with independent evidence, whether the SHEET is right or wrong on
each flagged point, and stage the fix.

cd ${REPO} first.

## The flags to resolve (nothing else)
${JSON.stringify(row.flags, null, 1)}

Flag semantics:
- source=wiki_alignment: the row's gem.wiki page disagrees with the sheet (sheet_value vs wiki_value).
  The wiki is a LEAD, never evidence \u2014 verify independently which side is right. If the row is one
  SEGMENT of a multi-segment wiki page, the sheet row should carry the SEGMENT's own value; a page-level
  union that differs is then fine (recommend "sheet correct \u2014 no change; wiki covers all segments").
- source=route_integrity: the drawn GeoJSON route's geodesic length conflicts with the sheet's length.
  Research the pipeline's actual routing/length. You cannot fix geometry \u2014 a route fix is a separate
  human PR \u2014 but decide whether the LENGTH VALUE is wrong (stage a fill) or the drawn route is
  wrong/partial (say so in the recommendation).
- source=mechanical Date_logic "Status=operating but no StartYear1": find the year the pipeline
  actually started up; stage it as a fill with verified refs. If genuinely unfindable, say so \u2014 never guess.

## Row lookup
Current sheet values: python3 -c "import pandas as pd; df=pd.read_csv('${A.csv}',header=2,dtype=str,low_memory=False).fillna(''); r=df[df['ProjectID']=='${row.project_id}']; import json; print(r.to_dict('records')[0])"
Operator/Owner live on the SEPARATE operators/owners tab: '${A.owners_csv}' (header=1, ProjectID-keyed).
The row's gem.wiki page (READ for leads, NEVER cite): ${row.wiki || '(none)'}

## Standing rules (NON-NEGOTIABLE)
1. NEVER cite gem.wiki / globalenergymonitor.org, theodora.com, or any wikidot.com page.
2. NEVER fabricate a URL. If you cannot verify, say so in researcher_notes \u2014 no invented links.
3. Run EVERY url through the verifier before you cite it:
   python scripts/url_verifier.py "<url>" "<expected substring>" [more] \u2192 cite only on OK/200 + token present.
4. Corroborate with >=2 INDEPENDENT sources (separate origins, not one wire story reprinted).
   tier: high = >=2 independent working+value-present; medium = 1 strong; low = 1 weak/conflicting.
   Search Arabic-language sources too where English is thin (this is Egypt \u2014 try the Arabic name).

## Output \u2014 write a shard, then return a summary
Write ${STAGING}/rows/${row.project_id}.json = ONE JSON object exactly shaped:
{
  "project_id": "${row.project_id}", "pipeline_name": ${JSON.stringify(row.pipeline_name)},
  "sheet_row": ${row.sheet_row}, "wiki": ${JSON.stringify(row.wiki || '')},
  "validity": [
    { "segment_name": ${JSON.stringify(row.segment_name || '')}, "verdict": "confirmed (caveat)|concern",
      "concern_type": "attribution|spec|none",
      "recommendation": "<the decision per flag: 'sheet correct \u2014 update wiki to X' / 'sheet wrong \u2014 set <col>=X' / 'drawn route partial \u2014 needs routes-repo PR' / ...>",
      "researcher_notes": "<what you checked, what independent sources say vs the sheet vs the wiki, your reasoning>",
      "proposed_refs": ["https://...verified..."], "tier": "high|medium|low",
      "independent": true, "source_language": "en|ar" }
  ],
  "fills": [
    { "segment_name": ${JSON.stringify(row.segment_name || '')}, "sheet_row": ${row.sheet_row},
      "ref_col": "<exactly as in the CSV header, e.g. 'StartYear1 [ref]' / 'Operator [ref]'>",
      "value_cols": ["<col>"], "primary_value_col": "<col>", "values": {"<col>": "<val>"},
      "primary_value": "<val>", "proposed_refs": ["https://...verified..."],
      "verifications": [{"url":"https://...","ok":true,"contains_value":true}],
      "class_out": "REFS_ADDED|UNRESOLVED", "tier": "high|medium|low", "independent": true,
      "source_language": "en|ar", "researcher_notes": "<why this value / source>" }
  ],
  "summary": "<one line>"
}
Emit ONE validity object PER FLAG (verdict "confirmed (caveat)" + concern_type "none" when the sheet
is right; "concern" when the sheet is wrong or you cannot resolve it). Stage a fills[] object ONLY
when the sheet value should change or be filled AND you have verified refs \u2014 no orphan value/ref
pairs, no fill without a ref. An Operator/Owner fill targets the operators/owners tab (note that in
researcher_notes). Before finishing run:
python3 -c "import json; json.load(open('${STAGING}/rows/${row.project_id}.json'))"
Return ONLY a 2-line summary: your per-flag decisions, and any UNRESOLVED. The shard file is the
deliverable, not your message.`

phase('Research')
log(`Targeted QC research on ${ROWS.length} flagged ${COUNTRY} ${COMMODITY} rows, one subagent each.`)
const results = await parallel(ROWS.map(row => () =>
  agent(contract(row), { label: `qc:${row.project_id}`, phase: 'Research', agentType: 'general-purpose', model: MODEL })
))
const done = results.filter(Boolean).length
log(`Research complete: ${done}/${ROWS.length} subagents returned. Shards in ${STAGING}/rows/`)
return { researched: done, total: ROWS.length }
