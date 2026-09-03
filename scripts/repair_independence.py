#!/usr/bin/env python3
"""Repair the `independent` flag on already-staged resolutions.

`independent` encodes the rubric's ">=2 independent sources that AGREE" (see
docs/reference/confidence_tiers.md) — NOT "independent of GEM". Sweep agents
routinely set it True on a single-source unit whose own researcher_notes say
"single source -> medium", and the mergers passed it through verbatim, so the
claim survived even when merge-time QC had already stripped the refs. It renders
as the yes/no column a researcher trusts when deciding whether to paste a value,
which makes a wrong `yes` worse than a missing one.

The merge path is fixed at source (merge_qc.independence_qc, applied in
merge_deepsweep_shards / merge_ref_shards / merge_discovery_shards), so no future
pass reproduces this. This script applies the same invariant to staging dirs that
were merged before the fix — a deterministic metadata repair, NOT re-research:
no value, class_out, ref or verification is touched.

Dry-run by default; --apply writes. Rebuild any affected workbook afterwards.

Usage:
    python scripts/repair_independence.py --staging batches/egypt-gas/staging/qc
    python scripts/repair_independence.py --all --apply
"""
import argparse, glob, json, os, sys, collections
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from merge_qc import independence_qc  # noqa: E402


def repair(path, apply=False):
    doc = json.load(open(path))
    res = doc.get("resolutions")
    if res is None:
        return None
    flipped = demoted = 0
    for r in res:
        tier, indep, notes = independence_qc(
            r.get("proposed_refs") or [], r.get("tier", ""),
            r.get("independent", False), r.get("researcher_notes", ""))
        if indep != r.get("independent", False):
            flipped += 1
        if tier != r.get("tier", ""):
            demoted += 1
        r["tier"], r["independent"], r["researcher_notes"] = tier, indep, notes
    if apply and flipped:
        meta = doc.setdefault("meta", {})
        meta["independence_repaired"] = {"flipped": flipped, "tier_demoted": demoted}
        json.dump(doc, open(path, "w"), indent=1, ensure_ascii=False)
    return flipped, demoted, len(res)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--staging", help="one staging dir (or its staged_resolutions.json)")
    ap.add_argument("--all", action="store_true", help="every batches/*/staging/*/ dir")
    ap.add_argument("--apply", action="store_true", help="write (default: dry-run)")
    args = ap.parse_args()

    if args.all:
        paths = sorted(glob.glob("batches/*/staging/*/staged_resolutions.json"))
    elif args.staging:
        s = args.staging.rstrip("/")
        paths = [s if s.endswith(".json") else os.path.join(s, "staged_resolutions.json")]
    else:
        ap.error("pass --staging <dir> or --all")

    tot = collections.Counter()
    for p in paths:
        if not os.path.exists(p):
            print(f"  SKIP (no staged_resolutions.json) {p}")
            continue
        out = repair(p, apply=args.apply)
        if out is None:
            print(f"  SKIP (no resolutions[]) {p}")
            continue
        flipped, demoted, n = out
        if flipped or demoted:
            tot["dirs"] += 1; tot["flipped"] += flipped; tot["demoted"] += demoted
            print(f"  {flipped:4d} independent yes->no, {demoted:3d} tier high->medium "
                  f"(of {n} units)  {p}")
    verb = "REPAIRED" if args.apply else "WOULD REPAIR (dry-run)"
    print(f"{verb}: {tot['flipped']} flags, {tot['demoted']} tiers, "
          f"across {tot['dirs']} staging dir(s)")
    if not args.apply and tot["flipped"]:
        print("Re-run with --apply to write, then rebuild any affected workbook.")


if __name__ == "__main__":
    main()
