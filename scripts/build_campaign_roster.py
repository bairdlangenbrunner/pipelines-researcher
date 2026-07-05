#!/usr/bin/env python3
"""Build / refresh a campaign roster: per-country row counts for an annual update
campaign, with manual tracking columns preserved across refreshes.

Counts come from a fresh tracker snapshot (multi-country rows count once per country).
Manual columns (priority, indev_status, discovery_status, packet_file, applied, notes)
are PRESERVED when the roster already exists — a refresh only updates the counts.

    python scripts/build_campaign_roster.py --tracker gas --campaign ggit-2026
    # optionally --csv data/GGIT_gas_snapshot_<date>.csv (default: latest for the tracker)

Output: campaigns/<campaign>/roster.csv, sorted by in-dev total (desc).
"""
import argparse, glob, os
import pandas as pd

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEV = ["proposed", "construction", "shelved"]
COUNTED = INDEV + ["mothballed", "idle", "operating"]
MANUAL_COLS = ["priority", "indev_status", "discovery_status", "packet_file", "applied", "notes"]


def _latest_snapshot(tracker: str) -> str:
    pat = "GGIT_gas*" if tracker == "gas" else "GOIT_oil*"
    hits = sorted(glob.glob(os.path.join(REPO, "data", pat + ".csv")), key=os.path.getmtime)
    if not hits:
        raise SystemExit(f"no {pat}.csv snapshot in data/ — run ./scripts/refresh_csvs.sh")
    return hits[-1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tracker", required=True, choices=["oil", "gas"])
    ap.add_argument("--campaign", required=True, help="campaign slug, e.g. ggit-2026")
    ap.add_argument("--csv", help="snapshot CSV (default: latest data/ snapshot for the tracker)")
    args = ap.parse_args()

    csv_path = args.csv or _latest_snapshot(args.tracker)
    df = pd.read_csv(csv_path, header=2, low_memory=False)
    df = df[df["ProjectID"].notna() & df["ProjectID"].astype(str).str.startswith("P")]

    ex = df.assign(country=df["CountriesOrAreas"].astype(str).str.split(",")).explode("country")
    ex["country"] = ex["country"].str.strip()
    ex = ex[ex["country"].ne("") & ex["country"].ne("nan")]

    rows = []
    for country, g in ex.groupby("country"):
        rec = {"country": country}
        for s in COUNTED:
            rec[s] = int((g["Status"] == s).sum())
        rec["indev_total"] = sum(rec[s] for s in INDEV)
        rec["total_rows"] = len(g)
        rows.append(rec)
    counts = pd.DataFrame(rows)

    out_dir = os.path.join(REPO, "campaigns", args.campaign)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "roster.csv")

    if os.path.exists(out_path):
        prior = pd.read_csv(out_path, dtype=str).fillna("")
        manual = prior[["country"] + [c for c in MANUAL_COLS if c in prior.columns]]
        counts = counts.merge(manual, on="country", how="left")
    for c in MANUAL_COLS:
        if c not in counts.columns:
            counts[c] = ""
    counts[MANUAL_COLS] = counts[MANUAL_COLS].fillna("")

    cols = (["country", "indev_total"] + INDEV + ["mothballed", "idle", "operating", "total_rows"]
            + MANUAL_COLS)
    counts = counts[cols].sort_values(["indev_total", "total_rows"], ascending=False)
    counts.to_csv(out_path, index=False)
    print(f"wrote {out_path}: {len(counts)} countries from {os.path.basename(csv_path)}")
    print(f"  in-dev rows total (per-country sum, multi-country rows counted once per country): "
          f"{counts['indev_total'].sum()}")
    print(counts.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
