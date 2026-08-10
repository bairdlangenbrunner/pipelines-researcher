#!/usr/bin/env python3
"""Extract the GASCO-2007 map's own `<diameter>" <length> km` segment labels.

The map annotates most drawn lines with their diameter and length (e.g. `24 " 45 k.m`,
`12" 14.5km`). Those printed labels are the primary evidence for which drawn line is
which tracker row -- researcher NA read this sheet visually when adding the Egypt gas
rows, so a row's Diameter + LengthKnownKm is matched back to a label, and the label's
position picks out the trace.

The labels are real PDF text, and `pdftotext -bbox` reports them in the SAME visual
page space (842x595, y down) the traces were extracted in, so the existing graticule
transform georeferences them unchanged. Nothing here is research: it reads the sheet's
own printed annotations and attaches each to its nearest trace.

Writes:
  labels/gasco2007_labels.json      -- page-space + WGS84 labels, nearest-trace link
  labels/gasco2007_labels.geojson   -- Point layer (QGIS-openable, flat scalars only)
"""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
from pathlib import Path

import numpy as np
from pyproj import Geod

HERE = Path(__file__).parent
REPO = HERE.parents[3]
PDF = HERE / "maps" / "source_mashreq_gas_initiative_2008.pdf"
PAGE = 15
ORDER = 2  # same fit as emit_gasco2007.py

# `24 " 45 k.m` / `18/16" 13km` / `36" - 393 k.m` / `4.78 " 36`
DIA = r"\d+(?:\.\d+)?(?:/\d+)?"
LABEL_RE = re.compile(
    rf'^(?P<dia>{DIA})\s*["“”\']\s*-?\s*(?P<len>\d+(?:\.\d+)?)\s*(?:k\.?m|km)?\.?$',
    re.I,
)


