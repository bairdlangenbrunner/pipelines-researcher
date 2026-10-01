# Review app for pipelines — audit of the LNG app + build plan (written 2026-09-30)

An interactive accept / hold / reject surface for the staged pipelines work, modelled on
`lng-carriers-researcher/review_app/`. Part A audits what that app is and what it taught us.
Part B is the build spec for the pipelines version: a fresh session should be able to build
phase 1 from it without the conversation that produced it.

Status: **plan only — nothing built.** All three rulings passed 2026-09-30 (push from the app;
shared online with other researchers; high tier defaults to accept).

---

## Part A — audit of the LNG carriers review app

### What it is

A loopback-only local web app that replaces the combined xlsx as the place where a batch's
proposals get decided. Python standard library server + vanilla JS front end, no build step, no
dependencies, no network calls of its own (refs open in the reviewer's browser). It lives at
`lng-carriers-researcher/review_app/` and is documented in `review_app/README.md` (238 lines)
and the spec `docs/plans/2026-09-18_review-app.md`.

Size, as of 2026-09-30:

| File | Lines | Role |
|---|---|---|
| `review_data.py` | 635 | builds `work/review_data.json` (gitignored) from batch dirs |
| `store.py` | 440 | decision persistence: log, csv rewrite, overlay, `reviewed`, items, sync |
| `server.py` | 299 | `http.server` on `127.0.0.1`; the phase 1 `Store` |
| `push.py` | 284 | clicked accepts → live sheet, plan/token/confirm/verify |
| `suggestions.py` | 216 | `suggest` records → a `fix` batch |
| `living.py` | 445 | mirrors the `processed` column to a Drive "living workbook" |
| `web/app.js` / `style.css` / `index.html` | 1,497 / 224 / 83 | the UI |
| tests (`tests/test_review_*.py`, `test_living.py`, `review_fixture.py`) | 1,387 | pytest, fixture batch dirs |

### How it was built (git timeline)

- **2026-09-18, one day, six milestones**: `07d01ff` review dataset → `16d3fca` server + read-only
  UI → `dec04d1` decisions, undo, linked pairs → `dacf80a` bulk, Items tab, session summary →
  `db0baa2` suggest → `1ad0aa5` docs. Baird then used it on 528 real holds; that was the
  acceptance test.
- **2026-09-21**: push accepted (`push.py`), sync backend, living workbook, filter chips.
- **2026-09-22**: hide lines already in the backend; computed confidence.
- **2026-09-23/24**: re-key from column-A `row_id` to a uuid (row ids drifted between pulls);
  "directed writes" (Apply SOP §2d) for one-off writes Baird asks for by cell.
- **Phase 2 (Apps Script, shared with Rob) was designed twice (09-18, revised 09-21) and a
  handoff written (`docs/plans/2026-09-21_review-app-phase2_handoff.md`) but NEVER built.**
  There is no `review_app/gas/`. The design is reusable: Drive JSON dataset, append-only
  decisions spreadsheet, reviewer email stamped server-side, capability flags hide push/sync.

### The semantics that matter

- **Unit of review = the entity, not the field.** One card per vessel; every proposal on it is a
  line showing current → proposed, refs, note, confidence. Decide in place, one keypress, saved
  immediately, undo by appending a new record (never by deleting one).
- **Decision enum** `accept | hold | reject | suggest`. `suggest` is stored as `reject` in the
  pipeline's csv plus a suggestion record; suggestions are routed through a `fix` batch whose
  build re-runs the value↔ref gate. A reviewer never types a value that gets applied directly.
- **One reviewer's decision settles a proposal**; every decision records who and when.
- **`reviewed` = the latest record by a person.** Machine reviewers (`backend sync`, `§5 regrade`)
  write records too but do not count as review, and an undo record un-reviews.
- **Key** = `<batch_dir>::<id>` — ids collided across batches (36 of them), so the dir is part of
  the key.
- **Linked pairs** (Name ↔ Other names; value ↔ its `[ref]`) prompt to decide together.
- **Two stores per batch dir**: `review_log.jsonl` (append-only truth, committed) and the
  pipeline's own `decisions.csv` (only its `decision` column is rewritten, atomically, rollback on
  failure). Lesson: `decisions.csv` is lossy (80-char truncation) so it is never the display source.
