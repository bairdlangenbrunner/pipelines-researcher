"""Link each terminal name in the Gas tab's AssociatedLNGTerminal(s) cells to its gem.wiki page (Baird 2026-11-18).

    python scripts/link_lng_terminal_wiki.py            # plan: what would be linked, and names with no page
    python scripts/link_lng_terminal_wiki.py --apply    # write the links (gws-gem-write), back up, re-read

The page for a name comes from GEM's LNG terminal tracker export (../gem-db-ops/lng/gem_export.csv, `Wiki`), matched on
TerminalName, then on the tracker's other names (Driftwood LNG Terminal is Woodside Louisiana LNG Terminal), then on a
small alias table below for spellings the tracker does not list. A cell with several names gets one link per name (rich
text runs); a single-name cell is linked whole, like the cells Baird linked by hand. The cell text is never changed. The
write is formatting only, so it stamps LastUpdated and leaves Researcher (the style-only rule). A cell already linked
to the right page is left alone; a formula cell aborts the run.
"""
import csv, json, os, subprocess, sys, unicodedata
from datetime import date, datetime
from pathlib import Path

import pandas as pd

SHEET_ID = "1foPLE6K-uqFlaYgLPAUxzeXfDO5wOOqE7tibNHeqTek"
TAB, GID, HEADER_ROW = "Gas pipelines", 1020144097, 3
COL, STAMP = "AssociatedLNGTerminal(s)", "LastUpdated"
EXPORT = Path(os.environ.get("GEM_DB_OPS_REPO", "../gem-db-ops")) / "lng/gem_export.csv"
# names on the sheet the tracker spells differently and does not list among its other names
ALIASES = {"Papua New Guinea LNG Terminal (Exxon)": "Papua New Guinea LNG Terminal",
           "Rio Grande LNG": "Rio Grande LNG Terminal",
           "Prelude FLNG facility": "Prelude FLNG Terminal"}


def gws(config, method, params, body=None):
    env = dict(os.environ, GOOGLE_WORKSPACE_CLI_CONFIG_DIR=os.path.expanduser(f"~/.config/{config}"),
               GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND="file")
    cmd = ["gws", "sheets", "spreadsheets", method, "--params", json.dumps(params)] + (["--json", json.dumps(body)] if body else [])
    p = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if p.returncode:
        sys.exit(f"gws {method} failed: {p.stderr.strip()[:500]}")
    return json.loads(p.stdout[p.stdout.index("{"):])


