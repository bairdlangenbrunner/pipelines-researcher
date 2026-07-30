#!/usr/bin/env python3
"""Move URL-only RouteNotes cells into Route [ref] on the live backend sheet.

Authorized one-off (Baird, 2026-07-30). Protocol per CLAUDE.md hard requirements:
pre-read targets with FORMULA render (abort on formulas), before/after backup CSVs
to notes/, cell-scoped RAW writes via gws-gem-write, post-read verification.

Usage: python routenotes_url_migration.py {gas|oil} [--execute]
Without --execute: plan + pre-verify + before-backup only (no writes).
"""
import json, os, re, subprocess, sys, csv
import pandas as pd

REPO = "/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher"
SHEET_ID = "1foPLE6K-uqFlaYgLPAUxzeXfDO5wOOqE7tibNHeqTek"
STAMP = "20260730"
CFG = {
    "gas": dict(tab="Gas pipelines", csv=f"{REPO}/data/GGIT_gas_snapshot_{STAMP}.csv"),
    "oil": dict(tab="Oil/NGL pipelines", csv=f"{REPO}/data/GOIT_oil_ngl_snapshot_{STAMP}.csv"),
}
URL_RE = re.compile(r"^https?://\S+$")
CHUNK = 400


def col_letter(idx0: int) -> str:
    s = ""
    n = idx0 + 1
    while n:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s


def gws_values(subcmd: str, params: dict, write: bool = False, body: dict | None = None) -> dict:
    cfg = "~/.config/gws-gem-write" if write else "~/.config/gws-gem"
    env = dict(
        os.environ,
        GOOGLE_WORKSPACE_CLI_CONFIG_DIR=os.path.expanduser(cfg),
        GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND="file",
    )
    cmd = ["gws", "sheets", "spreadsheets", "values", subcmd, "--params", json.dumps(params)]
    if body is not None:
        cmd += ["--json", json.dumps(body)]
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
    if proc.returncode != 0:
        sys.exit(f"ERROR gws {subcmd}: {proc.stderr.strip()[:500]}")
    out = proc.stdout
    return json.loads(out[out.index("{"):])


def url_only_tokens(cell: str):
    toks = [t.rstrip(".,;") for t in str(cell).split()]
    toks = [t for t in toks if t]
    if toks and all(URL_RE.match(t) for t in toks):
        return toks
    return None


