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
- **EIA** Natural Gas Pipeline Projects workbook — project-level cost, miles, added capacity,
  diameter, in-service year, status, docket. **Every release since May 2018 is tracked** in
  `sources/eia_pipeline_projects/` (NOTES.md there: file-name quirks, citing a dated release,
  one-origin rule). `scripts/eia_crosswalk.py` pre-matches every US gas row to EIA projects and
  diffs the values; sweep prompts carry its per-PID block (from slice 2 onward — refresh the
  releases and re-run it at the start of each US gas batch).

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
last touched <=2023** ("stale operating cohort"), sub-sliced by region. **Slice 1 is fully
swept** (batch 1 Texas 45, batch 2 Gulf Coast 50, batch 3 Appalachian/Mid-Atlantic 46,
batch 4 West 46, batch 5 45). **Batch 5 (`deepsweep-remainder`, 45 rows) closed slice 1**: the 30-row
cohort remainder (scattered Midcontinent / Southeast / New England — "East" was a misnomer) plus,
by Baird's ruling 2026-09-10, **every US gas row with a blank `LastUpdated`** — 14 cancelled rows
and P2041 Taproot Baja / Rattlesnake Extension (operating; a segment of batch 4's P0386, and it
reads `Fuel = Oil` on the gas tab). It ran with `--status-review` so the 14 cancelled rows got
verdicts there, the first batch start-to-finish on the fixed rule-4(e) contract — delivered
2026-09-10 `_1526_ET`, **rebuilt 2026-09-15 `_1231_ET`** (the 09-10 file is in `archive/`), gates
E/F/I/I'/J/L 0, staged not applied. Headlines: four "cancelled"
rows were built (P0376, P0380, P2008 — re-scoped into Texas Eastern's TEAM projects — and P0317);
P0171 Constitution cancelled -> proposed on its 2025 revival; **P2649 and P4381 are one pipe**
(FERC CP15-504) on two rows; P2041 is crude/water gathering (classification flag only, oil is out
of scope); ownership moved on PNGTS (BlackRock + MSIP, 2024-08), Black Bear (Enstor, 2025-11) and
Guardian/Midwestern (DT Midstream, 2024-12). P2588/P2631 end in Maine, not Quebec.
P3162 North Bakken Expansion is now `Status = N/A` (was blank) and is out of scope.
**Slice 2 = 296 rows, never swept** (recounted 2026-09-10 against batches 1-5): 108 operating
(LastUpdated 2024-25), 97 proposed, 52 cancelled, 26 construction, 11 shelved, 2 idle —
**confirmed at scoping 2026-09-10 against the fresh snapshot: 4,520 units** (`--owe-fills`:
HAS_REF 1,832 / MISSING_REF 1,060 / MISSING_VALUE 1,628; 592 of them operator/owner). Its
citation base is ~63% (HAS_REF over ref-bearing units), so re-verifying existing refs is a large
share of the work. State audit + batch plan: `staging/state-audit-20260910/`
(`slice2_state_audit.csv`, `slice2_duplicate_candidates.csv`); 19 no-route blank-state rows carry
a name-based `region_src = name (provisional)`.
State-column typos outside slice 1, for slice 2's audit: `Kentuky`, `Tennesse`, `North Carolna`,
`North Caolina`, `West Virgina` (end). Batch 5's own: P2495 `Inidiana` (sourced to Indiana,
Lake County — not Illinois), P1997 `Masschusetts`, P0380 `Teaxs` — carried as `Location [ref]` fills on its shards.

**Order of work — Baird's ruling 2026-09-10, this is the campaign plan.**
1. **Gas batch 5** (cohort remainder 30 + blank-LastUpdated 15 = 45 rows / 666 units) — DONE
   2026-09-10, rebuilt 2026-09-15 (`_1231_ET`, staged not applied); slice 1 closed.
