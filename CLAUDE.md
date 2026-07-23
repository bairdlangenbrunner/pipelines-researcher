# Pipelines Researcher — operational guide

Backend scaffolding for an agentic research + reconciliation workflow that helps
maintain Global Energy Monitor's open-access pipeline databases:

- **GOIT** — Global Oil Infrastructure Tracker (crude oil + NGL pipelines, worldwide)
- **GGIT** — Global Gas Infrastructure Tracker (gas pipelines)

Deeper coverage in MENA, US, Iran, Iraq, Saudi Arabia. Researcher initials in the
tracker: **CB**. The agent **never writes to the live Google Sheet or the routes
repo** — every batch produces a reviewable Excel deliverable + staged JSON that
Baird applies manually.

Where things live — **read on demand as the workflow dictates, not all at once**:

- **Research methodology** (authoritative for *what* to research):
  `docs/GOIT_Pipeline_Research_Workflow.md` (the 4-phase deep-research workflow).
- **SOPs** (operational *how*): `docs/sops/` — `triage.md`, `reconciliation.md`
  (pluggable GEM↔dataset diff), `sweep.md` (Country Sweep — the research engine),
  `discovery.md`, `update.md` (targeted fixes), `qc.md` (QC + handoff packet),
  `annual_update.md` (campaign recipe).
- **Workflow recipes** (commands, in order): `docs/workflows.md`.
- **Reference**: `docs/reference/` — `gem_schema.md`, `controlled_vocab.md`,
  `confidence_tiers.md`, `workbook_conventions.md`, `route_conventions.md`,
  `source_roster.md`; plus `docs/country_notes/`.
- **Reference-dataset registry**: `sources/` — one `manifest.yml` (+ optional
  `adapter.py`) per scraped dataset; GulfPub today. How to add one: `sources/README.md`.
- **Scripts**: `scripts/` (engine + helpers).
- **Batches** (scope-first): `batches/<country-slug>-<commodity>/` holds
  `staging/<mode[-qualifier]>/` (staged JSON — the canonical pending-state; recon
  inputs are `staging/recon-<source>-<date>/`), `deliverables/` (current
  workbooks), `archive/` (applied/superseded — lifecycle is by move). Whole-tree
  lookup: `batches/INDEX.md`, regenerated via
  `python scripts/staged_summary.py --index` — never hand-edited.
- **Research backlog** (unfinished/ongoing threads): `docs/research_backlog.md`.
- **Session memos** (triage memos, escalation writeups): `notes/`.
- **Historical project context**: `docs/PROJECT_SETUP_AND_CONTEXT.md` (pre-migration
  snapshot; its pending-items list is stale — this file + country notes are authoritative).

---

## STANDING RULES — do not violate

1. **Never cite GEM as a source.** No gem.wiki, globalenergymonitor.org, or any GEM
   surface in `[ref]` columns or outputs unless Baird explicitly says to. The goal
   is to surface what *other*, independent sources exist.
2. **Never fabricate source URLs.** If a URL can't be verified, describe the source
   precisely in `ResearcherNotes` and flag inferred/presumed. Inferred status change
   → `ShelvedCancelledType = Presumed`, no fabricated URL.
3. **Don't defend wrong findings.** Baird challenges data points actively.
   Acknowledge errors, revise on evidence, regenerate outputs.
4. **Corroborate with 2+ independent sources (near-requirement).** For any data
   point (status, capacity, length, diameter, ownership, FID, dates, locations,
   route), try to find two *independent* sources that agree. 2+ independent → high;
   single → medium/low; none verifiable → inferred/presumed. The same wire story
   republished, multiple outlets tracing to one original, and anything citing GEM
   do NOT count. Record the tier + sources in `ResearcherNotes`. Detail:
   `docs/reference/confidence_tiers.md`.
5. **Banned source: abarrelfull** (`abarrelfull.wikidot.com`, `abarrelfull.co.uk`).
   Never use it as a reference, ever — not even alongside corroborating sources, not
   in any output, note, or lane (Baird directive 2026-07-17, all GEM researcher
   projects). If it's the only place a value appears, treat the value as unsourced;
   chase whatever primary source it footnotes and cite that.

---

## Live data access (the only correct way)