- **Bulk** = "apply to all N filtered", always behind a confirm. Single decisions never confirm.
- **Items tab** = non-cell review objects (conflicts, manual-review entries, duplicate pairs,
  flags) with their own `review_items.jsonl` and a free-text call.
- **Push** writes only *clicked* accepts, never defaults: plan → token → confirm → fresh pull →
  refuse if stale → `values batchUpdate` RAW via `gws-gem-write` → re-pull verify →
  `push_log.jsonl`. Skips new rows, missing rows, `=`-prefixed values, non-blank conflicting
  cells. "Never forge a click": a directed write is attributed as a directed write.
- **Defaults** (`accept` when derivable or green, else `hold`) are a display hint only.
- UI: queue with filters that combine, hash routing, light/dark, keyboard
  `j/k/J/K/a/h/r/s/u/o/d/?`, session summary listing touched batch dirs to commit.

### Lessons carried into Part B

1. Keep the app's decision store separate from files that other scripts rewrite.
2. Key on something stable and include the batch dir; expect the same proposal in several dirs.
3. Show the live sheet row to humans; never make it the key.
4. Push only clicked accepts, from a fresh pull, cell-scoped, verified, logged.
5. Suggest, don't edit — a reviewer's alternative value goes back through research.
6. Build read-only first, decide second, write the backend last and gated.
7. The whole thing is buildable on a cheaper model once the spec is settled.

---

## Part B — the pipelines review app

### Why pipelines needs its own, not a fork with the names changed

| | LNG carriers | Pipelines |
|---|---|---|
| Proposal source | `decisions.csv` + `apply_batch._detect` per batch dir | `staged_resolutions.json` + `staged_new.json` per staging dir (`scripts/staged_store.py` is the reader) |
| Record kinds | one shape: cell proposal | refs, fills, status changes, validity concerns, wiki diffs, route candidates/suggestions, route QC flags, discovery candidates, operators/owners fills |
| Entity | vessel (`row_id` → uuid) | pipeline **ProjectID** (stable; a PID can span several sheet rows) |
| Sheet targets | one tab | tracker tab **and** the ProjectID-keyed "Pipeline operators/owners" tab (GID 1489950650, header at row index 1, `[ref]` precedes values) |
| Existing apply path | `apply_batch.py` → Apps Script patch | **manual paste** from `-actions.xlsx` `<Cmdty>_AllFillsBackend`; the only sheet writer is `apply_route_candidates.py` (route columns only) |
| Decision store today | `decisions.csv` | **none** — "staged not applied / PARTIALLY APPLIED" lives in prose in `CLAUDE.md` and `docs/country_notes/` |
| Scale | ~2k lines per pass | 86 `staged_resolutions.json` / 29,588 records / 142 staging dirs / 24 scopes |
| Confidence | letter grades | rule-4 tiers `high/medium/low` + `contested` (anti-tier) |
| Routes | n/a | geometry goes to a separate repo via §8; never through this app |

### Decisions already made (from CLAUDE.md, in force)

- **The app never writes the live sheet or the routes repo by default.** Phase 1 writes only
  decision sidecars in this repo. The deliverable workbook stays the apply path; the app makes
  the workbook *and* the paste reflect the same decisions.
- **A sheet write, when authorized, is mechanical and pre-verified**: FORMULA pre-read (abort on
  any formula), before/after backup CSV in `notes/` and committed, RAW cell-scoped
  `values.batchUpdate` via `gws-gem-write`, re-read verify. `apply_route_candidates.py`
  (`gws()`, `batch_get()`, `a1()`, `apply_plan()`) is the pattern to generalize, not rewrite.
