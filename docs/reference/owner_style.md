# Owner names — the ownership team's style

How an **immediate owner** (`Owner1..Owner11` on the operators/owners tab) is written, so that
what this project stages reads like what GEM's ownership team writes. **The `Operator` column
follows the same style** (Baird 2026-10-01): it is the same kind of entity name, and on most
rows the operator is also `Owner1`, so the two must not drift apart. Parent research is the
ownership team's job, not ours (Baird 2026-10-01): we style the immediate owner and leave the
parent tree alone.

Code: `scripts/entity_style.py` (`style(name) -> StyleResult`; CLI `python scripts/entity_style.py
"<name>" [--json]`). Data: `data/legal_forms.csv`, `data/owner_gazetteer.csv`,
`data/owner_aliases.json`. Enforcement: `check_shard_coverage.py` (blocking, per shard) and
`sweep_gates.py` gate O (advisory, per store). Lint of the existing cells:
`scripts/owner_style_lint.py` → `notes/owner-style-lint-<date>.md` (+ `.csv`).

## Sources of the rules (read via `gws-gem`, never a public export URL)

| What | Where |
|---|---|
| "Immediate Ownership Guide" (the team's conventions, with examples) | Google Doc `1Eqat408hLd1o7OKBdNZoT5QUwYQ24mlUIn_-ubEBxeg` |
| "Ownership research guide" (process + parent methodology) | Google Doc `1SN3MpEpDr1Ck7qsSwscJIs2-lTVeAPeIA9qfwQvtFNM` |
| Legal forms list — 165 forms, `sp` = canonical spelling | Sheet `1XieqEs3A9tKOFo7eRQIJFAIrMllkA3NtKDxWKNBcbpI`, tab `list of types` → `data/legal_forms.csv` |
| Ownership export `ownership_v5_11_0` (entity names + `E…` ids as the team publishes them) | Sheet `1wGI0E4D1-VKbwwRFqnizr-ZDfaI4yMQ3794xjRNu1yQ` |
| Backend tab `Owner/parent formatted` (gid `1530223718`) — the team's own raw→formatted crosswalk | same sheet; source of the alias seed |

Rebuild the local copies: `python3 scripts/build_owner_gazetteer.py [--no-refresh] [--seed-aliases]`
(`--no-refresh` reuses the cached pulls; `--seed-aliases` regenerates
`data/owner_aliases.seed.json`, a review artifact that is gitignored — the curated
`data/owner_aliases.json` is hand-maintained and is never overwritten by the build).

## Which cells this touches

On the operators/owners tab, `Operator`, `Owner1..Owner11` and `Owner1%..Owner11%` are **data**;
`AggregateOwners` and `Percentage Verification` are formulas. On the tracker tabs `Owner`,
`Operator`, `Parent` and `ParentEntityIDs` are INDEX/MATCH formulas off this tab. So a styled name
is staged only into `Owner<N>` (with its `Owner<N>%`) or `Operator`, via a record with
`tab: "operators_owners"` and `ref_col: "Owner [ref]"` / `"Operator [ref]"` — never into the
tracker's `Owner` / `Operator` columns. `Operator` is ONE cell with no `Operator1..N`, and the
sheet does hold `A; B` lists there; the styler flags those `multi_owner` (the style batch files
them as `multi_operator`) and leaves the shape to a human.

## The rules (team examples where the guide gives one)

| Rule | Team writes | Not |
|---|---|---|
| Full legal name + legal form, **punctuation removed** | `Chubu Steel Plate Co Ltd` | `Chubu Steel Plate Co., Ltd.` |
| Legal form in the **short canonical spelling** (`sp` column of the legal-forms sheet) | `Acme Pipeline Corp`, `Acme Energia SpA`, `Acme Pipeline LLC` | `Corporation`, `S.p.A.`, `L.L.C.` |
| Form **trails** the name, in English | `Gazprom PJSC`, `Transneft PJSC` | `PAO Gazprom`, `Public Joint Stock Company Transneft` |
| Russian/CIS forms mapped: OOO→LLC, PAO→PJSC, AO→JSC, TOO→LLP; ZAO→CJSC and OAO→OJSC **only if still registered** so | `Gazprom Transgaz Moskva LLC` | `OOO Gazprom Transgaz Moskva` |
| "Company" **stays** when the form is LLC / LP | `Trail West Pipeline Company LLC` | `Trail West Pipeline Co LLC` |
| Omit the form only when a quick search cannot find one | `Energy Transfer LP` (found) | a bare `Energy Transfer` |
| **No trailing acronym / trade name in parentheses**; it goes to `researcher_notes` and `data/owner_aliases.json` | `Sui Northern Gas Pipelines Ltd` | `Sui Northern Gas Pipelines Ltd (SNGPL)` |
| **A parenthesized legal name after a short all-caps token IS the name** (flag `acronym_lead`, 2026-10-05): the inner name is kept, the acronym goes to the alias file | `Energía Argentina SA` | `Enarsa (Energía Argentina SA)` |
| Mid-name parentheticals that are part of the legal name **stay** | `GAIL (India) Ltd`¹, `Mettiki Coal (WV) LLC`, `PT Pertamina (Persero)` | |
| Integral punctuation stays | `E.ON SE` | `EON SE` |
| Dotted abbreviations lose the dots | `Chevron USA Inc` | `Chevron U.S.A. Inc.` |
| Leading `PT` (Indonesia) stays | `PT Pertamina (Persero)` | `Pertamina PT` |
| State bodies: `<Body> (<Country>)`, `Government of <Country>` | `Ministry of Oil (Iraq)`, `Government of Qatar` | `Iraq Ministry of Oil`, `Ministry of Oil of Iraq`, `State of Qatar`, `Republic of Iraq` |
| Joint ventures: no legal form expected | `Yamal LNG JV` | |
| Sentinels, lowercase | `unknown`, `small shareholder(s)`, `natural person(s)` | `Unknown`, `Various` |
| Former owner | `X Corp [former]` | |
| Share belongs in `Owner<N>%`, not the name | `Acme Corp` + `55.00%` | `Acme Corp [55%]` |
| One owner per `Owner<N>` cell | | `Energy Transfer; Enbridge` |

¹ `GAIL (India) Ltd` is a confirmed alias of the team's canonical `GAIL Ltd`, so the styler
adopts `GAIL Ltd`; the parenthetical rule itself keeps mid-name geography.

Country names inside a state body follow the GEM naming conventions sheet
(`docs/reference/gem_naming_conventions/`): `Türkiye`, `Russia`, `Iran`.

## Adoption policy (Baird 2026-10-01: adopt on exact / alias, flag fuzzy; 2026-10-05: plus rulings and mechanical rules)

`style()` returns `styled`, `basis`, `confidence`, `entity_id`, `aliases`, `candidates`, `flags`.
**`adoptable(res)` is the one policy every consumer calls** (the gates, `restyle_staged_owners.py`,
`stage_owner_style.py`, `push.py`): true when nothing changed, on basis `exact` / `alias` /
`ruling`, and on `rules` / `stem` when the styled form has no comma and every flag is in
`MECHANICAL_FLAGS` (`form_punctuation`, `form_long`, `form_moved`, `form_russian`,
`dots_stripped`, `acronym_dropped`, `acronym_lead`, `quotes_stripped`, `form_from_gazetteer`,
`percent_stripped`, `whitespace`, `ruled`). `acronym_not_initials` always holds unless a ruling
settles it.

| basis | when | confidence | action |
|---|---|---|---|
| `exact` | the raw or rules-styled name IS a gazetteer name (also exact modulo legal-form spelling: `Kuwait Oil Company Ltd` for our `Kuwait Oil Co Ltd` — the team's spelling wins) | high | adopt, carry the `E…` id |
| `alias` | a **confirmed** alias in `owner_aliases.json` (`Saudi Aramco` → `Saudi Arabian Oil Co`) | high | adopt |
| `ruling` | Baird ruled on this raw name (or on this `<PID>/<column>` cell) in `data/owner_rulings.json` | high, flag `ruled` | adopt; a cell ruling may also `clear` the cell |
| `stem` | no legal form on the input and the gazetteer has this exact stem under ONE form (`Petroleum Development Oman` → `… LLC`) | medium, flag `form_from_gazetteer` | adopt; confirm in a quick search |
| `rules` | no gazetteer hit; the rule table applied | medium with a form, low without | adopt when every flag is mechanical (a spelling, not a judgment), else a person decides |
| `sentinel` / `passthrough` | sentinel value / non-Latin script / empty | high / low | as returned |

Never adopted, always listed in `candidates` and flagged for a human:
- `alias_candidate` — the alias file lists the name as a **candidate** (subsidiary, JV vehicle,
  successor) of a canonical entity. The SPV ruling (`gem_schema.md`, 2026-09-15) says `Owner1`
  holds the SPV, never its parent, so `Kinder Morgan Freedom Pipeline LLC` stays and
  `Kinder Morgan Inc` is only noted.
- `form_conflict` — same stem in the gazetteer under a different form (`Tatneft OJSC` vs
  `Tatneft PJSC`): a registration question, decide by hand.
- `form_ambiguous` — same stem under several forms.
- `fuzzy_candidates` — `token_set_ratio ≥ 90` on the stem, filtered to names that keep at least
  half the query's tokens (and the same `(Country)` for state bodies).

A `rules`-basis name with `no_legal_form` is low confidence: do the quick registry search the
guide asks for, add the form if it turns up, otherwise stage as the source spells it and say so
in `researcher_notes`.

## `data/owner_aliases.json` — the contract

```json
{"canonical": "Saudi Arabian Oil Co", "entity_ids": ["E100000000888"],
 "aliases":    ["Saudi Aramco", "Aramco", "Saudi Arabian Oil Company"],
 "candidates": [],
 "status": "confirmed", "evidence": ["Owner/parent formatted: Saudi Aramco -> Saudi Arabian Oil Co"]}
```

- `aliases` = **confirmed** other spellings / abbreviations / former names of the SAME entity;
  `style()` adopts them. Every acronym the styler drops belongs here (and in the record's
  `researcher_notes`) — this file is the "owner name plus alt names" doc Baird asked for.
- `candidates` = names that are RELATED but not the same entity (subsidiary, JV, successor):
  surfaced as `alias_candidate`, never adopted. Promote to `aliases` only on evidence that it is
  one entity (a rename, a merger that kept the id).
- `status`: `confirmed` (checked against the team's crosswalk or by hand) or `seed` (machine
  pairing from `Owner/parent formatted`, unreviewed).
- Keyed by entity, one object each; `entity_ids` may hold several ids when the team's export
  carries the same name under more than one (the gazetteer takes the id of the row with the most
  tracker rows — see "Known oddities").

Add to it by hand when a sweep drops an acronym or a researcher confirms a spelling; keep the
JSON sorted by `canonical`. Nothing regenerates it.

## Where it runs

- **Every staged `Owner<N>` and `Operator` value** that differs from the sheet's current cell:
  `check_shard_coverage.py` lists an un-styled name as UNMERGEABLE (blocking, before the subagent
  finishes); `sweep_gates.py` gate O lists it per store at delivery, with O' (no legal form) and
  O'' (unadopted candidate) as sub-lists. A value equal to the sheet is carried, not proposed,
  and is the lint's business; "the sheet" means the worklist's snapshot OR the newest
  operators/owners snapshot in `data/` (`entity_style.carried_on_sheet`), since a push after the
  worklist's pull moves the sheet.
- **`review_app/push.py`** lists every Owner<N>/Operator cell a plan would write in a spelling
  `adoptable()` would change and refuses `--apply` until the staged record is restyled
  (`--allow-unstyled` overrides, by hand). A plan line marked `style_only` stamps `LastUpdated`
  only (Baird 2026-10-05).
- **`scripts/restyle_staged_owners.py`** re-spells pending staged proposals in place (every live
  `staged_resolutions.json` and shard `rows/*.json`), as string edits through
  `scripts/json_patch.py` so each file keeps its formatting; the source's spelling goes to
  `researcher_notes`; held cells are listed in `notes/owner-restyle-staged-<date>.md`. First run
  2026-10-05: 403 cells, 105 re-spellings, 32 held.
- **`data/owner_rulings.json`** holds Baird's rulings on names the styler cannot settle (`names`
  by raw name; `cells` by `<PID>/<column>`, including `clear`). `style()` returns basis `ruling`
  for a ruled name; `cell_ruling(pid, col)` for a ruled cell.
- `scripts/entity_lookup.py "<name>"` prints the styled form, basis, id, aliases and unadopted
  candidates after its duplicate check — run it before staging any new owner.
- The record: `values: {"Owner1": "<styled>", "Owner1%": "…"}`, `researcher_notes` carrying the
  source's spelling, the dropped acronym, and the parents found (never flattened into `Owner1`).

## Known oddities (team side, recorded 2026-10-01)

- The operators/owners tab has `OperatorLocalLanguage` but no owner local-language column, so a
  non-Latin owner name has nowhere to go except `researcher_notes` (`style()` passes it through
  with flag `non_latin`).
- `Owner/parent formatted` carries `Bangladesh Petroleum Corporation Corp` (doubled form) and maps
  `Government of China` → `Government of Pakistan`; both dropped from the alias seed.
- The ownership export zips names to ids positionally, so one name can carry several `E…` ids;
  `owner_gazetteer.csv` keeps them all (`n_rows` per pairing) and the styler uses the top row.
