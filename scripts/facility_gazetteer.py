#!/usr/bin/env python3
"""Facility gazetteer — GOGET/GOGPT name→coordinate lookup for route endpoints.

An INTERNAL endpoint-anchoring aid for the route-creation workflow (§8), backed by
the trimmed snapshots written by refresh_facility_gazetteer.py:

    data/GOGET_facilities_<date>.csv    extraction fields/projects (+WKT area)
    data/GOGPT_plants_<date>.csv        oil & gas power plants

Pipelines run between / terminate at named facilities, so these let the worklist and
candidate builder:
  - resolve(name, country)  a named start/end facility -> coordinate  (rung-4 endpoints)
  - nearest(lon, lat, r)     what facility a traced/fetched endpoint sits on (snap target)
  - serves_area(line, r)     the fields/plants a corridor plausibly serves (a note)

STANDING RULE 1 (hard): GOGET/GOGPT are GEM databases. Every record returned here
carries citable=False. These anchors NEVER go in a [ref]/Route [ref] cell and NEVER
count toward the 2-independent-source corroboration tier — an anchored endpoint still
needs its own independent public source. They orient geometry internally; that's all.
"""
from __future__ import annotations

import csv
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402
from normalize import normalize_country, normalize_name  # noqa: E402

csv.field_size_limit(2 ** 24)

DATA = paths.repo_root() / "data"
_GEOD = None


def _geod():
    global _GEOD
    if _GEOD is None:
        from pyproj import Geod
        _GEOD = Geod(ellps="WGS84")
    return _GEOD


@dataclass
class Facility:
    gem_id: str
    name: str
    name_other: str
    country: str
    lat: float
    lon: float
    status: str
    source: str          # "GOGET" | "GOGPT"
    wkt: str = ""
    citable: bool = field(default=False, init=False)  # STANDING RULE 1 — never a citation

    def as_anchor(self, role: str, dist_km: float | None = None) -> dict:
        """Render as a candidates.json facility_anchor entry (provenance, not a ref)."""
        return {
            "gem_id": self.gem_id, "name": self.name, "source": self.source,
            "role": role, "lon": self.lon, "lat": self.lat,
            "dist_km": None if dist_km is None else round(dist_km, 2),
            "citable": False,
        }


def _latest_snapshot(kind: str) -> Path | None:
    """kind in {GOGET_facilities, GOGPT_plants}; newest-dated snapshot, or None."""
    hits = sorted(DATA.glob(f"{kind}_*.csv"))
    return hits[-1] if hits else None


