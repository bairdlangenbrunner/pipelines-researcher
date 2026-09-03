# Research backlog — index of open threads

**One line per open thread: scope, what is open, where the detail lives.** Baselined
**2026-07-15** by a full-repo audit, maintained continuously since, and collapsed to an index
2026-09-03. The facts live in `docs/country_notes/`, `notes/escalation-*.md` and the SOPs — this
file never narrates them. Close a line when a thread closes; add one when a thread opens.

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

Cross-cutting — read before working any row below:

- **Non-citation ref screen (2026-08-27):** 10 units outside Egypt are owed again (`uzbekistan-gas/ref-sweep-operating` 8 on `liting.uz/page/4`, `iraq-gas/ref-sweep-operating` 1, `libya-gas/annual` 1); Uzbekistan's delivered workbook shows them as sourced until rebuilt. `notes/escalation-2026-08-27-ref-screen-defects.md`.
- **Every GulfPub recon re-run 2026-08-12** (multi-country `==` filter): current workbooks are stamped `20260812_1359_ET` (kazakhstan-gas `20260812_1344_ET`; none for saudi-arabia-oil / china-trunks-gas; malaysia-gas left alone); Pakistan's "0 status conflicts" is now 2. `notes/escalation-2026-08-12-multicountry-reference-filter-dropped-transit-trunks.md`.
- **Link checks run before 2026-08-11 carry false `DEAD_LINK`s** (incomplete-TLS `SSLError`; `insecure_tls: True` means live; Kazakhstan 51 of 105 cells, 0 real 404s) — re-run the worklist of any earlier scope whose flags show `SSLError`; discard any `Diameter_OutOfRange` QC sheet built before then. Sweep SOP §Verifier false-negatives; `docs/sops/{reconciliation,qc}.md`.
- **OSM `best_guess` is arithmetic, not geography, in four pre-2026-08-11 runs** (`iraq-oil/recon-osm-20260728` 82 of 184 additions, `egypt-gas/recon-osm-20260729` 10/21, `india-gas/recon-osm-20260810` 8/61, `iraq-gas/recon-osm-20260729` 2/46): ignore the `Nearest` PID on unnamed additions whose guessed row has no route; not re-run (locators). Reconciliation SOP → Engine invariants.
- **Re-verify refs in pending staged batches against the block-page false positive** (fixed 2026-08-12 + 2026-08-16; Ukraine gas done, nothing shipped wrong) — start with Russian-press-heavy scopes. `notes/escalation-2026-08-12-url-verifier-false-positive-on-block-pages.md`.

