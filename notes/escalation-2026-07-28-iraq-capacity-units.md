# Escalation — capacity **unit labels** are wrong on 3 Iraq gas rows, and the screen says it is a tracker-wide class

**Date:** 2026-07-28 · **Scope:** GGIT, Iraq, gas (with a tracker-wide screen) · **Ruling needed from Baird**
**Staged:** `batches/iraq-gas/staging/ref-gap-repass/staged_resolutions.json` (P7477),
`batches/iraq-gas/staging/cancelled-review/staged_resolutions.json` (P4041),
`notes/escalation-2026-07-28-asb-iraq-length-units.md` §companion finding (P1841)

## The claim

Three Iraq gas rows store a **correct number under the wrong unit label**. In each case
the source states the value plainly and GEM's own `[ref]` points at that source — so
this is not a sourcing gap, it is a transcription defect at ingest, and the computed
`CapacityBcm/y` column publishes the error.

| PID | pipeline | source says | GEM holds | computed `CapacityBcm/y` | truth | error |
|---|---|---|---|---|---|---|
| **P7477** | Mousal–Al Qayyarah PS (22 km, 18″) | "130 cubic feet" (= 130 MMcf/d) | `130` **`bcm/y`** | **130.00** | ~1.33 | **~98× HIGH** |
| **P4041** | North Rumela–Al-Najaf (350 km, 28″) | 258 **MMSCFD** | `258` **`MMSCMD`** | **94.17** | ~2.67 | **~35× HIGH** |
| **P1841** | Baiji-K3–Al Kaem (16″) | ASB: 2,410,000 (1,000 scm/yr) = 2.41 bcm/y | `2.41` **`MMcf/d`** | **0.02** | 2.41 | **~120× LOW** |

**The directions differ.** That is the load-bearing observation: two are inflated and
one is deflated, so this is **not one systematic conversion applied wrongly**. It is
careless unit tagging, row by row, which means **no blanket fix exists** — each row has
to be checked against its own source. (Contrast the length defect in
`escalation-2026-07-28-asb-iraq-length-units.md`, which *is* one systematic conversion
and *does* have a per-family blanket fix.)

## Why it matters beyond three cells

Two of the three land their row in **GGIT's global top ten by capacity**:

| rank | PID | pipeline | `CapacityBcm/y` | length | diameter |
|---|---|---|---|---|---|
| 1 | P0271 | Transcontinental (US) | 171.70 | 10,200 km | — |
| **2** | **P7477** | **Mousal–Al Qayyarah PS (Iraq)** | **130.00** | **22 km** | **18″** |
| 3 | P0262 | Texas Eastern (US) | 119.47 | 14,202 km | — |
| 4 | P4122 | Luxembourg network | 104.34 | 2,175.9 km | — |
| 5 | P2459 | Zapolyarnoye–Novy Urengoy (RU) | 100.00 | 190 km | 1420 |
| 6 | P1305 | Crib Point Pakenham (AU) | 98.20 | 59.5 km | — |
| 7 | P3220 | Eastern Gas Transmission (US) | 97.09 | 6,437 km | — |
| **8** | **P4041** | **North Rumela–Al-Najaf (Iraq)** | **94.17** | **350 km** | **28″** |

A 22 km spur feeding one power station should not outrank a 14,202 km interstate. Any
country total, regional roll-up, or global capacity chart built off this column is
currently distorted by these rows.

## The physical screen — and its honest limits

Method: a capacity ceiling from diameter alone, `bcm/y ≈ k · D^2.5` with **k = 0.0017**,
calibrated so a 48″ Nord Stream line reads 27.5 bcm/y (its actual per-line rating). The
ladder it produces: 16″→1.7, 18″→2.3, 24″→4.8, 36″→13.2, 42″→19.4, 48″→27.1, 56″→39.9
bcm/y. Deliberately generous — it assumes high pressure and ignores compression spacing.

Run across the **1,964 GGIT rows that carry both a capacity and a parseable diameter**:

| threshold | rows | reading |
|---|---|---|
| > 2× ceiling | **72** | a soft flag only — mostly real high-pressure lines the crude formula under-rates |
| > 4× ceiling | **13** | genuinely suspicious |
| > 10× ceiling | **4** | almost certainly defective |

> **State this plainly rather than overselling it:** I earlier characterised the class as
> "only 14 of ~1,984 rows exceed 2× the ceiling." **That was wrong** — 14 is roughly the
> >4× count (13), not the >2× count (72). The screen is a *triage filter*, not a defect
> detector: a 2× exceedance is expected for well-compressed trunk lines, so nothing here
> should be treated as a finding without reading the row's own source, which is exactly
> what was done for the three Iraq rows above.

**The four worst rows, and the most important thing in this memo:**

