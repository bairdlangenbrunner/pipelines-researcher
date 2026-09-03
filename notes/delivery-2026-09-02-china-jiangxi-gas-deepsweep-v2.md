# Delivery — China / Jiangxi gas, deep sweep v2 (2026-09-02)

**ONE file to work:**
`batches/china-jiangxi-gas/deliverables/pipelines_batch_20260902_1232_ET_china-jiangxi-gas_deepsweep.xlsx`

Staged, not applied. The 2026-08-26 v1 workbook and its staging dir are archived at
`batches/china-jiangxi-gas/archive/deepsweep-v1-20260826/` — v2's 44 PIDs are a strict
superset of v1's 18, so there is exactly one pending state and one workbook.

## Scope

44 rows: all 41 Jiangxi-terminus gas rows **plus** the three national mainlines that
transit the province (P4657, P4934, P4947), which v1 excluded. Legs: `refs`, `fills`,
`validity`, **`status-review`** (added this pass). No OSM recon, no routes leg, no
discovery — not selected.

The 18 rows v1 swept were carried forward, not re-discovered: every prior `REFS_ADDED`
was re-keyed onto the fresh worklist (the gas tab re-sorted, all 18 moved -2 rows), its
URLs re-verified, and only the `UNRESOLVED` units re-researched.

## Numbers

| | |
|---|---|
| rows / records | 44 / 453 |
| ref-lane records | 411 |
| **REFS_ADDED** | **270** |
| UNRESOLVED | 127 |
| REVERIFIED | 12 |
| DEAD_LINK | 2 |
| validity concerns | 26 |
| status reviews | 12 (6 stale / 4 unclear / 1 change / 1 confirm) |
| fills | 4 |
| distinct verified hosts | 49 |

Tiers on sourced ref units: **82 high / 175 medium / 14 low / 11 blank**; `independent: true`
on 71 (73 store-wide, counting the fill lane). v1 shipped 98 `REFS_ADDED` across 18 rows;
v2 ships 270 across 44. All four counts above are the REF LANE; the 4 fills, 26 validity
concerns and 12 status reviews are counted separately and carry their own classes.

Status reviews read 12, not the 16 records staged: a row has ONE status, so it gets one
verdict, and `split_shards` now keeps the last shard's (4 superseded — P4786×1, P5865×2,
P5866×1). See the method-defects section.

## Gates A–H

| gate | result |
|---|---|
| A source diversity | **1** — P5888, one sourced unit resting on `sohu.com` alone |
| B false `high` | **0 — PASS** |
| C dominant document | 33 flags (see below) |
| D independence flag | **0 — PASS** |
| E orphan refs | **0 — PASS** |
| F banned / GEM sources | **0 — PASS** (0 GEM surfaces, 0 abarrelfull) |
| G unopened live pool URLs on `UNRESOLVED` rows | 36 rows |
| H unopened recovered SPN origins | 34 rows |

**Gate C is concentration, not a defect.** Six documents carry 145 units between them:
`img9.qianzhan.com/…20230714-d7d735aa6fb9eae9.pdf` (50), `mee.gov.cn` (36),
`quannan.gov.cn/…faad1fb7c1214b8a8394299531ab10a8.pdf` (24),
`static.sse.com.cn/…242696_20250403_SXBW.pdf` (22),
`en.wikipedia.org/wiki/West–East_Gas_Pipeline` (18), `trqi.sinopec.com` (16),
`huaon.com` (16). Each flagged unit is a `high` whose second origin is one of those —
worth a look when deciding whether "two sources" is really two.

## The findings that need a human

