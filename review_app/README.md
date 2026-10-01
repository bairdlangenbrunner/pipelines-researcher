# review_app

Review app for staged pipeline research (plan: `docs/plans/2026-09-30_review-app.md`).

**After milestone 6: data builder + server/UI with line decisions (accept / hold / reject /
suggest, undo), item calls, bulk with confirm, self-resolving concerns, session summary and
backend refresh; consumers `build_ref_workbook.py --decisions`, `apply_route_candidates.py
--decisions`, `staged_summary.py` decided counts and `update_seed.py`. `push.py` (phase 1b) does
not exist yet.**

**The Google version (phase 2) is built and its Google objects exist, but it is NOT deployed yet**
(section "Google version" below): the data folder, the store spreadsheet and the Apps Script
project were created 2026-09-30 and the review-app gas batch was published once; the web app
deployment (a browser step only Baird can do) and the identity check are still to do. Once it is
deployed it is the review surface; the loopback server below stays as the build / debug tool.

```bash
python review_app/server.py                                         # the review-app batch (below), gas
python review_app/server.py --country Russia --commodity gas        # one scope; builds the dataset, opens the browser
python review_app/server.py --country Russia --country "United States" --commodity gas   # several countries, one queue
python review_app/server.py --no-build --data work/review_r7.json   # serve an existing dataset
```

**The review-app batch** (`batches/review-app/manifest.json`, managed by `review_app/scopes.py`)
says which researched countries the app shows when started without `--country`. It holds one
yes / no / later answer per country+commodity and nothing else: the staged data stays in its
staging dirs (they are the pending-state store, and every decision key names its dir). An included
country's dirs are discovered fresh on every build, so a new batch for it comes in on the next
start or `/api/refresh`. A country with nothing left to decide (every line decided by a person or
already in the backend, every asked item called) is left out of that build and listed beside the
country filter as "all decided, hidden"; `--include-done` keeps it, and a new batch brings it
back. The researcher asks at each delivery (`docs/workflows.md`, "Review-app batch").

```bash
python review_app/scopes.py list                                     # every researched scope + its answer
python review_app/scopes.py pending                                  # researched, never answered or "later"
python review_app/scopes.py check --country Egypt --commodity gas    # exit 3 = ask
python review_app/scopes.py set --country Egypt --commodity gas yes  # or no / later
```

Binds `127.0.0.1:8766` only (8765 is the LNG carriers app). Flags: `--country` (repeatable or a
comma list; omit for the review-app batch), `--commodity` (required with `--country`, else gas),
`--include-done`, `--dirs`, `--exclude-pids`, `--data`, `--reviewer` (default
`git config user.name`; recorded as initials, below), `--host` (loopback only), `--port`, `--no-open`, `--no-build`. The
snapshot flag is `review_data.py --snapshot`, not a server flag.
Routes: `GET /`, `/api/data`, `/api/decisions?dir=`, `/geo/<path>`, `POST /api/decide`, `/api/item`,
`/api/refresh`, `/api/whoami` (`{reviewer, caps}`; `caps` drive which controls the
UI shows). Keyboard: `j/k` next/previous line, `J/K` next/previous pipeline, `o` open the line's
first ref, `d` toggle details, `/` search, `?` help. Filters combine; `in_backend` lines are
hidden by default. With several `--country` values the filter bar leads with one checkbox per
country (multi-select; none ticked = all); it keys on the BATCH country of the staging dir a card
came from (`scope_countries`), not `CountriesOrAreas`, and rides in the URL as `cty=Russia|United States`.
Scope-level items get one card per country. Keys are unchanged, so decisions carry over. A line is drawn grayed once it is settled — accepted, rejected or suggested by a
person, or `in_backend` — while hold stays bright (still open); an item grays once it carries a
reviewed call (same convention as the LNG carriers app). Tier colours are the workbook's (`docs/reference/workbook_conventions.md`)
and appear on the tier chip and the line's left border.

**Line cards** show one now / proposed table per line: a row per paired value column (`value_cols`
with anything on either side), then the `[ref]` row. Each row carries a tag for what the line does
to that cell: `fill` (empty cell → value / refs; an empty cell is drawn empty), `change`, `clear`, `add` / `replace` / `drop` (refs),
`re-verified`, or none when it is unchanged (the value is repeated, muted). New values and added
refs are green, changed values amber, contested current values orange; each added URL gets one
verification mark (`✓`, or the failed checks). Class, default, language, batch dir, notes and
verification notes sit under "notes & record". Clicking the pipeline name (or the **Everything**
tab) shows every line on the pipeline, filters ignored, then its items, on one page.

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

