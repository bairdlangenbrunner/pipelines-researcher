#!/usr/bin/env python3
"""Reconcile a scraped reference dataset against GEM (the orchestrator).

    python scripts/reconcile.py --source gulfpub --country "Saudi Arabia" \
        --commodity both --staging batches/<scope>/staging/recon-<source>-<date>/

Reads canonical_records.json (+ geometry_sidecar.json) produced by ingest.py, matches
each reference record against GEM rows (segment + synthetic-network level) by name /
endpoints / diameter / length / route geometry, classifies the result, and writes:
  - match_diff.json     (overlaps / additions / gem_only / status_conflicts / ambiguous / routes)
  - route_metrics.json  (per-pair geometry signals)
Never edits the live Sheet or the routes repo.
"""
from __future__ import annotations

import argparse
import glob
import json
import sys
from collections import defaultdict
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))

import paths  # noqa: E402
import normalize as N  # noqa: E402
from ingest import load_manifest, _FAMILY  # noqa: E402
from match import load_gem_df, gem_rows_for_country, attribute_signals  # noqa: E402
from route_compare import load_gem_route, merge_geoms, geometry_signals, replacement_candidate  # noqa: E402

DEFAULTS = {
    "name_weight": 0.30, "endpoint_weight": 0.25, "diameter_weight": 0.15,
    "length_weight": 0.10, "geometry_weight": 0.20,
    "green_threshold": 0.75, "yellow_threshold": 0.45, "buffer_km_for_overlap": 2.0,
    # When the REFERENCE has geometry but a GEM candidate has no route, the geometry
    # test could not be run. Dropping g_score and renormalizing (the old behaviour)
    # scored that candidate as if it had PASSED — so a routeless GEM row outranked a
    # correctly-matched row whose real geometry scored anything less than perfect.
    # Rows with no route were structurally advantaged. This is the untested stand-in:
    # low, because the match is genuinely unverified, but not 0 — absence of geometry
    # is not evidence against. Only applied when the reference itself has geometry.
    "geometry_untested_score": 0.15,
}
_KEYMAP = {"s_name": "name_weight", "s_endpoints": "endpoint_weight",
           "s_diameter": "diameter_weight", "s_length": "length_weight", "g_score": "geometry_weight"}
TOPK_GEOMETRY = 5      # only the top-K attribute candidates per ref get a (costlier) geometry pass
AMBIGUOUS_DELTA = 0.10


def tracker_for(commodity: str) -> str:
    return "oil" if commodity in ("oil", "ngl") else "gas"


def route_commodity(tracker: str) -> str:
    return "oil" if tracker == "oil" else "gas"


def find_gem_csv(tracker: str, override: str | None) -> str | None:
    if override:
        return override
    pat = "GOIT_oil_ngl_snapshot_*.csv" if tracker == "oil" else "GGIT_gas_snapshot_*.csv"
    files = sorted(glob.glob(str(paths.repo_root() / "data" / pat)))
    return files[-1] if files else None


def composite(w: dict, sig: dict) -> float:
    num = den = 0.0
    for k, wk in _KEYMAP.items():
        v = sig.get(k)
        if v is not None:
            num += w[wk] * v
            den += w[wk]
    return round(num / den, 4) if den else 0.0


def _system_key(g) -> str:
    """Identity of the pipeline a GEM row belongs to — two segments of the same
    system are NOT an ambiguous match."""
    return N.normalize_name(g.network_grouping or g.pipeline_name)


# A physical signal — one that pins the pipe to the ground or the steel. Name and
# length do neither: names share boilerplate, and length is a bare ratio two
# unrelated lines match by coincidence. Composite renormalizes over PRESENT signals,
# so a ref with only those two can score 0.90 on the weakest evidence the engine has.
PHYSICAL_SIGNALS = ("s_endpoints", "s_diameter", "g_score")


def confidence(score: float, w: dict, sig: dict | None = None) -> str:
    if score >= w["green_threshold"]:
        # Green = "corroborated". Withhold it when no physical signal was available,
        # even at a high composite; the ref drops to yellow for human adjudication.
        # an untested g_score is a stand-in, not evidence — it must not satisfy the gate
        have = [k for k in PHYSICAL_SIGNALS if sig and sig.get(k) is not None
                and not (k == "g_score" and sig.get("g_untested"))]
        if sig is not None and not have:
            return "yellow"
        return "green"
    if score >= w["yellow_threshold"]:
        return "yellow"
    return "red"


def ref_view(r: dict) -> dict:
    return {
        "ref_id": r["ref_id"], "oid": r["ref_id"].split(":")[-1], "name": r["name"],
        "status": r["status"], "status_raw": r["status_raw"], "country": r["country_raw"],
        "start": r["start_loc"], "end": r["end_loc"], "diameter": r["diameter_raw"],
        "length_km": r["length_km"], "geodesic_km": r["geodesic_km"],
        "capacity": r["capacity"], "capacity_units": r["capacity_units"], "capacity_raw": r["capacity_raw"],
        "operator": r["operator"], "owners": r["owners"], "start_year": r["start_year"],
        "description": r["description"], "source_url": r["source_url"],
        "report_citation": r["report_citation"], "has_geometry": r["has_geometry"],
    }


