#!/usr/bin/env python3
"""Digitize the pipeline network off page 6 of the PPIS 'Investment Brochure 2025'.

Page 6 is the Directorate General of Petroleum Concessions / PPIS "Energy
Infrastructure Map - 2025" -- VECTOR art, so the routes are recovered as exact
page-space geometry rather than raster-traced, then georeferenced.

    python sources/pakistan/prepare.py

Rebuilds data/ppis-pipelines.geojson from the tracked PDF. Deterministic:
same PDF in, byte-identical geometry out. READ NOTES.md before using the output.
"""
import fitz, json, re, sys, numpy as np
from pathlib import Path
from collections import defaultdict
from scipy.optimize import least_squares
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import minimum_spanning_tree

HERE = Path(__file__).resolve().parent
PDF = HERE / "Investment Brochure 2025.pdf"
PAGE = 5                                   # 0-based; page 6 of 28
D = np.pi / 180

# ---------------------------------------------------------------- map frame
# Neat-line of the map body, from the page's single large stroked rect.
X0, Y0, X1, Y1 = 44.97, 160.93, 504.13, 627.24
# Panels and insets drawn INSIDE the neat-line. The two insets (Hyderabad-Badin,
# Karachi) are at their own, larger scales -- georeferencing them with the
# main-map transform would be wrong, so they are excluded, not reprojected.
EXCL = [(420, 358, 504.2, 627.3),   # HYDERABAD-BADIN inset (+ KARACHI inset below it)
        (44.9, 160.9, 278, 280),    # energy-supply statistics panels
        (46, 495, 165, 620),        # LEGEND
        (340, 490, 420, 575),       # installed-capacity panel
        (290, 575, 420, 620)]       # energy-reserves panel

def in_map(x, y):
    if not (X0 <= x <= X1 and Y0 <= y <= Y1):
        return False
    return not any(a <= x <= c and b <= y <= d for a, b, c, d in EXCL)

# ------------------------------------------------------- the class dictionary
# Colours are the ones used ON THE MAP, which drift slightly from the LEGEND
# swatches (legend crude (1.0,.6,.204) vs map (1.0,.522,.039); legend refined
# (0,.659,.349) vs map (.216,.839,.043)). Legend text is the authority for the
# NAME, the map colour is the authority for the MATCH.
#
# The PDF carries NO dash arrays at all (every drawing reports dashes '[] 0'), so a
# dashed line exists only as many separate primitives. There are TWO such encodings:
#   * filled polygons ('f')  -- the legend swatches and the inset-scale dashes
#   * HAIRLINE strokes ('s' at width 0.035 pt, ~0.46 pt long, period ~0.7 pt)
#     -- how every dashed line in the MAP BODY is drawn
# The hairline marks therefore land in the same colour+type bucket as the solid
# EXISTING lines, and are separated from them by STROKE WIDTH (see DASH_* below),
# then stitched end-to-end into one LineString per dashed run.
CLASSES = {
    "sngpl_gas_existing":        ((1.0,   0.0,   0.008), "s", "SNGPL GAS PIPELINE EXISTING",        "gas"),
    "ssgcl_gas_existing":        ((0.008, 0.2,   0.8),   "s", "SSGCL GAS PIPELINE EXISTING",        "gas"),
    "sngpl_gas_planned":         ((1.0,   0.0,   0.008), "f", "SNGPL GAS PIPELINE PLANNED",         "gas"),
    "ssgcl_gas_planned":         ((0.008, 0.2,   0.8),   "f", "SSGCL GAS PIPELINE PLANNED",         "gas"),
    "iran_pakistan_gas_planned": ((1.0,   0.0,   1.0),   "f", "IRAN-PAKISTAN GAS PIPELINE PLANNED", "gas"),
    "tapi_gas_planned":          ((0.0,   0.8,   1.0),   "f", "TAPI GAS PIPELINE PLANNED",          "gas"),
    "pakistan_stream_gas_planned":((0.4,  0.2,   1.0),   "f", "PAKISTAN STREAM GAS PIPELINE PLANNED","gas"),
    "crude_oil_existing":        ((1.0,   0.522, 0.039), "s", "CRUDE OIL PIPELINE EXISTING",        "oil"),
    "refined_oil_existing":      ((0.216, 0.839, 0.043), "s", "REFINED OIL PIPELINE EXISTING",      "oil"),
    "oil_planned_uc":            ((0.016, 1.0,   0.008), "s", "OIL PIPELINE UNDER CONST./PLANNED",  "oil"),
}
# The map's legend conflates two GEM statuses in one class ("OIL PIPELINE UNDER
# CONST./PLANNED"), so that class gets a BLANK status rather than a coin-flip between
# 'construction' and 'proposed'. A blank is honest and means this source raises no
# Status_Conflicts for it, by design -- same call the Malaysian Gas Map makes.
STATUS = {"existing": "operating", "planned": "proposed", "uc": ""}

