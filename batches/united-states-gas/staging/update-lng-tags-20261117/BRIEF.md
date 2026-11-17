# LNG terminal tags, US gas, 2026-11-17 (brief for each research agent)

You judge three Gas tab fields for a few GGIT rows and stage what you find with a source. Read your rows from `worklist.json` in this folder by `project_id`. Each row carries its current values (`current`), its existing refs, and the EIA Natural Gas Pipeline Projects entries matched to it (`eia`, with EIA's notes, demand served, and the names used in press releases). Terminal names to use are in `lng_terminals.json` (GEM's LNG terminal tracker names for the US, Mexico, and Canada).

The fields:

- `AssociatedWithLNGExports`: `export`, `import`, or blank, never `no`. (Changed from `yes` or blank on 17 November 2026, after the agents ran; their `yes` became `export`.)
- `AssociatedLNGTerminal`: the terminal name or names, comma and space separated, written exactly as `lng_terminals.json` names them (`Sabine Pass LNG Terminal`, `Corpus Christi LNG Terminal`). If the terminal is not in that file, write the name the source uses plus "LNG Terminal" and say so in your note.
- `AssociatedLNGNotes`: one to three plain sentences on why the pipeline is tied to the terminal, naming the source for each fact.
- One ref column, `AssociatedLNG [ref]`, holds the URLs for all three.

## Rules (Baird 2026-11-17)

- **`AssociatedWithLNGExports = export` when a validated ref names this pipeline, segment, or expansion project and ties it to LNG export.** The tie can be any of: it delivers gas into an LNG export terminal or a header built for one; it was built or expanded to carry feedgas for LNG export; an LNG exporter or terminal is a named shipper, anchor customer, or the reason in the filing; or the source names LNG exports among the demand drivers for this project. Upstream supply lines count (a Permian or Haynesville takeaway line built partly for Gulf Coast LNG feedgas is yes), as long as the source ties THIS project to LNG.
- Terminals in Mexico that export US gas (Costa Azul, Saguaro Energia, Mexico Pacific, AMIGO, Vista Pacifico, and similar) count as US LNG exports.
- **Leave it blank with a ledger note** when the LNG talk is company-wide and not about this project, comes only from opponents, or is about another row or system. A tie guessed from a line's location or name is not a tie.
- **Mainline vs expansion.** When the source ties an expansion or lateral to LNG, tag that expansion or lateral row, not the legacy mainline it hangs off. Tag a mainline or main segment only when the source says that line itself delivers gas to the terminal.
- **Import terminals.** A pipeline built for an LNG import terminal (Cove Point, Elba Island, Lake Charles, Everett, Northeast Gateway, and so on) gets the terminal name in `AssociatedLNGTerminal`, a note, and the flag `import`, which becomes `export` when a source also ties the line to exports, for example after the terminal added liquefaction.
- **Existing values.** A flag or a terminal name already on the sheet is never removed or cleared. If you confirm it, stage a record with the same value plus the ref and a note (this is still useful output). If you cannot find support, record `existing_unsupported` in the ledger with what you searched, and stage nothing. If a terminal cell is clearly wrong (a URL, the word `yes`, or a terminal in another country such as `Wuhu LNG` on a US line), stage the corrected terminal name with a ref and put the old text in `researcher_notes`. If you find more terminals than the cell lists, stage the full list, keeping the existing names.
- One validated ref is enough. Take a second source only if it is cheap.

## Method

