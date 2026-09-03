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
| Guangxi | 43 (+9 trunk excluded) | pilot DELIVERED 2026-07-29, staged not applied | `pipelines_batch_20260730_1637_ET_china-guangxi-gas_deepsweep.xlsx` (repackaged 07-30: recommended edits now overlay `Gas_Backend`; 07-29 build archived); staging `batches/china-guangxi-gas/staging/deepsweep-pilot/` |
| Jiangxi | **44** — all 41 Jiangxi-terminus rows + the 3 transiting national mainlines (P4657/P4934/P4947) | **v2 DELIVERED 2026-09-02, staged not applied** (supersedes v1); **v3 PLANNED** off MZ's 2026-09-03 feedback — `notes/plan-2026-09-03-china-jiangxi-gas-deepsweep-v3.md` | `pipelines_batch_20260902_1232_ET_china-jiangxi-gas_deepsweep.xlsx` (11 tabs); staging `batches/china-jiangxi-gas/staging/deepsweep-20260902/`; v1 archived at `archive/deepsweep-v1-20260826/` |

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

- **Guangxi pilot — DELIVERED 2026-07-29, staged not applied.** Full deep sweep +
  status-review over all 43 grid rows
  (`…_20260730_1637_ET_china-guangxi-gas_deepsweep.xlsx`, 9 tabs; rebuilt 07-30 so
  the 13 change/stale status verdicts + 33 tracker fills overlay `Gas_Backend`
  tier-colored with their corroborating refs). Headline: 219/295
  existing ref links dead (116 = geo-blocked `fgw.gxzf.gov.cn` alone); ref-gap
  fan-out recovered 235/364 gap units with verified (mostly zh) sources, 129
  UNRESOLVED; 75 refs re-verified live. Status review: 23 confirm / 10 stale /
  3 change / 7 unclear. Validity: 43 concerns incl. 6 existence, 2 duplicate,
  10 attribution. 89 fills. Baird reviews the workbook; nothing applied.
