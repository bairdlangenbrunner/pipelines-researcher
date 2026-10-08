"""
The decision ledger: ONE place every review decision lands, whoever makes it and however.

    python review_app/ledger.py status                       # store configured? who writes? last row
    python review_app/ledger.py decide --key KEY --decision accept|hold|reject|suggest [--note N] [--value V]
    python review_app/ledger.py undo --key KEY
    python review_app/ledger.py item --key KEY --call confirmed|dismissed|needs_research|noted|todo|dismissed [--note N]
    python review_app/ledger.py decide --records FILE.json   # [{key, decision, note?, suggested_value?} | {key, undo: true}]

The ledger IS the `log` tab of the store spreadsheet (review_app/google.json: store_sheet_id), the
same tab the served Google page (review_app/gas/Code.gs) appends to, one row per record, in the
same 19 columns (COLS; the test asserts the two lists agree). Everything that used to write a
staging dir's review_log.jsonl directly now writes HERE FIRST and the sidecars second:

    served Google page  -> Code.gs write_/append_          (origin 'gas')
    loopback server     -> store.decide(..., sink=Ledger.sink)   (origin 'local')
    a Claude chat       -> `ledger.py decide`              (origin 'chat'; then review_app/push.py)
    push.py             -> `push` machine records          (origin 'push')
    refresh / publish   -> `backend sync`, carry-forward   (origin 'sync' / 'publish')
    artifact page       -> import_log.py (the page's download or shared log; origin 'artifact')

so the store holds every decision, the sidecars are its committed mirror (pull.py fills in whatever
was written by the Google page), and the workbook, the push plan and the published dataset all read
one history. Appending to the `log` tab is the standing authorization Baird gave 2026-10-01 (CLAUDE.md
"Hard requirements"); it is the ONLY Google write this module makes, through gws-gem-write, and it
never touches the backend sheet (that is push.py, asked per run).

Rules
  * the store comes first. A record is appended to the sheet, read back by `id`, and only then
    written to the sidecar. If the store cannot be reached the decision is REFUSED (StoreError ->
    HTTP 502 on the server, exit 2 on the CLI) and nothing is written anywhere: there is no
    offline mode, because an offline decision is exactly the divergence this module exists to end.
    `--no-store` on server.py is for tests and dev only and says so on every start.
  * the store keeps the reviewer's EMAIL (Code.gs compares addresses when it refuses a clash); the
    sidecars keep initials (store.initials, Baird 2026-10-01). Machine reviewers are kept as is.
  * a record's `id` is a uuid4 stamped here (an id already present -- a carry-forward's `~rekey` --
    is kept), so pull.py's mirror, which dedupes by id, never writes the same record twice.
  * the sheet append is verified: the rows the API says it wrote are re-read and their `id` column
    must be these records' ids. A mismatch (Code.gs's getLastRow()+1 landing on the same rows in
    the same instant) is retried once, then refused.
"""
import argparse
import json
import re
import sys
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for p in (ROOT / "scripts", HERE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import pull  # noqa: E402
import store  # noqa: E402

# Code.gs COLS, verbatim (tests/test_review_ledger.py parses the .gs and asserts equality)
COLS = ["ts", "reviewer", "rec", "pid", "sheet_row", "ref_col", "kind", "decision", "call", "suggested_value",
        "note", "undecided", "via", "batch", "snapshot", "key", "id", "scope", "json"]
LOG_TAB = pull.LOG_TAB
ORIGINS = ("gas", "local", "chat", "push", "sync", "publish", "artifact")
MAX_JSON = 49000          # Code.gs refuses a longer record; a cell holds 50k chars
_FORMULA = re.compile(r"^[=+\-@]")
_RANGE = re.compile(r"^'?(?P<tab>[^'!]+)'?!(?P<c1>[A-Z]+)(?P<r1>\d+)(?::(?P<c2>[A-Z]+)(?P<r2>\d+))?$")


class StoreError(RuntimeError):
    """The store could not be written (or read back as written): nothing was recorded anywhere."""


def scope_id(countries, commodity, batch=False):
    """The published scope's id, the same string publish.py stores: `review-app-<commodity>` for the
    review-app batch, else the joined country slugs + commodity."""
    import staged_store
    if batch:
        return f"review-app-{commodity.lower()}"
    slugs = ["tracker-wide" if c == staged_store.TRACKER_WIDE else
             staged_store.scope_dirname(c, commodity)[: -len(commodity) - 1] for c in countries]
    return "-".join(slugs) + "-" + commodity.lower()


def scope_of(data):
    """(scope id, snapshot name) of a built dataset."""
    sc = data.get("scope") or {}
    countries = sc.get("countries") or ([sc["country"]] if sc.get("country") else [])
    return scope_id(countries, sc.get("commodity") or "gas", bool(sc.get("batch"))), sc.get("snapshot") or ""


def cell(v):
    """Code.gs cell_: a display column is never a formula and never longer than a cell."""
    s = "" if v is None else str(v)
    if _FORMULA.match(s):
        s = "'" + s
    return s[:2000] + "…" if len(s) > 2000 else s


def row_for(rec):
    """Code.gs append_: one sheet row (19 strings) for a record; the `json` column is the record."""
    j = json.dumps(rec, ensure_ascii=False, separators=(",", ":"))
    if len(j) > MAX_JSON:
        raise StoreError("a record is too long to store: shorten the note")
    return [str(rec.get("ts") or ""), str(rec.get("reviewer") or ""), "item" if "call" in rec else "line",
            cell(rec.get("pid")), "" if rec.get("sheet_row") is None else str(rec["sheet_row"]),
            cell(rec.get("ref_col")), str(rec.get("kind") or ""), str(rec.get("decision") or ""),
            str(rec.get("call") or ""), cell(rec.get("suggested_value")), cell(rec.get("note")),
            "undone" if rec.get("undecided") else "", cell(rec.get("via")), str(rec.get("batch") or ""),
            cell(rec.get("snapshot")), cell(rec.get("key")), str(rec.get("id") or ""), str(rec.get("scope") or ""), j]


def stamp_fields(recs, scope, snapshot, origin, batch=None, ts=None):
    """Code.gs write_'s stamping, for records made here: every record gets this `origin` and one
    `batch` uuid per call; `id`, `scope`, `snapshot` and `ts` are filled only where missing (a
    carry-forward keeps the original's id~rekey, scope, snapshot and time). Returns recs."""
    if origin not in ORIGINS:
        raise ValueError(f"origin {origin!r} is not one of {ORIGINS}")
    batch = batch or str(uuid.uuid4())
    ts = ts or store.now()
    for r in recs:
        r["id"] = r.get("id") or str(uuid.uuid4())
        r["scope"] = r.get("scope") or scope
        r["batch"] = batch
        r["snapshot"] = r.get("snapshot") if r.get("snapshot") is not None and r.get("snapshot") != "" else snapshot
        r["origin"] = origin
        if not r.get("ts"):
            r["ts"] = ts
    return recs


def _range_rows(rng):
    m = _RANGE.match(rng or "")
    if not m:
        raise StoreError(f"cannot read the range the store reports: {rng!r}")
    r1 = int(m.group("r1"))
    return r1, int(m.group("r2") or r1)


def append(recs, sheet_id, gws=pull.gws, profile=pull.WRITE_PROFILE, read_profile=pull.READ_PROFILE, retries=1):
    """Append the records to the store's `log` tab (one RAW row each, after the last row) and
    verify by re-reading the `id` column of the rows the API reports. -> (first row, last row).
    Raises StoreError (nothing to clean up: a failed append wrote nothing we can rely on, and a
    verified-mismatch means our rows were overwritten, so the retry appends again)."""
    if not recs:
        return None
    rows = [row_for(r) for r in recs]
    ids = [r["id"] for r in recs]
    idc = pull._col_letter(COLS.index("id"))
    last_err = None
    for attempt in range(retries + 1):
        try:
            resp = gws(profile, "sheets", "spreadsheets", "values", "append",
                       "--params", json.dumps({"spreadsheetId": sheet_id, "range": f"{LOG_TAB}!A:{pull._col_letter(len(COLS) - 1)}",
                                               "valueInputOption": "RAW", "insertDataOption": "INSERT_ROWS",
                                               "includeValuesInResponse": False}),
                       "--json", json.dumps({"majorDimension": "ROWS", "values": rows}, ensure_ascii=False))
        except pull.GwsError as e:
            raise StoreError(f"the decision store could not be written: {e}") from e
        upd = (resp or {}).get("updates") or {}
        first, last = _range_rows(upd.get("updatedRange"))
        if last - first + 1 != len(rows):
            raise StoreError(f"the store reports {last - first + 1} rows written for {len(rows)} records ({upd.get('updatedRange')})")
        try:
            got = gws(read_profile, "sheets", "spreadsheets", "values", "get", "--params",
                      json.dumps({"spreadsheetId": sheet_id, "range": f"{LOG_TAB}!{idc}{first}:{idc}{last}",
                                  "majorDimension": "ROWS", "valueRenderOption": "UNFORMATTED_VALUE"}))
        except pull.GwsError as e:
            raise StoreError(f"written to the store (rows {first}-{last}) but the read-back failed: {e}") from e
        back = [(r[0] if r else "") for r in (got.get("values") or [])]
        back += [""] * (len(ids) - len(back))
        if back == ids:
            for r, i in zip(recs, range(first, last + 1)):
                r["row"] = i
            return first, last
        last_err = StoreError(f"the store's rows {first}-{last} do not hold these records after the append "
                              f"(another writer landed on them); " + ("retried once" if attempt else "retrying"))
    raise last_err


class Ledger:
    """A configured sink: `sink(recs, dirs, stamp=True)` has store._write's signature and is passed
    to store.decide / record_items / sync_backend / append_records. `reviewer_email` is the
    address written on a person's store rows (the account that writes the store, by default)."""

    def __init__(self, sheet_id, scope, snapshot, origin, reviewer_email=None, gws=pull.gws, emails=None):
        if not sheet_id:
            raise ValueError("no store configured (review_app/google.json: store_sheet_id)")
        self.sheet_id, self.scope, self.snapshot, self.origin = sheet_id, scope, snapshot, origin
        self.reviewer_email = reviewer_email or ""
        self.emails = dict(emails or {})      # store record id -> address (pull.mirror's), for copies of others' records
        self.gws = gws
        self.written = 0
        self.last_row = 0                     # the last store row this ledger wrote

    @classmethod
    def for_data(cls, data, origin, cfg=None, reviewer_email=None, gws=pull.gws):
        """A ledger for a built dataset, or None when no store is configured."""
        cfg = pull.config() if cfg is None else cfg
        sheet = (cfg or {}).get("store_sheet_id") or ""
        if not sheet:
            return None
        sid, snap = scope_of(data)
        return cls(sheet, sid, snap, origin, reviewer_email=reviewer_email, gws=gws)

    def to_store(self, rec):
        """The store's copy of a record: a person's initials become an address -- the original
        decider's when this is a copy of a store record (`emails`, by the id before `~`), else the
        writer's. A machine reviewer is kept as is."""
        r = dict(rec)
        who = r.get("reviewer")
        if who and who not in store.MACHINE_REVIEWERS:
            orig = self.emails.get(str(r.get("id") or "").split("~")[0])
            if orig or self.reviewer_email:
                r["reviewer"] = orig or self.reviewer_email
        return r

    def sink(self, recs, dirs, stamp=True):
        """Store first, sidecars second (caller holds store._LOCK). Stamps id/scope/batch/snapshot/
        origin (and ts unless the records bring their own). The local copy keeps the initials and
        every stamped field, exactly what pull.mirror would write for the same store row, so a later
        pull dedupes it by id. Raises StoreError before anything local is written."""
        recs = list(recs)
        if not recs:
            return []
        ts = store.now() if stamp else None
        for r in recs:
            if stamp:
                r["ts"] = ts
            r["reviewer"] = store.initials(r.get("reviewer"))
            if r["dir"] not in dirs:          # refuse an unknown dir BEFORE the store write, as _write would
                raise store.Invalid(f"staging dir not known to the server: {r['dir']}")
        stamp_fields(recs, self.scope, self.snapshot, self.origin, ts=ts)
        rows = [self.to_store(r) for r in recs]
        first, last = append(rows, self.sheet_id, gws=self.gws)
        store._write([dict(r) for r in recs], dirs, stamp=False)
        for r, s in zip(recs, rows):
            r["row"] = s.get("row")
        self.written += len(recs)
        self.last_row = max(self.last_row, last)
        return recs


def whoami(gws=pull.gws, profile=pull.WRITE_PROFILE):
    """The address of the account that writes the store (Drive `about.user`), or '' when it cannot
    be read. The store row's reviewer must be the account that wrote it, so this is the default."""
    try:
        body = gws(profile, "drive", "about", "get", "--params", json.dumps({"fields": "user"}))
    except pull.GwsError:
        return ""
    return str(((body or {}).get("user") or {}).get("emailAddress") or "")


# ---- CLI: a Claude chat (or anyone at a shell) decides through the same door ---------------

def _dataset(commodity, root=None):
    """The review-app batch dataset for `commodity`, overlaid, like push.build_plan builds it."""
    import review_data
    import scopes
    import staged_store
    root = Path(root) if root else staged_store.BATCHES_ROOT
    countries = scopes.included(commodity, None)
    if not countries:
        raise SystemExit(f"the review-app batch includes no {commodity} countries")
    dirs, dc = review_data._country_dirs(countries, commodity, root, None)
    ds, _ = review_data.build(dirs, countries, commodity, root=root, dir_country=dc)
    ds["scope"]["batch"] = True
    paths = store.dir_paths(ds, root.parent)
    store.overlay(ds, paths)
    return ds, paths


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status", help="store configured? who writes it? how many rows?")
    for name in ("decide", "undo", "item"):
        sp = sub.add_parser(name)
        sp.add_argument("--commodity", default="gas")
        sp.add_argument("--key", action="append", default=[], help="a line (decide/undo) or item key; repeatable")
        sp.add_argument("--records", help="JSON file: a list of records as /api/decide or /api/item take them")
        sp.add_argument("--reviewer", default=None, help="the person deciding (default: the store account's address)")
        sp.add_argument("--note", default="")
        if name == "decide":
            sp.add_argument("--decision", choices=sorted(store.DECISIONS))
            sp.add_argument("--value", default="", help="suggested_value for --decision suggest")
        if name == "item":
            sp.add_argument("--call", default="", help="confirmed|dismissed|needs_research (concern); noted|todo|dismissed (others)")
            sp.add_argument("--undo", action="store_true")
    a = ap.parse_args(argv)
    cfg = pull.config()
    sheet = cfg.get("store_sheet_id") or ""
    if a.cmd == "status":
        if not sheet:
            print("no store configured (review_app/google.json: store_sheet_id)")
            return 1
        me = whoami()
        rows = pull.read_store(sheet)
        print(f"store {sheet}: `{LOG_TAB}` tab, {max(0, len(rows) - 1)} records; writer {me or '(unknown: gws-gem-write auth?)'}")
        return 0
    if not sheet:
        sys.exit("no store configured (review_app/google.json: store_sheet_id): a chat decision has nowhere to land")
    email = a.reviewer or whoami()
    if not email:
        sys.exit("cannot tell who is deciding: pass --reviewer, or fix gws-gem-write auth")
    if a.records:
        records = json.loads(Path(a.records).read_text(encoding="utf-8"))
    elif a.cmd == "decide":
        if not a.decision:
            ap.error("--decision is required with --key")
        records = [{"key": k, "decision": a.decision, "note": a.note, "suggested_value": a.value} for k in a.key]
    elif a.cmd == "undo":
        records = [{"key": k, "undo": True} for k in a.key]
    else:
        records = [({"key": k, "undo": True} if a.undo else {"key": k, "call": a.call, "note": a.note}) for k in a.key]
    if not records:
        ap.error("nothing to record: pass --key (repeatable) or --records FILE")
    ds, dirs = _dataset(a.commodity)
    led = Ledger.for_data(ds, "chat", cfg=cfg, reviewer_email=email)
    try:
        if a.cmd == "item":
            saved = store.record_items(records, ds, email, dirs, sink=led.sink)
        else:
            saved = store.decide(records, ds, email, dirs, sink=led.sink)
    except store.Invalid as e:
        sys.exit(f"refused: {e}")
    except StoreError as e:
        sys.exit(f"{e}\nnothing was recorded (not in the store, not in a staging dir)")
    for r in saved:
        what = r.get("call") or r.get("decision")
        print(f"{'UNDO ' if r.get('undecided') else ''}{what:<14} {r['key']}  store row {r.get('row')}  id {r['id']}")
    print(f"{len(saved)} records in the store and in {len({r['dir'] for r in saved})} staging dir(s). "
          "Accepted cells reach the sheet only via review_app/push.py (plan, ask Baird, --apply).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
