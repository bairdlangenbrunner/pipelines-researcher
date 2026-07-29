# Research backlog — unfinished / ongoing projects

Inventory of started-but-unfinished research threads. Baselined **2026-07-15** by a
full-repo audit and maintained continuously since (latest entries 2026-07-28). Update
this file when a thread closes or a new one opens; per-country detail stays in
`docs/country_notes/`, and this file just tracks what's open and where.

---

## 1. Global GGIT Stage A/B/C rollout — RETIRED (2026-07-15)

Plan doc: `docs/plans/ggit_update_2026-07.md` (decisions locked 2026-06-10) —
**superseded by the campaign annual-packet mechanism** (`campaigns/ggit-2026` roster
+ per-country Country Sweep `in-dev` preset / Discovery / Handoff Packet,
`docs/workflows.md §7`). Stage A's work (in-dev status sweep) IS the in-dev preset;
Stage B/C's ref/sweep-up work is the sweep's refs leg, run per country as the
campaign reaches it. The plan's Process-B tooling (`build_backfill_worklist.py`,
the ledger) was never built and won't be. The plan doc's row counts remain useful
as a scale reference (in-dev ~998 rows / 137 countries; stale tier-1 refs ~1,854
rows; incl. 9 broken-status rows flagged as data bugs). 4 of 137 countries done so
far via the campaign path (Iraq, Iran, Saudi Arabia, Egypt).

## 2. Research legs started but not finished

