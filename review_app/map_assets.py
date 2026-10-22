"""
Record map pictures uploaded to an artifact page, so the next build of that page shows them.

    python review_app/build_all.py --assets gas-batch          # the files that page has not uploaded yet
    (upload them with the Artifact tool: publish, url = the page's url, asset: true, file_paths = up to 25 of them)
    python review_app/map_assets.py --page gas-batch NAME=URL ...
    python review_app/map_assets.py --page gas-batch --uploads results.json     # {"<asset name>": "<url>", ...}
    python review_app/build_all.py --only gas-batch               # rebuild with the urls filled in, then publish

NAME is the uploaded file's name in work/review_assets/ (<sha256>.jpg or .png); a path to it works too. URL is
the url the upload returned, as given. The record goes into review_app/assets.json (review_core/assets.py), which
is committed so every session's build reuses the uploads. Nothing here uploads, publishes or writes Drive.
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

import store  # noqa: E402,F401  (puts ../gem-review-app on sys.path)
from review_core import assets  # noqa: E402
from review_core import pages  # noqa: E402

REGISTRY = HERE / "artifacts.json"
MANIFEST = HERE / "assets.json"


def page_url(name, registry=None):
    for e in pages.load_entries(registry or REGISTRY):
        if e["name"] == name:
            if not e.get("url"):
                raise SystemExit(f"page {name} has no url in artifacts.json")
            return e["url"]
    raise SystemExit(f"no page named {name} in artifacts.json")


def parse(pairs, uploads_file=None):
    """{asset name: url} from NAME=URL pairs and/or a JSON file; a path is cut to its file name."""
    out = json.loads(Path(uploads_file).read_text(encoding="utf-8")) if uploads_file else {}
    for p in pairs:
        name, sep, url = p.partition("=")
        if not sep:
            raise SystemExit(f"expected NAME=URL: {p}")
        out[name] = url
    return {Path(k).name: v for k, v in out.items()}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--page", required=True, help="the page name in artifacts.json")
    ap.add_argument("--uploads", default=None, help="a JSON file of {asset name: url}")
    ap.add_argument("pairs", nargs="*", help="NAME=URL")
    a = ap.parse_args(argv)
    ups = parse(a.pairs, a.uploads)
    if not ups:
        ap.error("nothing to record")
    url = page_url(a.page)
    n = assets.record(MANIFEST, url, ups, root=ROOT)
    print(f"recorded {n} uploads for {a.page} ({url}) in {MANIFEST.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
