"""
Push a person's CLICKED ACCEPTS from the review app to the live backend sheet (phase 1b).

    python review_app/push.py                # PLAN only (reads the live sheet, gws-gem; writes a plan file)
    python review_app/push.py --apply PLAN   # write exactly that plan (gws-gem-write): ASK BAIRD FIRST, every run
    python review_app/push.py --include-stale  # also plan lines whose backend cells changed since they were decided

This is THE ONLY route from an accepted suggestion to the backend sheet, whichever door the decision
came through (loopback server, served Google page, `ledger.py decide` from a chat): the decisions
are read from the staging-dir sidecars, which mirror the Google decision store (run pull.py first).

Rules (CLAUDE.md "Hard requirements"; docs/plans/2026-09-30_review-app.md §5):
  * only lines a PERSON accepted (kinds ref | fill | status | oo); machine records never push
  * a `[ref]` cell is ADDITIVE (Baird 2026-10-01): the cell's live text is kept verbatim and each
    proposed URL not already in it is appended, comma-separated. A proposal never replaces or
    drops a URL that is already there (staged `kept_current_refs`/"superseded" notes do not matter)
  * a fill writes its value(s) and its `[ref]` together, or neither (no orphan refs); a non-blank
    differing value cell is a conflict and the whole line is skipped (a `status` change may overwrite
    Status); several lines on one cell merge, two lines wanting different values abort
  * rows are re-located by ProjectID on the LIVE tab (never trust a recorded sheet_row); route
    columns, new rows and `=`-prefixed cells are out of scope
  * STALE (Baird 2026-10-01): a line whose backend cells (review_data.BASIS_FIELDS: the current
    values, `[ref]` text, Status) differ on the LIVE tab from what the reviewer saw when deciding --
    the record's `basis` no longer matches, or the sheet moved since the snapshot -- is skipped with
    "stale: <what changed>" and listed in the plan's `stale`; the decision still stands in the ledger
    and the workbook. --include-stale pushes them anyway (the conflict rules above still apply).
  * apply: FORMULA pre-read (abort on any formula cell / changed cell), before/after backup CSV in
    notes/, valueInputOption RAW with cell-scoped ranges, re-read verify, `push` machine records
    written to the Google decision store (review_app/ledger.py, origin 'push') and into each line's
    staging dir log so the lines show as applied everywhere.
"""
import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for p in (HERE, ROOT / "scripts"):
    sys.path.insert(0, str(p))

import ledger  # noqa: E402
import pull  # noqa: E402
import review_data  # noqa: E402
import scopes  # noqa: E402
import staged_store  # noqa: E402
import store  # noqa: E402
from apply_route_candidates import SHEET_ID, a1, gws  # noqa: E402

ET = ZoneInfo("America/New_York")
TABS = {("tracker", "gas"): ("Gas pipelines", 2), ("tracker", "oil"): ("Oil/NGL pipelines", 2)}
OO_TITLE, OO_HEADER = "Pipeline operators/owners", 1
PUSH_KINDS = {"ref", "fill", "status", "oo"}
NUM = re.compile(r"^-?\d+(\.\d+)?$")


def read_tab(title, render="FORMULA"):
    body = gws("gws-gem", "get", "--params", json.dumps({
        "spreadsheetId": SHEET_ID, "range": f"'{title}'", "valueRenderOption": render,
        "majorDimension": "ROWS"}))
    return body.get("values") or []


class Tab:
    def __init__(self, title, header_idx):
        self.title, self.header_idx = title, header_idx
        self.rows = read_tab(title)
        self.header = self.rows[header_idx]
        self.col = {}
        for i, c in enumerate(self.header):
            self.col.setdefault(c, i)
        pid = self.col["ProjectID"]
        self.by_pid = {}
        for i, r in enumerate(self.rows):
            if i > header_idx and len(r) > pid and r[pid].strip():
                self.by_pid.setdefault(r[pid].strip(), []).append(i + 1)      # 1-based sheet row

    def cell(self, row, col):
        r = self.rows[row - 1]
        i = self.col[col]
        return r[i] if i < len(r) else ""

    def locate(self, pid, want):
        rows = self.by_pid.get(pid, [])
        if str(want) in {str(x) for x in rows}:
            return int(want)
        return rows[0] if len(rows) == 1 else None


def add_refs(current, urls):
    have = [u.strip() for u in current.split(",") if u.strip()]
    new = [u for u in dict.fromkeys(urls) if u not in current]
    return (", ".join(have + new) if new else current), new


