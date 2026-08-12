# Escalation — Kazakhstan gas: system-level lengths and capacities restated on every string of a multi-string system

**Date:** 2026-08-11 · **Scope:** GGIT gas, Kazakhstan (52 rows in scope) · **Raised by:** the §9 full-pass redundancy leg
**Staged as:** `batches/kazakhstan-gas/staging/redundancy/staged_resolutions.json`, clusters **A, B, D, E, J**
**Class:** a whole class of GEM values looks systematically wrong (CLAUDE.md escalation gate 2), not a row-by-row finding

## The pattern

Kazakhstan's gas network is mostly **multi-string trunk systems**: two or more parallel
pipes on one right-of-way, each carried as its own GEM row. In at least five of those
systems, the row set carries **one system-level figure on every string** rather than each
string's own value. Summing the rows therefore double- or triple-counts real pipe and real
throughput.

| System | Rows | The restated value | What it should be |
|---|---|---|---|
| Central Asia–Center | P2291 (CAC-2), P5770 (CAC-4), P5771 (CAC-5) | **Capacity 60.20 bcm/y on all three** (CAC-3 P2292 reads 5.00 — the contrast that proves it) | per-string throughput, or blank + the system figure in `ResearcherNotes` |
| Bukhara–Tashkent–Bishkek–Almaty | P0739 (I), P5810 (II) | **LengthKnownKm 1,585.00 on both** | per-string length; the drawn corridor is 1,270.28 km, so both figures are also 315 km long |
| Bukhara–Ural | P2289 (I), P5695 (II) | **Capacity 21.00 bcm/y on both**; P5695's 2,382.00 km is KMG AR2019/2020's WHOLE-SYSTEM length | per-string values; AR2021 restates the system at 1,567.8 km |
| Zhanaozen(Uzen)–Zhetybay–Aktau | P3948, P5776, P5777, P5783 (+ P5789) | **Capacity 4.54 bcm/y on all four** — legitimately a system figure (Intergas states it for the corridor's strings together), so it belongs on the grouping, not on each row. The length column is **not** a double count: see cluster A below, where that reading is refuted | the system figure on `PipelineNetworkGrouping`; per-row throughput unknown |
| Makat–North Caucasus | P1476 (trunk), P3999 (looping line) | Capacity 21.90 + 13.15 bcm/y — unclear whether the loop's figure is an increment or the post-loop system total | stated explicitly either way |
| Bukhara–Ural CS14–Aktobe | P5927, P5928 | **every attribute identical** — 158.00 km, 530 mm, 1.96 bcm/y, blank StartYear1, same trace | unresolved: see cluster F |

This is the same defect India carries with 107.00 MMSCMD stamped on five HVJ rows, so it is
a tracker-wide *shape*, not a Kazakhstan quirk — but the proven scope here is Kazakhstan
gas. The control that proves it is **P2292 (CAC-3)**: it sits in the same system, on the
same corridor, entered by the same researcher, and reads 5.00 bcm/y. If 60.20 were each
string's own capacity, CAC-3 would carry it too.

## Cluster A: measured, then REFUTED — the double count is withdrawn, twice over

This cluster was staged, then re-staged, and the recommendation reversed each time. The
final answer is: **P3948 is a real physical pipeline, the ~149 km double count is REFUTED,
and the recommendation to fold it is WITHDRAWN.** The trail is kept in full because the
refuted reading is genuinely compelling on the numbers, and because the same evidence
shape will recur in every multi-string Kazakh system.

**What was measured (all still true):** P3948's own drawn route measures **137.85 km**
(Zhanaozen 52.843,43.358 → Aktau 51.197,43.659). P5777 (Zhanaozen–Zhetybay) measures
**58.22 km**; P5783 (Zhetybay–Aktau) measures **79.63 km**; 58.22 + 79.63 = **137.85 km**,
exact, each child lying 100 % inside the parent's 2 km corridor. The sheet's length column
appeared to say the same: P5776 17.80 + P5777 60.70 + P5783 70.80 = **149.30** against
P3948's **149.10**, i.e. P3948 exceeding Zhanaozen→Aktau (131.50 km by its own segment
rows) by almost exactly the 17.80 km KazGPP feeder. Read that way there is no residual
length left over, and the fix looked like folding P3948 rather than shortening it.

**What refutes it:** two **independent** official Russian-language documents describe this
corridor as carrying separately-**named**, separately-**diametered** trunk lines — and
P3948 is one of them by name, diameter *and* length.

- Intergas Central Asia's own environmental-permit filing for its Aktau branch
  («Краткое нетехническое резюме» for МГ «Жанаозен–Актау», 2025–2030,
  `ecoportal.kz/Public/PubHearings/LoadFile/182922`) states verbatim: **«Магистральный
  газопровод высокого давления Ду 720 мм «Жанаозен - Жетыбай - Актау» протяженностью
  149,1 км»** — the diameter *and* the length, under the row's exact name. It is a PDF, so
  `url_verifier`'s substring check reports a documented false negative; read locally with
  `pdftotext -layout`.
