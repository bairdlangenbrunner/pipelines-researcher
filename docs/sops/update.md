# SOP — Update (targeted fixes)

The small-batch doer: fix or refresh **specific** GOIT/GGIT rows — named rows, a
handful of stale in-dev rows, fixes detected by a handoff packet. It also
**consumes reconciliation candidates** — a value/status disagreement surfaced by
the Reconciliation SOP is resolved here through normal source-search, not
auto-applied. **Whole-country "re-verify everything" work is NOT an Update** —
that is a Country Sweep (`docs/sops/sweep.md`, workflows.md §3).

The deep research rules (source hierarchy, URL-verification, corroboration,
expansion-vs-construction, divestiture sweeps, route research) live in the
authoritative methodology, `docs/GOIT_Pipeline_Research_Workflow.md` Phase 2. This
SOP is the operational sequence; cite the methodology for the *how*.

## Inputs
- Scope: country + commodity (oil / NGL / gas) + the specific rows/questions.

## Sequence
1. `scripts/refresh_csvs.sh` → fresh snapshot; load `header=2`; exclude buffer rows.
2. **Derive the worklist**: the named rows ∪ any reconciliation value-disagreements
   or handoff-packet fixes queued for this scope ∪ (if asked) stale in-dev rows.
3. For each pipeline:
   - Research per methodology Phase 2 — source hierarchy in
     `docs/reference/source_roster.md`, country tips in `docs/country_notes/`.
   - **Expansion vs. new construction:** if no new physical pipe is built →
     `LengthKnown = 0`, `Diameter = blank`; note the expansion type in `ResearcherNotes`.
   - **Ownership divestitures:** if a divestiture touched multiple pipelines, update
     **all** affected rows, not only those that surfaced in search.
   - Record the confidence tier + corroborating sources in `ResearcherNotes`
     (`docs/reference/confidence_tiers.md`).
4. `scripts/url_verifier.py <url> <expected…>` on **every** URL before it enters the
   workbook — no exceptions, even URLs that worked last batch. Reject GEM URLs.
5. `scripts/entity_lookup.py "<owner>" "<country>"` before staging any new owner —
   don't create duplicate entities.
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
