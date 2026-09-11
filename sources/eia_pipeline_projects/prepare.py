"""Re-derive the EIA Natural Gas Pipeline Projects tables from the tracked raw/ workbooks.

EIA publishes the workbook quarterly-ish (29 releases, May 2018 -> Aug 2026 as of 2026-09-10).
Each release has a current-projects sheet and a historical sheet; the header is the row whose
cells include "Project Name". Output (gitignored, regenerable):

  data/eia_projects_long.csv    one line per (release, sheet, project row) — every value as published
  data/eia_projects_latest.csv  one line per project, latest release's values + status/value history

raw/vintages.csv (tracked) records each file's release, origin URL, bytes and sha256.

usage: python sources/eia_pipeline_projects/prepare.py [--manifest-only]
"""
import argparse
import csv
import datetime as dt
import hashlib
import re
import sys
from pathlib import Path

import openpyxl

HERE = Path(__file__).resolve().parent
RAW, DATA = HERE / "raw", HERE / "data"
BASE_URL = "https://www.eia.gov/naturalgas/pipelines/"
MONTHS = {m: i for i, m in enumerate(
    "jan feb mar apr may jun jul aug sep oct nov dec".split(), 1)}


def release_of(name: str) -> str:
    """'EIA-NaturalGasPipelineProjects_July2019.xlsx' -> '2019-07'; undated -> 'current'."""
    m = re.search(r"Projects_?([A-Za-z]+)(\d{4})\.xlsx$", name)
    if not m:
        return "current"
    return f"{m.group(2)}-{MONTHS[m.group(1)[:3].lower()]:02d}"


def snake(h) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(h).strip().lower()).strip("_")


def cell(v):
    if isinstance(v, dt.datetime):
        return v.date().isoformat()
    if isinstance(v, str):
        return v.strip()
    return "" if v is None else v


def read_release(path: Path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    for ws in wb.worksheets:
        rows = ws.iter_rows(values_only=True)
        header, hdr_row = None, 0
        for i, r in enumerate(rows, 1):
            if r and any(str(c).strip() == "Project Name" for c in r if c is not None):
                header, hdr_row = [snake(c) if c is not None else "" for c in r], i
                break
            if i > 10:
                break
        if not header:
            continue
        kind = "historical" if "historical" in ws.title.lower() else "current"
        for j, r in enumerate(rows, hdr_row + 1):
            rec = {h: cell(v) for h, v in zip(header, r) if h}
            if not str(rec.get("project_name", "")).strip():
                continue
            yield ws.title, kind, j, rec


def norm_key(rec) -> str:
    name = re.sub(r"[^a-z0-9]+", " ", str(rec.get("project_name", "")).lower()).strip()
    op = re.sub(r"[^a-z0-9]+", " ", str(rec.get("pipeline_operator_name", "")).lower()).strip()
    return f"{name}|{op}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest-only", action="store_true")
    a = ap.parse_args()

    files = sorted(RAW.glob("EIA-NaturalGasPipelineProjects*.xlsx"))
    if not files:
        sys.exit(f"no workbooks in {RAW}")
    man = []
    for f in files:
        b = f.read_bytes()
        man.append({"file": f.name, "release": release_of(f.name), "url": BASE_URL + f.name,
                    "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()})
    man.sort(key=lambda m: (m["release"] == "current", m["release"]))
    with open(RAW / "vintages.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(man[0]))
        w.writeheader()
        w.writerows(man)
    dated = [m for m in man if m["release"] != "current"]
    cur = next((m for m in man if m["release"] == "current"), None)
    if cur:
        twin = [m["release"] for m in dated if m["sha256"] == cur["sha256"]]
        print(f"undated current workbook = release {twin[0] if twin else '(no dated twin — a newer release?)'}")
    print(f"{len(dated)} dated releases: {dated[0]['release']} .. {dated[-1]['release']}")
    if a.manifest_only:
        return

    DATA.mkdir(exist_ok=True)
    long_rows, cols = [], ["release", "file", "sheet", "sheet_kind", "excel_row", "project_key"]
    for m in dated:  # the undated file is a copy of the newest release — never double-count it
        n = 0
        for sheet, kind, j, rec in read_release(RAW / m["file"]):
            for k in rec:
                if k not in cols:
                    cols.append(k)
            long_rows.append({"release": m["release"], "file": m["file"], "sheet": sheet,
                              "sheet_kind": kind, "excel_row": j, "project_key": norm_key(rec), **rec})
            n += 1
        print(f"  {m['release']}  {n:5d} project rows  {m['file']}")
    with open(DATA / "eia_projects_long.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(long_rows)

    by = {}
    for r in long_rows:
        by.setdefault(r["project_key"], []).append(r)
    keep = ["project_name", "pipeline_operator_name", "project_type", "status", "completed_date",
            "year_in_service_date", "state_s", "beg_state", "end_state", "cost_millions", "miles",
            "additional_capacity_mmcf_d", "pipeline_diameter_inches", "pipeline_type", "authority",
            "docket_number", "demand_served", "website"]
    latest = []
    for key, rs in by.items():
        rs.sort(key=lambda r: (r["release"], r["sheet_kind"] == "current"))
        last = rs[-1]
        rec ={"project_key": key, "first_release": rs[0]["release"], "last_release": last["release"],
               "last_file": last["file"], "last_sheet": last["sheet"], "last_excel_row": last["excel_row"],
               "n_releases": len({r["release"] for r in rs})}
        rec.update({k: last.get(k, "") for k in keep})
        for f in ("status", "year_in_service_date", "cost_millions", "miles",
                  "additional_capacity_mmcf_d", "pipeline_diameter_inches"):
            rec[f"{f}_history"] = _hist(rs, f)
        rec["notes_latest"] = last.get("notes", "") or last.get("project_notes", "")
        latest.append(rec)
    latest.sort(key=lambda r: r["project_key"])
    with open(DATA / "eia_projects_latest.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(latest[0]))
        w.writeheader()
        w.writerows(latest)
    print(f"wrote {len(long_rows)} long rows, {len(latest)} distinct projects -> {DATA}")


def _hist(rs, f) -> str:
    """Value changes across releases, e.g. 'Applied@2018-05 > Approved@2019-01 > Completed@2020-01'."""
    out, prev = [], object()
    for r in rs:
        v = str(r.get(f, "")).strip()
        if v and v != prev:
            out.append(f"{v}@{r['release']}")
            prev = v
    return " > ".join(out)


if __name__ == "__main__":
    main()
