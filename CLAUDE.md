# Pipelines Researcher — operational guide

Backend scaffolding for an agentic research + reconciliation workflow that helps
maintain Global Energy Monitor's open-access pipeline databases:

- **GOIT** — Global Oil Infrastructure Tracker (crude oil + NGL pipelines, worldwide)
- **GGIT** — Global Gas Infrastructure Tracker (gas pipelines)

Deeper coverage in MENA, US, Iran, Iraq, Saudi Arabia. Researcher initials in the
tracker: **CB**. The agent **never writes to the routes repo**, and by default
doesn't write the live Google Sheet either — every batch produces a reviewable
Excel deliverable + staged JSON that Baird applies manually. Direct sheet writes
are allowed only as a **separately authorized one-off** (see the hard requirement
below), never as a way to "apply" a batch.

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
  `adapter.py`) per scraped dataset; GulfPub + OpenStreetMap today. How to add one:
  `sources/README.md`.
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

Backend Google Sheet `1foPLE6K-uqFlaYgLPAUxzeXfDO5wOOqE7tibNHeqTek`. Pull via
`./scripts/refresh_csvs.sh` — **always use the script, don't hand-roll a curl.**

**AUTHENTICATED ACCESS IS THE ONLY PATH — for this sheet and for every other work
shared-drive / Google Docs-Sheets-Slides object.** Baird is deliberately withdrawing
anonymous link access, so reach for the `gws` CLI (`gws-gem`, read-only, the default) or the
Google Drive MCP tools first, never a public export URL, and never treat auth as a fallback.
The anonymous CSV export died 2026-07-29 (401 on every tab; the sheet lives in shared drive
`0AFOra93TfZAeUk9PVA`) and has been removed from the script — don't re-add it. `refresh_csvs.sh`
reads each tab through Sheets `values.get` in `scripts/_sheets_pull.py`, reproducing the
export's byte-shape (verified against the 07-28 snapshots: identical headers and row counts).
If it fails on auth, ask Baird to run `gws-gem auth login` (needs a browser) — don't try it
headlessly. Writes still require per-edit authorization and `gws-gem-write` (see Hard
requirements). Tabs: Oil/NGL (107 cols, GID 456134080), Gas (131 cols, GID 1020144097),
Pipeline operators/owners (44 cols, GID 1489950650) — the script pulls all three.

**Header is at CSV row index 2 for the two tracker tabs**: `pd.read_csv(path, header=2, low_memory=False)`.
**The operators/owners tab's header is at row index 1** (`header=1`) — row 0 is a filter-view banner.
For a multi-tab spreadsheet, prefer Sheets `values.get` per tab over Drive MCP
`download_file_content` (first tab only) or `read_file_content` (lossy). Schema gotchas
(multi-value diameter, buffer rows,
`SheetRow = CSV index + 4`, `[ref]` pairing, segment-vs-network granularity):
`docs/reference/gem_schema.md`.

---

## Workflow router

Read the relevant `docs/workflows.md` section + SOP before starting a batch.

