"""Readiness report for pipeline wiki page generation.

Answers the data team's prep steps from the newest tracker snapshots:

- step 3: rows whose wiki page name differs from `PipelineName` (pages that may need moving), split into punctuation-only differences and real renames
- rows with no wiki page yet (new pages the generator would create)
- pages shared by several rows (segments), and pages that appear on both the oil and gas tabs
- data gaps that would show up on a generated page: blank Status, Status with no ref, blank country, no route, no owner row

Writes `wiki/out/readiness_<date>.xlsx` and prints a summary. Read-only.
"""

from __future__ import annotations

import datetime as dt
import os
import re
import unicodedata

import pandas as pd
from openpyxl.styles import Alignment

from _common import OUT, ensure_out, load, page_name


def _fold(name: str) -> str:
    """Collapse dash, space and accent differences so only real renames remain."""
    s = unicodedata.normalize("NFKD", name)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[‐-―\-]+", "-", s)
    s = re.sub(r"\s*-\s*", "-", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip().casefold()


def tracker_frame(key: str) -> pd.DataFrame:
    df = load(key)
    df["tracker"] = key
    df["page"] = df["Wiki"].map(page_name)
    df["name"] = df["PipelineName"].str.strip()
    return df


def main() -> None:
    oil, gas = tracker_frame("oil"), tracker_frame("gas")
    owners = load("owners")
    both = pd.concat([oil, gas], ignore_index=True)

    # Renames (step 3)
    has_page = both[both["page"] != ""]
    differs = has_page[has_page["page"] != has_page["name"]]
    real = differs[differs["page"].map(_fold) != differs["name"].map(_fold)]
    cosmetic = differs.drop(real.index)
    rename_cols = ["tracker", "ProjectID", "PipelineName", "SegmentName", "page", "Wiki"]
    renames = real[rename_cols].sort_values(["tracker", "page"]).copy()
    # A page named after the segment is a segment-level page, not a rename
    renames["page_is_segment_name"] = (renames["SegmentName"].map(_fold) == renames["page"].map(_fold)).map({True: "yes", False: ""})
    cosmetic_out = cosmetic[rename_cols].sort_values(["tracker", "page"])

    # New pages
    new_pages = both[both["page"] == ""][["tracker", "ProjectID", "PipelineName", "SegmentName", "CountriesOrAreas", "Status"]].sort_values(["tracker", "PipelineName"])

    # Pages and segments
    seg_counts = has_page.groupby("page").agg(rows=("ProjectID", "size"), trackers=("tracker", lambda s: ",".join(sorted(set(s)))), pids=("ProjectID", lambda s: "; ".join(s)))
    multi = seg_counts[seg_counts["rows"] > 1].sort_values("rows", ascending=False).reset_index()
    cross = seg_counts[seg_counts["trackers"].str.contains(",")].reset_index()

    # Data gaps a generated page would expose
    owner_ids = set(owners["ProjectID"])
    gaps = []
    for _, r in both.iterrows():
        issues = []
        if r["Status"].strip() == "":
            issues.append("blank Status")
        elif r["Status [ref]"].strip() == "":
            issues.append("Status has no ref")
        if r["CountriesOrAreas"].strip() == "":
            issues.append("blank CountriesOrAreas")
        if r["RouteType"].strip() != "Mapped route (at any accuracy)":
            issues.append("no mapped route")
        if r["ProjectID"] not in owner_ids and r["Owner"].strip() == "":
            issues.append("no owner")
        if r["LengthKnown"].strip() == "" and r["RouteType"].strip() != "Mapped route (at any accuracy)":
            issues.append("no length and no route")
        if issues:
            gaps.append({"tracker": r["tracker"], "ProjectID": r["ProjectID"], "PipelineName": r["PipelineName"], "page": r["page"], "issues": "; ".join(issues)})
    gaps_df = pd.DataFrame(gaps)

    # Summary
    lines = []
    for key, df in (("oil", oil), ("gas", gas)):
        pages = df[df["page"] != ""]["page"].nunique()
        lines.append(f"{key}: {len(df)} rows, {pages} existing pages, {int((df['page'] == '').sum())} rows with no page")
    segpages = int((renames["page_is_segment_name"] == "yes").sum())
    lines.append(f"real renames (step 3): {len(renames)} rows on {renames['page'].nunique()} pages, of which {segpages} rows sit on a page named after the segment")
    lines.append(f"cosmetic name differences (dash, spacing, accents): {len(cosmetic_out)} rows")
    lines.append(f"pages with several segments: {len(multi)}; pages on both tabs: {len(cross)}")
    if not gaps_df.empty:
        counts = gaps_df["issues"].str.split("; ").explode().value_counts()
        lines.append("data gaps: " + ", ".join(f"{k} {v}" for k, v in counts.items()))
    summary = pd.DataFrame({"line": lines})

    ensure_out()
    stamp = dt.date.today().strftime("%Y%m%d")
    path = os.path.join(OUT, f"readiness_{stamp}.xlsx")
    with pd.ExcelWriter(path, engine="openpyxl") as xw:
        summary.to_excel(xw, sheet_name="Summary", index=False)
        renames.to_excel(xw, sheet_name="Renames", index=False)
        cosmetic_out.to_excel(xw, sheet_name="CosmeticNameDiffs", index=False)
        new_pages.to_excel(xw, sheet_name="NewPages", index=False)
        multi.to_excel(xw, sheet_name="MultiSegmentPages", index=False)
        cross.to_excel(xw, sheet_name="PagesOnBothTabs", index=False)
        gaps_df.to_excel(xw, sheet_name="DataGaps", index=False)
        for ws in xw.book.worksheets:
            for row in ws.iter_rows():
                for c in row:
                    c.alignment = Alignment(wrap_text=False)
    print("\n".join(lines))
    print(f"wrote {path}")


if __name__ == "__main__":
    main()
