# Owner-style lint — existing Owner1..Owner11 cells (2026-10-20)

Input: `data/GEM_operators_owners_snapshot_20261019.csv` (operators/owners tab, header row index 1). Styler: `scripts/entity_style.py` against `data/owner_gazetteer.csv` + `data/owner_aliases.json`. Rules: `docs/reference/owner_style.md`.

**Counts only.** Nothing is staged and nothing is written to the sheet; this report is the input to a decision on whether to run a normalization batch over existing owners (Baird 2026-10-01: new owners first, lint on existing). The sibling `.csv` holds one line per distinct name so that batch can be scoped from it.

## Headline

| | distinct names | owner cells |
|---|---:|---:|
| non-blank Owner<N> cells | 1663 | 7044 |
| already in team style (exact gazetteer / confirmed alias, unchanged) | 215 | 1297 |
| styler would CHANGE | 352 | 2560 |
| … of which gazetteer-backed (exact / alias / stem) | 241 | 2233 |
| … of which rules-only (no gazetteer hit) | 99 | 266 |

## By basis (all distinct names)

| basis | distinct | cells |
|---|---:|---:|
| rules | 1188 | 3389 |
| exact | 257 | 1544 |
| alias | 153 | 1879 |
| stem | 46 | 107 |
| ruling | 19 | 125 |

## By confidence

| confidence | distinct |
|---|---:|
| medium | 849 |
| high | 429 |
| low | 385 |

## By flag (a name can carry several)

| flag | distinct | cells | meaning |
|---|---:|---:|---|
| `no_legal_form` | 384 | 1153 | no trailing legal form recognized — add one if a quick registry search gives it |
| `fuzzy_candidates` | 116 | 515 | fuzzy gazetteer near-match listed, not adopted |
| `form_punctuation` | 47 | 87 | legal form spelled with punctuation (`Co., Ltd.`, `S.p.A.`) |
| `form_from_gazetteer` | 46 | 107 | stem matches ONE gazetteer entry; its legal form adopted (medium) |
| `form_long` | 28 | 69 | long form (`Corporation`, `Company Limited`) where the team writes the short one |
| `acronym_dropped` | 27 | 146 | trailing parenthetical acronym dropped (kept as alias) |
| `alias_candidate` | 19 | 173 | owner_aliases.json lists it as a CANDIDATE (subsidiary/JV/successor) — never adopted |
| `ruled` | 19 | 125 |  |
| `group` | 17 | 43 | `… Group` — may be a holding name with no form |
| `form_conflict` | 14 | 77 | same stem in the gazetteer under a DIFFERENT form — registration question |
| `acronym_lead` | 8 | 32 |  |
| `state_body` | 7 | 7 | ministry / government rewritten to `Body (Country)` / `Government of X` |
| `jv` | 6 | 9 | joint venture — no legal form expected |
| `form_moved` | 4 | 15 | legal form leads the name (`PAO Gazprom`); the team writes it trailing |
| `form_ambiguous` | 2 | 5 | same stem in the gazetteer under several forms — pick by hand |
| `slash` | 1 | 1 |  |
| `form_russian` | 1 | 1 | CIS form (OOO/PAO/AO/TOO) mapped to LLC/PJSC/JSC/LLP |

## Top 60 changes by owner cells affected

