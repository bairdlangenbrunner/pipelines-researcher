"""Assemble the 11 adjudicated replacement candidates (Egypt gas §8, 2026-08-04).

ENTSOG traced (medium, --replace): P7567 P8019 P8024 P0436 P8010 P0462 P3928 P3936
GulfPub sidecar (high, --replace): P3935 P6034 P6037

Wraps each accepted ENTSOG shortest-path Feature as a FeatureCollection, snaps its
ends to the existing GEM route's (sourced) termini, and shells out to
scripts/build_route_candidate.py once per PID. P3935 is NOT snapped: its existing
south endpoint is the defect the replacement fixes.
"""
import json
import subprocess
import sys
from pathlib import Path

from shapely.geometry import shape

STAGING = Path(__file__).resolve().parent
ROOT = STAGING.parents[3]
sys.path.insert(0, str(ROOT / "scripts"))
from route_compare import load_gem_route  # noqa: E402

ENTSOG_URL = ("https://www.entsog.eu/sites/default/files/2026-01/"
              "ENTSOG_GIE_SYSCAP_2026_1600x1200_FULL_016_FLAT.pdf")
ENTSOG_NAME = "ENTSOG/GIE System Capacity Map 2026 (January 2026 edition)"
ENTSOG_BASIS = ("corridor from the ENTSOG/GIE System Capacity Map 2026 vector layer "
                "(sources/entsog/, georef: PDF coastline ICP vs Natural Earth, median "
                "residual 1 m); empirical accuracy over 24 Egypt high/medium GEM routes: "
                "median lateral offset 4.2 km, p90 13 km")

ENTSOG_PIDS = {
    "P7567": "network path parallels the very-low straight line 4 km west along the drawn Idku-Abu Hummus corridor; path 29.7 km vs sheet 30",
    "P8019": "drawn Damanhur-Tanta corridor sags south of the straight line; path 61.5 km vs sheet 60",
    "P8024": "ENTSOG draws the documented dogleg via Tanta that the straight line misses; path 134.9 km vs sheet 125",
    "P0436": "AGP corridor drawn and name-tagged on the map; path 232 km vs sheet 264 hugs the existing low-accuracy zigzag within 2.1 km",
    "P8010": "coastal arc Edku-Gamasa drawn on the map vs the inland straight line; path 135.8 km vs sheet 121",
    "P0462": "EMG Arish-Ashkelon marine corridor as drawn; path 102.3 km vs sheet 90; offshore cartographic centreline",
    "P3928": "drawn Nubaria-Sadat corridor just south of the straight line; path 56.7 km vs sheet 73 (snapped ends close part of the gap)",
    "P3936": "follows the drawn western-desert corridor to Amreya; path 211.4 km vs sheet 160 (ratio 1.32, at the gate edge) - REVIEW: corridor may include WDGP trunk alignment",
}

GULFPUB_PIDS = {
    "P3935": ("gulfpub:gas:20005",
              "GulfPub 'Salam - Matruh' trace 84.7 km vs sheet 90; REPLACES a straight line whose south endpoint sits ~400 km too far south (existing geodesic length wildly exceeds sheet length) - this replacement corrects a real endpoint defect"),
    "P6034": ("gulfpub:gas:3792",
              "GulfPub 'Hurghada - Port Safaga Pipeline' trace 57.1 km follows the coastal corridor alongside the existing straight line; sheet length 38.5 km conflicts with the 57 km geometry (road distance Hurghada-Safaga ~55-60 km) - length cell likely low, flagged, not edited"),
    "P6037": ("gulfpub:gas:3802",
              "GulfPub 'Damietta - Port Said Pipeline' trace 58.9 km, clean coastal corridor vs sheet 50; preferred over the ENTSOG network path (62 km) as the higher source-ladder rung"),
}


def endpoints(pid):
    gj = load_gem_route(pid, "gas")
    geom = shape(gj)
    lines = [geom] if geom.geom_type == "LineString" else list(geom.geoms)
    big = max(lines, key=lambda l: l.length)
    (x0, y0), (x1, y1) = big.coords[0], big.coords[-1]
    return f"{x0:.6f},{y0:.6f}", f"{x1:.6f},{y1:.6f}"


def run(cmd):
    print("\n$ " + " ".join(str(c) for c in cmd)[:220])
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(r.stdout[-1500:] if r.stdout else "", r.stderr[-800:] if r.stderr else "")
    return r.returncode


def main() -> None:
    fails = []
    for pid, note in ENTSOG_PIDS.items():
        feat = json.load(open(STAGING / "overlays" / f"{pid}_entsog_path.geojson"))
        fc = {"type": "FeatureCollection", "features": [feat]}
        fc_path = STAGING / "prep" / f"{pid}_entsog_fc.geojson"
        fc_path.parent.mkdir(exist_ok=True)
        fc_path.write_text(json.dumps(fc))
        s, e = endpoints(pid)
        cmd = [sys.executable, str(ROOT / "scripts/build_route_candidate.py"),
               "--pid", pid, "--commodity", "gas", "--staging", str(STAGING),
               "--method", "traced", "--geom", str(fc_path), "--replace",
               "--accuracy", "medium",
               "--snap-start", s, "--snap-end", e, "--snap-max-km", "10",
               "--route-ref", ENTSOG_URL,
               "--source-url", ENTSOG_URL, "--source-name", ENTSOG_NAME,
               "--map", ENTSOG_URL,
               "--notes", f"{note}. {ENTSOG_BASIS}."]
        if run(cmd) != 0:
            fails.append(pid)

    for pid, (ref_id, note) in GULFPUB_PIDS.items():
        cmd = [sys.executable, str(ROOT / "scripts/build_route_candidate.py"),
               "--pid", pid, "--commodity", "gas", "--staging", str(STAGING),
               "--method", "sidecar", "--ref-id", ref_id, "--replace",
               "--notes", note]
        if run(cmd) != 0:
            fails.append(pid)

    print("\nFAILED:" if fails else "\nall candidates assembled", fails or "")


if __name__ == "__main__":
    main()
