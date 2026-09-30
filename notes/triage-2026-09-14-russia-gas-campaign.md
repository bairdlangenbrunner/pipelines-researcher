# Triage 2026-09-14 — Russia gas: campaign plan (deep sweep + discovery)

Scope requested: a GGIT research pass on Russia run the way the US gas pass is being run —
sliced deep sweeps with status review on, rule-4(e) completeness, then a discovery pass.
This memo scopes it against the 2026-09-14 snapshot and proposes the batch plan. Nothing is
staged for research yet; the only outputs are the scoping artifacts under
`batches/russia-gas/staging/scoping-20260914/` and `batches/russia-gas/carried_from_others.txt`.

## 1. What is there

| | |
|---|---|
| GGIT rows with Russia in `CountriesOrAreas` | **285** (227 Russia-only, 58 multi-country) |
| Status | operating 182 · proposed 62 · construction 16 · cancelled 12 · mothballed 5 · retired 4 · shelved 3 · idle 1 |
| `LastUpdated` year | 2023: 142 · 2025: 93 · 2024: 38 · 2022: 8 · 2026: 4 (no blanks) |
| Researcher | NF 225 · ZK 27 · AV 16 · HF 6 · others 11 |
| Ref units (`build_ref_worklist --owe-fills`) | **4,293** = HAS_REF 978 / MISSING_REF 1,697 / MISSING_VALUE 1,618 (570 operator/owner) |
| Citation base (HAS_REF over ref-bearing units) | **36.6%** — between Ukraine (3%) and US slice 2 (63%) |
| Owed fills by column | Pressure 284 · SegmentCost 243 · Proposal 215 · Construction 214 · Operator 209 · FuelSource 155 · Capacity 95 · Start 75 · Diameter 65 · Length 48 · Owner 15 |
| Routes repo | 284 of 285 have a geojson (only P8087 Ishim–Astana missing); `RouteAccuracy` very low 52 · low 9 · no route 4 · blank 1 = **66 weak rows** |
| `PipelineType` | transmission 224 · **distribution 46** · blank 14 · gathering 1 |
| GulfPub gas extract | **739 Russia features** vs 285 rows (2.6:1 — recon is viable, unlike the US) |
| OSM | no RU extract fetched yet |

Sizing against the US: US slice 2 is 296 rows / 4,520 units in 7 batches of 40–46 rows.
Russia is 285 rows / 4,293 units — the same shape, so the same cut: **7 batches, one pass each,
status review on**.

## 2. Rows another scope already staged (exclude from research legs)

**33 PIDs** carry pending staged research from other countries' passes (Ukraine 20, Kazakhstan 15,
Uzbekistan 7, Iran 1, China 2, overlapping): the Ukraine transit trunks (Urengoy–Pomary–Uzhgorod,
Progress, Soyuz, the Yelets and Novopskov strings, Taganrog–Mariupol–Berdyansk ×3), the Central
Asia–Center / Bukhara–Ural strings, Makat–North Caucasus, Kartaly–Rudny–Kostanai,
Russia–Kazakhstan–China, Russia–Iran P7104, Sakhalin–Khabarovsk–Vladivostok upgrade P3894 and
Jilin P6577. The derived list is `batches/russia-gas/carried_from_others.txt` (with the source run
per PID). Per the Sweep SOP they are excluded from every research leg and kept in recon. They carry
495 units; the residual scope is **252 rows / 3,798 units**.

Caveat worth a ruling: those rows were researched from the other country's side (Ukraine's pass
settled owner attribution on the Russia–Ukraine rows, escalation 2026-08-15). If a Russia-side
re-look is wanted, it is a targeted §5 Update after the other packets are applied, not a second
sweep record on the same cells.

## 3. Slicing — by federal district, derived from geometry, after a state audit

The sheet's `Start/EndState/Province` column cannot be sliced on as-is: the same subject is spelled
several ways (`Yamalo-Nenets Autonomus Okrug` 18 vs `…Autonomous Okrug` 14; `Republic of Komi` vs
`Komi Republic`; `Sakha Republic` vs `Republic of Sakha (Yakutia)`; `Chelyabinsk region` vs
`… Oblast`; `Reublic of Adygea`; bare `Rostov`, `Orenburg`, `Leningrad`) and 26 start / 29 end
cells are blank. Same lesson as the US: **audit the column first, slice on the audit's `derived`
value, never on the sheet**. A provisional spatial join of each route's termini against Natural
Earth admin-1 (which carries the federal district as `region`) resolves 279 of 285 rows:

| Federal district (provisional, non-carried rows) | operating-class | in-dev-class | rows | units |
|---|---|---|---|---|
| Northwestern | 29 | 27 | 56 | 849 |
| Volga | 41 | 9 | 50 | 752 |
| Urals (incl. YaNAO/KhMAO trunk heads) | 40 | 9 | 49 | 737 |
| Siberian | 16 | 17 | 33 | 498 |
| Far Eastern | 17 | 11 | 28 | 423 |
| Central | 15 | 8 | 23 | 345 |
| foreign terminus (TR 3, CN 2, MN, AZ, BY, GE) | 6 | 3 | 9 | 134 |
| unresolved (no/odd geometry) | | | 4 | ~60 |

Russia-specific audit rules the US script does not have: **Tyumen Oblast legally contains KhMAO
and YaNAO** (and Arkhangelsk contains NAO), so `Tyumen region` vs a geometry starting in
Khanty-Mansi is a vocabulary question, not a mismatch; and a start/end swap against the geometry
is direction, not a wrong state. 44 rows show a sheet-vs-geometry start mismatch on the crude
provisional join, most of them these two cases. The audit script for the US
(`state-audit-20260910/audit_slice2.py`) ports directly: swap the NE filter to `RU` and add a
subject-name normaliser; the typos become `Location [ref]` fills on the shards, as in US batch 5.

**Proposed batches (≈ 7, final cut after the audit):**

