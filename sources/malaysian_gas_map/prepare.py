#!/usr/bin/env python3
"""Turn the as-delivered Malaysian Gas Map extraction into ingest-ready GeoJSON.

    python sources/malaysian_gas_map/prepare.py

Reads  extraction/malaysia_gas_map_extraction.geojson  (683 features: 67 pipeline
LineStrings + 616 field polygons, one flat FeatureCollection, no per-feature id) and
writes two files into data/ (gitignored — this script re-derives them):

  data/mgm-pipelines.geojson   the 67 pipeline LineStrings, the reconcilable dataset
  data/mgm-fields.geojson      the 616 field polygons, an anchor gazetteer only

What it deliberately does NOT carry into the pipeline records is a `name`. The
extraction's `feature_class` / `candidate_name` are nearest-label-in-this-inset
artifacts, not per-segment identities — see NOTES.md § "The class labels are wrong".
Both strings are preserved verbatim as `map_label` / `nearest_text` (and folded into
`description`, which the matcher never scores) so a reviewer sees the raw label
without the engine trusting it.

Shape ids are assigned by position, matching the "Shape ID" column of the workbook's
Pipelines / Fields sheets (both are 1-based within their own feature type).
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "extraction" / "malaysia_gas_map_extraction.geojson"


def main() -> None:
    fc = json.loads(SRC.read_text())
    pipes: list[dict] = []
    fields: list[dict] = []

    for feat in fc["features"]:
        p = feat.get("properties") or {}
        if p.get("feature_type") == "pipeline":
            n = len(pipes) + 1
            label = (p.get("feature_class") or "").strip()
            nearest = (p.get("candidate_name") or "").strip()
            desc = f"map label: {label or '(none)'}"
            if nearest and nearest != label:
                desc += f" | nearest map text: {nearest}"
            desc += (f" | inset: {p.get('inset')} | label gap {p.get('label_gap_px')} px"
                     " | labels are label-proximity artifacts, unverified")
            pipes.append({
                "type": "Feature",
                "properties": {
                    "shape_id": f"MGM-P-{n:03d}",
                    "country": "Malaysia",
                    "inset": p.get("inset"),
                    "map_label": label,
                    "nearest_text": nearest,
                    "label_gap_px": p.get("label_gap_px"),
                    "description": desc,
                },
                "geometry": feat["geometry"],
            })
        elif p.get("feature_type") == "field":
            n = len(fields) + 1
            fields.append({
                "type": "Feature",
                "properties": {
                    "shape_id": f"MGM-F-{n:03d}",
                    "country": "Malaysia",
                    "inset": p.get("inset"),
                    "field_class": p.get("feature_class"),
                    "nearest_text": p.get("candidate_name"),
                    "label_gap_px": p.get("label_gap_px"),
                    "lon": p.get("longitude"),
                    "lat": p.get("latitude"),
                },
                "geometry": feat["geometry"],
            })

    out = HERE / "data"
    out.mkdir(exist_ok=True)
    (out / "mgm-pipelines.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": pipes}, ensure_ascii=False))
    (out / "mgm-fields.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": fields}, ensure_ascii=False))
    print(f"wrote data/mgm-pipelines.geojson — {len(pipes)} pipeline feature(s)")
    print(f"wrote data/mgm-fields.geojson    — {len(fields)} field polygon(s)")


if __name__ == "__main__":
    main()
