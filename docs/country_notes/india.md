# India

**75 gas rows** in scope (GGIT): 71 whose `CountriesOrAreas` is exactly `India`, plus 4
multi-country rows in which India is a participant (P0451 IPI, P0766 TAPI, P0928
India–Myanmar–Bangladesh, P2213 Gorakhpur–Rupandehi). Plus **26 oil rows (GOIT)**.

Gas got a **§9 full country pass on 2026-08-10** — operating deep sweep (35 rows),
in-development annual review (27, including 3 of the cross-border rows), cancelled review
(13, including P0451), redundancy adjudication (11 clusters / 34 rows), GulfPub and OSM
reconciliations, a **PNGRB register crosswalk**, and the handoff packet. **Oil has not
been swept.**

Staged, not applied. Counts regenerate via
`python scripts/staged_summary.py --country India --commodity gas`.

## Deliverables (2026-08-10) — FOUR files to work

The packet does **not** subsume the recons (`recon_actions: 0`), so the two reconciliation
workbooks are separate review surfaces, as in Libya, Iraq and Pakistan.

| File (`batches/india-gas/deliverables/`) | What it holds |
|---|---|
| `pipelines_batch_20260930_1455_ET_india-gas_handoff-actions.xlsx` (re-tiered 2026-09-30) | THE paste surface. 161 open decisions, 15 status changes, 469 backend paste units, 119 operators/owners units, 111 wiki updates, 209 open flags |
| `…_20260810_1851_ET_india-gas_handoff-evidence.xlsx` | Audit trail — 50 confirmed audits, 87 fill details, 672 ref details, 75 re-verified refs, 25 status confirms |
| `…_20260810_1851_ET_india-gas_reconciliation-gulfpub.xlsx` | 74 overlaps / 84 additions / 22 status conflicts — **both escalation gates crossed** |
| `…_20260810_1851_ET_india-gas_reconciliation-osm.xlsx` | 1 overlap / 60 additions (34 fragments, 25 discovery candidates) |

The superseded `20260810_1645_ET` recon pair is in `batches/india-gas/archive/`.
Twelve structural escalations are written up in
`batches/india-gas/staging/qc/escalations.json` and surface on the actions file's README.

## India is the inverse of Pakistan — read this first

Pakistan's problem was provenance: three quarters of its rows came from one bulk map load,
so per-row research had no text to grip. **India has the opposite shape.** The country is
actively maintained on the annual July cycle by a single researcher (73 of the rows), the
row set is coherent, and the names are real. What India lacks is **citations**: refs are
filled on roughly **9% of ref cells (149 of 1,650)**.

The gap is not evenly spread, and this is the useful part:

- **In-development rows are well cited.** PNGRB citations sit on **27 of 28**
  construction/proposed rows.
- **Operating rows are the weak flank.** **34 of 35** operating rows carry **no PNGRB ref
  at all**, even though (see below) PNGRB is demonstrably where their numbers came from.

So India's deficit is a *citation* deficit on *operating* rows, not a research deficit.
That is why the operating leg got the deep sweep and the register crosswalk.

## The PNGRB NGPL MIS register — India's unlock (2026-08-10)

> `https://pngrb.gov.in/data-bank/20260531-NGPL-MIS-Report.pdf` (month-end stamped;
> swap the date for other editions)

The regulator's monthly MIS report contains a **line-wise register of every authorised
common-carrier gas pipeline** in three sections — OPERATIONAL, PARTIALLY COMMISSIONED,
UNDER CONSTRUCTION — with authorised / operating / under-construction length, authorised
and design capacity in MMSCMD, authorisation date, target completion and states traversed.

Parse it with **`scripts/parse_pngrb_ngpl_mis.py`**, which extracts on the PDF's own ruling
lines (so merged cells stay honest) and **refuses to emit unless the parsed sections
reconcile to the report's printed TOTALs**. Crosswalk it with
**`scripts/crosswalk_pngrb_india.py`**, which holds the hand-adjudicated
`(section, sno) → PIDs` mapping and recomputes every delta from the two source files on
each run — so a re-scrape or a sheet re-sort cannot silently invalidate a quoted number.

Artifacts: `batches/india-gas/staging/register-crosswalk/` →
`pngrb_ngpl_mis.json` (37 authorisations, all three sections reconcile),
`register_crosswalk.json`, `staged_resolutions.json`.

It is a **better** register than Pakistan's SNGPL one on three axes: it is the
**regulator** (an origin independent of the GAIL/GSPL/IOCL company reports GEM cites), it
**carries dates**, and it reports operating *and* under-construction length on the same row.