| Thread | State | Source |
|---|---|---|
| **Egypt oil (GOIT)** | never swept | `docs/country_notes/egypt.md` |
| **Saudi oil ref-sweep** | 3-row validation slice (2026-06-08) + 10-row batch staged; partial toward intended 50-row run | `batches/saudi-arabia-oil/staging/ref-sweep{,-10row}/`; `docs/country_notes/saudi-arabia.md` |
| **Saudi GulfPub route-consistency pass** | low/medium-accuracy matches not finished; route-replacement candidates not staged | `docs/country_notes/saudi-arabia.md` |
| **GulfPub route-comparison QC leg** | not started — Baird explicitly wants this later: extend the handoff packet's route-integrity leg to compare drawn routes against GulfPub *geometries* (ties into the unfinished Saudi route-consistency pass above). Distinct from the sweep's *attribute* crosswalk, which IS built and shipping (`build_recon_crosswalk.py`) | `docs/workflows.md` §6; `docs/sops/qc.md` |
| **Handoff-packet rollout (researcher onboarding, Arabic-speaking gas)** | Egypt is the pilot (2026-07-15); **Libya 38 done 2026-07-28**; remaining candidates by GGIT row count: Algeria 126, Qatar 59, UAE 39, Oman 23, Tunisia 21. Do Algeria next — 4 of its rows share the Libya `scm/y` capacity defect, so the fix and the sweep are one job | `docs/workflows.md` §6; `docs/country_notes/{egypt,libya}.md` |
| **Nigeria divestiture ownership sweep** | not started | `docs/country_notes/nigeria.md` |
| **United States** | deepwater-export terminal open item; 131-row Stage A queue slot unstarted | `docs/country_notes/united-states.md`; plan doc |
| **Iraq oil open items** | Grand Faw third offshore line (Esta/Micoperi) length/diameter/route; P0544 Basra–Haditha status review | `docs/country_notes/iraq.md`; CLAUDE.md |
| **Iraq oil: OSM + GulfPub recon untriaged** | First-ever OSM run for Iraq oil (2026-07-28, 246 features): 71 overlaps, 175 unmatched — **84 DISCOVERY_CANDIDATE (366 km, largest 26.5 km)**, 61 FRAGMENT_OF_EXISTING (incl. 80.9 km near P0548, 52.3 km near P0577), 21 ROUTE_FOR_EXISTING (86.1 km → P6255), 9 NEAR_MISS (80.3 + 53.6 km near P7898). GulfPub oil re-run: 20 overlaps, 8 status conflicts, 1 near-miss. Nothing triaged; no oil sweep or handoff packet exists to carry it | `batches/iraq-oil/deliverables/pipelines_batch_20260728_1804_ET_iraq-oil_{osm,gulfpub}-reconciliation.xlsx`; `docs/country_notes/iraq.md` |
| **Egypt gas: OSM + GulfPub recon untriaged** | Run 2026-07-29 to give Egypt the coverage Libya has; **both workbooks are standalone and NOT in the handoff packet**, so nothing routes them into the actions file. GulfPub (92 features): 52 overlaps, **40 additions all bucketed `NEAR_MISS`** (over the >30 escalation gate — adjudicate each against the near row before treating any as a discovery), 43 GEM-only, 3 status conflicts, 12 ambiguous clusters, 1 route-replacement candidate. First-ever Egypt OSM run (21 features / 476.6 km): **0 overlaps**, both `MATCH_QUALITY` escalations raised (0/21 named × 62/78 GEM rows routeless; top composite 0.4094 vs 0.45, threshold NOT lowered) → 9 `ROUTE_FOR_EXISTING`, 2 `FRAGMENT_OF_EXISTING`, 10 `DISCOVERY_CANDIDATE`. ⚠️ Ignore `Ref Length (km)` — it's miles (see §4) | `batches/egypt-gas/deliverables/pipelines_batch_20260729_0910_ET_egypt-gas_reconciliation-{gulfpub,osm}.xlsx`; `docs/country_notes/egypt.md` |
| **Libya gas: OSM + GulfPub recon untriaged** | Same structural gap as Egypt's — the 2026-07-28 full pass built both recon workbooks but the handoff packet does **not** subsume them (`gulfpub_crosscompare=0`; neither recon dir appears in "Prior staged packets"), so ~100 gas rows needing a decision live only in those two files: 32 GulfPub overlaps / 8 additions / 18 GEM-only / 3 status conflicts / 36 ambiguous, plus 5 OSM additions / 37 GEM-only. The GulfPub file also holds **untriaged `Oil_*` tabs** (72 overlaps / 17 additions / 19 GEM-only) from a `--commodity both` run — the only oil-facing Libya output that exists, and Libya oil has never been swept | `batches/libya-gas/deliverables/pipelines_batch_20260728_114{8,9}_ET_libya-gas_reconciliation-{gulfpub,osm}.xlsx`; `docs/country_notes/libya.md` |
| **Israel gas: Ashdod–Ashkelon onshore gap (P3620)** | routes + sheet edits APPLIED 2026-07-23 (Baird bridged the Ashdod HDD bore so P3620 meets P3657; routes-repo merge `72d29de1`; sheet RouteAccuracy→medium/RouteNotes/Route [ref] written rows 1036/1063; batch archived), but P3620 geometry is still partial — 2.1 of 4 sheet km; the Ashkelon-side ~2.4 km onshore run has no public vector yet (OSM empty, TAMA 37/A/2/7 blueprint sheets cover Ashdod only) — need the Ashkelon-side statutory sheet or an INGL/permit map to finish it. P3657 is complete | `batches/israel-gas/archive/route-creation-p3620-p3657/README.md` |
| **Iran general open items** | P6074 verify-before-removal; P5367 reclassify as Neka–Ray segment | `docs/country_notes/iran.md`; CLAUDE.md |
| **LNG carrier quarterly reconciliation** | "designed and partially executed" vs SFOC data; referenced `instructions.md` methodology is **not in this repo** — orphaned | `docs/PROJECT_SETUP_AND_CONTEXT.md` §9/§11 |

## 3. Staged, awaiting Baird's manual application (research complete)

Roster `applied` column is blank for all four countries — log the date when pasted.
Iraq/Iran xlsx deliverables are already pruned from disk, so file presence is not a
signal of application status. Neither is the blank roster column: Saudi and Egypt turn
out to be **partially applied** on the live sheet (see the second note below), so verify
per cell rather than trusting either signal.

