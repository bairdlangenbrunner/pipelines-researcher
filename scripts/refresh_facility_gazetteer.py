#!/usr/bin/env python3
"""Refresh the GOGET/GOGPT facility gazetteer snapshots (workflow §8).

Pulls trimmed, route-creation-relevant columns from the sibling gem-db-ops repo
into small, committed snapshots under data/:

  data/GOGET_facilities_<date>.csv   extraction plants/projects (name, coords, WKT area)
  data/GOGPT_plants_<date>.csv       oil & gas power plants (name, coords)

Why snapshots (not live reads): the gem-db-ops exports are large and refresh on
their own cadence; route creation needs a stable, self-contained gazetteer keyed
to a known date, like the PHMSA / GulfPub pattern. The big raw exports stay in
gem-db-ops (gitignored here).

Country is NOT taken from the export (it carries only numeric country_id with no
name table); it is reverse-geocoded from each facility's point against the same
Natural Earth 1:50m admin-0 shapefile the route QC uses — so gazetteer country
names match everything else in the pipeline. Offshore points get "".

STANDING RULE 1: GOGET/GOGPT are GEM databases. This gazetteer is an internal
endpoint-anchoring aid ONLY — never a [ref] citation, never a corroboration
source. facility_gazetteer.py stamps every record citable=False.

Sources (in sibling ../gem-db-ops):
  goget/gem_export_goget_tables/public.plant.csv           (entity: name, lat, lng, status)
  goget/gem_export_goget_tables/public.goget_project.csv   (which plants are GOGET extraction)
  goget/gem_export_goget_tables/public.project_geospatial.csv  (WKT field/block polygons)
  gogpt/gem_export_gogpt.csv                               (GOGPT export; optional — run gogpt/pull.py first)

Usage:
  python scripts/refresh_facility_gazetteer.py                 # both, date = today
  python scripts/refresh_facility_gazetteer.py --goget-only
  python scripts/refresh_facility_gazetteer.py --date 20260722
  python scripts/refresh_facility_gazetteer.py --no-country    # skip reverse-geocode (faster)
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date, datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402

csv.field_size_limit(2 ** 24)  # GOGET WKT polygons blow past the default field limit

DB_OPS = paths.repo_root().parent / "gem-db-ops"
GOGET_DIR = DB_OPS / "goget" / "gem_export_goget_tables"
GOGPT_CSV = DB_OPS / "gogpt" / "gem_export_gogpt.csv"
DATA = paths.repo_root() / "data"
BOUNDARIES = DATA / "boundaries" / "ne_50m_admin_0_countries.shp"

OUT_COLS = ["gem_id", "name", "name_other", "country", "lat", "lon", "status", "kind", "wkt"]


def _num(v):
    try:
        f = float(str(v).strip())
        return f if -1e6 < f < 1e6 else None
    except (ValueError, TypeError):
        return None


def _first_json_scalar(v: str) -> str:
    """GEM 'search' columns hold JSON arrays like '[\"Operating\"]' or '[239]'."""
    v = (v or "").strip()
    if not v or v in ("[]", "null"):
        return ""
    try:
        parsed = json.loads(v)
        if isinstance(parsed, list) and parsed:
            return str(parsed[0])
        return str(parsed)
    except (ValueError, TypeError):
        return v


def _load_csv(path: Path) -> list[dict]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _reverse_geocoder():
    """-> fn(lon, lat) -> normalized country name ('' offshore). Uses the NE
    shapefile + a spatial index; None if geopandas/boundaries unavailable."""
    if not BOUNDARIES.exists():
        print(f"  (no {BOUNDARIES.name}; skipping country reverse-geocode)", file=sys.stderr)
        return None
    try:
        import geopandas as gpd
        from shapely.geometry import Point
        from normalize import normalize_country
    except Exception as e:
        print(f"  (reverse-geocode unavailable: {e})", file=sys.stderr)
        return None
    gdf = gpd.read_file(BOUNDARIES)[["NAME", "geometry"]]
    gdf["cn"] = gdf["NAME"].map(normalize_country)
    sindex = gdf.sindex

    def geocode(lon, lat):
        p = Point(lon, lat)
        for i in sindex.query(p, predicate="intersects"):
            row = gdf.iloc[i]
            if row.geometry.contains(p):
                return row["cn"]
        return ""

    return geocode


def refresh_goget(date_str: str, geocode) -> Path:
    plants = {p["id"]: p for p in _load_csv(GOGET_DIR / "public.plant.csv")}
    goget_ids = {g["project_id"] for g in _load_csv(GOGET_DIR / "public.goget_project.csv")}
    wkt_by_pid: dict[str, str] = {}
    for g in _load_csv(GOGET_DIR / "public.project_geospatial.csv"):
        if g.get("wkt"):
            wkt_by_pid[g["project_id"]] = g["wkt"]

    rows = []
    for pid in goget_ids:
        p = plants.get(pid)
        if not p:
            continue
        lat, lon = _num(p.get("latitude")), _num(p.get("longitude"))
        if lat is None or lon is None:
            continue
        rows.append({
            "gem_id": pid,
            "name": (p.get("name") or "").strip(),
            "name_other": _first_json_scalar(p.get("nameOther", "")),
            "country": geocode(lon, lat) if geocode else "",
            "lat": round(lat, 6), "lon": round(lon, 6),
            "status": _first_json_scalar(p.get("statusSearch", "")),
            "kind": "GOGET",
            "wkt": wkt_by_pid.get(pid, ""),
        })
    return _write(DATA / f"GOGET_facilities_{date_str}.csv", rows, "GOGET")


def refresh_gogpt(date_str: str, geocode) -> Path | None:
    if not GOGPT_CSV.exists():
        print(f"  GOGPT export not found ({GOGPT_CSV}); run gem-db-ops/gogpt/pull.py "
              f"first (needs GEM_READONLY_DB_URL). Skipping GOGPT.", file=sys.stderr)
        return None
    src = _load_csv(GOGPT_CSV)

    def pick(row, *names):
        for n in names:
            if n in row and (row[n] or "").strip():
                return row[n].strip()
        return ""

    rows = []
    for p in src:
        lat = _num(pick(p, "Latitude", "latitude"))
        lon = _num(pick(p, "Longitude", "longitude"))
        if lat is None or lon is None:
            continue
        rows.append({
            "gem_id": pick(p, "GEM unit ID", "GEM location ID", "unit_id", "id"),
            "name": pick(p, "Plant name", "Plant", "name"),
            "name_other": pick(p, "Other plant names", "nameOther"),
            "country": geocode(lon, lat) if geocode else pick(p, "Country/area", "Country"),
            "lat": round(lat, 6), "lon": round(lon, 6),
            "status": pick(p, "Status", "status"),
            "kind": "GOGPT",
            "wkt": "",
        })
    return _write(DATA / f"GOGPT_plants_{date_str}.csv", rows, "GOGPT")


def _write(path: Path, rows: list[dict], label: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=OUT_COLS)
        w.writeheader()
        w.writerows(rows)
    n_wkt = sum(1 for r in rows if r["wkt"])
    n_country = sum(1 for r in rows if r["country"])
    print(f"wrote {path.name} — {len(rows)} {label} facilities "
          f"({n_country} with country, {n_wkt} with WKT area)")
    return path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date", help="snapshot date stamp (default: today, YYYYMMDD)")
    ap.add_argument("--goget-only", action="store_true")
    ap.add_argument("--gogpt-only", action="store_true")
    ap.add_argument("--no-country", action="store_true",
                    help="skip reverse-geocoding country (faster; country left blank)")
    args = ap.parse_args()

    if not GOGET_DIR.exists() and not args.gogpt_only:
        sys.exit(f"missing {GOGET_DIR} — clone/pull the sibling gem-db-ops repo, or "
                 f"pass --gogpt-only")

    date_str = args.date or date.fromtimestamp(
        datetime.now(timezone.utc).timestamp()).strftime("%Y%m%d")
    geocode = None if args.no_country else _reverse_geocoder()

    if not args.gogpt_only:
        refresh_goget(date_str, geocode)
    if not args.goget_only:
        refresh_gogpt(date_str, geocode)


if __name__ == "__main__":
    main()
