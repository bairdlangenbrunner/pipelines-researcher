# Triage — Egypt gas full pass + route completion (2026-08-26)

Scope agreed with BL 2026-08-26: **Egypt gas only** (oil stays unswept), the unapplied
07-28 handoff packet is **superseded** rather than reconciled, and the route work covers
**both** the coverage gap and an **accuracy upgrade** of the 52 `very low` rows.

Trigger: `NA` has finished her Egypt update pass. This memo is the pre-flight — nothing
is staged yet. Per §1, no batch spins up until BL signs off.

---

## State of the tab (fresh pull `GGIT_gas_snapshot_20260826.csv`, 08:52 ET)

| | |
|---|---|
| Egypt gas rows | **126** (117 on 08-11) — 122 `NA`, 4 `BL` |
| Statuses | operating 110 · construction 11 · proposed 4 · cancelled 1 |
| Ref-cell coverage | **901 / 2,772 = 32.5%** (22 `[ref]` columns) |
| Values with no `[ref]` | 57 cells across 28 rows |
| Orphan `[ref]` (ref, no value) | 2 cells |
| Routes | 104 routed (23 `high` · 29 `medium` · **52 `very low`**) · 22 unrouted |
| Unrouted | 11 blank (`P8070`–`P8080`) · 10 known partials · `P0477` (by design) |

### What changed 08-12 → 08-26

- **8 new rows**: `P8073`–`P8080`, all `NA`, all `operating`, all blank `RouteType`/
  `RouteAccuracy` (= `no route`, routable per the 2026-08-11 convention).
- **3 further rows never worked by us**: `P8070`–`P8072` landed 08-12, also unrouted.
- **21 rows edited / 70 cells**, all `NA`. Concentrated in `OtherLanguagePrimaryPipelineName`
  (9), `PipelineName` (6), and ref cells; but also real value moves that need verifying:
  - `P3939` — `LengthKnown` 260.00 → **262.50**, `StartYear1` blank → **1974**.
  - `P8023` — `LengthKnown` 40.00 → **35.00** (Length [ref] repointed).
  - `P7580` — `Diameter` blank → **`16,30,42`** (multi-value, World Bank PDF ref).
  - `P8024` — `FuelSource` "Abu Madi Gas Field" → **blanked** (value deleted).
  - `P8065`/`P8066` — start/end columns **swapped** (Ameriya ↔ WDGC), against the
    direction of the geometry we applied 08-10.
  - `P8005` — `ResearcherNotes` **overwrote BL's own flag** ("BL: doesn't exist, Sumed
    Oil Pipeline does though") with NA's replacement text. The flag was erased, not
    answered.
