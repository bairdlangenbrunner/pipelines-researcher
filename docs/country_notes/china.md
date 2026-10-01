# China

**Gas only this cycle** (decision 2026-07-29). Biggest single scope in GGIT: 984 gas
rows at the 2026-07-29 snapshot (23% of the tracker — 612 operating, 294 in-dev,
74 cancelled/shelved/retired; 971 domestic-only). GOIT has 363 China oil rows, staler
(140 pre-2024 `LastUpdated`), but oil is **out of scope until after the GGIT 2026
cycle**. Work happens **at the province level**, not whole-country.

## Division of labor (locked 2026-07-29)

- **MZ** owns China (+ HK, Taiwan, Macau, Mongolia, North Korea) for
  the GGIT 2026 cycle — active Jul 16–Sep 11, province by province, triage pace
  (solo). Their core work: **routes + wiki sync, operating rows first**. Cycle
  planning, their 529-row route-target list, and the "chinese researcher assignments –
  2026" sheet tab (keyed on `PipelineName`; 996 China-scope rows → 94 unique names)
  live in the **gem-desk repo**, `research-cycles/ggit-2026-pipelines-update/`.
- **Agent batches run AHEAD of their province queue**, pre-staging what triage pace
  can't cover: ref sweeps, value backfill, status re-verification, document-driven
  discovery. Routes and wiki edits stay theirs. Never re-audit a province they have
  finished without being asked.
- **National trunk systems are MZ's own scope**, excluded from agent province
  batches (see scoping idiom below).

## Backend structure (why province batching works)

- The gas backend is already province-organized: **30 provincial-grid networks**
  (`PipelineNetworkGrouping` ending `输气管网`, e.g. 山西输气管网) hold 756 rows;
  **41 national/transnational trunk systems** (西气东输一–五线, 川气东送, 中俄东线,
  陕京线, 中缅, Central Asia A–D, …) hold 227 rows; 1 row has a blank grouping.
- Province fields are effectively complete (Start 977/984, End 984/984; the two known
  bugs — P7609 "Shangdong" typo, P6902 blank — were fixed on the sheet by 2026-07-29).
  845/984 rows start and end in the same province. Chinese names on 979/984 rows.
- Route quality is the tracker-wide weak spot: 285 `very low` + 165 `low` + 101
  `no route` — over half. That's MZ's lane, not the agent's.

## Batch scoping

Batch dirs: `batches/china-<province>-gas/`. Worklist scoping:

```bash
python scripts/build_ref_worklist.py --tracker gas --country China \
    --province Guangxi --exclude-network-regex '^(?!.*输气管网$)' \
    --out batches/china-guangxi-gas/staging/ref-sweep/worklist.json
```

- `--province` matches **either terminus** (`StartState/Province` / `EndState/Province`);
  transited provinces don't count.
- The negative-lookahead regex keeps only provincial-grid rows — trunk rows
  terminating in the province (e.g. Guangxi has 9: Sino-Myanmar branches, three
  WEP2 branches, 新粤浙, 渝黔桂, 川滇黔桂) drop out to MZ's trunk scope. Drop
  the flag to see the full province picture including trunks.
- A trunk-scope batch, if ever agent-run, would be `batches/china-trunks-gas/`
  (invert the regex). Currently not planned.

## Research approach

- **Research runs in Chinese.** Query in Chinese, cite Chinese-language sources;
  `OtherLanguagePrimaryPipelineName` is filled on 979/984 rows and is the search key.
- **Expect dead/unreachable sites and route around them** (Baird, 2026-07-29): many
  Chinese sites are geo-blocked, bot-blocked, or link-rotted from here. When a source
  fails, find an alternative *working* host for the same information — official
  announcements are widely republished (Xinhua, 人民网, sohu, sina, 澎湃, trade press
  like 北极星) — or cite a `web.archive.org` snapshot. Republications of ONE original
  still count as ONE source for corroboration (standing rule 4).
