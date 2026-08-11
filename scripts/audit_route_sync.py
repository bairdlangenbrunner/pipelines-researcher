#!/usr/bin/env python3
"""Audit the three-way route sync: RouteType <-> RouteAccuracy <-> routes repo.

CARDINAL RULE (Baird 2026-07-31): those three must ALWAYS agree. They are one
fact stated three ways, not three independent judgments:

  geojson with real coords  =>  RouteType 'Mapped route (at any accuracy)'
                                RouteAccuracy = the earned tier (any tier —
                                'very low (straight line/schematic)' is mapped)
  no geojson / empty file   =>  RouteType 'Not mapped …' / 'Unavailable …'
                                RouteAccuracy 'no route'

Run this after EVERY §8 apply (workflows.md §8 step 6c). Read-only — it reports
drift, it never writes. Repair our own rows with
`apply_route_candidates.py --backfill-route-type`.

Findings:
  A  repo has real geometry, RouteType is not 'Mapped'      (the 2026-07-30 defect)
  B  repo has real geometry, RouteAccuracy == 'no route'
  C  no live geometry, but RouteType == 'Mapped'
  D  no live geometry, but RouteAccuracy != 'no route'

RouteTypes that intentionally describe a non-route row (capacity expansion,
bidirectionality upgrade, folded into another ProjectID, network placeholder)
are exempt — listed under --show-exempt.

Usage:
  python scripts/audit_route_sync.py [--commodity gas|oil|both] [--country China]
                                     [--csv <snapshot>] [--out <dir>]
"""
import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ROUTES_REPO = REPO.parent / "GOIT-GGIT-pipeline-routes"
ROUTE_DIRS = {"gas": "gas-pipelines", "oil": "liquid-pipelines"}
MAPPED = "Mapped route (at any accuracy)"
NO_ROUTE = "no route"
# RouteTypes that describe a row which legitimately has no route of its own
EXEMPT = {"Capacity expansion only", "Bidirectionality upgrade only",
          "Included in other ProjectID", "NETWORK ROUTE"}


def coord_count(path: str) -> int:
    """Number of coordinate pairs in a geojson; 0 = empty placeholder, -1 = unreadable."""
    n = 0

    def walk(g):
        nonlocal n
        if not g:
            return
        t = g.get("type")
        if t == "FeatureCollection":
            for ft in g.get("features") or []:
                walk(ft)
        elif t == "Feature":
            walk(g.get("geometry"))
        elif t == "GeometryCollection":
            for gg in g.get("geometries") or []:
                walk(gg)
        else:
            def cc(x):
                nonlocal n
                if isinstance(x, (int, float)):
                    return
                if x and isinstance(x[0], (int, float)):
                    n += 1
                    return
                for y in x or []:
                    cc(y)
            cc(g.get("coordinates"))
    try:
        walk(json.load(open(path)))
    except Exception:
        return -1
    return n


def repo_geometry(commodity: str) -> dict:
    root = ROUTES_REPO / "data" / "individual-routes" / ROUTE_DIRS[commodity]
    if not root.is_dir():
        sys.exit(f"routes repo not found at {root} — clone/pull it first")
    out: dict = {}
    for f in glob.glob(str(root / "**" / "*.geojson"), recursive=True):
        m = re.search(r"(P\d{4,6})", os.path.basename(f))
        if m:
            out[m.group(1)] = max(out.get(m.group(1), 0), coord_count(f))
    return out


def latest_snapshot(commodity: str) -> str:
    pat = "GGIT_gas_snapshot_*.csv" if commodity == "gas" else "GOIT_oil_ngl_snapshot_*.csv"
    files = sorted(glob.glob(str(REPO / "data" / pat)))
    if not files:
        sys.exit(f"no {pat} in data/ — run ./scripts/refresh_csvs.sh")
    return files[-1]


def audit(commodity: str, args) -> int:
    import pandas as pd
    csv_path = args.csv or latest_snapshot(commodity)
    df = pd.read_csv(csv_path, header=2, low_memory=False)
    df = df[df["ProjectID"].notna()].copy()
    df["SheetRow"] = df.index + 4
    # buffer rows: pre-allocated ProjectIDs at the bottom of the tab with no
    # pipeline on them yet (gas P8038-P8100 as of 2026-07-31). They have no
    # RouteType/RouteAccuracy by design and are not drift.
    buffers = df["PipelineName"].isna()
    if buffers.any():
        print(f"  (excluding {int(buffers.sum())} buffer rows: "
              f"{df.loc[buffers, 'ProjectID'].iloc[0]}–{df.loc[buffers, 'ProjectID'].iloc[-1]})")
    df = df[~buffers]
    country_col = next(c for c in df.columns if "ountr" in c)
    if args.country:
        df = df[df[country_col].astype(str).str.contains(args.country, na=False)]

    geom = repo_geometry(commodity)
    df["repo_coords"] = df["ProjectID"].map(lambda p: geom.get(p, -1))
    live = df["repo_coords"] > 0
    exempt = df["RouteType"].isin(EXEMPT)

    # a blank RouteAccuracy is the same fact as 'no route' — on a new row the
    # cell just hasn't been filled in yet (Baird 2026-08-11)
    unrouted = df["RouteAccuracy"].fillna("").astype(str).str.strip().isin({NO_ROUTE, ""})

    checks = {
        "A  live geometry, RouteType not 'Mapped'": df[live & ~exempt & (df["RouteType"] != MAPPED)],
        "B  live geometry, RouteAccuracy 'no route'/blank": df[live & ~exempt & unrouted],
        "C  no live geometry, RouteType 'Mapped'": df[~live & (df["RouteType"] == MAPPED)],
        "D  no live geometry, RouteAccuracy is a real tier": df[~live & ~exempt & ~unrouted],
    }

    cols = ["ProjectID", "SheetRow", "PipelineName", country_col,
            "RouteType", "RouteAccuracy", "repo_coords"]
    total = 0
    print(f"\n=== {commodity.upper()}  ({len(df)} rows"
          + (f", country~{args.country}" if args.country else "")
          + f"; snapshot {Path(csv_path).name})")
    if args.show_exempt:
        print(f"  exempt RouteTypes present: {sorted(set(df.loc[exempt, 'RouteType']))}")
    for label, sub in checks.items():
        print(f"  {label}: {len(sub)}")
        total += len(sub)
        if len(sub) and args.verbose:
            print(sub[cols].to_string(index=False))
        if len(sub) and args.out:
            Path(args.out).mkdir(parents=True, exist_ok=True)
            sub[cols].to_csv(Path(args.out) / f"route_sync_{commodity}_{label[0]}.csv", index=False)
    return total


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--commodity", default="both", choices=["gas", "oil", "both"])
    ap.add_argument("--country", help="substring match on the country column")
    ap.add_argument("--csv", help="explicit snapshot (single commodity only)")
    ap.add_argument("--out", help="write per-finding CSVs to this dir")
    ap.add_argument("--show-exempt", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true", help="print every drifted row")
    args = ap.parse_args()
    if args.csv and args.commodity == "both":
        sys.exit("--csv requires a single --commodity")

    total = sum(audit(c, args) for c in
                (["gas", "oil"] if args.commodity == "both" else [args.commodity]))
    print(f"\ntotal out-of-sync rows: {total}")
    sys.exit(1 if total else 0)


if __name__ == "__main__":
    main()
