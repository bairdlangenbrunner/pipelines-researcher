#!/usr/bin/env python3
"""Prep split/merged GulfPub trace geometries for the Egypt route-creation run.

All coordinates exit the recon-gulfpub-20260729 geometry sidecar verbatim (standing
rule 2 — nothing fabricated); this script only cuts one trace at an existing vertex
and merges others:

  - WDGP-N trunk (gulfpub:gas:463, Obaiyed field -> Ameriya Refinery, 322.5 km) is
    split at trunk vertex 28 — the vertex nearest (4.5 km) the Tarek Spur trace's
    junction endpoint (gulfpub:gas:462, Ras Kanayes 4 -> Tarek) — into:
      P3934 Tarek->Ameriya portion (~227 km; sheet 231 km, ratio 0.98)
      P6687 Obaiyed->Tarek portion (~95 km; sheet 41.5 km — ratio flag, see notes)
  - P7447 Denise system = merge of the four Denise-anchored traces
    (409 Denise-Port Said, 429 Akhen-Denise, 437 Denise-Wakar, 7072 Denise-El Gamil)
    as one MultiLineString (segments stay separate; nothing bridged).

Outputs land in prep_geoms/ next to this script.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SIDECAR = HERE.parent / "recon-gulfpub-20260729" / "geometry_sidecar.json"
OUT = HERE / "prep_geoms"
OUT.mkdir(exist_ok=True)

TAREK_SPLIT_VTX = 28  # trunk vertex nearest the gulfpub:gas:462 spur junction

sc = json.loads(SIDECAR.read_text())


def line(ref_id):
    g = sc[ref_id]
    if g["type"] == "LineString":
        return g["coordinates"]
    if g["type"] == "MultiLineString" and len(g["coordinates"]) == 1:
        return g["coordinates"][0]
    raise SystemExit(f"{ref_id}: expected a single LineString, got {g['type']}")


def write(name, geom, props):
    fc = {"type": "FeatureCollection",
          "features": [{"type": "Feature", "properties": props, "geometry": geom}]}
    (OUT / name).write_text(json.dumps(fc, indent=1))
    print("wrote", OUT / name)


trunk = line("gulfpub:gas:463")  # vertex 0 = Ameriya end, vertex 39 = Obaiyed end
# P3934 Tarek–Ameriya: junction vertex -> Ameriya end (inclusive of the junction vertex)
write("P3934_tarek_ameriya.geojson",
      {"type": "LineString", "coordinates": trunk[: TAREK_SPLIT_VTX + 1]},
      {"source_ref_id": "gulfpub:gas:463", "split": f"vertices 0..{TAREK_SPLIT_VTX} "
       "(Ameriya end -> Tarek junction, nearest vertex to gulfpub:gas:462 endpoint)"})
# P6687 Obaiyed spur/western portion: junction vertex -> Obaiyed end
write("P6687_obaiyed_tarek.geojson",
      {"type": "LineString", "coordinates": trunk[TAREK_SPLIT_VTX:]},
      {"source_ref_id": "gulfpub:gas:463", "split": f"vertices {TAREK_SPLIT_VTX}..39 "
       "(Tarek junction -> Obaiyed end)"})

denise = ["gulfpub:gas:409", "gulfpub:gas:429", "gulfpub:gas:437", "gulfpub:gas:7072"]
parts = []
for rid in denise:
    g = sc[rid]
    parts += [g["coordinates"]] if g["type"] == "LineString" else list(g["coordinates"])
write("P7447_denise_system.geojson",
      {"type": "MultiLineString", "coordinates": parts},
      {"source_ref_ids": denise, "note": "four Denise-anchored GulfPub traces merged "
       "as one system; gaps never bridged"})