- **Timeliest angle (Baird, 2026-07-23):** whether unfinished in-dev pipelines were
  re-included in the **15th Five-Year Plan** (2025 closed the 14th) — a systematic
  status-review pass across the in-dev rows, driven by national/provincial FYP and
  重点建设项目 (key-construction-project) lists.
- **Sources:** provincial 发改委/能源局 plans and approvals, NDRC/NEA, PipeChina
  (国家管网), CNPC/Sinopec disclosures, trade press 北极星 (`bjx.com.cn`) and cnlng.
  Standing rules apply (no GEM, no fabricated URLs, ≥2 independent).
- **Recon sources are weak here:** GulfPub carries **120** China gas features
  (trunks only — useless against the provincial grids; useful if the trunk scope
  ever runs). OSM would need per-province Overpass pulls, coverage unverified.
  Discovery signal comes from **document sweeps, not scraped geodata**.
  - The count was **108** until 2026-08-12, when the reference-side country filter was found
    comparing GulfPub's country string with `==` and dropping every multi-country record —
    for China, the cross-border import trunks. Fixed same day:
    `notes/escalation-2026-08-12-multicountry-reference-filter-dropped-transit-trunks.md`.
  - `batches/china-trunks-gas/staging/recon-gulfpub-20260812/` is the re-run (the 07-30 dir
    is archived). **No workbook** — this batch never had a GulfPub deliverable, so there is
    no review surface to refresh. It moved hard: **118 overlaps / 2 additions / 532 gem_only
    / 18 status conflicts** (was 87 / 21 / 925 / 21). Only 4 of the falsified `gem_only`
    entries are down to this filter; the rest is **other matcher fixes landed since 07-30**,
    confirmed by the GEM pool being stable (986 → 988 China gas rows). If the trunk scope is
    ever worked, build off this dir, not the 07-30 numbers.

## Coordination gotchas

- **MZ edits the live sheet continuously** through Sep 11 — pull a fresh CSV at
  every batch start (standing rule, but load-bearing here) and expect `LastUpdated`
  drift between staging and apply.
- Province priority MZ sketched (gem-desk, 2026-07-23): Guangdong (current) →
  Guangxi → Jiangsu → Fujian; **Shandong/Hebei deliberately deferred** — Hebei has
  real double-counting risk against national trunk lines. Shanghai done.
- Known backend name-variant near-dupes ("Hebei Gas Pipeline Network" vs
  "…pipeline…", en-dash vs hyphen in "Hebei–Nanjing"); hydrogen rows live on a
  separate backend tab and are excluded from the China gas scope.

## Province ledger (agent-side; batches only, MZ's progress lives in gem-desk)

| province | scope (grid rows) | status | batch |
|---|---|---|---|
| Guangxi | 43 (+9 trunk excluded) | pilot DELIVERED 2026-07-29, staged not applied | `pipelines_batch_20260930_1455_ET_china-guangxi-gas_deepsweep.xlsx` (re-tiered 2026-09-30) (rebuilt 09-04 so open validity concerns render orange on `Gas_Backend`; 07-29/07-30 builds archived); staging `batches/china-guangxi-gas/staging/deepsweep-pilot/` |
| Jiangxi | **44** — all 41 Jiangxi-terminus rows + the 3 transiting national mainlines (P4657/P4934/P4947) | **v3 DELIVERED 2026-09-10, staged not applied** — SUPERSEDES v2, which supersedes v1. Built off MZ's 2026-09-03 feedback (`notes/plan-2026-09-03-china-jiangxi-gas-deepsweep-v3.md`); delivery note `notes/delivery-2026-09-10-china-jiangxi-gas-deepsweep-v3.md` | `pipelines_batch_20260930_1455_ET_china-jiangxi-gas_deepsweep.xlsx` (re-tiered 2026-09-30) (10 tabs); staging `batches/china-jiangxi-gas/staging/deepsweep-20260903/`. `deliverables/` holds exactly one file: v2 (workbook + `archive/deepsweep-v2-20260902/`), v1 (`archive/deepsweep-v1-20260826/`) and the two intermediate 09-10 rebuilds are all archived |

## Route creation §8 — ALL 103 no-route gas rows (2026-07-30, staged NOT applied)

