#!/usr/bin/env python3
"""Assemble one route candidate per resolved PID (workflow §8 step 2).

Rung choice per PID was adjudicated by hand against the ENTSOG overlays:
  traced  (ENTSOG SYSCAP 2026 path)  — only where BOTH endpoint snaps fall inside
          ENTSOG's measured Egypt cartographic error (median 4.2 km / p90 13 km),
          i.e. the network genuinely reaches both researched termini.
  endpoints (great-circle)           — everywhere else; a snap beyond p90 means the
          ENTSOG path stops short of the real terminus and would be worse than a chord.
P8055 stays ROUTE_PARTIAL (endpoints unresolved) — no geometry.
"""
import glob
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
STAGING = Path(__file__).resolve().parent

RUNG = {
    # pid: (method, accuracy)
    "P8050": ("endpoints", "very low (straight line/schematic)"),
    "P8051": ("endpoints", "very low (straight line/schematic)"),
    "P8052": ("endpoints", "very low (straight line/schematic)"),
    "P8053": ("endpoints", "very low (straight line/schematic)"),
    "P8054": ("endpoints", "very low (straight line/schematic)"),
    "P8056": ("endpoints", "very low (straight line/schematic)"),
    "P8057": ("traced", "medium"),
    "P8058": ("endpoints", "very low (straight line/schematic)"),
    "P8059": ("traced", "medium"),
}

# why this rung, stated in the candidate notes so review can second-guess the call
RUNG_WHY = {
    "P8050": "ENTSOG rejected: its shortest path (54.6 km) is 1.9x the sheet length and "
             "swings well west of the direct Rosetta-Abu Hummus line; snaps 3.2/4.2 km.",
    "P8051": "ENTSOG rejected: end snap 14.1 km — the network path stops short of the "
             "Nubaria plant, outside ENTSOG's p90 Egypt error (13 km).",
    "P8052": "No ENTSOG coverage in North Sinai (NO_NETWORK_MATCH; nearest nodes 17-30 km).",
    "P8053": "No ENTSOG coverage in North Sinai (NO_NETWORK_MATCH; nearest nodes ~29-30 km).",
    "P8054": "ENTSOG rejected: end snap 14.4 km — path stops ~14 km short of El Wasta, "
             "outside ENTSOG's p90 Egypt error (13 km).",
    "P8056": "ENTSOG rejected: start snap 18.6 km — the trunk it matched runs well west of "
             "Abu Qurqas, beyond ENTSOG's p90 Egypt error (13 km).",
    "P8057": "ENTSOG accepted: snaps 2.9/1.4 km (inside median error), coherent north-south "
             "Cairo corridor, path 50.4 km = 1.24x the 40.8 km chord.",
    "P8058": "ENTSOG path available (snaps 2.6/8.6 km) but NOT used: the end-point identity "
             "itself is contested (see flags), so a medium-accuracy grid path would assert "
             "the New Administrative Capital reading more strongly than the evidence does.",
    "P8059": "ENTSOG accepted: snaps 0.0/2.0 km — both termini sit on the mapped network.",
}

research = {}
for f in sorted(STAGING.glob("research_results_*.json")):
    for rec in json.load(open(f)):
        research[rec["project_id"]] = rec


def notes_for(r):
    parts = [RUNG_WHY[r["project_id"]], r.get("corridor_desc") or "", r.get("notes") or ""]
    for fl in r.get("flags") or []:
        parts.append("FLAG: " + fl)
    return "  ".join(p.strip() for p in parts if p and p.strip())


fails = []
for pid, (method, acc) in RUNG.items():
    r = research[pid]
    s, e = r["start"], r["end"]
    cmd = [
        sys.executable, "scripts/build_route_candidate.py",
        "--pid", pid, "--commodity", "gas",
        "--staging", str(STAGING.relative_to(ROOT)),
        "--method", method,
        "--accuracy", acc,
        "--start-name", s["name"], "--end-name", e["name"],
        "--start-ref", s["evidence_url"], "--end-ref", e["evidence_url"],
        "--notes", notes_for(r),
    ]
    if method == "endpoints":
        cmd += ["--start", f"{s['lon']},{s['lat']}", "--end", f"{e['lon']},{e['lat']}",
                "--densify-km", "10"]
    else:
        cmd += ["--geom", str(STAGING / "overlays" / f"{pid}_entsog_path.geojson"),
                "--snap-start", f"{s['lon']},{s['lat']}",
                "--snap-end", f"{e['lon']},{e['lat']}",
                "--snap-max-km", "20",
                "--source-name", "ENTSOG/GIE System Capacity Map 2026 (January 2026 edition)",
                "--source-url", "https://www.entsog.eu/sites/default/files/2026-01/"
                                "ENTSOG_GIE_SYSCAP_2026_1600x1200_FULL_016_FLAT.pdf"]
    for u in (r.get("route_refs") or []):
        cmd += ["--route-ref", u]
    print("\n=== " + pid + " (" + method + ") ===", flush=True)
    p = subprocess.run(cmd, cwd=ROOT)
    if p.returncode != 0:
        fails.append(pid)

print("\nfailed:", fails or "none")
