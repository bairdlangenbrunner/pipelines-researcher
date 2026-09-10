# Pipelines Researcher — operational guide

Backend scaffolding for an agentic research + reconciliation workflow that helps
maintain Global Energy Monitor's open-access pipeline databases:

- **GOIT** — Global Oil Infrastructure Tracker (crude oil + NGL pipelines, worldwide)
- **GGIT** — Global Gas Infrastructure Tracker (gas pipelines)

Deeper coverage in MENA, US, Iran, Iraq, Saudi Arabia. Researcher initials in the
tracker: **CB**. The agent **never writes to the routes repo or the live Google
Sheet by default** — every batch produces a reviewable Excel deliverable + staged
JSON that Baird applies manually. Both are writable only on **explicit per-batch
authorization** (see the hard requirement below): sheet writes as a mechanical
pre-verified one-off, and §8 route candidates via the apply recipe in
`workflows.md` §8 step 6 — never as a blanket way to "apply" batches.

Where things live — **read on demand as the workflow dictates, not all at once**:

- **Research methodology** (*what* to research) lives in the SOPs + reference: source
  hierarchy `source_roster.md`, tiers `confidence_tiers.md`, discovery search + route
  research `sops/discovery.md`, targeted research `sops/update.md`.
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
- **Archived docs**: `docs/archive/` — `PROJECT_SETUP_AND_CONTEXT.md` (pre-migration
  snapshot; its pending list is stale — this file + country notes are authoritative) and
  `GOIT_Pipeline_Research_Workflow.md` (the original 4-phase methodology, superseded).

---

## STANDING RULES — do not violate

1. **Never cite GEM as a source.** No gem.wiki, globalenergymonitor.org, or any GEM
   surface in `[ref]` columns or outputs unless Baird explicitly says to. The goal
   is to surface what *other*, independent sources exist.
2. **Never fabricate source URLs.** If a URL can't be verified, describe the source
   precisely in `ResearcherNotes` and flag inferred/presumed. Inferred status change
   → `ShelvedCancelledType = inferred`, no fabricated URL.
3. **Don't defend wrong findings.** Baird challenges data points actively.
   Acknowledge errors, revise on evidence, regenerate outputs.
4. **Corroborate with 2+ independent sources (near-requirement).** For any data
   point (status, capacity, length, diameter, ownership, FID, dates, locations,
   route), try to find two *independent* sources that agree. 2+ independent → high;
   single → medium/low; none verifiable → inferred/presumed. The same wire story
   republished, multiple outlets tracing to one original, and anything citing GEM
   do NOT count. Record the tier + sources in `ResearcherNotes`. Detail:
   `docs/reference/confidence_tiers.md`. **Five corollaries from researcher feedback
   (a)–(d) MZ 2026-09-03 on Jiangxi v2, (e) Baird 2026-09-09 on US gas — all encoded in the
   Sweep SOP + `sweep_gates.py`:**
   (a) a ref must NAME the pipeline (`url_verifier … name=`, `name_found`; a page about one
   terminus or the parent trunk is not a ref for the "A–B" row); (b) every document opened is
   read to exhaustion for EVERY column and sibling row (one approval notice sources
   Length/Diameter/Cost/Construction/Start at once); (c) blank values are OWED units
   (`build_ref_worklist.py --owe-fills` → `MISSING_VALUE`), not skipped; (d) the second
   source is owed for every unit — a single-source note says what was searched;
   (e) **AN UNCITED VALUE IS OWED A REF EXACTLY AS A BLANK IS OWED A VALUE, AND CONFIRMING
   IT IS AN OUTPUT, NOT A NO-OP.** A `MISSING_REF` unit (value on the sheet, `[ref]` cell
   empty) ends as a record carrying the ref that states the value — `class_out="REFS_ADDED"`
   with the SAME value when sources agree — or an `UNRESOLVED` saying what was searched.
   "Confirmed as recorded" in a summary and nowhere machine-readable is the same as never
   checking it. A source agreeing within rounding (51.97 mi + 0.5 mi vs a recorded 52) IS a
   ref, at medium/high with the discrepancy noted — `UNRESOLVED` means nothing was found,
   never that something slightly different was found. Enforced by
   `scripts/check_shard_coverage.py` (per shard, blocking, before a subagent finishes) and
   `sweep_gates.py` gate L (per store, at delivery).
