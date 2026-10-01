# Triage 2026-09-30 — Russia gas: discovery pass (§4) plan + rulings

Follows the regional deep-sweep pass (R1–R7, all delivered, staged not applied —
`notes/triage-2026-09-14-russia-gas-campaign.md`). The campaign-wide fills pass over the lean
`deferred_units.json` ledgers is deferred until after discovery (Baird 2026-09-30).

## Starting position
- Roster: 285 GGIT rows touching Russia (09-30 snapshot). **Every slice matches against the full
  285**, carried rows and `Status = N/A` included — only the search briefs are sliced.
- GulfPub recon (09-14): 2 `DISCOVERY_CANDIDATE` (nearest P3982 and P6684, both Siberian), 1
  `FRAGMENT_OF_EXISTING` (P0756), 190 `NEAR_MISS` still unadjudicated.
- OSM `gas_ru` extract registered (5,520 features / 1,816 named, 62% sub-1 km stubs) but never
  reconciled — the systematic source for operating lines GEM never captured.
- Tooling: `country-discovery` is country-only; slice by passing district-scoped
  `args.strategies` briefs with the full roster. Its search contract says "skip distribution
  networks" — the briefs must carry the length rule below instead.
- GGIT has no row touching Crimea/Sevastopol (Krasnodar–Crimea has operated since 2016).

## Rulings (Baird 2026-09-30)
1. **Inclusion: length threshold 25 km.** A candidate ≥ 25 km that passes the add-threshold
   (sponsor + endpoints + concrete step) is a new row. Anything under 25 km, **or anything of
   uncertain length**, goes on the `monitor` list.
2. **Territory naming follows GEM's naming-conventions sheet**
   (`docs/reference/gem_naming_conventions/`): occupied Ukraine (Crimea, Sevastopol, Donbas) is
   Ukraine, so a line into it is Russia–Ukraine cross-border with a `UKR` terminus subdivision;
   Abkhazia is Georgia.
3. **Escalation gate (>5 candidate clusters) applies per slice, soft:** report each slice's
   clusters in its summary; stop and ask only if one slice produces an outsized number (> ~15).
4. **Time window:** new announcements from the last ~3 years **plus** operating/built lines GEM
   never captured.

