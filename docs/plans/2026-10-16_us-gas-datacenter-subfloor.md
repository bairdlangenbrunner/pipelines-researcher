# US gas pipelines serving data centers, including lines under 25 km (plan, 2026-10-16)

Goal: every US gas pipeline that supplies the data center buildout is a GGIT row, whatever its length, and carries `DataCenter = yes` with a `DataCenter [ref]`. Background and the funder context are in gem-desk `grants/beyond-carbon/2026-10-16-data-center-pipelines-research-plan.md`. That plan left two questions open, and Baird settled both on 2026-10-16: lines under 25 km go into GGIT itself (no supplement tab), and the tag is a yes/blank column with its own ref.

## Why the 2026 US discovery missed them

The October 2 discovery seeded only EIA projects of 15.5 mi (25 km) or more and sent shorter ones to monitor (`batches/united-states-gas/staging/discovery-seeds-20261002/below_floor.csv`, 543 projects). The pipelines that explicitly serve data centers are mostly short laterals: Energy Transfer's Abilene lateral (14 mi), the Tiger lateral (12 mi), Kinder Morgan's Creekside lateral (11.2 mi), Transwestern's Green Chile (17 mi). Many are Texas intrastate lines that never reach FERC, so they barely appear in EIA either.

EIA's August 2026 workbook, 137 current projects, as counted 2026-10-16: 8 name data centers in demand served or notes (6 match a GEM row on the crosswalk, Green Chile and Dalton Lateral II do not). 22 more cite power demand and are under the floor; most are compression-only. EIA alone is a few dozen leads. Most new rows will come from the GOGPT side: 149 US data center gas plants in development, 123 of 153 plant locations within 15 km of an existing GGIT route.

## Rulings (Baird 2026-10-16)

1. **`DataCenter = yes` needs a validated ref that names this pipeline and ties it to a data center**: the filing, the developer, the shipper, a named end user (a campus or a hyperscaler), or press stating it. Blank otherwise. A utility shipper whose load forecast is driven by data centers, or a claim made only by project opponents, stays blank with a note in `ResearcherNotes`. Standing rule 4 applies as usual (one validated ref suffices).
2. **A compression-only expansion tied to data centers is a new row with `LengthKnown = 0`** (Diameter blank, `no route`), in the parent-system / `SegmentName` shape. The parent system row is not tagged for it.
3. **No length floor** for a pipeline tied to data centers. Pipe inside the plant fence and local utility distribution mains are still out of scope (that is a pipeline-type rule, not a length rule).
4. **The columns are tracker-wide** on the Gas tab, so they are never renamed later. Only the US is researched now.
5. **The GOGPT plant pass is in scope**, not deferred.

## Steps

**Step 0, the columns.** Order matters: the sheet first, then everything that reads the header.
- Live sheet (authorized write only): append two columns to `Gas pipelines` after `SciGridNames` (grid 132 to 134, columns EC and ED). Row 2 there is `=COLUMN()` on every column, not a typed number, so EC2 and ED2 get the same formula (written USER_ENTERED, the one non-RAW write). Row 3 gets the headers `DataCenter` and `DataCenter [ref]` (RAW). Row 1 (the banner) stays blank. Two rows on `Data dictionary - Gas pipelines` (rows 134 and 135): column A is `=INDEX('Gas pipelines'!$A$2:$EB$2, MATCH(...,'Gas pipelines'!$A$3:$EB$3,0))` on every row, so the new rows use the same formula widened to `$ED`, column B is the name, column D the definition. Nine personal filter views end at column 132 and do not widen by themselves; only `PipelineDirectionality` has a dropdown.
- After the write: `gem-db-ops/gem_colmap.py` (`data_center`, `data_center_ref`; adding them earlier would read as a missing column), refresh snapshots.
- Repo, can go first: `DataCenter` takes `yes` or blank (`controlled_vocab.md`, `check_shard_coverage.py`, `check_discovery_staged.py`, `goit-ggit-data-ops/updates/qc/tracker_qc.py`). `ref_pairs.py` needs no change: an exact name match pairs `DataCenter [ref]` with `DataCenter`. A blank `DataCenter` is never an owed fill (not in `FILL_PAIRS_DEFAULT`), because blank is the normal state.