- The Mangistau regional development plan, item 116
  (`adilet.zan.kz/rus/docs/P2100000784#z12`) states verbatim: **«Капитальный ремонт 3-х
  ниток магистрального газопровода "Жанаозен – Жетыбай – Актау" Ду 720 мм, магистрального
  газопровода "КазГПЗ-КС "Жанаозен" Ду 720 мм, магистрального газопровода "Жанаозен –
  Жетыбай – Актау" Ду 529/530 мм»** — one joint capital-repair programme (Q4 2022 – Q2
  2024) over three distinctly named, distinctly diametered lines.

So GEM's rows map **1:1 onto real physical lines**:

| Row | The line it is | Diameter | Length |
|---|---|---|---|
| P3948 | Zhanaozen–Zhetybay–Aktau, the 720 mm trunk | 720 mm | 149.1 km (sourced verbatim) |
| P5776 | KazGPZ–KS Zhanaozen, a separately named feeder | 720 mm | 17.8 km |
| P5777 + P5783 | Zhanaozen–Zhetybay–Aktau, the 529/530 mm trunk, split at Zhetybay | 530 mm / 529 mm | 60.70 + 70.80 = 131.50 km |
| P5789 | the fourth thread, under construction since 2023 | unknown | unknown |

**Why the evidence that looked decisive is not.** Two things had to be given up:

1. The 0.20 km arithmetic near-identity (149.30 vs 149.10) is a **coincidence** of two
   parallel trunks of similar length plus a feeder. An aggregate row would not have its own
   diameter class stated in the operator's own permit filing at its own stated length.
2. The geometric identity is exactly what you get if the segment routes were digitized by
   **cutting the parent's trace** — the same shared-right-of-way convention six other
   Kazakh systems follow (see the end of this memo). Geometry cannot distinguish parallel
   strings here, and that cuts both ways: it neither proves duplication nor refutes it.

**Consequences:**

1. **The fold is withdrawn.** P3948 stays as it is; its name, diameter and length need no
   change. Severity stays `escalate` because a *withdrawn* structural recommendation is
   something Baird must see, not a silent edit.
2. **The ~280 km "missing parallel pipe" reading is also withdrawn** — but not entirely
   settled. «3-х ниток» is grammatically ambiguous: it may enumerate the three named lines
   that follow it (in which case GEM's numerals `I` / `II` / `III` / `III` are **correct**,
   since the two rows numbered III are the two stretches of the third line, and the earlier
   claim that the numerals mislabel segments as threads is withdrawn too), or it may mean
   three threads of the 720 mm line *alone*, in which case GEM is missing parallel pipe.
   **Do not decide this on the numerals.** Either way P3948 is a real line, so the fold is
   withdrawn under both readings.
3. **Carry 4.54 bcm/y as a system figure on the grouping,** not on each of the four rows —
   Intergas's 2023 AR states the post-repair 2.68 → 4.54 bcm/y for the corridor's strings
   **together**. The 3.60 bcm/y that kt.kz (2008) and Neft i Gaz (2019) give stays a
   separate open spec question: Intergas dates the *pre*-repair figure at 2.68, and one
   shard reads 3.60 as belonging to the distinct Zhetybay–Kuryk branch (P5784) on its own
   2020 procurement spec. Both readings are recorded; neither is applied.
4. **New open spec question:** the 529/530 trunk measures 131.50 km against the 720 mm
   trunk's 149.10 km for nominally the same endpoints. Under the fold reading that ~18 km
   was just the feeder; now it needs explaining on its own.
5. **529 mm is not a typo.** ecoportal's segment table puts 530 mm on the
   Zhanaozen–Zhetybay stretch and 529 mm on Zhetybay–Aktau, so P5777/P5783's differing
   values are a real along-the-length change — the earlier reading of 529-vs-530 as one
   being a mistyping of the other is withdrawn.

### P5789 (thread IV) — real, and its shared corridor trace is legitimate

Thread IV's **existence is confirmed** and independent of GEM: Turan Times (2023-02) on the
4th thread's construction start, two InAktau articles tracking progress, and Intergas
Central Asia's own network list carrying the line as «Узень-Жетыбай-Актау». It is
specifically the *new* fourth thread, distinct from the 2023 capital repair of the three
existing ones — so it is neither a phantom nor a duplicate of P3948, and an earlier reading
of it as a copied "segment" is withdrawn.

