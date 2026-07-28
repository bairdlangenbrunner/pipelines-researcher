# SOP — QC & the handoff packet

Two jobs live here: the **mechanical-check library** (tracker-wide data-health
audits — **QC detects; Update fixes**) and the **handoff packet** (workflows.md §6),
the per-country deliverable that runs three QC legs of its own AND assembles every
pending staged action for the scope into a two-workbook split (actions + evidence).

## Mechanical checks (`scripts/build_qc_workbook.py`)

The tracker-wide QC workbook (one sheet per check) and the check library the
handoff assembler reuses country-scoped. Build **one sheet at a time** for large
scopes (token/review budget). Diameter and similar out-of-range checks are
**review flags, not auto-rejections**.

| Sheet | Checks |
|---|---|
| `Status` | values ∈ the locked `Status` vocab; status↔date consistency (operating⇒StartYear; cancelled⇒CancelledYear/presumed) |
| `RouteAccuracy` | values ∈ the locked ladder (incl. `very high (within meters)`) |
| `OtherVocab` | `PipelineType`, `DelayType`, `ShelvedCancelledType`, `FIDStatus`, `Delayed`, `Opposition` casing |
| `Owner_format` | structure sanity — but `--` is valid, and commas/&/slashes/`[NN.%]` inside Owner are legitimate (don't flag) |
| `WikiLink_health` | `Wiki` column links resolve |
| `Geo_consistency` | start/end country fields vs `CountriesOrAreas`; cross-border sanity |
| `Name_uniqueness` | duplicate `PipelineName`/`SegmentName` within a grouping |
| `Date_logic` | year ordering (ProposalYear ≤ ConstructionYear ≤ StartYear1) |
| `Diameter_OutOfRange` | parsed diameter set values outside plausible bounds (flag) |
| `BroadSweep_Misc` | orphan `[ref]` (filled ref / blank value or vice-versa), missing required fields |

**Permanently dropped:** the route/WKT-format sheet (old Sheet 10) — do not rebuild.

## Wiki-alignment (handoff Leg 1 — `scripts/wiki_alignment.py`)

Per-field diff of each row's gem.wiki page against the sheet (+ the operators/owners
tab for Operator). **The wiki is VISITED for the diff but NEVER cited as a source**
(standing rule 1) — the fetch is read-only, cached under `<staging>/wiki_html/`,
polite-interval, browser UA.

Parser: walks the "Project details" `<h2>` collecting `<li><b>Label:</b> value`
bullets; multi-segment pages (per-segment `<h3>` sections) merge — agreeing values
collapse, Diameter/Owner/Operator/Parent union across segments, disagreeing scalars
become info-only "ambiguous" records. Comparators are field-aware: Status lowercase,
Capacity via `capacity_to_bcmy` (a wiki range matches if the sheet value falls
inside), Length ±10% or ±2 km, Diameter/StartYear set-compare, Operator/Owner/Parent
entity-set compare (parentheticals + Co/Ltd/SA-style suffixes stripped). Sheet
sentinels (`--`, `unknown`, `n/a`, `tbd`) count as blank-with-intent → info severity.

