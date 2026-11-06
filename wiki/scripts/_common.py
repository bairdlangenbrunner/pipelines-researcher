"""Shared loading for the wiki automation prep scripts.

Reads the newest tracker snapshots the same way the rest of the repo does: header on row 3 for the two tracker tabs, row 2 for the operators/owners tab, `N/A` kept as text, buffer rows dropped.
"""

from __future__ import annotations

import glob
import os
import urllib.parse

import pandas as pd

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(REPO, "data")
OUT = os.path.join(REPO, "wiki", "out")

TRACKERS = {
    "oil": {"glob": "GOIT_oil_ngl_snapshot_*.csv", "header": 2, "label": "GOIT oil and NGL"},
    "gas": {"glob": "GGIT_gas_snapshot_*.csv", "header": 2, "label": "GGIT gas"},
    "owners": {"glob": "GEM_operators_owners_snapshot_*.csv", "header": 1, "label": "Pipeline operators/owners"},
}


def newest(tracker: str) -> str:
    files = sorted(glob.glob(os.path.join(DATA, TRACKERS[tracker]["glob"])))
    if not files:
        raise SystemExit(f"no {tracker} snapshot in data/; run ./scripts/refresh_csvs.sh")
    return files[-1]


def load(tracker: str) -> pd.DataFrame:
    path = newest(tracker)
    df = pd.read_csv(path, header=TRACKERS[tracker]["header"], low_memory=False, keep_default_na=False, na_values=[], dtype=str)
    df = df[df["ProjectID"].str.startswith("P")].copy()
    if "Status" in df.columns:
        df = df[df["Status"].str.strip() != "N/A"].copy()
    df.attrs["path"] = path
    return df


def page_name(wiki_url: str) -> str:
    """The wiki page name a `Wiki` cell points at, decoded, or '' when blank."""
    url = (wiki_url or "").strip()
    if not url:
        return ""
    tail = url.split("gem.wiki/", 1)[-1]
    tail = tail.split("#", 1)[0]
    return urllib.parse.unquote(tail).replace("_", " ").strip()


def ensure_out() -> str:
    os.makedirs(OUT, exist_ok=True)
    return OUT
