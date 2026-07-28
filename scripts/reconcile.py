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
import geo_signals  # noqa: E402
from ingest import load_manifest, _FAMILY  # noqa: E402
from match import load_gem_df, gem_rows_for_country, attribute_signals  # noqa: E402
from route_compare import load_gem_route, merge_geoms, geometry_signals, replacement_candidate  # noqa: E402

DEFAULTS = {
    "name_weight": 0.30, "endpoint_weight": 0.25, "diameter_weight": 0.15,
    "length_weight": 0.10, "geometry_weight": 0.20,
    # Admin-area signal (geo_signals.py). DEFAULT 0.0 = OFF: switching it on changes
    # every composite for that dataset, so it is opt-in per source/dataset and no
    # already-committed run moves. See sources/osm/NOTES.md.
    "geoarea_weight": 0.0,
    "green_threshold": 0.75, "yellow_threshold": 0.45, "buffer_km_for_overlap": 2.0,
    # When the REFERENCE has geometry but a GEM candidate has no route, the geometry
    # test could not be run. Dropping g_score and renormalizing (the old behaviour)
    # scored that candidate as if it had PASSED — so a routeless GEM row outranked a
    # correctly-matched row whose real geometry scored anything less than perfect.
    # Rows with no route were structurally advantaged. This is the untested stand-in:
    # low, because the match is genuinely unverified, but not 0 — absence of geometry
    # is not evidence against. Only applied when the reference itself has geometry.
    "geometry_untested_score": 0.15,
    "near_miss_delta": 0.10,
    "route_containment_threshold": 0.60,
    "spatial_candidates": 8,
}
_KEYMAP = {"s_name": "name_weight", "s_endpoints": "endpoint_weight",
           "s_diameter": "diameter_weight", "s_length": "length_weight",
           "s_geoarea": "geoarea_weight", "g_score": "geometry_weight"}
TOPK_GEOMETRY = 5      # only the top-K attribute candidates per ref get a (costlier) geometry pass
AMBIGUOUS_DELTA = 0.10

# Admin-area score at/above which an unmatched trace is read as candidate geometry FOR a
# routeless GEM row rather than a discovery. Province-coarse, hence advisory-only: it
# routes the finding to a human, it never confirms a match (see PHYSICAL_SIGNALS).
GEOAREA_ROUTE_FLOOR = 0.5

# Dispositions for a reference record that did not clear the match threshold. The old
# code had one bucket ("Addition"), which is why 52 unmatched Iraq OSM traces could be
# written out as an undifferentiated pile and never triaged. A reference route is
# presumptively a REAL pipeline; the open question is only WHICH of these it is.
DISPOSITIONS = ("NEAR_MISS", "FRAGMENT_OF_EXISTING", "ROUTE_FOR_EXISTING", "DISCOVERY_CANDIDATE")


def resolve_weights(manifest: dict, dataset_name: str | None) -> dict:
    """Engine DEFAULTS <- source `matching` <- dataset `matching`.

    Per-dataset layering exists so one country's extract can be tuned without
    rewriting the source's other, already-committed runs — the framework gap the
    GulfPub-Iraq match-quality escalation identified and deferred.
    """
    w = dict(DEFAULTS)
    w.update(manifest.get("matching", {}) or {})
    if dataset_name:
        for d in manifest.get("datasets", []) or []:
            if d.get("name") == dataset_name:
                w.update(d.get("matching", {}) or {})
                break
    return w


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
# s_geoarea is deliberately EXCLUDED: it is physical but province-coarse, and a
# province-level hit alone must not unlock green for a Tier-2/3 source.
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


def _shape(geom):
    try:
        from shapely.geometry import shape
        return shape(geom)
    except Exception:
        return None


