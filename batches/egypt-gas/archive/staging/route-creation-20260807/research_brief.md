# Endpoint-research brief — Egypt gas §8 pass 2026-08-07 (new NA rows P8050–P8059)

You are researching START/END points + route-informing references for ten Egypt gas
pipeline rows that were added to GEM's GGIT tracker on 2026-08-05/06/07 by researcher
`NA` and currently read `RouteAccuracy = no route`, so candidate geometry can be drawn.
Work from the repo root
`/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher`.

You are ALSO doing a light critical review: these rows are brand new and unverified.
If the sheet's own Start/End text, name, or length looks internally inconsistent, say
so in `flags` — do not quietly "fix" it by picking convenient coordinates.

## Inputs

- Your PIDs' full sheet context:
  `batches/egypt-gas/staging/route-creation-20260807/new_rows_context.json`
  (keys are ProjectIDs; each value is the list of sheet rows for that PID, with the
  Arabic `OtherLanguagePrimaryPipelineName` — often the best clue to the real
  endpoints, since the English `StartLocation`/`EndPrefecture` cells are sometimes
  truncated, transliterated oddly, or duplicated.)
- `batches/egypt-gas/staging/route-creation-20260807/worklist.json` — per-PID sheet
  facts as the engine sees them.
- Seed source for most rows: **EGAS Annual Report 2018**,
  `https://egyptoil-gas.com/wp-content/uploads/2019/01/EGAS-Annual-Report-2018-EN.pdf`
  (download with `curl -A "Mozilla/5.0"`, read with `pdftotext -layout`; it has a
  national-grid pipeline table — find your line's row: name, length, diameter, year).
- **GASCO grid-expansion deck** (seed ref on P8055):
  `https://www.gasco.com.eg/wp-content/uploads/2024/12/National-Natural-Gas-Grid-Expansion-Projects.pdf`
- Petroleum Magazine (`petro-mag.org`) GASCO reports are a good second source:
  Nov 2025 issue `https://petro-mag.org/Uploads/Files/8485d495-066a-4039-af4c-1eb97a28c3ef.pdf`
  (GASCO section pp. 55–57), Dec 2024 issue
  `https://petro-mag.org/Uploads/Files/1db11fff-b2e2-445c-aa2f-a1c78dbd7c9b.pdf` (p. 94).
  Arabic text is kashida-justified: strip U+0640 and bidi control chars before searching.
- Egyptian Ministry of Petroleum news pages (`petroleum.gov.eg`) are cited on several
  rows — the `?utm_source=chatgpt.com` suffix on some seed URLs is junk, strip it.
- Sinai rows: EIB "Abr Sinai Onshore Gas Pipeline" EIA
  `https://www.eib.org/files/pipeline/20070088_eia1_en.pdf` (El-Tina East–El-Arish, 111 km).
- OSM/Overpass is a legitimate way to coordinate a named plant, station or town
  (cite the node/way id). Wikidata/Wikipedia coords are fine. Local gas-station and
  power-plant lists are fine.

## Hard rules (GEM standing rules — do not violate)

1. **NEVER use GEM sources** (gem.wiki, globalenergymonitor.org, any GEM surface) as
   evidence or as a ref.
2. **NEVER fabricate a URL or a coordinate.** Every lon/lat must come from geocoding a
   NAMED place/facility via a checkable source (OSM node/way id, Wikidata item,
   Wikipedia article coords, a paper/EIA map caption naming the site, a plant database
   entry, …) and must carry a `coord_basis` explaining exactly where it came from, plus
   an `evidence_url`.
3. **Banned source: abarrelfull** (any domain, `abarrelfull.wikidot.com` /
   `abarrelfull.co.uk`). Never cite it, not even alongside others. If a value appears
   only there, treat it as unsourced and chase the primary source it footnotes.
4. Aim for **2+ independent sources** per endpoint/fact; record what you found either
   way. The same wire story republished does not count as two.
5. **Verify every URL you output** with `python3 scripts/url_verifier.py <url>` (or note
   precisely why it could not be verified). Wayback snapshots are welcome *additions*,
   never swaps.
6. Do not edit anything outside the staging dir; your ONLY write is your results file.

## Output — write JSON to
`batches/egypt-gas/staging/route-creation-20260807/research_results_<group>.json`

A list, one object per PID:

```json
{
  "project_id": "P####",
  "resolved": true,
  "start": {"name": "...", "lon": 0.0, "lat": 0.0, "coord_basis": "...", "evidence_url": "..."},
  "end":   {"name": "...", "lon": 0.0, "lat": 0.0, "coord_basis": "...", "evidence_url": "..."},
  "route_refs": ["verified urls that inform the route"],
  "corridor_desc": "prose corridor description (which side of the Nile/canal, waypoints, what it parallels)",
  "facts": {"length_km": null, "diameter_in": null, "year": null, "source": "..."},
  "flags": ["duplicate-of:P####", "name-misread:...", "endpoint-mismatch:...", "length-implausible:..."],
  "notes": "what you searched, what agreed/disagreed, your confidence tier and why"
}
```

Use `"resolved": false` with whatever partial fields you have rather than guessing. A
named city/town is an acceptable endpoint anchor at reduced accuracy IF the line's
terminus is that settlement's gas station/plant and you say so in `coord_basis`; a
governorate, or "somewhere in Sinai", is NOT — that stays `resolved: false`.

Write the file even if most rows are unresolved. Report the straight-line distance
between your two endpoints and compare it to the sheet's `LengthKnownKm`: a
straight-line longer than the stated length, or a ratio worse than ~1.4x, is a signal
that you have the wrong endpoint — flag it.
