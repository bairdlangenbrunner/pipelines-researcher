"""
Push a person's CLICKED ACCEPTS from the review app to the live backend sheet (phase 1b).

    python review_app/push.py                # PLAN only (reads the live sheet, gws-gem; writes a plan file)
    python review_app/push.py --apply PLAN   # write exactly that plan (gws-gem-write): ASK BAIRD FIRST, every run
    python review_app/push.py --include-stale  # also plan lines whose backend cells changed since they were decided

This is THE ONLY route from an accepted suggestion to the backend sheet, whichever door the decision
came through (loopback server, served Google page, `ledger.py decide` from a chat): the decisions
are read from the staging-dir sidecars, which mirror the Google decision store (run pull.py first).

Rules (CLAUDE.md "Hard requirements"; docs/plans/2026-09-30_review-app.md §5):
  * only lines a PERSON accepted OR SUGGESTED (kinds ref | fill | status | oo); machine records never push.
    A SUGGEST (Baird 2026-10-02) writes the reviewer's own value instead of the proposal, to the one
    cell it names: `Column=value; Column2=value2` names cells outright; a bare value goes to the line's
    only proposed column (fill | oo), to Status (status), or -- if it is all URLs -- onto the `[ref]` cell
    (ref). Any other bare value is skipped as ambiguous (a ref line proposes many columns), never
    guessed. The line's proposed refs back the suggested value (the reviewer judged that line). A rival
    suggest (a concern's candidate taken) stays an Update item. Writing a state / prefecture / country
    cell next to a non-blank, unwritten location cell of the same Start/End group raises a CONCERN:
    printed with the plan and, on apply, appended to notes/push_concerns.csv
  * a `[ref]` cell is ADDITIVE (Baird 2026-10-01): the cell's live text is kept verbatim and each
    proposed URL not already in it is appended, comma-separated. A proposal never replaces or
    drops a URL that is already there (staged `kept_current_refs`/"superseded" notes do not matter)
  * a CLEAR (a blank proposed value over a filled cell, kind fill | status | oo -- never ref) writes ""
    to that one cell (RAW); the backup CSV holds the before text. Its `[ref]` is cleared with it (no
    orphan ref) unless a value of the same cluster stays. A value CHANGED to a different one likewise
    replaces its `[ref]` with the proposed refs (the old ones supported the old value; none proposed =
    skipped). `[ref]` is additive ONLY while the value it supports stays the same
  * a fill writes its value(s) and its `[ref]` together, or neither (no orphan refs); a non-blank
    differing value cell is OVERWRITTEN: accept is the authorization (Baird 2026-10-01) -- the
    stale check guards it, the backup CSV keeps the old text; several lines on one cell merge, two lines wanting different values abort
  * rows are re-located by ProjectID on the LIVE tab (never trust a recorded sheet_row); route
    columns, new rows and `=`-prefixed cells are out of scope
  * a line this script already wrote (its `push` record is newer than the person's call -> the
    overlay's `applied.by == "push"`) is skipped as "already pushed"; the person's accept keeps
    speaking for it (store.speaker), a push record never undecides a line. A plan entry whose
    `before` is a non-blank value (not a `[ref]`) carries `replaces: true` -- the page and `show()`
    flag it so the reviewer sees which accepts overwrite a value
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


def ref_write(cur_ref, proposed, cleared, changed, remaining):
    """The text a line writes to its `[ref]` cell, or None for no write, or ("skip", why).
    Additive only while the value the refs support stays put (Baird 2026-10-01): a value that is
    CLEARED takes its refs with it (when no value of the cell's cluster remains), and a value that is
    CHANGED to a different one takes its refs with it -- the old refs supported the old value -- so the
    proposed refs replace them (none proposed = skip, no orphan value). Otherwise: append."""
    if changed:
        if not proposed:
            return ("skip", "value changes but no proposed refs (the old refs supported the old value)")
        text = ", ".join(dict.fromkeys(u.strip() for u in proposed if u.strip()))
        return text if text != cur_ref.strip() else None
    if cleared:
        return "" if (not remaining and cur_ref.strip()) else None
    text, new = add_refs(cur_ref, proposed)
    return text if new else None


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
    """(pid, line) for every line a PERSON accepted (store.overlay: `reviewed`, the latest person
    call; a push record after the accept marks it `applied`, it does not undecide it)."""
    out = []
    for p in ds["pipelines"]:
        for l in p["lines"]:
            if l.get("reviewed") and l.get("decision") == "accept" and l["kind"] in PUSH_KINDS \
                    and l.get("decided_by") not in store.MACHINE_REVIEWERS:
                out.append((p["pid"] if "pid" in p else p.get("project_id"), l))
    return out


GEO_PARTS = ("Location", "Prefecture/District", "State/Province", "CountryOrArea")
COARSE = ("Prefecture/District", "State/Province", "CountryOrArea")


def parse_suggest(text, tab):
    """`Col=value; Col2=value2` -> {col: value} when every Col is a column of the tab, else None."""
    out = {}
    for part in str(text or "").split(";"):
        c, eq, v = part.partition("=")
        if not eq or c.strip() not in tab.col:
            return None
        out[c.strip()] = v.strip()
    return out or None


def suggest_writes(l, text, tab):
    """({col: value} the suggestion writes, why-not). A ref line takes URLs onto its `[ref]` cell
    (returned as {}: the ref cell is handled by the caller from `proposed_refs`)."""
    named = parse_suggest(text, tab)
    if named:
        return named, ""
    text = str(text or "").strip()
    if not text:
        return None, "suggestion has no value (note only)"
    if l["kind"] == "status":
        return {"Status": text}, ""
    if l["kind"] in ("fill", "oo"):
        cols = [c for c, v in (l.get("proposed_values") or {}).items() if v not in (None, "")]
        if len(cols) == 1:
            return {cols[0]: text}, ""
    if l["kind"] == "ref" and all(re.match(r"https?://", u.strip()) for u in text.split(",")):
        return {}, ""
    cols = ", ".join((l.get("value_cols") or [])[:4]) or "a column"
    return None, f"suggested value {text[:30]!r} names no cell; resave as 'Column=value' (e.g. {cols.split(', ')[0]}=...)"


def geo_concerns(pid, row, writes, tab):
    """Concerns a suggest's geography writes raise: a coarser cell (state / prefecture / country)
    written next to a non-blank location cell of the same Start/End group that stays as it was."""
    out = []
    for end in ("Start", "End"):
        hit = [c for c in writes if c.startswith(end) and c[len(end):] in COARSE]
        if not hit:
            continue
        stale = [f"{end}{p}" for p in GEO_PARTS if f"{end}{p}" in tab.col and f"{end}{p}" not in writes
                 and p not in ("CountryOrArea",) and str(tab.cell(row, f"{end}{p}")).strip()]
        if stale:
            out.append({"pid": pid, "sheet_row": row, "written": {c: writes[c] for c in hit}, "check": stale,
                        "text": f"{', '.join(hit)} set to {', '.join(repr(str(writes[c])) for c in hit)}, but "
                                + "; ".join(f"{c} still reads {str(tab.cell(row, c))!r}" for c in stale)
                                + " -- check it still fits"})
    return out


def pushable_lines(ds):
    """(pid, line, decision) for every line a PERSON accepted or suggested a value for (not a rival)."""
    out = []
    for p in ds["pipelines"]:
        for l in p["lines"]:
            if l.get("reviewed") and l["kind"] in PUSH_KINDS and l.get("decided_by") not in store.MACHINE_REVIEWERS:
                if l.get("decision") == "accept" or (l.get("decision") == "suggest" and not l.get("rival")):
                    out.append((p["pid"] if "pid" in p else p.get("project_id"), l, l["decision"]))
    return out


def pushed(l):
    """The push record's timestamp when push.py already wrote this line, else ''."""
    a = l.get("applied") or {}
    return (a.get("at") or "?") if a.get("by") == "push" else ""


def newer(a, b):
    """Record `a` was written after record `b` (ISO timestamps with offsets; text order as a fallback)."""
    ta, tb = (a or {}).get("ts") or "", (b or {}).get("ts") or ""
    try:
        return datetime.fromisoformat(ta) > datetime.fromisoformat(tb)
    except (TypeError, ValueError):
        return ta > tb


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


def build_plan(commodity="gas", include_stale=False):
    root = staged_store.BATCHES_ROOT
    countries = scopes.included(commodity, None)
    dirs, dc = review_data._country_dirs(countries, commodity, root, None)
    ds, _ = review_data.build(dirs, countries, commodity, root=root, dir_country=dc)
    ds["scope"]["batch"] = True
    paths = store.dir_paths(ds, root.parent)
    store.overlay(ds, paths)
    logs = {d: store.calls(store.read_log(p)) for d, p in paths.items()}
    tabs = {"tracker": Tab(*TABS[("tracker", commodity)]), "oo": Tab(OO_TITLE, OO_HEADER)}
    cells, skipped, meta, stale = {}, [], {}, []     # (tab, row, col) -> {"after", "before", "pid", "lines": [keys]}
    meta["__scope__"] = dict(zip(("id", "snapshot"), ledger.scope_of(ds)))
    concerns = []
    for pid, l, dec in pushable_lines(ds):
        pid = pid or l["key"].split("::")[1].split("|")[0]
        tab = tabs["oo" if l["kind"] == "oo" else "tracker"]
        tname = "oo" if l["kind"] == "oo" else "tracker"
        row = tab.locate(pid, l["sheet_row"])
        if row is None:
            skipped.append((l["key"], "row not found / ambiguous on the live tab"))
            continue
        prec, mrec = store.speaker(logs.get(l["dir"], {}), l["key"])
        if pushed(l) and not (prec and mrec and newer(prec, mrec)):
            skipped.append((l["key"], f"already pushed {pushed(l)}"))      # a newer person call re-plans it
            continue
        writes, bad = {}, None
        values = l.get("proposed_values") or {}
        if dec == "suggest":
            values, why_not = suggest_writes(l, l.get("suggested_value"), tab)
            if values is None:
                skipped.append((l["key"], why_not))
                continue
        for c, v in values.items():
            if v in (None, ""):
                # a blank proposal over a filled cell is a CLEAR (the page draws it "(clear)" and the
                # reviewer accepted it as such); never on a ref-only line, where blanks are placeholders
                if v is None or l["kind"] == "ref" or c not in tab.col or str(tab.cell(row, c)).strip() == "":
                    continue
                writes[c] = ""
                continue
            if c not in tab.col:
                bad = f"column {c} missing on the live tab"
                break
            cur = tab.cell(row, c)
            if str(cur).strip() == "":
                writes[c] = coerce(v)
            elif same_value(cur, v):
                continue
            else:                       # an accepted change overwrites: the click is the authorization
                writes[c] = coerce(v) if not (l["kind"] in ("status", "fill") and c == "Status") else str(v)
        if bad:
            skipped.append((l["key"], bad))
            continue
        rc = l.get("ref_col") or ""
        if rc:
            if rc not in tab.col:
                skipped.append((l["key"], f"column {rc} missing on the live tab"))
                continue
            cleared, changed = [], []
            for c, v in writes.items():
                if c != rc and str(tab.cell(row, c)).strip() != "":
                    (cleared if v == "" else changed).append(c)
            remaining = [c for c in (l.get("value_cols") or []) if c in tab.col and c not in cleared
                         and str(writes.get(c, tab.cell(row, c))).strip() != ""]
            urls = l.get("proposed_refs") or []
            if dec == "suggest" and not values:       # a URL suggestion: those URLs, additively
                urls = [u.strip() for u in str(l["suggested_value"]).split(",") if u.strip()]
            w = ref_write(tab.cell(row, rc), urls, cleared, changed, remaining)
            if isinstance(w, tuple):
                skipped.append((l["key"], w[1]))
                continue
            if w is not None:
                writes[rc] = w
        if not writes:
            skipped.append((l["key"], "already in the backend"))
            continue
        why = staleness(l, prec, tab, row)
        if why:
            stale.append((l["key"], why))
            if not include_stale:
                skipped.append((l["key"], "stale: " + why))
                continue
        meta[l["key"]] = {"kind": l["kind"], "sheet_row": row, "ref_col": rc or l.get("column") or "", "decision": dec}
        if dec == "suggest":
            concerns += [dict(c, key=l["key"]) for c in geo_concerns(pid, row, writes, tab)]
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
                     "ProjectID": d["pid"], "before": d["before"], "after": d["after"], "lines": sorted(set(d["lines"])),
                     "replaces": bool(str(d["before"]).strip()) and not c.endswith("[ref]")})
    meta["__stale__"] = stale
    meta["__concerns__"] = concerns
    return plan, skipped, meta


