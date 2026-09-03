# SOP — Country Sweep (the research engine)

One scoped pass over existing rows (country + commodity + status filter) with
**selectable legs** — `refs`, `fills`, `validity`, `status-review`, `routes`,
`recon` (formerly `gulfpub`; now one pass per registered reference dataset —
`gulfpub` AND `osm` in the `deep` preset) — staged into ONE dir per scope. Presets (`refs-only`, `deep`, `in-dev`)
and the command sequences: `docs/workflows.md §3`. This SOP is the operational
rules: the `refs` leg first (the base every preset includes), then the further
legs under "Legs beyond refs".

## The `refs` leg (fill & re-verify every `[ref]`)

Crawl every row and every ref-bearing data point in scope and, for
each one, reach the target: **≥2 links that both WORK (HTTP 200, no error) AND
corroborate each other AND contain the precise data point** being referenced.

- **Blank `[ref]` + filled value** → research and add corroborating source URLs.
- **Filled `[ref]`** → re-check the URLs still resolve *and* still contain the value.

Distinct from QC's link-rot detection: **QC *detects*, the sweep *researches & stages*.**
QC's BroadSweep flags orphan refs (ref filled, value blank); the refs leg fixes the
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
- **Transit countries share ROWS, so the second scope swept must exclude the first's.** A
  trunk crossing Uzbekistan and Kazakhstan is ONE row that both `--country` scopes select —
  Uzbekistan gas overlaps Kazakhstan gas on **13 of its 31 rows** (the CAC, CA–China,
  Bukhara–Ural and BTBA strings). Re-researching them stages a second record against the
  same sheet cell, and whichever workbook is pasted last wins silently.
  `build_ref_worklist.py --exclude-pids` takes a comma list or `@<file>` (one PID per line,
  `#` comments); **derive the file from the other country's
  `staging/*/staged_resolutions.json`, never by hand**, keep it at
  `batches/<scope>/carried_from_<other>.txt` as the batch's record of what it is not
  accountable for, and note the carried rows in the country note. The run prints an
  `EXCLUDED …` line — never let rows drop silently. **The exclusion applies to the research
  legs ONLY (§9 steps 1–4, 7), never to the recon leg:** `reconcile.py` needs the FULL
  in-country GEM roster on the GEM side, or the excluded rows' reference counterparts
  re-bucket as `DISCOVERY_CANDIDATE` — manufacturing phantom additions out of trunks GEM
  already tracks. Leave `--country` alone there.

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

The **`deep` preset** adds `<Cmdty>_Validity`, `<Cmdty>_Fills`, `<Cmdty>_RouteSuggestions`
(routes leg), and **one tab per reference dataset** from the recon leg — `<Cmdty>_GulfPub`,
`<Cmdty>_OSM`, and any source registered later, discovered by glob rather than named in the
builder.
The **`in-dev` preset** leads with `<Cmdty>_StatusReview`.

The `<Cmdty>_Refs_Added / _Reverified / _DeadLinks / _Unresolved` bucket tabs remain as
supporting detail (full verifications, current-ref, notes) but are not the primary view.

