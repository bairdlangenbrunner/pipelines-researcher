# SOP — Reference sweep (fill & re-verify every `[ref]`)

Crawl every row and every ref-bearing data point in a country+tracker scope and, for
each one, reach the target: **≥2 links that both WORK (HTTP 200, no error) AND
corroborate each other AND contain the precise data point** being referenced.

- **Blank `[ref]` + filled value** → research and add corroborating source URLs.
- **Filled `[ref]`** → re-check the URLs still resolve *and* still contain the value.

Distinct from QC's link-rot detection: **QC *detects*, Ref Sweep *researches & stages*.**
QC's BroadSweep flags orphan refs (ref filled, value blank); the Ref Sweep fixes the
inverse (value present, ref blank) and re-verifies live refs. Both share the one ref-pair
model in `scripts/ref_pairs.py`.

The deep-research rules (source hierarchy, corroboration, independence) live in
`docs/GOIT_Pipeline_Research_Workflow.md` Phase 2 and `docs/reference/confidence_tiers.md`;
this SOP is the operational sequence.

## Inputs
- Scope: country + tracker (oil / gas). One tracker per batch.
- Optional `--status` filter (default: **all** statuses, incl. operating).
- Decision for the current program: **upgrade single-source data points to ≥2
  corroborating links** (a lone working source still needs a second, independent one).

## The ref-pair model (group-walk)
`scripts/ref_pairs.py::discover_ref_pairs` re-derives, from the **fresh header every
batch**, which value columns each `X [ref]` sources. A `[ref]` governs the run of value
columns since the previous `[ref]`, minus identity/derived/no-ref columns; when the ref's
name matches a column (exact/prefix) the cluster starts there. Known irregulars (flagged
`irregular:true` for reviewer sanity):
- gas `Location [ref]` sources **both** start and end endpoint blocks (one ref, 8 cols).
- gas `H2RepurposedKmOr% [ref]` → the H2 km/% cols.
- **Owner/operator refs come from a separate tab.** The tracker tab carries the `Owner`/`Parent`
  *value* but has **no `[ref]` column** for it. The real refs live on the **"Pipeline
  operators/owners" backend tab** (GID `1489950650`, header at CSV row index 1), which is
  **ProjectID-keyed** (same `ProjectID`s as the trackers) and has two ref cols whose `[ref]`
  **precedes** its values (opposite of the trackers): `Operator [ref]` → Operator block;
  `Owner [ref]` → Owner1..Owner11(+%). `build_ref_worklist.py` joins that tab by ProjectID
  (`--owners-csv`, default latest `GEM_operators_owners_snapshot_*.csv`; `--no-owners` to skip)
  and emits **two real ref units per in-scope ProjectID** (`tab:'operators_owners'`,
  `kind:'operator'|'owner'`), classified `MISSING_REF`/`HAS_REF` like any other unit — they go
  through the same research + verifier loop. The deliverable routes them to a dedicated
  **`<Cmdty>_OperatorsOwners`** paste-ready tab (ProjectID-keyed, ref-precedes-values), so Baird
  pastes each `[ref]` onto that ProjectID's row of the operators/owners tab — *not* a tracker
  row, *not* `ResearcherNotes`. Because the tab is ProjectID-keyed (not entity-keyed) the ref is
  per-pipeline; no entity-level de-dup. (`discover_ref_pairs` still emits a synthetic
  `kind:'owner'` placeholder for the QC BroadSweep, but the sweep drops it in favour of the join.)
  Full column layout: `docs/reference/gem_schema.md`.
- **Route/geometry is OUT OF SCOPE.** `RouteType`/`RouteAccuracy`/`RouteNotes` → `Route [ref]`
  is dropped by `discover_ref_pairs` (`SKIP_REF_COLS`); **never research, fill, or re-verify a
  `Route [ref]`.** Pipeline geometry is reconciled against the `GOIT-GGIT-pipeline-routes` repo
  (a separate human branch + PR), not corroborated from media `[ref]` URLs.

