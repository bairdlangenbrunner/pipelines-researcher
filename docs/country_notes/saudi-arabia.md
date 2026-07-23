# Saudi Arabia

Crude, NGL, and gas. Deep-dive country and the home of the GulfPub reconciliation
proof-of-concept (`working_files/GOIT_SaudiArabia_Gulfpub_Comparison.xlsx`, the
golden reference the engine generalizes).

## Regulators / official data
- Saudi Aramco corporate + AramcoLife — project status, capacities, the Master Gas
  System (MGS) program.
- Saudipedia — Saudi infrastructure encyclopedia entries.

## Key operators / owners
- **Saudi Aramco** — operator/owner of essentially the entire network (`Saudi
  Aramco [100.%]` is the common Owner string). BAPCO (Bahrain) co-owns the AB-4
  cross-border line (P0637).

## Preferred sources (beyond the global roster)
- KS Al-Hajri, Samsung E&A — EPC contractors on MGS packages (good for diameters,
  scope, schedule).
- MEED — Gulf project tracking and tenders.

## Reconciliation notes
- GulfPub covers Saudi crude well; gas coverage thinner (GulfPub historically
  tracks mostly crude). Known matched anchors for validation: P0637 (AB-4), P1972
  (Abqaiq Plants–Qatif Junction), P3966 (East–West Gas), P6734 (MGS III / MGS-3).
- **Route-replacement candidates:** several matched lines have `low`/`medium` GEM
  `RouteAccuracy` while GulfPub carries a route (e.g. P3966 East–West, GEM
  `medium`) — prime targets for the geometry pass + human review.
- Diameters are frequently multi-valued (`56,10,16`, `40/42/48`) — set-membership
  matching, not equality.

## Gas-specific (from the 2026-06 gas deep sweep — all 65 GGIT rows)
- **Sourceability bifurcates sharply.** In-construction **MGS-3 / East-West expansion**
  segments (P6717–P6737) are well-documented — MEED, Blackridge, OGJ corroborate
  packages, diameters (56-in), and 2028 schedules. Legacy **operating gathering /
  GIS-node-coded** segments (P1897–P1925: names like `UBTG-1-km0-UBTG-1-km56`,
  `AY-1 KP 943-Riyadh`) are internal Aramco route-database segments with essentially
  **no public press footprint** — expect them to end UNRESOLVED, and don't mistake that
  for a sweep failure. `FuelSource` on the gas rows is the upstream field/plant, not
  "Natural Gas" (see `gem_schema.md`).
- **Province tagging error:** P1915 / P1918 / P1919 carry `State/Province = Makkah`, but
  Hawiyah / Haradh / Khuff are all in the **Eastern Province** (Ghawar / Al-Ahsa).
- **Likely duplicate/relabel clusters** flagged for review: P1897 "A47-Yanbu"
  (966 km, trunk-scale — echoes the MGS / Shedgum-Yanbu trunk); P3962 "East-West Gas"
  Main Line maps to the Shedgum-Yanbu **NGL** line (commodity may be NGL, not gas);
  near-identical pairs/triples P1922/P1923 and P1917/P1918/P1919.
- **P0458 Qatar-Turkey** is a *transit* route — start (Qatar) and end (Türkiye) are
  outside Saudi; Owner1 `Gassled` is wrong (should be QatarEnergy/Qatari state). Weakest
  entity: **P1925 "Depco-Abqaiq"** — no independent source mentions it at all.

## Gotchas
- Status_Conflicts seen in the POC: P2702 (Al Khafji Joint Operations Offshore) GEM
  `cancelled` vs GulfPub Operating; P0545 (IPSA) GEM `mothballed` vs GulfPub
  Operating — verify true current status, don't auto-flip.

## Open items — gas (staged, NOT applied — 2026-07-08 full packet: in-dev sweep + discovery + operating deep sweep; candidates for review)
Workbooks: `pipelines_batch_20260708_1310_ET_saudi-arabia-gas_annual-indev.xlsx`,
`pipelines_batch_20260707_0918_ET_saudi-arabia-gas_discovery.xlsx`,
`pipelines_batch_20260708_1322_ET_saudi-arabia-gas_deepsweep.xlsx`.
- **In-dev leg (22 rows, MGS-3 era):** all 22 status verdicts `confirm` — no status
  edits proposed. 79/82 gap ref cells corroborated. 5 spec concerns (P7711 cost is the
  package budget, not the line's; see Validity tab).
- **Class-wide existence gap (the sweep's headline):** the 2022-07-19 GIS/km-post row
  family (P1897–P1925: `UBTG-1-km…`, `AY-1 KP 943`, `Haradh Khuff-Hawiyah 1/2/3`) has
  essentially **no independent per-line attestation** — 18 existence + 15 duplicate
  concerns. These read as internal Aramco route-database segments, not independently
  named pipelines. Treat as one class decision (keep-as-GIS-segments vs de-dup/merge),
  not row-by-row fixes.
- **De-dup families for a human pass:** UBTG-1 trunk cluster (P1898/P1899/P1900/P1901/
  P1910/P1911/P1912); Haradh Khuff–Hawiyah triple (P1917/P1918/P1919 — identical
  43 km/30 in); Berri–Abu Ali pair (P1922/P1923); P1897 "A47-Yanbu" + P1903 vs P3962
  East–West; P7545 (subsea) is a sub-component of P7544 Marjan GOSP-4; P7768 offshore
  leg double-counts P1921 (strip its Capacity if merged).
- **P3962 East–West:** LengthKnown 1200 km / 48 in are the **crude Petroline's**
  numbers, and the 48-in leg was NGL — commodity + specs need adjudication before the
  row is trusted as gas transmission.
- **Attribution fixes staged:** P1915/P1917/P1918 province `Makkah`→`Eastern Province`;
  P3961 is the Haradh–Hawiyah "Free Flow Pipelines" (rename; StartYear 2024→~2019);
  P1921 endpoint likely Khursaniyah, not Berri.
- **Placeholder capacities:** P7766/P7767 `1.00 MMcf/d` and P7768 `220 MMcf/d` are
  unsupported — blank or re-source.

## Open items
- Finish the GulfPub route-consistency pass for low/medium-accuracy matches; stage
  route-replacement candidates for review before any GeoJSON swap.
- **Oil ref-sweep incomplete:** a 3-row validation slice (2026-06-08) then a 10-row
  batch (108 units: 67 REFS_ADDED / 25 DEAD_LINK / 10 REVERIFIED / 6 UNRESOLVED;
  redone after the abarrelfull/wikidot blocklist) are staged in
  `batches/saudi-arabia-oil/staging/ref-sweep{,-10row}/` — partial toward the intended
  50-row run; staged, NOT applied.
