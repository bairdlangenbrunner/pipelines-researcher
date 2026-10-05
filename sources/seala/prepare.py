#!/usr/bin/env python3
"""Turn the Seala scrape into ingest-ready GeoJSON: the 31 lines that diverge from GEM.

    python sources/seala/scrape_seala_datalens.py work/seala-20260917   # re-pull (optional)
    python sources/seala/prepare.py [work/seala-20260917]

Reads  seala_russia_gas_pipelines.geojson  (185 LineStrings, each already tagged with
`gem_overlap_class` against the GEM routes repo) and writes data/seala-ru-gas-divergent.geojson
(gitignored): ONLY class D, "diverges" (p90 > 5 km from the nearest GEM route). The other 154
lines are GEM's own geometry or a re-densified copy of it, so they would only echo GEM back
(NOTES.md). Baird 2026-10-02: register it for the divergent lines.

`name` is the English name when Seala has one, else the Russian one (the matcher
romanizes Cyrillic). `gem_nearest_pid` rides along in `description` for the reviewer and
is never scored.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parents[1] / "work" / "seala-20260917"


def main() -> None:
    fc = json.loads((RAW / "seala_russia_gas_pipelines.geojson").read_text())
    out = []
    for f in fc["features"]:
        p = f["properties"]
        if not p["gem_overlap_class"].startswith("D"):
            continue
        out.append({
            "type": "Feature",
            "properties": {
                "seala_id": f"SEALA-{p['seala_idx']:03d}",
                "name": p["name_en"] or p["name_ru"] or p["name_raw"],
                "name_ru": p["name_ru"],
                "owner": p["owner_ru"],
                "status": p["status_en"],
                "length_km": p["length_km"],
                "n_vertices": p["n_vertices"],
                "country": "Russia",
                "description": (f"Seala map, class D (diverges from GEM): nearest GEM {p['gem_nearest_pid']}, "
                                f"median {p['gem_dist_median_m']} m / p90 {p['gem_dist_p90_m']} m from its route; "
                                f"{p['n_vertices']} vertices"),
            },
            "geometry": f["geometry"],
        })
    dst = HERE / "data" / "seala-ru-gas-divergent.geojson"
    dst.parent.mkdir(exist_ok=True)
    dst.write_text(json.dumps({"type": "FeatureCollection", "features": out}, ensure_ascii=False))
    print(f"wrote {len(out)} features -> {dst}")


if __name__ == "__main__":
    main()
