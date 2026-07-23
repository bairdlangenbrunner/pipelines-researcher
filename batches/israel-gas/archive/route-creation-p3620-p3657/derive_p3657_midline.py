#!/usr/bin/env python3
"""Derive the P3657 (Ashdod-Ashkelon marine gas pipeline) centerline from the
works-corridor polygon published in Israel Shipping & Ports Authority
Notice to Mariners 113/2024 ("gas pipeline laying project", 02 Dec 2024).

Every output coordinate is a deterministic midpoint of source-polygon vertices
or interpolants — no coordinate is hand-typed or fabricated.

The 23-point polygon is a ~1.0 km-wide lay corridor whose vertices pair 1:1
across the band (verified: every pair below is 0.99-1.05 km apart):
  (13,14) (12,15) (11,16) (10,17) (9,18) (8,19) (7,20) (6,21) (5,22) (4,23)
ordered south (Ashkelon landfall, pts 13/14) -> north. Beyond pair (4,23) the
corridor continues southeast toward the Ashdod shore bounded by side-A tail
4-3-2-1 and the closure edge 23->1; both boundaries converge at point 1 on the
shoreline, so the tail midline (resampled midpoints of those two polylines)
naturally terminates at point 1 (the Ashdod landfall vicinity).

Output centerline runs Ashdod (north) -> Ashkelon (south) to match the sheet's
segment naming. Positional uncertainty ~ half corridor width (~0.5-0.7 km).
"""
import json
import math
from pathlib import Path

from shapely.geometry import LineString, Polygon, mapping

HERE = Path(__file__).parent
OUT = HERE / "fetched_layers"

# Verbatim table from NtM 113/2024 (lat N, lon E), DMS as published.
DMS = {
    1: ("31 51 30", "034 39 47"),
    2: ("31 52 41", "034 38 38"),
    3: ("31 53 14", "034 37 33"),
    4: ("31 53 21", "034 36 45"),
    5: ("31 53 18", "034 35 57"),
    6: ("31 53 01", "034 35 05"),
    7: ("31 52 39", "034 34 40"),
    8: ("31 47 39", "034 31 52"),
    9: ("31 41 29", "034 27 34"),
    10: ("31 41 02", "034 27 22"),
    11: ("31 40 15", "034 27 27"),
    12: ("31 39 38", "034 28 01"),
    13: ("31 38 17", "034 31 29"),
    14: ("31 38 46", "034 31 47"),
    15: ("31 40 03", "034 28 25"),
    16: ("31 40 28", "034 28 04"),
    17: ("31 40 58", "034 28 01"),
    18: ("31 41 15", "034 28 08"),
    19: ("31 47 23", "034 32 25"),
    20: ("31 52 20", "034 35 11"),
    21: ("31 52 33", "034 35 26"),
    22: ("31 52 46", "034 36 05"),
    23: ("31 52 49", "034 36 43"),
}

PAIRS_S_TO_N = [(13, 14), (12, 15), (11, 16), (10, 17), (9, 18),
                (8, 19), (7, 20), (6, 21), (5, 22), (4, 23)]

SRC = "Notice to Mariners 113/2024, Israel Ports & Shipping Authority (Rasfan), 02 Dec 2024"
URL = "https://kachol.com/wp-content/uploads/2024/12/הודעה-למשיטים-1132024-פרויקט-הנחת-צינור-גז.pdf"


def dms_to_dec(s: str) -> float:
    d, m, sec = (float(x) for x in s.split())
    return d + m / 60 + sec / 3600


PTS = {k: (dms_to_dec(lon), dms_to_dec(lat)) for k, (lat, lon) in DMS.items()}  # (lon, lat)


def geodesic_km(a, b):
    """Haversine, km."""
    lon1, lat1, lon2, lat2 = map(math.radians, (*a, *b))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371.0088 * math.asin(math.sqrt(h))


def line_length_km(coords):
    return sum(geodesic_km(coords[i], coords[i + 1]) for i in range(len(coords) - 1))


def resample(coords, n):
    """n points at equal arc-length fractions (geodesic)."""
    cum = [0.0]
    for i in range(len(coords) - 1):
        cum.append(cum[-1] + geodesic_km(coords[i], coords[i + 1]))
    total = cum[-1]
    out = []
    j = 0
    for t in (total * i / (n - 1) for i in range(n)):
        while j < len(cum) - 2 and cum[j + 1] < t:
            j += 1
        seg = cum[j + 1] - cum[j]
        f = 0.0 if seg == 0 else (t - cum[j]) / seg
        out.append((coords[j][0] + f * (coords[j + 1][0] - coords[j][0]),
                    coords[j][1] + f * (coords[j + 1][1] - coords[j][1])))
    return out


