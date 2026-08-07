# Escalation — `ShelvedCancelledType` / `DelayType` vocabulary was wrong in our docs, code and QC check

**Date:** 2026-08-07
**Scope:** tracker-wide (both GGIT and GOIT). Surfaced during the Pakistan gas pass.
**Severity:** no live cell was corrupted — nothing was ever written to the sheet — but
18 staged records across 6 countries carry a value that does not exist in the column,
and the QC vocab check was inverted (it would flag every real row and pass ours).
**Status:** code, QC table and docs fixed; Pakistan re-merged and clean.

## The defect

`docs/reference/controlled_vocab.md`, `CLAUDE.md`, `docs/GOIT_Pipeline_Research_Workflow.md`
and the `critical-deep-sweep` subagent contract all specified:

> **Title Case:** `DelayType`, `ShelvedCancelledType` … values `Presumed`, `Confirmed`

Re-derived from both live tabs (snapshots `20260807`), the columns actually hold:

| Column | Live values (gas / oil) |
|---|---|
| `ShelvedCancelledType` | `inferred` 84 / 63 · `confirmed` 83 / 52 |
| `DelayType` | `inferred` 114 / 37 · `confirmed` 138 / 41 (+1 stray `Assumed`, a real data error) |
| `Delayed` | `yes` 254 / 78 — all lowercase |
| `Opposition` | gas: `no` 66 · `Yes` 46 · `yes` 29 · `No` 26; oil: all lowercase |
| `FIDStatus` | `Pre-FID`, `FID` — the only genuinely capitalized field |

`Presumed` appears **zero** times in either tracker. It is not a casing slip: it is a
different word from `inferred`.

This is exactly the case CLAUDE.md's own rule covers — "when in doubt, pull a real row
from the sheet and copy the exact casing" — and the reference doc had drifted from the
sheet without anyone re-checking.

## What it affected

1. **`merge_qc.status_qc`** hard-coded `changes["ShelvedCancelledType"] = "Presumed"` on
   every dormancy-rule status change. Every `stale` verdict we have ever staged carries
   it: **18 records across 6 countries** — china-guangxi 10, iraq 3, egypt 1, iran 1,
   pakistan 3 (now fixed). Had one been pasted, it would have introduced a value the
   column has never held.
2. **`build_qc_workbook.py`'s `TITLE_VOCAB`** validated against `{"Presumed",
   "Confirmed"}` and `{"Yes"}`. Run tracker-wide it would have flagged **all 282 real
   `ShelvedCancelledType` rows and all 330 `DelayType` rows** as vocab violations, while
   passing our own out-of-vocab staged values. The check was inverted end to end.
3. **The subagent contract** told every deep-sweep agent to emit `"Presumed"`, so the
   defect regenerated itself on each run.

## Fixed

- `merge_qc.status_qc` now writes `inferred`, and normalizes any subagent-supplied
  `Presumed`/`Confirmed` to the live vocabulary with a `[QC]` note on the record.
- `build_qc_workbook.TITLE_VOCAB` re-derived from the snapshots. `Opposition` accepts
  both cases deliberately — the gas tab is genuinely mixed, and silently "fixing" 46+26
  capitalized cells is a data decision, not a QC rule.
- `controlled_vocab.md`, `CLAUDE.md`, `GOIT_Pipeline_Research_Workflow.md` and
  `.claude/workflows/critical-deep-sweep.js` corrected.
- Pakistan re-merged: P0452 → `confirmed`, P3173/P3174 → `inferred`.

## Open for Baird

- **The 15 non-Pakistan staged records** (china-guangxi 10, iraq 3, egypt 1, iran 1) still
  read `Presumed` in their committed `staged_resolutions.json`. They are staged, not
  applied. Cheapest fix is a re-merge of those dirs when each country is next touched —
  same regeneration question as the ref-only-fills memo, and worth doing in one pass.
  **Until then: if you paste a shelved/cancelled row out of one of those packets, type
  `inferred`, not what the workbook shows.**
- **`Opposition` is inconsistent in the live gas tab** (75 lowercase vs 72 capitalized).
  Worth a one-time normalization decision, but it is a live-data edit and needs your
  authorization — not something to fold into a country pass.
- **Two stray values worth a look**, unrelated to this fix: `DelayType='Assumed'` (1 gas
  row) and `FIDStatus` holding `Yes` ×3, `in progress`, and a bare argaam.com URL in the
  gas tab.
