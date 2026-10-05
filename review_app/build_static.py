"""
Build the review app as ONE self-contained page, for a claude.ai artifact (or to open from disk).

    python review_app/build_static.py                      # the review-app gas batch -> work/review_static/pipelines-reviewer.html
    python review_app/build_static.py --country Ukraine --commodity gas
      [--commodity gas|oil] [--include-done] [--dirs DIR ...] [--exclude-pids P1,P2] [--snapshot CSV]
      [--no-pull] [--reviewer BL] [--out FILE]

The page is review_app/web/ (index.html, style.css, static_store.js, app.js) with the dataset inside
it: the same dataset publish.py builds for the Google page (review_data.build, the decision overlay,
`basis` stamps), gzipped with its key index into one inline block. There is no server behind it.
web/static_store.js checks each decision against the index the way gas/Code.gs does and keeps the
records in the reviewer's browser and, on a published artifact, in the artifact's shared database.

What it does, in order:
  1. pull.py: mirror the Google decision store into the staging dirs' review_log.jsonl, so the page
     starts from every decision made so far. --no-pull skips it (and reads nothing from Google).
  2. publish.publish(write=False) into a temporary folder: no store write, no sidecar write, no
     Drive upload. Carry-forwards are reported, not written (run publish.py for those).
  3. Write the page. It has no doctype / html / head / body tags of its own: the Artifact tool wraps
     it, and a browser opening the file from disk does the same.

Publish the file with the Artifact tool, capabilities {db: {}, user: {scopes: ["profile"]},
downloads: true} (the "email" scope is refused by the publish service, 2026-10-05), from the WORK profile (~/.claude-gem): the shared log and the download button only
work for members of the publishing account's organization. Share it by email, as an editor; a viewer
who can only view, or who opens a link share, keeps their decisions in the browser and is offered
"download decisions". Publishing a rebuilt file to the same url keeps the link.

Decisions come back through review_app/import_log.py (store `log` tab first, sidecars second).
Nothing here writes the decision store, the backend sheet, Drive, the routes repo or staged_*.json.
"""
import argparse
import base64
import gzip
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for p in (ROOT / "scripts", HERE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import bundle  # noqa: E402
import paths  # noqa: E402
import publish  # noqa: E402
import pull as pull_mod  # noqa: E402
import scopes  # noqa: E402
import store  # noqa: E402

WEB = HERE / "web"
SCRIPTS = ("static_store.js", "app.js")
MAX_BYTES = 16 * 1024 * 1024          # the Artifact tool's page limit
BLOB_ID = "review-blob"


def read_scope(out, entry):
    """The dataset and the packed index publish.write_scope wrote into `out`."""
    out = Path(out)
    data = None
    for name in entry["parts"]:
        part = json.loads(gzip.decompress((out / name).read_bytes()).decode("utf-8"))
        if data is None:
            data = part
        else:
            data["pipelines"] += part["pipelines"]
    index = json.loads((out / entry["index"]).read_text(encoding="ascii"))
    return data, index


def blob(data, index):
    raw = json.dumps({"data": data, "index": index}, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    return base64.b64encode(gzip.compress(raw, 9, mtime=0)).decode("ascii")


def render(data, index, reviewer="", web=WEB):
    """The page: title and style first, the app's body, the dataset block, then the two scripts."""
    web = Path(web)
    html = (web / "index.html").read_text(encoding="utf-8")
    css = (web / "style.css").read_text(encoding="utf-8")
    if "</style" in css.lower():
        raise SystemExit("style.css: contains '</style'")
    m = re.search(r"<title>(.*?)</title>", html, re.S)
    b = re.search(r"<body[^>]*>(.*)</body>", html, re.S)
    if not m or not b:
        raise SystemExit("index.html: no <title> or no <body>")
    body = b.group(1)
    for name in bundle.SCRIPTS:
        tag = f'<script src="{name}"></script>'
        if body.count(tag) != 1:
            raise SystemExit(f"index.html: expected exactly one {tag}")
        body = body.replace(tag, "")
    left = re.findall(r'<(?:script|link)[^>]+(?:src|href)="(?!https?:)[^"]*"', body)
    if left:
        raise SystemExit(f"index.html still references local files the page cannot load: {left}")
    cfg = json.dumps({"reviewer": reviewer or "", "built": data.get("built", "")}).replace("</", "<\\/")
    return (f"<title>{m.group(1).strip()}</title>\n<style>\n{css.rstrip()}\n</style>\n"
            f"{body.strip()}\n"
            f'<script type="application/octet-stream" id="{BLOB_ID}">{blob(data, index)}</script>\n'
            f"<script>window.REVIEW_STATIC = {cfg};</script>\n"
            + "\n".join(bundle._inline_js(n, web) for n in SCRIPTS) + "\n")


def git_initials():
    try:
        name = subprocess.run(["git", "config", "user.name"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    except OSError:
        return ""
    who = store.initials(name)
    return who if who and store._INITIALS_RE.match(str(who)) else ""


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
    ap.add_argument("--no-pull", action="store_true", help="do not read the Google decision store first")
    ap.add_argument("--reviewer", default=None,
                    help="initials recorded when the file is opened from disk (default: from git user.name); "
                         "on a published artifact each viewer is recorded under their own")
    ap.add_argument("--out", default=None, help="default work/review_static/pipelines-reviewer.html")
    ap.add_argument("--config", default=None, help="default review_app/google.json")
    ap.add_argument("--batches-root", default=None, help=argparse.SUPPRESS)
    ap.add_argument("--data-dir", default=None, help=argparse.SUPPRESS)
    a = ap.parse_args(argv)
    batch = not a.country
    if batch:
        a.commodity = a.commodity or "gas"
        countries = scopes.included(a.commodity, a.manifest)
        if not countries:
            raise SystemExit(f"the review-app batch includes no {a.commodity} countries")
    else:
        if not a.commodity:
            ap.error("--commodity is required with --country")
        countries = list(dict.fromkeys(c.strip() for cs in a.country for c in cs.split(",") if c.strip()))
    if not a.no_pull:
        try:
            res = pull_mod.pull(pull_mod.config(a.config), root=Path(a.batches_root).parent if a.batches_root else None)
        except pull_mod.GwsError as e:
            raise SystemExit(f"pull failed: {e}\n(auth? run `gws-gem auth login` yourself; it needs a browser)")
        print(pull_mod.report(res), file=sys.stderr)
    with tempfile.TemporaryDirectory() as tmp:
        entry, rep = publish.publish(countries, a.commodity, tmp, dirs=a.dirs,
                                     exclude_pids=[p for p in a.exclude_pids.split(",") if p], snapshot=a.snapshot,
                                     batches_root=a.batches_root, data_dir=a.data_dir, batch=batch,
                                     include_done=a.include_done, write=False)
        data, index = read_scope(tmp, entry)
    reviewer = a.reviewer if a.reviewer is not None else git_initials()
    page = render(data, index, reviewer=reviewer)
    size = len(page.encode("utf-8"))
    out = Path(a.out) if a.out else paths.work_dir() / "review_static" / "pipelines-reviewer.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    c = entry["counts"]
    print(f"{entry['label']}: {c['pipelines']} pipelines, {c['lines']} lines, {c['items']} items; "
          f"{rep['decided']} lines already decided by a person; snapshot {entry['snapshot']}")
    if rep["carried"]:
        print(f"  {len(rep['carried'])} decisions would carry forward to a new sheet row: not written here, run publish.py")
    if rep["orphans"]:
        print(f"  {len(rep['orphans'])} earlier decisions match no line of this build (publish.py lists them)")
    print(f"wrote {out} ({size:,} bytes)")
    if size > MAX_BYTES:
        raise SystemExit(f"the page is over the artifact limit of {MAX_BYTES:,} bytes: narrow it with --country")
    return out


if __name__ == "__main__":
    main()