## Sequence
1. `scripts/refresh_csvs.sh` → fresh snapshots (don't sweep a stale CSV). This now also pulls
   the **operators/owners tab** (`GEM_operators_owners_snapshot_<date>.csv`, header at row idx 1).
2. **Worklist** — `scripts/build_ref_worklist.py --tracker <t> --country <C>
   [--province <P> [--exclude-network-regex …]] [--status …] --verify-existing
   --out batches/<scope>/staging/ref-sweep[-<qualifier>]/worklist.json`.
   `--province` scopes sub-country by Start/End province (either terminus; China's
   province batches — idiom + trunk-exclusion regex in `docs/country_notes/china.md`).
   Classifies each row×pair ref cell: `SKIP` (all values blank), `MISSING_REF` (value
   filled, ref blank), `HAS_REF` (ref filled → re-verify) — and, with **`--owe-fills`**,
   **`MISSING_VALUE`** (value blank → the `fills` leg OWES a sourced value or an honest
   `UNRESOLVED`). Always pass `--owe-fills` on a `deep` sweep: without it a blank cell is a
   non-unit nobody reports on, which is how Jiangxi v2 shipped 4 fills against 571 blanks
   (MZ 2026-09-03: "lots of blank data on operating projects"). Default owed stems are
   Length / Capacity / Diameter / Start / Construction / SegmentCost / Pressure / FuelSource /
   Proposal / Operator / Owner; `--fill-pairs <stems|all>` overrides. The run prints
   `fills owed … by status / by column`; **`operating` rows carry the bulk and matter most.**
   It also **joins the operators/owners
   tab by ProjectID** (default latest snapshot; `--owners-csv` to override, `--no-owners` to skip)
   and emits real `Operator [ref]` / `Owner [ref]` units (`tab:'operators_owners'`) classified the
   same way. `--verify-existing` HTTP-checks every existing ref URL up front (tracker + OO;
   deterministic, **no agent tokens**) so most `HAS_REF` units pre-classify live vs dead. It
   passes the row's `pipeline_name` to the verifier, so an existing ref that is live and
   carries the value but **never names the pipeline** comes back `name_absent: true` — an
   advisory relevance flag (an English name won't appear on a Chinese page), and the unit
   is a re-read, not a pass.
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
     any_of=surface_forms(value), name=<pipeline/entity name>)` each — **`name=` is
     mandatory, not optional**: it is the relevance check. A page that contains the number
     but does not name THIS pipeline (its FULL name — "A–B", not a page about A or about B, and
     not a page about the parent system when the row is a segment) is not a ref for it. The
     verifier records `name_found` on every verification; when the name is in another script
     (Chinese/Arabic/Cyrillic) pass the `OtherLanguage*` name too, or read the page and
     encode the hand-confirmed match as `name_found: true` with the matched string in `note`.
     A `[ref]` whose page doesn't name the pipeline is MZ's 2026-09-03 finding #3 — the
     merge caps such a unit at `low` (`merge_qc.relevance_qc`) and `sweep_gates.py` gate I
     lists it. Keep the live + value-present + pipeline-named ones. **For status, don't gate on the status token**: a page describing
     the line operating/expanding/inaugurated/transiting gas confirms `operating` by
     inference (§ Verifier false-negatives → Content). If the verifier flags a short/stub
     body, **re-fetch the full text** before deciding. If gem.wiki
     citations are insufficient, web-search down the source hierarchy — those URLs also
     pass `url_verifier`. **Exhaust the harvested list against every blank/weak cell** — a
     citation captured to `wiki_citations.json` but never matched to the data point it
     supports is a miss (e.g. Iran P5984's pgjonline "Rasht–Chelvand … completed" was
     harvested but not staged onto `Status [ref]`). A harvested URL whose page confirms the
     value is fillable even as a lone source (yellow), per `confidence_tiers.md`.
   - **Read every document you open to EXHAUSTION — for every column, and for every
     sibling row.** A source found for one cell is a source for every fact on its page: when
     an approval notice found for `Status [ref]` also states length, diameter, investment,
     construction start and commissioning, stage it onto `Length [ref]`, `Diameter [ref]`,
     `SegmentCost [ref]`, `Construction [ref]` and `Start [ref]` too (as `REFS_ADDED` where
     the value is on the sheet, as a `FILL` where the cell is blank). Then check the run's
     other in-scope rows: a page about the trunk usually names its branches, and a page about
     segment I usually states segment II's numbers. Jiangxi v2 shipped P4777's length, cost and
     construction date `UNRESOLVED` while the Sina article staged on P4776 stated all three
     (MZ 2026-09-03, finding #2). The one limit is the aggregate-vs-segment rule: a SYSTEM
     figure is not a ref for a SEGMENT cell — say so in notes and file `__VALIDITY__` rather
     than stage it. Record in `researcher_notes` which other cells/rows the document served.
   - **Two refs per data point is the target for EVERY unit, not just the hard ones.** After
     the first source lands, the second search is owed: different publisher, different
     document class (regulator ↔ operator ↔ press ↔ EIA), never a restatement. A single-source
     unit is fillable at `medium`, but its notes must say what was searched for the second and
     why it was not found — a bare single ref with no second-search note is unfinished
     (MZ 2026-09-03, finding #4: "limited range of sources"). `sweep_gates.py` gate K counts
     the single-source `REFS_ADDED`; gates A/C catch a row or a batch resting on one origin.
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
   `batches/<scope>/staging/ref-sweep[-<qualifier>]/staged_resolutions.json`.
6. **Build** — `scripts/build_ref_workbook.py --staging batches/<scope>/staging/ref-sweep[-<qualifier>]/
   --output batches/<scope>/deliverables/pipelines_batch_<stamp>_<scope>_refsweep.xlsx`; then `recalc.py`;
   present. Leads with the `<Cmdty>_Backend` and `<Cmdty>_OperatorsOwners` paste-ready tabs
   (see **Output** above), bucket tabs follow. `<stamp>` from
   `TZ=America/New_York date "+%Y%m%d_%H%M_ET"`; never overwrite.

## Verifier false-negatives — a `url_verifier` FAIL is not proof of anything
`url_verifier.verify_url` can fail a URL that is a **live, legitimate source that supports the
value**. The substring check is a **screen, not the verdict** — *you* read the page and make the
call. Two families of false negative:

**Liveness false-negatives** (page is live; don't class `DEAD_LINK`). **Seven families now**, and
the hit rate is not marginal: the Iraq ref-gap re-pass (2026-07-28) found **33 of 41 "dead" refs
were false negatives** (an earlier Iraq sweep: 6 of 27). Treat a `DEAD_LINK` classification as a
hypothesis you still have to test by hand. **Standing rule (Baird, 2026-07-30): a once-working
existing ref is NEVER dropped from its `[ref]` cell because it fails from here** — geo-blocks,
anti-bot 403s/WAFs, and timeouts are access problems, not deletions; only a confirmed-deleted
page (HTTP 404/410) may be replaced. The workbook builder enforces this mechanically
(`_annotate_kept_refs` in `build_ref_workbook.py` keeps every not-proven-dead current URL in
the cell ahead of the proposed refs), so a blocked origin gets its Wayback snapshot *added*,
never swapped in as a replacement:
- **401 bot-walls.** Some live pages (e.g. `iraq-businessnews.com`) return HTTP 401 to the
  verifier's UA. Confirm the page manually / via a normal browser; if genuinely live, cite the
  **Wayback Machine** snapshot (`web.archive.org/web/…`) — which itself passes the verifier — and
  note the bot-wall in `ResearcherNotes`.
- **Ligature-encoded (esp. Arabic) PDFs.** The "contains the value" substring check can't read
  contiguous Arabic in ligature-encoded PDFs, so a live official document (e.g. a SCOP report at
  `opc-storage.oil.gov.iq`) gets marked `DEAD_LINK` falsely. Verify with `pdftotext` before
  discarding; if the value is present, keep the ref and record the language.
- **SSL cert-chain errors — now handled automatically (2026-08-11).** Some live hosts serve an
  incomplete/misconfigured certificate chain (seen: `pgjonline.com`, `eeer.org` bare host, and
  **`adilet.zan.kz`**, the official Kazakh legal database). `verify_url` used to return a bare
  `request failed: SSLError`, which read as a dead link; it now **retries once with TLS
  verification off** and stamps the verdict with `insecure_tls: True` plus a reason note. So an
  `insecure_tls` verdict means **the page IS live** — never class it `DEAD_LINK`, and never drop
  the ref over it; note the cert issue in `ResearcherNotes` (identity unconfirmed, content read).
  **Blast radius:** every ref check run before 2026-08-11 misclassified these hosts. In Kazakhstan
  gas it was **51 of 105** ref cells (45 `SSLError` + 5 `ConnectionError` + 1 `ReadTimeout`, and
  **zero** 404s) — the operating leg went 55 → 63 all-live once fixed. Any earlier country whose
  worklist shows `SSLError` link-rot flags is suspect; re-run the worklist rather than trusting it.
- **Large PDFs.** A token FAIL on a big PDF (OPEC ASB editions, ministry annual reports) is **not
  evidence the source lacks the value** — the verifier may never have read far enough into the
  document. Extract with `pdftotext` and search the table yourself before ruling.
- **CAPTCHA / bot / IP-block interstitials that return HTTP 200.** The response is a challenge or
  access-denied page, not the article, but nothing in the status code says so. Pair this with the
  stub-body flag below: a 200 whose body is short *or* reads as a challenge is an unread page, not
  a missing value. **`verify_url` now detects these itself and returns `blocked: True`** — but note
  the fix landed in two halves, and until **2026-08-16** detection only ran when an expected-content
  needle was supplied. A bare `verify_url(url)` reachability screen — which is how most `[ref]`
  cells get checked — returned a plain `ok=True, reason='200'` on a page nobody had read. Seen on
  `energybase.ru`, which serves «Доступ ограничен» naming the caller's IP and ASN. **A `blocked`
  verdict is emphatically NOT a deletion**: keep the ref and add a Wayback capture alongside.
- **JS-gated stubs.** The server returns a 200 shell and the article text is injected client-side,
  so the substring check sees an empty article. Fetch the rendered page (or a Wayback capture,
  which usually snapshots the hydrated HTML) before concluding anything.
- **A `ConnectionError` you caused yourself — never fan out verification at web.archive.org.**
  Re-verifying Ukraine's 390 staged URLs at 10 concurrent threads (2026-08-16) got our IP
  connection-*refused* by the Internet Archive: `ConnectionError … [Errno 61]`. Fifteen Wayback
  URLs sitting in `proposed_refs` failed, including captures that had returned 200 minutes
  earlier and still do. **The verifier reports this identically to a dead ref**, so a burst of
  Wayback failures in one run is a rate-limit signature, not link rot — re-test a known-good
  capture serially before believing any of them. Keep archive.org verification serial with a
  pause; the throttle outlasts the run by several minutes. Same shape as the SSL family above:
  a transport failure on our side is never evidence a page is gone.

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
- **VALUES are often phrased in prose / equivalent units — do the equivalence yourself.**
  "an additional 6 BCM of natural gas to be exported to Egypt annually" fully supports
  `Capacity = 6` + `CapacityUnits = bcm/y` — "annually" / "per year" / "a year" **is** the
  `/y`, and spelled-out units ("billion cubic meters") and convertible figures
  (600 MMcf/d ≈ 6.2 bcm/y) count too. The substring check only hunts for the literal
  number/unit tokens and misses all of these. **Never write "the existing ref doesn't
  support the value" off a failed substring check alone — read the passage and quote it in
  `ResearcherNotes` either way.** (This is the Egypt P3620 failure: energy-sea.gov.il
  states the 6-BCM-annually figure verbatim, but the note called the ref unconfirmable.)
- **DATE columns can be supported by the source's own dateline.** An official announcement
  of a proposal/approval dated May 2023 supports `ProposalYear = 2023` (and the month)
  even if "2023" never appears in the body — the event's date IS the article date. Note
  which milestone the date attaches to (first floated vs formal approval).
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

## Legs beyond refs: `fills` + `validity` (the `deep` preset)
**Subagent brief:** start every fan-out from `docs/sops/templates/deep_sweep_brief.md` (copy to the
run dir as `BRIEF.md`, fill the scope slots, delete no rules) — it carries the four review rules
(relevance / exhaustion / owed blanks / second source) and the record contract.

The combined mode (`workflows.md §3`, `deep` preset): in one pass per row, do the standard
refs leg **plus** (a) research and fill **blank value fields** with paired refs, and (b)
**critically confirm the existing data points and judge each pipeline's validity /
existence**. **(a) is an OWED set, not an opportunistic one:** the worklist's
`MISSING_VALUE` units (`--owe-fills`, step 2) are the fills leg's worklist, and every one
ends as a sourced `FILL` or an `UNRESOLVED` with a note saying what was searched — the same
contract as a `MISSING_REF`. Never force a number (a weak Capacity stays blank rather than
fabricated), but never skip a blank silently either; the delivery note reports
`fills owed / filled / unresolved` by status, and `sweep_gates.py` gate J lists owed blanks
with no record at all. Prioritise `operating` rows — a blank Length/Diameter/Capacity/
StartYear on an operating line is the gap the researchers see first. Same standing rules —
still read-and-stage only. **Operating-status rows are a legitimate deep-sweep target** (not
just in-dev) — Baird often runs a deep sweep on operating pipelines specifically to catch
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
- **(d) Reference-dataset cross-comparison.** Fold in a reconcile pass against **every**
  registered dataset in scope — GulfPub / PE World Map *and* OSM by default in the `deep`
  preset — to catch pipelines GEM is **missing**, geometry GEM **lacks**, and rows where
  **GEM's data disagrees**. Delivered as one `<Cmdty>_<Source>` tab per dataset. Traps:
  a scraped **"addition" is often a mislabel, not a miss** (the 2 GulfPub-only Iraq gas additions
  were Iran pipelines with `country=Iraq` — verify the `country`/endpoints before treating an
  addition as discovery); **`Capacity_mmcfd` is a constant `300` placeholder** in the GulfPub gas
  schema — never a capacity corroboration; and **OSM's `osm_id_key` is not unique** across
  differently-merged ways, so `ingest.py` suffixes collisions `#2..` and warns — a warning there
  means cross-scrape identity for that dataset is unreliable until the manifest's `oid_field`
  is fixed.

**Tooling status (all four legs are built in):** legs (a)/(b) and the `_Validity`/`_Fills`
tabs are wired into the committed `critical-deep-sweep` workflow + `build_ref_workbook.py`.
Legs (c)/(d) are now committed too: `merge_deepsweep_shards.py` folds each shard's `routes[]`
into `__ROUTE__` records (`class_out` `ROUTE_SUGGESTED` when both endpoints are coordinated,
`ROUTE_PARTIAL` otherwise), and `build_ref_workbook.py` renders `<Cmdty>_RouteSuggestions`
whenever they're present. For the recon leg, run the scoped recon (`ingest.py` →
`reconcile.py`) **once per source** then `build_recon_crosswalk.py --match-diff
<recon>/match_diff.json --sweep-dir <staging>/`; `build_ref_workbook.py` globs
`recon_*_crosswalk.json` and emits one `<Cmdty>_<Source>` tab each. Nothing here is
auto-applied.