| cells | PIDs | raw | styled | basis/conf | flags |
|---:|---:|---|---|---|---|
| 173 | 173 | Sonatrach | Sonatrach SpA | alias/high |  |
| 117 | 117 | National Iranian Gas Company | National Iranian Gas Co | alias/high |  |
| 115 | 115 | Enbridge | Enbridge Inc | alias/high |  |
| 103 | 103 | Iraq Ministry of Oil | Ministry of Oil (Iraq) | alias/high |  |
| 92 | 92 | Transneft | Transneft PJSC | alias/high |  |
| 78 | 78 | Saudi Aramco | Saudi Arabian Oil Co | alias/high |  |
| 60 | 60 | Enagás | Enagás SA | alias/high |  |
| 52 | 52 | Sui Northern Gas Pipelines Ltd (SNGPL) | Sui Northern Gas Pipelines Ltd | exact/high | acronym_dropped |
| 49 | 49 | Gaz-System | Operator Gazociagow Przesylowych GAZ-SYSTEM SP zoo | alias/high |  |
| 46 | 46 | TC Energy | TC Energy Corp | alias/high |  |
| 42 | 42 | Gas Transmission Co Ltd (GTCL) | Gas Transmission Co Ltd | rules/medium | acronym_dropped, fuzzy_candidates |
| 41 | 41 | Petrobras | Petróleo Brasileiro SA | alias/high |  |
| 40 | 40 | Qatar Energy | QatarEnergy | alias/high |  |
| 38 | 38 | Energy Transfer | Energy Transfer LP | alias/high |  |
| 37 | 37 | Enterprise Products Partners | Enterprise Products Partners LP | alias/high |  |
| 37 | 37 | Kinder Morgan | Kinder Morgan Inc | alias/high |  |
| 37 | 37 | PDVSA | Petróleos de Venezuela SA | alias/high |  |
| 37 | 37 | Shell plc | Shell PLC | exact/high |  |
| 34 | 34 | PipeChina Guangdong Natural Gas Pipeline Company | PipeChina Guangdong Natural Gas Pipeline Co | rules/medium | form_long |
| 34 | 34 | Tokyo Gas | Tokyo Gas Co Ltd | alias/high |  |
| 32 | 32 | GAIL (India) Ltd | GAIL Ltd | alias/high |  |
| 30 | 30 | BOTAŞ | BOTAŞ AŞ | alias/high |  |
| 28 | 28 | Plains All American Pipeline | Plains All American Pipeline LP | alias/high |  |
| 27 | 27 | Aramco | Saudi Arabian Oil Co | alias/high |  |
| 27 | 27 | ExxonMobil | Exxon Mobil Corp | alias/high |  |
| 27 | 27 | SNTGN Transgaz SA | Transgaz SA | alias/high |  |
| 26 | 26 | SOCAR | State Oil Company of Azerbaijan Republic | alias/high |  |
| 25 | 25 | Chevron | Chevron Corp | alias/high |  |
| 25 | 25 | Engie SA | ENGIE SA | exact/high |  |
| 25 | 25 | Osaka Gas | Osaka Gas Co Ltd | alias/high |  |
| 25 | 24 | Plinacro Ltd | Plinacro doo | alias/high |  |
| 22 | 22 | Transco | Transcontinental Gas Pipe Line Co LLC | ruling/high | ruled |
| 21 | 21 | ConocoPhillips | ConocoPhillips Corp | alias/high |  |
| 20 | 20 | ShaanXi Provincial Natural Gas Co Ltd | Shaanxi Provincial Natural Gas Co Ltd | exact/high |  |
| 19 | 19 | TGI SAS E.S.P | TGI SAS ESP | rules/medium | form_punctuation |
| 19 | 19 | Williams Companies | Williams Companies Inc | alias/high |  |
| 18 | 18 | Pemex | Petróleos Mexicanos EPE | alias/high |  |
| 18 | 18 | Srbijagas | Srbijagas JP | alias/high |  |
| 16 | 16 | Engie Brasil Energia | Engie Brasil Energia SA | stem/medium | form_from_gazetteer |
| 16 | 16 | Saibu Gas | Saibu Gas Holdings Co Ltd | alias/high |  |
| 15 | 15 | Net4Gas | Net4Gas Holdings sro | alias/high |  |
| 14 | 14 | FIP (Fundo de Investimentos em Participações Multiestratégia) | Fundo de Investimentos em Participações Multiestratégia | rules/low | acronym_lead, no_legal_form, fuzzy_candidates |
| 14 | 14 | other | Other | exact/high |  |
| 13 | 13 | Iran Ministry of Petroleum | Ministry of Petroleum (Iran) | alias/high |  |
| 12 | 12 | BP plc | BP PLC | exact/high |  |
| 12 | 12 | Sui Southern Gas Co (SSGC) | Sui Southern Gas Co Ltd | ruling/high | ruled |
| 12 | 12 | YPFB | Yacimientos Petrolíferos Fiscales Bolivianos Corp | alias/high |  |
| 11 | 11 | MPLX | MPLX LP | alias/high |  |
| 11 | 11 | State of Qatar | Government of Qatar | alias/high |  |
| 11 | 11 | Transnet | Transnet SOC Ltd | alias/high |  |
| 10 | 10 | Naftogaz Ukraine NJSC | Naftogaz of Ukraine JSC | alias/high |  |
| 10 | 10 | Titas Gas Transmission and Distribution Co (TGTDCL) | Titas Gas Transmission and Distribution Co Ltd | ruling/high | ruled |
| 9 | 9 | Enarsa (Energía Argentina SA) | Energía Argentina SA | alias/high |  |
| 9 | 9 | Equinor | Equinor ASA | alias/high |  |
| 9 | 9 | Hokkaido Gas | Hokkaido Gas Co Ltd | alias/high |  |
| 9 | 9 | Occidental Petroleum | Occidental Petroleum Corp | alias/high |  |
| 9 | 9 | Petronas | Petroliam Nasional Bhd | alias/high |  |
| 8 | 8 | MER JSC Skopje | NER JSC Skopje | alias/high |  |
| 8 | 8 | Magellan Midstream Partners | Magellan Midstream Partners LP | stem/medium | form_from_gazetteer |
| 8 | 8 | OMV | OMV AG | alias/high |  |