def gem_view(g) -> dict:
    return {
        "kind": g.kind, "project_id": g.project_id, "project_ids": g.project_ids,
        "pipeline_name": g.pipeline_name, "segment_name": g.segment_name,
        "network_grouping": g.network_grouping, "status": g.status, "owner": g.owner,
        "diameter": g.diameter_raw, "length_km": g.length_km,
        "start": g.start_raw, "end": g.end_raw, "route_accuracy": g.route_accuracy, "wiki": g.wiki,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", required=True)
    ap.add_argument("--country", required=True)
    ap.add_argument("--commodity", default="both", choices=["oil", "ngl", "gas", "hydrogen", "both"])
    ap.add_argument("--staging", required=True, help="dir with canonical_records.json from ingest")
    ap.add_argument("--gem-oil", help="GOIT oil CSV (default: latest data/GOIT_oil_ngl_snapshot_*.csv)")
    ap.add_argument("--gem-gas", help="GGIT gas CSV (default: latest data/GGIT_gas_snapshot_*.csv)")
    args = ap.parse_args()

    manifest, _ = load_manifest(args.source)
    w = dict(DEFAULTS)
    w.update(manifest.get("matching", {}) or {})
    buffer_km = w["buffer_km_for_overlap"]

    staging = Path(args.staging)
    records = json.loads((staging / "canonical_records.json").read_text())
    sidecar = json.loads((staging / "geometry_sidecar.json").read_text())

    want_country = N.normalize_country(args.country)
    fam = None if args.commodity == "both" else _FAMILY.get(args.commodity, {args.commodity})
    ref = [r for r in records
           if r["country"] == want_country and (fam is None or r["commodity"] in fam)]
    if not ref:
        sys.exit(f"no reference records for country='{args.country}' commodity='{args.commodity}'")

    by_tracker: dict[str, list] = defaultdict(list)
    for r in ref:
        by_tracker[tracker_for(r["commodity"])].append(r)

    overlaps, additions, gem_only, status_conflicts, ambiguous, routes = [], [], [], [], [], []
    route_metrics: dict[str, dict] = {}
    meta_csv: dict[str, str] = {}

    for tracker, refs in by_tracker.items():
        csv = find_gem_csv(tracker, args.gem_oil if tracker == "oil" else args.gem_gas)
        if not csv:
            print(f"warn: no GEM {tracker} CSV found — skipping {len(refs)} {tracker} refs "
                  f"(run ./scripts/refresh_csvs.sh)", file=sys.stderr)
            continue
        meta_csv[tracker] = Path(csv).name
        df = load_gem_df(csv)
        segs, nets = gem_rows_for_country(df, args.country)
        pool = segs + nets
        pid2seg = {s.project_id: s for s in segs}
        rcom = route_commodity(tracker)
        route_cache: dict[str, dict | None] = {}

        def gem_geom(g):
            if g.kind == "segment":
                if g.project_id not in route_cache:
                    route_cache[g.project_id] = load_gem_route(g.project_id, rcom)
                return route_cache[g.project_id]
            parts = []
            for pid in g.project_ids:
                if pid not in route_cache:
                    route_cache[pid] = load_gem_route(pid, rcom)
                if route_cache[pid]:
                    parts.append(route_cache[pid])
            return merge_geoms(parts)

        for r in refs:
            ref_geom = sidecar.get(r["geometry_ref"]) if r.get("has_geometry") else None
            scored = []
            for g in pool:
                asig, reasons = attribute_signals(r, g)
                scored.append([composite(w, asig), asig, reasons, g])
            scored.sort(key=lambda x: x[0], reverse=True)

            cands = []
            for i, (acomp, asig, reasons, g) in enumerate(scored):
                sig = dict(asig)
                gsig = {}
                if ref_geom is not None:
                    if i < TOPK_GEOMETRY:
                        gsig = geometry_signals(ref_geom, gem_geom(g), buffer_km)
                    # untested, not passed (see geometry_untested_score). Applied to the
                    # whole pool, not just the top-K, or the untested tail would keep the
                    # free pass and could leapfrog a geometry-tested leader.
                    if gsig.get("g_score") is not None:
                        sig["g_score"] = gsig["g_score"]
                    else:
                        sig["g_score"] = w["geometry_untested_score"]
                        sig["g_untested"] = True
                cands.append({"comp": composite(w, sig), "sig": sig, "gsig": gsig,
                              "reasons": reasons, "gem": g})
            cands.sort(key=lambda c: c["comp"], reverse=True)
            best = cands[0]
            second = cands[1] if len(cands) > 1 else None
            reason_str = "; ".join(best["reasons"])
            if best["gsig"].get("iou") is not None:
                reason_str += f"; route IoU {best['gsig']['iou']}"

            if best["comp"] >= w["yellow_threshold"]:
                g = best["gem"]
                conf = confidence(best["comp"], w, best["sig"])
                if conf == "yellow" and best["comp"] >= w["green_threshold"]:
                    reason_str += "; capped at yellow — no physical signal"
                # mark matched
                if g.kind == "segment":
                    g.matched = True
                else:
                    for pid in g.project_ids:
                        if pid in pid2seg:
                            pid2seg[pid].matched = True
                iou = best["gsig"].get("iou")
                repl = replacement_candidate(g.route_accuracy, best["gsig"]) if g.kind == "segment" else False
                row = {"tracker": tracker, "confidence": conf, "composite": best["comp"],
                       "reason": reason_str, "signals": best["sig"],
                       "ref": ref_view(r), "gem": gem_view(g),
                       "gem_segments": g.project_ids, "route_iou": iou,
                       "route_replacement_candidate": repl}
                overlaps.append(row)
                if best["gsig"]:
                    route_metrics[r["ref_id"]] = {"gem": g.project_ids, "signals": best["gsig"]}
                if ref_geom is not None:
                    routes.append({"tracker": tracker, "ref_id": r["ref_id"], "oid": r["ref_id"].split(":")[-1],
                                   "name": r["name"], "status": r["status"], "diameter": r["diameter_raw"],
                                   "length_km": r["length_km"], "geodesic_km": r["geodesic_km"],
                                   "matched_project_ids": g.project_ids,
                                   "gem_route_accuracy": g.route_accuracy, "route_iou": iou,
                                   "replacement_candidate": repl, "wkt": _to_wkt(ref_geom)})
                if r["status"] and g.status and r["status"] != g.status:
                    status_conflicts.append({"tracker": tracker, "ref_id": r["ref_id"], "ref_name": r["name"],
                                             "ref_status": r["status"], "gem_project_ids": g.project_ids,
                                             "gem_name": g.pipeline_name, "gem_segment": g.segment_name,
                                             "gem_status": g.status,
                                             "recommendation": "verify true current status; do not auto-flip"})
                if (second and second["comp"] >= w["yellow_threshold"]
                        and best["comp"] - second["comp"] < AMBIGUOUS_DELTA
                        and _system_key(best["gem"]) != _system_key(second["gem"])):
                    ambiguous.append({"tracker": tracker, "ref_id": r["ref_id"], "ref_name": r["name"],
                                      "candidates": [{"project_ids": c["gem"].project_ids,
                                                      "name": c["gem"].pipeline_name, "composite": c["comp"]}
                                                     for c in cands[:2]]})
            else:
                additions.append({"tracker": tracker, "confidence": "red", "ref": ref_view(r),
                                  "best_guess": {"project_ids": best["gem"].project_ids,
                                                 "name": best["gem"].pipeline_name,
                                                 "composite": best["comp"]} if best["comp"] > 0 else None,
                                  "note": "[REVIEW] no confident GEM match — try matching to an existing "
                                          "pipeline under another name before treating as a discovery"})

        for s in segs:
            if not s.matched:
                gem_only.append({"tracker": tracker, **gem_view(s),
                                 "fuel": tracker, "note": "in GEM, no reference match"})

    diff = {
        "meta": {"source": args.source, "display_name": manifest.get("display_name"),
                 "source_tier": manifest.get("source_tier"), "country": args.country,
                 "commodity": args.commodity, "gem_csv": meta_csv,
                 "weights": w,
                 "counts": {"reference_records": len(ref), "overlaps": len(overlaps),
                            "additions": len(additions), "gem_only": len(gem_only),
                            "status_conflicts": len(status_conflicts), "ambiguous": len(ambiguous),
                            "routes": len(routes)}},
        "overlaps": overlaps, "additions": additions, "gem_only": gem_only,
        "status_conflicts": status_conflicts, "ambiguous": ambiguous, "routes": routes,
    }
    (staging / "match_diff.json").write_text(json.dumps(diff, indent=1, ensure_ascii=False))
    (staging / "route_metrics.json").write_text(json.dumps(route_metrics, indent=1, ensure_ascii=False))

    c = diff["meta"]["counts"]
    print(f"reconciled {args.source} vs GEM for {args.country} ({args.commodity})")
    print(f"  reference={c['reference_records']}  overlaps={c['overlaps']}  additions={c['additions']}  "
          f"gem_only={c['gem_only']}  status_conflicts={c['status_conflicts']}  ambiguous={c['ambiguous']}")
    by_conf = defaultdict(int)
    for o in overlaps:
        by_conf[o["confidence"]] += 1
    print(f"  overlap confidence: {dict(by_conf)}; route-replacement candidates: "
          f"{sum(1 for o in overlaps if o['route_replacement_candidate'])}")
    print(f"  -> {staging/'match_diff.json'}")


def _to_wkt(geom: dict) -> str:
    try:
        from shapely.geometry import shape
        return shape(geom).wkt
    except Exception:
        return ""


if __name__ == "__main__":
    main()
