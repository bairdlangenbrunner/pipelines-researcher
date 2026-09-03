#!/usr/bin/env python3
"""Extract pipeline polylines from the PE/World Oil Middle East 2026 vector PDF.

Pipelines are stroked paths separable by colour + dash pattern. Per the map's own
legend (swatch positions verified against the section headers in page coords):
    red   (0.844, 0.098, 0.126) -> GAS pipelines
    green (0.0,   0.573, 0.28 ) -> OIL pipelines
    solid -> in service; dashed [2 2] -> under construction / planned / proposed
Output is in PDF page space (y down); georeferencing happens downstream.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import fitz

PDF = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
    "/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher/sources/"
    "middle-east/energy-map-of-the-middle-east-2026-peregrine-bush.pdf")

RED = (0.844, 0.098, 0.126)
GREEN = (0.0, 0.573, 0.28)
COMMODITY = {RED: "gas", GREEN: "oil"}

# Page furniture to drop (page coords, x0 y0 x1 y1). Verified by overlay render.
EXCLUDE = {
    "legend": (40, 2055, 700, 2365),
    "sources": (50, 1690, 480, 1870),
    "disclaimer": (20, 1875, 700, 2050),
    "hormuz_inset": (2020, 1740, 2520, 2370),
    "producer_box": (1520, 2230, 2010, 2340),
    "title": (45, 20, 595, 225),
}
TOL = 0.05  # endpoint chaining tolerance, pt


def key(pt, q=2):
    return (round(pt[0], q), round(pt[1], q))


def flatten(item):
    """One drawing item -> list of points (beziers flattened to 8 chords)."""
    kind = item[0]
    if kind == "l":
        return [(item[1].x, item[1].y), (item[2].x, item[2].y)]
    if kind == "c":
        p0, p1, p2, p3 = (item[1], item[2], item[3], item[4])
        out = []
        for i in range(9):
            t = i / 8
            u = 1 - t
            out.append((
                u**3 * p0.x + 3 * u * u * t * p1.x + 3 * u * t * t * p2.x + t**3 * p3.x,
                u**3 * p0.y + 3 * u * u * t * p1.y + 3 * u * t * t * p2.y + t**3 * p3.y,
            ))
        return out
    if kind == "re":
        r = item[1]
        return [(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1), (r.x0, r.y0)]
    return []


def chain(segments):
    """Chain shared-endpoint segments into maximal polylines.

    Greedy walk from each unused segment, extending the tail and then the head.
    Junction nodes (>2 incident segments) just take the first unused branch --
    the split point is arbitrary but no geometry is lost or duplicated.
    """
    from collections import defaultdict
    adj = defaultdict(list)
    for i, seg in enumerate(segments):
        adj[key(seg[0])].append(i)
        adj[key(seg[-1])].append(i)
    used = [False] * len(segments)

    def grow(pts):
        """Extend pts at its tail as far as possible."""
        while True:
            tip = key(pts[-1])
            nxt = next((j for j in adj[tip] if not used[j]), None)
            if nxt is None:
                return pts
            used[nxt] = True
            s = list(segments[nxt])
            if key(s[0]) != tip:
                s.reverse()
            pts.extend(s[1:])

    lines = []
    for i in range(len(segments)):
        if used[i]:
            continue
        used[i] = True
        pts = grow(list(segments[i]))       # forward from the seed
        pts.reverse()
        pts = grow(pts)                     # then backward
        lines.append(pts)
    return lines


def excluded(pts):
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
    for name, (x0, y0, x1, y1) in EXCLUDE.items():
        if x0 <= cx <= x1 and y0 <= cy <= y1:
            return name
    return None


def main():
    doc = fitz.open(PDF)
    page = doc[0]
    feats = []
    dropped = {}
    for pi, path in enumerate(page.get_drawings()):
        col = path.get("color")
        if not col:
            continue
        col = tuple(round(v, 3) for v in col)
        if col not in COMMODITY:
            continue
        if (path.get("width") or 0) < 0.6:   # symbols/markers, not routes
            continue
        dashes = (path.get("dashes") or "[] 0").strip()
        status = "in_service" if dashes.startswith("[]") else "uc_planned_proposed"
        segs = [flatten(it) for it in path["items"]]
        segs = [s for s in segs if len(s) >= 2]
        if not segs:
            continue
        for pts in chain(segs):
            if len(pts) < 2:
                continue
            drop = excluded(pts)
            if drop:
                dropped[drop] = dropped.get(drop, 0) + 1
                continue
            feats.append({
                "path_index": pi,
                "commodity": COMMODITY[col],
                "status": status,
                "points": [[round(x, 3), round(y, 3)] for x, y in pts],
            })
    out = {"source_pdf": PDF.name, "space": "pdf_page_pt_y_down",
           "page_size": [page.rect.width, page.rect.height], "features": feats}
    Path("traces/pipelines_pagespace.json").write_text(json.dumps(out))
    n = len(feats)
    import collections
    c = collections.Counter((f["commodity"], f["status"]) for f in feats)
    print(f"polylines: {n}")
    for k, v in sorted(c.items()):
        print("  ", k, v)
    print("dropped (page furniture):", dropped)
    print("total vertices:", sum(len(f["points"]) for f in feats))


if __name__ == "__main__":
    main()