def same_value(cur, v):
    """Equal as text, as numbers, or as a percent ('70.00%' vs the sheet's 0.7)."""
    a, b = str(cur).strip(), str(v).strip()
    if a == b:
        return True

    def num(x):
        try:
            return float(x[:-1]) / 100 if x.endswith("%") else float(x)
        except ValueError:
            return None
    na, nb = num(a), num(b)
    return na is not None and nb is not None and abs(na - nb) < 1e-9


def coerce(v):
    s = str(v).strip()
    if NUM.match(s):
        f = float(s)
        return int(f) if f == int(f) and "." not in s else f
    return s


def accepted_lines(ds):
    out = []
    for p in ds["pipelines"]:
        for l in p["lines"]:
            if l.get("reviewed") and l.get("decision") == "accept" and l["kind"] in PUSH_KINDS \
                    and l.get("decided_by") not in store.MACHINE_REVIEWERS:
                out.append((p["pid"] if "pid" in p else p.get("project_id"), l))
    return out


def staleness(l, rec, tab, row):
    """Why this accepted line is stale, or "" -- the backend cells it was judged against
    (review_data.BASIS_FIELDS) as they are on the LIVE tab vs as the reviewer saw them. Two tests:
    the record's `basis` against the line's (the snapshot moved under the decision; a record with
    no basis -- pre-ledger -- is not judged on it), then every basis cell on the live tab against the
    snapshot's (the sheet moved since the pull)."""
    why = []
    if rec and rec.get("basis") and l.get("basis") and rec["basis"] != l["basis"]:
        why.append(f"decided against snapshot {rec.get('snapshot') or '?'}, cells differ now")
    cells = dict(l.get("current") or {})
    if l.get("ref_col"):
        cells[l["ref_col"]] = l.get("current_ref") or ""
    if "current_status" in l:
        cells["Status"] = l.get("current_status") or ""
    for c, was in cells.items():
        if c not in tab.col:
            continue
        live = tab.cell(row, c)
        if not same_value(live, was):
            why.append(f"{c} was {str(was)[:40]!r}, live {str(live)[:40]!r}")
    return "; ".join(why)


def build_plan(commodity="gas", overwrite=(), include_stale=False):
    root = staged_store.BATCHES_ROOT
    countries = scopes.included(commodity, None)
    dirs, dc = review_data._country_dirs(countries, commodity, root, None)
    ds, _ = review_data.build(dirs, countries, commodity, root=root, dir_country=dc)
    ds["scope"]["batch"] = True
    paths = store.dir_paths(ds, root.parent)
    store.overlay(ds, paths)
    logs = {d: store.latest(store.read_log(p)) for d, p in paths.items()}
    tabs = {"tracker": Tab(*TABS[("tracker", commodity)]), "oo": Tab(OO_TITLE, OO_HEADER)}
    cells, skipped, meta, stale = {}, [], {}, []     # (tab, row, col) -> {"after", "before", "pid", "lines": [keys]}
    meta["__scope__"] = dict(zip(("id", "snapshot"), ledger.scope_of(ds)))
    for pid, l in accepted_lines(ds):
        pid = pid or l["key"].split("::")[1].split("|")[0]
        tab = tabs["oo" if l["kind"] == "oo" else "tracker"]
        tname = "oo" if l["kind"] == "oo" else "tracker"
        row = tab.locate(pid, l["sheet_row"])
        if row is None:
            skipped.append((l["key"], "row not found / ambiguous on the live tab"))
            continue
        writes, bad = {}, None
        for c, v in (l.get("proposed_values") or {}).items():
            if v in (None, ""):
                continue
            if c not in tab.col:
                bad = f"column {c} missing on the live tab"
                break
            cur = tab.cell(row, c)
            if str(cur).strip() == "":
                writes[c] = coerce(v)
            elif same_value(cur, v):
                continue
            elif l["kind"] == "status" and c == "Status":
                writes[c] = str(v)
            elif any(o in l["key"] for o in overwrite):      # Baird named this line: overwrite the value
                writes[c] = coerce(v)
            elif l["kind"] == "fill" and c == "Status":
                writes[c] = str(v)
            else:
                bad = f"conflict: {c} is {cur!r}, proposal {v!r}"
                break
        if bad:
            skipped.append((l["key"], bad))
            continue
        rc = l.get("ref_col") or ""
        if rc:
            if rc not in tab.col:
                skipped.append((l["key"], f"column {rc} missing on the live tab"))
                continue
            cur = tab.cell(row, rc)
            text, new = add_refs(cur, l.get("proposed_refs") or [])
            if new:
                writes[rc] = text
        if not writes:
            skipped.append((l["key"], "already in the backend"))
            continue
        why = staleness(l, logs.get(l["dir"], {}).get(l["key"]), tab, row)
        if why:
            stale.append((l["key"], why))
            if not include_stale:
                skipped.append((l["key"], "stale: " + why))
                continue
        meta[l["key"]] = {"kind": l["kind"], "sheet_row": row, "ref_col": rc or l.get("column") or ""}
        for c, v in writes.items():
            k = (tname, row, c)
            if k in cells and cells[k]["after"] != v:
                if c.endswith("[ref]"):        # two lines on one ref cell: union
                    text, _ = add_refs(str(cells[k]["after"]), [u.strip() for u in str(v).split(",")])
                    cells[k]["after"] = text
                else:
                    sys.exit(f"ABORT: two accepted lines want different values for {k}: {cells[k]['after']!r} vs {v!r}")
            elif k not in cells:
                cells[k] = {"before": tab.cell(row, c), "after": v, "pid": pid, "lines": []}
            cells[k]["lines"].append(l["key"])
    plan = []
    for (tname, row, c), d in sorted(cells.items(), key=lambda x: (x[0][0], x[0][1], tabs[x[0][0]].col[x[0][2]])):
        tab = tabs[tname]
        if str(d["before"]).startswith("="):
            sys.exit(f"ABORT: formula cell {tab.title}!{a1(tab.col[c])}{row}")
        plan.append({"tab": tab.title, "tabkey": tname, "column": c, "cell": f"{a1(tab.col[c])}{row}", "sheet_row": row,
                     "ProjectID": d["pid"], "before": d["before"], "after": d["after"], "lines": sorted(set(d["lines"]))})
    meta["__stale__"] = stale
    return plan, skipped, meta