def token(plan):
    return hashlib.sha1(json.dumps(plan, sort_keys=True).encode()).hexdigest()[:12]


def save_plan(plan, meta, commodity="gas"):
    """Write work/push_plan.json (what --apply and the review server's push button read)."""
    out = ROOT / "work" / "push_plan.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"token": token(plan), "commodity": commodity, "plan": plan, "meta": meta,
                               "stale": meta.get("__stale__", []), "concerns": meta.get("__concerns__", [])}, ensure_ascii=False, indent=1))
    return out


def show(plan, skipped, concerns=()):
    for p in plan:
        a = str(p["after"])
        b = str(p["before"])
        tag = "REPLACES " if p.get("replaces") else ""
        print(f"{p['tab']}!{p['cell']:8} {p['ProjectID']} {p['column']:18} {tag}{b[:50]!r} -> {a[:110]!r}")
    n_rep = sum(1 for p in plan if p.get("replaces"))
    print(f"\n{len(plan)} cells in the plan ({n_rep} replace a value the reviewer saw); token {token(plan)}")
    for k, why in skipped:
        print(f"  skipped {k.split('::')[1]}: {why}")
    for c in concerns:
        print(f"  CONCERN {c['pid']} row {c['sheet_row']}: {c['text']}")
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
    if pl.get("concerns"):
        cf = ROOT / "notes" / "push_concerns.csv"
        new = not cf.exists()
        with cf.open("a", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if new:
                w.writerow(["ts", "ProjectID", "sheet_row", "cells_to_check", "concern", "line_key"])
            for c in pl["concerns"]:
                w.writerow([ts, c["pid"], c["sheet_row"], "; ".join(c["check"]), c["text"], c["key"]])
        print(f"{len(pl['concerns'])} concern(s) appended to {cf.relative_to(ROOT)}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--commodity", default="gas")
    ap.add_argument("--include-stale", action="store_true",
                    help="plan lines whose backend cells changed since they were decided (default: skip, listed)")
    ap.add_argument("--apply", metavar="PLAN", help="write this plan file (ASK BAIRD FIRST)")
    a = ap.parse_args(argv)
    if a.apply:
        return apply(a.apply)
    plan, skipped, meta = build_plan(a.commodity, a.include_stale)
    show(plan, skipped, meta.get("__concerns__", []))
    print("plan written:", save_plan(plan, meta, a.commodity))


if __name__ == "__main__":
    main()
