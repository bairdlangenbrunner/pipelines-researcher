"""
Append staged DISCOVERY new rows (`staged_new.json`, class new_row) to the live backend sheet.

    python scripts/append_new_rows.py --staging DIR [--staging DIR ...] [--commodity gas]   # PLAN only (gws-gem)
    python scripts/append_new_rows.py --apply PLAN.json                                       # write it (gws-gem-write): ASK BAIRD FIRST

Authorized per batch only (CLAUDE.md "Hard requirements": the sheet is written on explicit authorization
for that specific edit; new rows are outside review_app/push.py's scope by design). First run: US gas,
Baird 2026-10-05 ("add the 210 rows and copy the formulas, and do the same for the owner tab; create the
additional ProjectIDs as long as there are no overlaps with the oil pipelines; Researcher = CB").

What a plan does
  * one tracker row per candidate, in (PipelineName, SegmentName) order: the tab's BUFFER rows first (the
    blank-name rows at the tail that already carry a ProjectID; their IDs are kept), then rows inserted
    after the grid's last row (insertDimension, inheritFromBefore) with the next free ProjectIDs
  * the next free ProjectID = 1 + the highest P-number on the two tracker tabs; the whole range is then
    checked against EVERY tab holding a ProjectID column (trackers, operators/owners, hydrogen, the
    Removed tabs, the Copy tab) and the plan aborts on any hit
  * the tab's FORMULA columns are copied down from the last buffer row, re-rowed (A4354 -> A4400; an
    absolute $4354 is left alone), after a self-test that re-rowing the second-to-last buffer row
    reproduces the last one exactly
  * values are written as the candidate stages them (original units, full-currency costs; numbers
    coerced), refs are consolidated onto the tracker's real [ref] columns exactly as
    build_discovery_workbook.REF_ALIAS does; a ref key with no tracker column (PipelineName [ref],
    SegmentName [ref]) is NOT written and is counted in the plan summary
  * Owner / Parent on the tracker tab are FORMULAS reading the operators/owners tab, so the owner goes
    there: one operators/owners row per new ProjectID (the buffer rows already have one; it is reused),
    ProjectID + Owner1 (+ Operator) + their [ref]s + the same formula copy-down. The owner-style guard
    from push.py applies (an Owner<N>/Operator the styler would re-spell with no person looking aborts
    the plan). A Parent value has no cell anywhere (both tabs derive it), so it goes into the row's
    ResearcherNotes as a sentence
  * every written row is stamped Researcher = CB, LastUpdated = today's date serial (Baird 2026-10-02)

Apply: preconditions re-read (grid sizes, buffer rows still blank, template formulas unchanged, the
ProjectID range still free), before/after backup CSV in notes/, insertDimension on both tabs, values
RAW + formulas USER_ENTERED in cell-scoped ranges, full read-back verification, then each candidate is
marked `applied` (+ `project_id`) in its staged_new.json so the review app and the workbooks stop
offering it as a new candidate.
"""
import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "review_app"))

import entity_style  # noqa: E402
from apply_route_candidates import SHEET_ID, a1  # noqa: E402
from build_discovery_workbook import OWNER_REF_KEYS, REF_ALIAS  # noqa: E402

ET = ZoneInfo("America/New_York")
AGENT = "CB"
NUM = re.compile(r"^-?\d+(\.\d+)?$")
NAME_COL = re.compile(r"Owner\d+|Operator")
TEXT_COLS = {"Diameter"}   # stored as text on the sheet: DiameterInMm runs regexmatch() over it (multi-value "24, 36"), a number errors to "--"
TRACKER = {"gas": ("Gas pipelines", 1020144097, 3), "oil": ("Oil/NGL pipelines", 456134080, 3)}   # title, sheetId, header row (1-based)
OO_TITLE, OO_SHEET_ID, OO_HEADER_ROW = "Pipeline operators/owners", 1489950650, 2
LAST_COL = {"Gas pipelines": 132, "Oil/NGL pipelines": 107, OO_TITLE: 44}
# tabs whose ProjectID column must not already hold a planned ID (title -> header row to search)
PID_TABS = ["Gas pipelines", "Oil/NGL pipelines", "Hydrogen pipelines", OO_TITLE,
            "Removed oil/NGL/gas pipelines", "Removed Chinese pipelines", "Removed hydrogen pipelines",
            "Copy of Gas pipelines", "Removed operators/owners (from removed pipelines)",
            "Pipeline operators/owners - HYDROGEN ONLY"]