2. **Gas slice 2** (296 rows) — scoped 2026-09-10. **Baird chose Option A: deep sweep ALL 296
   with `--status-review` on**, in 7 batches `staging/deepsweep-s2-*` (the `planA` column of
   `state-audit-20260910/slice2_state_audit.csv`). This absorbs step 3. Batches A1-A7 =
   `gulf-indev`, `gulf-se-operating`, `tx-indev`, `tx-midcon-operating`, `appalachian-indev`,
   `northeast-alaska`, `west`; each dir's `BRIEF.md` carries its route-first cases, duplicate
   families and status leads (passed as `extra_brief`).
   **Progress: ALL SEVEN BATCHES DELIVERED, slice 2 research closed 2026-09-15** (staged not
   applied — seven workbooks to work). A5 `appalachian-indev` `_0656_ET`, A6 `northeast-alaska`
   `_0629_ET`, A7 `west` `_0648_ET`; A1 `gulf-indev`, A2 `gulf-se-operating`, A3 `tx-indev` and
   A4 `tx-midcon-operating` all rebuilt together at `20260915_1116_ET` (the `_1712_ET`,
   `_0952_ET` and `_1022_ET` A1/A2/A3 workbooks are superseded and moved to `archive/`).
   Every batch closes the required gates **E, F, I', J, L at 0**, is coverage-clean
   (0 unmergeable records, 0 silent UNRESOLVED) and recalc-clean; the advisory gates
   (A single-host, B/C/D/K, and gate I where a source supports the value without naming the
   segment) stay open by design — gate B's `__VALIDITY__` hits in particular are a repo
   convention artifact, not a defect.

   A1-A4 needed a repair pass first (2026-09-15): 41 finished records were silently
   unmergeable because `merge_qc.verified_refs` keeps a ref only when a verification is `ok`
   AND `contains_value` AND its URL is byte-identical to the staged `proposed_refs` entry —
   26 were missing `contains_value` outright, 8 had a URL mismatch or an unstaged ref, and 11
   were never actually supported (a contradicting figure, a system total standing in for a
   per-segment cell, or "adds zero pipe" inferred from a blank EIA cell) and are now
   `UNRESOLVED`-with-notes. Nine validity/status verdict-vocabulary variances were repaired at
   the same time. All seven `ADDENDUM.md` files are synced to one canonical version carrying
   those rules; the full account is in `notes/handoff-us-gas-slice2-20260914.md`.

   Open leads for the reviewer: A2 — P6584's operator is Kinetica Deepwater Express (not ANR)
   and OGJ suggests Delfin ownership; P7809 is in construction per EIA against an Aug-2025
   target, operator East Tennessee Natural Gas, spanning TN-VA-NC; P7106 Cumberland went
   proposed -> operating 2026-05-26; P0311's owner moves SCANA -> Enbridge Inc. A3 — P3969 is
   keyed `spec` but also carries an **existence** signal (no independent mention of a distinct
   "Texas LNG Lateral Extension" in any EIA vintage, FERC docket or Enbridge release). A1 —
   P7769 cites an opaque `storage.xata.sh` mirror for FERC order 183 FERC 61,049 because
   ferc.gov 403s; substitute the eLibrary accession, never fabricate one. Groups to adjudicate
   together at review (A6/A7): P7455/P7461/P7454, P7830, P7820/P7821, P7790/P7812, P3942,
   P7863, P2626, P0230, the slice-wide "Northwest Pipeline Co" -> "Northwest Pipeline LLC"
   rename, P3171, P7860, P7823, and P7109's possible identity with Targa's Bull Run Extension.
3. ~~In-dev / status-review leg~~ — **retired for US gas**: slice 2's deep + `--status-review`
   covers the 134 proposed/construction/shelved and 52 cancelled rows (the other 14 cancelled
   were reviewed in batch 5). Do not stage a second pass over the same cells.
4. **Discovery (§4)** — never run for the US. Must be sliced like the sweep; whole-country
   trips the >5-candidate-cluster escalation gate immediately.
5. **Then, maybe:** route creation (§8 — 85 gas rows are `Not mapped (but could be)` or
   `Unavailable`) and reconciliation.

**OIL IS OUT OF SCOPE for this whole cycle** (Baird 2026-09-10). The 448 GOIT US rows /
6,140 units are not being worked, and neither are their legs. The two staged oil update
batches (Delaware Express, Permian Express) stay staged. Do not fold oil into a US pass,
and do not propose it as a next step.

**Reconciliation is dead for the US on GulfPub** — the extract holds 10 US gas features
and **0 US oil features**. There is nothing to diff. OSM is the opposite failure (62,221
US gas ways vs 529 rows); treat it as a route source for §8, not a recon input.

