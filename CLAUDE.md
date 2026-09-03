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
   → `ShelvedCancelledType = inferred`, no fabricated URL.
3. **Don't defend wrong findings.** Baird challenges data points actively.
   Acknowledge errors, revise on evidence, regenerate outputs.
4. **Corroborate with 2+ independent sources (near-requirement).** For any data
   point (status, capacity, length, diameter, ownership, FID, dates, locations,
   route), try to find two *independent* sources that agree. 2+ independent → high;
   single → medium/low; none verifiable → inferred/presumed. The same wire story
   republished, multiple outlets tracing to one original, and anything citing GEM
   do NOT count. Record the tier + sources in `ResearcherNotes`. Detail:
   `docs/reference/confidence_tiers.md`. **Four corollaries from researcher feedback
   (MZ, 2026-09-03, on Jiangxi v2) — all encoded in the Sweep SOP + `sweep_gates.py`:**
   (a) a ref must NAME the pipeline (`url_verifier … name=`, `name_found`; a page about one
   terminus or the parent trunk is not a ref for the "A–B" row); (b) every document opened is
   read to exhaustion for EVERY column and sibling row (one approval notice sources
   Length/Diameter/Cost/Construction/Start at once); (c) blank values are OWED units
   (`build_ref_worklist.py --owe-fills` → `MISSING_VALUE`), not skipped; (d) the second
   source is owed for every unit — a single-source note says what was searched.
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
   **A country scope is a JOIN, not an equality test — the reference side got this wrong
   until 2026-08-12.** `ingest.py`, `reconcile.py` and `adapter_base.py` each compared a
   scraped record's country string with `==`, so every **multi-country** record was silently
   dropped — i.e. exactly the cross-border transit trunks, which in a transit country are
   the majority of what GEM tracks (Ukraine gas 111 → 158 refs, Kazakhstan 32 → 63). The GEM
   side never had the bug. Fixed onto one shared `normalize.country_matches()`; **never
   write a bare `==` against a country string.** ALL committed GulfPub recons were re-run
   2026-08-12 and their predecessors archived — the falsified bucket is `gem_only`
   ("no reference counterpart exists"). Ledger + per-scope A/B:
   `notes/escalation-2026-08-12-multicountry-reference-filter-dropped-transit-trunks.md`.
   Corollary: **a thin recon is a claim about the pipeline until the input count is
   checked** — `MATCH_QUALITY` covers a dead matcher, never records that never arrived.
   **A non-Latin reference name was INVISIBLE to the name axis until 2026-08-14.**
   `normalize_name()`'s `[^a-z0-9]` filter reduced a Cyrillic-only name to the empty string,
   and `reconcile`'s health line counted the RAW name — so Ukraine OSM reported "9.2% of refs
   named" on a run where the matcher saw none, and `MATCH_QUALITY` stayed silent through a
   0.1% overlap rate. Fixed via `normalize.translit_cyrillic()` + a transliterated-boilerplate
   stoplist in `match.GENERIC_NAME_TOKENS`; the health line now counts `name_norm`. Rule:
   **a diagnostic must report the MATCHER's view of the data, never the data's own.** Only
   Ukraine + Kazakhstan OSM carried Cyrillic (GEM's own columns are 100% Latin); both re-run
   2026-08-14 and **no bucket count moved in either** — the gain is corrected "closest GEM"
   attribution (49 records in Ukraine, 2 in Kazakhstan), because the OSM manifest weights
   `name` at only 0.10 against geometry 0.45. That is the correct reading, NOT a reason to
   retune weights. Ledger + A/B:
   `notes/escalation-2026-08-14-cyrillic-names-invisible-to-matcher.md`.
   **OSM is a second registered source and runs by default in the `deep`
   preset**; unmatched reference records are bucketed by `disposition`
   (ROUTE_FOR_EXISTING / FRAGMENT_OF_EXISTING / NEAR_MISS / DISCOVERY_CANDIDATE) on the
   standing principle that a reference route is presumptively real pipe.
   **`osm_id_key` was not unique until 2026-08-26** — `fetch_overpass._stitch()` keyed each merged
   part by which source ways touch it, so disjoint parts of one way group collided (62 features
   across the 10 registered extracts; worst by distance uz 6/865.8 km, kz 7/711.7 km, ua 26/251.7 km).
   `ingest.py`'s `#2`/`#3` suffixing meant **no geometry was lost and no committed finding is
   falsified** — what broke is *identity*, since that suffix is assignment-order dependent, so the
   manifest's `provenance.oid_field` could not survive a re-scrape. `_disambiguate_keys()` appends a
   geometry-derived blake2s discriminator **only to colliding keys**, leaving every unique key
   byte-identical; **so re-fetching a country moves nothing but unstable ids, and no re-run is owed.**
   Only Uzbekistan has been re-fetched (it had no committed run); every other extract keeps its
   current keys until next fetched. Writeup: `sources/osm/NOTES.md`.
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
  not a phantom. **+ §8 route creation 2026-07-31: all 34 exactly-`no route` gas
  PIDs — the 15 candidate GeoJSONs were APPLIED 2026-08-03 (authorized; routes merge
  `ab2e6bbd` + 75 sheet cells, RouteCreator `CB`, backup in `notes/`,
  `audit_route_sync.py` clean), including the three routes-repo WARNs (P2233/P4068
  length undershoot, P7434 geocoder false match on a second Mahmudiyah) and P2231
  despite its stricter internal-gate length FAIL; 19 corridor partials still open;
  workbook `…_20260731_1525_ET_iraq-gas_route-creation.xlsx`.** + oil open items — Grand Faw third line,
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
  10 `DISCOVERY_CANDIDATE`. **+ §8 route creation 2026-07-30: all 55 no-route gas rows —
  37 candidate geojsons APPLIED same day (routes-repo merge `0c8c01f4` + authorized
  sheet write of RouteNotes/RouteCreator/Route [ref] + RouteAccuracy, backups in
  `notes/`; South Valley RouteType flipped by Baird), then a same-day retry pass on
  the 18 partials resolved + APPLIED 3 more (P8013/P8014/P8021, routes merge
  `241ef5aa`, backup in `notes/`); 15 corridor partials still open; workbooks
  `…_20260730_1239_ET_…route-creation.xlsx` + `…_1415_ET_…route-creation-retry.xlsx`.
  + §8 ENTSOG pass 2026-08-04/05 off the new `sources/entsog/` SYSCAP 2026 vector
  layer (Egypt accuracy median 4.2 km → medium cap): **ALL 23 candidates APPLIED** —
  10 replacements for very-low/low rows 2026-08-04 (authorized; routes merge
  `752ab5d3`, sheet via the NEW `apply_route_candidates.py --replace` mode, 50
  cells; P0436 withdrawn, Baird re-graded its row to medium) + the 13 no-route
  candidates 2026-08-05 (authorized; routes merge `a2fa41c8`, 65 cells, QC 11 pass
  / 2 WARN included). RouteCreator CB, backups in `notes/`, `audit_route_sync.py`
  A/B/C = 0; 4 documented gate FAILs applied deliberately (3 = suspected
  sheet-length defects).
  **+ §8 pass 2026-08-07 on researcher `NA`'s ten NEWEST rows (P8050–P8059, all
  `no route`): 9 candidates + 1 partial, since SUPERSEDED (see the 08-10 pass below);
  routes-repo QC 4 pass / 5 warn / 0 fail. Recency came from walking daily snapshots
  for first-non-blank `PipelineName` — P8000–P8099 were pre-allocated blank on
  07-15, so PID order is NOT a recency signal; and `NA` is in pandas' default
  `na_values`, so read with `keep_default_na=False, na_values=[]` or her 423 gas
  rows vanish. Ten-row data-quality escalation →
  `notes/escalation-2026-08-07-egypt-gas-new-rows-citations.md`: 5 of 10 rows cite
  EGAS Annual Report 2018 for facts it does not contain, six lengths conflict with
  their own endpoints, P8058 likely belongs to the P3930 (New Administrative
  Capital) family not P8040, P8055's "Trans Gulf … II" lineage to P8013 is false.
  Routes to Update, not §8. **The citation finding was WITHDRAWN 2026-08-10: `NA` was
  identifying these lines VISUALLY off the GASCO national-grid MAP on printed p.35, so
  full-text search was the wrong test. The map annotates segments `NN" NN km`; P8052/
  P8053/P8057/P8059 match it exactly and 6 of 7 rows match on diameter. Survivors are
  narrow: P8051's 32" conflicts with the 65 km label's 42", and P8050 needs a
  duplicate-check vs P7567. OUR retracted claims, both 08-10: "P8059 = 7.5 km decimal
  misread" (the map raster is 200 ppi, so the 600 dpi page render upsampled ~3× and
  blurred an inter-glyph seam into a dot — the label reads `24" 75 km`, so P8059's
  *endpoints* are what's wrong; never read a fine detail off an upsampled render —
  check `pdfimages -list` for the native raster size first), and "P8052/P8053 are
  anchored to the wrong cement plant" (WITHDRAWN — OSM has exactly two Sinai cement
  works and both are in the Jabal Lubna district we already used, and the map's own
  georeferenced `Sinai`/`Cement` captions land on them). Gas tab re-sorted
  08-10 (P8051 4322→4313); P8058 renamed per the memo. Rule of thumb: a report cited for
  a pipeline is not "unsupported" until its MAPS have been read, not just its text.**
  **+ §8 pass 2026-08-10, THE one open route surface for Egypt gas — Baird reset the bar
  to "every Egypt pipeline should have at least a very low resolution route", which
  relaxes PRECISION (a settlement/facility anchor pair is what `very low` means) but not
  SOURCING. All 34 routeless rows (33 `no route` + P8067 blank) of 115: **24 candidates
  APPLIED same day (authorized, both halves — routes merge `d0d8ba77`, 7 of them replacing
  pre-existing `geometry: null` placeholders; sheet 120 cells, RouteCreator CB, backup in
  `notes/`, `audit_route_sync.py` A/B/C = 0) + 10 partials still open**, workbook
  `…_20260810_1800_ET_…route-creation.xlsx`,
  internal gate 24/0, routes-repo QC 17 pass / 7 warn / 0 fail. It SUPERSEDES the 08-05
  pending + 08-07 workbooks and the July/08-04 staging dirs — all moved to
  `batches/egypt-gas/archive/`, so `staging/` now holds exactly one route dir. Newly
  resolved anchors did the work: Abu Madi via GeoNames (P8022/P8023/P8049), the TWO
  distinct GEM "Ameriya" nodes 10.2 km apart (P8065/P8066), the OSM El-Tina station
  (P8026/P8035). P8035 is NOT a duplicate of P8013 (July claim withdrawn) — it is the
  Port Said UGDC line. P0477 South Valley (parent network row merged from its own six
  applied segment routes) was a CONVENTION question — "add all candidates" answered it,
  applied at `high`. Applied despite unresolved lengths (corridors right): P8020, P8035,
  P8057, P8059. P8063/P8065/P8066 have an empty `Route [ref]` BY DESIGN — internally
  anchored off GEM's own geometry, which rule 1 forbids citing; provenance in RouteNotes.
  **+ two rows NA added after that batch was scoped, both routed and APPLIED 2026-08-11**
  (`staging/route-creation-20260811/`, both `very low`, QC PASS, 5 cells each): **P8068**
  El Noubareya–Qusina (merge `1a2c64b5`) and **P8069** Bader3–Ameriya (merge `950df475`).
  Both arrived with a **blank `RouteAccuracy`, which MEANS `no route`** — a new row whose cell
  is not filled in yet gets routed and applied like any other (Baird 2026-08-11); encoded in
  `apply_route_candidates` (blank passes the guard unless `RouteType` is already `Mapped`) and
  in `audit_route_sync` B/D. **Egypt gas is now 117 rows: 107 routed, 10 unrouted, and the 10
  are exactly the known partials.** **+ one of those partials, P7589 (Faramid), RESOLVED
  2026-08-11 and STAGED NOT APPLIED** (`staging/route-creation-20260811-p7589/`, QC PASS,
  36.9 km vs 38.0, `low`): Faramid is a development lease (code 94, East Obaiyed) on the EUG
  concession map with five wellpads on imagery, and the "159 km false match" that blocked it
  is withdrawn — **"Badr El Din Company" is BAPETCO the OPERATOR, not the BED field**, so the
  end anchor is the Obaiyed gas plant 35 km west; geometry follows the existing Obaiyed export
  ROW (OSM way/545729460). Applying it makes Egypt gas 108 routed / 9 unrouted.
  Egypt OIL is effectively done — 45/46 mapped, P7326 legitimately null-placeholdered;
  the one defect is **P7338**, real geometry but `RouteType = Unavailable`, a three-way-
  sync violation fixable with `--backfill-route-type`.**
  **+ deep sweep + research pass 2026-08-27 — gas (40 rows) AND oil (ALL 46, the
  tracker's FIRST-EVER Egypt oil sweep), staged not applied. SEVEN files to work**, the
  deep sweeps do NOT subsume the recons: `…_20260827_1326_ET_egypt-gas_deepsweep.xlsx` + `…_1343_ET_egypt-oil_deepsweep.xlsx`
  + `…_1326_ET_egypt-gas_route-creation.xlsx` + `…_20260827_1108_ET_egypt-{gas,oil}_reconciliation-{gulfpub,osm}.xlsx`.
  Gas is 40 of 127 rows because the 88 carrying staged-unapplied July/August research are
  `--exclude-pids`'d — **research legs only, never the recon leg**. Totals: gas 266 ref
  records (46 `REFS_ADDED` / 202 `REVERIFIED` / 18 `UNRESOLVED`) + 9 fills + 80 validity;
  oil 444 (172/201/71) + 14 fills + 110 validity.
  **The headline is a citation-FORM defect, not a research gap:** 106 `[ref]` cells on 20
  Egypt rows cite an `egyptoil-gas.com` **navigation surface** — a mutable site-search page
  (65 gas cells) or page 7 of a paginated category index (41 oil cells) — instead of the
  article, which is live, verifier-clean and supports the values (EOG Newspaper Sept 2020
  Issue 165, *"Gulf of Suez, Eastern Desert and Sinai: Egypt's Crude Oil Squad"*, two tables
  covering 7 crude + 7 gas lines). The correct form is already in use on the same tab (69 gas
  cells / 21 rows) and **both forms sit on P8013 at once**. Recovering it yielded 26 oil + 15
  gas ref upgrades and 14 fills, incl. P8084's `Diameter` (blank on the sheet) and closure of
  **9 pre-existing orphan `[ref]` cells** on P7975–P7979.
  **The method lesson is ours: findings do not propagate across a fan-out.** In SEVEN places
  an agent asked for exactly the document a sibling agent in the same run was reading, and
  **two of those recommended destroying real rows** — P8084 (*"drop/relabel as an
  unverified/GEM-only entry"*; the source names it and its 150 km matches exactly) and P8018
  (*"retire the row"* / fold into P8002's family; the source matches name, both endpoints AND
  diameter). Both WITHDRAWN in staging with the originals preserved. Neither agent was
  careless — both tested the wrong document (EGAS AR 2018). **Rule: no `existence` concern
  ships without first grepping the run's other shards for the row's name and endpoints.**
  Surviving existence concerns are real: P8010, P8042.
  **A crossed recon gate is a claim until you read what crossed it** (Uzbekistan, again):
  oil GulfPub reads **57.5% status conflicts** and it is an artifact — 21 of 23 are the single
  row **P7326** matched to 21 unrelated *Gulf of Suez offshore* lines because it is blind on
  every separating axis (`no route`, **both endpoints blank**), leaving diameter+length alone;
  all 21 are `yellow`, none `green`. Real oil conflicts: **two** (P7315, P3689). Gas GulfPub's
  6 / 44 = 13.6% are 6 genuine row-level questions. No additions gate crossed (15/20/28/27).
  Both OSM runs healthy, and **`ROUTE_FOR_EXISTING` = 0 in both** — OSM offers no geometry for
  any routeless Egypt row. **Generalisable: a row with no route AND no endpoints is a
  false-match attractor for any attribute-axis source** — fix by giving it endpoints, never by
  retuning weights.
  **Length pattern, flagged not applied:** this one document disagrees with four rows and the
  sheet is longer EVERY time (P7341 340/280, P8016 256/245, P8018 165/160, out-of-scope P3659
  235/185) — reads as a measurement-convention difference, to settle once for the family.
  P7341's 340 km is independently backed by a live Youm7 2019-05-26 article, so that one is a
  genuine two-source conflict. Also: **P8013 is called "Trans Gulf Gas"**, never "Trans Sinai",
  staged as an `OtherEnglishNames` alias NOT a rename (the family is segment-numbered). The
  report's *"operated by the Petroleum Pipeline Company (PPC)"* attaches to **SUMED alone** —
  it reads like a blanket attribution for all eight lines and would be wrong. Rule 1 verified
  clean: 0 GEM-surface URLs in any `[ref]` cell across all 173 Egypt rows.
  **Routes (the ask's second half):** 21 routeless gas rows (11 blank `RouteAccuracy` + 10
  `no route`; blank MEANS no route) → **5 candidates + 15 partials**, all 5 PASS
  `validate_route_candidate.py`. The 21st, P7589, deliberately NOT re-drawn — its candidate is
  already staged from 08-11 and re-drawing would stage a competitor for the same PID. The 52
  rows at `very low` already have geometry, so out of scope. Oil has exactly one routeless row,
  **P7326, NOT DRAWN** — one endpoint only, the other inferable solely from GEM's own geometry,
  which rule 1 forbids citing.
  **Harvest coverage, and a correction to how it is measured:** 36 of 90 harvested
  citations were never opened by the harvest path — but **4 are also the row's own
  `current_ref`**, read through ref *verification* instead, so the honest figure is **32**.
  Subtract already-cited URLs before reporting harvest coverage, or the metric credits the
  leg with less reading than it did. Screened: **11 live / 7 confirmed 404 / 8 blocked
  (403-401-502) / 4 network / 2 rejected as navigation surfaces** — those last two
  (`google.com/search?q=…`, `petrojet.com.eg/view/company/page/6`) are the EOG defect
  arriving by a different route, since **the harvester takes whatever a wiki page footnotes
  and wiki pages footnote search surfaces** — screen harvested URLs for index-ness, not just
  reachability. `wepco-eg.com` restructured: three genuine 404s (P3689/P3691/P3693), the only
  harvested sources here confirmed *gone* rather than merely unreachable. `bit.ly/2oFzXCm`
  verifies live but a shortener is never a citable ref — resolve it or drop it.
  **P5121's `StartYear1` is a THIRD instance of the cross-leg blindness, caught in QC:** the
  sheet's 1977 is the SUMED *system* year (both sources behind it date the system, so neither
  can corroborate a segment cell) while sumed.org separates Pipeline 1 = Jan 1977 from
  Pipeline 2 = Oct 1978, and **P5121 is Pipeline 2**. The finding already existed as an aside
  inside P0530's *duplicate* record while P5121's own record asserted *"StartYear all
  corroborate"*. Now staged as a `concern/spec` on P5121 with that claim carved out; oil
  workbook rebuilt at `1343_ET` (validity 110 → 111, every ref class unchanged). Also:
  `ar.wikipedia`'s SUMED **infobox says 30″ against its own body's 42″** — cite the prose.
  Escalation:
  `notes/escalation-2026-08-27-egypt-eog-navigation-surface-citations.md`):**
  `docs/country_notes/egypt.md`.