## Output (what Baird works from)
Two paste-ready, backend-mirroring tabs lead the deliverable:
- **`<Cmdty>_Backend`** — a **1:1 mirror of the GEM tracker backend, not a diff view**: the
  **FULL backend column set in exact sheet order** (every column, *including* computed/formula
  ones — CapacityBcm/y, LengthKnownKm, StartRegion, CostUSD, …), **one row per in-scope segment
  with the current value prefilled in every cell** from the snapshot CSV. Only *touched* cells
  carry an overlay: the proposed ref(s) on the `[ref]` cell (**color-coded by corroboration
  tier** — green/yellow/red/blue, below) and any proposed value on its value cell. A single
  leading **`SheetRow`** locator column (the tracker's own row number, not a backend field) lets
  Baird find each scattered row. **Paste-back caveat:** the computed/formula columns hold
  *snapshot-computed* values — **do not paste those over the live-sheet formulas**; paste only
  the touched (colored) cells. Built by `_backend_snapshot` + `_backend_view` in
  `build_ref_workbook.py`, which key snapshot rows by the composite `(ProjectID, SheetRow)`
  (a multi-segment ProjectID like P7445 has >1 row — ProjectID alone is not a key).
- **`<Cmdty>_OperatorsOwners`** — mirror of the separate "Pipeline operators/owners" backend tab
  (GID `1489950650`): ProjectID-keyed, with the `[ref]` column **preceding** its values (as on
  that tab); `Operator [ref]` / `Owner [ref]` cells carry the proposed ref(s), same tier colors.
  Paste each `[ref]` back onto that tab by ProjectID — *not* onto a tracker row.

A **deep sweep** (§6b) adds up to four more tabs: `<Cmdty>_Validity`, `<Cmdty>_Fills`, and —
when routes/GulfPub legs run — `<Cmdty>_RouteSuggestions` and `<Cmdty>_GulfPub`.

The `<Cmdty>_Refs_Added / _Reverified / _DeadLinks / _Unresolved` bucket tabs remain as
supporting detail (full verifications, current-ref, notes) but are not the primary view.

## Sequence
1. `scripts/refresh_csvs.sh` → fresh snapshots (don't sweep a stale CSV). This now also pulls
   the **operators/owners tab** (`GEM_operators_owners_snapshot_<date>.csv`, header at row idx 1).
2. **Worklist** — `scripts/build_ref_worklist.py --tracker <t> --country <C>
   [--status …] --verify-existing --out batches/staging/ref-sweep-<scope>/worklist.json`.
   Classifies each row×pair ref cell: `SKIP` (all values blank), `MISSING_REF` (value
   filled, ref blank), `HAS_REF` (ref filled → re-verify). It also **joins the operators/owners
   tab by ProjectID** (default latest snapshot; `--owners-csv` to override, `--no-owners` to skip)
   and emits real `Operator [ref]` / `Owner [ref]` units (`tab:'operators_owners'`) classified the
   same way. `--verify-existing` HTTP-checks every existing ref URL up front (tracker + OO;
   deterministic, **no agent tokens**) so most `HAS_REF` units pre-classify live vs dead.
3. **Harvest** — `scripts/harvest_wiki_citations.py --worklist … --out …/wiki_citations.json`.
   Start research from the row's gem.wiki page: harvest its **outbound** external citations
   (once per ProjectID). We *visit* gem.wiki but **never cite it** — only the underlying
   URLs (gem.wiki/globalenergymonitor/theodora/abarrelfull/wikidot are filtered out here and at the verifier).
   Expect many harvested links to be dead — verify each before use.
4. **Research loop (per ProjectID):**
   - **HAS_REF:** if `--verify-existing` shows all URLs live AND containing the value AND
     there are ≥2 independent → **Re-verified (blue)**, done. A single live source still
     needs a 2nd independent corroborating link.
   - **MISSING_REF / degraded HAS_REF:** rank harvested candidates (link text/context vs
     the value + source tier in `source_roster.md`), `url_verifier.verify_url(url,
     any_of=surface_forms(value), name=<pipeline/entity name>)` each — pass `name=` so a
     transliteration variant (Chelavend↔Chelavand) still matches — keep the live +
     value-present ones. **For status, don't gate on the status token**: a page describing
     the line operating/expanding/inaugurated/transiting gas confirms `operating` by
     inference (§ Verifier false-negatives → Content). If the verifier flags a short/stub
     body, **re-fetch the full text** before deciding. If gem.wiki
     citations are insufficient, web-search down the source hierarchy — those URLs also
     pass `url_verifier`. **Exhaust the harvested list against every blank/weak cell** — a
     citation captured to `wiki_citations.json` but never matched to the data point it
     supports is a miss (e.g. Iran P5984's pgjonline "Rasht–Chelvand … completed" was
     harvested but not staged onto `Status [ref]`). A harvested URL whose page confirms the
     value is fillable even as a lone source (yellow), per `confidence_tiers.md`.
   - **Search in the country's language(s), not just English.** Seed from the row's
     `OtherLanguage*` name columns and transliterations (Saudi → Arabic: Aramco Arabic
     press, Argaam, SPA). Foreign pages still pass `url_verifier`; the "contains the value"
     check leans on language-agnostic tokens (numbers, years, diameters). Record the source
     language in `ResearcherNotes`.
   - **Corroboration & tier:** seek ≥2 working, **independent** links (independence per
     `confidence_tiers.md`: separate origins; NOT the same wire story / GEM-citing). Assign
     tier → 2+ independent = **high/green**; a single source that **verifiably confirms the
     value on its page** = **medium/yellow** (fill it — don't leave blank — regardless of the
     source's roster rank); single source that does **not** actually confirm / partial
     conflict = **low/red**; none verifiable = **Unresolved + ResearcherNotes** (no
     fabricated URL — standing rule 2).
5. Stage one resolution per unit (`class_out` ∈ `REFS_ADDED` / `REVERIFIED` / `DEAD_LINK` /
   `UNRESOLVED`, `proposed_refs`, `verifications`, `tier`, `independent`, `source_language`,
   `researcher_notes`, `harvested_from_wiki`; carry `tab` through for owner/operator units) into
   `batches/staging/ref-sweep-<scope>/staged_resolutions.json`.
6. **Build** — `scripts/build_ref_workbook.py --staging batches/staging/ref-sweep-<scope>/
   --output batches/pipelines_batch_<stamp>_<scope>_refsweep.xlsx`; then `recalc.py`;
   present. Leads with the `<Cmdty>_Backend` and `<Cmdty>_OperatorsOwners` paste-ready tabs
   (see **Output** above), bucket tabs follow. `<stamp>` from
   `TZ=America/New_York date "+%Y%m%d_%H%M_ET"`; never overwrite.

## Verifier false-negatives — a `url_verifier` FAIL is not proof of anything
`url_verifier.verify_url` can fail a URL that is a **live, legitimate source that supports the
value**. The substring check is a **screen, not the verdict** — *you* read the page and make the
call. Two families of false negative:

**Liveness false-negatives** (page is live; don't class `DEAD_LINK` — Iraq gas sweep: **6 of 27
"dead links" were false**):
- **401 bot-walls.** Some live pages (e.g. `iraq-businessnews.com`) return HTTP 401 to the
  verifier's UA. Confirm the page manually / via a normal browser; if genuinely live, cite the
  **Wayback Machine** snapshot (`web.archive.org/web/…`) — which itself passes the verifier — and
  note the bot-wall in `ResearcherNotes`.
- **Ligature-encoded (esp. Arabic) PDFs.** The "contains the value" substring check can't read
  contiguous Arabic in ligature-encoded PDFs, so a live official document (e.g. a SCOP report at
  `opc-storage.oil.gov.iq`) gets marked `DEAD_LINK` falsely. Verify with `pdftotext` before
  discarding; if the value is present, keep the ref and record the language.
- **SSL cert-chain errors.** Some live hosts serve an incomplete/misconfigured certificate chain and
  the verifier raises `SSLError` (seen: `pgjonline.com`, `eeer.org` bare host). Confirm the page is
  live + contains the value via `curl` (or use the `https://www.…` form / a Wayback snapshot, which
  verify cleanly), then keep the ref and note the cert issue in `ResearcherNotes`.

**Content false-negatives** (page is live *and supports the value*, but the dumb substring check
misses it — this is the eurasianet/P5984 failure):
- **STATUS is inferred from context, not matched literally.** Do **not** require the status token
  (`operating`, etc.) to appear on the page. A page saying the line *carries gas / is being
  expanded / was inaugurated / transits N bcm to <country>* **confirms `operating`** even though
  the word never appears — **make that inference yourself.** (eurasianet's "work on expanding its
  Rasht-Chelavand pipeline would be completed … boosting the volume it can transit to Azerbaijan
  to 5.5 bcm" confirms P5984 = operating; the automated check failed only because it substring-
  searched for the literal token `operating`.) Treat a status `any_of` miss as **expected**, not
  disqualifying.
- **NAME spelling varies by transliteration.** Backend `Chelavend` vs page `Chelavand`, `Kordkuy`
  vs `Kordkoy`, etc. Pass the pipeline/entity name to the verifier via **`name=`** (fuzzy on by
  default: `name_forms` + difflib token matching), instead of relying on an exact substring. Don't
  reject a source because the outlet spells the name one letter off.
- **Truncated / stub fetches.** A 200 with a suspiciously short body (`< _MIN_BODY_CHARS`, 1500)
  is almost always a block page / cookie wall / **archive interstitial** / partial fetch — **not
  the article**. `verify_url` now flags this ("re-fetch full text (body only N chars …)"); when
  you see it, **pull the FULL page text** (rendered/browser fetch, another mirror, or a proper
  Wayback capture) before concluding anything — never bank a "value not found" from a stub. *This
  is the specific mistake that produced the wrong "eurasianet doesn't name the line" note: the
  archive fetch returned ~3 KB of interstitial, and that was treated as the article.*

No mode is a fabricated-URL exception (standing rule 2) — you must still *confirm the page is real
and supports the value* (by full-text read, `pdftotext`, `curl`, or a real Wayback capture) before
keeping the ref.

## Deep sweep variant (ref sweep + deep-fill + validity check)
The combined mode (`workflows.md §6b`): in one pass per row, do the standard ref sweep
**plus** (a) research and fill **blank value fields** with paired refs (best-effort on weak
fields like Capacity — don't force a number), and (b) **critically confirm the existing data
points and judge each pipeline's validity / existence**. Same standing rules — still
read-and-stage only. **Operating-status rows are a legitimate deep-sweep target** (not just
in-dev) — Baird often runs a deep sweep on operating pipelines specifically to catch
**redundant/duplicate** entries, so the existence/duplicate leg can be the *driving* reason.

Two further legs run on request (both were standing expectations for the Iraq gas sweep):
- **(c) Route suggestions when `RouteAccuracy` is weak.** For rows whose `RouteAccuracy` is
  `no route` / `low` / `medium`, search for and *suggest* a route at **corridor + endpoints**
  depth: named endpoints + **sourced** lat/lon + a corridor description. Delivered as candidates
  on a `<Cmdty>_RouteSuggestions` tab for a **human routes-repo branch + PR** — never
  auto-replaced, and **never fabricate coordinates** (null coords, flagged, if unsourced). This
  is the one route work that is *in scope* for a deep sweep; route *geometry `[ref]` cells*
  (media URLs for `RouteType`/`RouteAccuracy`/`RouteNotes`) stay out of scope. See
  `docs/reference/route_conventions.md`.
- **(d) GulfPub cross-comparison.** Fold in a reconcile pass against the registered GulfPub /
  PE World Map dataset to catch pipelines GEM is **missing** *and* rows where **GEM's data
  disagrees** with the dataset. Delivered on a `<Cmdty>_GulfPub` tab. Watch two dataset traps:
  a scraped **"addition" is often a mislabel, not a miss** (the 2 GulfPub-only Iraq gas additions
  were Iran pipelines with `country=Iraq` — verify the `country`/endpoints before treating an
  addition as discovery); and **`Capacity_mmcfd` is a constant `300` placeholder** in the gas
  schema — never use it as a capacity corroboration.

**Tooling status (all four legs are built in):** legs (a)/(b) and the `_Validity`/`_Fills`
tabs are wired into the committed `critical-deep-sweep` workflow + `build_ref_workbook.py`.
Legs (c)/(d) are now committed too: `merge_deepsweep_shards.py` folds each shard's `routes[]`
into `__ROUTE__` records (`class_out` `ROUTE_SUGGESTED` when both endpoints are coordinated,
`ROUTE_PARTIAL` otherwise), and `build_ref_workbook.py` renders `<Cmdty>_RouteSuggestions`
whenever they're present. For the GulfPub leg, run the scoped recon (`ingest.py` →
`reconcile.py`) then `build_gulfpub_crosswalk.py --match-diff <recon>/match_diff.json --out
<staging>/gulfpub_crosswalk.json`; `build_ref_workbook.py` adds `<Cmdty>_GulfPub` whenever that
crosswalk file is in the staging dir. Nothing here is auto-applied.

**Critically confirm, don't just check ref liveness (standing requirement).** A re-verified
`[ref]` is not the goal; *a confirmed value* is. For every non-trivial data point (status,
length, diameter, capacity, endpoints, owner/operator, classification, dates) actively ask
whether independent sources **agree with the GEM value**, not merely whether a live page
mentions the pipeline. When sources **materially disagree** with GEM, that is a finding —
raise a `__VALIDITY__` record (`verdict="concern"`), never a silent `REVERIFIED`. Beyond
per-value confirmation, take a skeptical pass on every pipeline and flag:
- **existence** — no independent evidence the pipeline is real (possible hallucination / a
  GEM-only entity entered from a misread source);
- **duplicate** — likely the same physical pipe as another GEM row under a different name/relabel;
- **classification** — not a transmission line at all, or wrong commodity (e.g. an NGL line
  recorded as dry gas, a gathering/process/feeder line recorded as a trunk transmission line);
- **attribution** — wrong owner/operator, province, FuelSource, or endpoint;
- **spec** — length/diameter/capacity that independent sources contradict.

Schema extensions to `staged_resolutions.json` (and to each subagent shard):
- **`class_in="FILL"`** — a deep-fill record (blank value → researched value). `values`
  carries the filled field(s); `proposed_refs`/`verifications` corroborate them; `class_out`
  is `REFS_ADDED` if a paired ref verifies, else `UNRESOLVED`. `build_ref_workbook.py`
  routes these to a dedicated **`<Cmdty>_Fills`** tab (Outcome = `filled (corroborated)` vs
  `not corroborated / dropped`), NOT the `_Backend` mirror.
- **`ref_col="__VALIDITY__"`** — a per-pipeline validity flag, not a ref (one per flagged
  ProjectID). Routed to a dedicated **`<Cmdty>_Validity`** tab. Emit these structured fields
  so the tab reads them directly (the builder falls back to parsing `researcher_notes` only
  for legacy shards that omit them):
  - `verdict` — `"confirmed (caveat)"` (pipeline is real; lesser caveat noted) or `"concern"`
    (open existence/duplicate/classification doubt). Drives the tab's red/green flag.
  - `concern_type` — one of `existence` / `duplicate` / `classification` / `attribution` /
    `spec` / `none`.
  - `recommendation` — short human-facing next step (e.g. "reclassify as NGL", "merge into
    P####", "verify endpoint before keeping").
  - `researcher_notes` — the full finding (authoritative); `proposed_refs` + `verifications`
    — the independent sources backing the judgment (encouraged, even though it is not a ref edit).
- **`ref_col="__STATUS__"` (annual-update mode only)** — a per-segment-row status verdict,
  staged when the deep sweep runs with `build_deepsweep_args.py --status-review` (workflows.md
  §7). `verdict` ∈ `confirm` / `change` / `stale` / `unclear`; `values` carries the exact
  column→value edits (`change`: Status + matching date cols, refs required; `stale`: the
  dormancy-rule inference, `ShelvedCancelledType=Presumed` force-added at merge, no ref by
  design). Routed to a dedicated **`<Cmdty>_StatusReview`** tab that leads the workbook.
  Verdict vocabulary + QC rules: `docs/sops/annual_update.md`; full record schema:
  `docs/reference/staged_json_schema.md`.
- **`routes[]` (deep-sweep route-suggestion leg)** — a per-row list of suggested routes for
  `RouteAccuracy`-weak rows, carried on the subagent shard. Each entry:
  `start_name`/`start_lat`/`start_lon`, `end_name`/`end_lat`/`end_lon`, `waypoints[]`,
  `corridor_desc`, `current_route_accuracy`, `suggested_route_accuracy`, `proposed_refs`,
  `verifications`, `tier`, `researcher_notes` (optional `waypoint_note`). **Coords are null
  (flagged yellow) when unsourced — never fabricated.** `merge_deepsweep_shards.py` folds these
  into `__ROUTE__` records (`class_out` `ROUTE_SUGGESTED` when both endpoints are coordinated,
  else `ROUTE_PARTIAL`) and `build_ref_workbook.py` renders the `<Cmdty>_RouteSuggestions` tab.

## At scale (subagent fan-out)
A whole-country deep sweep is too large for one context. Fan out:
0. **Choose each subagent's model at dispatch time** (global standing rule — see
   CLAUDE.md). The saved workflows (`critical-deep-sweep.js`, `country-discovery.js`)
   fall back to `MODEL = A.model || 'sonnet'` — pass `args.model` to carry the
   dispatch-time choice; baked one-off scripts set `model:` on their `agent()` calls
   the same way.
1. After the worklist + harvest, **bundle rows into small batches** (~4 ProjectIDs each)
   and write one input file per batch under `…/batches/batch_NN.json`.
2. Spawn **one general-purpose subagent per batch**, each handed the same fixed **record
   contract** (the per-unit staged-resolution schema: `project_id, sheet_row, ref_col,
   value_cols, values, proposed_refs, verifications[{url,ok,contains_value}], class_out,
   tier, researcher_notes`, + `tab:'operators_owners'` for OO units, + the `FILL` /
   `__VALIDITY__` extensions). Each subagent researches its rows, runs `url_verifier` on
   every URL itself, and writes its own **shard** to `…/shards/batch_NN.json`. Run in
   background waves.
3. **Validate the contract on the first shard before scaling** — confirm all required
   keys present, zero blocklisted URLs, every `proposed_ref` has a passing verification,
   OO units preserved. Only then launch the rest.
4. **Merge** all shards → `staged_resolutions.json`, computing `meta` (commodity, scope,
   project_ids, n_units, class_out_counts, tier_counts, n_operator_owner_units).

### Merge-time QC normalization (run before `build_ref_workbook.py`)
Subagents are not perfectly consistent; normalize deterministically at merge:
- **Strip any `proposed_ref` whose verification is not `ok && contains_value`** (a
  live-but-non-matching page is not a valid ref — no orphan/unsupported refs).
- **Downgrade to `UNRESOLVED`** any `REFS_ADDED`/`REVERIFIED`/`DEAD_LINK` record left with
  zero valid refs after stripping; add a `[QC]` note.
- **Watch field semantics** — e.g. drop `FuelSource="Natural Gas"` fills (`FuelSource` is
  the upstream field/plant, not the fuel type; `gem_schema.md`).
- Re-assert the pre-delivery invariants (below) on the merged file: 0 unverified refs,
  0 blocklisted URLs, every UNRESOLVED has a note.

## Tier → color
Applied to each `[ref]` cell on the `<Cmdty>_Backend` and `<Cmdty>_OperatorsOwners` tabs (and the tier cell on the bucket tabs):
green = ≥2 independent working sources · yellow = single source · red = low/none ·
**blue = re-verified existing ref (no action)** · red Current-ref cell (DeadLinks tab) = dead/value-missing.

## Standing rules (echoed)
Visit-but-**never-cite** gem.wiki/globalenergymonitor (rule 1) · **never theodora** ·
**never A Barrel Full / abarrelfull.wikidot.com or any wikidot.com page** (tertiary
aggregators; `url_verifier` rejects them — read for leads only, cite the underlying source) ·
every URL through `url_verifier` (even ones that worked last batch) · no orphan refs ·
**no fabricated URLs** (rule 2) · nothing auto-applied — the xlsx is a candidate set Baird
pastes manually.

## Pre-delivery checks
README present; every `Proposed ref(s)` cell verified (HTTP 200 + value present) and free
of GEM/theodora/abarrelfull/wikidot; tier colors correct; no orphan refs; Unresolved units have a
`ResearcherNotes` reason and no fabricated URL. Full checklist: `docs/sops/qc.md`.

## Escalation gates
Stop and report rather than mass-producing low-value rows if: a large fraction of
MISSING_REF units end **Unresolved**, or the harvester hit-rate is very low, or a whole
class of values looks systematically unsupported (likely a schema misread, not a finding).

## Iterate
Expect Baird to challenge specific refs. Acknowledge, re-search with verified sources,
regenerate — **do not defend** wrong findings (standing rule 3).
