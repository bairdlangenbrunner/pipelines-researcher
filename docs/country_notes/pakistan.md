# Pakistan

70 gas rows (GGIT) and 4 oil rows (GOIT). Gas was swept in full on **2026-08-07** —
operating deep sweep (63 rows), in-development annual review (6), cancelled review
(1), GulfPub and OSM reconciliations — and the SNGPL asset-register crosswalk plus a
re-run of both wiki legs followed on **2026-08-10** (the 08-07 pass ran with gem.wiki
403ing). **Oil has not been swept** (4 rows: 2 operating, 2 cancelled).

**THREE files to work**, none of which subsumes the others:
`…_20260810_1112_ET_pakistan-gas_handoff-{actions,evidence}.xlsx` (the packet — the
researcher works from the ACTIONS file) plus the two STANDALONE recon workbooks
`…_20260807_1530_ET_pakistan-gas_reconciliation-{gulfpub,osm}.xlsx`. The packet's
`recon_actions` count is **0** — the GulfPub/OSM decisions live ONLY in those two files.
Staged, not applied. Counts regenerate via
`python scripts/staged_summary.py --country Pakistan --commodity gas`.

Pakistan's distinguishing problem is not thin research; it is **provenance**. Nearly
three quarters of the country's gas rows came from one bulk load off two map files,
so the usual "find a second independent source for this value" loop has no text to
grip. **That problem is now largely solved for SNGPL** — SNGPL's own audited asset
register (Annual Report 2018) accounts for 49 of the 51-row cohort, added
2026-08-10. Read the escalation memo before working the packet:
`notes/escalation-2026-08-07-pakistan-sngpl-map-bulk-load.md`.

## The July-2023 map bulk-load (read this first)

**51 of 70 rows** share one provenance — last updated within a 5-day window in July
2023, owner SNGPL 100%, and exactly two refs on every row:

- `https://www.sngpl.com.pk/images/transmission/TransmissionMap042022L.jpg` (JPG map)
- `https://www.pepl.com.pk/assets/images/downloads/Energy-MapA4-2020.pdf` (PDF map)

A further 8 rows are the SSGC equivalent. Only 4 rows in the whole country are
sourced to news or industry reporting. Both artifacts are **cartographic**, so
lengths, diameters and endpoints were digitized or inferred from a map, and there is
usually no text naming the individual segment.

What follows from that:

- **`UNRESOLVED` is a normal outcome here**, not a research failure. 362 of the ref
  units in the packet came back unresolved, overwhelmingly on this cohort.
- **The sweep's 16 `existence` concerns track segment obscurity, not existence.** The
  GulfPub recon — an *independent* cartographer — traces 11 of the 16, and the SNGPL
  register (below) names the other five. **No existence question remains open.**
- **Both source URLs are live and must be kept.** The PEPL PDF fails
  `url_verifier.py` on an SSL chain error while `curl -sI` returns 200 — that is a
  transport artifact, not a dead link. Wayback: SNGPL `20250527234936`, PEPL
  `20260731113845`. Standing rule applies: never drop a ref over an access failure.

## The SNGPL asset register — the document that unlocks the cohort (2026-08-10)

> `https://www.sngpl.com.pk/download/AnnualReport-2018/SNGPLAR-2018.pdf`
> — *"TRANSMISSION SYSTEM As at June 30, 2018"*, printed pp. 32–37.

A **270-row, text-searchable, auditor-attested inventory** of every SNGPL
transmission section: name, diameter in inches, mainline and loopline kilometres.
Parsed to `batches/pakistan-gas/staging/register-crosswalk/sngpl2018_transmission_register.json`;
the parse reconciles to the register's own printed grand total (mainline
**4,685.92 km**, loopline **4,190.05 km**), so it is a controlled extraction, not
eyeballed. Per-row match record: `register_crosswalk.json`.

- **49 of the 51-row SNGPL cohort are accounted for** — 45 single-section matches on
  name + length + diameter at the register's two-decimal precision, plus 4 exact
  arithmetic composites where GEM aggregates and the register itemises (P4101, P4107,
  P4136, P4162). **A composite is a granularity difference, not an error — do not
  "fix" it.**
- Staged as **98 ref-only units across 49 rows** (`Length [ref]` + `Diameter [ref]`,
  every one of which was empty). **No sheet value changes.**
- **Tiering is about origins, not document quality:** `high` only where GulfPub
  independently traces the same line; `medium` where the register stands alone, because
  SNGPL is the same *publisher* as the row's existing map ref — a far better document,
  but not a second independent origin.
- `url_verifier.py` returns 200 + "value not found" on it — the documented large-PDF
  false negative (3.9 MB, 186 pp.). Values were confirmed with `pdftotext -layout`.