**Step 1, the floor becomes an argument.** `country-discovery` takes `args.minKm` (default 25; 0 = no floor, any sourced length including 0 for compression-only). `check_discovery_staged.py --min-km 0`.

**Step 2, seeds** (`batches/united-states-gas/staging/discovery-datacenter-seeds-<date>/build_seeds.py`), each seed with a source label:
- A. EIA, releases from 2024 on, unmatched on a fresh crosswalk, any length, demand served or notes naming data centers or power. Reversals and abandonments are dropped.
- B. The named leads from the gem-desk web survey: Abilene lateral, Creekside lateral, Amarillo Expansion (CP26-581), the DT Midstream NEXUS interconnect, Homer City supply, Cheyenne Power Hub, Kosciusko Junction.
- C. GOGPT data center plants (fresh pull through gem-db-ops, `Captive industry type = data center` plus a notes search), one seed per plant with coordinates, owner, MW, status, and the nearest GGIT routes. The plant agent finds how the plant gets its gas: a new lateral (a new row), an existing GGIT row (tag it), on-site or behind-the-meter supply with no new pipe (recorded, no row), or not found. Texas plants are checked against Texas Railroad Commission T-4 permits as well as FERC.

Run as five regional slices like the October 2 discovery (`seedIntro`/`seedSearch` per source, `priorStaging` = the 10-02 runs, `vetRule` = rulings 1 to 3 above, `minKm: 0`).

**Step 3, tag existing rows.** An update batch over the 81 US in-development pipelines, operating rows with a 2023 or later start, the EIA rows matched to GEM, and the existing rows step 2 points at. Each tag is a `DataCenter` fill with its ref, through the review app and `push.py`.

**Step 4, deliver.** Discovery workbooks, review app, `append_new_rows.py` for the new rows (per-batch authorization), `push.py` for the tags. New laterals arrive routeless; §8 route creation can follow.

## Status

- 2026-10-16: plan written. Step 1 done (`country-discovery` `args.minKm`, `check_discovery_staged.py --min-km`). Step 0 repo side done: `DataCenter` checks in `check_shard_coverage.py`, `check_discovery_staged.py` and goit-ggit-data-ops `tracker_qc.py`; `controlled_vocab.md`, `gem_schema.md`, `workflows.md` §4 and the US country note updated; `append_new_rows.py` now reads the live grid width instead of a fixed 132. Sheet columns ADDED 2026-10-16 on Baird's authorization (Gas EC/ED, dictionary rows 134 and 135; backup `notes/sheet-write-2026-10-16-1628-add-datacenter-columns.csv`), `gem_colmap.py` maps `data_center` / `data_center_ref`, snapshots refreshed. Next: step 2 seeds.
- 2026-10-16, steps 2 to 4 staged, not applied. Seeds A, B and C built. Five regional slices plus three seedsOnly retries for seeds the search rate limit left unresearched; every seed has a disposition in its run's `seed_ledger`. 14 new rows, 0 `check_discovery_staged.py --min-km 0` findings. With no floor, that check now treats an unknown length as an owed fill, not a blocker, and accepts `LengthKnown = 0` with no unit. Tag pass: 217 rows (the worklist plus 9 rows discovery pointed at, a follow-up chunk), 10 `yes`. The consistency line for `yes`: EIA's demand served field or the developer says this project serves data center demand (medium), or names a campus, customer or hyperscaler (high). Blank with a note when data centers are only one of several demand drivers named, company-wide or for the project (Transwestern Desert Southwest P7840, Creekside Lateral), or the lead names the system and not this row (Kern River P3856, Enable P0161). Next: review-app decisions, then `append_new_rows.py` and `push.py`, each on Baird's yes for that plan.
- 2026-10-16, `DataCenterNotes` column ADDED on Baird's request (Gas EE, dictionary row 136; backup `notes/sheet-write-2026-10-16-1816-add-datacenternotes-column.csv`; `gem_colmap.py` `data_center_notes`). Every `yes` line carries a note on the related data center: the 10 tag fills (`merge_tags.py` reads `dc_notes/notes-*.json`) and the 13 new rows (in their vetted shards). The 21 matched existing cards were tag leads the tag pass already checked; `convert_matched_to_alias.py` drops them, and it has to be re-run after any re-merge of a discovery dir. Workbooks `…20261016_1821_ET…` supersede the 1806 set.
