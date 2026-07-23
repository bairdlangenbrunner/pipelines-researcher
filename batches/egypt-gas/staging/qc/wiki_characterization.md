# Wiki page characterization — Egypt gas QC pilot (2026-07-15)

Sampled pages (cached in `wiki_html/`): P0462 (interconnector), P3346 (GASCO trunk),
P0477 (network row), P7597 (in-dev), P3938 (no-route, staged existence concern), plus
P3343 El Tina (fetched during planning). All 6 parseable → decision gate passed, no
escalation.

## Structure (what the parser must handle)

- Data lives in a details section: `<h2>` titled **"Project details"** OR **"Pipeline
  details"** (P0477) — match heading text case-insensitively, both variants.
- Bullets are `<li><b>Key:</b> value` items. Two markup variants:
  1. one `<ul>` holding all `<li>` (common);
  2. **each `<li>` in its own `<ul>`** (P7597) → collect ALL sibling `<ul>`s until the
     next `<h2>`/`<h3>`.
- Sometimes the value is INSIDE the bold: `<b>Owner: EGAS…</b>` (P0477) → split on the
  first `:` of the bold text when no text follows the `</b>`.
- Strip `<sup>` citation markers before extracting values.
- Network pages (P0477) add per-segment `<h3>` subsections after the main bullets —
  main bullets only are compared at row level.
- Key casing varies: `Parent company` / `Parent Company`; `Capacity` / `Current
  capacity`. Normalize keys to lowercase, colon-stripped.
- Empty bullet values are common and meaningful (wiki missing a value the sheet has).
- Status also appears in prose (intro sentence + "Location" section) — parse both for
  the internal-inconsistency check (El Tina shows construction/proposed/Construction
  in three places while the sheet says operating).
- "Location" prose start/end pattern: "runs/running from X … to Y", "starts in X and
  ends in Y" — country tokens compared hard, place names info-only.

## Observed value formats

- Capacity: `5–7 bcm/y` (range), `12 billion cubic meters per year`, `180 MMcf/d`,
  `500 MMcf/d` → normalize to bcm/y (`capacity_to_bcmy`); range matches if sheet
  value falls inside.
- Length: `90 kilometers`, `130 km`, `930 kilometers`.
- Diameter: `32 /42 inches`, `36,32,32,32,32,30 inches` (dups fine — set compare), `20 in`.
- Start year: `2008, 2020` (multi-value), `2015`, `2027`.
- Owner/Parent: `East Mediterranean Gas Company [61%]; EMED [39%]` — GEM-style
  bracket shares; entity-set compare via `normalize.parse_owners`.
- Cost: `EGP 1.197 billion`, `US$9.3 billion` — currencies vary; soft compare only
  (severity info), never a hard flag across currencies.

## Frozen field map (wiki key → sheet column)

| wiki key (lc)              | sheet column(s)               | compare |
|----------------------------|-------------------------------|---------|
| status                     | Status                        | lowercase equality |
| capacity / current capacity| Capacity + CapacityUnits (CapacityBcm/y) | bcm/y, ±5%, range-inclusive |
| length                     | LengthKnownKm (LengthMergedKm fallback) | ±10% or ±2 km |
| diameter                   | Diameter / DiameterInMm       | inch set compare |
| start year                 | StartYear1..N                 | year set compare |
| operator                   | operators/owners tab Operator | entity set |
| owner                      | operators/owners tab Owner (main-tab Owner fallback) | entity set |
| parent company             | operators/owners tab Parent   | entity set |
| cost                       | ProjectLevelCost/Cost         | info-only |
| location prose start/end   | Start/EndCountryOrArea (hard), Start/EndLocation (info) | tokens |
