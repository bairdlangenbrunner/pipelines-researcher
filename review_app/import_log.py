"""
Bring decisions made on the artifact page (build_static.py) into the decision ledger.

    python review_app/import_log.py pipelines_review_log_20261005_1712_ET_AL.json --dry-run
    python review_app/import_log.py FILE [FILE ...] [--commodity gas] --reviewer EMAIL [--reviewer XX=EMAIL ...]

FILE is what the page's "download decisions" button saves, or the artifact's shared `logs`
collection saved as JSON (an ArtifactData list or get result). Either way it holds one or more
log documents, each {reviewer, email, records: [...]}.

Every new record goes through the ledger like any other decision: appended to the store
spreadsheet's `log` tab first (origin 'artifact', under the reviewer's own address), then to the
staging dir's review_log.jsonl. Each record keeps the id and the time the page gave it. Rules:

  - a record whose id is already in a staging dir's log is skipped, so importing the same file
    twice, or a later download that repeats an earlier one, is safe
  - a record is skipped as superseded when the log already holds a later decision by a person on
    the same line or item (someone decided it on the Google page or the local server afterwards)
  - a record whose key is not in the current review-app dataset, or whose staging dir is not,
    stops the import before anything is written (the batch was rebuilt since the page was made:
    rebuild the page and publish it again)
  - the page is not given reviewers' addresses (the artifact's "email" user scope is refused by the
    publish service, 2026-10-05), only their names, so name each one:
    --reviewer amalia.llano@globalenergymonitor.org (matched to the initials AL), or --reviewer AL=ADDRESS

This appends to the store `log` tab (the standing authorization in CLAUDE.md) and to the sidecars.
It never writes the backend sheet: accepted cells reach it only through review_app/push.py (plan,
ask Baird, --apply).
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for p in (ROOT / "scripts", HERE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import ledger  # noqa: E402
import pull  # noqa: E402
import store  # noqa: E402

ORIGIN = "artifact"


def read_docs(path):
    """Every log document in a file, wherever it sits: the download ({logs: [...]}), one document,
    or an ArtifactData result that wraps documents in its own envelope."""
    body = json.loads(Path(path).read_text(encoding="utf-8"))
    docs = []

    def walk(x):
        if isinstance(x, dict):
            if isinstance(x.get("records"), list):
                docs.append(x)
            else:
                for v in x.values():
                    walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(body)
    return docs


def _when(ts):
    try:
        return datetime.fromisoformat(str(ts))
    except ValueError:
        return None


def plan(docs, ds, dirs, emails=None):
    """-> {"new": [(email, record), ...] in time order, "dup": n, "stale": [records], "people": {initials: email}}.
    SystemExit on a record this dataset cannot take; nothing is written here."""
    idx = store.index(ds)
    have, last = set(), {}
    for d in dirs.values():
        for r in store.read_log(d):
            if r.get("id"):
                have.add(str(r["id"]))
            t = _when(r.get("ts"))
            if r.get("key") and t and not store.is_machine(r) and (r["key"] not in last or t > last[r["key"]]):
                last[r["key"]] = t
    new, stale, people, dup, seen = [], [], {}, 0, set()
    for doc in docs:
        doc_email = str(doc.get("email") or "").strip()
        for i, r in enumerate(doc["records"]):
            where = f"{doc.get('reviewer') or '?'} record {i + 1}"
            if not isinstance(r, dict) or not r.get("key") or not r.get("id") or not r.get("reviewer") or not r.get("dir"):
                raise SystemExit(f"{where}: not a review record (needs key, id, reviewer, dir)")
            t = _when(r.get("ts"))
            if t is None or t.tzinfo is None:
                raise SystemExit(f"{where}: no usable time ({r.get('ts')!r})")
            if r["reviewer"] in store.MACHINE_REVIEWERS or not store._INITIALS_RE.match(str(r["reviewer"])):
                raise SystemExit(f"{where}: reviewer {r['reviewer']!r} is not a person's initials")
            if str(r["id"]) in have or str(r["id"]) in seen:
                dup += 1
                continue
            seen.add(str(r["id"]))
            if r["key"] not in idx:
                raise SystemExit(f"{where}: {r['key']} is not in the current review-app dataset "
                                 "(rebuilt since the page was made? rebuild the page and publish it again)")
            if r["dir"] not in dirs:
                raise SystemExit(f"{where}: staging dir {r['dir']} is not part of the current review-app dataset")
            grp = idx[r["key"]][2]
            if ("call" in r) != (grp == "items"):
                raise SystemExit(f"{where}: {r['key']} is {'an item' if grp == 'items' else 'a line'} "
                                 f"but the record is {'an item call' if 'call' in r else 'a line decision'}")
            if "decision" in r and r["decision"] not in store.DECISIONS:
                raise SystemExit(f"{where}: decision {r['decision']!r} is not one of {sorted(store.DECISIONS)}")
            email = doc_email or (emails or {}).get(r["reviewer"]) or ""
            if not email:
                raise SystemExit(f"{where}: the log of {r['reviewer']} carries no address: pass --reviewer {r['reviewer']}=EMAIL")
            full = store.initials(email)         # a one-word profile name logs "B": record "BL" (Baird 2026-10-05)
            if len(r["reviewer"]) < 2 and full.startswith(r["reviewer"]):
                r["reviewer"] = full
            if people.setdefault(r["reviewer"], email) != email:
                raise SystemExit(f"{where}: {r['reviewer']} appears under two addresses ({people[r['reviewer']]}, {email})")
            if r["key"] in last and last[r["key"]] > t:
                stale.append(r)
                continue
            new.append((t, email, r))
    new.sort(key=lambda x: x[0])
    return {"new": [(e, r) for _, e, r in new], "dup": dup, "stale": stale, "people": people}


def runs(new):
    """Consecutive records of one address, so the log keeps time order across reviewers."""
    out = []
    for email, r in new:
        if out and out[-1][0] == email:
            out[-1][1].append(r)
        else:
            out.append((email, [r]))
    return out


def write(pl, ds, dirs, cfg=None, gws=pull.gws):
    """Append the planned records, store first. -> the saved records (each with its store `row`)."""
    saved = []
    for email, recs in runs(pl["new"]):
        led = ledger.Ledger.for_data(ds, ORIGIN, cfg=cfg, reviewer_email=email, gws=gws)
        if led is None:
            raise SystemExit("no store configured (review_app/google.json: store_sheet_id): nothing was recorded")
        saved += store.append_records([dict(r) for r in recs], dirs, sink=led.sink)
    return saved


def report(pl):
    out = []
    by = {}
    for email, r in pl["new"]:
        by.setdefault((r["reviewer"], email), []).append(r)
    for (who, email), recs in sorted(by.items()):
        n_item = sum(1 for r in recs if "call" in r)
        undo = sum(1 for r in recs if r.get("undecided"))
        out.append(f"{who} ({email}): {len(recs) - n_item} line decisions, {n_item} item calls"
                   + (f", {undo} of them undos" if undo else "")
                   + (f"  [note: the address reads as {store.initials(email)}]" if store.initials(email) != who else ""))
    out.append(f"{len(pl['new'])} new, {pl['dup']} already in the log, {len(pl['stale'])} superseded by a later decision")
    for r in pl["stale"][:20]:
        out.append(f"  superseded: {r['key']} ({r['reviewer']}, {r.get('ts')})")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("file", nargs="+", help="the page's download, or the artifact's `logs` collection saved as JSON")
    ap.add_argument("--commodity", choices=["gas", "oil"], default="gas")
    ap.add_argument("--reviewer", action="append", default=[], metavar="EMAIL or XX=EMAIL",
                    help="a reviewer's address, for a log that carries none (the page is not given addresses); "
                         "repeat per reviewer. A bare EMAIL is matched to its own initials")
    ap.add_argument("--dry-run", action="store_true", help="report only; write nothing")
    a = ap.parse_args(argv)
    docs = [d for f in a.file for d in read_docs(f)]
    if not any(d["records"] for d in docs):
        raise SystemExit("no records in " + ", ".join(a.file))
    ds, dirs = ledger._dataset(a.commodity)
    emails = {}
    for v in a.reviewer:
        who, _, addr = v.rpartition("=")
        emails[who.strip() or store.initials(addr.strip())] = addr.strip()
    pl = plan(docs, ds, dirs, emails=emails)
    print(report(pl))
    if a.dry_run:
        print("dry run: nothing written")
        return 0
    if not pl["new"]:
        return 0
    try:
        saved = write(pl, ds, dirs)
    except ledger.StoreError as e:
        sys.exit(f"{e}\nthe records of this run were not recorded; run the import again (earlier runs are skipped by id)")
    print(f"{len(saved)} records in the store (rows {min(r['row'] for r in saved)}-{max(r['row'] for r in saved)}) "
          f"and in {len({r['dir'] for r in saved})} staging dir(s). "
          "Accepted cells reach the sheet only via review_app/push.py (plan, ask Baird, --apply).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