**A reference route is presumptively real pipe** — every unmatched reference record
carries a `Disposition` (`ROUTE_FOR_EXISTING` / `FRAGMENT_OF_EXISTING` / `NEAR_MISS` /
`DISCOVERY_CANDIDATE`) and is worked by it, never dismissed wholesale; the table, the
`partial` Coverage guard and the License (ODbL) guard live in the Reconciliation SOP §4.

**Check the run's health before believing a thin result.** `reconcile.py` emits
`MATCH_QUALITY` when the name and geometry axes are both mostly dead — unnamed reference
features against routeless GEM rows — which is OSM's normal condition and produces a
convincing-looking zero. Iraq gas 2026-07-28: 52 features, 0 overlaps, top composite
0.438 against a 0.45 threshold. The remedy is the admin-area signal (`geoarea_weight`,
set per-dataset in the source manifest so committed runs elsewhere stay reproducible),
never a lowered threshold.

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

### Two follow-on passes the `validity` leg keeps generating (Libya + Iraq, 2026-07)

Both are separate run dirs under the same scope, not new legs — they *adjudicate* what
the row-by-row legs detected. Both are read-and-flag only.

- **Redundancy-cluster adjudication** (`staging/redundancy/`). The row-by-row legs emit
  *pairwise* duplicate flags ("compare P0483 against P1862"). Resolving those one pair
  at a time is wrong: the real unit of decision is the **cluster** (an aggregate corridor
  row plus its member segments). Detection stays in the prior dirs; adjudication happens
  here, staging one `__VALIDITY__` record per implicated row carrying the **cluster-level**
  recommendation, so the handoff shows one coherent ruling instead of N contradictory pairs.
  Built by a per-batch one-off `build_redundancy.py` in the run dir (the clusters are
  country-specific findings, not a reusable algorithm) — copy the Libya or Iraq script.
  **Resolve to in-tracker precedent, not invention** — see the aggregate-corridor
  convention in `docs/reference/gem_schema.md`, and cite the precedent rows in the record.
  The pass cuts both ways: on Iraq it **withdrew 12 of our own 16** duplicate/existence
  flags once ASB provenance was understood (`notes/escalation-2026-07-28-asb-iraq-provenance.md`).
  Retracting your own flag is a first-class outcome here.
