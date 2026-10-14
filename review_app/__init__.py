"""Local review app for staged pipelines research (see review_app/README.md).

The app itself is shared with the other GEM researcher repos and lives in the sibling checkout ../gem-review-app (same convention as ../gem-db-ops). Importing this package puts that checkout on sys.path. GEM_REVIEW_APP in the environment overrides the location.
"""
import os
import sys
from pathlib import Path

GEM_REVIEW_APP = Path(os.environ.get("GEM_REVIEW_APP") or Path(__file__).resolve().parent.parent.parent / "gem-review-app").resolve()

if not (GEM_REVIEW_APP / "review_core" / "store.py").is_file():
    raise ImportError(f"the shared review app is not at {GEM_REVIEW_APP}: clone gem-review-app next to this repo, "
                      "or set GEM_REVIEW_APP to its folder")
if str(GEM_REVIEW_APP) not in sys.path:
    sys.path.append(str(GEM_REVIEW_APP))
