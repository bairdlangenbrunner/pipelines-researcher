#!/usr/bin/env python3
"""Extract GASCO 2007 'Natural Gas Network' pipeline geometry from PDF vector art.

The map (Mashreq Gas Initiative deck, p.15, GASCO, Nov 2007) is not a raster —
its pipelines are stroked PDF paths. `pdftocairo -svg` renders them as plain
`M x y L x y ...` polylines with a per-path affine transform, so the geometry can
be read out EXACTLY rather than traced. No skeletonization, no pixel guessing.

Legend binding is read off the art itself (the legend swatches are strokes too),
not eyeballed -- see decode_legend().

Output: traces/gasco2007_paths.json, polylines in SVG page space (842x595 pt,
y down). Georeferencing happens downstream in georef_gasco2007.py.
"""
from __future__ import annotations

import json
import math
import re
from pathlib import Path

HERE = Path(__file__).parent
SVG = HERE / "maps" / "gasco2007_p15.svg"
OUT = HERE / "traces" / "gasco2007_paths.json"

# Legend swatches sit in the bottom-left legend block, all sharing one x-extent.
# decode_legend() finds them by geometry; these are the expected labels in the
# order they are drawn top-to-bottom (verified against the rendered page).
LEGEND_LABELS = ["existing_pl", "under_construction_pl", "under_study_pl"]

# Colour families that carry pipeline strokes. The map author used several
# near-identical blues for under-construction line work; all are bound to the
# blue legend swatch. Confirmed visually via the diagnostic overlay.
FAMILY = {
    "#019901": "existing_pl",
    "#01CC01": "existing_pl",
    "#018001": "existing_pl",
    "#FF0101": "under_study_pl",
    "#FF3401": "under_study_pl",
    "#0101CC": "under_construction_pl",
    "#0101FF": "under_construction_pl",
    "#3434FF": "under_construction_pl",
    "#343499": "under_construction_pl",
}

# Non-pipeline strokes, excluded by colour:
#   #FF9934  204 two-point ticks -- label leader lines
#   #010101  map frame, dotted graticule, border/coastline detail
EXCLUDE_COLOURS = {"#FF9934", "#010101"}

# Non-pipeline strokes that share a pipeline colour but are separable by
# (colour, stroke-width, dash) -- each adjudicated by zooming the rendered page:
#   #FF3401 w1.0416 dash  2 paths  the international boundary (Egypt-Israel/
#                                  Jordan, then Jordan-Saudi to the map edge),
#                                  NOT the red "Under Study" pipe (w2.08/3.125)
#   #3434FF w6.25   solid 1 path   the legend's "Under Const. Comp. St." glyph
#   #3434FF w3.125  solid 1 path   the Romana compressor-station glyph
#   #01CC01 w9.375  solid 1 path   the El-Tina valve/metering bar symbol
#   #018001 w1.0416 solid 1 path   1.5-unit mark inside the Port Said P.S glyph
# Deliberately KEPT after the same inspection: #343499 w3.125 dash is the
# Assiut-Aswan Nile Valley under-construction trunk (it lands on the navy dashed
# line, offset from the lavender river band, and starts where the Assiut segment
# ends); #343499 w2.0833 dash are its New Minya laterals; #01CC01 w4.1666 is the
# Aqaba P.S spur.
EXCLUDE_GROUPS = {
    ("#FF3401", 1.0416, True),
    ("#3434FF", 6.25, False),
    ("#3434FF", 3.125, False),
    ("#01CC01", 9.375, False),
    ("#018001", 1.0416, False),
}


def hexof(rgb_pct: str) -> str:
    return "#" + "".join(
        "%02X" % round(float(v.strip().rstrip("%")) * 255 / 100)
        for v in rgb_pct.split(",")
    )


def _xform(p: str, pts):
    tm = re.search(r'transform="matrix\(([^\)]+)\)"', p)
    if not tm:
        return pts
    a, b, c, d, e, f = (float(x) for x in tm.group(1).split(","))
    return [(a * x + c * y + e, b * x + d * y + f) for x, y in pts]


def parse_paths(svg_text: str):
    """Yield (hex_colour, stroke_width, dashed, [(x, y), ...]) in page space."""
    for p in re.findall(r"<path[^>]*?/>", svg_text, re.S):
        m = re.search(r'stroke="rgb\(([^\)]+)\)"', p)
        if not m:
            continue
        dm = re.search(r'd="([^"]+)"', p)
        if not dm or "C" in dm.group(1) or "Q" in dm.group(1):
            continue  # glyph outlines / curves are never pipeline strokes here
        pts = [
            (float(a), float(b))
            for a, b in re.findall(r"[ML] (-?[\d.]+) (-?[\d.]+)", dm.group(1))
        ]
        if len(pts) < 2:
            continue
        pts = _xform(p, pts)
        w = re.search(r'stroke-width="([\d.]+)"', p)
        yield hexof(m.group(1)), float(w.group(1)) if w else None, "stroke-dasharray" in p, pts