- **Cancelled/shelved review** (`staging/cancelled-review/`). `cancelled` rows fall through
  both the operating sweep and the `in-dev` preset's `--status proposed,construction,shelved`
  filter, so a country's dead rows go unswept indefinitely. This pass asks three questions
  per row — is the status still right, are the values credible, can each ref cell be sourced
  — staging `__STATUS__` + `__VALIDITY__` sentinels alongside ordinary ref units. Enumerate
  the units from the live header via `ref_pairs.discover_ref_pairs` and read row/value/current-ref
  data from the CSV so nothing is retyped; only findings are authored by hand. Consolidate a
  status ruling into whichever leg already owns that ProjectID so the handoff carries **one
  status decision per ProjectID**.

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
- **`ref_col="__STATUS__"` (the `status-review` leg / `in-dev` preset)** — a per-segment-row
  status verdict, staged when the sweep runs with `build_deepsweep_args.py --status-review`
  (workflows.md §3). `verdict` ∈ `confirm` / `change` / `stale` / `unclear`; `values` carries the exact
  column→value edits (`change`: Status + matching date cols, refs required; `stale`: the
  dormancy-rule inference, `ShelvedCancelledType=inferred` force-added at merge, no ref by
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

## Check for a bulk-load provenance BEFORE fanning out (Pakistan, 2026-08)

Cheap first move on a new country: group the rows by `LastUpdated` + owner + `[ref]` set.
If a large share collapses into one narrow window with the **same one or two refs**, the
country is a **bulk load**, and if those refs are *cartographic* (a JPG/PDF network map),
no amount of per-row research will find text naming the individual segments — 51 of
Pakistan's 70 gas rows were one such load, and 63 per-row subagents returned 362
`UNRESOLVED` units and 16 `existence` flags that were really tracking segment obscurity.

**What actually resolves a bulk-load cohort is one document: the operator's own audited
annual report.** SNGPL's *"TRANSMISSION SYSTEM As at June 30, 2018"* (a 270-row line-wise
inventory in its 2018 annual report) accounted for 49 of the 51 rows on name + length +
diameter at two-decimal precision, closing every residual existence question and all three
redundancy flags in a single pass. So on a bulk-load country, **look for that operator's
annual reports, licence schedules and regulator filings before dispatching per-row
research**, and stage the result as its own `register-crosswalk` dir.

