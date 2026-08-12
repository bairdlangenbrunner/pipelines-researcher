# Kazakhstan

52 gas rows (GGIT) and 41 oil rows (GOIT). Gas was swept in full on **2026-08-11** — the §9
composite: operating deep sweep (39 rows), in-development annual review (11), cancelled /
mothballed review (2), a redundancy-cluster adjudication (11 clusters / 28 rows), GulfPub and
OSM reconciliations, and the handoff packet. **Oil has not been swept.**

Staged, not applied. Counts regenerate via
`python scripts/staged_summary.py --country Kazakhstan --commodity gas` — never hand-edit them.

**THREE files to work** — the packet does **not** subsume the recons (`recon_actions = 0`):

- `pipelines_batch_20260812_1255_ET_kazakhstan-gas_handoff-actions.xlsx` (+ its `-evidence`
  twin) — 119 open decisions, 3 status changes, 266 backend paste units, 64 operators/owners
  units, 31 wiki updates, 180 open flags; evidence side 67 confirmed audits, 47 fill-detail
  and 448 ref-detail rows.
- `pipelines_batch_20260811_1001_ET_kazakhstan-gas_reconciliation-gulfpub.xlsx`
- `pipelines_batch_20260811_1043_ET_kazakhstan-gas_reconciliation-osm.xlsx`

The 08-11 `1145_ET` handoff pair was replaced by the 08-12 `1255_ET` build after cluster A
was reversed (below) — do not work from it.

Row profile: `operating` 39, `proposed` 8, `construction` 3, `cancelled` 1, `mothballed` 1.
Researchers **NF** 39, **AV** 11, **BL** 1, **ZK** 1. Every row is `Fuel = Gas`,
`PipelineType = transmission`. Routes are unusually complete for a first pass —
`RouteAccuracy` high 30 / medium 12 / low 6 / `no route` 4, and 48 of 52 rows are
`Mapped route (at any accuracy)`.

**Read the escalation memo before working the packet:**
`notes/escalation-2026-08-11-kazakhstan-system-level-values-on-strings.md`.

## What defines Kazakhstan: multi-string trunks and no line-wise register

Kazakhstan's gas network is mostly **multi-string trunk systems** — two or more parallel pipes
on one right-of-way, each carried as its own GEM row. The country's characteristic defect
follows directly: in at least six systems the row set repeats **one system-level figure on
every string** instead of each string's own value, so summing the rows double- or
triple-counts real pipe and throughput. It is the same shape India carries with 107.00 MMSCMD
on five HVJ rows.

The reason it is hard to fix is the second defining fact: **there is no public line-wise
register of Kazakh trunk gas pipelines** (surveyed 2026-08-11 — full writeup in
`docs/reference/source_roster.md`). The best line-wise source, the KazMunayGas Annual Report's
"Gas Transportation and Marketing" table, itemises only the **8 major systems** — i.e. it
publishes exactly the system-level aggregates that are the problem. So several rows will
legitimately end as `ResearcherNotes` explanations rather than value changes: the per-string
number does not exist publicly to be filled in.

## Gotchas

- **`adilet.zan.kz` serves an INCOMPLETE TLS certificate chain.** `url_verifier.py` retries
  with verification off and returns `ok=true` with `insecure_tls: True`. **That verdict means
  the page IS LIVE — never class an adilet URL `DEAD_LINK`.** Fetching by hand needs
  `curl -sk` with a browser User-Agent. This was *our* defect: before it was fixed on
  2026-08-11, the verifier reported a bare `request failed: SSLError` and hit 51 of 105 ref
  cells with **zero real 404s** (45 SSLError + 5 ConnectionError + 1 ReadTimeout). Confirmed
  genuine deaths, for contrast: `gurk.kz` and `kazazot.kz`, both 404.
