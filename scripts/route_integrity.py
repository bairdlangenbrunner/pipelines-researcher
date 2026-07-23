#!/usr/bin/env python3
"""Route-integrity QC (Leg 2 of the wiki/route QC workflow).

Checks each in-scope row's GeoJSON route (local mirror of
GOIT-GGIT-pipeline-routes, fetch_route.sh fallback) against the row's OWN sheet
attributes — catching routes drawn wrong by past researchers:

  length_ratio      geodesic length vs LengthKnownKm/LengthMergedKm,
                    flag ratio outside [0.75, 1.33]
  countries         countries the line makes landfall in (Natural Earth 1:50m
                    admin-0, >= 2 km inside a polygon to ignore border-clip
                    noise) vs CountriesOrAreas + start/end countries.
                    Offshore-lenient: sea gaps never flag; landfall in an
                    unlisted country does.
  null_geometry     no/empty geometry while RouteAccuracy says a route exists —
                    and the inverse (geometry present, RouteAccuracy 'no route')
  degenerate        <= 2 vertices (a straight stub) claiming medium+ accuracy
  endpoint_country  a route endpoint lands in a country that is neither the
                    Start nor End country (orientation-agnostic; offshore
                    endpoints are fine)

This is route *correctness* QC — geometry vs the row's own attributes. It is
NOT a revival of the permanently-dropped WKT/route-format checks (old QC
Sheet 10); no format/validity linting is done here. GulfPub route comparison
is separate future work. Flags are only staged for human review — a route is
never auto-replaced (routes-repo edits go through a human branch + PR).

One-time dependency: data/boundaries/ne_50m_admin_0_countries.shp
(Natural Earth 1:50m admin-0, public domain).

Output: <staging>/route_integrity.json, records per the ROUTEQC class
(ref_col "__ROUTEQC__") documented in docs/reference/staged_json_schema.md.

Usage:
  python scripts/route_integrity.py --csv data/GGIT_gas_snapshot_<date>.csv \
      --country Egypt --commodity gas --staging batches/egypt-gas/staging/qc/ \
      [--pids P3620,P0462] [--staged-dir <dir> ...]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402
from adapter_base import geodesic_km, geom_endpoints  # noqa: E402
from normalize import normalize_country, parse_number, split_countries  # noqa: E402
from staged_store import annotate, discover_staging_dirs, load_staged_context  # noqa: E402
from route_compare import load_gem_route  # noqa: E402

ROUTEQC_REF = "__ROUTEQC__"
BOUNDARIES = paths.repo_root() / "data" / "boundaries" / "ne_50m_admin_0_countries.shp"

LENGTH_RATIO_LO, LENGTH_RATIO_HI = 0.75, 1.33
MIN_LANDFALL_KM = 2.0          # ignore <2 km border-clip slivers (1:50m polygons)
_MEDIUM_PLUS = {"medium", "high", "very high (within meters)"}


def _s(v) -> str:
    if v is None:
        return ""
    s = str(v).strip()
    return "" if s.lower() in ("nan", "none") else s


def _record(row: dict, check: str, measured, expected, detail: str,
            severity: str = "flag", staged_note: str = "") -> dict:
    return {
        "project_id": row["ProjectID"], "sheet_row": row["SheetRow"],
        "pipeline_name": _s(row.get("PipelineName")),
        "segment_name": _s(row.get("SegmentName")),
        "route_accuracy": _s(row.get("RouteAccuracy")),
        "ref_col": ROUTEQC_REF, "class_in": "ROUTEQC", "class_out": "ROUTE_FLAG",
        "check": check, "measured": measured, "expected": expected,
        "detail": detail, "severity": severity, "staged_note": staged_note,
        # common-core so records pass merge/apply tooling untouched
        "value_cols": [], "values": {}, "primary_value_col": None,
        "primary_value": "", "current_ref": "", "proposed_refs": [],
        "verifications": [], "tier": "", "independent": False,
        "source_language": "en", "researcher_notes": "",
    }


def load_boundaries():
    """Natural Earth 1:50m admin-0 GeoDataFrame with a normalized country column.
    Public: shared by route_integrity and validate_route_candidate (§8 gate)."""
    import geopandas as gpd
    gdf = gpd.read_file(BOUNDARIES)[["NAME", "NAME_LONG", "geometry"]]
    gdf["country_norm"] = gdf["NAME"].map(normalize_country)
    return gdf


def _vertex_count(geom: dict) -> int:
    c = geom.get("coordinates") or []
    if geom.get("type") == "LineString":
        return len(c)
    return sum(len(part) for part in c)


def _lines_only(shp) -> dict | None:
    """Shapely intersection result -> (Multi)LineString geojson dict (line parts
    only — Points/GeometryCollections from border touches are dropped), or None."""
    parts = []
    for g in getattr(shp, "geoms", [shp]):
        if g.geom_type == "LineString":
            parts.append(list(g.coords))
        elif g.geom_type == "MultiLineString":
            parts.extend(list(sub.coords) for sub in g.geoms)
    if not parts:
        return None
    if len(parts) == 1:
        return {"type": "LineString", "coordinates": parts[0]}
    return {"type": "MultiLineString", "coordinates": parts}


def landfall_countries(geom: dict, boundaries, min_km: float) -> dict[str, float]:
    """{normalized country -> km of the line inside its polygon}, >= min_km only."""
    from shapely.geometry import shape
    line = shape(geom)
    out: dict[str, float] = {}
    cand = boundaries.iloc[list(boundaries.sindex.query(line, predicate="intersects"))]
    for _, poly in cand.iterrows():
        inter = _lines_only(line.intersection(poly.geometry))
        if inter is None:
            continue
        km = geodesic_km(inter) or 0.0
        if km >= min_km:
            out[poly["country_norm"]] = round(km, 1)
    return out


def point_country(pt, boundaries) -> str:
    """Normalized country a lon/lat point falls in, '' if offshore."""
    from shapely.geometry import Point
    p = Point(pt[0], pt[1])
    hits = boundaries.iloc[list(boundaries.sindex.query(p, predicate="intersects"))]
    for _, poly in hits.iterrows():
        if poly.geometry.contains(p):
            return poly["country_norm"]
    return ""


def check_row(row: dict, commodity: str, boundaries, ctx) -> tuple[list[dict], bool]:
    """-> (records, has_geometry)."""
    recs: list[dict] = []
    pid = row["ProjectID"]
    acc = _s(row.get("RouteAccuracy")).lower()
    note = annotate(ctx, pid, kind="route")
    geom = load_gem_route(pid, commodity)

    # (c) null geometry vs RouteAccuracy — both directions
    if geom is None and acc and acc != "no route":
        recs.append(_record(
            row, "null_geometry", "no usable geometry", f"RouteAccuracy = '{acc}'",
            f"route file missing/null but RouteAccuracy claims '{acc}' — either draw the "
            f"route or set RouteAccuracy to 'no route'", staged_note=note))
        return recs, False
    if geom is not None and acc == "no route":
        recs.append(_record(
            row, "null_geometry", "geometry present", "RouteAccuracy = 'no route'",
            "a route exists in the routes repo but RouteAccuracy says 'no route' — "
            "update RouteAccuracy (or the route was added for another segment)",
            severity="info", staged_note=note))
    if geom is None:
        return recs, False

    measured_km = geodesic_km(geom)
    n_vertices = _vertex_count(geom)

    # (d) degenerate line claiming medium+ accuracy
    if n_vertices <= 2 and acc in _MEDIUM_PLUS:
        recs.append(_record(
            row, "degenerate", f"{n_vertices} vertices ({measured_km} km straight line)",
            f"RouteAccuracy = '{acc}'",
            f"route is a {n_vertices}-point straight stub but claims '{acc}' accuracy — "
            f"redraw or downgrade RouteAccuracy", staged_note=note))

    # (a) geodesic length vs sheet length
    sheet_km = None
    used_col = ""
    for col in ("LengthKnownKm", "LengthMergedKm"):
        sheet_km = parse_number(_s(row.get(col)))
        if sheet_km:
            used_col = col
            break
    if sheet_km and measured_km:
        ratio = measured_km / sheet_km
        if not (LENGTH_RATIO_LO <= ratio <= LENGTH_RATIO_HI):
            recs.append(_record(
                row, "length_ratio",
                f"geodesic {measured_km:.0f} km (ratio {ratio:.2f})",
                f"{used_col} = {sheet_km:g} km",
                f"drawn route is {measured_km:.0f} km but the sheet says {sheet_km:g} km "
                f"(ratio {ratio:.2f}, allowed {LENGTH_RATIO_LO}–{LENGTH_RATIO_HI}) — "
                f"wrong route, wrong length value, or a partial segment drawn",
                staged_note=note))

    # (b) countries traversed vs sheet countries
    expected = set(split_countries(_s(row.get("CountriesOrAreas"))))
    for col in ("StartCountryOrArea", "EndCountryOrArea"):
        c = normalize_country(_s(row.get(col)))
        if c:
            expected.add(c)
    landfalls = landfall_countries(geom, boundaries, MIN_LANDFALL_KM)
    unlisted = {c: km for c, km in landfalls.items() if c not in expected}
    if unlisted and expected:
        recs.append(_record(
            row, "countries",
            "; ".join(f"{c} ({km} km)" for c, km in sorted(unlisted.items())),
            "CountriesOrAreas/start/end = " + ", ".join(sorted(expected)),
            "route makes landfall in countr(ies) the sheet never lists — wrong route "
            "or incomplete CountriesOrAreas", staged_note=note))

    # (e) endpoints inside the start/end countries (orientation-agnostic)
    start_c = normalize_country(_s(row.get("StartCountryOrArea")))
    end_c = normalize_country(_s(row.get("EndCountryOrArea")))
    allowed = {c for c in (start_c, end_c) if c}
    if allowed:
        ep = geom_endpoints(geom)
        for label, pt in zip(("first", "last"), ep):
            if not pt:
                continue
            pc = point_country(pt, boundaries)
            if pc and pc not in allowed:
                recs.append(_record(
                    row, "endpoint_country",
                    f"{label} endpoint in {pc} ({pt[1]:.3f}, {pt[0]:.3f})",
                    f"start/end = {start_c or '?'} / {end_c or '?'}",
                    f"route's {label} endpoint lands in '{pc}', which is neither the "
                    f"start nor end country — endpoint drawn wrong or start/end "
                    f"columns wrong", staged_note=note))
    return recs, True


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--csv", required=True)
    ap.add_argument("--country", required=True)
    ap.add_argument("--commodity", default="gas", choices=["gas", "oil", "ngl"])
    ap.add_argument("--staging", required=True)
    ap.add_argument("--pids", help="comma-separated subset (sample runs)")
    ap.add_argument("--staged-dir", action="append", default=[])
    args = ap.parse_args()

    if not BOUNDARIES.exists():
        sys.exit(f"missing {BOUNDARIES} — download Natural Earth 1:50m admin-0 "
                 f"(ne_50m_admin_0_countries.zip) into data/boundaries/")

    import pandas as pd
    df = pd.read_csv(args.csv, header=2, low_memory=False)
    df = df[df["PipelineName"].notna()].copy()
    df["SheetRow"] = df.index + 4
    scope = df[df["CountriesOrAreas"].fillna("").str.contains(args.country, case=False)]
    if args.pids:
        keep = {p.strip() for p in args.pids.split(",") if p.strip()}
        scope = scope[scope["ProjectID"].isin(keep)]

    staged_dirs = args.staged_dir or discover_staging_dirs(
        args.country, args.commodity, exclude=[args.staging])
    ctx = load_staged_context(staged_dirs)
    boundaries = load_boundaries()

    records: list[dict] = []
    n_with_geom = 0
    for _, row in scope.iterrows():
        row = row.to_dict()
        recs, has_geom = check_row(row, args.commodity, boundaries, ctx)
        n_with_geom += int(has_geom)
        records.extend(recs)
        if recs:
            print(f"  {row['ProjectID']}: " + ", ".join(r["check"] for r in recs),
                  file=sys.stderr)

    from collections import Counter
    out = {
        "meta": {
            "mode": "route_integrity",
            "scope": {"csv": Path(args.csv).name, "country": args.country,
                      "commodity": args.commodity, "rows": int(len(scope))},
            "staged_dirs": ctx["dirs"],
            "boundaries": BOUNDARIES.name,
            "n_rows_with_geometry": n_with_geom,
            "check_counts": dict(Counter(r["check"] for r in records)),
            "severity_counts": dict(Counter(r["severity"] for r in records)),
        },
        "records": records,
    }
    staging = Path(args.staging)
    staging.mkdir(parents=True, exist_ok=True)
    path = staging / "route_integrity.json"
    path.write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print(f"wrote {path} — {len(records)} flags over {len(scope)} rows "
          f"({n_with_geom} with geometry); {out['meta']['check_counts']}")


if __name__ == "__main__":
    main()
