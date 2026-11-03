"""Trace the magenta dashed 'S Mississippi Project' line on page 1 of Energy Transfer's
binding open season notice (map dated 10/9/2026). Pixels only; lon/lat come from georef.py.

Mask: magenta (r>140, b>140, g<110, r-g>80) in the window x 525-660, y 575-655. The dashes are
solid blobs; the label text under the line is thin, so connected blobs under 6 pixels are dropped.
The blob centroids, ordered from the Perryville star to the southeast end, are the trace.
Usage: python -I trace_magenta.py <map.jpg> <trace.json>"""
import json, sys
import numpy as np
from PIL import Image
from scipy import ndimage

img, out = sys.argv[1], sys.argv[2]
a = np.array(Image.open(img).convert("RGB")).astype(int)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
m = (r > 140) & (b > 140) & (g < 110) & (r - g > 80)
win = np.zeros_like(m); win[575:655, 525:660] = True
lab, n = ndimage.label(m & win, structure=np.ones((3, 3)))
pts = []
for i in range(1, n + 1):
    ys, xs = np.nonzero(lab == i)
    if len(xs) >= 6:
        pts.append((float(xs.mean()), float(ys.mean()), len(xs)))
pts.sort(key=lambda p: p[0] + 0.5 * p[1])          # along the NW -> SE line
# Label letters that survive the size cut sit 6-10 px BELOW the line: drop any point east of the
# bend at the star that lies more than 4 px below the chord from the bend to the last dash.
bend = next(p for p in pts if p[0] > 560 and p[1] > 600)
last = max(pts, key=lambda p: p[0])
k = (last[1] - bend[1]) / (last[0] - bend[0])
pts = [p for p in pts if p[0] < 555 or p[1] - (bend[1] + k * (p[0] - bend[0])) <= 4]
line = [[round(x, 1), round(y, 1)] for x, y, _ in pts]
# The dashes start at the rim of the Perryville star (the receipt point the notice names). The
# star's center, from its blue fill (b>180, r<80, g<120) in x 522-548, y 570-595, starts the trace.
sb = (b > 180) & (r < 80) & (g < 120); sw = np.zeros_like(sb); sw[570:595, 522:548] = True
sy, sx = np.nonzero(sb & sw)
line.insert(0, [round(float(sx.mean()), 1), round(float(sy.mean()), 1)])
# The line ends in an arrowhead that touches the FGT line (the delivery point). Its tip, the
# magenta pixel of the last dash farthest along the line (max x + y), ends the trace.
ly, lx = np.nonzero(lab == lab[int(round(last[1])), int(round(last[0]))]) if lab[int(round(last[1])), int(round(last[0]))] else np.nonzero(m & win)
tip = max(zip(lx.tolist(), ly.tolist()), key=lambda q: q[0] + q[1])
line.append([float(tip[0]), float(tip[1])])
json.dump({"image": "maps/et_binding_open_season_20261028_p1_map.jpg", "polylines": [line],
           "notes": "Centroids of the magenta dashes of the 'S Mississippi Project' line, ordered from the Perryville star southeast, starting at the star center and ending at the arrowhead tip on the FGT line; blobs under 6 px and blobs more than 4 px below the line (label text) dropped."},
          open(out, "w"), indent=1)
print(len(line), "points"); print(line)