def token(plan):
    return hashlib.sha1(json.dumps(plan, sort_keys=True).encode()).hexdigest()[:12]


def save_plan(plan, meta, commodity="gas"):
    """Write work/push_plan.json (what --apply and the review server's push button read)."""
    out = ROOT / "work" / "push_plan.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"token": token(plan), "commodity": commodity, "plan": plan, "meta": meta,
                               "stale": meta.get("__stale__", [])}, ensure_ascii=False, indent=1))
    return out


def show(plan, skipped):
    for p in plan:
        a = str(p["after"])
        b = str(p["before"])
        print(f"{p['tab']}!{p['cell']:8} {p['ProjectID']} {p['column']:18} {b[:50]!r} -> {a[:110]!r}")
    print(f"\n{len(plan)} cells in the plan; token {token(plan)}")
    for k, why in skipped:
        print(f"  skipped {k.split('::')[1]}: {why}")
    n = sum(1 for _, why in skipped if why.startswith("stale:"))
    if n:
        print(f"  {n} stale line(s) skipped: the backend changed under the decision (--include-stale pushes them anyway)")


def apply(plan_path):
    pl = json.loads(Path(plan_path).read_text())
    plan = pl["plan"]
    assert token(plan) == pl["token"], "plan file was edited"
    # 1. pre-read with FORMULA: nothing may have changed since the plan, no formulas
    by_tab = {}
    for p in plan:
        by_tab.setdefault(p["tab"], []).append(p)
    for title, ps in by_tab.items():
        got = gws("gws-gem", "batchGet", "--params", json.dumps({
            "spreadsheetId": SHEET_ID, "ranges": [f"'{title}'!{p['cell']}" for p in ps],
            "valueRenderOption": "FORMULA", "majorDimension": "ROWS"}))["valueRanges"]
        for p, vr in zip(ps, got):
            cur = ((vr.get("values") or [[""]])[0] or [""])[0]
            if str(cur).startswith("="):
                sys.exit(f"ABORT formula at {title}!{p['cell']}")
            if str(cur) != str(p["before"]):
                sys.exit(f"ABORT {title}!{p['cell']} changed since the plan: {cur!r} != {p['before']!r}")
    # 2. backup
    # one file per push, never overwritten: the date-only name clobbered the morning's committed
    # backup on the second push of 2026-10-01 (restored from git; that run's file is `-3`).
    stamp = datetime.now(ET).strftime("%Y-%m-%d-%H%M")
    bk = ROOT / "notes" / f"sheet-write-{stamp}-review-app-push.csv"
    n = 2
    while bk.exists():
        bk = bk.with_name(f"sheet-write-{stamp}-review-app-push-{n}.csv")
        n += 1
    with bk.open("x", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["tab", "column", "cell", "sheet_row", "ProjectID", "before", "after"])
        for p in plan:
            w.writerow([p["tab"], p["column"], p["cell"], p["sheet_row"], p["ProjectID"], p["before"], p["after"]])
    print("backup:", bk)
    # 3. write, RAW, cell-scoped
    data = [{"range": f"'{p['tab']}'!{p['cell']}", "majorDimension": "ROWS", "values": [[p["after"]]]} for p in plan]
    for i in range(0, len(data), 100):
        resp = gws("gws-gem-write", "batchUpdate", "--params", json.dumps({"spreadsheetId": SHEET_ID}),
                   "--json", json.dumps({"valueInputOption": "RAW", "data": data[i:i + 100]}))
        print("batchUpdate:", resp.get("totalUpdatedCells"), "cells")
    # 4. verify
    bad = 0
    for title, ps in by_tab.items():
        got = gws("gws-gem", "batchGet", "--params", json.dumps({
            "spreadsheetId": SHEET_ID, "ranges": [f"'{title}'!{p['cell']}" for p in ps],
            "valueRenderOption": "UNFORMATTED_VALUE", "majorDimension": "ROWS"}))["valueRanges"]
        for p, vr in zip(ps, got):
            cur = ((vr.get("values") or [[""]])[0] or [""])[0]
            if str(cur) != str(p["after"]) and not (isinstance(p["after"], (int, float)) and float(cur) == float(p["after"])):
                bad += 1
                print(f"MISMATCH {title}!{p['cell']}: got {cur!r} want {p['after']!r}", file=sys.stderr)
    if bad:
        sys.exit(f"{bad} cells failed verification")
    print(f"verified: all {len(plan)} cells read back as planned")
    # 5. `push` machine records (a machine record is not a click; the line shows as applied): to the
    #    decision store first (ledger, origin 'push'), then each staging dir's log; + push_log
    ts = datetime.now(ET).isoformat(timespec="seconds")
    meta, recs, dirs = pl["meta"], [], {}
    sc = meta.get("__scope__") or {}
    for k, m in sorted(meta.items()):
        if k.startswith("__"):
            continue
        d = k.split("::")[0]
        dirs[d] = ROOT / d
        recs.append({"key": k, "dir": d, "pid": k.split("::")[1].split("|")[0], "sheet_row": m["sheet_row"],
                     "ref_col": m["ref_col"], "kind": m["kind"], "decision": "accept", "suggested_value": "",
                     "note": f"written to the sheet by review_app/push.py {ts}", "reviewer": "push", "ts": ts,
                     "undecided": False})
    cfg = pull.config()
    if cfg.get("store_sheet_id"):
        led = ledger.Ledger(cfg["store_sheet_id"], sc.get("id") or f"review-app-{pl.get('commodity', 'gas')}",
                            sc.get("snapshot") or "", "push")
        store.append_records(recs, dirs, sink=led.sink)
        print(f"push records in the decision store: rows {recs[0].get('row')}-{recs[-1].get('row')}")
    else:
        print("WARNING: no decision store configured; push records written to the staging dirs only", file=sys.stderr)
        store.append_records(recs, dirs)
    for d in dirs:
        with (ROOT / d / "push_log.jsonl").open("a", encoding="utf-8") as f:
            for p in plan:
                if any(k.startswith(d + "::") for k in p["lines"]):
                    f.write(json.dumps({"keys": p["lines"], "range": f"{p['tab']}!{p['cell']}", "before": p["before"],
                                        "after": p["after"], "ts": ts}, ensure_ascii=False) + "\n")
    print(f"push records written for {len(recs)} lines in {len(dirs)} staging dirs")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--commodity", default="gas")
    ap.add_argument("--overwrite", action="append", default=[], metavar="KEY",
                    help="let the accepted line whose key contains KEY overwrite a differing value (Baird names each)")
    ap.add_argument("--include-stale", action="store_true",
                    help="plan lines whose backend cells changed since they were decided (default: skip, listed)")
    ap.add_argument("--apply", metavar="PLAN", help="write this plan file (ASK BAIRD FIRST)")
    a = ap.parse_args(argv)
    if a.apply:
        return apply(a.apply)
    plan, skipped, meta = build_plan(a.commodity, a.overwrite, a.include_stale)
    show(plan, skipped)
    print("plan written:", save_plan(plan, meta, a.commodity))


if __name__ == "__main__":
    main()