| Workflow | Trigger phrases | Recipe + rules |
|---|---|---|
| **Triage** (plan the batch; memo, no xlsx) | "what should we work on", "what's stale", "where are the gaps" | `workflows.md` §1 + Triage SOP |
| **Reconcile vs a scraped dataset** (per-source diff) | "reconcile gulfpub for <country>", "gulfpub diff", "compare GEM to <dataset>", "run reconciliation for <scope>" | `workflows.md` §2 + Reconciliation SOP |
| **Country Sweep** (THE research engine — legs `refs` / `fills` / `validity` / `status-review` / `routes` / `recon` (gulfpub + osm); presets `refs-only`, `deep`, `in-dev`) | "ref sweep for <country>", "deep sweep <country>", "go deep on <country>", "re-verify refs", "in-dev status sweep", "check the in-dev segments in <country>" | `workflows.md` §3 + Sweep SOP (`docs/sops/sweep.md`) |
| **Discover new pipelines** | "find new pipelines in <country>", "discovery run", "what's missing in <country>" | `workflows.md` §4 + Discovery SOP |
| **Update** (targeted fixes to named rows/questions) | "update <these pipelines>", "fix P0544's status", "resolve the recon disagreements", "apply the QC fixes" | `workflows.md` §5 + Update SOP |
| **Handoff packet** (assembly + delivery — QC legs + ALL pending staged work for the scope, two workbooks: actions + evidence) | "handoff packet for <country>", "qc packet for <country>", "wiki alignment qc", "route integrity for <country>", "assemble everything for <country>", "should we even be tracking these" | `workflows.md` §6 + QC SOP |
| **Annual update packet** (campaign recipe = §3 in-dev + §4 + §6) | "annual update for <country>", "country packet", "run the <campaign> packet for <country>" | `workflows.md` §7 + Annual Update SOP; roster in `campaigns/` |
| **Route creation** (candidate route geometry via a source ladder → staged `<PID>.geojson` for a human routes-repo PR) | "create a route for P1234", "draw routes for <country>", "route creation run", "digitize the <name> route" | `workflows.md` §8 + Route Creation SOP (`docs/sops/route_creation.md`) |
| **Full country pass** (composite: operating deep sweep + in-dev + cancelled review + redundancy adjudication + every recon + handoff — one run dir each) | "full pass on <country>", "sweep everything in <country>", "go all the way on <country>" | `workflows.md` §9 (chains §2/§3/§6) |

Routing notes:
- **A reference route is presumptively REAL pipe** — an unmatched OSM/GulfPub trace is
  either geometry GEM is missing or a pipeline GEM is missing, never noise to filter.
  Triage by `disposition`, never as one undifferentiated "Addition" pile:
  `ROUTE_FOR_EXISTING` (candidate geometry for a routeless GEM row → human routes-repo
  PR, never auto-replaced), `FRAGMENT_OF_EXISTING`, `NEAR_MISS` (adjudicate by hand),
  `DISCOVERY_CANDIDATE` — and even then **match it to an existing GEM pipeline under
  another name first** (→ `OtherEnglishNames`); only genuine misses go to Discovery.
  A `partial` coverage label = corroborates LOCATION only, not length/capacity/extent.
- **A null or thin recon run is a claim about the matcher until you read its health
  line.** `reconcile.py` emits `MATCH_QUALITY` when the name and geometry axes are both
  mostly dead (unnamed reference features × routeless GEM rows). Fix it with the
  per-dataset `geoarea_weight` override in the source manifest — never by lowering a
  threshold, and never by retuning a shared source-level block (that moves committed
  runs in other countries).
- A scraped dataset is **one source in a conflict, never automatically
  authoritative** — value disagreements route to Update's normal source-search.
- **Sweep vs full pass vs Update:** Update is *targeted* (named rows, specific
  questions); a Country Sweep is one scoped pass with selected legs; a **full pass
  (§9)** is the composite of several sweeps + every recon + the handoff, each in its
  own run dir — don't try to run it as one sweep.
  Anything whole-country / "re-verify everything" is a Country Sweep with the
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

