"""
Say which live review pages are stale, and rebuild the artifact pages from the shared interface in the
sibling gem-review-app repo (review_core/web plus trackers/pipelines/web).

    python review_app/build_all.py --check               # fresh / stale (why) / unmarked per page; exit 1 if any is not fresh
    python review_app/build_all.py [--only NAME] [--all] [--no-pull] # build the stale or unmarked artifact pages (--all: every one)
    python review_app/build_all.py --list                # the page table: name, url, published at
    python review_app/build_all.py --mark-published NAME # after publishing NAME's file to its url
    python review_app/build_all.py --hook EVENT          # Claude Code hook (SessionStart, UserPromptSubmit, Stop): one JSON object

An artifact page is built with build_static.py into work/review_static/<name>.html and printed as name, url
and file: publish that file to its url (Artifact tool, work profile), then --mark-published NAME records what
the page was built from. A Google page (kind google, parked 2026-10-09) would be refreshed by `publish.py --upload --yes` (ask Baird
first) and marks itself published. The check makes no network call and never reads the decision store; a stale
review_log.jsonl is caught when the build's pull runs. The dirs of a batch page are resolved at check time from
batches/review-app/manifest.json, so a new staging dir for an included country makes the page stale on its own;
the `manifest` part is the hash of the included country list (a declined or later country changes nothing).

Each build pulls the decision store first (build_static.py); when that pull fails it warns and builds from the local logs, and --no-pull skips it. The command line itself is review_core.pages.cli and the hook output is the JSON contract in review_core/hooks.py. The check and the hook keep work/.review_pages_cache.json (pages.FileCache), so store files whose size and modification time did not change are not read again.

Logic: ../gem-review-app/review_core/pages.py; plan: ../gem-review-app/docs/refresh.md.
"""
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for p in (ROOT / "scripts", HERE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import paths  # noqa: E402
import review_data  # noqa: E402
import scopes  # noqa: E402
import staged_store  # noqa: E402
import store  # noqa: E402
from review_core import assets as core_assets  # noqa: E402
from review_core import pages  # noqa: E402

REGISTRY = HERE / "artifacts.json"
LAST_BUILD = ROOT / pages.LAST_BUILD
DATA = ROOT / "data"
ASSETS = HERE / "assets.json"         # uploaded map pictures, per artifact page (build_static.ASSETS)


def _countries(entry):
    sc = entry.get("scope") or {}
    return list(sc["countries"]) if sc.get("countries") else scopes.included(sc.get("commodity", "gas"))


def _dirs(entry, cache=None):
    if entry.get("dirs"):
        return [ROOT / d for d in entry["dirs"]]
    sc = entry.get("scope") or {}
    if cache is None:
        dirs, _ = review_data._country_dirs(_countries(entry), sc.get("commodity", "gas"), staged_store.BATCHES_ROOT)
    else:
        with staged_store.meta_cache(cache):
            dirs, _ = review_data._country_dirs(_countries(entry), sc.get("commodity", "gas"), staged_store.BATCHES_ROOT)
    return [Path(d) for d in dirs]


def _extra(entry):
    commodity = (entry.get("scope") or {}).get("commodity", "gas")
    tracker = review_data._pick_snapshot(commodity, [], DATA)
    owners = review_data._pick_owners([], tracker, DATA)
    out = {"manifest": hashlib.sha256("|".join(sorted(_countries(entry))).encode()).hexdigest(),
           "snapshot": tracker.name if tracker else "", "owners": owners.name if owners else ""}
    up = sorted((sha, v["url"]) for sha, per in core_assets.load_manifest(ASSETS).items()
                for art, v in per.items() if art == entry.get("url"))
    if up:      # a recorded upload changes the page (its picture urls); pages with none keep their old parts
        out["assets"] = hashlib.sha256(json.dumps(up).encode()).hexdigest()
    return out


def _assets(entry):
    """The map pictures the last build of this page showed (build_static writes <page>.assets.json)."""
    f = paths.work_dir() / "review_static" / f"{entry['name']}.assets.json"
    return json.loads(f.read_text(encoding="utf-8")).get("shown", []) if f.is_file() else []


def adapter(cache=None):
    """The page adapter. `cache` (a pages.FileCache) also covers the store meta that dir discovery reads."""
    return pages.PageAdapter(
        root=ROOT, resolve_dirs=lambda e: _dirs(e, cache),
        staged_files=lambda d: sorted(p.name for p in Path(d).glob("staged_*.json")),
        decision_files=("review_log.jsonl",), extra_inputs=_extra, assets=_assets, asset_manifest=ASSETS,
        builder_files=tuple(f"review_app/{n}" for n in ("review_data.py", "publish.py", "build_static.py", "store.py", "months.py")),
        cache=cache)


def reports():
    return pages.check(pages.load_entries(REGISTRY), adapter(), store.CONFIG)


def mark(name):
    """Record the CURRENT inputs as what page `name` was built from, then mark it published. For the Google
    page, publish.py calls this right after a successful upload (its pull and sync already ran, so the
    inputs on disk are the ones the uploaded dataset was built from)."""
    return pages.mark_current(REGISTRY, name, LAST_BUILD, adapter(), store.CONFIG,
                              datetime.now(store.ET).isoformat(timespec="seconds"))


def mark_google(commodity):
    """After publish.py --upload --yes: mark the google entry for that commodity published (quietly nothing when none)."""
    for e in pages.load_entries(REGISTRY):
        if e.get("kind") == "google" and (e.get("scope") or {}).get("commodity") == commodity:
            return mark(e["name"])
    return None


def build_page(entry, args):
    """Build one artifact page with build_static.py (which pulls first unless --no-pull) -> (file, built)."""
    import build_static   # late: it imports publish, which imports this module's mark_google lazily
    sc = entry.get("scope") or {}
    out = paths.work_dir() / "review_static" / f"{entry['name']}.html"
    argv = ["--commodity", sc.get("commodity", "gas"), "--out", str(out), "--artifact", entry.get("url", "")]
    for c in (sc["countries"] if sc.get("countries") else []):
        argv += ["--country", c]
    if entry.get("dirs"):
        argv += ["--dirs", *[str(ROOT / d) for d in entry["dirs"]]]
    if args.no_pull:
        argv.append("--no-pull")
    build_static.main(argv)
    return out, datetime.now(store.ET).isoformat(timespec="seconds")


def main(argv=None):
    cache = pages.FileCache(paths.work_dir() / pages.CACHE)
    return pages.cli(adapter(cache), REGISTRY, build_page, argv, config=store.CONFIG, last_build=LAST_BUILD,
                     work=paths.work_dir(), description=__doc__.split("\n\n")[0])


if __name__ == "__main__":
    main()
