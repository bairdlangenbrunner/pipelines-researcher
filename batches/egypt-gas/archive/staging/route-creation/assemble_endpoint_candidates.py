#!/usr/bin/env python3
"""Assemble bucket-C route candidates from the endpoint-research fan-out (§8, 2026-07-30).

Reads the eight research_results_*.json files (subagent output; every URL already
passed scripts/url_verifier.py inside the research runs) and:

  - resolved PIDs -> scripts/build_route_candidate.py --method endpoints, suggested
    accuracy `very low (straight line/schematic)` (Baird asked for two-point routes;
    that is the sheet vocab for them, below the endpoints rung's `low` cap);
  - P3937/P3938 -> --method sidecar off the GulfPub traces the research corroborated
    (gulfpub:gas:465 BED-2->BED-3 26.8 km; gulfpub:gas:3783 BED->Alam El Shawish
    70 km). Their 130 km sheet lengths are flagged by the gate as intentional FAILs
    (the research shows both figures are wrong -- likely a garbled OGJ 130-mile echo);
  - unresolved PIDs (one/both endpoints not publicly coordinated) + P6704 (both
    facilities share one geocode -> a degenerate two-point line) -> ROUTE_PARTIAL
    records appended to staged_resolutions.json: corridor + the sourced half, no
    geometry (standing rule 2 -- coordinates are never fabricated).
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
STAGING = HERE
ACC_VLOW = "very low (straight line/schematic)"

# research corroborated these GulfPub traces -> best rung is sidecar, not endpoints
SIDECAR = {
    "P3937": ("gulfpub:gas:465",
              "GulfPub 'Badr el Din 2 - Badr el Din' trace (26.8 km) matches the "
              "BED-2->BED-3 corridor the research corroborated."),
    "P3938": ("gulfpub:gas:3783",
              "GulfPub 'Badr el Din Field - Alam El Shawish' trace (70 km) matches the "
              "BED-3->Alam El Shawish corridor the research corroborated."),
}

GROUPS = ["westdesert", "fayoum", "delta_west", "delta_central",
          "offshore_med", "suez_gulf", "cairo_east", "upper_egypt"]


def _notes(r: dict) -> str:
    bits = [(r.get("notes") or "").strip()]
    sc = (r.get("sheet_conflicts") or "").strip()
    if sc:
        bits.append(f"SHEET CONFLICT: {sc}")
    fixes = r.get("spelling_fixes") or {}
    for col, val in fixes.items():
        bits.append(f"Suggest {col} -> '{val}'.")
    return " ".join(b for b in bits if b)


def _coord(p: dict | None):
    p = p or {}
    lon, lat = p.get("lon"), p.get("lat")
    return (lon, lat) if lon is not None and lat is not None else None


def main() -> None:
    results = []
    for g in GROUPS:
        results += json.loads((HERE / f"research_results_{g}.json").read_text())
    wl = {u["project_id"]: u for u in
          json.loads((HERE / "worklist.json").read_text())["units"]}

    candidates, partials, failures = [], [], []
    for r in results:
        pid = r["project_id"]
        start, end = _coord(r.get("start")), _coord(r.get("end"))
        degenerate = start and end and start == end
        base = [sys.executable, "scripts/build_route_candidate.py", "--pid", pid,
                "--commodity", "gas", "--staging", str(STAGING)]

        if pid in SIDECAR:
            ref_id, why = SIDECAR[pid]
            cmd = base + ["--method", "sidecar", "--ref-id", ref_id,
                          "--accuracy", "medium",  # trace identity vs the 'Spur' rows isn't settled
                          "--notes", f"{why} {_notes(r)}"]
            for u in dict.fromkeys(r.get("route_refs") or []):
                cmd += ["--route-ref", u]
        elif r.get("resolved") and start and end and not degenerate:
            s, e = r["start"], r["end"]
            cmd = base + ["--method", "endpoints",
                          "--start", f"{start[0]},{start[1]}", "--end", f"{end[0]},{end[1]}",
                          "--start-name", s.get("name", ""), "--end-name", e.get("name", ""),
                          "--start-ref", s.get("evidence_url", ""),
                          "--end-ref", e.get("evidence_url", ""),
                          "--accuracy", ACC_VLOW,
                          "--notes", " ".join(x for x in (
                              _notes(r),
                              f"Start coord basis: {s.get('coord_basis', '')}.",
                              f"End coord basis: {e.get('coord_basis', '')}.") if x.strip())]
            extra = [u for u in dict.fromkeys(r.get("route_refs") or [])
                     if u not in (s.get("evidence_url"), e.get("evidence_url"))]
            for u in extra:
                cmd += ["--route-ref", u]
        else:
            partials.append(r)
            continue

        p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
        print(p.stdout.strip())
        if p.returncode != 0:
            failures.append((pid, p.stderr.strip()))
            print(p.stderr.strip(), file=sys.stderr)
        else:
            candidates.append(pid)
            if p.stderr.strip():
                print(p.stderr.strip(), file=sys.stderr)

    # ---- ROUTE_PARTIAL records: corridor + sourced half, no geometry ---------- #
    sr_path = STAGING / "staged_resolutions.json"
    data = json.loads(sr_path.read_text())
    recs = data.setdefault("resolutions", [])
    for r in partials:
        pid = r["project_id"]
        u = wl.get(pid) or {}
        s, e = r.get("start") or {}, r.get("end") or {}
        sc, ec = _coord(s), _coord(e)
        degenerate = sc and ec and sc == ec
        why = ("both endpoints geocode to the same point (degenerate two-point line)"
               if degenerate else "endpoint(s) not publicly coordinated")
        refs = list(dict.fromkeys(r.get("route_refs") or []))
        rec = {
            "project_id": pid,
            "sheet_row": ", ".join(str(x) for x in (u.get("sheet_rows") or [])),
            "pipeline_name": u.get("pipeline_name", ""),
            "segment_name": "; ".join(u.get("segment_names") or []),
            "ref_col": "__ROUTE__", "class_in": "ROUTE", "class_out": "ROUTE_PARTIAL",
            "value_cols": [], "primary_value_col": None, "values": {},
            "primary_value": "", "current_ref": "",
            "start_name": s.get("name", ""),
            "start_lon": sc[0] if sc and not degenerate else None,
            "start_lat": sc[1] if sc and not degenerate else None,
            "end_name": e.get("name", ""),
            "end_lon": ec[0] if ec and not degenerate else None,
            "end_lat": ec[1] if ec and not degenerate else None,
            "waypoints": [], "waypoint_note": "",
            "corridor_desc": (r.get("notes") or "").strip(),
            "current_route_accuracy": u.get("current_route_accuracy", ""),
            "suggested_route_accuracy": "",
            "proposed_refs": refs,
            "verifications": [{"url": x, "ok": True} for x in refs],
            "tier": "low" if refs else "",
            "independent": len(refs) >= 2,
            "source_language": "en",
            "researcher_notes": " ".join(x for x in (
                f"NO GEOMETRY STAGED: {why} -- coordinates are never fabricated "
                "(standing rule 2).",
                _notes(r)) if x),
        }
        recs[:] = [x for x in recs if x.get("project_id") != pid] + [rec]
    sr_path.write_text(json.dumps(data, indent=1, ensure_ascii=False))

    print(f"\n{len(candidates)} candidates assembled, {len(partials)} ROUTE_PARTIAL "
          f"records staged, {len(failures)} hard failures")
    for pid, err in failures:
        print(f"  FAILED {pid}: {err[:300]}", file=sys.stderr)


if __name__ == "__main__":
    main()