> **Stale `SheetRow` locators — RESOLVED 2026-07-28.** `SheetRow` is positional, so it
> perishes as the sheet is re-sorted or rows are inserted (GGIT gas was re-ordered between
> the 07-04 and 07-05 pulls), which silently invalidated every locator staged by an earlier
> leg. Fixed three ways: `build_ref_workbook.py` now re-derives every locator from the fresh
> CSV at build time (`_restamp_sheet_rows`); all staged JSON was corrected at rest
> (8,853 nodes — saudi-arabia-gas 4,879 · egypt-gas 973 · saudi-arabia-oil 933 · iran-gas 600 ·
> libya-gas 4 · israel-gas 1 — a provably value-only diff); and the three affected packets were
> rebuilt against `GGIT_gas_snapshot_20260728.csv` (egypt-gas handoff, 43 bad cells →
> `…_20260728_1731_ET_…`; saudi-arabia-gas deepsweep 436 →; annual-indev 275 →), with the
> pre-fix files moved to each batch's `archive/`. **All 19 current deliverables now audit
> 0-bad against the live sheet.** No values were ever wrong (they were current at build time)
> and nothing was auto-applied. Any *new* consumer must re-derive from the current CSV keyed on
> ProjectID rather than trusting a staged `sheet_row` — see `docs/reference/gem_schema.md`.
>
> **Found while rebuilding: parts of these packets are already on the live sheet.** Measured by
> testing whether each staged ref URL is now present in its target `[ref]` cell —
> **saudi annual-indev 100 of 199** ref units fully live (4 partial), **saudi deepsweep 46 of
> 306** (5 partial), **egypt handoff 16 of 284** (26 partial); Iraq gas is 0 of 134, so the
> test isn't over-reporting. Corroborating: 32 of 40 in-scope Saudi *operating* rows were
> edited live between the 07-08 and 07-28 pulls (`Researcher`/`LastUpdated` churn on 28,
> plus `RouteNotes`/`StartLocation`/`ResearcherNotes` fills). So "staged, not applied" is
> wrong for Saudi and Egypt — they are **partially applied**, by whom and how deliberately is
> unknown. Because the rebuilt workbooks prefill from the 07-28 snapshot they now show that
> state, but nothing de-duplicates it: **before pasting Saudi/Egypt, check whether the cell
> already carries the ref.**

- **Iraq gas** — **full pass re-run 2026-07-28** (refs sweep · cancelled review · redundancy
  clusters · GulfPub + OSM recon · wiki alignment · route integrity · ref-gap re-pass · Leg-3),
  superseding the 2026-07-05 packet and the 2026-07-07 ASB ref-harvest, both folded in. Work from
  `pipelines_batch_20260728_1804_ET_iraq-gas_handoff-actions.xlsx` (100 open decisions ·
  9 status changes · 265 backend paste units · 114 wiki updates · 36 route suggestions ·
  171 open flags · 104 recon rows needing a decision) + the `-evidence` companion. The recon
  legs were **re-run 2026-07-28 with the fixed engine** and now reach the workbook: the earlier
  OSM null (0 overlaps from 52 features) was a matcher failure, not a coverage finding. **Twelve escalations open** — the structural ones
  are the ASB length mi→km defect (19 rows, two families with two *different* one-cell fixes),
  CapacityUnits on 3 rows, P6824 as a diesel line misfiled in GGIT, and the ASB-provenance ruling
  that **withdrew 12 of 16** of our own earlier duplicate/existence flags. **Three retractions —
  do not act on the older findings:** P4067 is *not* a misfiled crude line (stays in GGIT),
  "status stale forward" on P7435/P6826 is wrong (GEM was right), and P6007 is not a phantom.
  The earlier 37.5% status-change rate that tripped the >30% gate does not recur — 9 status
  changes across the country this pass. `docs/country_notes/iraq.md`.
- **Iran gas** — full packet staged 2026-07-05 (+ re-pass 2026-07-07, 35 refs).
  62.5% in-dev change rate (gate tripped); class-wide Owner NIOC→NIGC/IGTC fix on
  ~27 operating rows. `docs/country_notes/iran.md`.
- **Saudi gas** — full packet staged 2026-07-08 (discovery 2026-07-13), **partially applied**
  and **rebuilt 2026-07-28** as `pipelines_batch_20260728_1731_ET_saudi-arabia-gas_{annual-indev,
  deepsweep}.xlsx` (the 07-08 originals are in `archive/`). In-dev clean (22/22 confirm);
  hinges on the P1897–P1925 class decision (§4). `docs/country_notes/saudi-arabia.md`.
