#!/usr/bin/env python3
"""Extract the map's basemap linework, grouped by stroke colour.

Two layers matter downstream:
  cyan  (0.0, 0.681, 0.938) - coastline; the registration source for register.py
  grey  (0.427, 0.433, 0.442) - country borders; held OUT of the fit and used
                                only to validate it independently

Output traces/basemap_lines.json is ~12 MB and regenerable, so it is gitignored.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import fitz

PDF = Path("/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher/"
           "sources/middle-east/energy-map-of-the-middle-east-2026-peregrine-bush.pdf")
KEEP = {(0.0, 0.681, 0.938): "coastline", (0.427, 0.433, 0.442): "border"}


def flatten(item):
    k = item[0]
    if k == "l":
        return [(item[1].x, item[1].y), (item[2].x, item[2].y)]
    if k == "c":
        p0, p1, p2, p3 = item[1], item[2], item[3], item[4]
        out = []
        for i in range(9):
            t, u = i / 8, 1 - i / 8
            out.append((u**3 * p0.x + 3 * u * u * t * p1.x + 3 * u * t * t * p2.x + t**3 * p3.x,
                        u**3 * p0.y + 3 * u * u * t * p1.y + 3 * u * t * t * p2.y + t**3 * p3.y))
        return out
    if k == "re":
        r = item[1]
        return [(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1), (r.x0, r.y0)]
    return []


def main():
    doc = fitz.open(PDF)
    groups = defaultdict(list)
    for path in doc[0].get_drawings():
        c = path.get("color")
        if not c:
            continue
        c = tuple(round(v, 3) for v in c)
        if c not in KEEP:
            continue
        # One polyline per PATH, not per item: register.py drops short polylines,
        # so splitting a coastline path into its 2-point segments would throw the
        # whole registration source away.
        pts = []
        for it in path["items"]:
            seg = flatten(it)
            if len(seg) >= 2:
                pts.extend(seg if not pts or pts[-1] != seg[0] else seg[1:])
        if len(pts) >= 2:
            groups[str(c)].append([[round(x, 3), round(y, 3)] for x, y in pts])
    Path("traces").mkdir(exist_ok=True)
    Path("traces/basemap_lines.json").write_text(json.dumps(groups))
    for k, v in groups.items():
        print(f"  {KEEP[tuple(json.loads(k.replace('(', '[').replace(')', ']')))]:9s} "
              f"{k}: {len(v)} polylines, {sum(len(p) for p in v)} vertices")


if __name__ == "__main__":
    main()