- **The tracker's dominant Kazakh gas ref is a planning document whose evidence is in MAPS.**
  About half of all Kazakhstan gas `[ref]` cells cite Order of the Minister of Energy №350
  (29.09.2023, "General Gasification Scheme 2023–2030",
  `adilet.zan.kz/rus/docs/G23JVM00350`), usually with anchor `#z250`. That anchor lands in
  **Appendices 5–7, which are графические схемы — maps.** A full-text search that fails to
  find a length or capacity is therefore **not** evidence the ref fails. Same lesson as Egypt's
  GASCO grid map: a report cited for a pipeline is not "unsupported" until its maps have been
  read, not just its text. Say "text only, maps not read" in `ResearcherNotes` rather than
  asserting the ref is unsupported.
- **Two vintages of one publisher are ONE origin.** KMG's AR2019/AR2020 and AR2021 disagree
  materially on the same systems (Central Asia–Centre 5,306 → 4,149.2 km; Bukhara–Ural 2,382 →
  1,567.8; BGR-TBA + Gazli–Shymkent 2,462 → 1,903.4; Soyuz + Orenburg–Novopskov 1,147 → 805).
  That is a scope redefinition, not a correction. A row matching AR2020 is **dated, not
  corroborated**, and picking whichever vintage agrees with the sheet is not verification. KMG
  stopped publishing the table after AR2021 (the gas arm was carved out to Samruk-Kazyna in
  November 2021 and renamed QazaqGaz), so there is no 2022+ successor.
- **Identical drawn geometry is NOT evidence of duplication here.** Six systems assign one
  corridor geojson to every string (P0739/P5810, P2289/P5695, P2291/P5771 with P5770 a subset,
  P1124/P2299/P2300, P5927/P5928, P6830/P6831). For parallel strings on one right-of-way that
  is a defensible convention. The one shape geometry *would* decide is aggregate-vs-segment —
  one row's trace equal to the union of other rows that each have their own — and cluster A is
  the cautionary tale: it had that signature *and* matching arithmetic to 0.20 km, and it was
  still wrong (below). Segment traces cut from a parent produce the union identity for free, so
  **only sourcing decides duplication in this country.**
- **Research in Russian and Kazakh.** Ministry orders, QazaqGaz/Intergas material and regional
  news are overwhelmingly Russian-language; English coverage is thin and often derivative.
- **A number in an `ecoportal.kz` EIA is not a length until you read its column header.** Our
  own P5927 shard claimed the CS14–Aktobe EIA (project 113/2020-12-03-ОПЗ) itemises
  "158.573 km" per string, corroborating the sheet's 158.00 km. It does not: that figure sits
  under «**Объем стравленного газа, тыс.м3**» — gas *blown down*, thousand m³ — and recurs
  identically across different chainage segments, so it cannot be a length at all. Corrected
  at rest 2026-08-12; cluster F's two-strings refutation stands on independent evidence and
  never depended on it. These filings are engineering documents full of plausible three-decimal
  numbers in unfamiliar units; quote the header, not just the value.
- **What does not exist — do not re-hunt.** QazaqGaz's Integrated Annual Report 2024 lists 25
  Intergas lines by **name only** (good for existence and current operatorship, useless for
  specs); the KASE/KazTransGas 2023 bond prospectus carries aggregates only; Government
  decrees №463/2022 №488 are **forward-looking project tables**, not inventories of existing
  pipe; Order 182-Н/Қ (29.04.2025) is a single embedded JPEG map.

## Redundancy clusters (11 adjudicated, 7 refutations recorded)

Staged in `batches/kazakhstan-gas/staging/redundancy/`. Seven clusters **refute** a duplicate
hypothesis — recorded deliberately so the next sweep does not re-raise them.

