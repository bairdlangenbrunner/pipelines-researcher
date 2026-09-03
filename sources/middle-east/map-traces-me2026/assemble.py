#!/usr/bin/env python3
"""Assemble georeferenced pipeline routes + labels into GeoJSON.

Inputs (all produced upstream in this directory):
  pipelines_pagespace.json  - polylines in PDF page space
  labels.json               - decoded text lines in PDF page space
  fit_order2.npy            - page -> lon/lat quadratic transform

Outputs:
  middle_east_2026_pipelines.geojson
  middle_east_2026_labels.geojson
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
from pyproj import Geod

GEOD = Geod(ellps="WGS84")
COEF = np.load("georef/fit_order2.npy")

# Genealogy stamped on every emitted feature (repo convention: a produced route
# geojson must carry where it came from and how good the registration is).
GENEALOGY = {
    "source_map": "me2026",
    "source_file": "../energy-map-of-the-middle-east-2026-peregrine-bush.pdf",
    "source_page": 1,
    "source_title": "Energy Infrastructure Map of the Middle East, 2026 edition",
    "source_publisher": "Petroleum Economist / World Oil / Gulf Energy Information "
                        "/ Global Energy Infrastructure",
    "geometry_source": "stroke",
    "georef_order": 2,
    "georef_source": "map's own coastline vector registered to Natural Earth 10m "
                     "coastline+lakes by trimmed ICP",
    "georef_insample_rmse_km": 0.97,
    "georef_holdout_layer": "ne_10m_admin_0_countries vs the map's own border strokes",
    "georef_holdout_median_km": 1.45,
    "georef_holdout_rmse_km": 1.60,
    # measured in qc_vs_gem.py against GEM routes already at RouteAccuracy
    # high/very high, inside the sheet footprint -- how faithfully the pipe is
    # DRAWN, which the georef residual does not tell you. Commodity-specific,
    # so it is stamped per feature from DRAWN_OFFSET_MEDIAN_KM below; the
    # placeholder only fixes its position in the field order.
    "drawn_feature_offset_median_km": None,
    "accuracy_tier": "medium",
}
# Every emitted property must be a flat scalar: QGIS reads a nested object as a
# QVariantMap and the OGR GeoJSON writer then refuses to write the feature, so
# the layer cannot be re-exported after tracing a route off it.
DRAWN_OFFSET_MEDIAN_KM = {"gas": 3.06, "oil": 2.39}
STROKE_RGB = {"gas": "#d7191f", "oil": "#00922f"}
NAME_MAX_PT = 75.0      # max page-space distance for a name label -> route
NAME_NEAR_PT = 15.0     # a caption sitting on its line
NAME_MID_PT = 35.0      # offset caption, still unambiguous
DIAM_MAX_PT = 18.0      # diameter tags sit right on the line

DIAM_ONLY = re.compile(r"^\[([\d/]+)\]$")
DIAM_TRAIL = re.compile(r"\s*\[([\d/]+)\]\s*$")
DIAM_LEAD = re.compile(r"^\s*\[([\d/]+)\]\s*")

# The caption text often states its own commodity. That is a CROSS-CHECK on the
# stroke colour, never an override: where the two disagree the route keeps the
# colour's commodity and gets commodity_conflict=True for the researcher.
GAS_WORDS = re.compile(r"\b(gas|lng|ngl|igat|mgs)\b", re.I)
OIL_WORDS = re.compile(r"\b(oil|crude|petroline|products?|condensate)\b", re.I)


def name_hint(text):
    g, o = bool(GAS_WORDS.search(text)), bool(OIL_WORDS.search(text))
    return "gas" if g and not o else "oil" if o and not g else None

# Label classification by the font the publisher used for each category.
FONT_KIND = {
    "Gen_Arial_Bold": "pipeline_name",
    "Gen_Arial-Narrow_Bold": "pipeline_name",
    "Gen_District-Pro-Bold_": "field",
    "Gen_District-Pro-Demi_": "plant_or_refinery",
    "Gen_Arial": "place",
    "Gen_Calibri_Bold": "capital_city",
    "Gen_Calibri": "country",
    "Gen_Arial_Italic": "island_or_water",
    "Gen_Times-New-Roman_It": "sea_or_disclaimer",
    "Gen_Futura-PT-Cond-Bold": "project_annotation",
    "Gen_Futura-PT-Book": "legend_or_sources",
    "Gen_Futura-PT-Demi": "heading",
}
FURNITURE = {  # page furniture -> drop labels whose centre falls inside
    "legend": (40, 2055, 700, 2365), "sources": (50, 1690, 480, 1870),
    "disclaimer": (20, 1875, 700, 2050), "hormuz_inset": (2020, 1740, 2520, 2370),
    "producer_box": (1520, 2230, 2010, 2340), "title": (45, 20, 595, 225),
}


def to_lonlat(pts):
    p = np.asarray(pts, float)
    x, y = p[:, 0], p[:, 1]
    A = np.column_stack([np.ones_like(x), x, y, x * x, x * y, y * y])
    return np.column_stack([A @ COEF[0], A @ COEF[1]])


def in_furniture(cx, cy):
    return any(x0 <= cx <= x1 and y0 <= cy <= y1
               for x0, y0, x1, y1 in FURNITURE.values())


def seg_dist(px, py, pts):
    """Min distance from a point to a polyline, in page units."""
    a = pts[:-1]
    b = pts[1:]
    ab = b - a
    ap = np.array([px, py]) - a
    denom = (ab * ab).sum(1)
    t = np.where(denom > 0, (ap * ab).sum(1) / np.maximum(denom, 1e-12), 0.0)
    t = np.clip(t, 0, 1)
    proj = a + t[:, None] * ab
    d = np.hypot(proj[:, 0] - px, proj[:, 1] - py)
    return float(d.min())


def leader_anchor(bbox, leaders, pad=4.0):
    """If a leader rule touches this caption, return its far endpoint.

    The caption is then attached from where the leader POINTS, not from the
    text centroid -- the map routinely sets a caption on top of an unrelated
    line and relies on the leader to disambiguate.
    """
    x0, y0, x1, y1 = bbox
    best = None
    for lx0, ly0, lx1, ly1 in leaders:
        for (nx, ny), (fx, fy) in (((lx0, ly0), (lx1, ly1)),
                                   ((lx1, ly1), (lx0, ly0))):
            if not (x0 - pad <= nx <= x1 + pad and y0 - pad <= ny <= y1 + pad):
                continue
            if x0 - pad <= fx <= x1 + pad and y0 - pad <= fy <= y1 + pad:
                continue                     # wholly inside the caption box
            reach = ((fx - nx) ** 2 + (fy - ny) ** 2) ** 0.5
            if best is None or reach > best[0]:
                best = (reach, (fx, fy))
    return best[1] if best else None


def name_conf(dist_pt, ambiguous):
    """Deterministic label->route confidence from distance + corridor ambiguity.

    'ambiguous' means a route of the OTHER commodity is about as close, so the
    name may belong to the parallel line. Never resolved by reading the name --
    the stroke colour is the evidence, the name is not.
    """
    if ambiguous:
        return "low"
    if dist_pt <= NAME_NEAR_PT:
        return "high"
    return "medium" if dist_pt <= NAME_MID_PT else "low"


def merge_stacked(labels):
    """Join label lines stacked vertically into one caption (same font/size)."""
    out, used = [], [False] * len(labels)
    for i, a in enumerate(labels):
        if used[i]:
            continue
        group = [a]
        used[i] = True
        changed = True
        while changed:
            changed = False
            for j, b in enumerate(labels):
                if used[j] or b["font"] != a["font"] or abs(b["size"] - a["size"]) > 0.3:
                    continue
                for g in group:
                    # A line already ending in a diameter tag is a COMPLETE label.
                    # Parallel lines get stacked captions ("IGAT 3 [56]" over
                    # "IGAT 4 [56]"); merging those would invent a pipeline.
                    upper = g if g["bbox"][1] <= b["bbox"][1] else b
                    if DIAM_TRAIL.search(upper["text"].strip()):
                        continue
                    gx0, gy0, gx1, gy1 = g["bbox"]
                    bx0, by0, bx1, by1 = b["bbox"]
                    overlap = min(gx1, bx1) - max(gx0, bx0)
                    # signed vertical separation, order-agnostic; negative means
                    # the two line boxes overlap (identical rows go strongly
                    # negative and are rejected below)
                    gap = max(gy0, by0) - min(gy1, by1)
                    # Consecutive lines of one caption overlap by ~1.5 pt here
                    # (line boxes overlap, they do not gap), so allow a small
                    # negative gap.
                    if (overlap > 0.35 * min(gx1 - gx0, bx1 - bx0)
                            and -0.35 * a["size"] <= gap <= 0.6 * a["size"]):
                        group.append(b)
                        used[j] = True
                        changed = True
                        break
        group.sort(key=lambda s: s["bbox"][1])
        x0 = min(g["bbox"][0] for g in group)
        y0 = min(g["bbox"][1] for g in group)
        x1 = max(g["bbox"][2] for g in group)
        y1 = max(g["bbox"][3] for g in group)
        out.append({"text": " ".join(g["text"] for g in group),
                    "font": a["font"], "size": a["size"],
                    "bbox": [x0, y0, x1, y1],
                    "center": [(x0 + x1) / 2, (y0 + y1) / 2]})
    return out


def main():
    pipes = json.load(open("traces/pipelines_pagespace.json"))["features"]
    labels = [l for l in json.load(open("traces/labels.json"))
              if not in_furniture(*l["center"])]
    for l in labels:
        l["kind"] = FONT_KIND.get(l["font"], "other")

    names = merge_stacked([l for l in labels if l["kind"] == "pipeline_name"])
    diam_tags = [l for l in names if DIAM_ONLY.match(l["text"].strip())]
    name_tags = [l for l in names if not DIAM_ONLY.match(l["text"].strip())]

    arr = [np.asarray(p["points"], float) for p in pipes]

    # --- diameter tags: nearest route, tight radius
    for t in diam_tags:
        cx, cy = t["center"]
        ds = [seg_dist(cx, cy, a) for a in arr]
        k = int(np.argmin(ds))
        if ds[k] <= DIAM_MAX_PT:
            pipes[k].setdefault("_diam", []).append(
                (ds[k], DIAM_ONLY.match(t["text"].strip()).group(1)))

    # --- name tags: nearest route, looser radius; keep the distance for QC.
    # Gas and oil often share a corridor, so the nearest route can belong to the
    # other commodity. Never override the colour with the name -- record the
    # runner-up instead and flag the label as ambiguous for the researcher.
    leaders = json.load(open("traces/leaders.json"))
    unattached = []
    for t in name_tags:
        anchor = leader_anchor(t["bbox"], leaders)
        t["via_leader"] = anchor is not None
        cx, cy = anchor if anchor else t["center"]
        txt = t["text"].strip()
        d_in = DIAM_TRAIL.search(txt) or DIAM_LEAD.match(txt)
        clean = DIAM_LEAD.sub("", DIAM_TRAIL.sub("", txt)).strip()
        ds = np.array([seg_dist(cx, cy, a) for a in arr])
        k = int(ds.argmin())
        t["nearest_pt"] = round(float(ds[k]), 1)
        t["nearest_route"] = f"ME2026-{k:04d}"
        for cmdty in ("gas", "oil"):
            m = np.array([p["commodity"] == cmdty for p in pipes])
            t[f"nearest_{cmdty}_pt"] = (round(float(ds[m].min()), 1)
                                        if m.any() else None)
        rival = min((d for j, d in enumerate(ds)
                     if pipes[j]["commodity"] != pipes[k]["commodity"]),
                    default=float("inf"))
        t["ambiguous"] = bool(rival <= max(1.5 * ds[k], ds[k] + 3.0))
        if ds[k] <= NAME_MAX_PT:
            pipes[k].setdefault("_names", []).append(
                (float(ds[k]), clean, t["ambiguous"]))
            if d_in:
                pipes[k].setdefault("_diam", []).append((float(ds[k]), d_in.group(1)))
        else:
            unattached.append((round(float(ds[k]), 1), clean))

    feats = []
    for i, p in enumerate(pipes):
        ll = to_lonlat(p["points"])
        lon, lat = ll[:, 0], ll[:, 1]
        length_km = (GEOD.line_length(lon, lat) / 1000.0) if len(ll) > 1 else 0.0
        nm = sorted(p.get("_names", []))
        dm = sorted(p.get("_diam", []))
        props = {
            "id": f"ME2026-{i:04d}",
            "commodity": p["commodity"],
            "status_class": p["status"],
            "name": nm[0][1] if nm else None,
            "name_dist_pt": round(nm[0][0], 1) if nm else None,
            "name_ambiguous": nm[0][2] if nm else None,
            "name_confidence": name_conf(nm[0][0], nm[0][2]) if nm else None,
            "commodity_conflict": (nm and name_hint(nm[0][1]) is not None
                                   and name_hint(nm[0][1]) != p["commodity"]) or None,
            # ";"-joined, not a list: same reason as DRAWN_OFFSET_MEDIAN_KM,
            # and it matches the sheet's OtherEnglishNames delimiter
            "other_names": "; ".join(n for _, n, _ in nm[1:]) or None,
            "diameter_in": dm[0][1] if dm else None,
            "length_km": round(length_km, 2),
            "n_vertices": len(ll),
            "legend_class": f"{p['commodity']}_{p['status']}",
            "stroke_rgb": STROKE_RGB[p["commodity"]],
            "dashed": p["status"] != "in_service",
            **GENEALOGY,
            "drawn_feature_offset_median_km":
                DRAWN_OFFSET_MEDIAN_KM[p["commodity"]],
        }
        feats.append({"type": "Feature", "properties": props,
                      "geometry": {"type": "LineString",
                                   "coordinates": [[round(a, 6), round(b, 6)]
                                                   for a, b in ll]}})
    Path("me2026_pipelines.geojson").write_text(json.dumps(
        {"type": "FeatureCollection", "features": feats}, indent=1))
    # Per-commodity splits alongside the combined file: GOIT and GGIT are
    # separate trackers, so the usable unit downstream is one commodity at a
    # time. Same features, same properties -- a filter, not a second extraction.
    for cm in ("gas", "oil"):
        sub = [f for f in feats if f["properties"]["commodity"] == cm]
        Path(f"me2026_{cm}_pipelines.geojson").write_text(json.dumps(
            {"type": "FeatureCollection", "features": sub}, indent=1))
        print(f"  {cm}: {len(sub)} routes, "
              f"{sum(f['properties']['length_km'] for f in sub):,.0f} km "
              f"-> me2026_{cm}_pipelines.geojson")

    # Label layer: everything that is not a pipeline name as decoded, plus the
    # MERGED pipeline-name captions carrying their attachment diagnostics.
    lfeats = []
    for l in [x for x in labels if x["kind"] != "pipeline_name"] + name_tags:
        lon, lat = to_lonlat([l["center"]])[0]
        props = {"text": l["text"], "kind": l.get("kind", "pipeline_name"),
                 "font": l["font"], "size": l["size"]}
        for k in ("nearest_route", "nearest_pt", "nearest_gas_pt",
                  "nearest_oil_pt", "ambiguous", "via_leader"):
            if k in l:
                props[k] = l[k]
        lfeats.append({"type": "Feature", "properties": props,
                       "geometry": {"type": "Point",
                                    "coordinates": [round(lon, 6), round(lat, 6)]}})
    Path("me2026_labels.geojson").write_text(json.dumps(
        {"type": "FeatureCollection", "features": lfeats}, ensure_ascii=False, indent=1))

    named = [f for f in feats if f["properties"]["name"]]
    print(f"routes: {len(feats)}  named: {len(named)}  labels: {len(lfeats)}")
    print(f"total length: {sum(f['properties']['length_km'] for f in feats):,.0f} km")

    # ---- decisive check: known-commodity trunk lines must land on the colour
    # the legend assigns. Petroline/BTC/Tapline are crude; Dolphin/IGAT/TANAP gas.
    expect = {"East-West (Petroline)": "oil", "BTC Pipeline": "oil",
              "Trans-Arabian Pipeline (Tapline) mothballed": "oil",
              "Iraq-Turkey Pipeline (ITP)": "oil", "ADCOP": "oil",
              "Shaybah-Abqaiq": "oil", "Iraq-Saudi Arabia Oil Pipeline (IPSA) rehabilitated": "oil",
              "Dolphin": "gas", "TANAP": "gas", "Arab Gas Pipeline": "gas",
              "TAPI Pipeline": "gas", "Trans Caspian Gas Pipeline": "gas",
              "Master Gas System 2 (MGS 2)": "gas", "IGAT 4": "gas", "IGAT 9": "gas"}
    print("\ncommodity self-check (expected vs extracted colour class):")
    ok = bad = bad_conf = 0
    for f in feats:
        pr = f["properties"]
        n = pr["name"]
        if n in expect:
            got = pr["commodity"]
            good = got == expect[n]
            ok, bad = ok + good, bad + (not good)
            # A mismatch on a low-confidence (ambiguous-corridor) label is the
            # flag working, not a colour error. Only a HIGH/MEDIUM confidence
            # mismatch would indict the colour->commodity mapping.
            if not good and pr["name_confidence"] != "low":
                bad_conf += 1
            print(f"  {'OK ' if good else 'MISMATCH'} {n:44s} expect={expect[n]:3s} "
                  f"got={got:3s} conf={pr['name_confidence']}")
    print(f"  -> {ok} correct, {bad} mismatched "
          f"({bad_conf} of them at medium/high confidence)")

    amb = [f for f in named if f["properties"]["name_ambiguous"]]
    print(f"\nname labels: {len(name_tags)} captions, "
          f"{len(unattached)} beyond {NAME_MAX_PT:.0f} pt, "
          f"{len(amb)} attached but ambiguous (a route of the other commodity "
          f"is about as close)")
    for d, n in sorted(unattached, reverse=True)[:15]:
        print(f"    unattached {d:6.1f} pt  {n}")


if __name__ == "__main__":
    main()
