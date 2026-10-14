"""
Say which live review pages are stale, and rebuild the artifact pages from the shared interface in the
sibling gem-review-app repo (review_core/web plus trackers/pipelines/web).

    python review_app/build_all.py --check               # fresh / stale (why) / unmarked per page; exit 1 if any is not fresh
    python review_app/build_all.py [--only NAME] [--all] # build the stale or unmarked artifact pages (--all: every one)
    python review_app/build_all.py --mark-published NAME # after publishing NAME's file to its url
    python review_app/build_all.py --hook EVENT          # Claude Code hook (SessionStart, UserPromptSubmit, Stop)

An artifact page is built with build_static.py into work/review_static/<name>.html and printed as name, url
and file: publish that file to its url (Artifact tool, work profile), then --mark-published NAME records what
the page was built from. A Google page (kind google, parked 2026-10-09) would be refreshed by `publish.py --upload --yes` (ask Baird
first) and marks itself published. The check makes no network call and never reads the decision store; a stale
review_log.jsonl is caught when the build's pull runs. The dirs of a batch page are resolved at check time from
batches/review-app/manifest.json, so a new staging dir for an included country makes the page stale on its own;
the `manifest` part is the hash of the included country list (a declined or later country changes nothing).
Logic: ../gem-review-app/review_core/pages.py; plan: ../gem-review-app/docs/refresh.md.
"""
import argparse
import hashlib
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
from review_core import hooks, pages  # noqa: E402

REGISTRY = HERE / "artifacts.json"
LAST_BUILD = ROOT / pages.LAST_BUILD
DATA = ROOT / "data"


def _countries(entry):
    sc = entry.get("scope") or {}
    return list(sc["countries"]) if sc.get("countries") else scopes.included(sc.get("commodity", "gas"))


def _dirs(entry):
    if entry.get("dirs"):
        return [ROOT / d for d in entry["dirs"]]
    sc = entry.get("scope") or {}
    dirs, _ = review_data._country_dirs(_countries(entry), sc.get("commodity", "gas"), staged_store.BATCHES_ROOT)
    return [Path(d) for d in dirs]


def _extra(entry):
    commodity = (entry.get("scope") or {}).get("commodity", "gas")
    tracker = review_data._pick_snapshot(commodity, [], DATA)
    owners = review_data._pick_owners([], tracker, DATA)
    return {"manifest": hashlib.sha256("|".join(sorted(_countries(entry))).encode()).hexdigest(),
            "snapshot": tracker.name if tracker else "", "owners": owners.name if owners else ""}


def adapter():
    return pages.PageAdapter(
        root=ROOT, resolve_dirs=_dirs,
        staged_files=lambda d: sorted(p.name for p in Path(d).glob("staged_*.json")),
        decision_files=("review_log.jsonl",), extra_inputs=_extra,
        builder_files=tuple(f"review_app/{n}" for n in ("review_data.py", "publish.py", "build_static.py", "store.py", "bundle.py")))


def reports():
    return pages.check(pages.load_entries(REGISTRY), adapter(), store.CONFIG)


def mark(name):
    """Record the CURRENT inputs as what page `name` was built from, then mark it published. For the Google
    page, publish.py calls this right after a successful upload (its pull and sync already ran, so the
    inputs on disk are the ones the uploaded dataset was built from)."""
    entry = next((e for e in pages.load_entries(REGISTRY) if e["name"] == name), None)
    if entry is None:
        raise KeyError(name)
    fp, parts = pages.fingerprint(entry, adapter(), store.CONFIG)
    pages.record_build(LAST_BUILD, name, fp, parts, datetime.now(store.ET).isoformat(timespec="seconds"))
    return pages.mark_published(REGISTRY, name, LAST_BUILD, adapter(), store.CONFIG)


def mark_google(commodity):
    """After publish.py --upload --yes: mark the google entry for that commodity published (quietly nothing when none)."""
    for e in pages.load_entries(REGISTRY):
        if e.get("kind") == "google" and (e.get("scope") or {}).get("commodity") == commodity:
            return mark(e["name"])
    return None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--only", help="build just this page name")
    ap.add_argument("--all", action="store_true", help="build every artifact page, not just the stale or unmarked ones")
    ap.add_argument("--check", action="store_true", help="report which pages are stale; exit 1 if any is not fresh")
    ap.add_argument("--mark-published", metavar="NAME", help="record the last build of NAME as published")
    ap.add_argument("--hook", metavar="EVENT", help="Claude Code hook mode")
    args = ap.parse_args(argv)
    if args.hook:
        out = hooks.hook(args.hook, sys.stdin.read(), reports(), paths.work_dir())
        if out:
            print(out)
        return
    if args.mark_published:
        try:
            name = args.mark_published
            entry = next((e for e in pages.load_entries(REGISTRY) if e["name"] == name), None)
            if entry and entry.get("kind") == "google":
                raise SystemExit(f"{name} is the Google page: publish.py --upload --yes marks it")
            pub = pages.mark_published(REGISTRY, name, LAST_BUILD, adapter(), store.CONFIG)
        except (pages.PublishError, KeyError) as e:
            raise SystemExit(f"not marked: {e}")
        print(f"{name} marked published ({pub['profile']} profile, built {pub['built']})")
        return
    if args.check:
        bad = False
        for r in reports():
            print(f"{r['name']}\t{r['status']}" + (f"\t{'; '.join(r['reasons'])}" if r["reasons"] else ""))
            bad = bad or r["status"] != "fresh"
        sys.exit(1 if bad else 0)
    entries = pages.load_entries(REGISTRY)
    if args.only:
        entries = [e for e in entries if e["name"] == args.only]
        if not entries:
            raise SystemExit(f"no page named {args.only} in artifacts.json")
    elif not args.all:
        todo = {r["name"] for r in reports() if r["status"] != "fresh"}
        entries = [e for e in entries if e["name"] in todo]
    import build_static   # late: it imports publish, which imports this module's mark_google lazily
    rows = []
    for e in entries:
        if e.get("kind") == "google":
            print(f"{e['name']}\tgoogle\trefresh with: python review_app/publish.py --upload --yes (ask Baird first)")
            continue
        sc = e.get("scope") or {}
        out = paths.work_dir() / "review_static" / f"{e['name']}.html"
        argv2 = ["--commodity", sc.get("commodity", "gas"), "--out", str(out)]
        for c in (sc["countries"] if sc.get("countries") else []):
            argv2 += ["--country", c]
        if e.get("dirs"):
            argv2 += ["--dirs", *[str(ROOT / d) for d in e["dirs"]]]
        build_static.main(argv2)
        fp, parts = pages.fingerprint(e, adapter(), store.CONFIG)      # after the build's pull: the sidecars it wrote
        pages.record_build(LAST_BUILD, e["name"], fp, parts, datetime.now(store.ET).isoformat(timespec="seconds"), out)
        rows.append((e["name"], e.get("url", ""), out))
    if not rows and not entries:
        print("every page is fresh; nothing to build (--all to rebuild anyway)")
    for name, url, out in rows:
        print(f"{name}\t{url}\t{out}")


if __name__ == "__main__":
    main()
