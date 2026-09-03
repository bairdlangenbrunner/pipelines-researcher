#!/usr/bin/env python3
"""Extract the map's black leader lines.

Many pipeline captions do not sit on their own line: a short black rule runs
from the caption to the pipeline it names (see IGAT 5 / IGAT 6, where the
caption text lies on top of an unrelated oil line and only the leader points at
the two red gas trunks). Attaching a caption by its centroid gets those wrong,
so the leader's FAR endpoint is the anchor to use.

Output: leaders.json - [[x0, y0, x1, y1], ...] in PDF page space.
"""
from __future__ import annotations

import json
from pathlib import Path

import fitz

PDF = Path("/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher/"
           "sources/middle-east/energy-map-of-the-middle-east-2026-peregrine-bush.pdf")
MIN_LEN, MAX_LEN = 4.0, 70.0


def main():
    doc = fitz.open(PDF)
    out = []
    for path in doc[0].get_drawings():
        c = path.get("color")
        if not c or max(c) > 0.25:          # black / near-black only
            continue
        for it in path["items"]:
            if it[0] != "l":
                continue
            (x0, y0), (x1, y1) = (it[1].x, it[1].y), (it[2].x, it[2].y)
            L = ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5
            if MIN_LEN < L < MAX_LEN:
                out.append([round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2)])
    Path("traces/leaders.json").write_text(json.dumps(out))
    print(f"candidate leader strokes: {len(out)}")


if __name__ == "__main__":
    main()
