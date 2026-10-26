"""
Mirror the Google decision store into the staging dirs (phase 2).

    python review_app/pull.py [--dry-run]

The Apps Script web app (review_app/gas/Code.gs) appends every decision to the `log` tab of the store spreadsheet named in review_app/google.json (`store_sheet_id`). This reads that tab with the READ-ONLY work profile (gws-gem) and appends each record it has not seen (by `id`) to the `review_log.jsonl` of the staging dir the record names, as stored (the server's timestamp and the extras `id`, `scope`, `batch`, `snapshot`, `basis`, `origin`) except for ONE field: the reviewer's email is written as their first and last INITIALS (store.initials: baird.langenbrunner@globalenergymonitor.org gives BL), the rule for every recorded reviewer, because the staging dirs are committed and the store spreadsheet is private. The store keeps the full address and is the authority on who decided what; two reviewers whose addresses share initials share them here, and the pull says so when it happens. Then it regenerates that dir's `review_decisions.json`. So after a pull the committed sidecars hold everything the sheet holds, `decisions.py` and `build_ref_workbook.py --decisions` read them as before, and git is the second copy of the history.

Idempotent: run it as often as you like. It never writes to Google. It returns (and prints) the cursor, the last sheet row it read; publish.py stores that in the published scope so the web app only lays rows AFTER it over the published dataset. The pull's `emails` map (never written to disk) lets publish.py put the full address back into the dataset it sends to the private Drive folder. The write profile (gws-gem-write) is used by publish.py --upload only.

A record is only ever written under <repo>/batches/: a `dir` that resolves anywhere else, or to a directory that does not exist, is reported and skipped.

The code is shared with gogpt-researcher and lives in ../gem-review-app/review_core/pull.py; this file holds the pipelines settings (the repo root, the store shim and review_app/google.json, whose keys are data_folder_id, store_sheet_id, script_id and web_app_url).
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import store  # noqa: E402  (first: importing it puts ../gem-review-app on the path)
from review_core import pull as core  # noqa: E402

core.bind(sys.modules[__name__], root=ROOT, store=store, config_path=HERE / "google.json")

if __name__ == "__main__":
    main()  # noqa: F821  (bound above)
