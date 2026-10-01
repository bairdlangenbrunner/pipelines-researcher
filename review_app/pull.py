"""
Mirror the Google decision store into the staging dirs (phase 2).

    python review_app/pull.py [--dry-run]

The Apps Script web app (review_app/gas/Code.gs) appends every decision to the `log` tab of the
store spreadsheet named in review_app/google.json (`store_sheet_id`). This reads that tab with the
READ-ONLY work profile (gws-gem) and appends each record it has not seen (by `id`) to the
`review_log.jsonl` of the staging dir the record names, as stored (the server's timestamp and the
extras `id`, `scope`, `batch`, `snapshot`, `basis`, `origin`) except for ONE field: the reviewer's
email is written as their first + last INITIALS (store.initials:
baird.langenbrunner@globalenergymonitor.org -> BL), the rule for every recorded reviewer, because
the staging dirs are committed and the store spreadsheet is private. The store keeps the full
address and is the authority on who decided what; two reviewers whose addresses share initials
share them here, and the pull says so when it happens. Then it regenerates that dir's
`review_decisions.json`. So after a pull the committed sidecars hold
everything the sheet holds, `decisions.py` / `build_ref_workbook.py --decisions` read them as
before, and git is the second copy of the history.

Idempotent: run it as often as you like. It never writes to Google. It returns (and prints) the
cursor = the last sheet row it read; publish.py stores that in the published scope so the web app
only lays rows AFTER it over the published dataset.

A record is only ever written under <repo>/batches/: a `dir` that resolves anywhere else, or to a
directory that does not exist, is reported and skipped.
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import store  # noqa: E402

CONFIG = HERE / "google.json"
LOG_TAB = "log"
READ_PROFILE = "gws-gem"            # read-only scopes
WRITE_PROFILE = "gws-gem-write"     # publish.py --upload only


class GwsError(RuntimeError):
    pass


def config(path=None):
    """review_app/google.json: {data_folder_id, store_sheet_id, script_id, web_app_url}."""
    p = Path(path) if path else CONFIG
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def gws(profile, *args, parse=True):
    """Run the gws CLI under one of the work profiles (the zsh wrappers, replicated). It runs from
    the repo root: gws refuses an --upload / -o path outside its working directory, and every file
    this app sends or fetches lives under the repo (work/)."""
    env = dict(os.environ,
               GOOGLE_WORKSPACE_CLI_CONFIG_DIR=os.path.expanduser(f"~/.config/{profile}"),
               GOOGLE_WORKSPACE_CLI_KEYRING_BACKEND="file")
    proc = subprocess.run(["gws", *args], capture_output=True, text=True, env=env, cwd=ROOT)
    out = proc.stdout or ""
    if proc.returncode != 0:
        raise GwsError(f"gws {' '.join(args[:3])} failed: {(proc.stderr or out).strip()[:600]}")
    if not parse:
        return out
    if "{" not in out:
        raise GwsError(f"gws {' '.join(args[:3])}: no JSON in the output: {out.strip()[:300]}")
    body = json.loads(out[out.index("{"):])
    if isinstance(body, dict) and body.get("error"):
        raise GwsError(f"gws {' '.join(args[:3])}: {json.dumps(body['error'])[:600]}")
    return body


def _col_letter(i):
    s, i = "", i + 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


def read_store(sheet_id, profile=READ_PROFILE):
    """-> the `json` column of the log tab as a list of cell texts, header first (index i = sheet
    row i + 1). [] when the tab does not exist yet (nobody has decided anything)."""
    def get(rng):
        return gws(profile, "sheets", "spreadsheets", "values", "get", "--params",
                   json.dumps({"spreadsheetId": sheet_id, "range": rng, "majorDimension": "ROWS",
                               "valueRenderOption": "UNFORMATTED_VALUE"}))
    try:
        head = (get(f"{LOG_TAB}!1:1").get("values") or [[]])[0]
    except GwsError as e:
        if "Unable to parse range" in str(e):
            return []
        raise
    if "json" not in head:
        raise GwsError(f"the store's `{LOG_TAB}` tab has no `json` column (header: {head})")
    c = _col_letter(head.index("json"))
    vals = get(f"{LOG_TAB}!{c}1:{c}").get("values") or []
    return [str(r[0]) if r else "" for r in vals]


def parse_rows(cells):
    """-> (records, cursor, bad). `cells` is read_store's list; a record gets `row` = its sheet row.
    cursor = the last sheet row read (1 = header only; values.get drops trailing empty rows, and a
    record row always has its json cell)."""
    recs, bad = [], []
    for i, text in enumerate(cells):
        if i == 0 or not text:
            continue
        try:
            r = json.loads(text)
        except json.JSONDecodeError:
            bad.append(i + 1)
            continue
        if not isinstance(r, dict) or not r.get("id") or not r.get("key") or not r.get("dir"):
            bad.append(i + 1)
            continue
        r["row"] = i + 1
        recs.append(r)
    return recs, max(1, len(cells)), bad


def resolve_dir(label, root=None):
    """The staging dir a record names, or None: it must be an existing directory under <root>/batches."""
    base = (Path(root) if root else ROOT).resolve()
    batches = base / "batches"
    try:
        d = (base / str(label)).resolve()
    except (OSError, ValueError):
        return None
    if batches not in d.parents or not d.is_dir():
        return None
    return d


def mirror(records, root=None, dry_run=False):
    """Append the records not yet in their dir's review_log.jsonl (by `id`), in sheet order.
    -> {"new": n, "by_dir": {label: n}, "skipped": {label: n}, "emails": {record id: address},
    "shared": {initials: [addresses]}}. The sheet row (`row`) is not stored locally: it is the
    sheet's business, and a restored sheet may renumber. The reviewer is stored as `store.initials()`;
    `emails` (never written to disk) lets publish.py put the full address back into the dataset
    it sends to the private Drive folder, and `shared` lists the initials that stand for more
    than one address in the store."""
    by_dir, skipped, dirs, seen, emails, behind = {}, {}, {}, {}, {}, {}
    for r in records:
        short = store.initials(r.get("reviewer"))
        if short != r.get("reviewer"):
            emails[r["id"]] = r["reviewer"]
            behind.setdefault(short, set()).add(str(r["reviewer"]).lower())
        label = r["dir"]
        if label not in dirs:
            dirs[label] = resolve_dir(label, root)
            if dirs[label] is not None:
                seen[label] = {x.get("id") for x in store.read_log(dirs[label]) if x.get("id")}
        if dirs[label] is None:
            skipped[label] = skipped.get(label, 0) + 1
            continue
        if r["id"] in seen[label]:
            continue
        seen[label].add(r["id"])
        by_dir.setdefault(label, []).append(dict({k: v for k, v in r.items() if k != "row"}, reviewer=short))
    new = [r for rs in by_dir.values() for r in rs]
    if new and not dry_run:
        store.append_records(new, {k: v for k, v in dirs.items() if v is not None})
    return {"new": len(new), "by_dir": {k: len(v) for k, v in by_dir.items()}, "skipped": skipped,
            "emails": emails, "shared": {a: sorted(v) for a, v in behind.items() if len(v) > 1}}


def pull(cfg=None, root=None, dry_run=False, reader=read_store):
    """Read the store, mirror it. -> {"cursor", "rows", "new", "by_dir", "skipped", "bad_rows",
    "configured", "emails", "shared"}. With no store configured there is nothing to pull: cursor 1."""
    cfg = config() if cfg is None else cfg
    sheet = (cfg or {}).get("store_sheet_id") or ""
    if not sheet:
        return {"configured": False, "cursor": 1, "rows": 0, "new": 0, "by_dir": {}, "skipped": {}, "bad_rows": [],
                "emails": {}, "shared": {}}
    recs, cursor, bad = parse_rows(reader(sheet))
    out = mirror(recs, root, dry_run)
    out.update(configured=True, cursor=cursor, rows=len(recs), bad_rows=bad)
    return out


def report(res, dry_run=False):
    if not res["configured"]:
        return "no store configured (review_app/google.json: store_sheet_id): nothing to pull"
    verb = "would append" if dry_run else "appended"
    out = [f"store: {res['rows']} records, last sheet row {res['cursor']}; {verb} {res['new']} new"]
    out += [f"  {n:>5}  {d}" for d, n in sorted(res["by_dir"].items())]
    out += [f"  SKIPPED {n} records naming a dir that is not under batches/: {d}" for d, n in sorted(res["skipped"].items())]
    if res["bad_rows"]:
        out.append(f"  UNREADABLE sheet rows (not a record): {res['bad_rows'][:20]}")
    out += [f"  SHARED INITIALS {a} stand for {len(v)} reviewers in the store: the pulled logs cannot tell them "
            f"apart (the store spreadsheet can)" for a, v in sorted(res.get("shared", {}).items())]
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dry-run", action="store_true", help="read the store, write nothing")
    ap.add_argument("--config", default=None, help="default review_app/google.json")
    a = ap.parse_args(argv)
    try:
        res = pull(config(a.config), dry_run=a.dry_run)
    except GwsError as e:
        sys.exit(f"pull failed: {e}\n(if this is an auth failure, run `gws-gem auth login` yourself; it needs a browser)")
    print(report(res, a.dry_run))
    return res


if __name__ == "__main__":
    main()