class Gazetteer:
    def __init__(self, facilities: list[Facility]):
        self.facilities = facilities
        self._by_norm: dict[str, list[Facility]] = {}
        for f in facilities:
            for nm in (f.name, f.name_other):
                key = normalize_name(nm, drop_stopwords=True)
                if key:
                    self._by_norm.setdefault(key, []).append(f)
        self._norm_keys = list(self._by_norm)

    # -- name resolution ---------------------------------------------------- #
    def resolve(self, name: str, country: str | None = None,
                min_score: float = 88.0, limit: int = 5) -> list[dict]:
        """Fuzzy name -> ranked facility matches (rapidfuzz token_set_ratio),
        optionally country-filtered. Each hit: {..., score, citable: False}."""
        from rapidfuzz import fuzz, process
        q = normalize_name(name, drop_stopwords=True)
        if not q or not self._norm_keys:
            return []
        cf = normalize_country(country) if country else None
        matches = process.extract(q, self._norm_keys, scorer=fuzz.token_set_ratio,
                                  limit=limit * 4)
        out: list[dict] = []
        seen: set[str] = set()
        for key, score, _ in matches:
            if score < min_score:
                continue
            for f in self._by_norm[key]:
                if cf and f.country and f.country != cf:
                    continue
                if f.gem_id in seen:
                    continue
                seen.add(f.gem_id)
                out.append({**f.as_anchor("resolved"), "score": round(float(score), 1),
                            "country": f.country})
                if len(out) >= limit:
                    return out
        return out

    # -- spatial lookups ---------------------------------------------------- #
    def nearest(self, lon: float, lat: float, max_km: float = 15.0,
                limit: int = 5) -> list[dict]:
        """Facilities within max_km of a point, nearest first (great-circle)."""
        g = _geod()
        hits = []
        for f in self.facilities:
            d = g.inv(lon, lat, f.lon, f.lat)[2] / 1000.0
            if d <= max_km:
                hits.append((d, f))
        hits.sort(key=lambda t: t[0])
        return [{**f.as_anchor("near", d), "country": f.country}
                for d, f in hits[:limit]]

    def serves_area(self, line_geom: dict, max_km: float = 10.0,
                    limit: int = 20) -> list[dict]:
        """GOGET/GOGPT facilities whose point lies within max_km of a route line —
        the extraction fields / plants the corridor plausibly serves (a note only)."""
        from shapely.geometry import shape, Point
        from shapely.ops import transform as shp_transform
        from pyproj import Transformer
        try:
            line = shape(line_geom)
        except Exception:
            return []
        if line.is_empty:
            return []
        c = line.centroid
        aeqd = f"+proj=aeqd +lat_0={c.y} +lon_0={c.x} +datum=WGS84 +units=m +no_defs"
        tf = Transformer.from_crs("EPSG:4326", aeqd, always_xy=True).transform
        mline = shp_transform(tf, line)
        buf = mline.buffer(max_km * 1000)
        buf_wgs = None
        hits = []
        for f in self.facilities:
            mp = shp_transform(tf, Point(f.lon, f.lat))
            if buf.contains(mp):
                d = mline.distance(mp) / 1000.0
                hits.append((d, f))
        hits.sort(key=lambda t: t[0])
        return [{**f.as_anchor("serves", d), "country": f.country}
                for d, f in hits[:limit]]


def load_gazetteer(include_gogpt: bool = True) -> Gazetteer:
    """Load the newest GOGET (+ optional GOGPT) snapshots into one Gazetteer.
    Raises FileNotFoundError if no GOGET snapshot exists (run the refresh helper)."""
    facilities: list[Facility] = []
    kinds = [("GOGET_facilities", True)]
    if include_gogpt:
        kinds.append(("GOGPT_plants", False))
    loaded_any = False
    for kind, required in kinds:
        snap = _latest_snapshot(kind)
        if snap is None:
            if required:
                raise FileNotFoundError(
                    f"no {kind}_*.csv in {DATA} — run "
                    f"scripts/refresh_facility_gazetteer.py first")
            continue
        loaded_any = True
        for r in csv.DictReader(open(snap, newline="")):
            try:
                lat, lon = float(r["lat"]), float(r["lon"])
            except (ValueError, KeyError):
                continue
            facilities.append(Facility(
                gem_id=r.get("gem_id", ""), name=r.get("name", ""),
                name_other=r.get("name_other", ""),
                country=normalize_country(r.get("country", "")),
                lat=lat, lon=lon, status=r.get("status", ""),
                source=r.get("kind", kind.split("_")[0]),
                wkt=r.get("wkt", "")))
    if not loaded_any:
        raise FileNotFoundError(f"no gazetteer snapshots in {DATA}")
    return Gazetteer(facilities)


if __name__ == "__main__":
    import argparse
    import json
    ap = argparse.ArgumentParser(description="Query the facility gazetteer (GOGET/GOGPT).")
    ap.add_argument("--resolve", metavar="NAME", help="fuzzy-resolve a facility name")
    ap.add_argument("--country")
    ap.add_argument("--near", nargs=2, type=float, metavar=("LON", "LAT"))
    ap.add_argument("--max-km", type=float, default=15.0)
    ap.add_argument("--no-gogpt", action="store_true")
    args = ap.parse_args()

    gz = load_gazetteer(include_gogpt=not args.no_gogpt)
    print(f"loaded {len(gz.facilities)} facilities", file=sys.stderr)
    if args.resolve:
        print(json.dumps(gz.resolve(args.resolve, args.country), indent=2))
    elif args.near:
        print(json.dumps(gz.nearest(args.near[0], args.near[1], args.max_km), indent=2))
    else:
        ap.error("give --resolve NAME or --near LON LAT")
