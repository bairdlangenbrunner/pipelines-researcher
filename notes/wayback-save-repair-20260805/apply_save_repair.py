#!/usr/bin/env python3
"""Replace broken web.archive.org/save/<target> links with VERIFIED snapshot URLs
on the live backend sheet.

Authorized one-off (Baird, 2026-08-05). Protocol per CLAUDE.md hard requirements:
pre-read targets with FORMULA render (abort on formulas), before/after backup CSVs
to notes/, cell-scoped RAW writes via gws-gem-write, post-read verification.

Usage: python apply_save_repair.py [--execute]
Without --execute: plan + pre-verify + before-backup only (no writes).
"""
import csv, json, os, re, subprocess, sys
from collections import defaultdict

import pandas as pd

REPO = "/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher"
DIR = f"{REPO}/notes/wayback-save-repair-20260805"
SHEET_ID = "1foPLE6K-uqFlaYgLPAUxzeXfDO5wOOqE7tibNHeqTek"
CHUNK = 300
SAVE_RE = re.compile(r"https?://web\.archive\.org/save/", re.I)
TRAIL = ",;)\"' "

TAB_TITLE = {"gas": "Gas pipelines", "oil": "Oil/NGL pipelines",
             "oo": "Pipeline operators/owners"}

# Cells where the /save/ string is PROSE, not a reference — the researcher quoted the
# broken URL (with an elided path) while describing the defect. Rewriting these would
# corrupt the note, so they are never touched.
PROSE_EXCLUDE = {("gas", "RouteNotes", 3921)}

# Not an independent cell: the operators/owners `Wiki` column (E) is a FORMULA that
# mirrors the tracker tabs — E3392 is
#   =iferror(xlookup(F3392,'Gas pipelines'!F:F,'Gas pipelines'!D:D), …)
# with F3392 = P4526, i.e. it displays Gas row 2437's Wiki cell. Repairing the gas cell
# fixes this one's display for free; writing here would destroy the formula.
DERIVED_EXCLUDE = {("oo", "Wiki", 3392)}
CSV_FOR = {
    "gas": (f"{REPO}/data/GGIT_gas_snapshot_20260805.csv", 2),
    "oil": (f"{REPO}/data/GOIT_oil_ngl_snapshot_20260805.csv", 2),
    "oo":  (f"{REPO}/data/GEM_operators_owners_snapshot_20260805.csv", 1),
}


def col_letter(idx0: int) -> str:
    s, n = "", idx0 + 1
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def gws_values(subcmd, params, write=False, body=None):
    cfg = "~/.config/gws-gem-write" if write else "~/.config/gws-gem"
    env = dict(os.environ,
               GOOGLE_WORKSPACE_CLI_CONFIG_DIR=os.path.expanduser(cfg),
               GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND="file")
    cmd = ["gws", "sheets", "spreadsheets", "values", subcmd,
           "--params", json.dumps(params)]
    if body is not None:
        cmd += ["--json", json.dumps(body)]
    p = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if p.returncode != 0:
        sys.exit(f"ERROR gws {subcmd}: {p.stderr.strip()[:500]}")
    out = p.stdout
    return json.loads(out[out.index("{"):])


def repair_cell(cell: str, mapping: dict):
    """Swap the /save/ token for its verified snapshot, preserving all surrounding text
    (leading '(' , trailing ',' , other refs in the same cell)."""
    m = SAVE_RE.search(cell)
    if not m:
        return None, "no-save-token"
    tail = cell[m.end():]
    raw = re.match(r"\S*", tail).group(0)
    core = raw.rstrip(TRAIL)
    punct = raw[len(core):]
    snap = mapping.get(core.strip())
    if not snap:
        return None, "unresolved"
    new = cell[:m.start()] + snap + punct + cell[m.end() + len(raw):]
    return new, None


