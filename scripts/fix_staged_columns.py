#!/usr/bin/env python3
"""Find and repair staged records that name a column the sheet does not have.

    python scripts/fix_staged_columns.py            # report only (exit 1 if anything is off)
    python scripts/fix_staged_columns.py --apply    # rewrite the staged files in place

A `values` key lands in a real cell, so a name that is not a sheet header (`ConstructionYear1`,
`LengthUnits`, `StartState`, `Operator1`) is a defect in the staged record (P0168, P4039, P4040,
Iraq P7459; found 2026-10-09). Known slips are renamed to the real header. A `value_cols` /
`primary_value_col` label that is only a ref-column stem (`Proposal`, `Construction`, `Length`)
is reset to the ref pair's real columns. Anything else off-schema is only reported, never guessed.
Files keep their own JSON formatting (indent 1; ensure_ascii as found).
"""
import argparse, csv, glob, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from merge_qc import load_sheet  # noqa: E402

RENAME = {  # known slips -> the real header (a None drops the key: no such column exists)
    "ConstructionYear1": "ConstructionYear", "ConstructionMonth1": "ConstructionMonth",
    "ProposalYear1": "ProposalYear", "ProposalMonth1": "ProposalMonth",
    "LengthUnits": "LengthKnownUnits", "Length": "LengthKnown",
    "StartState": "StartState/Province", "EndState": "EndState/Province",
    "Operator1": "Operator", "Operator1%": None,
}
FILES = ("staged_resolutions.json", "staged_new.json")


def newest(pattern):
    return sorted(glob.glob(str(ROOT / "data" / pattern)))[-1]


def headers(path, row):
    return [c for c in list(csv.reader(open(path)))[row] if c]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    snap = Path(newest("GGIT_gas_snapshot_2*.csv"))
    sheet = load_sheet({"csv": snap.name})
    cols = set(headers(snap, 2)) | set(headers(newest("GEM_operators_owners_snapshot_2*.csv"), 1))
    order = {c: i for i, c in enumerate(headers(snap, 2))}
    left, fixed = [], 0
    for f in sorted(glob.glob(str(ROOT / "batches/*-gas/staging/*/*.json"))):
        if Path(f).name not in FILES:
            continue
        text = Path(f).read_text()
        d = json.loads(text)
        recs = d.get("resolutions") if isinstance(d, dict) else d
        raw_unicode = any(ord(c) > 127 for c in text)
        changed = False
        for r in recs or []:
            if not isinstance(r, dict):
                continue
            where = f"{Path(f).parent.name} {r.get('project_id')} {r.get('ref_col')}"
            vals = r.get("values")
            if isinstance(vals, dict):
                for k in [k for k in vals if k not in cols]:
                    if k in RENAME and RENAME[k] not in vals:
                        new = RENAME[k]
                        v = vals.pop(k)
                        if new:
                            vals[new] = v
                        else:
                            r["researcher_notes"] = (r.get("researcher_notes") or "") + f" Dropped {k}={v!r}: no such column."
                        print(f"values   {where}: {k} -> {new}")
                        changed = True
                    else:
                        left.append(f"values {where}: {k!r}")
            pair = sheet.pairs.get(r.get("ref_col") or "") if sheet else None
            bad = [c for c in (r.get("value_cols") or []) if c not in cols]
            pbad = r.get("primary_value_col") and r["primary_value_col"] not in cols
            if bad or pbad:
                if pair and all(b in RENAME or b == (r.get("ref_col") or "").removesuffix(" [ref]") for b in bad):
                    # label what the record proposes; the whole pair only when it proposes nothing yet
                    proposed = [c for c in (vals or {}) if c in cols]
                    if bad:
                        r["value_cols"] = sorted(proposed or pair, key=lambda c: order.get(c, 999))
                    if pbad:
                        r["primary_value_col"] = (sheet.primary[r["ref_col"]] if not proposed or sheet.primary[r["ref_col"]] in proposed
                                                  else r["value_cols"][0])
                    print(f"labels   {where}: {bad or ''} {r.get('primary_value_col') if pbad else ''} -> {r['value_cols']}")
                    changed = True
                elif r.get("ref_col") in ("Operator [ref]",) and bad and set(bad) <= {"Operator1", "Operator1%"}:
                    r["value_cols"] = [("Operator" if c == "Operator1" else c) for c in r["value_cols"] if c != "Operator1%"]
                    if pbad:
                        r["primary_value_col"] = "Operator"
                    print(f"labels   {where}: Operator1/Operator1% -> Operator")
                    changed = True
                else:
                    left.append(f"labels {where}: {bad} {r.get('primary_value_col') if pbad else ''}")
        if changed:
            fixed += 1
            if a.apply:
                Path(f).write_text(json.dumps(d, indent=1, ensure_ascii=not raw_unicode) + ("\n" if text.endswith("\n") else ""))
    print(f"\n{fixed} file(s) {'rewritten' if a.apply else 'would change'}; {len(left)} left alone (report only):")
    for l in left:
        print("  ", l)
    sys.exit(1 if (left or (fixed and not a.apply)) else 0)


if __name__ == "__main__":
    main()