One pass over every `no route` China gas row (Baird 2026-07-30: include MZ's 33
operating rows — they don't make routes right now — plus P8028/P8029 and the 6
cancelled/shelved rows; duplicate pairs get the same route drawn). All research ran
in Chinese via parallel agents; every endpoint is a Nominatim geocode or
official-document coordinate of a SOURCED named place; all candidates are
`endpoints_greatcircle` at `very low (straight line/schematic)` (Egypt convention).
**80 candidate geojsons + 23 corridor-only partials**, three batches:

- **Wave 1 — Guangxi grid (23):** 18 candidates + 5 partials (P7655 start
  uncoordinated, P7660 no verifier-passing refs, P7663 existence unconfirmed,
  P7679 refs geo-blocked, P7680 start==end county seat).
  `batches/china-guangxi-gas/staging/route-creation/` →
  `…_20260730_1700_ET_china-guangxi-gas_route-creation.xlsx`.
- **Wave 2 — other provincial grids (38):** 28 candidates + 10 partials. **Batch-dir
  naming deviation (agreed 2026-07-30):** single cross-province dir
  `batches/china-gas/staging/route-creation-grids/` instead of per-province dirs →
  `…_20260730_1706_ET_china-gas_route-creation-grids.xlsx`. The three MULTI_BRANCH
  networks (P6229/P6230/P7448, Xinjiang) are drawn as ONE schematic leg each
  (trunk or best-sourced branch) with full topology in the routenote.
- **Wave 3 — trunk-family rows (42):** 34 candidates + 8 partials.
  `batches/china-trunks-gas/staging/route-creation/` →
  `…_20260730_1708_ET_china-trunks-gas_route-creation.xlsx`. (Trunk rows are
  MZ's scope, run here on Baird's explicit instruction.)