# ----------------------------------------------------------------------------- gws
def gws(config, *args):
    import os
    env = dict(os.environ, GOOGLE_WORKSPACE_CLI_CONFIG_DIR=os.path.expanduser(f"~/.config/{config}"),
               GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND="file")
    proc = subprocess.run(["gws", "sheets", "spreadsheets", *args], capture_output=True, text=True, env=env)
    if proc.returncode != 0:
        sys.exit(f"ERROR: gws {' '.join(args[:2])} failed: {proc.stderr.strip()[:800]}")
    out = proc.stdout
    return json.loads(out[out.index("{"):]) if "{" in out else {}


def meta():
    m = gws("gws-gem", "get", "--params", json.dumps({"spreadsheetId": SHEET_ID, "fields": "sheets.properties"}))
    out = {}
    for s in m["sheets"]:
        pr = dict(s["properties"])
        pr["rowCount"] = pr["gridProperties"]["rowCount"]
        out[pr["title"]] = pr
    return out


def get_range(rng, render="FORMULA"):
    return gws("gws-gem", "values", "get", "--params", json.dumps({
        "spreadsheetId": SHEET_ID, "range": rng, "valueRenderOption": render,
        "majorDimension": "ROWS"})).get("values") or []


def batch_get(ranges, render, chunk=40):
    out = []
    for i in range(0, len(ranges), chunk):
        part = ranges[i:i + chunk]
        got = gws("gws-gem", "values", "batchGet", "--params", json.dumps({
            "spreadsheetId": SHEET_ID, "ranges": part, "valueRenderOption": render,
            "majorDimension": "ROWS"}))["valueRanges"]
        assert len(got) == len(part), f"got {len(got)} ranges, asked {len(part)}"
        out += [vr.get("values") or [] for vr in got]
    return out


def col_letter_of(header, name):
    return a1(header.index(name))


# ----------------------------------------------------------------------------- helpers
def nonempty(v):
    return v is not None and str(v).strip() != ""


def coerce(v):
    s = str(v).strip()
    if NUM.match(s):
        f = float(s)
        return int(f) if f == int(f) and "." not in s else f
    return s


def dedup(seq):
    return list(dict.fromkeys(u.strip() for u in seq if nonempty(u)))


def stamp_values():
    today = datetime.now(ET).date()
    return {"Researcher": AGENT, "LastUpdated": (today - date(1899, 12, 30)).days}


def rerow(formula, src_row, dst_row):
    """Re-row every relative row reference (A4354, $A4354) to dst_row; an absolute row ($4354) stays."""
    pat = re.compile(r"(?<![A-Za-z0-9_])(\$?[A-Z]{1,3})" + str(src_row) + r"(?![0-9])")
    return pat.sub(lambda m: m.group(1) + str(dst_row), formula)


def pid_num(p):
    m = re.fullmatch(r"P(\d+)", str(p).strip())
    return int(m.group(1)) if m else None


def tab_pids(title):
    """Every P#### in the tab's ProjectID column (header searched in the first 3 rows)."""
    top = get_range(f"'{title}'!A1:EZ3", "FORMATTED_VALUE")
    hdr = next((r for r in top if "ProjectID" in r), None)
    if hdr is None:
        sys.exit(f"{title}: no ProjectID header in its first 3 rows")
    L = a1(hdr.index("ProjectID"))
    col = get_range(f"'{title}'!{L}1:{L}", "FORMATTED_VALUE")
    return {r[0].strip() for r in col if r and pid_num(r[0]) is not None}