**The rule-4(e) recovery pass is COMPLETE (2026-09-09), and all four deliverables were rebuilt on
top of it** (`_1906_ET` stamps; every earlier US gas workbook is superseded and predates the
recovered refs). 70 subagents / 70 shards, 0 errors, into `ref_shards_recovery/` per slice
(tx 5, gulf 24, appalachian 27, west 14) — kept out of `ref_shards/` so a recovery shard cannot
clobber an original-leg one. **Gate L — uncited values never worked, the measure the pass
existed to close — went from 258 units of debt to zero on all four slices** (owed: tx 357,
gulf 422, appalachian 404, west 399), and gates E (orphan refs), F (banned/GEM) and J (blanks
coverage) are zero everywhere too. Coverage reports `0 with gaps` on all four.
Five defects in the merge/QC chain were fixed to get there, each now guarded: `merge_ref_shards.py`
appends an unseeded `MISSING_VALUE` unit as a `FILL` (the seeder never stages those, so recovery
research for them was being dropped at merge — the exact silent loss the pass existed to fix);
those records are tagged `leg: "refs"` so `merge_deepsweep_shards.py`'s FILL purge leaves them
alone; `check_shard_coverage.py` now blocks a sourced record whose `values` is empty (the ref-only
fold has nothing to compare, so the ref lands orphaned — appalachian P0310 shipped all 9 columns
that way and passed the old check); and the ref-less name columns (`OtherEnglishNames`, the
`OtherLanguage*` set) are exempted in both the coverage checker and gate E, since they have no
paired `[ref]` column at all.
Substantive findings the recovery surfaced: **P2497 Acadiana Expansion is documented throughout as
a Kinder Morgan Louisiana Pipeline LLC facility** (FERC CP19-484-000, KMI 8-Ks), not Tennessee Gas
Pipeline as tracked — a classification question, flagged not applied. P3585 North Bakken Operator =
WBI Energy Transmission, Inc.; P0239 Panhandle Eastern = Panhandle Eastern Pipe Line Company, LP;
P3170 Santa Fe Mainline construction began May 2020.
Still open from the pass: **21 contradictory duplicate `(ProjectID, ref_col)` records** where two
records on the same cell disagree (gulf P0192/P0263 Location, P2497 Start, P2500 SegmentCost,
P2594 Length, P5823 Diameter, P0165 Owner; appalachian P0153/P0182 Location; west P0151 FuelSource,
P0194/P0208/P0273 Location, P0231 Capacity+Length, P0273 Capacity+Length+Owner, P3158
Diameter+SegmentCost, P0281 Operator) — adjudicate before pasting those cells. A further 106
duplicates are complementary (one record refines the other) and 66 benign; the fold should absorb
those rather than let them accrete.

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
`Start/EndState/Province` was spatial-joined against its routes-repo geometry. **A sheet-vs-route
state mismatch is a research task on the pipeline, route FIRST (Baird 2026-09-10):** open the
geometry and judge whether it is an accurate trace of this pipeline (right corridor, right
termini, not the parent system or a sibling phase) against sourced maps/county lists; only then
decide whether the start/end cells or the route is wrong. A wrong route is a validity concern
(`contested: {"RouteAccuracy": ...}`, route-candidate recommendation for §8), never an edit to
the state cells to match it. Of the 172
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

- **Staged, NOT applied (gas):** batch 5, `batches/united-states-gas/staging/deepsweep-remainder/`
  (45 rows: cohort remainder 30 + the 15 blank-`LastUpdated` rows; deliverable
  `pipelines_batch_20260915_1231_ET_united-states-gas_deepsweep-remainder.xlsx`). 380 fills,
  136 validity records (83 concerns: spec 44, attribution 34, classification 3, duplicate 2),
  43 status reviews (10 change, 33 confirm); refs leg REFS_ADDED 279, UNRESOLVED 114.
  **Rebuilt 2026-09-15** after a post-delivery audit of the shards found defects the per-shard
  finish gate of the time did not look for; `ADDENDUM.md` in the staging dir is the full writeup.
  In short: 165 records cited the undated `EIA-NaturalGasPipelineProjects.xlsx` and were
  re-grounded onto `…Aug2026.xlsx` with a `[file / sheet / Excel row / project]` citation
  (watch the duplicate — EIA carries `Columbia to Eastover Pipeline` at BOTH row 833 and a
  stale row 838); 103 records overclaimed `tier`/`independent` against their own publisher
  count; 6 `UNRESOLVED` records staged refs they had not verified; 12 `contested` maps held
  prose where a pasteable candidate belongs; P0292's ref-less `ShelvedCancelledType` status
  change was re-keyed to the validity record that already carried it. `audit_shard.py` (added
  2026-09-14) now reports 0 findings across all 45 shards.
  No ref-gap/recovery leg was needed — coverage reported 0 gaps across all 45 shards. Two shards
  were hand-normalized before merge (originals in `rows_orig/`): P0186 wrote `refs:[{url,...}]`
  instead of `proposed_refs` + `verifications`, which the merge silently dropped (all 6 URLs
  re-verified with `--name KPC`); P2565's Location fill used `StartState`/`EndState`. P3295 stalled
  6x on the workflow's 180 s no-progress watchdog and was re-run as one agent with hard fetch
  timeouts.