- **United States (oil: Delaware Express + Permian Express batches staged not
  applied; deepwater-export open item):** `docs/country_notes/united-states.md`.
- **Pakistan (gas: first-ever full pass 2026-08-07, staged not applied. **THREE files to
  work**, the packet does NOT subsume the recons (`recon_actions=0`):
  `…_20260810_1112_ET_pakistan-gas_handoff-{actions,evidence}.xlsx` +
  `…_20260807_1530_ET_pakistan-gas_reconciliation-{gulfpub,osm}.xlsx`. The country's
  defining fact is **provenance**: 51 of 70 rows are ONE July-2023 bulk load off two MAP
  files, so 362 `UNRESOLVED` ref units are the correct outcome and the 16 `existence`
  flags track segment obscurity — never delete a row off one. **The SNGPL asset-register
  crosswalk (2026-08-10) resolves that cohort**: SNGPL's own audited *"TRANSMISSION SYSTEM
  As at June 30, 2018"* (Annual Report 2018, 270 sections, parse reconciles to the printed
  grand total) accounts for **49 of the 51 rows** at two-decimal precision → all five
  residual existence questions and all three redundancy clusters CLOSED, staged as 98
  ref-only units with no value changes. Two items survive: **P4074** (register 52.23 km vs
  sheet 55.23; direction unknown — don't apply blind) and **P5486** (the one unaccounted
  row). Untouched by it: the 8 SSGC rows and all 60 `operating`-with-no-`StartYear1` rows.
  gem.wiki 403'd through the whole 08-07 pass; **fixed and both wiki legs re-run 2026-08-10**
  (`WIKI_UA` — the WAF needs a UA leading with the `baird-wiki` token, kept byte-identical to
  `goit-ggit-data-ops/gem-wiki/gemwiki.py`), so the packet carries 99 real records
  (69 SHEET_SUSPECT / 24 WIKI_UPDATE / 6 WIKI_STALE_VS_STAGED) instead of 70 UNPARSED — but
  **68 of the 69 SHEET_SUSPECT are one question**, blank `Operator`, which is the GGIT norm
  (filled on 1,464/6,462 rows tracker-wide) and not a Pakistan defect. Oil (4 rows) not
  swept):** `docs/country_notes/pakistan.md`.