- **Standing rules hold inside the app**: never cite GEM (the `wiki` link is shown as context,
  never pasted into a `[ref]`), never fabricate URLs, banned hosts stay banned (`url_verifier`
  is already the gate; the app does not re-verify), no orphan `[ref]` cells (a ref line and its
  value are one unit), `Status = N/A` rows never appear.
- **Route three-way sync**: an accepted `ROUTE_CANDIDATE` is an input to `apply_route_candidates.py --pids`,
  which writes `RouteType` + `RouteAccuracy` together; the app never writes route columns itself.
- **Subagent models chosen at dispatch time**; the build is well-specified and goes to a cheaper
  model (see "Model guidance").
- Commits lowercase, succinct, no Claude attribution. `work/` stays gitignored.
- **Push from the app is allowed (Baird, 2026-09-30).** CLAUDE.md's "never write the sheet to
  apply a batch" now carries the exception: *a review-app push of clicked accepts is the
  mechanical pre-verified write, authorized per push run, and produces the same cell text the
  workbook would paste.* Every safeguard the rule demands is in §5 below. Phase 1b is unblocked
  once phase 1 exists.
- **Other GEM researchers review too, from their own computers (Baird, 2026-09-30).** So phase 2
  is not optional. Hosting: **Google Apps Script, domain-restricted, execute-as-Baird** — the
  design already written for LNG (`…/2026-09-21_review-app-phase2_handoff.md`), free, GEM login,
  decisions appended server-side. Baird floated GitHub Pages (`bairdlangenbrunner.github.io`);
  rejected for the same reason the LNG plan rejected it: Pages is **public and static** — a
  personal account cannot restrict access, so unreleased tracker values and researcher notes
  would be on the open web, and it has no write path for decisions anyway. If Pages is ever
  wanted for the shell, it still needs an authenticated backend for data and decisions, which is
  Apps Script again. Phase 1 builds the `Store` adapter with capability flags
  (`{refresh, push}`) from day one so phase 2 is a second adapter, not a rewrite.
- **Default decision = `accept` for every `high`-tier line, any kind, including status changes
  (Baird, 2026-09-30).** High tier already means the ref cleared `url_verifier`, names the
  pipeline and states the value, and for a status change means 2+ independent publishers
  (rule 4). `medium`, `low`, untiered, contested, and every item start as `hold`. The default is a
  display hint for bulk confirmation; **only clicked accepts ever push**.

### Facts about the existing data the builder must know

Verified against the repo on 2026-09-30 (survey over all 142 staging dirs).

1. **`staged_resolutions.json`** (86 files, 29,588 records) is the canonical apply target;
   `{meta, resolutions:[…]}`. Records key on `(project_id, sheet_row, ref_col)`; there is no
   `unit_id`, no `old_value`, and **no decision/applied field anywhere** (`_STATUS_PENDING` in
   `staged_store.py` is a verdict filter, not a review state). `staged_actions.json` (10 handoff
   dirs, 11,663 records) is a render-only re-join of the same records with `source_dir` — **never
   build cards from it** or every carried record becomes two cards. `*.prior.json` (58 files) are
   backups — ignore.
2. **Record classes** (`class_in` → `class_out`) and what accepting means:

   | Kind | Selector | Accept = |
   |---|---|---|
   | `ref` | real `[ref]` column, `class_out` ∈ REFS_ADDED, REVERIFIED, DEAD_LINK, REF_BLOCKED, REF_UNSUPPORTED | write the `[ref]` cell text (`build_ref_workbook._ref_cell_text`) |
   | `fill` | `class_in = FILL` | write `values` **and** the `[ref]` together (rule: no orphan) |
   | `status` | `ref_col = __STATUS__`, `class_out` ∈ CHANGE_PROPOSED, STALE | write `values` (Status, ShelvedCancelledType, ShelvedYear, …) + `[ref]`; STALE has no ref by design |
   | `oo` | any of the above with `tab = operators_owners` (1,798 records) | same, on the owners tab by ProjectID |
   | `route` | `ref_col = __ROUTE__`, `class_out = ROUTE_CANDIDATE` (133) | record "approved for §8 apply"; no cell write |
   | `new_row` | `staged_new.json` `class` ∈ new_row (34), matched_existing (1) | record; no cell write in phase 1 (append is a separate ask) |
   | *item* | `__VALIDITY__` concerns (3,752; `contested` on 2,312), `__WIKIDIFF__` (4,333), `__ROUTEQC__` (225), ROUTE_SUGGESTED/PARTIAL (225), `staged_new` monitor (8), `qc_flags.json`, `escalations.json`, and every UNRESOLVED (9,826) / CONFIRMED (537) record | a call + note; never a cell write |

   Counts are tree-wide; the app loads one scope at a time.
