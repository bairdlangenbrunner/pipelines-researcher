# Workflow recipes

Step-by-step command sequences for the workflows routed from `CLAUDE.md`. The
research methodology (`docs/GOIT_Pipeline_Research_Workflow.md`) is authoritative
for *what* to research; the SOPs (`docs/sops/`) are the operational rules; this file
is the glue — which commands, in which order. Read the section for the workflow
you're running, plus its SOP.

**Fresh-pull shorthand:** `./scripts/refresh_csvs.sh` → dated GOIT + GGIT +
operators/owners snapshots in `data/` (tracker tabs `header=2`, operators/owners tab
`header=1`). Re-derive the column→index map each run; the schema drifts.

**How they fit together:** Triage (§1) writes a memo picking the next batch. Four
research engines stage findings as JSON, one run dir per mode under the scope's
`batches/<scope>/staging/`:
Reconcile (§2), **Country Sweep** (§3 — THE research engine, legs selected per run),
Discovery (§4), Update (§5 — small targeted fixes). The **Handoff Packet** (§6)
assembles *everything currently staged* for a country+commodity — plus its own
wiki-alignment / route-integrity / mechanical-QC legs — into an actions workbook
the researcher works from + an evidence workbook (audit trail). The Annual packet
(§7) is a *recipe*: Sweep `in-dev` preset + Discovery + Handoff. **Route creation**
(§8) stages candidate route *geometry* (`ROUTE_CANDIDATE` `<PID>.geojson` files) that
§6 auto-carries — the one workflow whose deliverable targets the routes repo, not the
sheet.

**Staged JSON is the canonical pending-state.** Every staging run dir MUST write a
store file (`staged_resolutions.json` / `staged_new.json` / `staged_updates.json`)
whose `meta.scope.country` + commodity make it auto-discoverable
(`staged_store.discover_staging_dirs`) — a storeless dir is invisible to every
downstream assembly. Narrative counts in country notes / CLAUDE.md are regenerated
with `scripts/staged_summary.py`, never hand-maintained.

**Batch artifacts — scope-first layout.** Everything for one country+commodity
lives under `batches/<country-slug>-<commodity>/` (e.g. `batches/egypt-gas/`):

- `staging/<mode[-qualifier]>/` — one dir per run: `annual`, `ref-sweep-operating`,
  `discovery`, `update-<topic>`, `qc`, `route-creation[-<qualifier>]`, …
  Reconciliation inputs are `staging/recon-<source>-<date>/` (no store file —
  deliberately invisible to discovery; route scripts scan them separately).
- `deliverables/` — current workbooks:
  `pipelines_batch_<YYYYMMDD>_<HHMM>_ET[_<scope>]_<mode>.xlsx`
  (stamp via `TZ=America/New_York date "+%Y%m%d_%H%M_ET"`; never overwrite).
- `archive/` — lifecycle is by MOVE: when a batch is applied to the sheet or a
  workbook is superseded by a regeneration, move the staging dir / old xlsx here.
  Anything still in `staging/`+`deliverables/` is live pending work, by definition.

`batches/INDEX.md` is the whole-tree lookup — regenerate it with
`python scripts/staged_summary.py --index` after adding/moving anything; never
hand-edit it.

---

## §1 Triage (memo)

