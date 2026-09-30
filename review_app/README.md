# review_app

Review app for staged pipeline research (plan: `docs/plans/2026-09-30_review-app.md`).

**After milestone 1 this is only the data builder.** No server, no UI, no decision log yet.

- `review_data.py` turns one scope's pending staging dirs into `work/review_data.json`:
  one card per pipeline, with `lines` (ref / fill / status / oo / route / new_row: one
  decision each) and `items` (concern / wikidiff / routeqc / route_suggestion / monitor /
  flag / escalation / unresolved / confirmed / other: a call plus a note). Records fitting
  no kind become `other` and are counted in the summary.
- Reads only `staged_resolutions.json`, `staged_new.json`, `qc_flags.json`,
  `escalations.json` per dir; never `staged_actions.json` or `*.prior.json`.
  Read-only over `batches/` and `data/`.
- `default` is `accept` iff tier is `high`, else `hold`; items have no default.
  `overlay_decisions` is the milestone-3 hook and is a no-op for now.

```bash
python review_app/review_data.py --country Russia --commodity gas \
    [--dirs batches/russia-gas/staging/deepsweep-r7-central-south ...] \
    [--exclude-pids P1,P2] [--snapshot data/GGIT_gas_snapshot_<stamp>.csv] \
    [--out work/review_data.json]
python -m pytest tests/ -q
```

Without `--dirs` it discovers every staging dir for the scope, handoff packets included.
The summary goes to stderr.