1. **P4778 ↔ P5861 — reciprocal double-count, deliver as ONE cluster.** Two agents at
   opposite ends of the fan-out each filed a `__REDUNDANCY__` naming the other's row:
   P4778 "Phase I, Gao'an–Xinyu" vs P5861 "West-East Gas Pipeline 2, XinYu Branch
   (Gao'an–Xinyu)" — identical corridor, same StartYear. That reciprocity is
   *corroboration*, not two findings. Recommend adjudication, not unilateral deletion.
2. **The Phase I / Phase II operator split, filed as a cohort question** (P5862, plus
   cross-shard tension notes on P4785 / P4790 / P5860 / P4793). Batch 17 found it on ONE
   row, buried inside a `FuelSource [ref]` record's notes on an `UNRESOLVED` unit — the
   same burial pattern as Egypt's P5121 `StartYear1`. Promoted to a coordinator sentinel
   after cross-tabbing all 44 rows: 23 carry a phase label (15 Phase I / 8 Phase II),
   12 have a blank `FuelSource`, 5 filled, **3 in tension**. The CCXI credit-rating PDF
   splits the operator by phase. Not auto-corrected.
3. **Two aggregate-vs-segment defects.** P4788's `SegmentCost` (2,172,600,000 CNY) is the
   total for all four Ganzhou South branches, not this segment; P4928's `Capacity`
   (30.00 bcm/y) is the WEP3 *system* total, not the Ji'an–Fuzhou East Section.
   By contrast **P4934's 125 bn RMB is correct** — that row *is* the whole-system row,
   so a system-level total is the right match there (adjudicated, no change).
4. **P4947 owner misattribution risk** — staged as the full WEP2 trunk, Khorgas→Guangzhou,
   where the west/east sections have different owners.
5. **P5862's 30.1× route-vs-sheet length ratio is a route-geometry defect, not a data
   error** — the geojson, not the 18.45 km, is what's wrong.
6. **P5865 / P5866 — the access failure was BEATEN, and it changed both rows.** The two
   `jxgajc.com` completion-acceptance filings (the host no longer resolves in DNS, so
   Wayback is the only route) were read at 12:1x off captures `20230902005946` (P5865) and
   `20230902105154` (P5866), staged as `batch_20_wayback_recovered.json` — 26 records, 21
   ref units. **The earlier "the limit is IP-level and still in force" reading was wrong:**
   archive.org's 429 / `http=000` is PER-REQUEST and transient. A plain bounded retry loop
   (6 tries, ~6–8 s apart) returned 200 on both captures within a minute, and `url_verifier`
   confirms 200 on both URLs. What did *not* work, so nobody re-tries them: `web.archive.org`
   has **no AAAA record** (IPv6 egress is not a route), the Memento aggregator
   `timetravel.mementoweb.org` returns **403 Request Denied**, and the IA login cookies in
   `~/.config/internetarchive/ia.ini` made no difference (the first 200 came with an empty
   `Cookie` header). Rule: a 429 from archive.org is a *rate* limit, so the answer is
   patience inside the same session, not a different day or a different IP.
   What the documents settled:
   - **P5865's status is wrong and its own new ref proves it.** 竣工 (construction
     completion) Nov 2021 → recommend `construction` → `operating`, `StartYear1` = 2021.
     `medium`, deliberately: 竣工 is completion, not gas-in.
   - **P5865 `StartPrefecture/District` = `Fengcheng`, not `Yifeng`** — the filing opens
     「项目位于樟树市、丰城市境内」 and allots 12.7 of 20.2 km to 丰城市; Tuochuan is a town of
     Fengcheng. Yifeng is a different county under the same Yichun prefecture, which is the
     likely source of the mix-up. Staged tinted on `Gas_Backend`, not silently applied.
   - **P5865's capacity stays `UNRESOLVED`** — the document prints 5×10⁶ Nm³/a (0.005 bcm/y)
     against the sheet's 0.13, and that printed figure is itself implausible against sister
     segment P5866, so it settles nothing. The agent that recalled ~5×10⁶ Nm³/a from memory
     was right to refuse to stage it, and it is still not staged.
   - **P5866 is fully corroborated on eight values exactly** — 19.12 km, DN500, 2017-12,
     2021, 0.50 bcm/y, 80,830,000 RMB, `FuelSource` verbatim, and `operating` at 14.6% of
     design. `StartPrefecture/District` filled (blank → `Jiujiang`).
   - **P5866's 6.43× capacity outlier flag is REFUTED and re-filed as a ROUTE defect** — the
     geometry is over-drawn against a documented 19.12 km branch. Routes to a §8 redraw, the
     same shape as P5862.
   - **No direction swap on P5866, deliberately.** The filing names Jinshawan → Hukou, the
     reverse of the sheet, but that is chainage/construction order; gas enters this branch
     from the national trunks at the Hukou distribution station, so the sheet reads as flow
     direction. Recorded so it is not rediscovered as a defect.
7. **P4777's length is unresolvable as stated** — six independent hosts give Phase I
   lengths from 553 km to 825 km. Flagged, not replaced.

## Method defects found in our own tooling (all fixed this pass)

Recorded in `batches/china-jiangxi-gas/staging/deepsweep-20260902/shard_normalizations.md`:

- **Batch 17 emitted two `__STATUS__` records keyed `sentinel:` instead of `ref_col:`.**
  `split_shards` routes on `ref_col`, so both would have fallen into the ref lane, matched
  no baseline and been dropped with a single WARN — a status-change finding lost silently.
  Shard repaired *and* `split_shards` hardened to accept the alias.
- **The verdict parser rejected a plainly-stated verdict.** Two records led with
  `Required status-review verdict: 'unclear'.` and parsed as blank, because the apostrophe
  was not in the separator class and "status-review" was hyphenated. Regex widened; status
  verdicts moved from `{stale 7, unclear 4, confirm 1, blank 2}` to `{stale 7, unclear 6,
  confirm 1}`.