def tail_state(title, header_row, props):
    """(header, rows) for the tab's tail: header + the last 40 grid rows, FORMULA render."""
    n = props["rowCount"]
    header = get_range(f"'{title}'!A{header_row}:{a1(LAST_COL[title] - 1)}{header_row}", "FORMULA")[0]
    header += [""] * (LAST_COL[title] - len(header))
    first = max(header_row + 1, n - 39)
    rows = get_range(f"'{title}'!A{first}:{a1(LAST_COL[title] - 1)}{n}", "FORMULA")
    rows = [r + [""] * (LAST_COL[title] - len(r)) for r in rows]
    rows += [[""] * LAST_COL[title]] * (n - first + 1 - len(rows))
    return header, {first + i: r for i, r in enumerate(rows)}


def buffer_rows(header, tail, key_cols):
    """Tail rows that carry a ProjectID but none of the key columns (PipelineName, Status) — contiguous
    up to the last grid row."""
    pid_i = header.index("ProjectID")
    idx = [header.index(c) for c in key_cols]
    out = []
    for r in sorted(tail, reverse=True):
        row = tail[r]
        if pid_num(row[pid_i]) is not None and all(not nonempty(row[i]) for i in idx):
            out.append(r)
        else:
            break
    return sorted(out)


def formula_template(header, tail, row):
    return {header[i]: v for i, v in enumerate(tail[row]) if str(v).startswith("=")}


def selftest_rerow(header, tail, rows):
    """Re-rowing the second-to-last buffer row must reproduce the last one byte for byte."""
    if len(rows) < 2:
        return
    a, b = rows[-2], rows[-1]
    fa, fb = formula_template(header, tail, a), formula_template(header, tail, b)
    assert set(fa) == set(fb), f"formula columns differ between rows {a} and {b}: {set(fa) ^ set(fb)}"
    for c in fa:
        got = rerow(fa[c], a, b)
        if got != fb[c]:
            sys.exit(f"ABORT re-row self-test failed on {c}: row {a} re-rowed -> {got[:120]!r} vs row {b} {fb[c][:120]!r}")


# ----------------------------------------------------------------------------- plan
def load_candidates(dirs):
    out = []
    for d in dirs:
        f = Path(d) / "staged_new.json"
        data = json.loads(f.read_text())
        for i, c in enumerate(data.get("candidates", [])):
            if c.get("class") != "new_row" or c.get("applied"):
                continue
            out.append((str(f), i, c))
    out.sort(key=lambda t: ((t[2]["values"].get("PipelineName") or t[2].get("name") or "").lower(),
                            (t[2]["values"].get("SegmentName") or "").lower()))
    slugs = [c["slug"] for _, _, c in out]
    dups = {s for s in slugs if slugs.count(s) > 1}
    if dups:
        sys.exit(f"ABORT duplicate slugs across staging dirs: {sorted(dups)}")
    return out


def tracker_cells(c, header, unmapped):
    """{column: value} a candidate writes on the tracker tab (no formulas, no stamps, no ProjectID)."""
    cells = {}
    for k, v in (c.get("values") or {}).items():
        if not nonempty(v):
            continue
        if k in ("Owner", "Parent", "Operator"):
            continue          # formulas on the tracker tab; the owner goes to the operators/owners tab
        if k not in header:
            unmapped[k] += 1
            continue
        if str(header_formula_marker.get(k, "")).startswith("="):
            unmapped[k] += 1
            continue
        cells[k] = str(v).strip() if k in TEXT_COLS else coerce(v)
    refs = {}
    oo_refs = {}
    for rc, urls in (c.get("refs") or {}).items():
        urls = dedup(urls if isinstance(urls, list) else [urls])
        if not urls:
            continue
        target = REF_ALIAS.get(rc, rc)
        if not target.endswith(" [ref]"):
            target += " [ref]"
        if target in OWNER_REF_KEYS:
            oo_refs.setdefault(target, []).extend(urls)
        elif target in header:
            refs.setdefault(target, []).extend(urls)
        else:
            unmapped[rc] += 1
    for col, urls in refs.items():
        cells[col] = ", ".join(dedup(urls))
    notes = str(c.get("researcher_notes") or "").strip()
    parent = str((c.get("values") or {}).get("Parent") or "").strip()
    if parent and parent.lower() not in notes.lower():
        notes = (notes + " " if notes else "") + f"Parent company named by the sources: {parent}."
    if notes:
        cells["ResearcherNotes"] = notes
    return cells, oo_refs


