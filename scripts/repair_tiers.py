#!/usr/bin/env python3
"""Re-tier already-staged resolutions to rule 4 as of 2026-09-30.

One validated ref is now SUFFICIENT and shows green: a `medium` record carrying a
surviving ref whose verification loaded and names the pipeline is promoted to `high`
(merge_qc.validated_tier). A STATUS CHANGE is the exception — green only on 2+
independent publishers (STATUS_CHANGE_MIN_PUBLISHERS), so a single-publisher status
change at `high` drops to `medium` and is never promoted. The mergers apply this at
source; this script applies it to stores merged before 2026-09-30, including the
record copies a handoff packet's staged_actions.json carries.

A deterministic metadata repair, NOT re-research: only `tier` and `researcher_notes`
change — no value, class_out, ref, verification or `independent` flag is touched.
`low` is never promoted. Dry-run by default; --apply writes. Rebuild any affected
workbook afterwards.

Usage:
    python scripts/repair_tiers.py --staging batches/russia-gas/staging/deepsweep-r7-central-south
    python scripts/repair_tiers.py --all --apply
"""
import argparse, glob, json, os, sys, collections
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from merge_qc import (independence_qc, validated_tier, is_status_change,  # noqa: E402
                      load_sheet, STATUS_CHANGE_MIN_PUBLISHERS)


# staged_actions.json (handoff packets) carries copies of other stores' records, each
# with its own tier; these lists are re-tiered alongside `resolutions`.
ACTION_LISTS = ("status_changes", "fills", "ref_work", "new_rows")


def status_change(r, sheet):
    if (r.get("ref_col") == "__STATUS__" or r.get("class_in") == "STATUS"
            or "proposed_status" in r):
        return str(r.get("verdict") or "").lower() == "change"
    if r.get("class_in") != "FILL":      # a ref on the sheet's own value never changes it
        return False
    return is_status_change(r.get("values"), sheet, r.get("project_id") or r.get("ProjectID", ""),
                            r.get("sheet_row"))


_SRC = {}
PROMO = "tier medium -> high (one validated ref is sufficient, rule 4)."   # validated_tier's note


def source_verifs(r):
    """A carried handoff record's verifications, taken from its source store when the
    source record carries the SAME refs — packets assembled before a source was re-merged
    hold stale verifications without `name_found`. Falls back to the record's own."""
    sd = r.get("source_dir") or ""
    if "/" in sd:
        p = Path("batches") / sd.split("/", 1)[0] / "staging" / sd.split("/", 1)[1] / "staged_resolutions.json"
        if p not in _SRC:
            idx = {}
            if p.exists():
                for s in json.load(open(p)).get("resolutions") or []:
                    idx[(s.get("project_id"), s.get("ref_col"), tuple(sorted(s.get("proposed_refs") or [])))] = s.get("verifications") or []
            _SRC[p] = idx
        k = (r.get("project_id"), r.get("ref_col") or ("__STATUS__" if "proposed_status" in r else None),
             tuple(sorted(r.get("proposed_refs") or [])))
        if k in _SRC[p]:
            return _SRC[p][k]
    return r.get("verifications") or []


def repair(path, apply=False):
    doc = json.load(open(path))
    if path.endswith("staged_actions.json"):
        res = [r for k in ACTION_LISTS for r in (doc.get(k) or []) if isinstance(r, dict)]
    else:
        res = doc.get("resolutions")
    if res is None:
        return None
    meta = doc.get("meta") or {}
    scope = dict(meta.get("scope") or {})
    if not scope.get("csv"):             # pre-scope stores (Saudi ref sweeps): newest snapshot
        gas = "gas" in str(meta.get("commodity") or scope.get("tracker") or path)
        snaps = sorted((Path(__file__).resolve().parent.parent / "data").glob(
            "GGIT_gas_snapshot_*.csv" if gas else "GOIT_oil_ngl_snapshot_*.csv"))
        if snaps:
            scope["csv"] = str(snaps[-1])
    sheet = load_sheet(scope)
    c = collections.Counter()
    for r in res:
        refs = r.get("proposed_refs") or r.get("refs") or []
        tier0, notes = r.get("tier", ""), r.get("researcher_notes", "")
        chg = status_change(r, sheet)
        tier, _, notes = independence_qc(
            refs, tier0, r.get("independent", False), notes,
            high_min=STATUS_CHANGE_MIN_PUBLISHERS if chg else 1)
        if not chg:
            tier, notes = validated_tier(refs, source_verifs(r), tier, notes,
                                         cls=r.get("class_out"), ref_col=r.get("ref_col"))
        if (tier0 == "high" and PROMO in notes and (r.get("class_out") == "UNRESOLVED"
                                                  or r.get("ref_col") == "__VALIDITY__")):
            tier, notes = "medium", notes.replace(PROMO, "").replace("  ", " ").strip()
        if tier != tier0:
            c[f"{tier0}->{tier}"] += 1
            r["tier"], r["researcher_notes"] = tier, notes
    if apply and c:
        doc.setdefault("meta", {})["tiers_repaired_20260930"] = dict(c)
        json.dump(doc, open(path, "w"), indent=1, ensure_ascii=False)
    return c, len(res), sheet is not None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--staging", help="one staging dir (or one store json)")
    ap.add_argument("--all", action="store_true", help="every batches/*/staging/*/ dir")
    ap.add_argument("--apply", action="store_true", help="write (default: dry-run)")
    args = ap.parse_args()
    if args.all:
        paths = sorted(glob.glob("batches/*/staging/*/staged_resolutions.json")
                       + glob.glob("batches/*/staging/*/staged_actions.json"))
    elif args.staging:
        s = args.staging.rstrip("/")
        paths = [s] if s.endswith(".json") else [
            p for p in (os.path.join(s, "staged_resolutions.json"),
                        os.path.join(s, "staged_actions.json")) if os.path.exists(p)]
    else:
        ap.error("pass --staging <dir> or --all")

    tot = collections.Counter(); dirs = 0
    for p in paths:
        if not os.path.exists(p):
            print(f"  SKIP (no staged_resolutions.json) {p}"); continue
        out = repair(p, apply=args.apply)
        if out is None:
            print(f"  SKIP (no resolutions[]) {p}"); continue
        c, n, has_sheet = out
        if c:
            dirs += 1; tot.update(c)
            flag = "" if has_sheet else "  [no snapshot: Status fills treated as changes]"
            print(f"  {dict(c)} (of {n} units)  {p}{flag}")
    verb = "RE-TIERED" if args.apply else "WOULD RE-TIER (dry-run)"
    print(f"{verb}: {dict(tot)} across {dirs} staging dir(s)")


if __name__ == "__main__":
    main()
