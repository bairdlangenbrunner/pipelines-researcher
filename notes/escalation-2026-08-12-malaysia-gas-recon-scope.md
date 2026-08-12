# Escalation — Malaysia gas §2 recon: GEM tracks 5 rows, three sources describe ~150

**Date:** 2026-08-12
**Scope:** Malaysia, gas (GGIT). 5 GEM rows: P1065, P1066, P1067, P1068, P7105.
**Runs:** `batches/malaysia-gas/staging/recon-{gulfpub,osm,malaysian-gas-map}-20260812/`
**Workbooks:** `pipelines_batch_20260812_1343_ET_malaysia-gas_reconciliation-{gulfpub,osm,malaysian-gas-map}.xlsx`

Two CLAUDE.md escalation gates tripped, plus a third that needs a scope ruling from
Baird before any of it becomes Discovery work.

| gate | threshold | GulfPub | OSM | Malaysian Gas Map |
|---|---|---|---|---|
| reference-only Additions | >30 | **51 (41 disc.)** ⚠️ | 29 (8 disc.) | **67 (65 disc.)** ⚠️ |
| matched rows in material conflict | >10% | **3 of 4 = 75%** ⚠️ | n/a (0 matched) | n/a (0 matched) |
| `MATCH_QUALITY` null run | — | no | **yes** | **yes** |

> **The GulfPub run was rebuilt at `1343_ET`; the `1256_ET` set is deleted, don't look
> for it.** The first run predated the same-day fix to the reference-side country filter
> (`N.country_matches` — membership, not equality), which had been silently dropping every
> record whose country field names more than one country. GulfPub Malaysia went **50 → 55**
> reference records and additions **46 → 51**. See §2.1: one of the five recovered records
> is P1068's own line.

---

## 1. The two null runs are NOT discovery sets — and they fail for opposite reasons

Both OSM and the Malaysian Gas Map returned **0 overlaps**, and both raised
`MATCH_QUALITY`. Per the standing rule I measured the geometry directly before
reading either as a finding (`nearest GEM route` distance and containment fraction
per reference trace). The two answers are completely different:

**OSM — a granularity artifact. The extract corroborates GEM almost totally.**

- **1,502 of 1,640 km (92%)** of the OSM Malaysia gas extract lies ≥60% inside the
  drawn route of a GEM row — 21 traces at **100%** containment.
- 20 of those are pieces of **P1065 (PGU)**; one 215.6 km trace is **P1066 (SSGP)**.
- Only **three** traces (0.1 + 3.6 + 2.0 = **5.7 km**) sit outside every GEM route.
- Why it scored 0: OSM splits PGU into 20+ unnamed ways, so *every* pair fails on
  name (0 of 29 named) and on length ratio (a 7 km way against a 2,623 km row).
  Max composite 0.3396 vs a 0.45 threshold.

  **Read this as: the OSM extract is the same pipe GEM already has drawn. It is not 29
  missing pipelines.** No `geoarea_weight` override is warranted (documented in the
  manifest) — the fix would be granularity-aware matching, not an admin-area fallback.

  **RETRACTED (same day, before delivery): "OSM independently confirms the geometry of
  P1065 and P1066 — the single strongest corroboration in this batch."** It does not,
  because it is not independent. Both rows' `Route [ref]` cells cite
  `https://openinframap.org/#2/26/12` — OpenInfraMap is a *render of OSM data*. GEM's
  routes for P1065/P1066 were traced from OSM (plus the Malaysian Gas Map, see §5), so
  OSM ways lying inside those routes is close to tautological. The 92%-containment
  number is still the right *diagnosis of the null run* — it proves the matcher didn't
  miss 29 pipelines — but it carries **no corroborative weight** for the geometry, and
  neither of this batch's two null-run sources is independent of the routes it appears
  to confirm. Read the `Route [ref]` cell before crediting a route source.

**Malaysian Gas Map — genuine spatial complementarity. It covers what GEM does not.**

- **Median** nearest-GEM-route distance across the 67 traces: **92.6 km**.
- Only 18 of 67 come within 12 km of any GEM route; only 3 exceed 60% containment.
- The extraction is the **offshore gathering/trunk network** off Terengganu, Sarawak
  and Sabah. GEM's 5 rows are onshore/cross-border transmission trunks. They are
  describing different infrastructure, in the same country, and they barely intersect.

  **Read this as: the matcher worked and the two datasets genuinely do not overlap.**
  Whether those 65 traces should become GGIT rows is the scope question in §3 below,
  not a matcher question. Note the map's own caveats in
  `sources/malaysian_gas_map/NOTES.md` — its per-segment labels are provably wrong
  (37 of 67 read "Sabah–Sarawak Gas Pipeline (SSGP)", which is every feature in the
  Borneo inset), so the source is mapped **name-less** on purpose.

