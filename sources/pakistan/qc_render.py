#!/usr/bin/env python3
"""Regenerate the two tracked QC renders in extraction/ from the current extraction.

    python sources/pakistan/qc_render.py

  * qc_page_overlay.png  -- extracted geometry drawn back over the rendered page, in
    PAGE space. This is the check that answers "did we pick up the right ink?"
  * qc_georeferenced.png -- the same geometry in lon/lat with the GCP cities, i.e.
    the check that answers "did the projection put it in the right place?"

Dashed classes are drawn dashed, so a stitched run is visually distinguishable from a
solid line at a glance. Run prepare.py first; this reads data/ppis-pipelines.geojson.
"""
import json, importlib.util, numpy as np, fitz
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("prep", HERE / "prepare.py")
P = importlib.util.module_from_spec(spec); spec.loader.exec_module(P)

STYLE = {                       # class -> (colour, short label)
    "sngpl_gas_existing":         ("#e03030", "SNGPL existing"),
    "sngpl_gas_planned":          ("#e03030", "SNGPL planned (dashed)"),
    "ssgcl_gas_existing":         ("#1030c0", "SSGCL existing"),
    "ssgcl_gas_planned":          ("#1030c0", "SSGCL planned (dashed)"),
    "iran_pakistan_gas_planned":  ("#ff00ff", "Iran-Pakistan"),
    "tapi_gas_planned":           ("#00c8ff", "TAPI"),
    "pakistan_stream_gas_planned":("#6633ff", "Pakistan Stream"),
    "crude_oil_existing":         ("#ff8000", "crude oil"),
    "refined_oil_existing":       ("#187018", "refined oil"),
    "oil_planned_uc":             ("#00c000", "oil planned/UC"),
}

def page_overlay(out, zoom=4):
    page, DR = P.load_drawings()
    PATHS, _, _ = P.build_paths(DR)
    pm = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    img = np.frombuffer(pm.samples, np.uint8).reshape(pm.height, pm.width, pm.n)
    fig, ax = plt.subplots(figsize=(pm.width/110, pm.height/110), dpi=110)
    ax.imshow(img); ax.set_axis_off()
    seen = set()
    for nm, paths in PATHS.items():
        col, lab = STYLE[nm]
        for pl, drawn, nmarks, _ in paths:
            a = np.array(pl) * zoom
            ax.plot(a[:, 0], a[:, 1], color=col, lw=1.1,
                    ls=(0, (2.5, 1.5)) if drawn == "dashed" else "-",
                    label=None if nm in seen else f"{lab} ({len(paths)})")
            seen.add(nm)
    ax.set_xlim(30*zoom, 515*zoom); ax.set_ylim(640*zoom, 152*zoom)   # the map body only
    ax.legend(loc="lower left", bbox_to_anchor=(0.30, 0.03), fontsize=8, framealpha=.92)
    ax.set_title("PPIS Energy Infrastructure Map 2025 (p.6) — extracted geometry over the page",
                 fontsize=9)
    fig.tight_layout(pad=0.2); fig.savefig(out, bbox_inches="tight"); plt.close(fig)

def georeferenced(out):
    fc = json.loads((HERE / "data" / "ppis-pipelines.geojson").read_text())
    import sys; sys.path.insert(0, str(HERE / "extraction"))
    from gcps import GCP
    fig, ax = plt.subplots(figsize=(11, 11), dpi=110)
    seen = set()
    for f in fc["features"]:
        pr = f["properties"]; col, lab = STYLE[pr["feature_class"]]
        a = np.array(f["geometry"]["coordinates"])
        ax.plot(a[:, 0], a[:, 1], color=col, lw=0.8,
                ls=(0, (2.5, 1.5)) if pr.get("drawn_as") == "dashed" else "-",
                label=None if pr["feature_class"] in seen else lab)
        seen.add(pr["feature_class"])
    ax.scatter([g[2] for g in GCP], [g[3] for g in GCP], s=6, c="k", zorder=5)
    for g in GCP[:14]: ax.annotate(g[4], (g[2], g[3]), fontsize=6, xytext=(3, 2),
                                   textcoords="offset points")
    acc = fc["ppis_extraction"]["georeference_accuracy_km"]
    ax.set_xlabel("lon"); ax.set_ylabel("lat"); ax.set_aspect(1/np.cos(np.radians(30)))
    ax.grid(alpha=.25, lw=.4)
    ax.set_title("PPIS Energy Infrastructure Map 2025 (p.6) — georeferenced pipelines\n"
                 f"{len(fc['features'])} features · "
                 f"{sum(f['properties']['geodesic_km'] for f in fc['features']):.0f} km · "
                 f"median GCP residual {acc['median_km']:.1f} km", fontsize=10)
    ax.legend(loc="lower left", fontsize=7)
    fig.tight_layout(); fig.savefig(out); plt.close(fig)

if __name__ == "__main__":
    page_overlay(HERE / "extraction" / "qc_page_overlay.png")
    georeferenced(HERE / "extraction" / "qc_georeferenced.png")
    print("wrote extraction/qc_page_overlay.png, extraction/qc_georeferenced.png")
