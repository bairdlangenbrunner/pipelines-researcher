# Plan — China / Jiangxi gas deep sweep **v3** (2026-09-03, not yet run)

Trigger: MZ's review of v2 (`pipelines_batch_20260902_1232_ET_china-jiangxi-gas_deepsweep.xlsx`,
email thread "Updated Jiangxi file", 2026-09-03). Overall verdict: *"most of the links are
relevant … looks really good"*, with four points. Each one is a **method gap in the engine**, not
a Jiangxi-specific miss, so the fixes below are generic and v3 is the first run under them.

## MZ's four points → what was wrong in the engine → what changed

| # | MZ's point | Why v2 did this | Fix (landed 2026-09-03) |
|---|---|---|---|
| 1 | Lots of blank data on operating projects; look for missing capacity, length, diameter etc. | The worklist classified a blank value as `SKIP` — a non-unit nobody owed. v2 skipped **571** blank cells and staged **4** fills; the contract said "DEEP-FILL … best-effort". | `build_ref_worklist.py --owe-fills` → new class **`MISSING_VALUE`** (241 units on these 44 rows, 171 on `operating`). Fills leg now OWES each one a sourced `FILL` or an `UNRESOLVED` with a note. Gate **J** lists owed blanks with no record. |
| 2 | P4776's ref contains cost and construction date but they were not added to those columns; check found sources for additional key info. | No per-document exhaustion rule. One subagent per row × one owed cell at a time: a source was consumed for the cell it was found for. P4777's 825 km / 3.1 bn RMB / Oct 2008 sat in the Sina article staged on P4776 while P4777's Length/SegmentCost/Construction shipped `UNRESOLVED`. | **Exhaustion rule** in the SOP, the contract and the brief template: every document read for every column AND every sibling row; `cross_row_leads[]` in the shard so the orchestrator routes cross-row facts (findings do not propagate across a fan-out). |
| 3 | Some links don't contain info about the relevant pipeline — keyword matching on "A" or "B" instead of "A-B". | `url_verifier` had a `name=` check since July but the deep-sweep contract never passed it; a ref was accepted on *value present*. 9 v2 records self-describe as "generic/system-level"; Fuel/PipelineType/Location/Status refs (47% of `REFS_ADDED`) are the exposed class. | `--name` mandatory; every verification carries **`name_found`**; `merge_qc.relevance_qc` caps a unit whose refs never name the pipeline at `low`; `--verify-existing` flags existing refs `name_absent`; gate **I** lists unnamed + unchecked units. |
| 4 | Limited range of sources; try to find two refs per data point. | Two-source was a tier rubric, not an obligation. **168 of 270 `REFS_ADDED` are single-source**; 7 documents carry 166 units (qianzhan PDF 53, quannan 24, SSE bond 22, en.wikipedia WEP 18, jxgajc capture 17, huaon 16, trqi.sinopec 16). | Second source is OWED: different publisher AND document class, notes say what was searched when none found. Gate **K** counts single-source `REFS_ADDED`; A/C catch one-origin rows and dominant documents. |

All four are also written into CLAUDE.md standing rule 4 as corollaries (a)–(d).

## Scope

Same 44 rows as v2 (41 Jiangxi-terminus + P4657/P4934/P4947). Worklist rebuilt with `--owe-fills`
on a fresh snapshot:

```
units 652 = MISSING_REF 382 / MISSING_VALUE 241 / HAS_REF 29     (v2: 411, no MISSING_VALUE)
fills owed by status: operating 171 / proposed 39 / construction 21 / shelved 6 / cancelled 4
fills owed by column: Pressure 42 / Proposal 37 / Construction 31 / Owner 30 / SegmentCost 26 /
                      FuelSource 22 / Start 17 / Diameter 16 / Capacity 13 / Length 7
```

Pressure (42) is owed but low-yield in Chinese approvals unless the EIA states 设计压力 — do not
force it. **Work order for fills: Length → Diameter → Capacity → StartYear1 → ConstructionYear →
SegmentCost → Owner → FuelSource → Pressure, operating rows first.**

## Carry-forward rule (v2 → v3)

v3 **carries v2 forward and supersedes it**; it does not re-discover. Reuse
`batches/china-jiangxi-gas/staging/deepsweep-20260902/carry_prior.py`'s pattern:

1. Re-key every v2 `REFS_ADDED` / `REVERIFIED` onto the fresh worklist (`sheet_row` may move —
   the gas tab re-sorts).
2. Re-verify each carried URL **with `--name`** so every carried verification gains `name_found`.
   A carried ref that comes back `name_found: false` is a **re-read**, not a carried pass.