- **`P0477` network route nulled out again** (routes commit `609cc429`; the repo README
  now says don't repeat segment geometry on system/network rows) and the row reads
  `Included in other ProjectID`. **The country note's claim that P0477 was applied at
  `high` is stale and needs correcting.**

---

## Step 0 — QC gate (blocking; run before any research spend)

Three findings, in priority order. A deep sweep that researches `P8075` without knowing
it may be a third copy of `P8065`/`P8066` burns the spend twice.

### 0a. ESCALATION — `P8017` / `P8020` ProjectIDs were recycled for Iraq

Both PIDs now hold **`Baiji-Mosul Gas Pipeline`**, `CountriesOrAreas = Iraq`, researcher
`AL`, `LastUpdated 2026-08-24`, `RouteType = Mapped route (at any accuracy)`,
`RouteAccuracy = high`, `RouteCreator = AL`. (Two Iraq rows sharing one name is itself a
duplicate question on that side.)

The Egypt rows that held those PIDs — *Suez-Cairo Ring Gas Pipeline* (150 km, `medium`)
and *Cairo Ring-Port Said Gas Pipeline* (130 km, `very low`) — are gone from the gas tab
with no renamed survivor anywhere in it.

**Meanwhile `GOIT-GGIT-pipeline-routes` still holds our Egyptian geometry under those
filenames**: `data/individual-routes/gas-pipelines/P8017.geojson` and `P8020.geojson`,
first vertex `31.3077, 29.8223` — greater Cairo, not Mosul. So two Iraqi rows currently
render Egyptian pipe.

**The weekly backend archives settle how it happened** (folder
`1vu773vt44TTIyUDnlLkuxVnA6Cq_UT5c` → *Weekly archives - automated* → *Pipelines*; tab is
named `Gas pipelines`, not `Gas`). It was a **partial in-place wipe, not a row deletion**:

| checkpoint | `P8017` | `P8020` |
|---|---|---|
| 08-03 archive | Egypt, full row, `RouteCreator = CB` | Egypt, full row, `RouteCreator` **blank** |
| 08-10 archive | Egypt, full row, `CB`, `medium` | Egypt, full row, `NA`, `no route`, `Not mapped` |
| **08-17 archive** | **8 non-empty cells** — `ProjectID` + the route block only | **9 non-empty cells** — same, `RouteCreator = NA; CB` |
| 08-24 archive | identical to 08-17 (still wiped, route block orphaned) | identical to 08-17 |
| 08-26 live | Iraq, `Baiji-Mosul`, `AL`, `high`, `RouteCreator = AL` | same |

Confirmed real, not an archive artifact: neighbours `P8016`/`P8021` are fully populated in
the same archive, and the only other ProjectID-without-name rows in the 08-17 tab are the
19 pre-allocated blanks `P8081`–`P8099`. **Neither PID was logged in the
`Removed oil/NGL/gas pipelines` tab** — 849 rows, no `P8017`/`P8020`, no matching name —
so there is no deletion rationale on record.

**Attribution, from the sheet's own Drive revision history: `NA`, 2026-08-14 19:26 UTC.**
Cell-level edit history is UI-only, but Drive keeps per-revision `lastModifyingUser` plus
per-revision export links, so the wipe is bisectable — see "How to redo this" below.
Retention runs ~14 days (oldest retained revision `345383`, 08-13 08:43 UTC) and the wipe
falls inside it. Binary search over the 20 revisions between that and the 08-17 archive:

| revision | UTC | actor | `P8017` / `P8020` |
|---|---|---|---|
| `345383` | 08-13 08:43 | `MZ` | full (37 / 38 non-empty) |
| `345798` | 08-14 10:16 | `MZ` | full |
| `345871` | 08-14 17:02 | `NA` | full |
| `345873` | 08-14 17:46 | `NA` | **full — last clean** |
| **`345949`** | **08-14 19:26** | **`NA`** | **wiped (8 / 9)** |
| `345974` | 08-17 03:17 | `MZ` | wiped |

Attribution is unambiguous: `345873` and `345949` are consecutive and both `NA`, so no
other editor could have made the change inside that interval.

**Revision `345949` contains exactly four row changes on the gas tab** — `P8017` cleared,
`P8020` cleared, `P8080` filled in (*West Cairo P.S. Gas Pipeline*, 34 cells,
`Researcher = NA`), `P8079`'s `LastUpdated` bumped 08-13 → 08-14. So the two rows were
cleared in the same working session as the last of the new-row additions, not in a separate
cleanup pass.

**The mechanism was a range clear of `C:CF`** — `PipelineName` through `Location [ref]`, 21
hand-entered cells per row. The 16 survivors inside that span are all array-formula columns
that regenerate (`Owner`, `Parent`, `ParentEntityIDs`, `StartYearEarliest`,
`CapacityBcm/y`, `CapacityBOEd`, `LengthKnown/Estimate/MergedKm`, `DiameterInMm`,
`Start/EndRegion`, `Start/EndSubRegion`, `NumberOfCountries`), plus `ProjectID` in `F`.
The route block **`DC:DG`** (`RouteType`, `RouteAccuracy`, `RouteNotes`, `RouteCreator`,
`Route [ref]`) sits *outside* the cleared span and survived untouched — which is why the
row read as free while still carrying our route metadata.

**The wipe is a coverage loss, not only an ID accident.** GulfPub's `gulfpub:gas:424`
*Suez - Dahshour Pipeline* (Gasco 100%, 16", 88 mi = 141.6 km, trace 135.9 km, operating,
Dahshour `31.3077, 29.8223` ↔ Suez `32.5590, 29.9593`) matched **exactly one GEM row ever**
— `P8017`, green at composite 0.770, coverage *comparable*. Nothing in the current 126-row
tab is that line: no row carries the corridor by name, **no Egypt gas route in the repo has
an endpoint pair within 40 km of both reference endpoints**, and none of the 22 geometry-less
rows spans it (the only Suez-area ones are `P8005` 6.1 km, `P8006`/`P8007` 9/7 km, `P8055`
28 km). Best corridor overlap is `P8058` at **27.5%** of the reference — the shared western
tail into Dahshour, not the Suez run — then `P3930` at 10.3%. The nearest hypothesis is a
chain, `P7574` (Ain Sokhna–New Admin Capital PS, 65 km) + `P3930`/`P8058`
(New Admin Capital–Dahshur, 70/67 km) ≈ 132–135 km, but those are 32" against GulfPub's
16", `P7574`'s geometry is off-corridor (<5%), and `P3930`/`P8058` are themselves a likely
duplicate pair. So on the next §2 GulfPub run `424` will drop out of `overlaps` and
re-bucket as an unmatched addition — correctly. `P8020` has **no** GulfPub counterpart
(GulfPub's *Suez - Port Said Pipeline*, 3794, matches `P8018`), so its loss is not
externally corroborated.

Note also that `AL` cleared `RouteNotes` on both rows, so the GulfPub provenance for those
two traces now survives **only** in `batches/egypt-gas/staging/recon-gulfpub-20260812/` and
the weekly archives — and `P8017.geojson` carries no genealogy in its properties, just
`{"ProjectID": "P8017"}`. Capture it before deciding retire-vs-recreate.

Also on the Iraq side: `Baiji-Mosul Gas Pipeline` now appears **three times** — `P1842`
(no length), `P8017` (no length, `StartState/Province = Baiji`) and `P8020` (22.00 km,
`StartState/Province = Mainline`). AL appears to be building a parent + segments in
recycled rows, with segment names in a province column.

- `audit_route_sync.py --country Egypt` reports **A/B/C/D = 0**, and that is correct by
  its own logic: every finding is per-row, so a *recycled* PID looks perfectly in sync.
  This is a **new defect class** — geometry whose centroid falls outside the row's own
  country. Proposal: add it as **finding E**, tracker-wide, so PID reuse is detectable.
- Repair touches another researcher's rows and both halves of the sync, so it is
  **report-first**: BL decides whether the Egypt rows were deleted deliberately (and the
  two geojsons should be retired) or the PIDs were reused by mistake (and the Egypt rows
  need re-creating under fresh PIDs). No write until then.

### 0b. Mechanical ref defects — 15 / 10 / 3 rows

- **Search URLs carrying no data** — `egyptoil-gas.com/?s=Gas+Pipelines+Egypt` sits in
  `[ref]` cells on **15 rows**: `P3937 P3938 P6035 P8013 P8014 P8015 P8016 P8018 P8019
  P8021 P8022 P8023 P8024 P8049 P8076`. Flagged in the 07-28 review; it has **spread**
  (`P8076` is new), not shrunk.
- **`?utm_source=chatgpt.com`** on refs, **10 rows**: `P3936 P7574 P8032 P8045 P8050
  P8052 P8053 P8058 P8072 P8080`. `P8051`'s was stripped 08-10; these remain. The
  parameter must go regardless of whether the underlying source holds up.
- **Arabic comma `، ` used as the multi-ref delimiter**, 3 rows: `P3620 P3936 P8074`.
  This breaks `ref_pairs` parsing — the cell reads as one malformed URL.
- Plus the 57 unref'd values / 2 orphan refs above, which the `refs` leg absorbs.

### 0c. Duplicate-name clusters — 15, two of them new

Same-name clusters within Egypt gas. New or newly aggravated:

- **`P8065` / `P8066` / `P8075`** — *Western Desert Gas Complex-Ameriya Gas Pipeline*,
  three rows, 15.00 / 14.50 / 26.00 km. `P8065`/`P8066` are the two genuinely distinct
  Ameriya nodes 10.2 km apart (established 08-10, both routed); `P8075` is new and
  unrouted. Renaming made all three indistinguishable by name.
- **`P8072` *Kima Aswan Industrial* (4 km) vs `P8073` *Aswan-Kima* (20 km)** — likely one
  asset entered twice.

Standing clusters, unchanged: `P8008`/`P8009` · `P0436`/`P7482` · `P3620`/`P3657` ·
`P3937`/`P3938` · `P7577`/`P7578` · `P8052`/`P8053` · `P3366`/`P8002` · `P3930`/`P8058` ·
`P3932`/`P8049` · `P0474`/`P3934`/`P6687` · `P8006`/`P8007` · South Valley
(`P0477`+`P6697`–`P6702`+`P8056`) · `P5132`/`P6036`.

**Deliverable for step 0:** a row-by-row delta review in the shape of
`notes/review-2026-07-28-na-egypt-gas-additions.md`, covering the 11 new + 21 edited
rows, plus the escalation memo for 0a. Read-and-flag; nothing applied.

---

## Steps 1–7 — §9 full pass on gas (126 rows)

One run dir each under `batches/egypt-gas/staging/`, per `workflows.md` §9.

| # | Step | Run dir | Size |
|---|---|---|---|
| 1 | Sweep, `deep` preset, operating rows | `ref-sweep-operating-20260826/` | **110 rows** — the main spend |
| 2 | Sweep, `in-dev` preset | `annual-20260826/` | 15 rows (11 construction + 4 proposed) |
| 3 | Cancelled/shelved review | `cancelled-review/` | 1 row |
| 4 | Redundancy adjudication (**after** 1–3) | `redundancy/` | all 15 clusters, cluster-level rulings |
| 5 | Recon re-run, both sources | `recon-gulfpub-20260826/`, `recon-osm-20260826/` | cheap; both stale against a 126-row tab |
| 6 | Handoff packet | `qc-20260826/` | two files, actions + evidence |
| 7 | Ref-gap re-pass, if 1–3 leave red cells | `ref-gap-repass/` | India-style; 32.5% coverage says expect one |

Supersession, per §9 doctrine and BL's call: the 07-28 packet's 284 `REFS_ADDED` / 201
`REVERIFIED` / 135 fills / 89 concerns / 87 route suggestions are **re-derived** against
the 126-row tab. Old deliverables and their staging dirs move to `archive/` by MOVE, and
every retraction gets written into the country note explicitly.

Two sequencing constraints:
- **Steps 1–3 detect; step 4 adjudicates.** Duplicate flags are not resolved row-by-row —
  pairwise rulings contradict each other (Iraq withdrew 12 of 16 of its own flags this way).
- **Step 5 runs before the route upgrade pass** (step 8b), because its GulfPub sidecars
  and OSM `ROUTE_FOR_EXISTING` traces are inputs to the upgrade adjudication.

---

## Step 8 — routes

**8a. Close the coverage gap — 22 rows.**
- Apply the already-staged `P7589` (Faramid; `staging/route-creation-20260811-p7589/`,
  routes-repo QC **PASS**, 36.9 km vs 38.0). This is the one candidate ready to go today.
- Route the **11 blank rows** `P8070`–`P8080`. Several should resolve off anchors already
  established: Abu Madi (GeoNames, 08-10), OSM El-Tina station, the two Ameriya nodes,
  Kima/Aswan.
- Retry the **10 partials** (`P8005`/`P8006`/`P8007`, `P8008`/`P8009`, `P8001`, `P8003`,
  `P7605`, `P8055` — each needs a *source*, not another geocoding attempt).
- `P0477` stays unrouted by design; the network-row convention is now settled against it.

**8b. Upgrade the 52 `very low` rows** (BL's call this pass). Ladder: ENTSOG/GIE SYSCAP
2026 (`sources/entsog/`, measured Egypt accuracy median 4.2 km / p90 13 km → `medium`
cap), GulfPub sidecar geometry, and OSM traces from step 5. **Adjudicated per PID against
the overlay PNGs, never accepted wholesale** — accept only where *both* endpoint snaps
fall inside the measured error, exactly as the 08-07 pass did (it rejected 5 of 9 on that
test). Expect a large review surface; a rejected candidate leaves the existing route alone.

Both halves of every apply stay one unit — routes-repo merge **and** the sheet's
`RouteType`/`RouteAccuracy`/`RouteNotes`/`RouteCreator`/`Route [ref]` in the same batch,
then `audit_route_sync.py` — per the cardinal rule and the three-way sync rule.

---

## Open decisions for BL

1. ~~**`P8017`/`P8020` (0a)**~~ — **RESOLVED 2026-08-27, applied.** BL directed the
   restore: `P8017`'s row is back as **`P8084`** (26 cells recovered verbatim from revision
   `345873`) and its geojson renamed `P8017.geojson` → `P8084.geojson` (routes merge
   `1ccf6cfa`); the two Iraq rows that inherited the PIDs are reset to `Not mapped`/`no
   route` against null placeholders, because **`AL` has not uploaded replacement geojsons**
   (a freshly re-synced `drive-uploads/` holds one file in her folder, `P2232`). GulfPub `424`
   keeps its overlap, now against `P8084`. Two follow-ups left: **`P8020`'s Egypt row is
   still unrestored** — its 27 cells are preserved in
   `notes/recovered-2026-08-27-p8017-p8020-cleared-row-values.md`, and the Drive revision
   they came from ages out around 2026-08-28 — and **`AL` still owes Iraq geometry** for
   `P8017`/`P8020`. Why `NA` cleared the rows is still only recoverable from her.
2. **`P8005`** — your flag was overwritten. Restate it, or accept NA's reading that the
   line feeds the New Capital power station?
3. **`P8065`/`P8066`/`P8075`** — the swapped start/end columns contradict the applied
   geometry's direction. Fix the columns, or re-cut the routes?
4. Whether **finding E** (geometry outside the row's country) goes into
   `audit_route_sync.py` now, as part of step 0, or waits for its own batch.

---

## Appendix — how to attribute a cleared cell without UI access

Google exposes no cell-level history API ("Show edit history" is UI-only), and the Admin
Reports drive audit log needs admin scopes we don't have (`403 insufficient
authentication scopes`). But `drive.revisions.list` returns `lastModifyingUser` per
revision, and each revision carries `exportLinks`, so the *content* at a revision is
fetchable and the change is bisectable:

1. `gws drive revisions list --params '{"fileId":"<sheet>","fields":"revisions(id,modifiedTime,lastModifyingUser(displayName,emailAddress))","pageSize":1000}' --page-all`
   — note retention is only ~14 days, so do this promptly.
2. Mint a bearer token from the CLI's own credentials: `gws auth export --unmasked` gives
   `client_id` / `client_secret` / `refresh_token`; POST them to
   `https://oauth2.googleapis.com/token` with `grant_type=refresh_token`.
3. `GET https://docs.google.com/spreadsheets/export?id=<sheet>&revision=<id>&exportFormat=xlsx`
   with `Authorization: Bearer <token>`. **This is authenticated access, not the
   withdrawn anonymous export path** — it 401s without the header. ~26 MB per revision for
   this sheet, so bisect rather than sweeping.
4. Read the archive tab by name (`Gas pipelines`), header at row 3, and binary-search the
   predicate. `lastModifyingUser` on the first revision satisfying it is the editor;
   confirm the bracketing revision has the same actor, or the coalescing makes attribution
   ambiguous.

`alt=media` on `drive.revisions.get` does **not** work for native Sheets (`404 Revision
not found`) — the export links are the only content path. And `gws --output` refuses paths
outside the working directory.