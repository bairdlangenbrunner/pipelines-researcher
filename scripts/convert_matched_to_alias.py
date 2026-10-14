#!/usr/bin/env python3
"""Turn `matched_existing` discovery candidates into alias fills (Baird 2026-10-14).

A candidate that is probably part of, or another name for, a pipeline GEM already tracks is a
data-enrichment finding, never a "new row". This moves each such record out of a staging dir's
`staged_new.json` `candidates` (kept under `converted_to_alias` for audit) and stages it as a ref-less
FILL on the matched row's `OtherEnglishNames` (`OtherLanguageAlternativePipelineNames` for a
non-English name) in that dir's `staged_resolutions.json`. The existing cell text is kept and the new
name appended, semicolon-separated. The note says plainly that the match is a judgment and there is
a chance it is a different pipeline. Idempotent: converted records are no longer candidates.

    python scripts/convert_matched_to_alias.py            # dry run
    python scripts/convert_matched_to_alias.py --apply
"""
import argparse, csv, glob, json, re, sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNAP = ROOT / "data" / "GGIT_gas_snapshot_20261014.csv"
OEN, OLA = "OtherEnglishNames", "OtherLanguageAlternativePipelineNames"

# (matched PID, candidate name) -> (column, name(s) to add, semicolon-joined) ; None = the row already
# carries that name, so there is nothing to add and the card just goes away
ALIAS = {
    ("P3951", "Iran-UAE (Salman-Sharjah) Gas Pipeline"): (OEN, "Iran-UAE (Salman-Sharjah) Gas Pipeline"),
    ("P3895", "Far Eastern Route Russian branch (SKhV to Chinese border, Lesozavodsk district)"): (OEN, "Far Eastern Route (Russian section); Primorye-China Gas Pipeline"),
    ("P6535", "Eastern Gas Supply System (VSG) western section, Yamal-HMAO-Tomsk-Kuzbass-Krasnoyarsk-Irkutsk"): (OEN, "Eastern Gas Supply System (Vostochnaya Sistema Gazosnabzheniya, VSG) western section"),
    ("P6535", "Eastern Gas Supply System (VSG) umbrella, Yamal-Nadym-Purovsky-Noyabrsk-...-Khabarovsk"): (OEN, "Eastern Gas Supply System (Vostochnaya Sistema Gazosnabzheniya, VSG)"),
    ("P8087", "Russia-Kazakhstan Gas Pipeline (Tyumen region to Ishim-Astana border section)"): (OEN, "Russia-Kazakhstan Gas Pipeline (Tyumen-North Kazakhstan)"),
    ("P4109", "Ust-Luga Gas Pipeline Branch (Kohtla-Yarve-Leningrad tie-in to GRS Ust-Luga)"): (OEN, "Ust-Luga Gas Pipeline Branch"),
    ("P3070", "Izborsk-Värska-Tartu Gas Pipeline"): (OEN, "Izborsk-Tartu-Rakvere Gas Pipeline; Izborsk-Värska-Tartu Gas Pipeline"),
    ("P2380", "Yakhroma-Noginsk Gas Pipeline (Moscow Oblast)"): (OEN, "Yakhroma-Noginsk Gas Pipeline"),
    ("P4013", "Gas pipeline-branch to GRS Breytovo (Borok-Breytovo)"): (OEN, "Gas pipeline-branch to GRS Breytovo"),
    ("P2387", "Shebelinka-Belgorod-Kursk-Bryansk gas pipeline, Belgorod bypass (relocation outside city)"): (OEN, "ShBKB"),
    ("P2343", "Nevinnomyssk-Mozdok Gas Pipeline (second string)"): (OEN, "Nevinnomyssk-Mozdok Gas Pipeline"),
    ("P5989", "Berdyansk-Melitopol Gas Pipeline"): (OEN, "Berdyansk-Melitopol Gas Pipeline"),
    ("P5517", 'МГ "Омск-Новосибирск"'): (OLA, 'МГ "Омск-Новосибирск"'),
    ("P2335", "Ленинград — Выборг — Госграница 1"): (OLA, "Ленинград — Выборг — Госграница 1"),
    ("P2313", "Gryazovets-Vyborg loops on the Gryazovets-Volkhov section (2017 NS2-capacity project)"): (OEN, "Gryazovets-Vyborg loops (Gryazovets-Volkhov section)"),
    ("P2383", "Саратов — Горький"): (OLA, "Саратов — Горький"),
    ("P0788", "Transbalkanskii"): (OEN, "Trans-Balkan Gas Pipeline (Russian section); Transbalkanskii"),
    ("P0793", "Ставрополь — Москва 2"): (OLA, "Ставрополь — Москва 2"),
    ("P0732", "White Stream Gas Pipeline (GulfPub seed 1527)"): None,
    ("P2948", "Romania-Ukraine Mediesu Aurit-Tekovo interconnector capacity project"): (OEN, "Mediesu Aurit-Tekovo Gas Pipeline"),
    ("P3933", "Trans-Balkan Pipeline, Isaccea-Orlovka Ukrainian leg"): (OEN, "Trans-Balkan Pipeline, Isaccea-Orlovka Ukrainian leg"),
    ("P1465", "Chernihiv-Boyarka (GulfPub seed 963)"): (OEN, "Chernihiv-Boyarka Gas Pipeline"),
    ("P2008", "TEMAX/TIME III Expansion"): (OEN, "TEMAX and TIME III Project"),
    ("P3221", "SCG Pipeline Project (Port Wentworth to Jasper County)"): (OEN, "SCG Pipeline"),
    ("P0176", "Cove Point Pipeline"): (OEN, "Cove Point Pipeline"),
    ("P0261", "Appalachian Lease Project (TEAL) Phase 2"): (OEN, "Appalachian Lease Project (TEAL) Phase 2"),
    ("P2518", "Interconnect Pipeline Project"): (OEN, "Interconnect Pipeline Project"),
    ("P2622", "Supply Header Project"): (OEN, "Supply Header Project"),
    ("P0283", "Cheniere Southern Trail Pipeline"): (OEN, "Cheniere Southern Trail Pipeline"),
    ("P5113", "DTE LEAP Project"): (OEN, "DTE LEAP Project"),
    ("P4039", "FGT Phase IV Project"): (OEN, "FGT Phase IV Project"),
    ("P4034", "FGT Phase VI Project"): (OEN, "FGT Phase VI Project"),
    ("P2547", "Index 99 Expansion Project"): (OEN, "Index 99 Expansion Project"),
    ("P5823", "Northern Louisiana Expansion (Winnsboro Ext)"): (OEN, "Northern Louisiana Expansion (Winnsboro Extension)"),
    ("P3158", "Dakota Natural Gas Pipeline"): (OEN, "Dakota Natural Gas Pipeline"),
    ("P2099", "Northern Border Chicago Project (Harper extension, Manhattan extension, Monchy expansion)"): (OEN, "Northern Border Chicago Project"),
    ("P2578", "Northern Lights 2019"): (OEN, "Northern Lights 2019"),
    ("P0255", "Spire St. Louis Pipeline (Laclede Lateral)"): (OEN, "Spire St. Louis Pipeline; Laclede Lateral"),
    ("P2499", "Sendero Carlsbad Gateway Project"): (OEN, "Sendero Carlsbad Gateway Project"),
    ("P2617", "South Mainline Expansion Project"): (OEN, "South Mainline Expansion Project"),
    ("P3682", "Whislter Pipeline Midland Basin Expansion"): (OEN, "Whistler Pipeline Midland Basin Expansion; Whistler Martin County Lateral"),
    ("P6899", "Overthrust Wamsutter Expansion"): (OEN, "Overthrust Wamsutter Expansion"),
    ("P7856", "Paiute North Tahoe Lateral"): (OEN, "Paiute North Tahoe Lateral"),
    ("P6898", "Questar Main Line 58 Expansion"): (OEN, "Questar Main Line 58 Expansion"),
    ("P7860", "Great Basin 2028 Expansion Project"): (OEN, "Great Basin 2028 Expansion Project"),
    ("P0205", "Iroquois Eastchester Extension"): (OEN, "Iroquois Eastchester Extension; Eastchester Extension"),
    ("P0246", "Entrega Gas Pipeline"): (OEN, "Entrega Gas Pipeline"),
    ("P0208", "KM KN Interstate Pony Express"): (OEN, "KM KN Interstate Pony Express"),
    ("P0207", "KR Mainline 2001 System Expansion"): (OEN, "KR Mainline 2001 System Expansion"),
    ("P2553", "Line 1600 Replacement Project"): (OEN, "Line 1600 Replacement Project"),
    ("P0212", "Maritimes & Northeast Phase II (ME)"): (OEN, "Maritimes & Northeast Phase II"),
    ("P7454", "Ninilchik Pipeline"): (OEN, "Ninilchik Pipeline"),
}
# P6119 (Karachaganak-Orenburg) is on the OIL tab, not in the gas snapshot: left as it is.


