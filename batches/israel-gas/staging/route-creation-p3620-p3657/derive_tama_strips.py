#!/usr/bin/env python3
"""Derive pipeline-strip midlines from the TAMA 37/A/2/7 statutory blueprint GIS
bundle (fetched_layers/tama_37a27_1053432_gis.zip, from
https://apps.land.gov.il/IturTabotData/download/jerus/1053432.zip).

The zip holds two scanned "proposed state" sheets as JPG + JGW world file
(EPSG:2039 ITM): sheet 1 onshore (0.42 m/px), sheet 2 marine (1.02 m/px).
The green cross-hatched pipeline strip (רצועת צנרת) is color-segmented; every
output coordinate is a centroid of segmented source pixels mapped through the
world-file affine — nothing is hand-drawn.

Outputs (fetched_layers/):
  p3620_ashdod_strip_midline.geojson  — onshore strip midline (~1.5 km)
  p3657_combined_midline.geojson      — marine strip midline (Ashdod ~9.2 km)
                                        spliced onto the NtM 113/2024 corridor
                                        midline (see derive_p3657_midline.py)

Requires: numpy, scipy, pillow, pyproj, shapely (requirements.txt).
"""
import json
import math
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image
from pyproj import Transformer
from scipy import ndimage

Image.MAX_IMAGE_PIXELS = None
HERE = Path(__file__).parent
FL = HERE / "fetched_layers"
T_FWD = Transformer.from_crs(2039, 4326, always_xy=True)
T_INV = Transformer.from_crs(4326, 2039, always_xy=True)


def load_sheets(tmp: Path):
    """Extract the two JPG+JGW pairs (Hebrew cp1255 names → positional)."""
    z = zipfile.ZipFile(FL / "tama_37a27_1053432_gis.zip")
    infos = sorted(z.infolist(), key=lambda i: i.filename)
    out = {}
    # pairs sort as (-1.jgw, -1.jpg, -2.jgw, -2.jpg)
    for tag, (jgw_i, jpg_i) in {"onshore": (0, 1), "marine": (2, 3)}.items():
        jgw = z.read(infos[jgw_i]).decode().split()
        A, D, B, E, C, F = (float(v) for v in jgw)
        p = tmp / f"{tag}.jpg"
        p.write_bytes(z.read(infos[jpg_i]))
        out[tag] = (p, (A, D, B, E, C, F))
    return out


def green_mask(img_path: Path):
    im = np.asarray(Image.open(img_path).convert("RGB"))
    r, g, b = (im[..., i].astype(int) for i in range(3))
    return (g > r + 20) & (g > b + 10) & (g > 90)


def components(mask, close_px=15):
    m2 = ndimage.binary_closing(mask, structure=np.ones((close_px, close_px)))
    lab, n = ndimage.label(m2)
    sizes = ndimage.sum(m2, lab, range(1, n + 1))
    order = np.argsort(sizes)[::-1]
    return lab, [int(o) + 1 for o in order], sizes[order].astype(int)


def px_to_itm(cols, rows, wf):
    A, D, B, E, C, F = wf
    return A * cols + B * rows + C, D * cols + E * rows + F


def pca_bin_midline(mask, nbins=40):
    """Centroid path along the principal axis — for near-straight pieces."""
    ys, xs = np.nonzero(mask)
    pts = np.column_stack([xs, ys]).astype(float)
    mean = pts.mean(0)
    _, _, vt = np.linalg.svd(pts - mean, full_matrices=False)
    t = (pts - mean) @ vt[0]
    bins = np.linspace(t.min(), t.max(), nbins + 1)
    return np.array([pts[(t >= bins[i]) & (t <= bins[i + 1])].mean(0)
                     for i in range(nbins)
                     if ((t >= bins[i]) & (t <= bins[i + 1])).sum() > 20])


def chain(segs):
    """Order near-straight pieces end-to-end by nearest endpoints."""
    segs = [s.tolist() for s in segs]
    used = [False] * len(segs)
    path = segs[0]
    used[0] = True
    for _ in range(len(segs) - 1):
        best = None
        for j, s in enumerate(segs):
            if used[j]:
                continue
            for flip in (False, True):
                ss = s[::-1] if flip else s
                for front in (False, True):
                    d = (math.dist(path[0], ss[-1]) if front
                         else math.dist(path[-1], ss[0]))
                    if best is None or d < best[0]:
                        best = (d, j, flip, front)
        _, j, flip, front = best
        ss = segs[j][::-1] if flip else segs[j]
        path = (ss + path) if front else (path + ss)
        used[j] = True
    return np.array(path)


def gkm(a, b):
    lon1, lat1, lon2, lat2 = map(math.radians, (*a, *b))
    h = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
    return 2 * 6371.0088 * math.asin(math.sqrt(h))