`class_out` per record: **WIKI_UPDATE** (wiki lags the sheet → edit the wiki page),
**SHEET_SUSPECT** (the sheet side is the suspect — blank/sentinel sheet vs a filled
wiki, or a multi-segment union the single sheet row may under-carry → verify
independently, then fix the sheet), **WIKI_STALE_VS_STAGED** (the sheet cell already
has a staged pending correction — apply that packet first, then align the wiki),
**UNPARSED** (no Wiki URL / page didn't parse — review row, never silently skipped).
Page-internal status inconsistencies (intro vs Location vs details) are their own
records. SHEET_SUSPECT records carry a `staged_note` when a prior packet's concern
already covers the field — those never reach the Leg-3 research worklist.

## Route-integrity (handoff Leg 2 — `scripts/route_integrity.py`)

Checks each drawn GeoJSON route (mirror-first via `route_compare.load_gem_route`)
against **the row's own attributes** — this is route *correctness* QC and is NOT a
revival of the permanently-dropped WKT/route-format sheet (old Sheet 10), which
checked formatting. GulfPub route comparison is deliberately excluded (future work,
`docs/research_backlog.md`). Checks: `length_ratio` (geodesic vs
LengthKnownKm→LengthMergedKm, flag outside [0.75, 1.33]); `countries` (landfalls ≥2 km
via Natural Earth 1:50m admin-0 in `data/boundaries/`, must be ⊆ CountriesOrAreas ∪
start/end — offshore-lenient); `null_geometry` (both directions vs
`RouteAccuracy='no route'`); `degenerate` (≤2 vertices claiming medium+ accuracy);
`endpoint_country` (endpoint's land country ∈ {start, end country}). A route is
NEVER auto-replaced — fixes go via a human branch+PR against
`GOIT-GGIT-pipeline-routes`; a staged route suggestion annotates the flag
"known — staged" instead of re-flagging it for research.

## Assembly + Leg 3 (`scripts/build_qc_staging.py`)

Runs the ten mechanical checks country-scoped **plus the `Existence_support`
ref-thinness check** (≤1 distinct reference URL across a row's `[ref]` cells → the
whole entry may rest on a single source; verify the pipeline is real and worth
tracking at all — URL counting only, liveness stays the sweep's job), then:

- **Auto-discovers the scope's prior staging dirs** (`staged_store.discover_staging_dirs`,
  keyed on `meta.scope.country` + commodity; `--staged-dir` overrides; dirs with
  `meta.mode ∈ {qc, handoff}` are assembled packets and never re-imported).
- **Annotates every flag** against the staged context (keyed (ProjectID, column) —
  never sheet_row; row-level existence coverage via `existence_note()`: a staged
  existence/duplicate concern, or ANY prior validity verdict = already
  existence-audited).
- Writes **`staged_actions.json`** — the full-ingestion sidecar: ALL carried
  concerns (every type, not just existence/duplicate), pending status changes,
  corroborated fills, actionable ref work (REFS_ADDED/DEAD_LINK/UNRESOLVED;
  REVERIFIED counts-only), route suggestions, and discovery candidates — every
  record with `source_dir` provenance, `sheet_row` re-resolved against THIS
  packet's snapshot, and `also_flagged` cross-references onto this run's own
  wiki/mechanical flags. **Render input only, never an apply target** (apply from
  the source dirs' canonical files). Contract:
  `docs/reference/staged_json_schema.md`.
- Combines Legs 1+2 into `staged_resolutions.json` (`meta.mode: "handoff"`) and
  writes `worklist.json` — only rows whose flags question the SHEET (uncovered
  SHEET_SUSPECT diffs, hard route flags, geo/date/diameter/existence mechanical
  flags) go to the Leg-3 targeted-research fan-out; wiki-editing work stays in the
  workbook, and staged work is never re-researched.

Leg-3 subagents resolve the SPECIFIC flagged disagreement (≥2 independent sources,
`url_verifier`, in-country-language search where English is thin), shard to
`rows/<PID>.json`, merged by `merge_deepsweep_shards.py` (preserves the
WIKIDIFF/ROUTEQC records). Brief prompts must carry the Sweep SOP's "Verifier
false-negatives" rules (`docs/sops/sweep.md`) — esp. prose/equivalent-unit value
support ("6 BCM … annually" = 6 bcm/y) and never declaring an existing ref
unsupported off a substring miss without reading + quoting the passage.

**ESCALATION RULE:** if the country has no prior sweep validity pass (no staged
packet with `__VALIDITY__` records), every Leg-3 brief MUST include the existence
check — is this pipeline real, and should GEM track it? — not just the flagged field.

**After the Leg-3 merge, re-run the assembler ONLY with `--sidecars-only`** — a full
re-run would clobber the merged validity/fills in `staged_resolutions.json` (the
script's guard refuses, but don't rely on it).

## The handoff contract (full ingestion, two files)

The packet's promise to the researcher: **nothing staged for the scope stays buried
in an earlier deliverable — and nothing that needs no action clutters the work
order.** The deliverable is TWO workbooks (split adopted 2026-07-16):
`<stem>-actions.xlsx` holds only what to act on, tab order = work order
(`<Cmdty>_Decisions` — open concerns only, read FIRST — → StatusChanges →
AllFillsBackend, the one paste surface unifying fills + paste-ready ref work →
OperatorsOwners → discovery tabs → WikiUpdates → RouteSuggestions → OpenFlags);
`<stem>-evidence.xlsx` holds the audit trail (ConfirmedAudit, FillDetail,
RefWorkDetail, non-action wiki/route/flag context, MonitorList). Confirmed and
known-staged rows appear ONLY in the evidence file. After delivery, run
`python scripts/staged_summary.py --country <C> --commodity <c>` and reconcile the
country note — the summary output wins over any hand-written count. Workbook
layout: `docs/reference/workbook_conventions.md` §Handoff packet.

## Pre-delivery quality checklist (any doer batch)
1. **URL spot-check** — fetch 3–5 `[ref]` URLs; confirm they resolve and contain the claim.
2. **Expansion length** — every expansion: new pipe? if not, length 0 / diameter blank.
3. **Ownership consistency** — divestiture touched all affected rows.
4. **Status logic** — 2y→shelved, 4y→cancelled; `ShelvedCancelledType` set right.
5. **Date consistency** — operating⇒StartYear; cancelled⇒CancelledYear/presumed.
6. **ResearcherNotes** — every changed row explains what/why/caveats.
7. **No GEM self-citation** — no `[ref]` is a gem.wiki/globalenergymonitor URL.
8. **Corroboration** — confidence tier recorded; single-source flagged medium/low;
   "corroboration" isn't the same story republished or circling back to GEM.

## Escalate
>10% of a spot-check sample unsupported, or a whole class of values looks
systematically wrong → stop and discuss (schema misunderstanding, not a finding).

**Write it in two places, not one.** A `notes/escalation-<date>-<slug>.md` memo holds
the argument; a matching entry in `<staging>/escalations.json`
(`[{title, summary, memo}]`) puts it in the `ESCALATIONS` README row of both handoff
workbooks. The researcher works from the workbook and will not go looking in `notes/`.

Two things a class memo must state explicitly, because both were nearly lost on the
Libya ASB pass:
- **Which affected rows are staged as applicable actions and which exist only in the
  memo.** Rows found row-by-row before the pattern was visible become ordinary fills;
  rows found by pattern-matching afterwards are staged nowhere, and a row carrying no
  QC flag at all was never even looked at (P1859).
- **The proven scope, and the control that proves it.** "Tracker-wide" is a guess until
  tested. The Libya length defect looked tracker-wide and turned out Libya-only —
  Qatar's Dolphin row converts to its real 364 km, so the same ingest is *correct*
  elsewhere and a blanket fix would have introduced errors. Name the control row.