def load_rows():
    raw = list(csv.reader(open(SNAP, encoding="utf-8")))
    h = raw[2]
    ix = {c: h.index(c) for c in ("ProjectID", "PipelineName", "SegmentName", OEN, OLA)}
    out = {}
    for i, r in enumerate(raw):
        if i > 2 and len(r) > ix[OLA] and r[ix["ProjectID"]]:
            out[r[ix["ProjectID"]]] = {"sheet_row": i + 1, **{c: r[j] for c, j in ix.items()}}
    return out


def split(s):
    return [x.strip() for x in s.split(";") if x.strip()]


def merge(current, add):
    have = {x.lower() for x in split(current)}
    new = [x for x in split(add) if x.lower() not in have]
    return "; ".join(split(current) + new), new


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    rows = load_rows()
    ts = datetime.now().isoformat(timespec="seconds")
    total = {"converted": 0, "dropped_same_name": 0, "left": []}
    for f in sorted(glob.glob(str(ROOT / "batches/*/staging/*/staged_new.json"))):
        p = Path(f)
        d = json.loads(p.read_text(encoding="utf-8"))
        keep, moved, fills = [], [], {}
        for c in d.get("candidates", []):
            if c.get("class") != "matched_existing" or c.get("applied"):
                keep.append(c)
                continue
            pid, key = c.get("matched_project_id"), (c.get("matched_project_id"), c.get("name"))
            if key not in ALIAS or pid not in rows:
                total["left"].append(f"{pid} {c.get('name')} ({p.parent.name}): not in the gas snapshot or unmapped, left as is")
                keep.append(c)
                continue
            moved.append(c)
            spec = ALIAS[key]
            if spec is None:
                total["dropped_same_name"] += 1
                continue
            col, add = spec
            fl = fills.setdefault((pid, col), {"adds": [], "cands": []})
            fl["adds"] += split(add)
            fl["cands"].append(c)
        if not moved:
            continue
        recs = []
        for (pid, col), fl in fills.items():
            row = rows[pid]
            value, new = merge(row[col], "; ".join(fl["adds"]))
            if not new:
                total["dropped_same_name"] += len(fl["cands"])
                continue
            names = "; ".join(new)
            orig = " | ".join((c.get("researcher_notes") or "").strip() for c in fl["cands"] if c.get("researcher_notes"))
            tail = (" The cell already lists: " + row[col] + "." if row[col] else "")
            note = (f"Possible other name for {pid}, {row['PipelineName']}. A discovery search found a pipeline called "
                    f"\"{names}\" and judged it to be part of this row or another name for it. That is a judgment, and there is "
                    f"a chance it is a different pipeline, so check before accepting. Accepting adds the name to the "
                    f"{'other-language names' if col == OLA else 'other English names'} cell and changes nothing else.{tail} "
                    f"What the search found: {orig}")
            recs.append({
                "project_id": pid, "sheet_row": row["sheet_row"], "pipeline_name": row["PipelineName"],
                "segment_name": row["SegmentName"] or "nan", "ref_col": "", "value_cols": [col],
                "primary_value_col": col, "primary_value": value, "values": {col: value},
                "current_ref": "nan", "class_in": "FILL", "class_out": "REFS_ADDED", "tier": "medium",
                "independent": False, "source_language": "en", "proposed_refs": [],
                "verifications": [v for c in fl["cands"] for v in (c.get("verifications") or [])],
                "researcher_notes": note, "alias_of_match": True,
                "converted_from": [{"name": c.get("name"), "class": "matched_existing"} for c in fl["cands"]],
            })
        total["converted"] += len(recs)
        print(f"{p.parent.relative_to(ROOT / 'batches')}: {len(moved)} candidates -> {len(recs)} alias fills")
        if not a.apply:
            continue
        rp = p.parent / "staged_resolutions.json"
        if rp.exists():
            rd = json.loads(rp.read_text(encoding="utf-8"))
        else:
            sc = dict((d.get("meta") or {}).get("scope") or {})
            sc["csv"] = SNAP.name
            rd = {"meta": {"commodity": "gas", "mode": "update", "scope": sc, "generated": ts,
                           "qualifier": "alias-fills-from-matched-existing"}, "resolutions": []}
        rd["resolutions"] += recs
        rd["meta"]["n_fills"] = sum(1 for r in rd["resolutions"] if r.get("class_in") == "FILL")
        rp.write_text(json.dumps(rd, indent=1, ensure_ascii=False), encoding="utf-8")
        d["candidates"] = keep
        d.setdefault("converted_to_alias", []).extend(moved)
        cc = d.setdefault("meta", {}).get("class_counts", {})
        cc["matched_existing"] = sum(1 for c in keep if c.get("class") == "matched_existing")
        d["meta"]["n_candidates"] = len(keep)
        p.write_text(json.dumps(d, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(total, indent=1, ensure_ascii=False))
    if not a.apply:
        print("dry run; pass --apply")


if __name__ == "__main__":
    sys.exit(main())