- **Egypt gas** — in-dev 2026-07-09 + operating deep sweep 2026-07-13 + discovery
  2026-07-15 (4 new rows / 3 monitor) + QC packet 2026-07-15. No escalation gate.
  All assembled into ONE two-file handoff packet, **rebuilt 2026-07-28** as
  `pipelines_batch_20260728_1731_ET_egypt-gas_handoff-{actions,evidence}.xlsx` (supersedes the
  07-16 pairs, now in `archive/`) — work from ACTIONS, not the four per-leg workbooks. Apply the
  Nitzana items (P3620/P7864 duplicate + discovery new-row Egyptian side) as one linked
  decision. Partially applied already (16/284 ref units live). `docs/country_notes/egypt.md`.
- **Israel gas: INGL/TMNG-map ground-truth batch** (2026-07-23) — 2 new discovery rows
  (P8001 Mari-B–Ashdod, P8003 Karish–Tanin FPSO), 5 validation candidate edits
  (P0462/P0479/P5276/P7604/P7606, none auto-applied), 5 route candidates (P7602/P7603/
  P0480/P8003 QC-pass, **P2197 QC-fail** documented). Deliverables:
  `pipelines_batch_20260723_1606_ET_israel-gas_discovery.xlsx` (+ P8001/P8003 wiki texts)
  and `…_1105_ET_israel-gas_route-creation.xlsx` (gitignored; predates the P8003 retrace —
  regenerate from the updated staged state before use). P8003 re-traced 2026-07-23 through the
  map's legend point-anchors (Tanin ⊕ → Karish ⊕ FPSO → Dor ○ OOAT; ~129 km incl. a
  future Tanin field-tieback leg) — see `route-creation-tmng-map/legend.md`. Open:
  Ashdod-vs-Ashkelon landfall (P8001 geometry deferred), Karish gem.wiki duplicate check,
  P8003 extent (full drawn vs operating-only trim), P0462 diameter needs a 2nd source.
  `docs/country_notes/israel.md`; `batches/israel-gas/staging/{discovery,validation}-tmng-map/`.
