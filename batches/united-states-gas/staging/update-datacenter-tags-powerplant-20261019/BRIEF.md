# DataCenter re-tag under ruling 6, US gas, 2026-10-19 (brief for each research agent)

You re-judge the DataCenter field for a few GGIT rows (US gas pipelines in development, DataCenter blank today). Read your rows from `worklist.json` in this folder by project_id. Each row carries `prior_notes` from the two 2026-10-16 tag passes; start from them, do not repeat their dead ends, and re-judge under the rulings below.

## Rulings (Baird, docs/plans/2026-10-16_us-gas-datacenter-subfloor.md)

- Ruling 1 (loosened 2026-10-16): DataCenter = yes with a validated ref that names THIS pipeline or project and mentions data centers at all as a demand driver or a reason for the project (the filing, the developer, a shipper, EIA, or press). One of several drivers counts. Company-wide data center talk that is not about this project, talk only from opponents, or talk about another row leaves it blank.
- Ruling 6 (2026-10-18): a tie THROUGH A POWER PLANT counts. If the pipeline, lateral, or expansion supplies a gas plant (or a utility shipper's named plants), and the plant's own filings, its developer, or the utility tie THAT PLANT to data center load, DataCenter = yes. A named campus or customer is high specificity; data center load named among the plant's reasons is medium. Company-wide resource-plan talk about data centers, not about this plant, stays blank. One ref must name the pipeline; a second ref may carry the plant's data center tie. DataCenterNotes says how the two connect (the pipeline serves plant X; plant X is tied to data center load by source Z). Tag the expansion or lateral serving the plant, never a legacy mainline it hangs off.
- Ruling 7: big interstate expansions with such an indirect tie are included. Many FERC expansions name their shippers (Duke Energy, Georgia Power, Southern Company, TVA, Dominion, Entergy, Xcel, Ameren, and so on) and the plants they serve. Find the shipper or plant, then find whether that plant is tied to data center load.
- Ruling 9: US only.

## Method

1. Budget: about 4 to 6 web searches per row for group A, 2 to 4 for group B, more only when a lead appears. Pace searches a few seconds apart; if a search fails for quota, wait a minute and retry once, then record the row as unfinished in the ledger note ("search quota hit, not finished").
2. Look at: the FERC application or Federal Register notice (shippers, plants served), the sponsor's project page and earnings calls, the shipper utility's integrated resource plan or plant certificate case for the named plant, state commission dockets, the plant developer's releases, trade press (Pipeline and Gas Journal, Natural Gas Intelligence, RBN, Utility Dive, Data Center Dynamics), and the EIA pipeline projects workbook (sources/eia_pipeline_projects/raw/, cite the dated release URL https://www.eia.gov/naturalgas/pipelines/<file>).
3. A blocked page is not a dead end: `python scripts/fetch.py <url> --head 4000`, then the Wayback copy.
4. Verify EVERY ref you propose: `python scripts/url_verifier.py "<url>" "<substring>"` (use a phrase that is on the page, e.g. "data center"). The substring check is a screen; you read the page and make the call. Never cite GEM, gem.wiki, or GOGPT. Never fabricate or guess a URL; only cite URLs you loaded.

## Output: write `shards/tags-<N>.json` (N is given in your task), then reply with one line per row

```json
{"chunk": N, "records": [ ...one per yes row... ], "ledger": [ ...one per row, all rows... ]}
```

Ledger entry: `{"project_id": "P....", "outcome": "yes" | "blank_noted", "note": "<plain sentence or two>"}`. For blank_noted say what was checked and what was not found, in words.

Record (yes rows only), exactly this shape:

```json
{"project_id": "P7855", "pipeline_name": "<from worklist>", "segment_name": "<from worklist>", "sheet_row": 0,
 "class_in": "FILL", "class_out": "REFS_ADDED", "ref_col": "DataCenter [ref]",
 "value_cols": ["DataCenter", "DataCenterNotes"], "primary_value_col": "DataCenter",
 "values": {"DataCenter": "yes", "DataCenterNotes": "<how the pipeline ties to data centers, naming the plant and source>"},
 "primary_value": "yes", "current_ref": "", "proposed_refs": ["<url naming the pipeline>", "<url carrying the plant tie, if separate>"],
 "verifications": [{"url": "...", "ok": true, "contains_value": true, "name_found": true, "note": "<what the page says>"}],
 "tier": "high" | "medium", "independent": false, "source_language": "en",
 "researcher_notes": "<plain-language note for Baird>", "action": "change"}
```

`independent` is true only when two refs from different publishers each support the tag. `tier` is high for a named campus or customer and medium for data center load named among the plant's reasons.

## Notes style (Baird's rule for anything a person reads)

Plain and short. One idea per sentence. Name sources by what they are ("a Southern Company Georgia commission filing from March 2026"), not by role labels. No repo jargon (shard, lane, tier, staged, ruling numbers) in DataCenterNotes or researcher_notes. Spell out abbreviations on first use. No em-dashes, arrows, or parenthetical asides. American spelling, serial comma.
