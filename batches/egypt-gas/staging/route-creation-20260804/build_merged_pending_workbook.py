"""Build the single merged PENDING-routes workbook for Egypt gas (Baird 2026-08-04).

Unions the two route-creation staging dirs into one review surface, keeping only
what is still actionable:

  - ROUTE_CANDIDATE: August pass only, records without an `applied` stamp.
    Excluded: the July 40, the August 10 replacements (applied 2026-08-04,
    routes merge 752ab5d3) and the August 13 no-route candidates (applied
    2026-08-05, routes merge a2fa41c8) — all live in the routes repo + sheet.
    As of 2026-08-05 that leaves ZERO pending candidates, so the workbook is
    the partials surface only.
  - ROUTE_PARTIAL: August 4 + July 15, deduped on ProjectID with the AUGUST
    record winning (P8022/P8023 were re-researched in the August pass) -> 17.

The merged staging dir is a derived VIEW written OUTSIDE batches/ (so
staged_summary / handoff auto-discovery never double-count these records);
the two real staging dirs remain the canonical pending state.

Usage:
  python batches/egypt-gas/staging/route-creation-20260804/build_merged_pending_workbook.py \
      --workdir /tmp/somewhere --output batches/egypt-gas/deliverables/<stamp>.xlsx
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

AUG = Path(__file__).resolve().parent
JUL = AUG.parent / "route-creation"
ROOT = AUG.parents[3]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workdir", required=True,
                    help="scratch dir for the derived merged staging (NOT under batches/)")
    ap.add_argument("--output", required=True, help="deliverable xlsx path")
    args = ap.parse_args()

    aug = json.loads((AUG / "staged_resolutions.json").read_text())
    jul = json.loads((JUL / "staged_resolutions.json").read_text())

    cands = [r for r in aug["resolutions"]
             if r.get("class_out") == "ROUTE_CANDIDATE" and not r.get("applied")]

    partials = {r["project_id"]: dict(r, merged_from="route-creation (2026-07-30 pass)")
                for r in jul["resolutions"] if r.get("class_out") == "ROUTE_PARTIAL"}
    for r in aug["resolutions"]:          # August wins on overlap (P8022/P8023)
        if r.get("class_out") == "ROUTE_PARTIAL":
            partials[r["project_id"]] = dict(
                r, merged_from="route-creation-20260804 (ENTSOG pass)")

    merged = {
        "meta": dict(aug["meta"], note=(
            "MERGED PENDING VIEW built by build_merged_pending_workbook.py — unions "
            "route-creation/ (July) + route-creation-20260804/ (August), applied "
            "records dropped, July P8022/P8023 partials superseded by the August "
            "re-research. The two source staging dirs stay canonical.")),
        "resolutions": cands + sorted(partials.values(),
                                      key=lambda r: r["project_id"]),
    }
    work = Path(args.workdir)
    work.mkdir(parents=True, exist_ok=True)
    (work / "staged_resolutions.json").write_text(
        json.dumps(merged, indent=1, ensure_ascii=False))
    print(f"merged: {len(cands)} pending candidates + {len(partials)} partials -> {work}")

    for cmd in ([sys.executable, str(ROOT / "scripts/build_ref_workbook.py"),
                 "--staging", str(work), "--output", args.output],
                [sys.executable, str(ROOT / "scripts/recalc.py"), args.output]):
        r = subprocess.run(cmd)
        if r.returncode != 0:
            sys.exit(r.returncode)


if __name__ == "__main__":
    main()