# Not every pipeline on this page is a stroke. The Fajr Gas Pipeline (Aqaba ->
# Rehab ps -> Samra ps, Jordan) is drawn as a FILLED green ribbon polygon with a
# separate arrowhead subpath -- the stroke pass misses it entirely. Any filled
# pipeline-coloured polygon whose largest subpath exceeds this perimeter is a
# ribbon, not a glyph/arrowhead (the runners-up are ~15 pt triangles).
FILL_RIBBON_MIN_PERIM = 50.0


def parse_fill_ribbons(svg_text: str):
    """Yield (hex_colour, half_width, [(x, y), ...]) centrelines for filled pipe.

    A ribbon polygon runs up one side of the line and back down the other, so the
    centreline is the elementwise mean of the outbound half and the reversed
    return half. Collinear duplicate vertices (mitre artefacts) are dropped first
    so the two halves pair up.
    """
    for p in re.findall(r"<path[^>]*?/>", svg_text, re.S):
        fm = re.search(r'fill="rgb\(([^\)]+)\)"', p)
        if not fm or re.search(r'stroke="rgb', p):
            continue
        colour = hexof(fm.group(1))
        if colour not in FAMILY:
            continue
        dm = re.search(r'd="([^"]+)"', p)
        if not dm or "C" in dm.group(1) or "Q" in dm.group(1):
            continue
        subs = [q for q in _subpaths(dm.group(1), p) if len(q) >= 4]
        if not subs:
            continue
        ring = max(subs, key=plen)          # the ribbon; the rest is the arrowhead
        if plen(ring) < FILL_RIBBON_MIN_PERIM:
            continue
        ded = [ring[0]]
        for q in ring[1:]:
            if math.hypot(q[0] - ded[-1][0], q[1] - ded[-1][1]) > 0.75:
                ded.append(q)
        if len(ded) % 2:                    # closed rings can repeat the origin
            ded = ded[:-1]
        half = len(ded) // 2
        a, b = ded[:half], ded[half:][::-1]
        centre = [((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2) for p1, p2 in zip(a, b)]
        hw = sum(math.hypot(p1[0] - p2[0], p1[1] - p2[1])
                 for p1, p2 in zip(a, b)) / (2 * len(a))
        yield colour, round(hw, 3), centre


def _subpaths(d: str, attrs: str):
    out = []
    for s in d.split("M")[1:]:
        q = [(float(a), float(b))
             for a, b in re.findall(r"(-?[\d.]+) (-?[\d.]+)", s)]
        if len(q) >= 3:
            out.append(_xform(attrs, q))
    return out


def _centroid(q):
    return sum(x for x, _ in q) / len(q), sum(y for _, y in q) / len(q)


# The EMG "Marine P/L" arrow (Arish -> Israel) is drawn as a chain of FILLED
# dash blobs plus a triangular arrowhead, not as a dashed stroke -- both the
# stroke pass and the ribbon pass miss it. A dash chain is recognisable without
# guessing: every blob is the same drawn shape (identical node count), each is
# tiny, and there are at least five. Text rendered as outlines fails the
# equal-node-count test, so this rule matches exactly one path on the page.
DASH_CHAIN_MIN_BLOBS = 5
DASH_CHAIN_MAX_BLOB_DIAG = 8.0


def parse_fill_dash_chains(svg_text: str):
    """Yield (hex_colour, [(x, y), ...]) centrelines for filled dash chains."""
    for p in re.findall(r"<path[^>]*?/>", svg_text, re.S):
        fm = re.search(r'fill="rgb\(([^\)]+)\)"', p)
        if not fm or re.search(r'stroke="rgb', p):
            continue
        colour = hexof(fm.group(1))
        if colour not in FAMILY:
            continue
        dm = re.search(r'd="([^"]+)"', p)
        if not dm:
            continue
        subs = _subpaths(dm.group(1), p)
        head = subs[-1] if len(subs) > 1 and len(subs[-1]) == 3 else None
        body = subs[:-1] if head else subs
        if len(body) < DASH_CHAIN_MIN_BLOBS:
            continue
        if len({len(q) for q in body}) != 1:
            continue
        if max(math.hypot(max(x for x, _ in q) - min(x for x, _ in q),
                          max(y for _, y in q) - min(y for _, y in q))
               for q in body) > DASH_CHAIN_MAX_BLOB_DIAG:
            continue
        pts = [_centroid(q) for q in body]
        if head:  # the arrowhead tip is the vertex furthest along the chain
            pts.append(max(head, key=lambda v: math.hypot(v[0] - pts[-1][0],
                                                          v[1] - pts[-1][1])))
        yield colour, pts


def plen(pts) -> float:
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(pts, pts[1:]))