# Which class a stitched DASHED run belongs to. The legend is unambiguous on this:
# SNGPL EXISTING / PLANNED are the same red and SSGCL EXISTING / PLANNED the same
# blue -- solid-vs-dashed is the ONLY thing that separates them. So a dashed run
# found in an "_existing" colour bucket is that operator's PLANNED class, not an
# existing line. (Caveat carried into every such feature and into NOTES.md: the map
# body draws these at hairline weight, ~9x lighter than the legend's own dashed
# swatch, so the assignment rests on colour + dashedness, not on line weight.)
DASH_CLASS = {"sngpl_gas_existing": "sngpl_gas_planned",
              "ssgcl_gas_existing": "ssgcl_gas_planned",
              "oil_planned_uc":     "oil_planned_uc"}

# Hairline-dash detection + stitching. A stroke-width group is dash marks when it is
# hairline, populated, and uniformly short; a run needs >=3 marks and >=1.5 pt of
# extent, which is what keeps arrowhead/symbol clusters (tight groups of ~0.25 pt
# strokes inside a 0.1 x 0.3 pt box) from being welded into a "pipeline".
DASH_W_MAX, DASH_LEN_MAX, DASH_MIN_N = 0.10, 0.80, 5
DASH_GAP, DASH_ANG_DEG, DASH_MIN_MARKS, DASH_MIN_RUN_PT = 1.6, 60.0, 3, 1.5

# Deliberately NOT pipelines, though they sit in the same colour neighbourhood.
# Recorded here so a future run does not "discover" them again:
#   (0.137,0.588,0.929)s rivers        (1.0,0.0,0.0)s   power stations
#   (0.023,0.0,1.0)s     plant icons   (0.929,0.18,0.22)f LoC / disputed boundary
#   (0.929,0.196,0.216)f GAS FIELD ellipses   (0.341,0.725,0.325)f OIL FIELD ellipses
# The two field-ellipse classes are the only real trap: they are filled polygons in
# a pipeline-ish colour. They separate cleanly on SHAPE -- field ellipses run
# aspect ~2.0 at ~1.0 pt, true dash marks aspect ~1.3-1.5 at ~0.33 pt.

def load_drawings():
    page = fitz.open(PDF)[PAGE]
    return page, page.get_drawings()

def class_key(d):
    t = "s" if d["type"] == "s" else "f"
    c = d.get("color") if t == "s" else (d.get("fill") or d.get("color"))
    return None if c is None else (tuple(round(v, 3) for v in c), t)

def flatten(items):
    """PDF path items -> list of point sequences (cubics sampled at 8 points)."""
    out = []
    for i in items:
        if i[0] == "l":
            out.append([(i[1].x, i[1].y), (i[2].x, i[2].y)])
        elif i[0] == "c":
            P = [np.array([q.x, q.y]) for q in i[1:5]]
            t = np.linspace(0, 1, 8)[:, None]
            b = (1-t)**3*P[0] + 3*(1-t)**2*t*P[1] + 3*(1-t)*t**2*P[2] + t**3*P[3]
            out.append([tuple(v) for v in b])
        elif i[0] == "re":
            r = i[1]
            out.append([(r.x0, r.y0), (r.x1, r.y0), (r.x1, r.y1), (r.x0, r.y1), (r.x0, r.y0)])
        elif i[0] == "qu":
            q = i[1]
            out.append([(q.ul.x, q.ul.y), (q.ur.x, q.ur.y), (q.lr.x, q.lr.y),
                        (q.ll.x, q.ll.y), (q.ul.x, q.ul.y)])
    return out

