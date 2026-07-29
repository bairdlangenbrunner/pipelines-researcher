#!/usr/bin/env python3
"""Authenticated tab->CSV pull for the backend sheet — THE way refresh_csvs.sh reads it.

Anonymous access to these documents is being deliberately withdrawn, so the
authenticated gws CLI (or the Drive/Sheets MCP) is the standing path for every
shared-drive and Google Docs/Sheets operation. The old
`export?format=csv&gid=` URL started returning 401 on every tab on 2026-07-29 (the sheet
lives in a shared drive, driveId 0AFOra93TfZAeUk9PVA); it is not a fallback to keep warm.
Drive's file-level export is not a substitute either: for a spreadsheet it emits the FIRST
tab only. So we read each tab through the Sheets API values endpoint and write the CSV
ourselves.

Values come back FORMATTED_VALUE, which is what the CSV export produced, so the row
offsets the whole repo depends on are preserved (header at index 2 for the two
tracker tabs, index 1 for operators/owners). Rows are right-padded to the widest row
because the API truncates trailing empties per row while the CSV export padded them.

Verified 2026-07-29 against the 07-28 anonymous-export snapshots: identical column
lists and identical row counts on all three tabs.

Usage:  python scripts/_sheets_pull.py <tab title> <out.csv>
Reads gws from ~/.config/gws-gem (READ-ONLY work profile).
"""
import json
import os
import subprocess
import sys
import csv

SHEET_ID = "1foPLE6K-uqFlaYgLPAUxzeXfDO5wOOqE7tibNHeqTek"


def pull(title: str) -> list[list[str]]:
    params = json.dumps(
        {
            "spreadsheetId": SHEET_ID,
            "range": f"'{title}'",
            "valueRenderOption": "FORMATTED_VALUE",
            "majorDimension": "ROWS",
        }
    )
    env = dict(
        os.environ,
        GOOGLE_WORKSPACE_CLI_CONFIG_DIR=os.path.expanduser("~/.config/gws-gem"),
        GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND="file",
    )
    proc = subprocess.run(
        ["gws", "sheets", "spreadsheets", "values", "get", "--params", params],
        capture_output=True,
        text=True,
        env=env,
    )
    if proc.returncode != 0:
        sys.exit(f"ERROR: gws failed for '{title}': {proc.stderr.strip()[:400]}")
    out = proc.stdout
    # gws prints a keyring banner before the JSON body on some paths
    try:
        body = out[out.index("{"):]
    except ValueError:
        sys.exit(f"ERROR: no JSON in gws output for '{title}': {out[:200]}")
    values = json.loads(body).get("values")
    if not values:
        sys.exit(f"ERROR: no values returned for '{title}' (auth expired? run: gws-gem auth login)")
    return values


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    title, out_path = sys.argv[1], sys.argv[2]
    rows = pull(title)
    width = max(len(r) for r in rows)
    with open(out_path, "w", newline="") as fh:
        csv.writer(fh).writerows(r + [""] * (width - len(r)) for r in rows)
    print(f"   {len(rows)} rows x {width} cols -> {out_path}")


if __name__ == "__main__":
    main()