Every one of the 71 GEM rows is now accounted for: **40 matched**, 14
`ABSENT_DEDICATED_OR_TIE_IN`, 16 `ABSENT_NOT_AUTHORISED` (proposed/shelved/cancelled),
1 `ABSENT_SECTION_OF_SYSTEM` (P0957). Nothing is left unexplained.

### What it settles, and the independence caveat

**Settles:** length (three ways), capacity in MMSCMD, authorisation date, target
completion, and the operating-vs-under-construction split.

**Does not settle:** **diameter** — there is no diameter column, and diameter is India's
biggest raw gap (only ~10 of the gas rows carry one). Nor **commissioning year**.

**The independence caveat matters.** GEM's India `Capacity` equals PNGRB's authorised
MMSCMD **at two decimals** on ~20 rows (P0917 20.00, P0912 35.00, P0933 16.00, P0920
85.00, P0921 36.00, P0929 23.00, …). PNGRB is therefore already the de facto **origin** of
that column. Citing it is the correct *primary* citation but is **not** an independent
second source for a value GEM took from it — do not let a PNGRB ref alone carry a row to
high tier on capacity. A company report that merely restates the PNGRB figure doesn't
change this: PNGRB + a company restatement of PNGRB's number is still **one** origin, not two.

## Gotchas

- **`CountriesOrAreas`, not `Countries`** — the GGIT gas column name. And read the CSV with
  `keep_default_na=False, na_values=[]`.
- **Authorisation date is NOT a commissioning year.** They can be a decade apart, and for
  pre-existing lines brought under common-carrier regulation the authorisation *postdates*
  construction by decades (Uran–Taloja: authorised 2014, commissioned 1983). This is the
  easiest wrong answer to produce on this country.
- **A live authorisation is not evidence of activity.** PNGRB keeps a pipeline listed until
  the authorisation is formally surrendered, so a row can sit in UNDER CONSTRUCTION for
  years with 0 km built against a target that lapsed in 2020 (P0921 Ennore–Nellore). GEM's
  `shelved` is the better reading there — a deliberate, documented divergence.
- **Conversely, absence from the register proves nothing.** It is **common-carrier only**;
  dedicated and tie-in lines are inside the grand totals but not itemised (1,601 km of
  residual). 14 GEM rows are correctly absent for this reason.
- **The Assam naming trap.** Register #1 "Assam Regional Network" (GAIL, 8 km) is **NOT**
  GEM's P0906 "Assam Regional Gas Network" — that row is AGCL's 105 km network and matches
  register #17 "Assam Natural Gas Pipeline" on owner, length and capacity. The *closer
  string match is the wrong answer*, so a name-similarity matcher gets this backwards.
- **`url_verifier` FAILs on the PNGRB PDF** with "missing expected value". That is the
  documented large-PDF false negative, not a bad ref — confirm with `pdftotext -layout` and
  record that in the ref note.
- **Anchor drift on India's most-cited ref URL:** the PNGRB page anchors `#bm6`/`#bm7` have
  become `#collapseNew`/`#collapse11`. That is **anchor drift, not a dead link** — the page
  is live and the ref must not be deleted.
- **GulfPub repeats system totals on segment features.** 15 of 158 India GulfPub features
  carry a recorded length more than twice their own geometry — the whole HVJPL/GREP/DVPL
  family shares one 4,657 km figure across 6 features, and MBPL, Dabhol–Bengaluru, BJSPL and
  a JHBDPL section do the same. A GulfPub-vs-GEM length disagreement on those lines is
  GulfPub's artifact, not GEM's error. (Most *other* repeated GulfPub lengths are just
  integer-mile rounding collisions — 6.44 km = 4 mi, 1.61 km = 1 mi — and are not a defect.)
- **OSM ref_id collisions:** 5 features collide on `provenance.oid_field` (merged-way keys),
  suffixed `#2..` at ingest. Cross-scrape identity for India OSM is unreliable until that
  field is fixed.
- **India's redundancy questions are regulatory, not bibliographic.** The register
  crosswalk adjudicates the 11 redundancy clusters by whether authorisation number /
  sponsor / date hold constant across register editions while only the NAME changes —
  that's dispositive, and it confirmed one cluster (P0938/P3602, finding 5 above) and
  refuted 5 of the 11. Name-similarity alone gets this backwards (see the Assam trap).

## Regulators / official data

- **PNGRB** (`pngrb.gov.in`) — the register above, plus public notices, tariff orders and
  bid-round documents, which *do* announce withdrawals and re-bids explicitly.