# ------------------------------------------------------------------ chaining
def chain_strokes(segs, tol=0.25):
    """Exact: solid lines are already polylines. Quantize endpoints, walk the graph.
    Splits at junctions, so one path == one branch between network nodes."""
    q = lambda p: (round(p[0]/tol), round(p[1]/tol))
    adj, node = defaultdict(list), {}
    for a, b in segs:
        ka, kb = q(a), q(b); node[ka], node[kb] = a, b
        if ka == kb: continue
        adj[ka].append(kb); adj[kb].append(ka)
    used, out = set(), []
    e = lambda u, v: (u, v) if u <= v else (v, u)
    for start in [k for k in adj if len(adj[k]) != 2] + list(adj):
        for nxt in list(adj[start]):
            if e(start, nxt) in used: continue
            used.add(e(start, nxt)); path, cur = [start, nxt], nxt
            while True:
                cand = [w for w in adj[cur] if e(cur, w) not in used]
                if len(cand) != 1: break
                used.add(e(cur, cand[0])); path.append(cand[0]); cur = cand[0]
            if len(path) > 1: out.append([node[k] for k in path])
    return out

def chain_dashes(dds, maxgap=3.0, minlen=4.0):
    """Dashed lines: reduce each dash polygon to its centroid, MST over the k-NN
    graph, then split the tree into branches. MST (not nearest-neighbour walk)
    because the planned corridors have spurs, and a greedy walk jumps across them."""
    C = [np.array([p for poly in flatten(d["items"]) for p in poly]).mean(0) for d in dds
         if flatten(d["items"])]
    C = np.array([c for c in C if in_map(*c)])
    if len(C) < 3: return []
    pairs = cKDTree(C).query_pairs(maxgap)
    if not pairs: return []
    I = np.array(sorted(pairs)); W = np.linalg.norm(C[I[:, 0]] - C[I[:, 1]], axis=1)
    M = minimum_spanning_tree(coo_matrix((W + 1e-9, (I[:, 0], I[:, 1])), shape=(len(C),)*2)).tocoo()
    adj = defaultdict(list)
    for a, b in zip(M.row, M.col): adj[a].append(b); adj[b].append(a)
    used, out = set(), []
    for start in [k for k in adj if len(adj[k]) != 2] + list(adj):
        for nxt in list(adj[start]):
            k = (min(start, nxt), max(start, nxt))
            if k in used: continue
            used.add(k); path, cur = [start, nxt], nxt
            while True:
                cand = [w for w in adj[cur] if (min(cur, w), max(cur, w)) not in used]
                if len(cand) != 1: break
                used.add((min(cur, cand[0]), max(cur, cand[0]))); path.append(cand[0]); cur = cand[0]
            if np.linalg.norm(np.diff(C[path], axis=0), axis=1).sum() >= minlen:
                out.append([tuple(v) for v in C[path]])
    return out

def split_dash_marks(dds):
    """Split one stroke class's in-map segments into (dash marks, solid segments).

    Dash marks are recognised by STROKE WIDTH, not by length or isolation: the map
    body draws every dashed line with a hairline pen while solid lines use
    0.141/0.247/0.317/0.493 pt. Length alone is not enough -- arrowheads and symbol
    strokes are short too, but they are not hairline."""
    g = defaultdict(list)
    for d in dds:
        w = round(d.get("width") or 0, 3)
        for poly in flatten(d["items"]):
            for a, b in zip(poly, poly[1:]):
                if in_map(*a) and in_map(*b) and np.hypot(b[0]-a[0], b[1]-a[1]) > 1e-6:
                    g[w].append((a, b))
    marks, solid = [], []
    for w, S in sorted(g.items()):
        L = np.array([np.hypot(b[0]-a[0], b[1]-a[1]) for a, b in S])
        dash = w <= DASH_W_MAX and len(S) >= DASH_MIN_N and np.median(L) < DASH_LEN_MAX
        (marks if dash else solid).extend(S)
    return marks, solid

