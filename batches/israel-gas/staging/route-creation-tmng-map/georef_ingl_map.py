#!/usr/bin/env python3
"""Georeference the INGL transmission-system map (big-map.jpg, full-res 2524x3494).

Source: https://www.ingl.co.il/wp-content/uploads/2024/04/big-map.jpg (the
"Transmission Map" on https://www.ingl.co.il/en/holancha/, fetched 2026-07-23).
The sheet is rendered on the Israeli TM grid (ITM, EPSG:2039) with gridlines
every 20,000 m. Gridlines are faint (~4-10 luminance dips, 1-3 px wide) so
per-line peak detection fails; instead a comb fit (period + phase maximizing
the summed dip score over the sea region) recovers the grid on each axis.
Label anchoring was verified visually against the margin labels:
  vertical line x=60.5  <-> E 60000   (period 216.25 px)
  horizontal line y=190 <-> N 800000  (period 216.80 px)
=> ~92.5 m/px, square pixels. pyproj EPSG:2039 -> 4326 completes pixel->WGS84.
No GDAL/rasterio (pattern: derive_tama_strips.py).

Outputs georef_params.json (fit + landmark check pixels).
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image
from pyproj import Transformer

HERE = Path(__file__).parent
IMG = HERE / "maps" / "ingl_big_map_fullres.jpg"
GRID = 20000.0

im = Image.open(IMG).convert("RGB")
W, H = im.size
a = np.asarray(im, dtype=np.int16)


def comb_fit(dip, extent):
    """Find (period, phase) maximizing summed dip score on a 20-km comb."""
    best = None
    for p in np.arange(210.0, 224.0, 0.05):
        for ph in np.arange(0, p, 0.5):
            idx = np.arange(ph, extent, p).astype(int)
            idx = idx[idx < extent]
            s = sum(dip[np.clip(idx + d, 0, extent - 1)].sum() for d in (-1, 0, 1))
            if best is None or s > best[0]:
                best = (s, p, ph)
    return best


# vertical gridlines: dip score per column over the (mostly sea) left band
band = a[300:2800, :1100].mean(axis=2)
dip_v = (band < np.median(band, axis=1, keepdims=True) - 3).mean(axis=0)
sv, pv, phv = comb_fit(dip_v, 1100)

# horizontal gridlines: dip score per row over the sea columns
band2 = a[:, 60:900].mean(axis=2)
dip_h = (band2 < np.median(band2, axis=0, keepdims=True) - 3).mean(axis=1)
sh, ph_, phh = comb_fit(dip_h, H)

print(f"vertical:   period {pv:.2f} px, phase {phv:.1f}, score {sv:.2f}")
print(f"horizontal: period {ph_:.2f} px, phase {phh:.1f}, score {sh:.2f}")

# label anchors (verified visually against margin labels 2026-07-23)
E_AT_PHASE = 60000.0   # easting of vertical line at x=phv
N_AT_PHASE = 800000.0  # northing of horizontal line at y=phh

e_per_px = GRID / pv
n_per_px = -GRID / ph_
e_int = E_AT_PHASE - e_per_px * phv
n_int = N_AT_PHASE - n_per_px * phh
print(f"E = {e_per_px:.4f}*x + {e_int:.1f}")
print(f"N = {n_per_px:.4f}*y + {n_int:.1f}")
print(f"scale: {e_per_px:.2f} m/px E-W, {-n_per_px:.2f} m/px N-S "
      f"(square-pixel delta {abs(abs(n_per_px) - e_per_px):.2f} m/px)")

to_itm = Transformer.from_crs(4326, 2039, always_xy=True)
to_wgs = Transformer.from_crs(2039, 4326, always_xy=True)


def px_to_lonlat(x, y):
    return to_wgs.transform(e_per_px * x + e_int, n_per_px * y + n_int)


def lonlat_to_px(lon, lat):
    E, N = to_itm.transform(lon, lat)
    return (E - e_int) / e_per_px, (N - n_int) / n_per_px


landmarks = {
    "Orot Rabin power plant (Hadera)": (34.8790, 32.4703),
    "Ashdod port breakwater": (34.6480, 31.8300),
    "Haifa Bazan refinery": (35.0520, 32.8060),
    "Sdom Dead Sea Works": (35.3650, 31.0300),
    "Beer Sheva center": (34.7913, 31.2530),
    "Sea of Galilee south tip": (35.5880, 32.7080),
}
lm_px = {k: [round(v, 1) for v in lonlat_to_px(*ll)] for k, ll in landmarks.items()}
for k, v in lm_px.items():
    print(f"  {k}: px {v}")

params = {
    "image": IMG.name,
    "source_url": "https://www.ingl.co.il/wp-content/uploads/2024/04/big-map.jpg",
    "source_page": "https://www.ingl.co.il/en/holancha/",
    "fetched": "2026-07-23",
    "width": W, "height": H,
    "crs_grid": "EPSG:2039",
    "v_period_px": pv, "v_phase_px": phv, "e_at_phase": E_AT_PHASE,
    "h_period_px": ph_, "h_phase_px": phh, "n_at_phase": N_AT_PHASE,
    "e_per_px": e_per_px, "e_intercept": e_int,
    "n_per_px": n_per_px, "n_intercept": n_int,
    "landmark_check_px": lm_px,
}
(HERE / "georef_params.json").write_text(json.dumps(params, indent=2))
print("wrote georef_params.json")
