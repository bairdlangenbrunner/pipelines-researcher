# United States

Crude + NGL (GOIT) and a very large gas network (GGIT). Richest regulatory data of
any country — use it for both attributes and routes.

## Regulators / official data
- **FERC** eLibrary (`elibrary.ferc.gov`) — interstate gas/LNG.
- **PHMSA** — safety + the National Pipeline Mapping System (`npms.phmsa.dot.gov`)
  for routes.
- **MARAD** — deepwater ports (export terminals).
- **BOEM** (`data.boem.gov`) / **BSEE** — offshore/OCS pipelines + permits.
- **Texas RRC** GIS viewer; **Alaska DNR** State Pipeline Coordinator.
- **EIA** — petroleum & natural-gas project tracking.

## Routing / GIS tips
- NPMS, Texas RRC, and BOEM give traceable routes (`high`/`medium`).
- Gulf of Mexico subsea lines: use OCS block coordinates for `low`-accuracy
  endpoints (e.g. Green Canyon 19 ≈ 27.88°N, 89.17°W). Offshore Magazine's annual
  GoM map and the Enbridge interactive map help.

## Gotchas
- **Deepwater crude export terminals** — four competing projects (SPOT, Texas
  GulfLink, Blue Marlin, Bluewater Texas): track MARAD license, EPA CAA permits, and
  FID *separately*; the pipeline component may have no new onshore pipe.
- **GoM deepwater 2024 FIDs** (Canyon Oil, Rome, Oceanus) — subsea, limited route
  data; low-accuracy routing from block coords.
- **Conversions** (e.g. Double H → Hiland Express): note as a conversion in
  `RouteNotes`; the existing route may already be in PHMSA/GEM.

## Gas (GGIT) — the staged campaign

US gas is **529 rows / 4,935 ref units**, ~12x the largest pass this repo has run, so it
is being worked in slices, not as one country sweep. Slice 1 = the **217 operating rows
last touched <=2023** ("stale operating cohort"), sub-sliced by region. **141 of them are
swept** (batch 1 Texas 45, batch 2 Gulf Coast 50, batch 3 Appalachian/Mid-Atlantic 46) —
76 of the cohort remain (a clean 46 West / 30 East split, scoped as batches 4 and 5),
and 434 US gas rows have never been swept at all.

**Scope the slice by region, and audit the column you slice on first.**
`StartState/Province` is wrong on at least 2 of the 45 rows in batch 1 — P2613 Sierrita
(SheetRow 1349) reads `Texas` but the whole route is in **Arizona**; P2636 Wildcat
(SheetRow 1362) reads Texas->Texas but its origin traces to **Grady County, Oklahoma**
(flagged, not confirmed). Both were caught independently by two agents. A wrong state
does not just mis-describe a row, it silently pulls the wrong rows into the batch and
leaves the right ones out.

**The state columns were audited before batch 2** (2026-09-04,
`notes/audit-2026-09-04-us-gas-startstate-column.md`; data in
`batches/united-states-gas/staging/state-audit-20260904/`): every stale-operating row's
`Start/EndState/Province` was spatial-joined against its routes-repo geometry. Of the 172
non-Texas rows, 98 agree, 15 disagree (8 start / 7 end), 9 are blank on a routed row, and 50
have no route at all — 18 of those blank in the start column (14 FGT expansion phases,
P0251 Sea Robin, P2497, P2614, P5401). **Slice by the audit's `derived` state, never by
`--province`**, and cut the slice with `--country` + `--exclude-pids @<complement>`:
`--include-pids` is a UNION with the country scope, not a filter (Sweep SOP → carried rows).

**Recon legs are deliberately OFF for US gas.** GulfPub carries only 10 US gas features,
and OSM carries 62,221 US gas ways against 529 GEM rows — a 118:1 scope mismatch that
would bury the research legs in unmatched-reference triage. Revisit per-slice, never
whole-country.

