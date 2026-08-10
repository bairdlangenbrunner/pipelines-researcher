#!/usr/bin/env python3
"""Stage every resolvable Egypt no-route row as a §8 candidate, in one packet.

Scope (Baird 2026-08-10): "every single Egypt pipeline should have at least a very
low resolution route". This pass therefore drops the *precision* bar that left 18
rows as ROUTE_PARTIAL across three earlier passes — a settlement- or facility-level
anchor pair is enough for `very low (straight line/schematic)`, which is exactly
what that accuracy tier means — while keeping the *sourcing* bar unchanged: every
coordinate below comes from OSM, GeoNames, a published facility record, or (flagged
as such) GEM's own already-applied route geometry used as an internal tie-in anchor.

Rows with no sourceable second endpoint stay ROUTE_PARTIAL. They are listed in
PARTIALS with the reason, and are NOT dressed up as candidates.

Run:  python batches/egypt-gas/staging/route-creation-20260810/build_candidates.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
REPO = HERE.parents[3]
ROUTES = REPO.parent / "GOIT-GGIT-pipeline-routes/data/individual-routes/gas-pipelines"

OSM = "https://www.openstreetmap.org/"
GEONAMES_ABUMADI = "https://www.geonames.org/search.html?q=Abu+Madi&country=EG"

# ---------------------------------------------------------------------------
# Shared anchors. `ref=""` marks an INTERNAL anchor (a point read off GEM's own
# applied route geometry) — usable to place a line, never citable as a source.
# ---------------------------------------------------------------------------
A = {
    "rashid":      (30.418428, 31.4013811, "Rashid (Rosetta) town", OSM + "node/768815269"),
    "abuhummus":   (30.3129485, 31.1005864, "Abu Hummus town / gas collection unit", OSM + "node/769122369"),
    "nubaria":     (30.6667343, 30.6992006, "Nubaria combined-cycle power station", OSM + "way/218972673"),
    "zuweid":      (34.1107742, 31.2127686, "El Sheikh Zuweid town, North Sinai", OSM + "node/768030243"),
    "sinaicement": (33.7765239, 30.7241954, "Sinai Cement industrial area (Sinai White Cement / Jabal Lubna cluster)", OSM + "way/97684492"),
    "milcement":   (33.848726, 30.7008117, "Military Cement (El-Areesh Co. for Cement / NSPO), Jabal Lubna", OSM + "node/11306111943"),
    "dahshur_v":   (31.240815, 29.751277, "Dahshur (GASCO Dahshur compressor-station locality), Giza", OSM + "node/331876352"),
    "dahshur_m":   (31.2406635, 29.7959331, "Manshaat Dahshur (GASCO Dahshur compressor-station locality), Giza", OSM + "node/768779115"),
    "elwasta":     (31.205556, 29.337778, "El Wasta town, Beni Suef", OSM + "node/768557743"),
    "abuqurqas":   (30.8377108, 27.930588, "Abu Qurqas town, Minya", OSM + "node/768584680"),
    "asyut":       (31.1853836, 27.1832822, "Asyut city", OSM + "way/94168759"),
    "mostorod":    (31.2995361, 30.1429608, "Mostorod refining/petrochemical area, Qalyubia", OSM + "way/28830035"),
    "tebbin":      (31.2975165, 29.7758346, "El Tebbin power station, Helwan", OSM + "way/502404024"),
    "nac":         (31.7549459, 30.023829, "New Administrative Capital", OSM + "node/7152775457"),
    "amreya_dist": (29.8015842, 31.0121567, "Al Amreya district, west Alexandria", OSM + "way/750048825"),
    "sidikrir34":  (29.6581136, 31.0428256, "Sidi Krir 3&4 power station (InterGen)", OSM + "way/930414508"),
    "newdamietta": (31.667, 31.4368, "New Damietta industrial/urban zone (broad-area anchor)", "https://en.wikipedia.org/wiki/New_Damietta"),
    "segas":       (31.74732, 31.46872, "SEGAS / Damietta LNG plant, New Damietta", OSM + "way/232403505"),
    "wdgc":        (29.8429334, 31.0093571, "GASCO Western Desert Gas Complex (WDGC), Amreya", ""),
    "merghem":     (29.8260893, 31.0600318, "Merghem industrial zone (GASCO Amerya LPG plant area), Alexandria", OSM + "way/744666834"),
    "edfu_sugar":  (32.8523728, 25.0432598, "Edfu sugar-factory village (مصنع السكر بادفو), Aswan", OSM + "node/13622439309"),
    "abumadi":     (31.3667, 31.4133, "Abu Madi gas field / treatment plant, Dakahlia", GEONAMES_ABUMADI),
    "talkha":      (31.39211, 31.06225, "Talkha distribution station / Talkha CCGT, Dakahlia", "https://globalenergyobservatory.org/geoid/5649"),
    "eltina_stn":  (32.3075, 31.0425, "El-Tina station (محطة التينة), El-Tina plain", OSM + "node/768596447"),
    "ayounmoussa": (32.5969, 29.9124, "Ayoun Moussa steam power station, Suez/Sinai", OSM + "way/210209240"),
    "elgamil":     (32.2025, 31.2844, "El Gamil (Al Gamil), west Port Said", OSM + "node/768598442"),
    "abuqir":      (30.0641979, 31.3203016, "Abu Qir, Alexandria", OSM + "node/332504177"),
    "idku":        (30.2985965, 31.3057473, "Idku (Edku), Beheira", OSM + "node/1039327711"),
    "portsaid":    (32.305505, 31.263235, "Port Said", OSM + "node/27564975"),
    # internal anchors, read off GEM's own applied route geometry (never a [ref])
    "eltina_gem":  (32.3000, 31.2502, "El Tina gas-grid node (GEM-internal anchor: start of the applied P3343/P3366 routes)", ""),
    "mitnema":     (31.2283, 30.1478, "Mit Nema, Qalyubia (GEM-internal anchor: end of the applied P3343 route)", ""),
    "amreya_plant": (29.8648, 31.0948, "Amreya oil & gas plant (GEM-internal anchor: end of the applied P0474 route)", ""),
    "cairoring":   (31.3077, 29.8223, "Cairo Ring gas node (GEM-internal anchor: start of the applied P8017 route)", ""),
    "svt_edfu":    (32.56065, 24.83748, "South Valley trunk nearest-approach point off Edfu (GEM-internal anchor: point on the applied P6702 route)", ""),
}

VLOW = "very low (straight line/schematic)"

# pid, start-key, end-key, extra note
CANDIDATES = [
    # ---- carried forward from the 2026-08-07 pass, geometry unchanged --------
    ("P8050", "rashid", "abuhummus",
     "Carried forward from the 2026-08-07 pass unchanged. OPEN: duplicate-check against "
     "P7567 'Idku-Abu Hummus Gas Pipeline' (30 km, 42 in) — EGAS 2018's prose item "
     "'Ezdwaj Edku / Abu Houmas 30 km - 42\"' matches P7567, and on the GASCO grid map "
     "'Rosetta' is an offshore field whose tie-back lands at Idku, not the Delta town of Rashid."),
    ("P8051", "abuhummus", "nubaria",
     "Carried forward from the 2026-08-07 pass unchanged. OPEN (value, not geometry): the "
     "GASCO map's 65 km label reads 42\" against the sheet's 32\" — probable mis-pairing "
     "inside the stacked Abu Homos label bundle. Routes to Update."),
    ("P8052", "zuweid", "sinaicement",
     "Carried forward from the 2026-08-07 pass. The 2026-08-10 'wrong cement plant' finding "
     "is WITHDRAWN: the GASCO Nov-2007 grid sheet's own captions georeference to "
     "33.82,30.71-30.76, i.e. the Jabal Lubna cluster OSM maps at 33.77-33.85,30.70-30.72 — "
     "the same anchor already used here. OPEN: the 45 km sheet/map length is shorter than the "
     "63 km chord from Sheikh Zuweid town, so the real take-off is a tie-in on the coastal "
     "trunk nearer El-Arish, not the town centre. Geometry is schematic; length unresolved."),
    ("P8053", "sinaicement", "milcement",
     "Carried forward from the 2026-08-07 pass. Do-not-apply status LIFTED — it rested only on "
     "P8052's withdrawn anchor finding. 7.4 km chord vs 16 km sheet (2.2x winding), possible."),
    ("P8054", "dahshur_v", "elwasta",
     "Carried forward from the 2026-08-07 pass unchanged. Length corroborated twice "
     "(EGAS 2018 68.5 km; petro-news 65 km / 36 in)."),
    ("P8056", "abuqurqas", "asyut",
     "Carried forward from the 2026-08-07 pass unchanged. Announced twin of the operating "
     "P6700 (Abu Qurqas-Asyut, 150 km, high route) — same corridor, same 1.5x winding factor. "
     "Cross-reference the two rows in RouteNotes."),
    ("P8057", "mostorod", "tebbin",
     "Carried forward from the 2026-08-07 pass. OPEN: 40.8 km chord vs the 25 km the sheet AND "
     "the GASCO map label both state — a source-vs-geography conflict, not a transcription "
     "slip. Also: EndPrefecture/District wrongly repeats 'Mostorud'; the Arabic name names "
     "El Tebbin. Apply only once the length question is settled."),
    ("P8058", "dahshur_m", "nac",
     "Carried forward from the 2026-08-07 pass unchanged. The row was renamed on the sheet "
     "2026-08-10 to the New-Administrative-Capital reading this geometry assumes."),
    ("P8059", "amreya_dist", "sidikrir34",
     "Carried forward from the 2026-08-07 pass. OPEN, and the open question is OUR endpoints, "
     "not the length: no '7.5 km' label exists anywhere on the georeferenced GASCO sheet (the "
     "earlier 7.5-misread reading is withdrawn), so 75 km stands and a 14.1 km Amreya -> Sidi "
     "Krir chord is 5.3x too short. This straight line gets the row off 'no route' but the "
     "west-Alexandria end is almost certainly not Sidi Krir 3&4. Apply only if a schematic "
     "placeholder is wanted ahead of the real corridor."),

    # ---- retries of long-standing ROUTE_PARTIALs ----------------------------
    ("P6033", "newdamietta", "segas",
     "Retry of a three-pass ROUTE_PARTIAL. No national-grid take-off station for the SEGAS "
     "feed is independently named anywhere, so the start is a broad-area New Damietta anchor; "
     "at 'very low' that is what the tier is for. End is facility-precise."),
    ("P6704", "wdgc", "merghem",
     "Retry of a three-pass ROUTE_PARTIAL. Both anchors are zone-level; the 5.87 km chord "
     "marginally exceeds the 5 km sheet length, which means the Amerya LPG plant sits in the "
     "southern part of the Merghem zone. Direction and corridor are right; endpoints are not "
     "facility-precise. Start anchor is Wikimapia-derived (tier low) — not carried as a [ref]."),
    ("P7588", "edfu_sugar", "svt_edfu",
     "Retry of a three-pass ROUTE_PARTIAL. The spur's trunk-side tie-in is taken off GEM's own "
     "applied South Valley route (P6702) as an internal anchor — geometry only, not a source. "
     "37.3 km chord against the sheet's 37 km."),
    ("P8022", "abumadi", "talkha",
     "Retry of a three-pass ROUTE_PARTIAL — resolved by the GeoNames gasfield entry "
     "'Haql Ghaz Abu Madi' (Dakahlia), corroborated within 1.3 km by an unnamed OSM "
     "industrial polygon (way 690415406). 39.1 km chord vs the 40 km sheet length."),
    ("P8023", "abumadi", "talkha",
     "Retry of a three-pass ROUTE_PARTIAL; same corridor as P8022 (parallel line, 22 in vs "
     "12 in). Same anchors, same 39.1 km chord vs 40 km."),
    ("P8026", "eltina_stn", "ayounmoussa",
     "Retry of a ROUTE_PARTIAL. Start is the only independently geocodable place named "
     "'El-Tina' (an OSM station node tagged Port Said governorate) — the EIA source that "
     "establishes El-Tina East as the Sinai-side trunk origin gives no coordinate, so the "
     "start may be on the wrong canal bank. End is facility-precise."),
    ("P8035", "elgamil", "eltina_stn",
     "Retry of a ROUTE_PARTIAL. NOTE: the 2026-07 pass mis-resolved this row to P8013's "
     "Petreco/Ras Bakr endpoints — that is withdrawn; this is the Port Said UGDC line. "
     "UGDC's plant is anchored to El Gamil, west Port Said. 28.7 km chord vs 40 km sheet."),
    ("P8049", "abumadi", "elgamil",
     "Never previously routed. Second segment of the Nooros-Abu Madi-El Gamil line "
     "(P3932 is the Nooros-Abu Madi segment). 80.9 km chord vs the 92 km sheet length."),
    ("P8063", "eltina_gem", "mitnema",
     "Never previously routed. Parallel first line of the corridor GEM already maps at "
     "'medium' for its twin P3343 'El Tina Gas Pipeline II' (same El Tina-Mit Nema segment "
     "name, 170 km vs 167 km); both anchors are read off that applied route as internal "
     "tie-ins. 160 km chord vs 167 km. Consider reusing P3343's mapped geometry instead of "
     "this straight line if a human review agrees the two lines share one corridor."),
    ("P8064", "wdgc", "abuqir",
     "Never previously routed. 40.8 km chord vs the 45 km sheet length."),
    ("P8065", "amreya_plant", "wdgc",
     "Never previously routed. The two 'Ameriya' nodes GEM already uses are 10.2 km apart — "
     "the Amreya oil & gas plant (end of the applied P0474 route) and the WDGC (start of the "
     "applied P3934/P8032 routes); this line runs between them. 10.2 km chord vs 15 km. "
     "Supporting but not positional: the GASCO sheet carries a '24\" 15km' label matching this "
     "row on BOTH bore and length — it sits in the stacked Abu Homos bundle ~25 km east, i.e. "
     "beyond the sheet's ~14 km median feature offset, so read it as an attribute match."),
    ("P8066", "amreya_plant", "wdgc",
     "Never previously routed; parallel to P8065 (12 in vs 24 in). Same anchors, 10.2 km "
     "chord vs 14.5 km. Same caveat as P8065: the sheet's '12\" 14.5km' label matches this row "
     "on bore and length but sits in the Abu Homos bundle, so it corroborates the pair of rows, "
     "not their position."),
    ("P8067", "idku", "abuhummus",
     "Never previously routed. Parallel first line of P7567 'Idku-Abu Hummus Gas Pipeline II' "
     "(30 km, medium route applied). 22.2 km chord vs 27 km. OPEN: check P8067/P7567/P8050 "
     "are three real lines and not one line entered three times."),
    ("P8020", "cairoring", "portsaid",
     "Never previously routed. OPEN and material: the 186 km chord between GEM's own Cairo "
     "Ring node (start of the applied P8017 route) and Port Said is far longer than the 130 km "
     "the sheet states, so either the length is wrong or 'Cairo Ring' here denotes a different, "
     "more northerly node than P8017's. Geometry is directionally right, length unresolved."),
]

# South Valley network row — handled separately (merge of its own six segments)
NETWORK_MERGE = {
    "P0477": ["P6697", "P6698", "P6699", "P6700", "P6701", "P6702"],
}

PARTIALS = {
    "P7326": "oil, 'El Minya Connection' segment (20 km, 12 in) — no endpoint named on the row "
             "and no facility identified at either end of the connection.",
    "P7589": "Faramid field (Western Desert) — the only name-matched end anchor (Badr El Din) "
             "is 159 km from the derived field centroid against a 38 km sheet length. Both "
             "ends are concession-scale at best; a straight line between them would be wrong, "
             "not merely imprecise.",
    "P7605": "'Wanda Gas Pipeline' (Western Desert, 10 km) — neither endpoint named on the row "
             "and no Wanda field/facility geocodable in any public gazetteer.",
    "P8001": "NORPETCO-Abu Gharadig (27 km) — end anchored (GeoNames Abu al Gharadiq oilfield) "
             "but no NORPETCO facility is geocodable; a single anchor cannot make a line.",
    "P8003": "'Fayoum-Giza Gas Pipeline' (27 km, 24 in) — EGAS 2018 lists the project but names "
             "no endpoints, and Fayoum city to Giza is ~80 km, so the row's two governorate "
             "names cannot be used as the anchor pair.",
    "P8005": "SUMED (6.1 km) — start is the SUMED Ain Sokhna terminal; nothing names the "
             "grid-side end of the 6.1 km spur.",
    "P8006": "Sonker phase 1 (9 km) — start is the Sonker Ain Sokhna terminal; the grid-side "
             "end is unnamed in every source found.",
    "P8007": "Sonker phase 2 (7 km) — same as P8006.",
    "P8008": "'Sinia Gas Pipeline 1' (15.5 km, 36 in) — no endpoint, city or facility named "
             "anywhere on the row or in any source; 'Sinia' is the governorate only.",
    "P8009": "'Sinia Gas Pipeline 2' (27 km, 36 in) — same as P8008.",
    "P8055": "Trans-Sinai II (28 km duplication) — GASCO's own deck gives the length, diameter "
             "and cost but no endpoints for the duplicated stretch. Also carries two name "
             "defects (see the 2026-08-07 escalation, Finding 4).",
}


def build(pid, s_key, e_key, note, commodity="gas"):
    slon, slat, sname, sref = A[s_key]
    elon, elat, ename, eref = A[e_key]
    cmd = [
        sys.executable, str(REPO / "scripts/build_route_candidate.py"),
        "--pid", pid, "--commodity", commodity, "--staging", str(HERE),
        "--method", "endpoints",
        "--start", f"{slon},{slat}", "--end", f"{elon},{elat}",
        "--start-name", sname, "--end-name", ename,
        "--accuracy", VLOW, "--notes", note,
    ]
    if sref:
        cmd += ["--start-ref", sref]
    if eref:
        cmd += ["--end-ref", eref]
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    ok = r.returncode == 0
    print(f"{'ok ' if ok else 'FAIL'} {pid}  {s_key} -> {e_key}")
    if not ok:
        print(r.stdout[-2000:] or "", r.stderr[-2000:] or "")
    else:
        for line in r.stdout.splitlines():
            if any(k in line for k in ("length", "ratio", "gate", "PASS", "FAIL", "WARN")):
                print("      " + line.strip())
    return ok


def build_network_merge(pid, segs):
    """P0477: the parent network row's geometry IS its segments' applied routes."""
    feats = []
    for s in segs:
        p = ROUTES / f"{s}.geojson"
        d = json.loads(p.read_text())
        feats.extend(d["features"] if d.get("type") == "FeatureCollection" else [d])
    merged = HERE / "inputs"
    merged.mkdir(exist_ok=True)
    out = merged / f"{pid}_merged_segments.geojson"
    out.write_text(json.dumps({"type": "FeatureCollection", "features": feats}) + "\n")
    cmd = [
        sys.executable, str(REPO / "scripts/build_route_candidate.py"),
        "--pid", pid, "--commodity", "gas", "--staging", str(HERE),
        "--method", "gis", "--geom", str(out), "--accuracy", "high",
        "--routenote", "CB: route merged from the row's own segment routes",
        "--notes",
        "CONVENTION QUESTION, not a research finding. P0477 is the South Valley "
        "SYSTEM/NETWORK row (930 km) and its six segments (P6697 90, P6698 28, P6699 150, "
        "P6700 150, P6701 121, P6702 390 km) already carry applied 'high' routes summing to "
        "929 km. This candidate is simply those six geometries merged. 15 network rows "
        "tracker-wide already carry routes (4 high, 3 medium, 2 very high, 1 low), so this is "
        "not unprecedented — but whether GEM wants parent network rows routed at all is "
        "Baird's call, not ours. Do not apply without that decision.",
    ]
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    print(f"{'ok ' if r.returncode == 0 else 'FAIL'} {pid}  merge of {', '.join(segs)}")
    if r.returncode:
        print(r.stdout[-2000:], r.stderr[-2000:])
    return r.returncode == 0


def main():
    n = 0
    for pid, s, e, note in CANDIDATES:
        n += build(pid, s, e, note)
    for pid, segs in NETWORK_MERGE.items():
        n += build_network_merge(pid, segs)
    print(f"\n{n} candidates staged into {HERE.name}")
    print(f"{len(PARTIALS)} rows stay ROUTE_PARTIAL: {', '.join(sorted(PARTIALS))}")
    (HERE / "partials.json").write_text(json.dumps(PARTIALS, indent=1) + "\n")


if __name__ == "__main__":
    main()