def spatial_rank(ref_geom: dict, gem_shapes: list, k: int) -> list:
    """The k GEM rows physically closest to the reference trace.

    WHY THIS EXISTS. The geometry pass is costly, so only a handful of candidates get
    one — and they used to be chosen by ATTRIBUTE rank. When the reference is unnamed
    and the GEM rows are routeless, the attribute ranking is noise, so the geometry
    test was being spent on essentially random rows and the true match never got
    tested. Iraq OSM 2026-07-28 returned 0 overlaps from 52 features that way.
    Proximity is the one ranking that stays meaningful when every text signal is dead.

    Distance is planar degrees — wrong as a distance, fine as an ORDERING at country
    scale, and it keeps this to a cheap pre-filter ahead of the real metric pass.
    """
    rs = _shape(ref_geom)
    if rs is None or rs.is_empty:
        return []
    out = []
    for key, gs in gem_shapes:
        if gs is None or gs.is_empty:
            continue
        try:
            out.append((gs.distance(rs), key))
        except Exception:
            continue
    out.sort(key=lambda t: t[0])
    return [key for _, key in out[:k]]


# Below this length ratio the reference covers only a sliver of the GEM row. OSM in
# particular is drawn in fragments: Iraq gas 2026-07-28 has 40 of 52 features under
# 0.5 km, several of them lying squarely on a 105 km GEM route.
PARTIAL_COVERAGE_RATIO = 0.25


def coverage(r: dict, g, gsig: dict) -> tuple:
    """How much of the GEM row this reference actually covers.

    A matched 0.1 km OSM stub is a TRUE match to the 105 km line it sits on — and
    reporting it as a bare "overlap" still misleads, because a reviewer reads that as
    "the reference corroborates this pipeline" when the reference has evidence for
    0.1% of it. Nothing here changes the match; it labels what the match is worth.
    """
    ref_km = r.get("geodesic_km") or r.get("length_km")
    ratio = gsig.get("length_ratio")
    if ratio is None and ref_km and g.length_km:
        ratio = round(min(ref_km, g.length_km) / max(ref_km, g.length_km), 3)
    if ratio is None:
        return "unknown", None, ""
    if ratio >= PARTIAL_COVERAGE_RATIO:
        return "comparable", ratio, ""
    return "partial", ratio, (
        f"PARTIAL: the reference trace is {ref_km or '?'} km against a GEM row of "
        f"{g.length_km or '?'} km (ratio {ratio}). It corroborates this row's LOCATION, "
        f"not its length, capacity or extent — do not read it as whole-line confirmation.")


def disposition(best: dict, w: dict, ref_has_geometry: bool) -> tuple:
    """Why this reference missed, and what a human should do with it.

    Ordered most-specific first. Every branch keeps the trace: none of these is
    "discard", because a route in a reference dataset is presumptively real pipe.
    """
    sig, gsig, pids = best["sig"], best["gsig"], "/".join(best["gem"].project_ids) or "—"
    gap = w["yellow_threshold"] - best["comp"]
    near = f" (composite {best['comp']:.3f}, {gap:.3f} below threshold)"

    cont = gsig.get("containment")
    if cont is not None and cont >= w["route_containment_threshold"]:
        return ("FRAGMENT_OF_EXISTING",
                f"{cont:.0%} of this trace lies inside the drawn route of {pids} — a partial "
                f"trace of a line GEM already tracks, not a new pipeline.{near}")

    # Ahead of NEAR_MISS deliberately: "the nearest row has no route and sits in the same
    # provinces" is a concrete, actionable finding, where NEAR_MISS only says the scorer
    # came close without saying why. A record satisfying both should be reported as the
    # former; the composite and gap ride along either way.
    if ref_has_geometry and sig.get("g_untested") and (sig.get("s_geoarea") or 0) >= GEOAREA_ROUTE_FLOOR:
        return ("ROUTE_FOR_EXISTING",
                f"{pids} has NO drawn route and its declared geography matches this trace "
                f"(geoarea {sig['s_geoarea']:.2f}) — candidate GEOMETRY for that row. Verify, "
                f"then route via a human routes-repo PR; never auto-replace.{near}")

    if gap <= w["near_miss_delta"]:
        return ("NEAR_MISS",
                f"nearest GEM row is {pids}{near}. Adjudicate by hand — a false Addition "
                f"hides a real one.")

    return ("DISCOVERY_CANDIDATE",
            "no GEM row is a plausible match — treat as real pipe GEM may not track, after "
            "checking for an existing row under another name (→ OtherEnglishNames)."
            f" Nearest was {pids}{near}.")