1. **Group A rows** (likely LNG ties): about 3 to 5 web searches per row, more only when a lead appears. **Group B rows**: start with the EIA text and the existing refs, then one or two searches (for example `"<pipeline name>" LNG`); stop when nothing turns up.
2. Look at: EIA's text in the worklist (cite the dated release URL in `cite_url`, for example `https://www.eia.gov/naturalgas/pipelines/EIA-NaturalGasPipelineProjectsOct2026.xlsx`, only when EIA's own notes or demand-served text state the LNG tie), the operator's project page and press releases, the FERC application or order or the Federal Register notice (shippers and delivery points), the terminal developer's releases (feedgas supply deals name pipelines), state regulator filings such as the Texas Railroad Commission, and trade press (Natural Gas Intelligence, Pipeline and Gas Journal, RBN Energy, LNG Prime, Reuters).
3. Pace searches a few seconds apart. If a search fails for quota, wait a minute and retry once. If it fails again, record the row as `unfinished` in the ledger ("search quota hit, not finished").
4. A blocked page is not a dead end: `python scripts/fetch.py <url> --head 4000`, then the Wayback copy.
5. Verify EVERY ref you propose: `python scripts/url_verifier.py "<url>" "<phrase on the page>"`. Read the page and make the call yourself; the substring check is only a screen. Never cite GEM, gem.wiki, or GOGPT, or the banned hosts. Never guess or build a URL; cite only URLs you loaded.

## Output

Write `shards/lng-<CHUNK>.json` (CHUNK is given in your task), then run `python batches/united-states-gas/staging/update-lng-tags-20261117/check_shard.py <CHUNK>` and fix anything it reports. Reply with one short line per row.

```json
{"chunk": "<CHUNK>", "records": [ ...one per row you stage... ], "ledger": [ ...one per row, every row in your chunk... ]}
```

Ledger entry: `{"project_id": "P....", "outcome": "yes" | "terminal_only" | "confirmed_existing" | "existing_unsupported" | "blank_noted" | "unfinished", "note": "<plain sentence or two: what was checked and what was or was not found>"}`. `terminal_only` is an import-terminal tie (flag `import`). `confirmed_existing` is a staged record that keeps the sheet's values and adds a ref.

Record shape (rows with outcome yes, terminal_only, or confirmed_existing):

```json
{"project_id": "P3663", "pipeline_name": "<from worklist>", "segment_name": "<from worklist>", "sheet_row": 0,
 "class_in": "FILL", "class_out": "REFS_ADDED", "ref_col": "AssociatedLNG [ref]",
 "value_cols": ["AssociatedWithLNGExports", "AssociatedLNGTerminal", "AssociatedLNGNotes"],
 "primary_value_col": "AssociatedWithLNGExports",
 "values": {"AssociatedWithLNGExports": "export", "AssociatedLNGTerminal": "Commonwealth LNG Terminal",
            "AssociatedLNGNotes": "<why the pipeline is tied to the terminal, naming the source>"},
 "primary_value": "export", "current_ref": "", "proposed_refs": ["<url naming the pipeline and the LNG tie>"],
 "verifications": [{"url": "...", "ok": true, "contains_value": true, "name_found": true, "note": "<what the page says>"}],
 "tier": "high" | "medium" | "low", "independent": false, "source_language": "en",
 "researcher_notes": "<plain-language note for Baird>", "action": "change"}
```

- `values` always holds all three columns. Leave `AssociatedLNGTerminal` as `""` only when no source names a terminal (an upstream line feeding Gulf Coast LNG in general), and set `AssociatedWithLNGExports` to `import` on a `terminal_only` record tied to an import terminal.
- `tier`: high when the ref names this pipeline and states the terminal or the LNG export purpose directly; medium when LNG exports are one of several demand drivers named for the project, or the tie runs through a shipper; low when the ref is weak or only partly fits the row.
- `independent` is true only when two refs from different publishers each support the tie.

## Notes style (Baird's rule for anything a person reads)

Plain and short. One idea per sentence. Name sources by what they are ("a Kinder Morgan press release from March 2024", "a FERC order from 2019"), not by role labels. No repo jargon (shard, tier, staged, worklist, ruling) in `AssociatedLNGNotes` or `researcher_notes`. Spell out abbreviations on first use, except LNG. No em-dashes, arrows, or parenthetical asides. American spelling, serial comma.
