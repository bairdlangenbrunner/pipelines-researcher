"""
Publish a review scope for the Google web app (phase 2).

    python review_app/publish.py                   # plan: build the review-app batch + write the local mirror
    python review_app/publish.py --upload          # + list what Drive would change
    python review_app/publish.py --upload --yes    # do it (ask Baird first, every run)
    python review_app/publish.py --country Russia --commodity gas    # one named scope instead

      [--commodity gas|oil] [--include-done] [--country C ...] [--dirs DIR ...] [--exclude-pids P1,P2]
      [--snapshot CSV] [--scope-id ID] [--refresh] [--no-pull] [--out work/review_publish]

With no --country it publishes the review-app batch (batches/review-app/manifest.json, see
review_app/scopes.py): one scope, id `review-app-<commodity>`, over every included country, with
the all-decided countries dropped unless --include-done. That is the same dataset the local server
builds by default. With --country it publishes that country set as its own scope
(`<country-slug>-<commodity>`); the web app's scope picker lists every published scope.

What it does, in order:
  1. --refresh only: scripts/refresh_csvs.sh (reads the LIVE sheet, read-only, ~1 min).
  2. pull.py: mirror the Google decision store into the staging dirs' review_log.jsonl and note the
     last sheet row read (the cursor). The published dataset already carries every decision up to
     the cursor; the web app lays only LATER rows over it. --no-pull skips this (cursor 1) and is
     refused with --upload once a store is configured.
  3. review_data.build + the decision overlay (the same dataset the local server serves). Every
     line the sheet already holds and no one has decided gets a `backend sync` accept
     (store.sync_backend): with --refresh the records are written (store first, then the
     sidecars); otherwise they are laid over the dataset in memory only (sync_in_memory), so the
     page shows those lines as landed without a write. Either way the line is not a person's call.
  4. Stamp every line with `basis`: a short hash of the backend cells the proposal was judged
     against (current value, current refs, current status, current route accuracy). The web app
     copies it into each decision record. A line whose latest person decision carries a DIFFERENT
     basis gets `drift` = the backend changed under that decision; nothing is reverted, the app
     shows it and filters on it.
  5. CARRY FORWARD, then report ORPHANS. A decision key holds the sheet row, so a row inserted
     above a pipeline renumbers its key and the decision would match nothing. When a person's
     decision is orphaned and exactly one line or item of this build has the same staging dir,
     ProjectID and column (only the row differs) and nothing is recorded under that key yet, a
     copy of the record is appended to the log under the new key (`rekeyed_from` = the old key;
     reviewer, time, basis and snapshot kept). The old record is never rewritten. Anything else
     whose key matches no line of this build is reported as an orphan, with its reason
     (explain_orphans), and left alone. Orphans are counted over every country of the build,
     before the all-decided countries are dropped: a decision in a hidden country is not lost.
  6. Write the flat file set into --out (gitignored work/review_publish by default; the dev server
     review_app/gas_dev/dev_server.js reads it as if it were the Drive folder):

       scopes.json                     {updated, scopes: [{id, label, ver, parts, index, geo, store_cursor, ...}]}
       <id>.<ver>.part<k>.json.gz      the dataset, split so no part is big; part 0 has everything but
                                       the later pipelines, the others are {"pipelines": [...]}
       <id>.<ver>.index.json           what Code.gs validates a decision against (ASCII JSON; the
                                       same index the artifact page carries, review_core.build_static.pack_index)
       <id>.<ver>.geo.json.gz          candidate route geometry, only when the scope has route lines

  7. --upload: create the new files in the Drive data folder (review_app/google.json
     `data_folder_id`), then update scopes.json (the switch: the app serves the new version from
     that moment, within a minute), then trash this scope's files older than the previous version.
     Without --yes it only lists those actions. Drive writes use the gws-gem-write profile.

Nothing here writes the backend tracker sheet, the routes repo or staged_*.json.
"""
import argparse
import gzip
import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for p in (ROOT / "scripts", HERE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import ledger  # noqa: E402
import paths  # noqa: E402
import pull as pull_mod  # noqa: E402
import review_data  # noqa: E402
import scopes  # noqa: E402
import staged_store  # noqa: E402
import store  # noqa: E402
from review_core import build_static as core  # noqa: E402
from trackers.pipelines.config import key_index, parse_key, resolve_key  # noqa: E402

ET = ZoneInfo("America/New_York")
PART_BYTES = 2_500_000          # raw JSON per part; gzips to well under 1 MB
SCOPE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
BASIS_FIELDS = review_data.BASIS_FIELDS
basis = review_data.basis          # review_data.build stamps it on every line; kept here for callers


# ---- basis, drift, orphans ---------------------------------------------------------


def _logs(data, dirs):
    """{dir label: store.calls(its log)} — read through `store.speaker`, so a machine record written
    after a person's call (a push) never hides that call."""
    return {d: store.calls(store.read_log(p)) for d, p in dirs.items()}


def _rec(logs, d, key):
    return store.speaker(logs.get(d) or {}, key)[0]


def stamp_basis(data, dirs):
    """Set `basis` on every line; set `drift` on a line whose latest PERSON decision was made
    against a different basis and which the backend does not already hold. -> [drifted line]."""
    logs = _logs(data, dirs)
    out = []
    for p in data.get("pipelines", []):
        for l in p.get("lines", []):
            l["basis"] = basis(l)
            l.pop("drift", None)
            rec = _rec(logs, l.get("dir"), l["key"])
            if not store.reviewed(rec) or not rec.get("basis") or rec["basis"] == l["basis"] or l.get("in_backend"):
                continue
            l["drift"] = {"decided_snapshot": rec.get("snapshot", ""), "decided_basis": rec["basis"]}
            out.append(l)
    return out


def known_keys(data):
    keys = set()
    for p in data.get("pipelines", []):
        for grp in ("lines", "items"):
            for o in p.get(grp, []):
                keys.add(o["key"])
                keys.update(c["key"] for c in o.get("covers") or [])
    return keys


def _rows(data):
    """{key: sheet_row} for every line, item and covered record of the build."""
    out = {}
    for p in data.get("pipelines", []):
        for grp in ("lines", "items"):
            for o in p.get(grp, []):
                out[o["key"]] = o.get("sheet_row")
                for c in o.get("covers") or []:
                    out[c["key"]] = c.get("sheet_row")
    return out


def _orphans(keys, logs, dirs):
    """[(dir label, record)]: latest live PERSON records whose key is not in `keys` and that were
    not already carried to another key (some record in the log names them in `rekeyed_from`)."""
    out = []
    for d, by_key in logs.items():
        carried = {r["rekeyed_from"] for r in store.read_log(dirs[d]) if r.get("rekeyed_from")}
        for k in by_key:
            r = _rec(logs, d, k)
            if k not in keys and k not in carried and store.reviewed(r):
                out.append((d, r))
    return out


def orphans(data, dirs):
    """Latest live PERSON records in the scope's logs whose key matches nothing in this build
    (and that carry_forward has not moved to a key that does)."""
    return [r for _, r in _orphans(known_keys(data), _logs(data, dirs), dirs)]


ORPHAN_REASONS = {
    "row_renumbered": "row renumbered: one line of this build has the same dir, ProjectID and column at another "
                      "sheet row, but the decision was not carried to it (a person already decided that line, "
                      "or other moved decisions on it disagree)",
    "column_left": "column left the batch: the ProjectID is still in this dir, but none of its lines or items has the column",
    "dir_skipped": "dir dropped or skipped: the dir is not in this build, or the build leaves its records out on "
                   "purpose (a recon dir, a route-QC record, a sheet-vs-wiki diff, a country update store, a new-row "
                   "candidate already on the sheet or now matched to an existing row)",
    "multi_row": "multi-row ProjectID: several lines of this build have the same dir, ProjectID and column, "
                 "so the decision cannot be carried without a guess",
    "unknown": "unknown: none of the above (the key does not parse, or the ProjectID has nothing left in this dir)",
}


def stray_logs(data, countries, commodity, root):
    """{dir label: path} of the staging dirs under the countries' scope dirs that hold a
    review_log.jsonl but are not part of this build (discovery no longer finds them)."""
    root, have, out = Path(root), set(data.get("dirs", [])), {}
    for c in countries:
        if c == review_data.TRACKER_WIDE:
            continue
        for f in sorted((root / staged_store.scope_dirname(c, commodity) / "staging").glob("*/review_log.jsonl")):
            label = review_data._rel(f.parent, root)
            if label not in have:
                out[label] = f.parent
    return out


def explain_orphans(data, dirs, stray=None, carried=()):
    """Every orphan (orphans(), plus the live person records in the `stray` dirs) with the reason
    its key matches nothing in this build, as [{"reason", "dir", "key", "decision", "reviewer",
    "ts", "detail"}]; ORPHAN_REASONS says what each reason means. `carried` are the records
    carry_forward returned on a dry run: they are reported as carried, not as orphans."""
    rows = _rows(data)
    ix = key_index(rows)
    pids = {(s[0], s[1]) for s in map(parse_key, rows) if s}
    cols = {}                                   # (dir, pid, colid without its #suffix) -> keys
    for k in rows:
        s = parse_key(k)
        if s:
            cols.setdefault((s[0], s[1], s[3].split("#", 1)[0]), []).append(k)
    new_left = {}                               # dir -> {"new:<slug>": why the build leaves it out}

    def left_out(d):
        if d not in new_left:
            new_left[d] = {}
            f = Path(dirs[d]) / "staged_new.json" if d in dirs else None
            for i, c in enumerate(review_data._read_json(f).get("candidates", []) if f and f.exists() else []):
                slug = c.get("slug") or (c.get("name") or f"cand{i}").lower().replace(" ", "-")
                if c.get("applied"):
                    new_left[d][f"new:{slug}"] = "a new-row candidate already appended to the sheet"
                elif c.get("class") == "matched_existing":
                    new_left[d][f"new:{slug}"] = "a new-row candidate now matched to an existing row"
        return new_left[d]
    done = {r.get("rekeyed_from") for r in carried}
    upd = {d for d, path in dirs.items() if (Path(path) / "staged_updates.json").exists()}

    def why(d, key, r):
        if d in (stray or {}):
            return "dir_skipped", "the dir is not part of this build"
        if review_data.SKIP_RECON_DIRS and Path(d).name.startswith("recon-"):
            return "dir_skipped", "a recon dir (SKIP_RECON_DIRS)"
        s = parse_key(key)
        if not s:
            return "unknown", "the key does not parse"
        if r.get("kind") == "routeqc" or s[3].startswith("__ROUTEQC__"):
            return "dir_skipped", "a route-QC record (SKIP_ROUTEQC)"
        if r.get("kind") == "wikidiff" or s[3].startswith("__WIKIDIFF__"):
            return "dir_skipped", "a sheet-vs-wiki diff record"
        ident = (s[0], s[1], s[3])
        cands = ix["ident"].get(ident) or ix["legacy"].get(ident) or []
        if len(cands) > 1:
            return "multi_row", f"{len(cands)} lines match: " + ", ".join(sorted(cands)[:4])
        if cands:
            return "row_renumbered", f"the line is now {cands[0]}"
        if (s[0], s[1]) in pids:
            same = cols.get((s[0], s[1], s[3].split("#", 1)[0]))
            return "column_left", (f"the column is still there under another record number: {same[0]}" if same else "")
        if s[3] in left_out(d):
            return "dir_skipped", left_out(d)[s[3]]
        if d in upd:
            return "dir_skipped", "a country update store (not read by the review app)"
        return "unknown", "the ProjectID has no line or item in this dir"

    logs = _logs(data, dirs)
    found = [(d, r) for d, r in _orphans(set(rows), logs, dirs) if r["key"] not in done]
    for d, path in (stray or {}).items():
        by_key = store.calls(store.read_log(path))
        found += [(d, r) for k in by_key for r in [store.speaker(by_key, k)[0]] if store.reviewed(r)]
    out = []
    for d, r in found:
        reason, detail = why(d, r["key"], r)
        out.append({"reason": reason, "dir": d, "key": r["key"], "kind": r.get("kind") or "",
                    "decision": r.get("decision") or r.get("call") or "", "reviewer": r.get("reviewer") or "",
                    "ts": r.get("ts") or "", "detail": detail})
    return out


def sync_in_memory(data, dirs, snapshot="", ts=None):
    """The backend sync without a write: the records store.sync_backend would append (a `backend
    sync` accept for every line the sheet already holds that no one has decided, and for its
    covers) are laid over `data` exactly as the overlay lays a logged one, and nothing is written.
    A line so marked shows decision accept by "backend sync", `applied` by it, and stays not
    `reviewed`: it is not a person's call, and the page never sends a machine record back
    (import_log refuses one). A later --refresh, or the local server's refresh, writes the same
    records for real. -> the records."""
    recs = store.sync_backend(data, dirs, snapshot, sink=lambda recs, dirs: recs)
    if not recs:
        return []
    ts = ts or data.get("built") or datetime.now(ET).isoformat(timespec="seconds")
    who = store.SYNC_REVIEWER
    keys = {r["key"] for r in recs}
    for p in data.get("pipelines", []):
        for l in p.get("lines", []):
            if l["key"] in keys:
                l.update(decision="accept", suggested_value="", decision_note="", reviewed=False,
                         decided_by=who, decided_at=ts, rival=None, applied={"by": who, "at": ts})
            if l.get("covers"):
                for c in l["covers"]:
                    if c["key"] in keys:
                        c.update(decision="accept", decided_by=who, decided_at=ts)
                l["uncovered"] = [c["key"] for c in l["covers"] if c["decision"] != l["decision"]]
    return recs


def carry_forward(data, dirs, sink=None, write=True):
    """Re-key the person decisions that a renumbered sheet row orphaned (module docstring, step 5).
    Appends the copies to the logs (store.append_records: time and reviewer kept; `sink` = the
    ledger's, so the copies land in the decision store too) and returns them; the caller overlays
    the dataset again. Carried only when the match is beyond doubt (config.resolve_key):
      - exactly one key of this build has the orphan's dir, ProjectID and full colid — or, for a
        fill decided before 2026-10-01 under its first value column alone (`…|ProposalYear`),
        exactly one multi-column fill key of this build names that column
        (`…|ProposalYear+ProposalMonth`; review_data._fill_colid),
      - no PERSON record sits under that key (a later decision wins; a machine record there — a
        backend sync, a push — is not a decision and does not block the carry),
      - no other orphan wants the same key, unless every orphan that wants it made the same call on
        the same cells (decision or call, basis and suggested value all equal): the same line
        decided again on a later build, before a second re-sort. The latest one is carried.
    `write=False` (a --no-pull dry run against a configured store) only reports the carries: a
    sidecar-only record would put the sidecars ahead of the store, the single source of truth."""
    rows = _rows(data)
    ix = key_index(rows)                        # config.resolve_key: the one rule for "the same line"
    logs = _logs(data, dirs)
    want = {}                                   # target key -> [(dir, orphan record)]
    for d, r in _orphans(set(rows), logs, dirs):
        k = resolve_key(r["key"], rows, ix)
        if k and not (logs.get(d, {}).get(k) or {}).get("person"):
            want.setdefault(k, []).append((d, r))
    def same_call(r):
        return (r.get("decision"), r.get("call"), r.get("basis"), r.get("suggested_value") or "")
    chosen = {}                                 # target key -> the orphan record carried to it
    for k, rs in want.items():
        if len({same_call(r) for _, r in rs}) == 1 and all(r.get("basis") for _, r in rs):
            chosen[k] = max((r for _, r in rs), key=lambda r: r.get("ts") or "")
        elif len(rs) == 1:
            chosen[k] = rs[0][1]
    moved = {r["key"]: k for k, r in chosen.items()}                           # old key -> new key
    new = []
    for old, k in moved.items():
        r = dict(chosen[k], key=k, sheet_row=rows[k], rekeyed_from=old)
        if r.get("id"):
            r["id"] = f"{r['id']}~rekey"        # pull.py dedupes by id: the copy is its own record
        if r.get("via") in moved:
            r["via"] = moved[r["via"]]
        new.append(r)
    if new and write:
        store.append_records(new, dirs, sink=sink)
    return new


def restore_reviewers(data, dirs, emails):
    """Put the full address back on `decided_by` where the log holds pull.py's initials. `emails` is
    {store record id: address} from the pull; the dataset goes to the private Drive folder, where
    the app shows and filters by the same address the live store rows carry. -> how many."""
    if not emails:
        return 0
    logs, n = _logs(data, dirs), 0
    for p in data.get("pipelines", []):
        for grp in ("lines", "items"):
            for o in p.get(grp, []):
                for x in [o] + list(o.get("covers") or []):
                    rec = _rec(logs, x.get("dir"), x["key"])
                    full = emails.get(str((rec or {}).get("id") or "").split("~")[0])
                    if full and x.get("decided_by") == rec.get("reviewer"):
                        x["decided_by"] = full
                        n += 1
    return n


# ---- the files -----------------------------------------------------------------------

def _dump(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def split_parts(data, target=PART_BYTES):
    """-> [dict]. Part 0 = every non-pipeline key + the first pipelines; later parts hold only
    pipelines. A pipeline is never split; a part closes once it passes `target` bytes of JSON."""
    head = {k: v for k, v in data.items() if k != "pipelines"}
    parts, cur, size = [], [], len(_dump(head).encode("utf-8"))
    for p in data.get("pipelines", []):
        n = len(_dump(p).encode("utf-8"))
        if cur and size + n > target:
            parts.append(cur)
            cur, size = [], 0
        cur.append(p)
        size += n
    parts.append(cur)
    return [dict(head, pipelines=ps) if i == 0 else {"pipelines": ps} for i, ps in enumerate(parts)]


def geo_bundle(data, base):
    """{"<dir>/<geometry_file>": geojson} for every route line whose candidate file exists and
    resolves inside <base>/batches; None when the scope has none."""
    base = Path(base).resolve()
    out = {}
    for p in data.get("pipelines", []):
        for l in p.get("lines", []):
            gf = l.get("geometry_file")
            if not gf:
                continue
            name = f"{l['dir']}/{gf}"
            f = (base / name).resolve()
            if (base / "batches") not in f.parents or not f.is_file() or f.suffix.lower() not in (".geojson", ".json"):
                continue
            try:
                out[name] = json.loads(f.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
    return out or None


def _gz(text):
    return gzip.compress(text.encode("utf-8"), 9, mtime=0)


scope_id = ledger.scope_id        # one rule for the scope's id, shared with the ledger's stamping


def write_scope(data, out, sid, cursor, base, ver=None, build=None, target=PART_BYTES, label=None):
    """Write one scope's files into `out` (flat) and return its scopes.json entry."""
    if not SCOPE_ID_RE.match(sid):
        raise SystemExit(f"scope id {sid!r}: lowercase letters, digits and hyphens only")
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ET)
    ver = ver or now.strftime("%Y%m%dT%H%M%S")
    names = []
    for i, part in enumerate(split_parts(data, target)):
        name = f"{sid}.{ver}.part{i}.json.gz"
        (out / name).write_bytes(_gz(_dump(part)))
        names.append(name)
    index_name = f"{sid}.{ver}.index.json"
    (out / index_name).write_text(json.dumps(core.pack_index(data, store.CONFIG), ensure_ascii=True, separators=(",", ":")),
                                  encoding="ascii")
    geo, geo_name = geo_bundle(data, base), None
    if geo:
        geo_name = f"{sid}.{ver}.geo.json.gz"
        (out / geo_name).write_bytes(_gz(_dump(geo)))
    sc = data.get("scope", {})
    pipes = data.get("pipelines", [])
    return {"id": sid, "label": label or f"{sc.get('country', '')} {sc.get('commodity', '')}".strip(),
            "country": sc.get("country", ""), "commodity": sc.get("commodity", ""),
            "ver": ver, "published": now.isoformat(timespec="seconds"), "built": data.get("built", ""),
            "snapshot": sc.get("snapshot", ""), "store_cursor": int(cursor), "parts": names,
            "index": index_name, "geo": geo_name,
            "counts": {"pipelines": len(pipes), "lines": sum(len(p.get("lines", [])) for p in pipes),
                       "items": sum(len(p.get("items", [])) for p in pipes)},
            "build": build or {}}


def merge_scopes(existing, entry):
    """scopes.json body with `entry` replacing the scope of the same id (others untouched)."""
    scopes = [s for s in (existing or {}).get("scopes", []) if s.get("id") != entry["id"]]
    scopes.append(entry)
    scopes.sort(key=lambda s: s.get("label", ""))
    return {"updated": entry["published"], "scopes": scopes}


def read_scopes(path):
    path = Path(path)
    if not path.exists():
        return {"scopes": []}
    return json.loads(path.read_text(encoding="utf-8"))


def write_scopes(out, body):
    store.atomic_write(Path(out) / "scopes.json", json.dumps(body, indent=1, ensure_ascii=True) + "\n")


# ---- Drive ---------------------------------------------------------------------------

def drive_list(folder, gws=pull_mod.gws):
    files, token = [], None
    while True:
        params = {"q": f"'{folder}' in parents and trashed = false", "pageSize": 1000,
                  "fields": "nextPageToken, files(id, name, modifiedTime, size)",
                  "supportsAllDrives": True, "includeItemsFromAllDrives": True}
        if token:
            params["pageToken"] = token
        body = gws(pull_mod.READ_PROFILE, "drive", "files", "list", "--params", json.dumps(params))
        files += body.get("files", [])
        token = body.get("nextPageToken")
        if not token:
            return files


def drive_scopes(files, tmp, gws=pull_mod.gws):
    """The scopes.json the Drive folder holds now (the truth for every OTHER scope), or empty."""
    hit = sorted((f for f in files if f["name"] == "scopes.json"), key=lambda f: f.get("modifiedTime", ""))
    if not hit:
        return {"scopes": []}, None
    # gws prints an alt=media body to stdout and does not honor -o for it, so read stdout
    out = gws(pull_mod.READ_PROFILE, "drive", "files", "get", "--params",
              json.dumps({"fileId": hit[-1]["id"], "alt": "media", "supportsAllDrives": True}), parse=False)
    return json.loads(out[out.index("{"):]), hit[-1]["id"]


def plan_upload(entry, files, prev_ver):
    """-> (create [name], trash [file]). Trash = this scope's files of any version but the new one
    and the one being replaced (a page loaded a minute ago may still be fetching its parts)."""
    have = {f["name"] for f in files}
    new = [n for n in entry["parts"] + [entry["index"]] + ([entry["geo"]] if entry["geo"] else []) if n not in have]
    keep = {entry["ver"], prev_ver}
    trash = [f for f in files if f["name"].startswith(entry["id"] + ".")
             and f["name"][len(entry["id"]) + 1:].split(".", 1)[0] not in keep]
    return new, trash


def upload(out, entry, cfg, yes=False, gws=pull_mod.gws, say=print):
    """Create the scope's files in the data folder, switch scopes.json, trash what is superseded.
    Without `yes` it only says what it would do. Returns the merged scopes.json body."""
    folder = (cfg or {}).get("data_folder_id") or ""
    if not folder:
        raise SystemExit("review_app/google.json has no data_folder_id: nothing to upload to")
    out = Path(out)
    files = drive_list(folder, gws)
    current, scopes_file = drive_scopes(files, out, gws)
    prev = next((s.get("ver") for s in current.get("scopes", []) if s.get("id") == entry["id"]), None)
    create, trash = plan_upload(entry, files, prev)
    body = merge_scopes(current, entry)
    say(f"Drive folder {folder}: {len(files)} files now; this scope's live version: {prev or '(none)'}")
    for n in create:
        say(f"  CREATE  {n}  ({(out / n).stat().st_size:,} bytes)")
    say(f"  {'UPDATE' if scopes_file else 'CREATE'}  scopes.json  ({len(body['scopes'])} scopes; {entry['id']} -> {entry['ver']})")
    for f in trash:
        say(f"  TRASH   {f['name']}")
    if not yes:
        say("nothing uploaded (plan only). Re-run with --upload --yes once Baird has OK'd this run.")
        return body
    w = pull_mod.WRITE_PROFILE
    for n in create:
        gws(w, "drive", "files", "create", "--json", json.dumps({"name": n, "parents": [folder]}),
            "--upload", str(out / n), "--params", json.dumps({"supportsAllDrives": True, "fields": "id,name"}))
    write_scopes(out, body)
    if scopes_file:
        gws(w, "drive", "files", "update", "--upload", str(out / "scopes.json"),
            "--params", json.dumps({"fileId": scopes_file, "supportsAllDrives": True, "fields": "id,name"}))
    else:
        gws(w, "drive", "files", "create", "--json", json.dumps({"name": "scopes.json", "parents": [folder]}),
            "--upload", str(out / "scopes.json"), "--params", json.dumps({"supportsAllDrives": True, "fields": "id,name"}))
    for f in trash:
        gws(w, "drive", "files", "update", "--json", json.dumps({"trashed": True}),
            "--params", json.dumps({"fileId": f["id"], "supportsAllDrives": True, "fields": "id,name"}))
    say(f"uploaded: {len(create)} files created, scopes.json switched, {len(trash)} trashed")
    return body


# ---- the run -------------------------------------------------------------------------

def scope_label(countries, commodity, batch):
    if batch:
        return f"review batch: {commodity} ({len(countries)} countr{'y' if len(countries) == 1 else 'ies'})"
    return f"{', '.join(countries)} {commodity}".strip()


def skipped_dirs(data, stats, countries, commodity, root):
    """What the build left out under the countries' scope dirs, for the build report:
    {"no_store": [dir labels with none of the store files], "other_scope": [dirs whose store names
    another scope], "loose": [files sitting in staging/ itself], "recon": [recon-* dirs, read but
    skipped while SKIP_RECON_DIRS], "routeqc", "wikidiff", "updates": record and store counts}."""
    root, have = Path(root), set(data.get("dirs", []))
    out = {"no_store": [], "other_scope": [], "loose": [], "recon": [],
           "routeqc": stats.get("routeqc_skipped", 0), "wikidiff": stats.get("wikidiff_skipped", 0),
           "updates": stats.get("updates_skipped", 0)}
    for c in countries:
        if c == review_data.TRACKER_WIDE:
            continue
        sd = root / staged_store.scope_dirname(c, commodity) / "staging"
        for d in sorted(sd.glob("*")) if sd.is_dir() else []:
            label = review_data._rel(d, root)
            if not d.is_dir():
                out["loose"].append(label)
            elif label in have:
                if review_data.SKIP_RECON_DIRS and d.name.startswith("recon-"):
                    out["recon"].append(label)
            elif not any((d / fn).exists() for fn in staged_store._STORE_FILES):
                out["no_store"].append(label)
            else:
                out["other_scope"].append(label)
    return out


def build_dataset(countries, commodity, dirs=None, exclude_pids=(), snapshot=None, batches_root=None,
                  data_dir=None, sync=False, batch=False, include_done=False, emails=None, led=None, write=True):
    """Build, overlay, sync, carry, stamp: the dataset both pages show. -> (data, report dict).
    No network unless `led` (a ledger.Ledger): then the records this run writes -- backend syncs
    with `sync`, carried-forward decisions -- go to the decision store first. `batch` = the
    countries are the review-app batch: all-decided ones are dropped (unless `include_done`),
    exactly as review_data.main does for the local server; that drop comes last, so carries and
    orphans see every country. `write=False` = a dry run: carries are reported, not appended, and
    the backend sync stays in memory (nothing lands in a sidecar that the decision store does not
    hold). Without `sync` the backend sync is always in memory (sync_in_memory)."""
    root = Path(batches_root) if batches_root else staged_store.BATCHES_ROOT
    ds, dir_country = review_data._country_dirs(countries, commodity, root, dirs)
    if batch:   # an included country with no staging dir left (archived) has nothing to show
        have = set(dir_country.values())
        countries = [c for c in countries if c in have]
    if not ds:
        raise SystemExit(f"no staging dirs found for {', '.join(countries)} {commodity}")
    data, stats = review_data.build(ds, countries, commodity, snapshot=snapshot, data_dir=data_dir,
                                    exclude_pids=list(exclude_pids), root=root, dir_country=dir_country)
    data["scope"]["batch"] = batch
    base = root.parent
    paths_by_label = store.dir_paths(data, base)
    snap = data.get("scope", {}).get("snapshot", "")
    sink = None
    if led is not None:
        led.scope, led.snapshot = ledger.scope_of(data)
        sink = led.sink
    synced = []
    if sync and write:
        if led is not None:
            led.origin = "sync"
        synced = store.sync_backend(data, paths_by_label, snap, sink=sink)
        store.overlay(data, paths_by_label)
    if led is not None:
        led.origin = "publish"
    carried = carry_forward(data, paths_by_label, sink=sink, write=write)
    if carried and write:
        store.overlay(data, paths_by_label)
    synced_mem = [] if (sync and write) else sync_in_memory(data, paths_by_label, snap)
    drifted = stamp_basis(data, paths_by_label)
    lost = orphans(data, paths_by_label)
    why = explain_orphans(data, paths_by_label, stray=stray_logs(data, countries, commodity, root),
                          carried=[] if write else carried)
    restore_reviewers(data, paths_by_label, emails)
    label_country = {review_data._rel(d, root): dir_country.get(Path(d).resolve(), countries[0]) for d in ds}
    review_data.settle_countries(data, label_country, countries, stats, drop=batch and not include_done)
    rep = {"summary": review_data.summary(data, stats), "drift": drifted, "orphans": lost, "orphan_reasons": why,
           "carried": carried, "synced": len(synced), "synced_in_memory": len(synced_mem), "dry": not write,
           "decided": sum(1 for p in data["pipelines"] for l in p["lines"] if l.get("reviewed")),
           "countries": countries, "stats": stats, "label": scope_label(countries, commodity, batch),
           "skipped": skipped_dirs(data, stats, countries, commodity, root)}
    return data, rep


def publish(countries, commodity, out, dirs=None, exclude_pids=(), snapshot=None, sid=None, cursor=1,
            batches_root=None, data_dir=None, sync=False, ver=None, target=PART_BYTES, batch=False,
            include_done=False, emails=None, led=None, write=True):
    """build_dataset, then write the mirror. -> (entry, report dict). The store cursor advances
    past the records the build wrote to the decision store (`led`)."""
    data, rep = build_dataset(countries, commodity, dirs=dirs, exclude_pids=exclude_pids, snapshot=snapshot,
                              batches_root=batches_root, data_dir=data_dir, sync=sync, batch=batch,
                              include_done=include_done, emails=emails, led=led, write=write)
    countries = rep["countries"]
    root = Path(batches_root) if batches_root else staged_store.BATCHES_ROOT
    if led is not None and led.last_row:
        cursor = max(int(cursor), led.last_row)      # the page lays only rows AFTER this dataset over it
    sid = sid or (f"review-app-{commodity.lower()}" if batch else scope_id(countries, commodity))
    build = {"country": list(countries), "commodity": commodity, "batch": batch, "include_done": include_done,
             "dirs": [str(d) for d in dirs] if dirs else None, "exclude_pids": sorted(exclude_pids)}
    entry = write_scope(data, out, sid, cursor, root.parent, ver=ver, build=build, target=target,
                        label=rep["label"] if batch else None)
    write_scopes(out, merge_scopes(read_scopes(Path(out) / "scopes.json"), entry))
    rep["files"] = {n: (Path(out) / n).stat().st_size
                    for n in entry["parts"] + [entry["index"]] + ([entry["geo"]] if entry["geo"] else [])}
    return entry, rep


def report(entry, rep):
    c = entry["counts"]
    out = [f"scope {entry['id']}  version {entry['ver']}  snapshot {entry['snapshot']}",
           f"  {c['pipelines']} pipelines, {c['lines']} lines, {c['items']} items; {rep['decided']} lines decided by a person",
           f"  store cursor (last sheet row already in this dataset): {entry['store_cursor']}"]
    out += [f"  {n:<52} {s:>10,} bytes" for n, s in rep["files"].items()]
    if rep["synced"]:
        out.append(f"  backend sync: {rep['synced']} machine records written for lines the sheet already holds")
    if rep.get("synced_in_memory"):
        out.append(f"  backend sync in memory only: {rep['synced_in_memory']} records shown, not written (--refresh writes them)")
    out.append(f"  drift (decided against backend cells that have since changed): {len(rep['drift'])}")
    out += [f"    {l['key']}  decided by {l.get('decided_by')} on {l['drift'].get('decided_snapshot') or '?'}" for l in rep["drift"][:25]]
    out.append(f"  carried forward (a person's decision moved to its line's new sheet row): {len(rep['carried'])}"
               + ("  -- DRY RUN (--no-pull): reported, not written; run without --no-pull to carry them" if rep.get("dry") and rep["carried"] else ""))
    out += [f"    {r['rekeyed_from']}  ->  row {r['sheet_row']}  {r.get('decision') or r.get('call')}  {r.get('reviewer')}"
            for r in rep["carried"][:25]]
    out.append(f"  orphans (a person's decision whose key matches no line of this build): {len(rep['orphans'])}")
    out += [f"    {r['key']}  {r.get('decision') or r.get('call')}  {r.get('reviewer')}  {r.get('ts')}" for r in rep["orphans"][:25]]
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--country", action="append", default=None,
                    help="repeat (or comma-separate) for several countries; omit for the review-app batch")
    ap.add_argument("--commodity", choices=["gas", "oil"], default=None,
                    help="required with --country; default gas for the review-app batch")
    ap.add_argument("--include-done", action="store_true", help="review-app batch: keep countries with nothing left to decide")
    ap.add_argument("--manifest", default=None, help="review-app batch manifest (default batches/review-app/manifest.json)")
    ap.add_argument("--dirs", nargs="*", default=None, help="explicit staging dirs (skips discovery)")
    ap.add_argument("--exclude-pids", default="", help="comma-separated ProjectIDs to drop")
    ap.add_argument("--snapshot", default=None, help="tracker snapshot CSV (default: the newest data/ snapshot)")
    ap.add_argument("--scope-id", default=None, help="default: review-app-<commodity>, or <country-slug>-<commodity> with --country")
    ap.add_argument("--refresh", action="store_true", help="pull the live sheet first (scripts/refresh_csvs.sh), then backend-sync")
    ap.add_argument("--no-pull", action="store_true", help="do not read the Google decision store (cursor 1)")
    ap.add_argument("--out", default=None, help="local mirror of the Drive folder (default work/review_publish)")
    ap.add_argument("--upload", action="store_true", help="list what the Drive data folder would change")
    ap.add_argument("--yes", action="store_true", help="with --upload: actually write to Drive")
    ap.add_argument("--config", default=None, help="default review_app/google.json")
    ap.add_argument("--batches-root", default=None, help=argparse.SUPPRESS)
    ap.add_argument("--data-dir", default=None, help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    cfg = pull_mod.config(a.config)
    batch = not a.country
    if batch:
        a.commodity = a.commodity or "gas"
        countries = scopes.included(a.commodity, a.manifest)
        if not countries:
            raise SystemExit(f"the review-app batch includes no {a.commodity} countries: "
                             "python review_app/scopes.py set --country C --commodity c yes")
    else:
        if not a.commodity:
            ap.error("--commodity is required with --country")
        countries = list(dict.fromkeys(c.strip() for cs in a.country for c in cs.split(",") if c.strip()))
    if a.no_pull and a.upload and cfg.get("store_sheet_id"):
        raise SystemExit("--no-pull with --upload would publish a dataset that ignores the decision store: refused")
    if a.yes and not a.upload:
        raise SystemExit("--yes only means something with --upload")
    out = Path(a.out) if a.out else paths.work_dir() / "review_publish"
    if a.refresh:
        r = subprocess.run([str(ROOT / "scripts" / "refresh_csvs.sh")], cwd=ROOT)
        if r.returncode != 0:
            raise SystemExit(f"refresh failed (exit {r.returncode}): nothing published")
    cursor, emails = 1, {}
    if not a.no_pull:
        try:
            res = pull_mod.pull(cfg, root=Path(a.batches_root).parent if a.batches_root else None)
        except pull_mod.GwsError as e:
            raise SystemExit(f"pull failed: {e}\n(auth? run `gws-gem auth login` yourself; it needs a browser)")
        print(pull_mod.report(res), file=sys.stderr)
        cursor, emails = res["cursor"], res["emails"]
    led = None
    if cfg.get("store_sheet_id") and not a.no_pull:
        led = ledger.Ledger(cfg["store_sheet_id"], "", "", "publish", reviewer_email=ledger.whoami(), emails=emails)
    try:
        entry, rep = publish(countries, a.commodity, out, dirs=a.dirs,
                             exclude_pids=[p for p in a.exclude_pids.split(",") if p], snapshot=a.snapshot,
                             sid=a.scope_id, cursor=cursor, batches_root=a.batches_root, data_dir=a.data_dir,
                             sync=a.refresh, batch=batch, include_done=a.include_done, emails=emails, led=led,
                             write=not (a.no_pull and cfg.get("store_sheet_id")))
    except ledger.StoreError as e:
        raise SystemExit(f"{e}\nnothing published: the records this run would write could not reach the decision store")
    print(report(entry, rep))
    print(f"mirror written to {out}")
    if a.upload:
        try:
            upload(out, entry, cfg, yes=a.yes)
        except pull_mod.GwsError as e:
            raise SystemExit(f"upload failed: {e}")
        if a.yes and batch:      # record what the live Google page was built from (review_app/artifacts.json)
            import build_all
            pub = build_all.mark_google(a.commodity)
            if pub:
                print(f"artifacts.json: Google page marked published ({pub['profile']} profile)")
    return entry, rep


if __name__ == "__main__":
    main()
