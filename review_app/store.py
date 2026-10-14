"""
The pipelines review app's decision store: the shared store in ../gem-review-app (review_core/store.py) bound to the pipelines config (trackers/pipelines/config.py).

Two sidecars live in each staging dir and are committed with the batch: review_log.jsonl (append-only truth, every decision and every undo, one record per line) and review_decisions.json (derived: {"generated": ts, "decisions": {key: latest record}}).

Record shape: {key, dir, pid, sheet_row, ref_col, kind, decision, suggested_value, note, reviewer, ts, undecided, basis}. `reviewer` is a person's initials (initials()) or a machine reviewer. `basis` (review_data.basis) names the backend cells the call was made against. A record that went through the ledger (review_app/ledger.py) also carries id, scope, batch, snapshot and origin. An undo appends a record with `undecided: true`; nothing is ever deleted from the log. A line that `covers` other staged records (a status line and the `Status [ref]` record folded into it) writes one more record per covered key, same call, with `via` = the line's key. A `suggest` that took a validity concern's candidate value instead of the proposal (request field `rival` = the concern's key) carries `rival`.

Every name this module has always exported is still here (decide, record_items, append_records, overlay, sync_backend, rival_of, resolves, initials, dir_paths, read_log, _write, _LOCK, Invalid, SYNC_REVIEWER, MACHINE_REVIEWERS and the rest), whether it is imported as `store` or as `review_app.store`. The writes look their helpers up on this module, so a test can replace `store.atomic_write`. Nothing here touches the sheet, the routes repo or staged_*.json.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
import review_app  # noqa: E402,F401  (puts ../gem-review-app on sys.path)
from review_core.store import bind  # noqa: E402
from trackers.pipelines.config import CONFIG  # noqa: E402

bind(CONFIG, ROOT, into=sys.modules[__name__])