**One ledger** (Baird 2026-10-01): every decision, whichever door it comes through, is appended
to the `log` tab of the store spreadsheet (`google.json: store_sheet_id`) FIRST and to the staging
dir's sidecars second — `review_app/ledger.py`, the same 19-column row Code.gs writes. Doors:
the served Google page (Code.gs, origin `gas`), the loopback server (`store.decide(…, sink=Ledger.sink)`,
origin `local`), a Claude chat (`python review_app/ledger.py decide --key K --decision accept`, origin
`chat`), `push.py`'s `push` records, a refresh's `backend sync` records and a publish's carry-forwards.
The store is the single source of truth; the sidecars are its committed mirror (`pull.py` fills in
what the Google page wrote); the workbook, the push plan and the published dataset all read one
history. A store that cannot be written **refuses the decision** (502 on the server, exit 2 on the
CLI; nothing recorded anywhere) — there is no offline mode. `server.py --no-store` (dev/tests only)
writes the sidecars alone and says so on every start. Appending to that tab is a standing
authorization (CLAUDE.md → Hard requirements); it never touches the backend sheet, which only
`push.py` writes, asked per run. The store keeps the reviewer's address (default: the
`gws-gem-write` account's, `--reviewer-email` to override); the sidecars keep initials.

Every staging dir gets two sidecars, committed with the batch:

