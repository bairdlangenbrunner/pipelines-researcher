# Ukraine

47 gas rows (GGIT) and 20 oil rows (GOIT). Gas was swept in full on **2026-08-15** — the §9
composite: operating deep sweep (39 rows), in-development annual review (2), cancelled /
mothballed review (6), a redundancy-cluster adjudication (8 clusters / 23 rows), GulfPub and
OSM reconciliations, and the handoff packet. **Oil has not been swept.**

**Gas re-swept 2026-10-02 (lean pass + discovery), staged not applied. FOUR files to work.**
The new run is the only pending input: the August research legs (`annual`, `cancelled-review`,
`qc`, `redundancy`, `ref-sweep-operating`) and both August handoff packets moved to
`batches/ukraine-gas/archive/` on 2026-10-03. The open items below came from that pass and
still stand where the new sweep did not revisit them (the P7817 / P7818 route sync and the
shared P3381 / P3382 geojson were QC-leg findings). Ukraine gas is in the review app.

- `pipelines_batch_20261002_2032_ET_ukraine-gas_deepsweep.xlsx`. All 47 rows. 267 of 357
  uncited values now carry a ref (90 still unresolved), 39 of 105 fill records sourced, 47
  status reviews with no change (23 unclear, mostly transit trunks idle since 1 January 2025),
  33 validity concerns. Lean pass: 239 units deferred (fills_deferred 221,
  has_ref_access_blocked 15, has_ref_cleared_by_script 3), in
  `staging/deepsweep-20261002/deferred_units.json`. Length, capacity, diameter, start and
  operator blanks were owed, not deferred.
- `pipelines_batch_20261002_2038_ET_ukraine-gas_discovery.xlsx`. 26 seeds (23 GulfPub
  candidates + 3 Crimea leads from the Russia pass): 2 new rows, 24 monitor, 4 matched to
  existing rows. **Check new row "Dolyna-Uzhhorod-State Border II" (182 km, 1400 mm) against
  P0774 / P0768 before adding.** It rests only on the VTG table, and the rowspan trap below
  could make it the western tail of one of those systems. Most Crimea lines stay on monitor
  for want of a sourced length. The 62 GulfPub near-miss records were not seeded and still
  need hand adjudication.

Counts regenerate via
`python scripts/staged_summary.py --country Ukraine --commodity gas` — never hand-edit them.
The recons are standalone (not carried by any packet):

- `pipelines_batch_20260812_1409_ET_ukraine-gas_reconciliation-gulfpub.xlsx`
- `pipelines_batch_20260814_0120_ET_ukraine-gas_reconciliation-osm.xlsx` — the **re-run** after
  the Cyrillic name defect was fixed
  (`notes/escalation-2026-08-14-cyrillic-names-invisible-to-matcher.md`). **No finding moved**
  — the buckets are identical; 49 records got a corrected "closest GEM" attribution. Nothing
  in this note is retracted on its account.

Row profile: `operating` 39, `mothballed` 2, `retired` 2, `cancelled` 2, `construction` 1,
`proposed` 1. Researchers **ZK** 21, **NF** 17, **AV** 4, **HH** 2, **BL** 1, **DOB** 1,
**SZ** 1. Every row is `Fuel = Gas`; `PipelineType` is blank on **23 of 47**, which is its own
small gap. Routes are complete on paper — every row carries a `RouteAccuracy` (high 13,
medium 10, low 10, very low 14) and 45 of 47 are `Mapped route (at any accuracy)` — but see
the route caveat below, because "mapped" here often means a two-vertex straight line.

**Read the escalation memos before working the packet:**
`notes/escalation-2026-08-15-ukraine-citation-base.md` and
`notes/escalation-2026-08-15-ukraine-owner-percentages-and-attribution.md`.

## What defines Ukraine: an empty citation base, not empty facts

**34 of 1,034 `[ref]` cells are filled — 3.29%**, against 18.49% tracker-wide, and 17 of the
22 refs sitting on operating rows are dead links. `Length [ref]` and `Capacity [ref]` are each
filled on **exactly one** of the 47 rows — and length and capacity are precisely what this
pass found wrong, repeatedly and independently. The cells the country cannot cite are the
cells it gets wrong.

**So calibrate the opposite way from Kazakhstan.** In Kazakhstan an `UNRESOLVED` on a
per-string spec is frequently the *correct* outcome, because no line-wise public register
exists. In Ukraine a blank is usually evidence that **nobody has looked**: the operator
question — 22 of the 30 Leg-3 worklist rows — is squarely documented, and the sweep legs moved
a large block of cells off `UNRESOLVED` once they were actually worked. Read the packet's 126
`UNRESOLVED` ref units as *unfinished*, not as *unavailable*.

