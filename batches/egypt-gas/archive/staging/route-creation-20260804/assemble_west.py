"""Assemble the west-group candidates (Egypt gas §8, 2026-08-04).

P8032 -> traced (ENTSOG network path, medium): drawn Amreya-Dahshour desert trunk,
         path 207.8 km vs sheet 200 (ratio 1.039), snaps 1.9/0.6 km.
P8031 -> endpoints great-circle (very low): 14 km local cement line, no ENTSOG
         counterpart (network hop was 7.6 km of unrelated trunk); gc 8.4 km.
P8039 -> endpoints great-circle (very low): network path REJECTED (101 km zigzag
         over strokes that are not this corridor, ratio 1.36); gc 77.5 km vs
         sheet 74 (ratio 1.047).
"""
import json
import subprocess
import sys
from pathlib import Path

STAGING = Path(__file__).resolve().parent
ROOT = STAGING.parents[3]

ENTSOG_URL = ("https://www.entsog.eu/sites/default/files/2026-01/"
              "ENTSOG_GIE_SYSCAP_2026_1600x1200_FULL_016_FLAT.pdf")
ENTSOG_NAME = "ENTSOG/GIE System Capacity Map 2026 (January 2026 edition)"
ENTSOG_BASIS = ("corridor from the ENTSOG/GIE System Capacity Map 2026 vector layer "
                "(sources/entsog/, georef: PDF coastline ICP vs Natural Earth, median "
                "residual 1 m); empirical accuracy over 24 Egypt high/medium GEM routes: "
                "median lateral offset 4.2 km, p90 13 km")
ACC_VLOW = "very low (straight line/schematic)"

res = {r["project_id"]: r for r in
       json.load(open(STAGING / "research_results_west.json"))}


def run(cmd):
    print("\n$ " + " ".join(str(c) for c in cmd)[:200])
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(r.stdout[-1200:] if r.stdout else "", r.stderr[-600:] if r.stderr else "")
    return r.returncode


def main() -> None:
    fails = []

    # --- P8032: traced off the drawn desert trunk ---
    pid = "P8032"
    r = res[pid]
    feat = json.load(open(STAGING / "overlays" / f"{pid}_entsog_path.geojson"))
    fc_path = STAGING / "prep" / f"{pid}_entsog_fc.geojson"
    fc_path.write_text(json.dumps({"type": "FeatureCollection", "features": [feat]}))
    note = ("drawn Amreya-Dahshour desert trunk, path 207.8 km vs sheet 200 (ratio "
            "1.039), snaps 1.9/0.6 km; endpoints: Amreya industrial/refining cluster "
            "(cluster-level anchor) and the Dahshour valve room at the 2005 EIB/"
            "PETROSAFE EIA's DMS coordinate (31.097E 29.890N) - that EIA names this "
            "exact 'Amriya-Dahshour 32-inch pipeline'; NOT a duplicate of P0474/P3934 "
            "(those flow INTO Amreya from the Western Desert; this line flows OUT "
            "toward Dahshour). Anchor caveat: start is cluster-level, so treat "
            "endpoint vicinity as +/- a few km")
    cmd = [sys.executable, str(ROOT / "scripts/build_route_candidate.py"),
           "--pid", pid, "--commodity", "gas", "--staging", str(STAGING),
           "--method", "traced", "--geom", str(fc_path),
           "--accuracy", "medium",
           "--snap-start", f'{r["start"]["lon"]},{r["start"]["lat"]}',
           "--snap-end", f'{r["end"]["lon"]},{r["end"]["lat"]}',
           "--snap-max-km", "10",
           "--source-url", ENTSOG_URL, "--source-name", ENTSOG_NAME,
           "--map", ENTSOG_URL,
           "--notes", f"{note}. {ENTSOG_BASIS}."]
    for u in [ENTSOG_URL] + (r.get("route_refs") or []):
        cmd += ["--route-ref", u]
    if run(cmd) != 0:
        fails.append(pid)

    # --- P8031 / P8039: endpoints great-circle, very low ---
    extra_notes = {
        "P8031": ("14 km local line with no ENTSOG counterpart (the map does not draw "
                  "sub-regional laterals; a 7.6 km network hop between snap points was "
                  "rejected as unrelated trunk). Straight line 8.4 km vs sheet 14 "
                  "(ratio 0.60) - normal undershoot for a schematic two-point line; "
                  "NOT a duplicate of P6032 Borg El Arab-Midor (24in vs this 12in, "
                  "different terminus)"),
        "P8039": ("ENTSOG network path REJECTED (101 km zigzag over strokes that are "
                  "not this corridor, ratio 1.36 vs sheet 74); straight line 77.5 km "
                  "(ratio 1.047) fits the sheet length well. Dahshour end reuses "
                  "P8032's EIA valve-room coordinate as the shared hub (inference, "
                  "flagged, not a separately surveyed point for this line); start is "
                  "Sadat City city-level (no named in-city station found)"),
    }
    for pid in ("P8031", "P8039"):
        r = res[pid]
        s, e = r["start"], r["end"]
        cmd = [sys.executable, str(ROOT / "scripts/build_route_candidate.py"),
               "--pid", pid, "--commodity", "gas", "--staging", str(STAGING),
               "--method", "endpoints",
               "--start", f'{s["lon"]},{s["lat"]}', "--end", f'{e["lon"]},{e["lat"]}',
               "--start-name", s.get("name", ""), "--end-name", e.get("name", ""),
               "--start-ref", s.get("evidence_url", ""),
               "--end-ref", e.get("evidence_url", ""),
               "--accuracy", ACC_VLOW,
               "--notes", " ".join(x for x in (
                   extra_notes[pid],
                   f'. {r.get("notes", "")}',
                   f' Start coord basis: {s.get("coord_basis", "")}.',
                   f' End coord basis: {e.get("coord_basis", "")}.') if x.strip())]
        for u in dict.fromkeys(r.get("route_refs") or []):
            if u not in (s.get("evidence_url"), e.get("evidence_url")):
                cmd += ["--route-ref", u]
        if run(cmd) != 0:
            fails.append(pid)

    print("\nFAILED:" if fails else "\nassembled P8032 P8031 P8039", fails or "")


if __name__ == "__main__":
    main()