3. Carried `FILL`s go into the store as `class_in: FILL` with the fresh `sheet_row` (never a side
   file — v2's `carried_fills.json` was read by nobody).
4. Only v2's `UNRESOLVED` (127 ref units) + all 241 `MISSING_VALUE` + the relevance re-reads are
   researched.

## Re-research list — concrete, in priority order

1. **Exhaustion pass over the seven dominant documents FIRST, before any new search.** Each is
   already verified live; read each once for every column of every in-scope row it names, and
   stage the matches. Expected yield is the cheapest in the batch:
   - `finance.sina.com.cn` article on P4776 → **P4777** `Length` 825 km, `SegmentCost` 3.1 bn RMB,
     `Construction` Oct 2008 (MZ's own example); check P4778/P4779 while there.
   - qianzhan DRC-plan PDF (53 units) → lengths / diameters / schedules for every grid row it lists;
     it is ONE origin, so anything it sources stays `medium` until a second class lands.
   - SSE bond prospectus (22 units, Operator only so far) → the issuer's asset table usually
     states length, diameter and year per line; it is an **operator disclosure**, a different
     class from the DRC plan, so it is the natural second source for the grid rows.
   - quannan PDF (24), huaon (16), trqi.sinopec (16), jxgajc Wayback capture (17): same treatment.
2. **P4776 `Diameter` and the other 13 owed `Diameter` cells** — approvals (核准批复) state 管径;
   search per row.
3. **Blank `Owner` on 20 operating rows** — the SSE prospectus + 企查查 (`m.qcc.com` is a WAF 567,
   access failure, keep trying via Wayback) + Jiangxi Natural Gas Group disclosures. Stage on the
   OO tab (`tab: operators_owners`).
4. **Relevance re-read of the exposed class:** the 9 records whose notes say "generic/system-level",
   and every Fuel / PipelineType / Location / Status ref sourced from a system page. Where the page
   names only the trunk, either find the segment-level page or downgrade with a note.
5. **Second-source pass on the 168 single-source `REFS_ADDED`**, by document class: for a unit
   sourced from the DRC plan, look for the approval or EIA; for one sourced from press, look for the
   regulator. Log the search in notes when nothing lands.
6. **Re-open the harvested pool:** gate G reports 36 rows with unopened live pool URLs (P4649/P4657
   29 of 31; the P479x/P5861/P4947 cluster 10 of 11); gate H reports two unopened Save-Page-Now
   origins (toutiao 7394374433810432575 on the grid rows; news.china.com.cn 2022-12-19 on the
   WEP cluster; sina 2021-04-27 on P4928/P4931/P4934). Open every one; report `harvest_opened`.
7. **P5888** (gate A: the only row on one host, sohu.com) — needs a second origin or a prose reason.
8. Carry the open v2 adjudications unchanged: P4778 ↔ P5861 reciprocal redundancy; Phase I/II
   operator question (P5862 sentinel); P4788 length/route; P5865/P5866 route redraws.

## Run recipe

```bash
STG=batches/china-jiangxi-gas/staging/deepsweep-<date>
./scripts/refresh_csvs.sh
python scripts/build_ref_worklist.py --tracker gas --country China --province Jiangxi \
  --include-pids P4657,P4934,P4947 --owe-fills --verify-existing --out $STG/worklist.json
python scripts/harvest_wiki_citations.py --worklist $STG/worklist.json --out $STG/wiki_citations.json
# carry v2 forward (re-key + re-verify --name), then fan out from
#   docs/sops/templates/deep_sweep_brief.md  (copy → $STG/BRIEF.md, fill the scope blocks)
# … merge chain as v2 (harvester LAST), then:
python scripts/sweep_gates.py --staging $STG/          # quote A–K counts in the delivery note
python scripts/build_ref_workbook.py --staging $STG/ --output batches/china-jiangxi-gas/deliverables/pipelines_batch_<stamp>_china-jiangxi-gas_deepsweep.xlsx
```

Delivery note must report, in this order: fills owed / filled / unresolved by status; gate I
(unnamed refs) count; gate K (single-source) count vs v2's 168; dominant-document table vs v2's.
v2's workbook and staging move to `archive/deepsweep-v2-20260902/` on delivery — one pending state.

## Baseline (v2, measured 2026-09-03 with the new gates)

```
sweep_gates.py --staging batches/china-jiangxi-gas/staging/deepsweep-20260902/
A 1 (P5888)  B 0  C 33  D 0  E 0  F 0  G 36 rows  H 34 rows
I 0 unnamed / 286 UNCHECKED (v2 never passed --name)   J skipped (no --owe-fills)   K 168 of 270
```
