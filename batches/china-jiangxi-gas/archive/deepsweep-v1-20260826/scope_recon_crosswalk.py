#!/usr/bin/env python3
"""Scope the China-wide GulfPub crosswalk down to this sweep's 18 rows.

`reconcile.py` is run per COUNTRY, so a province sweep gets a country-wide
match_diff: 118 overlaps / 2 additions / 4 ambiguous across all 1,041 China gas
rows. `build_ref_workbook._recon_view` does NOT filter by ProjectID — it writes
every crosswalk row — so dropping the raw file into the sweep dir would put 117
out-of-scope China decisions into a Jiangxi deliverable. That is scope creep in
the review surface, and it buries the one row that matters.

Scoped down, the answer is a clean RECORDED NEGATIVE, which is a finding and must
survive to the workbook rather than being represented by an empty tab:
  * GulfPub's 120 China gas records mention Jiangxi ZERO times.
  * 17 of the 18 in-scope rows land in `gem_only` — no reference counterpart.
  * The single "overlap" (P4782) is a FALSE POSITIVE and is annotated as such here.

The country-wide file stays untouched in recon-gulfpub-20260826/ as the audit trail;
this writes only the scoped view the workbook consumes.

    python scope_recon_crosswalk.py
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "recon_gulfpub_crosswalk.json"

# The P4782 match is geographically impossible and was adjudicated by hand: GulfPub's
# Cang-Zi Line runs lon 116.21-116.56 / lat 39.22-39.89 (Beijing/Hebei), while P4782
# Nanchang-Fengcheng sits near lon 115.9 / lat 28.7 -- ~1,240 km apart, route IoU 0.0.
# The composite reached 0.4748 on name/attribute similarity alone.
FALSE_POSITIVE = {
    "P4782": "NOT A MATCH (hand-adjudicated). GulfPub's Cang-Zi Line is a Beijing/Hebei "
             "line at lon 116.21-116.56 / lat 39.22-39.89; P4782 Nanchang-Fengcheng is at "
             "~lon 115.9 / lat 28.7 -- ~1,240 km away, route IoU 0.0. The 0.4748 composite "
             "is name/attribute similarity with no geometric support. No GulfPub corroboration "
             "for this row; treat as gem_only. Do not act on any value in this row.",
}


def main() -> None:
    cw = json.loads(SRC.read_text())
    pids = {u["project_id"] for u in json.loads((HERE / "worklist.json").read_text())["units"]}

    before = {k: len(cw[k]) for k in ("overlaps", "additions", "ambiguous")}
    for key in ("overlaps", "additions", "ambiguous"):
        cw[key] = [r for r in cw[key] if r.get("gem_pid") in pids]

    for r in cw["overlaps"]:
        note = FALSE_POSITIVE.get(r.get("gem_pid"))
        if note:
            r["action"] = note
            r["disposition"] = "FALSE_POSITIVE"
            r["status_conflict"] = ""      # a non-match cannot conflict on status
            r["diam_flag"] = ""
            r["len_flag"] = ""

    d = cw.setdefault("diagnostics", {})
    d["scope"] = "Jiangxi provincial grid, 18 operating rows"
    d["scoped_from_country_run"] = before
    d["recorded_negative"] = (
        "GulfPub's 120 China gas records mention Jiangxi zero times; 17 of 18 in-scope rows "
        "are gem_only and the 1 apparent overlap is a hand-adjudicated false positive. So "
        "GulfPub offers NO corroboration for any Jiangxi grid row. This is a recorded "
        "negative, not a null run: the matcher is healthy (100% of reference records named "
        "AND routed, 97.4% of the GEM pool routed, country-wide overlap rate 98.3%), so the "
        "absence is about GulfPub's coverage of inland provincial grids, not about matching."
    )
    SRC.write_text(json.dumps(cw, ensure_ascii=False, indent=1))
    after = {k: len(cw[k]) for k in ("overlaps", "additions", "ambiguous")}
    print(f"scoped {before} -> {after}")
    for r in cw["overlaps"]:
        print(f"  {r['gem_pid']}  {r.get('disposition')}  {r.get('ref_name')}")


if __name__ == "__main__":
    main()
