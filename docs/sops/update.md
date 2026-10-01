# SOP — Update (targeted fixes)

The small-batch doer: fix or refresh **specific** GOIT/GGIT rows — named rows, a
handful of stale in-dev rows, fixes detected by a handoff packet. It also
**consumes reconciliation candidates** — a value/status disagreement surfaced by
the Reconciliation SOP is resolved here through normal source-search, not
auto-applied. **Whole-country "re-verify everything" work is NOT an Update** —
that is a Country Sweep (`docs/sops/sweep.md`, workflows.md §3).

The deep research rules each have one home: source hierarchy →
`docs/reference/source_roster.md`; URL verification → standing rule 2 + `scripts/url_verifier.py`;
corroboration and tiers → `docs/reference/confidence_tiers.md`; route research →
`docs/sops/discovery.md` "Route / map research" + `docs/reference/route_conventions.md`;
expansion-vs-construction and divestiture sweeps → step 3 below. This SOP is the
operational sequence.

## Inputs
- Scope: country + commodity (oil / NGL / gas) + the specific rows/questions.

## Sequence
1. `scripts/refresh_csvs.sh` → fresh snapshot; load `header=2`; exclude buffer rows.
2. **Derive the worklist**: the named rows ∪ any reconciliation value-disagreements
   or handoff-packet fixes queued for this scope ∪ (if asked) stale in-dev rows ∪ the
   review-app seed, if one exists: `python scripts/update_seed.py --country <C> --commodity
   <gas|oil> [--dirs …] [--out PATH]` reads each staging dir's `review_decisions.json` (latest
   live record, undone ones ignored) and writes
   `batches/<scope>/staging/update-seed-<YYYYMMDD>/staged_updates_seed.json`: one update unit
   per line a person `suggest`ed (reviewer's value + note; `old` / `tier` / `refs` left empty)
   and one research unit per concern called `confirmed` or `needs_research`. It is a WORKLIST,
   not findings: research each unit as in step 3, then stage the results in this run's
   `staged_updates.json` (the seed's filename differs on purpose so `staged_store` never loads
   it as pending values). No decision files: empty seed, exit 0.
3. For each pipeline:
   - Research priorities, in order: status changes (proposed → construction →
     operating, or → shelved/cancelled); missing `[ref]` URLs; then the key data
     fields. Source hierarchy in `docs/reference/source_roster.md`, country tips in
     `docs/country_notes/`.
   - **Expansion vs. new construction:** for any capacity expansion (pump-station
     additions, DRA injection, terminal upgrades, looping) check whether new physical
     pipe is laid. None → `LengthKnown = 0`, `Diameter = blank`. Some (a looping project
     adds parallel pipe) → record the NEW pipe's length and diameter, never the existing
     system's. Note the expansion type in `ResearcherNotes`.
   - **Ownership divestitures:** if a divestiture touched multiple pipelines, update
     **all** affected rows, not only those that surfaced in search.
   - Record the confidence tier + corroborating sources in `ResearcherNotes`
     (`docs/reference/confidence_tiers.md`).
4. `scripts/url_verifier.py <url> <expected…>` on **every** URL before it enters the
   workbook — no exceptions, even URLs that worked last batch. Reject GEM URLs. Never
   guess paths, query strings or page IDs; a fact whose exact URL can't be located goes
   in `ResearcherNotes` as `Source: <company> press release dated <date>, titled
   '<title>' — URL not verified`, with the `[ref]` cell left blank.
5. `scripts/entity_lookup.py "<owner>"` before staging any new owner — don't create
   duplicate entities. It also prints the name in the ownership team's style
   (`docs/reference/owner_style.md`): stage THAT in `Owner<N>`, and put the source's spelling
   + any dropped acronym in `researcher_notes` (and the acronym in `data/owner_aliases.json`).
6. Stage findings as `batches/<scope>/staging/<run>/staged_updates.json` (committed
   audit trail).
7. Build the update workbook (no generic builder yet — copy the per-batch
   `build_update_workbook.py` pattern from `batches/united-states-oil/staging/update-delaware-express/`;
   layout per `docs/reference/workbook_conventions.md` "Update workbook") →
   `batches/<scope>/deliverables/pipelines_batch_<stamp>_<scope>_update.xlsx`; `scripts/recalc.py`; present.

## Pre-delivery checks
URL spot-check (fetch 3–5), expansion-length, ownership consistency, status logic
(2y→shelved / 4y→cancelled), date consistency, every changed row has a
`ResearcherNotes` rationale, no GEM self-citation, corroboration tier recorded.
See `docs/sops/qc.md` for the full checklist.

## Iterate
Expect Baird to challenge specific data points. Acknowledge the error, re-search
with verified sources, regenerate — **do not defend** wrong findings (standing rule 3).
