# Escalation — deep-sweep `fills[]` are overwhelmingly ref-only work, staged as value changes

**Date:** 2026-08-07
**Scope:** tracker-wide (every country with a deep-sweep run). Surfaced during the Pakistan gas pass.
**Severity:** no wrong values were written, but delivered workbooks overstate the work
order — ~666 value cells across 7 countries are tinted as "proposed values" when the
value proposed is the one already on the sheet.
**Status:** fixed going forward (Pakistan is built on the fix). Regenerating the
already-delivered packets is Baird's call — see "What I did NOT do".

## The defect

`critical-deep-sweep.js` tells each subagent to "DEEP-FILL genuinely blank value fields".
In practice subagents also — correctly — use `fills[]` to report the ref they found for a
cell that was already populated but had a blank `[ref]` (class `MISSING_REF`). There is no
other slot in the shard contract for that: the schema offers `validity[]`, `fills[]`,
`status_reviews[]`, `routes[]` — and no plain "here is a ref for this cell" array.

`merge_deepsweep_shards.py` then staged every `fills[]` entry as `class_in="FILL"`
unconditionally, never comparing the proposed value to the current one. In
`build_ref_workbook.py`:

```python
proposed = r.get("class_in") in ("FILL", "STATUS")
```

a FILL's value cell always earns the tier color, **including on the paste surface**. The
workbook's own README legend reserves that for a real proposal:

> a tier-colored value cell = a proposed value, a colored `[ref]` with an untinted value
> = ref-only work

So ref-only work was rendered as a value change. Pasting it is a no-op (the value is
identical), which is why nothing is *wrong* in the sheet — but the researcher is told to
paste hundreds of unchanged cells, and the handful of genuine changes are buried in them.

## Proven scope — and there is NO clean control

Measured by comparing each shard fill's values against the current sheet values in the
same dir's `worklist.json` (numeric-aware compare, `merge_qc.is_ref_only`):

| staging dir | fills | value-unchanged | value-changed | current-blank | key-miss |
|---|---:|---:|---:|---:|---:|
| china-guangxi-gas/deepsweep-pilot | 89 | **76** | 10 | 0 | 3 |
| egypt-gas/annual | 20 | **19** | 0 | 0 | 1 |
| egypt-gas/ref-sweep-operating | 142 | **125** | 11 | 0 | 6 |
| iran-gas/annual | 19 | **17** | 1 | 0 | 1 |
| iran-gas/ref-sweep-operating | 103 | **81** | 15 | 0 | 7 |
| iraq-gas/annual | 54 | **41** | 8 | 0 | 5 |
| iraq-gas/ref-sweep-operating | 86 | **71** | 9 | 0 | 6 |
| libya-gas/annual | 15 | **9** | 3 | 0 | 3 |
| libya-gas/ref-sweep-operating | 87 | **82** | 5 | 0 | 0 |
| saudi-arabia-gas/annual | 26 | **4** | 18 | 0 | 4 |
| saudi-arabia-gas/ref-sweep-critical | 141 | **117** | 23 | 0 | 1 |
| saudi-arabia-gas/ref-sweep-operating | 90 | **74** | 9 | 0 | 7 |
| pakistan-gas (this pass, partial) | 107 | **100** | 2 | 0 | 5 |

~83% of all deep-sweep `fills[]` output is ref-only. `fills[]` is, in practice, the
ref-attachment channel, not the blank-field channel it was written to be.

The `current-blank` column reads 0 everywhere for a mechanical reason, not because blank
fills never happen: `build_ref_worklist.py` emits no unit for a cell whose value **and**
ref are both blank (those fall in its `skip` bucket — 927 of them in Pakistan). A genuine
deep-fill of a blank field therefore has no worklist unit to match and lands in the
**key-miss** column instead. Pakistan's key-misses resolve to exactly that: P3101 and
P3178 `Diameter` (blank fields, real fills) plus four owner units (see below).

The SOP asks a class memo to name the control that proves the scope. **I could not find
one.** My first cut appeared to show Iraq and `saudi/ref-sweep-critical` at zero, which
would have made this look Libya/Egypt-flavoured; that was an artifact — those dirs are
100% *key-miss* against their own `staged_resolutions.prior.json` (no ref baseline existed
at the matching `(ProjectID, sheet_row, ref_col)` keys, so nothing could fold). Measured
against the worklist instead, Iraq shows the same 71/86 pattern as everyone else. Treat
the scope as universal until a genuine counter-example appears.

## The fix (applied)

Two small changes, both in shared code, both no-ops where the condition doesn't hold:

1. `scripts/merge_qc.py` — new `is_ref_only(proposed_values, current_values)`: true when
   every proposed column equals the current sheet value (numeric-aware, so `1814` ==
   `1814.00` == `1,814`). Requires a non-empty current value, so a genuinely blank field
   stays a real fill.
2. `scripts/merge_deepsweep_shards.py` — a fill satisfying `is_ref_only` against the
   preserved ref record at its key upgrades that record in place
   (`class_out = REFS_ADDED`, carrying refs/tier/verifications/notes) instead of being
   appended as a FILL. The merge prints a `ref-only folds: N` line.

Result on Pakistan's `cancelled-review`: 10 fills → 10 folds, 0 spurious FILLs, 0 orphan
`REFS_ADDED` records. The record shape is exactly what a separate refs leg would have
produced (`class_in="MISSING_REF"`, `class_out="REFS_ADDED"`).

A third change was needed for **owner/operator units**: they live on the separate
operators/owners tab, and a worklist unit carries both `sheet_row` (tracker) and
`oo_sheet_row` (that tab). Subagents report the *oo* row, but
`seed_resolutions_from_worklist.py` drops `oo_sheet_row` (it is `null` on every seeded
record), so the row can never match. The merge now falls back to a `(ProjectID, ref_col)`
key **only when exactly one kept record has that pair**, so a multi-segment row can never
fold onto the wrong segment. That recovered 5 owner units in Pakistan's `annual` alone.
Carrying `oo_sheet_row` through the seeder would be the cleaner fix.

**Known gap:** the fold needs a ref baseline for the PID. Dirs whose fills key-miss
entirely (the `qc`/handoff dirs — egypt/qc 10/10, libya/qc 37/37, iraq/qc 3/3 miss) are
untouched by the fix and would need their Leg-3 keys reconciled separately. Not chased
here.

## What I did NOT do

I did **not** re-run the merges for the 7 committed countries. Those staging dirs back
already-delivered workbooks, and two of them are **partially applied by researchers**
(Saudi 100/199 annual-indev + 46/306 deepsweep ref units live; Egypt 16/284). Re-merging
would rewrite the canonical pending-state under a deliverable someone is mid-way through
working. That is a scope call, not a bug fix.

**Recommendation:** regenerate on the next natural touch of each country rather than as a
sweep — the rendering is misleading, not incorrect, so it can ride along with the next
packet rebuild. If a country is to be regenerated now, Libya (82/87) and
`saudi/ref-sweep-critical` (117/141) get the most benefit, and Saudi's partial-apply state
means its rebuild needs the usual check-each-cell-before-pasting warning.

## Longer-term

The real fix is in the shard contract, not the merge: give `critical-deep-sweep.js` an
explicit `refs[]` array for "I found a source for the value already there", so the
subagent states its intent instead of the merge inferring it from a value comparison.
The merge-side fold should stay regardless as a safety net.