- **Never modify the routes repo.** Batch output is a staging xlsx + staged JSON; the
  user applies edits manually. **The live GEM Sheet is writable only on explicit
  authorization** — Baird asks for the edit, or the agent asks permission and gets a
  yes, *for that specific edit*. Approval never carries to the next task. Never write
  the sheet to "apply" a batch: batches go through the deliverable, always. An
  authorized write must be **mechanical and pre-verified** (a fix whose correctness is
  established before writing, not a research judgment applied live), and must:
  (1) read the target range with `valueRenderOption: FORMULA` first and abort on any
  formula cell; (2) write a before/after backup CSV to `notes/` and commit it;
  (3) use `valueInputOption: RAW` and cell-scoped ranges, never whole rows/columns;
  (4) re-read afterwards and verify against the plan. Use `gws-gem-write`
  (`gws-gem` is read-only and stays the default).
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
   inside the Country Sweep's recon crosswalk leg (`build_recon_crosswalk.py`, one
   `<Cmdty>_<Source>` tab per registered dataset — `build_gulfpub_crosswalk.py` is now a
   deprecated shim). First standalone §2 workbooks delivered 2026-07-28 (Iraq oil, OSM +
   GulfPub); Egypt gas followed 2026-07-29, then Iraq/Saudi/Iran gas the same day off the
   length-units re-run, and **Iraq gas moved its recon OUT of the packet entirely the same
   day** (both sources standalone at `20260729_1104_ET`; the packet's recon tabs retired).
   **A standalone §2 workbook is NOT picked up by a
   handoff packet** — the packet only carries staging dirs listed in its "Prior staged
   packets" line, so Libya's, Egypt's and Iraq's recon output are separate review surfaces
   that must be worked alongside the actions file (all logged in
   `docs/research_backlog.md` §2). Whether recon ships inside the packet or standalone is a
   per-country choice, so **read the packet's `recon_actions` count before assuming**:
   `0` means the recon findings are in separate files.
   **A unit declared in a manifest is a claim to verify, not a given** — the gas
   `length_units` sat wrong (`km`, actually miles) through a scrape repoint and four
   countries' workbooks. `units.length_units_by_country` exists for the case where one
   country's block differs (GulfPub gas: Canada is km, everything else miles); fixed and
   re-run 2026-07-29 (`notes/escalation-2026-07-29-gulfpub-gas-length-miles.md`). Any gas
   recon workbook stamped before `20260729_0941_ET` has `Ref Length (km)` ~38% short.
   **OSM is a second registered source and runs by default in the `deep`
   preset**; unmatched reference records are bucketed by `disposition`
   (ROUTE_FOR_EXISTING / FRAGMENT_OF_EXISTING / NEAR_MISS / DISCOVERY_CANDIDATE) on the
   standing principle that a reference route is presumptively real pipe.
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
- **Iraq (gas: full pass 2026-07-28 rebuilt 2026-07-29, staged not applied — supersedes
  the 2026-07-05 packet. **FOUR files to work** (Libya's shape), all stamped
  `20260729_1104_ET`: `…_iraq-gas_handoff-{actions,evidence}.xlsx` +
  `…_iraq-gas_reconciliation-{gulfpub,osm}.xlsx` — recon is now STANDALONE and the
  packet's `Gas_GulfPubActions`/`Gas_OSMActions` tabs are retired (`recon_actions=0`),
  so ~150 GulfPub/OSM decisions live ONLY in those two files, incl. 30 OSM traces that
  are candidate geometry for routeless rows and an OSM `MATCH_QUALITY` warning
  (3.8% of refs named × 35.7% of GEM rows routed). The 07-29 rebuild was necessary
  twice over: the GGIT gas tab was re-sorted to ProjectID order between the two pulls
  (4,262/4,370 rows moved → every 07-28 locator wrong), and the retired GulfPub tab
  came from the pre-fix miles-as-km run. THIRTEEN escalations
  open, structurally: the ASB Table 4.10/9.9 length mi→km defect on 19 rows (two
  families, two *different* one-cell fixes —
  `notes/escalation-2026-07-28-asb-iraq-length-units.md`), CapacityUnits on 3 rows,
  P6824 as a diesel line misfiled in GGIT, and the ASB-provenance ruling that
  withdrew 12 of 16 of our own duplicate/existence flags. THREE retractions — P4067
  is *not* a misfiled crude line, "stale forward" on P7435/P6826 is wrong, P6007 is
  not a phantom. + oil open items — Grand Faw third line,
  P0544, and an UNTRIAGED first OSM oil run: 175 unmatched traces, 84 of them
  discovery candidates, delivered as
  `…_20260728_1804_ET_iraq-oil_{osm,gulfpub}-reconciliation.xlsx`):**
  `docs/country_notes/iraq.md`.
- **Saudi Arabia (gas packet 2026-07-08, rebuilt 2026-07-28 as
  `…_20260728_1731_ET_saudi-arabia-gas_{annual-indev,deepsweep}.xlsx` — and
  **PARTIALLY APPLIED already**: 100/199 annual-indev + 46/306 deepsweep ref units are
  live, 32 of 40 operating rows edited on the sheet since 07-08, so check each cell
  before pasting; hinges on the P1897–P1925 class decision; GulfPub route-consistency
  pass + oil ref-sweep partial):** `docs/country_notes/saudi-arabia.md`.
- **Egypt (gas: handoff regenerated 2026-07-16 as the TWO-file split, rebuilt 2026-07-28 as
  `pipelines_batch_20260728_1731_ET_egypt-gas_handoff-{actions,evidence}.xlsx` —
  the researcher works from the ACTIONS file, not the per-leg workbooks; 16/284 ref
  units already live; Nitzana = one linked decision. **+ §2 recon added 2026-07-29 to match
  Libya's coverage — TWO standalone workbooks NOT in the handoff**
  (`…_20260729_0910_ET_egypt-gas_reconciliation-{gulfpub,osm}.xlsx`): GulfPub 52 overlaps /
  40 all-`NEAR_MISS` additions (over the >30 gate) / 3 status conflicts, and a first OSM run
  that returned 0 overlaps on both `MATCH_QUALITY` escalations → 9 `ROUTE_FOR_EXISTING` +
  10 `DISCOVERY_CANDIDATE`. Oil not yet swept):** `docs/country_notes/egypt.md`.
- **United States (oil: Delaware Express + Permian Express batches staged not
  applied; deepwater-export open item):** `docs/country_notes/united-states.md`.
- **Nigeria (divestiture ownership sweep not started):**
  `docs/country_notes/nigeria.md`.
- **Israel (gas: INGL/TMNG-map ground-truth batch 2026-07-23 staged not applied —
  2 new rows P8001/P8003, 5 validation candidate edits, 5 route candidates
  (P2197 QC-fail); Ashdod-vs-Ashkelon landfall + P3620 Ashkelon-gap open):**
  `docs/country_notes/israel.md`.
- **China (gas: province-level program agreed 2026-07-29 — agent batches run AHEAD of
  Maggie Zheng's province queue (she has routes/wiki + the trunk systems; cycle plan in
  gem-desk `research-cycles/ggit-2026-pipelines-update/`); scope via
  `build_ref_worklist.py --province` + trunk-exclusion regex; Guangxi pilot queued;
  oil out of scope until post-cycle):** `docs/country_notes/china.md`.
- **Libya (gas: full pass 2026-07-28 staged not applied — ref sweep, cancelled
  review, 7 redundancy clusters, GulfPub + OSM recon, handoff packet
  `…_20260728_1235_ET_libya-gas_handoff-{actions,evidence}.xlsx`. **THREE files to work:**
  the actions file plus the two recon workbooks, which the packet does NOT subsume (~100 gas
  rows live only there; the GulfPub one also holds untriaged `Oil_*` tabs from a
  `--commodity both` run). The 07-23 annual-indev + discovery workbooks were archived
  2026-07-29 as subsumed. Four
  structural escalations open: cluster-A coastal double-count, three condensate
  lines misfiled in GGIT, and two OPEC-ASB Table 4.10 ingest defects — the `scm/y`
  zero-capacity rows (`notes/escalation-2026-07-28-scm-capacity-units.md`) and 14
  lengths converted mi→km when the Libya block was already in km
  (`notes/escalation-2026-07-28-asb-libya-length-units.md`). Oil not swept):**
  `docs/country_notes/libya.md`.

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
  `243795339`; header at row index 1. Read it through `gws-gem`/Drive MCP like everything
  else — if an anonymous CSV export still happens to work here, it is being withdrawn too.
- **SFOC sheet** (LNG carrier reconciliation): `1LwgbR4jnMrzaTIyhWeuOf0Z4Foj0lOMGEABBd58eIhY`;
  authenticated read only (Sheets `values.get`, or Drive MCP `read_file_content` for its
  pipe-delimited markdown); anonymous CSV export → 401.
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
