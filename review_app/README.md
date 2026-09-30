# review_app

Review app for staged pipeline research (plan: `docs/plans/2026-09-30_review-app.md`).

**After milestone 6: data builder + server/UI with line decisions (accept / hold / reject /
suggest, undo), item calls, bulk with confirm, self-resolving concerns, session summary and
backend refresh; consumers `build_ref_workbook.py --decisions`, `apply_route_candidates.py
--decisions`, `staged_summary.py` decided counts and `update_seed.py`. `push.py` (phase 1b) does
not exist yet.**

```bash
python review_app/server.py --country Russia --commodity gas        # builds the dataset, opens the browser
python review_app/server.py --no-build --data work/review_r7.json   # serve an existing dataset
```

Binds `127.0.0.1:8766` only (8765 is the LNG carriers app). Flags: `--country`, `--commodity`
(both required unless `--no-build`), `--dirs`, `--exclude-pids`, `--data`, `--reviewer` (default
`git config user.name`), `--host` (loopback only), `--port`, `--no-open`, `--no-build`. The
snapshot flag is `review_data.py --snapshot`, not a server flag.
Routes: `GET /`, `/api/data`, `/api/decisions?dir=`, `/geo/<path>`, `POST /api/decide`, `/api/item`,
`/api/refresh`, `/api/whoami` (`{reviewer, caps}`; `caps` drive which controls the
UI shows). Keyboard: `j/k` next/previous line, `J/K` next/previous pipeline, `o` open the line's
first ref, `d` toggle details, `/` search, `?` help. Filters combine; `in_backend` lines are
hidden by default. A line is drawn grayed once it is settled — accepted, rejected or suggested by a
person, or `in_backend` — while hold stays bright (still open); an item grays once it carries a
reviewed call (same convention as the LNG carriers app). Tier colours are the workbook's (`docs/reference/workbook_conventions.md`).

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
  `{key, dir, pid, sheet_row, ref_col, kind, decision, suggested_value, note, reviewer, ts, undecided}`
  (plus `via` on a record written through the line that covers it, below).
  `decision` is `accept|hold|reject|suggest`; `ts` is ISO-8601 with timezone, stamped by the
  server along with `reviewer` (the client cannot set either).
- `review_decisions.json` is derived: `{generated, decisions: {key: latest record}}`, rewritten
  atomically after each append. If that write fails the log is rolled back byte for byte.

Latest record wins. **Undo** (`u`, or clicking the pressed button) appends a record with
`undecided: true`; nothing is deleted. A line is reviewed only when its latest record is by a
person (not `backend sync` / `push`) and not undecided. `suggest` needs a `suggested_value` or a
note and applies to lines only; item keys are refused (use `/api/item`). `/api/data` re-overlays the
sidecars on every request, so rebuilt datasets and reloads show decisions.

**One card per status call.** A status-review line and the refs-leg record that stages the SAME
Status value onto `Status [ref]` are two staged records for one decision, so the builder folds the
ref record into the status line: no card of its own, its refs and verifications join the status
card, and the line carries `covers` (one entry per folded record: key, dir, kind, classes, notes).
Deciding the status line (accept / hold / reject / suggest, undo, backend sync) writes the same
record to every covered key in the same transaction, with `via` = the status line's key, so each
staged record still has its own decision and the consumers below need no special case
(`update_seed.py` skips `via` records: one suggestion, one unit). Folded only when the partner
agrees: same row, `Status [ref]`, a Status value equal to the proposed status. A ref record that
backs the CURRENT status while the status leg proposes a change is contrary evidence and stays its
own card. A call made before a record was folded in is never back-filled: `/api/data` reports the
line's `uncovered` keys, the card stays bright and says to press the same call again.

**Contested lock.** A line whose column (`column`, `value_cols`, or `Status` for status lines) is
named in the `contested` map of an open concern item (no call yet) shows "held: concern open";
accept is refused with 409 server-side. Hold and reject stay allowed.
Any call on the concern (including `needs research`) releases the lock, and the UI unlocks that
card's lines in place.

**Self-resolving concerns.** When an open concern's `contested[col]` equals the line's proposed
value on that column, the line IS the resolution: that column does not lock the line (the card shows
"resolves concern", and the contested chip reads "concern agrees with this value"), and accepting
it records a `dismissed` call on the concern (note "resolved by accepted <col> fill", reviewer =
the person) in the same write, so the concern's other contested columns unlock too. Equality is on
trimmed strings against `proposed_values[col]`; an empty contested value never matches (it means
"unsourced", not a proposed blank). A line is still locked by any contested column it touches that
is not self-resolved (per concern). `/api/decide` returns the item records after the line records
(item records carry `call`). Only a person's accept does it: hold / reject / suggest, undo and
machine reviewers never dismiss, and a concern that already has a call is left alone. Undoing the
line accept does NOT re-open the concern; undo the item call by hand (Items tab, "no call").
Within one bulk request the lock is evaluated against the dataset before the request, so a line
that depends on a dismissal made by another line of the same bulk is still refused. No Name/OtherEnglishNames linked-pair prompt: no such pairs exist in the
Russia gas data.

## Suggest

`s` (or the "suggest (s)" button) opens an inline form on the current line: **Suggested value**
(prefilled with the proposed value for fill / owners-tab lines, the proposed status for status
lines, the proposed `[ref]` cell text for ref lines; empty for routes) and **Note**. Enter or
"Save suggestion" posts `decision: suggest` with `suggested_value` + `note` to `/api/decide`;
Esc cancels. Either field may be empty but not both (400). The line then reads
"suggested: <value> by <reviewer> <time>", counts as decided (a person's call: `store.reviewed`,
the progress bar, the Decision filter's `suggest` chip), is skipped by every bulk action, and
shows in the session summary ("decided lines by call", "this session"). Clicking the pressed
button or `u` undoes it. Re-opening the form on a suggested line prefills the earlier suggestion.
Paste surfaces never carry a suggestion; `scripts/update_seed.py` routes it to an Update worklist.

## Consumers

- `python scripts/build_ref_workbook.py --staging DIR --output OUT.xlsx --decisions` (handoff packet
  or sweep workbook): the paste surfaces carry only lines a person accepted; see
  `docs/sops/qc.md` (handoff contract). It also reads the decision files of every carried source dir.
- `python scripts/update_seed.py --country C --commodity gas [--dirs ...] [--out PATH]` reads each
  staging dir's `review_decisions.json` and writes a §5 Update worklist seed
  (`batches/<scope>/staging/update-seed-<YYYYMMDD>/staged_updates_seed.json`): an update unit per
  `suggest` line (pid, sheet_row, column, ref_col, proposed_value, suggested_value, note,
  reviewer, source dir) and a research unit per concern called `confirmed` or `needs_research`
  (pid, concern_type, contested columns, text, note). Shape = `staged_updates.json` `rows` plus a
  flat `units` list; `old` / `tier` / `refs` are left empty. No decision files: empty seed, exit 0.
- `python scripts/staged_summary.py` prints `decided=12a/3h/1r/0s of 40` per dir (and
  `batches/INDEX.md` a `decided` column via `--index`); a dir with no decision file shows `—`.
  Counts are over that dir's LINE records only (resolution lines + discovery candidates), by
  the person's latest call; a line carried into a handoff packet is decided in its primary dir,
  so the packet dir shows it undecided.
- `python scripts/apply_route_candidates.py --staging DIR ... --decisions` takes its PID list
  from the accepted `route` lines instead of `--pids` (both together, or none accepted, is
  refused). Plan / review / `--apply` are unchanged.

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
