#!/usr/bin/env python3
"""Re-target the 19 ASB Iraq length records onto EDITABLE cells.

The original staging named `LengthKnownKm` on every record. That is a COMPUTED
column in the sheet (LengthKnown converted per LengthKnownUnits), so per CLAUDE.md
it must never be pasted over -- and for the six `mi`-unit rows the proposed edit
would have been reverted by the sheet's own formula on the next recalc, because
`LengthKnown` would still have held the ASB integer with LengthKnownUnits='mi'.

The two families need DIFFERENT edits:

  * 13 rows (P18xx/P22xx): LengthKnown holds the already-converted km and
    LengthKnownUnits='km'. Fix the NUMBER: LengthKnown -> the ASB figure.
  * 6 rows (P40xx): LengthKnown already holds the ASB figure verbatim and
    LengthKnownUnits='mi'. The number is RIGHT. Fix only the UNIT LABEL:
    LengthKnownUnits 'mi' -> 'km'. Leave LengthKnown untouched.

Idempotent: re-running on an already-corrected file changes nothing.
"""
import json
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[4]
STAGED = Path(__file__).resolve().parent / "staged_resolutions.json"
CSV = REPO / "data" / "GGIT_gas_snapshot_20260728.csv"

NOTE = (
    " || RE-TARGETED 2026-07-28: this record originally proposed a value for "
    "LengthKnownKm, which is a COMPUTED column (LengthKnown converted per "
    "LengthKnownUnits) and must never be pasted over. The editable cells are named "
    "above. {extra}"
)
EXTRA_MI = (
    "For this row the ingest never converted anything -- it wrote the ASB integer "
    "verbatim into LengthKnown and simply believed the column header, setting "
    "LengthKnownUnits='mi'. The sheet's own formula then produced the inflated km "
    "figure. So the ONLY edit needed is the unit label; changing the number would "
    "double-correct. (Had LengthKnownKm been pasted as proposed, the formula would "
    "have re-derived the wrong value on the next recalc and the fix would have "
    "silently reverted.)"
)
EXTRA_KM = (
    "For this row LengthKnown holds the already-converted kilometre figure with "
    "LengthKnownUnits='km', so the NUMBER is what must change; the unit label is "
    "already correct."
)


def main():
    df = pd.read_csv(CSV, header=2, low_memory=False)
    sheet = df.set_index("ProjectID")[["LengthKnown", "LengthKnownUnits", "LengthKnownKm"]].copy()
    # LengthKnownKm arrives as object (the sheet writes "--" for blanks)
    for c in ("LengthKnown", "LengthKnownKm"):
        sheet[c] = pd.to_numeric(sheet[c], errors="coerce")

    doc = json.loads(STAGED.read_text())
    n_mi = n_km = 0
    for r in doc["resolutions"]:
        pid = r["project_id"]
        if r.get("primary_value_col") != "LengthKnownKm":
            continue  # already re-targeted
        raw = r["values"]["LengthKnownKm"]
        cur_len = sheet.at[pid, "LengthKnown"]
        cur_unit = sheet.at[pid, "LengthKnownUnits"]
        cur_km = sheet.at[pid, "LengthKnownKm"]

        if cur_unit == "mi":
            n_mi += 1
            r["value_cols"] = ["LengthKnownUnits"]
            r["primary_value_col"] = "LengthKnownUnits"
            r["primary_value"] = "km"
            r["values"] = {"LengthKnownUnits": "km"}
            r["recommendation"] = (
                f"Set LengthKnownUnits 'mi' -> 'km'. LengthKnown={cur_len:g} is ALREADY the "
                f"ASB figure and must NOT be changed. This one-cell edit corrects the computed "
                f"LengthKnownKm from {cur_km:g} to {raw:g}."
            )
            extra = EXTRA_MI
        else:
            n_km += 1
            r["value_cols"] = ["LengthKnown"]
            r["primary_value_col"] = "LengthKnown"
            r["primary_value"] = raw
            r["values"] = {"LengthKnown": raw}
            r["recommendation"] = (
                f"Set LengthKnown {cur_len:g} -> {raw:g} (LengthKnownUnits stays 'km'). "
                f"Corrects the computed LengthKnownKm from {cur_km:g} to {raw:g}."
            )
            extra = EXTRA_KM

        r["current_length_known"] = None if pd.isna(cur_len) else float(cur_len)
        r["current_length_known_units"] = cur_unit
        r["researcher_notes"] = r["researcher_notes"] + NOTE.format(extra=extra)

    if n_mi or n_km:
        m = doc["meta"]
        m["note"] = (
            "Class defect: 19 Iraq gas rows misread the OPEC ASB length column, which is "
            "headed '(miles)' while the IRAQ block is tabulated in KILOMETRES. Staged as "
            "VALIDITY concerns (not fills) because each targets a populated, published "
            "value. TWO FAMILIES, TWO DIFFERENT ONE-CELL FIXES: 13 rows (P18xx/P22xx) hold "
            "the converted km in LengthKnown with units 'km' -> correct the NUMBER; 6 rows "
            "(P40xx) hold the ASB figure verbatim in LengthKnown with units 'mi' -> correct "
            "only the UNIT LABEL, never the number. Records were re-targeted 2026-07-28 off "
            "the computed LengthKnownKm column onto these editable cells. Memo: "
            "notes/escalation-2026-07-28-asb-iraq-length-units.md"
        )
        m["retargeted_utc"] = "2026-07-28"
        m["fix_families"] = {"LengthKnown (units already km)": n_km,
                             "LengthKnownUnits mi->km (number already correct)": n_mi}
        STAGED.write_text(json.dumps(doc, indent=1) + "\n")

    print(f"re-targeted: {n_km} LengthKnown-number rows, {n_mi} LengthKnownUnits-label rows")
    for r in doc["resolutions"]:
        print(f"  {r['project_id']:6s} {r['primary_value_col']:18s} -> {r['values']}")


if __name__ == "__main__":
    main()
