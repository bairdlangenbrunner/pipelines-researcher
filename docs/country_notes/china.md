# China

**Gas only this cycle** (decision 2026-07-29). Biggest single scope in GGIT: 984 gas
rows at the 2026-07-29 snapshot (23% of the tracker — 612 operating, 294 in-dev,
74 cancelled/shelved/retired; 971 domestic-only). GOIT has 363 China oil rows, staler
(140 pre-2024 `LastUpdated`), but oil is **out of scope until after the GGIT 2026
cycle**. Work happens **at the province level**, not whole-country.

## Division of labor (locked 2026-07-29)

- **Maggie Zheng (MZ)** owns China (+ HK, Taiwan, Macau, Mongolia, North Korea) for
  the GGIT 2026 cycle — active Jul 16–Sep 11, province by province, triage pace
  (she's solo). Her core work: **routes + wiki sync, operating rows first**. Cycle
  planning, her 529-row route-target list, and the "chinese researcher assignments –
  2026" sheet tab (keyed on `PipelineName`; 996 China-scope rows → 94 unique names)
  live in the **gem-desk repo**, `research-cycles/ggit-2026-pipelines-update/`.
- **Agent batches run AHEAD of her province queue**, pre-staging what triage pace
  can't cover: ref sweeps, value backfill, status re-verification, document-driven
  discovery. Routes and wiki edits stay hers. Never re-audit a province she has
  finished without being asked.
- **National trunk systems are Maggie's own scope**, excluded from agent province
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
  `no route` — over half. That's Maggie's lane, not the agent's.

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
  WEP2 branches, 新粤浙, 渝黔桂, 川滇黔桂) drop out to Maggie's trunk scope. Drop
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

- **Maggie edits the live sheet continuously** through Sep 11 — pull a fresh CSV at
  every batch start (standing rule, but load-bearing here) and expect `LastUpdated`
  drift between staging and apply.
- Province priority she sketched (gem-desk, 2026-07-23): Guangdong (current) →
  Guangxi → Jiangsu → Fujian; **Shandong/Hebei deliberately deferred** — Hebei has
  real double-counting risk against national trunk lines. Shanghai done.
- Known backend name-variant near-dupes ("Hebei Gas Pipeline Network" vs
  "…pipeline…", en-dash vs hyphen in "Hebei–Nanjing"); hydrogen rows live on a
  separate backend tab and are excluded from the China gas scope.

## Province ledger (agent-side; batches only, Maggie's progress lives in gem-desk)

| province | scope (grid rows) | status | batch |
|---|---|---|---|
| Guangxi | 43 (+9 trunk excluded) | pilot DELIVERED 2026-07-29, staged not applied | `pipelines_batch_20260729_1929_ET_china-guangxi-gas_deepsweep.xlsx`; staging `batches/china-guangxi-gas/staging/deepsweep-pilot/` |

## Open items

- **Guangxi pilot — DELIVERED 2026-07-29, staged not applied.** Full deep sweep +
  status-review over all 43 grid rows
  (`…_20260729_1929_ET_china-guangxi-gas_deepsweep.xlsx`, 9 tabs). Headline: 219/295
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
- Oil (363 rows, stale) — unassigned, post-cycle decision.