1. Fresh pull. 2. Gap analysis (methodology Phase 1) + staleness flags + recon
backlog + `python scripts/staged_summary.py --all` (what's already staged and
awaiting application — don't re-research it). 3. Write
`notes/triage-<YYYY-MM-DD>.md` with options (workflow + scope + sweep legs).
Present; **stop and ask** before spinning up any batch. Detail: Triage SOP.

---

## §2 Reconcile against a scraped dataset

The pluggable diff engine. `<source>` is any folder under `sources/` — `gulfpub`
(tier 2, global) and `osm` (tier 3, per-country Overpass pulls that must be **fetched
before** the run) today. See the Reconciliation SOP for phase detail.

1. Confirm parameters (SOP §1): `--source`, `--commodity oil|gas|both`, `--country`,
   lifecycle states, geometry pass on (default). Note the source's `scraped_date`.
2. Fresh pull (shorthand).
3. **Ingest** the reference → canonical records:
   ```bash
   python scripts/ingest.py --source gulfpub --commodity both \
     --out batches/saudi-arabia-oil/staging/recon-gulfpub-<DATE>/
   ```
   Reads `sources/gulfpub/manifest.yml` (+ `adapter.py` if present). Spot-check 5
   records vs the raw GeoJSON (status mapped, diameter set, length→km, geodesic
   computed, geometry sidecar present).
   **If `geodesic_km ÷ length_km` sits near 1.609 on those records, stop — the manifest's
   `length_units` is wrong.** Confirm it dataset-wide *and per country* before continuing
   (one country's block can differ: `units.length_units_by_country`), fix the manifest, and
   re-run. That is a manifest fix plus a re-run, not an escalation — and re-run every other
   country already shipped off the same dataset, because their `Ref Length` columns are wrong
   too. `notes/escalation-2026-07-29-gulfpub-gas-length-miles.md`.
4. **Reconcile** (match + geometry + diff + score):
   ```bash
   python scripts/reconcile.py --source gulfpub --country "Saudi Arabia" \
     --commodity both --gem-oil data/GOIT_oil_ngl_snapshot_<DATE>.csv \
     --gem-gas data/GGIT_gas_snapshot_<DATE>.csv \
     --staging batches/saudi-arabia-oil/staging/recon-gulfpub-<DATE>/
   ```
   → `match_diff.json` + `route_metrics.json`. Pulls GEM routes from the local
   mirror (else `fetch_route.sh`) for geometry signals.
5. **Route findings (SOP §4):** Additions → Discovery (match-to-existing FIRST);
   value/status disagreements → Update; GEM-only → log. **Do not auto-apply.**
   Author `staged_*.json` resolutions in the run folder as you review.
6. **Build:**
   ```bash
   python scripts/build_recon_workbook.py \
     --staging batches/saudi-arabia-oil/staging/recon-gulfpub-<DATE>/ \
     --output batches/saudi-arabia-oil/deliverables/pipelines_batch_<stamp>_gulfpub-saudi-arabia_reconciliation.xlsx
   python scripts/recalc.py batches/saudi-arabia-oil/deliverables/pipelines_batch_<stamp>_gulfpub-saudi-arabia_reconciliation.xlsx
   ```
   Then present. **Adding a new dataset later = a new `sources/<name>/` manifest;
   the §2 commands are unchanged** (`--source <name>`). A crosswalk against a sweep
   is the `gulfpub` leg of §3, built from this section's `match_diff.json`.

---

## §3 Country Sweep (the research engine)

One scoped pass over **existing rows** (country + commodity + status filter) with
**selectable legs**, staging everything into ONE dir per scope
(`staged_resolutions.json`). Detail: Sweep SOP (`docs/sops/sweep.md`).

| Leg | What it stages |
|---|---|
| `refs` | fill blank `[ref]`s + re-verify filled ones to the ≥2-independent target (`REFS_ADDED`/`REVERIFIED`/`DEAD_LINK`/`UNRESOLVED`; incl. operators/owners-tab units) |
| `fills` | research blank *value* fields, paired verified ref required (`class_in="FILL"`) |
| `validity` | skeptical existence / duplicate / classification / attribution / spec check (`__VALIDITY__`, read-and-flag) |
| `status-review` | per-segment-row status verdict confirm/change/stale/unclear (`__STATUS__`) |
| `routes` | corridor + sourced-endpoint route suggestions for weak `RouteAccuracy` (`__ROUTE__`; candidates for a human routes-repo PR) |
| `recon` | one crosswalk tab per registered reference dataset (`gulfpub`, `osm`, …) from a scoped §2 recon. Formerly the `gulfpub` leg — that name still works, but it means "GulfPub only" |

**Presets:**
- **`in-dev`** = status-review + refs + validity, scope
  `--status proposed,construction,shelved` (the annual packet's leg A) →
  `…_annual-indev.xlsx`.
- **`deep`** = refs + fills + validity + routes + recon (**gulfpub AND osm** — both
  run by default; see §3's recon-leg block), any statuses — **operating rows are a
  prime target** (duplicate/existence hunting) → `…_deepsweep.xlsx`.
- **`refs-only`** = refs alone → `…_refsweep.xlsx`.

**Two follow-on passes the `validity` leg keeps generating** (own run dirs, same scope,
read-and-flag only; rules + how to build each: Sweep SOP §"Two follow-on passes"):
`staging/redundancy/` resolves the row-by-row *pairwise* duplicate flags into
**cluster-level** `__VALIDITY__` rulings (per-batch one-off `build_redundancy.py` — copy
the Libya or Iraq script), and `staging/cancelled-review/` sweeps the `cancelled` rows
that fall through both the operating sweep and the `in-dev` status filter.

### Common first steps (all presets)

```bash
STG=batches/<scope>/staging/<run>      # e.g. batches/egypt-gas/staging/ref-sweep-operating, batches/egypt-gas/staging/annual
python scripts/build_ref_worklist.py --tracker gas --country "<Country>" \
  [--status proposed,construction,shelved] --verify-existing --out $STG/worklist.json
python scripts/harvest_wiki_citations.py --worklist $STG/worklist.json \
  --out $STG/wiki_citations.json
```

The worklist joins the **operators/owners tab** (GID 1489950650, ProjectID-keyed)
and emits `Operator [ref]`/`Owner [ref]` units; `--verify-existing` HTTP-checks
existing refs deterministically (no agent tokens). Route/geometry `[ref]` cells are
**out of scope** (dropped by `discover_ref_pairs`). Start research from the
harvested gem.wiki outbound citations — visit gem.wiki, **never cite it**.

### refs-only preset (inline research loop)

Research per ProjectID (Sweep SOP §Sequence-4): rank harvested candidates, verify
each with `url_verifier` (pass `name=`; search in-country languages), reach ≥2
independent working sources, assign tier; stage one resolution per unit into
`$STG/staged_resolutions.json`. **Never auto-apply; no fabricated URLs.**

### deep / in-dev presets (subagent fan-out via `critical-deep-sweep`)

```bash
python scripts/build_deepsweep_args.py --staging $STG/ [--status-review]  # JSON → Workflow args
#   --status-review = the in-dev preset (subagents also stage per-row __STATUS__ verdicts)
#   → Workflow({ name: 'critical-deep-sweep', args: <the JSON> })
#     one skeptical subagent per PID writes $STG/rows/<PID>.json
# in-dev preset only (no separate refs research pass) — seed the ref baseline the
# merge preserves onto (HAS_REF/MISSING_REF + link-rot flags from the worklist):
python scripts/seed_resolutions_from_worklist.py --staging $STG/
python scripts/merge_deepsweep_shards.py --staging $STG/
```

Optional **ref-gap pass** (the seed leaves blank/dead-link refs red because the
in-dev preset does no ref hunting; to fill those cells to the ≥2-independent target
in the SAME workbook):

```bash
python scripts/build_refsweep_briefs.py --staging $STG/   # → ref_shards/_briefs/<PID>.json
#   → one research subagent per brief writes ref_shards/<PID>.json
python scripts/merge_ref_shards.py --staging $STG/        # fold onto staged_resolutions.prior.json
python scripts/harvest_sentinel_findings.py --staging $STG/  # REQUIRED if that printed a WARN
python scripts/merge_deepsweep_shards.py --staging $STG/  # re-fold validity/fills/status
```

`merge_ref_shards.py` matches shards by `(project_id, ref_col, sheet_row)`, so any
`__VALIDITY__`/`__REDUNDANCY__` sentinel a research subagent wrote has no baseline record
and is **dropped with a WARN** — the refs land, the sourced verdict vanishes.
`harvest_sentinel_findings.py` folds them back in (idempotent). Never ship a batch whose
WARN count you haven't reconciled (Sweep SOP §Sentinels).

The `routes` leg is carried on the shards automatically (`routes[]` →
`__ROUTE__` at merge). The `recon` leg runs **once per reference dataset** — in the
`deep` preset that is **both `gulfpub` and `osm`**, not GulfPub alone. OSM needs a
per-country Overpass pull first (see `sources/osm/NOTES.md`); GulfPub is a global
extract already on disk.

```bash
# OSM only: fetch the country+substance extract, then register it in sources/osm/manifest.yml
python scripts/fetch_overpass.py --iso IQ --substance gas --include-lifecycle \
  --out sources/osm/data/ --name osm-iq-gas          # --iso, NOT --area; lifecycle REQUIRED

for SRC in gulfpub osm; do
  R=batches/<scope>/staging/recon-$SRC-<DATE>
  python scripts/ingest.py --source $SRC --commodity gas --country "<Country>" --out $R/
  python scripts/reconcile.py --source $SRC --country "<Country>" --commodity gas --staging $R/
  python scripts/build_recon_crosswalk.py --match-diff $R/match_diff.json --sweep-dir $STG/
done
# → $STG/recon_<source>_crosswalk.json; build_ref_workbook globs them and emits one
#   <Cmdty>_<Source> tab each. Adding a source needs no workbook edit.
```

**Read the run's health line before trusting a thin result.** `reconcile.py` emits a
`MATCH_QUALITY` escalation when the name and geometry axes are both mostly dead
(unnamed reference features × routeless GEM rows), which is the normal OSM condition —
Iraq gas 2026-07-28 scored 0 overlaps from 52 features with a top composite of 0.438
against a 0.45 threshold, and that null read as a legitimate finding for weeks. The fix
is the admin-area signal (`geoarea_weight`, per-dataset in the manifest), not a lower
threshold.

**Triage by `Disposition`, not by matched/unmatched.** A reference route is
presumptively REAL pipe: `ROUTE_FOR_EXISTING` = candidate geometry for a routeless GEM
row (human routes-repo PR; never auto-replaced), `FRAGMENT_OF_EXISTING` = partial trace
of a tracked line, `NEAR_MISS` = adjudicate by hand, `DISCOVERY_CANDIDATE` = check for an
existing row under another name (→ `OtherEnglishNames`) *before* treating it as new. A
`partial` Coverage label means the trace corroborates LOCATION only — a 0.1 km OSM stub
is not evidence about a 105 km line. Check the tab's License column before any OSM
geometry is reused (ODbL share-alike; Baird's call).

### Build (all presets)

```bash
python scripts/build_ref_workbook.py --staging $STG/ \
  --output batches/<scope>/deliverables/pipelines_batch_<stamp>_<scope>_<preset-mode>.xlsx
python scripts/recalc.py batches/<scope>/deliverables/pipelines_batch_<stamp>_<scope>_<preset-mode>.xlsx
```

Leads with the paste-ready **`<Cmdty>_Backend`** tab (1:1 mirror of the FULL
tracker backend — every column in sheet order, current values prefilled, overlays
tier-colored only on touched cells, leading `SheetRow` locator; **don't paste the
computed/formula columns back over the live formulas**) and
**`<Cmdty>_OperatorsOwners`** (mirror of the operators/owners tab, `[ref]` precedes
its values). In-dev preset leads with `<Cmdty>_StatusReview`. Residual red cells =
no independent source supports the current GEM value (often a value disagreement),
not merely unsearched. Present standalone, or roll into a §6 handoff packet.

---

## §4 Discover new pipelines

Find projects **not** in GOIT/GGIT → `staged_new.json`. Detail: Discovery SOP.
Reconciliation Additions feed here — **match-to-existing first**.

```bash
STG=batches/<scope>/staging/<run>      # may share the annual dir (e.g. batches/egypt-gas/staging/annual)
python scripts/build_discovery_context.py --tracker gas --country "<Country>" --staging $STG/
#   → Workflow({ name: 'country-discovery', args: <the printed JSON> })
#     (strategy fan-out → consolidate/match-to-existing → one vetting agent per candidate)
python scripts/merge_discovery_shards.py --staging $STG/
python scripts/build_discovery_workbook.py --staging $STG/ \
  --output batches/<scope>/deliverables/pipelines_batch_<stamp>_<scope>_discovery.xlsx
python scripts/recalc.py batches/<scope>/deliverables/pipelines_batch_<stamp>_<scope>_discovery.xlsx
```

Apply the add-threshold (sponsor + geography + concrete step); below → `monitor`.
`url_verifier.py` every URL; `entity_lookup.py` every new owner. New rows render
green on `<Cmdty>_NewRows`; >5 candidate clusters in one country → escalate first.

---

## §5 Update (targeted fixes)

Small, specific batches: named rows, recon value-disagreements, fixes detected by a
handoff packet. (Whole-country "re-verify everything" work is a §3 sweep, not an
Update.) 1. Fresh pull. 2. Confirm scope (Update SOP). 3. Research per methodology
Phase 2 → stage `batches/<scope>/staging/<run>/staged_updates.json` (its `meta`
must carry the scope country + tracker so discovery finds it). 4.
`url_verifier.py` every URL; `entity_lookup.py` every new owner. 5. Build
`…_<scope>_update.xlsx` (changed cells red); `recalc.py`; present.

---

## §6 Handoff packet (assembly + delivery)

**THE researcher deliverable** for a country+commodity: three QC legs of its own
(wiki alignment, route integrity, mechanical checks) PLUS an assembly of **every
pending staged action** from the scope's prior staging dirs (auto-discovered) —
concerns, status changes, fills, ref work, route suggestions, discovery candidates —
each with `Source packet` provenance, into TWO workbooks: `…_handoff-actions.xlsx`
(only suggested changes + open issues, tab order = work order) and
`…_handoff-evidence.xlsx` (the audit trail — confirmed/known-staged/info rows live
ONLY here). Nothing staged stays buried in an earlier per-leg workbook. Detail:
QC/Handoff SOP (`docs/sops/qc.md`); sidecar contract:
`docs/reference/staged_json_schema.md`.

1. Fresh pull (both the tracker tab and the operators/owners tab).
2. **Leg 1 — wiki alignment** (fetches pages politely, caches to `<staging>/wiki_html/`):
   ```bash
   python scripts/wiki_alignment.py --csv data/GGIT_gas_snapshot_<date>.csv \
     --owners-csv data/GEM_operators_owners_snapshot_<date>.csv \
     --country Egypt --commodity gas --staging batches/egypt-gas/staging/qc/
   ```
3. **Leg 2 — route integrity** (offline; needs `data/boundaries/ne_50m_admin_0_countries.shp`
   + the routes-repo mirror; run from the repo root):
   ```bash
   python scripts/route_integrity.py --csv data/GGIT_gas_snapshot_<date>.csv \
     --country Egypt --commodity gas --staging batches/egypt-gas/staging/qc/
   ```
4. **Assemble** (mechanical checks incl. the `Existence_support` ref-thinness check
   + the `staged_actions.json` full-ingestion sidecar + combined staged JSON +
   Leg-3 worklist). Prior staging dirs are **auto-discovered** by country+commodity
   (`--staged-dir` overrides; assembled packets are never re-imported):
   ```bash
   python scripts/build_qc_staging.py --csv data/GGIT_gas_snapshot_<date>.csv \
     --country Egypt --commodity gas --staging batches/egypt-gas/staging/qc/
   ```
   Re-running after the Leg-3 merge (step 5): add `--sidecars-only`, or the merged
   validity/fills get clobbered (the script guards, but be deliberate). If the
   country has NO prior sweep validity pass, every Leg-3 brief must add the
   existence check for its row (SOP escalation rule).
5. **Leg 3 — targeted research fan-out** on `worklist.json` rows (bake a one-off
   workflow from the packet's research script; one subagent per flagged row
   resolves the SPECIFIC flagged disagreement, ≥2 independent sources, every URL
   through `url_verifier`). Then:
   ```bash
   python scripts/merge_deepsweep_shards.py --staging batches/egypt-gas/staging/qc/
   python scripts/build_qc_staging.py … --sidecars-only     # refresh the sidecars
   ```
6. **Build** (two files derived from `--output`: `…-actions.xlsx` — tab order =
   work order, `<Cmdty>_Decisions` read FIRST — and `…-evidence.xlsx`, the audit
   trail):
   ```bash
   python scripts/build_ref_workbook.py --staging batches/egypt-gas/staging/qc/ \
     --output batches/egypt-gas/deliverables/pipelines_batch_<stamp>_egypt-gas_handoff.xlsx
   python scripts/recalc.py batches/egypt-gas/deliverables/pipelines_batch_<stamp>_egypt-gas_handoff-actions.xlsx
   python scripts/recalc.py batches/egypt-gas/deliverables/pipelines_batch_<stamp>_egypt-gas_handoff-evidence.xlsx
   python scripts/staged_summary.py --country Egypt --commodity gas   # drift check vs docs
   ```
   gem.wiki is VISITED for the diff but NEVER cited as a source. No GulfPub route
   comparison in this pass (future work; see `docs/research_backlog.md`).

   **Class-level escalations → `<staging>/escalations.json`** (optional). Anything no
   single row action can carry — a whole class of wrong values, an ingest defect, a
   scope ruling — goes in a `notes/escalation-*.md` memo AND a one-line entry here
   (`[{title, summary, memo}]`), which `build_ref_workbook` renders as an
   `ESCALATIONS` row in both READMEs. Without it the researcher working from the
   workbook never learns the memo exists. Say in the summary which affected rows are
   staged as fills and which are memo-only — that gap is the thing that gets lost.

**Tracker-wide mechanical QC workbook** (global audits, no assembly):
`python scripts/build_qc_workbook.py --tracker oil [--country <C>] --output
batches/<scope>/deliverables/pipelines_batch_<stamp>_<scope>_qc.xlsx` — one sheet at a time for large
scopes (sheet list: QC/Handoff SOP; route/WKT sheet permanently dropped);
`recalc.py`; route fixes to a follow-on §5 Update. **QC detects; Update fixes.**

---

## §7 Annual country update packet (campaign recipe)

Per country: **Country Sweep `in-dev` preset (§3) + Discovery (§4) + Handoff
Packet (§6)**, sharing the annual staging dir for the first two. Rules, verdict
vocabulary, escalation gates: Annual Update SOP (`docs/sops/annual_update.md`).

```bash
# once per campaign (re-run anytime; manual tracking columns survive):
python scripts/build_campaign_roster.py --tracker gas --campaign ggit-2026
#   → campaigns/ggit-2026/roster.csv (pick the next country; track phase status there)

# per country:
#   A) §3 Country Sweep, in-dev preset  → …_annual-indev.xlsx
#   B) §4 Discovery, same staging dir   → …_discovery.xlsx
#   C) §6 Handoff packet                → …_handoff-actions.xlsx + …_handoff-evidence.xlsx
#                                          ← the researcher works from the ACTIONS file
```

Update the campaign roster row; stop at the SOP's escalation gates (>30% status
changes; >5 discovery clusters; a whole missing network class).

---

## §8 Route creation (candidate geometry)

Produces candidate route **geometry** (a routes-repo-valid `<PID>.geojson`) for a
single PID or every weak-`RouteAccuracy` row in a country, by walking a source ladder
(GulfPub sidecar → public GIS/OSM → agent digitization → endpoints great-circle) and
staging it for a **human branch+PR** against `GOIT-GGIT-pipeline-routes`. The agent
never writes the routes repo or the sheet; no coordinate is ever fabricated. Consumes
(does not duplicate) the sweep `routes` leg's corridor/endpoint suggestions. Rules,
rung logic, GCP/RMSE thresholds, packet contents, escalation gates: Route Creation SOP
(`docs/sops/route_creation.md`).

1. Fresh pull, then build the worklist (group by ProjectID; gather existing-route km,
   prior `__ROUTE__` suggestions, GulfPub sidecar hits, facility anchors):
   ```bash
   python scripts/build_route_worklist.py --csv data/GGIT_gas_snapshot_<date>.csv \
     --country Egypt --commodity gas --staging batches/egypt-gas/staging/route-creation/ \
     [--include-medium] [--pids P0436,P3935]
   ```
2. **Agent map/portal research** (non-script, rungs 2–3): find the best public GIS
   layer / published map. **Every URL through `scripts/url_verifier.py`** (GEM URLs
   rejected); new endpoints get a `sources/gis_endpoints.yml` entry + a roster line.
3. Fetch or trace per rung (raw layers land in `fetched_layers/` with `.meta.json`):
   ```bash
   # both fetchers take a DIRECTORY --out + a --name basename → <name>.geojson + <name>.meta.json
   python scripts/fetch_arcgis.py --source rrc_pipelines --bbox <minlon,minlat,maxlon,maxlat> \
     --out batches/egypt-gas/staging/route-creation/fetched_layers/ --name rrc
   python scripts/fetch_overpass.py --area Egypt --substance gas \
     --out batches/egypt-gas/staging/route-creation/fetched_layers/ --name osm_eg   # ODbL flagged
   python scripts/georef.py --gcps gcps.json --trace trace.json --order 1 \
     --max-rmse-km 10 --out .../fetched_layers/P1234_traced.geojson --report .../P1234_georef.json
   ```
4. Assemble one candidate per PID per method (writes the geojson, runs the gate,
   frames replacement + `geometry_signals`, upserts the `ROUTE_CANDIDATE` record):
   ```bash
   python scripts/build_route_candidate.py --pid P3935 --commodity gas \
     --staging batches/egypt-gas/staging/route-creation/ --method sidecar \
     --ref-id gulfpub:gas:20005 --replace
   # rungs: --method gis|osm --geom <fetched.geojson> [--feature-index N|--where-prop K=V]
   #        --method traced --geom <P1234_traced.geojson>
   #        --method endpoints --start <lon,lat> --end <lon,lat> --start-name … --start-ref … --end-ref …
   ```
5. Re-validate (optional) + build the workbook + recalc:
   ```bash
   python scripts/validate_route_candidate.py \
     --candidates batches/egypt-gas/staging/route-creation/candidates.json    # exit = # FAILs
   python scripts/build_ref_workbook.py --staging batches/egypt-gas/staging/route-creation/ \
     --output batches/egypt-gas/deliverables/pipelines_batch_<stamp>_egypt-gas_route-creation.xlsx
   python scripts/recalc.py batches/egypt-gas/deliverables/pipelines_batch_<stamp>_egypt-gas_route-creation.xlsx
   ```

Deliverables: `candidate_routes/<PID>.geojson` (committed) + digitization
`packets/<PID>/` (when RMSE fails) + the `<Cmdty>_RouteCandidates` workbook tab.
Because `meta.mode="route-creation"` and `meta.scope` carry country+commodity, a later
§6 handoff **auto-carries** these `ROUTE_CANDIDATE` records untouched. Refresh the
facility gazetteer (`scripts/refresh_facility_gazetteer.py`) when the GOGET/GOGPT
snapshots in `data/` are stale.

6. **Apply (ONLY on explicit per-batch authorization from Baird — approval never
   carries over; default remains staged-for-human-PR).** Two halves, in order,
   established on the Egypt gas batch 2026-07-30 (merges `0c8c01f4`/`241ef5aa`):

   a. **Routes repo** — gate through ITS OWN QC, branch, merge, push:
   ```bash
   cd ../GOIT-GGIT-pipeline-routes
   python scripts/qc_routes.py <candidate_routes/P####.geojson …>          # REPORT first
   git checkout -b <scope>-routes-<date>
   python scripts/qc_routes.py <targets…> --copy --include <WARN PIDs>    # targets BEFORE flags
   python scripts/validate_geojson.py <copied files…>                     # CI check locally
   git add … && git commit && git checkout main && git merge --no-ff <branch> && git push origin main
   ```
   FAILs are never copied; WARNs need an explicit `--include` (straight-line
   endpoints candidates always undershoot routed length — expected WARNs).

   b. **Sheet route columns** — `scripts/apply_route_candidates.py` (plan phase →
   review → `--apply`). Pull a FRESH snapshot first; the script derives column
   letters from the header, appends (never overwrites) RouteNotes (CB stamp + " — "
   + researcher notes) / RouteCreator `CB` (gas tab only) / Route [ref] URLs, sets
   RouteAccuracy from the staged suggestion (current cell must be `no route`), and
   enforces the full authorized-write protocol: FORMULA pre-check, ProjectID match,
   double-append guard, `notes/` backup CSV (commit it), RAW cell-scoped writes via
   `gws-gem-write`, exact readback verification.
   ```bash
   ./scripts/refresh_csvs.sh
   python scripts/apply_route_candidates.py --staging batches/<scope>/staging/route-creation \
     --commodity gas --csv data/GGIT_gas_snapshot_<date>.csv --scope-slug <scope> \
     [--pids P8013,P8014,P8021]          # plan; then re-run with --apply
   ```
   Then update the country note + CLAUDE.md pending bullet, regenerate
   `batches/INDEX.md`, and commit.

7. **Partials retry (optional, later).** ROUTE_PARTIAL rows are worth ONE re-research
   pass once the original blocker (usually web-search quota) clears: build per-PID
   retry payloads seeding each agent with the prior findings/blockers, fan out
   geographically-grouped subagents, then assemble resolved PIDs via
   `build_route_candidate.py --method endpoints` and refresh the still-unresolved
   ROUTE_PARTIAL records in place. Exemplars from the Egypt gas retry (3/18 resolved):
   `batches/egypt-gas/staging/route-creation/{retry_payload_*,retry_results_*,assemble_retry_candidates.py}`.
   Cross-read the results before assembling — one group's source can resolve another
   group's PID (the P8021 World Bank ICR also named P8014's Zafarana–Kureimat line).

---

## §9 Full country pass (composite recipe)

"**Full pass on `<country>`**" is not one sweep — it is the whole-country recipe below,
run identically for Libya gas and Iraq gas (both 2026-07-28) and now the de facto
deepest workflow. Each numbered step is its **own run dir** under
`batches/<scope>/staging/`, so each stays separately reviewable and the §6 packet
auto-discovers all of them. Order matters only where noted.

| # | Step | Run dir | Recipe |
|---|---|---|---|
| 1 | Sweep, `deep` preset, **operating** rows | `ref-sweep-operating/` | §3 |
| 2 | Sweep, `in-dev` preset | `annual/` | §3 + §7 |
| 3 | Cancelled/shelved review | `cancelled-review/` | §3 + Sweep SOP |
| 4 | Redundancy-cluster adjudication (**after** 1–3) | `redundancy/` | §3 + Sweep SOP |
| 5 | Reconcile every registered source | `recon-<source>-<date>/` | §2 |
| 6 | Handoff packet (wiki · route · mechanical · Leg-3) | `qc/` | §6 |
| 7 | Ref-gap re-pass, if step 1–3 left red cells | `ref-gap-repass/` | §3 |

Notes that cost real work to learn:

- **Steps 1–3 detect; step 4 adjudicates.** Don't try to resolve duplicate flags inside
  the row-by-row legs — the decision unit is the cluster, and pairwise rulings contradict
  each other. Step 4 is also where you *retract* your own flags (Iraq: 12 of 16 withdrawn).
- **A class defect needs its own staging dir, not just a memo.** When a finding spans N
  rows (the ASB length units → `iraq-gas/staging/asb-length-units/`, 19 `__VALIDITY__`
  records), stage a per-row record targeting the **editable** cell so the packet actually
  carries the work. A memo alone reaches nobody — and state in it which affected rows are
  staged and which are memo-only (QC SOP §Escalate).
- **Run the recon step even when you expect a null result.** OSM found nothing for Libya
  but exposed three engine defects in `match.py` / `reconcile.py` / `route_compare.py`
  that affected *every* source.
- **A re-run supersedes; it does not append.** Both passes folded in and superseded
  earlier packets, and both produced **retractions** of earlier findings. Archive the
  superseded deliverables (lifecycle is by move) and write the retractions into the
  country note explicitly — a stale finding left standing is worse than no finding.
- Close with `staged_summary.py --country <C> --commodity <c>` + `--index`, and reconcile
  the country note, `docs/research_backlog.md` and CLAUDE.md's pending-items line.

---

**Workflow-launch gotcha (learned on the Iraq pilot, 2026-07):** invoking a saved
workflow by *name* can (a) deliver `args` to the script as a JSON-encoded *string* and
(b) serve a **stale cached copy** of the script that predates same-session edits. The
reliable launch path: bake the builder's JSON directly into a copy of the script
(replace the `const A = …` args line with `const A = <the JSON object>`), `node --check`
it, and launch with `Workflow({ scriptPath: <the copy> })`. Both workflow scripts also
keep the string-tolerant `const A = (typeof args === 'string') ? JSON.parse(args) : …`
guard for the by-name path.