**FERC silence is not an existence concern.** Many Texas gas lines are **intrastate** and
therefore never appear in FERC eLibrary. Check the **Texas RRC** (T-4/T-4A permits) before
treating a FERC gap as a signal — P0268's operator name was settled by an RRC permit.

- **Staged, NOT applied (gas):** batch 3, `batches/united-states-gas/staging/deepsweep-appalachian-operating/`
  (46 operating Appalachian Basin + Mid-Atlantic rows — OH/PA/WV/NY/MI/NJ/MD/DE/VA/IN, sliced by
  the state audit's `derived` state; deliverable
  `pipelines_batch_20260908_2103_ET_united-states-gas_deepsweep-appalachian.xlsx`). 861 records over
  the 663-unit worklist -> REFS_ADDED 384, REVERIFIED 6, DEAD_LINK 3, UNRESOLVED 318, 296 fills
  (248 folded to ref-only), 150 validity findings (83 `concern` — spec 45, attribution 33,
  classification 3, duplicate 2). 119 orange contested cells across 43 of the 46 rows on
  `Gas_Backend`, plus 43 on `Gas_OperatorsOwners`. **Gate J passes** — every owed blank was
  reported on, unlike batch 2. Citation base was the thinnest of the three slices (11 filled refs
  against 663 owed units, 1.7%), so the brief calibrated it as India/Ukraine: a blank means nobody
  looked.
  Headline findings: **P0176 `Dominion Gas Pipeline` and P3220 `Eastern Gas Transmission and
  Storage System` flag each other as duplicates** (both agents independently; adjudicate before
  editing either, and P3220 may belong as a SYSTEM/NETWORK row like P0169). P0176's
  `New United Kingdom` scar resolves to **New York** with a ref, and its Owner1 moves off Dominion
  Energy to Berkshire Hathaway Energy on the documented 2020 transaction. **Three Rover rows
  (P2438/P2604/P2635) carry a stale Owner2 = Blackstone; the 32.4% stake is Ares Management's.**
  P3202 Blue Water Compressor's `EndState/Province = Wisconsin` is wrong (Michigan — the station is
  entirely in-state). P2531 Empire North Expansion is compression-only -> `LengthKnown = 0`,
  Diameter blank. P0307 Mountaineer Phase I starts in **West Virginia**, not Virginia. P0221
  Diameter `29, 36` should read `24, 36`. P5830 REX Zone 3 East-to-West Capacity 1800 -> 1200 MMcf/d.
  P0169 Columbia Gas Transmission LengthKnown 19,312 -> 18,768 km.
  **P0182 Eastern Shore's 732 is stored in KM, not miles** (the batch brief's shorthand said miles —
  the agent caught the mismatch); it and Capacity 100 MMcf/d are both contested with no replacement
  value found, so they carry a row-level flag for human review, not a candidate.
- **Staged, NOT applied (gas):** batch 2, `batches/united-states-gas/staging/deepsweep-gulf-operating/`
  (50 operating Gulf Coast rows — LA/MS/AL/FL + offshore GoM; deliverable
  `pipelines_batch_20260908_1712_ET_united-states-gas_deepsweep-gulf.xlsx`). 926 records over
  the 715-unit worklist -> REFS_ADDED 244, REVERIFIED 9, DEAD_LINK 10, UNRESOLVED 184,
  326 fills, 153 validity findings (60 `concern` — spec 34, attribution 24, classification 1,
  duplicate 1). 90 orange contested cells across 39 of the 50 rows, concentrated in
  Capacity (9), LengthKnown (8) and SegmentCost (8). Researched in two runs: 13 rows
  2026-09-04, the other 37 on 09-08.
  **Two owed blanks carry no record at all** (gate J: P0192 `SegmentCost [ref]`,
  P2497 `Operator [ref]`) — the subagents skipped them; they are owed, not resolved.
  17 of the 50 rows are Florida Gas Transmission, 14 of those expansion phases, so read
  segment-vs-system carefully: a system figure restated on a phase row is a `spec` concern,
  not a ref.
