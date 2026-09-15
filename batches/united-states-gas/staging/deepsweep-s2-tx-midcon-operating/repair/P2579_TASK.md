# Re-research task — P2579 Northern Natural Gas Pipeline, "Main Line"

The previous pass staged 10 values for this row citing `https://www.eia.gov/naturalgas/data.php`.
That citation was **withdrawn as fabricated attribution**: EIA's Natural Gas Pipeline Projects
workbook carries only individual PROJECTS (expansions, laterals, compressor stations), never
system-level attributes. Do NOT cite EIA for any of the values below — it does not state them.

## The row (GGIT sheet, ProjectID P2579)
PipelineName `Northern Natural Gas Pipeline`, SegmentName `Main Line`, Status `operating`,
StartYear1 `1930`, Capacity `6300.00 MMcf/d`, LengthKnown `14300.00 mi`,
StartState/Province `Texas`, EndState/Province `Illinois, Wisconsin, Minnesota, Michigan`,
Owner `Northern Natural Gas [100.%]`.

## Units owed (each is MISSING_REF — a value is on the sheet, the [ref] cell is empty)
Status, Fuel, PipelineType, Start (StartYear1), Capacity, Length, Location, Operator, Owner.

Rule 4(e) applies to every one: it ends as `class_out="REFS_ADDED"` carrying the SAME value when
sources agree (a source agreeing within rounding IS a ref — note the delta), or as `UNRESOLVED`
whose notes say exactly what was searched. "Confirmed as recorded" in prose only is a failure.

## Source ladder for a system-level US interstate pipeline — use these, in order
1. **PHMSA** — the operator's annual report / National Pipeline Mapping System operator page
   gives system mileage (`phmsa.dot.gov`, `npms.phmsa.dot.gov`).
2. **FERC Form 2** annual report for Northern Natural Gas Company (system statistics).
3. **The operator's own site** — `northernnaturalgas.com` (informational postings, system map,
   about/fact-sheet pages give miles, Bcf/d capacity, states served, founding year).
4. **Berkshire Hathaway Energy / BHE 10-K** — Northern Natural Gas is a BHE subsidiary; the 10-K
   states mileage, design capacity and the ownership chain. `sec.gov` EDGAR.
5. Dated trade press, only as a second source, never as the first.

## Hard rules
- **Never cite GEM** (gem.wiki, globalenergymonitor.org). Never cite abarrelfull, theodora.com,
  yingdodo.com.
- **Never fabricate a URL.** Every URL must pass `python scripts/url_verifier.py --name "<pipeline
  name>" <url> "<expected substring>"` before you stage it. Paste the verifier's result into the
  `verifications[]` entry (`ok`, `contains_value`, `name_found`, `note`).
- A blocked fetch (403/Cloudflare/garbled PDF) is a TOOLING failure, not evidence: escalate with
  `curl -sL -A 'Mozilla/5.0'`, the www/bare host form, `web.archive.org/web/<ts>/<url>`, or
  `curl -o` + `pdftotext -layout`. Only after that may you call a source unreachable, and then say
  what you tried.
- **Two independent PUBLISHERS are required for `tier: "high"` and `independent: true`.** One
  publisher (or a page plus its own Wayback snapshot) is `medium` at best. Do not over-claim — the
  merge re-derives this and a false claim is worse than an honest `medium`.
- Owner vs Operator: Northern Natural Gas Company is the operator; state the corporate parent
  precisely and cite the filing that says it. Do not assert a corporate relationship no source states.

## Output
Write **ONLY** `batches/united-states-gas/staging/deepsweep-s2-tx-midcon-operating/repair/P2579_fills.json`.
Do NOT touch `rows/P2579.json` — the orchestrator merges your file.

Format: a JSON list; one object per unit:
```json
[{"ref_col":"Length [ref]","value_cols":["LengthKnown","LengthKnownUnits"],
  "values":{"LengthKnown":"14300.00","LengthKnownUnits":"mi"},
  "primary_value_col":"LengthKnown","primary_value":"14300.00",
  "class_out":"REFS_ADDED","tier":"medium","independent":false,
  "proposed_refs":["https://..."],
  "verifications":[{"url":"https://...","ok":true,"contains_value":true,"name_found":true,
                    "note":"what the page literally says, with the figure quoted"}],
  "source_language":"en",
  "researcher_notes":"what was searched, which sources agree, any delta from the sheet"}]
```
Cover all 9 units. Report the count of REFS_ADDED vs UNRESOLVED when you finish.