Ukraine is **2nd from the bottom** of the 52 country scopes with 20+ gas rows, not the worst
(Netherlands 3.03%, Bangladesh 3.30%, Indonesia 4.27%, Thailand 4.28%). It is the first of
that bottom-tier cohort to get a §9 pass; the other four are triage candidates.

## The one source that unlocks the Soviet-era trunks — and its trap

`vtg.com.ua/experience/main/gts.html` (ВНІПІтрансгаз, the Ukrainian gas-transmission design
institute) publishes an **"Основные объекты" table** with name, diameter, pressure, length,
number of strings and countries for every Soviet-era trunk crossing Ukraine. **The live URL is
a genuine 404; the Wayback capture serves the whole table and verifies 200:**
`https://web.archive.org/web/20220608014635/http://www.vtg.com.ua/experience/main/gts.html?lang=ru`.
It is the single source behind seven ref units in this packet (P0793, P1471, P1457, P5938).

**An earlier stage of this pass concluded from the 404 that figures resting on VTG were
"unsourced, not merely unverified". That is withdrawn** — repointing a dead ref to its
archived capture is standing practice, and it matters most in exactly this kind of scope.

**The trap: the table's name cells carry `rowspan`s.** Several lines sit under one system
heading whose sub-names are listed inside that single cell, mapping *in order* onto the data
rows beneath. Read a row without checking its grouping and you attribute another line's spec
to yours. That is what produced P0777's 1,112 km — 522 km is Шебелинка–Диканька–Київ and
590 km is Київ–Захід України, two **different** lines in one block, summed. The same structure
puts Ставрополь–Москва, Краснодарський край–Серпухов and Новопсков–Аксай–Моздок under one
"Північний Кавказ–Центр" heading with a single countries cell reading «Россия» — an aggregate
imprecision, **not** evidence against Novopskov being in Ukraine.

## Gotchas

- **`utg.ua` and `tsoua.com` return HTTP 403** (operator WAF). That is a **block, not a
  deletion** — never class them `DEAD_LINK`. Between them they hold the Ukrtransgaz
  construction chronology, which is the single source that settles clusters A and C; read it
  through Wayback.
- **`moldovatransgaz.md` fails TLS** (SSLError and ConnectionError, with and without
  verification). The **`mtg.md` mirror** serves the same content and verifies 200; it is what
  this pass staged.