3. **A validity concern's `contested` values are never pushed.** They are research judgments
   (existence, duplicate, classification). An accepted concern is routed to a §5 Update
   worklist (the pipelines analogue of LNG's suggestion → fix batch).
4. **Current values are not on the record.** Read them from the snapshot named in
   `meta.scope.csv` (fall back to the newest `data/GGIT_gas_snapshot_*.csv` /
   `GOIT_oil_ngl_snapshot_*.csv`; header row index 2; `keep_default_na=False, na_values=[]`).
   `__STATUS__` records carry `current_status`, `__WIKIDIFF__` carry `sheet_value`. Show the
   snapshot date next to "current".
5. **`sheet_row` drifts and is sometimes a string.** ProjectID is the key; re-resolve the row from
   the snapshot at build time and again at push time (`apply_route_candidates.py` already checks
   the live ProjectID cell against the plan). `SheetRow = CSV index + 4`.
6. **Duplicates across dirs are normal**: 2,550 of 17,620 `(pid, row, ref_col)` keys appear in
   more than one staging dir (carried into a handoff `qc/` dir, superseded runs, v1/v2/v3).
   `staged_store.discover_staging_dirs` + `_dir_mode` already decide which dirs are pending for a
   scope; use them. Show the reviewer one line, keyed to the *source* dir, with a "also in …"
   note; a decision on it applies to every copy (the workbook builder gets the same resolution).
7. **Schema drift the loader must absorb** (or fix first — see milestone 0): `meta.mode` absent on
   52 of 86 files; ~20 shapes of `meta.scope`; `tier` missing on 6 records, `independent` on 4,
   `wiki` on ~600, `link_live` present on only 8,110. **Repaired by milestone 0
   (`scripts/repair_staged_drift.py`, 2026-09-30):** 199 string `sheet_row`s in 11 route-creation
   stores → int; 3 old israel `staged_new` candidates with refs inlined as `values["X [ref]"]`
   → `refs`. The survey's claim of Python-repr `proposed_refs` strings in iran-gas was wrong:
   none exist. Missing tier renders as "untiered" and defaults to `hold`.
8. **Tier colours are the workbook's** (`docs/reference/workbook_conventions.md`): high `C6EFCE`,
   medium `FFEB9C`, low `FFC7CE`, re-verified `DDEBF7`, contested `FCD5A5`, new row `E2EFDA`. Use
   the same hex in the UI so the app and the xlsx read identically.
9. **`ref_pairs.py`** owns which value columns a `[ref]` covers (`value_cols` on the record is its
   output). The app displays the pairing; it does not recompute it.
10. **The sheet writer pattern** is `scripts/apply_route_candidates.py`: `gws sheets spreadsheets
    values batchGet --params valueRenderOption=FORMULA` under `gws-gem`, `values batchUpdate`
    RAW under `gws-gem-write`, column letters from the fresh CSV header, plan JSON + backup CSVs
    in `notes/sheet-write-<date>-<scope>-*.csv`. Tabs: `Gas pipelines`, `Oil/NGL pipelines`,
    `Pipeline operators/owners`.

### Architecture

```
batches/<scope>/staging/<run>/            (existing, committed)
  staged_resolutions.json  staged_new.json  qc_flags.json  escalations.json
  review_log.jsonl            ← NEW, append-only, committed: every decision/undo/item call
  review_decisions.json       ← NEW, derived from the log (latest per key), committed;
                                the file every other script reads
work/review_data.json         ← gitignored dataset for one scope (built by review_data.py)
notes/sheet-write-*.csv       ← push backups (existing convention)
batches/<scope>/staging/<run>/push_log.jsonl  ← NEW, phase 1b

review_app/
  review_data.py   build the dataset for --country/--commodity (uses staged_store)
  store.py         decide(), overlay(), reviewed(), record_items()   (port of LNG store.py)
  server.py        loopback server; phase 1 Store                    (port of LNG server.py)
  update_seed.py   accepted concerns + suggestions → §5 Update worklist   (analogue of suggestions.py)
  push.py          phase 1b only; generalizes apply_route_candidates.py's write path
  web/index.html web/app.js web/style.css                            (port; kinds + tabs differ)
tests/                          ← NEW dir (the repo has none); pytest, fixture staging dirs
```

Port, don't share: `store.py`, `server.py`, the `Store` adapter, routing, theme, keyboard, undo,
bulk, session summary and the Items tab come across from LNG nearly verbatim. `review_data.py`,
the line-kind rendering and `push.py` are pipelines-specific. Hoisting the generic half into
`gem-db-ops` is a later refactor, not a phase 1 job.

### 1. `review_app/review_data.py`

`python review_app/review_data.py --country "Russia" --commodity gas [--dirs …] [--exclude-pids …]`

- Resolves the pending staging dirs via `staged_store.discover_staging_dirs` (same exclusions
  the handoff uses; `--dirs` overrides). Loads each `staged_resolutions.json`, `staged_new.json`,
  `qc_flags.json`, `escalations.json`. Loads the snapshot for current values and the colmap for
  column order.
- Emits `work/review_data.json`:

  ```json
  {"built": "...", "scope": {"country": "Russia", "commodity": "gas", "snapshot": "GGIT_gas_snapshot_20260930.csv"},
   "dirs": ["batches/russia-gas/staging/deepsweep-r7-central-south", ...],
   "pipelines": [{"pid": "P0736", "name": "Blue Stream Gas Pipeline", "segments": [{"sheet_row": 357, "segment": ""}],
                  "country": "...", "status": "operating", "wiki": "...", "lines": [...], "items": [...]}],
   "columns": ["ProjectID", ...]}
  ```
  Each **line**: `key` (`<dir>::<pid>|<sheet_row>|<ref_col or column>`), `kind`, `dir`, `also_in`,
  `sheet_row`, `column`/`ref_col`, `value_cols`, `current` (from snapshot), `current_ref`,
  `proposed_values`, `proposed_refs`, `ref_cell_text` (what would be pasted), `verifications`,
  `tier`, `independent`, `link_live`, `source_language`, `class_in`, `class_out`, `notes`,
  `default` (`accept` iff `tier == high`, else `hold`), `decision` (overlay from the sidecar), `reviewed`, `in_backend` (the snapshot
  already holds this exact value/ref → filtered out by default, as LNG does).
  Status lines add `current_status`, `proposed_status`, `verdict`, `evidence_date`,
  `staleness_rule`, `publishers`. Route lines add `geometry_file`, `length_km`,
  `sheet_length_km`, `length_ratio`, `suggested_route_accuracy`, `qc_passed`.
  Each **item**: `key`, `kind` (`concern | wikidiff | routeqc | route_suggestion | monitor |
  flag | escalation | unresolved | confirmed`), the record's own fields, `contested`, `call`.
- Sorting: pipelines by SheetRow; lines within a card in sheet column order; items after lines.

### 2. `review_app/web/` — the front end

Everything from the LNG UI, with these pipelines changes:

- **Card header**: ProjectID, name, segment(s) with live SheetRow(s), country, current Status,
  `wiki` (labelled "context — never a ref"), tier summary, open/decided counts. A multi-segment
  PID is one card with a segment divider per sheet row.
- **Line rendering by kind**: `ref` shows current `[ref]` → proposed cell text, each URL a link,
  with the verification chips (`ok`, `contains_value`, `name_found`), `independent`, language;
  `fill` shows blank → value + ref together, decided as one; `status` shows
  `current_status → proposed_status`, the verdict, evidence date, staleness rule, and a **yellow
  "single source" chip when publishers < 2** (rule 4: status change stays green only on 2+);
  `oo` carries an "owners tab" chip; `route` shows length vs sheet length, ratio, suggested
  accuracy, QC pass, and a link to the geojson; `new_row` shows the whole candidate row.
- **Contested values** render orange on the *current* value, with the concern inline; the card's
  lines on that column are held until the concern has a call (linked-pair behaviour, like
  Name ↔ Other names in LNG).
- **Filters**: decision state, kind, tier, class_out, dir, column, contested, single-source status,
  owners-tab, `in_backend`. Counts update live.
- **Items tab**: per kind, with the call form (`agree | disagree | defer` + note for concerns and
  route suggestions; `noted | dismissed` for flags/wikidiff/unresolved/confirmed).
- **Suggest** on any line: proposed value pre-filled, editable, note required → recorded as
  `suggest` (stored as `reject` for consumers) and routed by `update_seed.py`.
- Keyboard, hash routing (`#/P0736`), bulk with confirm, undo, session summary (dirs touched,
  "commit these"), light/dark: unchanged.

### 3. `review_app/store.py` and `server.py`

- `decide(records, data, dirs, reviewer)`: validate every record (key exists in the dataset,
  decision in enum, suggest has a note), append to each touched dir's `review_log.jsonl`, then
  regenerate that dir's `review_decisions.json` atomically (rollback the log on failure).
  Record shape: `{key, dir, pid, sheet_row, ref_col, kind, decision, suggested_value, note,
  reviewer, ts, undecided}`.
- `reviewed()` and `MACHINE_REVIEWERS` as in LNG (`backend sync`, and later `push`).
- `record_items()` → `review_items.jsonl` per dir, same pattern.
- `sync_backend`: re-pulls via `scripts/refresh_csvs.sh`, rebuilds the dataset, marks lines whose
  value and ref are now on the sheet as `in_backend`, and writes a `backend sync` record for them.
- Server: same routes as LNG (`/api/data`, `/api/whoami`, `/api/decide`, `/api/item`,
  `/api/refresh`; `/api/push/plan` and `/api/push` only exist when phase 1b is enabled).
  `--country`, `--commodity`, `--reviewer`, `--port 8766` (8765 is the LNG app), `--no-open`, `ensure_loopback`.

### 4. Consumers — where decisions pay off

This is the part LNG did not need, because there the pipeline already read `decisions.csv`.
Here nothing reads a decision yet, so phase 1 adds readers:

- **`build_ref_workbook.py`** gains `--decisions`: `<Cmdty>_AllFillsBackend` (and `Gas_Backend`
  overlays) carry only lines with `decision = accept`; holds keep their tier colour and get a
  `Decision` column on `Decisions` / `RefWorkDetail` / `FillDetail`; rejects and suggests drop
  out of paste surfaces and appear on the evidence workbook with the reason. The paste and the app
  now agree by construction.
- **`staged_summary.py --index`** adds decided / held / rejected counts per dir; `batches/INDEX.md`
  stops needing the prose "staged not applied".
- **`apply_route_candidates.py`** accepts `--decisions` as the source of `--pids`.
- **`update_seed.py`** turns accepted concerns and `suggest` records into a §5 Update worklist
  (`staged_updates.json` seed per `docs/sops/update.md`).
- Country notes: the per-country "staged not applied / PARTIALLY APPLIED" line becomes a pointer
  to the counts; the app's session summary prints the line to paste.

### 5. `review_app/push.py` — phase 1b (approved 2026-09-30)

Generalizes `apply_route_candidates.py`; nothing new in mechanics.

1. **Fresh pull** (`refresh_csvs.sh`), colmap re-derived; every plan cell located by ProjectID on
   the fresh snapshot, `sheet_row` recomputed and compared to the record's (mismatch → warn,
   use the fresh row). Owners-tab lines located by ProjectID on that tab (header row 1).
