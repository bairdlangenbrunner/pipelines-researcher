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
last touched <=2023** ("stale operating cohort"), sub-sliced by region.

**Scope the slice by region, and audit the column you slice on first.**
`StartState/Province` is wrong on at least 2 of the 45 rows in batch 1 — P2613 Sierrita
(SheetRow 1349) reads `Texas` but the whole route is in **Arizona**; P2636 Wildcat
(SheetRow 1362) reads Texas->Texas but its origin traces to **Grady County, Oklahoma**
(flagged, not confirmed). Both were caught independently by two agents. A wrong state
does not just mis-describe a row, it silently pulls the wrong rows into the batch and
leaves the right ones out.

**Recon legs are deliberately OFF for US gas.** GulfPub carries only 10 US gas features,
and OSM carries 62,221 US gas ways against 529 GEM rows — a 118:1 scope mismatch that
would bury the research legs in unmatched-reference triage. Revisit per-slice, never
whole-country.

**FERC silence is not an existence concern.** Many Texas gas lines are **intrastate** and
therefore never appear in FERC eLibrary. Check the **Texas RRC** (T-4/T-4A permits) before
treating a FERC gap as a signal — P0268's operator name was settled by an RRC permit.

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