- **Jiangxi v3 — PLANNED 2026-09-03, not run.** MZ reviewed v2 ("looks really good") with
  four points: blanks on operating rows unfilled (241 owed `MISSING_VALUE` units on the 44 rows,
  171 on `operating`; v2 staged 4 fills); facts in found sources not carried to the other
  columns (P4777's 825 km / 3.1 bn RMB / Oct 2008 are in the Sina article staged on P4776);
  refs that don't name the pipeline (keyword hits on "A" or "B" for an "A–B" row); and one
  ref per data point (168 of 270 `REFS_ADDED` are single-source; 7 documents carry 166
  units). Mechanisms now in the engine (`--owe-fills`, `name_found` + `relevance_qc`,
  document-exhaustion + two-source rules in the SOP/contract, `sweep_gates.py` I/J/K); the
  plan, the re-research list and the carry-forward rule:
  `notes/plan-2026-09-03-china-jiangxi-gas-deepsweep-v3.md`. v3 carries v2 forward (re-key,
  re-verify, don't re-discover) and SUPERSEDES it when delivered — one pending state.
- **Jiangxi grid v2 — DELIVERED 2026-09-02, staged not applied; SUPERSEDES v1.** Baird
  reset the scope ("it wasn't very comprehensive… include any trunk lines"): **44 rows** =
  all 41 Jiangxi-terminus rows **plus** the three transiting national mainlines P4657,
  P4934, P4947 that v1 excluded. Legs `refs` / `fills` / `validity` / **`status-review`**
  (new); no OSM recon, no routes leg, no discovery. The 18 rows v1 swept were **carried
  forward, not re-discovered** — every prior `REFS_ADDED` re-keyed onto the fresh worklist
  (the gas tab re-sorted; all 18 moved -2 rows), its URLs re-verified, only the
  `UNRESOLVED` re-researched. ONE file to work:
  `…_20260902_1232_ET_china-jiangxi-gas_deepsweep.xlsx` (11 tabs); v1's workbook and
  staging dir archived to `batches/china-jiangxi-gas/archive/deepsweep-v1-20260826/`, so
  there is exactly one pending state. Store 453 = 411 ref units + 26 validity + 12 status
  reviews + 4 fills. Ref-lane outcome **270 `REFS_ADDED` / 127 `UNRESOLVED` / 12 `REVERIFIED`
  / 2 `DEAD_LINK`**, tiers 82 high / 175 medium / 14 low, **49 distinct verified hosts**;
  status verdicts 6 stale / 4 unclear / 1 change / 1 confirm (16 records staged, 12 kept —
  a row has ONE status, so `split_shards` keeps the last shard's verdict). Gates B/D/E/F clean, A=1 (P5888 on
  `sohu.com` alone); **gate C's 33 flags are concentration, not a defect** — each is a `high`
  whose second origin is one of six documents that carry 145 units between them (the qianzhan
  DRC-plan rehost 50, `mee.gov.cn` 36, `quannan.gov.cn` 24, `static.sse.com.cn` 22, the
  en.wikipedia WEP article 18, `trqi.sinopec.com` / `huaon.com` 16 each), so read them when
  deciding whether "two sources" is really two. Delivery note:
  `notes/delivery-2026-09-02-china-jiangxi-gas-deepsweep-v2.md`.
  **The province's defining fact is still a 3.7% citation base** (v1 measured
  `MISSING_REF` 156 / `HAS_REF` 6) — calibrate this like India, not Pakistan: a blank here
  means nobody looked, so an `UNRESOLVED` is an unfinished result, not a correct one. v1's
  98 `REFS_ADDED` over 18 rows became 270 over 44.
- **The Jiangxi cluster to adjudicate is P4778 ↔ P5861, and it arrived reciprocally.** Two
  agents at opposite ends of the fan-out each filed a `__REDUNDANCY__` naming the other's
  row — "Phase I, Gao'an–Xinyu" vs "West-East Gas Pipeline 2, XinYu Branch (Gao'an–Xinyu)",
  identical corridor and StartYear. Reciprocity is **corroboration, not two findings**:
  deliver it as ONE cluster or the same question gets adjudicated twice. `validate_shards.py`
  now detects reciprocal filings, including when the counterpart is named only in prose.
- **Phase I vs Phase II is an operator question across the whole grid, not a row defect.**
  The CCXI credit-rating PDF splits the operator by phase; cross-tabbing all 44 rows gives
  23 phase-labelled (15 Phase I / 8 Phase II), 12 blank `FuelSource`, 5 filled, **3 in
  tension**. It surfaced on ONE row buried inside a `FuelSource [ref]` record's notes on an
  `UNRESOLVED` unit — the Egypt P5121 burial pattern again — and was promoted to a
  cohort-level sentinel on P5862. Not auto-corrected.
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
- **Jiangxi's `UNRESOLVED` fills are uncitable, not unknown.** All 8 unresolved fills sit on
  rows that already carry route geometry (P4776 62.34 km/2 vtx, P4778 56.88/11, P4780
  136.02/20, P4781 19.37/6, P4782 100.96/38, P5859 50.62/2). GEM's own geometry can't be
  cited under standing rule 1, so the cells correctly stay unfilled on our side — but MZ owns
  those routes and can fill them from her own lane. Carry the table, don't report bare
  UNRESOLVEDs.
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
- `docs/reference/source_roster.md` has no China section yet — seed it from the
  pilot's verified sources (live: news.bjx.com.cn, gx.chinanews.com.cn,
  gx.xinhuanet.com, ndrc.gov.cn, pipechina.com.cn, cnpc.com.cn, sinopec.com,
  sasac.gov.cn, wsbs.liuzhou.gov.cn; archive.org snapshots for fgw.gxzf.gov.cn).
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