2. **Plan** = clicked accepts only, kinds `ref | fill | status | oo`; cell text is exactly
   `build_ref_workbook._ref_cell_text` / the value the workbook would paste. Skip: rows missing
   from the sheet, `=`-prefixed values, a non-blank differing value cell (conflict) unless the
   line is a `status` change, a `[ref]` cell that already contains every proposed URL (`in_backend`),
   and (2026-10-01) a **stale** line — the live basis cells (`review_data.BASIS_FIELDS`) differ
   from what the reviewer saw (record `basis` ≠ line `basis`, or live ≠ snapshot); listed in the
   plan's `stale`, pushed only with `--include-stale`. The decision stands in the ledger either way.
   Print the plan cell by cell; token = hash of the plan.
3. **Pre-read** the exact ranges with `valueRenderOption=FORMULA`; abort on any formula cell or
   any ProjectID mismatch.
4. **Backup** before-CSV of the touched cells to `notes/sheet-write-<date>-<scope>-before.csv`.
5. **Write** `values.batchUpdate` RAW, cell-scoped ranges, chunked, under `gws-gem-write`.
6. **Verify** by re-read; write the after-CSV; append `push_log.jsonl` (`{key, range, before,
   after, ts, reviewer}`); write a `push` machine-reviewer record — through `ledger.py` (the store
   `log` tab first, origin `push`, then the sidecars) — so the lines show `applied` everywhere.
