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
- **SOPs** (operational *how*): `docs/sops/` — `reconciliation.md` (pluggable
  GEM↔dataset diff), `update.md`, `discovery.md`, `triage.md`, `qc.md`.
- **Workflow recipes** (commands, in order): `docs/workflows.md`.
- **Reference**: `docs/reference/` — `gem_schema.md`, `controlled_vocab.md`,
  `confidence_tiers.md`, `workbook_conventions.md`, `route_conventions.md`,
  `source_roster.md`; plus `docs/country_notes/`.
- **Reference-dataset registry**: `sources/` — one `manifest.yml` (+ optional
  `adapter.py`) per scraped dataset; GulfPub today. How to add one: `sources/README.md`.
- **Scripts**: `scripts/` (engine + helpers).
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
| **Reconcile vs a scraped dataset** (the engine; per-source) | "reconcile gulfpub for <country>", "gulfpub diff", "compare GEM to <dataset>", "run reconciliation for <scope>" | `workflows.md` §1 + Reconciliation SOP |
| **Update existing pipelines** (most common) | "update pipelines in <country>", "refresh <country>", "fill blank refs", "status sweep for <country>", "resolve the recon disagreements" | `workflows.md` §2 + Update SOP |
| **Discover new pipelines** | "find new pipelines in <country>", "discovery run", "what's missing in <country>" | `workflows.md` §3 + Discovery SOP |
| **Triage** (plan the batch; memo) | "what should we work on", "what's stale", "where are the gaps" | `workflows.md` §4 + Triage SOP |
| **Quality control** (xlsx; detects → Update fixes) | "qc pass", "data-health audit", "rebuild the QC workbook" | `workflows.md` §5 + QC SOP |
| **Reference sweep** (xlsx; fill & re-verify every `[ref]`) | "ref sweep for <country>", "fill and verify refs", "corroborate the refs in <country>", "re-verify refs", "link-rot + refill" | `workflows.md` §6 + Ref Sweep SOP |
| **Deep sweep** (xlsx; ref sweep + deep-fill blanks + per-row validity check, one pass) | "deep sweep <country>", "go deep on <country>'s pipelines", "ref sweep AND fill blanks AND check validity", "full pass on <country>" | `workflows.md` §6b + Ref Sweep SOP ("At scale" + "Schema extensions") |
| **Annual update packet** (campaign; per country: in-dev status sweep + discovery) | "annual update for <country>", "country packet", "run the <campaign> packet for <country>", "in-dev status sweep", "check the in-dev segments in <country>" | `workflows.md` §7 + Annual Update SOP (`docs/sops/annual_update.md`); campaign roster in `campaigns/` |

Routing notes:
- A reconciliation reference-only (`Addition`) row is usually **not** a missing
  pipeline — **match it to an existing GEM pipeline under another name first**
  (→ `OtherEnglishNames`); only genuine misses go to Discovery.
- A scraped dataset is **one source in a conflict, never automatically
  authoritative** — value disagreements route to Update's normal source-search.
- QC never edits: it audits and routes fixes to Update ("QC detects, Update fixes").
- **Ref Sweep vs QC vs Update:** QC *detects* orphan refs (ref filled, value blank);
  Ref Sweep *systematically researches & stages* refs across all rows×ref-cells
  (fills blank refs to the ≥2-independent-corroborating target AND re-verifies live
  ones). Update's "fill blank refs" is ad-hoc enrichment of in-dev rows; the dedicated
  at-scale crawl is Ref Sweep. They share one ref-pair model (`scripts/ref_pairs.py`).
  **Route/geometry `[ref]` cells are out of scope** for Ref Sweep (geometry → routes repo,
  not media URLs) — but a **deep sweep** may *suggest routes* (corridor + sourced endpoints →
  `<Cmdty>_RouteSuggestions`, candidates for a human routes-repo PR) for `RouteAccuracy`-weak
  rows; never auto-replace, never fabricate coords. The deliverable leads with a
  `<Cmdty>_Backend` tab that is a **1:1 mirror of the FULL tracker backend** (every column in
  sheet order, current values prefilled, overlays tier-colored only on touched cells, leading
  `SheetRow` locator) — **don't paste the computed/formula columns back over the live formulas**.
  **Owner/operator refs** live on the separate ProjectID-keyed "Pipeline operators/owners"
  tab (GID 1489950650) — the worklist joins it and stages `Operator [ref]`/`Owner [ref]`
  onto a dedicated `<Cmdty>_OperatorsOwners` tab (`[ref]` precedes its values there).

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
  separate human branch+PR against `GOIT-GGIT-pipeline-routes`.
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
- When in doubt, pull a real row from the sheet and copy the exact casing.

---

## Active workstreams

1. **Reconciliation engine + GulfPub** — the pluggable framework (this build).
   Generalizes the one-off `working_files/GOIT_SaudiArabia_Gulfpub_Comparison.xlsx`
   (the golden reference) to any source/country/commodity, with a route-geometry
   pass (GulfPub treated as more accurate than low/medium GEM routes; human review
   before any replacement). In practice GulfPub corroboration has so far shipped
   inside the deep-sweep `<Cmdty>_GulfPub` crosswalk leg (`build_gulfpub_crosswalk.py`);
   no standalone §1 reconciliation workbook has been delivered yet.