- **India (gas: first-ever full pass 2026-08-10, staged not applied. **FOUR files to work**,
  the packet does NOT subsume the recons (`recon_actions=0`), all stamped `20260810_1851_ET`:
  `…_india-gas_handoff-{actions,evidence}.xlsx` + `…_india-gas_reconciliation-{gulfpub,osm}.xlsx`.
  **India is the INVERSE of Pakistan** — its rows are actively maintained, coherent and real;
  what they lack is **citations** (~9% of ref cells, 149/1,650), concentrated on *operating*
  rows (34 of 35 carry no PNGRB ref) while in-dev rows are well cited (27/28). **So an
  `UNRESOLVED` is a WEAK result here, not the correct outcome** — a second ref-gap pass moved
  the operating leg 116 → **251** `REFS_ADDED`. Do NOT carry Pakistan's heuristics across.
  The unlock is the **PNGRB NGPL MIS register** (`scripts/parse_pngrb_ngpl_mis.py` +
  `crosswalk_pngrb_india.py`), which accounts for all 71 India-only rows and beats SNGPL's on
  three axes (regulator not operator; carries dates; splits operating vs under-construction) —
  but it is **common-carrier only** and is the de facto **ORIGIN** of GEM's capacity column
  (equal at two decimals on ~20 rows), so PNGRB + a company restatement is ONE origin.
  **India's duplicates are REGULATORY, not bibliographic:** authorisation number / sponsor /
  date holding constant across register editions while the NAME changes is dispositive — it
  confirmed one cluster and REFUTED 5 of 11. Twelve escalations, led by P0907 being a section
  of P0929 (~718 km double count), 107.00 MMSCMD stamped on five HVJ rows, GulfPub crossing
  BOTH gates (84 additions / 30% conflicts), and `Operator` blank on 74/75 — **a genuine gap,
  not the tracker norm** (18.2% of GGIT gas rows carry one; the `Operator [ref]` column is what
  reads ~1%). The thin OSM overlap (1 of 75) is **granularity, not a matcher defect** — health
  line clean, no `MATCH_QUALITY` warning, India is the healthiest OSM extract in the registry
  (44% named); do NOT add a `geoarea_weight` override. Oil (26 rows) not swept):**
  `docs/country_notes/india.md`.
