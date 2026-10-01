"""
The review app's decision store (milestone 3). Port of the LNG app's store.py, reshaped for
the two sidecars that live IN each staging dir and are committed with the batch:

    review_log.jsonl        append-only truth: every decision and every undo, one record per line
    review_decisions.json   derived: {"generated": ts, "decisions": {key: latest record}}

Record shape: {key, dir, pid, sheet_row, ref_col, kind, decision, suggested_value, note,
reviewer, ts, undecided, basis}; `reviewer` is a person's initials (initials()) or a machine
reviewer; `basis` (review_data.basis) names the backend cells the call was made against. A record
that went through the ledger (review_app/ledger.py) also carries id, scope, batch, snapshot, origin. An undo appends a record with `undecided: true`; nothing is ever
deleted from the log. A line that `covers` other staged records (a status line and the
`Status [ref]` record folded into it) writes one more record per covered key, same call, with
`via` = the line's key. A `suggest` that took a validity concern's candidate value instead of the
proposal (review_data._attach_rivals; request field `rival` = the concern's key) carries `rival`.
Nothing here touches the sheet, the routes repo or staged_*.json.
"""
import json
import os
import re
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
# them) but are not a click, so `reviewed()` leaves the line undecided. `backend sync`
# (sync_backend, after a refresh) and `push` (push.py, after a verified sheet write) write them.
MACHINE_REVIEWERS = {"backend sync", "push"}
SYNC_REVIEWER = "backend sync"
# A person is recorded by their first and last initials, never their full name (Baird
# 2026-10-01): "Baird Langenbrunner" and baird.langenbrunner@globalenergymonitor.org both
# record as "BL". The private Google store keeps the full address (pull.py maps it back).
_INITIALS_RE = re.compile(r"^[A-Z]{1,3}$")
_EMAIL_RE = re.compile(r"^([^@\s]+)@[^@\s]+\.[^@\s]+$")
LINE_KINDS = ("ref", "fill", "status", "oo", "route", "new_row")
ITEM_KINDS = ("concern", "wikidiff", "routeqc", "route_suggestion", "monitor", "flag", "escalation",
              "unresolved", "confirmed", "other")
# The call vocabulary per item kind. A concern's call settles the validity question
# (confirmed = it stands, dismissed = closed, needs_research = goes to an Update worklist).
# A concern never holds a line: a line it contests is decided on its own, and the two calls
# that answer a concern from the line (accept proposed -> dismissed, accept its candidate ->
# confirmed) are written by `decide` in the same transaction. Everything else is
# noted / todo / dismissed. Items never write a cell.
CONCERN_CALLS = ("confirmed", "dismissed", "needs_research")
OTHER_CALLS = ("noted", "todo", "dismissed")
ITEM_CALLS = {k: (CONCERN_CALLS if k == "concern" else OTHER_CALLS) for k in ITEM_KINDS}

_LOCK = threading.Lock()     # one process-wide lock around every read-modify-write of a sidecar


def initials(who):
    """A person -> their first + last initials, uppercased: "Baird Langenbrunner" -> "BL",
    baird.langenbrunner@globalenergymonitor.org -> "BL" (the local part split on . _ - +), a
    one-part name or address -> its first letter. A machine reviewer, a value already in initials
    form, and an empty value come back unchanged, so applying it twice is a no-op."""
    v = str(who or "").strip()
    if not v or v in MACHINE_REVIEWERS or _INITIALS_RE.match(v):
        return who
    m = _EMAIL_RE.match(v)
    parts = [t for t in re.split(r"[._+\-]+" if m else r"\s+", m.group(1) if m else v) if t[:1].isalpha()]
    if not parts:
        return who
    return (parts[0][0] + (parts[-1][0] if len(parts) > 1 else "")).upper()


