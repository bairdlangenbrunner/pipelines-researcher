"""
The review app's decision store (milestone 3). Port of the LNG app's store.py, reshaped for
the two sidecars that live IN each staging dir and are committed with the batch:

    review_log.jsonl        append-only truth: every decision and every undo, one record per line
    review_decisions.json   derived: {"generated": ts, "decisions": {key: latest record}}

Record shape: {key, dir, pid, sheet_row, ref_col, kind, decision, suggested_value, note,
reviewer, ts, undecided}. An undo appends a record with `undecided: true`; nothing is ever
deleted from the log. Nothing here touches the sheet, the routes repo or staged_*.json.
"""
import json
import os
import threading
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
ET = ZoneInfo("America/New_York")
DECISIONS = {"accept", "hold", "reject", "suggest"}
LOG_NAME = "review_log.jsonl"
DERIVED_NAME = "review_decisions.json"
# Reviewers that are machines, not people: their records are honest (they name what wrote
# them) but are not a click, so `reviewed()` leaves the line undecided. Nothing writes
# them yet (backend sync = milestone 4, push = phase 1b).
MACHINE_REVIEWERS = {"backend sync", "push"}
LINE_KINDS = ("ref", "fill", "status", "oo", "route", "new_row")

_LOCK = threading.Lock()     # one process-wide lock around every read-modify-write of a sidecar


class Invalid(ValueError):
    """A request the store refuses before writing anything (HTTP 400)."""


class Contested(Invalid):
    """Accept refused: a validity concern contests a column on this line and has no call (HTTP 409)."""


# ---- reading ---------------------------------------------------------------------

def read_jsonl(path):
    """Records of a JSONL file; a torn last line (crash mid-append) is skipped, not fatal."""
    out = []
    path = Path(path)
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def read_log(d):
    return read_jsonl(Path(d) / LOG_NAME)


def latest(records, field="key"):
    """field value -> the last record carrying it (the log is append-only; latest wins)."""
    out = {}
    for r in records:
        if r.get(field):
            out[r[field]] = r
    return out


def reviewed(rec):
    """True when the latest record is a person's call: not a machine's, not an undo."""
    return bool(rec) and rec.get("reviewer") not in MACHINE_REVIEWERS and not rec.get("undecided")


def dir_paths(data, root=None):
    """{dir label: Path}. Labels are relative to the repo root (review_data._rel), or absolute."""
    base = Path(root) if root else ROOT
    return {d: base / d for d in data.get("dirs", [])}


def overlay(data, dirs=None, root=None):
    """Fill `decision`, `reviewed`, `decided_by`, `decided_at` on every line and item of `data`
    (in place; returns it) from each dir's review_log.jsonl. `decision` is the latest record's
    call (None after an undo or with no record); `reviewed` says whether a person made it.
    Items (milestone 4) get reviewed/decided_by/decided_at only; `call` is left to that milestone."""
    dirs = dirs if dirs is not None else dir_paths(data, root)
    logs = {}
    for p in data.get("pipelines", []):
        for grp in ("lines", "items"):
            for o in p.get(grp, []):
                d = o.get("dir")
                if d not in logs:
                    logs[d] = latest(read_log(dirs[d])) if d in dirs else {}
                rec = logs[d].get(o["key"])
                live = rec if rec and not rec.get("undecided") else None
                if grp == "lines":
                    o["decision"] = live["decision"] if live else None
                o["reviewed"] = reviewed(rec)
                o["decided_by"] = rec.get("reviewer") if live else None
                o["decided_at"] = rec.get("ts") if live else None
                if live and live.get("decision") == "suggest" and grp == "lines":
                    o["suggested_value"] = live.get("suggested_value", "")
                    o["decision_note"] = live.get("note", "")
    return data


# ---- validation ------------------------------------------------------------------

def now():
    return datetime.now(ET).isoformat(timespec="seconds")


def index(data):
    """key -> (pipeline, object, group) for every line and item."""
    out = {}
    for p in data.get("pipelines", []):
        for grp in ("lines", "items"):
            for o in p.get(grp, []):
                out[o["key"]] = (p, o, grp)
    return out


def contested_cols(pipeline):
    """Columns named by an open validity concern on this pipeline (`call` still empty)."""
    cols = set()
    for it in pipeline.get("items", []):
        c = it.get("contested")
        if it.get("kind") == "concern" and not it.get("call") and isinstance(c, dict):
            cols.update(c)
    return cols


