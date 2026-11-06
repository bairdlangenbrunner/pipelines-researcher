"""Build the example tracker file the data team asks for in prep step 2.

Takes the newest snapshots and writes one workbook with the three input tabs in the layout the generator would read (one header row, no banner rows, no buffer rows, no `N/A` rows), plus a `PageGroups` tab showing how rows group into pages. By default it keeps a sample of pages that covers the cases the template describes: single-segment, multi-segment, each status, oil and gas, with and without a route. `--all` keeps every row.

The private note columns (`ResearcherNotes`, `ESJNotes`, `Notes/Links`, `OPEC/problems (for AL+NE)`) are dropped, so the file can leave the team.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os

import pandas as pd
from openpyxl.styles import Alignment

from _common import OUT, ensure_out, load, page_name

DROP = {"ResearcherNotes", "ESJNotes", "Notes/Links", "OPEC/problems (for AL+NE)", "Percentage Verification"}
STATUSES = ["operating", "proposed", "construction", "shelved", "cancelled", "retired", "idled", "mothballed"]


def sample_pages(df: pd.DataFrame, per_status: int) -> set[str]:
    """Pick pages covering each status, single and multi segment, routed and not."""
    df = df[df["page"] != ""]
    sizes = df.groupby("page").size()
    keep: set[str] = set()
    for status in STATUSES:
        rows = df[df["Status"].str.strip() == status]
        for multi in (False, True):
            cand = rows[rows["page"].map(lambda p: (sizes[p] > 1) == multi)]
            for routed in (True, False):
                c2 = cand[(cand["RouteType"].str.strip() == "Mapped route (at any accuracy)") == routed]
                keep.update(c2["page"].drop_duplicates().head(per_status).tolist())
    return keep


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--all", action="store_true", help="keep every row instead of a sample")
    ap.add_argument("--per-case", type=int, default=1, help="pages per status x segment-count x routed case (default 1)")
    args = ap.parse_args()

    frames = {}
    pages: set[str] = set()
    for key in ("oil", "gas"):
        df = load(key)
        df["page"] = df["Wiki"].map(page_name)
        frames[key] = df
        if not args.all:
            pages |= sample_pages(df, args.per_case)
    owners = load("owners")

    stamp = dt.date.today().strftime("%Y%m%d")
    ensure_out()
    path = os.path.join(OUT, f"example_tracker_{'all' if args.all else 'sample'}_{stamp}.xlsx")
    groups = []
    with pd.ExcelWriter(path, engine="openpyxl") as xw:
        pids: set[str] = set()
        for key, sheet in (("oil", "Oil_NGL"), ("gas", "Gas")):
            df = frames[key]
            if not args.all:
                df = df[df["page"].isin(pages)]
            pids |= set(df["ProjectID"])
            for p, g in df.groupby("page"):
                groups.append({"tracker": key, "page": p, "segments": len(g), "ProjectIDs": "; ".join(g["ProjectID"]), "statuses": ", ".join(sorted(set(g["Status"])))})
            out = df.drop(columns=[c for c in df.columns if c in DROP or c == "page"])
            out.to_excel(xw, sheet_name=sheet, index=False)
        own = owners[owners["ProjectID"].isin(pids)] if not args.all else owners
        own.drop(columns=[c for c in own.columns if c in DROP]).to_excel(xw, sheet_name="Operators_Owners", index=False)
        pd.DataFrame(groups).sort_values(["tracker", "page"]).to_excel(xw, sheet_name="PageGroups", index=False)
        for ws in xw.book.worksheets:
            for row in ws.iter_rows():
                for c in row:
                    c.alignment = Alignment(wrap_text=False)
    print(f"wrote {path}: {len(pids)} rows on {len(groups)} pages")


if __name__ == "__main__":
    main()