| # | dir | rows | notes |
|---|---|---|---|
| R1 | `deepsweep-r1-fareast` | ~31 | Far Eastern + CN/MN termini: Power of Siberia 1/2 family, Sakhalin lines, Yakutia's 8-row Srednevilyuyskoye–Yakutsk family, Messoyakha–Norilsk. **Pilot** — mid-size, best English+Russian coverage, exercises the Russian-language contract before the big batches |
| R2 | `deepsweep-r2-nw-operating` | ~29 | Northwestern operating: Gryazovets–Vyborg/Leningrad, Ukhta–Torzhok, Kohtla-Järve, Nord Stream 1 (mothballed) |
| R3 | `deepsweep-r3-nw-indev` | ~27 | Northwestern in-dev: Karelia/Vologda gasification stages (Sheksna–…–Pudozh, Volkhov–Segezha), Nord Stream 2, Murmansk |
| R4 | `deepsweep-r4-urals` | ~49 | YaNAO/KhMAO trunk heads: Bovanenkovo–Ukhta ×6, Nadym–Punga ×5, Urengoy/Yamburg strings, SRTO–Ural. Largest batch — split op/in-dev if the audit lands it above ~45 |
| R5 | `deepsweep-r5-volga` | ~50 | Volga: Nizhnyaya Tura–Perm–Gorky ×5, Minnibaevo–Kazan, Orenburg lines; 46 of 50 last touched 2023 — the stalest cohort |
| R6 | `deepsweep-r6-siberia` | ~33 | Siberian: Novosibirsk–Barnaul ×5 (distribution-typed), Omsk–Novosibirsk–Kuzbass, Kovykta–Sayansk–Irkutsk, Bratsk |
| R7 | `deepsweep-r7-central-south` | ~32 | Central + Southern/Caucasus + TR/AZ/BY/GE termini: TurkStream ×2, Blue Stream, Rostov–Maykop, Krasnodar–Serpukhov, Zaterechny |

Each batch: `--country Russia --exclude-pids @<complement + carried>` (never `--include-pids`,
which unions), `--owe-fills --verify-existing`, `build_deepsweep_args.py --status-review`, a
`BRIEF.md` carrying the batch's segment families, duplicate candidates and status leads, then
`critical-deep-sweep` → `check_shard_coverage --all` → merges → `sweep_gates` (E/F/I/I'/J/L at 0)
→ workbook + `recalc`. Same gate discipline as the US rule-4(e) contract.

## 4. What the validity leg must carry for Russia

- **49 segment families** (name-only grouping) — the I/II/III string convention is the dominant
  row model here (Bovanenkovo–Ukhta 6, Nadym–Punga 5, Novosibirsk–Barnaul 5, Nizhnyaya
  Tura–Perm–Gorky 5, four 4-row families). System-vs-string figures restated on a string row are a
  `spec` concern, not a ref — the FGT lesson from US batch 2, at scale.
- **Duplicate suspects:** TurkStream P0765/P1368 (strings 1 and 2, probably legitimate);
  Sakhalin–Khabarovsk–Vladivostok P0758 vs P2027; Power of Siberia 2 P0734 vs P5409 Soyuz Vostok
  (Mongolian section as a separate row); Kovykta–Sayansk–Irkutsk P2327/P5510 (both proposed, no
  segment name); Vuktyl–Ukhta P7538 "I" created after P5540 "II".
- **46 `distribution`-typed rows** (regional gasification branch lines, e.g. Kurgan, Omsk,
  Astrakhan, Ivanovo) + 14 blank `PipelineType`: a classification question for the leg — are
  these interregional/branch trunks (GGIT scope) or intra-region distribution? Flag, don't
  reclassify.
- **Status nuance post-2022:** Nord Stream 1/2 mothballed (NS1 lines A+B destroyed 2022-09; NS2
  line B intact), Yamal–Europe idle since 2022-05, Ukraine transit stopped 2025-01-01 (carried
  rows, but the Russian-side segments feeding Sudzha/Sokhranivka are in scope), TurkStream now the
  only Europe route, Power of Siberia 1 at 38 bcm/y design in 2025, Power of Siberia 2 memorandum
  2025-09-02 (legally binding per Gazprom, price unsettled). `--status-review` judges each row;
  the brief should name these so agents do not treat a 2019 press release as current.
- **Unit conventions:** Russian trunk diameters are metric (1,420 mm = 56 in; `Diameter = 1420`
  on a Russia row is mm, escalation 2026-07-28 Iraq note); capacities in bcm/y; pressures in MPa
  (7.5 / 9.8 / 11.8 MPa standard classes) — Pressure is owed on 284 rows and is the one column a
  Gazprom subsidiary page routinely states.

## 5. Sources and access (the risk that is different from the US)

There is no FERC/EIA analogue. The source ladder is Russian-language and corporate:

- **Gazprom**: `gazprom.ru` project pages, annual/sustainability reports, IFRS statements,
  investor presentations; the 17 **Gazprom Transgaz** subsidiaries' sites (each lists the trunk
  pipelines, compressor stations, diameters and pressures it operates — the primary source for
  the operating cohort); **Gazprom Mezhregiongaz** + the regional gasification programme
  (`программа развития газоснабжения и газификации … до 2025/2030`) for the in-dev branch lines.
- **State**: Minenergo (energy strategy, general schemes for gas industry development to 2035),
  the FAS tariff orders (list every trunk pipeline by name for transport tariffs),
  Rosstat, regional governments' gasification decrees, Glavgosexpertiza approvals (per-project
  approvals name diameter/length — a strong Construction/Start source).
- **Trade press**: Interfax, TASS, Kommersant, Vedomosti, RBC, neftegaz.ru, Oil&Gas Journal
  Russia edition, energybase.ru (geoblocks non-Russian IPs — the 2026-08-12 verifier
  false-positive case), Gazprom's own corporate magazine.
- **International**: IEA/OIES analyses, Reuters/Bloomberg on export lines, Argus/S&P for flows.

Access rules that will bite: (1) energybase.ru and some Gazprom-affiliated hosts serve geo-block
pages — `url_verifier` now catches the block-page family, but agents must add a Wayback snapshot
alongside, never swap it in; (2) `docs.google`/`docviewer` mirrors of Russian PDFs need signed
requests (unarchivable-refs note 2026-08-12) — download and item-upload to IA where SPN 520s;
(3) sanctions-era disclosure thinning — Gazprom stopped publishing some operating statistics after
2022, so a 2021 annual report may be the last primary source for a capacity figure and that is a
`medium` tier with the date noted, not a `UNRESOLVED`; (4) the research backlog already asks that
Russian-press-heavy scopes re-verify refs against the block-page false positive — this campaign
does that for Russia by construction (`--verify-existing` on every HAS_REF unit).