**Flags for human review** (all carried in the workbooks' notes columns):
duplicates drawn-same-route per Baird's ruling — P7666→P7664, P7534→P7531
(aggregate: family lengths sum exactly to 913.80 km); duplicate checks NOT
auto-drawn — P4957→P6002, P4678→P5024, P6230↔P7448 west-trunk overlap,
P7613↔P7646 shared 皖西支干线 corridor, P3894 = capacity upgrade of P0758 (reuse
P0758's real geometry at review); NOT-defects confirmed — P5923 (point tie-in
station, but its 20 km sheet length is likely wrong vs sourced ~0.8 km), P6586
(0.13 km confirmed by Chongqing DRC approval); sheet-value flags — P7645
EndProvince should be Anhui not Henan, P5052 StartLocation Yichuan not Yuheng,
P7585 length 39.24 vs 14.18, P7432 PID mapping doubt (~55 km Jintan vs 31 km
Liyang–Yixing), P7476 length 40.11 vs 52.35, P7689 endpoints in Hechi not Laibin,
P7678 "cancellation" ref is actually a 2020 approval-extension, P7713 "Heibei"
typo, P8028/P8029 embedded `\r` in PipelineName; retirement reviews — P6679/P6680/
P6681 (cancelled Hebei lines, documented connectors ~1/~0.1 km vs GEM 8.8/3.5 km);
row-split — P4513 (two corridors ~400 km apart).

**§8 step 6 apply — routes-repo half DONE 2026-07-30** (per-batch authorized):
79/80 candidates merged to `GOIT-GGIT-pipeline-routes` main (merge `3d943da2`,
branch `routes-china-gas-no-route-batch`) through its own `qc_routes.py` gate —
27 PASS + 52 WARN included (all length-ratio/geocode hints, expected for
schematics); **P3894 excluded on a QC FAIL** (endpoint-country mismatch
Russia→Russia vs DB Russia→China — consistent with the reuse-P0758-geometry
recommendation; now effectively a 24th partial). **Sheet-side half APPLIED
same day** (authorized after the merge — the two halves are one unit, cardinal
rule): 316 cells (RouteAccuracy/RouteNotes/RouteCreator/Route [ref] × 79 rows)
via `apply_route_candidates.py`, all readback-verified; backups committed in
`notes/sheet-write-2026-07-30-china-{guangxi-gas,gas-grids,trunks-gas}-route-columns.csv`.
Remaining work tracked in Baird's work Asana (gem-desk project). Workbooks
remain the review surface for the flags above.

**`RouteType` backfill — 2026-07-31 (defect + repair).** That 07-30 apply wrote
`RouteAccuracy` but **not `RouteType`**, leaving all 79 merged rows still reading
`Not mapped (but could be…)` (76) or `Unavailable (cannot find route)` (3) — the
sheet denied 79 routes that were live in the routes repo. Repaired the same day
under authorization: 79 cells written to `Mapped route (at any accuracy)`,
all readback-verified (backup
`notes/sheet-write-2026-07-31-china-gas-route-type-backfill.csv`).
`python scripts/audit_route_sync.py --country China --commodity gas` now returns
only P4939 (not ours — logged in
`notes/review-2026-07-31-route-sync-drift-other-rows.md`). The three-way sync
rule and the tooling that enforces it: `docs/sops/route_creation.md`.

## Open items

- **P5596 (Anhui Gas Pipeline Network / Bengbu Branch, Liuxiangzi–High-Tech Industrial
  Development Zone) — `ProjectID` cell overwritten with a URL; found 2026-08-27, NOT written.**
  GGIT gas SheetRow 3114 (cell F3114) reads `ProjectID =
  https://archive.org/details/p-5596-bengbu-branch` — the same value as its own, correctly
  placed, `Route [ref]`. Four independent signals give **P5596**: the neighbours run P5594,
  P5595, ⟨this row⟩, P5597, P5598; the archive slug itself reads `p-5596-bengbu-branch`;
  `P5596` appears nowhere else in either tracker (no duplicate-ID risk); and the routes repo
  already holds `P5596.geojson`. It is the only malformed ProjectID across all 4,342 gas +
  2,096 oil rows, and it is why `audit_route_sync.py` reports the row (`Mapped` + `high`) as
  "no live geometry" — the audit resolves geometry by the ProjectID cell. One cell, mechanical
  and pre-verified; needs Baird's authorization (a live-sheet write). Out of MZ's province
  queue — found incidentally during the Egypt 2026-08-27 pass.
- **Guangxi pilot — DELIVERED 2026-07-29, staged not applied.** Full deep sweep +
  status-review over all 43 grid rows
  (`…_20260904_1355_ET_china-guangxi-gas_deepsweep.xlsx`, 9 tabs; rebuilt 09-04 so
  the 13 change/stale status verdicts + 33 tracker fills overlay `Gas_Backend`
  tier-colored with their corroborating refs). Headline: 219/295
  existing ref links dead (116 = geo-blocked `fgw.gxzf.gov.cn` alone); ref-gap
  fan-out recovered 235/364 gap units with verified (mostly zh) sources, 129
  UNRESOLVED; 75 refs re-verified live. Status review: 23 confirm / 10 stale /
  3 change / 7 unclear. Validity: 43 concerns incl. 6 existence, 2 duplicate,
  10 attribution. 89 fills. Baird reviews the workbook; nothing applied.
- **Jiangxi v3 — DELIVERED 2026-09-10, staged not applied; SUPERSEDES v2 (which superseded
  v1).** ONE file to work:
  `…_20260910_1154_ET_china-jiangxi-gas_deepsweep.xlsx` (10 tabs); staging
  `batches/china-jiangxi-gas/staging/deepsweep-20260903/`; delivery note
  `notes/delivery-2026-09-10-china-jiangxi-gas-deepsweep-v3.md`. **ONE pending state** —
  v2's workbook and staging dir are archived (`archive/deepsweep-v2-20260902/`), as v1's
  were when v2 landed. Same 44 rows (all 41
  Jiangxi-terminus + the three transiting mainlines P4657/P4934/P4947), legs
  `refs` / `fills` / `validity` / `status-review`; no recon, no routes, no discovery.
  v3 exists to answer MZ's four v2 points and each is now measured by a gate: **248 owed
  blanks all reported on** (94 filled with a corroborated value, 154 honest `UNRESOLVED`,
  gate J = 0) against v2's 4 fills; document-exhaustion enforced per shard by
  `check_shard_coverage.py`; **relevance down to 5 units whose refs don't name the row's
  pipeline** plus 1 unchecked (P4788 `Pressure [ref]`), via `name_found` +
  `merge_qc.relevance_qc`; and **gate K counts the 72 single-ref `REFS_ADDED`** out of 194.
  Store **772 records / 44 rows** = 411 ref units + 248 fills + 99 validity + 14 status
  reviews. Ref lane **194 `REFS_ADDED` / 106 `REVERIFIED` / 109 `UNRESOLVED` / 2
  `DEAD_LINK`** — the `REFS_ADDED` fall from v2's 270 is the carry-forward working (a
  `REVERIFIED` is a v2 `REFS_ADDED` whose URLs still resolve and still state the value), so
  **300 of 411 ref units are sourced** vs v2's 282. Tiers 125 high / 154 medium / 21 low,
  **79 distinct verified hosts** (was 49). Status: 2 change (P5865 → `operating` +
  `StartYear1` 2021, P5886 `proposed` → `construction`), 2 confirm, 6 stale, 4 unclear.
  Gates B/D/E/F/J/L clean; A=2, C=60, G=41, H=39, I=5, I'=1, K=72. **Gate C is
  concentration, not a defect** — eleven documents carry 404 units, listed in the delivery
  note; the 19 wikipedia-cited units (P4657, P4793–P4797, P4934, P4947) are the ones to
  challenge first. `Gas_Validity` carries a **specific `Recommendation` on 7 of 99 rows**
  (P4778, P4931, P4944 ×2, P5861, P5862, P5866) — the other 92 keep the boilerplate on
  purpose, because an orchestrator recommendation is not a licence to convert an open
  question into an instruction. Four adjudicated rulings: **retire P5861 into P4778**
  (the batch's one genuine duplicate, settled by a negative in PipeChina's exhaustive 2026
  公平开放 inventory; the 2024-12-31 WEP2 tie-in may not rescue its `FuelSource`);
  **P5866's 金沙湾 → 金砂湾**; **P5862's batch-wide phase sentinel** (ruling A applied, 20
  rows normalized; B–E still owed); and **P4944's start location, 2 cells**. Deliberately
  NOT staged, each carrying a "CANDIDATE VALUE CHANGE / decision owed at merge" concern:
  P4928 `Capacity` 30 → 15 bcm/y and `LengthKnown` 817 → 832.40 km, P5865 0.13 vs 0.005
  bcm/y, P5866 0.50 vs 0.492 and 19.12 vs 19.13, P5889 31.32 vs ~34 km — several published
  figures are all true of something, so the convention is the decision, not the number.
  **The province's defining fact is still a 3.7% citation base** (v1 measured
  `MISSING_REF` 156 / `HAS_REF` 6) — calibrate this like India, not Pakistan: a blank here
  means nobody looked, so an `UNRESOLVED` is an unfinished result, not a correct one.