---

## 2. GulfPub: three status conflicts on four matched rows

This is the substantive research output of the batch and routes to **Update**, not
Discovery. None of it is auto-applied.

**P1066 Sabah–Sarawak Gas Pipeline — GEM says `operating`; GulfPub splits the line
in two and says 77% of it is shut.**

| GulfPub record | segment | length | status |
|---|---|---|---|
| `1940` "Sabah - Sarawak Pipeline (**Closed Section**)" | Lawas → MLNG Bintulu | 386.2 km | Non operational |
| `89189` "Sabah - Sarawak Pipeline (**Operating Section**)" | Kimanis → Lawas | 112.7 km | Operating |

  386.2 + 112.7 = **498.9 km against GEM's 512 km** — the split reconciles to GEM's own
  length, which makes the segmentation credible rather than a matcher artifact. Route
  IoU 0.72 on the closed section. GEM's row carries `Status = operating` with **no
  `Status [ref]`** and `LastUpdated 2023-08-31`. Needs verification against Petronas /
  Malaysian press before any flip — GulfPub alone never settles a status (tier 2, one
  source). But a wholly-`operating` 512 km row is very likely wrong.

**P1067 Trans Sabah Gas Pipeline — GEM says `cancelled` (2018, `confirmed`); GulfPub
says "Non operational" on both halves.** GulfPub's two records (Kimanis→Sandakan
270.4 km + Sandakan→Tawau 391.1 km = **661.5 km vs GEM's 662 km**) corroborate GEM's
length and endpoints precisely. The status wording is weaker than GEM's, not stronger
— GEM's row cites 2025 NST/Daily Express coverage of the project being scrapped again,
which outranks GulfPub here. **Recommend: no change; record the corroboration of
length/route.** Also note GulfPub `101412` declares 391.1 km against a 216.4 km
geodesic trace — a defect in GulfPub's own record, not evidence about GEM.

**Ambiguity to adjudicate:** GulfPub `101411` (TSGP) scores against both P1067 (0.59)
and P1066 (0.50) because Kimanis is the origin of both lines.

---

## 2.1 The five records the country filter had been eating — one of them is P1068

Recovered by the `N.country_matches` fix, all previously invisible to a Malaysia-scoped run:

| ref | name | country field | length | status | disposition now |
|---|---|---|---|---|---|
| `gulfpub:gas:2006` | **Trans Thailand-Malaysia Gas Pipeline** | `Thailand / Malaysia` | **254.3 km** | operating | `NEAR_MISS` (0.4207) |
| `gulfpub:gas:1954` | West Natuna Transportation System | `Malaysia / Indonesia` | 640.5 km | operating | `DISCOVERY_CANDIDATE` |
| `gulfpub:gas:1989` | Sarawak - Philippines Pipeline Project | `Malaysia / Philippines` | 1,158.7 km | idle | `NEAR_MISS` |
| `gulfpub:gas:1945` | Dumai Barat - Melaka | `Indonesia / Malaysia` | 103.0 km | proposed | `DISCOVERY_CANDIDATE` |
| `gulfpub:gas:1970` | Keong - Duyong Pipeline | `Malaysia / Indonesia` | 96.6 km | operating | `DISCOVERY_CANDIDATE` |

`2006` is **P1068**. It is a `NEAR_MISS` rather than an overlap only because it fell
0.0293 short of the 0.45 threshold: the names match almost verbatim, but P1068's drawn
route is a `very low (straight line/schematic)` 173 km line, so its IoU against GulfPub's
real trace is near zero. Do not "fix" that by lowering the threshold. Two things follow:

- **P1068 IS corroborated.** GulfPub's 254.3 km against GEM's 267 km is a **5% delta**, not
  a conflict, and it agrees on `operating` and on the Kangar landfall. Before the fix this
  row sat in `gem_only` with no reference support of any kind.
- **GulfPub's trace is a route-improvement candidate** for a row whose own geometry is
  admittedly schematic. Routes-repo work, never an auto-replacement.

The other four are scope-question material (§3), not corrections. Note that `1954` runs
Natuna → **Jurong Island, Singapore** and `1945` lands at Melaka — GulfPub's Malaysia block
includes lines that only transit or terminate in Malaysia.

---

## 3. The scope question — this is the ruling I need

**Malaysia is the most under-covered gas country in Southeast Asia**, and it isn't
close. GGIT row counts, same snapshot:

