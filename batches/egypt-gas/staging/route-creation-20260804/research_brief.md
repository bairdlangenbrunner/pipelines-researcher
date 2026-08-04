# Endpoint-research brief — Egypt gas §8 pass 2026-08-04

You are researching START/END points + route-informing references for Egypt gas
pipelines that have `RouteAccuracy = no route` on GEM's GGIT tracker, so candidate
geometry can be drawn. Work from the repo root
`/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher`.

## Inputs

- Your PIDs' full sheet context: `batches/egypt-gas/staging/route-creation-20260804/new_rows_context.json`
  (also `worklist.json` in the same dir — per-PID prior suggestions if present).
- Seed source for most rows: EGAS Annual Report 2018,
  `https://egyptoil-gas.com/wp-content/uploads/2019/01/EGAS-Annual-Report-2018-EN.pdf`
  (download with curl -A "Mozilla/5.0", read with pdftotext -layout; it has a
  national-grid pipeline table — find your line's row: name, length, diameter, year).
- Petroleum Magazine (petro-mag.org) GASCO reports are a good second source:
  Nov 2025 issue PDF `https://petro-mag.org/Uploads/Files/8485d495-066a-4039-af4c-1eb97a28c3ef.pdf`
  (GASCO section pp. 55–57), Dec 2024 issue PDF
  `https://petro-mag.org/Uploads/Files/1db11fff-b2e2-445c-aa2f-a1c78dbd7c9b.pdf` (p. 94).
  Arabic text is kashida-justified: strip U+0640 and bidi control chars before searching.
- Useful for Sinai rows: EIB "Abr Sinai Onshore Gas Pipeline" EIA
  `https://www.eib.org/files/pipeline/20070088_eia1_en.pdf` (El-Tina East–El-Arish, 111 km).

## Hard rules (GEM standing rules — do not violate)

1. NEVER use GEM sources (gem.wiki, globalenergymonitor.org) as evidence or refs.
2. NEVER fabricate a URL or a coordinate. Every lon/lat must come from geocoding a
   NAMED place/facility via a checkable source (OSM/Overpass node-way id, Wikimapia id,
   Wikipedia article coords, a paper/EIA map caption naming the site, etc.) and carry a
   `coord_basis` explaining exactly where it came from, plus an `evidence_url`.
3. Banned source: abarrelfull (any domain). Ignore anything only it claims.
4. Aim for 2+ independent sources per endpoint/fact; record what you found either way.
5. Verify every URL you output with `python3 scripts/url_verifier.py <url>` (or note
   precisely why it could not be verified). Wayback snapshots are welcome additions.
6. Do not edit anything outside the staging dir; your ONLY write is your results file.

## Output — write JSON to
`batches/egypt-gas/staging/route-creation-20260804/research_results_<group>.json`

A list, one object per PID:

```json
{
  "project_id": "P####",
  "resolved": true/false,           // true = both endpoints have defensible lon/lat
  "start": {"name": "...", "lon": 0.0, "lat": 0.0, "coord_basis": "...", "evidence_url": "..."},
  "end":   {... same ...},
  "route_refs": ["verified urls that inform the route"],
  "corridor_desc": "prose corridor description (which side of the Nile/canal, waypoints)",
  "facts": {"length_km": null, "diameter_in": null, "year": null, "source": "..."},
  "flags": ["duplicate-of:P####", "name-misread:...", "endpoint-mismatch:..."],
  "notes": "what you searched, what agreed/disagreed, confidence"
}
```

Use `resolved: false` with partial fields rather than guessing. A named city/town is
an acceptable endpoint anchor at reduced accuracy IF the line's terminus is that
settlement's gas station/plant and you say so in coord_basis; a governorate or
"somewhere in Sinai" is NOT.