def _georef():
    spec = importlib.util.spec_from_file_location("georef", REPO / "scripts" / "georef.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def words():
    """(text, cx, cy) for every word on the page, in visual page space."""
    xml = subprocess.run(
        ["pdftotext", "-f", str(PAGE), "-l", str(PAGE), "-bbox", str(PDF), "-"],
        capture_output=True, text=True, check=True,
    ).stdout
    out = []
    for m in re.finditer(
        r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>',
        xml, re.S,
    ):
        x0, y0, x1, y1 = (float(m.group(i)) for i in range(1, 5))
        out.append({"text": m.group(5), "x0": x0, "y0": y0, "x1": x1, "y1": y1,
                    "cx": (x0 + x1) / 2, "cy": (y0 + y1) / 2})
    return out


def group_lines(ws, y_tol=1.2, x_gap=6.0):
    """Cluster words into printed lines: same baseline, small horizontal gaps.

    Printed line spacing on this sheet is ~3 pt, so bands are built by a sweep
    against the running baseline (rounding cy into fixed bins would split one
    printed line across two bins and mix unrelated labels into a third).
    """
    bands, cur = [], []
    for w in sorted(ws, key=lambda w: w["cy"]):
        if cur and w["cy"] - cur[0]["cy"] <= y_tol:
            cur.append(w)
        else:
            if cur:
                bands.append(cur)
            cur = [w]
    if cur:
        bands.append(cur)

    lines = []
    for band in bands:
        run = []
        for w in sorted(band, key=lambda w: w["x0"]):
            if run and w["x0"] - max(r["x1"] for r in run) <= x_gap:
                run.append(w)
            else:
                if run:
                    lines.append(run)
                run = [w]
        if run:
            lines.append(run)
    return lines


def main() -> None:
    m = _georef()
    geod = Geod(ellps="WGS84")
    gcps = json.loads((HERE / "gcps" / "gcps_gasco2007.json").read_text())
    g = m.fit_transform(gcps, ORDER)

    traces = json.loads((HERE / "gasco2007_gas_network.geojson").read_text())["features"]
    pages = json.loads((HERE / "traces" / "gasco2007_paths.json").read_text())["features"]
    by_id = {p["path_id"]: np.asarray(p["points"], float) for p in pages}

    found = []
    for line in group_lines(words()):
        txt = " ".join(w["text"] for w in line)
        mm = LABEL_RE.match(txt.strip())
        if not mm:
            continue
        cx = sum(w["cx"] for w in line) / len(line)
        cy = sum(w["cy"] for w in line) / len(line)
        lon, lat = g.apply([[cx, cy]])[0]

        # nearest trace, measured in page space (label sits beside its own line)
        best = (1e9, None, None)
        for t in traces:
            pid = t["properties"]["path_id"]
            pts = by_id[pid]
            d = float(np.min(np.hypot(pts[:, 0] - cx, pts[:, 1] - cy)))
            if d < best[0]:
                best = (d, pid, t)
        dist_pt, pid, tr = best

        found.append({
            "label_text": txt,
            "diameter_in": mm.group("dia"),
            "length_km_label": float(mm.group("len")),
            "page_x": round(cx, 3), "page_y": round(cy, 3),
            "lon": round(lon, 6), "lat": round(lat, 6),
            "nearest_path_id": pid,
            "nearest_dist_pagept": round(dist_pt, 2),
            "nearest_legend_class": tr["properties"]["legend_class"],
            "nearest_trace_length_km": tr["properties"]["length_km"],
        })

    # Place / facility captions on the same sheet, georeferenced by the same transform.
    # These are what a row's Start/End location text was read off, so they pin which
    # drawn line a label belongs to. Legend text and the graticule numbers are dropped.
    LEGEND = {
        "Existing", "Under", "Cons.", "Study.", "P/L", "Comp.", "Station", "St.", "Gas",
        "Fields", "Future", "Facilities", "Distribution", "Power", "Industrial", "Area",
        "Consumer", "Co.", "Off", "Take", "Export", "Total", "Length", "Thousand", "Km",
        "Natural", "Network", "Nov.", "2007", "Sea", "Red", "Mediterranean",
    }
    places = []
    for line in group_lines(words(), y_tol=1.2, x_gap=8.0):
        txt = " ".join(w["text"] for w in line).strip()
        if LABEL_RE.match(txt) or not txt:
            continue
        if re.fullmatch(r"[\d\s°.,\-/\"“”']+", txt):        # graticule numbers
            continue
        if any(t in LEGEND for t in txt.split()):
            continue
        if not re.search(r"[A-Za-z]{3}", txt):               # Arabic-only / stray glyphs
            continue
        cx = sum(w["cx"] for w in line) / len(line)
        cy = sum(w["cy"] for w in line) / len(line)
        lon, lat = g.apply([[cx, cy]])[0]
        places.append({"text": txt, "page_x": round(cx, 3), "page_y": round(cy, 3),
                       "lon": round(lon, 6), "lat": round(lat, 6)})
    places.sort(key=lambda r: (r["page_y"], r["page_x"]))

    found.sort(key=lambda r: (r["page_y"], r["page_x"]))
    outd = HERE / "labels"
    outd.mkdir(exist_ok=True)
    (outd / "gasco2007_places.json").write_text(json.dumps({
        "note": "captions printed on the GASCO Nov-2007 sheet, georeferenced by the same "
                "graticule transform; positions are ON THE MAP (schematic, median 14 km "
                "off the real place) -- use them to identify a line, never as coordinates",
        "count": len(places), "places": places,
    }, indent=1) + "\n")
    (outd / "gasco2007_labels.json").write_text(json.dumps({
        "source": {
            "file": "maps/source_mashreq_gas_initiative_2008.pdf", "page": PAGE,
            "title": "GASCO, Natural Gas Network, Nov. 2007",
            "method": "pdftotext -bbox (real PDF text) + the graticule transform from emit_gasco2007.py",
        },
        "georef": {"order": ORDER, "gcps": len(gcps),
                   "note": "registration RMSE 1.91 km / LOO 2.15 km; drawn-feature offset median 14 km "
                           "(schematic drawing) -- a label's lon/lat locates it ON THE MAP, not on the ground"},
        "count": len(found),
        "labels": found,
    }, indent=1) + "\n")

    (outd / "gasco2007_labels.geojson").write_text(json.dumps({
        "type": "FeatureCollection",
        "features": [{
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [r["lon"], r["lat"]]},
            "properties": {k: v for k, v in r.items() if k not in ("lon", "lat")},
        } for r in found],
    }, indent=1) + "\n")

    print(f"{len(found)} segment labels extracted -> labels/")
    for r in found:
        print(f"  {r['label_text']:<22} {r['lon']:.3f},{r['lat']:.3f}  "
              f"-> {r['nearest_path_id']} ({r['nearest_dist_pagept']} pt, "
              f"trace {r['nearest_trace_length_km']} km)")


if __name__ == "__main__":
    main()
