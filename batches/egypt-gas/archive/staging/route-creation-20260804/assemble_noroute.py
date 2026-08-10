"""Assemble adjudicated no-route candidates (Egypt gas §8, 2026-08-04).

ENTSOG traced (medium), endpoints from research_results_<group>.json, path from
noroute_match.py (overlays/<PID>_entsog_path.geojson). Run AFTER adjudicating the
nr_<PID>.png overlays. Sinai rows (P8034/P8041/P8044/P8045) were assembled earlier.

  python3 batches/egypt-gas/staging/route-creation-20260804/assemble_noroute.py [PID ...]
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

# pid -> (group, [extra route refs beyond ENTSOG], note)
PIDS = {
    "P8033": ("suez",
              ["https://www.elbalad.news/2332558",
               "https://www.wikidata.org/wiki/Q56359816"],
              "drawn Ain Sokhna-Abu Sultan corridor, path 102.6 km vs sheet 106 "
              "(ratio 0.968), end snaps 3.2/2.9 km; endpoints: Ain Sokhna town/port "
              "(OSM node 11489833146) and Abu Sultan Power Station (Wikidata Q56359816, "
              "corroborated by elbalad.news naming this exact 32in line); distinct from "
              "P8002 which passes through Abu Sultan from the north toward NAC"),
    "P8036": ("suez",
              ["https://www.wikidata.org/wiki/Q12246558",
               "https://www.wikidata.org/wiki/Q56359816"],
              "drawn Mit Nama-Abu Sultan corridor via the delta edge, path 143.4 km vs "
              "sheet 114 (ratio 1.258, in gate), snaps 1.7/2.9 km; Mit Nama is a "
              "settlement-level anchor (Wikidata Q12246558) whose GASCO grid-node role is "
              "corroborated by the presidency.eg Nubariya-Mit Nama project page; Abu "
              "Sultan hub coordinate shared with P8033/P8002 (verified distinct segments)"),
    "P8038": ("suez",
              ["https://www.geonames.org/6412825/ra-s-bakr.html",
               "https://egyptoil-gas.com/reports/gulf-of-suez-eastern-desert-and-sinai-egypts-crude-oil-squad/"],
              "drawn Gulf-of-Suez west-shore coastal corridor, path 163.5 km vs sheet 192 "
              "(ratio 0.852), snaps 7.7/3.2 km (start snap within the p90 map accuracy); "
              "Ras Bakr Transmission Station re-verified via GeoNames 6412825 (same "
              "resolution as applied P8013); corridor continuity: P8013 feeds this line's "
              "start, P8033 continues from its end"),
    "P8042": ("suez",
              ["https://energy.frontieregypt.com/downstream/refining-and-petrochemicals/united-gas-derivatives-company-ugdc",
               "http://web.archive.org/web/20240526082111/https://theenergyyear.com/articles/a-vital-link-in-egypts-gas-chain/"],
              "drawn canal-west-bank corridor Port Said-Suez, path 155.9 km vs sheet 215 "
              "(ratio 0.725, gate FAIL documented) with snaps 0.6/1.3 km; the 215 km sheet "
              "length looks high - Port Said-Suez along the canal is ~162 km, so 215 "
              "implies an unexplained detour; both termini are city-level anchors (UGDC "
              "plant confirmed in Port Said by 2 sources but no verifiable street-level "
              "footprint; no named Suez facility in any source) - REVIEW length cell"),
    "P8027": ("delta",
              ["https://globalenergyobservatory.org/geoid/46030",
               "https://www.wikidata.org/wiki/Q17466774",
               "https://petro-mag.org/Uploads/Files/8485d495-066a-4039-af4c-1eb97a28c3ef.pdf"],
              "drawn coastal Mediterranean trunk between the two LNG/grid hubs, path "
              "153.2 km vs sheet 165 (ratio 0.929), snaps 1.1/1.7 km; anchors: SEGAS "
              "Damietta LNG (GEO 46030) and Egyptian LNG Idku (Wikidata Q17466774); "
              "GASCO Nov-2025 magazine names an operating Idku/Damietta line"),
    "P8040": ("delta",
              ["https://egyptoil-gas.com/wp-content/uploads/2019/01/EGAS-Annual-Report-2018-EN.pdf",
               "https://www.turboden.com/company/media/press/press-releases/4120/turboden-together-with-siemens-energy-starts-the-development-of-a-first-of-its-kind-high-efficient-gas-compressor-station-at-gasco-in-dahshour-egypt",
               "https://www.egypttoday.com/Article/3/98691/Italian-investments-in-Dahshur-gas-station-reach-25M"],
              "drawn desert-edge dogleg west then north to 6 October, path 54.7 km vs "
              "sheet 65 (ratio 0.842) - the detour explains the 65 km length vs the 32 km "
              "straight line; 6 October end snaps 0.1 km onto a drawn stroke terminus; "
              "endpoints: GASCO Dahshur compressor-station hub (Turboden/egypttoday) and "
              "6 October power station (GEO 44898); NAME FLAG: PipelineName says "
              "'Damanhur' but StartLocation + the sheet's own Arabic name both say "
              "'Dahshour' (Damanhur is ~170 km away, impossible for a 65 km line) - "
              "recommend renaming to 'Dahshur-6 October Gas Pipeline'"),
}


def run(cmd):
    print("\n$ " + " ".join(str(c) for c in cmd)[:200])
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(r.stdout[-1200:] if r.stdout else "", r.stderr[-600:] if r.stderr else "")
    return r.returncode


def main() -> None:
    only = set(sys.argv[1:])
    fails = []
    for pid, (grp, refs, note) in PIDS.items():
        if only and pid not in only:
            continue
        res = {r["project_id"]: r for r in
               json.load(open(STAGING / f"research_results_{grp}.json"))}[pid]
        feat = json.load(open(STAGING / "overlays" / f"{pid}_entsog_path.geojson"))
        fc_path = STAGING / "prep" / f"{pid}_entsog_fc.geojson"
        fc_path.parent.mkdir(exist_ok=True)
        fc_path.write_text(json.dumps(
            {"type": "FeatureCollection", "features": [feat]}))
        s = f'{res["start"]["lon"]},{res["start"]["lat"]}'
        e = f'{res["end"]["lon"]},{res["end"]["lat"]}'
        cmd = [sys.executable, str(ROOT / "scripts/build_route_candidate.py"),
               "--pid", pid, "--commodity", "gas", "--staging", str(STAGING),
               "--method", "traced", "--geom", str(fc_path),
               "--accuracy", "medium",
               "--snap-start", s, "--snap-end", e, "--snap-max-km", "10",
               "--source-url", ENTSOG_URL, "--source-name", ENTSOG_NAME,
               "--map", ENTSOG_URL,
               "--notes", f"{note}. {ENTSOG_BASIS}."]
        for u in [ENTSOG_URL] + refs:
            cmd += ["--route-ref", u]
        if run(cmd) != 0:
            fails.append(pid)
    print("\nFAILED:" if fails else "\nassembled", fails or sorted(
        p for p in PIDS if not only or p in only))


if __name__ == "__main__":
    main()
