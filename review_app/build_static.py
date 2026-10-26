"""
Build the review app as ONE self-contained page, for a claude.ai artifact (or to open from disk).

    python review_app/build_static.py                      # the review-app gas batch -> work/review_static/gas-batch.html
    python review_app/build_static.py --country Ukraine --commodity gas
      [--commodity gas|oil] [--include-done] [--dirs DIR ...] [--exclude-pids P1,P2] [--snapshot CSV]
      [--no-pull] [--reviewer BL] [--out FILE] [--artifact URL]

The page is built by the shared builder in ../gem-review-app (review_core/build_static.py): the shared page (review_core/web: index.html, style.css, static_store.js, app.js) and the pipelines extension (trackers/pipelines/web: ext.css, ext.js), with the dataset inside it: the dataset publish.build_dataset builds (review_data.build, the decision overlay, the backend sync, `basis` stamps; the same one publish.py writes for the parked Google page), gzipped with its key index (review_core.build_static.pack_index) into one inline block. There is no server behind it. The page store (static_store.js plus the pipelines checks in ext.js) checks each decision against the index the way gas/Code.gs does and keeps the records in the reviewer's browser and, on a published artifact, in the artifact's shared database.

What it does, in order:
  1. pull.py: mirror the Google decision store (the store spreadsheet's `log` tab) into the
     staging dirs' review_log.jsonl, so the page starts from every decision made so far. --no-pull
     skips it (and reads nothing from Google). When the pull fails (auth, network), the build
     says so on stderr and goes on from the sidecars as they are, writing nothing.
  2. publish.build_dataset. A line the sheet already holds that no one has decided shows as
     accepted by "backend sync", in memory only (publish.sync_in_memory). A person's decision
     whose line moved to a new sheet row is carried forward to it (store `log` tab first, then the
     sidecar), exactly as publish.py does, so the page shows it decided. With --no-pull, or after a
     failed pull, nothing is written and the carries are only reported.
  3. Write the page. It has no doctype / html / head / body tags of its own: the Artifact tool wraps
     it, and a browser opening the file from disk does the same.
  4. Fill each map picture's url from review_app/assets.json for the page at --artifact (build_all.py
     passes the registry url) and write <page>.assets.json next to it: every picture the page shows and
     the ones that page has not uploaded yet (an image with no url shows its caption only). Upload those
     with the Artifact tool and record them with review_app/map_assets.py, then rebuild.
  5. Write orphans.json next to the page: every earlier decision whose key matches nothing in this
     build, grouped by reason (publish.ORPHAN_REASONS), and what the build skipped under the
     countries' scope dirs. The counts are printed too.

Publish the file with the Artifact tool, capabilities {db: {}, user: {scopes: ["profile"]},
downloads: true, comments: {}} (the "email" scope is refused by the publish service, 2026-10-05; comments lets "push to log"
wake the watching session, 2026-10-15), from the WORK profile (~/.claude-gem): the shared log and the download button only
work for members of the publishing account's organization. Share it by email, as an editor; a viewer
who can only view, or who opens a link share, keeps their decisions in the browser and is offered
"download decisions". Publishing a rebuilt file to the same url keeps the link.

Decisions come back through review_app/import_log.py (store `log` tab first, sidecars second).
Apart from those carried-forward records (store `log` tab first, then the sidecars), nothing here writes the decision store; it never writes the backend sheet, Drive, the routes repo or staged_*.json.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for p in (ROOT / "scripts", HERE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import ledger  # noqa: E402
import paths  # noqa: E402
import publish  # noqa: E402
import pull as pull_mod  # noqa: E402
import scopes  # noqa: E402
import store  # noqa: E402
from review_core import assets as core_assets  # noqa: E402
from review_core import build_static as core  # noqa: E402

WEB = core.CORE_WEB                   # the shared page; the pipelines extension is store.CONFIG.web_dir
SCRIPTS = core.CORE_SCRIPTS           # ("static_store.js", "app.js"), inlined in this order, then ext.js
MAX_BYTES = core.MAX_BYTES            # the Artifact tool's page limit
BLOB_ID = core.BLOB_ID
blob = core.blob
ASSETS = HERE / "assets.json"         # uploaded map pictures, per artifact page (review_core/assets.py)


def ledger_url(cfg=None):
    sheet = (cfg if cfg is not None else pull_mod.config(None) or {}).get("store_sheet_id") or ""
    return f"https://docs.google.com/spreadsheets/d/{sheet}/edit" if sheet else ""


def render(data, index=None, reviewer=""):
    """The page: title and style first, the app's body, the dataset block, then the scripts (review_core.build_static.render with the pipelines config). `index` defaults to the shared packer (review_core.build_static.pack_index), the index publish.write_scope writes too."""
    return core.render(data, reviewer, store.CONFIG, index=index, ledger_url=ledger_url(), root=store.ROOT)


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
    ap.add_argument("--out", default=None, help="default work/review_static/<commodity>-batch.html, or <scope id>.html with --country")
    ap.add_argument("--config", default=None, help="default review_app/google.json")
    ap.add_argument("--artifact", default="", help="the artifact url the page goes to: fills map picture urls from review_app/assets.json")
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
    led, pulled = None, False
    if not a.no_pull:
        cfg = pull_mod.config(a.config)
        try:
            res = pull_mod.pull(cfg, root=Path(a.batches_root).parent if a.batches_root else None)
        except pull_mod.GwsError as e:
            print(f"WARN pull failed: {e}\n(auth? run `gws-gem auth login` yourself; it needs a browser)\n"
                  "building from the sidecars as they are; nothing is written to the decision store", file=sys.stderr)
        else:
            pulled = True
            print(pull_mod.report(res), file=sys.stderr)
            if cfg.get("store_sheet_id"):      # carries go to the store first, as in publish.py
                led = ledger.Ledger(cfg["store_sheet_id"], "", "", "publish", reviewer_email=ledger.whoami(),
                                    emails=res["emails"])
    try:
        data, rep = publish.build_dataset(countries, a.commodity, dirs=a.dirs,
                                          exclude_pids=[p for p in a.exclude_pids.split(",") if p], snapshot=a.snapshot,
                                          batches_root=a.batches_root, data_dir=a.data_dir, batch=batch,
                                          include_done=a.include_done, led=led, write=pulled)
    except ledger.StoreError as e:
        raise SystemExit(f"{e}\nnothing built: the carried-forward decisions could not reach the decision store")
    reviewer = a.reviewer if a.reviewer is not None else git_initials()
    shown = list(dict.fromkeys(i["asset"] for i in core_assets.images_in(data)))
    missing = core_assets.fill_urls(data, core_assets.load_manifest(ASSETS), a.artifact) if shown else []
    page = render(data, reviewer=reviewer)
    size = len(page.encode("utf-8"))
    name = f"{a.commodity}-batch" if batch else publish.scope_id(countries, a.commodity)
    out = Path(a.out) if a.out else paths.work_dir() / "review_static" / f"{name}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page, encoding="utf-8")
    asset_list(out).write_text(json.dumps({"artifact": a.artifact, "shown": shown, "missing": missing}, indent=1) + "\n",
                               encoding="utf-8")
    pipes = data["pipelines"]
    print(f"{rep['label']}: {len(pipes)} pipelines, {sum(len(p['lines']) for p in pipes)} lines, "
          f"{sum(len(p['items']) for p in pipes)} items; {rep['decided']} lines already decided by a person; "
          f"snapshot {data['scope'].get('snapshot', '')}")
    if rep["synced_in_memory"]:
        print(f"  {rep['synced_in_memory']} backend sync records shown in memory "
              "(lines the sheet already holds that no one had decided; not written)")
    if rep["carried"]:
        print(f"  {len(rep['carried'])} decisions carried forward to a new sheet row"
              + (": reported only (nothing written)" if rep.get("dry") else ""))
    orphans_file = write_orphans(out.parent / "orphans.json", data, rep, out.name)
    print(f"  {len(rep['orphan_reasons'])} earlier decisions match no line of this build ({orphans_file}):")
    counts = orphan_counts(rep["orphan_reasons"])
    for reason, n in counts.items():
        print(f"    {reason}: {n}")
    sk = rep["skipped"]
    print(f"  skipped under the scope dirs: {len(sk['no_store'])} dirs with no store file, "
          f"{len(sk['other_scope'])} dirs whose store names another scope, {len(sk['loose'])} loose files, "
          f"{len(sk['recon'])} recon dirs; records: {sk['routeqc']} route-QC, {sk['wikidiff']} sheet-vs-wiki diffs, "
          f"{sk['updates']} country update stores")
    if shown:
        print(f"  {len(shown)} map pictures, {len(missing)} not uploaded for "
              f"{a.artifact or 'any page (no --artifact)'}; list: build_all.py --assets <page>")
    print(f"wrote {out} ({size:,} bytes)")
    if size > MAX_BYTES:
        raise SystemExit(f"the page is over the artifact limit of {MAX_BYTES:,} bytes: narrow it with --country")
    return out


def asset_list(page):
    """The <page>.assets.json written beside a built page: {artifact, shown, missing} asset names."""
    page = Path(page)
    return page.with_name(page.stem + ".assets.json")


def orphan_counts(orphans):
    """{reason: n} in publish.ORPHAN_REASONS order, every reason listed."""
    return {r: sum(1 for o in orphans if o["reason"] == r) for r in publish.ORPHAN_REASONS}


def write_orphans(path, data, rep, page):
    """orphans.json: {built, page, snapshot, counts, reasons (what each means), orphans {reason: [...]},
    skipped (publish.skipped_dirs)}. -> the path."""
    body = {"built": data.get("built", ""), "page": page, "snapshot": data["scope"].get("snapshot", ""),
            "counts": orphan_counts(rep["orphan_reasons"]), "reasons": publish.ORPHAN_REASONS,
            "orphans": {r: [o for o in rep["orphan_reasons"] if o["reason"] == r] for r in publish.ORPHAN_REASONS},
            "skipped": rep["skipped"]}
    Path(path).write_text(json.dumps(body, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


if __name__ == "__main__":
    main()
