# SOP — Annual country update packet (campaign mode)

The country-by-country annual update. For each country, this repo produces a **packet**
researchers can rely on **entirely** for two of the three legs of a normal update year:

1. **In-dev check** — every `proposed` / `construction` / `shelved` row re-audited, with a
   per-row **status verdict** (the `__STATUS__` record type) plus the standard deep-sweep
   ref/fill/validity work.
2. **New + missing projects** — country-scoped discovery: newly announced projects AND
   older lines GEM never captured (the "maps" stance), consolidated with
   match-to-existing FIRST.
3. **Operating pipelines** — researchers handle these themselves this cycle. A lighter
   *operating refresh* tier (event scan: shutdown / idle / expansion / ownership change;
   ref re-verify only where the deterministic HTTP check finds dead links) is planned as a
   follow-on once in-dev batches prove out — design note below, not yet implemented.

Commands, in order: `docs/workflows.md §7`. Everything here is **read-and-stage only** —
all standing rules apply; nothing touches the live Sheet.

## Campaign layer

- `python scripts/build_campaign_roster.py --tracker gas --campaign ggit-2026` →
  `campaigns/<campaign>/roster.csv`: one row per country, in-dev/operating counts from a
  fresh snapshot, sorted by in-dev total. **Manual tracking columns survive refreshes**
  (`priority`, `indev_status`, `discovery_status`, `packet_file`, `applied`, `notes`) —
  update them by hand (or ask the agent) as countries move through the pipeline.
- One staging dir per country: `batches/staging/annual-<tracker>-<country-slug>/` holds
  both legs (worklist + shards for the in-dev sweep; `discovery_context.json` +
  `discovery/` for the discovery leg; `staged_resolutions.json` + `staged_new.json` as the
  committed audit trail).
- The **packet** = the pair of deliverables for the country, same scope slug:
  `…_<slug>_annual-indev.xlsx` (StatusReview / Backend / OperatorsOwners / Fills /
  Validity tabs) + `…_<slug>_discovery.xlsx` (NewRows / MonitorList / MatchedExisting).

## The status verdict (`__STATUS__` record, annual-update mode)

`build_deepsweep_args.py --status-review` puts the `critical-deep-sweep` workflow in
annual-update mode: every subagent also stages one `status_reviews` object **per segment
row**. Verdict vocabulary:

| verdict | meaning | merge-time QC |
|---|---|---|
| `confirm` | recorded Status verified, with evidence date | — |
| `change` | evidence-based new status; `proposed_changes` = exact column→value edits (Status + matching date cols) | zero verified refs → downgraded to `unclear` (a status change is a claim; it needs sources) |
| `stale` | no independent news; dormancy rules (proposed ≥2y → shelved, shelved ≥4y → cancelled) | `ShelvedCancelledType=Presumed` force-added; **no ref by design** (an inference has no URL — standing rule 2) |
| `unclear` | genuinely undeterminable; notes say what was tried | — |

Class-out mapping: `CONFIRMED` / `CHANGE_PROPOSED` / `STALE` / `UNRESOLVED`. The
`<Cmdty>_StatusReview` tab leads the workbook when present — it is what researchers act
on first. Full record schema: `docs/reference/staged_json_schema.md`.

## Discovery leg

`build_discovery_context.py` (full-roster dedup context, ALL statuses) → the
`country-discovery` workflow (strategy fan-out → consolidate/match-to-existing → one
vetting agent per survivor, add-threshold enforced) → `merge_discovery_shards.py`
(merge-time QC: blocklist strip, no orphan values/refs, refless new_row → monitor) →
`build_discovery_workbook.py`. Rules of the Discovery SOP apply unchanged — reference-only
candidates match to existing rows first; below-threshold → monitor list; >5 candidate
clusters in one country → escalate before mass-producing rows.

## Sequencing the campaign

1. **Pilot** one mid-size country end-to-end (Iraq-sized, ~15–25 in-dev rows) and review
   the packet before scaling.
2. **Long tail** — the ~60 countries with ≤3 in-dev rows batch several-per-run.
3. **China / US / Russia** (over half of all in-dev rows) need sub-country chunking
   (province/state scopes via a filtered worklist) and in-country-language search.

## Escalation gates (campaign-specific, on top of the standing ones)

- **>30% of a country's in-dev rows get `change`/`stale` verdicts** → present before
  building the packet (possible systematic staleness, or a schema misread).
- Discovery: the standing >5-clusters gate; also a `maps` strategy that surfaces a whole
  missing network class (e.g. a national grid GEM never covered) → scope discussion, not
  row-by-row adds.
- The ref-sweep gates (Unresolved fraction, harvester hit-rate) apply to the in-dev leg.

## Operating refresh (planned follow-on — do not run yet)

Same fan-out machinery, cheaper contract: per-row **event scan only** (status-changing
events since last update: shutdown, idle, retirement, expansion, ownership change,
incidents) + ref re-verification only for rows where `--verify-existing` flags dead URLs.
No deep-fill, no full ≥2-corroboration re-derivation of every field. To be specified as a
`--tier operating-refresh` variant after the in-dev leg has run in a few countries.

## Gotchas (seeding the ref baseline)

Annual mode runs no separate ref-sweep pass, so the merge needs a **ref baseline** to preserve
records onto: `seed_resolutions_from_worklist.py` converts worklist ref units into the initial
`staged_resolutions.json`.
- **Commodity is inferred from the snapshot filename** ("gas"/"ggit" → gas) into `meta.commodity`,
  so `build_ref_workbook.py` prefixes tabs correctly. Without it, a gas packet mislabels tabs
  `Oil_`.
- **Re-seeding requires deleting the stale `staged_resolutions.prior.json`** first — the merge
  snapshots the baseline to `.prior.json` on first run, and a stale snapshot (e.g. one captured
  with an empty commodity) will be re-applied and re-break the tab prefix.
- On resume, retrying only the failed workflow agents on a stronger model works because changing
  an agent's `opts` (e.g. `model: 'opus'`) busts *that* agent's cache while completed agents
  replay from cache untouched.

## Hand-off contract (data-ops)

`staged_resolutions.json` and `staged_new.json` are the machine-readable outputs; their
schemas are documented in `docs/reference/staged_json_schema.md`. Any apply-side tooling
(e.g. the goig-ggit-data-ops repo) should build against that document — treat it as the
interface; version-note any field changes there.