header_formula_marker = {}   # tracker column -> template formula (set in build_plan; a value never lands on a formula column)


def oo_cells(c, oo_refs, oo_header):
    """{column: value} for the operators/owners row: Owner1 / Operator + their [ref]s."""
    vals = c.get("values") or {}
    cells = {}
    owner = str(vals.get("Owner") or "").strip()
    owners = split_owners(owner)
    if len(owners) > 11:
        sys.exit(f"ABORT {c['slug']}: {len(owners)} owners, the tab has 11 slots")
    for i, (name, share) in enumerate(owners, 1):
        cells[f"Owner{i}"] = name
        if share is not None:
            cells[f"Owner{i}%"] = share
    op = str(vals.get("Operator") or "").strip()
    if op:
        cells["Operator"] = op
    urls = dedup(oo_refs.get("Owner [ref]", []) + oo_refs.get("Parent [ref]", []) + oo_refs.get("ParentEntityIDs [ref]", []))
    if urls and owner:
        cells["Owner [ref]"] = ", ".join(urls)
    ourls = dedup(oo_refs.get("Operator [ref]", []))
    if ourls and op:
        cells["Operator [ref]"] = ", ".join(ourls)
    for k in cells:
        if k not in oo_header:
            sys.exit(f"ABORT operators/owners tab has no {k} column")
    return cells


STAKE = re.compile(r"^(.*?)\s*\[\s*(\d+(?:\.\d*)?)\s*%\s*\]$")


def split_owners(owner):
    """'A [60%]; B [40%]' -> [('A', 0.6), ('B', 0.4)]; 'A' -> [('A', None)]. The tab stores Owner<N>% as a
    fraction (1 = 100%); a stake the source did not state stays blank (not researched)."""
    out = []
    for part in re.split(r"\s*;\s*", owner) if owner else []:
        part = part.strip()
        if not part:
            continue
        m = STAKE.match(part)
        if m:
            out.append((m.group(1).strip(), round(float(m.group(2)) / 100, 6)))
        else:
            out.append((part, None))
    return out


def unstyled(cells):
    out = []
    for col, v in cells.items():
        if NAME_COL.fullmatch(col) and nonempty(v):
            st = entity_style.style(str(v).strip())
            if st.changed and entity_style.adoptable(st):
                out.append((col, v, st.styled))
    return out


