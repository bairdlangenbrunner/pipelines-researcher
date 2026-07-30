#!/usr/bin/env python3
"""Build a route-creation worklist (workflow §8, step 1).

Scopes the tracker rows that need route geometry (weak/absent RouteAccuracy),
groups them by ProjectID (routes-repo files are per-PID; a multi-segment network
becomes one merged candidate), and gathers every input the source ladder can use:

  - sheet facts: rows, summed length, countries, Start/End location text + country
  - existing GEM route presence + its geodesic length (→ replacement framing)
  - prior staged __ROUTE__ suggestions from sweeps (donate sourced endpoints)
  - GulfPub geometry-sidecar hits from recon runs (rung-1 shortcut)
  - facility-gazetteer resolutions for Start/End location text (GOGET/GOGPT
    name→coord anchors — flagged citable:false, endpoint hints only, NEVER a ref)

Writes <staging>/worklist.json. Reads a FRESH snapshot (header=2); never writes the
sheet or routes repo. No geometry is produced here — that's build_route_candidate.py.

Usage:
  python scripts/build_route_worklist.py --csv data/GGIT_gas_snapshot_<date>.csv \\
      --country Egypt --commodity gas --staging batches/egypt-gas/staging/route-creation/ \\
      [--include-medium] [--pids P1234,P5678] [--no-gazetteer]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402
from adapter_base import geodesic_km  # noqa: E402
from normalize import normalize_country, parse_number, split_countries  # noqa: E402
from route_compare import load_gem_route  # noqa: E402
from staged_store import discover_staging_dirs, load_staged_context  # noqa: E402

# +"medium" with --include-medium. `very low (straight line/schematic)` is a REAL sheet
# value (added GEM-side; 1,428 rows carried it as of the 2026-07-28 re-pull, 911 gas + 517
# oil, largely re-graded from `low`). Omitting it silently excluded the very rows this
# worklist exists to fix — the worst geometry in the tracker — so it is eligible by
# definition, not by option.
ELIGIBLE_ACCURACY = {"", "no route", "very low (straight line/schematic)", "low"}


def _s(v) -> str:
    if v is None:
        return ""
    s = str(v).strip()
    return "" if s.lower() in ("nan", "none") else s


def _gulfpub_hits(pid: str) -> list[dict]:
    """Recon-run GulfPub sidecar matches for this PID (ref_id + whether it has
    geometry). Best-effort across batches/*/staging/recon-*/."""
    hits = []
    batches = paths.repo_root() / "batches"
    for run in sorted(batches.glob("*/staging/recon-*")):
        md = run / "match_diff.json"
        sc = run / "geometry_sidecar.json"
        if not md.exists():
            continue
        try:
            diff = json.loads(md.read_text())
        except Exception:  # noqa: BLE001
            continue
        sidecar_keys = set()
        if sc.exists():
            try:
                sidecar_keys = set(json.loads(sc.read_text()).keys())
            except Exception:  # noqa: BLE001
                pass
        for ov in diff.get("overlaps", []) or []:
            gem = ov.get("gem", {})
            pids = set(gem.get("project_ids") or []) | {gem.get("project_id")}
            if pid in pids:
                ref = ov.get("ref", {})
                rid = ref.get("ref_id", "")
                hits.append({"recon_dir": f"{run.parent.parent.name}/{run.name}", "ref_id": rid,
                             "has_geometry": bool(ref.get("has_geometry")
                                                  and rid in sidecar_keys),
                             "confidence": ov.get("confidence", ""),
                             "ref_name": ref.get("name", "")})
    return hits


def _prior_suggestions(ctx, pid: str) -> list[dict]:
    """Prior staged __ROUTE__ suggestion for this PID (from sweeps), if any —
    donates already-sourced endpoints to the endpoints/traced rungs."""
    entry = (ctx.get("route_staged", {}) or {}).get(pid) if ctx else None
    r = entry.get("record") if entry else None
    if not r:
        return []
    return [{k: r.get(k) for k in (
        "class_out", "start_name", "start_lat", "start_lon",
        "end_name", "end_lat", "end_lon", "corridor_desc",
        "suggested_route_accuracy")}]


def _anchor(gz, name: str, country: str, role: str) -> list[dict]:
    if not gz or not name:
        return []
    try:
        return [{**h, "role": role} for h in gz.resolve(name, country, limit=2)]
    except Exception:  # noqa: BLE001
        return []


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--country", required=True)
    ap.add_argument("--commodity", default="gas", choices=["gas", "oil", "ngl"])
    ap.add_argument("--staging", required=True)
    ap.add_argument("--include-medium", action="store_true")
    ap.add_argument("--pids", help="comma-separated subset (overrides accuracy filter)")
    ap.add_argument("--no-gazetteer", action="store_true")
    args = ap.parse_args()

    import pandas as pd
    df = pd.read_csv(args.csv, header=2, low_memory=False)
    df = df[df["PipelineName"].notna()].copy()
    df["SheetRow"] = df.index + 4
    scope = df[df["CountriesOrAreas"].fillna("").str.contains(args.country, case=False)]

    eligible = set(ELIGIBLE_ACCURACY) | ({"medium"} if args.include_medium else set())
    if args.pids:
        keep = {p.strip() for p in args.pids.split(",") if p.strip()}
        scope = scope[scope["ProjectID"].isin(keep)]
    else:
        scope = scope[scope["RouteAccuracy"].fillna("").str.strip().str.lower().isin(eligible)]

    # facility gazetteer (optional / graceful-absent)
    gz = None
    gz_snapshot = ""
    if not args.no_gazetteer:
        try:
            from facility_gazetteer import load_gazetteer, _latest_snapshot
            gz = load_gazetteer()
            snap = _latest_snapshot("GOGET_facilities")
            gz_snapshot = snap.name if snap else ""
        except Exception as e:  # noqa: BLE001
            print(f"  (facility gazetteer unavailable: {e}); continuing without anchors",
                  file=sys.stderr)

    staged_dirs = discover_staging_dirs(args.country, args.commodity, exclude=[args.staging])
    ctx = load_staged_context(staged_dirs)

    units = []
    for pid, grp in scope.groupby("ProjectID"):
        rows = grp.to_dict("records")
        countries = sorted({c for r in rows for c in split_countries(_s(r.get("CountriesOrAreas")))})
        sheet_km = sum(parse_number(_s(r.get("LengthMergedKm")))
                       or parse_number(_s(r.get("LengthKnownKm"))) or 0 for r in rows) or None
        r0 = rows[0]
        start = {"location": _s(r0.get("StartLocation")),
                 "country": normalize_country(_s(r0.get("StartCountryOrArea")))}
        end = {"location": _s(r0.get("EndLocation")),
               "country": normalize_country(_s(r0.get("EndCountryOrArea")))}

        existing = load_gem_route(pid, args.commodity)
        anchors = (_anchor(gz, start["location"], start["country"], "start")
                   + _anchor(gz, end["location"], end["country"], "end"))

        units.append({
            "project_id": pid,
            "sheet_rows": [int(r["SheetRow"]) for r in rows],
            "pipeline_name": _s(r0.get("PipelineName")),
            "segment_names": [_s(r.get("SegmentName")) for r in rows if _s(r.get("SegmentName"))],
            "commodity": args.commodity,
            "countries": countries,
            "start": start, "end": end,
            "sheet_length_km": round(sheet_km, 1) if sheet_km else None,
            "current_route_accuracy": _s(r0.get("RouteAccuracy")).lower(),
            # current sheet values for the route provenance columns — the candidate
            # stages APPEND-style proposed values (never overwrites what's there)
            "current_route_notes": _s(r0.get("RouteNotes")),
            "current_route_creator": _s(r0.get("RouteCreator")),
            "current_route_ref": _s(r0.get("Route [ref]")),
            "existing_route": {"present": existing is not None,
                               "geodesic_km": round(geodesic_km(existing), 1)
                               if existing else None},
            "prior_suggestions": _prior_suggestions(ctx, pid),
            "gulfpub_hits": _gulfpub_hits(pid),
            "facility_anchors": anchors,
        })

    units.sort(key=lambda u: u["project_id"])
    out = {
        "meta": {
            "mode": "route-creation",
            "scope": {"csv": Path(args.csv).name, "country": args.country,
                      "commodity": args.commodity, "rows": int(len(scope)),
                      "project_ids": len(units)},
            "include_medium": args.include_medium,
            "eligible_accuracy": sorted(eligible),
            "gazetteer_snapshot": gz_snapshot,
            "staged_dirs": ctx["dirs"],
        },
        "units": units,
    }
    staging = Path(args.staging)
    staging.mkdir(parents=True, exist_ok=True)
    (staging / "worklist.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))

    n_existing = sum(u["existing_route"]["present"] for u in units)
    n_gulf = sum(1 for u in units if any(h["has_geometry"] for h in u["gulfpub_hits"]))
    n_anchor = sum(1 for u in units if u["facility_anchors"])
    print(f"wrote {staging / 'worklist.json'} — {len(units)} PIDs "
          f"({n_existing} with an existing GEM route → replacement candidates; "
          f"{n_gulf} with a GulfPub geometry hit; {n_anchor} with facility anchors)")


if __name__ == "__main__":
    main()
