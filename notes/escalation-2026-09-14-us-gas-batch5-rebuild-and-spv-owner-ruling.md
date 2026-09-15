# Escalation — two decisions I should not make alone (US gas, 2026-09-14)

Both surfaced during the slice-2 deep sweep. Neither is a research question; both are
scope/convention calls that belong to Baird. Nothing has been applied to the live sheet.

---

## 1. Slice 1 batch 5 (`deepsweep-remainder`) is a CLOSED deliverable that now carries known defects

The batch-5 workbook `deliverables/pipelines_batch_20260910_1526_ET_united-states-gas_deepsweep-remainder.xlsx`
(45 rows) was delivered 2026-09-10 and closed slice 1. Since then three things have
happened to its staging, and the workbook reflects none of them.

### (a) 165 undated-EIA refs across 19 of its 45 rows

Refs citing the bare `https://www.eia.gov/naturalgas/pipelines/EIA-NaturalGasPipelineProjects.xlsx`
— the rolling current-release file, which is overwritten each release, so the URL does
not state any particular value and a reviewer cannot get from the link to the number.
The correct form is the dated release (`..._<Mon><Year>.xlsx`) plus sheet name and Excel
row in the note.

Affected rows: P0284 P0314 P0315 P1997 P2008 P2039 P2495 P2496 P2510 P2541 P2560 P2565
P2588 P2617 P2631 P2649 P3280 P4381 P4382.

**This is a cohort defect confined to batch 5.** A slice-wide scan found **zero** undated
refs and **zero** `data.php` refs anywhere in slice 2 (six populated batches, 222 rows) —
the rule was tightened after batch 5 shipped. It is a clean cohort to re-ground, not a
scattered leak.

### (b) Two rows patched under the status-flip clearing rule after delivery

Sweep item 7(b) found rows whose Status had flipped to a live value while
`CancelledYear` / `ShelvedYear` / `ShelvedCancelledType` stayed populated. Four hits
slice-wide; **two are in batch 5**:

- **P0171 Constitution Gas Pipeline** — Status `cancelled` -> `proposed`. Williams
  filed a Notice of Petition (Jan 2026) and a Federal Register EA availability notice
  (2026-17399, Aug 2026) revived it. `CancelledYear` 2020 and
  `ShelvedCancelledType` cleared; the Feb-2020 cancellation refs were moved off the
  Status fill onto `Cancelled [ref]`, where the 2020 date legitimately lives.
- **P2008 TETCO / `TEMAX Pipeline Expansion`** — `ShelvedYear` 2010, `CancelledYear`
  2012 and `ShelvedCancelledType` cleared; no candidate project for this row was ever
  cancelled under any identity reading.

Pre-edit state of all four rows is backed up at
`batches/united-states-gas/staging/statusflip_clearing_backup_20260914.json`.

### (c) An unresolved identity flag on P2008 that touches two slice-2 rows

P2008's sheet SegmentName is **TEMAX Pipeline Expansion** (TEMAX/TIME III, FERC docket
CP09-68, completed 2011-08-26, 38.6 mi, 30/36 in, $472M, PA — EIA Aug 2026 release,
sheet `Historical Projects (1996-2024)`, Excel row 694). But the row's recorded 53.10 km
/ 33.0 mi and $500M match **TEAM 2014**, and a prior agent documented that the row mixes
TEAM 2012 and TEAM 2014 signals.

The risk is a **duplicate**: TEAM 2012 and TEAM 2021 are separately tracked as **P5832**
and **P5835**, both in slice 2 batch A6. So attributing P2008 to a TEAM phase would
collide with a row that already exists. I added TEMAX to the shard as an unconsidered
candidate plus the duplicate-risk flag rather than picking a winner. The A6 agents for
P5832/P5835 carry the flag and will report back on it.

### The decision

**Do we rebuild the batch-5 deliverable?** Options as I see them:

1. **Rebuild it** — re-ground the 165 refs (mechanical: the dated release, sheet and row
   are already recoverable from `sources/eia_pipeline_projects/data/eia_projects_long.csv`
   for most), then re-merge, re-gate and rebuild the workbook so it carries the two
   clearings and the identity flag. Highest quality, costs a merge cycle plus the
   re-grounding pass. My recommendation, because you have not applied batch 5 yet — the
   defect is cheaper to fix now than after it is pasted.
2. **Ship an erratum alongside it** — leave the workbook, hand you this memo plus a
   short list of the 19 rows and 2 clearings to apply by hand. Cheapest, but it puts the
   correction on your side of the handoff.
3. **Defer to a slice-1 cleanup pass** after slice 2 closes, bundling batch 5 with
   anything else slice 2 turns up.