def locked_by(pipeline, line):
    """Contested columns this line touches (its column, its value columns, Status for a status
    line), as a sorted list; non-empty means accept is refused until the concern has a call."""
    cols = {line.get("column")} | set(line.get("value_cols") or [])
    if line.get("kind") == "status":
        cols.add("Status")
    return sorted(c for c in cols & contested_cols(pipeline) if c)


def validate(records, data, reviewer=None):
    """Normalised decision records (reviewer / ts stamped later), or Invalid; nothing is written
    for a bad request. A record is {key, decision, suggested_value?, note?} or {key, undo: true}
    (an undo is stored as undecided: true)."""
    if not isinstance(records, list) or not records:
        raise Invalid("expected a non-empty list of decision records")
    idx = index(data)
    out = []
    for i, r in enumerate(records):
        if not isinstance(r, dict):
            raise Invalid(f"record {i}: not an object")
        key = r.get("key")
        if key not in idx:
            raise Invalid(f"record {i}: unknown key {key!r}")
        pipe, obj, grp = idx[key]
        if grp != "lines" or obj.get("kind") not in LINE_KINDS:
            raise Invalid(f"record {i}: {key!r} is an item, not a line (item calls arrive in milestone 4)")
        undo = bool(r.get("undo") or r.get("undecided"))
        decision = r.get("decision")
        if undo and not decision:
            decision = obj.get("default") or "hold"      # an undo record still carries a decision field
        if not undo and not decision:
            raise Invalid(f"record {i}: no decision given (a bare key never defaults to accept)")
        if decision not in DECISIONS:
            raise Invalid(f"record {i}: decision {decision!r} is not one of {', '.join(sorted(DECISIONS))}")
        note = str(r.get("note") or "")
        sv = str(r.get("suggested_value") or "")
        if decision == "suggest" and not undo and not (sv.strip() or note.strip()):
            raise Invalid(f"record {i}: a suggestion needs a suggested_value or a note")
        if decision == "accept" and not undo:
            held = locked_by(pipe, obj)
            if held:
                raise Contested(f"record {i}: {key!r} is held: a validity concern contests "
                                f"{', '.join(held)} and has no call yet")
        out.append({"key": key, "dir": obj["dir"], "pid": pipe["pid"], "sheet_row": obj.get("sheet_row"),
                    "ref_col": obj.get("ref_col") or obj.get("column") or "", "kind": obj["kind"],
                    "decision": decision, "suggested_value": sv, "note": note,
                    "reviewer": reviewer, "ts": None, "undecided": undo})
    return out


# ---- writing ---------------------------------------------------------------------

def atomic_write(path, text):
    path = Path(path)
    tmp = path.with_name(f".{path.name}.tmp")
    try:
        with open(tmp, "w", encoding="utf-8", newline="") as f:
            f.write(text)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


def append_jsonl(path, records):
    """Append records; returns the file's prior size so a failed step can roll it back."""
    path = Path(path)
    size = path.stat().st_size if path.exists() else 0
    with open(path, "a", encoding="utf-8", newline="") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())
    return size


def rollback(path, size):
    path = Path(path)
    if size == 0:
        path.unlink(missing_ok=True)
    else:
        with open(path, "r+b") as f:
            f.truncate(size)


def write_derived(d, ts):
    """Regenerate <d>/review_decisions.json from the whole log (latest record per key)."""
    body = {"generated": ts, "decisions": latest(read_log(d))}
    atomic_write(Path(d) / DERIVED_NAME, json.dumps(body, indent=1, ensure_ascii=False) + "\n")


def decide(records, data, reviewer, dirs=None, root=None):
    """Validate, then per touched dir (under the process lock): append to review_log.jsonl,
    regenerate review_decisions.json atomically; if that fails, roll the log back to its
    previous byte length. Returns the records written (with reviewer and ts)."""
    dirs = dirs if dirs is not None else dir_paths(data, root)
    with _LOCK:
        recs = validate(records, data, reviewer)
        ts = now()
        by_dir = {}
        for r in recs:
            r["ts"] = ts
            if r["dir"] not in dirs:
                raise Invalid(f"staging dir not known to the server: {r['dir']}")
            by_dir.setdefault(r["dir"], []).append(r)
        done = []          # (dir, log path, prior size) of dirs touched so far, for a multi-dir rollback
        try:
            for label, rs in by_dir.items():
                log = Path(dirs[label]) / LOG_NAME
                size = append_jsonl(log, rs)
                done.append((dirs[label], log, size))
                write_derived(dirs[label], ts)
        except Exception:
            for d, log, size in done:
                rollback(log, size)
            for d, log, size in done[:-1]:      # dirs whose derived file already moved: re-derive
                try:
                    write_derived(d, ts)
                except Exception:
                    pass
            raise
        return recs