2. **QC workbook** (`build_qc_workbook.py`) — rebuild of `GOIT_oil_ngl_QC.xlsx`
   (Status, RouteAccuracy, OtherVocab, Owner, WikiLink, Geo, NameUniqueness,
   DateLogic, Diameter, BroadSweep; route/WKT sheet dropped).
3. **Country-level research** — 80+ countries swept; Iraq, Iran, Saudi Arabia deep.

### Pending country items
- **Iran:** P6074 (Goureh–Persian Gulf Coast) needs verification before any
  duplicate/removal. P5367 (Golpa–Moghanak) reclassify as a Neka–Ray segment.
- **Iraq:** Grand Faw Port third offshore pipeline (Esta/Micoperi, contracted April
  2025) entered as one new row. Basra–Haditha (P0544) status review (listed
  `construction`, appeared still pre-construction/tender as of early 2026).
- **Iraq gas (2026-07-05 deep sweep, staged not applied):** national dry-gas trunk likely
  duplicated under three naming families (Strategic / Trans-Iraq / National-Gas — a human
  de-dup pass); two rows wrong-tracker (P4067 crude→GOIT, P6824 products→not gas); several
  status/attribution fixes. Full list: `docs/country_notes/iraq.md` "Open items — gas".
- **Iran gas (2026-07-05 full packet — in-dev + discovery + operating deep sweep, staged not
  applied):** class-wide Owner=NIOC→NIGC/IGTC on ~27 operating rows; duplicate/segmentation
  cluster (P0748↔P3957 IGAT-1 double-count; P6022/P6023/P6024 one project split 3 ways; P6027);
  existence cluster P6024/P6025/P6027 (one dead iranertebat source); P3951 Siri–Mobarak status
  wrong; 5/8 in-dev status changes (P0452, P2225, P6006, P7104, P3174). Full list:
  `docs/country_notes/iran.md` "Open items — gas".
- **Saudi gas (2026-07-08 full packet — in-dev + discovery + operating deep sweep, staged not
  applied):** in-dev clean (22/22 status `confirm`); class-wide existence gap on the 2022-vintage
  GIS/km-post family P1897–P1925 (18 existence + 15 duplicate concerns — one class decision, not
  row fixes); de-dup families UBTG-1 cluster, Haradh Khuff–Hawiyah triple, P1922/P1923,
  P7545→P7544, P7768→P1921; P3962 East–West carries the crude Petroline's specs. Full list:
  `docs/country_notes/saudi-arabia.md` "Open items — gas".
- **Egypt gas (in-dev sweep delivered 2026-07-09, operating deep sweep delivered 2026-07-13,
  staged not applied; Sonnet fan-out):** NO escalation gate — no class-wide existence gap (contrast
  Saudi/Iran). In-dev 1/7 status changes (P3657→shelved). Operating (50 rows): 109 validity records,
  concerns = attribution 37 (recurring GASCO-operator vs EGAS-owner nuance, row-specific not
  class-wide; P0462 FuelSource Egypt→Israel), spec 31, existence 4 (P3938 = a CO2-EOR concept not a
  built gas line; P0476/P6693/P6687 reref), duplicate 4 (P0477 network vs P6697–P6702 segments;
  P6687/P0474/P3934 one Obaiyed trunk; P7574 vs P3930). Discovery (Leg B) NOT built — 6 vetted
  candidates staged. Oil (GOIT) not yet swept. Full list: `docs/country_notes/egypt.md`.
- **Saudi Arabia (general):** finish the GulfPub route-consistency pass for low/medium-accuracy
  matches (stage route-replacement candidates for human review). Oil ref-sweep: 10-row batch
  staged (`batches/staging/ref-sweep-saudi-arabia-10row/`), partial toward the intended 50-row run.
- **United States (oil, staged not applied):** Delaware Express (P7995/P0354, researched
  2026-06-12) and Permian Express I–IV (P0113/P2581/P2660/P2661, researched 2026-06-11)
  update batches in `batches/staging/delaware-express/` + `permian-express/`. Open item:
  keep deepwater-export terminal pipeline components distinct from terminal records.
- **Nigeria:** sweep divestiture-affected rows for ownership consistency after each
  package update (not started).

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
python scripts/ingest.py --source gulfpub --commodity both --out batches/staging/recon/<run>/
python scripts/reconcile.py --source gulfpub --country "Saudi Arabia" --commodity both --staging batches/staging/recon/<run>/
python scripts/build_recon_workbook.py --staging batches/staging/recon/<run>/ --output batches/pipelines_batch_<stamp>_<scope>_reconciliation.xlsx   # <stamp> from: TZ=America/New_York date "+%Y%m%d_%H%M_ET"
pip install -r requirements.txt
```

## When starting a new task

1. Confirm country + commodity scope (and, for reconciliation, the `--source`).
2. Refresh CSVs — don't work from stale snapshots for live research.
3. Load with `pd.read_csv(path, header=2, low_memory=False)`; exclude buffer rows.
4. Read the relevant `docs/workflows.md` section + SOP, then execute.
5. Run the pre-delivery checks (`docs/sops/qc.md`) before presenting.