- **P4778 ↔ P5861 is ADJUDICATED (v3, 2026-09-10): retire P5861 into P4778.** It arrived
  reciprocally — two agents at opposite ends of the fan-out each filed a `__REDUNDANCY__`
  naming the other's row, "Phase I, Gao'an–Xinyu" vs "West-East Gas Pipeline 2, XinYu
  Branch (Gao'an–Xinyu)", identical corridor and StartYear. Reciprocity is **corroboration,
  not two findings**: deliver it as ONE cluster or the same question gets adjudicated twice
  (`validate_shards.py` now detects reciprocal filings, including when the counterpart is
  named only in prose). What settled it is a **negative in PipeChina's exhaustive 2026
  公平开放 inventory** — an enumeration that omits the leg, which is evidence, not silence.
  The 2024-12-31 WEP2 tie-in is explicitly barred from rescuing P5861's `FuelSource`. The
  ruling is in `Gas_Validity`'s `Recommendation` on both rows; it is still a
  recommendation, not applied.
- **Phase I vs Phase II is an operator question across the whole grid, not a row defect.**
  The CCXI credit-rating PDF splits the operator by phase; cross-tabbing all 44 rows gives
  23 phase-labelled (15 Phase I / 8 Phase II), 12 blank `FuelSource`, 5 filled, **3 in
  tension**. It surfaced on ONE row buried inside a `FuelSource [ref]` record's notes on an
  `UNRESOLVED` unit — the Egypt P5121 burial pattern again — and was promoted to a
  cohort-level sentinel on P5862. Not auto-corrected. **Ruling A applied in v3** (20 rows
  normalized to the mapping below); rulings B–E still owed.
- **The authoritative Jiangxi phase mapping** — CCXI 2022 fn1 + SSE disclosure 242696 fn5,
  and the only version to write into a record:
  - **PHASE I** = 一期管网, fed by 川气东送, project company **江西省天然气管道有限公司**,
    owned **54% 江西省天然气集团有限公司 / 46% 国家管网集团东部原油储运有限公司**. That 46%
    holder is the **SUBSIDIARY** — never the parent 国家石油天然气管网集团有限公司.
  - **PHASE II** = 二期管网, fed by **WEP2/WEP3**, operated by
    **江西省天然气集团有限公司管道分公司** — a **100%-group BRANCH, not a JV**, formed early
    2016 to build ~1,500 km across 40 counties for 62.49亿元. So a Phase II row resolves to
    **100% Group**, and `normalize_owner_entities.py`'s 54/46 gate must let it pass untouched.
  - **The phase test** is the county list, not the label: CCXI fn2's 42 Phase I counties
    (南昌、九江、景德镇、新余、宜春、抚州、鹰潭、上饶) vs fn3's 40 Phase II counties
    (井冈山市、莲花县、永新县、大余县). **Phase comes from the sources' wording, never from
    the sheet label and never from the `一期/二期` string in `segment_name`.**
  - **Phase II's entity name is unstable in primary sources** — the same 管道分公司 appears
    under four different parents across four tenders (two of them in ONE 2020-04 document),
    so a name-match on the tender string alone mis-keys rows. Match on the phase, then the
    entity.
  - **P5863's phase is genuinely open:** geography reads Phase I, chronology reads Phase II
    (it is a 2023 project, and 管道分公司 was formed in 2016 expressly to build the Phase II
    remainder). Don't resolve it from geography alone.
- **Two aggregate-vs-segment defects, and one adjudicated non-defect.** P4788's
  `SegmentCost` 2,172,600,000 CNY is the total for all four Ganzhou South branches; P4928's
  `Capacity` 30.00 bcm/y is the WEP3 *system* total, not the Ji'an–Fuzhou East Section.
  **P4934's 125 bn RMB is correct** — that row IS the whole-system row, so a system-level
  total is the right match. Read the row's granularity before calling a system figure a
  defect.
- **P5865/P5866 — an archive.org 429 is a RATE limit, so the answer is patience in the same
  session, not another day or another IP.** Two `jxgajc.com` completion-acceptance filings
  settle both rows; the **host no longer resolves in DNS**, so Wayback is the only route, and
  archive.org 429'd every path for hours (the `id_` fetches *and* the CDX API). The reading
  that "the limit is IP-level and both rows stay open" was **WRONG**: the 429 / `http=000` is
  per-request and transient, and a plain bounded retry loop (6 tries, ~6–8 s apart) got a 200
  on both captures — `20230902005946` (P5865) and `20230902105154` (P5866) — within a minute.
  What is NOT a route, so nobody re-tries it: `web.archive.org` has no AAAA record (IPv6
  egress), the Memento aggregator `timetravel.mementoweb.org` returns 403 Request Denied, and
  IA login cookies from `~/.config/internetarchive/ia.ini` make no difference (the first 200
  came with an empty `Cookie` header). Staged as `batch_20_wayback_recovered.json`, 26 records
  / 21 ref units. What the documents settled: **P5865's status is stale and its own new ref
  proves it** (竣工 Nov 2021 → `construction` → `operating`, `StartYear1` 2021, `medium`
  because 竣工 is completion, not gas-in); **P5865 `StartPrefecture/District` = `Fengcheng`,
  not `Yifeng`** (「项目位于樟树市、丰城市境内」 plus 12.7 of 20.2 km allotted to 丰城市;
  Tuochuan is a town of Fengcheng, Yifeng a different county under the same Yichun
  prefecture); **P5865's capacity stays `UNRESOLVED`** (the filing prints 5×10⁶ Nm³/a =
  0.005 bcm/y against the sheet's 0.13, and that figure is itself implausible against sister
  segment P5866, so it settles nothing — the agent that recalled ~5×10⁶ Nm³/a from memory was
  right to refuse to stage it, and it is still not staged); **P5866 corroborated on eight
  values exactly** (19.12 km, DN500, 2017-12, 2021, 0.50 bcm/y, 80,830,000 RMB, `FuelSource`
  verbatim, `operating` at 14.6% of design) with `StartPrefecture/District` filled blank →
  `Jiujiang`; and **P5866's 6.43× capacity outlier is REFUTED and re-filed as a ROUTE defect**
  — the geometry is over-drawn against a documented 19.12 km branch, so it joins P5862 as a §8
  redraw. **No direction swap on P5866, deliberately:** the filing names Jinshawan → Hukou,
  the reverse of the sheet, but that is chainage order — gas enters the branch from the
  national trunks at the Hukou distribution station, so the sheet reads as flow direction.