| Thread | Open | Where |
|---|---|---|
| **Egypt oil** | first-ever sweep 2026-08-27 (all 46 rows), staged not applied | `docs/country_notes/egypt.md` |
| **Saudi oil ref-sweep** | 3-row slice + 10-row batch staged (108 units); 50-row run unfinished | `batches/saudi-arabia-oil/staging/ref-sweep{,-10row}/`; `docs/country_notes/saudi-arabia.md` |
| **Saudi GulfPub route-consistency pass** | low/medium matches unfinished; no replacement candidates staged | `docs/country_notes/saudi-arabia.md` |
| **GulfPub route-comparison QC leg** | not started (Baird: later) — compare drawn routes vs GulfPub geometries in the packet's route-integrity leg; distinct from the shipping attribute crosswalk | `docs/workflows.md` §6; `docs/sops/qc.md` |
| **Handoff-packet rollout (Arabic-speaking gas)** | Egypt pilot 2026-07-15, Libya done 2026-07-28; next Algeria 126 rows (shares the `scm/y` defect), then Qatar 59, UAE 39, Oman 23, Tunisia 21 | `docs/workflows.md` §6; `docs/country_notes/{egypt,libya}.md` |
| **Nigeria divestiture ownership sweep** | not started | `docs/country_notes/nigeria.md` |
| **Japan P1050 owner: JAPEX or ENEOS?** | JOGMEC 2024 vs the dead 2022 edition; needs an independent source, do not apply ENEOS off one document | `notes/escalation-2026-08-12-unarchivable-xlsx-refs.md` §2 |
| ~~Gazprom Orenburg refs unarchivable~~ | RESOLVED 2026-08-12 via the sibling edition in Wayback | `notes/escalation-2026-08-12-unarchivable-xlsx-refs.md` §1 |
| **United States** | deepwater-export open item; 131-row Stage A slot unstarted | `docs/country_notes/united-states.md` |
| **Iraq oil** | Grand Faw third line, P0544 status; first OSM + GulfPub recon (2026-07-28) untriaged, no oil sweep or packet to carry it | `docs/country_notes/iraq.md` |
| **Egypt gas recon (GulfPub + OSM, 2026-07-29)** | standalone, not in the packet; 40 all-`NEAR_MISS` additions over the gate | `docs/country_notes/egypt.md` |
| **Libya gas recon (GulfPub + OSM, 2026-07-28)** | standalone, not in the packet; the GulfPub file also holds untriaged `Oil_*` tabs — the only Libya oil output | `docs/country_notes/libya.md` |
| **Iraq gas recon (GulfPub + OSM, 2026-07-29)** | standalone (packet tabs retired); 30 OSM `ROUTE_FOR_EXISTING` traces; OSM `MATCH_QUALITY` | `docs/country_notes/iraq.md` |
| **Pakistan gas recon (GulfPub + OSM, 2026-08-07)** | standalone; OSM coverage effectively absent (9 features) — do not read as agreement | `docs/country_notes/pakistan.md` |
| **India gas recon (GulfPub + OSM, 2026-08-10)** | standalone; GulfPub crossed both gates; thin OSM overlap is granularity, no `geoarea_weight` override | `docs/country_notes/india.md` |
| **Malaysia gas recon (GulfPub + OSM + Malaysian Gas Map, 2026-08-12)** | standalone; all three crossed the additions gate; nothing to Discovery until the §4 scope ruling | `docs/country_notes/malaysia.md` |
| **Ukraine gas recon (GulfPub + OSM, 2026-08-12/14)** | standalone; 23 named GulfPub discovery candidates; OSM 1,003 additions are scope, not signal | `docs/country_notes/ukraine.md` |
| **Ukraine oil** | never swept (20 rows); expect the gas pass's empty citation base | `docs/country_notes/ukraine.md` |
| **Malaysia oil** | never swept (5 rows P7908–P7912); the concrete form of the gas scope question | `docs/country_notes/malaysia.md` |
| **Saudi / Iran gas GulfPub recon (2026-07-29 re-run)** | standalone, in no packet; read as fresh runs, not deltas — packet `Gas_GulfPub` tabs are stale | `docs/country_notes/{saudi-arabia,iran}.md` |
| **Israel gas P3620 Ashdod–Ashkelon gap** | applied 2026-07-23 but geometry still partial (Ashkelon-side ~2.4 km has no public vector) | `batches/israel-gas/archive/route-creation-p3620-p3657/README.md`; `docs/country_notes/israel.md` |
| **Iran open items** | P6074 verify-before-removal; P5367 reclassify as Neka–Ray segment | `docs/country_notes/iran.md` |
| **LNG carrier quarterly reconciliation** | orphaned — its `instructions.md` methodology is not in this repo | `docs/archive/PROJECT_SETUP_AND_CONTEXT.md` §9/§11 |

## 3. Staged, awaiting Baird's manual application (research complete)

Roster `applied` is blank for every country, deliverable presence is not a signal (Iraq/Iran xlsx pruned), and Saudi + Egypt are **partially applied** on the live sheet — verify per cell before pasting. `SheetRow` locators are re-derived at build time since 2026-07-28 (`_restamp_sheet_rows`; `docs/reference/gem_schema.md`).