Backend Google Sheet `1foPLE6K-uqFlaYgLPAUxzeXfDO5wOOqE7tibNHeqTek` ("Anyone with
link can view"). Pull via `./scripts/refresh_csvs.sh`, or curl directly:

```bash
# Oil/NGL tab (107 cols, GID 456134080); Gas tab (~140 cols, GID 1020144097);
# Pipeline operators/owners tab (44 cols, GID 1489950650) — refresh_csvs.sh pulls all three
curl -sL "https://docs.google.com/spreadsheets/d/1foPLE6K-uqFlaYgLPAUxzeXfDO5wOOqE7tibNHeqTek/export?format=csv&gid=456134080" -o data/GOIT_oil_ngl.csv
```

**Header is at CSV row index 2 for the two tracker tabs**: `pd.read_csv(path, header=2, low_memory=False)`.
**The operators/owners tab's header is at row index 1** (`header=1`) — row 0 is a filter-view banner.
Do **not** use Drive MCP `download_file_content` (first tab only) or
`read_file_content` (lossy). Schema gotchas (multi-value diameter, buffer rows,
`SheetRow = CSV index + 4`, `[ref]` pairing, segment-vs-network granularity):
`docs/reference/gem_schema.md`.

---

## Workflow router

Read the relevant `docs/workflows.md` section + SOP before starting a batch.

| Workflow | Trigger phrases | Recipe + rules |
|---|---|---|
| **Triage** (plan the batch; memo, no xlsx) | "what should we work on", "what's stale", "where are the gaps" | `workflows.md` §1 + Triage SOP |
| **Reconcile vs a scraped dataset** (per-source diff) | "reconcile gulfpub for <country>", "gulfpub diff", "compare GEM to <dataset>", "run reconciliation for <scope>" | `workflows.md` §2 + Reconciliation SOP |
| **Country Sweep** (THE research engine — legs `refs` / `fills` / `validity` / `status-review` / `routes` / `gulfpub`; presets `refs-only`, `deep`, `in-dev`) | "ref sweep for <country>", "deep sweep <country>", "go deep on <country>", "full pass on <country>", "re-verify refs", "in-dev status sweep", "check the in-dev segments in <country>" | `workflows.md` §3 + Sweep SOP (`docs/sops/sweep.md`) |
| **Discover new pipelines** | "find new pipelines in <country>", "discovery run", "what's missing in <country>" | `workflows.md` §4 + Discovery SOP |
| **Update** (targeted fixes to named rows/questions) | "update <these pipelines>", "fix P0544's status", "resolve the recon disagreements", "apply the QC fixes" | `workflows.md` §5 + Update SOP |
| **Handoff packet** (assembly + delivery — QC legs + ALL pending staged work for the scope, two workbooks: actions + evidence) | "handoff packet for <country>", "qc packet for <country>", "wiki alignment qc", "route integrity for <country>", "assemble everything for <country>", "should we even be tracking these" | `workflows.md` §6 + QC SOP |
| **Annual update packet** (campaign recipe = §3 in-dev + §4 + §6) | "annual update for <country>", "country packet", "run the <campaign> packet for <country>" | `workflows.md` §7 + Annual Update SOP; roster in `campaigns/` |
| **Route creation** (candidate route geometry via a source ladder → staged `<PID>.geojson` for a human routes-repo PR) | "create a route for P1234", "draw routes for <country>", "route creation run", "digitize the <name> route" | `workflows.md` §8 + Route Creation SOP (`docs/sops/route_creation.md`) |

Routing notes:
- A reconciliation reference-only (`Addition`) row is usually **not** a missing
  pipeline — **match it to an existing GEM pipeline under another name first**
  (→ `OtherEnglishNames`); only genuine misses go to Discovery.
- A scraped dataset is **one source in a conflict, never automatically
  authoritative** — value disagreements route to Update's normal source-search.
- **Sweep vs Update:** Update is *targeted* (named rows, specific questions);
  anything whole-country / "re-verify everything" is a Country Sweep with the
  right legs. The sweep's `refs` leg researches & stages refs across all
  rows×ref-cells to the ≥2-independent target; both share one ref-pair model
  (`scripts/ref_pairs.py`).
- QC/handoff legs never edit: they detect and route ("QC detects, Update fixes").
  The tracker-wide mechanical audit ("rebuild the QC workbook", "data-health
  audit" → `build_qc_workbook.py`) is a standalone artifact — see the note in
  `workflows.md` §6 + QC SOP.
- **Route/geometry `[ref]` cells are out of scope** for the refs leg (geometry →
  routes repo, not media URLs) — but the `routes` leg may *suggest routes*
  (corridor + sourced endpoints → `<Cmdty>_RouteSuggestions`, candidates for a
  human routes-repo PR) for `RouteAccuracy`-weak rows; never auto-replace, never
  fabricate coords.
- Sweep deliverables lead with a `<Cmdty>_Backend` tab — a **1:1 mirror of the FULL
  tracker backend** (every column in sheet order, current values prefilled, overlays
  tier-colored only on touched cells, leading `SheetRow` locator). The handoff packet
  is TWO files: `…-actions.xlsx` (only suggested changes + open issues; its
  `<Cmdty>_AllFillsBackend` is THE one paste surface — ALL fills AND paste-ready refs,
  carried + own, unified in that full backend layout but with NO leading `SheetRow`
  locator, so every column aligns 1:1 with the sheet for copy-paste; a tier-colored
  value cell = a proposed value, a colored `[ref]` with an untinted value = ref-only
  work) and
  `…-evidence.xlsx` (audit trail: confirmed/known-staged/info rows + per-fill/per-ref
  detail). Either way,
  **don't paste the computed/formula columns back over the live formulas**.
  **Owner/operator refs** live on the separate ProjectID-keyed "Pipeline
  operators/owners" tab (GID 1489950650) — the worklist joins it and stages
  `Operator [ref]`/`Owner [ref]` onto a dedicated `<Cmdty>_OperatorsOwners` tab
  (`[ref]` precedes its values there).

---

## Reconciliation is pluggable (the one big difference from LNG)

The LNG-terminals project diffs one canonical PDF (GIIGNL) via a hard-coded
extractor. Pipelines have **no canonical reference**. Each scraped route database is
registered under `sources/<name>/` as a declarative `manifest.yml` (column maps,
units, status map, geometry source, `source_tier`) + an optional `adapter.py` for
custom parsing. `ingest.py` normalizes any source into one **canonical schema**
(`sources/_schema/canonical_record.md`); `match.py` + `route_compare.py` +
`reconcile.py` then run the **same** hybrid (name + attribute + route-geometry)
diff. **Adding a dataset is config, not engine code** — drop a new manifest and run
`reconcile.py --source <name>`.

---

## Hard requirements (override anything below)

- **Never modify the live GEM Sheet or the routes repo.** Output is a staging xlsx +
  staged JSON; the user applies edits manually.
- **Pull a fresh GEM CSV at the start of every batch**; re-derive the column map
  from the fresh header (schema drifts; don't hard-code offsets).
- **Every URL passes `scripts/url_verifier.py` before going in the xlsx** — even
  URLs that worked in prior batches. Reject GEM URLs.
- **Never auto-apply a reference value.** A reconciliation finding is a *candidate*
  for Update, not an applied edit. A single Tier-2 dataset never reaches green alone.
- **A `ResearcherNotes` cell can document a deliberate GEM divergence** — flag the
  delta but defer the recommendation (verify, don't overwrite).
- **No orphan `[ref]` cells** — never fill a `[ref]` without a paired data value,
  or leave a researched value without a `[ref]`.
- **Expansion with no new physical pipe → `LengthKnown = 0`, `Diameter = blank`.**
- **Don't create duplicate entities** — `entity_lookup.py` before staging a new owner.
- **A route is never auto-replaced.** A route-replacement candidate is flagged for a
  separate human branch+PR against `GOIT-GGIT-pipeline-routes`; §8 candidate geometry
  (`ROUTE_CANDIDATE` `<PID>.geojson`) is staged in this repo only — never fabricate
  coordinates, and the GOGET/GOGPT facility gazetteer anchors endpoints internally but
  is never a `[ref]` or a corroboration source.
- **WKT/route-format QC checks are permanently dropped** — do not rebuild them.
- **Subagent models are chosen at dispatch time, never pinned** (global standing rule —
  user-level CLAUDE.md). Repo mechanics: the saved workflows fall back to
  `MODEL = A.model || 'sonnet'`, so pass `args.model` to carry the dispatch-time choice;
  baked one-off scripts set `model:` per `agent()` call.

---

## Controlled vocabulary (locked — full table in `controlled_vocab.md`)

- **lowercase:** `Status`, `RouteAccuracy`, `PipelineType`.
- **Title Case:** `DelayType`, `ShelvedCancelledType`, `FIDStatus`, `Delayed`, `Opposition`.
- `very high (within meters)` is a valid `RouteAccuracy`.
- **`*CostUnits` = bare currency code** (`USD`, `EGP`, …) — never `EGP million` /
  `USD (millions)`; the magnitude goes in the cost number itself.
- When in doubt, pull a real row from the sheet and copy the exact casing.

---

## Active workstreams

1. **Reconciliation engine + GulfPub** — the pluggable framework (this build).
   Generalizes the one-off `working_files/GOIT_SaudiArabia_Gulfpub_Comparison.xlsx`
   (the golden reference) to any source/country/commodity, with a route-geometry
   pass (GulfPub treated as more accurate than low/medium GEM routes; human review
   before any replacement). In practice GulfPub corroboration has so far shipped
   inside the Country Sweep's `gulfpub` crosswalk leg (`build_gulfpub_crosswalk.py`);
   no standalone §2 reconciliation workbook has been delivered yet.
2. **QC workbook** (`build_qc_workbook.py`) — rebuild of `GOIT_oil_ngl_QC.xlsx`
   (Status, RouteAccuracy, OtherVocab, Owner, WikiLink, Geo, NameUniqueness,
   DateLogic, Diameter, BroadSweep; route/WKT sheet dropped).
3. **Country-level research** — 80+ countries swept; Iraq, Iran, Saudi Arabia deep.

### Pending country items

One-line pointers only — the country notes hold the full open-items lists, and
staged counts regenerate via `python scripts/staged_summary.py --country <C>
--commodity <c>` (never hand-edit counts). Cross-country inventory:
`docs/research_backlog.md`.

- **Iran (gas packet 2026-07-05 staged not applied; + oil open items):**
  `docs/country_notes/iran.md`.
- **Iraq (gas packet 2026-07-05 staged not applied; + oil open items — Grand Faw
  third line, P0544):** `docs/country_notes/iraq.md`.
- **Saudi Arabia (gas packet 2026-07-08 staged not applied — hinges on the
  P1897–P1925 class decision; GulfPub route-consistency pass + oil ref-sweep
  partial):** `docs/country_notes/saudi-arabia.md`.
- **Egypt (gas: handoff regenerated 2026-07-16 as the TWO-file split
  `pipelines_batch_20260716_2359_ET_egypt-gas_handoff-{actions,evidence}.xlsx` —
  the researcher works from the ACTIONS file, not the per-leg workbooks; Nitzana =
  one linked decision; oil not yet swept):** `docs/country_notes/egypt.md`.
- **United States (oil: Delaware Express + Permian Express batches staged not
  applied; deepwater-export open item):** `docs/country_notes/united-states.md`.
- **Nigeria (divestiture ownership sweep not started):**
  `docs/country_notes/nigeria.md`.

---

## External tools & resources

- **Pipeline routes (GeoJSON):** `GlobalEnergyMonitor/GOIT-GGIT-pipeline-routes`
  (sibling mirror `../GOIT-GGIT-pipeline-routes`). See `docs/reference/route_conventions.md`
  + `scripts/fetch_route.sh`.
- **Scraped reference datasets:** `../GOIT-GGIT-scraping` (GulfPub PE World Map);
  registered under `sources/`.
- **GEM Project Database MCP:** wraps `gem-project-db.herokuapp.com`; auth via
  `GEM_SESSION_COOKIE` (Django sessionid; rotates ~2 weeks). Not needed for reconciliation.
- **GEM LNG tracker:** Sheet `1FjjeQD8AlQ_kQAMrohA3jAV3yZy7Lb61djt25D-4Fh8`, GID
  `243795339`; CSV export works; header at row index 1.
- **SFOC sheet** (LNG carrier reconciliation): `1LwgbR4jnMrzaTIyhWeuOf0Z4Foj0lOMGEABBd58eIhY`;
  Drive MCP `read_file_content` only (pipe-delimited markdown); CSV export → 401.
- **Preferred sources** + the reference-dataset registry: `docs/reference/source_roster.md`.
- **Python/GIS:** `requirements.txt`; QGIS, GeoPandas, shapely, fiona; EPSG:4326.

---

## When to escalate to the user

- A reference disagrees on >10% of matched rows (material conflicts), or a source
  produces >30 reference-only Additions in one country.
- A whole class of GEM values looks systematically wrong (schema misunderstanding,
  not a finding).
- Discovery surfaces >5 candidate clusters in one country.
- A QC spot-check shows >10% of sampled cells unsupported.
- An OID-unstable source was re-scraped (cross-scrape identity needs a decision).

---

## Common commands

```bash
./scripts/refresh_csvs.sh                 # pull GOIT + GGIT snapshots from the live sheet
./scripts/fetch_route.sh P5367            # fetch one route GeoJSON by ProjectID
python scripts/ingest.py --source gulfpub --commodity both --out batches/<scope>/staging/recon-gulfpub-<date>/
python scripts/reconcile.py --source gulfpub --country "Saudi Arabia" --commodity both --staging batches/<scope>/staging/recon-gulfpub-<date>/
python scripts/build_recon_workbook.py --staging batches/<scope>/staging/recon-gulfpub-<date>/ --output batches/<scope>/deliverables/pipelines_batch_<stamp>_<scope>_reconciliation.xlsx   # <stamp> from: TZ=America/New_York date "+%Y%m%d_%H%M_ET"
pip install -r requirements.txt
```

## When starting a new task

1. Confirm country + commodity scope (and, for reconciliation, the `--source`).
2. Refresh CSVs — don't work from stale snapshots for live research.
3. Load with `pd.read_csv(path, header=2, low_memory=False)`; exclude buffer rows.
4. Read the relevant `docs/workflows.md` section + SOP, then execute.
5. Run the pre-delivery checks (`docs/sops/qc.md`) before presenting.
