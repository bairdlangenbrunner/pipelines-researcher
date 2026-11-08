"""
Bring decisions made on the artifact page (build_static.py) into the decision ledger.

    python review_app/import_log.py pipelines_review_log_20261005_1712_ET_AL.json --dry-run
    python review_app/import_log.py FILE [FILE ...] [--commodity gas] --reviewer EMAIL [--reviewer XX=EMAIL ...]

FILE is what the page's "download decisions" button saves, or the artifact's shared `logs` collection saved as JSON (an ArtifactData `list` or `get` result on the published page's url; the page's "push to log" button writes each reviewer's document there). Either way it holds one or more log documents, each {reviewer, email, records: [...]}; read_docs finds them inside any wrapper.

Every new record goes through the ledger like any other decision: appended to the store spreadsheet's `log` tab first (origin 'artifact', under the reviewer's own address), then to the staging dir's review_log.jsonl. Each record keeps the id and the time the page gave it. Rules:

  - a record whose id is already in a staging dir's log is skipped, so importing the same file twice, or a later download that repeats an earlier one, is safe
  - a record is skipped as superseded when the log already holds a later decision by a person on the same line or item (someone decided it on the Google page or the local server afterwards)
  - a record whose key is not in the current review-app dataset is matched the way the build carries a decision forward (config.resolve_key): when exactly one line of the same staging dir, ProjectID and column sits at another sheet row, or exactly one two-column fill names that column, the record is imported under that line's key and keeps the page's key in `rekeyed_from`
  - a record that still matches nothing, or whose staging dir is not in the dataset, is parked: written with its reason to work/review_import_parked_<time>.jsonl and left out, and the rest of the import goes ahead (the batch was rebuilt since the page was made; a person looks at the parked file, and rebuilding and republishing the page stops it happening again)
  - the page is not given reviewers' addresses (the artifact's "email" user scope is refused by the publish service, 2026-10-05), only their names, so name each one: --reviewer analyst.lead@globalenergymonitor.org (matched to the initials AL), or --reviewer AL=ADDRESS

This appends to the store `log` tab (the standing authorization in CLAUDE.md) and to the sidecars. It never writes the backend sheet: accepted cells reach it only through review_app/push.py (plan, ask Baird, --apply).

The plan, write and report code is shared with gogpt-researcher in ../gem-review-app/review_core/import_log.py. This file holds the pipelines rules: where a record lands (Rules, with resolve_key and parking), write_parked, and the --commodity dataset.
"""
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
import paths  # noqa: E402
import store  # noqa: E402
from review_core import import_log as core  # noqa: E402
from trackers.pipelines.config import key_index, parse_key, resolve_key  # noqa: E402


def _known(ds):
    """{key: (group, object)} for every line, item and covered record of the dataset."""
    out = {}
    for k, (_, o, grp) in store.index(ds).items():
        out[k] = (grp, o)
        for c in o.get("covers") or []:
            out[c["key"]] = ("lines", dict(c, sheet_row=c.get("sheet_row", o.get("sheet_row"))))
    return out


def _unplaced(key, d, dirs, ix):
    """Why a key that resolve_key could not place is parked, in words."""
    if d not in dirs:
        return f"the staging dir {d} is not part of the current review-app dataset"
    s = parse_key(key)
    if not s:
        return "the key does not have the <dir>::<ProjectID>|<row>|<column> shape"
    n = len(ix["ident"].get((s[0], s[1], s[3])) or ix["legacy"].get((s[0], s[1], s[3])) or [])
    if n > 1:
        return f"{n} lines of the current dataset have this ProjectID and column at other rows, so the record cannot be placed without a guess"
    return "no line or item of the current dataset has this key, or this ProjectID and column at another row"


class Rules:
    """Where a pipelines record lands: its own key, the key its line moved to (rekeyed), or nowhere (parked). The plan adds "rekeyed" (records moved to their line's new key) and "parked" ([{reason, reviewer, email, record}]). A line or item mismatch, or a decision outside the vocabulary, stops the import."""

    def __init__(self, ds, dirs):
        self.dirs = dirs
        self.known = _known(ds)
        self.ix = key_index(self.known)
        self.rekeyed, self.parked = [], []

    def place(self, r, where, email):
        known, ix = self.known, self.ix
        k = resolve_key(r["key"], known, ix) if r["dir"] in self.dirs else None
        if k is None:
            self.parked.append({"reason": _unplaced(r["key"], r["dir"], self.dirs, ix), "reviewer": r["reviewer"],
                                "email": email, "record": r})
            return None
        if k != r["key"]:
            via = resolve_key(r["via"], known, ix) if r.get("via") else None
            r = dict(r, key=k, rekeyed_from=r["key"])
            if "sheet_row" in r:
                r["sheet_row"] = known[k][1].get("sheet_row", r["sheet_row"])
            if via:
                r["via"] = via
            self.rekeyed.append(r)
        grp = known[r["key"]][0]
        if ("call" in r) != (grp == "items"):
            raise SystemExit(f"{where}: {r['key']} is {'an item' if grp == 'items' else 'a line'} "
                             f"but the record is {'an item call' if 'call' in r else 'a line decision'}")
        if "decision" in r and r["decision"] not in store.DECISIONS:
            raise SystemExit(f"{where}: decision {r['decision']!r} is not one of {sorted(store.DECISIONS)}")
        return r

    def extra(self):
        return {"rekeyed": self.rekeyed, "parked": self.parked}


def write_parked(pl, work=None, now=None):
    """Write the parked records to work/review_import_parked_<time>.jsonl, one {reason, reviewer,
    email, record} per line. -> the path, or None when nothing was parked."""
    if not pl.get("parked"):
        return None
    work = Path(work) if work else paths.work_dir()
    work.mkdir(parents=True, exist_ok=True)
    f = work / f"review_import_parked_{(now or datetime.now()).strftime('%Y%m%d_%H%M%S')}.jsonl"
    f.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in pl["parked"]), encoding="utf-8")
    return f


def _add_args(ap):
    ap.add_argument("--commodity", choices=["gas", "oil", "both"], default="both",
                    help="the dataset keys are placed in; both = gas plus oil, as the gas-batch page carries them")


def _parked_lines(pl):
    f = write_parked(pl)
    return [f"parked records written to {f}"] if f else []


core.bind(sys.modules[__name__], required=("key", "id", "reviewer", "dir"), rules=Rules, add_args=_add_args,
          dataset_for=lambda a, docs: ledger._dataset(a.commodity), after_plan=_parked_lines,
          next_step="Accepted cells reach the sheet only via review_app/push.py (plan, ask Baird, --apply).")

if __name__ == "__main__":
    sys.exit(main())  # noqa: F821  (bound above)
