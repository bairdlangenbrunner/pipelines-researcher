#!/usr/bin/env python3
"""Derive the `args` payload for the `critical-deep-sweep` workflow from a ref-sweep worklist.

The workflow itself has no filesystem access, so the in-scope ProjectID list and the
duplicate-detection roster must be passed in as `args`. This reads the worklist (for the
authoritative in-scope PIDs + the snapshot it was built from) and the GEM snapshot CSV
(for the per-pipeline spec descriptors), and prints a JSON object ready to hand to the
Workflow tool as `args`:

    { repo, staging, commodity, country, pids: [...], roster: ["P#### | name | a->b | len/dia/cap | status", ...] }

Usage:
    python scripts/build_deepsweep_args.py --staging batches/staging/ref-sweep-gas-saudi-arabia/
    # optionally --out batches/staging/.../deepsweep_args.json
"""
import argparse, json, os, sys
import pandas as pd

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _col(cols, *names):
    """First column in `cols` matching one of `names` (case-insensitive exact)."""
    low = {c.lower(): c for c in cols}
    for n in names:
        if n.lower() in low:
            return low[n.lower()]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--staging", required=True, help="ref-sweep staging dir (has worklist.json)")
    ap.add_argument("--out", help="also write the JSON here (default: stdout only)")
    ap.add_argument("--status-review", action="store_true",
                    help="annual-update mode: subagents also stage a per-segment status verdict "
                         "(confirm/change/stale/unclear) as status_reviews in each shard")
    args = ap.parse_args()

    staging = args.staging.rstrip("/")
    wl = json.load(open(os.path.join(staging, "worklist.json")))
    scope = wl["scope"]
    country = scope.get("country", "")
    csv_name = scope["csv"]
    commodity = "gas" if "GGIT" in csv_name else ("oil" if "GOIT" in csv_name else "")

    # in-scope PIDs, in worklist order, deduped
    pids, seen = [], set()
    for u in wl["units"]:
        pid = u.get("project_id")
        if pid and pid not in seen:
            seen.add(pid); pids.append(pid)

    # enrich a duplicate-detection roster from the snapshot the worklist was built on
    df = pd.read_csv(os.path.join(REPO, "data", csv_name), header=2, low_memory=False)
    C = df.columns
    c_pid = _col(C, "ProjectID")
    c_name = _col(C, "PipelineName")
    c_len = _col(C, "LengthKnown")
    c_dia = _col(C, "Diameter")
    c_cap = _col(C, "Capacity")
    c_stat = _col(C, "Status")
    c_upd = _col(C, "LastUpdated")
    c_sloc = _col(C, "StartLocation", "StartState/Province", "StartCountryOrArea")
    c_eloc = _col(C, "EndState/Province", "EndCountryOrArea")
    by_pid = {str(r[c_pid]): r for _, r in df.iterrows()}

    def cell(r, c):
        if not c:
            return "?"
        v = r.get(c, "")
        if pd.isna(v) or v == "":
            return "?"
        return str(v).strip()

    roster = []
    for pid in pids:
        r = by_pid.get(pid)
        if r is None:
            roster.append(f"{pid} | (not in snapshot) | ?->? | ? | ?")
            continue
        roster.append(
            f"{pid} | {cell(r, c_name)} | {cell(r, c_sloc)}->{cell(r, c_eloc)} | "
            f"len={cell(r, c_len)} dia={cell(r, c_dia)} cap={cell(r, c_cap)} | "
            f"status={cell(r, c_stat)} | updated={cell(r, c_upd)}"
        )

    payload = {
        "repo": REPO,
        "staging": staging,
        "commodity": commodity,
        "country": country,
        "pids": pids,
        "roster": roster,
    }
    if args.status_review:
        payload["status_review"] = True
    out = json.dumps(payload, indent=1)
    if args.out:
        open(args.out, "w").write(out)
    print(out)
    print(f"\n# {len(pids)} pids, commodity={commodity}, country={country!r}", file=sys.stderr)


if __name__ == "__main__":
    main()