- **Watch for `fzggw.jiangsu.gov.cn` in a Jiangxi harvest — Jiangsu is not Jiangxi.** The
  wiki harvest surfaces it repeatedly and it is always a false lead.
- **A whole class of Jiangxi's `UNRESOLVED` fills is uncitable, not unknown.** The 8
  unresolved **`Length`** fills all sit on rows that already carry route geometry (P4776
  62.34 km/2 vtx, P4778 56.88/11, P4780 136.02/20, P4781 19.37/6, P4782 100.96/38, P5859
  50.62/2). GEM's own geometry can't be cited under standing rule 1, so the cells correctly
  stay unfilled on our side — but MZ owns those routes and can fill them from her own lane.
  Carry the table, don't report bare UNRESOLVEDs. (v3's 154 unresolved fills span nine
  columns; this reasoning applies to the Length ones, not to all of them.)
- **Jiangxi route-vs-sheet length: 7 divergences, one of them not a defect.** P5862 30.10x,
  P5866 6.43x, P5887 2.12x, P4784 1.87x, P4783 0.57x, P4788 0.09x, P4777 0.07x. **P4777 is
  expected** — it is the Phase I network-granularity parent row (825 km system vs a 14-vertex
  corridor trace), so it is not a finding. Routes are MZ's lane; nothing redrawn here.
