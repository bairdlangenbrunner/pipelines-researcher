# review_app

Review app for staged pipeline research (plan: `docs/plans/2026-09-30_review-app.md`).

**After milestone 4: data builder + server/UI with line decisions, item calls, bulk, session
summary, and backend refresh.** `s` (suggest) in the UI is not wired yet.

```bash
python review_app/server.py --country Russia --commodity gas        # builds the dataset, opens the browser
python review_app/server.py --no-build --data work/review_r7.json   # serve an existing dataset
```

Binds `127.0.0.1:8766` only (8765 is the LNG carriers app). `--dirs`, `--exclude-pids`,
`--snapshot`, `--reviewer` (default `git config user.name`), `--port`, `--no-open`.
Routes: `GET /`, `/api/data`, `/api/decisions?dir=`, `POST /api/decide`, `/api/whoami` (`{reviewer, caps}`; `caps` drive which controls the
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
  `overlay_decisions` (via `store.overlay`) stamps each line with the sidecar decision.
- Snapshot default is the NEWEST `data/<commodity>` snapshot (`--snapshot` overrides).
  `scope.snapshot` is the one used, `scope.recorded_snapshot` the one the staging dirs name.

## Decisions

Every staging dir gets two sidecars, committed with the batch:

- `review_log.jsonl` is the truth: append-only, one record per decision
  `{key, dir, pid, sheet_row, ref_col, kind, decision, suggested_value, note, reviewer, ts, undecided}`.
  `decision` is `accept|hold|reject|suggest`; `ts` is ISO-8601 with timezone, stamped by the
  server along with `reviewer` (the client cannot set either).
- `review_decisions.json` is derived: `{generated, decisions: {key: latest record}}`, rewritten
  atomically after each append. If that write fails the log is rolled back byte for byte.

Latest record wins. **Undo** (`u`, or clicking the pressed button) appends a record with
`undecided: true`; nothing is deleted. A line is reviewed only when its latest record is by a
person (not `backend sync` / `push`) and not undecided. `suggest` needs a `suggested_value` or a
note and applies to lines only; item keys are refused (use `/api/item`). `/api/data` re-overlays the
sidecars on every request, so rebuilt datasets and reloads show decisions.

**Contested lock.** A line whose column (`column`, `value_cols`, or `Status` for status lines) is
named in the `contested` map of an open concern item (no call yet) shows "held: concern open";
accept is refused with 409 server-side. Hold and reject stay allowed.
Any call on the concern (including `needs research`) releases the lock, and the UI unlocks that
card's lines in place. No Name/OtherEnglishNames linked-pair prompt: no such pairs exist in the
Russia gas data.

## Items and calls

The card's **Items** tab (`i` toggles Lines/Items) gives every item a call selector and a note;
a change saves immediately (`POST /api/item`, same sidecars, same latest-wins and undo rules; "no
call" undoes). Call vocabulary per kind: `concern` takes `confirmed | dismissed | needs_research`
(confirmed: it stands; dismissed: closed; needs research: goes to an Update worklist); every other
kind takes `noted | todo | dismissed`. A wrong call is a 400. Item records are
`{key, dir, pid, kind, call, note, reviewer, ts, undecided}`; items in the dataset carry
`call`, `call_note`, `reviewed`, `decided_by`, `decided_at`.

## Bulk

Three header-bar buttons (and `A` for the first) act on the CURRENT filtered queue and always
confirm with the exact count and a per-kind breakdown: accept all defaults in view, hold all in
view, accept all high in this pipeline. They skip lines locked by an open concern and lines a
person already decided, and send one `POST /api/decide`. The server is all-or-nothing: if any
line is locked or invalid the request is refused (409/400) and nothing is written.

## Session summary

`S` or the header "summary" button: decided / open / in-backend counts by kind, tier and staging
dir, item calls, and what this reviewer saved in this page session, with "copy summary as
markdown".

## Refresh backend

"refresh backend" (header; confirm first, ~1 min) calls `POST /api/refresh`: runs the pull
(`scripts/refresh_csvs.sh`, read-only against the sheet, 600 s timeout), rebuilds the dataset with
the stored build args, reloads, then runs a `backend sync` pass and returns
`{snapshot, lines, synced}`. Every line now `in_backend` with no live record gets a `backend sync`
accept record ("already in backend after refresh <snapshot>"); lines a person decided or that are
already synced are skipped, so it is idempotent. Such records are machine records, never
`reviewed`. Servers started with `--no-build` answer 409 and the button is disabled
(`caps.refresh` false).

```bash
python review_app/review_data.py --country Russia --commodity gas \
    [--dirs batches/russia-gas/staging/deepsweep-r7-central-south ...] \
    [--exclude-pids P1,P2] [--snapshot data/GGIT_gas_snapshot_<stamp>.csv] \
    [--out work/review_data.json]
python -m pytest tests/ -q
```

Without `--dirs` it discovers every staging dir for the scope, handoff packets included.
The summary goes to stderr.
