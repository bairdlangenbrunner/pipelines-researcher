# `independent` was a claim no merger ever checked — 1,450 staged units, 12 countries

**Found:** 2026-08-27, mid-flight in the Egypt oil deep sweep, by censusing shard
`fills[]` before merging rather than after.

## The defect

`independent` encodes the confidence rubric's **">=2 independent sources that agree"**
(`docs/reference/confidence_tiers.md`). Sweep agents routinely set it `true` on a
single-source unit — often in the same record whose own `researcher_notes` end
*"Single source -> medium."* All three mergers
(`merge_deepsweep_shards` / `merge_ref_shards` / `merge_discovery_shards`) passed the
field through **verbatim**, so nothing ever tested the claim against the refs the
record carried.

Worse, merge-time QC already strips refs that fail verification
(`merge_qc.verified_refs`) — but it stripped them *without* revisiting `independent`.
So **306 of the affected units claim independent corroboration while carrying ZERO
refs**: the flag outlived the very sources it was a claim about.

This is not cosmetic. `independent` renders as the yes/no column a researcher reads
when deciding whether to paste a value. A wrong `yes` is worse than a missing one.

Egypt oil alone: **38 single-ref units flagged `independent: true`**, 2 of them also
tier `high`.

## Precedent — this is the Uzbekistan finding, generalized

The Uzbekistan pass (2026-08-26) caught **13** units of exactly this shape and fixed
them by hand, reading the field as "independent of GEM". Hand-fixing the instance left
the cause in place; the repo-wide census shows the true blast radius is **1,450 units
across 41 staging dirs in 12 countries** — and 16 units in Uzbekistan's own
`ref-sweep-operating` survived that hand pass.

## Fix (cause, not instance)

- `merge_qc.independence_qc(refs, tier, independent, notes)` — `independent` may be
  `true` only with **2+ surviving refs**; a unit that loses the claim and sits at tier
  `high` drops to `medium` (a single source is medium at best); a `[QC]` note records
  the demotion.
- Applied at **all five** record sites in `merge_deepsweep_shards` (validity, fills
  ref-only branch, fills, status_reviews, routes) and in `merge_ref_shards` /
  `merge_discovery_shards`. No future pass can restate the claim.
- `scripts/repair_independence.py` applies the same invariant to dirs merged before
  the fix (dry-run by default). It is a **deterministic metadata repair, not
  re-research**: no value, `class_out`, ref or verification is touched.

## Applied

**Egypt — repaired 2026-08-27** (this batch's scope): 113 flags `yes -> no`, 39 tiers
`high -> medium`, across `egypt-gas/staging/{annual,qc,ref-sweep-operating}`. Egypt now
audits clean at 0 residual units. The Egypt dirs merged *after* the fix
(`deepsweep-20260827`, `ref-sweep-all`) never carried it.

## Residue — NOT repaired, needs a call

The remaining 11 scopes are pending review surfaces whose **delivered workbooks were
built from these staging dirs**. Repairing staging without rebuilding leaves the two
inconsistent, and rebuilding a researcher's current deliverable mid-review is not a
call to make unasked. The repair itself is one command.

| country-commodity | flags yes→no | tier high→medium |
|---|---:|---:|
| `india-gas` | 252 | 102 |
| `saudi-arabia-gas` | 210 | 40 |
| `pakistan-gas` | 181 | 102 |
| `china-guangxi-gas` | 167 | 45 |
| `ukraine-gas` | 140 | 26 |
| `kazakhstan-gas` | 113 | 43 |
| `iraq-gas` | 95 | 25 |
| `libya-gas` | 90 | 17 |
| `iran-gas` | 66 | 16 |
| `uzbekistan-gas` | 16 | 2 |
| `saudi-arabia-oil` | 4 | 2 |
| `malaysia-gas` | 3 | 0 |
| **total** | **1337** | **420** |

```bash
python scripts/repair_independence.py --all            # dry-run
python scripts/repair_independence.py --all --apply    # then rebuild affected workbooks
```

A tier demotion is the half that changes what a reader sees (green -> yellow); the flag
flip changes what they trust. Neither changes a value.

## The method lesson

Same shape as the China/Jiangxi silent-loss defects and the Cyrillic matcher defect:
**found by reconciling counts, not by any error surfacing.** Nothing failed, nothing
warned — the census only happened because shards were inspected mid-flight. A field
that no code path ever tests is a claim, not data. Corollary to the Cyrillic rule
("a diagnostic must report the MATCHER's view, never the data's own"): **a
provenance flag must be recomputed wherever the provenance it describes is edited** —
`verified_refs` had every reason to know the flag was now false, and never asked.
