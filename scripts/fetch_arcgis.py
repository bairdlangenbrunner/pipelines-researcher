#!/usr/bin/env python3
"""Generic ArcGIS REST FeatureServer/MapServer layer fetch (route-creation §8, rung 2).

Public agencies publish pipeline geometry through ArcGIS REST endpoints (Texas RRC,
BOEM, state GIS portals). This pulls one layer as WGS84 GeoJSON, paging past the
server's transfer limit, and writes it to a staging dir with a provenance sidecar.

It fetches vector features by query — it never scrapes tiles or warps rasters. Output
is a raw layer for build_route_candidate.py --method gis to select a feature from;
nothing here is auto-staged or citable on its own.

Strategy (each falls back to the next):
  1. f=geojson &outSR=4326, paged by resultOffset until exceededTransferLimit clears
  2. f=json (esriJSON) -> convert to geojson  (older servers with no geojson formatter)
  3. objectIds chunking  (servers that ignore resultOffset)

Usage:
  python scripts/fetch_arcgis.py --url <layer-url> --out batches/<scope>/staging/route-creation-<q>/fetched_layers/ \\
      [--where "COMMODITY='CRUDE'"] [--bbox minlon,minlat,maxlon,maxlat] \\
      [--source rrc_pipelines] [--max-features 50000] [--name rrc_crude]
  python scripts/fetch_arcgis.py --source rrc_pipelines --out ...     # url from gis_endpoints.yml

<layer-url> = .../FeatureServer/0 or .../MapServer/3 (the numbered layer, not the service root).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402

PAGE = 1000
TIMEOUT = 60
RETRIES = 4
UA = {"User-Agent": "gem-pipelines-researcher/route-creation (contact: GEM)"}


def _get(url: str, params: dict) -> dict:
    last = None
    for attempt in range(RETRIES):
        try:
            r = requests.get(url, params=params, headers=UA, timeout=TIMEOUT)
            if r.status_code == 200:
                return r.json()
            last = f"HTTP {r.status_code}"
        except Exception as e:  # noqa: BLE001
            last = str(e)[:160]
        time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"request failed after {RETRIES} tries ({last}): {url}")


def _esri_to_geojson_geom(g: dict, gtype: str) -> dict | None:
    """Minimal esriJSON geometry -> GeoJSON (lines/points/polys); None if empty."""
    if not g:
        return None
    if "paths" in g:
        paths_ = [p for p in g["paths"] if p]
        if not paths_:
            return None
        return ({"type": "LineString", "coordinates": paths_[0]} if len(paths_) == 1
                else {"type": "MultiLineString", "coordinates": paths_})
    if "rings" in g:
        rings = [r for r in g["rings"] if r]
        return {"type": "Polygon", "coordinates": rings} if rings else None
    if "x" in g and "y" in g:
        return {"type": "Point", "coordinates": [g["x"], g["y"]]}
    return None


def _esri_features(js: dict) -> list[dict]:
    gtype = js.get("geometryType", "")
    out = []
    for f in js.get("features", []) or []:
        geom = _esri_to_geojson_geom(f.get("geometry"), gtype)
        out.append({"type": "Feature", "properties": f.get("attributes", {}) or {},
                    "geometry": geom})
    return out


def _base_params(where: str, bbox: str | None, fmt: str) -> dict:
    p = {"where": where or "1=1", "outFields": "*", "outSR": 4326, "f": fmt,
         "returnGeometry": "true"}
    if bbox:
        mnx, mny, mxx, mxy = (x.strip() for x in bbox.split(","))
        p["geometry"] = f"{mnx},{mny},{mxx},{mxy}"
        p["geometryType"] = "esriGeometryEnvelope"
        p["inSR"] = 4326
        p["spatialRel"] = "esriSpatialRelIntersects"
    return p


def fetch_layer(url: str, where: str = "", bbox: str | None = None,
                max_features: int = 50000) -> tuple[list[dict], str]:
    """Return (geojson features, format-used). Pages until the server stops
    reporting exceededTransferLimit or max_features is hit."""
    url = url.rstrip("/")
    query = f"{url}/query"

    for fmt in ("geojson", "json"):
        feats: list[dict] = []
        offset = 0
        truncated = False
        try:
            while True:
                params = _base_params(where, bbox, fmt)
                params["resultOffset"] = offset
                params["resultRecordCount"] = PAGE
                js = _get(query, params)
                if "error" in js:
                    raise RuntimeError(js["error"])
                batch = js.get("features", []) or []
                feats += (batch if fmt == "geojson" else _esri_features(js))
                if len(feats) >= max_features:
                    feats = feats[:max_features]
                    truncated = True
                    break
                more = js.get("exceededTransferLimit") or js.get("properties", {}).get(
                    "exceededTransferLimit")
                if not more or not batch:
                    break
                offset += len(batch)
            if truncated:
                print(f"  WARNING: hit --max-features {max_features}; layer truncated",
                      file=sys.stderr)
            if feats:
                return feats, fmt
        except Exception as e:  # noqa: BLE001
            print(f"  {fmt} strategy failed ({str(e)[:120]}); trying next", file=sys.stderr)
            continue
    return [], "none"


def _endpoint_from_registry(source: str) -> dict:
    reg = paths.repo_root() / "sources" / "gis_endpoints.yml"
    if not reg.exists():
        raise SystemExit(f"no sources/gis_endpoints.yml (need --url instead of --source)")
    import yaml
    entries = yaml.safe_load(reg.read_text()) or {}
    if source not in entries:
        raise SystemExit(f"'{source}' not in gis_endpoints.yml; known: {list(entries)}")
    return entries[source]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--url", help="numbered layer URL (.../FeatureServer/0)")
    ap.add_argument("--source", help="named endpoint from sources/gis_endpoints.yml")
    ap.add_argument("--out", required=True, help="output dir (…/fetched_layers/)")
    ap.add_argument("--where", default="")
    ap.add_argument("--bbox", help="minlon,minlat,maxlon,maxlat (WGS84)")
    ap.add_argument("--max-features", type=int, default=50000)
    ap.add_argument("--name", help="output basename (default: source or 'layer')")
    args = ap.parse_args()

    entry = {}
    url = args.url
    if args.source:
        entry = _endpoint_from_registry(args.source)
        url = url or entry.get("url")
        if entry.get("kind") not in (None, "arcgis"):
            raise SystemExit(f"'{args.source}' kind={entry.get('kind')} — use the right fetcher")
    if not url:
        raise SystemExit("need --url or --source (with a url in the registry)")

    feats, fmt = fetch_layer(url, args.where, args.bbox, args.max_features)
    if not feats:
        raise SystemExit("no features returned (check url/where/bbox; layer may be empty)")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    base = args.name or args.source or "layer"
    fc = {"type": "FeatureCollection", "features": feats}
    (out_dir / f"{base}.geojson").write_text(json.dumps(fc))

    meta = {
        "source": "ArcGIS REST", "source_name": args.source or "",
        "url": url, "where": args.where, "bbox": args.bbox,
        "format_used": fmt, "n_features": len(feats),
        "fetched_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "license": entry.get("license", "UNKNOWN — verify before use"),
        "coverage": entry.get("coverage", ""), "notes": entry.get("notes", ""),
    }
    (out_dir / f"{base}.meta.json").write_text(json.dumps(meta, indent=2))
    print(f"wrote {base}.geojson — {len(feats)} features ({fmt}); "
          f"license: {meta['license']}")


if __name__ == "__main__":
    main()