def main():
    execute = "--execute" in sys.argv
    occ = json.load(open(f"{DIR}/occurrences.json"))
    resolved = json.load(open(f"{DIR}/resolved.json"))
    mapping = {r["target"]: r["snapshot"] for r in resolved
               if r.get("bucket") == "RESOLVED" and r.get("snapshot")}
    print(f"verified snapshot mapping: {len(mapping)} targets")

    # ---- build plan from the snapshot CSVs
    plan, skipped = [], []
    dfs = {k: pd.read_csv(p, header=h, low_memory=False, dtype=str)
           for k, (p, h) in CSV_FOR.items()}
    colidx = {}
    for o in occ:
        key3 = (o["tab"], o["col"], o["sheet_row"])
        if key3 in PROSE_EXCLUDE:
            skipped.append(dict(**{k: o[k] for k in ("tab", "col", "sheet_row")},
                                reason="prose-quotes-the-broken-url", cell=o["cell"]))
            continue
        if key3 in DERIVED_EXCLUDE:
            skipped.append(dict(**{k: o[k] for k in ("tab", "col", "sheet_row")},
                                reason="derived-formula-mirror-of-tracker-tab", cell=o["cell"]))
            continue
        df = dfs[o["tab"]]
        cell = df.at[o["csv_idx"], o["col"]]
        if not isinstance(cell, str):
            skipped.append(dict(**{k: o[k] for k in ("tab", "col", "sheet_row")},
                                reason="cell-not-string"))
            continue
        new, err = repair_cell(cell, mapping)
        if err:
            skipped.append(dict(**{k: o[k] for k in ("tab", "col", "sheet_row")},
                                reason=err, cell=cell))
            continue
        key = (o["tab"], o["col"])
        if key not in colidx:
            colidx[key] = col_letter(df.columns.get_loc(o["col"]))
        pid = ""
        for pidcol in ("ProjectID", "Project ID", "ProjectId"):
            if pidcol in df.columns:
                v = df.at[o["csv_idx"], pidcol]
                pid = v if isinstance(v, str) else ""
                break
        plan.append(dict(tab=o["tab"], sheet_tab=TAB_TITLE[o["tab"]], col=o["col"],
                         col_letter=colidx[key], sheet_row=o["sheet_row"],
                         pid=pid, old=cell, new=new))
    print(f"plan: {len(plan)} cells to rewrite; {len(skipped)} skipped")
    from collections import Counter
    for r, n in Counter(s["reason"] for s in skipped).most_common():
        print(f"   skipped[{r}]: {n}")

    # ---- pre-verify against live (FORMULA render), per (tab, column)
    bycol = defaultdict(list)
    for p in plan:
        bycol[(p["sheet_tab"], p["col_letter"])].append(p)
    formulas, drift = [], []
    for (tab, L), items in sorted(bycol.items()):
        last = max(i["sheet_row"] for i in items)
        got = gws_values("get", {"spreadsheetId": SHEET_ID,
                                 "range": f"'{tab}'!{L}1:{L}{last}",
                                 "valueRenderOption": "FORMULA"})
        vals = [(row[0] if row else "") for row in got.get("values", [])]
        for i in items:
            j = i["sheet_row"] - 1
            live = str(vals[j]) if j < len(vals) and vals[j] is not None else ""
            i["live"] = live
            if live.startswith("="):
                formulas.append((tab, L, i["sheet_row"]))
            elif live.strip() != i["old"].strip():
                drift.append((tab, L, i["sheet_row"], i["col"], live[:70], i["old"][:70]))
    if formulas:
        sys.exit(f"ABORT: formula cells at {formulas[:20]}")
    if drift:
        print(f"WARNING: {len(drift)} cells drifted from snapshot — EXCLUDED:")
        for d in drift[:12]:
            print("   ", d)
        dk = {(d[0], d[1], d[2]) for d in drift}
        plan = [p for p in plan
                if (p["sheet_tab"], p["col_letter"], p["sheet_row"]) not in dk]
    print(f"pre-verify OK: {len(plan)} cells confirmed live == snapshot, no formulas")

    # ---- before backup
    bpath = f"{DIR}/before.csv"
    with open(bpath, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Tab", "SheetTab", "Column", "ColLetter", "SheetRow", "ProjectID",
                    "Before", "After"])
        for p in plan:
            w.writerow([p["tab"], p["sheet_tab"], p["col"], p["col_letter"],
                        p["sheet_row"], p["pid"], p["old"], p["new"]])
    print(f"before-backup: {bpath} ({len(plan)} cells)")
    with open(f"{DIR}/skipped.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Tab", "Column", "SheetRow", "Reason", "Cell"])
        for s in skipped:
            w.writerow([s.get("tab"), s.get("col"), s.get("sheet_row"),
                        s.get("reason"), s.get("cell", "")])

    if not execute:
        print("DRY RUN — no writes. Re-run with --execute.")
        return

    # ---- write (RAW, cell-scoped)
    for k in range(0, len(plan), CHUNK):
        chunk = plan[k:k + CHUNK]
        gws_values("batchUpdate", {"spreadsheetId": SHEET_ID}, write=True, body={
            "valueInputOption": "RAW",
            "data": [{"range": f"'{p['sheet_tab']}'!{p['col_letter']}{p['sheet_row']}",
                      "values": [[p["new"]]]} for p in chunk]})
        print(f"  batchUpdate {k + len(chunk)}/{len(plan)}")

    # ---- post-verify + after backup
    bycol = defaultdict(list)
    for p in plan:
        bycol[(p["sheet_tab"], p["col_letter"])].append(p)
    bad = []
    with open(f"{DIR}/after.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Tab", "Column", "SheetRow", "ProjectID", "After_live"])
        for (tab, L), items in sorted(bycol.items()):
            last = max(i["sheet_row"] for i in items)
            got = gws_values("get", {"spreadsheetId": SHEET_ID,
                                     "range": f"'{tab}'!{L}1:{L}{last}",
                                     "valueRenderOption": "FORMULA"})
            vals = [(row[0] if row else "") for row in got.get("values", [])]
            for i in items:
                j = i["sheet_row"] - 1
                live = str(vals[j]) if j < len(vals) and vals[j] is not None else ""
                w.writerow([tab, i["col"], i["sheet_row"], i["pid"], live])
                if live.strip() != i["new"].strip():
                    bad.append((tab, i["col"], i["sheet_row"], live[:60], i["new"][:60]))
    if bad:
        print(f"VERIFY FAILED on {len(bad)} cells:")
        for b in bad[:20]:
            print("   ", b)
        sys.exit(1)
    print(f"post-verify OK: all {len(plan)} cells match plan. after-backup: {DIR}/after.csv")


if __name__ == "__main__":
    main()