def col_letter(i):
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def fold(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower().strip()


def pages():
    t = pd.read_csv(EXPORT, low_memory=False, keep_default_na=False, na_values=[])
    by = {}
    other = [c for c in t.columns if c.lower().startswith("other") and "name" in c.lower()]
    for _, r in t.iterrows():
        u = r["Wiki"].strip()
        if not u:
            continue
        by.setdefault(fold(r["TerminalName"]), u)
    for _, r in t.iterrows():  # other names only after every main name, so a main name always wins
        u = r["Wiki"].strip()
        for c in other:
            for n in str(r[c]).split(","):
                if u and n.strip():
                    by.setdefault(fold(n), u)
    for a, n in ALIASES.items():
        by[fold(a)] = by[fold(n)]
    return by


def spans(text):
    """(start, end, name) for each comma-separated name, positions in UTF-16 units as the Sheets API counts them."""
    out, pos = [], 0
    u16 = lambda s: len(s.encode("utf-16-le")) // 2
    for part in text.split(","):
        name = part.strip()
        if name:
            lead = len(part) - len(part.lstrip())
            a = u16(text[:pos + lead])
            out.append((a, a + u16(name), name))
        pos += len(part) + 1
    return out


def read():
    h = gws_values("get", {"spreadsheetId": SHEET_ID, "range": f"'{TAB}'!A{HEADER_ROW}:EZ{HEADER_ROW}"})["values"][0]
    ci, si, pi = h.index(COL), h.index(STAMP), h.index("ProjectID")
    L = col_letter(ci)
    d = gws("gws-gem", "get", {"spreadsheetId": SHEET_ID, "ranges": [f"'{TAB}'!{L}{HEADER_ROW + 1}:{L}9000"],
                               "fields": "sheets.data.rowData.values(userEnteredValue,formattedValue,textFormatRuns,hyperlink)"})
    rows = d["sheets"][0]["data"][0].get("rowData", [])
    pids = gws_values("get", {"spreadsheetId": SHEET_ID, "range": f"'{TAB}'!{col_letter(pi)}{HEADER_ROW + 1}:{col_letter(pi)}9000"}).get("values", [])
    return ci, si, rows, pids


def gws_values(method, params, body=None, config="gws-gem"):
    env = dict(os.environ, GOOGLE_WORKSPACE_CLI_CONFIG_DIR=os.path.expanduser(f"~/.config/{config}"),
               GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND="file")
    cmd = ["gws", "sheets", "spreadsheets", "values", method, "--params", json.dumps(params)] + (["--json", json.dumps(body)] if body else [])
    p = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if p.returncode:
        sys.exit(f"gws values {method} failed: {p.stderr.strip()[:500]}")
    return json.loads(p.stdout[p.stdout.index("{"):])


def links_now(v, text):
    """{(start, end): uri} the cell carries now."""
    if v.get("hyperlink") and not v.get("textFormatRuns"):
        return {(0, len(text.encode("utf-16-le")) // 2): v["hyperlink"]}
    runs, out = v.get("textFormatRuns") or [], {}
    n = len(text.encode("utf-16-le")) // 2
    for k, r in enumerate(runs):
        uri = (r.get("format", {}).get("link") or {}).get("uri")
        if uri:
            out[(r.get("startIndex", 0), runs[k + 1]["startIndex"] if k + 1 < len(runs) else n)] = uri
    return out


def plan():
    by = pages()
    ci, si, rows, pids = read()
    todo, missing, done = [], [], 0
    for i, r in enumerate(rows):
        v = (r.get("values") or [{}])[0]
        text = v.get("formattedValue", "")
        if not text:
            continue
        if "formulaValue" in v.get("userEnteredValue", {}):
            sys.exit(f"row {HEADER_ROW + 1 + i}: formula cell in {COL}; aborting")
        row = HEADER_ROW + 1 + i
        pid = (pids[i][0] if i < len(pids) and pids[i] else "")
        want = {}
        for a, b, name in spans(text):
            u = by.get(fold(name))
            if u:
                want[(a, b)] = u
            else:
                missing.append((row, pid, name))
        if not want:
            continue
        have = links_now(v, text)
        if all(have.get(k) == u for k, u in want.items()):
            done += 1
            continue
        todo.append({"row": row, "pid": pid, "text": text, "want": [[a, b, u] for (a, b), u in sorted(want.items())],
                     "before_links": json.dumps({f"{a}-{b}": u for (a, b), u in have.items()})})
    return ci, si, todo, missing, done


def runs_for(text, want):
    n = len(text.encode("utf-16-le")) // 2
    if len(want) == 1 and want[0][0] == 0 and want[0][1] == n:
        return [{"startIndex": 0, "format": {"link": {"uri": want[0][2]}}}]
    runs, at = [], 0
    for a, b, u in want:
        if a > at:
            runs.append({"startIndex": at, "format": {}})
        runs.append({"startIndex": a, "format": {"link": {"uri": u}}})
        at = b
    if at < n:
        runs.append({"startIndex": at, "format": {}})
    if runs[0]["startIndex"] != 0:
        runs.insert(0, {"startIndex": 0, "format": {}})
    return runs


def main():
    ci, si, todo, missing, done = plan()
    print(f"{len(todo)} cells to link, {done} already linked right")
    for t in todo:
        print(f"  row {t['row']} {t['pid']}: {t['text']!r} -> " + ", ".join(u.rsplit('/', 1)[-1] for _, _, u in t["want"]))
    print(f"{len(missing)} names with no gem.wiki page in the LNG tracker export:")
    for row, pid, name in missing:
        print(f"  row {row} {pid}: {name!r}")
    if "--apply" not in sys.argv or not todo:
        return
    stamp = (date.today() - date(1899, 12, 30)).days
    bk = Path("notes") / f"sheet-write-{datetime.now():%Y-%m-%d-%H%M}-lng-terminal-wiki-links.csv"
    with open(bk, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["row", "ProjectID", "text", "links_before", "links_after", "LastUpdated_after"])
        for t in todo:
            w.writerow([t["row"], t["pid"], t["text"], t["before_links"], json.dumps(t["want"]), stamp])
    print("backup:", bk)
    reqs = []
    for t in todo:
        reqs.append({"updateCells": {
            "range": {"sheetId": GID, "startRowIndex": t["row"] - 1, "endRowIndex": t["row"], "startColumnIndex": ci, "endColumnIndex": ci + 1},
            "rows": [{"values": [{"userEnteredValue": {"stringValue": t["text"]}, "textFormatRuns": runs_for(t["text"], t["want"])}]}],
            "fields": "userEnteredValue,textFormatRuns"}})
        reqs.append({"updateCells": {
            "range": {"sheetId": GID, "startRowIndex": t["row"] - 1, "endRowIndex": t["row"], "startColumnIndex": si, "endColumnIndex": si + 1},
            "rows": [{"values": [{"userEnteredValue": {"numberValue": stamp}}]}], "fields": "userEnteredValue"}})
    for k in range(0, len(reqs), 100):
        gws("gws-gem-write", "batchUpdate", {"spreadsheetId": SHEET_ID}, {"requests": reqs[k:k + 100]})
    _, _, left, _, _ = plan()
    if left:
        sys.exit(f"{len(left)} cells did not read back linked: {[t['row'] for t in left]}")
    print(f"verified: all {len(todo)} cells read back linked; LastUpdated set to {stamp} on those rows")


if __name__ == "__main__":
    main()