5. **Banned sources: abarrelfull** (`abarrelfull.wikidot.com`, `abarrelfull.co.uk`) **and theodora.com** (tertiary aggregator; `url_verifier` rejects both).
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
is now a thin wrapper around the shared pull engine in **`../gem-db-ops`** (as of 2026-08-11):
it calls `gem-db-ops/goit/pull.py --with-owners` and `gem-db-ops/ggit/pull.py`, which read each
tab through Sheets `values.get` in `gem-db-ops/gem_sheets.py`, reproducing the export's
byte-shape (verified identical on the Oil/NGL tab against the 2026-08-11 snapshot; headers and
row counts identical on all three tabs). The local reader `scripts/_sheets_pull.py` is **gone** —
don't re-create it; fix `gem-db-ops` instead so every consumer repo gets the fix. Override the
sibling path with `GEM_DB_OPS_REPO` if the checkout isn't beside this repo. Each pull also drops
a gitignored `<snapshot>.colmap.json` (re-derive with `python3 ../gem-db-ops/gem_colmap.py <csv>
--tracker goit|ggit`).
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

### Fetching gem.wiki needs a specific User-Agent

`harvest_wiki_citations.py` and `wiki_alignment.py` *visit* gem.wiki (never cite it —
standing rule 1). The gem.wiki zone ran Cloudflare **Under Attack Mode** 2026-08-07
→ ~08-11 (every non-`baird-wiki` UA got `403` `cf-mitigated: challenge`); UAM is
**off again** (verified 2026-08-11), but the `baird-wiki` UA token stays — it is the
identity GEM's infra admin knows in the firewall logs, and the WAF-bypass key if UAM
returns. If gem.wiki fetches start 403ing again, check the UA first.

- Use `url_verifier.WIKI_UA` for gem.wiki. It is **byte-identical** to
  `USER_AGENT` in `goit-ggit-data-ops/gem-wiki/gemwiki.py`, deliberately: both repos
  present as one client in GEM's firewall logs. **Change one, change the other.**
- Do **not** use `WIKI_UA` for external sites — they need the browser-ish `_UA`, and
  the token means nothing off GEM's zone.
- GEM's infra admin asked for ~5 req/sec against gem.wiki (part of the standing
  arrangement, not a UAM-era measure). `_MIN_INTERVAL` (1.0s) is already stricter,
  so the existing pauses comply — but the two repos share one identity, so don't
  run wiki-fetching passes in both at the same time.
- Full writeup, including the account's actual rights: that repo's
  `gem-wiki/README.md` → Auth and the Cloudflare section.

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
| **Route creation** (candidate route geometry via a source ladder → staged `<PID>.geojson` for a human routes-repo PR, or the per-batch-authorized §8 step 6 apply) | "create a route for P1234", "draw routes for <country>", "route creation run", "digitize the <name> route", "apply the route candidates" | `workflows.md` §8 + Route Creation SOP (`docs/sops/route_creation.md`) |
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
  tier-colored only on touched cells — proposed refs AND every recommended edit,
  i.e. corroborated fills + status-review change/stale verdicts — leading `SheetRow`
  locator). The handoff packet
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