`docs/reference/source_roster.md` has no Russia block; `docs/country_notes/russia.md` did not exist
before today — both are seeded with the above and should grow as batches ship.

## 6. Recon, discovery, routes — order after the sweep

1. **GulfPub recon (§2), standalone, run early** — 739 features vs 285 rows will trip the ">30
   reference-only Additions" escalation immediately, so plan for it: triage by `disposition`
   (`ROUTE_FOR_EXISTING` / `FRAGMENT_OF_EXISTING` / `NEAR_MISS` / `DISCOVERY_CANDIDATE`), match to
   existing under another name first. Its Additions list is also the best seed for discovery, so
   running it before the sweep's batches finish is worth it. Read the `MATCH_QUALITY` line: GulfPub
   names Russia features in Latin transliteration, so the 2026-08-14 Cyrillic fix matters less
   here than in Uzbekistan, but check.
2. **OSM**: fetch `--iso RU --substance gas --include-lifecycle` and *size it before deciding*.
   Russia is likely the US failure mode (tens of thousands of ways vs 285 rows); if so, treat OSM
   as a §8 route source, not a recon input. Country-level, unlike GulfPub, this is a fetch-then-rule.
3. **Discovery (§4)**: after the sweep, **sliced by federal district** like the batches (the US
   lesson: whole-country trips the >5-cluster gate at once). Seeds: GulfPub unmatched Additions,
   the Gazprom gasification programme lists (hundreds of interregional branch lines — the
   add-threshold will do most of the filtering), Minenergo's general scheme, Power of Siberia 2 /
   Far Eastern route sections, the Murmansk and Kaliningrad supply projects.
4. **Routes**: the `routes` leg rides on the shards for the 66 weak rows; §8 route creation is a
   maybe, later (only 1 row has no geometry at all).

## 7. Decisions for Baird — RULED 2026-09-14 ("go for it")

1. **Carried rows**: EXCLUDED from research legs now; re-look from the Russian side later as a §5
   Update once the other scopes' packets apply.
2. **Batch shape**: regional deep-sweep batches, all statuses, `--status-review` on, one pass per row
   (the US slice-2 "Option A" shape). Pilot with R1 Far Eastern. The state audit cut **8** batches
   (Urals split YaNAO vs southern subjects), not 7 — see §9.
