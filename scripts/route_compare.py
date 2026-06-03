"""Route geometry comparison (GEM route vs a reference route).

Loads GEM route GeoJSON from the local mirror (fallback: fetch_route.sh), computes
spatial-similarity signals in a local equidistant CRS, and flags route-replacement
candidates. Geometry can be null (expansions) — every function degrades to None/{}
cleanly so the matcher simply omits geometry signals.
"""
from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path

import paths
from adapter_base import geodesic_km, geom_endpoints


# --------------------------------------------------------------------------- #
# loading / merging
# --------------------------------------------------------------------------- #
def load_gem_route(project_id: str, commodity: str | None = None) -> dict | None:
    """Return a single (Multi)LineString geojson geometry for a GEM ProjectID, or
    None (missing, null, or unfetchable). Tries the local mirror, then fetch_route.sh."""
    p = paths.gem_route_path(project_id, commodity)
    if p is None:
        p = _fetch(project_id)
    if p is None:
        return None
    try:
        gj = json.loads(Path(p).read_text())
    except Exception:
        return None
    return _featurecollection_to_geom(gj)


def _featurecollection_to_geom(gj: dict) -> dict | None:
    lines: list = []
    for feat in gj.get("features", []) or []:
        lines += _lines(feat.get("geometry"))
    if not lines:
        # some files are a bare geometry, not a FeatureCollection
        lines += _lines(gj.get("geometry"))
    return _lines_to_geom(lines)


def merge_geoms(geoms: list) -> dict | None:
    """Merge several route geometries (e.g. a network's member segments) into one."""
    lines: list = []
    for g in geoms:
        lines += _lines(g)
    return _lines_to_geom(lines)


def _lines(g: dict | None) -> list:
    if not g:
        return []
    t, c = g.get("type"), g.get("coordinates") or []
    if t == "LineString":
        return [c] if c else []
    if t == "MultiLineString":
        return [p for p in c if p]
    return []


def _lines_to_geom(lines: list) -> dict | None:
    if not lines:
        return None
    if len(lines) == 1:
        return {"type": "LineString", "coordinates": lines[0]}
    return {"type": "MultiLineString", "coordinates": lines}


def _fetch(project_id: str) -> Path | None:
    cache = paths.routes_cache() / f"{project_id}.geojson"
    if cache.exists():
        return cache
    script = paths.repo_root() / "scripts" / "fetch_route.sh"
    if not script.exists():
        return None
    try:
        subprocess.run(["bash", str(script), project_id, str(paths.routes_cache())],
                       capture_output=True, timeout=30, check=False)
    except Exception:
        return None
    hits = list(paths.routes_cache().glob(f"*{project_id}*.geojson"))
    return hits[0] if hits else (cache if cache.exists() else None)


# --------------------------------------------------------------------------- #
# metric projection + signals
# --------------------------------------------------------------------------- #
def _center(*geoms):
    xs, ys = [], []
    for g in geoms:
        for ln in _lines(g):
            for pt in ln:
                xs.append(pt[0])
                ys.append(pt[1])
    return (sum(xs) / len(xs), sum(ys) / len(ys)) if xs else None


def _to_metric(geom: dict, lon0: float, lat0: float):
    """Local azimuthal-equidistant projection (meters), centered on the data —
    accurate for distance/area locally and robust to cross-UTM-zone lines."""
    from shapely.geometry import shape
    from shapely.ops import transform as shp_transform
    from pyproj import Transformer
    aeqd = f"+proj=aeqd +lat_0={lat0} +lon_0={lon0} +datum=WGS84 +units=m +no_defs"
    tf = Transformer.from_crs("EPSG:4326", aeqd, always_xy=True)
    return shp_transform(tf.transform, shape(geom))


def endpoint_distance_km(a: dict, b: dict) -> float | None:
    aS, aE = geom_endpoints(a)
    bS, bE = geom_endpoints(b)
    if not all([aS, aE, bS, bE]):
        return None
    from pyproj import Geod
    g = Geod(ellps="WGS84")

    def d(p, q):
        return g.inv(p[0], p[1], q[0], q[1])[2] / 1000.0

    return round(min((d(aS, bS) + d(aE, bE)) / 2, (d(aS, bE) + d(aE, bS)) / 2), 2)


def geometry_signals(ref_geom: dict | None, gem_geom: dict | None, buffer_km: float = 2.0) -> dict:
    """Spatial-similarity signals between a reference route and a GEM route.
    Returns {} if either geometry is missing. Keys: iou, endpoint_km/_score,
    hausdorff_km/haus_score, length_ratio, g_score (composite)."""
    if not ref_geom or not gem_geom:
        return {}
    out: dict = {}

    ed = endpoint_distance_km(ref_geom, gem_geom)
    if ed is not None:
        out["endpoint_km"] = ed
        out["endpoint_score"] = round(math.exp(-ed / 5.0), 3)

    la, lb = geodesic_km(ref_geom), geodesic_km(gem_geom)
    if la and lb:
        out["length_ratio"] = round(min(la, lb) / max(la, lb), 3)

    ctr = _center(ref_geom, gem_geom)
    if ctr:
        try:
            ma, mb = _to_metric(ref_geom, *ctr), _to_metric(gem_geom, *ctr)
            ba, bb = ma.buffer(buffer_km * 1000), mb.buffer(buffer_km * 1000)
            union = ba.union(bb).area
            if union > 0:
                out["iou"] = round(ba.intersection(bb).area / union, 3)
            hd = ma.hausdorff_distance(mb) / 1000.0
            out["hausdorff_km"] = round(hd, 2)
            out["haus_score"] = round(math.exp(-hd / 10.0), 3)
        except Exception as e:  # projection/topology hiccup — keep the cheaper signals
            out["geom_error"] = str(e)[:120]

    comps = []
    for w, k in ((0.45, "iou"), (0.25, "endpoint_score"), (0.20, "haus_score"), (0.10, "length_ratio")):
        if k in out:
            comps.append((w, out[k]))
    if comps:
        wsum = sum(w for w, _ in comps)
        out["g_score"] = round(sum(w * v for w, v in comps) / wsum, 3)
    return out


def replacement_candidate(route_accuracy: str | None, sig: dict) -> bool:
    """GulfPub route is treated as more accurate than a low/medium GEM route. Flag
    for human review when the GEM route isn't already high-accuracy and the geometry
    is corroborated. Never edits anything."""
    if not sig:
        return False
    acc = (route_accuracy or "").strip().lower()
    if acc in ("high", "very high (within meters)"):
        return False
    return sig.get("iou", 0) >= 0.5 or sig.get("endpoint_score", 0) >= 0.7