- **Libya gas: full pass** (2026-07-28) — operating ref sweep (30 rows) + cancelled-status
  review (P1728/P3985, both statuses failed review) + a 7-cluster redundancy pass +
  GulfPub and OSM reconciliations + handoff packet. GulfPub: 129 records at
  `--commodity both`, 25 additions (under the escalation gate). OSM: coverage null
  result for Libya, but it exposed three engine defects now fixed in `match.py` /
  `reconcile.py` / `route_compare.py` that affect every source. Three structural
  escalations are open (§4), plus a fourth found late in the pass: 14 lengths carry a
  spurious ASB miles→km conversion. Deliverable:
  `pipelines_batch_20260728_1235_ET_libya-gas_handoff-{actions,evidence}.xlsx` (work
  from ACTIONS; its README's `ESCALATIONS` row lists all five rulings needed).
  `docs/country_notes/libya.md`;
  `batches/libya-gas/staging/{ref-sweep-operating,cancelled-review,redundancy,recon-gulfpub-20260728,recon-osm-20260728,qc}/`.
- **US oil: Delaware Express** (P7995/P0354, researched 2026-06-12) and
  **Permian Express I–IV** (P0113/P2581/P2660/P2661, researched 2026-06-11) —
  `batches/united-states-oil/staging/update-{delaware,permian}-express/staged_updates.json`.
- **Saudi oil ref-sweep 10-row batch** (108 units: 67 REFS_ADDED / 25 DEAD_LINK /
  10 REVERIFIED / 6 UNRESOLVED) — `batches/saudi-arabia-oil/staging/ref-sweep-10row/`.

## 4. Decisions needed from Baird

- **P1897–P1925 (Saudi gas, 29 rows):** the 2026-06-19 escalation memo
  (`notes/escalation-2026-06-19-saudi-gas-opec-block.md`) requested a class-level
  decision (provenance of the 2022 GIS/km-post family, disposition of synthetic rows,
  dup-merge approval, re-citation) and was never answered; the identical question
  resurfaced in the 2026-07-08 packet. One decision closes both.
- **Libya cluster A (6 gas rows):** does P0483 "Libya Coastal Gas Pipeline" aggregate
  its own member segments P1862/P1863/P1864/P1865 (+ P1789)? Either delete the members
  or move P0483 to a network-route designation — remembering `n/a` is **not** a valid
  `Status`; aggregates take a blank Status + a `PipelineNetworkGrouping` label.
  `batches/libya-gas/staging/redundancy/`.
- **Three condensate lines in the GAS tracker (Libya):** P6705 and P6713 are already
  carried by GOIT (P0606, P6457) so they should be **deleted**, not moved; P6709 has no
  GOIT counterpart so it should be **moved**. Same defect, three different actions —
  needs one ruling. `batches/libya-gas/staging/redundancy/`.
- **`scm/y` / `scm/yr` zero-capacity class defect (8 rows: 4 Libya, 4 Algeria):** the
  OPEC ASB "(1,000 scm/yr)" multiplier was dropped at ingest and `scm/yr` is not a unit
  the `CapacityBcm/y` conversion recognises. ×1000 fits Libya's four and does **not**
  fit Algeria's, so no blanket fix.
  `notes/escalation-2026-07-28-scm-capacity-units.md`.
- **ASB length mi→km defect — now TWO countries, 33 rows: 14 Libya + 19 Iraq.** ASB Table
  4.10/9.9's length column is headed "miles" but those countries' blocks are tabulated in
  **kilometres** — the ingest converted anyway. Same table and same ingest as the `scm` defect
  above, different column, different fix. **The Libya memo's original "scope is Libya only,
  the Qatar/Iraq/Saudi blocks *are* miles" claim is superseded** — the Iraq gas pass
  (2026-07-28) found 19 Iraq rows with the same defect, arbitrated 6–0 by route geometry. The
  Qatar, Saudi and UAE controls *are* miles and their conversions stay correct, so the ingest is
  not broken — but "Libya only" is dead as a scope claim, and the remaining ASB countries should
  be tested the same way (take a row whose real length is independently known and see which
  reading it matches). Iraq needs TWO different one-cell fixes (13 rows fix the number;
  6 rows fix only the unit label). Fixing it should also clear most of both countries'
  route-integrity flags. `notes/escalation-2026-07-28-asb-libya-length-units.md` +
  `notes/escalation-2026-07-28-asb-iraq-length-units.md`.
- **GulfPub gas `Length` is MILES, manifest says km — dataset-wide, affects 4 shipped
  countries.** Re-confirmed 2026-07-29 on the Dec-2025 SDE scrape (median `geodesic_km ÷
  Length` = 1.595 over 5,284 features; 74.5% within 10% of 1.609, 3.2% near 1.0), which is
  the re-confirmation `sources/gulfpub/NOTES.md` had asked for and never got. Every
  `Ref Length (km)` cell in the Egypt / Libya / Iraq gas recon workbooks is ~38% short, and
  the matcher's length signal has been comparing km against miles. **Canada is genuinely km**
  (median 0.943) and `length_units` is per-dataset with no per-country override, so the
  decision is: flip to `mi` and accept Canada wrong (nothing shipped regresses — no Canada
  recon has run), add per-country overrides to the schema, or leave it and rely on
  `Ref Geodesic (km)`. No GEM cell is wrong from this — it only mis-informed comparisons.
  `notes/escalation-2026-07-29-gulfpub-gas-length-miles.md`.
- **GGIT small-diameter inclusion threshold:** GulfPub's Libya run surfaced 6–8in field
  gathering laterals, below the tracker-wide 12in 5th-percentile diameter, but GGIT does
  already carry 34 gathering rows globally. A one-time scope ruling stops this being
  re-litigated at every scrape. `batches/libya-gas/staging/recon-gulfpub-20260728/staged_addition_scope.json`.
- **Roster `applied` dates:** confirm whether the Iraq/Iran packets were actually
  applied to the live Sheet, and record dates in `campaigns/ggit-2026/roster.csv`.