class Invalid(ValueError):
    """A request the store refuses before writing anything (HTTP 400)."""


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
    Items get `call` / `call_note` (the latest item call; None after an undo or with no record)
    plus reviewed / decided_by / decided_at. Run this before `validate` sees the dataset: `decide`
    reads the overlaid `call` to know which concern calls an accept still owes."""
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
                else:
                    o["call"] = live.get("call") if live else None
                    o["call_note"] = live.get("note", "") if live else None
                o["reviewed"] = reviewed(rec)
                o["decided_by"] = rec.get("reviewer") if live else None
                o["decided_at"] = rec.get("ts") if live else None
                if live and live.get("decision") == "suggest" and grp == "lines":
                    o["suggested_value"] = live.get("suggested_value", "")
                    o["decision_note"] = live.get("note", "")
                    o["rival"] = live.get("rival") or None
                elif grp == "lines":
                    o["rival"] = None
                if grp == "lines" and o.get("covers"):
                    # a covered record (review_data._fold_status_covers) is decided with its
                    # line; `uncovered` names the ones whose own record says something else
                    # (the line was decided before the record was folded in, or the record
                    # was decided as its own card) until the line is decided again.
                    for c in o["covers"]:
                        cd = c.get("dir")
                        if cd not in logs:
                            logs[cd] = latest(read_log(dirs[cd])) if cd in dirs else {}
                        crec = logs[cd].get(c["key"])
                        clive = crec if crec and not crec.get("undecided") else None
                        c["decision"] = clive["decision"] if clive else None
                        c["decided_by"] = clive.get("reviewer") if clive else None
                        c["decided_at"] = clive.get("ts") if clive else None
                    o["uncovered"] = [c["key"] for c in o["covers"] if c["decision"] != o["decision"]]
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


def open_concerns(pipeline):
    """Validity concerns on this pipeline with a contested map and no call yet."""
    return [it for it in pipeline.get("items", [])
            if it.get("kind") == "concern" and not it.get("call") and isinstance(it.get("contested"), dict)]


def contested_cols(pipeline):
    """Columns named by an open validity concern on this pipeline (`call` still empty)."""
    cols = set()
    for it in open_concerns(pipeline):
        cols.update(it["contested"])
    return cols


def line_cols(line):
    """Columns a line touches: its column, its value columns, Status for a status line."""
    cols = {line.get("column")} | set(line.get("value_cols") or [])
    if line.get("kind") == "status":
        cols.add("Status")
    return {c for c in cols if c}


def proposed_on(line, col):
    """The value the line proposes on `col`, stripped ("" = nothing proposed there): its
    proposed_values entry, or the proposed status of a status line on Status."""
    pv = line.get("proposed_values") or {}
    v = pv.get(col)
    if (v is None or str(v).strip() == "") and col == "Status" and line.get("kind") == "status":
        v = line.get("proposed_status")
    return "" if v is None else str(v).strip()


def resolves(line, concern):
    """Sorted contested columns of `concern` on which the line IS the resolution: the concern's
    contested value is non-empty and equals the line's proposed value on that column (both
    stripped strings). An empty contested value means "unsourced", never a proposed blank, so it
    never matches."""
    cont = concern.get("contested") or {}
    return sorted(c for c in line_cols(line) & set(cont)
                  if str(cont[c]).strip() and str(cont[c]).strip() == proposed_on(line, c))


def rival_of(line, concern_key):
    """The line's rival entry for `concern_key` that carries a differing candidate (a second
    proposal the reviewer can take), or None."""
    for rv in line.get("rivals") or []:
        if rv.get("key") == concern_key and rv.get("cols"):
            return rv
    return None


def validate(records, data, reviewer=None):
    """Normalized decision records (reviewer / ts stamped later), or Invalid; nothing is written
    for a bad request. A record is {key, decision, suggested_value?, note?} or {key, undo: true}
    (an undo is stored as undecided: true), or {key, rival: <concern key>} to take a validity
    concern's candidate value instead of the proposal: stored as a `suggest` whose
    suggested_value is the candidate (review_data.rival_value) and which carries `rival`; the
    decision, if given, must be `suggest`. A line is never refused because a concern contests
    it: the concern's own call is written by `decide` alongside."""
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
            raise Invalid(f"record {i}: {key!r} is an item, not a line (use /api/item)")
        undo = bool(r.get("undo") or r.get("undecided"))
        decision = r.get("decision")
        if undo and not decision:
            decision = obj.get("default") or "hold"      # an undo record still carries a decision field
        rival = str(r.get("rival") or "") if not undo else ""
        if rival and not decision:
            decision = "suggest"
        if not undo and not decision:
            raise Invalid(f"record {i}: no decision given (a bare key never defaults to accept)")
        if decision not in DECISIONS:
            raise Invalid(f"record {i}: decision {decision!r} is not one of {', '.join(sorted(DECISIONS))}")
        note = str(r.get("note") or "")
        sv = str(r.get("suggested_value") or "")
        if rival:
            rv = rival_of(obj, rival)
            if rv is None:
                raise Invalid(f"record {i}: {rival!r} is not a concern with a candidate value on {key!r}")
            if decision != "suggest":
                raise Invalid(f"record {i}: taking a concern's candidate is recorded as suggest, not {decision}")
            sv = sv.strip() or rv["value"]
        if decision == "suggest" and not undo and not (sv.strip() or note.strip()):
            raise Invalid(f"record {i}: a suggestion needs a suggested_value or a note")
        rec = {"key": key, "dir": obj["dir"], "pid": pipe["pid"], "sheet_row": obj.get("sheet_row"),
               "ref_col": obj.get("ref_col") or obj.get("column") or "", "kind": obj["kind"],
               "decision": decision, "suggested_value": sv, "note": note,
               "reviewer": reviewer, "ts": None, "undecided": undo}
        if obj.get("basis"):        # the backend cells this call was made against (review_data.basis)
            rec["basis"] = obj["basis"]
        if rival:
            rec["rival"] = rival
        out.append(rec)
        out.extend(cover_records(obj, rec))
    return out