- **MoPNG** annual report; **PPAC** (`ppac.gov.in`) for throughput.
- **Parliament Q&A** (Lok Sabha / Rajya Sabha) — unusually good in India for "what actually
  happened to project X".

## Key operators / owners

GAIL (the dominant transmission owner), GSPL / Gujarat State Petronet, GIGL, GITL, IGGL
(Indradhanush Gas Grid, the North-East grid), IOCL, ONGC, Petronet LNG, Pipeline
Infrastructure Ltd (PIL — the register's "PIL", held by GEM's recorded owner India
Infrastructure Trust), Reliance Gas Pipelines Ltd (RGPL), H-Energy, DFPCL, AGCL, DNP Ltd.

## Structural findings from the register crosswalk

Ordered as a reviewer should meet them. All staged, none applied.

1. **P0907 Barauni–Guwahati is a SECTION of P0929 JHBDPL — a double-count, and its owner is
   wrong.** The authorisation name itself embeds it
   ("Jagdishpur-Haldia-Bokaro Dhamra-Paradip-Barauni-Guwahati"), and the register carries
   ONE asset of 3,546 km. India's gas total is overstated by ~718 km. Independently
   corroborated by Indian Infrastructure, World Pipelines and Swarajya, all of which
   describe it as a section/extension. **Separate second defect:** `Owner1` reads Assam Gas
   Co Ltd, but GAIL built, owns and operates it — and that correction stands even if the
   duplicate ruling is rejected. *(The step-1 subagent reached the same owner conclusion
   independently.)*
2. **P2216 Mumbai–Nagpur–Jharsuguda is stale at `construction`.** The regulator files it
   under OPERATIONAL with 1,707 of 1,755 km operating. First gas 2025; full completion
   targeted Jun-2026 having slipped from Dec-2025 and Mar-2026. Corroborated independently
   of PNGRB (Indian Infrastructure Nov-2025 testing completion; FPJ Mar-2026 board report).
   Keep the 15.05.2020 authorisation date distinct from commissioning.
3. **P0934 / P2746 KKBMPL — GEM understates commissioned length by ~600 km, on two
   independent sources.** The pair sums to 1,104 km, matching the authorisation *exactly*,
   so the extent is right and only the commissioned boundary is wrong: register says 675
   operating / 429 under construction, GEM says 44 / 1,060. **Second origin:** the
   2026-08-10 OSM extract independently maps four "KKBMPL GAIL Pipeline" traces totalling
   **306 km, all tagged `lifecycle=operating`** — seven times GEM's 44 km, and a floor
   rather than an estimate since OSM coverage is partial.
4. **The HVJ system's capacity is repeated across five rows.** P0925, P0919, P3298, P3297
   and P3299 all carry `Capacity = 107.00 MMSCMD`, which is one earlier edition's *system*
   total, not five pipelines' capacity — summing India by row overstates this system
   roughly five-fold. The register reports the whole thing as ONE authorisation (snos 3+4
   merged, now 111.3 MMSCMD), so it cannot settle a per-segment apportionment; this is a
   flag for a human, not a proposed value. GEM's five segment lengths also sum to 5,277 km
   (5,944 with P0957) against a 6,169 km authorisation, so the decomposition does not cover
   the system.
5. **Four phase pairs, three of which need reconciling.** A GEM operating + construction row
   pair on one pipeline name is a **legitimate phased split, not a duplicate** — the
   regulator's own "partially commissioned" category is the same concept.
   - **P0938 / P3602 Mallavaram** — matches the register on **both** halves (365 / 1,517).
     This is the reference case; a redundancy pass that flags this shape is wrong.
   - **P0941 / P5411 Mehsana–Bhatinda** — total within 3 km, split differs (register
     1,339/604 vs GEM 1,177/763).
   - **P0934 / P2746 KKBMPL** — see finding 3.
   - **P5533 / P3913 Bhatinda–Gurdaspur** — **the one pair whose total does not close**:
     102 + 290 = 392 km against a 261 km authorisation, an excess of 131 km, even though
     both rows carry the register's 42.4 MMSCMD exactly. The register's split is 101/160, so
     Phase I is right and **Phase II's 290 km looks like the defect**.
6. **Four rows carried as wholly unbuilt that the register shows partly operating** —
   P0922 Ennore–Tuticorin (1,121 of 1,431 km), P0915 Dabhol–Bangalore (232 km still under
   construction against a **Feb-2013** target, the longest-lapsed in the register),
   P1309 North East grid (392 of 1,863), P0954 Srikakulam–Angul (470 of 690). Each needs
   either a status move or the phase split GEM already uses elsewhere.