| ratio | PID | pipeline | country | D | `CapacityBcm/y` | length |
|---|---|---|---|---|---|---|
| **157.8×** | P2009 | Mountaineer Gas Pipeline | **United States** | 8″ | 48.55 (4,750 MMcf/d) | 5.47 km |
| 55.6× | **P7477** | Mousal–Al Qayyarah PS | Iraq | 18″ | 130.00 | 22 km |
| 31.4× | P0693 | Frigg UK | United Kingdom | 9″ | 12.99 (1,271 MMcf/d) | 362 km |
| 13.4× | **P4041** | North Rumela–Al-Najaf | Iraq | 28″ | 94.17 | 350 km |

**The worst row in the tracker is not Iraqi.** P2009 stores 4,750 MMcf/d on an **8-inch,
5.5 km** line — 157× its ceiling, and 4,750 MMcf/d is roughly the throughput of a major
interstate system, not a 3.4-mile 8-inch lateral. Mountaineer Gas is a West Virginia
*local distribution company*; the figure looks like a system-wide or annual-total number
attached to one small segment. P0693 Frigg UK is the same shape: 1,271 MMcf/d down a 9″
line. Neither was researched here — Iraq was the scope — but they mean **the honest
conclusion is that capacity/diameter incoherence is a tracker-wide problem that the
Iraq pass happened to surface locally.** Do not close this as an Iraq item.

## Two loose ends the screen cannot test

`P4122` Luxembourg (104.34 bcm/y, ranked 4th globally) and `P1305` Crib Point
(98.20 bcm/y for 59.5 km, cancelled) both have a **blank `Diameter`**, so they never
enter the screen. Both look implausible on length alone — Luxembourg's entire national
network at 104 bcm/y would be ~⅓ of Germany's throughput. Untested, flagged.

Separately, **`P2459` has `Diameter = 1420`** — that is 1420 **mm** (a standard Russian
size, ≈56″) sitting in an inches column. Out of scope here, but it means the diameter
column has its own unit-label problem, and any tracker-wide capacity screen should
normalise diameter units first.

## Recommended fixes

| PID | edit | leave alone |
|---|---|---|
| P7477 | `CapacityUnits` `bcm/y` → **`MMcf/d`** | `Capacity = 130` — correct |
| P4041 | `CapacityUnits` `MMSCMD` → **`MMSCFD`** | `Capacity = 258` — correct |
| P1841 | `CapacityUnits` `MMcf/d` → **`bcm/y`** | `Capacity = 2.41` — correct |

Each is a **one-cell edit**. `CapacityBcm/y` is a **computed column — never paste over
it**; all three fixes correct it automatically.

Then, as a separate tracker-wide task: normalise `Diameter` units, re-run the screen,
and read the source on every row over ~4×, starting with P2009 and P0693.

## Sources

- **P7477** — Shafaq News, 2021-02-18: "The Iraqi Oil Projects Company completed the
  22 km-130 cubic feet natural gas pipeline supplying al-Qayyarah power plant … It runs
  22 km long, with a diameter of 18 inches."
  `https://shafaq.com/en/Economy/The-Ministry-of-Oil-completes-a-22-km-pipeline-that-supplies-al-Qayyarah-Power-Plant`
  (This ref was previously written off as `DEAD_LINK`; it returns HTTP 200 under a
  browser UA. The defect was invisible until the re-pass recovered it.)
- **P4041** — Saymar PDF, 258 MMSCFD.
  `https://saymar.org/wp/wp-content/uploads/2020/10/1485449570186424.pdf`
  (HTTP 200, 4.2 MB — exceeds `url_verifier.py`'s large-PDF limit; read with `pdftotext`.)
- **P1841** — OPEC ASB2012 Table 4.10, Iraq block: 2,410,000 in a column headed
  `(1,000 scm/yr)`.
  `http://web.archive.org/web/20250110032615/https://opec.org/opec_web/static_files_project/media/downloads/publications/ASB2012.pdf`
- Nord Stream per-line rating (48″ → 27.5 bcm/y) is the screen's calibration anchor; it
  is a sanity constant, not a citation for any row.

## Companion memos

- `notes/escalation-2026-07-28-asb-iraq-length-units.md` — the 19-row length defect;
  its §"the capacity column is *fine* in Iraq (one row excepted)" section identified
  P1841 and should be read with this memo, which **upgrades** that finding from a
  one-row exception to a class.
- `notes/escalation-2026-07-28-iraq-gasoil-misfiled.md` — P6824, the other defect the
  ref re-pass surfaced.
- `notes/escalation-2026-07-28-asb-iraq-provenance.md` — why the ASB is a per-pipeline
  table, which is what makes the P1841 comparison above valid.