def length_km(cs):
    return sum(gkm(cs[i], cs[i + 1]) for i in range(len(cs) - 1))


def write_fc(path, name, props, coords):
    fc = {"type": "FeatureCollection", "features": [{
        "type": "Feature",
        "properties": {"name": name, **props},
        "geometry": {"type": "LineString",
                     "coordinates": [[round(x, 6), round(y, 6)] for x, y in coords]},
    }]}
    path.write_text(json.dumps(fc, indent=1))


def main():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        sheets = load_sheets(Path(td))

        # ---- onshore sheet -> P3620 Ashdod strip midline ----------------- #
        p, wf = sheets["onshore"]
        lab, order, sizes = components(green_mask(p))
        # largest = HDD shore-crossing compound; pieces 2-5 = the thin strip
        segs = [pca_bin_midline(lab == order[i]) for i in range(1, 5)]
        path_px = chain(segs)
        x, y = px_to_itm(path_px[:, 0], path_px[:, 1], wf)
        lon, lat = T_FWD.transform(x, y)
        onshore = np.column_stack([lon, lat])
        print(f"onshore strip: {length_km([tuple(c) for c in onshore]):.2f} km, "
              f"{len(onshore)} pts; compound size {sizes[0]} px")
        write_fc(FL / "p3620_ashdod_strip_midline.geojson",
                 "P3620 Ashdod onshore pipeline-strip midline "
                 "(TAMA 37/A/2/7 georeferenced blueprint)", {}, onshore)

        # ---- marine sheet -> strip midline, spliced onto NtM midline ----- #
        p, wf = sheets["marine"]
        lab, order, _ = components(green_mask(p))
        strip = lab == order[0]
        ys, xs = np.nonzero(strip)
        rng = np.random.default_rng(0)
        sel = rng.choice(len(ys), size=min(len(ys), 300000), replace=False)
        ix, iy = px_to_itm(xs[sel].astype(float), ys[sel].astype(float), wf)

        ntm = json.load(open(FL / "p3657_ntm_midline.geojson"))
        ref_ll = ntm["features"][0]["geometry"]["coordinates"]
        rx, ry = T_INV.transform([c[0] for c in ref_ll], [c[1] for c in ref_ll])
        ref = np.column_stack([rx, ry])
        cum = np.concatenate([[0], np.cumsum(np.hypot(np.diff(ref[:, 0]),
                                                      np.diff(ref[:, 1])))])

        idx = np.random.default_rng(1).choice(len(ix), size=40000, replace=False)
        pts = np.column_stack([ix[idx], iy[idx]])
        best_s = np.zeros(len(pts))
        best_d = np.full(len(pts), np.inf)
        for i in range(len(ref) - 1):
            a, b = ref[i], ref[i + 1]
            v = b - a
            L2 = v @ v
            if L2 == 0:
                continue
            t = np.clip(((pts - a) @ v) / L2, 0, 1)
            proj = a + t[:, None] * v
            d = np.einsum("ij,ij->i", pts - proj, pts - proj)
            upd = d < best_d
            best_d[upd] = d[upd]
            best_s[upd] = cum[i] + t[upd] * math.sqrt(L2)
        keep = np.sqrt(best_d) < 1500
        s, P = best_s[keep], pts[keep]
        bins = np.arange(s.min(), s.max() + 200, 200.0)
        mids = np.array([[P[m].mean(0)[0], P[m].mean(0)[1], 0.5 * (bins[i] + bins[i + 1])]
                         for i in range(len(bins) - 1)
                         for m in [(s >= bins[i]) & (s < bins[i + 1])] if m.sum() > 30])
        mids = mids[np.argsort(mids[:, 2])]
        lon, lat = T_FWD.transform(mids[:, 0], mids[:, 1])
        marine = np.column_stack([lon, lat])   # Ashdod compound -> seam

        seam = tuple(marine[-1])
        dists = [gkm(seam, tuple(c)) for c in ref_ll]
        i0 = int(np.argmin(dists))
        combined = [tuple(c) for c in marine] + [tuple(c) for c in ref_ll[i0 + 1:]]
        print(f"marine strip: {length_km([tuple(c) for c in marine]):.2f} km; "
              f"seam at ntm vertex {i0} ({dists[i0]*1000:.0f} m); "
              f"combined {length_km(combined):.2f} km")
        write_fc(FL / "p3657_combined_midline.geojson",
                 "P3657 combined centerline: TAMA 37/A/2/7 marine strip midline "
                 "(Ashdod ~9.2 km) + NtM 113/2024 corridor midline (remainder)",
                 {"seam_wgs84": [round(seam[0], 6), round(seam[1], 6)]}, combined)


if __name__ == "__main__":
    main()
