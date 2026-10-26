#!/usr/bin/env python3
"""Which `proposed` rows are old enough for the 2-year (shelved) / 4-year (cancelled) dormancy rules?

Baird 2026-10-16 (P4449): a proposed row older than 2 years is checked for shelved + inferred,
older than 4 for cancelled + inferred. This lists every such row on the newest snapshots and
the staged status verdict (if any) already sitting on it, so a `confirm` or a missing verdict
on an aged proposed row is visible.

    python scripts/audit_proposed_age.py [--commodity gas|oil|both] [--country C] [--csv OUT]
"""
from __future__ import annotations

import argparse
import csv
import datetime
import glob
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
SNAP = {"gas": "GGIT_gas_snapshot_*.csv", "oil": "GOIT_oil_ngl_snapshot_*.csv"}


def newest(pattern: str) -> Path:
    return sorted((ROOT / "data").glob(pattern))[-1]


def year(v) -> int | None:
    try:
        return int(float(str(v).strip()))
    except ValueError:
        return None


def staged_verdicts() -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for f in glob.glob(str(ROOT / "batches/*/staging/*/rows/P*.json")):
        try:
            d = json.load(open(f))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(d, dict):
            continue
        for s in d.get("status_reviews") or []:
            if isinstance(s, dict):
                tag = f"{s.get('verdict')}->{s.get('proposed_status') or '-'} ({Path(f).parts[-4]}/{Path(f).parts[-3]})"
                out.setdefault(Path(f).stem, []).append(tag)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--commodity", default="both", choices=["gas", "oil", "both"])
    ap.add_argument("--country")
    ap.add_argument("--csv")
    a = ap.parse_args()
    this = datetime.date.today().year
    verdicts = staged_verdicts()
    rows = []
    for cm in (["gas", "oil"] if a.commodity == "both" else [a.commodity]):
        d = pd.read_csv(newest(SNAP[cm]), header=2, low_memory=False, keep_default_na=False, na_values=[])
        for _, r in d[d.Status == "proposed"].iterrows():
            if a.country and a.country.lower() not in str(r.get("CountriesOrAreas", "")).lower():
                continue
            py, sy = year(r.get("ProposalYear")), year(r.get("StartYear1"))
            age = this - py if py else None
            overdue = bool(sy and sy < this)
            if age is not None and age >= 4:
                rule = "cancelled-4yr"
            elif age is not None and age >= 2:
                rule = "shelved-2yr"
            elif age is None and overdue:
                rule = "no-proposal-year-start-overdue"
            else:
                continue
            rows.append({"commodity": cm, "ProjectID": r["ProjectID"], "name": r.get("PipelineName", ""),
                         "country": r.get("CountriesOrAreas", ""), "ProposalYear": py or "",
                         "StartYear1": sy or "", "rule": rule, "start_overdue": overdue,
                         "staged_status_verdicts": " | ".join(verdicts.get(r["ProjectID"], []))})
    df = pd.DataFrame(rows)
    if df.empty:
        print("none"); return
    print(df.groupby(["commodity", "rule"]).size().to_string())
    print("with a staged status verdict:", int((df.staged_status_verdicts != "").sum()), "of", len(df))
    if a.csv:
        df.to_csv(a.csv, index=False)
        print("wrote", a.csv)


if __name__ == "__main__":
    main()