- **Kazakhstan gas** — first pass 2026-08-11, THREE files (`…_20260812_1255_ET_…handoff-{actions,evidence}.xlsx` + standalone recons); no line-wise register, `UNRESOLVED` on a per-string spec is often correct; only sourcing decides duplication. `docs/country_notes/kazakhstan.md`.
- **India gas** — first pass 2026-08-10, FOUR files (`…_20260810_1851_ET_…`); inverse of Pakistan — `UNRESOLVED` is weak here; PNGRB register crosswalk; 12 escalations. `docs/country_notes/india.md`.
- **Pakistan gas** — first pass 2026-08-07, THREE files (`…_20260810_1112_ET_…handoff` + `20260807_1530_ET` recons); SNGPL register crosswalk closes the bulk-load cohort; P4074 + P5486 survive. `docs/country_notes/pakistan.md`.
- **Iraq gas** — full pass rebuilt 2026-07-29, FOUR files (`…_20260729_1104_ET_…`); 13 escalations, 3 retractions (P4067, P7435/P6826, P6007). `docs/country_notes/iraq.md`.
- **Iran gas** — packet 2026-07-05 (+ re-pass 2026-07-07); 62.5% in-dev change rate; Owner NIOC→NIGC/IGTC class fix. `docs/country_notes/iran.md`.
- **Saudi gas** — packet 2026-07-08, rebuilt 2026-07-28 (`…_20260728_1731_ET_…{annual-indev,deepsweep}.xlsx`), partially applied; hinges on P1897–P1925 (§4). `docs/country_notes/saudi-arabia.md`.
- **Egypt gas** — handoff rebuilt 2026-07-28 (`…_20260728_1731_ET_…handoff-{actions,evidence}.xlsx`), partially applied (16/284); Nitzana = one linked decision; + 2026-08-27 deep sweep. `docs/country_notes/egypt.md`.
- **Israel gas INGL/TMNG batch 2026-07-23** — 2 new rows (P8001/P8003), 5 validation edits, 5 route candidates (P2197 QC-fail); route workbook predates the P8003 retrace, regenerate before use. `docs/country_notes/israel.md`; `batches/israel-gas/staging/{discovery,validation}-tmng-map/`.
- **Libya gas full pass 2026-07-28** — `…_20260728_1235_ET_…handoff-{actions,evidence}.xlsx`, work from ACTIONS; five rulings in its README `ESCALATIONS` row. `docs/country_notes/libya.md`.
- **US oil Delaware Express + Permian Express I–IV** (2026-06-11/12) — `batches/united-states-oil/staging/update-{delaware,permian}-express/staged_updates.json`; `docs/country_notes/united-states.md`.
- **Saudi oil ref-sweep 10-row batch** — `batches/saudi-arabia-oil/staging/ref-sweep-10row/`; `docs/country_notes/saudi-arabia.md`.

## 4. Decisions needed from Baird

- **Repair the `independent` flag in 11 other scopes (1,337 units) and rebuild their workbooks** — one command (`repair_independence.py --all --apply`), but it changes researchers' current review surfaces. `notes/escalation-2026-08-27-independent-flag-outlived-its-refs.md`.
- **GGIT gas SheetRow 3114: `ProjectID` overwritten with a URL — restore `P5596`** (one pre-verified cell, gas F3114; also explains a route-sync audit entry). `notes/review-2026-07-31-route-sync-drift-other-rows.md`; `docs/country_notes/china.md`.
- **Egypt gas: are P8055 and P8009 one pipeline?** (Trans-Sinai / Abr Sinai; both staged as corridor-only partials) — `docs/country_notes/egypt.md`.
- **Egypt gas: P8055's whole citation base is one confirmed-404 GASCO PDF** — re-source Length/Diameter/Cost via Update before any ref drops; re-check Wayback first. `docs/country_notes/egypt.md`.
- **Route three-way sync drift, 39 rows, two ours (P7338 oil CV1210 `RouteType` flip; P5596 above), two urgent (P7274, P5970)** — `notes/review-2026-07-31-route-sync-drift-other-rows.md`.
- **Malaysia gas scope: are offshore field-to-shore feeders in GGIT?** Yes ⇒ Discovery campaign of ~30–65; no ⇒ write the rule into the country note. `notes/escalation-2026-08-12-malaysia-gas-recon-scope.md`.
- **P1897–P1925 (Saudi gas, 29 rows) class decision** — unanswered since `notes/escalation-2026-06-19-saudi-gas-opec-block.md`; resurfaced in the 07-08 packet.
- **Libya cluster A: does P0483 aggregate P1862–P1865 (+ P1789)?** delete members or make P0483 a network row (blank Status + `PipelineNetworkGrouping`, never `n/a`). `docs/country_notes/libya.md`.
- **Libya condensate line P6709 in the GAS tracker** — move to GOIT (P6705/P6713 already deleted). `docs/country_notes/libya.md`.
- **`scm/y` zero-capacity class defect (4 Libya + 4 Algeria)** — ×1000 fits Libya, not Algeria; no blanket fix. `notes/escalation-2026-07-28-scm-capacity-units.md`.
- **ASB length mi→km defect, 33 rows (14 Libya + 19 Iraq, two different fixes)** — test the remaining ASB countries the same way. `notes/escalation-2026-07-28-asb-{libya,iraq}-length-units.md`.
- ~~GulfPub gas `Length` is miles~~ — FIXED AND RE-RUN 2026-07-29. `notes/escalation-2026-07-29-gulfpub-gas-length-miles.md`.
- **GGIT small-diameter inclusion threshold** (6–8in gathering laterals vs 34 gathering rows already tracked) — one-time scope ruling. `batches/libya-gas/staging/recon-gulfpub-20260728/staged_addition_scope.json`.
- **Roster `applied` dates** for the Iraq/Iran packets — `campaigns/ggit-2026/roster.csv`.