def build_plan(dirs, commodity):
    title, sheet_id, hdr_row = TRACKER[commodity]
    cands = load_candidates(dirs)
    if not cands:
        sys.exit("nothing to append: no un-applied new_row candidates")
    props = meta()
    t_props, oo_props = props[title], props[OO_TITLE]
    header, tail = tail_state(title, hdr_row, t_props)
    oo_header, oo_tail = tail_state(OO_TITLE, OO_HEADER_ROW, oo_props)
    buf = buffer_rows(header, tail, ("PipelineName", "Status"))
    if not buf or buf[-1] != t_props["rowCount"]:
        sys.exit(f"ABORT {title}: buffer rows {buf} do not run to the grid's last row {t_props['rowCount']}")
    selftest_rerow(header, tail, buf)
    tmpl_row = buf[-1]
    tmpl = formula_template(header, tail, tmpl_row)
    header_formula_marker.clear()
    header_formula_marker.update(tmpl)
    # operators/owners: template = the last grid row (every row there is a real row); rows for the buffer PIDs exist
    oo_last = oo_props["rowCount"]
    oo_tmpl = formula_template(oo_header, oo_tail, oo_last)
    selftest_rerow(oo_header, oo_tail, [oo_last - 1, oo_last])
    oo_pid_i = oo_header.index("ProjectID")
    oo_row_of = {}
    for r, row in oo_tail.items():
        if pid_num(row[oo_pid_i]) is not None:
            oo_row_of[row[oo_pid_i].strip()] = r
    # ProjectIDs
    print("reading ProjectID columns on", len(PID_TABS), "tabs ...")
    pids_by_tab = {t: tab_pids(t) for t in PID_TABS}
    tracker_max = max(pid_num(p) for t in ("Gas pipelines", "Oil/NGL pipelines") for p in pids_by_tab[t])
    n_new = len(cands) - len(buf)
    if n_new < 0:
        sys.exit(f"ABORT fewer candidates ({len(cands)}) than buffer rows ({len(buf)}); this script fills buffers only when every one is used")
    new_pids = [f"P{tracker_max + 1 + i:04d}" for i in range(n_new)]
    for t, ps in pids_by_tab.items():
        hit = sorted(set(new_pids) & ps)
        if hit:
            sys.exit(f"ABORT ProjectID overlap on '{t}': {hit[:10]}")
    pid_i = header.index("ProjectID")
    buf_pids = [tail[r][pid_i].strip() for r in buf]
    # per-row assignment
    stamps = stamp_values()
    unmapped = {}
    from collections import Counter
    unmapped = Counter()
    rows = []
    writes = []           # {tab, cell, row, column, value, kind, pid}
    structural = [{"tab": title, "sheetId": sheet_id, "insert_at": t_props["rowCount"], "count": n_new},
                  {"tab": OO_TITLE, "sheetId": OO_SHEET_ID, "insert_at": oo_last, "count": 0}]
    oo_next = oo_last
    bad_style = []
    oo_cols_formula = set(oo_tmpl)
    for k, (src, idx, c) in enumerate(cands):
        if k < len(buf):
            row, pid, is_new = buf[k], buf_pids[k], False
        else:
            row, pid, is_new = t_props["rowCount"] + 1 + (k - len(buf)), new_pids[k - len(buf)], True
        cells, oo_refs = tracker_cells(c, header, unmapped)
        ocells = oo_cells(c, oo_refs, oo_header)
        bad_style += [(pid, *x) for x in unstyled(ocells)]
        for col, v in cells.items():
            if col in tmpl:
                sys.exit(f"ABORT {pid}: value for formula column {col}")
            writes.append({"tab": title, "row": row, "column": col, "cell": f"{col_letter_of(header, col)}{row}",
                           "value": v, "kind": "value", "pid": pid})
        if is_new:
            writes.append({"tab": title, "row": row, "column": "ProjectID", "cell": f"{col_letter_of(header, 'ProjectID')}{row}",
                           "value": pid, "kind": "pid", "pid": pid})
            for col, f in tmpl.items():
                writes.append({"tab": title, "row": row, "column": col, "cell": f"{col_letter_of(header, col)}{row}",
                               "value": rerow(f, tmpl_row, row), "kind": "formula", "pid": pid})
        for col, v in stamps.items():
            writes.append({"tab": title, "row": row, "column": col, "cell": f"{col_letter_of(header, col)}{row}",
                           "value": v, "kind": "stamp", "pid": pid})
        # operators/owners row
        if pid in oo_row_of:
            orow, o_new = oo_row_of[pid], False
        else:
            oo_next += 1
            orow, o_new = oo_next, True
            structural[1]["count"] += 1
        for col, v in ocells.items():
            if col in oo_cols_formula:
                sys.exit(f"ABORT {pid}: operators/owners value for formula column {col}")
            writes.append({"tab": OO_TITLE, "row": orow, "column": col, "cell": f"{col_letter_of(oo_header, col)}{orow}",
                           "value": v, "kind": "value", "pid": pid})
        if o_new:
            writes.append({"tab": OO_TITLE, "row": orow, "column": "ProjectID", "cell": f"{col_letter_of(oo_header, 'ProjectID')}{orow}",
                           "value": pid, "kind": "pid", "pid": pid})
            for col, f in oo_tmpl.items():
                writes.append({"tab": OO_TITLE, "row": orow, "column": col, "cell": f"{col_letter_of(oo_header, col)}{orow}",
                               "value": rerow(f, oo_last, orow), "kind": "formula", "pid": pid})
        for col, v in stamps.items():
            writes.append({"tab": OO_TITLE, "row": orow, "column": col, "cell": f"{col_letter_of(oo_header, col)}{orow}",
                           "value": v, "kind": "stamp", "pid": pid})
        rows.append({"pid": pid, "sheet_row": row, "new_row": is_new, "oo_row": orow, "oo_new": o_new,
                     "name": c["values"].get("PipelineName") or c.get("name"), "segment": c["values"].get("SegmentName") or "",
                     "slug": c["slug"], "source": src, "index": idx, "owner": c["values"].get("Owner") or ""})
    if bad_style:
        for pid, col, v, styled in bad_style:
            print(f"UNSTYLED {pid} {col}: {v!r} -> {styled!r}", file=sys.stderr)
        sys.exit(f"ABORT {len(bad_style)} owner/operator cells in a spelling the styler would adopt; run scripts/restyle_staged_owners.py and re-plan")
    # preconditions the apply re-checks
    pre = {
        "grid": {title: t_props["rowCount"], OO_TITLE: oo_last},
        "buffer_rows": {str(r): tail[r] for r in buf},
        "template": {"tab": title, "row": tmpl_row, "formulas": tmpl},
        "oo_template": {"row": oo_last, "formulas": oo_tmpl},
        "oo_buffer_rows": {str(oo_row_of[p]): oo_tail[oo_row_of[p]] for p in buf_pids if p in oo_row_of},
        "new_pids": new_pids,
        "pid_tabs": PID_TABS,
        "header": header, "oo_header": oo_header,
    }
    plan = {"commodity": commodity, "tab": title, "created": datetime.now(ET).isoformat(timespec="seconds"),
            "staging_dirs": [str(d) for d in dirs], "structural": structural, "rows": rows, "writes": writes,
            "pre": pre, "unmapped": dict(unmapped), "stamps": stamps}
    plan["token"] = hashlib.sha256(json.dumps({k: plan[k] for k in ("structural", "rows", "writes", "pre")}, sort_keys=True, default=str).encode()).hexdigest()[:16]
    return plan


