#!/usr/bin/env python3
"""Discovery step 1: build the dedup context + the `args` payload for the
`country-discovery` workflow.

Discovery (docs/sops/discovery.md) needs the FULL roster of existing GEM rows for the
scope — every status, including operating/cancelled — so search agents can pre-filter
and the consolidator can match-to-existing FIRST (a candidate matching an existing row
under another name is an OtherEnglishNames suggestion, not a new row).

Writes <staging>/discovery_context.json and prints the workflow `args` JSON
(the workflow has no filesystem access, so the roster rides in `args`):

    { repo, staging, commodity, country, roster: ["P#### | name | aka=... | a->b | status | specs", ...] }

Usage:
    python scripts/build_discovery_context.py --tracker gas --country "Iraq" \
        --staging batches/iraq-gas/staging/annual/
    # optionally --csv data/GGIT_gas_snapshot_<date>.csv (default: latest snapshot for the tracker)
"""
import argparse, glob, json, os, sys
import pandas as pd

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _latest_snapshot(tracker: str) -> str:
    pat = "GGIT_gas*" if tracker == "gas" else "GOIT_oil*"
    hits = sorted(glob.glob(os.path.join(REPO, "data", pat + ".csv")), key=os.path.getmtime)
    if not hits:
        raise SystemExit(f"no {pat}.csv snapshot in data/ — run ./scripts/refresh_csvs.sh")
    return hits[-1]


def _col(cols, *names):
    low = {c.lower(): c for c in cols}
    for n in names:
        if n.lower() in low:
            return low[n.lower()]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tracker", required=True, choices=["oil", "gas"])
    ap.add_argument("--country", required=True)
    ap.add_argument("--staging", required=True, help="staging dir (created if missing)")
    ap.add_argument("--csv", help="snapshot CSV (default: latest data/ snapshot for the tracker)")
    ap.add_argument("--out", help="also write the args JSON here (default: stdout only)")
    args = ap.parse_args()

    csv_path = args.csv or _latest_snapshot(args.tracker)
    df = pd.read_csv(csv_path, header=2, low_memory=False)
    C = df.columns
    c_pid = _col(C, "ProjectID")
    df = df[df[c_pid].notna() & df[c_pid].astype(str).str.startswith("P")]
    c_ctry = _col(C, "CountriesOrAreas", "Countries")
    in_scope = df[df[c_ctry].astype(str).str.split(",").apply(
        lambda parts: any(p.strip().lower() == args.country.lower() for p in parts))]
    if in_scope.empty:
        raise SystemExit(f"no rows for country={args.country!r} in {csv_path}")

    c_name = _col(C, "PipelineName")
    c_seg = _col(C, "SegmentName")
    c_aka = _col(C, "OtherEnglishNames")
    c_stat = _col(C, "Status")
    c_len = _col(C, "LengthKnown")
    c_dia = _col(C, "Diameter")
    c_cap = _col(C, "Capacity")
    c_wiki = _col(C, "Wiki")
    c_sloc = _col(C, "StartLocation", "StartState/Province", "StartCountryOrArea")
    c_eloc = _col(C, "EndLocation", "EndState/Province", "EndCountryOrArea")

    def cell(r, c):
        if not c:
            return "?"
        v = r.get(c, "")
        return "?" if (pd.isna(v) or v == "") else str(v).strip()

    records, roster = [], []
    for _, r in in_scope.iterrows():
        rec = {"project_id": cell(r, c_pid), "pipeline_name": cell(r, c_name),
               "segment_name": "" if cell(r, c_seg) == "?" else cell(r, c_seg),
               "other_names": "" if cell(r, c_aka) == "?" else cell(r, c_aka),
               "status": cell(r, c_stat), "start": cell(r, c_sloc), "end": cell(r, c_eloc),
               "length": cell(r, c_len), "diameter": cell(r, c_dia),
               "capacity": cell(r, c_cap), "wiki": "" if cell(r, c_wiki) == "?" else cell(r, c_wiki)}
        records.append(rec)
        aka = f" aka={rec['other_names']}" if rec["other_names"] else ""
        seg = f" / {rec['segment_name']}" if rec["segment_name"] else ""
        roster.append(f"{rec['project_id']} | {rec['pipeline_name']}{seg}{aka} | "
                      f"{rec['start']}->{rec['end']} | status={rec['status']} | "
                      f"len={rec['length']} dia={rec['diameter']} cap={rec['capacity']}")

    os.makedirs(args.staging, exist_ok=True)
    ctx = {"scope": {"tracker": args.tracker, "country": args.country,
                     "csv": os.path.basename(csv_path)},
           "n_existing": len(records), "existing": records}
    ctx_path = os.path.join(args.staging.rstrip("/"), "discovery_context.json")
    json.dump(ctx, open(ctx_path, "w"), indent=1)

    payload = {"repo": REPO, "staging": args.staging.rstrip("/"),
               "commodity": args.tracker, "country": args.country, "roster": roster}
    out = json.dumps(payload, indent=1)
    if args.out:
        open(args.out, "w").write(out)
    print(out)
    print(f"\n# wrote {ctx_path}; {len(records)} existing rows in scope "
          f"(all statuses, for match-to-existing)", file=sys.stderr)


if __name__ == "__main__":
    main()