- **The v1 sweep's one real fill reached no tab.** `carry_prior.py` correctly routes fills
  to `carried_fills.json` (a fill has no owed unit), but `build_ref_workbook` reads
  `pending_fills` from an **actions packet**, never from that file — so on a standalone
  deep-sweep build it is written by one stage and read by none. The lost record was
  **P4788 `Pressure [ref]` = 6.30 MPa**, sourced to the Quannan EIA PDF at 设计压力6.3MPa
  for the 信丰-瑞金段 by name. Re-injected as a shard, locator corrected 2679 → 2677,
  URL re-verified (403 — an access failure on `quannan.gov.cn`, not a deletion, and the
  same 403 the other 24 verifications against this document carry).
- **A row's status collected contradictory verdicts side by side.** `split_shards` appended
  every `__STATUS__` record, so P5865 reached `Gas_StatusReview` three times — `stale` from a
  batch-06 inference, `unclear` from the batch-17 followup, `change` from batch 20 once the
  blocked source was actually read — with nothing marking which was current. That is the
  silent-*duplication* twin of this batch's silent-loss defects: no record is lost, but the
  reader cannot tell a superseded verdict from a live one. A row has ONE status, so it now
  gets one verdict, last shard wins (the ref lane's `(pid, ref_col)` key already behaved this
  way); supersessions are reported, not swallowed. `__VALIDITY__`/`__REDUNDANCY__` are
  deliberately NOT deduped — a row can carry several distinct concerns.
- **A proposed value carried on a ref-lane record never tinted, and rendered as if it were
  the sheet's own.** `_backend_view` tints a value only from the FILL and STATUS lanes; a
  ref-leg record's values are *current-sheet context*, overlaid untinted. So P5865's
  Yifeng→Fengcheng correction and P5866's blank→Jiujiang fill printed on the primary paste
  surface **looking like existing sheet values** — worse than invisible. Re-filed as the
  designed pattern the workbook already supports: the ref record carries the sheet's current
  values, a `kind: FILL` twin on the same cluster carries the proposed value, and
  `_merge_ref_unit` unions both records' refs onto the one `[ref]` cell. `validate_shards`
  now keys duplicate detection by LANE, so that designed pair reads as a note instead of an
  ambiguous collision (it also surfaced the pre-existing pair on P5862 `Operator [ref]`).
- **Every row on `Gas_Validity` shipped with blank name columns.**
  `harvest_sentinel_findings` reads `pipeline_name` off the shard DOC and hardcoded
  `segment_name` to `""`, but `split_shards` wrote `{project_id, resolutions}` only — so the
  tab that carries a sweep's highest-value findings gave the reader a bare ProjectID. Fixed
  at the cause in both scripts (26 of 26 rows now named); the harvester fix is repo-wide and
  only fills what was previously empty.
- **`independent: true` on a single-origin unit** (P4788 `__VALIDITY__`) — the same defect
  Uzbekistan shipped 13 of. Corrected; gate D is now clean.
- **Citation FORM is now a structural gate.** `validate_shards.py` rejects a prose
  description written into a citation field and a bare host (a site root is a mutable
  navigation surface, never a citation — the Egypt `egyptoil-gas.com` lesson). Caught four:
  three prose-in-URL in batch 18, one angle-bracketed in batch 03, and `http://jskedun.com`
  cited bare four times.

## Harvest coverage — measured honestly

Pool: 187 harvested URLs, 100 live / 87 failed. 30 were opened anywhere; **70 are live and
were never opened** (one more was already the row's own `current_ref` — subtract those, or
the metric credits the leg with less reading than it did). **None of the 70 attaches solely
to the three transiting mainlines** (P4657 / P4934 / P4947), so the Uzbekistan parent-trunk
discount does not apply here the way an earlier draft of this note claimed; widening "trunk"
to every national-mainline segment in scope (the five WEP rows, P4928 / P4931, P5861) takes
only 18 out, leaving **52 that touch a Jiangxi provincial row — the real untested yield**.
Failure reasons: 22×404, 18× SPN instruction
endpoint, 10×403, 9× ConnectTimeout, 7× ConnectionError, 6×412, 6×567, 3×401.

Separately, `FINDING-spn-citation-form.md` in the staging dir: 18 harvested citations point
at `web.archive.org/save/<url>`, the Save Page Now **instruction** endpoint, not a snapshot.
`url_verifier` rightly fails them, so they never entered the live pool and gate G was blind
to them — 10 of the 18 origins are live. Recovered into `spn_recovered_origins.json`; gate H
reports them.

Watch for `fzggw.jiangsu.gov.cn` in the pool — **Jiangsu is not Jiangxi**, a false lead the
harvest surfaces repeatedly.

## One flag for timing

**MZ owns 23 of the 44 rows** (XJ 20, AY 1) — a larger share than earlier Jiangxi batches
carried. A same-week live-sheet edit on those rows is the one failure mode staging cannot
catch; worth checking `researcher_lanes.txt` against the sheet's own edit history before
pasting.