def summarize(plan):
    from collections import Counter
    w = plan["writes"]
    by = Counter((x["tab"], x["kind"]) for x in w)
    print(f"\nPLAN {plan['tab']}: {len(plan['rows'])} rows "
          f"({sum(1 for r in plan['rows'] if not r['new_row'])} buffer rows reused, {sum(1 for r in plan['rows'] if r['new_row'])} inserted)")
    for s in plan["structural"]:
        print(f"  insert {s['count']} rows on '{s['tab']}' after row {s['insert_at']}")
    for (tab, kind), n in sorted(by.items()):
        print(f"  {tab:32s} {kind:8s} {n:6d} cells")
    print(f"  total cells: {len(w)}")
    print(f"  ProjectIDs: buffer {plan['rows'][0]['pid']} .. new {plan['pre']['new_pids'][0]} .. {plan['pre']['new_pids'][-1]}" if plan["pre"]["new_pids"] else "")
    print(f"  owners written: {sum(1 for r in plan['rows'] if r['owner'])} of {len(plan['rows'])}")
    if plan["unmapped"]:
        print(f"  NOT written (no tracker column): {plan['unmapped']}")
    print(f"  token {plan['token']}")


# ----------------------------------------------------------------------------- apply
def check_pre(plan):
    pre = plan["pre"]
    props = meta()
    for tab, n in pre["grid"].items():
        if props[tab]["rowCount"] != n:
            sys.exit(f"ABORT grid of '{tab}' is {props[tab]['rowCount']} rows, plan expects {n}")
    title = plan["tab"]
    hdr_row = TRACKER[plan["commodity"]][2]
    header, tail = tail_state(title, hdr_row, props[title])
    if header != pre["header"]:
        sys.exit("ABORT tracker header changed since the plan")
    for r, row in pre["buffer_rows"].items():
        if tail[int(r)] != row:
            sys.exit(f"ABORT buffer row {r} on '{title}' changed since the plan")
    oo_header, oo_tail = tail_state(OO_TITLE, OO_HEADER_ROW, props[OO_TITLE])
    if oo_header != pre["oo_header"]:
        sys.exit("ABORT operators/owners header changed since the plan")
    for r, row in pre["oo_buffer_rows"].items():
        if oo_tail[int(r)] != row:
            sys.exit(f"ABORT operators/owners row {r} changed since the plan")
    if formula_template(oo_header, oo_tail, pre["oo_template"]["row"]) != pre["oo_template"]["formulas"]:
        sys.exit("ABORT operators/owners template row changed since the plan")
    new = set(pre["new_pids"])
    for t in pre["pid_tabs"]:
        hit = sorted(new & tab_pids(t))
        if hit:
            sys.exit(f"ABORT ProjectID now present on '{t}': {hit[:10]}")
    print("preconditions hold: grids, buffer rows, templates, ProjectID range all as planned")