- **It carries no dates**, so it does nothing for the 60 `operating`-with-no-`StartYear1`
  rows, and nothing for the 8 SSGC rows. SNGPL dropped this table after 2018 (2019–2024
  all 404 at the same URL pattern), so 2018 is the edition to use.
- **The transferable lesson:** 63 per-row subagents could not crack this cohort because
  no source names the individual segments; one operator asset register did it in a single
  pass. Where a country's rows trace to a bulk load off an operator artifact, look for
  **that operator's audited annual report** before dispatching per-row research.

## Regulators / official data
- **OGRA** (Oil and Gas Regulatory Authority, ogra.org.pk) — licences the transmission
  companies; its licence schedules and State of the Industry reports are the most
  promising untapped source for segment-level facts.
- **SNGPL** (sngpl.com.pk) — annual reports carry province-wise transmission length
  and FY additions, and the **2018 edition carries the line-wise asset register** (see
  below) — the single most valuable document for this country. The transmission map is
  the origin of most GEM Pakistan rows.
- **SSGC** (ssgc.com.pk) — the southern equivalent; better-documented network than
  SNGPL's Punjab distribution-region lines.
- **HDIP** (Pakistan Energy Yearbook), **PPIB**, **Pakistan Economic Survey** — national
  statistics, occasionally segment-level.
- **PEPL** (pepl.com.pk) — Pakistan Energy Map, the second half of the bulk-load pair.

## Key operators / owners
The country is a two-company system, and the split is geographic, not commercial:

- **Sui Northern Gas Pipelines Ltd (SNGPL)** — 52 of 70 rows. Punjab and Khyber
  Pakhtunkhwa. Also the operator of the RLNG (re-gasified LNG) trunk lines.
- **Sui Southern Gas Company (SSGC)** — 12 rows. Sindh and Balochistan.
- Transnational/proposed rows carry their own owners: **Interstate Gas Systems (ISGS)**
  for the Pakistan side of IP, **Iran Ministry of Petroleum**, **Turkmengaz** (TAPI),
  **Gazprom** (Pakistan Stream / North-South).
- Upstream producers appear as sources, not owners: **OGDCL**, **PPL**, **Mari
  Energies**, **OMV** (Sawan).

**`Pasargad Energy Development Co` on P0451 (IPI) has ZERO corroboration as an owner** —
the cancelled review recommends NIGEC, and possibly ISGS on the Pakistan side.

## Gotchas
- **Every row is `RouteType = Mapped route (at any accuracy)`** (70/70), but 55 are
  `RouteAccuracy = very low (straight line/schematic)` and only 7 are `medium`. So when
  a drawn route disagrees with `LengthKnown`, **the route is the more likely error** —
  do not "correct" a sourced length to match a schematic line. 13 rows carry a
  length-vs-route flag.
- **60 of 70 rows are `Status = operating` with no `StartYear1`** — 51 of them the map
  cohort. A map gives you geometry, not a commissioning date; same root cause.
- **A gas FIELD's first-production year is not the PIPELINE's commissioning year.** The
  Potohar rows (Dhulian, Meyal, Dakhni) invite this error — the fields date to the
  1930s–40s.
- **Loop/second lines are systematically present**: `… Gas Pipeline` and `… Gas
  Pipeline II` with identical endpoints (Sidhnai–Faisalabad, Faisalabad–Shahdara,
  Dandot–Gali Jagir–Wah, Sahiwal–Lahore, Wah–Nowshera). A "II" must be dated later
  than its "I". An identical length on the pair is **expected**, not a copy-paste
  signature — the register lists parallel loops at the same km and different diameters.
  **Diameter is what distinguishes them**, so treat a pair with the same length AND the
  same diameter as the suspicious case.
- **Identical lengths across different rows** are NOT automatically a defect here:
  P4088 and P4089 both read `53.14 km`, and the SNGPL register confirms **both** — Sr. 20
  `QADIRPUR LINE` at 36 in and Sr. 21 `QADIRPUR LINE (LNG PHASE-II)` at 42 in, two
  parallel loops over the same 53.14 km corridor (Sr. 19 is a third, 30 in / 53.13 km).
  Equal lengths on parallel loops are the norm on this network, not a copy-paste
  signature. P4088/P4089's drawn routes measure 93 km and 107 km, so it is the ROUTES
  that disagree with the sourced length.
- **`Presumed` is not a valid `ShelvedCancelledType`** — the live column holds
  `inferred`/`confirmed`. Corrected repo-wide 2026-08-07;
  `notes/escalation-2026-08-07-shelvedcancelledtype-vocab.md`.