## Not for the styler to decide (listed for a human)

### Several owners in one cell — 0


### Subsidiary / JV / successor of a canonical entity (SPV ruling: stays as is) — 19

- 'Snam Rete Gas SpA' (129 cells) ~ 'Snam SpA'
- 'Phillips 66 Partners' (10 cells) ~ 'Phillips 66'
- 'Shandong Natural Gas Pipeline Co Ltd' (9 cells) ~ 'National Petroleum and Natural Gas Pipeline Network Group Co Ltd'
- 'Norske ConocoPhillips AS' (3 cells) ~ 'ConocoPhillips Corp'
- 'Alrosa-Gas JSC' (3 cells) ~ 'Alrosa PJSC'
- 'Shanxi Linxian Guoxin Gas Co Ltd' (3 cells) ~ 'Shanxi Guoxin Energy Co Ltd'
- 'Venture Global LNG' (2 cells) ~ 'Venture Global Holdings Inc'
- 'OKEA AS' (2 cells) ~ 'OKEA ASA'
- 'Phillips 66 Carrier LLC' (2 cells) ~ 'Phillips 66'
- 'Kinder Morgan Freedom Pipeline LLC' (1 cells) ~ 'Kinder Morgan Inc'
- 'Kinder Morgan Crude & Condensate LLC' (1 cells) ~ 'Kinder Morgan Inc'
- 'ConocoPhillips Transportation Alaska Inc' (1 cells) ~ 'ConocoPhillips Corp'
- 'Southern Union Panhandle LLC' (1 cells) ~ 'Southern Union Co'
- 'Black Hills Energy' (1 cells) ~ 'Black Hills Corp'
- 'Enbridge Frontier Inc' (1 cells) ~ 'Enbridge Inc'
- 'Repsol Sinopec' (1 cells) ~ 'Repsol SA'
- 'NextEra Energy Resources LLC' (1 cells) ~ 'NextEra Energy Inc'
- 'Shanxi Sanjin New Energy Development Co Ltd' (1 cells) ~ 'Shanxi Guoxin Energy Co Ltd'
- 'Phillips 66 Pipeline LLC' (1 cells) ~ 'Phillips 66'

### Same stem, different legal form in the gazetteer — 14

- 'Kuwait Petroleum Co' (24 cells) ~ 'Kuwait Petroleum Corp'
- 'Shanxi Guoxin Energy Corp Ltd' (16 cells) ~ 'Shanxi Guoxin Energy Co Ltd'
- 'Indian Oil Corp' (13 cells) ~ 'Indian Oil Corp Ltd'
- 'DCP Midstream LLC' (8 cells) ~ 'DCP Midstream LP'
- 'Alberta Investment Management Co' (3 cells) ~ 'Alberta Investment Management Corp'
- 'Emirates National Oil Co' (3 cells) ~ 'Emirates National Oil Company LLC'
- 'CPC Co' (2 cells) ~ 'CPC Corp'
- 'OKEA AS' (2 cells) ~ 'OKEA ASA'
- 'China Investment Co Ltd' (1 cells) ~ 'China Investment Corp'
- 'Gujarat Gas Co Ltd' (1 cells) ~ 'Gujarat Gas Ltd'
- 'Nepal Oil Corp' (1 cells) ~ 'Nepal Oil Corp Ltd'
- 'Mineral Resources Development Co Ltd' (1 cells) ~ 'Mineral Resources Development Corp'
- 'Kuwait Oil Co' (1 cells) ~ 'Kuwait Oil Company Ltd'
- 'The Energy Cooperative' (1 cells) ~ 'The Energy'

### Dropped parenthetical that is not the name's initials — 0