7. **Stale capacities.** Several rows sit on an earlier edition's authorised figure —
   P0927 (31.00 vs 44.8), P2212 (~19.89 vs 22.5), P5413 (2.0 vs 3.1), P1309 (4.75 vs 5.8),
   P0941/P5411 (80.11 vs 83.1), the HVJ family (107.00 vs 111.3). Because GEM matches PNGRB
   at two decimals wherever they agree, the likely story is staleness, not a unit error — so
   the fix is a re-read of the current register, not new research. **Do not apply blind.**
8. **P0921 Ennore–Nellore — deliberate divergence, documented.** Register lists it as
   authorised/under construction with 0 km built against an Apr-2020 target; GEM's
   `shelved` is the better description. Length and capacity agree exactly. No change.
9. **P0906 — add "Assam Natural Gas Pipeline" to `OtherEnglishNames`.** Do not rename, and
   see the Assam naming trap above.

## Discovery candidates — authorised pipelines with no GEM row

Five, of which **three are verified `RECOMMEND_ADD`**:

- **Kochi–Kanyakumari–Thoothukudi** (IOCL, 425 km, 6.84 MMSCMD, authorised 09.03.2026,
  target Mar-2029) — the newest authorisation in the register. PNGRB ran a Jan-2024 public
  consultation and a suo-motu bid round (bids opened 17 Oct 2024) that IOCL won. Runs
  **south** from Kochi via Kanyakumari to Thoothukudi, tying into IOCL's
  Ennore–Thoothukudi line, so it is **not** an extension of KKBMPL (which runs north).
- **Uran–Taloja** (DFPCL, 42 km, 10-inch, 0.7 MMSCMD) — authorisation letter
  Infra/PL/Exis/17/UTPL/DFPCL/01/14 (21.10.2014) states the line was **commissioned in
  1983**; the 2014 date is a common-carrier formalisation. DFPCL's own investor material
  independently describes "its own 43 km gas pipeline from … Uran to its plant at Taloja".
- **Uran–Trombay** (ONGC, 24 km, 20-inch, 6.0 MMSCMD) — current line commissioned
  30.05.2008 replacing a 1978-79 18-inch original (PNGRB tariff order TO/2022-23/06, ONGC
  Schedule-1 filing, APTEL Appeal 110/2020). **Distinct from** GEM's P0926 (Heera–Uran) and
  P0944 (Mumbai–Uran), which are the offshore *feeders* — those run field-to-Uran, these run
  Uran-to-shore-industry. GEM has neither Uran line.

Two recorded but **not** recommended (too small / unverified): the GAIL 8 km "Assam Regional
Network" (register #1 — see the naming trap) and Dukli–Maharajganj (GAIL, 5 km authorised,
**0 km operating**).

## Reconciliation results (2026-08-10; GulfPub re-run 2026-08-12)

Both **standalone** — the handoff packet does **not** subsume them.

> **GulfPub RE-RUN 2026-08-12 — work
> `pipelines_batch_20260812_1359_ET_india-gas_reconciliation-gulfpub.xlsx`; the
> `20260810_1851` workbook and its staging dir are in `archive/`.** The reference-side
> country filter compared GulfPub's country string with `==`, dropping every multi-country
> record. Engine defect, fixed same day:
> `notes/escalation-2026-08-12-multicountry-reference-filter-dropped-transit-trunks.md`.
> **India is the least affected country in the tracker — 158 → 159 refs, and *no* `gem_only`
> finding was falsified.** New totals: **75 overlaps / 84 additions / 40 gem_only / 24 status
> conflicts** (was 74 / 84 / 40 / 22). Both escalation gates stay crossed and every
> conclusion below stands; conflicts are now 24 on 75 matched rows (32%). OSM is unaffected.

- **GulfPub** (158 India gas records): 74 overlaps, **84 additions**, 40 GEM-only,
  **22 status conflicts**, 22 ambiguous. Health line clean — 100% refs named, 100% with
  geometry, GEM routes 98.7%. Dispositions: NEAR_MISS 56, DISCOVERY_CANDIDATE 23,
  FRAGMENT_OF_EXISTING 5. **Two escalation thresholds are crossed**: >30 additions in one
  country, and 22 conflicts on 74 matched rows (30%) is >10%.