def main():
    which = sys.argv[1]
    execute = "--execute" in sys.argv
    cfg = CFG[which]
    df = pd.read_csv(cfg["csv"], header=2, low_memory=False)
    notes_i = df.columns.get_loc("RouteNotes")
    ref_i = df.columns.get_loc("Route [ref]")
    notes_L, ref_L = col_letter(notes_i), col_letter(ref_i)
    tab = cfg["tab"]
    print(f"{which}: RouteNotes={notes_L} Route[ref]={ref_L} tab={tab!r}")

    # ---- plan from snapshot
    plan = []  # dicts: sheet_row, pid, old_notes, old_ref, new_ref
    for i in df.index:
        cell = df.at[i, "RouteNotes"]
        if not isinstance(cell, str) or not cell.strip():
            continue
        toks = url_only_tokens(cell)
        if not toks:
            continue
        pid = df.at[i, "ProjectID"]
        if not isinstance(pid, str) or not pid.strip():
            print(f"  SKIP row idx {i}: URL-only RouteNotes but no ProjectID (buffer?): {cell[:80]!r}")
            continue
        old_ref = df.at[i, "Route [ref]"]
        old_ref = old_ref.strip() if isinstance(old_ref, str) else ""
        existing = {t.rstrip(".,;") for t in re.split(r"[,;]\s+|\s+", old_ref)} if old_ref else set()
        add = [t for t in toks if t.rstrip(".,;") not in existing]
        new_ref = (old_ref + ", " + ", ".join(add)).strip(", ") if add else old_ref
        plan.append(dict(sheet_row=i + 4, pid=pid, name=str(df.at[i, "PipelineName"]),
                         old_notes=cell, old_ref=old_ref, new_ref=new_ref,
                         ref_changed=new_ref != old_ref))
    n_refwrite = sum(p["ref_changed"] for p in plan)
    print(f"plan: {len(plan)} rows (clear RouteNotes); {n_refwrite} Route [ref] writes; "
          f"{len(plan) - n_refwrite} already had all URLs in ref")

    # ---- pre-verify against live (FORMULA render)
    last = max(p["sheet_row"] for p in plan)
    got = gws_values("batchGet", {
        "spreadsheetId": SHEET_ID,
        "ranges": [f"'{tab}'!{notes_L}1:{notes_L}{last}", f"'{tab}'!{ref_L}1:{ref_L}{last}"],
        "valueRenderOption": "FORMULA",
    })
    def colvals(vr):
        vals = vr.get("values", [])
        return [(row[0] if row else "") for row in vals]
    live_notes, live_ref = (colvals(v) for v in got["valueRanges"])
    def live(vals, sheet_row):
        j = sheet_row - 1
        v = vals[j] if j < len(vals) else ""
        return str(v) if v is not None else ""

    formulas, drift = [], []
    for p in plan:
        ln, lr = live(live_notes, p["sheet_row"]), live(live_ref, p["sheet_row"])
        if ln.startswith("=") or lr.startswith("="):
            formulas.append(p["sheet_row"])
        if ln.strip() != p["old_notes"].strip() or lr.strip() != p["old_ref"]:
            drift.append((p["sheet_row"], p["pid"], ln[:60], lr[:60]))
    if formulas:
        sys.exit(f"ABORT: formula cells at sheet rows {formulas[:20]}")
    if drift:
        print(f"WARNING: {len(drift)} rows drifted from snapshot — EXCLUDED:")
        for d in drift[:10]:
            print("   ", d)
        drifted = {d[0] for d in drift}
        plan = [p for p in plan if p["sheet_row"] not in drifted]
    print(f"pre-verify OK: {len(plan)} rows confirmed live == snapshot, no formulas")

    # ---- before backup
    bdir = f"{REPO}/notes/routenotes-url-migration-{STAMP}"
    os.makedirs(bdir, exist_ok=True)
    bpath = f"{bdir}/{which}-before.csv"
    with open(bpath, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["SheetRow", "ProjectID", "PipelineName", "RouteNotes_before",
                    "RouteRef_before", "RouteRef_after"])
        for p in plan:
            w.writerow([p["sheet_row"], p["pid"], p["name"], p["old_notes"],
                        p["old_ref"], p["new_ref"]])
    print(f"before-backup: {bpath} ({len(plan)} rows)")

    if not execute:
        print("DRY RUN — no writes. Re-run with --execute.")
        return

    # ---- write: batchUpdate ref cells (RAW, cell-scoped), batchClear notes cells
    ref_writes = [p for p in plan if p["ref_changed"]]
    for k in range(0, len(ref_writes), CHUNK):
        chunk = ref_writes[k:k + CHUNK]
        gws_values("batchUpdate", {"spreadsheetId": SHEET_ID}, write=True, body={
            "valueInputOption": "RAW",
            "data": [{"range": f"'{tab}'!{ref_L}{p['sheet_row']}",
                      "values": [[p["new_ref"]]]} for p in chunk],
        })
        print(f"  ref batchUpdate {k + len(chunk)}/{len(ref_writes)}")
    for k in range(0, len(plan), CHUNK):
        chunk = plan[k:k + CHUNK]
        gws_values("batchClear", {"spreadsheetId": SHEET_ID}, write=True, body={
            "ranges": [f"'{tab}'!{notes_L}{p['sheet_row']}" for p in chunk],
        })
        print(f"  notes batchClear {k + len(chunk)}/{len(plan)}")

    # ---- post-verify + after backup
    got = gws_values("batchGet", {
        "spreadsheetId": SHEET_ID,
        "ranges": [f"'{tab}'!{notes_L}1:{notes_L}{last}", f"'{tab}'!{ref_L}1:{ref_L}{last}"],
        "valueRenderOption": "FORMULA",
    })
    live_notes, live_ref = (colvals(v) for v in got["valueRanges"])
    bad = []
    apath = f"{bdir}/{which}-after.csv"
    with open(apath, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["SheetRow", "ProjectID", "RouteNotes_after", "RouteRef_after"])
        for p in plan:
            ln, lr = live(live_notes, p["sheet_row"]), live(live_ref, p["sheet_row"])
            w.writerow([p["sheet_row"], p["pid"], ln, lr])
            if ln.strip() != "" or lr.strip() != p["new_ref"]:
                bad.append((p["sheet_row"], p["pid"], ln[:60], lr[:60]))
    if bad:
        print(f"VERIFY FAILED on {len(bad)} rows:")
        for b in bad[:20]:
            print("   ", b)
        sys.exit(1)
    print(f"post-verify OK: all {len(plan)} rows match plan. after-backup: {apath}")


if __name__ == "__main__":
    main()