- **`energybase.ru` returns HTTP 200 carrying an IP-block interstitial** («Доступ ограничен»,
  naming the caller's IP and ASN), so `url_verifier` reports a **false pass**. A 200 is not
  proof of content. Wayback also 403s on that host, so it is unreachable from here — treat it
  as blocked, not as a working ref.
- **Ukrainian routes are 2–5 vertex schematics.** A drawn span is a **lower bound** on
  corridor extent, never a measurement, and it must not be used to overwrite a sourced length.
  45 of 47 rows read `Mapped route (at any accuracy)` on that basis.
- **Geocoder false matches are the dominant route defect here, not bad lengths.** P0778's
  route flags all collapse into one: its start resolved to **Komárno, Slovakia** instead of
  Komarno, Lviv Oblast, and its end to the wrong **Drozdovychi** (Horodok Hromada, Lviv Raion,
  not the border one in Dobromyl Hromada, Sambir Raion). Corrected, the sheet's 80 km is
  vindicated. Reverse-geocode both endpoints before believing a length ratio.

## Open items

- **P7817 / P7818 — three-way sync violation (finding A).** Both have real geometry in the
  routes repo (104.2 km and 68.8 km) and a `RouteAccuracy` of `very low`, but `RouteType`
  still reads `Not mapped (but could be…)`. Repair with
  `python scripts/apply_route_candidates.py --backfill-route-type`, then verify with
  `python scripts/audit_route_sync.py`. These are the only two Ukrainian rows out of sync.
- **Cluster A (P0777 / P1480) — duplicate confirmed, length resolved to 399.90 km** on UTG's
  own chronology (183.6 km in 1970 + 216.3 km in 1972). Fold into one row. VTG independently
  gives Київ–Захід України as 590 km on one string; the operator's chronology is the better
  source, so record the 590 as a documented second-source tension rather than resolving it
  silently. The competing 367 + 506 = 873 km pair is **withdrawn on ATTRIBUTION, not on the
  host** — the figure was credited to a chronology page that contains neither number. (Wikipedia
  itself became citable 2026-08-27; if the uk.wikipedia article states the pair in its own voice
  it is a usable medium-tier `[ref]`, so this one is worth re-reading, but a misattributed number
  stays withdrawn either way.)
- **Cluster G / P5938 — 292.00 km is rejected by two independent sources** (VTG 374.1 / 394.2
  km; UTG 357.7 km in 1976 and 366.7 km in 1977), and 29.00 bcm/y is a system total restated
  on both P3484 and P5938. The duplicate was **refuted** — a refuted duplicate is not a clean
  row. VTG also evidences a **third string** GEM does not carry.
- **Shebelinka–Slovyansk (P3381 / P3382) share ONE geojson** that is not the named corridor —
  it runs Lozova Raion → Pokrovsk Raion, passing ~24 km south of Sloviansk, with Shebelynka
  itself ~64 km north of the path. The 3.08 and 3.99 length ratios measure one over-drawn
  trace twice. Re-draw or un-share before touching either length.
- **P1471 — `StartCountryOrArea` is wrong.** Novopskov is in **Luhansk Oblast, Ukraine**; the
  route endpoint is correct and the country columns are the defect. VTG corroborates
  internally via its «Оренбург–Новопсков» row.
- **P1457 — 516 km is the whole Rostov–Taganrog–Zhdanov system**, while the row is named
  Taganrog–Mariupol–Berdyansk and its geometry draws only that partial corridor. Do not
  shorten the length toward the drawn 169.7 km; extend the route or state the scope.
- **P1773 — Transgaz's own PDSNT 2021–2030 carries the Romanian counterpart as LIVE** with a
  2026 completion estimate, 146 km (raised from 130 in the 2020–2029 edition), €150m and TYNDP
  code TRA-N-596 — against GEM's `cancelled`. The plan footnotes that its schedule depends on
  the Ukrainian-side implementation, so the two readings can both be right. Route to Update;
  do not flip on this alone.
- **Occupied-territory operators are deliberately `UNRESOLVED`** on P1488, P7817 and P7818.
  GTSOU is the right answer for the rest of the scope and is affirmatively **wrong** for pipe
  being laid by the occupying power; naming an occupation authority as "the operator" without
  qualification would misrepresent the row. A documented contested-and-unresolved is the
  correct outcome, not a weak one.
- **Owner notation (`[100.%]` beside a second named owner) is a convention question only
  Baird can settle** — P0768, P0776 and P0761. Narrow and separate from it: P1485 is a 532 km
  wholly-Ukrainian operating line recorded as 100% Gazprom-owned, which the 2020 unbundling
  contradicts, and P1487 still names **Ukrtransgaz**, the pre-2020 entity.
- **GulfPub crossed all three gates** — 158 reference records, 73 overlaps (46.2%, a healthy
  run), 85 additions with **23 discovery candidates** that are named Ukrainian trunk lines at
  25–170 km, plus 15 status conflicts. Do not read the 20.5% conflict rate at face value: it
  collapses to five GEM rows, two of which (P1487, P0788) are one-to-many **attractor**
  matches rather than disagreements.
- **OSM's 1,003 additions cross the gate on volume alone and should not be read as a Discovery
  signal.** The health line is clean and `MATCH_QUALITY` correctly did not fire; the 0.1%
  overlap rate is a **scope** mismatch. 815 of 1,004 features are under 1 km and the named
  operator tags (Talnivske UEGG, Cherkasytransgaz, Kyivgaz) are district and city
  **distribution** utilities, which GGIT does not cover. The worth-a-look subset is small: the
  two Krasnodar Krai–Crimea traces, "Soyuz", and three unnamed 300–429 km traces.
- **Oil (20 rows) has not been swept.**

## Retracted by this pass

- **"111 GulfPub reference records"** — an earlier analysis in this pass ran before the
  multi-country reference filter was fixed
  (`notes/escalation-2026-08-12-multicountry-reference-filter-dropped-transit-trunks.md`).
  The true count is **158**; in a transit country the dropped records were exactly the
  cross-border trunks. Any conclusion drawn from the 111-record run is void.
- **"Ukraine is the worst-cited scope in the tracker"** — it is 2nd of 52.
- **"P0783 is an instance of the Owner over-attribution defect"** — withdrawn. On a genuinely
  transnational Russia+Ukraine row the unweighted pair "Gazprom PJSC; Gas Transmission System
  Operator of Ukraine" is the defensible convention, not a defect; that reading applies to 14
  of the 20 rows where Gazprom appears.
- **"Cluster A's 367 + 506 km"** — withdrawn, see above.
- **"VTG is a genuine 404, therefore its figures are unsourced"** — withdrawn; the archived
  capture serves the table.