def stitch_dashes(marks):
    """Dash marks -> one polyline per dashed run (the user-visible 'single long line').

    Each mark has two ports. Candidate links are port pairs within DASH_GAP that are
    COLLINEAR with both marks' own axes (the angle gate is what stops a dashed line
    from jumping onto a different dashed line it merely passes near); links are then
    taken shortest-first under union-find, so every mark ends up on exactly one chain.

    Returns (runs, n_unstitched). A mark left in a chain too short to be a line is
    DROPPED, not emitted -- a lone 0.46 pt mark is ~1.5 km of fabricated pipeline."""
    A = [np.array(m, float) for m in marks]
    n = len(A)
    if n < DASH_MIN_MARKS: return [], n
    pts = np.array([p for a in A for p in a])
    dirs = np.array([(a[1]-a[0]) / (np.linalg.norm(a[1]-a[0]) or 1) for a in A])
    cos_gate = np.cos(np.radians(DASH_ANG_DEG))
    cand = []
    for i, j in cKDTree(pts).query_pairs(DASH_GAP):
        mi, pi = divmod(i, 2); mj, pj = divmod(j, 2)
        if mi == mj: continue
        v = pts[j] - pts[i]; d = np.linalg.norm(v)
        if d < 1e-12: continue
        u = v / d
        if abs(u @ dirs[mi]) < cos_gate or abs(u @ dirs[mj]) < cos_gate: continue
        cand.append((d, mi, pi, mj, pj))
    cand.sort()
    par = list(range(n))
    def find(x):
        while par[x] != x: par[x] = par[par[x]]; x = par[x]
        return x
    used, link = np.zeros((n, 2), bool), defaultdict(dict)
    for d, mi, pi, mj, pj in cand:
        if used[mi, pi] or used[mj, pj] or find(mi) == find(mj): continue
        used[mi, pi] = used[mj, pj] = True; par[find(mi)] = find(mj)
        link[mi][pi] = (mj, pj); link[mj][pj] = (mi, pi)
    seen, chains = set(), []
    for start in [m for m in range(n) if len(link[m]) < 2] + list(range(n)):
        if start in seen: continue
        entry = 0 if 0 not in link[start] else 1
        chain, cur, ent = [(start, entry)], start, entry
        seen.add(start)
        while True:
            ex = 1 - ent
            if ex not in link[cur]: break
            nxt, npt = link[cur][ex]
            if nxt in seen: break
            seen.add(nxt); chain.append((nxt, npt)); cur, ent = nxt, npt
        chains.append(chain)
    runs, dropped = [], 0
    for ch in chains:
        pl = []
        for m, e in ch:
            pl += [tuple(v) for v in (A[m] if e == 0 else A[m][::-1])]
        extent = np.linalg.norm(np.diff(np.array(pl), axis=0), axis=1).sum()
        if len(ch) >= DASH_MIN_MARKS and extent >= DASH_MIN_RUN_PT:
            runs.append((pl, len(ch)))
        else:
            dropped += len(ch)
    return runs, dropped

# ------------------------------------------------------------ georeferencing
def fit_projection():
    """Lambert Conformal Conic fit to 57 map symbols at known real-world coords.

    The drawn graticule is NOT used as control: its left/right ticks are mutually
    inconsistent by ~1.6 pt in a way that contradicts conic parallel curvature, and
    fitting to it leaves a systematic +12 km NORTH bias across the whole map. Fitting
    to the city symbols instead removes the bias entirely -- and independently
    recovers lam0 = 68.08 E and n = 0.437 against the graticule's own 68 E / 0.439,
    so the two controls agree once the bias is out.
    """
    sys.path.insert(0, str(HERE / "extraction"))
    from gcps import GCP
    G = [g for g in GCP if g[4] != "Skardu"]     # ambiguous symbol: 2.3 pt from SKARDU,
    A = np.array([[g[0], g[1], g[2], g[3]] for g in G], float)   # 3.2 pt from SATPARA
    px, py, lon, lat = A[:, 0], A[:, 1], A[:, 2], A[:, 3]
    def fwd(p, lo, la):
        xa, ya, n, l0, F = p
        rho = F * np.tan(np.pi/4 - la*D/2)**n
        return xa + rho*np.sin(n*(lo-l0)*D), ya + rho*np.cos(n*(lo-l0)*D)
    p0 = [249.8, -2289, 0.506, 67.88, 2912.75/np.tan(np.pi/4 - 36*D/2)**0.506]
    s = least_squares(lambda p: np.concatenate(np.array(fwd(p, lon, lat)) - np.array([px, py])),
                      p0, x_scale="jac", max_nfev=40000)
    P = s.x
    def inv(x, y):
        xa, ya, n, l0, F = P
        x, y = np.asarray(x, float), np.asarray(y, float)
        rho = np.hypot(x - xa, y - ya)
        return (l0 + np.arctan2(x - xa, y - ya)/(n*D),
                (np.pi/2 - 2*np.arctan((rho/F)**(1/n)))/D)
    lo, la = inv(px, py)
    err = np.hypot((lo - lon)*111.32*np.cos(lat*D), (la - lat)*110.57)
    return inv, P, {"n_gcp": len(G), "mean_km": float(err.mean()),
                    "median_km": float(np.median(err)), "p90_km": float(np.percentile(err, 90)),
                    "max_km": float(err.max())}