- **Kazakhstan (gas: first-ever full pass 2026-08-11, staged not applied. **THREE files to work**,
  the packet does NOT subsume the recons (`recon_actions=0`):
  `…_20260812_1255_ET_kazakhstan-gas_handoff-{actions,evidence}.xlsx` (rebuilt from the 08-11
  `1145_ET` pair after the cluster-A reversal below — don't work the old one) +
  `…_20260812_1344_ET_kazakhstan-gas_reconciliation-gulfpub.xlsx` (**RE-RUN — the `20260811_1001`
  workbook is archived; the multi-country filter defect had hidden HALF this country's
  reference records, 32 of 63, and 15 of the 31 `gem_only` "no reference counterpart"
  findings were artifacts**) + `…_20260814_0120_ET_…reconciliation-osm.xlsx` (**RE-RUN after the
  Cyrillic name defect, `20260811_1043` archived — but NO finding moved**: 2/110/50 identical, two
  corrected "closest GEM" guesses only). The country is **multi-string trunk systems with
  NO public line-wise register** — the best line-wise source (KMG's AR gas-transportation table)
  itemises only the 8 major *systems*, i.e. exactly the aggregates that are the defect, so in six
  systems one system figure is restated on every string and an honest `UNRESOLVED` on a per-string
  spec is often the CORRECT outcome (the inverse of India). **Cluster A is the country's method
  lesson:** it had the aggregate-vs-segment signature (P3948's trace = P5777 + P5783 exactly) AND
  the sheet's lengths agreed to 0.20 km, and the double count was still **REFUTED** — two
  independent official sources name P3948 as its own 720 mm / 149.1 km trunk parallel to a
  separately-named 529/530 mm one, and segment traces cut from a parent produce the union identity
  for free. Our fold recommendation is WITHDRAWN, as are the "mislabelled numerals" and
  "529-is-a-typo" findings; **only sourcing decides duplication here.** Two verifier rules:
  `adilet.zan.kz` serves an incomplete TLS chain, so `insecure_tls: True` means the page IS LIVE
  (our defect hit 51 of 105 ref cells with zero real 404s), and its `#z250` anchors land in
  Appendices 5–7, which are MAPS — a full-text miss is not evidence a ref fails. Both recon gates
  crossed and both empty in fact (GulfPub's 14.8% conflicts = two segment-vs-network artifacts;
  OSM's 110 additions = 55 explicit `FRAGMENT_OF_EXISTING` + 55 mostly-stub candidates, health
  line clean — do NOT add a `geoarea_weight` override). Open: P7819's three-way route-sync
  violation, P5776 the one operating row at `no route`, cluster F (P5927/P5928 byte-identical),
  P3945's `Osh` province, the CA–China 1,833 km question. Oil (41 rows) not swept):**
  `docs/country_notes/kazakhstan.md`.
- **Malaysia (gas: first-ever full pass 2026-08-12, staged not applied. **FIVE files to work** —
  the packet does NOT subsume the recons (`recon_actions=0`) and with THREE sources the recon
  surface is the larger half: `…_20260812_1344_ET_malaysia-gas_handoff-{actions,evidence}.xlsx`
  + `…_20260812_1343_ET_malaysia-gas_reconciliation-{gulfpub,osm,malaysian-gas-map}.xlsx`
  (+ the `…_1344_ET_…deepsweep.xlsx` per-leg workbook, carried into actions). **The batch's
  headline is a SCOPE RULING, not a data defect**: GEM tracks **5** Malaysian gas rows (vs
  Indonesia 50 / Australia 151 / Thailand 34) while three independent sources describe ~150, and
  all three crossed the >30-additions gate (GulfPub 51/41 disc., Malaysian Gas Map 67/65, OSM
  29/8). The cross-tracker argument is the sharp one — **GOIT already carries 5 Malaysian OIL
  rows (P7908–P7912, IM, Feb 2026) on the same offshore corridors GulfPub proposes on the gas
  side**, so excluding the gas feeders tracks half of one physical bundle. Nothing is staged as
  Discovery pending that ruling; if the answer is "out of scope", write the inclusion rule into
  the country note. **The registry's first digitized document** (`sources/malaysian_gas_map/`,
  MGA 2022 vector wall map) debuted here — labels provably unreliable, so it corroborates
  CORRIDORS only. Two of the three runs are `MATCH_QUALITY` null runs (0 overlaps), and
  **OSM is NOT independent here** — P1065/P1066 cite `openinframap.org`, an OSM render, so the
  92% containment is the null run's diagnosis and carries zero corroborative weight (rule: read
  `Route [ref]` before crediting a geometry source). Open: P1066 status (GulfPub splits the
  512 km line and calls 386.2 km of it closed, summing to 498.9 km — GEM says wholly
  `operating`, no `Status [ref]`, last touched 2023), **P7105** (the one row no source
  corroborates; its 70 km is unspannable by its own endpoints — P1065's route ends at the Johor
  Bahru Causeway, 5.8 km from Attap Valley ORF — so it is an existence/duplicate question, NOT a
  length fix), P1066's `Operator` (the batch's only value change, medium, and **PGB is an
  equally defensible reading**), and P1067's route (redraw via Sandakan; 662 km is right).
  P1065's 0.46 length ratio is network-vs-mainline granularity, closed with no change. A blank
  `Operator` here IS the tracker norm (22.53% filled overall / 18.44% gas) — do not import
  India's reading. Oil (5 rows) not swept):** `docs/country_notes/malaysia.md`.
- **Ukraine (gas: first-ever full pass 2026-08-15, staged not applied. **THREE files to work** —
  the packet does NOT subsume the recons (`recon_actions=0`):
  `…_20260815_1946_ET_ukraine-gas_handoff-{actions,evidence}.xlsx` +
  `…_20260812_1409_ET_…reconciliation-gulfpub.xlsx` +
  `…_20260814_0120_ET_…reconciliation-osm.xlsx` (re-run after the Cyrillic name fix; **no
  finding moved**, 49 corrected "closest GEM" attributions only). The country's defining fact
  is an **empty citation base, not empty facts**: **34 of 1,034 `[ref]` cells are filled —
  3.29%**, 2nd lowest of the 52 scopes with 20+ gas rows, and 17 of the 22 refs on operating
  rows are dead links. `Length [ref]` and `Capacity [ref]` are each filled on **exactly one**
  of 47 rows — and length and capacity are precisely what this pass found wrong, repeatedly.
  **So calibrate the INVERSE of Kazakhstan:** there an `UNRESOLVED` on a per-string spec is
  often correct; here a blank usually means nobody looked, and the legs moved a large block
  off `UNRESOLVED` once actually worked. Read the 126 `UNRESOLVED` units as *unfinished*.
  The unlock for the Soviet-era trunks is **VNIPItransgaz's "Основные объекты" table**
  (`vtg.com.ua/experience/main/gts.html`) — live URL a genuine 404, **Wayback capture serves
  the whole table**, sourcing seven ref units; our earlier "404 ⇒ unsourced" reading is
  WITHDRAWN. **Its trap: the name cells carry `rowspan`s**, several lines under one heading
  mapping in order onto the rows beneath — that is what produced P0777's 1,112 km (522 km and
  590 km are two DIFFERENT lines, summed). Open: P7817/P7818 three-way sync violation (real
  geometry, `RouteType` still `Not mapped` — the only two out of sync); cluster A confirmed
  duplicate at 399.90 km; P3381/P3382 sharing ONE over-drawn geojson that is not their
  corridor; P1471's `StartCountryOrArea` (**Novopskov is in Luhansk Oblast, UKRAINE** — the
  route is right, the country columns are the defect); P1457's 516 km being the whole
  Rostov–Taganrog–Zhdanov system; P1773 carried as LIVE in Transgaz's own PDSNT against GEM's
  `cancelled`. Occupied-territory operators (P1488/P7817/P7818) are **deliberately**
  `UNRESOLVED` — GTSOU is affirmatively wrong for pipe laid by the occupying power. Gotchas:
  `utg.ua`/`tsoua.com` 403 (block, not deletion), `moldovatransgaz.md` fails TLS (use the
  `mtg.md` mirror), `energybase.ru` serves a 200 block page, Ukrainian routes are 2–5 vertex
  **schematics** so a drawn span is a LOWER BOUND, and geocoder false matches are the dominant
  route defect (P0778 resolved to Komárno **Slovakia** — corrected, its 80 km is vindicated).
  OSM's 1,003 additions cross the gate on volume alone and are a **scope** mismatch, not a
  Discovery signal — 815 of 1,004 features are sub-1 km distribution stubs. Oil (20 rows) not
  swept):** `docs/country_notes/ukraine.md`.
