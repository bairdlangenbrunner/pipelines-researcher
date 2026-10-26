"""
The decision ledger: ONE place every review decision lands, whoever makes it and however.

    python review_app/ledger.py status                       # store configured? who writes? last row
    python review_app/ledger.py decide --key KEY --decision accept|hold|reject|suggest [--note N] [--value V]
    python review_app/ledger.py undo --key KEY
    python review_app/ledger.py item --key KEY --call confirmed|dismissed|needs_research|noted|todo|dismissed [--note N]
    python review_app/ledger.py decide --records FILE.json   # [{key, decision, note?, suggested_value?} | {key, undo: true}]

The ledger IS the `log` tab of the store spreadsheet (review_app/google.json: store_sheet_id), the same tab the served Google page (review_app/gas/Code.gs) appends to, one row per record, in the same 19 columns (COLS; the test asserts the two lists agree). Everything that used to write a staging dir's review_log.jsonl directly now writes HERE FIRST and the sidecars second:

    served Google page  -> Code.gs write_/append_          (origin 'gas')
    loopback server     -> store.decide(..., sink=Ledger.sink)   (origin 'local')
    a Claude chat       -> `ledger.py decide`              (origin 'chat'; then review_app/push.py)
    push.py             -> `push` machine records          (origin 'push')
    refresh / publish   -> `backend sync`, carry-forward   (origin 'sync' / 'publish')
    artifact page       -> import_log.py (the page's download or shared log; origin 'artifact')

so the store holds every decision, the sidecars are its committed mirror (pull.py fills in whatever was written by the Google page), and the workbook, the push plan and the published dataset all read one history. Appending to the `log` tab is the standing authorization Baird gave 2026-10-01 (CLAUDE.md "Hard requirements"); it is the ONLY Google write this module makes, through gws-gem-write, and it never touches the backend sheet (that is push.py, asked per run).

The rules (store first, verified appends, ids, emails in the store and initials in the sidecars) and the code that keeps them are shared with gogpt-researcher in ../gem-review-app/review_core/ledger.py. This file holds the pipelines side: COLS, ORIGINS, row_of, scope_of (with scope_id) and the CLI. Two pipelines details: Code.gs compares addresses when it refuses a clash, which is why the store keeps the email, and Code.gs's getLastRow()+1 is the other writer a verified append can collide with.
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for p in (ROOT / "scripts", HERE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import pull  # noqa: E402
import store  # noqa: E402
from review_core import ledger as core  # noqa: E402

# Code.gs COLS, verbatim (tests/test_review_ledger.py parses the .gs and asserts equality)
COLS = ["ts", "reviewer", "rec", "pid", "sheet_row", "ref_col", "kind", "decision", "call", "suggested_value",
        "note", "undecided", "via", "batch", "snapshot", "key", "id", "scope", "json"]
ORIGINS = ("gas", "local", "chat", "push", "sync", "publish", "artifact", "apply")


def scope_id(countries, commodity, batch=False):
    """The published scope's id, the same string publish.py stores: `review-app-<commodity>` for the review-app batch, else the joined country slugs and the commodity."""
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


def row_of(rec):
    """Code.gs append_: one sheet row (19 strings) for a record; the `json` column is the record."""
    j = core.record_json(rec)
    return [str(rec.get("ts") or ""), str(rec.get("reviewer") or ""), "item" if "call" in rec else "line",
            core.cell(rec.get("pid")), "" if rec.get("sheet_row") is None else str(rec["sheet_row"]),
            core.cell(rec.get("ref_col")), str(rec.get("kind") or ""), str(rec.get("decision") or ""),
            str(rec.get("call") or ""), core.cell(rec.get("suggested_value")), core.cell(rec.get("note")),
            "undone" if rec.get("undecided") else "", core.cell(rec.get("via")), str(rec.get("batch") or ""),
            core.cell(rec.get("snapshot")), core.cell(rec.get("key")), str(rec.get("id") or ""), str(rec.get("scope") or ""), j]


core.bind(sys.modules[__name__], pull=pull, store=store)


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