7. Every run is one explicit authorization from Baird; the server's `/api/push` requires the
   token from `/api/push/plan` and a typed confirm, as LNG does.

Out of push scope, permanently: route columns (§8 apply script), new rows, contested values,
wiki edits, anything on a row whose Status is `N/A`.

**The ledger (2026-10-01).** Three decision paths (chat, loopback server, Google page) plus hand
edits to the sheet had drifted apart. Ruling: the store spreadsheet's `log` tab is the single
source of truth — `review_app/ledger.py` appends every record there first (Code.gs's exact row),
the sidecars are the mirror, `pull.py` brings home the Google page's rows, a chat decides through
`ledger.py decide` and reaches the sheet only through `push.py`, and a store write that fails
refuses the decision. Hand edits to the sheet are detected, not reconciled: `push.py` skips the
line as stale, `publish.py --refresh` reports it as drift, the decision stands.

### 6. Tests (`tests/`, new)

The repo has no test dir; add `tests/conftest.py` putting `scripts/` and `review_app/` on
`sys.path`, a fixture scope with two staging dirs (one deepsweep with every kind, one handoff
`qc/` dir carrying half of them, plus a `*.prior.json` to ignore) and a 6-row snapshot CSV.
Cover: dataset build (kinds, keys, dedupe across dirs, snapshot current values, drift cases from
fact 7, `in_backend`), `decide` (log + derived file, rollback, undo, machine reviewers),
linked contested behaviour, workbook `--decisions` filtering, `update_seed`, and the push plan
(skips, conflicts, token, formula abort) with the gws calls mocked — **never against the live
sheet**.

### 7. Docs to update when phase 1 lands (same PR)

`review_app/README.md` (new), `CLAUDE.md` router entry "Review a batch's decisions" (the
hard-requirements exception is already written), `docs/workflows.md` §6 step (review before
building the actions workbook), `docs/sops/qc.md` handoff contract (`--decisions`),
`docs/reference/staged_json_schema.md` (the two sidecars), `docs/sops/update.md` (`update_seed.py`),
`docs/sops/route_creation.md` step 6 (`--decisions`).

### Phase 1 milestones (each ends with passing tests and a commit)

0. **Repair the drift before parsing around it**: a one-off script normalizes `sheet_row` to int,
   parses the repr-string `proposed_refs`/`verifications` (iran-gas STATUS), and lifts the old
   israel `staged_new` inline refs into `refs`; re-runs `staged_summary.py --index`. Small, keeps
   `review_data.py` honest.
1. `review_app/` skeleton + `review_data.py` + fixture + tests; build the dataset for one real
   scope (Russia gas R7, 531 records, or Egypt gas) and eyeball kinds and counts.
2. Server + Store + read-only UI (queue, cards by kind, filters, keyboard).
3. Decisions, undo, contested linking, `review_log.jsonl` / `review_decisions.json` + tests.
4. Bulk with confirm; Items tab with calls; session summary; sync backend.
5. Suggest + `update_seed.py`; `build_ref_workbook.py --decisions`; `staged_summary` counts;
   `apply_route_candidates.py --decisions`.
6. README + doc updates; **self-resolving concerns** (Baird 2026-09-30): when an open concern's
   `contested[col]` value equals a fill/status line's proposed value on that column, the fill IS
   the resolution — the line is not locked, and accepting it records a `dismissed` call on the
   concern (note "resolved by accepted <col> fill") so the other contested columns unlock too;
   first seen on P2227 StartYear1 (R7). Acceptance: Baird decides one real pending scope end to
   end and rebuilds its handoff actions workbook from the decisions.
7. **One card per status call** (Baird 2026-09-30, built): a status-review line and the refs-leg
   record that stages the SAME Status value onto `Status [ref]` are one decision. `review_data`
   folds the ref record into the status line (`covers`), and `store` writes the line's call to
   every covered key in the same transaction (`via` = the line's key), so the staged records
   stay separate on disk and the consumers are unchanged. A ref record backing a different
   status stays its own card. First seen on P2227 (R7); detail in `review_app/README.md`.

**Phase 1b** (ruling 1 passed): `push.py` + tests + CLAUDE.md wording; first push on a scope with
< 50 accepted cells, backups committed.

**Phase 2** (approved; BUILT 2026-09-30, Google objects created and first dataset published the same day, web app NOT yet deployed): the LNG Apps Script design
(`lng-carriers-researcher/docs/plans/2026-09-21_review-app-phase2_handoff.md`) on the pipelines
dataset. As built: `review_app/publish.py` (dataset → Drive data folder, versioned parts + a
validation index), `gas/Code.gs` (a port of `store.py`'s validation; appends to the store
spreadsheet's `log` tab under the script lock; refuses a write when another reviewer's record for
the key is newer than the page has seen), `web/gas.js` (the second `Store` adapter),
`pull.py` (store → staging-dir sidecars, read-only on Google), `bundle.py`, and the local stand-in
`gas_dev/`. Additions over the LNG design: every record carries `snapshot` + `basis` (a hash of
the backend cells it was judged against), so a later publish reports decisions the backend has
moved under (`drift`) and decisions whose key no longer exists (orphans). Detail:
`review_app/README.md` → "Google version". Rulings (Baird 2026-09-30): a drifted decision
STANDS (flagged, never reopened); a decision orphaned by a renumbered row is carried to the new
key at publish when the match by staging dir + ProjectID + column is unique
(`publish.carry_forward`), otherwise it stays an orphan; pulled logs hold the reviewer's
initials (`BL`; Baird 2026-10-01 — every recorded reviewer is first + last initials, never a full
name), never the address, and the store spreadsheet keeps the address.
`gas_push.py` updates the Apps Script project through Drive, so clasp is not used. Still open:
the web app deployment (a browser step only Baird can do), the milestone 0 identity spike, where
the script project lives (it is in Baird's My Drive), protecting the store's `log` tab, and
whether the loopback server stops recording decisions once the web app is live.

### Model guidance

Milestones 0–4 and 6 are mechanical ports from a working codebase against this spec: Sonnet.
Milestone 5's `build_ref_workbook.py` change touches a 2,605-line builder with paste-surface
invariants, and `push.py` is a live-sheet writer: build those on the top tier or review the diff
there. Verification gates run the same either way.
