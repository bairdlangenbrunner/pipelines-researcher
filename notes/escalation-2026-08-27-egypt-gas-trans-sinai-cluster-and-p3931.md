# Egypt gas — the Trans-Sinai cluster, a recovered "dead" source, and a URL in a value column

Three findings, all from opening documents that were sitting unread in this batch's own
inputs. Two of the three **retract earlier claims of ours**, so read the retractions first.

---

## 1. RETRACTION — the GASCO grid-expansion PDF is NOT deleted. Its URL is mistyped.

This batch's route pass recorded, of P8055:

> DEAD SOURCE: all seven of its live [ref] cells … cite ONE GASCO PDF … which is now a
> CONFIRMED HTTP 404, not a block — re-verified directly through url_verifier.py, so this is
> a genuine deletion.

**Withdrawn.** The document is live, and I have read it.

| form | result |
|---|---|
| what the sheet cites (`…/National-Natural-Gas-Grid-Expansion-Projects.pdf`) | **404**, 196 bytes |
| what the route pass actually tested (same, but bare host `gasco.com.eg`) | `ConnectionError` — bare host has **no A record**; only `www.` resolves |
| **the real file** (`…/National%20Natural%20Gas%20Grid%20Expansion%20Projects.pdf`) | **200, 77,826 bytes, application/pdf** |

The filename uses **spaces, not hyphens**. Something converted one to the other on the way into
the sheet; Wayback's host-wide CDX listing for `gasco.com.eg` PDFs shows only the space form
(capture `20260222074837`), so the hyphenated URL probably never existed.

The 404 is honest, not soft — a nonsense sibling under the same directory returns the identical
196-byte body, which is the test. The live form passes `url_verifier` at `ok=True, status=200`
with `insecure_tls: True` (incomplete chain — the page IS live; same signature as
`adilet.zan.kz`).

**Two lessons, and the second is the one that generalises.** The route pass reported a
`ConnectionError` as a "CONFIRMED HTTP 404" — but a connection error is precisely the failure
class the standing rule says is *not* a deletion, so the rule would have caught this if the
failure class had been read rather than summarised. And **a 404 on one spelling of a URL is not
evidence about the document**: before calling a source deleted, vary the encoding (spaces vs
hyphens vs `%20`), the host (`www.` vs bare), and check the archive's host-wide file listing —
the capture here was invisible to an exact-URL CDX query (`[]`) and turned up immediately in a
`matchType=domain` listing.

### What the document is

**"National Natural Gas Grid Expansion Projects"**, GASCO, 1 page, generated from Excel
18 Dec 2024. English, machine-readable, no visual read needed. It is a **project register**:
per project — length (km), diameter (in), governorate, cost in **both EGP and USD millions**,
status, and completion date. That is a far better source than the news pages this project
usually works from, and it is GASCO's own.

| project | km | in | governorate | EGP M | USD M | status | completion |
|---|---|---|---|---|---|---|---|
| Gas import pipeline from SUMED dock, Ain El Sokhna | 6.1 | 32 | Suez | 242 | 20 | Engineering / Procurement / Construction | April 2025 |
| El Solimanya / North Giza | 25 | 42 | Giza | 391 | 12 | Procurement / Construction | September 2025 |
| Gas import pipeline from Sonker dock, Ain El Sokhna | 17 | 36 | Suez | 777 | 16 | Under Study | — |
| Gas import pipeline from UGDC dock, Damietta | 2.3 | 36 | Damietta | 176 | 13 | Under Study | — |
| **Duplication of the Trans-Sinai pipeline** | **28** | **36** | **Sinai** | **631** | **13** | Under Study | — |
| *(compressors)* Dahshour units 5 & 6 | 18 MMSCMD | — | Giza | 2,548.72 | 150.45 | Testing and operation | March 2025 |

Registered in `docs/reference/source_roster.md`.

### The 8 cells that cite the 404 form