class _Diagnostics:
    """Did the matcher have anything to work with?

    A run returning zero overlaps is ambiguous on its face: either GEM genuinely lacks
    all of this, or every signal the matcher reads was blank. Those demand opposite
    responses, and nothing distinguished them — Iraq OSM 2026-07-28 wrote
    `overlaps: 0, additions: 52` and an empty route_metrics.json, and the null run went
    unnoticed because the output looked like a legitimate finding. These counters make
    the difference explicit and escalate when the evidence says "blind".
    """

    # Escalate a zero-overlap run once the reference set is big enough that zero is
    # implausible rather than merely small.
    MIN_REFS_FOR_NULL_GATE = 5
    BLIND_FRACTION = 0.50

    def __init__(self, manifest: dict, source: str):
        self.source = source
        self.display = manifest.get("display_name") or source
        self.refs = self.named = self.with_geom = 0
        self.gem: dict = {}
        self.composites: list = []
        self.geoarea_scored = 0
        self.boundaries_error = ""

    def note_gem(self, tracker: str, n_pool: int, n_with_geom: int) -> None:
        self.gem[tracker] = {"rows": n_pool, "with_route": n_with_geom,
                             "pct_with_route": _pct(n_with_geom, n_pool)}

    def note_ref(self, r: dict, best: dict) -> None:
        self.refs += 1
        if (r.get("name") or "").strip():
            self.named += 1
        if r.get("has_geometry"):
            self.with_geom += 1
        self.composites.append(best["comp"])
        if best["sig"].get("s_geoarea") is not None:
            self.geoarea_scored += 1

    def build(self, overlaps: list, buckets: dict) -> dict:
        comps = sorted(self.composites)
        rows = sum(v["rows"] for v in self.gem.values())
        routed = sum(v["with_route"] for v in self.gem.values())
        d = {
            "reference_records": self.refs,
            "pct_reference_named": _pct(self.named, self.refs),
            "pct_reference_with_geometry": _pct(self.with_geom, self.refs),
            "pct_reference_geoarea_scored": _pct(self.geoarea_scored, self.refs),
            "gem_pool": self.gem,
            "overlap_rate": _pct(len(overlaps), self.refs),
            "composite_distribution": {
                "max": comps[-1] if comps else None,
                "p90": comps[int(0.90 * (len(comps) - 1))] if comps else None,
                "median": comps[len(comps) // 2] if comps else None,
                "min": comps[0] if comps else None,
            },
            "dispositions": {k: len(v) for k, v in buckets.items()},
            "escalations": [],
        }
        if self.boundaries_error:
            d["escalations"].append({
                "code": "GEOAREA_UNAVAILABLE", "detail": self.boundaries_error,
                "action": "geoarea_weight is set for this dataset but the admin-1 boundaries "
                          "could not be loaded — the signal silently contributed nothing. "
                          "Fix the data/boundaries install and re-run before using this diff."})

        name_blind = _pct(self.named, self.refs) < self.BLIND_FRACTION * 100
        route_blind = _pct(routed, rows) < self.BLIND_FRACTION * 100
        if not overlaps and self.refs >= self.MIN_REFS_FOR_NULL_GATE:
            d["escalations"].append({
                "code": "MATCH_QUALITY", "detail":
                    f"zero overlaps from {self.refs} reference records "
                    f"(max composite {d['composite_distribution']['max']}, "
                    f"threshold not reached by any pair).",
                "action": "Do NOT read this as 'GEM is missing all of these'. Confirm the "
                          "matcher had live signal (see pct_reference_named / pct_with_route) "
                          "before any of these records is treated as a discovery."})
        if name_blind and route_blind:
            geo_on = self.geoarea_scored > 0
            d["escalations"].append({
                "code": "MATCH_QUALITY", "detail":
                    f"{d['pct_reference_named']}% of reference records are named and "
                    f"{_pct(routed, rows)}% of GEM rows have a drawn route — the name and "
                    f"geometry axes are both mostly dead for this pairing"
                    + (f", carried by the admin-area signal on "
                       f"{d['pct_reference_geoarea_scored']}% of records." if geo_on
                       else ", and geoarea_weight is OFF, so nothing replaces them."),
                "action": ("Admin-area evidence is province-coarse: it routes a finding to a "
                           "human, it never confirms a match. Review dispositions by hand and "
                           "do not treat unmatched records as confirmed discoveries." if geo_on
                           else "Set geoarea_weight for this dataset (scripts/geo_signals.py) "
                                "and re-run; composites here otherwise rest on nothing.")})
        return d


def _pct(n: int, d: int) -> float:
    return round(100.0 * n / d, 1) if d else 0.0


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
    near_misses: list = []
    buckets: dict[str, list] = {k: [] for k in DISPOSITIONS}
    weights_used: dict[str, dict] = {}
    route_metrics: dict[str, dict] = {}
    meta_csv: dict[str, str] = {}
    diag = _Diagnostics(manifest, args.source)

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

        # Every GEM geometry once, up front: bounded by the country's row count and it
        # is what makes proximity ranking possible (see spatial_rank).
        gem_shapes = []
        for idx, g in enumerate(pool):
            gs = _shape(gem_geom(g))
            if gs is not None and not gs.is_empty:
                gem_shapes.append((idx, gs))
        diag.note_gem(tracker, len(pool), len(gem_shapes))

        for r in refs:
            w = resolve_weights(manifest, r.get("dataset"))
            weights_used[r.get("dataset") or "_source"] = w
            buffer_km = w["buffer_km_for_overlap"]
            ref_geom = sidecar.get(r["geometry_ref"]) if r.get("has_geometry") else None

            footprint = {}
            if w["geoarea_weight"] and ref_geom is not None:
                try:
                    footprint = geo_signals.admin_footprint(ref_geom)
                except geo_signals.BoundariesUnavailable as e:
                    diag.boundaries_error = str(e)

            scored = []
            for idx, g in enumerate(pool):
                asig, reasons = attribute_signals(r, g)
                if footprint:
                    gsc, greason = geo_signals.geoarea_score(footprint, g, scope_country=args.country)
                    if gsc is not None:
                        asig["s_geoarea"] = gsc
                        reasons.extend(greason)
                scored.append([composite(w, asig), asig, reasons, g, idx])
            scored.sort(key=lambda x: x[0], reverse=True)

            # Candidates that earn a geometry test: the attribute leaders UNION the
            # physically closest rows. The union is the point — attribute rank alone
            # goes blind on unnamed references, proximity alone goes blind on
            # references with no geometry.
            geom_idx = set(i for *_, i in scored[:TOPK_GEOMETRY])
            if ref_geom is not None:
                geom_idx |= set(spatial_rank(ref_geom, gem_shapes, w["spatial_candidates"]))

            cands = []
            for acomp, asig, reasons, g, idx in scored:
                sig = dict(asig)
                gsig = {}
                if ref_geom is not None:
                    if idx in geom_idx:
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
            diag.note_ref(r, best)
            reason_str = "; ".join(best["reasons"])
            if best["gsig"].get("iou") is not None:
                reason_str += f"; route IoU {best['gsig']['iou']}"
            if footprint:
                fs = geo_signals.footprint_summary(footprint)
                if fs:
                    reason_str += f"; trace crosses {fs}"

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
                cov, cov_ratio, cov_note = coverage(r, g, best["gsig"])
                if cov_note:
                    reason_str += "; " + cov_note
                    # A sliver can co-locate but it cannot corroborate a route: a 0.1 km
                    # trace must never nominate itself as a replacement for a 105 km route.
                    repl = False
                row = {"tracker": tracker, "confidence": conf, "composite": best["comp"],
                       "reason": reason_str, "signals": best["sig"],
                       "coverage": cov, "coverage_ratio": cov_ratio,
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
                disp, why = disposition(best, w, ref_geom is not None)
                add = {"tracker": tracker, "confidence": "red", "disposition": disp,
                       "ref": ref_view(r),
                       "best_guess": {"project_ids": best["gem"].project_ids,
                                      "name": best["gem"].pipeline_name,
                                      "composite": best["comp"],
                                      "route_accuracy": best["gem"].route_accuracy,
                                      "signals": best["sig"]} if best["comp"] > 0 else None,
                       "reason": reason_str, "note": f"[{disp}] {why}"}
                if footprint:
                    add["trace_footprint"] = geo_signals.footprint_summary(footprint)
                additions.append(add)
                buckets[disp].append(add)
                if disp == "NEAR_MISS":
                    near_misses.append(add)
                # The trace itself is carried on EVERY unmatched record, not just matched
                # ones. It is the whole value of a ROUTE_FOR_EXISTING / DISCOVERY finding
                # and the reason the record can be acted on at all downstream.
                if ref_geom is not None:
                    routes.append({"tracker": tracker, "ref_id": r["ref_id"],
                                   "oid": r["ref_id"].split(":")[-1], "name": r["name"],
                                   "status": r["status"], "diameter": r["diameter_raw"],
                                   "length_km": r["length_km"], "geodesic_km": r["geodesic_km"],
                                   "matched_project_ids": [], "disposition": disp,
                                   "candidate_for": best["gem"].project_ids
                                                    if disp in ("ROUTE_FOR_EXISTING", "FRAGMENT_OF_EXISTING",
                                                                "NEAR_MISS") else [],
                                   "gem_route_accuracy": best["gem"].route_accuracy,
                                   "route_iou": best["gsig"].get("iou"),
                                   "replacement_candidate": False, "wkt": _to_wkt(ref_geom)})

        for s in segs:
            if not s.matched:
                gem_only.append({"tracker": tracker, **gem_view(s),
                                 "fuel": tracker, "note": "in GEM, no reference match"})

    diagnostics = diag.build(overlaps, buckets)
    diff = {
        "meta": {"source": args.source, "display_name": manifest.get("display_name"),
                 "source_tier": manifest.get("source_tier"), "country": args.country,
                 "commodity": args.commodity, "gem_csv": meta_csv,
                 # Per DATASET, not one global block: weights now resolve per dataset, so a
                 # single "weights" key would misreport a multi-dataset run.
                 "weights": weights_used,
                 "diagnostics": diagnostics,
                 "counts": {"reference_records": len(ref), "overlaps": len(overlaps),
                            "additions": len(additions), "gem_only": len(gem_only),
                            "status_conflicts": len(status_conflicts), "ambiguous": len(ambiguous),
                            "near_misses": len(near_misses), "routes": len(routes),
                            "dispositions": {k: len(v) for k, v in buckets.items()}}},
        "overlaps": overlaps, "additions": additions, "near_misses": near_misses,
        "gem_only": gem_only, "status_conflicts": status_conflicts,
        "ambiguous": ambiguous, "routes": routes,
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
    disp_str = ", ".join(f"{k}={len(v)}" for k, v in buckets.items() if v)
    print(f"  unmatched by disposition: {disp_str or 'none'}")
    dd = diagnostics
    print(f"  signal: {dd['pct_reference_named']}% refs named, "
          f"{dd['pct_reference_with_geometry']}% with geometry, "
          f"{dd['pct_reference_geoarea_scored']}% geoarea-scored; GEM routes "
          + ", ".join(f"{t} {v['pct_with_route']}%" for t, v in dd["gem_pool"].items()))
    for e in dd["escalations"]:
        print(f"  !! {e['code']}: {e['detail']}\n     -> {e['action']}", file=sys.stderr)
    print(f"  -> {staging/'match_diff.json'}")


def _to_wkt(geom: dict) -> str:
    try:
        from shapely.geometry import shape
        return shape(geom).wkt
    except Exception:
        return ""


if __name__ == "__main__":
    main()
