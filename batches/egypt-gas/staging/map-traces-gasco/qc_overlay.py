#!/usr/bin/env python3
"""Re-draw the extracted GASCO 2007 traces back onto the rendered source page.

The point of this check is falsifiability: if a trace does NOT sit on a drawn
line, it is not pipe. Run it after any change to extract_gasco2007.py.

Writes overlays/qc_gasco2007_on_source.png (traces over the page) and
overlays/qc_gasco2007_traces_only.png (geometry alone, to read the network
shape without the basemap).
"""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).parent
TRACES = HERE / "traces" / "gasco2007_paths.json"
PAGE = HERE / "maps" / "gasco2007_p15.png"
OUTDIR = HERE / "overlays"

COLOUR = {
    "existing_pl": (255, 0, 255),
    "under_construction_pl": (0, 255, 255),
    "under_study_pl": (255, 153, 0),
}


def main() -> None:
    d = json.loads(TRACES.read_text())
    page = Image.open(PAGE).convert("RGB")
    s = page.width / 842.0  # SVG page space (pt) -> rendered pixels

    over = page.copy()
    only = Image.new("RGB", page.size, (255, 255, 255))
    for im, w in ((over, 5), (only, 4)):
        dr = ImageDraw.Draw(im)
        for f in d["features"]:
            dr.line([(x * s, y * s) for x, y in f["points"]],
                    fill=COLOUR[f["legend_class"]], width=w)

    OUTDIR.mkdir(exist_ok=True)
    for im, name in ((over, "qc_gasco2007_on_source.png"),
                     (only, "qc_gasco2007_traces_only.png")):
        im.save(OUTDIR / name)
    print(f"{len(d['features'])} traces -> {OUTDIR}")


if __name__ == "__main__":
    main()