def geodesic_km(c):
    c = np.asarray(c); la, lo = np.radians(c[:, 1]), np.radians(c[:, 0])
    a = (np.sin(np.diff(la)/2)**2
         + np.cos(la[:-1])*np.cos(la[1:])*np.sin(np.diff(lo)/2)**2)
    return float((6371.0088*2*np.arcsin(np.sqrt(a))).sum())

# ------------------------------------------------------------- map annotations
DIA_RE = re.compile(r'(\d{1,2}(?:\.\d)?)\s*["”″]')
KM_RE  = re.compile(r'(\d{1,4}(?:\.\d+)?)\s*KM', re.I)

def harvest_labels(page):
    out = []
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            txt = re.sub(r"\s+", " ", " ".join(s["text"] for s in l["spans"]).strip())
            if not txt: continue
            bb = l["bbox"]; xc, yc = (bb[0]+bb[2])/2, (bb[1]+bb[3])/2
            if not in_map(xc, yc): continue
            if not (DIA_RE.search(txt) or KM_RE.search(txt)): continue
            out.append({"text": txt, "xy": (xc, yc),
                        "dia_in": [float(v) for v in DIA_RE.findall(txt)],
                        "len_km": [float(v) for v in KM_RE.findall(txt)]})
    return out

def build_paths(DR):
    """Page-space geometry, per class. Returns (paths, buckets, dashinfo), where
    paths[class] is a list of (polyline, 'solid'|'dashed', n_dash_marks, source_class)."""
    buckets = defaultdict(list)
    for d in DR:
        k = class_key(d)
        for nm, (col, ty, _, _) in CLASSES.items():
            if k == (col, ty): buckets[nm].append(d)

    # Build every class's paths FIRST: a dashed run found in an "_existing" stroke
    # bucket is emitted under a DIFFERENT class (DASH_CLASS), so nothing can be
    # emitted until all buckets have been walked.
    PATHS = defaultdict(list)
    dashinfo = {"hairline_stroke_runs": {}, "filled_polygon_marks": {}}
    for nm, (col, ty, legend, commodity) in CLASSES.items():
        dds = buckets.get(nm, [])
        if ty == "s":
            marks, solid = split_dash_marks(dds)
            if marks:
                runs, dropped = stitch_dashes(marks)
                tgt = DASH_CLASS.get(nm, nm)
                dashinfo["hairline_stroke_runs"][nm] = {
                    "dash_marks": len(marks), "stitched_runs": len(runs),
                    "marks_dropped_unstitched": dropped, "emitted_as": tgt}
                for pl, k in runs:
                    PATHS[tgt].append((pl, "dashed", k, nm))
            for pl in chain_strokes(solid):
                PATHS[nm].append((pl, "solid", None, nm))
        else:
            runs = chain_dashes(dds)
            for pl in runs:
                PATHS[nm].append((pl, "dashed", None, nm))
            if dds:
                inset = sum(1 for d in dds if flatten(d["items"]) and not in_map(*np.array(
                    [q for poly in flatten(d["items"]) for q in poly]).mean(0)))
                dashinfo["filled_polygon_marks"][nm] = {
                    "marks": len(dds), "marks_in_inset": inset, "chained_runs": len(runs)}
    return PATHS, buckets, dashinfo