Its route file **`P5789.geojson` is byte-identical to P3948's** — the same three vertices
52.84349,43.35762 → 52.17066,43.54285 → 51.19745,43.6588 — and that copy is **legitimate**:
thread IV runs Uzen→Aktau along the same right-of-way, which is exactly the shared-corridor
convention six other Kazakh systems use (see the end of this memo). What the copy does *not*
confer is a length or an accuracy grade of its own: the `LengthMergedKm = 137.85` it yields is
the corridor's length, not a sourced length for thread IV, so it must not enter a total as
one; and `RouteAccuracy = medium` describes the drawing **P3948** got, so it is a re-grade
question, not a route problem. The row's own `LengthKnownKm` and `Capacity` are both `--`.
Contrast `P5776.geojson`, which holds `geometry: null` — the honest placeholder for a row with
no route of its own, and the one operating Kazakh gas row still at `no route` / `Not mapped`,
hence a §8 route-creation candidate. Separately, the in-dev leg recommends **proposed →
construction** for P5789 on the dated construction evidence.

## Which rows are staged as actions, and which exist only here

**All of them are staged** — every row in the table above has a `__VALIDITY__` record in the
redundancy dir carrying the cluster-level recommendation, so nothing in this memo is
memo-only. What is *not* staged is any edit: this is read-and-flag, and the per-string
figures do not exist to be filled in. Resolving them needs a source that does not appear to
exist publicly (see below), so several will legitimately end as `ResearcherNotes`
explanations rather than value changes.

## Why this is hard to fix, and the trap to avoid

Kazakhstan has **no public line-wise gas-pipeline register** (surveyed 2026-08-11, full
writeup in `docs/reference/source_roster.md`). The best line-wise source is the
KazMunayGas Annual Report's "Gas Transportation and Marketing" table, which itemises only
the **8 major systems** — i.e. it reports exactly the system-level aggregates that are the
problem, and never the individual strings. QazaqGaz's IGO 2024 lists 25 Intergas lines by
**name only**.

**The trap:** KMG's AR2019/AR2020 and AR2021 disagree materially on the same systems
(Central Asia–Centre 5,306 → 4,149.2 km; Bukhara–Ural 2,382 → 1,567.8; BGR-TBA +
Gazli–Shymkent 2,462 → 1,903.4; Soyuz + Orenburg–Novopskov 1,147 → 805). That is a scope
redefinition, not a correction — and **two vintages of one publisher are ONE origin**. A row
matching AR2020 is therefore *dated*, not corroborated, and picking whichever vintage
agrees with the sheet is not verification.

## Recorded refutations (do not re-raise)

Seven of the eleven clusters refute a duplicate hypothesis (A, C, D, E, H, I, J). Cluster A
is above; two more matter most here because they look exactly like this defect and are not:

- **Central Asia–China Lines A/B/C** (P2299/P2300/P1124), all 1,833 km: **not** a triple
  count. Their capacities 15.00 + 15.00 + 25.00 **sum to 55 bcm/y**, which is precisely the
  system figure Order of the Minister of Energy №350 (29.09.2023) ¶44 states — the opposite
  of the CAC pattern. The shared 1,833 km is the Turkmen-border-to-Khorgos transit length
  all three strings share (¶44 gives "до 1300 км" for the Kazakh portion; + ~530 km Uzbek).
- **Almaty–Taldykorgan vs Taldykorgan–Usharal** (P3964 302.6 km / P5901 302.4 km): distinct
  consecutive links meeting at Taldykorgan, sharing 1.5 % / 0.8 % of their length, and named
  separately in Intergas Central Asia's own asset list. But the matching lengths are **not**
  a coincidence: two independent primary sources (KazTAG 2012, Kazakhstanskaya Pravda 2018)
  put Almaty–Taldykorgan at **264.8 km**, and GulfPub's 263.93 km agrees with them to within
  1 km. **Our earlier claim that GulfPub was the outlier is withdrawn** — it rested on GEM's
  own 303.78 km drawn route, and a GEM-drawn route is not an independent source. P3964's
  length goes to Update, alongside the observation that its `RouteAccuracy='high'` trace
  terminates ~61 km west of Almaty city, so a scope/endpoint difference is a live
  alternative to a value copied from P5901.

And the method rule that follows from the same evidence: **in Kazakhstan gas, identical
drawn geometry is NOT evidence of duplication.** Six systems share one corridor geojson
across all their strings (P0739/P5810, P2289/P5695, P2291/P5771 with P5770 a subset,
P1124/P2299/P2300, P5927/P5928, P6830/P6831). For parallel strings on one right-of-way that
is defensible. The one shape geometry *would* decide is the aggregate-vs-segment case — one
row's trace equal to the union of other rows that each have their own — and cluster A is the
cautionary tale: it had that signature *and* matching arithmetic to 0.20 km, and it was
still wrong. Segment traces cut from a parent's line produce the union identity for free.
**Only sourcing decides duplication in this country** — here, an operator's own permit
filing naming the parent line's diameter at the parent line's length.
