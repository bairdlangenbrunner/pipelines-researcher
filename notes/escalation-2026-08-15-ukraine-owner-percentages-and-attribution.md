# Ukraine gas — `Owner` percentages that cannot be right, and non-Ukrainian sole owners on Ukrainian rows

**Raised:** 2026-08-15, during the Ukraine gas §9 full pass (redundancy leg + handoff QC).
**Scope:** GGIT gas, the 47 rows whose `CountriesOrAreas` / `StartCountryOrArea` /
`EndCountryOrArea` include Ukraine, read off `data/GGIT_gas_snapshot_20260812.csv`.
**Status:** read-and-flag. Nothing staged as a value change; two of the three classes
below need a *convention* decision from Baird before any row can be corrected.

---

## Read the narrow version, not the broad one

The redundancy leg's first pass reported this as "Gazprom attributed ownership of
Ukrainian pipe". A full-tab count run afterwards shows that framing is too broad and
**one of its cited instances (P0783) is withdrawn.**

Gazprom appears in `Owner` on **20 of the 47 rows**. For **14** of them the cell reads
some unweighted form of `Gazprom PJSC; Gas Transmission System Operator of Ukraine` on a
row whose `CountriesOrAreas` is genuinely `Russia, Ukraine` (or `Russia, Belarus,
Ukraine`). Naming both national owners on a cross-border trunk, with no percentages, is
the **defensible convention** — it is what the column has to do when one GEM row spans
two jurisdictions with different owners on each side. Those 14 are not a finding, and
P0783 (`Gazprom PJSC; Gas Transmission System Operator of Ukraine`, `Russia, Ukraine`) is
one of them.

What survives are two narrow classes, plus one staleness marker.

---

## Class 1 — `[100.%]` recorded alongside a second named owner (3 rows)

Arithmetically impossible as written, and **not a Gazprom problem** — the third instance
runs the other way:

| ProjectID | `CountriesOrAreas` | `Owner` |
|---|---|---|
| P0768 | Russia, Ukraine | `Gazprom PJSC [100.%]; Gas Transmission System Operator of Ukraine` |
| P0776 | Russia, Ukraine | `Gazprom PJSC [100.%]; Gas Transmission System Operator of Ukraine` |
| P0761 | Russia, Ukraine, Kazakhstan | `Gas Transmission System Operator of Ukraine [100.%]; Gazprom PJSC; QazaqGaz` |

Because P0761 puts the **Ukrainian** operator at 100% beside two foreign co-owners, this
cannot be diagnosed as a pro-Gazprom bias. It is a **notation question**, and it is the
decision this memo actually needs:

- If `[100.%]` is meant as *"100% of the section lying in that party's own country"*,
  then all three cells are defensible and the convention should be written into
  `docs/reference/gem_schema.md` — because as rendered it reads as a share of the whole
  line, and every downstream consumer will read it that way.
- If `[100.%]` is meant as a share of the whole pipeline, **all three cells are wrong**
  and the percentages should come off (leaving the unweighted multi-owner form the other
  14 rows use).

Not fixable by research — a researcher cannot source which of the two GEM means.

## Class 2 — a sole non-Ukrainian owner on a row that lists Ukraine (6 rows)

| ProjectID | `CountriesOrAreas` | `Owner` |
|---|---|---|
| **P1485** | **Ukraine** | `Gazprom PJSC [100.%]` |
| P0793 | Ukraine, Russia | `Gazprom PJSC [100.%]` |
| P1471 | Russia, Ukraine | `Gazprom PJSC [100.%]` |
| P2387 | Russia, Ukraine | `Gazprom PJSC [100.%]` |
| P0791 | Ukraine, Kazakhstan, Russia | `Gazprom PJSC; QazaqGaz` |
| P5935 | Moldova, Ukraine | `Moldovatransgaz [100.%]` |

**P1485 is the unambiguous one and the row to fix first.** Its `CountriesOrAreas` is
`Ukraine` **alone** — a wholly Ukrainian pipeline (Kremenchuk–Anan'iv–Bohorodchany,
532.00 km, `operating`) recorded as 100% owned by Gazprom PJSC. After the unbundling that
took effect 1 January 2020 the Ukrainian transmission system sits with Gas TSO of Ukraine
LLC; there is no reading on which Gazprom owns all of a line that never leaves Ukraine.
The redundancy leg staged P1485 with an `attribution` concern of its own (cluster C).

The other five are weaker and each needs its own judgement rather than a blanket fix: on
a two-country row a sole foreign owner may be shorthand for "the section we describe is
the Russian one", in which case the row's *scope*, not its owner, is what is
mis-stated — which is the same question class 1 raises. P5935 is included because it is
the same shape with a different party (Moldovatransgaz at 100% on a Moldova+Ukraine row),
which again argues this is a convention gap rather than a bias.

## Class 3 — one stale entity name (1 row)

P1487 (Poland-Ukraine Interconnector, `cancelled`) still names **Ukrtransgaz**, the
pre-2020 entity, rather than GTSOU. For a project cancelled before or around the
unbundling this may be historically correct as-of; flagging rather than fixing.

---

## What is staged, and what is memo-only

- **Staged as a row-level `attribution` concern:** P1485 (cluster C), P0775 and P0776
  (cluster H). Those three reach the researcher through the actions workbook.
- **Memo-only — no row action exists for them:** the class-1 notation question (P0768,
  P0776, P0761), the four remaining class-2 rows (P0793, P1471, P2387, P0791, P5935), and
  P1487's stale entity name. If the class-1 convention is settled one way, class 2
  largely resolves with it.

## Carry-forward rule

Before reporting "party X is attributed ownership it cannot have", **count the whole tab
first**. On transnational rows a foreign co-owner is the norm, not the exception, and the
real defect is almost always in the *percentage notation* or the *row's country scope* —
both of which are convention questions rather than research questions.