def backup(plan):
    stamp = datetime.now(ET).strftime("%Y-%m-%d-%H%M")
    bk = ROOT / "notes" / f"sheet-write-{stamp}-append-new-rows-{plan['commodity']}.csv"
    n = 2
    while bk.exists():
        bk = bk.with_name(f"sheet-write-{stamp}-append-new-rows-{plan['commodity']}-{n}.csv")
        n += 1
    with bk.open("x", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["tab", "column", "cell", "sheet_row", "ProjectID", "kind", "before", "after"])
        for x in plan["writes"]:
            w.writerow([x["tab"], x["column"], x["cell"], x["row"], x["pid"], x["kind"], "", x["value"]])
    return bk


def insert_rows(plan):
    reqs = []
    for s in plan["structural"]:
        if s["count"]:
            reqs.append({"insertDimension": {"range": {"sheetId": s["sheetId"], "dimension": "ROWS",
                                                        "startIndex": s["insert_at"], "endIndex": s["insert_at"] + s["count"]},
                                              "inheritFromBefore": True}})
    if not reqs:
        return
    gws("gws-gem-write", "batchUpdate", "--params", json.dumps({"spreadsheetId": SHEET_ID}),
        "--json", json.dumps({"requests": reqs}))
    props = meta()
    for s in plan["structural"]:
        want = plan["pre"]["grid"][s["tab"]] + s["count"]
        if props[s["tab"]]["rowCount"] != want:
            sys.exit(f"ABORT after insert: '{s['tab']}' has {props[s['tab']]['rowCount']} rows, want {want}; STOP and inspect")
        print(f"inserted {s['count']} rows on '{s['tab']}' -> {want} rows")


def write_cells(plan):
    vals = [x for x in plan["writes"] if x["kind"] != "formula"]
    forms = [x for x in plan["writes"] if x["kind"] == "formula"]
    for group, opt in ((vals, "RAW"), (forms, "USER_ENTERED")):
        data = [{"range": f"'{x['tab']}'!{x['cell']}", "majorDimension": "ROWS", "values": [[x["value"]]]} for x in group]
        done = 0
        for i in range(0, len(data), 400):
            resp = gws("gws-gem-write", "values", "batchUpdate", "--params", json.dumps({"spreadsheetId": SHEET_ID}),
                       "--json", json.dumps({"valueInputOption": opt, "data": data[i:i + 400]}))
            done += resp.get("totalUpdatedCells") or 0
        print(f"wrote {done} cells ({opt}; planned {len(group)})")


def norm_formula(s):
    return re.sub(r"\s+", "", str(s)).lower()


