# Research backlog — unfinished / ongoing projects

Inventory of started-but-unfinished research threads, as of **2026-07-15** (full-repo
audit). Update this file when a thread closes or a new one opens; per-country detail
stays in `docs/country_notes/`, and this file just tracks what's open and where.

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
| **GulfPub route-comparison QC leg** | not started — Baird explicitly wants this later: extend the handoff packet's route-integrity leg to compare drawn routes against GulfPub *geometries* (ties into the unfinished Saudi route-consistency pass above). Distinct from the sweep's `gulfpub` *attribute* crosswalk, which IS built and shipping (`build_gulfpub_crosswalk.py`) | `docs/workflows.md` §6; `docs/sops/qc.md` |
| **Handoff-packet rollout (researcher onboarding, Arabic-speaking gas)** | Egypt is the pilot (2026-07-15); **Libya 38 done 2026-07-28**; remaining candidates by GGIT row count: Algeria 126, Qatar 59, UAE 39, Oman 23, Tunisia 21. Do Algeria next — 4 of its rows share the Libya `scm/y` capacity defect, so the fix and the sweep are one job | `docs/workflows.md` §6; `docs/country_notes/{egypt,libya}.md` |
| **Nigeria divestiture ownership sweep** | not started | `docs/country_notes/nigeria.md` |
| **United States** | deepwater-export terminal open item; 131-row Stage A queue slot unstarted | `docs/country_notes/united-states.md`; plan doc |
| **Iraq oil open items** | Grand Faw third offshore line (Esta/Micoperi) length/diameter/route; P0544 Basra–Haditha status review | `docs/country_notes/iraq.md`; CLAUDE.md |
| **Israel gas: Ashdod–Ashkelon onshore gap (P3620)** | routes + sheet edits APPLIED 2026-07-23 (Baird bridged the Ashdod HDD bore so P3620 meets P3657; routes-repo merge `72d29de1`; sheet RouteAccuracy→medium/RouteNotes/Route [ref] written rows 1036/1063; batch archived), but P3620 geometry is still partial — 2.1 of 4 sheet km; the Ashkelon-side ~2.4 km onshore run has no public vector yet (OSM empty, TAMA 37/A/2/7 blueprint sheets cover Ashdod only) — need the Ashkelon-side statutory sheet or an INGL/permit map to finish it. P3657 is complete | `batches/israel-gas/archive/route-creation-p3620-p3657/README.md` |
| **Iran general open items** | P6074 verify-before-removal; P5367 reclassify as Neka–Ray segment | `docs/country_notes/iran.md`; CLAUDE.md |
| **LNG carrier quarterly reconciliation** | "designed and partially executed" vs SFOC data; referenced `instructions.md` methodology is **not in this repo** — orphaned | `docs/PROJECT_SETUP_AND_CONTEXT.md` §9/§11 |

## 3. Staged, awaiting Baird's manual application (research complete)

Roster `applied` column is blank for all four countries — log the date when pasted.
Iraq/Iran xlsx deliverables are already pruned from disk, so file presence is not a
signal of application status.

- **Iraq gas** — full packet staged 2026-07-05 (+ OPEC-ASB ref-harvest re-pass
  2026-07-07, 68 refs). 37.5% status-change rate **tripped the >30% escalation gate**.
  `docs/country_notes/iraq.md`.
- **Iran gas** — full packet staged 2026-07-05 (+ re-pass 2026-07-07, 35 refs).
  62.5% in-dev change rate (gate tripped); class-wide Owner NIOC→NIGC/IGTC fix on
  ~27 operating rows. `docs/country_notes/iran.md`.
- **Saudi gas** — full packet staged 2026-07-08 (discovery 2026-07-13). In-dev clean
  (22/22 confirm); hinges on the P1897–P1925 class decision (§4). xlsx on disk.
  `docs/country_notes/saudi-arabia.md`.
- **Egypt gas** — in-dev 2026-07-09 + operating deep sweep 2026-07-13 + discovery
  2026-07-15 (4 new rows / 3 monitor) + QC packet 2026-07-15. No escalation gate.
  All assembled into ONE handoff workbook (regenerated 2026-07-16,
  `pipelines_batch_20260716_0959_ET_egypt-gas_handoff.xlsx`) — work from that, not
  the four per-leg workbooks. Apply the Nitzana items (P3620/P7864 duplicate +
  discovery new-row Egyptian side) as one linked decision. xlsx on disk.
  `docs/country_notes/egypt.md`.
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
  escalations are open (§4). `docs/country_notes/libya.md`;
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
- **GGIT small-diameter inclusion threshold:** GulfPub's Libya run surfaced 6–8in field
  gathering laterals, below the tracker-wide 12in 5th-percentile diameter, but GGIT does
  already carry 34 gathering rows globally. A one-time scope ruling stops this being
  re-litigated at every scrape. `batches/libya-gas/staging/recon-gulfpub-20260728/staged_addition_scope.json`.
- **Roster `applied` dates:** confirm whether the Iraq/Iran packets were actually
  applied to the live Sheet, and record dates in `campaigns/ggit-2026/roster.csv`.