def main():
    page, DR = load_drawings()
    PATHS, buckets, dashinfo = build_paths(DR)
    inv, P, acc = fit_projection()
    labels = harvest_labels(page)
    LT = cKDTree(np.array([l["xy"] for l in labels])) if labels else None

    feats, skipped, seq = [], {}, 0
    for nm, (col, ty, legend, commodity) in CLASSES.items():
        dds = buckets.get(nm, [])
        paths = PATHS.get(nm, [])
        if not paths:
            inset = sum(1 for d in dds if not in_map(*np.array(
                [p for poly in flatten(d["items"]) for p in poly]).mean(0)))
            skipped[nm] = {"legend": legend, "marks_total": len(dds), "marks_in_inset": inset,
                           "reason": ("all marks fall in the Hyderabad-Badin / Karachi insets, "
                                      "which are at a different scale and are not georeferenced"
                                      if inset == len(dds) and dds else
                                      "too few / too scattered to chain into a route without "
                                      "fabricating geometry")}
            continue
        status = STATUS["uc" if nm.endswith("_uc") else nm.rsplit("_", 1)[-1]]
        for pl, drawn, nmarks, src in paths:
            a = np.array(pl); lo, la = inv(a[:, 0], a[:, 1])
            coords = [[round(float(x), 6), round(float(y), 6)] for x, y in zip(lo, la)]
            seq += 1
            props = {"shape_id": f"PPIS-{seq:04d}", "country": "Pakistan",
                     "feature_class": nm, "map_legend": legend, "commodity": commodity,
                     "status": status, "geodesic_km": round(geodesic_km(coords), 3),
                     "drawn_as": drawn}
            if nmarks: props["dash_marks_stitched"] = nmarks
            if LT is not None:
                dist, idx = LT.query(a.mean(0))
                if dist <= 6.0:
                    L = labels[int(idx)]
                    props.update({"nearest_text": L["text"], "label_gap_pt": round(float(dist), 2),
                                  "label_diameter_in": L["dia_in"][0] if L["dia_in"] else None,
                                  "label_length_km": L["len_km"][0] if L["len_km"] else None})
            props["description"] = (f"{legend} | {props.get('nearest_text','no nearby map label')}"
                                    + (f" | label gap {props['label_gap_pt']} pt" if "label_gap_pt" in props else "")
                                    + " | labels are label-proximity artifacts, unverified"
                                    + (f" | one dashed run stitched from {nmarks} hairline marks; "
                                       f"class read off the legend (same colour as {src}, dashed = PLANNED) "
                                       f"and not off line weight" if src != nm else ""))
            feats.append({"type": "Feature", "properties": props,
                          "geometry": {"type": "LineString", "coordinates": coords}})

    fc = {"type": "FeatureCollection",
          "ppis_extraction": {
              "source_pdf": PDF.name, "page": PAGE + 1,
              "map_title": "Energy Infrastructure Map - 2025",
              "publisher": "Directorate General of Petroleum Concessions / "
                           "Pakistan Petroleum Information Service (PPIS) / LMK Resources",
              "origin_url": "https://ppisonline.com/Brochure/Investment%20Brochure%202025.pdf",
              "method": "vector-geometry extraction (PyMuPDF get_drawings) + LCC georeference",
              "projection": {"family": "lambert_conformal_conic",
                             "apex_x_pt": round(float(P[0]), 3), "apex_y_pt": round(float(P[1]), 2),
                             "n": round(float(P[2]), 6), "lon0_deg": round(float(P[3]), 4),
                             "F": round(float(P[4]), 2)},
              "georeference_accuracy_km": {k: round(v, 3) if isinstance(v, float) else v
                                           for k, v in acc.items()},
              "classes_not_extracted": skipped,
              "dashed_lines": dashinfo,
              "map_annotations_harvested": len(labels)},
          "features": feats}
    (HERE / "data").mkdir(exist_ok=True)
    (HERE / "data" / "ppis-pipelines.geojson").write_text(json.dumps(fc))
    (HERE / "extraction" / "map_annotations.json").write_text(json.dumps(labels, indent=1))

    print(f"georeference: {acc['n_gcp']} GCPs  mean {acc['mean_km']:.2f} km  "
          f"median {acc['median_km']:.2f} km  max {acc['max_km']:.2f} km")
    print(f"{'feature_class':30s}{'paths':>6s}{'km':>10s}{'longest':>9s}{'labelled':>9s}")
    for nm in CLASSES:
        F = [f for f in feats if f["properties"]["feature_class"] == nm]
        if not F:
            print(f"{nm:30s}{'--':>6s}   NOT EXTRACTED: {skipped[nm]['reason'][:44]}"); continue
        L = [f["properties"]["geodesic_km"] for f in F]
        nl = sum(1 for f in F if "nearest_text" in f["properties"])
        print(f"{nm:30s}{len(F):6d}{sum(L):10.1f}{max(L):9.1f}{nl:9d}")
    print(f"\ntotal {len(feats)} features, "
          f"{sum(f['properties']['geodesic_km'] for f in feats):.0f} km -> data/ppis-pipelines.geojson")

if __name__ == "__main__":
    main()
