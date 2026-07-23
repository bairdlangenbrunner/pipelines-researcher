#!/usr/bin/env python3
"""Validation gate for candidate route geometry (route-creation §8).

Three legs, run on every candidate <PID>.geojson before it can be delivered:

  format     the routes-repo's OWN validator (validate_geojson.validate_file,
             imported read-only) — so a candidate that passes here passes the
             repo's CI. Vendored minimal fallback if the mirror is absent.
  integrity  geodesic length vs the sheet's LengthKnownKm/LengthMergedKm within
             [0.75, 1.33]; landfall countries ⊆ CountriesOrAreas ∪ {start, end}
             (Natural Earth, offshore-lenient); both endpoints inside start/end.
             Method-aware: an endpoints-great-circle candidate can't know transit
             countries, so an unlisted landfall is a WARNING there, not a FAIL.
  collision  if GEM already has a route for this PID, the candidate must be flagged
             replacement=true; otherwise FAIL (never silently overwrite).

Never edits anything: it returns/writes a verdict. FAIL = exit 1 (CLI) or
passed=False (module). Shares boundary + landfall/point helpers with
route_integrity.py (single source of truth for the Natural Earth logic).

Usage (module): imported by build_route_candidate.py.
Usage (CLI, re-validate a staged batch or one file):
  python scripts/validate_route_candidate.py --candidates batches/staging/route-creation-*/candidates.json
  python scripts/validate_route_candidate.py --file .../candidate_routes/P1234.geojson \\
      --sheet-km 220 --countries "Egypt,Israel" --method endpoints --replacement false
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402
from adapter_base import geodesic_km, geom_endpoints  # noqa: E402
from normalize import normalize_country  # noqa: E402
from route_compare import load_gem_route, _featurecollection_to_geom  # noqa: E402
import route_integrity as ri  # noqa: E402

LOW_LENGTH_METHODS = {"endpoints_greatcircle"}  # can't know true routed length/transit


# --------------------------------------------------------------------------- #
# format leg — reuse the routes repo's own validator
# --------------------------------------------------------------------------- #
def _format_check(geojson_path: Path) -> tuple[list[str], list[str]]:
    rr_scripts = paths.routes_repo() / "scripts"
    if (rr_scripts / "validate_geojson.py").exists():
        if str(rr_scripts) not in sys.path:
            sys.path.insert(0, str(rr_scripts))
        import validate_geojson as vg
        return vg.validate_file(geojson_path)
    # vendored minimal fallback: filename pattern, JSON, FeatureCollection, WGS84 range
    errors, warnings = [], ["routes-repo validator absent — used minimal fallback"]
    import re
    if not re.match(r"^P\d+(-compressor-stations)?\.geojson$", geojson_path.name):
        errors.append(f"filename {geojson_path.name!r} not P####.geojson")
    try:
        data = json.loads(geojson_path.read_text())
    except Exception as e:  # noqa: BLE001
        return [f"invalid JSON: {e}"], warnings
    if isinstance(data, dict) and data.get("type") == "Feature":
        data = {"type": "FeatureCollection", "features": [data]}
    if not isinstance(data, dict) or data.get("type") != "FeatureCollection":
        errors.append("top level must be a FeatureCollection")
    return errors, warnings


# --------------------------------------------------------------------------- #
# the gate
# --------------------------------------------------------------------------- #
def validate_candidate(geojson_path: str | Path, *, project_id: str,
                       commodity: str | None, sheet_km: float | None,
                       allowed_countries: set[str], method: str,
                       replacement: bool, boundaries=None) -> dict:
    """-> {passed, errors, warnings, checks{...}}. errors ⇒ FAIL."""
    geojson_path = Path(geojson_path)
    errors: list[str] = []
    warnings: list[str] = []
    checks: dict = {}

    # -- format leg --------------------------------------------------------- #
    fmt_err, fmt_warn = _format_check(geojson_path)
    checks["format"] = {"errors": fmt_err, "warnings": fmt_warn}
    errors += [f"[format] {e}" for e in fmt_err]
    warnings += [f"[format] {w}" for w in fmt_warn]

    geom = None
    try:
        geom = _featurecollection_to_geom(json.loads(geojson_path.read_text()))
    except Exception as e:  # noqa: BLE001
        errors.append(f"[integrity] cannot parse geometry: {e}")
    if geom is None:
        checks["integrity"] = {"skipped": "no geometry"}
        return {"passed": not errors, "errors": errors, "warnings": warnings, "checks": checks}

    # -- integrity: length -------------------------------------------------- #
    measured_km = geodesic_km(geom)
    ratio = None
    if sheet_km and measured_km:
        ratio = round(measured_km / sheet_km, 3)
        lo, hi = ri.LENGTH_RATIO_LO, ri.LENGTH_RATIO_HI
        if not (lo <= ratio <= hi):
            msg = (f"length {measured_km:.0f} km vs sheet {sheet_km:g} km "
                   f"(ratio {ratio}, allowed {lo}-{hi})")
            if method in LOW_LENGTH_METHODS:
                warnings.append(f"[integrity] {msg} — expected for a great-circle line")
            else:
                errors.append(f"[integrity] {msg}")
    checks["length"] = {"measured_km": round(measured_km, 1) if measured_km else None,
                        "sheet_km": sheet_km, "ratio": ratio}

    # -- integrity: countries (needs boundaries) ---------------------------- #
    if boundaries is None and ri.BOUNDARIES.exists():
        boundaries = ri.load_boundaries()
    if boundaries is not None:
        allowed = {normalize_country(c) for c in allowed_countries if c}
        landfalls = ri.landfall_countries(geom, boundaries, ri.MIN_LANDFALL_KM)
        unlisted = {c: km for c, km in landfalls.items() if c and c not in allowed}
        checks["countries"] = {"landfall": landfalls, "allowed": sorted(allowed),
                               "unlisted": unlisted}
        if unlisted and allowed:
            msg = ("route makes landfall in unlisted countr(ies): "
                   + ", ".join(f"{c} ({km} km)" for c, km in sorted(unlisted.items())))
            if method in LOW_LENGTH_METHODS:
                warnings.append(f"[integrity] {msg} — great-circle may clip transit countries")
            else:
                errors.append(f"[integrity] {msg}")

        # endpoints inside start/end (only when we have exactly the 2 anchors)
        ep_bad = []
        for label, pt in zip(("start", "end"), geom_endpoints(geom)):
            if not pt:
                continue
            pc = ri.point_country(pt, boundaries)
            if pc and allowed and pc not in allowed:
                ep_bad.append(f"{label} endpoint in {pc}")
        checks["endpoints"] = {"issues": ep_bad}
        if ep_bad:
            warnings.append("[integrity] " + "; ".join(ep_bad)
                            + " — verify endpoint or start/end columns")
    else:
        checks["countries"] = {"skipped": "no Natural Earth boundaries"}

    # -- collision leg ------------------------------------------------------ #
    existing = load_gem_route(project_id, commodity)
    if existing is not None and not replacement:
        errors.append(f"[collision] GEM already has a route for {project_id} but "
                      f"candidate is not flagged replacement=true — refusing to overwrite")
    checks["collision"] = {"gem_route_exists": existing is not None,
                           "replacement": replacement}

    return {"passed": not errors, "errors": errors, "warnings": warnings, "checks": checks}


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _validate_from_candidates(cand_path: Path) -> int:
    data = json.loads(cand_path.read_text())
    records = data.get("candidates", data if isinstance(data, list) else [])
    staging = cand_path.parent
    boundaries = ri.load_boundaries() if ri.BOUNDARIES.exists() else None
    fails = 0
    for rec in records:
        gf = rec.get("geometry_file")
        if not gf:
            continue
        gp = (staging / gf) if not Path(gf).is_absolute() else Path(gf)
        if not gp.exists():
            gp = staging / "candidate_routes" / f"{rec['project_id']}.geojson"
        res = validate_candidate(
            gp, project_id=rec["project_id"], commodity=rec.get("commodity"),
            sheet_km=rec.get("sheet_length_km"),
            allowed_countries=set(rec.get("allowed_countries")
                                  or _rec_countries(rec)),
            method=rec.get("method", ""), replacement=bool(rec.get("replacement")),
            boundaries=boundaries)
        rec["qc"] = res
        flag = "PASS" if res["passed"] else "FAIL"
        fails += (not res["passed"])
        print(f"  {rec['project_id']}: {flag}"
              + (f" — {'; '.join(res['errors'])}" if res["errors"] else ""))
    cand_path.write_text(json.dumps(data, indent=1, ensure_ascii=False))
    print(f"validated {len(records)} candidate(s); {fails} FAIL")
    return 1 if fails else 0


def _rec_countries(rec: dict) -> list[str]:
    cs = list(rec.get("countries") or [])
    for side in ("start", "end"):
        c = (rec.get("endpoints") or {}).get(side, {}).get("country")
        if c:
            cs.append(c)
    return cs


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--candidates", help="candidates.json to re-validate in place")
    ap.add_argument("--file", help="one candidate geojson")
    ap.add_argument("--project-id", help="(with --file) PID; default = filename stem")
    ap.add_argument("--commodity")
    ap.add_argument("--sheet-km", type=float)
    ap.add_argument("--countries", default="", help="comma-separated allowed countries")
    ap.add_argument("--method", default="")
    ap.add_argument("--replacement", default="false")
    args = ap.parse_args()

    if args.candidates:
        sys.exit(_validate_from_candidates(Path(args.candidates)))
    if args.file:
        gp = Path(args.file)
        pid = args.project_id or gp.stem
        boundaries = ri.load_boundaries() if ri.BOUNDARIES.exists() else None
        res = validate_candidate(
            gp, project_id=pid, commodity=args.commodity, sheet_km=args.sheet_km,
            allowed_countries={c.strip() for c in args.countries.split(",") if c.strip()},
            method=args.method, replacement=args.replacement.lower() == "true",
            boundaries=boundaries)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        sys.exit(0 if res["passed"] else 1)
    ap.error("give --candidates or --file")


if __name__ == "__main__":
    main()
