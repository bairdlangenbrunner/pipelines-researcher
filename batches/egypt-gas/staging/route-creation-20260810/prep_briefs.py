#!/usr/bin/env python3
"""Build per-PID research briefs for the Egypt route-creation completion batch.

Scope: every Egypt row that still lacks usable route geometry (`no route` / blank
RouteAccuracy) — the never-touched new NA rows, the four 08-07 candidates whose
geometry was withdrawn as defective, and the standing ROUTE_PARTIAL backlog.

Each brief carries, for one ProjectID:
  * sheet facts + the row's own citations (Route/Location/Length [ref], ResearcherNotes)
  * the GASCO Nov-2007 sheet's own `<dia>" <len> km` labels that match the row's
    Diameter + LengthKnownKm, with the nearest traced line — this is the map researcher
    NA read the rows off, so a label match identifies WHICH drawn line the row is
  * the traced GASCO lines near the row's map-space neighbourhood
  * every prior pass's findings/blockers for the PID (so a retry does not restart)

Writes briefs/<PID>.json + research_payload_<group>.json (geographic fan-out groups).
No geometry and no coordinates are produced here.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from pyproj import Geod

HERE = Path(__file__).parent
REPO = HERE.parents[3]
TRACES = REPO / "batches/egypt-gas/staging/map-traces-gasco"
CSV = REPO / "data/GGIT_gas_snapshot_20260810.csv"
OIL_CSV = REPO / "data/GOIT_oil_ngl_snapshot_20260810.csv"

GEOD = Geod(ellps="WGS84")

# Geographic fan-out groups. Every in-scope PID appears in exactly one.
GROUPS = {
    "sinai-north": ["P8052", "P8053", "P8008", "P8009", "P8055", "P8026"],
    "delta-east": ["P8035", "P8063", "P8049", "P8020", "P8022", "P8023", "P6033"],
    "alex-west": ["P8064", "P8065", "P8066", "P8067", "P8051", "P8050", "P6704", "P8059"],
    "cairo-fayoum": ["P8057", "P8058", "P8054", "P8003", "P8001", "P7326"],
    "upper-egypt": ["P8056", "P7588", "P7589", "P7605", "P0477"],
    "suez-sokhna": ["P8005", "P8006", "P8007"],
}


def norm_dia(s: str):
    """Diameter cell -> set of inch values (cells can be multi-valued: `24,20`)."""
    return {float(x) for x in re.findall(r"\d+(?:\.\d+)?", str(s or ""))}


def load_rows():
    gas = pd.read_csv(CSV, header=2, low_memory=False, keep_default_na=False, na_values=[])
    gas["SheetRow"] = gas.index + 4
    gas["_cmdty"] = "gas"
    oil = pd.read_csv(OIL_CSV, header=2, low_memory=False, keep_default_na=False, na_values=[])
    oil["SheetRow"] = oil.index + 4
    oil["_cmdty"] = "oil"
    return gas, oil


def prior_findings():
    """PID -> [{dir, resolved, notes, blockers, refs, endpoints}] from every prior pass."""
    out: dict[str, list] = {}
    for f in sorted((REPO / "batches/egypt-gas/staging").glob("route-creation*/re*_results_*.json")):
        try:
            recs = json.loads(f.read_text())
        except Exception:
            continue
        if not isinstance(recs, list):
            continue
        for r in recs:
            pid = r.get("project_id")
            if not pid:
                continue
            out.setdefault(pid, []).append({
                "pass": f"{f.parent.name}/{f.name}",
                "resolved": r.get("resolved"),
                "start": r.get("start"),
                "end": r.get("end"),
                "route_refs": r.get("route_refs") or [],
                "sheet_conflicts": r.get("sheet_conflicts") or "",
                "notes": r.get("notes") or "",
            })
    return out


def staged_state():
    """PID -> the most recent staged ROUTE_CANDIDATE / ROUTE_PARTIAL record."""
    out: dict[str, dict] = {}
    for d in sorted((REPO / "batches/egypt-gas/staging").glob("route-creation*")):
        p = d / "staged_resolutions.json"
        if not p.exists():
            continue
        for r in json.loads(p.read_text())["resolutions"]:
            out[r["project_id"]] = {
                "staging_dir": d.name,
                "class_out": r["class_out"],
                "method": r.get("method"),
                "geometry_file": r.get("geometry_file"),
                "length_km": r.get("length_km"),
                "sheet_length_km": r.get("sheet_length_km"),
                "length_ratio": r.get("length_ratio"),
                "suggested_route_accuracy": r.get("suggested_route_accuracy"),
                "start_name": r.get("start_name"), "start_lon": r.get("start_lon"),
                "start_lat": r.get("start_lat"),
                "end_name": r.get("end_name"), "end_lon": r.get("end_lon"),
                "end_lat": r.get("end_lat"),
                "proposed_refs": r.get("proposed_refs") or [],
                "researcher_notes": r.get("researcher_notes") or "",
            }
    return out


def main() -> None:
    gas, oil = load_rows()
    labels = json.loads((TRACES / "labels/gasco2007_labels.json").read_text())["labels"]
    places = json.loads((TRACES / "labels/gasco2007_places.json").read_text())["places"]
    traces = json.loads((TRACES / "gasco2007_gas_network.geojson").read_text())["features"]
    priors, staged = prior_findings(), staged_state()

    in_scope = [p for g in GROUPS.values() for p in g]
    briefs = {}
    for pid in in_scope:
        df = oil if pid == "P7326" else gas
        rows = df[df["ProjectID"] == pid]
        if rows.empty:
            print(f"  !! {pid} not found")
            continue
        r0 = rows.iloc[0]
        dias = set()
        for _, r in rows.iterrows():
            dias |= norm_dia(r.get("Diameter"))
        length = sum(float(x) for x in rows["LengthKnownKm"]
                     if str(x).replace(".", "").isdigit())

        # GASCO labels matching this row's diameter + length
        lab_hits = []
        for L in labels:
            ld = norm_dia(L["diameter_in"])
            dia_ok = bool(ld & dias) if dias else False
            len_ok = length > 0 and abs(L["length_km_label"] - length) / length <= 0.20
            if dia_ok and len_ok:
                score = "dia+len"
            elif len_ok:
                score = "len only"
            elif dia_ok and length and abs(L["length_km_label"] - length) / length <= 0.5:
                score = "dia + len within 50%"
            else:
                continue
            err = abs(L["length_km_label"] - length) / length if length else 9.0
            lab_hits.append({**L, "match": score, "length_err_frac": round(err, 3)})
        # closest length wins inside a match class, so an exact `24" 45 k.m` outranks
        # a merely-within-20% `24" 50 k.m`
        lab_hits.sort(key=lambda h: ({"dia+len": 0, "len only": 1, "dia + len within 50%": 2}[h["match"]],
                                     h["length_err_frac"]))

        # map-space neighbourhood: places whose caption shares a word with the row's
        # own Start/End text, then the traces nearest those captions
        words = {w.lower().strip(".,-") for w in
                 re.findall(r"[A-Za-z]{4,}", f"{r0.get('StartLocation','')} "
                                            f"{r0.get('EndLocation','')} "
                                            f"{r0.get('PipelineName','')}")}
        place_hits = [p for p in places
                      if {w.lower().strip(".,-") for w in re.findall(r"[A-Za-z]{4,}", p['text'])} & words]
        near_traces = []
        for p in place_hits[:6]:
            best = (1e9, None)
            for t in traces:
                pts = np.asarray(t["geometry"]["coordinates"], float)
                d = float(np.min(np.hypot((pts[:, 0] - p["lon"]) * 95, (pts[:, 1] - p["lat"]) * 111)))
                if d < best[0]:
                    best = (d, t)
            if best[1] is not None and best[0] < 40:
                pr = best[1]["properties"]
                near_traces.append({"via_place": p["text"], "km_from_place": round(best[0], 1),
                                    "path_id": pr["path_id"], "legend_class": pr["legend_class"],
                                    "length_km": pr["length_km"],
                                    "endpoints": [best[1]["geometry"]["coordinates"][0],
                                                  best[1]["geometry"]["coordinates"][-1]]})

        briefs[pid] = {
            "project_id": pid,
            "commodity": "oil" if pid == "P7326" else "gas",
            "sheet_rows": [int(x) for x in rows["SheetRow"]],
            "pipeline_name": r0.get("PipelineName", ""),
            "segment_names": [s for s in rows["SegmentName"] if str(s).strip()],
            "researcher": r0.get("Researcher", ""),
            "status": r0.get("Status", ""),
            "countries": r0.get("CountriesOrAreas", ""),
            "start_location": r0.get("StartLocation", ""),
            "end_location": r0.get("EndLocation", ""),
            "length_known_km": length,
            "diameter_in": sorted(dias),
            "capacity": f"{r0.get('Capacity','')} {r0.get('CapacityUnits','')}".strip(),
            "start_year": r0.get("StartYear1", ""),
            "current_route_accuracy": r0.get("RouteAccuracy", ""),
            "current_route_type": r0.get("RouteType", ""),
            "row_refs": {
                "Route [ref]": r0.get("Route [ref]", ""),
                "Location [ref]": r0.get("Location [ref]", ""),
                "Length [ref]": r0.get("Length [ref]", ""),
                "Status [ref]": r0.get("Status [ref]", ""),
            },
            "researcher_notes": r0.get("ResearcherNotes", ""),
            "gasco2007_label_matches": lab_hits,
            "gasco2007_nearby_traces": near_traces,
            "prior_passes": priors.get(pid, []),
            "staged_now": staged.get(pid),
        }

    outd = HERE / "briefs"
    outd.mkdir(exist_ok=True)
    for pid, b in briefs.items():
        (outd / f"{pid}.json").write_text(json.dumps(b, indent=1, ensure_ascii=False) + "\n")

    for grp, pids in GROUPS.items():
        payload = {"group": grp, "briefs": [briefs[p] for p in pids if p in briefs]}
        (HERE / f"research_payload_{grp}.json").write_text(
            json.dumps(payload, indent=1, ensure_ascii=False) + "\n")

    print(f"{len(briefs)} briefs -> briefs/ ; {len(GROUPS)} group payloads")
    for pid, b in briefs.items():
        best = b["gasco2007_label_matches"][0]["label_text"] if b["gasco2007_label_matches"] else "-"
        st = (b["staged_now"] or {}).get("class_out", "never staged")
        print(f"  {pid:<6} {b['length_known_km']:>7.1f} km  dia {b['diameter_in']!s:<12} "
              f"GASCO[{best:<14}] priors={len(b['prior_passes'])} {st}")


if __name__ == "__main__":
    main()
