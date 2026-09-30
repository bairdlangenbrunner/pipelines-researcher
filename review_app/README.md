# review_app

Review app for staged pipeline research (plan: `docs/plans/2026-09-30_review-app.md`).

**After milestone 2: data builder + read-only server/UI.** No decision log yet (milestone 3):
`a/h/r/s/u` show a toast, `POST /api/decide` returns 501.

```bash
python review_app/server.py --country Russia --commodity gas        # builds the dataset, opens the browser
python review_app/server.py --no-build --data work/review_r7.json   # serve an existing dataset
```

Binds `127.0.0.1:8766` only (8765 is the LNG carriers app). `--dirs`, `--exclude-pids`,
`--snapshot`, `--reviewer` (default `git config user.name`), `--port`, `--no-open`.
Routes: `GET /`, `/api/data`, `/api/whoami` (`{reviewer, caps}`; `caps` drive which controls the
UI shows). Keyboard: `j/k` next/previous line, `J/K` next/previous pipeline, `o` open the line's
first ref, `d` toggle details, `/` search, `?` help. Filters combine; `in_backend` lines are
hidden by default. Tier colours are the workbook's (`docs/reference/workbook_conventions.md`).

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