- **Staged, NOT applied (gas):** batch 1, `batches/united-states-gas/staging/deepsweep-tx-operating/`
  (45 operating TX-sliced rows; deliverable `pipelines_batch_20260904_1354_ET_united-states-gas_deepsweep.xlsx` — the 1144 build is archived: it predates the contested-cell fix, so its `Gas_Backend` shows none of the 74 open concerns).
  All 381 ref units carry an outcome -> REFS_ADDED 325, REVERIFIED 14, UNRESOLVED 42,
  595 proposed refs, 23 fills, 163 validity findings (74 `concern` verdicts; 90 records
  carry a `concern_type` — spec 65, attribution 23, classification 1, duplicate 1 — so
  16 sit on `confirmed (caveat)`). Three escalations ride in the workbook's
  README; the SegmentCost one has its own memo
  (`notes/escalation-2026-09-04-us-gas-segmentcost-unsupported.md`).
  **Only 208 of the 381 units got a dedicated ref-research pass** (`ref_researched`).
  The other 173 still resolved — 159 picked up refs harvested from the validity leg's
  evidence, 14 were reverified live links — but none of those 159 has had a
  >=2-independent search of its own. The batch is a finished pass over the rows, not
  over every cell.
- **P0271 Transco — Capacity is 7 years stale, candidate pinned (2026-09-04).** GEM's
  16800.00 MMcf/d is the year-end-2018 figure; the row's own cited ref (rextag) says 18.6
  Bcf/d, which is itself the 2021/2022 number. The FY2025 Williams/Transco joint Form 10-K
  (`sec.gov/Archives/edgar/data/99250/000010726326000006/wmb-20251231.htm`, filed 2026-02-24)
  states *"At December 31, 2025, Transco's system had a design capacity totaling approximately
  20.6 MMdth/d"* = **20,600 MMcf/d** (MMdth/d = MMcf/d for pipeline-quality gas), and its four
  itemised 2025 expansions sum to exactly the 19.8 -> 20.6 step. Tier **medium**, not high:
  no independent second source restates the system total (trade press traces to Williams' own
  April-2025 release; EIA's State-to-State workbook is independent but point-to-point, not a
  system figure). Staged as a CONTESTED candidate on `Gas_Backend`, not an applied edit —
  adjudicate before pasting, and repoint `Capacity [ref]` to the 10-K when you do.
- **`New United Kingdom` is a find-and-replace scar, and is NOT a mechanical fix.**
  P0176 (SheetRow 37) and P0259 (SheetRow 112) carry it in `EndState/Province`; both are
  New England termini. But the column holds individual STATES everywhere else
  (`Massachusetts`, `Connecticut`, `Maine`, `New Hampshire`, `New York` all present) and
  `New England` appears **zero** times in either tracker, so restoring it would introduce
  an unprecedented value. Research each row's real terminus state. The other 7
  `United Kingdom` hits in the tab are legitimate North Sea rows — leave them.

## Open items
- Keep deepwater-export terminal pipeline components distinct from the terminal
  records (LengthKnown often 0 — onshore expansion only).
- **Staged, NOT applied (oil):** Delaware Express update batch (P7995 Targa NGL +
  P0354 Medallion→Plains Oryx — same name, NOT duplicates: different commodities/
  owners/vintages; researched 2026-06-12, `batches/united-states-oil/staging/update-delaware-express/`) and
  Permian Express I–IV batch (P0113/P2581/P2660/P2661 — Parent split 87.7/12.3,
  Operator = Sunoco Pipeline L.P., PE1 capacity 200k→150k bpd, PE2 StartLocation
  Wichita Falls→Midland, PE4 zeroed as expansion; researched 2026-06-11,
  `batches/united-states-oil/staging/update-permian-express/`).
