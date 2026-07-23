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

The pluggable diff engine. `<source>` is any folder under `sources/` (GulfPub
today). See the Reconciliation SOP for phase detail.

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
| `gulfpub` | GulfPub/PE World Map crosswalk tab from a scoped §2 recon |

**Presets:**
- **`in-dev`** = status-review + refs + validity, scope
  `--status proposed,construction,shelved` (the annual packet's leg A) →
  `…_annual-indev.xlsx`.
- **`deep`** = refs + fills + validity + routes + gulfpub, any statuses —
  **operating rows are a prime target** (duplicate/existence hunting) →
  `…_deepsweep.xlsx`.
- **`refs-only`** = refs alone → `…_refsweep.xlsx`.

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
python scripts/merge_deepsweep_shards.py --staging $STG/  # re-fold validity/fills/status
```

The `routes` leg is carried on the shards automatically (`routes[]` →
`__ROUTE__` at merge). The `gulfpub` leg: run the scoped §2 recon, then

```bash
python scripts/build_gulfpub_crosswalk.py --match-diff <recon>/match_diff.json \
  --out $STG/gulfpub_crosswalk.json     # build_ref_workbook adds <Cmdty>_GulfPub when present
```

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

---

**Workflow-launch gotcha (learned on the Iraq pilot, 2026-07):** invoking a saved
workflow by *name* can (a) deliver `args` to the script as a JSON-encoded *string* and
(b) serve a **stale cached copy** of the script that predates same-session edits. The
reliable launch path: bake the builder's JSON directly into a copy of the script
(replace the `const A = …` args line with `const A = <the JSON object>`), `node --check`
it, and launch with `Workflow({ scriptPath: <the copy> })`. Both workflow scripts also
keep the string-tolerant `const A = (typeof args === 'string') ? JSON.parse(args) : …`
guard for the by-name path.