## Sequence
**Step 0 (mechanical, no agents):** fresh pull; §2 OSM recon for Russia, standalone (the >30
Additions gate will fire — expected; triage by `disposition`, filter to named features ≥ 25 km
after merging stubs by name, join to district via the state audit's spatial join); grep the R1–R7
validity stores for discovery-shaped leads. Output: a seed list per district.

**Steps 1–6: one `country-discovery` run per slice** in
`batches/russia-gas/staging/discovery-dN-<slug>/`, one workbook each, one slice per session:

| # | slice | leads |
|---|---|---|
| D1 (pilot) | Far Eastern | PoS-1 branches, Far Eastern route, Sakhalin–Khabarovsk–Vladivostok expansion, Amur GPP / Vladivostok LNG feeds, Yakutia |
| D2 | Siberian | Kovykta–Irkutsk extensions, Krasnoyarsk, Kuzbass, Altai; both GulfPub candidates |
| D3 | Urals (YaNAO/KhMAO + south) | Arctic LNG 2 / Ob LNG feeds, Kharasavey, Tambey, Gydan |
| D4 | Northwestern | Ust-Luga complex feed, Volkhov–Murmansk, Kaliningrad, Karelia, Arkhangelsk |
| D5 | Volga + Central | loops and gasification trunks ≥ 25 km |
| D6 | South + North Caucasus + cross-border | TurkStream feeders, Krasnodar–Crimea (as RU–UA), Abkhazia/South Ossetia (as RU–GE), KZ/AM/BY transit |

Per slice: 5 search agents (Sonnet) → consolidator (top tier — Cyrillic/translit/translated
name matching against 285 rows; the workflow's single `MODEL` needs a per-phase option) → one
vetting agent per candidate → `merge_discovery_shards.py` → `build_discovery_workbook.py` →
`recalc.py`. ~6 + 10–25 agents per slice; no measured discovery token cost on file — D1 sets it.

## Step 0 results (2026-09-30)
- **Pull:** fresh snapshots `*_20260930.csv` (Oil/NGL, Gas, operators/owners).
- **OSM recon** (`gas_ru`, standalone, 285-row roster): 5,520 features → 135 overlaps, 5,385 additions
  (3,078 DISCOVERY_CANDIDATE / 2,249 FRAGMENT / 58 NEAR_MISS), 224 GEM-only, 8 status conflicts. Workbook
  `deliverables/pipelines_batch_20260930_1504_ET_russia-gas_reconciliation-osm.xlsx`. Health:
  `MATCH_CONCENTRATION` — routeless P3894 (Main Line Capacity Upgrade, SKhV) is nearest row for 1,822 records
  on diameter/length alone; it has 0 overlaps and dispositions are geometry-based, so counts stand, but "nearest
  PID" is arithmetic. 32.9% named, 100% with geometry. The >30-additions gate fired as expected.
- **Seeds:** `staging/discovery-seeds-20260930/` — 88 seeds + 3 length-unknown store leads; D1 1+1, D2 3, D3 33+1,
  D4 17+1, D5 32, D6 2; 148 to monitor, 53 already tracked. Method and caveats in its `SUMMARY.md`.
- **Corrections to the plan above:** the two GulfPub candidates are *not* D2 Siberian (Tuchevo–Tver → D5,
  Valday–Borovichi → D4); D1 has almost no OSM signal; 2,214 unnamed OSM candidates (74 ≥ 25 km) are outside the
  named-only seed rule.

## Slice results (2026-09-30)
- **D1–D4** merged → `deliverables/pipelines_batch_20260930_2116_ET_russia-gas_discovery-d1-d4.xlsx`: 16 new / 8 monitor /
  6 matched existing.
- **D5 + D6** merged (`staging/discovery-d5-d6-merged-20260930/`) →
  `deliverables/pipelines_batch_20260930_2155_ET_russia-gas_discovery-d5-d6.xlsx`: 25 new (D5 15, D6 10) / 15 monitor /
  6 matched existing. D6 queued 20 (> the ~15 soft gate), only 10 cleared the add-threshold, so not escalated. Owner
  strings normalized to the tracker convention (`Gazprom PJSC [100.%]` / `[100.00%]`) on the merged shard copies; regional
  subsidiaries left as researched. Review flags: country notes → Discovery D5–D6.
- **Seed-coverage gap (engine defect, our own):** the workflow's search contract never requires a disposition per seed,
  so the maps agent reports the seeds it finds citable and silently skips the rest. A rough name-token check finds no
  trace of 3/3 D2, ~16/18 D4 and ~26/32 D5 seeds in any output (translit makes this an over-count, but Tuchevo–Tver (D5)
  and Valday–Borovichi (D4) are Latin-named and absent). D1, D3, D6 look covered. Fix: a per-seed ledger (every seed →
  matched PID / monitor-short / queued / dropped-with-reason, enforced at consolidate), then a seeds-only re-run of D2, D4, D5.
- **Seed re-run (2026-10-01):** the ledger fix landed in the `country-discovery` workflow (`args.seeds` → dedicated seed
  agents, `seed_ledger` in queue.json, consolidate-step coverage gate + one repair agent, `seeds_unadjudicated` in the
  result; `seedsOnly` + `priorStaging` for coverage re-runs) and in `merge_discovery_shards.py` / the `<Cmdty>_SeedLedger`
  tab. One combined seeds-only run over D2+D4+D5 (53 seeds incl. both GulfPub leads; prior = the five D-run dirs) →
  53/53 dispositioned, repair agent not needed → `deliverables/pipelines_batch_20261001_1237_ET_russia-gas_discovery-seeds-d2-d4-d5.xlsx`:
  5 new / 34 monitor / 6 matched. The gap was real but thin: most skipped seeds are GRS spurs with no sourced length
  (monitor). Review flags: country notes → Discovery seed re-run.