| | Cluster | Verdict |
|---|---|---|
| **A** | Zhanaozen(Uzen)–Zhetybay–Aktau (P3948, P5776, P5777, P5783, P5789, P5784) | **REFUTED** — the ~149 km "P3948 is an aggregate" double count is withdrawn; P3948 is its own 720 mm / 149.1 km trunk. See below. |
| **B** | Central Asia–Center (P2291, P5770, P5771; P2292 the control) | 60.20 bcm/y restated on three strings; P2292 reads 5.00 |
| **C** | Central Asia–China A/B/C (P1124, P2299, P2300) | **REFUTED, and the sheet is corroborated** — 15+15+25 = 55 bcm/y is exactly Order №350 ¶44 |
| **D** | Bukhara–Ural I/II (P2289, P5695) | Two real strings; II's 2,382 km is KMG AR2020's whole-system figure |
| **E** | BTBA I/II (P0739, P5810) | **REFUTED** (parallel strings) — but 1,585 km sits on both |
| **F** | Bukhara–Ural CS14–Aktobe I/II (P5927, P5928) | **UNRESOLVED** — byte-identical rows |
| **G** | Almaty–Bayserke–Talgar I/II (P6830, P6831) | II is sourced (QazaqGaz IGO 2024: 62.4 km, 530 mm); I's 64.4 km is not |
| **H** | Almaty–Taldykorgan vs Taldykorgan–Usharal (P3964, P5901) | **REFUTED** — distinct consecutive links; but P3964's length goes to Update |
| **I** | Okarem–Beyneu vs Beyneu–Zhanaozen II (P2492, P5772) | **REFUTED** — distinct lines, but the second is filed under the first's name |
| **J** | Makat–North Caucasus + its loop (P1476, P3999) | **REFUTED** — a real loop; capacity possibly restated rather than incremental |
| **K** | Soyuz (P0761) | Filed under `PipelineNetworkGrouping = Brotherhood pipeline system` — Soyuz is not Brotherhood |

