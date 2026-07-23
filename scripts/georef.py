#!/usr/bin/env python3
"""Georeference hand-picked map pixels -> lon/lat (workflow §8, digitization rung).

Fits a pixel->(lon,lat) transform from ground control points (GCPs) read off a
published map image, then applies it to traced pixel polylines. This is the ONLY
place a digitized coordinate may come from — the trace itself is pixels; lon/lat
exits only through the fitted transform (or an independently sourced endpoint,
handled downstream by build_route_candidate.py). No raster warping — numpy +
pyproj only, no rasterio/GDAL.

Transform: affine (order 1, min 3 / want >=4 GCPs) or full quadratic (order 2,
min 6 / want >=8). Pixel coords are centered/scaled before the least-squares fit
so the design-matrix condition number is meaningful; collinear or clustered GCPs
are refused. Fit quality is measured geodesically (pyproj.Geod): per-GCP residual
km, RMSE, max, and leave-one-out RMSE (n >= 5) — an affine through 3 points fits
itself perfectly, so LOO is the honest number.

Input contracts (agent-authored while reading the map):
  gcps.json   [{"px": [x, y], "lonlat": [lon, lat], "name": "Cairo",
                "source_ref": "<where the lonlat came from — REQUIRED>"}, ...]
              Every GCP lonlat must be independently sourced (geocoded city,
              labeled junction, coastline feature) — never read off the map.
  trace.json  {"image": "map1.png", "polylines": [[[x, y], ...], ...],
               "notes": "..."}

Output: GeoJSON FeatureCollection (one feature, LineString/MultiLineString,
EPSG:4326 [lon,lat], 6 dp) with the georef report embedded in properties.
Exits nonzero when the fit fails --max-rmse-km or GCP minimums — but still
writes the output (georef.pass = false) so partial work is preserved; the
caller then falls to the digitization-packet path (see docs/sops/route_creation.md).

Usage:
  python scripts/georef.py --gcps packets/P1234/gcps.json \
      --trace packets/P1234/trace.json --order 1 --max-rmse-km 10 \
      --out <staging>/candidate_intermediate/P1234_traced.geojson \
      [--report packets/P1234/georef_report.json] [--densify-km 25]
  python scripts/georef.py --selftest
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MIN_GCPS = {1: 3, 2: 6}          # hard minimums per order
WANT_GCPS = {1: 4, 2: 8}         # below this -> warning
MAX_CONDITION = 1e4              # normalized design matrix; collinear -> huge/inf
LOO_MIN = 5                      # leave-one-out needs headroom over the minimum


class GeorefError(ValueError):
    """Fit refused (too few GCPs, collinear/clustered GCPs, bad input)."""


def _design(px_norm, order: int):
    import numpy as np
    x, y = px_norm[:, 0], px_norm[:, 1]
    cols = [np.ones_like(x), x, y]
    if order == 2:
        cols += [x * x, x * y, y * y]
    return np.column_stack(cols)


class Georef:
    """A fitted pixel->(lon,lat) transform + fit diagnostics."""

    def __init__(self, order: int, mean, scale, coef_lon, coef_lat):
        self.order = order
        self._mean, self._scale = mean, scale
        self._coef_lon, self._coef_lat = coef_lon, coef_lat
        self.n_gcps: int = 0
        self.residuals_km: list[float] = []
        self.rmse_km: float | None = None
        self.max_residual_km: float | None = None
        self.loo_rmse_km: float | None = None
        self.condition: float | None = None

    def apply(self, pixels) -> list[list[float]]:
        """[[x, y], ...] -> [[lon, lat], ...] (6 dp)."""
        import numpy as np
        px = np.asarray(pixels, dtype=float)
        if px.ndim != 2 or px.shape[1] != 2:
            raise GeorefError("pixels must be an Nx2 array of [x, y]")
        A = _design((px - self._mean) / self._scale, self.order)
        lon = A @ self._coef_lon
        lat = A @ self._coef_lat
        return [[round(float(o), 6), round(float(a), 6)] for o, a in zip(lon, lat)]

    def polyline(self, pixels, densify_km: float | None = None) -> list[list[float]]:
        """Transform a traced pixel polyline; optionally insert great-circle
        intermediate points wherever consecutive vertices are > densify_km apart
        (long straight pixel runs on small-scale maps cut corners otherwise)."""
        pts = self.apply(pixels)
        if not densify_km or len(pts) < 2:
            return pts
        from pyproj import Geod
        g = Geod(ellps="WGS84")
        out = [pts[0]]
        for a, b in zip(pts, pts[1:]):
            dist_km = g.inv(a[0], a[1], b[0], b[1])[2] / 1000.0
            if dist_km > densify_km:
                n = int(dist_km // densify_km)
                mids = g.npts(a[0], a[1], b[0], b[1], n)
                out += [[round(lo, 6), round(la, 6)] for lo, la in mids]
            out.append(b)
        return out

    def report(self) -> dict:
        return {
            "order": self.order,
            "n_gcps": self.n_gcps,
            "rmse_km": self.rmse_km,
            "loo_rmse_km": self.loo_rmse_km,
            "max_residual_km": self.max_residual_km,
            "residuals_km": self.residuals_km,
            "condition": self.condition,
        }


def _fit_raw(px, lonlat, order: int):
    """Core least-squares fit (px, lonlat already numpy). -> Georef (no residuals)."""
    import numpy as np
    mean = px.mean(axis=0)
    scale = px.std(axis=0)
    scale[scale == 0] = 1.0
    A = _design((px - mean) / scale, order)
    cond = float(np.linalg.cond(A))
    if not np.isfinite(cond) or cond > MAX_CONDITION:
        raise GeorefError(
            f"GCPs too collinear/clustered for an order-{order} fit "
            f"(condition {cond:.3g} > {MAX_CONDITION:g}) — spread GCPs across the map")
    coef_lon, *_ = np.linalg.lstsq(A, lonlat[:, 0], rcond=None)
    coef_lat, *_ = np.linalg.lstsq(A, lonlat[:, 1], rcond=None)
    g = Georef(order, mean, scale, coef_lon, coef_lat)
    g.condition = round(cond, 2)
    return g


def fit_transform(gcps: list[dict], order: int = 1) -> Georef:
    """Fit pixel->(lon,lat) from GCP dicts ({"px": [x,y], "lonlat": [lon,lat], ...}).
    Residuals are geodesic km at each GCP; leave-one-out RMSE when n >= LOO_MIN."""
    import numpy as np
    from pyproj import Geod

    if order not in MIN_GCPS:
        raise GeorefError(f"order must be 1 or 2, got {order}")
    if len(gcps) < MIN_GCPS[order]:
        raise GeorefError(
            f"order-{order} fit needs >= {MIN_GCPS[order]} GCPs, got {len(gcps)}")
    try:
        px = np.asarray([g["px"] for g in gcps], dtype=float)
        lonlat = np.asarray([g["lonlat"] for g in gcps], dtype=float)
    except (KeyError, ValueError) as e:
        raise GeorefError(f"bad GCP record (need px + lonlat): {e}") from e
    if np.any(np.abs(lonlat[:, 0]) > 180) or np.any(np.abs(lonlat[:, 1]) > 90):
        raise GeorefError("GCP lonlat out of range (need [lon, lat], not [lat, lon]?)")

    g = _fit_raw(px, lonlat, order)
    geod = Geod(ellps="WGS84")
    pred = np.asarray(g.apply(px))
    res = [geod.inv(p[0], p[1], k[0], k[1])[2] / 1000.0 for p, k in zip(pred, lonlat)]
    g.n_gcps = len(gcps)
    g.residuals_km = [round(r, 3) for r in res]
    g.rmse_km = round(float(np.sqrt(np.mean(np.square(res)))), 3)
    g.max_residual_km = round(max(res), 3)

    if len(gcps) >= max(LOO_MIN, MIN_GCPS[order] + 1):
        loo = []
        for i in range(len(gcps)):
            keep = [j for j in range(len(gcps)) if j != i]
            try:
                gi = _fit_raw(px[keep], lonlat[keep], order)
            except GeorefError:
                continue  # dropping this GCP degenerates the rest — skip
            p = gi.apply(px[i:i + 1])[0]
            loo.append(geod.inv(p[0], p[1], lonlat[i][0], lonlat[i][1])[2] / 1000.0)
        if loo:
            g.loo_rmse_km = round(float(np.sqrt(np.mean(np.square(loo)))), 3)
    return g


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _load_gcps(path: Path) -> list[dict]:
    gcps = json.loads(path.read_text())
    if not isinstance(gcps, list):
        raise GeorefError(f"{path}: expected a JSON list of GCP records")
    for i, g in enumerate(gcps):
        if not str(g.get("source_ref", "")).strip():
            raise GeorefError(
                f"{path}: GCP #{i} ({g.get('name', '?')}) has no source_ref — every "
                f"GCP lonlat must be independently sourced, never read off the map")
    return gcps


def _polylines_to_geom(polys: list[list[list[float]]]) -> dict:
    polys = [p for p in polys if len(p) >= 2]
    if not polys:
        raise GeorefError("trace produced no polyline with >= 2 points")
    if len(polys) == 1:
        return {"type": "LineString", "coordinates": polys[0]}
    return {"type": "MultiLineString", "coordinates": polys}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gcps", help="gcps.json (px + lonlat + name + source_ref)")
    ap.add_argument("--trace", help="trace.json (image + pixel polylines)")
    ap.add_argument("--order", type=int, default=1, choices=[1, 2])
    ap.add_argument("--max-rmse-km", type=float, default=10.0,
                    help="fit fails (exit 1, pass=false) above this RMSE")
    ap.add_argument("--densify-km", type=float, default=None,
                    help="insert great-circle points on runs longer than this")
    ap.add_argument("--out", help="output GeoJSON path")
    ap.add_argument("--report", help="also write the georef report JSON here")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        _selftest()
        return
    if not (args.gcps and args.trace and args.out):
        ap.error("--gcps, --trace and --out are required (or --selftest)")

    gcps = _load_gcps(Path(args.gcps))
    trace = json.loads(Path(args.trace).read_text())
    polylines = trace.get("polylines") or []

    g = fit_transform(gcps, order=args.order)
    ok = g.rmse_km is not None and g.rmse_km <= args.max_rmse_km
    # LOO is the honest number when we have it — a self-fit through few points lies
    if ok and g.loo_rmse_km is not None and g.loo_rmse_km > 2 * args.max_rmse_km:
        ok = False
    if len(gcps) < WANT_GCPS[args.order]:
        print(f"warning: only {len(gcps)} GCPs (want >= {WANT_GCPS[args.order]} "
              f"for order {args.order})", file=sys.stderr)

    geom = _polylines_to_geom(
        [g.polyline(p, densify_km=args.densify_km) for p in polylines])
    report = g.report()
    report["pass"] = bool(ok)
    report["max_rmse_km"] = args.max_rmse_km
    report["image"] = trace.get("image", "")

    fc = {"type": "FeatureCollection",
          "features": [{"type": "Feature", "properties": {"georef": report},
                        "geometry": geom}]}
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(fc, indent=1))
    if args.report:
        Path(args.report).write_text(json.dumps(report, indent=1))

    from adapter_base import geodesic_km  # noqa: E402 — sibling import, lazy
    km = geodesic_km(geom)
    print(f"wrote {out} — {km or '?'} km traced; order {g.order}, {g.n_gcps} GCPs, "
          f"RMSE {g.rmse_km} km (LOO {g.loo_rmse_km}), max {g.max_residual_km} km "
          f"-> {'PASS' if ok else 'FAIL'}")
    if not ok:
        print("fit FAILED the RMSE gate — deliver a digitization packet "
              "(docs/sops/route_creation.md) alongside this partial output",
              file=sys.stderr)
        sys.exit(1)


# --------------------------------------------------------------------------- #
# selftest — synthetic map over Egypt, deterministic
# --------------------------------------------------------------------------- #
def _selftest() -> None:
    from pyproj import Geod
    geod = Geod(ellps="WGS84")

    # ground truth: a mildly rotated/scaled affine, lon 25-35, lat 22-32 (Egypt-ish)
    def true_tf(x, y):
        return (25.0 + 0.0020 * x + 0.00012 * y,
                32.0 - 0.0018 * y + 0.00008 * x)

    # 6 well-spread GCPs + deterministic sub-pixel "noise"
    px_pts = [(120, 90), (2050, 140), (1900, 1750), (200, 1800), (1050, 950), (600, 400)]
    noise = [(0.4, -0.3), (-0.5, 0.2), (0.3, 0.5), (-0.2, -0.4), (0.5, 0.1), (-0.3, 0.3)]
    gcps = []
    for i, ((x, y), (nx, ny)) in enumerate(zip(px_pts, noise)):
        lon, lat = true_tf(x, y)
        gcps.append({"px": [x + nx, y + ny], "lonlat": [lon, lat],
                     "name": f"gcp{i}", "source_ref": "selftest"})

    g = fit_transform(gcps, order=1)
    assert g.rmse_km is not None and g.rmse_km < 1.0, f"RMSE too high: {g.rmse_km}"
    assert g.loo_rmse_km is not None and g.loo_rmse_km < 2.0, f"LOO: {g.loo_rmse_km}"

    # a traced polyline must land within ~1 km of ground truth
    trace_px = [(300, 300), (800, 700), (1400, 1200), (1800, 1600)]
    for (x, y), (lon, lat) in zip(trace_px, g.apply(list(trace_px))):
        tlon, tlat = true_tf(x, y)
        d_km = geod.inv(lon, lat, tlon, tlat)[2] / 1000.0
        assert d_km < 1.0, f"trace point off by {d_km:.2f} km"

    # densification: a 2-point line ~1000 km long must gain intermediate points
    dense = g.polyline([(120, 90), (2050, 1750)], densify_km=50)
    assert len(dense) > 10, f"densify produced only {len(dense)} points"

    # collinear GCPs must be refused
    bad = [{"px": [i * 100, i * 100], "lonlat": true_tf(i * 100, i * 100),
            "name": f"c{i}", "source_ref": "selftest"} for i in range(4)]
    try:
        fit_transform(bad, order=1)
        raise AssertionError("collinear GCPs were not refused")
    except GeorefError:
        pass

    # too few GCPs for order 2 must be refused
    try:
        fit_transform(gcps[:4], order=2)
        raise AssertionError("order-2 with 4 GCPs was not refused")
    except GeorefError:
        pass

    print("georef selftest OK — affine RMSE %.3f km, LOO %.3f km, cond %.1f"
          % (g.rmse_km, g.loo_rmse_km, g.condition))


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    main()
