#!/usr/bin/env python3
"""QC overlays for the Middle East 2026 map traces.

1. Extracted routes redrawn on the rendered source page, in page space.
   Falsifiability check: a trace that does not sit on a drawn line is not pipe.
2. Georeferenced routes against Natural Earth coastline, in lon/lat.
"""
from __future__ import annotations

import json
from pathlib import Path

import fitz
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

PDF = Path("/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher/"
           "sources/middle-east/energy-map-of-the-middle-east-2026-peregrine-bush.pdf")
COL = {"gas": "#d7191f", "oil": "#00922f"}
OUT = Path("overlays")


def on_source(zoom=1.6):
    doc = fitz.open(PDF)
    pix = doc[0].get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    img = plt.imread(__import__("io").BytesIO(pix.tobytes("png")))
    pipes = json.load(open("traces/pipelines_pagespace.json"))["features"]
    fig, ax = plt.subplots(figsize=(22, 21), dpi=110)
    ax.imshow(img, extent=[0, pix.width / zoom, pix.height / zoom, 0])
    for p in pipes:
        xs = [q[0] for q in p["points"]]
        ys = [q[1] for q in p["points"]]
        ax.plot(xs, ys, color="black", lw=2.6, alpha=0.85, solid_capstyle="round")
        ax.plot(xs, ys, color=COL[p["commodity"]], lw=1.0, alpha=1.0)
    ax.set_axis_off()
    ax.set_title("extracted pipeline strokes (black halo) on the source page — "
                 "a trace off a drawn line is not pipe", fontsize=13)
    fig.tight_layout()
    fig.savefig(OUT / "qc_me2026_on_source.png", bbox_inches="tight")
    plt.close(fig)
    print("wrote overlays/qc_me2026_on_source.png")


def georeferenced():
    import geopandas as gpd
    ne = Path("/Users/baird/Dropbox/_gis-data/_natural_earth_data")
    coast = gpd.read_file(ne / "ne_10m_coastline" / "ne_10m_coastline.shp")
    feats = json.load(open("me2026_pipelines.geojson"))["features"]
    fig, ax = plt.subplots(figsize=(17, 15), dpi=110)
    coast.plot(ax=ax, color="#7fb8d8", lw=0.6)
    for f in feats:
        c = [p[0] for p in f["geometry"]["coordinates"]]
        d = [p[1] for p in f["geometry"]["coordinates"]]
        ax.plot(c, d, color=COL[f["properties"]["commodity"]], lw=0.9,
                ls="-" if not f["properties"]["dashed"] else "--")
    ax.set_xlim(32, 65)
    ax.set_ylim(11, 42)
    ax.set_aspect(1 / 0.85)
    ax.set_title("georeferenced routes (red=gas, green=oil) vs Natural Earth coastline")
    ax.grid(alpha=0.25, lw=0.4)
    fig.tight_layout()
    fig.savefig(OUT / "qc_me2026_georeferenced.png", bbox_inches="tight")
    plt.close(fig)
    print("wrote overlays/qc_me2026_georeferenced.png")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    on_source()
    georeferenced()
