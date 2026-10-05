#!/usr/bin/env python3
"""Pull the gas-pipeline layer out of Seala's public DataLens map.

Page:      https://seala.ru/lng/rossiyaeksport  ("Карта газовой отрасли")
Dashboard: https://datalens.yandex/0ouafys4kjyom  -> one widget, chart f39eeofbf6z21

The Squarespace page only iframes a public Yandex DataLens dashboard. DataLens serves it
through two anonymous JSON calls -- the same ones any browser makes to draw the map:
  POST /gateway/root/us/getPublicEntry {entryId}   -> dashboard definition (widget chartIds)
  POST /charts/api/run {id, params}                -> rendered layers, geometry included

Geometry gotchas (verified on all 185 features, 2026-09-17):
  * coordinates are Yandex order [lat, lon] -> swapped to GeoJSON [lon, lat]
  * each line arrives as a "Polygon" whose ring is the line traced out AND back:
    P0..Pm, Pm-1..P1 (always an even count, r[i] == r[n-i]). Keep r[:n//2+1];
    keeping the whole ring doubles every length.

RIGHTS / PROVENANCE -- read before using the output:
  * the owner has DataLens export switched off (DISABLED_EXPORT_CONNECTION,
    PROHIBITED_EXPORT_TENANT); redistribution rights are not established.
  * ~80% of this layer is GEM's own GGIT route geometry (vertex-identical), so it is
    circular for GEM purposes: never a [ref], never a corroborating source, never a route
    source for those rows. See README.md beside this script.
"""
import datetime
import json
import re
import sys
import urllib.request
from pathlib import Path

DASH = "0ouafys4kjyom"
BASE = "https://datalens.yandex"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
LABELS = {"Трубопровод": "name_raw", "Владелец": "owner_ru", "Статус трубопровода": "status_ru"}
STATUS = {"Действует": "operating", "Простаивает": "idle", "Строится": "construction"}
LINE_NO = re.compile(r"^(?:[IVX]{1,4}|\d{1,2}|CAC-\d)$")
CYRILLIC = re.compile(r"[А-Яа-яЁё]")


def post(path, body):
    req = urllib.request.Request(
        BASE + path, data=json.dumps(body).encode(), method="POST",
        headers={"User-Agent": UA, "Content-Type": "application/json", "Origin": BASE,
                 "Referer": f"{BASE}/{DASH}?_embedded=1"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def split_name(raw):
    """'<ru> — <English name | line number>'; a Cyrillic tail is part of the ru name."""
    head, sep, tail = raw.rpartition(" — ")
    tail = tail.strip()
    if not sep or CYRILLIC.search(tail):
        return raw.strip(), "", ""
    if LINE_NO.match(tail):
        return head.strip(), "", tail
    return head.strip(), tail, ""


def main(out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    dash = post("/gateway/root/us/getPublicEntry", {"entryId": DASH})
    chart_ids = [t["chartId"] for tab in dash["data"]["tabs"] for it in tab["items"]
                 if it.get("type") == "widget" for t in it["data"]["tabs"]]
    chart = post("/charts/api/run", {"id": chart_ids[0], "params": {},
                                     "workbookId": dash.get("workbookId")})
    (out_dir / "chart_run_raw.json").write_text(json.dumps(chart, ensure_ascii=False))

    layer = next(x for x in chart["data"] if "polygonmap" in x)
    feats = []
    for i, f in enumerate(layer["polygonmap"]["polygons"]["features"]):
        p = {"seala_idx": i}
        for item in (f.get("properties") or {}).get("data") or []:
            if not item:
                continue
            k, _, v = (item.get("text") or "").partition(": ")
            if k in LABELS:
                p[LABELS[k]] = v.strip()
        p["name_ru"], p["name_en"], p["line_number"] = split_name(p.get("name_raw", ""))
        p["status_en"] = STATUS.get(p.get("status_ru"), "")
        ring = f["geometry"]["coordinates"][0]
        n, m = len(ring), len(ring) // 2
        assert n % 2 == 0 and all(ring[j] == ring[n - j] for j in range(1, m)), \
            f"feature {i}: ring is not the expected out-and-back trace -- re-check the encoding"
        coords = [[lon, lat] for lat, lon in ring[: m + 1]]
        p["n_vertices"] = len(coords)
        feats.append({"type": "Feature", "properties": p,
                      "geometry": {"type": "LineString", "coordinates": coords}})

    fc = {"type": "FeatureCollection",
          "metadata": {
              "source_page": "https://seala.ru/lng/rossiyaeksport",
              "dashboard": f"{BASE}/{DASH}", "chart_id": chart.get("id"),
              "chart_rev": chart.get("revId"), "layer": layer["options"].get("layerTitle"),
              "retrieved_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
              "source_filter": "gas (PRODUCT_ID=8); start or end country = RU; "
                               "status in Действует/Простаивает/Строится",
              "crs": "EPSG:4326",
              "rights_note": "owner has DataLens export disabled; redistribution rights not "
                             "established; ~80% of geometry is GEM GGIT's own (circular)"},
          "features": feats}
    dest = out_dir / "seala_russia_gas_pipelines.geojson"
    dest.write_text(json.dumps(fc, ensure_ascii=False))
    print(f"{len(feats)} features -> {dest}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).parent)