def cover_records(line, rec):
    """The same call on every record the line covers (a status line and the `Status [ref]`
    record folded into it are one decision): one record per covered key, in that record's own
    dir, carrying `via` = the line's key. Written in the same transaction as the line's."""
    return [dict(rec, key=c["key"], dir=c["dir"], sheet_row=c.get("sheet_row"),
                 ref_col=c.get("ref_col") or "", kind=c["kind"], via=rec["key"])
            for c in line.get("covers") or []]


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


def _write(recs, dirs, stamp=True):
    """Per touched dir (caller holds _LOCK): append to review_log.jsonl and regenerate
    review_decisions.json atomically; on failure roll every touched log back to its previous
    byte length. `recs` already carry reviewer; ts is stamped here (`stamp=False` keeps the ts
    each record already has: records mirrored from the Google store). Returns recs."""
    ts = now()
    by_dir = {}
    for r in recs:
        if stamp:
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


def decide(records, data, reviewer, dirs=None, root=None, sink=None):
    """Validate, then write (under the process lock) to each touched dir's sidecars. `data` must
    already be overlaid (server.App does it) so the concern calls below see the live `call`.
    Returns the records written (with reviewer and ts): the line records, then any concern item
    records.

    `sink(recs, dirs)` replaces the write: ledger.Ledger.sink appends the records to the Google
    decision store FIRST and then to the sidecars (the store is the single source of truth, the
    sidecars its committed mirror); the default writes the sidecars alone. A sink runs under
    _LOCK, so it calls _write, never append_records.

    A person's line call answers a concern from the line, in the same transaction:
    - accept of a line that `resolves` an open concern (the candidate equals the proposal)
      writes `dismissed` on it ("resolved by accepted <col> fill");
    - a `rival` suggest (the concern's candidate taken instead of the proposal) writes
      `confirmed` on it ("candidate accepted on <col>"), unless it is already confirmed.
    A concern that already has a call is otherwise left alone; machine reviewers, hold, reject
    and undo write no concern call. Undoing the line call does NOT re-open the concern; undo the
    item call by hand."""
    reviewer = initials(reviewer)
    dirs = dirs if dirs is not None else dir_paths(data, root)
    with _LOCK:
        recs = validate(records, data, reviewer)
        items = []
        if reviewer not in MACHINE_REVIEWERS:
            owed = concern_calls(recs, data)
            items = validate_items(owed, data, reviewer) if owed else []
        return (sink or _write)(recs + items, dirs)


def concern_calls(recs, data):
    """The item-call requests a batch of validated line records owes (see `decide`), in the order
    the concerns are first met: {key, call, note} per concern. A confirmed-by-candidate call
    wins over a dismissal of the same concern in one request."""
    idx = index(data)
    calls = {}
    for r in recs:
        if r["undecided"] or r.get("via"):
            continue
        pipe, line, _ = idx[r["key"]]
        if r["decision"] == "accept":
            for c in open_concerns(pipe):
                cols = resolves(line, c)
                if not cols:
                    continue
                cur = calls.get(c["key"])
                if cur and cur["call"] == "confirmed":
                    continue
                have = cur["cols"] if cur else []
                calls[c["key"]] = {"call": "dismissed", "cols": have + [x for x in cols if x not in have]}
        elif r["decision"] == "suggest" and r.get("rival"):
            rv = rival_of(line, r["rival"])
            _, concern, _ = idx[r["rival"]]
            if concern.get("call") == "confirmed":
                continue
            calls[r["rival"]] = {"call": "confirmed", "cols": list(rv["cols"])}
    return [{"key": k, "call": v["call"],
             "note": ("resolved by accepted " if v["call"] == "dismissed" else "candidate accepted on ")
                     + ", ".join(v["cols"]) + (" fill" if v["call"] == "dismissed" else "")}
            for k, v in calls.items()]


