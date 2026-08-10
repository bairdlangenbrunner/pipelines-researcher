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
- **Recon sources are weak here:** GulfPub has only ~108 China gas features
  (trunks only — useless against the provincial grids; useful if the trunk scope
  ever runs). OSM would need per-province Overpass pulls, coverage unverified.
  Discovery signal comes from **document sweeps, not scraped geodata**.

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
under authorization: 79 single-cell writes to `Mapped route (at any accuracy)`,
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