**P8055** — `Status`, `Fuel`, `PipelineType`, `Length`, `Diameter`, `Location`,
`ProjectLevelCost` `[ref]` — and **P6685** `ProjectLevelCost [ref]`. All eight are the same
URL. Nothing needs re-sourcing: the values they support are all *in* the recovered document.
The repair is a **URL correction**, mechanical and now pre-verified — but it is a live-sheet
write and is **not authorized**, so it is staged and flagged, not made.

---

## 2. P8055 and P8009 — the duplicate question, now decidable

Five rows carry the Trans-Sinai name across two transliterations. "Abr Sinai" **is** عبر سيناء,
which **is** "Trans-Sinai" — so name-matching alone can never separate these rows, and GASCO's
own English materials use both spellings (the EIB's 2007 EIA is titled *"GASCO Abr Sinai Onshore
Gas Pipeline"*; this register says *"Trans-Sinai"*).

| PID | row | name / segment | status | km | in | cost | route |
|---|---|---|---|---|---|---|---|
| P8044 | 4304 | Abr Sinai **I** / Bair El Abd–Arish | operating (2019) | 75.00 | 36 | — | 77.2 km, `medium`, ENTSOG |
| P8013 | 4273 | Trans Sinai **I** | operating | 75.00 | 12 | — | 56.9 km, `very low`, ours |
| P8008 | 4268 | Abr Sinai **II** / Pipeline 1 | operating (2024) | 15.50 | 36 | — | none |
| P8009 | 4269 | Abr Sinai **II** / Pipeline 2 | **construction** | 27.00 | 36 | — | none |
| P8055 | 4315 | Trans-Sinai **II** | **proposed** | 28.00 | 36 | **13 M USD** | none |

**P8055 was entered from the recovered register, and matches it to the cell:** 28 km, 36",
Sinai, and a `ProjectLevelCost` of 13,000,000 USD against the register's "13" USD million. That
is not a resemblance, it is the same row of the same table.

**GASCO's register lists exactly ONE Trans-Sinai duplication.** Not two, not a phased pair. So
P8009 (27.00 km, 36", the same duplication as described by petro-mag.org) and P8055 (28.00 km,
36") are **very likely one project carried twice**, entered by the same researcher from two
different documents — the 27-vs-28 gap being the magazine's own internal inconsistency (Nov 2025
says 27, Dec 2024 says 28), already flagged in a prior pass.

**If they are folded, P8009's status should survive, not P8055's.** P8055's `proposed` faithfully
reflects its source — the register says "Under Study" — but that source is **December 2024**.
P8009's `construction` comes from petro-mag.org in **November 2025**, and is independently
supported twice over: the Ministry of Petroleum's grid document lists **خط ازدواج عبر سيناء**
(the Trans-Sinai *duplication*) among lines **under construction**, and an Akhbar El-Yom report
of 7 April 2026 has GASCO negotiating farmer compensation for "the second phase" of the
duplication with Arish's Agricultural Administration — i.e. land acquisition was active in 2026.
The correct reading is one project that moved Under Study → construction between Dec 2024 and
late 2025, and GEM is carrying both snapshots as separate rows.

**Recommended (a researcher adjudication, NOT an auto-fold):** fold P8055 into P8009, carrying
P8055's sourced cost (631 M EGP / 13 M USD) and the **corrected** GASCO URL onto the survivor.
**P8008 does not fold** — at 15.5 km it matches neither the register's 28 km nor P8009, and it
has already flowed gas (8 Jun 2024).

### P8013 vs P8044 — checked, NOT duplicates

Recorded so the question is not re-opened. The identical 75.00 km lengths are a coincidence.
P8044 is North Sinai (Bair El Abd 33.06/31.00 → Arish 33.84/31.10, 36", ENTSOG-traced,
`medium`, cited to the EGAS Annual Report 2018). P8013 is the **Gulf of Suez**, ~250 km south
(33.17/28.90 → 33.06/28.39, 12"), and its own columns say `EndState/Province = Gulf of Suez`,
`EndPrefecture/District = Ras Baker Transmissin Station`.

Two caveats on P8013, both ours: its route is **our own `very low` straight-line guess**
(`RouteCreator CB`, RouteNotes "route guessed from endpoints"), so the 56.9 km drawn span is a
lower bound and is not evidence about the row; and its `Status [ref]` is
`egyptoil-gas.com/?s=Gas+Pipelines+Egypt`, rejected by this batch's non-citation screen, so its
`operating` is now **unsourced**.

---

## 3. Rows the register speaks to that are outside this batch's research scope

The research legs deliberately exclude the 88 Egypt gas rows carrying prior staged, unapplied
research, so two workbooks cannot stage contradictory records onto the same cells. These are
logged here so the corroboration is not lost when those rows are next worked.

- **P8005 Sumed Port Gas Pipeline** — sheet 6.10 km / 32". Register: **6.1 km / 32" / Suez /
  242 M EGP / 20 M USD / EPC / April 2025**. Exact match on both specs; the register adds a
  governorate, two costs and a completion date the row does not carry. This row is also a
  `ROUTE_PARTIAL` in this batch, whose note settles the landfall question four prior passes
  left open.
- **P6685 Solaimaneyah–North Giza** — sheet 20.00 km / 42" / 12,000,000 USD. Register:
  **25 km / 42" / Giza / 391 M EGP / 12 M USD / Procurement-Construction / September 2025**.
  Diameter and cost match exactly; **the length does not** (20 vs 25). Since the row's own cost
  came from this document, its length disagrees with its own source — a real discrepancy, not a
  competing-source problem. The Ministry grid document separately confirms the line under
  construction.
- **P8006 / P8007 Sonker (Phase 1 / Phase 2)** — sheet 9.00 + 7.00 = **16.00 km**, both 36".
  Register: **one** Sonker line, **17 km / 36"**, no phase split. So GEM splits into two rows
  what GASCO carries as one project, and the halves sum 1 km short. The status divergence is
  *not* a conflict — the register is Dec 2024 and says "Under Study", GEM has P8006 operating
  from 2025, which is chronologically consistent. The phase split and the missing kilometre are
  the open items.
- **"Gas import pipeline from UGDC dock in Damietta", 2.3 km / 36" / Damietta** — no obvious GEM
  counterpart. **Not P8035**, which is the Port Said UGDC–El Tina line. A discovery candidate,
  noted only; Discovery (§4) was not in this batch's scope.
- **P3931 Amriya–El Alamein** — see below.

---

## 4. P3931 — a URL in a value column, and the empty ref cell it belongs in

**Row 1941.** Its **`FuelSource` cell (BQ1941) contains a URL** — the Ministry of Petroleum's
2020 national-grid PDF — while **`FuelSource [ref]` (BR1941) is empty** and **`Status [ref]`
(I1941) is empty**. A link in a value column is a schema violation on its face; here it is also
a *misfiled* link, because the document it points at is a genuine and sufficient source for the
row's `Status = operating`: it names **خط غاز العامرية/العلمين** among lines completed and
commissioned FY2014/15 → Jan 2023, consistent with the row's `StartYear1 = 2022` and
`ConstructionYear = 2021`.

**Routes to Update, not to a mechanical write.** Moving the URL into a `[ref]` cell is
mechanical; deciding what `FuelSource` should actually *say* is research, and blanking BQ1941
without answering that loses the only value there. Leaving it also strands a `[ref]`-less value,
and moving it alone would create an orphan `[ref]` — both forbidden. Recommended: cite the
Ministry PDF at `Status [ref]` (I1941), then resolve `FuelSource` on its own evidence. The rest
of P3931 is well cited (Fuel, PipelineType, Start, Length all cite Ministry news page
`Mop_28122022_01.aspx`), so this is one misfiled cell on an otherwise sound row.

---

## Method note

Both retractions in this file came from the same place: **a source that was in our own inputs and
had not been opened.** The Ministry grid PDF sat unread in this batch's harvested citation pool;
the GASCO register was declared deleted without varying the URL. Neither produced an error —
each produced a plausible, confident, wrong statement. Cf.
`notes/escalation-2026-08-27-ref-screen-defects.md`, whose four defects share the shape: *"the
only thing that caught them was reconciling counts that should have matched and didn't."*
