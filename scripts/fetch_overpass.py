#!/usr/bin/env python3
"""Fetch OSM pipeline geometry via the Overpass API (route-creation §8, rung 2).

Pulls `man_made=pipeline` ways (+ their member relations) for an area or bbox,
stitches connected ways with shapely linemerge, and writes GeoJSON where EVERY
feature carries ODbL provenance:

    properties = {source: "OSM", license: "ODbL", osm_type, osm_id, osm_ids,
                  attribution: "© OpenStreetMap contributors", ...osm tags}

That provenance is MANDATORY and must survive into candidates.json, the staged
record, and the workbook's License column — OSM is ODbL, and whether it can ship
in a GEM tracker is Baird's licensing call at review, so it is never laundered into
an unlabelled coordinate. Gaps between ways are kept as separate MultiLineString
parts; disconnected ways are NEVER bridged (no fabricated pipe).

Usage:
  python scripts/fetch_overpass.py --area "Egypt" --substance gas \\
      --out batches/staging/.../fetched_layers/ [--name egypt_gas_osm]
  python scripts/fetch_overpass.py --bbox 24,22,37,32 --out ...
  # --substance filters on the OSM `substance` tag (gas|oil|...); omit for all pipelines
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

MIRRORS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
]
TIMEOUT = 180
RETRIES = 3
UA = {"User-Agent": "gem-pipelines-researcher/route-creation (contact: GEM)"}


def _run_query(ql: str) -> dict:
    last = None
    for attempt in range(RETRIES):
        for mirror in MIRRORS:
            try:
                r = requests.post(mirror, data={"data": ql}, headers=UA, timeout=TIMEOUT)
                if r.status_code == 200:
                    return r.json()
                last = f"HTTP {r.status_code} @ {mirror}"
            except Exception as e:  # noqa: BLE001
                last = f"{str(e)[:120]} @ {mirror}"
        time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"Overpass failed after {RETRIES}×{len(MIRRORS)} tries ({last})")


def _build_ql(area: str | None, bbox: str | None, substance: str | None) -> str:
    filt = f'["man_made"="pipeline"]'
    if substance:
        filt += f'["substance"="{substance}"]'
    if area:
        return (f'[out:json][timeout:{TIMEOUT}];'
                f'area["name"="{area}"]["admin_level"~"2|4"]->.a;'
                f'(way{filt}(area.a);relation{filt}(area.a););'
                f'out geom;')
    if bbox:
        mnx, mny, mxx, mxy = (x.strip() for x in bbox.split(","))
        b = f"{mny},{mnx},{mxy},{mxx}"  # Overpass wants S,W,N,E
        return (f'[out:json][timeout:{TIMEOUT}];'
                f'(way{filt}({b});relation{filt}({b}););'
                f'out geom;')
    raise SystemExit("need --area or --bbox")


def _way_line(el: dict) -> list | None:
    geom = el.get("geometry")
    if not geom:
        return None
    coords = [[p["lon"], p["lat"]] for p in geom if "lon" in p and "lat" in p]
    return coords if len(coords) >= 2 else None


def _collect_lines(js: dict) -> list[tuple[list, dict]]:
    """-> [(coords, {osm_type, osm_id, tags})]; relation members flattened to ways."""
    lines = []
    for el in js.get("elements", []) or []:
        t = el.get("type")
        if t == "way":
            c = _way_line(el)
            if c:
                lines.append((c, {"osm_type": "way", "osm_id": el.get("id"),
                                  "tags": el.get("tags", {})}))
        elif t == "relation":
            rtags = el.get("tags", {})
            for m in el.get("members", []) or []:
                if m.get("type") == "way" and m.get("geometry"):
                    c = [[p["lon"], p["lat"]] for p in m["geometry"]
                         if "lon" in p and "lat" in p]
                    if len(c) >= 2:
                        lines.append((c, {"osm_type": "relation", "osm_id": el.get("id"),
                                          "tags": rtags}))
    return lines


def _stitch(lines: list[tuple[list, dict]]) -> list[dict]:
    """linemerge connected ways; each output feature keeps the osm_ids that fed it.
    Never bridges gaps — disconnected pieces stay separate features."""
    from shapely.geometry import LineString, MultiLineString, mapping
    from shapely.ops import linemerge
    if not lines:
        return []
    geoms = [LineString(c) for c, _ in lines]
    all_ids = sorted({str(m["osm_id"]) for _, m in lines})
    merged = linemerge(MultiLineString(geoms)) if len(geoms) > 1 else geoms[0]
    parts = list(merged.geoms) if merged.geom_type == "MultiLineString" else [merged]

    # attribute each merged part to the source ways whose vertices it contains
    feats = []
    for part in parts:
        pts = set(map(tuple, part.coords))
        contributing = sorted({str(m["osm_id"]) for c, m in lines
                               if pts & set(map(tuple, c))})
        sample_tags = next((m["tags"] for c, m in lines
                            if pts & set(map(tuple, c))), {})
        feats.append({
            "type": "Feature",
            "geometry": mapping(part),
            "properties": {
                "source": "OSM", "license": "ODbL",
                "attribution": "© OpenStreetMap contributors",
                "osm_ids": contributing or all_ids,
                "substance": sample_tags.get("substance", ""),
                "osm_name": sample_tags.get("name", ""),
                "man_made": sample_tags.get("man_made", "pipeline"),
            },
        })
    return feats


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--area", help='OSM admin area name, e.g. "Egypt"')
    ap.add_argument("--bbox", help="minlon,minlat,maxlon,maxlat (WGS84)")
    ap.add_argument("--substance", help="OSM substance tag filter (gas|oil|...)")
    ap.add_argument("--out", required=True, help="output dir (…/fetched_layers/)")
    ap.add_argument("--name", help="output basename")
    args = ap.parse_args()

    ql = _build_ql(args.area, args.bbox, args.substance)
    js = _run_query(ql)
    lines = _collect_lines(js)
    feats = _stitch(lines)
    if not feats:
        raise SystemExit("no OSM pipeline ways found for that area/substance")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    base = args.name or f"osm_{(args.area or 'bbox').lower().replace(' ', '_')}"
    fc = {"type": "FeatureCollection", "features": feats}
    (out_dir / f"{base}.geojson").write_text(json.dumps(fc))

    meta = {
        "source": "OSM", "license": "ODbL",
        "attribution": "© OpenStreetMap contributors",
        "query_area": args.area or "", "bbox": args.bbox or "",
        "substance": args.substance or "", "n_features": len(feats),
        "n_source_ways": len(lines),
        "fetched_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "notes": "ODbL — licensing acceptability for a GEM tracker is Baird's review call.",
    }
    (out_dir / f"{base}.meta.json").write_text(json.dumps(meta, indent=2))
    print(f"wrote {base}.geojson — {len(feats)} feature(s) from {len(lines)} OSM way(s); "
          f"license: ODbL (flagged for review)")


if __name__ == "__main__":
    main()