**Cluster A, refuted — read this before touching those rows.** It was first staged as a
~149 km aggregate-vs-segment **double count**, then reversed. Both halves of the apparent
proof failed: P3948's 137.85 km trace *is* the exact concatenation of P5777's 58.22 + P5783's
79.63, and the sheet's lengths *do* agree to 0.20 km (17.80 + 60.70 + 70.80 = 149.30 vs
149.10) — but two independent official sources name P3948 as its own physical line by name,
diameter **and** length. Intergas Central Asia's own environmental-permit filing
(`ecoportal.kz/Public/PubHearings/LoadFile/182922`, a PDF — read it with `pdftotext -layout`,
the verifier's substring check is a documented false negative there) states «Магистральный
газопровод высокого давления **Ду 720 мм** «Жанаозен - Жетыбай - Актау» протяженностью
**149,1 км**», and the Mangistau regional development plan item 116
(`adilet.zan.kz/rus/docs/P2100000784#z12`) enumerates «Жанаозен – Жетыбай – Актау» Ду 720 мм,
«КазГПЗ-КС «Жанаозен»» Ду 720 мм and «Жанаозен – Жетыбай – Актау» Ду 529/530 мм as one joint
capital-repair programme. So the rows map 1:1 onto real lines: **P3948** = the 720 mm trunk
(149.1 km), **P5776** = the KazGPZ–KS Zhanaozen feeder (720 mm, 17.8 km), **P5777 + P5783** =
the 529/530 mm trunk split at Zhetybay (131.50 km), **P5789** = the fourth thread under
construction. The 0.20 km near-identity is a coincidence of two parallel trunks plus a feeder;
the geometric identity is what cutting a parent's trace into segments produces for free.

Five things follow. **Do not fold P3948.** The ~280 km "missing parallel pipe" reading is
withdrawn too, but «3-х ниток» is grammatically ambiguous — it may enumerate the three named
lines (in which case the `SegmentName` numerals I / II / III / III are **correct**, since the
two rows numbered III are the two stretches of the third line, and the earlier "mislabelled
numerals" finding is withdrawn), or it may mean three threads of the 720 mm line alone, in
which case pipe is missing; **do not decide it on the numerals.** A *new* spec question opens:
why the 529/530 trunk measures 131.50 km against the 720 mm trunk's 149.10 km for nominally
the same endpoints. **529 mm is not a typo** — ecoportal's segment table puts 530 mm on
Zhanaozen–Zhetybay and 529 mm on Zhetybay–Aktau. And 4.54 bcm/y is still a *system* figure
belonging on the grouping, with the 3.60 bcm/y that kt.kz (2008) and Neft i Gaz (2019) give
still open (one shard reads it as the separate Zhetybay–Kuryk branch, P5784).

**P5789 (thread IV)** is real and independently sourced, and its byte-identical copy of P3948's
route file is **legitimate** under the shared-right-of-way convention above. What the copy does
not confer is a length or an accuracy grade of its own — `LengthMergedKm = 137.85` is the
corridor's length and `RouteAccuracy = medium` describes the drawing P3948 got.

## Reconciliation results (2026-08-11, both standalone)

Both recon workbooks are **separate review surfaces**; the packet's `recon_actions` is 0.

- **GulfPub** — 27 overlaps (84.4% overlap rate), 5 additions, 4 status conflicts. The >10%
  status-conflict gate is **crossed on paper (14.8%) and empty in fact**: the four collapse to
  two rows, P7819 (Karachaganak–Uralsk thread II) and P6712 (Beineu–Bozoy–Shymkent III
  expansion), both in-development *increments* on corridors GulfPub maps as operating lines —
  the segment-vs-network artifact, not a disagreement. Do not flip either status on it.
  Additions are below the 30-row gate: 1 `DISCOVERY_CANDIDATE` (Kairan–Zapadno Kashagan
  55.6 km) and 4 `NEAR_MISS`.
- **OSM** — 112 traces, 2 overlaps, 110 additions. The gate is crossed, but read the health
  line first: 3.6% named, 100% with geometry, 95.1% of GEM rows routed, **`escalations` empty**
  (no `MATCH_QUALITY` warning). The cause is granularity plus an unnamed extract: **55
  additions are explicitly `FRAGMENT_OF_EXISTING`** (6,084 km of trace inside routes GEM
  already draws, 11 over 100 km), and the 55 `DISCOVERY_CANDIDATE`s are mostly stubs (879 km
  total, median 0.9 km, only 5 ≥50 km). **Do NOT add a `geoarea_weight` override** — geoarea
  scores 0% because this extract carries no admin tags, not because the weights are wrong.
  Worth a look: the two 100+ km unmatched traces near Bukhara–Ural (198.7 km) and
  Karachaganak–Uralsk (146.2 km).
- **Triage caveat, engine-level:** on an unnamed trace whose guessed row has no drawn route,
  the old "Nearest was P####" note was computed on **length alone** — 18 traces spread from
  lon 51 to lon 78 all came back nearest to routeless P5776 (17.8 km), some 1,500 km from its
  corridor. `reconcile.py` was fixed 2026-08-11 to say so, and the Kazakhstan OSM run was
  rebuilt with the honest wording. Four older OSM runs in other countries still carry the
  misleading phrasing — logged in `docs/research_backlog.md` §2.

## Open items

- **P7819 is a three-way route-sync violation**: `RouteAccuracy = very low (straight
  line/schematic)` and `RouteType = Not mapped (but could be…)` while real geometry exists in
  the routes repo. Same defect as Egypt's P7338. The repair is mechanical
  (`apply_route_candidates.py --backfill-route-type`) but it writes the live sheet, so it needs
  explicit per-batch authorization and is **not** part of this staged packet.
- **P5776 is the one operating Kazakh gas row still at `no route` / `Not mapped`** — a §8
  route-creation candidate. Its geojson holds `geometry: null`, the honest placeholder.
- **Cluster F (P5927/P5928) is unresolved**: two byte-identical rows, with P5696 filed as
  "CS 14-Aktobe III" (construction).
- **P3945's `EndState/Province` reads `Osh`** — Osh is in Kyrgyzstan, on a line that runs
  inside Aktobe region. Attribution defect.
- **The Central Asia–China 1,833 km question**: repeated on all three strings, while KMG AR2021
  puts the system at 3,916 km and Order №350 gives the Kazakh portion as "до 1300 км". Neither
  matches — establish what 1,833 refers to.
- **Oil (41 rows) has not been swept.**