- **Uzbekistan (gas: first-ever full pass 2026-08-26, staged not applied. **THREE files to work** —
  the packet does NOT subsume the recons (`recon_actions=0`):
  `…_20260827_0931_ET_uzbekistan-gas_handoff-{actions,evidence}.xlsx` (rebuilt 2026-08-27 to carry the
  13 escalations — the `1412_ET` and `1419_ET` builds are archived and superseded, don't work them) +
  `…_20260826_1350_ET_…reconciliation-{gulfpub,osm}.xlsx`. Ref work
  on the 18 in-scope rows: **84 `REFS_ADDED` / 34 `UNRESOLVED` / 2 `DEAD_LINK`** (+38 reverified), 41
  open decisions, 43 concerns, 14 mechanical flags.
  The country's defining fact is that **13 of its 31 gas rows ARE Kazakhstan's rows** — a transit
  country's trunks are ONE row that both `--country` scopes select, so re-researching them stages
  contradictory records on the same sheet cells and the last workbook pasted wins silently. Baird
  set scope to the **18 domestic rows** (31 rows / 283 units → 18 / 152, 78 `HAS_REF` / 74
  `MISSING_REF`), enforced by the new `build_ref_worklist.py --exclude-pids` flag off
  `batches/uzbekistan-gas/carried_from_kazakhstan.txt` — **derived from Kazakhstan's
  `staged_resolutions.json`, never hand-typed**, and every PID confirmed to carry a real staged
  record first. Two consequences: those 13 rows now **depend on the Kazakhstan batch being applied**
  (until then neither batch researches them — the packet must say so), and **the exclusion stops at
  the research legs — the recon leg keeps all 31 GEM rows** or the trunks' reference counterparts
  re-bucket as `DISCOVERY_CANDIDATE`, manufacturing phantom additions for pipe GEM already tracks.
  §9 step 3 is consequently EMPTY (P0740 was the only `cancelled` row and it is one of the 13).
  **The wiki-ref trap is the sharp part of Baird's ask:** 18 rows map to 11 pages, so a harvested URL
  is a candidate for the unit *(ProjectID × ref column)* and earns the cell only when the page names
  that segment's own value — P6933/P6934/P6935 (`SegmentName = Mubarek-Zirabulak I/II/III`) point at
  the BTBA page **whose own parent rows P0739/P5810 are two of the excluded 13**, so its citations are
  about the parent trunk, not the strings. Link rot measured twice: **39 of 78 existing filled ref
  cells carry a dead/missing link — exactly half** — and 118 harvested URLs → 80 live / 14 true
  404-410 / 14 blocked (NOT deletions) / 8 timeout-DNS-5xx. Gotchas: **Uzbekistan is the THIRD
  Cyrillic scope** (Uzbek is Latin but OSM's 2 named features are Russian, so `translit_cyrillic` is
  load-bearing); `utg.uz/ru/about/history/` is a confirmed 404 whose **Wayback capture
  `20260314231446` exists and is UNREAD** — `web.archive.org` content serving was unreachable all day
  2026-08-26 while `archive.org`'s API answered in 0.5s, which is a network condition and **not
  evidence about the source**; `Operator` is not on the GGIT gas tab (OO tab, 13/31 filled,
  `Operator [ref]` 0/31). OSM `gas_uz` registered with **no `geoarea_weight` override** deliberately —
  29/31 GEM rows routed, 16 `high`, so the dead-axes condition does not hold and `MATCH_QUALITY` on
  the name axis alone is a true report, not a tuning signal. **Its ingest surfaced a registry-wide
  defect in OUR code, fixed the same day:** `osm_id_key` — the manifest's `provenance.oid_field`, i.e.
  the whole basis of cross-scrape identity — **was not unique**, because `_stitch()` keyed each merged
  part by *which source ways touch it*, so disjoint parts of one way group collided. Uzbekistan was the
  worst-hit extract by distance (6 features / 865.8 km; one key covering 618.01 + 144.95 + 25.49 km),
  Kazakhstan next (7 / 711.7 km), 62 features across the 10 registered extracts. **No committed finding
  is falsified** — `ingest.py` was already suffixing `#2`/`#3`, so no geometry was lost — but that suffix
  is assignment-order dependent, so identity across scrapes was unreliable. `_disambiguate_keys()` in
  `fetch_overpass.py` now appends a **geometry-derived** blake2s discriminator, and **only to keys that
  actually collide**, so every already-unique key is byte-identical and re-fetching a country moves
  nothing but unstable ids. Uzbekistan re-fetched immediately (no committed run to move): 124 features,
  geometry set identical, 113/124 keys unchanged, warning gone. **Every other extract keeps its current
  keys until it is next re-fetched** — no re-run is owed. Writeup: `sources/osm/NOTES.md`.
  **The pass's own findings.** `Operator` RESOLVED for 8 of 9 rows at **medium, deliberately not
  high** — no document names any of these pipelines together with its operator, so per-line
  attribution is inference from a sourced sole-operator regime (Decree 4388 of 9 July 2019, Uztransgaz
  as *"yagona operator"*) plus endpoints that are MGQB directorate seats. **P2698 must NOT be
  defaulted to Uztransgaz** — two independent signals make it the odd row out (no directorate covers
  Surxondaryo/Sherobod/Termiz/Denov/Qarshi, and its own `Owner1` is `Uzbekneftegaz`). The
  Cyrillic/Latin `Operator` split on P6933–P6937 is the SHEET's inconsistency, not ours (our staged
  values mirror it) — 5 attribution concerns, not auto-applied, since P6937's multi-party string needs
  a human split. Both border flags resolved and **neither warrants a country-column change**: P4071's
  Tajik crossing is a 2-vertex-chord artifact (redraw), and P6936/P6937's Afghan vertices at 14–36 km
  depth are too deep for Amu Darya slop (only 0.77 km is plausible) — **do NOT add Afghanistan**.
  **Both recon gates crossed and the conflict gate is EMPTY in fact:** GulfPub's 9/48 = 18.75% is all
  one disagreement on two rows (P6963/P6964, `construction → operating`), 0/33 = 0.00% excluding them,
  caused by P6964's off-corridor route inflating `LengthEstimateKm` to 111.29 km — **fix redundancy
  cluster E and the gate dissolves**; OSM's 124 additions crosses >30 on volume alone and is a SCOPE
  mismatch (69 sub-1 km stubs, 52.6% of mileage within 2 km of a GEM vertex). A `geoarea_weight`
  override was **REFUSED on measured evidence**: at 0.30 it yields 4 overlaps of which 3 are
  manufactured (a 1.625 km and a 0.036 km stub each "corroborating" the same ~350 km row at route IoU
  0.029/0.027, clearing on `s_geoarea = 1.0` alone) — unlike `gas_iq`/`gas_pk` where stubs sit ON the
  corridor. **Two method defects of OURS, both caught by reconciling counts:** `web.archive.org`
  content is unreadable from a session by BOTH available paths (local curl times out, harness fetcher
  refuses) while the CDX API answers in 0.5s, so existence is provable and content is not — 11 units
  cite a capture, **5 rest on one alone**, and P6933's `Owner [ref]` had claimed a clean read at tier
  high with "Independent? yes" while the escalation recorded that capture as unread (corrected to
  existence-only, support now on its live `lex.uz` leg); and **`independent` was set `True` on 13
  single-source units** whose own notes said "single independent source" — the field means the rubric's
  ≥2-agreeing, not "independent of GEM", and it renders as the yes/no column a researcher trusts when
  deciding to paste (all 13 → `False`, 2 also high → medium; classes unmoved at 84/34/2). WebSearch hit
  its 200/200 session quota, leaving exactly two questions open for a fresh session: **P2698's
  operator** and **P6936's `StartYear1`**.
  Open calls: GulfPub's 74-records-vs-31-rows inclusion rule (additions landed at 26, just under the
  gate), Russian/Uzbek research-language capability, and whether to add the recoverable Wayback
  snapshots (a sheet write). **The Wikipedia policy gap is CLOSED (Baird 2026-08-27): gem.wiki is
  never a source, Wikipedia IS citable** — `source_roster.md`'s ban is withdrawn and replaced by
  citable-with-conditions rules (tiers as ONE secondary source; two language editions of an article
  are one source; an article whose own footnote is GEM cannot corroborate, since rule 1 is about
  self-citation not encyclopedias). No verifier change was needed — `BLOCKLIST_HOSTS` never listed
  it — so the ~36 live Wikipedia `[ref]` cells tracker-wide are legitimate.
  **The pass's own coverage gap, measured 2026-08-27:** the wiki harvest pulled 127 unique citations
  and **88 were never opened**, because the ref legs were written to satisfy each owed cell rather
  than to exhaust the harvested pool — a subagent stopped at the first sufficient source and never
  returned to the rest of the page's citations. 83 of the 88 sit on rows that still report
  `UNRESOLVED`, though 72 of those are on the two PARENT-TRUNK pages (49 Central Asia–China, 23 BTBA)
  whose citations describe the trunk and not the string, so declining them is right and only ~11 are
  real untested yield. Rule going forward: **the harvested pool is a worklist, not a lookup table** —
  a ref leg reports how many harvested citations it opened, and an unopened citation on a row with an
  owed cell is an open item, not a silent pass. All 90 were then screened through `url_verifier`:
  **55 live / 35 failed, of which only 12 are confirmed 404/410** — the other 23 are access failures
  the standing rule does not treat as deletions — so the pool is now a measured 55-URL reading list,
  16 of them off the parent-trunk pages. **But a reachability screen is not a read, and `utg.uz` proves
  it: its `/ru/press-service/novosti/…` section serves a SOFT 404** — the Yangiyer–Akhangaran press
  release 200s with 139,482 bytes and a nonsense sibling slug 200s with 139,384, neither carrying an
  article, while `/ru/invest/` 404s honestly for a bogus slug (so the behaviour is section-specific and
  cannot be inferred from the host). Prove a suspected soft 404 by fetching a nonsense sibling and
  diffing the bodies. Nothing needs un-staging (these were harvested candidates, never filled cells),
  but the one page that might have settled **P6963/P6964** is unreadable at the origin and Wayback
  timed out again, so that conflict stays open. The one page from the pool that WAS readable,
  `utg.uz/ru/invest/aktsii-i-dividendy/`, is real and dated (share capital at 01.04.2024: MoEF 51.7%,
  Uzbekneftegaz 46.78%) and is **declined on the unit rule** — it names who owns the COMPANY, not any
  pipeline. Oil (2 rows) not swept):**
  `docs/country_notes/uzbekistan.md`.
