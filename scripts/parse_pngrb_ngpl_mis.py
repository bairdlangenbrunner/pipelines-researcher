#!/usr/bin/env python3
"""Parse PNGRB's monthly NGPL MIS report into a controlled JSON extraction.

The report (``https://pngrb.gov.in/data-bank/<YYYYMMDD>-NGPL-MIS-Report.pdf``) is the
Indian regulator's line-wise inventory of authorised natural-gas pipelines. Printed
page 2 ("PHYSICAL PROGRESS REPORT OF NATURAL GAS PIPELINE") is the only line-wise
table in the document; everything after it is aggregate or graphical. It carries, per
pipeline: entity, authorisation date, authorised length, authorised and
design/determined capacity, monthly gas supplied, capacity utilisation, **operating
length**, **under-construction length**, lowered/welded/hydrotested length, target
completion date and the states traversed.

Why this is the India analogue of Pakistan's SNGPL asset register (and better):

- it is the **regulator**, not the pipeline owner, so it is an origin independent of
  the GAIL / GSPL / IOCL annual reports GEM already cites;
- it carries **dates** (authorisation + target completion), which the SNGPL register
  did not; and
- its ``OPERATIONAL`` / ``PARTIALLY COMMISSIONED`` / ``UNDER CONSTRUCTION`` sections,
  with operating length *and* under-construction length on the same row, are the
  authoritative explanation of GEM's India operating/construction row pairs.

Scope caveat, and it matters: the line-wise table covers **common-carrier** pipelines
only. The page's grand totals are footnoted "Includes Common Carrier, Tie in &
Dedicated Pipelines", so dedicated lines (ONGC trunk lines, Duliajan-Numaligarh, …)
are inside the grand total but NOT itemised. The residual is reported as
``grand_total_residual_km`` rather than treated as a parse failure.

Extraction is by the PDF's own ruling lines (``vertical_strategy='lines'``), not by
text-column guessing, because the table genuinely contains a **merged numeric cell**:
S.No 3 (HVJ/GREP) and S.No 4 (DVPL-II/VDPL) share one set of numbers, so PNGRB reports
that system as one combined asset. Rows whose numeric cells are empty are emitted with
``shares_numbers_with`` pointing at the row that carries them and are grouped under
``composites``. A composite is a granularity difference from GEM, not an error.

The parse is only trusted if it reconciles to the report's own printed section TOTAL
rows; ``--check`` exits non-zero if any section is off. Verified against the
2026-05-31 edition: 37 pipelines, all three section totals exact.

Usage:
    python scripts/parse_pngrb_ngpl_mis.py --pdf <file.pdf> \
        --out batches/india-gas/staging/register-crosswalk/pngrb_ngpl_mis.json --check
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import pdfplumber

SECTIONS = {
    "OPERATIONAL COMMON CARRIER PIPELINE": "operational",
    "PARTIALLY COMMISSIONED COMMON CARRIER PIPELINE": "partially_commissioned",
    "UNDER CONSTRUCTION COMMON CARRIER PIPELINE": "under_construction",
}

# Column order on printed page 2. Index 2 is an unlabelled continuation of the
# pipeline-name cell, so the header has 17 slots for 16 real fields.
FIELDS = [
    "sno",
    "pipeline_name",
    "_name_cont",
    "entity",
    "authorisation_date",
    "authorised_length_km",
    "authorised_capacity_mmscmd",
    "determined_capacity_mmscmd",
    "gas_supplied_mmscmd",
    "capacity_utilisation_pct",
    "operating_length_km",
    "under_construction_length_km",
    "lowered_length_km",
    "welded_length_km",
    "hydrotested_length_km",
    "target_completion",
    "passing_through_states",
]

NUMERIC = {
    "authorised_length_km",
    "authorised_capacity_mmscmd",
    "determined_capacity_mmscmd",
    "gas_supplied_mmscmd",
    "capacity_utilisation_pct",
    "operating_length_km",
    "under_construction_length_km",
    "lowered_length_km",
    "welded_length_km",
    "hydrotested_length_km",
}

# Sums the report prints for itself; these are the reconciliation targets.
TOTAL_FIELDS = [
    "authorised_length_km",
    "authorised_capacity_mmscmd",
    "determined_capacity_mmscmd",
    "operating_length_km",
    "under_construction_length_km",
    "lowered_length_km",
    "welded_length_km",
    "hydrotested_length_km",
]


def _clean(cell: str | None) -> str:
    """Collapse the newlines pdfplumber leaves inside a wrapped cell."""
    if cell is None:
        return ""
    return re.sub(r"\s+", " ", cell.replace("\n", " ")).strip()


def _num(text: str) -> float | None:
    """Parse a table number. '-' and '' mean 'not applicable', not zero."""
    t = text.replace(",", "").strip()
    if t in {"", "-", "–", "—", "NA", "N/A"}:
        return None
    m = re.match(r"^-?\d+(?:\.\d+)?$", t)
    return float(m.group(0)) if m else None


def _find_table(page):
    tables = page.find_tables(
        table_settings={"vertical_strategy": "lines", "horizontal_strategy": "lines"}
    )
    if not tables:
        raise SystemExit("no ruled table found on the physical-progress page")
    return max(tables, key=lambda t: len(t.rows))


def _locate_page(pdf) -> int:
    """Find the physical-progress page by its heading, not a fixed page number."""
    for i, page in enumerate(pdf.pages):
        text = (page.extract_text() or "").upper()
        if "PHYSICAL PROGRESS REPORT OF NATURAL GAS PIPELINE" in text and (
            "OPERATIONAL COMMON CARRIER PIPELINE" in text
        ):
            return i
    raise SystemExit("could not locate the physical-progress page")


def parse(pdf_path: Path) -> dict:
    with pdfplumber.open(str(pdf_path)) as pdf:
        page_idx = _locate_page(pdf)
        page = pdf.pages[page_idx]
        rows = _find_table(page).extract()
        page_text = page.extract_text() or ""

    report_month = None
    m = re.search(r"NATURAL GAS PIPELINES:\s*MONTH OF\s*([A-Z]+\s*\d{4})", page_text.upper())
    if m:
        report_month = re.sub(r"\s+", " ", m.group(1)).title()

    grand = {}
    for label, key in (
        ("Total Authorised NGPL Length", "grand_total_authorised_km"),
        ("Total Operational NGPL Length", "grand_total_operational_km"),
    ):
        # The label itself ends in a year ("…as on March 2026*"), so skip to the
        # first number that is actually followed by the Km unit.
        gm = re.search(re.escape(label) + r"[^\n]*?([\d,]+)\s*Km", page_text, re.I)
        if gm:
            grand[key] = _num(gm.group(1))

    records: list[dict] = []
    printed_totals: dict[str, dict] = {}
    section = None
    order = 0

    for raw in rows:
        cells = [_clean(c) for c in raw]
        if not any(cells):
            continue
        head = cells[0].upper()

        if head in SECTIONS:
            section = SECTIONS[head]
            continue
        if head == "TOTAL" and section:
            vals = dict(zip(FIELDS, cells))
            printed_totals[section] = {f: _num(vals.get(f, "")) for f in TOTAL_FIELDS}
            continue
        if section is None or not re.match(r"^\d+$", cells[0]):
            continue

        vals = dict(zip(FIELDS, cells))
        name = " ".join(x for x in (vals["pipeline_name"], vals["_name_cont"]) if x)
        # PNGRB wraps names mid-token ("Kochi-Koottanad-Bangalore- Mangalore");
        # rejoin across a hyphen so the name matches cleanly downstream.
        name = re.sub(r"-\s+", "-", name).strip()

        order += 1
        rec = {
            "order": order,
            "section": section,
            "sno": int(vals["sno"]),
            "pipeline_name": name,
            "entity": vals["entity"] or None,
            "authorisation_date": vals["authorisation_date"] or None,
            "target_completion": vals["target_completion"] or None,
            "passing_through_states": vals["passing_through_states"] or None,
        }
        for f in NUMERIC:
            rec[f] = _num(vals.get(f, ""))
        rec["shares_numbers_with"] = None
        records.append(rec)

    # Merged numeric cells: a row with no authorised length and no entity is a
    # continuation of the preceding row's asset (PNGRB's HVJ/DVPL combined system).
    composites: list[dict] = []
    for i, rec in enumerate(records):
        if rec["authorised_length_km"] is None and rec["entity"] is None and i > 0:
            for prev in reversed(records[:i]):
                if prev["section"] == rec["section"] and prev["authorised_length_km"] is not None:
                    rec["shares_numbers_with"] = prev["sno"]
                    grp = next(
                        (
                            g
                            for g in composites
                            if g["section"] == prev["section"] and g["carrier_sno"] == prev["sno"]
                        ),
                        None,
                    )
                    if grp is None:
                        grp = {
                            "section": prev["section"],
                            "carrier_sno": prev["sno"],
                            "snos": [prev["sno"]],
                            "names": [prev["pipeline_name"]],
                            "authorised_length_km": prev["authorised_length_km"],
                            "operating_length_km": prev["operating_length_km"],
                        }
                        composites.append(grp)
                    grp["snos"].append(rec["sno"])
                    grp["names"].append(rec["pipeline_name"])
                    break

    # Reconcile our sums against the report's own printed TOTAL rows.
    recon = {}
    ok = True
    for section in SECTIONS.values():
        in_sec = [r for r in records if r["section"] == section]
        if not in_sec:
            continue
        block = {"rows": len(in_sec), "fields": {}}
        for f in TOTAL_FIELDS:
            got = sum(r[f] for r in in_sec if r[f] is not None)
            want = (printed_totals.get(section) or {}).get(f)
            match = want is not None and abs(got - want) <= max(1.0, abs(want) * 0.001)
            # The report rounds each printed cell, so allow 1 unit or 0.1%.
            block["fields"][f] = {
                "parsed": round(got, 2),
                "printed": want,
                "match": bool(match) if want is not None else None,
            }
            if want is not None and not match:
                ok = False
        recon[section] = block

    itemised_auth = sum(
        r["authorised_length_km"] for r in records if r["authorised_length_km"] is not None
    )
    itemised_op = sum(
        r["operating_length_km"] for r in records if r["operating_length_km"] is not None
    )

    return {
        "source": {
            "publisher": "Petroleum and Natural Gas Regulatory Board (PNGRB), Statistics Division",
            "document": "PNGRB MIS Report: NGPL — Physical Progress Report of Natural Gas Pipeline",
            "report_month": report_month,
            "pdf": pdf_path.name,
            "printed_page": 2,
            "coverage": "common-carrier NGPL only; dedicated and tie-in lines are in the "
            "grand totals but not itemised",
            "attribution": "Data submitted by Entities to PNGRB",
        },
        "grand_totals": grand,
        "itemised_totals": {
            "authorised_length_km": round(itemised_auth, 2),
            "operating_length_km": round(itemised_op, 2),
            "grand_total_residual_km": (
                round(grand["grand_total_authorised_km"] - itemised_auth, 2)
                if grand.get("grand_total_authorised_km")
                else None
            ),
        },
        "reconciliation": {"ok": ok, "sections": recon},
        "composites": composites,
        "records": records,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pdf", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero unless every printed section TOTAL reconciles",
    )
    args = ap.parse_args()

    data = parse(args.pdf)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    src = data["source"]
    print(f"wrote {args.out}")
    print(f"  {src['document']} — {src['report_month']}")
    print(f"  {len(data['records'])} pipelines, {len(data['composites'])} composite group(s)")
    for section, block in data["reconciliation"]["sections"].items():
        bad = [f for f, v in block["fields"].items() if v["match"] is False]
        state = "OK" if not bad else "MISMATCH: " + ", ".join(bad)
        print(f"  {section:24s} {block['rows']:2d} rows  {state}")
    it = data["itemised_totals"]
    gt = data["grand_totals"].get("grand_total_authorised_km")
    if gt and it["grand_total_residual_km"] is not None:
        print(
            f"  itemised authorised {it['authorised_length_km']:,.0f} km vs grand total "
            f"{gt:,.0f} km (residual {it['grand_total_residual_km']:,.0f} km = dedicated/tie-in)"
        )
    else:
        print(
            f"  itemised authorised {it['authorised_length_km']:,.0f} km "
            "(grand total not found on page — residual unknown)"
        )
    if args.check and not data["reconciliation"]["ok"]:
        print("FAIL: printed section totals did not reconcile", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