- `review_log.jsonl` is the mirror: append-only, one record per decision
  `{key, dir, pid, sheet_row, ref_col, kind, decision, suggested_value, note, reviewer, ts, undecided, basis}`
  (plus `via` on a record written through the line that covers it, below; plus the ledger's
  `id, scope, batch, snapshot, origin`). `basis` = `review_data.basis(line)`, the hash of the backend
  cells the call was made against, which `publish.py` (drift) and `push.py` (stale) compare.
  `decision` is `accept|hold|reject|suggest`; `ts` is ISO-8601 with timezone, stamped by the
  server along with `reviewer` (the client cannot set either). **A person is recorded by first +
  last initials, never a full name** (Baird 2026-10-01): `store.initials()` turns
  "Baird Langenbrunner" and `baird.langenbrunner@globalenergymonitor.org` into `BL` on every
  write (`decide`, `record_items`, the server's reviewer, `pull.py`); machine reviewers
  (`backend sync`, `push`) stay as they are.
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
the progress bar, the Decision filter's `suggest` option), is skipped by every bulk action, and
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
view, accept all high for this pipeline. They skip lines locked by an open concern and lines a
person already decided, and send one `POST /api/decide`. The server is all-or-nothing: if any
line is locked or invalid the request is refused (409/400) and nothing is written.

## Session summary

**Switched off for now (might add later):** set `SHOW_SUMMARY = true` in `web/app.js` to bring back the button and the `S` key.

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

## Google version (phase 2)

An Apps Script web app, open to globalenergymonitor.org logins only, running as Baird
(`gas/appsscript.json`: `access: DOMAIN`, `executeAs: USER_DEPLOYING`). Same front end
(`web/app.js` with the `web/gas.js` store adapter), same decision records, three Google objects:

| Object | What it is | Who writes it |
|---|---|---|
| Drive **data folder** | the published dataset: `scopes.json` + per scope and version `<id>.<ver>.part<k>.json.gz`, `<id>.<ver>.index.json`, optional `<id>.<ver>.geo.json.gz` | `publish.py --upload --yes` only (`gws-gem-write`; ask Baird before every run) |
| **Store spreadsheet**, tab `log` | THE decision store while reviewing: append-only, one row per decision record; column `json` is the record, the other columns are for reading and filtering in Sheets | `gas/Code.gs` only, under a script lock. Reviewers need no access to it |
| Apps Script project | `gas/Code.gs` + `gas/appsscript.json` + the generated `gas/index.html` and `gas/Config.gs` | `gas_push.py --yes` (ask Baird before every run), then a new deployment version in the browser |

Where they are (IDs in `review_app/google.json`; created 2026-09-30):

- Shared-drive folder "Pipeline reviewer app" (`1h2994w9SD1DwKCEiOXE3LN1BQdI8btYR`, in the shared
  drive that holds the backend sheet) holds the data folder `data`
  (`1A6G4O0FsiYQypsrQe214TPOqMF2ZNckp`) and the store spreadsheet "pipelines reviewer decision
  store" (`1uz0v_FoZ7zU8tlQ1yNbWua1jWrwhAu8P6BeZZm5S82g`). **Every member of that shared drive can
  open and edit both by hand.** Append-only is what the script does, not something Drive enforces:
  nobody edits, sorts or deletes rows of the `log` tab (the app counts on row order), and the tab
  is not protected (open question for Baird).
- The Apps Script project "pipelines reviewer"
  (`1QQmthEqS7HN4FiPyh7y3jjNHNfTku51XxKwdvagpVZlWIeqNWHW68fw6`) is in **Baird's My Drive**, not
  the shared folder: a Drive import ignores a shared-drive parent for a script project. It is left
  there on purpose until Baird rules: in the shared drive every member could edit code that runs
  as Baird, and Baird's role there (content manager) cannot move a file back out.

`Code.gs` opens only the store spreadsheet and the data folder (their IDs come from the generated
`Config.gs`, which `bundle.py` writes from `google.json`; a Script Property `STORE_SHEET_ID` /
`DATA_FOLDER_ID` overrides it), plus the backend tracker sheet **read-only** for the live drift
check (`google.json` `backend`: sheet id, tab gids, header rows); never `UrlFetchApp`; scopes
are `spreadsheets`, `drive.readonly`, `userinfo.email`. The page shows `caps = {decide: true,
refresh: false, push: false}`: no refresh-backend and no push there.

```bash
python review_app/publish.py                  # build the review-app batch + write the local mirror work/review_publish/
python review_app/publish.py --upload         # + list what Drive would change (writes nothing)
python review_app/publish.py --upload --yes   # do it: ASK BAIRD FIRST, every run
python review_app/pull.py [--dry-run]         # store spreadsheet -> each staging dir's review_log.jsonl (read-only on Google)
python review_app/ledger.py status            # store configured? writer address? row count
**Live drift check (2026-10-01).** The dataset is still a snapshot (only `publish.py` rebuilds it),
but the page now asks `Code.gs liveCheck` on load, and from the "check backend" button, whether the
backend cells each line was judged against have changed since. `publish.py` writes the watch list
(`make_watch`: per tab, ProjectID, row and the value / ref / Status / RouteAccuracy cells as the line
shows them) into the scope's index file (`w`); `liveCheck` reads those tabs with `getDisplayValues`,
matches rows by ProjectID (a row inserted above only moves a row, it is not a change) and returns
the differing cells. Matching lines get a "sheet changed live" chip and join the "sheet changed since
decided" filter. It flags; it never rebuilds a proposal or touches a decision. The executing user
(Baird) must be able to read the backend sheet. A scope published before this change has no watch
list, so the check finds nothing until it is republished.

python review_app/ledger.py decide --key KEY --decision accept|hold|reject|suggest [--note N]   # a chat's decision, same door
python review_app/push.py [--include-stale]   # the ONLY route to the backend sheet; stale lines skipped by default
python review_app/bundle.py [--check]         # web/ + google.json -> gas/index.html + gas/Config.gs (generated, gitignored)
python review_app/gas_push.py                 # list how the Apps Script project differs from gas/ (writes nothing)
python review_app/gas_push.py --yes           # replace the project's files: ASK BAIRD FIRST, every run; then deploy a new version
node review_app/gas_dev/dev_server.js         # local stand-in: http://127.0.0.1:8767/?user=you@globalenergymonitor.org
```

**The record.** A decision made on the Google page is one appended row: the same record
`review_log.jsonl` holds, plus `id`, `scope`, `batch` (one id per request, so a bulk action is one
batch), `snapshot` and `basis` (below) and `origin: "gas"`. `reviewer` is the Google login and `ts`
the server clock; the client can set neither. Latest row per key wins; undo appends. `pull.py`
copies rows it has not seen (by `id`) into the staging dir each record names and regenerates
`review_decisions.json`. **The pulled logs hold initials, not the address** (Baird 2026-10-01, replacing the
2026-09-30 `b*@domain` alias): `baird.langenbrunner@globalenergymonitor.org` is written as `BL`
(`store.initials`: the local part split on `. _ - +`, first letter of the first and last parts;
a one-part address gives one letter), because the staging dirs are committed. The store
spreadsheet keeps the full address (Code.gs needs it for identity and the clash check) and is the
authority on who decided what; two reviewers with the same initials share them in git, and the
pull prints `SHARED INITIALS` when the store holds such a pair. `publish.py` puts the full address back into the dataset it
sends to the private Drive folder, so the page and its "decided by" filter show one name per
person. So the consumers (`--decisions`, `update_seed.py`, `staged_summary.py`)
are unchanged and git holds the second copy of the history. **Pull before building a workbook from
decisions.** The loopback server, a chat (`ledger.py decide`) and the Google page all append to the
same `log` tab (→ Decisions, "One ledger"), so a decision made anywhere is in the store the moment
it is made; a pull only brings home what the Google page wrote.

**Two reviewers at once.** Every write runs under the script lock and carries the last store row
the page has seen. If someone else's record for the same key landed after that row, the write is
refused, nothing is saved, the page shows their call and a banner naming them; pressing again
overrules it (both rows stay in the log). A bulk request is all-or-nothing. Open pages poll every
45 s and show other reviewers' calls with a toast; "more filters > decided by" filters on reviewer.

**The backend moving under a decision.** `publish.py` stamps each line with `basis`, a short hash
of the backend cells the proposal was judged against (current value, current refs, current status,
current route accuracy), and the script copies `basis` + `snapshot` into every record. At the next
publish, a line whose latest person record has a different basis gets `drift` (chip on the card,
"sheet changed since decided" filter, count in the publish report). **A drifted decision STANDS**
(Baird 2026-09-30): it stays decided, counts as decided, and reaches the workbook like any other;
the flag is the prompt to look again, and looking again is the reviewer's choice. Nothing is
reopened or reverted by the app.

**A renumbered row.** The decision key holds the sheet row, so a row inserted above a pipeline
would leave its decisions matching nothing. At every publish, `publish.carry_forward` re-keys a
person's orphaned decision when exactly one line or item of the new build has the same staging
dir, ProjectID and column, nothing is recorded under that key yet, and no other orphan wants it:
a copy of the record is appended to the log under the new key (`rekeyed_from` = the old key;
reviewer, time, basis and snapshot kept; the old record is never rewritten) and the report counts
it as "carried forward". Whatever does not meet that bar is reported as an **orphan** and left
alone, to be re-decided by hand. Known limits: a ProjectID with several rows (segments) is
ambiguous by nature, and a decision made on a page still showing the previous version, under the
old key, is carried at the NEXT publish, not before.

**Publish, versions, limits.** Each publish writes a new version of the scope's files, then
rewrites `scopes.json` (the switch), then trashes that scope's versions older than the previous
one. The script caches `scopes.json` for 60 s, so the app serves a publish within a minute, an
open page reloads itself in place on its next poll, and two publishes of one scope inside a minute
are to be avoided. A publish runs `pull.py` first and stores the cursor (last store row read) in
the scope: the published dataset already holds every decision up to it and the app lays only later
rows over it. Every write reads the store rows after that cursor, so republish every few thousand
decisions to keep writes fast.

**Deploying.** Done 2026-09-30: the data folder, the store spreadsheet (its `log` tab set up as
the script would: plain-text cells, Calibri 10, bold frozen header), the Apps Script project
(created by a Drive import of `bundle.py --project`'s JSON, no clasp and no paste), `google.json`
filled but for `web_app_url`, and the first `publish.py --upload --yes` (review-app gas batch).
**Deployed 2026-10-01** by Baird in the browser (Deploy > New deployment > Web app, Execute as
"Me", access "Anyone within Global Energy Monitor"; the three permissions approved); the web app
URL is `google.json: web_app_url`. It is domain-restricted: an anonymous GET 302s to the GEM login.
Reviewers need only a globalenergymonitor.org login and that URL — no repo, no `gws`, no access to
the store spreadsheet. A code change needs `gas_push.py --yes` AND Deploy > Manage deployments >
edit > Version: New version, or the page keeps serving the old build. **Milestone 0 next:** open `<web app
url>?spike=1` as Baird and have a colleague open it too: it prints what `Session.getActiveUser()`
returns for each (the script refuses every call with 403 when that is empty) and times a 1 MB
round trip. Later code changes: `gas_push.py --yes` replaces the project's source (untested
against a real project beyond the plan; the first real push should be watched), and the web app
keeps serving its deployed version until Baird picks Deploy > Manage deployments > edit >
Version: New version. clasp (Google's command-line uploader for Apps Script) is not needed.

**Testing without Google.** `gas_dev/` runs the real `Code.gs` under fakes (`stubs.js`: the
spreadsheet, the Drive folder, the cache, the lock, the session) and serves the real bundle;
`?user=<email>` stands in for the login, `GET /store` shows the fake log, and nothing there
reaches Google or the staging dirs. `tests/test_review_gas.py` holds the script to the Python
store (same requests, same records), `tests/test_review_gas_e2e.py` drives two reviewers in a
headless browser, `tests/test_review_publish.py` / `test_review_pull.py` / `test_review_bundle.py` /
`test_review_gas_push.py` cover the rest. The script and browser tests skip without node / playwright.

## Suggested improvements (later)

- The `independent` flag (second independent publisher) was dropped from the line card
  (2026-09-30); if it is wanted again, a filter or a per-pipeline tally fits better than a chip on
  every line.
- The same Status proposal staged in two batch dirs shows as two identical-looking cards now that
  the batch name is off the header; fold them like `covers`, or mark the duplicate.
- A contested note (orange) still shows on a line after its concern has a call; it could drop once
  the concern is decided.