- **gem.wiki 403'd for the 08-07 pass and was re-read on 08-10** (the WAF passes a UA
  leading with the `baird-wiki` token — `WIKI_UA`, shared by `url_verifier.py`,
  `wiki_alignment.py` and `harvest_wiki_citations.py`, and deliberately byte-identical to
  `goit-ggit-data-ops/gem-wiki/gemwiki.py`; keep the two in sync). Both wiki legs were
  re-run and the packet carries the real results — **99 records over 70 rows**
  (69 `SHEET_SUSPECT` / 24 `WIKI_UPDATE` / 6 `WIKI_STALE_VS_STAGED`, zero `UNPARSED`,
  up from 70 all-`UNPARSED`), and the citation harvest 63/63 pages / 231 citations, up
  from 0. The blackout cost little on refs — those 63 pages hold only **10 distinct
  external URLs** between them, which is what a map-bulk-load country looks like — and a
  lot on alignment. `notes/escalation-2026-08-07-gem-wiki-cloudflare-403.md`.
- **68 of the 69 `SHEET_SUSPECT` wiki records are one question, not 68** — `Operator` is
  blank on all 70 rows while the wiki names one. That is the GGIT norm, not a Pakistan
  gap: `Operator` is filled on just **1,464 of 6,462 rows tracker-wide (22.7%)**, while
  `Owner1` is filled on 70 of 70 here. One bulk decision (52 SNGPL, 12 SSGC, 6
  transnational rows individually), and the wiki value is the lead — never the ref.
  `notes/escalation-2026-08-10-pakistan-wiki-operator-sheet-suspect.md`.
- **New leads the citation harvest surfaced** (none yet worked):
  `https://www.sngpl.com.pk/images/transmission/TransmissionMap032023L.jpg` — a **03/2023
  map, newer than the 04/2022 map every row cites**; plus `ssgc.com.pk` `page_id=5597`
  (downloads) for the still-missing SSGC register. `2023_05_may_cap_info_trans.pdf` was
  checked and is **not** a register — it is a TPA Rule 2018 Schedule-II capacity
  declaration (entry/exit points in MMCFD, gas specs), carrying no lengths or diameters.

## Redundancy candidates — ALL THREE RESOLVED AS NOT DUPLICATES (2026-08-10)
The sweep read these as one physical line digitized twice off a map. The SNGPL register
lists **both pipes of each pair separately, at different diameters** — the ordinary
mainline/loopline pattern, which is exactly what produces two rows with near-identical
totals. **Keep all rows.** Staged as `confirmed (caveat)` in
`staging/register-crosswalk/`:

- **P4105** (AV29–Sahiwal, 36 in, Sr. 74 = 145.46) vs **P4099** + **P4100** (24 in,
  Sr. 45+46 = 145.456) — two distinct pipes over one corridor, not a row plus its own
  segments.
- **P4079** (Sawan–Qadirpur, 24 in, Sr. 11 = 131.00) vs **P4101** (SV1–QV1, 42 in loop
  chain, Sr. 14–17 = 130.77) — different diameters, both in the register.
- **P4181** (Sakhakot–Swat, Sr. 267) and **P4179** (Sr. 254) are separate exact register
  entries. **P5486** (Mardan–Swat) is the one row the register does not account for —
  now an existence question rather than a duplicate one (see Open items).

## Reconciliation results (2026-08-07)
- **GulfPub**: 94 reference records, **82 overlaps** — much the best match rate of any
  country swept so far, and the reason the existence question narrowed to five rows.
  12 additions (under the >30 escalation gate), 0 status conflicts, 11 near-misses.
- **OSM**: only 9 features for the whole country — 4 overlaps, 3 `FRAGMENT_OF_EXISTING`,
  1 `ROUTE_FOR_EXISTING`, 1 `NEAR_MISS`, **0 discovery candidates**. OSM coverage of
  Pakistan gas transmission is effectively absent; do not read the thin result as
  agreement.

## Open items
1. **P4074 Kandhkot length** — register Sr. 18 `KAND KOT LINE` reads **52.23 km** (16 in,
   agrees) against the sheet's **55.23 km**. The *only* numeric disagreement across 49
   matched rows, and a one-digit slip in the same position — but direction unknown, so
   **do not apply it blind**; a second source decides it.
2. **P5486 Mardan–Swat** — the one SNGPL row the register does not account for at all.
   104.89 km at 12 in matches no section and no combination of the 12-inch Mardan-area
   sections (Sr. 256 `NOWSHERA - MARDAN` 19.76; Sr. 257 `MARDAN - PALAI` 56.00). Now that
   every other row reconciles to two decimals, this is a sharp signal.
3. **The 8 SSGC rows** have no equivalent register yet — `ssgc.com.pk` annual reports are
   the target, same shape of table.
4. **60 `operating` rows with no `StartYear1`.** The register carries no dates, so it
   cannot help; SNGPL FY narrative ("commissioned during the year") and OGRA licence
   dates are the leads.
5. **P0451 (IPI) owner attribution** — `Pasargad Energy Development Co` unsupported.
6. **Oil (4 rows) not swept.**
7. Neither recon workbook is subsumed by the handoff packet — they are separate review
   surfaces (see `docs/research_backlog.md` §2).