- **P4788 is the row to read first.** Three findings, all filed as questions not edits:
  `FuelSource` reads `Sichuan-Shanghai gas pipeline/West-East gas pipeline II` but the
  operator's own emergency plan names the feed points as WEP2 valve chamber #149 or the
  **WEP3** Ruijin station, with 川气东送 appearing 0 times in 494,223 chars (WEP2 corroborated,
  WEP3 missing, Sichuan-Shanghai unsupported — though absence in one document is not absence
  in fact); the redraw coordinates in its `__VALIDITY__` were **DMS read as decimal**, putting
  the Xinfeng anchor 38.7 km off (correct: Xinfeng 114.82255/25.43558, Ruijin
  116.00923/25.94623); and while 340.3 km IS attributed to this section by the document (the
  aggregate hypothesis stays refuted), the terminal stations are only 131.8 km apart
  great-circle, so 2.58x sinuosity leaves **both** the 340.30 length and the 31.78 km route
  open. A redraw should measure ~140–190 km.
- **Chinese engineering PDFs quote coordinates in DMS.** Transcribing the degree-minute digits
  as decimal degrees costs tens of kilometres (38.7 km on P4788's start anchor). Convert, and
  say which form you are writing.
- **Jiangxi's citable DRC plan is a third-party rehost.** 江西省天然气利用规划 2013–2020
  (赣发改规划 2014 325号) is served from `img9.qianzhan.com/policy/202307/14/…pdf` because the
  government copy at `nc.gov.cn` is NXDOMAIN. It is a rehosted **primary**, not a tertiary
  aggregator's own content, so it is citable — but it is a 2014 *planning* document, thin
  support for 2026 operating status unless paired (it backs 39 proposed refs, and `huaon.com`
  is the second source on the units that reach `high`).
- **`docs/reference/source_roster.md` now HAS a China (zh) section** — seeded 2026-09-10
  from the Guangxi pilot plus Jiangxi v3's 80 live-verified hosts, with the decoding and
  IPv6 gotchas alongside. Add to it rather than re-deriving the roster per province.
- **`www.quannan.gov.cn` returns 403 over IPv6 and 200 over IPv4 — that is not a deletion.**
  42 v3 units cite one Quannan county PDF, and it reads fine with `curl --ipv4` +
  `pdftotext -layout`. `url_verifier.py` has **no IPv4 retry on a 403**, so it reports the
  host as blocked; never drop a ref on that signal (standing rule: only a confirmed 404/410
  may drop one). Same family of defect: `chinanews.com.cn` decodes as a false negative
  because strict `gb18030` *and* `utf-8` both reject its mixed bytes, while
  `errors='replace'` reads cleanly.
- **Canonical `FuelSource` forms for the WEP/Sichuan–Shanghai family** — write these
  exactly, and don't invent variants: `Sichuan–Shanghai Gas Pipeline` and
  `Sichuan–Shanghai Parallel Gas Pipeline` (**EN DASH**), `West-East Gas Pipeline 1` / `2` /
  `3` (arabic numerals, ASCII hyphen), joined with `, `, **no CJK gloss** in the cell.
- **One wrong character in a name costs twelve ref reads.** P5866's `segment_name` carried
  金沙湾 for the real 金砂湾, and because every name-match on the wrong character missed, the
  row's refs came back as twelve "system-only" reads that looked like a sourcing problem and
  were actually an orthography problem. Check the CJK name against a primary document before
  concluding a row is unsourceable.
- **`worklist.json`'s name fields are English-only, and on a CJK batch that silently breaks
  matching.** It is the mechanism behind P4790's false "no PID identified" — the Chinese name
  never reached the matcher, so a correctly-identified row read as unidentifiable. Owed
  before the next CJK batch; until it lands, cross-check a "no PID" verdict by hand against
  `OtherLanguagePrimaryPipelineName`.
- **`url_verifier.py` vs Chinese domains — smoke-tested 2026-07-29:** NDRC, 北极星,
  PipeChina, CNPC, Sinopec, Guangdong DRC, Zhejiang DRC all pass. **`fgw.gxzf.gov.cn`
  (Guangxi DRC) ConnectTimeouts on both schemes — likely overseas geo-blocking**, so
  expect Guangxi-portal references to be unverifiable from here. Since every xlsx URL
  must pass the verifier, cite a `web.archive.org` snapshot of the page instead (the
  archive URL verifies) and note the original in `ResearcherNotes` — never drop the
  source, never ship the unverifiable URL.
- **P8062 null route — staged 2026-08-10, not applied.** Baird's instruction while
  routing Egypt: "for MZ's P8062, just add a null route for that." Staged at
  `batches/china-gas/staging/route-creation-null-20260810/candidate_routes/P8062.geojson`
  as a single `geometry: null` feature — the routes repo's own
  `data/example-empty-route.geojson` convention, already in production for
  `liquid-pipelines/P7326.geojson`. **No sheet write accompanies it**: under the
  three-way-sync rule a null placeholder is not mapped geometry, so `RouteType` stays
  `Not mapped (but could be — route or endpoints are known)`, `RouteAccuracy` stays
  `no route`, and `RouteCreator` stays `MZ` (we created nothing). Destination on
  authorization is one file, `data/individual-routes/gas-pipelines/P8062.geojson`.
- Oil (363 rows, stale) — unassigned, post-cycle decision.