- **Never modify the routes repo without explicit per-batch authorization.** Batch
  output is a staging xlsx + staged JSON; by default the user applies edits manually.
  When Baird authorizes a §8 apply for a specific batch, follow `workflows.md` §8
  step 6 exactly: the routes repo's own `qc_routes.py` gate → branch → `merge
  --no-ff` → push, then the sheet route columns via
  `scripts/apply_route_candidates.py` (plan → review → `--apply`).
  **CARDINAL RULE (Baird 2026-07-30): the routes repo and the backend sheet must
  stay in sync** — the two halves of a §8 apply are one unit. Never merge routes
  into `GOIT-GGIT-pipeline-routes` without applying the matching sheet route
  columns in the same batch (a QC-excluded PID is excluded from BOTH halves).
  **THREE-WAY SYNC (Baird 2026-07-31): `RouteType`, `RouteAccuracy`, and the routes
  repo must ALWAYS agree** — one fact stated three ways, never three separate
  judgments. A merged geojson ⇒ `RouteType = 'Mapped route (at any accuracy)'`,
  every time: "at any accuracy" is literal, so `very low (straight
  line/schematic)` is still mapped, and it overrides a stale `Unavailable (cannot
  find route)`. Moving `RouteAccuracy` off `no route` **without** moving
  `RouteType` is a defect, not a partial apply — never ship one without the other.
  Conversely never set `Mapped` for a PID whose geometry didn't merge.
  `apply_route_candidates.py` writes both columns in one batch and refuses any PID
  without a non-empty geojson in the routes repo; verify with
  `python scripts/audit_route_sync.py` after EVERY apply (findings A–D; A = this
  defect). Repair old rows with `--backfill-route-type`. Full table:
  `docs/sops/route_creation.md` → "The three-way sync rule".
  **The live GEM Sheet is writable only on explicit
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
- **Never delete a once-working ref over an access failure.** Geo-blocks, anti-bot
  403s/WAFs, and timeouts are not deletions — only a page confirmed deleted (HTTP
  404/410) may drop out of a `[ref]` cell. A blocked origin gets its Wayback snapshot
  *added* alongside, never swapped in (`_annotate_kept_refs` in
  `build_ref_workbook.py` enforces this in workbook builds).
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
  (`ROUTE_CANDIDATE` `<PID>.geojson`) stays staged in this repo until a human PR or a
  per-batch-authorized §8 step 6 apply — never fabricate coordinates, and the
  GOGET/GOGPT facility gazetteer anchors endpoints internally but is never a `[ref]`
  or a corroboration source.
- **WKT/route-format QC checks are permanently dropped** — do not rebuild them.
- **Subagent models are chosen at dispatch time, never pinned** (global standing rule —
  user-level CLAUDE.md). Repo mechanics: the saved workflows fall back to
  `MODEL = A.model || 'sonnet'`, so pass `args.model` to carry the dispatch-time choice;
  baked one-off scripts set `model:` per `agent()` call.

---

## Controlled vocabulary (locked — full table in `controlled_vocab.md`)

- **lowercase:** `Status`, `RouteAccuracy`, `PipelineType`, and — corrected 2026-08-07
  against both live tabs — `DelayType`, `ShelvedCancelledType`, `Delayed`, `Opposition`.
- **`ShelvedCancelledType` / `DelayType` are `inferred` / `confirmed`** — lowercase, and
  the dormancy-inference word is `inferred`. `Presumed` appears in neither tracker; the
  docs asserted it for months and `merge_qc` staged it. `Delayed` = `yes` (blank if not).
- **Only `FIDStatus` is capitalized:** `Pre-FID`, `FID`.
- `very high (within meters)` is a valid `RouteAccuracy`.
- **`Status = N/A` is an exclusion marker, not a status** — the row is not to be
  researched and does not belong in the database. Every research scope drops it
  (`build_ref_worklist.py`); discovery/recon keep it in the match roster so it does not
  return as a false Addition. Read tracker CSVs with `keep_default_na=False,
  na_values=[]` or pandas silently blanks it — and blanks `Researcher = NA` (Nagwa) on
  765 rows too.
- **`*CostUnits` = bare currency code** (`USD`, `EGP`, …) — never `EGP million` /
  `USD (millions)`; the magnitude goes in the cost number itself.
- When in doubt, pull a real row from the sheet and copy the exact casing.

---

## Active workstreams

1. **Reconciliation engine (GulfPub + OSM)** — the pluggable framework, generalizing
   `working_files/GOIT_SaudiArabia_Gulfpub_Comparison.xlsx` (the golden reference) to any
   source/country/commodity; also feeds the Country Sweep's recon crosswalk leg
   (`build_recon_crosswalk.py`; `build_gulfpub_crosswalk.py` is a deprecated shim). First
   standalone §2 workbooks 2026-07-28; most countries since ship recon standalone, and **a
   standalone §2 workbook is NOT picked up by a handoff packet** (read `recon_actions`; QC SOP
   → handoff contract). OSM runs by default in the `deep` preset; unmatched reference records
   bucket by `disposition` (Reconciliation SOP §4). Shipped engine defects, each now a rule in
   the Reconciliation SOP → "Engine invariants the bugs taught":
   - GulfPub gas `length_units` was miles read as km — fixed 2026-07-29; a manifest unit is a
     claim to verify (`notes/escalation-2026-07-29-gulfpub-gas-length-miles.md`).
   - Country scope compared with `==` dropped every multi-country transit trunk — fixed
     2026-08-12 via `normalize.country_matches()`, all GulfPub recons re-run
     (`notes/escalation-2026-08-12-multicountry-reference-filter-dropped-transit-trunks.md`).
   - Cyrillic reference names were invisible to the name axis and the health line hid it —
     fixed 2026-08-14, no bucket moved (`notes/escalation-2026-08-14-cyrillic-names-invisible-to-matcher.md`).
   - `osm_id_key` was not unique (62 features / 10 extracts; uz 6/865.8 km, kz 7/711.7 km,
     ua 26/251.7 km) — fixed 2026-08-26, no geometry lost, no re-run owed (`sources/osm/NOTES.md`).
2. **QC workbook** (`build_qc_workbook.py`) — rebuild of `GOIT_oil_ngl_QC.xlsx`
   (Status, RouteAccuracy, OtherVocab, Owner, WikiLink, Geo, NameUniqueness,
   DateLogic, Diameter, BroadSweep; route/WKT sheet dropped).
3. **Country-level research** — 80+ countries swept; Iraq, Iran, Saudi Arabia deep.

### Pending country items

One-line pointers only — the country notes hold the full open-items lists, and
staged counts regenerate via `python scripts/staged_summary.py --country <C>
--commodity <c>` (never hand-edit counts). Cross-country inventory:
`docs/research_backlog.md`. "Recons standalone" = the handoff packet does NOT carry the
§2 recon workbooks (`recon_actions=0`), so they are separate review surfaces.

- **Iran (gas packet 2026-07-05 staged not applied; + oil open items):** `docs/country_notes/iran.md`.
- **Iraq (gas: full pass 2026-07-28, rebuilt 2026-07-29, staged not applied — supersedes the 07-05
  packet; §8 routes APPLIED 2026-08-03; + oil open items; 4 files to work):** `docs/country_notes/iraq.md`.
  Recons standalone; the GulfPub recon was re-run 2026-08-12 — work the newer workbook.
- **Saudi Arabia (gas packet 2026-07-08, rebuilt 2026-07-28, PARTIALLY APPLIED — check each cell
  before pasting; hinges on the P1897–P1925 class decision; oil ref-sweep partial):** `docs/country_notes/saudi-arabia.md`.
- **Egypt (gas + oil: deep sweep + recon + routes 2026-08-27, staged not applied; 7 files to work):**
  `docs/country_notes/egypt.md`. Gas researched only 40 of 127 rows — the other 87 carry unapplied
  July/August staged work (`--exclude-pids`); the deep sweeps do NOT subsume the four recon workbooks.
- **United States (gas: slice 1 batches 1-4 staged not applied, 4 files to work — the rule-4(e)
  recovery pass is done and all four deliverables rebuilt on it (`_1906_ET`); next batch 5, then
  slice 2; oil: Delaware Express + Permian Express staged not applied; deepwater-export open
  item):** `docs/country_notes/united-states.md`. Sliced, never whole-country; recon legs
  deliberately off.
- **Pakistan (gas: first-ever full pass 2026-08-07 + SNGPL crosswalk 2026-08-10, staged not applied;
  3 files to work):** `docs/country_notes/pakistan.md`. Recons standalone; 51 of 70 rows are one bulk
  map load, so `UNRESOLVED` is often the correct outcome — never delete a row off an existence flag.
- **India (gas: first-ever full pass 2026-08-10, staged not applied; 4 files to work):**
  `docs/country_notes/india.md`. Recons standalone; India is the INVERSE of Pakistan — a blank ref
  means nobody looked, so `UNRESOLVED` is unfinished, not correct.
- **Kazakhstan (gas: first-ever full pass 2026-08-11, staged not applied; 3 files to work):**
  `docs/country_notes/kazakhstan.md`. Work the 08-12 handoff (the 08-11 pair is superseded after
  cluster A's reversal); recons standalone and both re-run (GulfPub 08-12, OSM 08-14).
- **Malaysia (gas: first-ever full pass 2026-08-12, staged not applied; 5 files to work):**
  `docs/country_notes/malaysia.md`. Recons standalone; the headline is a SCOPE ruling (5 GEM rows vs
  ~150 in three sources) that gates everything else — nothing staged as Discovery until Baird rules.
- **Ukraine (gas: first-ever full pass 2026-08-15, staged not applied; 3 files to work):**
  `docs/country_notes/ukraine.md`. Recons standalone; 3.29% citation base — calibrate as the inverse
  of Kazakhstan: a blank means nobody looked.
- **Uzbekistan (gas: first-ever full pass 2026-08-26, staged not applied; 3 files to work):**
  `docs/country_notes/uzbekistan.md`. 13 of its 31 gas rows ARE Kazakhstan's (research legs scoped to
  the 18 domestic rows, recon keeps all 31); recons standalone; work the 08-27 `0931_ET` handoff only.
- **Nigeria (divestiture ownership sweep not started):** `docs/country_notes/nigeria.md`.
- **Israel (gas: INGL/TMNG-map batch 2026-07-23 staged not applied; Ashdod-vs-Ashkelon landfall +
  P3620 open):** `docs/country_notes/israel.md`.
- **China (gas: province-level program ahead of MZ's queue; Guangxi pilot 2026-07-30 + Jiangxi v2
  2026-09-02 staged not applied, one file each; §8 routes applied; oil out of scope until post-cycle):**
  `docs/country_notes/china.md`. Scope is per-PROVINCE via `--province`, never whole-country.
- **Libya (gas: full pass 2026-07-28 staged not applied; 3 files to work):** `docs/country_notes/libya.md`.
  Recons standalone — ~100 gas rows are decided only there, and the GulfPub file's `Oil_*` tabs are
  Libya's only (untriaged) oil output.

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
- **Archiving a `[ref]` document (Internet Archive).** Two different routes, and the
  distinction matters: a **Wayback capture** (`web.archive.org/web/<ts>/<url>`) is IA's
  crawler fetching the origin, scriptable anonymously; an **item**
  (`archive.org/details/<id>`) is *our* bytes uploaded under our account, which works when
  the crawler is blocked. Save Page Now only captures in **path** form
  `https://web.archive.org/save/<url>` (302 → snapshot); the `?url=`/POST form returns the
  interstitial with HTTP 200 and captures nothing — never treat that 200 as success, it
  manufactures fake backup links. **Always verify a capture** by re-fetching it through the
  `id_` raw modifier and checking the bytes are the expected type *and* the byte count
  matches live. On an SPN `520` (IA can't reach the origin though we can), fall back to an
  item upload: `internetarchive` 5.11.0 + `ia` CLI are installed, S3 keys in
  `~/.config/internetarchive/ia.ini` (mode 600, outside the repo — never commit). Item
  identifier = the **original filename stem**, per existing practice (279
  `archive.org/details` refs in the tracker), and set `source`/`originalurl` metadata since
  an item URL — unlike a Wayback URL — does not embed the origin. Verify by matching IA's
  stored md5 to the local file. Worked example + the unarchivable cases:
  `notes/escalation-2026-08-12-unarchivable-xlsx-refs.md`.
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