| Indonesia | Australia | Thailand | Vietnam | Philippines | Myanmar | **Malaysia** |
|---|---|---|---|---|---|---|
| 50 | 151 | 34 | 15 | 13 | 9 | **5** |

Malaysia is the region's second-largest gas producer and holds one of the world's
largest LNG complexes (MLNG Bintulu). Five rows is an order of magnitude out of line
with its neighbours, and all three reference sources independently say the same thing.

The 51 GulfPub additions decompose into five families (exhaustive — every record is
assigned, and the km column is the sum of GulfPub's own stated lengths):

| family | records | km | what it is |
|---|---|---|---|
| **PGU system components** | 14 | 2,572 | "PGU Phase II/III", "PGU Loop I/II", the Georgetown / Lumut / Melaka / Port Dickson / Port Klang / Johor Bahru / Kota Bharu laterals, Tiong–Tok Arun (PGU), Pengerang (PGP) |
| **Offshore field feeders** | 24 | 2,828 | Jintan/F6/F23/D12/M3→MLNG, Duyong/Jerneh/Bintang→Tok Arun, Erb West/Kikeh/Samarang→Labuan, Limbayong→Kimanis, the Shallow Clastics group, … |
| **Cross-border lines filed under Malaysia** | 7 | 2,675 | West Natuna Transportation System (×2 records) + the Keong/Belinda/Malong/Siput feeders — several with **both endpoints in Indonesia**, one running to **Jurong Island, Singapore**; Dumai Barat–Melaka; proposed "Natuna Gas" (East Natuna→Bintulu, 542 km, 2028); Sarawak–Philippines (1,159 km, idle) |
| **Genuine Malaysian trunk candidates** | 5 | 1,030 | Malay Basin Pipeline System (237 km), RDP-A/OGT (246 km), Tok Arun–Meru (proposed, 309 km), Tok Arun–Kota Bharu, Tok Arun–Kertih |
| **P1068's own record** | 1 | 254 | Trans Thailand–Malaysia — **not a discovery**, a sub-threshold `NEAR_MISS` on an existing row (§2.1) |

Two GulfPub-internal duplicate pairs are visible in the counts and should not be read as
two pipelines each: `Kikeh - Labuan` appears twice at an identical 138.4 km, and
`West Natuna Transportation System` twice (640.5 km and 19.3 km).

Three separate rulings, and I do not think any of them is mine to make:

1. **The PGU family is granularity, not discovery.** GEM models PGU as ONE 2,623 km
   network row (P1065); GulfPub models it as phases + loops + laterals. Every one of
   the 13 either carries "PGU" in its name or terminates at a PGU phase. They should
   go to `OtherEnglishNames` / stay absorbed, **not** become 13 new rows — unless GGIT
   wants Malaysia segmented, which would be a modelling change, not a batch decision.
   (Geometry containment against P1065 is weak — 0.82 for two, ≤0.38 for the rest —
   because GEM's drawn route follows the mainline, not the laterals. The name lineage
   is the dispositive evidence here, not the geometry.)
2. **Offshore field feeders: in or out of GGIT scope?** 24 GulfPub records and most of
   the Malaysian Gas Map's 65 discovery candidates are the same infrastructure —
   field-to-shore gathering trunks.

   My first instinct was that these sit below GGIT's transmission line and that
   excluding them would make Malaysia's 5 rows roughly correct. **GGIT's own contents
   do not support that**, and I'd rather say so than let a convenient reading stand:

   - GGIT gas carries **13 rows typed `gathering`** and **22 typed `both transmission
     and gathering`** — the category exists and is used.
   - **148 gas rows** have "field" in `StartLocation`, i.e. field-origin lines are
     routine, not exceptional.
   - Size is no argument either: GGIT's median gas row is **102 km** and **1,877 of
     3,843** length-bearing rows are **under 100 km**. The Malaysian feeders run
     **34–296 km** — squarely inside the normal range.

   **And GEM's own oil tracker already carries this exact class, for this exact
   country.** GOIT has 5 Malaysian rows, all `operating`, all drawn at `high` accuracy
   by researcher IM — and three of them are offshore-field-to-shore lines on the same
   corridors GulfPub proposes on the gas side:

   | GOIT oil row | km | GulfPub gas addition on the same corridor | km |
   |---|---|---|---|
   | P7912 Erb West–Labuan | 143 | `Erb West - Labuan` | 136.8 |
   | P7908 Gumusut Kakap–Kimanis | 200 | `Limbayong - Kimanis` | 169.0 |
   | P7910 Kebabangan–Kimanis | 154 | (same Kimanis landfall) | — |
   | P7909 Angsi–Kerteh / P7911 Tapis–Kerteh | 166 / 197 | (Terengganu feeders) | — |

   Offshore fields produce oil and associated gas together, so a gas line beside the
   oil line is the normal arrangement, not a duplicate. Excluding the gas feeders while
   GOIT maps the oil ones would leave GEM tracking half of the same physical bundle.

   So the exclusion has to be argued on grounds other than type or size, and it is
   Baird's call, not mine.

   (Two GulfPub records for `Kikeh - Labuan`, identical name/endpoints/138.4 km, are a
   duplicate inside GulfPub itself — count 23, not 24, if the family is adopted.)
3. **The Indonesian records must not become Malaysian rows** regardless. That is a
   GulfPub country-attribution defect (it also labels "Tok Arun, **Indonesia**" on a
   PGU Phase III record whose other end is Segamat, Johor). Worth carrying back to the
   GulfPub source notes.

---

## 4. Rows no source corroborates

**P7105 Malaysia Singapore Gas Pipeline** is unmatched by all three sources, has
`no route`, and every single one of its `[ref]` cells — Status, Fuel, PipelineType,
Start, Length — points at **one** URL (`southeastasiainfra.com/pipeline-infrastructure/`).
Its `StartLocation` is "Attap Valley" (given as Johor, Malaysia) and its `EndLocation`
is "Attap Valley Onshore Receiving Facility" (given as Singapore) — the same place name
on both ends, across a border.

The deep sweep (§3) came back with four concerns on it, and one is structural:

- **Duplicate risk against P1065.** APERC's *Natural Gas Pipeline Development in
  Southeast Asia* (2000), Table 11, describes PGU-II as a 714 km mainline running
  "Telok Kalong to Segamat; Segamat to Kapar, Port Klang (west); **Segamat to Pasir
  Gudang & Singapore** (south)", completed 1991/92. On that account the first delivery
  of Malaysian gas to Singapore was not a standalone international pipeline at all — it
  was the southern branch of PGU-II. P1065 is GEM's aggregate row for that same network.
- **The geometry supports the concern, and adds a length problem the sweep couldn't
  see** (the sweep had no route data; I measured it after). P1065's drawn route ends at
  **(1.4578 N, 103.7680 E)** — the Johor Bahru waterfront, at the Causeway, i.e. GEM's
  PGU row already runs to the Malaysia–Singapore boundary. From there the Attap Valley
  ORF in Sembawang is **5.8 km**; from Pasir Gudang it is **8.9 km**. So whatever pipe
  P7105 describes beyond P1065's terminus is a **single-digit-km strait crossing, not a
  70 km line**. `LengthKnownKm = 70` cannot be spanned by this row's own stated
  endpoints under any reading.
- The other two: `StartYear1` should probably be **1992**, not 1991 (PGB's own corporate
  timeline + APERC, against the lone southeastasiainfra.com secondary), and the
  `Owner [ref]` currently cites a **Gentari/City Energy hydrogen-pipeline feasibility
  study** — an unbuilt, different project that passed the verifier only because
  "Petronas" appears in it.

**Recommended handling: treat P7105 as an open existence/duplicate question, not a
length fix.** Either it is the tail of P1065 double-counted (fold, record the name under
`OtherEnglishNames`), or it is a genuine short cross-border segment whose length and
Malaysian-side start location are both wrong. Both readings are staged as concerns; no
cell is changed.

**P1068 TTM was in this section and no longer belongs here** — see §2.1. GulfPub *does*
carry it (`gulfpub:gas:2006`, 254.3 km, operating, JDA → Kangar); the country filter was
eating the record because GulfPub files it as `Thailand / Malaysia`. It remains unmatched
by OSM, and the Malaysian Gas Map's "Thai–Malaysia Gas Pipeline"-labelled traces are still
**not** TTM (one runs through the Andaman Sea, the wrong side of the peninsula) — that is
the label defect, not a finding. So P7105 is the only row in this section.

---

## 5. Incidental: GEM already cites this map

P1065 and P1066 both carry
`https://malaysiangas.com/wp-content/uploads/2023/11/Malaysia-Gas-Map-Advert…` in
their `Route [ref]`. The newly registered `malaysian_gas_map` source is a digitization
of that same publication — so GEM has been using it as a route reference by eye
already. That does not make it self-citing (it is a third-party publication, not GEM),
but it does mean the routes for P1065/P1066 and this source are **not fully
independent** for corroboration purposes.
