#!/usr/bin/env python3
"""Overlay existing GEM route geometries (routes repo) on the georeferenced INGL map.

Draws each PID in a distinct color on a lightened copy of the full-res map and
saves (a) a full-map composite and (b) per-PID crops sized to the geometry bbox,
for visual match/improve/missing classification (Phase 1 of the crosswalk).
Reads the sibling routes-repo mirror directly (read-only).
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance
from pyproj import Transformer

HERE = Path(__file__).parent
ROUTES = Path("/Users/baird/Dropbox/_git_ALL/_github-repos-gem/GOIT-GGIT-pipeline-routes/data/individual-routes/gas-pipelines")
OUT = HERE / "overlays"
OUT.mkdir(exist_ok=True)

P = json.load(open(HERE / "georef_params.json"))
to_itm = Transformer.from_crs(4326, 2039, always_xy=True)


def lonlat_to_px(lon, lat):
    E, N = to_itm.transform(lon, lat)
    return (E - P["e_intercept"]) / P["e_per_px"], (N - P["n_intercept"]) / P["n_per_px"]


PIDS = {
    "P3658": (230, 0, 0),      # INGL network row - red
    "P2197": (255, 0, 255),    # Ramle-Elyakim - magenta
    "P0462": (0, 0, 0),        # El Arish-Ashkelon (EMG) - black
    "P0480": (255, 140, 0),    # Israel-Jordan - orange
    "P5276": (0, 200, 0),      # Gas for Gaza - green
    "P7864": (128, 0, 255),    # Nitzana - purple
    "P3620": (0, 120, 255),    # Ashdod-Ashkelon onshore - blue
    "P3657": (0, 220, 220),    # Ashdod-Ashkelon offshore - cyan
    "P8000": (140, 90, 0),     # Leviathan-Egypt (cancelled) - brown
    "P0479": (255, 220, 0),    # Israel-Cyprus - yellow
    "P0827": (90, 90, 90),     # EastMed - gray
}

base = Image.open(HERE / "maps" / "ingl_big_map_fullres.jpg").convert("RGB")
faded = ImageEnhance.Contrast(ImageEnhance.Brightness(base).enhance(1.35)).enhance(0.55)
W, H = base.size


def coords_of(geom):
    if geom is None:
        return []
    t = geom["type"]
    if t == "LineString":
        return [geom["coordinates"]]
    if t == "MultiLineString":
        return geom["coordinates"]
    if t == "GeometryCollection":
        out = []
        for g in geom["geometries"]:
            out += coords_of(g)
        return out
    return []


composite = faded.copy()
dc = ImageDraw.Draw(composite)
report = {}
for pid, color in PIDS.items():
    f = ROUTES / f"{pid}.geojson"
    if not f.exists():
        report[pid] = "NO FILE"
        continue
    gj = json.load(open(f))
    feats = gj.get("features", [])
    lines = []
    for ft in feats:
        lines += coords_of(ft.get("geometry"))
    if not lines:
        report[pid] = "EMPTY GEOMETRY"
        continue
    pts_all = []
    per = faded.copy()
    dp = ImageDraw.Draw(per)
    n_on = n_tot = 0
    for line in lines:
        px = [lonlat_to_px(c[0], c[1]) for c in line]
        pts_all += px
        n_tot += len(px)
        n_on += sum(1 for x, y in px if 0 <= x < W and 0 <= y < H)
        for d in (dc, dp):
            d.line([(x, y) for x, y in px], fill=color, width=5)
    xs = [p[0] for p in pts_all]
    ys = [p[1] for p in pts_all]
    x0, x1 = max(0, min(xs) - 120), min(W, max(xs) + 120)
    y0, y1 = max(0, min(ys) - 120), min(H, max(ys) + 120)
    if x1 > x0 and y1 > y0:
        crop = per.crop((int(x0), int(y0), int(x1), int(y1)))
        # keep crops viewable
        if max(crop.size) > 1500:
            r = 1500 / max(crop.size)
            crop = crop.resize((int(crop.width * r), int(crop.height * r)))
        crop.save(OUT / f"overlay_{pid}.png")
    report[pid] = f"{len(lines)} part(s), {n_tot} pts, {n_on}/{n_tot} on-sheet"

composite.save(OUT / "overlay_all.png")
half = composite.resize((W // 2, H // 2))
half.save(OUT / "overlay_all_half.png")
print(json.dumps(report, indent=2))
