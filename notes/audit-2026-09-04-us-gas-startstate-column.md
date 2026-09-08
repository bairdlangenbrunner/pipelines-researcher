# Audit — US gas `StartState/Province` / `EndState/Province` on the stale-operating cohort (2026-09-04)

Follow-up to batch 1's escalation 3 ("audit the column you slice on"). Batch 1 found two
wrong states among 45 rows by hand; this pass checks all **217** stale-operating US gas
rows (operating, `LastUpdated` <= 2023) mechanically, so batch 2 onward can be sliced by
a derived state instead of the sheet column.

**Method** (`batches/united-states-gas/staging/state-audit-20260904/audit_states.py`): first
and last vertex of each row's routes-repo geojson, spatially joined to Natural Earth 10m
admin-1 polygons (US/MX/CA; nearest polygon within 0.5 deg for offshore/coastal ends); the
sheet value is OK if it names the geometry state, OK_INTERIOR if it names a state the route
traverses but does not end in, else a mismatch. Rows without a route fall back to the
county in `StartLocation`/`EndLocation` (Census `cb_2023_us_county_20m`) — only 3 carry one.
Output: `state_audit.csv` (217 rows) + `state_audit_noroute_county_fallback.csv` (50 rows).

## Result

| verdict | batch 1 (45) | remaining (172) |
|---|---|---|
| OK / OK_INTERIOR | 33 | 98 |
| START_MISMATCH | 5 | 8 |
| END_MISMATCH | 1 | 7 |
| BLANK_START / BLANK_BOTH | 0 | 9 |
| NO_ROUTE (unchecked) | 6 | 50 |

Of the 50 remaining no-route rows, **18 have a blank `StartState/Province`** — 14 of them
Florida Gas Transmission expansion rows (P4028–P4040, P4050), plus P0251 Sea Robin, P2497
TGP Acadiana Expansion, P2614 Sierrita Puerto Libertad Expansion, P5401 Acadian Haynesville
Extension Capacity Expansion.

## What is wrong with the column (four defect classes)

1. **Typos** — P0263 `Louisana`, P2502 `West Virgina`, P1997 `Masschusetts`. Mechanical.
2. **Not a state at all** — P0156 `Lancaster County`; P0168 `Rocky Mountains, Anadarko
   Basin`; P0192/P0204 `Gulf of Mexico`; P0223 `offshore Louisiana`; P0153 `Clarington` /
   `Chatham` (towns); P0176/P0259 `New United Kingdom` (a find-and-replace scar for New
   England — see the country note; NOT a mechanical fix). A `--province` slice silently
   drops every one of these.
3. **Blank** — 27 rows in the cohort (9 with geometry, 18 without). Blank on a row whose
   geometry sits entirely in one state (P2552 California, P3995 Vermont) is a plain gap.
4. **Disagrees with the geometry — needs research, not a paste:**
   - start: P0316 South Saskatchewan Access (`North Dakota`; route wholly in
     Saskatchewan), P0252 Southern Natural Gas (`Texas`; route starts Georgia — likely a
     direction/orientation issue, the system does reach Louisiana), P1297 Stratton Ridge
     (`Louisiana`; route wholly in Texas), P2613 Sierrita (`Texas`; Arizona), P2636 Wildcat
     (`Texas`; Oklahoma).
   - end: P0157 BC Gas (`Washington`; route ends in BC), P0288 Empire (`Pennsylvania`; ends
     New York), P0294 Magnolia Intrastate (`Mississippi`; ends Alabama), P2099 Northern
     Border (`Indiana`; route ends Montana — route orientation is reversed, the sheet is
     plausibly right), P2531 Empire North Expansion (`Ontario`; ends Pennsylvania), P2551
     Leidy South (`Delaware`; ends Pennsylvania), P3221 Carolina Gas Transmission
     (`Georgia`; ends South Carolina), P0259 Tennessee Gas (`New United Kingdom`).
   - artifact, not a defect: P0215 Mier–Monterrey `Texas` — the route's first vertex lands
     0.0 deg into Tamaulipas at the border crossing.

## Consequences

- **Slice batches by the derived state** (`state_audit.csv` column `derived`: geometry
  first-vertex state, else the normalized sheet value, else the parent system) via
  `build_ref_worklist.py --country "United States" --exclude-pids @<complement>`, never
  `--province`. (`--include-pids` is a UNION with the country/status scope, not a filter —
  it cannot cut a slice; and the builder's country scope reads `CountriesOrAreas`, so build
  the complement from that column, not Start/EndCountryOrArea.) Batch 2 (Gulf Coast:
  LA / MS / AL / FL / offshore GoM) was cut this way — 50 rows, of which 19 would have been
  invisible to a `--province` slice (blank or non-state values).
- The class-1 typos and class-3 single-state blanks are **Update items** (not sheet writes):
  they ride as validity `spec` findings on the batch that covers the row. Class-2 and
  class-4 rows need the state settled from a source, which the deep-sweep subagent for
  that row is briefed to do.
- Batch 1's start mismatches are already in its staged validity findings (P0252 Southern
  Natural Gas carries an attribution concern on `Texas`; P2613 and P2636 were caught by the
  subagents) except **P1297 Stratton Ridge**, where batch 1 corroborated the sheet's
  Louisiana start from two sources while the routes-repo geometry is drawn wholly in
  Texas. That is a route-vs-sheet conflict for the routes QC leg, not a reason to reopen
  batch 1. P0215 is the border artifact above.
