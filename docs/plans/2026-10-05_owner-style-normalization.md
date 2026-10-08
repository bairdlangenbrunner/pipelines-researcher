# Owner and operator style normalization, tracker-wide (plan, 2026-10-05)

Goal: every non-blank `Operator` and `Owner1..Owner11` cell on the "Pipeline operators/owners"
tab reads the way GEM's ownership team writes entity names (`docs/reference/owner_style.md`),
and nothing this project pushes afterwards re-introduces an unstyled name. Style only, no
ownership research: who owns what, and the parent tree, stay the ownership team's business.

Numbers below are from the 2026-10-01 snapshot (the slice-1 input) unless marked 10-05.

## Where things stand

**Slice 1 is staged, not applied.** `batches/owners-style/staging/update-owner-style-20261001/`
holds 2,304 cells (2,145 `Owner<N>` + 159 `Operator`) on 2,015 ProjectIDs, 198 distinct names,
every one an exact gazetteer match or a confirmed alias. Workbook
`batches/owners-style/deliverables/pipelines_batch_20261001_1852_ET_owners-style_update.xlsx`.
Since then the tab lost 15 ProjectIDs (P0482, P0483, P1789, P1851, P1853, P1868, P1869, P1872,
P4602, P5314, P5315, P5638, P6823, P7617, P8100) and one staged cell drifted (P0277 `Owner1`,
`Enbridge` became `Enbridge Inc.` through a US gas push; the styled form is `Enbridge Inc`).
The batch has to be re-staged on a fresh snapshot before anything is applied; the script is
deterministic, so that is a re-run, not new work.

**574 cells were held back**, by reason:

| reason | cells | distinct names | what it is |
|---|---:|---:|---|
| `rules_only` | 408 (170 Operator) | 124 | no gazetteer hit; punctuation, long form, moved form, dropped acronym |
| `stem_medium` | 121 (19 Operator) | 44 | stem matches one gazetteer entry; its legal form adopted at medium |
| `form_conflict` | 25 | 4 | SSGC, TGTDCL, Anhui, KOC: `Co` here, `Co Ltd` in the gazetteer |
| `alias_candidate` | 7 | 2 | Norsk Hydro Produksjon, ConocoPhillips Alaska: subsidiaries, SPV ruling says they stay |
| `acronym_not_initials` | 6 | 4 | SUMED, MIMI, Bapco, IGNL |
| `multi_operator` | 3 | 3 | one `Operator` cell listing two or three operators |
| `non_latin` | 2 | 1 | `ТОО «Казахстанско-Китайский Трубопровод»` |
| `row_collision` | 2 | 1 | P1321 carries `Plinacro Ltd` in Owner1 and Owner2 |

Inside `rules_only` the flags are, by cells: `form_punctuation` 209, `acronym_dropped` 104,
`fuzzy_candidates` 78, `form_long` 71, `no_legal_form` 23, `form_moved` 18. Most of it is
mechanical (`Algonquin Gas Transmission, LLC` to `Algonquin Gas Transmission LLC`).

**The lint also lists names the styler leaves alone but the guide would not.** 337 distinct
names (1,107 cells) carry no legal form and no gazetteer hit: `QazaqGaz` (42 cells),
`Bulgartransgaz` (38), `Gas Transmission System Operator of Ukraine` (37), `Gasunie Transport
Services` (34), `PT Pertamina Gas` (28), `Gas Networks Ireland` (24), `Boardwalk Pipeline
Partners` (23), `Uztransgaz` (23), `OQGN` (22), `Transco` (21). The guide says to omit the form
only when a quick search cannot find one, so each of these owes one registry lookup. Another
103 unchanged names (459 cells) have a fuzzy gazetteer near-match listed for a human to look at.

**Our own pushes are leaking unstyled names onto the tab.** The US gas review-app pushes of
2026-10-02 wrote 215 operators/owners cells (188 `Operator` fills, 12 `Owner<N>` fills, 15
changes), and 113 of them are not in team style (`Algonquin Gas Transmission, LLC`,
`Transcontinental Gas Pipe Line Company, LLC`, `Northern Natural Gas Company`, `Energy
Transfer`, `TC Energy`). The US batches were staged before the styler existed (2026-10-01), the
shard check only runs on new shards, and `push.py` writes what was clicked. The pending staged
shards hold 1,848 more `Owner<N>`/`Operator` proposals of which 641 would restyle: about 450
across the US gas deep-sweep dirs, 48 India, 41 Saudi Arabia, 22 Pakistan, 14 Iraq, 9 Libya,
7 Iran, 4 Russia. Left alone, the next pushes undo part of the normalization.