def mid(a, b):
    return ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)


def main():
    OUT.mkdir(exist_ok=True)
    poly = Polygon([PTS[i] for i in range(1, 24)])
    assert poly.is_valid

    widths = [geodesic_km(PTS[a], PTS[b]) for a, b in PAIRS_S_TO_N]
    print("pair widths km:", " ".join(f"{w:.2f}" for w in widths))

    # main band: vertex-pair midpoints, south -> north
    band = [mid(PTS[a], PTS[b]) for a, b in PAIRS_S_TO_N]

    # Ashdod tail: side-A tail 4->1 vs closure edge 23->1, both -> point 1
    n = 60
    tail_a = resample([PTS[4], PTS[3], PTS[2], PTS[1]], n)
    tail_b = resample([PTS[23], PTS[1]], n)
    tail = [mid(pa, pb) for pa, pb in zip(tail_a, tail_b)]

    coords_s_to_n = band + tail[1:]          # tail[0] ~= band[-1]
    coords = list(reversed(coords_s_to_n))    # Ashdod (N) -> Ashkelon (S)

    inside = sum(poly.covers(LineString([coords[i], coords[i + 1]]).interpolate(0.5, normalized=True))
                 for i in range(len(coords) - 1))
    length = line_length_km(coords)
    print(f"vertices: {len(coords)}; segment midpoints inside corridor: {inside}/{len(coords)-1}")
    print(f"midline geodesic length: {length:.2f} km (sheet LengthKnown 42 km -> ratio {length/42:.3f})")
    print(f"Ashdod end: {coords[0][1]:.5f}N {coords[0][0]:.5f}E; Ashkelon end: {coords[-1][1]:.5f}N {coords[-1][0]:.5f}E")

    corridor_fc = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "properties": {"name": "NtM 113/2024 works corridor (verbatim 23-pt polygon)", "source": SRC},
            "geometry": mapping(poly),
        }],
    }
    (OUT / "ntm113_corridor.geojson").write_text(json.dumps(corridor_fc, indent=1))

    midline_fc = {
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "properties": {
                "name": "P3657 derived centerline (corridor midline), Ashdod -> Ashkelon",
                "derivation": ("1:1 vertex-pair midpoints (13,14)...(4,23) + Ashdod tail = midline of "
                               "side 4-3-2-1 vs closure edge 23-1 (converging at shoreline point 1); "
                               "corridor width 0.99-1.05 km on all pairs"),
                "source": SRC,
                "source_url": URL,
                "corridor_width_km": [round(w, 2) for w in widths],
                "midline_geodesic_km": round(length, 2),
            },
            "geometry": mapping(LineString([(round(x, 6), round(y, 6)) for x, y in coords])),
        }],
    }
    (OUT / "p3657_ntm_midline.geojson").write_text(json.dumps(midline_fc, indent=1))

    meta = {
        "fetched": "2026-07-22",
        "method": "derived-vector",
        "source_name": SRC,
        "source_url": URL,
        "source_doc_ref": "4000-0709-2024-0000908",
        "notes": ("23-point works-corridor polygon transcribed verbatim from the notice PDF "
                  "(scratchpad ntm/n113.pdf); DMS->decimal; datum not stated in the notice, "
                  "WGS84 assumed (NtM convention). Centerline = corridor midline; positional "
                  "uncertainty ~ half corridor width (~0.5-0.7 km). Corroborating statutory "
                  "context: TMA 37/A/2/7 (Ashdod reception <-> Ashkelon reception, marine "
                  "corridor widened to ~350 m at the Ashdod end, cabinet decision 1260 of "
                  "27.02.2022)."),
        "files": ["ntm113_corridor.geojson", "p3657_ntm_midline.geojson"],
    }
    (OUT / "p3657_ntm_midline.meta.json").write_text(json.dumps(meta, indent=1))
    print("wrote ntm113_corridor.geojson, p3657_ntm_midline.geojson, p3657_ntm_midline.meta.json")


if __name__ == "__main__":
    main()