def verify(plan):
    """Read every touched row back (row ranges, both renders) and compare cell by cell."""
    bad = 0
    for tab in {x["tab"] for x in plan["writes"]}:
        header = plan["pre"]["header"] if tab == plan["tab"] else plan["pre"]["oo_header"]
        rows = sorted({x["row"] for x in plan["writes"] if x["tab"] == tab})
        last = a1(LAST_COL[tab] - 1)
        ranges = [f"'{tab}'!A{r}:{last}{r}" for r in rows]
        got_f = {r: (v[0] if v else []) for r, v in zip(rows, batch_get(ranges, "FORMULA"))}
        got_v = {r: (v[0] if v else []) for r, v in zip(rows, batch_get(ranges, "UNFORMATTED_VALUE"))}
        for x in plan["writes"]:
            if x["tab"] != tab:
                continue
            ci = header.index(x["column"])
            if x["kind"] == "formula":
                row = got_f[x["row"]]
                cur = row[ci] if ci < len(row) else ""
                if norm_formula(cur) != norm_formula(x["value"]):
                    bad += 1
                    print(f"MISMATCH formula {tab}!{x['cell']}: {str(cur)[:80]!r}", file=sys.stderr)
            else:
                row = got_v[x["row"]]
                cur = row[ci] if ci < len(row) else ""
                want = x["value"]
                ok = str(cur) == str(want) or (isinstance(want, (int, float)) and NUM.match(str(cur)) and float(cur) == float(want))
                if not ok:
                    bad += 1
                    print(f"MISMATCH {tab}!{x['cell']}: got {str(cur)[:80]!r} want {str(want)[:80]!r}", file=sys.stderr)
    if bad:
        sys.exit(f"{bad} cells failed verification")
    print(f"verified: all {len(plan['writes'])} cells read back as planned")


def mark_applied(plan, bk):
    today = datetime.now(ET).date().isoformat()
    by_src = {}
    for r in plan["rows"]:
        by_src.setdefault(r["source"], []).append(r)
    for src, rs in by_src.items():
        p = Path(src)
        text = p.read_text()
        m = re.search(r"\n( +)\"", text)
        indent = len(m.group(1)) if m else 1
        data = json.loads(text)
        for r in rs:
            c = data["candidates"][r["index"]]
            assert c["slug"] == r["slug"], (src, r["index"], c["slug"], r["slug"])
            c["project_id"] = r["pid"]
            c["applied"] = {"date": today, "by": AGENT, "project_id": r["pid"], "sheet_row": r["sheet_row"],
                            "oo_row": r["oo_row"], "backup": bk.name, "plan_token": plan["token"]}
        p.write_text(json.dumps(data, ensure_ascii=False, indent=indent) + ("\n" if text.endswith("\n") else ""))
        print(f"marked {len(rs)} candidates applied in {src}")


def apply(path, verify_only_backup=None):
    plan = json.loads(Path(path).read_text())
    tok = hashlib.sha256(json.dumps({k: plan[k] for k in ("structural", "rows", "writes", "pre")}, sort_keys=True, default=str).encode()).hexdigest()[:16]
    assert tok == plan["token"], "plan file was edited"
    if verify_only_backup:
        bk = ROOT / "notes" / verify_only_backup
        assert bk.exists(), bk
    else:
        check_pre(plan)
        bk = backup(plan)
        print("backup:", bk)
        insert_rows(plan)
        write_cells(plan)
    verify(plan)
    mark_applied(plan, bk)
    out = Path(path).with_name(Path(path).stem + ".applied.json")
    out.write_text(json.dumps({"applied": datetime.now(ET).isoformat(timespec="seconds"), "backup": bk.name,
                               "token": plan["token"], "rows": plan["rows"]}, ensure_ascii=False, indent=1) + "\n")
    print("applied; receipt:", out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--staging", action="append", default=[], help="staging dir with staged_new.json (repeatable)")
    ap.add_argument("--commodity", default="gas", choices=sorted(TRACKER))
    ap.add_argument("--out", help="plan file path (default: <first staging dir>/../append-new-rows-<date>/plan.json)")
    ap.add_argument("--apply", metavar="PLAN", help="write this plan (gws-gem-write): ASK BAIRD FIRST")
    ap.add_argument("--verify-only", metavar="BACKUP_CSV", help="with --apply: re-run the read-back verification + applied markers for an already written plan (name of its backup csv in notes/); writes nothing to the sheet")
    a = ap.parse_args(argv)
    if a.apply:
        apply(a.apply, a.verify_only)
        return
    if not a.staging:
        ap.error("--staging DIR is required to plan")
    plan = build_plan(a.staging, a.commodity)
    summarize(plan)
    out = Path(a.out) if a.out else Path(a.staging[0]).parent / f"append-new-rows-{datetime.now(ET).strftime('%Y%m%d')}" / "plan.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(plan, ensure_ascii=False, indent=1, default=str) + "\n")
    print("plan:", out)


if __name__ == "__main__":
    main()
