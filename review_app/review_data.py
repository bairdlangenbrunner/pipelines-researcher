"""
Build the review app's dataset (work/review_data.json) for one scope from its pending
staging dirs.

    python review_app/review_data.py --country "Russia" --commodity gas \
        [--dirs DIR ...] [--exclude-pids P1,P2] [--snapshot PATH] [--out PATH]

Sources, per staging dir: staged_resolutions.json, staged_new.json, qc_flags.json,
escalations.json. NEVER staged_actions.json (a render-only re-join of the same records:
reading it would double every carried record) and never *.prior.json (backups). Only
those four exact filenames are opened, so both stay ignored by construction.

Kinds (docs/plans/2026-09-30_review-app.md, "Facts" item 2):
  lines  ref / fill / status / oo / route / new_row   (one decision each; push candidates)
  items  concern / wikidiff / routeqc / route_suggestion / monitor / flag / escalation /
         unresolved / confirmed / other              (a call + note, never a cell write)
`oo` is a modifier: a ref/fill/status record with tab == "operators_owners" is kind "oo"
and its current values come from the owners snapshot by ProjectID. A record that fits
no kind becomes an item of kind "other" and is counted -- never dropped.

Read-only over batches/ and data/. Deterministic apart from `built`.
"""
import argparse
import csv
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
for _p in (ROOT / "scripts", ROOT / "review_app"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import paths  # noqa: E402
import staged_store  # noqa: E402
import store  # noqa: E402
from ref_pairs import OO_PRIMARY  # noqa: E402
from build_ref_workbook import J, _annotate_kept_refs, _ref_cell_text  # noqa: E402

OO_TAB = "operators_owners"
LINE_KINDS = ("ref", "fill", "status", "oo", "route", "new_row")
ITEM_KINDS = ("concern", "wikidiff", "routeqc", "route_suggestion", "monitor", "flag",
              "escalation", "unresolved", "confirmed", "other")
_REF_CLASSES = {"REFS_ADDED", "REVERIFIED", "DEAD_LINK", "REF_BLOCKED", "REF_UNSUPPORTED"}
_NO_COL = 10 ** 6          # sort position for a column the snapshot does not have
_OO_OFFSET = 10 ** 4       # owners-tab columns sort after every tracker column
SCOPE_PID = "scope"        # pseudo-card for escalations / pid-less flags
COMMODITY_GLOB = {"gas": "GGIT_gas_snapshot_*.csv", "oil": "GOIT_oil_ngl_snapshot_*.csv"}


# ---------------------------------------------------------------- snapshots
def _read_csv(path, header_idx):
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    header = rows[header_idx]
    data = []
    for j in range(header_idx + 1, len(rows)):
        row = rows[j] + [""] * (len(header) - len(rows[j]))
        # sheet row == 1-based file record number (header at index 2 -> first data row 4)
        data.append((j + 1, dict(zip(header, row))))
    return header, data


class Snapshot:
    """One tab's rows: by ProjectID, each PID -> [(sheet_row, {col: value})]."""

    def __init__(self, path, header_idx):
        self.path = Path(path) if path else None
        self.header, self.rows, self.by_pid = [], [], defaultdict(list)
        self.col_idx = {}
        if self.path and self.path.exists():
            self.header, self.rows = _read_csv(self.path, header_idx)
            self.col_idx = {c: i for i, c in enumerate(self.header)}
            for sr, row in self.rows:
                pid = row.get("ProjectID", "").strip()
                if pid:
                    self.by_pid[pid].append((sr, row))

    def row(self, pid, sheet_row):
        """(resolved_sheet_row, row_dict, moved) for a PID; None if the PID is absent.
        A PID with several rows: the record's own row if it is one of them, else the
        first (moved=True)."""
        rows = self.by_pid.get(pid)
        if not rows:
            return None
        for sr, row in rows:
            if sr == sheet_row:
                return sr, row, False
        sr, row = rows[0]
        return sr, row, True


def _pick_snapshot(commodity, recorded, data_dir, override=None):
    """The NEWEST data/<commodity> snapshot (current values should be live-ish; sheet rows are
    re-resolved by ProjectID anyway), or --snapshot. `recorded` (what the staging dirs named)
    is kept on the dataset as scope.recorded_snapshot and is only the fallback when the data
    dir holds no snapshot for the commodity."""
    if override:
        return Path(override)
    found = sorted(Path(data_dir).glob(COMMODITY_GLOB[commodity]))
    if found:
        return found[-1]
    cands = [Path(data_dir) / c for c in recorded if c and (Path(data_dir) / c).exists()]
    return max(cands, key=lambda p: p.name) if cands else None


def _pick_owners(recorded, tracker_path, data_dir):
    """Owners snapshot with the tracker snapshot's stamp, else the newest, else a recorded one."""
    if tracker_path:
        stamp = tracker_path.stem.rsplit("_", 1)[-1]
        p = Path(data_dir) / f"GEM_operators_owners_snapshot_{stamp}.csv"
        if p.exists():
            return p
    found = sorted(Path(data_dir).glob("GEM_operators_owners_snapshot_*.csv"))
    if found:
        return found[-1]
    cands = [Path(data_dir) / c for c in recorded if c and (Path(data_dir) / c).exists()]
    return max(cands, key=lambda p: p.name) if cands else None


# ---------------------------------------------------------------- helpers
def _same(a, b):
    a, b = str(a if a is not None else "").strip(), str(b if b is not None else "").strip()
    if a == b:
        return True
    try:
        return float(a.replace(",", "")) == float(b.replace(",", ""))
    except ValueError:
        return False


def _urls(text):
    return [u.strip() for u in (text or "").replace("\n", ",").split(",") if u.strip().startswith("http")]


def _host(u):
    h = urlparse(u).netloc.lower()
    return h[4:] if h.startswith("www.") else h


def _listish(v):
    """proposed_refs is a list; tolerate a stray string (milestone-0 drift)."""
    if isinstance(v, list):
        return v
    return [v] if v else []


def _read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _rel(d, root):
    d = Path(d).resolve()
    try:
        return str(d.relative_to(Path(root).resolve().parent))
    except ValueError:
        return str(d)


# ---------------------------------------------------------------- classification
# Older FILL records name value columns by shorthand that is not a snapshot header.
# Display-only aliases so `current` / in_backend still resolve (Location has no 1:1 alias).
_ALIAS = {"Length": "LengthKnown", "LengthUnits": "LengthKnownUnits",
          "Start": "StartLocation", "End": "EndLocation"}


def _cell(row, col):
    if col in row:
        return row[col]
    return row.get(_ALIAS.get(col, ""), "")


def _has_col(tab, col):
    return col in tab.col_idx or _ALIAS.get(col) in tab.col_idx


def _is_oo(r):
    """tab == operators_owners, derived from the ref col when an older record lacks `tab`
    (same rule as staged_store._with_tab)."""
    return r.get("tab") == OO_TAB or (not r.get("tab") and (r.get("ref_col") or "") in OO_PRIMARY)


def classify(r):
    """-> ('line'|'item', kind) for a staged_resolutions record."""
    rc, ci, co = r.get("ref_col") or "", r.get("class_in") or "", r.get("class_out") or ""
    oo = _is_oo(r)
    if rc == "__VALIDITY__" or ci == "VALIDITY":
        return "item", ("confirmed" if (r.get("concern_type") or "none") == "none" else "concern")
    if rc == "__WIKIDIFF__" or ci == "WIKIDIFF":
        return "item", "wikidiff"
    if rc == "__ROUTEQC__" or ci == "ROUTEQC":
        return "item", "routeqc"
    if rc == "__ROUTE__" or ci == "ROUTE":
        if co == "ROUTE_CANDIDATE":
            return "line", "route"
        if co in ("ROUTE_SUGGESTED", "ROUTE_PARTIAL"):
            return "item", "route_suggestion"
        return "item", "other"
    if rc == "__STATUS__" or ci == "STATUS":
        if co in ("CHANGE_PROPOSED", "STALE"):
            return "line", "oo" if oo else "status"
        if co == "CONFIRMED":
            return "item", "confirmed"
        if co == "UNRESOLVED":
            return "item", "unresolved"
        return "item", "other"
    if co == "UNRESOLVED":
        return "item", "unresolved"
    if co == "CONFIRMED":
        return "item", "confirmed"
    if ci in ("FILL", "MISSING_REF_NO_COLUMN") and co == "REFS_ADDED":
        return "line", "oo" if oo else "fill"
    if co in _REF_CLASSES and rc:
        return "line", "oo" if oo else "ref"
    return "item", "other"


def _colid(r, kind):
    """The last element of the dedupe key: ref_col, or the value column for a fill."""
    rc = r.get("ref_col") or ""
    if kind == "status":
        return "__STATUS__"
    if kind == "route":
        return "__ROUTE__"
    if kind == "fill":
        return r.get("primary_value_col") or next(iter(r.get("values") or {}), "") or rc
    if kind == "oo":
        return "oo:" + (rc or r.get("primary_value_col") or "")
    if kind == "concern":
        return f"__VALIDITY__:{r.get('concern_type', '')}"
    if kind == "confirmed" and (rc == "__VALIDITY__" or r.get("class_in") == "VALIDITY"):
        return "__VALIDITY__:none"
    if kind == "wikidiff":
        return f"__WIKIDIFF__:{r.get('field', '')}"
    if kind == "routeqc":
        return f"__ROUTEQC__:{r.get('check', '')}"
    if kind == "route_suggestion":
        return f"__ROUTE__:{r.get('class_out', '')}"
    if kind in ("unresolved", "confirmed", "other") and r.get("class_in") == "FILL":
        # same ref_col as the ref unit on that cluster; the fill is identified by its value col
        return r.get("primary_value_col") or next(iter(r.get("values") or {}), "") or rc
    return rc or r.get("primary_value_col") or ""


# ---------------------------------------------------------------- entries
class Entry:
    """One reviewable object before dedupe/resolution."""

    def __init__(self, group, kind, pid, rec, dirp, src, colid, order):
        self.group, self.kind, self.pid, self.rec = group, kind, pid, rec
        self.dir, self.src, self.colid, self.order = dirp, src, colid, order
        self.also_in = []


def _dir_rank(d):
    """Primary-copy ordering: primary research before assembled packets, then newest
    (meta.generated, then run-dir name)."""
    gen = ""
    for fn in ("staged_resolutions.json", "staged_new.json"):
        f = Path(d) / fn
        if f.exists():
            try:
                gen = str(_read_json(f).get("meta", {}).get("generated", "") or "")
            except (OSError, ValueError):
                pass
            break
    assembled = staged_store._dir_mode(Path(d)) in staged_store._ASSEMBLED_MODES
    return (assembled, _neg(gen), _neg(Path(d).name))


class _neg(str):
    """str that sorts in reverse, so newest-first works inside one tuple key."""
    def __lt__(self, o): return str.__gt__(self, o)
    def __gt__(self, o): return str.__lt__(self, o)
    def __le__(self, o): return str.__ge__(self, o)
    def __ge__(self, o): return str.__le__(self, o)


def _load_dir(d, root, order0):
    """-> (entries, recorded_csvs, recorded_owner_csvs)."""
    d = Path(d)
    dirp = _rel(d, root)
    out, csvs, owners = [], [], []
    order = order0
    f = d / "staged_resolutions.json"
    if f.exists():
        data = _read_json(f)
        meta = data.get("meta", {})
        sc = meta.get("scope") or {}
        csvs.append(sc.get("csv") or "")
        owners.append(sc.get("owners_csv") or "")
        recs = data.get("resolutions", [])
        _annotate_kept_refs(recs, d)          # stamps kept_current_refs for _ref_cell_text
        for r in recs:
            group, kind = classify(r)
            pid = r.get("project_id") or ""
            if not pid:
                pid, group, kind = SCOPE_PID, "item", "other"
            out.append(Entry(group, kind, pid, r, dirp, "resolutions", _colid(r, kind), order))
            order += 1
    f = d / "staged_new.json"
    if f.exists():
        data = _read_json(f)
        sc = data.get("meta", {}).get("scope") or {}
        csvs.append(sc.get("csv") or "")
        for i, c in enumerate(data.get("candidates", [])):
            cls = c.get("class") or ""
            slug = c.get("slug") or (c.get("name") or f"cand{i}").lower().replace(" ", "-")
            if cls == "monitor":
                group, kind = "item", "monitor"
            elif cls in ("new_row", "matched_existing"):
                group, kind = "line", "new_row"
            else:
                group, kind = "item", "other"
            pid = c.get("matched_project_id") or c.get("project_id") or f"new:{slug}"
            out.append(Entry(group, kind, pid, c, dirp, "new", f"new:{slug}", order))
            order += 1
    f = d / "qc_flags.json"
    if f.exists():
        for fl in _read_json(f).get("flags", []):
            pid = fl.get("project_id") or SCOPE_PID
            cid = f"flag:{fl.get('check', '')}:{(fl.get('detail') or '')[:80]}"
            out.append(Entry("item", "flag", pid, fl, dirp, "flag", cid, order))
            order += 1
    f = d / "escalations.json"
    if f.exists():
        for i, e in enumerate(_read_json(f)):
            out.append(Entry("item", "escalation", SCOPE_PID, e, dirp, "escalation",
                             f"escalation:{(e.get('title') or str(i))[:120]}", order))
            order += 1
    return out, csvs, owners


# ---------------------------------------------------------------- build
def build(dirs, country, commodity, snapshot=None, owners=None, data_dir=None,
          exclude_pids=(), root=None):
    """-> (dataset, stats). `dirs` are staging dir paths; `root` is the batches root
    (repo-relative dir labels are taken against root.parent)."""
    root = Path(root or staged_store.BATCHES_ROOT)
    data_dir = Path(data_dir or ROOT / "data")
    exclude = set(exclude_pids)
    stats = {"dropped_na": 0, "not_in_snapshot": 0, "moved": 0, "status_covers": 0, "missing_cols": Counter(),
             "deduped": 0, "no_pid": 0, "excluded": 0, "cross_kind": 0, "line_over_item": 0, "warnings": []}

    ordered = sorted((Path(d) for d in dirs), key=_dir_rank)   # primary copy first
    entries, rec_csv, rec_own = [], [], []
    for i, d in enumerate(ordered):
        sc = staged_store._dir_scope(d)
        if sc is not None and sc[1] != commodity.lower():
            stats["warnings"].append(f"{d.name}: scope {sc} != commodity {commodity}")
        es, c, o = _load_dir(d, root, i * 10 ** 7)
        entries += es
        rec_csv += c
        rec_own += o

    recorded_snapshot = max((c for c in rec_csv if c), default="")   # what the staging dirs named
    snap_path = _pick_snapshot(commodity.lower(), rec_csv, data_dir, snapshot)
    snap = Snapshot(snap_path, 2)
    own_path = _pick_owners(rec_own, snap_path, data_dir)
    own = Snapshot(own_path, 1)

    # ---- resolve rows, drop N/A / excluded, compute dedupe keys
    kept, seen_in_dir = [], Counter()
    for e in entries:
        if e.pid in exclude:
            stats["excluded"] += 1
            continue
        rec = e.rec
        sr_rec = rec.get("sheet_row")
        try:
            sr_rec = int(sr_rec) if sr_rec not in (None, "") else None
        except (TypeError, ValueError):
            sr_rec = None
        e.sheet_row, e.moved, e.in_snapshot, e.tracker_row = sr_rec, False, True, None
        if e.pid not in (SCOPE_PID,) and not e.pid.startswith("new:"):
            tr = snap.row(e.pid, sr_rec)
            orow = own.row(e.pid, sr_rec) if e.kind == "oo" else None
            if tr is not None and tr[1].get("Status", "").strip() == "N/A":
                stats["dropped_na"] += 1
                continue
            if e.kind == "oo":
                if orow is not None:
                    # the record's sheet_row is the TRACKER row; the owners tab has its own
                    # row numbering, so a differing number is not drift
                    e.tracker_row, e.sheet_row, e.moved = sr_rec, orow[0], False
                else:
                    e.in_snapshot = False
            elif tr is not None:
                e.sheet_row, e.moved = tr[0], tr[2]
            else:
                e.in_snapshot = False
            if not e.in_snapshot:
                stats["not_in_snapshot"] += 1
            if e.moved:
                stats["moved"] += 1
        # unique key within a dir
        base = (e.dir, e.pid, e.sheet_row, e.colid)
        seen_in_dir[base] += 1
        n = seen_in_dir[base]
        if n > 1:
            e.colid = f"{e.colid}#{(e.rec.get('class_in') or e.kind)}{n}"
        kept.append(e)

    # ---- dedupe across dirs (primary copy first in `kept`)
    primary, by_key = [], {}
    for e in kept:
        k = (e.pid, e.sheet_row, e.colid)
        if k in by_key:
            p = by_key[k]
            if e.kind != p.kind:
                stats["cross_kind"] += 1
            if e.group == "line" and p.group == "item":
                # a proposal must never be hidden behind a newer copy that only says
                # "unresolved"/"confirmed": the line wins, the item's dir goes to also_in
                e.also_in = [p.dir] + [d for d in p.also_in if d != p.dir]
                by_key[k] = e
                primary[primary.index(p)] = e
                stats["line_over_item"] += 1
            else:
                if e.dir != p.dir and e.dir not in p.also_in:
                    p.also_in.append(e.dir)
            stats["deduped"] += 1
            continue
        by_key[k] = e
        primary.append(e)

    # ---- pipelines
    cards = {}
    for e in primary:
        card = cards.get(e.pid)
        if card is None:
            cards[e.pid] = card = {"pid": e.pid, "entries": []}
        card["entries"].append(e)

    pipelines = []
    for pid, card in cards.items():
        rows = snap.by_pid.get(pid, [])
        first = rows[0][1] if rows else {}
        rec0 = card["entries"][0].rec
        name = (first.get("PipelineName") or rec0.get("pipeline_name") or rec0.get("name")
                or rec0.get("title") or "")
        if pid == SCOPE_PID:
            name = "Scope-level items (escalations, flags with no ProjectID)"
        segs = [{"sheet_row": sr, "segment": r.get("SegmentName", "")} for sr, r in rows
                if r.get("Status", "").strip() != "N/A"]
        if not segs:
            sr0 = next((e.sheet_row for e in card["entries"] if e.sheet_row), None)
            segs = [{"sheet_row": sr0, "segment": rec0.get("segment_name", "")}] if sr0 else []
        lines, items, recs = [], [], {}
        for e in card["entries"]:
            obj = _line(e, snap, own, stats) if e.group == "line" else _item(e)
            (lines if e.group == "line" else items).append(obj)
            recs[obj["key"]] = e.rec
        lines = _fold_status_covers(lines, recs, stats)
        lines.sort(key=lambda l: (l["_sort"], l["key"]))
        for l in lines:
            del l["_sort"]
        items.sort(key=lambda i: (ITEM_KINDS.index(i["kind"]), i["key"]))
        pipelines.append({
            "pid": pid, "name": name, "segments": segs,
            "country": first.get("CountriesOrAreas", "") or rec0.get("countries", ""),
            "status": first.get("Status", ""),
            "wiki": first.get("Wiki", "") or rec0.get("wiki", ""),
            "lines": lines, "items": items,
        })
    pipelines.sort(key=lambda p: (p["pid"] == SCOPE_PID, p["pid"].startswith("new:"),
                                  p["segments"][0]["sheet_row"] if p["segments"] else _NO_COL,
                                  p["pid"]))

    data = {
        "built": datetime.now(ZoneInfo("America/New_York")).isoformat(timespec="seconds"),
        "scope": {"country": country, "commodity": commodity,
                  "snapshot": snap_path.name if snap_path else "",
                  "recorded_snapshot": recorded_snapshot},
        "dirs": [_rel(d, root) for d in sorted(ordered)],
        "columns": snap.header,
        "pipelines": pipelines,
    }
    overlay_decisions(data, root)
    stats["owners_snapshot"] = own_path.name if own_path else ""
    return data, stats


def overlay_decisions(data, root=None):
    """Lay each dir's review_log.jsonl over the dataset (store.overlay): every line carries
    decision / reviewed / decided_by / decided_at. `root` is the batches root (dir labels are
    relative to its parent). A rebuilt dataset therefore keeps every decision made so far."""
    base = Path(root).parent if root else ROOT
    return store.overlay(data, root=base)


# ---------------------------------------------------------------- line / item objects
def _line(e, snap, own, stats):
    r = e.rec
    kind = e.kind
    tier = r.get("tier") or ""
    base = {
        "key": f"{e.dir}::{e.pid}|{e.sheet_row}|{e.colid}",
        "kind": kind, "dir": e.dir, "also_in": e.also_in, "sheet_row": e.sheet_row,
        "sheet_row_moved": e.moved,
        "tier": tier, "independent": r.get("independent"),
        "link_live": r.get("link_live"), "source_language": r.get("source_language") or "",
        "class_in": r.get("class_in") or "", "class_out": r.get("class_out") or r.get("class") or "",
        "notes": r.get("researcher_notes") or "",
        "default": "accept" if tier == "high" else "hold",
        "decision": None, "reviewed": False,
    }
    if kind == "new_row":
        vals = r.get("values") or {}
        refs = r.get("refs") or {}
        base.update({
            "column": "", "ref_col": "", "value_cols": list(vals), "current": {}, "current_ref": "",
            "proposed_values": vals, "proposed_refs": refs,
            "ref_cell_text": {c: J(_listish(u)) for c, u in refs.items()},
            "verifications": r.get("verifications") or [], "in_backend": False,
            "name": r.get("name") or "", "slug": r.get("slug") or "",
            "matched_project_id": r.get("matched_project_id") or "",
            "class": r.get("class") or "",
            "_sort": 0,
        })
        return base

    oo = kind == "oo"
    tab = own if oo else snap
    srow = None
    for sr, row in tab.by_pid.get(e.pid, []):
        if sr == e.sheet_row:
            srow = row
    srow = srow or {}
    vals = r.get("values") or {}
    value_cols = list(r.get("value_cols") or []) if isinstance(r.get("value_cols"), list) else []
    for c in vals:
        if c not in value_cols:
            value_cols.append(c)
    ref_col = r.get("ref_col") or ""
    if ref_col.startswith("__"):
        ref_col = "Status [ref]" if ref_col == "__STATUS__" else ""
    primary = r.get("primary_value_col") or ""
    column = primary or (value_cols[0] if value_cols else "")
    for c in value_cols + ([ref_col] if ref_col else []):
        if tab.header and not _has_col(tab, c):
            stats["missing_cols"][("owners:" if oo else "") + c] += 1
    current = {c: _cell(srow, c) for c in value_cols}
    current_ref = srow.get(ref_col, "") if ref_col else ""
    refs = _listish(r.get("proposed_refs"))
    cell_text = _ref_cell_text(r) if (refs or r.get("class_out") == "REVERIFIED") else ""
    # in_backend: every proposed value already on the sheet AND every proposed URL already
    # in the current [ref] cell. A line with no proposed refs is judged on its values alone
    # (status STALE, a no-ref fill); a ref line with no proposed URL (REVERIFIED/DEAD_LINK/REF_*)
    # proposes nothing pasteable, so it is never "in backend".
    if kind in ("ref", "oo") and not vals and not refs:
        in_backend = False
    else:
        vals_ok = all(_same(_cell(srow, c), v) for c, v in vals.items() if v not in (None, ""))
        refs_ok = all(u in current_ref for u in refs)
        in_backend = bool(srow) and vals_ok and refs_ok and (bool(vals) or bool(refs))
        if kind == "ref":
            in_backend = bool(srow) and bool(refs) and refs_ok
    base.update({
        "column": column, "ref_col": ref_col, "value_cols": value_cols, "current": current,
        "current_ref": current_ref, "proposed_values": vals, "proposed_refs": refs,
        "ref_cell_text": cell_text, "verifications": r.get("verifications") or [],
        "in_backend": in_backend, "tab": OO_TAB if oo else "tracker",
    })
    if oo:
        base["tracker_sheet_row"] = e.tracker_row
    sort_col = "Status" if r.get("ref_col") == "__STATUS__" else (
        "RouteAccuracy" if kind == "route" else (ref_col or column))
    if oo:
        base["_sort"] = _OO_OFFSET + own.col_idx.get(sort_col, _NO_COL - _OO_OFFSET)
    else:
        base["_sort"] = snap.col_idx.get(sort_col, _NO_COL)
    if r.get("ref_col") == "__STATUS__" or r.get("class_in") == "STATUS":
        pub = {_host(u) for u in refs}
        base.update({
            "current_status": r.get("current_status") or srow.get("Status", ""),
            "proposed_status": r.get("proposed_status") or vals.get("Status", ""),
            "verdict": r.get("verdict") or "", "evidence_date": r.get("evidence_date") or "",
            "staleness_rule": r.get("staleness_rule") or "",
            "publishers": len(pub),      # distinct hosts among proposed refs (rule 4: <2 = single source)
        })
    if kind == "route":
        base.update({k: r.get(k) for k in (
            "geometry_file", "length_km", "sheet_length_km", "length_ratio",
            "suggested_route_accuracy", "qc_passed")})
        base["current_route_accuracy"] = r.get("current_route_accuracy") or srow.get("RouteAccuracy", "")
    return base


def _norm(v):
    return str(v or "").strip().lower()


def _fold_status_covers(lines, recs, stats):
    """One card per status call (Baird 2026-09-30): a status-review line and the refs-leg record
    that stages the SAME Status value onto `Status [ref]` are two staged records for one
    decision, so the ref record is folded into the status line instead of drawn as its own
    card. The status line gains `covers` (one entry per folded record: its key, dir, kind,
    classes, notes) and shows the union of both records' refs, composed the way the workbook
    composes two records on one cell (`extra_refs` -> _ref_cell_text). store.validate writes
    the status line's decision to every covered key in the same transaction, so each staged
    record still has its own decision record and the consumers need no change.

    Folded only when the partner AGREES: same row, tracker tab, `Status [ref]`, and a Status
    value equal to the proposed status. A ref record supporting the CURRENT status while the
    status leg proposes a change is contrary evidence and stays its own card."""
    status = {}
    for l in lines:
        if l["kind"] == "status" and _norm(l.get("proposed_status")):
            status.setdefault(l["sheet_row"], l)
    out = []
    for l in lines:
        s = status.get(l["sheet_row"])
        agrees = (s is not None and l is not s and l["kind"] in ("fill", "ref")
                  and l.get("ref_col") == "Status [ref]"
                  and _norm((l.get("proposed_values") or {}).get("Status")) == _norm(s["proposed_status"]))
        if not agrees:
            out.append(l)
            continue
        extra = [u for u in l.get("proposed_refs") or [] if u not in s["proposed_refs"]]
        if extra:
            s["proposed_refs"] = s["proposed_refs"] + extra
            s["ref_cell_text"] = _ref_cell_text(dict(recs[s["key"]], extra_refs=s["proposed_refs"]))
            s["publishers"] = len({_host(u) for u in s["proposed_refs"]})
        have = {v.get("url") for v in s["verifications"]}
        s["verifications"] = s["verifications"] + [v for v in l.get("verifications") or []
                                                   if v.get("url") not in have]
        s["in_backend"] = bool(s["in_backend"] and l["in_backend"])
        s.setdefault("covers", []).append({
            "key": l["key"], "dir": l["dir"], "kind": l["kind"], "sheet_row": l["sheet_row"],
            "ref_col": l.get("ref_col") or "", "class_in": l["class_in"], "class_out": l["class_out"],
            "tier": l["tier"], "independent": l["independent"], "notes": l["notes"],
            "verifications": [v for v in l.get("verifications") or [] if v.get("note")],
            "decision": None, "decided_by": None, "decided_at": None,
        })
        stats["status_covers"] += 1
    return out


def _item(e):
    r = e.rec
    obj = {k: v for k, v in r.items() if v not in ("", None, [], {}, False)}
    obj.pop("project_id", None)
    obj.update({
        "key": f"{e.dir}::{e.pid}|{e.sheet_row}|{e.colid}",
        "kind": e.kind, "dir": e.dir, "also_in": e.also_in, "sheet_row": e.sheet_row,
        "sheet_row_moved": e.moved,
        "contested": r.get("contested") or {},
        "default": None, "call": None, "reviewed": False,
    })
    return obj


# ---------------------------------------------------------------- CLI
def summary(data, stats):
    lines, items = Counter(), Counter()
    inb = 0
    for p in data["pipelines"]:
        for l in p["lines"]:
            lines[l["kind"]] += 1
            inb += bool(l["in_backend"])
        for i in p["items"]:
            items[i["kind"]] += 1
    out = [f"dirs: {len(data['dirs'])}  ({', '.join(Path(d).name for d in data['dirs'])})",
           f"snapshot: {data['scope']['snapshot']} (staging named {data['scope']['recorded_snapshot'] or 'none'})   owners: {stats.get('owners_snapshot', '')}",
           f"pipelines: {len(data['pipelines'])}",
           f"lines: {sum(lines.values())}  " + ", ".join(f"{k}={lines[k]}" for k in LINE_KINDS if lines[k]),
           f"items: {sum(items.values())}  " + ", ".join(f"{k}={items[k]}" for k in ITEM_KINDS if items[k]),
           f"dropped N/A records: {stats['dropped_na']}   in_backend lines: {inb}   "
           f"Status [ref] records folded into their status line: {stats['status_covers']}",
           f"deduped copies folded into also_in: {stats['deduped']} (cross-kind {stats['cross_kind']}, line kept over item {stats['line_over_item']})   "
           f"sheet_row moved: {stats['moved']}   not in snapshot: {stats['not_in_snapshot']}"]
    if stats["excluded"]:
        out.append(f"excluded by --exclude-pids: {stats['excluded']}")
    if stats["missing_cols"]:
        out.append(f"columns missing from snapshot: {dict(stats['missing_cols'])}")
    out += [f"WARN {w}" for w in stats["warnings"]]
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--country", required=True)
    ap.add_argument("--commodity", required=True, choices=["gas", "oil"])
    ap.add_argument("--dirs", nargs="*", default=None, help="explicit staging dirs (skips discovery)")
    ap.add_argument("--exclude-pids", default="", help="comma-separated ProjectIDs to drop")
    ap.add_argument("--snapshot", default=None, help="tracker snapshot CSV (default: the newest data/ snapshot)")
    ap.add_argument("--owners", default=None, help="owners snapshot CSV (default: same stamp as the tracker snapshot, else newest)")
    ap.add_argument("--batches-root", default=None, help="batches root (default: repo batches/)")
    ap.add_argument("--data-dir", default=None, help="snapshot dir (default: repo data/)")
    ap.add_argument("--out", default=None, help="default: work/review_data.json")
    a = ap.parse_args(argv)
    root = Path(a.batches_root) if a.batches_root else staged_store.BATCHES_ROOT
    if a.dirs:
        dirs = [Path(d) for d in a.dirs]
    else:
        dirs = staged_store.discover_staging_dirs(a.country, a.commodity, root=root,
                                                  include_assembled=True)
    if not dirs:
        sys.exit(f"no staging dirs found for {a.country} {a.commodity}")
    data, stats = build(dirs, a.country, a.commodity, snapshot=a.snapshot, owners=a.owners,
                        data_dir=a.data_dir, exclude_pids=[p for p in a.exclude_pids.split(",") if p],
                        root=root)
    out = Path(a.out) if a.out else paths.work_dir() / "review_data.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    print(summary(data, stats), file=sys.stderr)
    print(f"wrote {out} ({out.stat().st_size:,} bytes)", file=sys.stderr)
    return data


if __name__ == "__main__":
    main()