- **Staged, NOT applied (gas):** batch 4, `batches/united-states-gas/staging/deepsweep-west-operating/`
  (46 operating West rows — the Rockies, Northern Plains, Pacific Northwest, Southwest and
  Upper Midwest remainder, sliced by the state audit's `derived` state; deliverable
  `pipelines_batch_20260909_1906_ET_united-states-gas_deepsweep-west.xlsx`). 861 records over
  the 663-unit worklist -> REFS_ADDED 276, UNRESOLVED 123 on the refs leg, 332 fills
  (293 folded to ref-only — the highest fold rate of the four slices), 130 validity findings
  (75 `concern` + 2 `needs correction` — spec 43, attribution 28, classification 4, duplicate 2).
  100 orange contested cells across 38 of the 46 rows on `Gas_Backend`, plus 51 across 23 rows on
  `Gas_OperatorsOwners`. `contested` arrived structured on 72 of 77 concerns; the other 5 name no
  backend column and stay row-level markers. Gate J's 3 owed blanks (P3170 Construction, P0239 and P3585 Operator) and gate L's
  36 never-worked uncited values were all closed by the recovery pass; both gates now read 0.
  Ran in two passes — 29 rows, then the 17 that died on a session limit; the resumed 17 added only
  1 new gap, so the split is not a quality seam.
  Headline findings: **P0266 Cheyenne–Beatrice should be `retired`, not operating** (the only
  status reclassification in the slice). **P0222's Owner2 Brookfield Infrastructure has fully
  exited** — remove it and move Owner3 to 62.50%. **P0246 and P0248 both move to Tallgrass
  Energy**; P0151 to Pembina (100%), P0207 to Berkshire Hathaway Energy, P0278 to DT Midstream,
  P3170 to Bernhard Capital, P2573 to Northwest Natural. P0231 Northern Natural: LengthKnown
  1,353 -> 1,377 mi and Capacity 2,900 -> 2,700 MMcf/d, both with a concrete corrected value.
  P0273 Transwestern LengthKnown 4,168.20 and Capacity 2,100 contested; P0316 LengthKnown 2.2 mi.
  P0194 Great Lakes runs **Manitoba -> Michigan**, not as recorded. P2517's SegmentCost 185M is
  contradicted by FERC's own 132,805,200 (Docket CP18-103-000) — flagged, not applied.
  **P2517, P2569 and P2615 are compression-only expansions**, so their blank Diameter is correct,
  not an omission (the agents documented the FERC facility description rather than leaving the
  cell silent). P0254's shard arrived in a schema the agent invented and was re-encoded onto the
  contract by `staging/deepsweep-west-operating/repair_P0254_shard.py` (research unchanged;
  pre-repair shard kept as `rows/P0254.json.preraw`).
- **Staged, NOT applied (gas):** batch 3, `batches/united-states-gas/staging/deepsweep-appalachian-operating/`
  (46 operating Appalachian Basin + Mid-Atlantic rows — OH/PA/WV/NY/MI/NJ/MD/DE/VA/IN, sliced by
  the state audit's `derived` state; deliverable
  `pipelines_batch_20260909_1906_ET_united-states-gas_deepsweep-appalachian.xlsx`). 861 records over
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
  `pipelines_batch_20260909_1906_ET_united-states-gas_deepsweep-gulf.xlsx`). 926 records over
  the 715-unit worklist -> REFS_ADDED 244, REVERIFIED 9, DEAD_LINK 10, UNRESOLVED 184,
  326 fills, 153 validity findings (60 `concern` — spec 34, attribution 24, classification 1,
  duplicate 1). 90 orange contested cells across 39 of the 50 rows, concentrated in
  Capacity (9), LengthKnown (8) and SegmentCost (8). Researched in two runs: 13 rows
  2026-09-04, the other 37 on 09-08.
  The two owed blanks the original run skipped (gate J: P0192 `SegmentCost [ref]`,
  P2497 `Operator [ref]`) were both worked by the recovery pass; gate J now reads 0.
  17 of the 50 rows are Florida Gas Transmission, 14 of those expansion phases, so read
  segment-vs-system carefully: a system figure restated on a phase row is a `spec` concern,
  not a ref.
- **Staged, NOT applied (gas):** batch 1, `batches/united-states-gas/staging/deepsweep-tx-operating/`
  (45 operating TX-sliced rows; deliverable `pipelines_batch_20260909_1906_ET_united-states-gas_deepsweep-tx.xlsx` — the 09-04 builds are superseded: 1144 predates the contested-cell fix and 1354 predates the recovery pass).
  All 381 ref units carry an outcome -> REFS_ADDED 325, REVERIFIED 14, UNRESOLVED 42,
  595 proposed refs, 23 fills, 163 validity findings (74 `concern` verdicts; 90 records
  carry a `concern_type` — spec 65, attribution 23, classification 1, duplicate 1 — so
  16 sit on `confirmed (caveat)`). Three escalations ride in the workbook's
  README; the SegmentCost one has its own memo
  (`notes/escalation-2026-09-04-us-gas-segmentcost-unsupported.md`).
  Originally only 208 of the 381 units got a dedicated ref-research pass (`ref_researched`);
  the 173 that resolved off harvested validity-leg evidence were swept by the 2026-09-09
  recovery pass, which closed the slice's gate-L debt (357 owed) to zero.
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