def append_records(recs, dirs, sink=None):
    """Append records that were ALREADY decided elsewhere (the Google store, via pull.py) to
    their staging dirs' sidecars, exactly as stored: reviewer, ts and every extra field are
    kept, nothing is validated against a dataset or re-stamped. `dirs` is {label: Path}; a
    record whose dir is not in it is refused (Invalid) and nothing is written. `sink` as in
    decide (publish.carry_forward hands the ledger's; pull.mirror never does: its records CAME
    from the store)."""
    with _LOCK:
        return (sink or _write)(list(recs), dirs, stamp=False) if recs else []


def validate_items(records, data, reviewer=None):
    """Normalized item call records, or Invalid. A record is {key, call, note?} or {key, undo: true}.
    The call must be in ITEM_CALLS for the item's kind."""
    if not isinstance(records, list) or not records:
        raise Invalid("expected a non-empty list of item records")
    idx = index(data)
    out = []
    for i, r in enumerate(records):
        if not isinstance(r, dict):
            raise Invalid(f"record {i}: not an object")
        key = r.get("key")
        if key not in idx:
            raise Invalid(f"record {i}: unknown key {key!r}")
        pipe, obj, grp = idx[key]
        if grp != "items":
            raise Invalid(f"record {i}: {key!r} is a line, not an item (use /api/decide)")
        undo = bool(r.get("undo") or r.get("undecided"))
        call = "" if undo else str(r.get("call") or "")
        vocab = ITEM_CALLS.get(obj.get("kind"), OTHER_CALLS)
        if not undo and call not in vocab:
            raise Invalid(f"record {i}: call {call!r} is not one of {', '.join(vocab)} for a {obj.get('kind')} item")
        out.append({"key": key, "dir": obj["dir"], "pid": pipe["pid"], "kind": obj["kind"], "call": call,
                    "note": str(r.get("note") or ""), "reviewer": reviewer, "ts": None, "undecided": undo})
    return out


def record_items(records, data, reviewer, dirs=None, root=None, sink=None):
    """Item calls into the SAME review_log.jsonl / review_decisions.json as line decisions (an item
    key and a line key never coincide). Shape: {key, dir, pid, kind, call, note, reviewer, ts,
    undecided}; an undo is a record with undecided: true. Returns the records written."""
    reviewer = initials(reviewer)
    dirs = dirs if dirs is not None else dir_paths(data, root)
    with _LOCK:
        return (sink or _write)(validate_items(records, data, reviewer), dirs)


def sync_backend(data, dirs, snapshot="", sink=None):
    """After a fresh pull + rebuild: every line the snapshot already holds (`in_backend`) that no
    person has decided gets a `backend sync` accept record. A machine record is not `reviewed`,
    so the line stays undecided in the queue (the UI shows "in backend"). Lines that already
    carry a live backend-sync record are left alone (idempotent). Returns the records written."""
    note = f"already in backend after refresh {snapshot}".rstrip()
    logs, recs = {}, []
    with _LOCK:
        for p in data.get("pipelines", []):
            for l in p.get("lines", []):
                if not l.get("in_backend"):
                    continue
                d = l.get("dir")
                if d not in logs:
                    logs[d] = latest(read_log(dirs[d])) if d in dirs else {}
                rec = logs[d].get(l["key"])
                if rec and not rec.get("undecided"):       # a person's call, or already synced
                    continue
                mine = {"key": l["key"], "dir": d, "pid": p["pid"], "sheet_row": l.get("sheet_row"),
                        "ref_col": l.get("ref_col") or l.get("column") or "", "kind": l["kind"],
                        "decision": "accept", "suggested_value": "", "note": note,
                        "reviewer": SYNC_REVIEWER, "ts": None, "undecided": False}
                recs.append(mine)
                for c in cover_records(l, mine):           # same rule per covered record
                    if c["dir"] not in logs:
                        logs[c["dir"]] = latest(read_log(dirs[c["dir"]])) if c["dir"] in dirs else {}
                    crec = logs[c["dir"]].get(c["key"])
                    if not (crec and not crec.get("undecided")):
                        recs.append(c)
        return (sink or _write)(recs, dirs) if recs else []