def decode_legend(records):
    """Bind colour -> legend class from the legend swatch strokes themselves.

    The three swatches are horizontal segments of identical length sharing one
    x-extent, stacked vertically in the bottom-left legend block. Returns the
    ordered swatch list so the binding is provable, not assumed.
    """
    cands = []
    for colour, width, dashed, pts in records:
        if len(pts) != 2:
            continue
        (x1, y1), (x2, y2) = pts
        if abs(y2 - y1) > 2 or not (8 < abs(x2 - x1) < 70):
            continue
        if not (60 < x1 < 240 and 270 < y1 < 530):
            continue
        cands.append((y1, x1, x2, colour, width, dashed))
    # the swatches are the group sharing the modal (x1, x2, width)
    from collections import Counter

    key = Counter((round(c[1], 1), round(c[2], 1), c[4]) for c in cands).most_common(1)
    if not key:
        raise SystemExit("legend swatches not found")
    kx1, kx2, kw = key[0][0]
    sw = sorted(c for c in cands if (round(c[1], 1), round(c[2], 1), c[4]) == (kx1, kx2, kw))
    return [
        {"label": LEGEND_LABELS[i], "swatch_y": round(s[0], 2), "colour": s[3],
         "width": s[4], "dashed": s[5]}
        for i, s in enumerate(sw)
    ]


def main() -> None:
    records = list(parse_paths(SVG.read_text()))
    legend = decode_legend(records)
    swatch_colours = {s["colour"] for s in legend}
    swatch_ys = {round(s["swatch_y"], 1) for s in legend}

    # The map frame is a green rectangle spanning the whole page -- not pipe.
    frame_bbox_area = 200_000

    feats, dropped = [], {"frame": 0, "legend_swatch": 0, "excluded_colour": 0,
                          "excluded_group": 0, "unclassified": 0}
    for colour, width, dashed, pts in records:
        if colour in EXCLUDE_COLOURS:
            dropped["excluded_colour"] += 1
            continue
        if (colour, width, dashed) in EXCLUDE_GROUPS:
            dropped["excluded_group"] += 1
            continue
        cls = FAMILY.get(colour)
        if cls is None:
            dropped["unclassified"] += 1
            continue
        xs = [q[0] for q in pts]
        ys = [q[1] for q in pts]
        if (max(xs) - min(xs)) * (max(ys) - min(ys)) > frame_bbox_area:
            dropped["frame"] += 1
            continue
        # drop the legend swatches themselves
        if (len(pts) == 2 and colour in swatch_colours
                and round(pts[0][1], 1) in swatch_ys and 60 < pts[0][0] < 240):
            dropped["legend_swatch"] += 1
            continue
        feats.append({
            "path_id": f"g07-{len(feats):04d}",
            "legend_class": cls,
            "stroke_rgb": colour,
            "stroke_width": width,
            "dashed": dashed,
            "geometry_source": "stroke",
            "page_len": round(plen(pts), 3),
            "points": [[round(x, 3), round(y, 3)] for x, y in pts],
        })

    svg_text = SVG.read_text()
    for colour, hw, pts in parse_fill_ribbons(svg_text):
        feats.append({
            "path_id": f"g07-{len(feats):04d}",
            "legend_class": FAMILY[colour],
            "stroke_rgb": colour,
            "stroke_width": round(hw * 2, 3),
            "dashed": False,
            "geometry_source": "fill_centerline",
            "page_len": round(plen(pts), 3),
            "points": [[round(x, 3), round(y, 3)] for x, y in pts],
        })
    for colour, pts in parse_fill_dash_chains(svg_text):
        feats.append({
            "path_id": f"g07-{len(feats):04d}",
            "legend_class": FAMILY[colour],
            "stroke_rgb": colour,
            "stroke_width": None,
            "dashed": True,
            "geometry_source": "fill_dash_chain",
            "page_len": round(plen(pts), 3),
            "points": [[round(x, 3), round(y, 3)] for x, y in pts],
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "source": {
            "map": "gasco2007",
            "title": "Natural Gas Network",
            "publisher": "GASCO (Egyptian Natural Gas Company)",
            "map_date": "Nov 2007",
            "document": "Integrating the Mashreq Gas Market and the European "
                        "Internal Gas Market (Ministry of Petroleum, Egypt), p.15",
            "file": "maps/source_mashreq_gas_initiative_2008.pdf",
            "page": 15,
        },
        "space": {"crs": "SVG page space, 842x595 pt, y increases downward"},
        "method": "pdftocairo -svg; stroked path extraction (exact vector art, no tracing)",
        "legend_decoded_from_art": legend,
        "counts": {
            "features": len(feats),
            "by_class": {c: sum(1 for f in feats if f["legend_class"] == c)
                         for c in sorted({f["legend_class"] for f in feats})},
            "dropped": dropped,
        },
        "features": feats,
    }, indent=1))

    print(f"legend binding (from the art):")
    for s in legend:
        print(f"  {s['label']:22s} {s['colour']}  {'dashed' if s['dashed'] else 'solid'}"
              f"  y={s['swatch_y']}")
    print(f"\n{len(feats)} pipeline paths kept; dropped {dropped}")
    for c in sorted({f["legend_class"] for f in feats}):
        sel = [f for f in feats if f["legend_class"] == c]
        print(f"  {c:22s} n={len(sel):4d}  page_len={sum(f['page_len'] for f in sel):8.1f}")


if __name__ == "__main__":
    main()