3. **Oil**: out of scope this cycle.
4. **GulfPub recon**: run standalone now — delivered 2026-09-14, see §9.
5. **The 46 `distribution` rows**: swept (the validity leg judges scope; flag, don't reclassify).
6. **Campaign roster**: Russia `priority = 3`, `indev_status = in-progress`.

## 8. Next mechanical steps once the rulings land

```bash
STG=batches/russia-gas/staging/state-audit-20260914
python scripts/build_ref_worklist.py --tracker gas --country Russia --owe-fills \
  --exclude-pids @batches/russia-gas/carried_from_others.txt --out $STG/worklist.json
python $STG/audit_russia.py $STG/worklist.json $STG/    # port of the US audit_slice2.py, RU + subject normaliser
# -> region_audit.csv (derived district, vocab typos, duplicates), batch plan column, per-batch include/exclude files
```
Then R1 per `workflows.md` §3 deep preset with `--status-review`.

## 9. State audit + recon results (2026-09-14)

**State audit** — `batches/russia-gas/staging/state-audit-20260914/` (`audit_russia.py`,
`region_audit.csv`, `batch_plan.csv`, `duplicate_candidates.csv`, `batches/<batch>/include_pids.txt` +
`exclude_pids.txt`). 252 in-scope rows (285 − 33 carried), spatial join of routes-repo termini vs
Natural Earth admin-1, federal district hand-mapped from the subject (NE's `region` is coarse/stale).
Five rows placed by hand: P1472 (North Caucasus–Transcaucasia trunk) and P2227 (Blue Stream Turkish
leg) and P5656 (Petrovsk–Elets, no geometry) → R7; P4559 (Sakhalin–Jilin) and P5409 (Soyuz Vostok,
geometry starts in Shanghai) → R1.

| batch | rows | units | in-dev | op/idle | cancelled | scope |
|---|---|---|---|---|---|---|
| r1-fareast | 32 | 484 | 11 | 17 | 4 | Far Eastern FD (Sakhalin, Yakutia, Khabarovsk, Primorye, Amur, Kamchatka, Chukotka, Buryatia) |
| r2-nw-operating | 28 | 421 | 0 | 28 | 0 | Northwestern FD operating/idle |
| r3-nw-indev | 27 | 413 | 26 | 0 | 1 | Northwestern FD in-dev (Nord Stream / Baltic / Komi–Ukhta) |
| r4a-urals-yanao | 30 | 453 | 7 | 23 | 0 | Ural FD, Yamalo-Nenets AO |
| r4b-urals-south | 23 | 345 | 4 | 19 | 0 | Ural FD, KhMAO / Tyumen / Sverdlovsk / Chelyabinsk / Kurgan |
| r5-volga | 31 | 467 | 2 | 29 | 0 | Volga FD |
| r6-siberia | 32 | 483 | 11 | 16 | 5 | Siberian FD |
| r7-central-south | 49 | 732 | 14 | 34 | 1 | Central + Southern + North Caucasian FDs |

Order: R1 (pilot) → R2 → R3 → R4a → R4b → R5 → R6 → R7. Each batch's `Location [ref]` fills carry
the audit's typo list (`region_audit.typos`) and START/END mismatches for that batch.

**GulfPub recon** — `batches/russia-gas/staging/recon-gulfpub-20260914/` →
`deliverables/pipelines_batch_20260914_1648_ET_russia-gas_reconciliation.xlsx` (7 sheets, recalc ok).
739 gas features (all with geometry; 710 operating / 11 construction / 9 proposed / 9 idle) vs the
full 285-row roster: overlaps 546 (519 yellow, 27 green), additions 193 (NEAR_MISS 190,
FRAGMENT_OF_EXISTING 1, DISCOVERY_CANDIDATE 2, ROUTE_FOR_EXISTING 0), GEM-only 142, status conflicts
113 (71 are GEM `proposed` vs GulfPub `operating` — GulfPub's status field is stale-optimistic, treat
as a lead not a verdict), ambiguous clusters 225, 1 route-replacement candidate. Health: 100% named,
100% geometry, no `MATCH_QUALITY` warning, `escalations: []`, so the >30-Additions gate does not fire
on genuine additions (2 DISCOVERY_CANDIDATE). Triage notes: the 190 NEAR_MISS rows are hand
adjudication on the workbook (most are GulfPub splitting one GEM trunk into many named strings);
P6540 Tambeyskoye–Bovanenkovo absorbed 76 reference features (10.3%) — check it is not a catch-all
match on the Yamal cluster before trusting its overlap row. Standalone §2 workbook: NOT picked up
by a handoff packet.

## 10. R1 Far Eastern pilot — results + the two defects it found (2026-09-15)

`batches/russia-gas/staging/deepsweep-r1-fareast/` → `deliverables/pipelines_batch_20260915_1851_ET_russia-gas_deepsweep-r1-fareast.xlsx`
(10 sheets, recalc ok; rebuilt 09-15 for the three defects in §11 — UNRESOLVED 38 → 17). 32 shards, 0 coverage gaps, 0 missing PIDs. Staged: 213 fills, 257 refs
added, 102 validity records, 31 status reviews, 22 reverified, 18 dead links, 38 UNRESOLVED.

**Status review** (one per row, annual-update mode): 22 CONFIRMED, 7 CHANGE_PROPOSED, 1 STALE
(P1440 Trans-Korea — newest project-specific evidence is 2019), 1 UNRESOLVED (P2706 Yakutsk–Aldan,
where the real question is existence, not dormancy). The 7 changes: P3175 construction→operating
(two 2025-12 sources incl. ALROSA's own release), P6710 construction→operating (commissioned
2025-12-24), P3895 proposed→construction, P3896 shelved→(YATEK 2025-10-29 restart), P5521 and P7600
are StartYear1 changes on a confirmed status, P6682 construction with new 2026-05 evidence.

**Validity**: 60 open concerns (36 spec, 16 attribution, 3 route, 3 duplicate, 1 existence,
1 classification) + 38 confirmed/caveat. Headline items — P2706 flagged as a possible phantom row;
P3208 vs P5521 and P3603 vs P5409 sent to human redundancy adjudication; P2424's $3bn SegmentCost
and `CapacityUnits=mtpa` both unsupported; P2352/P2353/P5409 route geometry contested (P5409's
digitized route starts in Shanghai).

**Family finding — Sakhatransneftegaz StartYear1.** The Srednevilyuyskoye–Yakutsk family carries
1982 unsourced on P3364/P6691 and 2014 on the 530 mm String I/II rows (P3365, P6695), while the
operator's own commissioning table and a government press release put String I at 1967. Treat the
family as one question at review time, not four independent cells.

**Gates** (`sweep_gates.py`): A=1 (P4559, single-host but honestly `medium` throughout), B=0 PASS,
C=52 advisory, D=0 PASS, E=0 PASS, F=0 PASS, I=28, I'=0 PASS, **J=0 PASS, L=0 PASS**, K=119 advisory.

### Two engine defects the pilot exposed (both fixed, both live for R2+)

1. **`sweep_gates` scored validity records over the wrong ref set.** A `__VALIDITY__` record carries
   no `verifications` by repo convention (documented in `audit_shard.py`) and the merge carries its
   `proposed_refs` through unfiltered — so gates B and D, which count `ok AND contains_value` refs,
   scored every validity concern at zero. 33 of 33 gate-B flags and 49 of 49 gate-D flags were noise.
   Fixed with an `evidence()` helper that applies the convention; a validity record that *does* carry
   verifications is still judged strictly.
2. **`url_verifier` could not read a Cyrillic page at all.** The Latin matcher folded to `[a-z0-9]`,
   so a Russian-language page never matched an English GEM name, *and* it required the name's generic
   descriptor tail ("Gas Condensate Field", "Gas Pipeline") that no Russian source prints. Every
   Russian ref therefore read as "does not name the pipeline". Fixed by romanizing the page with the
   reconciler's own `normalize.translit_cyrillic` and requiring only the DISTINCTIVE tokens (shared
   `_NAME_STOP` + a module-local descriptor list, kept local so no committed recon run moves).
   Evidence: `backfill_name_found.py --recheck-false` flipped 36 of 36 shard verifications and every
   re-checked store verification from false to true, with unreadable documents left UNSTAMPED
   (unknown, never false). Endpoint proper nouns are all still required, so the "page about endpoint
   A only" failure the gate exists for is untouched.

   **Residue, and it is honest**: gate I's remaining 28 units are pipelines whose GEM name is
   *translated* rather than transliterated (P5409 `Power of Siberia 2` vs `Сила Сибири-2`), or whose
   Russian name is an abbreviation (P6682 `СБНГКМ` for Srednebotuobinskoye), or media the verifier
   cannot read (a .jpg schematic, a contractor PDF). Each carries the agent's own hand-read in its
   note; `merge_qc.relevance_qc` caps them at `low` with a note, which is the designed
   "the researcher decides" outcome, not a data error.

   **Owed**: Ukraine, Kazakhstan and Uzbekistan were swept under the broken matcher and are already
   delivered. Their `name_found=false` stamps are not evidence — re-check with
   `backfill_name_found.py --shards store --recheck-false` before anyone acts on a relevance flag
   in those workbooks.

## 11. R2 Northwestern operating — results + three workbook defects (2026-09-15)

`batches/russia-gas/staging/deepsweep-r2-nw-operating/` →
`deliverables/pipelines_batch_20260915_1851_ET_russia-gas_deepsweep-r2-nw-operating.xlsx`
(10 sheets, recalc ok — no error cells). 28 rows, one shard each, 0 coverage gaps, 0 missing PIDs.
Workflow `wf_a84178c3-177`: 28/28 agents, 0 errors, 3.8 h. Staged: 190 fills, 225 refs added,
58 validity records, 28 status reviews, 4 reverified, 27 dead links, 12 UNRESOLVED (the pre-defect-1
build reported 28 — see below; no research was lost, the 16 difference were phantom rows).

**Status review** (one per row): 26 CONFIRMED, 1 CHANGE_PROPOSED, 1 UNRESOLVED.
The single change is **P5539 Punga–Ukhta–Gryazovets IV, and it is not a status doubt** —
`operating` is well corroborated. It carries two edits: `Operator` blank → **Gazprom Transgaz Ukhta**
(two independent sources; NOT Gazprom Transgaz Yugorsk, whose territory the operator's own
Vuktylskoe-LPUMG page says ends upstream at the Pelenyor Ural pass — gem.wiki's uncited infobox has
this wrong), and `RouteAccuracy` `high` → **`low (subnational, imprecise, or unranked)`** because the
geometry staged in the routes repo is 1 of the 13 OSM member ways of relation 17195756, ~135 of
~943 km. `RouteType` stays `Mapped route (at any accuracy)` — a fragment is still mapped geometry.
A redigitization of the full relation is owed as a §8 route candidate.
The UNRESOLVED is **P7560 Volkhov–Petrozavodsk–Kondopoga**.

**Validity**: 58 records — 25 open concerns (14 spec, 9 attribution, 2 route), 24 confirmed (caveat),
1 confirmed (concern), 1 confirmed (not duplicate), 7 blank. Headline items beyond P5539: its
`zaogsp.ru/istoriya/punga` citation is **misattributed** (the page describes a 1976 Berezovsky-District
capital-repair object on the Punga end, a different physical segment under Transgaz Yugorsk) and was
removed from Fuel/PipelineType/Status; its `FuelSource = Medvezhye` is contested against an Urengoy
reading of the 1981 commissioning-era name; and three sources give three ordinals (OSM "4",
company newspaper "III", siyanie-severa "Уренгой — Ухта — Грязовец") for the same 1981 line — logged
as informational so a later pass does not rediscover it as a duplicate.

**Gates** (`sweep_gates.py`): A=2, B=0 PASS, C=42 advisory, D=0 PASS, E=0 PASS, F=0 PASS, I=2,
I'=0 PASS, **J=0 PASS, L=0 PASS**, K=115 advisory, M=1 advisory (see defect 3).
Gate I's residue is 2 units, both **P5540 Vuktyl–Ukhta II** (Length, Diameter) on one Wayback copy of
a Severgazprom journal PDF — capped at `low` with notes, the same honest-residue class as R1's 28.

**DEAD_LINK = 27, and 10 of them are not dead refs.** 10 carry `link_live: true` — the page returned
200 and merely failed the value-substring screen, i.e. "re-read this page", never "delete this ref".
The other 17 did not load at all, mostly geo-blocked `*.gazprom.ru` plus one 403 `e-disclosure.ru`.
Standing rule unchanged: only a confirmed 404/410 retires a ref.

**Two pre-run unit-error suspicions were wrong and are closed.** P3176 `Diameter = 55.91` and P5540
`Diameter = 48` both already carry `DiameterUnits = in` (1420 mm / 1220 mm). The agents found the
real nuance instead: P3176's 880 km route is genuinely **multi-diameter** — Gazregion 1420 mm;
Stroygazmontazh 1400 mm over km 538–852.7 and 800 mm over km 852.7–859.5.

### Three workbook defects QC-ing this packet exposed (all fixed; R1 and R2 rebuilt)

1. **Superseded seed baselines rendered as phantom bucket rows.**
   `seed_resolutions_from_worklist.py` gives every worklist unit a baseline record; the merge folds a
   shard fill onto that baseline only when the fill is *ref-only*, so a fill that also proposes a NEW
   value (`StartYear1` unchanged but `StartMonth1` added) is staged as its own FILL and the baseline
   stays behind untouched. The leftover reached the bucket tabs as a blank-note row — a cell resolved
   with two high-tier refs on `Gas_Fills` *also* appeared on `Gas_Refs_Unresolved` reading "could not
   reach 2 working sources", flatly contradicting the Backend paste surface, where the fill's refs had
   correctly won. The SOP rule ("a sourced FILL supersedes the carried record for the same cell") and
   `sweep_gates.py` gate I already honoured this; the workbook did not.
   Fixed by `_resolve_superseded()` in `build_ref_workbook.py`: a MISSING_REF baseline is DROPPED (its
   `[ref]` cell was empty by definition), a HAS_REF baseline is KEPT and annotated (the dead ref being
   replaced is information that lives nowhere else), and a baseline carrying the agent's own notes is
   left exactly as written. R2: 16 dropped / 37 annotated, UNRESOLVED 28 → 12. R1: 21 / 43, 38 → 17.
   Both now have zero blank-note rows on `Gas_Refs_Unresolved` and `Gas_Refs_DeadLinks`.
   **No research was missing** — every stub had a sibling FILL and the Backend surface was already right.
   **31 staging dirs outside Russia carry the same stubs** (largest: iran-gas ref-sweep-operating
   81/13, us-gas deepsweep-remainder 79/28, iraq-gas ref-sweep-operating 58/21). All are
   staged-not-applied, so nothing wrong reached the tracker; rebuilding them is a separate
   cross-country pass and needs a scope decision (some feed two-file handoff packets).

2. **An owner/operator FILL reached no paste surface at all.** P5539's sourced `Operator` was staged as
   `{ref_col: "Operator [ref]", class_in: "FILL", tier: "high"}` with **no `tab: "operators_owners"`
   key** — worklist ref units carry that key, a subagent-authored FILL for the same cell does not. The
   tracker Backend mirror excluded it by `ref_col in OO_PRIMARY`, and the `Gas_OperatorsOwners` tab did
   not draw it in because it filtered on `tab` alone, so R2's single headline finding survived only on
   the `Gas_Fills` detail tab — which also mislabelled its Target tab as "tracker". Fixed with a shared
   `_is_oo()` (either marker) used by the Backend exclusion, the oo tab's input, the handoff path's
   old local lambda, and the Target-tab column. P5539's `Operator` + `OperatorLocalLanguage` now render
   green beside their `[ref]` on `Gas_OperatorsOwners`.

3. **Prose in a pasteable Backend cell.** P5539's status-review `values` held
   `"downgrade from 'high' to 'low (…)' pending redigitization -- staged route geometry covers only
   ~14% …"` in `RouteAccuracy` and a similar narrative in `Operator` — recommendations, not cell
   content, tier-tinted on a surface whose whole purpose is copy-paste. Same class as the US-gas-batch-5
   fix (`7e75f26`), which was a hand fix with no guard behind it. Data corrected in both the shard and
   the store (`RouteAccuracy` = the bare vocabulary value; `Operator` dropped from the status record
   entirely, since it is staged as its own FILL) with the rationale moved to `researcher_notes`, and
   **new gate M** now catches it at delivery: a `values` entry carrying a narrative marker
   (` -- `, `see `, `pending `, `do not `, `downgrade`, a URL) or running past 120 chars, excluding
   the columns that are legitimately narrative. R2's remaining M=1 is P2447's long-but-genuine
   `FuelSource` string — advisory, not a defect.

## 12. R3 Northwestern in-development — results + two status-contract defects (2026-09-15)

`batches/russia-gas/staging/deepsweep-r3-nw-indev/` →
`deliverables/pipelines_batch_20260915_2130_ET_russia-gas_deepsweep-r3-nw-indev.xlsx`
(10 sheets, recalc ok — no error cells). 27 rows / 413 units, one shard each, 0 coverage gaps,
0 missing PIDs. Workflow `wf_a18c10bd-251`: 27/27 agents, 0 errors, 2 h 14 m, 4.97 M subagent tokens.
Merged store 552 records: 222 fills, 62 validity, 27 status reviews, and 220 ref records
(174 REFS_ADDED, 39 UNRESOLVED, 5 DEAD_LINK, 2 REVERIFIED) after 21 superseded MISSING_REF
baselines dropped and 29 carried records annotated. 191 fills folded to ref-only (the value the
agent proposed was already the sheet's).

**The brief reached every agent inline, and the R2 defect did not recur.** Dispatch was the baked
one-off script again (args compiled into a copy of `critical-deep-sweep.js`), pre-verified by a dry
run that asserted all 27 prompts carried `## Scope-specific guidance` plus the brief's first and
last lines (27 × 63,008 chars), then confirmed against live transcripts ~4 min in. Keep this as the
dispatch recipe — `args.extra_brief_path` is still never opened.

**Gates.** J **0**, L **0**, M **0**, B/D/E/F/I′ all PASS. Advisory: A=3, C=33, I=2, K=106.
A is three Pskov rows sourced only to `gazprommap.ru` (P4166, P4167, P4172) — the regional
gasification map is genuinely the only public document naming these отводы. C=33 is the batch's
own prediction realized: the 2015 territorial-planning decree **816-р** (42 units) and its 2024
amendment **3302-р** (25 units) carry a third of the batch, and a planning-schedule line item is
weak evidence of current status — every `high` leaning on them is worth a second look before paste.
K=106 single-ref REFS_ADDED is the expected shape for a slice where 14 of 27 rows began with zero
citations and 2–5 harvested wiki refs.

**Status review** (one per row): 17 confirm / 7 change / 3 unclear. Six of the seven changes move a
stale `proposed` forward, all on rows whose `LastUpdated` predates the evidence by 1–3 years:
P3990, P3991, P3992, P4080 → `construction` (medium; P3991/P3992 also `StartYear1=2026`, P4080 also
`ConstructionYear=2024`), P4109 → `construction` (high — signed April civil-works contracts),
P4149 Bezhanitsy–Novorzhev → `construction` (medium, one press origin, explicitly flagged). The
seventh is **P4085 Olonets–Pitkyaranta `construction` → `operating`** at high tier: two independent
dated accounts of the 26 Aug 2023 commissioning ceremony, 25 days after the row's own `LastUpdated`.
The three `unclear` (P4083, P4092, P4150) are honest: sources disagree on how far along the project
is, and P4150 is a dormancy candidate the pass deliberately would not infer without evidence.

**Validity**: 62 records, 30 open concerns — **classification 12**, spec 9, attribution 6,
spec-discrepancy 1, duplicate 1, existence 1. The classification count is the new brief section
working: 16 of 27 rows are `PipelineType = distribution`, and the sweep applied the
`магистральный газопровод` / `газопровод-отвод` vs `межпоселковый` test row by row, flagging
rather than reclassifying. Headline findings:

1. **P2707 / P7537 Ukhta–Torzhok III vs IV is NOT a duplicate — it is a naming error on P7537.**
   The pre-batch suspect (identical Cyrillic name `Газопровод Ухта - Торжок - 3 (III) (Ямал)`,
   identical 972.60 km) was settled against the primary legal text: directive 3302-р (16.11.2024)
   lists item 10 `Ухта - Торжок. III нитка (Ямал)` and item 13 `Ухта - Торжок. IV нитка (Ямал)` as
   two separate designated objects, mirroring Bovanenkovo–Ukhta III/IV at items 8/12, corroborated
   by neftegaz.ru. **P7537's `OtherLanguage*` name wrongly reads "3 (III)" and should read
   "4 (IV)"** — and its recorded 972.60 km is P7537's *own* miscitation: the cited PDF says
   `Магистральный газопровод Ухта-Торжок - 3 … протяженность … 972,6 км` twice, always "- 3",
   never IV. Fix the name; do not delete either row.
2. **The 40 bcm/y Karelia cluster (P4094 / P4095 / P4096) restates one corridor figure on three
   stage rows.** Decree 816-р item #388 covers the whole Volkhov–Segezha–Kostomuksha corridor end
   to end, with no per-stage breakdown, and GEM has copied 40.00 bcm/y (and 1400 mm) onto all three.
   P4094's `SegmentCost = 49,980,000` is separately diagnosed as the **programme-wide** 49.98 bn ₽
   Gazprom commitment for the entire 2021–2025 Karelia gasification programme, digits intact,
   magnitude lost. The three rows' merger/separation history (Interfax Mar-2024 merger report vs the
   Nov-2024 decree re-separating them) is left as an unresolved narrative tension, correctly.
3. **P4092 Kuznechnoe length: 114.5 km (as-designed survey, with full PK chainage) vs 111.3 km**
   (the operator's Apr-2023 press release and its two republications — one origin, not three).
   The 3.2 km gap is preliminary-vs-as-designed, not an error, but it is unresolved.
4. **P4150 existence**: both of the row's only two harvested citations fail to support this specific
   pipeline. **P5584 Belousovo**: the parent trunk is confirmed real and operating, but its
   `Capacity = 7.00 bcm/y` rests solely on an access-gated consultant.ru document.

Dead links: 5, down from the 40 the worklist flagged — the agents re-read the rest. The four
pre-identified 404s behaved as briefed (the P2313 asninfo typo path, P2437's act 2915-р found on a
live mirror by searching the act number, P4210 neftegazpro), and **P2707's apparent fifth 404 was
the malformed cell it was predicted to be** — two URLs concatenated without a separator, both halves
200.

### Two status-contract defects, both fixed in the engine (not in the shards)

1. **A malformed `proposed_changes` killed the whole merge.** P4085 wrote
   `proposed_changes: ["Status"]` — column names, not a `{column: value}` map — and
   `merge_qc.status_qc`'s `dict(changes or {})` raised `ValueError: dictionary update sequence
   element #0 has length 6; 2 is required`, naming no PID, aborting all 27 shards. New
   `merge_deepsweep_shards.status_changes()` recovers the Status column from the record's own
   `proposed_status`, drops any other column named without a value with a QC note, and never
   guesses. One bad record must not cost 26 good shards a merge.
2. **A `change` verdict whose value reached no paste surface.** P4109 stated `proposed_status`
   with `proposed_changes: null`; P4149 wrote the whole record under `current_value` /
   `candidate_value` instead of `current_status` / `proposed_status`. Both merged with
   `values = {}` — the Backend tints nothing, so the researcher reads "this row changed" with
   nothing to paste. Same defect class as R2's owner FILL that no tab drew. `status_changes()` now
   reads the synonym keys (`PROPOSED_STATUS_KEYS` / `CURRENT_STATUS_KEYS`) and recovers the change,
   and `status_qc` downgrades any remaining valueless `change` to `unclear` with a note — a change
   nobody can paste is not a change. Both rows now carry `{'Status': 'construction'}`.
   The `_2128_ET` build made before these fixes is in `archive/`.

## 13. R5 Volga — the lean-pass pilot (2026-09-16)

First batch run under `docs/sops/lean_pass.md`: 31 rows, 467 full units cut to 275 owed
(272 `MISSING_REF` + 3 `HAS_REF` the script could not clear); 192 deferred to
`deferred_units.json` (185 blank-value fills, 6 refs cleared by script, 1 access-blocked). Eleven
family groups (≤4 rows / ≤38 owed units), one Sonnet agent each, a 14,984-char brief carrying only
the batch traps (Transgaz subsidiary map, Soviet city names, the отвод-vs-межпоселковый test,
aggregate-vs-segment pairs, the measured host outages).

**Cost:** 1,176,315 subagent tokens, **~38 k/row against R3's ~184 k** (target ≤~70 k), 39 min
wall against 2 h 14 m. **Yield did not thin:** 236 refs added on 30 of 31 rows (66 unique URLs),
42 fills (21 sourced), 39 validity records with 22 open on 17 rows (R2, the comparable operating
slice, had 25 open on 28 rows), 31 status reviews at 29 confirm / 2 unclear / 0 change (R2: 1 change
on 28). Substantive catches: P2430 length 263 → 152 km on two sources; P2364 1973 vs 1974; the
operator's own history calling Saratov–Gorky распределительный (P2383); P4063/P4112 recorded
`distribution` but sourced as отводы to a GRS; capacity aggregates carried on both strings
(P2340/P5744, P1466/P5656); P2425's cost unsourced; P5714's geometry on the wrong leg.

**Where the lean shape shows:** gate K = 112 single-ref units and gate C = 43 units on four dominant
documents — including a uCoz free-hosted local page (`ulianovsk-8422.my1.ru`) carrying 19 units on
P2286/P2430. Those are the deferred second sources, not misses; the fills pass owes them. One engine
defect logged to `staging/deepsweep-r5-volga/DEFECTS.md` rather than fixed mid-batch: seven shards
wrote validity in a `contested: {col: text}` + `notes` shape that the merger does not read, so
P2390 and P2435 have a blank Finding in the workbook (Diameter 377 vs 530 mm; 325 vs 300 mm).

**Decision:** the pilot met its target without thinning findings — R4a, R4b, R6 and R7 run lean with
the same recipe, one batch per session. SOP unchanged apart from recording the pilot's numbers.

## 14. R4a Urals-YaNAO — second lean batch (2026-09-21)

30 rows (23 operating, 7 in-development), 453 full units cut to 183 owed (134 `MISSING_REF` + 49
`HAS_REF` the script could not clear); 270 deferred to `deferred_units.json` (146 blank-value fills,
82 access-blocked refs — mostly `*.gazprom.ru` timing out from a US IP — and 42 refs cleared by
script). Eleven family groups, one Sonnet agent each, a 15,948-char brief (operator ladder for
Transgaz Yugorsk/Surgut/Ukhta and the Gazprom Dobycha units, Cyrillic search names, the
aggregate-vs-segment traps on the multi-string rows, measured host outages). The brief was baked
into a copy of the workflow script (`workflow_baked.js`) rather than passed through `args`, so it
reached the agents byte-exact.

**Cost:** 1,361,070 subagent tokens, **~45 k/row against R3's ~184 k** (R5 ~38 k), 57 min wall.
Higher than R5 because a quarter of the owed units were failing `HAS_REF` re-reads and most operator
pages were reachable only through Wayback. **Yield:** 165 refs added on 28 of 30 rows (68 unique
URLs; 69 high / 94 medium / 2 low), 24 fills (13 sourced), 50 validity records with 19 concerns
open on 16 rows, 30 status reviews at 27 confirm / 2 unclear / **1 change** — P5404
Bovanenkovo–Ukhta VI `construction` → `proposed` (816-р lists нитка VI only among planned objects).

Substantive catches: P5402/P5403/P5404 all carry String III's 1158.60 km, from a PDF that never
names IV/V/VI; the three Nadym–Punga I/II/III route files measure ~50–60 km against ~570–700 km
recorded at `RouteAccuracy = high`; P4146's Length ref states a 1238 km combined figure; P4311
Yamburg–Tula II 3113 vs 2146 km in the table that matches string I exactly; P2450 carries P4311's
«вторая нитка» name and the two route files look like one trace; P0737/P0738 SegmentCost is an even
split of a two-line aggregate; P7546 118 vs 57 km on one source.

**Gates:** E/F/I/I'/L/M PASS, J skipped (lean), advisory C=15, D=3, K=83. Gate I first read 4 —
P3507/P5612 Status + Owner refs on the Wayback Шемордан ЛПУ page, stamped `name_found=false` because
the agent screened on the English name. The page reads «Уренгой-Центр 1, Уренгой-Центр 2»; stamped
true by hand with a note. Two engine defects logged to the batch's `DEFECTS.md` (the name matcher
misses the sheet's spaced-hyphen alias «Уренгой - Центр»; `backfill_name_found.py` never walks
`status_reviews`). R5's logged merge defect (validity text under `notes` dropped) was fixed before
this merge because it would have blanked findings here; R5's workbook rebuild is still owed.

Next: R4b Urals-south, then R6, R7 — lean, one batch per session.

## 15. R4b Urals-south — third lean batch (2026-09-22)

23 rows, 345 full units cut to 156 owed (139 `MISSING_REF` + 17 `HAS_REF`); 189 deferred (143
blank-value fills, 32 access-blocked refs, 14 cleared by script). Nine family groups, one Sonnet agent
each, a 17,491-char brief baked into `workflow_baked.js` (operator ladder led by Transgaz
Yekaterinburg; the copied-figure and whole-system-name traps on the paired rows; the Kurgan отвод
classification question).

**Cost:** 1,253,344 subagent tokens, **~54.5 k/row** (R4a ~45 k, R5 ~38 k, R3 ~184 k), 46 min wall.
Above R4a because 16 of 23 rows were fully uncited — nearly every unit was a fresh search. **Yield:**
115 refs added on 22 rows (47 unique URLs; 53 high / 54 medium / 2 low), 28 fills, 31 validity
records with 13 concerns open on 11 rows, 23 status reviews at 20 confirm / 2 unclear / **1 change** —
P3977 Shumikha–Almenevo `proposed` → `operating` (the object sat open on gazprommap.ru's 2021–2025
Kurgan list in a 2022 Wayback capture and is gone from the live 2026–2030 list).

Substantive catches: P2378 carries line II's 1420 mm / 1976 (line I is 1220 mm / 1977 per two
sources); P2350's own cited ref states 8.2 bcm/y for the whole line against NF's documented 4.10
split — the agent staged 8.20 as a fill, the orchestrator deferred it to a concern (a documented
divergence is flagged, not overwritten); P2320 repeats R4a's P2450 pattern («2-ая нитка» on нитка I);
P3975's 84 km belongs to a different segment; the four Kurgan отводы look like transmission.

