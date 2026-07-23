#!/usr/bin/env python3
"""Assemble one candidate route from a chosen source-ladder method (workflow §8, step 2).

One invocation = one ProjectID via one method. Normalizes the input geometry to a
routes-repo-valid `candidate_routes/<PID>.geojson`, runs the validation gate, frames
it as a replacement when GEM already has a route, and upserts both a rich
candidates.json record and a `__ROUTE__`/`ROUTE_CANDIDATE` staged record (which a §6
handoff carries automatically). Never writes the sheet or the routes repo.

Methods (→ suggested RouteAccuracy):
  sidecar    --ref-id gulfpub:gas:409   GulfPub geometry sidecar from a recon run   → high
  gis        --geom layer.geojson [--feature-index N | --where-prop K=V]   ArcGIS    → high
  osm        --geom osm.geojson         OSM (ODbL provenance carried through)        → high
  traced     --geom georef_out.geojson  georef.py digitization output                → medium
  endpoints  --start lon,lat --end lon,lat   great-circle between SOURCED endpoints   → low

No coordinate is ever fabricated: sidecar/gis/osm/traced coords come from a vector
source or a fitted georeference; endpoints coords must be independently sourced
(pass --start-ref/--end-ref, or they carry over from a prior staged suggestion).

Usage examples:
  python scripts/build_route_candidate.py --pid P7597 --commodity gas \\
      --staging batches/staging/route-creation-gas-egypt/ --method sidecar --ref-id gulfpub:gas:409
  python scripts/build_route_candidate.py --pid P0436 --commodity gas --staging <dir> \\
      --method endpoints --start 33.7984,31.1313 --end 34.8967,29.4917 \\
      --start-ref https://... --end-ref https://... --replace --densify-km 20
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paths  # noqa: E402
from adapter_base import geodesic_km, geom_endpoints  # noqa: E402
from route_compare import (load_gem_route, merge_geoms, geometry_signals,  # noqa: E402
                           _featurecollection_to_geom)
import validate_route_candidate as gate  # noqa: E402

METHOD_ACCURACY = {
    "sidecar": "high", "gis": "high", "osm": "high",
    "traced": "medium", "endpoints": "low",
}
METHOD_LABEL = {  # candidates.json / staged record method tag
    "sidecar": "gulfpub_sidecar", "gis": "arcgis", "osm": "osm",
    "traced": "digitized", "endpoints": "endpoints_greatcircle",
}


def _utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --------------------------------------------------------------------------- #
# geometry normalization
# --------------------------------------------------------------------------- #
def _strip_z(coords):
    if not coords:
        return coords
    if isinstance(coords[0], (int, float)):
        return [round(coords[0], 6), round(coords[1], 6)]
    return [_strip_z(c) for c in coords]


def _lines_from(geom: dict) -> list:
    t, c = geom.get("type"), geom.get("coordinates") or []
    if t == "LineString":
        return [c] if c else []
    if t == "MultiLineString":
        return [p for p in c if p]
    return []


def _normalize_geom(geom: dict | None) -> dict | None:
    """(Multi)LineString only, Z stripped, 6 dp, connected parts linemerged."""
    if not geom:
        return None
    merged = merge_geoms([geom])  # collapse to one Multi/LineString
    if merged is None:
        return None
    try:
        from shapely.geometry import shape, mapping, MultiLineString, LineString
        from shapely.ops import linemerge
        parts = _lines_from(merged)
        geoms = [LineString(p) for p in parts if len(p) >= 2]
        if not geoms:
            return None
        stitched = linemerge(MultiLineString(geoms)) if len(geoms) > 1 else geoms[0]
        merged = mapping(stitched)
    except Exception:  # noqa: BLE001 — shapely optional; fall back to raw merge
        pass
    merged["coordinates"] = _strip_z(merged["coordinates"])
    return merged


def _select_features(fc_or_geom: dict, feature_index: list[int],
                     where_prop: str | None) -> dict | None:
    """Pull a geometry out of a fetched layer: by --feature-index, by --where-prop
    KEY=VAL, or (default) merge every line feature."""
    feats = fc_or_geom.get("features")
    if feats is None:  # already a bare geometry
        return fc_or_geom
    chosen = []
    if feature_index:
        chosen = [feats[i] for i in feature_index if 0 <= i < len(feats)]
    elif where_prop and "=" in where_prop:
        k, v = where_prop.split("=", 1)
        chosen = [f for f in feats
                  if str((f.get("properties") or {}).get(k.strip(), "")).strip() == v.strip()]
    else:
        chosen = feats
    geoms = [f.get("geometry") for f in chosen if f.get("geometry")]
    return merge_geoms(geoms) if geoms else None


def _greatcircle(start: tuple, end: tuple, densify_km: float) -> dict:
    from pyproj import Geod
    g = Geod(ellps="WGS84")
    total = g.inv(start[0], start[1], end[0], end[1])[2] / 1000.0
    n = max(1, int(total // densify_km))
    pts = g.npts(start[0], start[1], end[0], end[1], n)
    coords = [[round(start[0], 6), round(start[1], 6)]]
    coords += [[round(lon, 6), round(lat, 6)] for lon, lat in pts]
    coords += [[round(end[0], 6), round(end[1], 6)]]
    return {"type": "LineString", "coordinates": coords}


def _load_geojson_arg(path: str) -> dict:
    return json.loads(Path(path).read_text())


def _osm_provenance(fc: dict) -> dict | None:
    """If a fetched layer is OSM, pull its ODbL provenance to carry into the candidate."""
    for f in fc.get("features", []) or []:
        p = f.get("properties") or {}
        if p.get("source") == "OSM":
            return {"osm_ids": p.get("osm_ids", []),
                    "attribution": p.get("attribution", "© OpenStreetMap contributors")}
    return None


def _sidecar_geom(ref_id: str) -> tuple[dict | None, dict]:
    """Find geometry for a gulfpub ref_id across recon-run sidecars. -> (geom, source)."""
    recon = paths.repo_root() / "batches" / "staging" / "recon"
    for run in sorted(recon.glob("*")):
        sc = run / "geometry_sidecar.json"
        if not sc.exists():
            continue
        try:
            data = json.loads(sc.read_text())
        except Exception:  # noqa: BLE001
            continue
        if ref_id in data:
            src_url = ""
            md = run / "match_diff.json"
            if md.exists():
                try:
                    diff = json.loads(md.read_text())
                    for ov in diff.get("overlaps", []) or []:
                        if ov.get("ref", {}).get("ref_id") == ref_id:
                            src_url = ov["ref"].get("source_url", "")
                            break
                except Exception:  # noqa: BLE001
                    pass
            return data[ref_id], {"name": "GulfPub PE World Map", "ref_id": ref_id,
                                  "recon_dir": run.name, "url": src_url,
                                  "license": "GulfPub (tier-2 scraped route DB)"}
    return None, {}


# --------------------------------------------------------------------------- #
# endpoint snapping
# --------------------------------------------------------------------------- #
def _snap(geom: dict, snap_start, snap_end, max_km: float) -> tuple[dict, list[str]]:
    """Move the nearest end vertex onto a snap target if within max_km; else refuse
    (never yank an endpoint across a big gap — that would fabricate geometry)."""
    from pyproj import Geod
    g = Geod(ellps="WGS84")
    notes = []
    parts = _lines_from(geom)
    if not parts:
        return geom, notes

    def dist(a, b):
        return g.inv(a[0], a[1], b[0], b[1])[2] / 1000.0

    for target, which in ((snap_start, "start"), (snap_end, "end")):
        if not target:
            continue
        first, last = parts[0][0], parts[-1][-1]
        d_first, d_last = dist(first, target), dist(last, target)
        d = min(d_first, d_last)
        if d > max_km:
            notes.append(f"snap-{which} refused: nearest end {d:.1f} km > {max_km} km")
            continue
        t = [round(target[0], 6), round(target[1], 6)]
        if d_first <= d_last:
            parts[0][0] = t
        else:
            parts[-1][-1] = t
        notes.append(f"snapped {which} endpoint ({d:.2f} km)")
    geom = ({"type": "LineString", "coordinates": parts[0]} if len(parts) == 1
            else {"type": "MultiLineString", "coordinates": parts})
    return geom, notes


def _parse_lonlat(s: str | None):
    if not s:
        return None
    lon, lat = (float(x) for x in s.split(","))
    return (lon, lat)


# --------------------------------------------------------------------------- #
# store upsert
# --------------------------------------------------------------------------- #
def _upsert(path: Path, key: str, record: dict, list_key: str, meta: dict):
    data = {"meta": meta, list_key: []}
    if path.exists():
        try:
            data = json.loads(path.read_text())
        except Exception:  # noqa: BLE001
            pass
    data.setdefault("meta", meta)
    data["meta"].update(meta)
    recs = data.setdefault(list_key, [])
    recs[:] = [r for r in recs if r.get("project_id") != key] + [record]
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False))


def _route_record(pid: str, commodity: str, method: str, geom: dict, gj_name: str,
                  source: dict, georef: dict | None, replacement: bool,
                  sig: dict, qc: dict, endpoints: dict, notes: str,
                  start_ref: str, end_ref: str, wl: dict | None,
                  packet: str = "") -> dict:
    refs = [r for r in (start_ref, end_ref) if r]
    wl = wl or {}
    rows = wl.get("sheet_rows") or []
    length_km = round(geodesic_km(geom), 1) if geom else None
    sheet_km = wl.get("sheet_length_km")
    return {
        "project_id": pid,
        "sheet_row": ", ".join(str(x) for x in rows),
        "pipeline_name": wl.get("pipeline_name", ""),
        "segment_name": "; ".join(wl.get("segment_names") or []),
        "ref_col": "__ROUTE__", "class_in": "ROUTE", "class_out": "ROUTE_CANDIDATE",
        "value_cols": [], "primary_value_col": None, "values": {}, "primary_value": "",
        "current_ref": "",
        # route-candidate specifics
        "method": METHOD_LABEL[method], "geometry_file": gj_name,
        "source": source, "georef": georef, "replacement": replacement,
        "geometry_signals": sig, "qc_passed": qc["passed"], "packet": packet,
        "length_km": length_km, "sheet_length_km": sheet_km,
        "length_ratio": round(length_km / sheet_km, 3) if (length_km and sheet_km) else None,
        "current_route_accuracy": wl.get("current_route_accuracy", ""),
        "suggested_route_accuracy": METHOD_ACCURACY[method],
        "start_name": endpoints.get("start", {}).get("name", ""),
        "start_lon": endpoints.get("start", {}).get("lon"),
        "start_lat": endpoints.get("start", {}).get("lat"),
        "end_name": endpoints.get("end", {}).get("name", ""),
        "end_lon": endpoints.get("end", {}).get("lon"),
        "end_lat": endpoints.get("end", {}).get("lat"),
        # common core
        "proposed_refs": refs, "verifications": [], "tier": "", "independent": False,
        "source_language": "en", "researcher_notes": notes,
    }


def _rmse_threshold_km(sheet_km: float | None) -> float:
    """SOP registration threshold: rmse <= max(5 km, 2% of pipeline length)."""
    return max(5.0, 0.02 * sheet_km) if sheet_km else 5.0


def _emit_packet(staging: Path, pid: str, *, georef: dict | None, sheet_km: float | None,
                 threshold_km: float, endpoints: dict, refs: list[str], map_ref: str,
                 gcps_path: str, geometry_file: str) -> Path:
    """Stage a digitization packet under packets/<PID>/ so a human can finish the
    registration in QGIS. Committed with the batch (audit trail + handoff input)."""
    pdir = staging / "packets" / pid
    pdir.mkdir(parents=True, exist_ok=True)
    rmse = (georef or {}).get("rmse_km")
    # copy the gcps.json if a local file was given
    gcps_note = "not provided"
    if gcps_path and Path(gcps_path).exists():
        (pdir / "gcps.json").write_text(Path(gcps_path).read_text())
        gcps_note = "gcps.json (copied here)"
    # a local map file gets copied; a URL is recorded as a pointer (never re-fetched here)
    map_note = "not provided"
    if map_ref:
        mp = Path(map_ref)
        if mp.exists() and mp.is_file():
            (pdir / ("map" + mp.suffix)).write_bytes(mp.read_bytes())
            map_note = f"map{mp.suffix} (copied here)"
        else:
            (pdir / "map_source.txt").write_text(map_ref + "\n")
            map_note = "map_source.txt (URL — verify with url_verifier before use)"
    (pdir / "georef_report.json").write_text(
        json.dumps({"georef": georef, "sheet_km": sheet_km,
                    "threshold_km": round(threshold_km, 2), "endpoints": endpoints,
                    "refs": refs, "partial_geometry_file": geometry_file}, indent=1))
    readme = (pdir / "README.md")
    readme.write_text(
        f"# Digitization packet — {pid}\n\n"
        f"Automatic georeferencing did **not** register below the SOP threshold "
        f"(`rmse <= max(5 km, 2% of length)` = **{threshold_km:.1f} km**; measured RMSE "
        f"**{rmse} km**). Partial geometry was still written to "
        f"`{geometry_file}` (`georef.pass=false`); finish the trace by hand in QGIS.\n\n"
        f"## Contents\n"
        f"- `README.md` — this file\n"
        f"- `georef_report.json` — RMSE, per-GCP residuals, endpoints, verified refs\n"
        f"- map: {map_note}\n"
        f"- GCPs: {gcps_note}\n\n"
        f"## QGIS next steps\n"
        f"1. Load the map (Georeferencer), place the GCPs from `gcps.json` (each lon/lat is "
        f"independently geocoded — never read a coordinate off the map).\n"
        f"2. Add/adjust GCPs until residuals drop below {threshold_km:.1f} km; re-run "
        f"`scripts/georef.py --gcps gcps.json --trace trace.json`.\n"
        f"3. When it passes, re-run `build_route_candidate.py --method traced --geom <out>` "
        f"to regenerate the candidate + gate.\n\n"
        f"No coordinate is ever fabricated (standing rule 2); the finished route is a human "
        f"branch+PR against `GOIT-GGIT-pipeline-routes`, never an auto-edit.\n")
    return pdir


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pid", required=True)
    ap.add_argument("--commodity", default="gas", choices=["gas", "oil", "ngl"])
    ap.add_argument("--staging", required=True)
    ap.add_argument("--method", required=True, choices=list(METHOD_ACCURACY))
    # method inputs
    ap.add_argument("--ref-id", help="(sidecar) gulfpub:<cmdty>:<oid>")
    ap.add_argument("--geom", help="(gis/osm/traced) input geojson layer/file")
    ap.add_argument("--feature-index", type=int, action="append", default=[])
    ap.add_argument("--where-prop", help='(gis) select features where PROP=VALUE')
    ap.add_argument("--start", help="(endpoints) lon,lat")
    ap.add_argument("--end", help="(endpoints) lon,lat")
    ap.add_argument("--start-name", default="")
    ap.add_argument("--end-name", default="")
    ap.add_argument("--start-ref", default="", help="independent source URL for the start point")
    ap.add_argument("--end-ref", default="")
    ap.add_argument("--densify-km", type=float, default=25.0)
    # snapping
    ap.add_argument("--snap-start", help="lon,lat snap target for the start endpoint")
    ap.add_argument("--snap-end", help="lon,lat snap target for the end endpoint")
    ap.add_argument("--snap-max-km", type=float, default=10.0)
    # framing / provenance
    ap.add_argument("--replace", action="store_true", help="frame as a route replacement")
    ap.add_argument("--source-url", default="")
    ap.add_argument("--source-name", default="")
    ap.add_argument("--notes", default="")
    ap.add_argument("--map", default="", help="(traced) source-map URL or local path — copied "
                    "into the digitization packet when registration fails")
    ap.add_argument("--gcps", default="", help="(traced) gcps.json used — copied into the packet")
    args = ap.parse_args()

    staging = Path(args.staging)
    (staging / "candidate_routes").mkdir(parents=True, exist_ok=True)
    notes_bits = [args.notes] if args.notes else []
    source: dict = {"name": args.source_name, "url": args.source_url,
                    "license": "", "odbl": False, "fetched_utc": _utc()}
    georef = None
    endpoints = {"start": {}, "end": {}}

    # ---- acquire geometry by method ------------------------------------- #
    if args.method == "sidecar":
        if not args.ref_id:
            raise SystemExit("--method sidecar needs --ref-id")
        geom, src = _sidecar_geom(args.ref_id)
        if geom is None:
            raise SystemExit(f"ref_id {args.ref_id} not found in any recon sidecar")
        source.update(src)

    elif args.method in ("gis", "osm", "traced"):
        if not args.geom:
            raise SystemExit(f"--method {args.method} needs --geom")
        fc = _load_geojson_arg(args.geom)
        geom = _select_features(fc, args.feature_index, args.where_prop)
        if geom is None:
            raise SystemExit("no geometry selected (check --feature-index/--where-prop)")
        if args.method == "osm":
            prov = _osm_provenance(fc)
            source.update({"name": "OSM", "license": "ODbL", "odbl": True,
                           "attribution": (prov or {}).get("attribution",
                                                           "© OpenStreetMap contributors"),
                           "osm_ids": (prov or {}).get("osm_ids", [])})
            notes_bits.append("OSM/ODbL geometry — licensing acceptability is Baird's review call.")
        if args.method == "traced":
            gr = (fc.get("features", [{}])[0].get("properties") or {}).get("georef")
            georef = gr
            if gr and not gr.get("pass", True):
                notes_bits.append(f"georef RMSE {gr.get('rmse_km')} km did NOT pass — see packet.")

    elif args.method == "endpoints":
        s, e = _parse_lonlat(args.start), _parse_lonlat(args.end)
        if not s or not e:
            raise SystemExit("--method endpoints needs --start and --end (lon,lat)")
        geom = _greatcircle(s, e, args.densify_km)
        endpoints = {"start": {"name": args.start_name, "lon": s[0], "lat": s[1]},
                     "end": {"name": args.end_name, "lon": e[0], "lat": e[1]}}
        if not (args.start_ref and args.end_ref):
            notes_bits.append("endpoints-only line: confirm both endpoint sources before applying.")

    geom = _normalize_geom(geom)
    if geom is None:
        raise SystemExit("geometry empty after normalization")

    # ---- optional snap --------------------------------------------------- #
    snap_s, snap_e = _parse_lonlat(args.snap_start), _parse_lonlat(args.snap_end)
    if snap_s or snap_e:
        geom, snap_notes = _snap(geom, snap_s, snap_e, args.snap_max_km)
        notes_bits += snap_notes

    if args.method != "endpoints":
        ep = geom_endpoints(geom)
        endpoints = {"start": {"name": args.start_name, "lon": ep[0][0] if ep[0] else None,
                               "lat": ep[0][1] if ep[0] else None},
                     "end": {"name": args.end_name, "lon": ep[1][0] if ep[1] else None,
                             "lat": ep[1][1] if ep[1] else None}}

    # ---- write geojson --------------------------------------------------- #
    props = {"ProjectID": args.pid}
    if args.method == "osm":
        props.update({"source": "OSM", "license": "ODbL",
                      "attribution": source.get("attribution"),
                      "osm_ids": source.get("osm_ids", [])})
    fc_out = {"type": "FeatureCollection",
              "features": [{"type": "Feature", "properties": props, "geometry": geom}]}
    gj_path = staging / "candidate_routes" / f"{args.pid}.geojson"
    gj_path.write_text(json.dumps(fc_out, indent=1))

    # ---- replacement framing + geometry signals ------------------------- #
    existing = load_gem_route(args.pid, args.commodity)
    replacement = bool(existing is not None and args.replace)
    sig = geometry_signals(geom, existing) if existing is not None else {}
    if existing is not None and not args.replace:
        notes_bits.append("GEM already has a route — re-run with --replace to frame as "
                          "a replacement candidate (never auto-replaced).")

    # ---- validation gate ------------------------------------------------- #
    from route_integrity import load_boundaries, BOUNDARIES
    boundaries = load_boundaries() if BOUNDARIES.exists() else None
    wl = _load_worklist_unit(staging, args.pid)
    qc = gate.validate_candidate(
        gj_path, project_id=args.pid, commodity=args.commodity,
        sheet_km=(wl or {}).get("sheet_length_km"),
        allowed_countries=set((wl or {}).get("countries") or [])
        | {endpoints["start"].get("country", ""), endpoints["end"].get("country", "")},
        method=METHOD_LABEL[args.method], replacement=replacement, boundaries=boundaries)

    length_km = round(geodesic_km(geom), 1)
    sheet_km = (wl or {}).get("sheet_length_km")

    # ---- digitization packet (traced rung, registration failed) --------- #
    # SOP threshold is authoritative (georef's own --max-rmse-km may differ): emit a
    # packet when the RMSE exceeds max(5 km, 2% of length) or georef flagged pass=false.
    packet_rel = ""
    if args.method == "traced" and georef:
        threshold_km = _rmse_threshold_km(sheet_km)
        rmse = georef.get("rmse_km")
        packet_needed = (georef.get("pass") is False) or (rmse is not None and rmse > threshold_km)
        if packet_needed:
            pdir = _emit_packet(
                staging, args.pid, georef=georef, sheet_km=sheet_km,
                threshold_km=threshold_km, endpoints=endpoints,
                refs=[r for r in (args.start_ref, args.end_ref) if r],
                map_ref=args.map, gcps_path=args.gcps,
                geometry_file=f"candidate_routes/{args.pid}.geojson")
            packet_rel = f"packets/{args.pid}/"
            if f"georef RMSE {rmse} km did NOT pass" not in " ".join(notes_bits):
                notes_bits.append(f"georef RMSE {rmse} km > {threshold_km:.1f} km threshold "
                                  f"— digitization packet at {packet_rel}")

    # ---- candidates.json record ----------------------------------------- #
    cand = {
        "project_id": args.pid, "commodity": args.commodity,
        "sheet_rows": (wl or {}).get("sheet_rows", []),
        "pipeline_name": (wl or {}).get("pipeline_name", ""),
        "segment_names": (wl or {}).get("segment_names", []),
        "countries": (wl or {}).get("countries", []),
        "method": METHOD_LABEL[args.method], "geometry_file": f"candidate_routes/{args.pid}.geojson",
        "source": source, "georef": georef, "endpoints": endpoints,
        "length_km": length_km, "sheet_length_km": sheet_km,
        "length_ratio": round(length_km / sheet_km, 3) if sheet_km else None,
        "current_route_accuracy": (wl or {}).get("current_route_accuracy", ""),
        "suggested_route_accuracy": METHOD_ACCURACY[args.method],
        "replacement": replacement, "geometry_signals": sig, "qc": qc,
        "packet": packet_rel,
        "facility_anchors": (wl or {}).get("facility_anchors", []),
        "proposed_refs": [r for r in (args.start_ref, args.end_ref) if r],
        "verifications": [], "tier": "", "researcher_notes": " ".join(notes_bits),
    }
    scope_meta = {"mode": "route-creation", "commodity": args.commodity,
                  "scope": {"country": (wl or {}).get("_country", ""),
                            "commodity": args.commodity}}
    _upsert(staging / "candidates.json", args.pid, cand, "candidates", scope_meta)

    rec = _route_record(args.pid, args.commodity, args.method, geom, cand["geometry_file"],
                        source, georef, replacement, sig, qc, endpoints,
                        " ".join(notes_bits), args.start_ref, args.end_ref, wl, packet_rel)
    _upsert(staging / "staged_resolutions.json", args.pid, rec, "resolutions", scope_meta)

    flag = "PASS" if qc["passed"] else "FAIL"
    print(f"{args.pid} [{METHOD_LABEL[args.method]}] → {gj_path.name}: {length_km} km, "
          f"accuracy '{METHOD_ACCURACY[args.method]}', gate {flag}"
          + (f", replacement (iou={sig.get('iou')})" if replacement else ""))
    if packet_rel:
        print(f"  → digitization packet staged at {staging / packet_rel} "
              f"(registration above the RMSE threshold — finish in QGIS).", file=sys.stderr)
    if not qc["passed"]:
        print("  gate errors: " + "; ".join(qc["errors"]), file=sys.stderr)


def _load_worklist_unit(staging: Path, pid: str) -> dict | None:
    wl = staging / "worklist.json"
    if not wl.exists():
        return None
    try:
        data = json.loads(wl.read_text())
    except Exception:  # noqa: BLE001
        return None
    country = data.get("meta", {}).get("scope", {}).get("country", "")
    for u in data.get("units", []):
        if u.get("project_id") == pid:
            u = dict(u)
            u["_country"] = country
            return u
    return None


if __name__ == "__main__":
    main()