- **Nigeria (divestiture ownership sweep not started):**
  `docs/country_notes/nigeria.md`.
- **Israel (gas: INGL/TMNG-map ground-truth batch 2026-07-23 staged not applied —
  2 new rows P8001/P8003, 5 validation candidate edits, 5 route candidates
  (P2197 QC-fail); Ashdod-vs-Ashkelon landfall + P3620 Ashkelon-gap open):**
  `docs/country_notes/israel.md`.
- **China (gas: province-level program agreed 2026-07-29 — agent batches run AHEAD of
  MZ's province queue (they have routes/wiki + the trunk systems; cycle plan in
  gem-desk `research-cycles/ggit-2026-pipelines-update/`); scope via
  `build_ref_worklist.py --province` + trunk-exclusion regex; Guangxi deep-sweep pilot
  DELIVERED 2026-07-30 staged not applied. **+ Jiangxi grid v2 DELIVERED 2026-09-02 staged not
  applied — SUPERSEDES the 08-26 v1** (`…_20260902_1232_ET_china-jiangxi-gas_deepsweep.xlsx`,
  11 tabs, **ONE file to work**; v1's workbook + staging archived to
  `batches/china-jiangxi-gas/archive/deepsweep-v1-20260826/`, so there is exactly one pending
  state). Baird reset the scope ("include any trunk lines"): **44 rows** = all 41
  Jiangxi-terminus rows **plus** the three transiting national mainlines P4657/P4934/P4947 that
  v1 excluded; legs refs/fills/validity **+ status-review** (no OSM recon, no routes, no
  discovery). v1's 18 rows were **carried forward, not re-discovered** — prior `REFS_ADDED`
  re-keyed onto the fresh worklist (the tab re-sorted, all 18 moved -2), URLs re-verified, only
  the `UNRESOLVED` re-researched. 453 records, ref lane 411: **270 `REFS_ADDED` / 127 `UNRESOLVED` / 12
  `REVERIFIED` / 2 `DEAD_LINK`**, tiers 82 high / 175 medium / 14 low across **49 verified
  hosts**, + 26 validity + 12 status reviews (6 stale / 4 unclear / 1 change / 1 confirm) + 4
  fills. Gates
  B/D/E/F clean; A=1 (P5888 on `sohu.com` alone); C flags 33 `high`s whose second origin is one
  of six documents carrying 145 units between them — concentration, not a defect. Delivery note:
  `notes/delivery-2026-09-02-china-jiangxi-gas-deepsweep-v2.md`. **3.7% citation base
  (`HAS_REF` 6/162) — calibrate as India, not Pakistan:** a blank means nobody looked, so an
  `UNRESOLVED` is unfinished, not correct. **The cluster to adjudicate is P4778 ↔ P5861, and it
  arrived RECIPROCALLY** — two agents at opposite ends of the fan-out each filed a
  `__REDUNDANCY__` naming the other's row (identical Gao'an–Xinyu corridor, same StartYear);
  reciprocity is corroboration, so deliver it as ONE cluster. **Phase I vs Phase II is a
  grid-wide operator question, not a row defect** (CCXI credit-rating PDF splits the operator by
  phase; 23 phase-labelled rows = 15 I / 8 II, 3 `FuelSource` in tension) — it surfaced buried
  inside one `FuelSource [ref]` record's notes on an `UNRESOLVED` unit, the Egypt P5121 burial
  pattern, and was promoted to a cohort sentinel on P5862. Two aggregate-vs-segment defects
  (P4788 `SegmentCost` = all four Ganzhou South branches; P4928 `Capacity` = the WEP3 system) —
  but **P4934's 125 bn RMB is CORRECT**, that row IS the whole-system row, so read granularity
  before calling a system figure a defect. **An archive.org 429 is a RATE limit — the answer is patience
  INSIDE the session, not a later day or a different IP** (P5865/P5866, the batch's one
  "blocked" finding, and our reading of it — *"the limit is IP-level, both rows stay open"* —
  was WRONG). `jxgajc.com` no longer resolves in DNS, so the two CDX-confirmed captures
  (`20230902005946`, `20230902105154`) were the only route, and archive.org 429'd every path
  including its own CDX API for hours; a plain bounded retry loop (6 tries, ~6–8 s apart)
  returned 200 on BOTH within a minute. Not routes, so don't re-try them: `web.archive.org`
  has no AAAA record, `timetravel.mementoweb.org` returns 403, and IA login cookies change
  nothing (the first 200 carried an empty `Cookie` header). Yield (`batch_20_wayback_recovered.json`,
  26 records / 21 ref units): P5865's status is **stale** off its own new ref (竣工 Nov 2021 →
  `operating`, `StartYear1` 2021, medium — 竣工 is completion, not gas-in) and its
  `StartPrefecture/District` is **`Fengcheng`, not `Yifeng`**; P5865's capacity stays
  `UNRESOLVED` (the filing's 5×10⁶ Nm³/a is itself implausible against sister segment P5866);
  P5866 corroborated on eight values exactly, `StartPrefecture/District` filled → `Jiujiang`,
  and its **6.43× capacity outlier REFUTED and re-filed as a ROUTE defect** (geometry
  over-drawn against a documented 19.12 km branch — joins P5862 as a §8 redraw).
  `fzggw.jiangsu.gov.cn` recurs in the harvest — **Jiangsu ≠ Jiangxi**.
  Its 8 unresolved fills (v1) are **uncitable, not unknown** — every one sits on a row that
  already has route geometry, which rule 1 forbids citing but MZ can fill from. Read P4788
  first (`FuelSource` names WEP3 not Sichuan-Shanghai; its redraw coords were DMS-as-decimal,
  38.7 km off; 340.30 km vs 131.8 km between its own terminals leaves length AND route open).
  **The batch's method lesson is ours, not the data's:** three silent-loss defects, all found
  by reconciling counts rather than by any error — the harvester must run LAST (it writes
  `__VALIDITY__`, which `merge_deepsweep_shards` purges, so harvest-then-merge zeroes sentinels
  2→0 silently); `split_shards` must route fills **structurally** off the worklist's owed set,
  never off the `kind` tag; and a hand-confirmed false negative must be encoded
  `ok=true/contains_value=true` + note, because `ok=false` + prose is stripped by
  `verified_refs` and then honestly downgraded to `UNRESOLVED`, so found evidence reports as
  *no source found* (batch 03: 11 records zeroed, 31→45 refs kept). **v2 added seven more of
  ours, same family — all caught by reconciling counts, none by an error:** a carried FILL
  parked in a side file (`carried_fills.json` is written by the carry step and read by NOBODY —
  `build_ref_workbook` takes `pending_fills` from an *actions* packet, so on a standalone
  deep-sweep build v1's one real fill, P4788 `Pressure` = 6.30 MPa sourced, reached no tab;
  a carried fill belongs in the store as `class_in: FILL`, with the FRESH `sheet_row`);
  a shard emitting `sentinel:` instead of `ref_col:` (routing is keyed on `ref_col`, so two
  `__STATUS__` records would have gone to the ref lane and been dropped with one WARN — shard
  fixed and `split_shards` hardened to accept the alias); a verdict parser that rejected
  `Required status-review verdict: 'unclear'.` because the apostrophe was not a separator
  (7/4/1/2-blank → 7/6/1); and **citation FORM is now a structural gate** in
  `validate_shards.py` — prose written into a citation field, and a BARE HOST (a site root is a
  mutable navigation surface, the Egypt `egyptoil-gas.com` lesson) both fail the validator.
  The last three are the **silent-DUPLICATION / silent-MISRENDER twins** of that family, all
  three surfaced by the batch_20 recovery: (a) `split_shards` APPENDED every `__STATUS__`, so
  P5865 reached `Gas_StatusReview` with three contradictory verdicts side by side (`stale`
  inferred, `unclear`, then `change` once the blocked source was read) and nothing saying which
  was current — a row has ONE status, so it gets one verdict, last shard wins, supersessions
  reported (4 here); (b) **a proposed value carried on a ref-lane record never tints** —
  `_backend_view` colors values only from the FILL and STATUS lanes, so a correction written
  into a `Location [ref]` record printed on the paste surface looking like the sheet's own
  value, which is worse than invisible; re-file it as the pattern the workbook already supports
  (ref record keeps the CURRENT values, a `kind: FILL` twin on the same cluster carries the
  proposed one, `_merge_ref_unit` unions both records' refs) and key `validate_shards`'
  duplicate detection by LANE so the designed pair is a note, not a collision; (c) every
  `Gas_Validity` row shipped with **blank name columns** because
  `harvest_sentinel_findings` reads `pipeline_name` off the shard DOC while `split_shards`
  wrote `{project_id, resolutions}` only — the tab carrying a sweep's highest-value findings
  gave the reader a bare ProjectID (fixed at the cause in both scripts; 26/26 now named). **+ §8 route creation 2026-07-30: ALL 103
  no-route gas rows (incl. MZ's operating rows + P8028/P8029 per Baird) — 80
  candidate geojsons + 23 corridor partials, three batches/workbooks (Guangxi grid
  18+5, other grids 28+10 in the cross-province dir
  `batches/china-gas/staging/route-creation-grids/`, trunks 34+8); **routes-repo half
  APPLIED same day** (authorized; 79/80 merged, routes merge `3d943da2`; P3894 QC-fail
  excluded → reuse-P0758-geometry review) **+ sheet-side route columns APPLIED same
  day** (316 cells verified, backups in `notes/`); 23 partials + P3894 + review flags
  tracked in work Asana (gem-desk). **`RouteType` backfill 2026-07-31: that apply set
  `RouteAccuracy` but not `RouteType`, so all 79 merged rows still read `Not mapped`/
  `Unavailable` — repaired under authorization (79 cells verified, backup in `notes/`);
  China gas now clean per `scripts/audit_route_sync.py`.** **+ P8062 (MZ's Dalian–Shenyang
  Dalian Branch) staged 2026-08-10 as a `geometry: null` placeholder at Baird's request —
  `batches/china-gas/staging/route-creation-null-20260810/`. A null route is NOT mapped
  geometry: no sheet write goes with it, `RouteType`/`RouteAccuracy` stay as they are, and
  `RouteCreator` stays `MZ`.**; oil out of scope until post-cycle):**
  `docs/country_notes/china.md`.
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