**Orchestrator fixes before delivery:** P2315 Owner ref tier high → low (gate I=1, left as residue);
prose moved out of `contested` on four concerns; the DeadLinks note no longer tells the researcher a
geo-blocked ref is "being replaced" when nothing replaces it (`build_ref_workbook.py`). Two open
defects in the batch's `DEFECTS.md`: gate M does not screen `contested`, and validity text written
under `summary` is not carried to `recommendation`.

Next: R6 Siberia (delivered — §16), then R7 Central+South — lean, one batch per session.

## 16. R6 Siberia — fourth lean batch (2026-09-22)

32 rows, 483 full units cut to 180 owed (159 `MISSING_REF` + 21 `HAS_REF`); 303 deferred (183
blank-value fills, 46 access-blocked refs, 74 cleared by script). Eleven family groups (hand-merged
from 22 auto groups), one Sonnet agent each, an 18,676-char brief baked into `workflow_baked.js`
(Transgaz Tomsk ladder; Norilsktransgaz as a non-Gazprom operator; the P7615 divergence; the
Omsk/Novosibirsk отвод classification test; the cancelled East Siberian rows).

**Cost:** 1,161,638 subagent tokens, **~36.3 k/row** (R4b ~54.5 k, R4a ~45 k, R5 ~38 k, R3 ~184 k),
32 min wall. Cheapest lean batch so far — the groups shared their decrees and programme pages.
**Yield:** 78 refs added on 27 rows (48 unique URLs; 20 high / 40 medium / 10 low), 60 fills, 42
validity records with 27 concerns open on 22 rows, 32 status reviews at 20 confirm / 8 unclear /
**4 change** — the three Omsk отводы (P3980, P3981 → operating, P3981 launched Dec 2025; P3982 →
operating from Dec 2022) and P4056 → construction (one source, Feb 2025).

Substantive catches: the P7615 divergence held without orchestrator help (the agent kept 4.10
UNRESOLVED and filed the aggregate), and found that string II is itself unfinished on its Novokuznetsk
stretch; four existence questions (P3367, P2703, P2705, P4110) and one duplicate (P3604 ≈ the Kovykta
trunk); P6535's Sonatrach owner and system-level capacity; P5510's miscited decree ref.

**Orchestrator fixes before delivery:** renamed non-column fill keys on the Novosibirsk–Barnaul
family; reverted changed values on UNRESOLVED fills (P2705, P3604); prose out of `contested` on six
concerns; empty recommendations filled on five; normalized the P4056/P4110 agent's off-schema records
(and dropped a gem.wiki ref it listed); P4056 Fuel tier high → medium (gate I); P5510's script-seeded
REVERIFIED marked low. Five defects in the batch's `DEFECTS.md` — two are R4b's still open, and the
merge-side schema checks (#2, #4, #5) are the ones worth fixing before R7.

Next: R7 Central+South — lean, one batch per session. Then the campaign-wide fills pass over the five
lean batches' `deferred_units.json`.