**Two gaps in the tooling.**
- `scripts/check_shard_coverage.py` (line 262) and `sweep_gates.py` gate O check `Owner\d+`
  only; a proposed `Operator` value is never style-checked, although `owner_style.md` says the
  column follows the same rules.
- The styler mishandles the "acronym, then the full legal name in parentheses" shape:
  `TGS (Transportadora de Gas del Sur SA)` becomes `TGS (Transportadora de Gas del Sur SA`
  (closing parenthesis lost, acronym kept). Five names, 65 cells: TGS, TAG, NTS, TGN, TGI. The
  team style for that shape is the full legal name, `Transportadora de Gas del Sur SA`, with the
  acronym kept as an alias.

**No route from the staged batch to the sheet yet.** `review_app/review_data.py::_load_dir`
reads four file kinds and `staged_updates.json` is not one of them (intake plan item A4,
`docs/plans/2026-10-02_review-app-intake.md`), and the review-app manifest is per
country+commodity with no tracker-wide entry (item A5, open question 4 of that plan).
`review_app/push.py` already writes `oo` lines to the operators/owners tab and stamps
`Researcher`/`LastUpdated`, so once lines exist the write path is ready.

**The ownership team's side.** Their `Owner/parent formatted` tab (gid `1530223718`) is keyed
by ProjectID with the raw `OwnerString` next to `ParentString` and `OwnerEntityIDString`. The
tracker `Parent` formulas look up by ProjectID, so re-spelling owners breaks nothing. But the
stored raw strings will differ from the live cells on about 2,000 rows after slice 1, and any
diff the team runs will show them all as changed ownership. They should hear about this before
the apply, as a spelling-only pass.

## Phases

### Phase 0: stop the leak and fix the styler (before any apply)

0.1 **Style check for `Operator`.** Widen the regex in `check_shard_coverage.py` and gate O
    from `Owner\d+` to `Owner\d+|Operator`. A `multi_owner`-flagged `Operator` value (an
    `A; B` list) is reported as a shape question, not blocked.

0.2 **Fix the parenthesized-legal-name shape in `entity_style.py`.** When the text in trailing
    parentheses itself ends in a recognized legal form and the stem before it is a short
    all-caps token, the parenthetical is the legal name: styled = inner name, acronym to
    `aliases`, flag `acronym_lead`. Add the five cases plus `Enarsa (Energía Argentina SA)`
    (already an alias hit) to the styler's self-test. Re-run `owner_style_lint.py` and confirm
    no other name changes shape.

0.3 **Restyle the pending staged proposals in place.** A new `scripts/restyle_staged_owners.py`
    walks every `rows/*.json` under `batches/*/staging/*/`, runs each `Owner<N>`/`Operator`
    value through the styler, and rewrites the value when the basis is `exact` or `alias`, or
    the only flags are mechanical (`form_punctuation`, `form_long`, `form_moved`, `form_russian`,
    `dots_stripped`, `acronym_dropped` with initials). The source spelling goes into
    `researcher_notes` ("source spells it Algonquin Gas Transmission, LLC"). Everything else is
    left as staged and listed in a report under `notes/`. Rebuild the review-app dataset so the
    person clicks the styled form. Decision 3 below covers the alternative (style at push time).

0.4 **`push.py` plan-time guard.** The plan lists any `oo` or `fill` line whose
    `Owner<N>`/`Operator` value the styler would change at `exact`/`alias` basis, and refuses
    to `--apply` while that list is non-empty unless `--allow-unstyled` is passed. This is a
    check, not a rewrite: it never changes a clicked value.

0.5 **Refresh inputs.** `./scripts/refresh_csvs.sh`, then
    `python scripts/build_owner_gazetteer.py` (the ownership export and legal-forms list were
    last pulled 2026-10-01); check the export version string and note it in the batch meta.

**Phase 0 results (done 2026-10-05, same session).**

- 0.1 done. Both gates check `Owner\d+|Operator`. A value equal to the NEWEST operators/owners
  snapshot is carried, not checked (`entity_style.carried_on_sheet`), because a push after the
  worklist's pull moves the sheet (the 2026-10-02 US gas push did).