I have not touched the deliverable. Say which and I will execute it.

**Not a defect, for the record:** batch 5 also has 69 verifications carrying `ok` with no
`name_found`, and slice 2 has 162. These are NOT a quality problem — `scripts/backfill_name_found.py`
fills the field from evidence by re-fetching, and it belongs in the merge recipe
(`--shards rows` before the merge, `--shards store` after). The recipe I inherited only
listed `--shards store`; I will run both.

---

## 2. Owner1 on single-asset SPV rows: the pipeline owns itself

Found on **P0302 Permian Highway Pipeline** (sheet row 152). `Owner1` is
`Permian Highway Pipeline LLC` at 100% — i.e. the row records the asset's own
special-purpose vehicle as its owner, which tells a data user nothing about who actually
holds the equity.

The sourced alternative is real: Kinder Morgan's 10-K states KMI holds **27.74%**, with
the balance reportedly Kinetik and an ExxonMobil affiliate.

**I did not flip it, for two reasons.**

- **It is the house convention, not a row defect.** The operators/owners tab records the
  same shape on the neighbours: **P0378** and **P3886** (Gulf Coast Express) both carry
  `Gulf Coast Express Pipeline LLC 100.00%`. Flipping P0302 alone would make the tab
  internally inconsistent — one row stating equity while its siblings state the SPV.
- **The contested value cannot be taken piecemeal.** 27.74% is only KMI's share; the
  remaining 72.26% is not sourced to the standard we hold everything else to. Writing
  `Kinder Morgan 27.74%` and leaving Owner2+ blank would be worse than what is there.

So I recorded the equity reading in the shard's `contested` (`Owner1: 'Kinder Morgan'`,
`Owner1%: '27.74%'`) with the ruling in the notes, and kept the staged value.

### The decision

**Tracker-wide: does `Owner1` hold the SPV or the equity holders?** This is not a P0302
question — it is a convention that governs every project-financed US pipeline row, and
probably rows in other countries too. Whichever way you rule, the fix is a sweep across
the operators/owners tab, not a one-row edit. Until you rule, I will keep staging the
SPV (matching the neighbours) and recording the equity split in `contested` so it is
visible without being applied.

---

## Status of everything else from this pass

- Standing-rule-1 (GEM citation) violations: P5113 fixed; **P0296 is the last one** and
  is being re-grounded now. Slice-wide count after that will be zero.
- Item 7(a), the "not in EIA" defect: closed.
- Item 7(b), status flips: all four rows patched, all pass `check_shard_coverage`.
- Item 2, the EIA Owner/Operator correction: closed (P0302 was its last open row).

---

## RULED — Baird, 2026-09-15. This memo is closed.

**§1 batch 5 — rebuild it.** "Go ahead and rebuild batch 5, yes." The rebuild re-grounds
the 165 undated-EIA refs across 19 rows to the dated release + sheet name + Excel row,
re-merges, re-gates, and rebuilds the workbook so it also carries the two post-delivery
status-flip clearings (P0171 Constitution, P2008 TETCO/TEMAX) and the P2008 TEMAX/TEAM
identity flag. The `20260910_1526_ET` workbook is superseded on delivery and moves to
`archive/`.

**§2 `Owner1` — the SPV, not the parent.** "Owner1 should hold SPVs. The ownership team
then builds parent trees with that SPV." So the staged behaviour was already right:
`Trail West Pipeline, LLC` (not Williams), the project company (not Kinder Morgan) —
and the equity reading stays in `contested`/`researcher_notes` where the ownership team
can see it. There is no sweep owed across the operators/owners tab, because the
convention matches what was staged. Recorded in `docs/reference/gem_schema.md` under the
operators/owners tab, and in the slice-2 `ADDENDUM.md`.

Two related rulings given in the same message, recorded here because they came off this
pass's findings:

- **P7455 / P7830 Fuel → Oil: hold as-is for now.** Oil is out of scope for the cycle, so
  the reclassification does not reach the paste surface. P7455's fill is re-keyed
  `UNRESOLVED` (the only sources that speak to its fuel service contradict the recorded
  `Gas`, and a contradicting source is not a ref) and its validity `contested` cleared to
  `{}`; the finding itself survives on the evidence tab. P7830 needed no change — the
  sheet already records `Fuel = 'Oil'`, so its fill confirms the recorded value rather
  than proposing a flip.
- **P7823 distribution: approved as staged.** "Distribution is OK in GGIT for now, as long
  as `PipelineType` is distribution." The staged `PipelineType = 'distribution'` correction
  is the fix; no existence or scope action is owed on the row.