- **OSM** (61 features from 98 ways, ODbL — 44% named, 2,721 km): 1 overlap, 60 additions,
  FRAGMENT_OF_EXISTING 34, DISCOVERY_CANDIDATE 25. **The thin overlap count is not a
  matcher defect and the threshold was not lowered.** India's OSM features are *fragments*
  of long GEM lines (median 7.8 km), so a 97 km trace of a 1,104 km pipeline scores a
  perfect 1.00 on name but 0.18 IoU → composite 0.34-0.44 against a 0.45 threshold. The
  `FRAGMENT_OF_EXISTING` bucket is the engine giving the right answer by a different route.
  Four GEM rows get location corroboration from perfectly-name-matched fragments: **P0934**
  KKBMPL (4 traces, 306 km — see finding 3), **P0925** HVJ (106 km), **P0915**
  Dabhol–Bangalore (4 traces, 70 km), **P0929** JHBDPL (66 km).
- India is the **healthiest OSM extract in the registry so far** (44% named vs Pakistan's 0%
  and Libya's 14%), so `sources/osm/manifest.yml` deliberately carries **no
  `geoarea_weight` override** for `gas_in` — both the name and geometry axes are live.

## Open items

- **Oil is unswept** — 26 GOIT rows, never researched. Its shape is **healthier than gas**,
  so do not assume the gas findings transfer: ref density is **35.5%** (194 of 546 ref cells)
  against gas's 9%, **all 26 rows carry a mapped route** (18 `medium`, 5 `low`, 3 `very low`),
  and only one operating row lacks a `StartYear1`. All 26 are one researcher's (`IM`).
  Status: 20 operating, 3 construction, 1 proposed, 1 cancelled, 1 retired. Fuel splits
  13 Oil / 11 LPG / 2 Oil products — the **LPG cohort is the distinctive part** (11 rows, all
  IOCL/GAIL/HPCL product lines), and **PNGRB's NGPL MIS register does not cover it** (natural
  gas only), so oil needs a different register: PNGRB's petroleum-products-pipeline
  authorisations and the MoPNG/PPAC product-pipeline tables. A §3 sweep is the right next
  step, not a §9 full pass.
- **`Operator` is blank on 74 of 75 gas rows.** This is a genuine India gap, **not** the
  tracker norm: the GGIT gas tab records an operator on 794 of 4,356 rows (18.2%), and
  overall 1,450 of 6,459 (22.4%). *(Corrects an earlier reading of this pass that put the
  tracker-wide figure at ~1% — that number came from the `Operator [ref]` column, not
  `Operator`.)* It is **one question per COMPANY, not per row** — GAIL, GSPL, IGGL, IOCL
  and PIL account for most of it. 119 operators/owners paste units are staged against it.
- **Diameter** is the largest raw gap and PNGRB cannot fill it: only ~10 of 71 gas rows
  carry one. Company annual reports, PNGRB tariff orders and bid documents are where they
  appear. P0906's "350, 400, 500, 800" are **millimetres**, not inches — confirm the
  intended figure from a source rather than converting blind.
- **166 ref units remain `UNRESOLVED` and 36 are `DEAD_LINK`** across the five staging
  dirs, against 470 `REFS_ADDED` and 75 `REVERIFIED`. Unlike Pakistan, an `UNRESOLVED`
  here is a weak result — the ref-gap pass moved the operating leg from 116 to 251
  `REFS_ADDED` on a second attempt, so the remainder is worth another look, not closure.
- **Two `length_ratio` rows are route-side defects, not length defects** — P5411
  Mehsana–Bhatinda draws 2,317 km against a stated 763 km (3.04×), exceeding both phases
  combined (1,940 km); and P3334's 599 km drawn route is close to the 705 km *stated*
  length of P0913 (Contai–Paradip–Dattapulia), i.e. the 115 km feeder appears to have been
  drawn with its neighbour's extent.
- **`ShelvedCancelledType` is blank on 8 of the 13 cancelled rows** (P0931, P0932, P0935,
  P2214, P2215, P2748, P2752, P3334) — the cancelled review targets this.
- **Three corridor clusters** deserve duplicate scepticism: Langtala (P0936 / P2215 / P2748,
  three rows on one origin point), West Bengal (P0913 / P3334 / P0935 / P2214 — and note
  P6562 Kanai Chhata–Panitar is a *live construction* row that may be P2214's successor),
  and Andhra (P0932 / P3342 / P2752).
- **P0451 Iran–Pakistan–India** — be precise about which *leg* is cancelled; India's
  withdrawal is separable from the Iran–Pakistan segment's continued life.
- **84 GulfPub additions and 22 status conflicts** are an untriaged review surface in the
  standalone workbook.