- 0.2 done. `acronym_lead` in `entity_style.py`; `form_punctuation` is set whenever the legal
  form's spelling moved; `adoptable()` is the one adoption policy (exact, alias, ruling, or a
  rules result whose flags are all mechanical; `acronym_not_initials` always holds).
- 0.3 done. `scripts/restyle_staged_owners.py --apply` over every live staging dir: 403 cells
  rewritten (201 in `staged_resolutions.json` files, the rest in shard rows), 105 distinct
  re-spellings, 32 cells held for a person (acronym_not_initials 16, fuzzy_candidates 10,
  alias_candidate 6), 3,654 proposed values equal to the sheet carried untouched. Report:
  `notes/owner-restyle-staged-2026-10-05.md` + `.csv`. Two defects in the first applies, both
  undone from pre-apply copies and fixed before the final run: the JSON was re-serialized (fixed
  with `scripts/json_patch.py`, string edits that keep each file's formatting), and carried shard
  values were restyled because shard records carry no `project_id` (fixed by passing the file's
  PID). Gate check after the apply: US west style findings 27 to 0, US gulf 36 to 0, India 28 to 4
  (the 4 are by-design holds); no other finding moved.
- 0.4 done. `push.py` lists unstyled Owner<N>/Operator cells on the plan and refuses `--apply`
  unless `--allow-unstyled`; a line marked `style_only` stamps `LastUpdated` only (decision 2).
- 0.5 done. Snapshots and gazetteer refreshed 2026-10-05 (`GEM_operators_owners_snapshot_20261005.csv`).

### Phase 1: apply slice 1 (exact and alias hits)

1.1 **Re-stage** with `stage_owner_style.py --owners-csv <10-05 or later snapshot>` into a new
    dir `update-owner-style-<date>`; move the 10-01 dir and workbook to `archive/`. Expect about
    2,300 cells; the summary line is the check.

1.2 **Decision surface at the NAME level, not the cell level.** 198 names cover 2,304 cells; a
    reviewer should decide `Enbridge` to `Enbridge Inc` once, not 125 times. Build the review-app
    update-store reader (A4) so each `staged_updates.json` `changes` entry becomes an `oo` line,
    and add a `group` key (`<dir>::name:<raw>|<styled>`) so the app renders one decision line per
    distinct name with its cell count and PID list, and a decision on the group fans out to its
    cells in the ledger. Add the tracker-wide manifest entry (A5: country `*`, commodity `both`)
    rendered under its own checkbox. The 113 unstyled cells the US push wrote are picked up here
    automatically because the re-stage reads the live snapshot.

1.3 **Push** through the normal route: `python review_app/push.py` plan, ask, `--apply PLAN`,
    chunked. The plan reads the target cells with the FORMULA render option and aborts on any
    formula cell (`AggregateOwners` and `Percentage Verification` are formulas on this tab and
    are never in scope). Backup CSV to `notes/`, re-read and verify, commit the backup.
    `push.py` stamps `Researcher = CB` and `LastUpdated` on every written row: about 2,000 rows
    on this tab. See decision 2.

1.4 ~~Tell the ownership team before 1.3~~ Dropped by decision 6.

**Phase 1 results (1.1 and 1.2 done 2026-10-05, same session; 1.3 pending).**

- 1.1 done. `scripts/stage_owner_style.py --owners-csv data/GEM_operators_owners_snapshot_20261005.csv`
  wrote `batches/owners-style/staging/update-owner-style-20261005/` (the script moved from the
  10-01 staging dir to `scripts/`, the workbook builder to `scripts/build_owner_style_workbook.py`;
  the 10-01 store and workbooks are in `batches/owners-style/archive/`). 2,878 cells (2,457
  `Owner<N>` + 421 `Operator`; 1 cleared, P1321 Owner2) on 2,334 PIDs, 397 names; basis alias
  2,059 / rules 363 / exact 278 / stem 134 / ruling 44; tier high 2,381 / medium 497; 131 held
  back (fuzzy_candidates 73, no_legal_form 42, comma_list 8, alias_candidate 4, group 2,
  state_body 1, acronym_not_initials 1). More than the 2,300 expected because the Phase 3
  rulings and the mechanical-rules basis joined the slice. Workbook `20261005_1948_ET`.
- 1.2 done. The review app reads a `staged_updates.json` with `meta.style_only` (and no other
  update store): one `oo` line per cell, key `<dir>::<PID>|<owners row>|oo:<col>:style`, no
  `ref_col`; lines grouped by current spelling into name cards (`pid = "name:<spelling>"`) so each
  name is decided once and fans out. The tracker-wide scope (country `*`, commodity `both`) is
  found by `staged_store.trackerwide_dirs`, handled by `scopes.py` (`check`/`set --country '*'
  --commodity both`), slugged `tracker-wide` in the ledger, and shown under its own checkbox; it
  joins both commodities' batch builds once included. `push.py`, `publish.py` and `store.py`
  take the line's own `pid`; a style-only line stamps `LastUpdated` only. Tests: 4 new tests
  (data, scopes, push plan), 268 passing. Live build: 397 cards, 2,877 lines (1 cell dropped
  because P3966 is `Status = N/A`), 1 clear, 0 moved rows, 4.6 MB; the 1,056 oil-PID lines have
  no tracker row in the gas snapshot, which is harmless because the push locates the owners tab
  by PID + owners row. `scopes.py check --country '*' --commodity both` exits 3 until Baird
  answers.
- 1.3 pending: include the scope, decide the name cards, `push.py` plan → ask → `--apply`, chunked.

### Phase 2a: the mechanical remainder (rules without a gazetteer hit)

Same staging script, a second adoption class: basis `rules`, confidence `medium`, and the flag
set is a subset of {`form_punctuation`, `form_long`, `form_moved`, `form_russian`,
`dots_stripped`, `acronym_dropped`, `acronym_lead`}, no `fuzzy_candidates`, no
`no_legal_form`. From the 10-01 numbers that is most of the 408 `rules_only` cells (about 100
names). Tier `medium` (no gazetteer entity behind it), one group line per name as in 1.2. The
`alias_candidate` pair (Norsk Hydro Produksjon a.s, ConocoPhillips Alaska, Inc) belongs here
too: the SPV ruling keeps the entity, the punctuation still normalizes, so the never-adopt block
should apply to the entity swap, not to the spelling.

### Phase 2b: the research slice (one quick lookup per name)

Three name sets owe a registry check, each a single question ("what legal form does this entity
carry, and where does it say so"):

| set | names | cells | source |
|---|---:|---:|---|
| `stem_medium` (form taken from one gazetteer entry; confirm it) | 44 | 121 | held-back list |
| unchanged, `no_legal_form`, no gazetteer hit | 337 | 1,107 | lint csv |
| `rules_only` with `no_legal_form` (mostly a dropped acronym on a form-less name) | ~12 | 23 | held-back list |

Run it as a fan-out of cheap subagents (Haiku or Sonnet; the task is a registry lookup with a
fixed answer shape), ten to fifteen names per agent, output one JSON record per name: raw name,
legal form found or `none found`, the source (registry page, annual report, the entity's own
site), one validated URL, and a one-line note. The URL goes through `url_verifier` like any ref.
A found form stages the change at `high` with the URL appended to the row's `Owner [ref]` or
`Operator [ref]` (additive; a researched value owes a ref). "None found" leaves the cell alone and
records the search in the batch's `names` map so the next lint does not re-ask. Names that are
sentinels or state bodies (`Gas Transmission System Operator of Ukraine` is a company; a
ministry is not) follow the state-body rule instead. Confirmed forms also go into
`data/owner_aliases.json` when the entity has an `E…` id, so the gazetteer covers it next time.

Budget: about 400 names at a few thousand tokens each; one or two sessions. The 103 unchanged
`fuzzy_candidates` names (459 cells) are a human list, not a research task: the candidate is
either the same entity (promote to alias) or not (dismiss), and the lint already prints them.

### Phase 3: rulings only a person can make

**Ruled 2026-10-05 (pickers in the session; recorded in `data/owner_rulings.json`, which the
staging and restyle scripts read, basis `ruling`):** form conflicts adopt the gazetteer form
(`Sui Southern Gas Co Ltd`, `Titas Gas Transmission and Distribution Co Ltd`, `Anhui Province
Natural Gas Development Co Ltd`, `Kuwait Oil Company Ltd`); non-initial acronyms (`SUMED`,
`MIMI`, `Bapco`) drop to the alias file; a multi-operator cell keeps its list with each name
styled; the Cyrillic operator becomes `Kazakhstan-China Pipeline LLP`; P1321 keeps `Plinacro doo`
in Owner1 and Owner2 is cleared; subsidiaries (`Norsk Hydro Produksjon AS`, `ConocoPhillips
Alaska Inc`) get punctuation fixes only, never a merge into the parent. Still open: whether the
15 operators/owners rows removed from the tab between 10-01 and 10-05 (P1851, P1853, P6823 and
12 others) were deleted on purpose.

The list as it stood before the rulings, each with the cells it unlocks:

- `form_conflict` (25 cells, 4 names): `Sui Southern Gas Co` vs the gazetteer's `Co Ltd`;
  `Titas Gas Transmission and Distribution Co` vs `Co Ltd`; `Anhui Province Natural Gas
  Development Co` vs `Co Ltd`; `Kuwait Oil Co` vs `Kuwait Oil Company Ltd`. The lint lists 13
  more unchanged names in the same situation (`Kuwait Petroleum Co` vs `Corp`, 24 cells;
  `Indian Oil Corp` vs `Corp Ltd`, 13; `DCP Midstream LLC` vs `LP`, 8). Registration questions;
  a registry check settles most of them and could ride along with 2b.
- `acronym_not_initials` (6 cells): keep `SUMED`, `MIMI`, `Bapco` as aliases and drop them
  from the cell, or keep the parenthetical? `IGNL` is a typo for INGL and resolves to the alias
  hit `Israel Natural Gas Lines Ltd`.
- `multi_operator` (3 cells): `Enterprise Products Partners; Enbridge`, `Swissgas; Fluxswiss`,
  `Gas Transmission System Operator of Ukraine; Gazprom; Intergas Central Asia`. The tab has no
  `Operator1..N`; pick one operator per cell, or keep the list.
- `non_latin` (2 cells): `ТОО «Казахстанско-Китайский Трубопровод»` to the romanized
  `Kazakhstan-China Pipeline LLP` (the local spelling has no owner-side column; it goes to
  `researcher_notes` or `OperatorLocalLanguage`).
- `row_collision` (P1321): `Plinacro Ltd` in both Owner1 and Owner2; merge the shares.
- Three operators/owners rows with no tracker match (P1851, P1853, P6823) were removed from the
  tab between 10-01 and 10-05 along with 12 others; confirm those deletions were intentional.

### Phase 4: keep it that way

- Re-run `owner_style_lint.py` after every push that touches the operators/owners tab and
  file the report under `notes/`; a non-zero "would change at exact/alias" count is a defect
  in a push, not a new batch.
- `build_owner_gazetteer.py` refresh at the start of every style batch, and whenever the
  ownership team publishes a new export version.
- Docs to update when each phase lands: `docs/reference/owner_style.md` (the `acronym_lead`
  rule, the Operator check, the push guard), `review_app/README.md` (update-store reader,
  tracker-wide scope, group lines), `docs/workflows.md` §5 (style batch recipe), CLAUDE.md
  pending item and `docs/research_backlog.md` (counts regenerate; pointers only).

## Decisions (Baird, 2026-10-05)

1. **Apply route: the review app.** Build the update-store reader (A4) with name-group lines
   and the tracker-wide scope (A5); push through `push.py`. No one-off write.
2. **Style-only pushes update `LastUpdated` only.** `Researcher` keeps the person who did the
   ownership research; the 2026-10-02 stamp rule is amended for style-only lines (`push.py`
   gets a per-line `style_only` marker the update-store reader sets on owner-style batches).
3. **Restyle the pending staged proposals in place** (0.3) before they are reviewed.
4. **Stop at gazetteer plus mechanical rules for now.** Phase 2b (legal-form lookups for the
   337 form-less names and the 44 stem confirmations) is parked as a todo in Baird's Asana
   gem-desk project, not scheduled:
   https://app.asana.com/1/1200305284526705/project/1215778291279370/task/1219187334243631
5. **Phase 3 rulings** are collected through pickers in the session and recorded in
   `data/owner_rulings.json` (`names`: one entry per raw name with the styled form, aliases,
   ruling and date; `cells`: per `<PID>/<column>` rulings, including `clear`), which the staging
   and restyle scripts read so a ruled name is staged on the next run instead of held back.
6. **The ownership team is not told ahead of the push.**

## Order and size

Phase 0 is one session and must precede any push to the operators/owners tab, including the
remaining US gas pushes. Phase 1 is one session of tooling plus Baird's clicks on 198 group
lines. Phase 2a is a re-run of the staging script with the second adoption class, same
session as the first 2b fan-out. Phase 2b is one to two sessions of cheap-model fan-out.
Phase 3 waits on rulings and can be applied in any later batch.