Two rules when you do:
- **Control the extraction.** Reconcile your parse against a total the document itself
  prints (SNGPL's grand total, 4,685.92 / 4,190.05 km). A parse that doesn't reconcile is
  a hypothesis. Two of the Pakistan matcher's own bugs — testing only the mainline column
  on rows that carry both, and roman-numeral tokens defeating the name gate — surfaced only
  because the totals were being checked.
- **A better document is not a second origin.** An operator register beats that operator's
  own map by a mile, but it has the same publisher, so it is still `medium`; `high` needs an
  unrelated source (GulfPub tracing the same line) on top. Also expect exact **arithmetic
  composites** where GEM aggregates and the register itemises — a granularity difference,
  never something to "fix".

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

### Sentinels get silently dropped by the ref merge — harvest them back

`merge_ref_shards.py` matches each shard resolution to a baseline record by
`(project_id, ref_col, sheet_row)`. A **sentinel** (`__VALIDITY__`, `__REDUNDANCY__`)
deliberately has no baseline record — it isn't a ref cell, it's the agent answering
"is this row real / is it a double-count?". So the merge prints
`WARN N shard unit(s) matched no baseline record` and **drops them**: the refs survive
and the sourced verdict is lost. These are the highest-value findings in a batch (the
three misfiled Libya condensate lines came from them), so **never wave that WARN through**:

```bash
python scripts/harvest_sentinel_findings.py --staging $STG/    # accepts repeated --staging
```

It appends each dropped sentinel as a proper `__VALIDITY__` resolution (`class_out:
UNRESOLVED` — validity is read-and-flag, never an applied edit) and is idempotent, so a
re-run replaces rather than duplicates. Run it whenever a ref-gap pass rode along with
validity work, and reconcile the count against the WARN.

**It runs LAST in the chain — after `merge_deepsweep_shards.py`, not just after
`merge_ref_shards.py`.** `merge_deepsweep_shards.py` re-folds by purge-and-rebuild, and
its `is_old_deepsweep()` drops every record whose `ref_col` is `__VALIDITY__` /
`__STATUS__` / `__ROUTE__` — precisely what the harvester writes. Harvest before it and
the sentinels are silently zeroed out again (verified on Jiangxi: 2 → 0, no warning).

**The harvester globs `ref_shards/P*.json` — the merge globs `ref_shards/*.json`.** So a
fan-out that shards by BATCH rather than by PID (`batch_03.json`, e.g. when one subagent
carries four rows) satisfies the merge and is **silently invisible to the harvester** — the
refs land, every sentinel vanishes, and nothing warns. Split batch shards to per-PID files
before merging (Jiangxi's `split_shards.py` is the pattern) and check the harvester's printed
resolution count is non-zero when you know the shards carried sentinels.

**A `kind: FILL` record falls through BOTH scripts.** A fill on a blank-value row has no
baseline ref unit either — correctly, since the no-orphan-refs rule means a blank value
column emits no ref unit for the worklist to carry — so `merge_ref_shards.py` drops it for
want of a key, and the harvester only rescues the two sentinels. It is harmless while the
fill is `UNRESOLVED` (no value, no refs), which is why this hid: **a successfully sourced
fill is the one that vanishes.** Fills are `merge_deepsweep_shards.py`'s job and it reads
them from `rows/<PID>.json` as `fills[]`, so route them there. `split_shards.py` sends each
record to exactly one destination **structurally, not on the `kind` tag**: if the worklist owes
no unit at `(pid, ref_col)` then the value column is blank, so the record IS a fill whatever it
called itself. Trusting the tag is not enough — three of Jiangxi's batch-02 records said "FILL
target: LengthKnown is blank" in their own notes and carried `kind: null`, and would have been
lost the moment one of them succeeded. It also joins row identity
(`pipeline_name`/`wiki`/`sheet_row`) back from the worklist, which a fill record doesn't carry.

**Re-sweeping a scope: a CARRIED fill needs the same care, and it has its own way to vanish.**
When a v2 sweep supersedes a v1 batch, the carry step folds v1's `REFS_ADDED` onto v2's units
by `(pid, ref_col)` — and a fill matches nothing, for exactly the reason above. Do not park it
in a side file: **`carried_fills.json` was written by Jiangxi's `carry_prior.py` and read by
nobody**, because `build_ref_workbook.py` takes `pending_fills` from an *actions* packet
(a §6 handoff), not from the staging dir. On a standalone deep-sweep build the file exists,
the count reports "wrote 1 prior fill(s)", and the record reaches no tab. That lost the v1
Jiangxi sweep's one real fill (P4788 `Pressure` = 6.30 MPa, sourced). Put a carried fill back
in the store with `class_in: "FILL"` — the store *is* the fills lane (`fill_res` selects on
that field) — taking the **fresh** `sheet_row` from a sibling record of the same PID, never
the prior run's locator. And reconcile the count across the two runs (`class_in FILL: 9 → 1`
is a question, not a statistic): **a file written by one stage and read by none is a silent
loss**, and the stage that wrote it will report success.

### Merge-time QC normalization (run before `build_ref_workbook.py`)
Subagents are not perfectly consistent; normalize deterministically at merge:
- **Strip any `proposed_ref` whose verification is not `ok && contains_value`** (a
  live-but-non-matching page is not a valid ref — no orphan/unsupported refs).
- **Downgrade to `UNRESOLVED`** any `REFS_ADDED`/`REVERIFIED`/`DEAD_LINK` record left with
  zero valid refs after stripping; add a `[QC]` note.
- **The converse of the strip rule is a shard-authoring requirement, and it is where evidence
  actually gets lost.** `verified_refs` reads the shard's OWN verification objects — it never
  re-fetches — so a manual confirmation of a false-negative page (bot-wall, large CJK PDF,
  prose/unit-form mismatch, engineering-convention equivalence) must be encoded as
  `ok: true, contains_value: true` **plus** a note stating who verified it and how. Recording it
  as `ok: false` with the explanation in prose reads to the merge as "not verified": the ref is
  stripped, the record is then honestly downgraded to `UNRESOLVED`, and the unit reports as
  *no source found* when in fact a source was found and discarded. The downgrade is a real safety
  net, which is exactly why this is invisible — nothing errors. **Check it per batch:** count
  records where `proposed_refs` is non-empty and `verified_refs()` returns empty; that number
  should be zero except for refs deliberately kept in-cell under standing rule 5 (a blocked or
  unparseable page that is not a 404/410 stays in the sheet but must NOT enter a proposal).
  Jiangxi's batch 03 encoded 14 confirmations as `ok: false` where batches 01/04/05 encoded the
  same situations correctly, zeroing 11 of its records — 31 of 47 refs kept before the fix, 45
  after, on the highest-yield batch of the five.
- **Watch field semantics** — e.g. drop `FuelSource="Natural Gas"` fills (`FuelSource` is
  the upstream field/plant, not the fuel type; `gem_schema.md`).
- Re-assert the pre-delivery invariants (below) on the merged file: 0 unverified refs,
  0 blocklisted URLs, every UNRESOLVED has a note.

## Tier → color
Applied to each `[ref]` cell on the `<Cmdty>_Backend` and `<Cmdty>_OperatorsOwners` tabs (and the tier cell on the bucket tabs):
green = ≥2 independent working sources · yellow = single source · red = low/none ·
**blue = re-verified existing ref (no action)** · red Current-ref cell (DeadLinks tab) = dead/value-missing.
A residual red cell after the pass = no independent source supports the current GEM value
(often a value disagreement), not merely unsearched.

## Standing rules (echoed)
Visit-but-**never-cite** gem.wiki/globalenergymonitor (rule 1) · **never theodora** ·
**never A Barrel Full / abarrelfull.wikidot.com or any wikidot.com page** (tertiary
aggregators; `url_verifier` rejects them — read for leads only, cite the underlying source) ·
every URL through `url_verifier` (even ones that worked last batch) · no orphan refs ·
**no fabricated URLs** (rule 2) · nothing auto-applied — the xlsx is a candidate set Baird
pastes manually.

## Pre-delivery checks
Run **`python scripts/sweep_gates.py --staging <run dir>`** on the merged store and quote its
counts in the delivery note. It is read-only and advisory (gates A–K): A source diversity per
row · B false `high` · C `high` leaning on a dominant document · D `independent` flag vs
verified refs · E orphans · F banned/GEM · G harvested pool URLs never opened on a still-
`UNRESOLVED` row · H recovered Save-Page-Now origins unopened · **I relevance** (sourced
units whose refs do not name the pipeline, and units where nobody checked) · **J owed blanks
with no record** · **K single-source `REFS_ADDED`** (the two-per-data-point target unmet).
A non-zero I/J/K is not a blocker but the count goes in the delivery note verbatim — it is
what the researcher will find, so say it first. Then: README present; every `Proposed
ref(s)` cell verified (HTTP 200 + value present) and free of GEM/theodora/abarrelfull/wikidot;
tier colors correct; Unresolved units have a `ResearcherNotes` reason and no fabricated URL.
Full checklist: `docs/sops/qc.md`.

## Escalation gates
Stop and report rather than mass-producing low-value rows if: a large fraction of
MISSING_REF units end **Unresolved**, or the harvester hit-rate is very low, or a whole
class of values looks systematically unsupported (likely a schema misread, not a finding).

## Iterate
Expect Baird to challenge specific refs. Acknowledge, re-search with verified sources,
regenerate — **do not defend** wrong findings (standing rule 3).
