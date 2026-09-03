# OpenStreetMap (Overpass) — source notes

**Tier 3.** Crowd-sourced. Per-feature provenance is not verifiable, so an OSM match
is never corroboration on its own — it is a lead, or a second voice next to a real
source. Read this file before trusting any run.

## Data files (per-country, per-substance; gitignored under `data/`)

Unlike gulfpub there is no global extract. Each `datasets:` entry in `manifest.yml`
is one Overpass pull, produced **before** the run:

```bash
python scripts/fetch_overpass.py --iso LY --substance gas --include-lifecycle \
    --out sources/osm/data/ --name osm-ly-gas
```

| Dataset | file `data/…` | features | fetched |
|---|---|---|---|
| `gas` (Libya) | `osm-ly-gas.geojson` | 6 | 2026-07-28 |
| `gas_iq` (Iraq) | `osm-iq-gas.geojson` | 52 | 2026-07-28 |
| `oil_iq` (Iraq) | `osm-iq-oil.geojson` | 246 | 2026-07-28 |
| `gas_eg` (Egypt) | `osm-eg-gas.geojson` | 21 | 2026-07-29 |
| `gas_pk` (Pakistan) | `osm-pk-gas.geojson` | 9 | 2026-08-07 |
| `gas_in` (India) | `osm-in-gas.geojson` | 61 | 2026-08-10 |
| `gas_kz` (Kazakhstan) | `osm-kz-gas.geojson` | 112 | 2026-08-11 |
| `gas_my` (Malaysia) | `osm-my-gas.geojson` | 29 | 2026-08-12 |
| `gas_ua` (Ukraine) | `osm-ua-gas.geojson` | 1004 | 2026-08-12 |
| `gas_uz` (Uzbekistan) | `osm-uz-gas.geojson` | 124 | 2026-08-26 |
| (reference) all Libya | `osm-ly-all.geojson` | 545 | 2026-07-28 |

Ukraine is the extract to keep in mind when reading any other one: 1,004 features is not
1,004 leads. 741 are stubs under 0.5 km and the commonest `operator` values are local gas
distribution utilities, so most of the file is the low-pressure network GGIT does not
track. Feature count is not coverage — trace length and operator are.

Because of that, `fetch_overpass.py` now also carries the **`pressure`** tag through as
`osm_pressure` (2026-08-16), alongside the `usage` tag it already extracted — together they
are the direct signal for transmission-vs-distribution, which is what decides whether an
unmatched trace is a Discovery lead or simply out of GGIT's scope. Neither tag *filters* the
fetch: both are sparse in OSM, and a missing tag must never drop real pipe. **The extracts
above were fetched before that change and do not carry `osm_pressure`** — it appears only in
files fetched from 2026-08-16 on. Re-fetching an existing country to pick it up is safe but
moves the extract under the recon runs already committed against it, so re-run those too.
`gas_uz` (2026-08-26) is the first extract fetched after the change — and it carries **no
`osm_pressure` at all**, because the key is emitted only where OSM has the tag and no Uzbek
feature does. `usage=transmission` on 7 of 124 features is the only transmission signal there.
So the tag being carried through is not the same as the tag being available.

Adding a country = one fetch + one `datasets:` entry. No code.

## Fetch gotchas (all three cost a debugging cycle — don't rediscover them)

- **Use `--iso`, not `--area`.** An OSM boundary's `name` is in the *local* language
  (Libya is `ليبيا`), so `--area "Libya"` matches no area and returns zero features —
  which is indistinguishable from "OSM has no pipelines here". `--iso LY` matches
  `ISO3166-1`. `--area` now unions `name:en` + `name` as a fallback.
- **`--include-lifecycle` is REQUIRED for reconciliation.** A planned or abandoned
  pipeline is not tagged `man_made=pipeline` but `proposed:man_made=pipeline`,
  `construction:man_made=…`, `disused:`, `abandoned:`, `razed:`. Without the flag
  Overpass returns operating pipe only, so every non-operating GEM row falsely reads
  as absent from OSM. The flag also stamps a `lifecycle` property, which the manifest
  maps to `status`.
- **Query the lifecycle keys as one regex, not a union.** A 6-key × (way|relation)
  union over a whole country reliably times Overpass out; `[~"^(man_made|proposed:man_made|…)$"~"^pipeline$"]`
  does not. (`:` is not a regex metacharacter — do not escape it.)
- **`osm_id_key` is NOT unique.** It is built from a merged way's contributing OSM ids, and
  two differently-merged features can land on the same key (Iraq gas: 3 colliding pairs;
  Iraq oil: 12; Egypt gas: 3 features on one key —
  `w1324000712_1324000713_1324000717`, a Y junction whose three branches all merge from
  the same way set, so the key cannot tell them apart). Because `ref_id` is the
  geometry-sidecar key, a collision silently
  *overwrote* one trace and scored both records against the survivor —
  `osm:gas_iq:w1526687293_1526687294` carried a 0.476 km and a 0.095 km trace with
  identical containment and IoU. `ingest.py` now suffixes duplicates `#2..` and warns; the
  warning also means **cross-scrape identity is unreliable** for that dataset until the
  manifest's `provenance.oid_field` names something actually unique.

## `osm_id_key` was NOT unique — FIXED 2026-08-26

`provenance.oid_field: osm_id_key` is what makes cross-scrape identity possible, and it was
broken. `_stitch()` sets the key from `contributing`, i.e. *which source ways share a vertex
with this part* — so when one way group merges into several **disconnected** parts that each
touch the same set of ways, every part got an **identical key**.

Measured across the 10 registered extracts: **62 features collided**, worst by distance in
Uzbekistan (6 features / 865.8 km) and Kazakhstan (7 / 711.7 km), worst by count Ukraine
(26 / 251.7 km); Malaysia and Pakistan had none. The Uzbekistan case is the clearest — one key covered three disjoint pieces of 618.01,
144.95 and 25.49 km.

**No committed finding is falsified.** `ingest.py` already caught it and suffixed `#2`/`#3`, so
no geometry was ever lost or merged. What was broken is **identity**: that suffix is
assignment-order dependent, so a re-scrape could hand `#2` to a different piece and a diff
against an earlier run could not tell you it was the same feature.

`_disambiguate_keys()` now appends a **geometry-derived** discriminator —
`blake2s(coords rounded to 6dp, digest_size=3)` → `…#0823b3`. Stable across re-fetches
(identical geometry ⇒ identical id), and it changes when the shape changes, which is what an
identity key should do.

**It touches ONLY keys that actually collide.** A key that was already unique is emitted
byte-identical, in every extract — verified against all 10: duplicates 62 → 0, no
previously-unique key altered, and the two collision-free extracts unchanged byte-for-byte. So
**re-fetching a country moves nothing except ids that are unstable garbage today**, and no
re-run is owed on any committed recon. Uzbekistan was re-fetched immediately (it had no
committed run to move): 124 features, geometry set identical, 113 of 124 keys unchanged, 11
suffixed, and the ingest collision warning is gone.

`osm-ly-all.geojson` predates the field entirely and has no `osm_id_key` — it is the
reference-only Libya pull, not a registered dataset, and the disambiguation skips it.

## `name:en` is fetched and then discarded — OPEN, measured 2026-08-26

`fetch_overpass.py` carries OSM's `name:en` through as **`osm_name_en`**, but no manifest maps
it and nothing downstream reads it, so **the matcher never sees it.** The canonical record has
an `aliases` field for exactly this (`sources/_schema/canonical_record.md` line 21) and it is
**declared but dead**: `adapter_base.py` defines `aliases` on the dataclass, never populates it
from `column_map`, and `match.py` scores `ref["name_norm"]` alone.

Measured across every extract we hold: **4 features carry a `name:en` the matcher cannot use,
and in all 4 the primary `name` is non-Latin** — so `name:en` is not a nicety, it is the only
name signal those features have.

| dataset | feature | `name` | `name:en` |
|---|---|---|---|
| `gas_kz` | `w291491982_294602571` | `месторождение Шагырлы-Шомышты - компрессорна…` | `Shagyrly Shomyshty Gas Field - Beyneau` |
| `gas_uz` | `w292481601_579695357` | `Средняя Азия - Центр` | `Central Asia-Center` |
| `oil_iq` | `w20171711` | `خط أنابيب كركوك-جيهان` | `Iraq-Turkey oil pipeline` |

The Iraq row is the one that proves the point: `normalize.translit_cyrillic()` does nothing for
Arabic, so `name:en` is the *only* route by which that feature is ever nameable. The 2026-08-14
Cyrillic fix closed the Cyrillic half of this problem and left this half open.

**Not fixed, deliberately.** It is three small changes — populate `aliases` from `column_map` in
`adapter_base.py`, score `max(name_norm, *aliases)` in `match.py`, add `aliases: osm_name_en` to
the OSM manifests — but the third touches the **shared** scorer and would move the committed
`gas_kz` and `oil_iq` runs for a gain of 4 features. Per the 08-14 precedent the likely gain is
corrected "closest GEM" attribution rather than moved buckets. Baird's call, not the agent's.
**It does not block Uzbekistan:** its one affected feature is the CAC trunk, whose GEM rows are
among the 13 excluded from that pass's research legs.

## Matching config (why it differs from the engine defaults)

- **Geometry-dominant weights** (`geometry_weight: 0.45`, `name_weight: 0.10`). Most
  OSM pipelines are unnamed — 74 of Libya's 545 features carry any name — so the
  default `name_weight: 0.30` would sink real matches.
- **`buffer_km_for_overlap: 10.0`**, not the 2 km default. OSM traces are hand-drawn
  and offshore trunks come from rough public sources. OSM's Greenstream and GEM's
  P0439 share a corridor to ~13 km (identical bounds, length ratio 0.96) but score
  IoU 0.07 at a 2 km buffer — the same pipeline reading as no match. 10 km recovers it
  (IoU 0.37) without pulling in neighbours; Libya's next-nearest gas line is ~100 km
  away. Tighten where OSM coverage is dense enough to create near-misses.

## Licence — ODbL, share-alike

Reading OSM to **corroborate** a GEM attribute (what this source does) is not
redistribution. **Copying OSM coordinates into a GEM route is.** Whether OSM-derived
geometry may ship in a GEM tracker is Baird's call at review, never the agent's — so
every feature carries `source`, `license`, and `attribution` properties, and they must
survive into the staged record and the workbook's License column. Never launder an OSM
coordinate into an unlabelled one.

## Coverage reality check — Libya, 2026-07-28

**OSM is not reconciliation-grade for Libya gas.** Of 545 Libyan pipeline features:
270 `substance=oil`, 248 untagged, 21 water, and **6 gas**. Four of the six gas
features are 0.0–0.1 km stubs with no name. The two real ones are both Greenstream.

The run therefore yields exactly one usable pairing — OSM Greenstream → **P0439**
(yellow, 0.53) — against 37 `gem_only` rows. Those 37 are *not* evidence that GEM has
37 pipelines OSM contradicts; they are evidence OSM has not mapped Libya's gas network.
**Do not present an OSM `gem_only` list as a finding.** Check the substance histogram
above before running a new country: if the gas count is single digits, the reconcile
will be noise.

Untagged features (248 here) are excluded by the `--substance gas` filter, so some
real gas pipe may be sitting in that bucket unlabelled. Fetching without `--substance`
and matching on geometry alone is possible but produces mostly oil — not worth it
unless a country's tagging is known to be good.

## Coverage reality check — Iraq, 2026-07-28

**Iraq is thin but genuinely usable — the opposite call from Libya.** The `--substance gas`
fetch returns **52 features**, all tagged `lifecycle=operating`. Length distribution is
what matters: **5 features carry real length** (122.8 / 116.6 / 108.3 / 64.6 / 42.6 km =
455 of the 483 km total) and **40 of 52 are <0.5 km stubs**. So the usable payload is five
traces, not fifty-two.

Only **2 features are named**, both "Erbil - Duhok Gas Pipeline" (GEM **P4053**). The
value here is in the *unnamed* features, which unusually carry real attributes:

- two **Dana Gas 24″** lines totalling ~173 km tracing Khor Mor → Chamchamal → Kirkuk —
  corroborates GEM **P6827** and the Chemchemal discovery candidates;
- one **42″, 116 km** line.

Findings the run produced (routed into the Iraq gas packet):

- **P4053 diameter conflict.** OSM tags 36″, and vemak.com.tr agrees; GEM carries "52″
  confirmed". A material spec conflict on an operating-status candidate.
- **P4053 route displacement.** Endpoint distance ~26 km despite a length ratio of 0.955 —
  a `RouteAccuracy` candidate, not a length problem.

### The 0-overlap run, and what fixed it

The first Iraq gas run returned **0 overlaps from 52 features** with an empty
`route_metrics.json`, and it looked like a legitimate "OSM has nothing here" finding for
weeks. It was not. `reconcile.py` only writes `route_metrics` inside the overlap branch,
so the empty file was a *consequence* of the null, not a cause. Every matching axis was
dead at once: only 2 of 52 features are named (against `name_weight: 0.10`), and 34 of 54
GEM Iraq gas rows have `no route`, so the 0.45-weight geometry signal collapsed to the
`geometry_untested_score` floor on most rows. Top composite in the whole country: **0.438**
against a 0.45 threshold. **A null run is a claim about the matcher until you check the
health line** — `reconcile.py` now emits a `MATCH_QUALITY` escalation for exactly this
shape, and it fires on both Iraq datasets.

The fix was **not** a lower threshold and **not** retuning the shared source-level block
(that would move Libya's committed run). It was two things:

1. **A per-dataset `matching:` override** — the manifest schema now supports one, and
   `gas_iq`/`oil_iq` carry `geoarea_weight: 0.30`. Libya reproduces bit-identically.
2. **The admin-area signal** (`scripts/geo_signals.py`): resolve the trace's Natural Earth
   admin-0/admin-1 footprint and score it against the GEM row's declared geography. This
   is the endpoint signal in the form both sides actually populate — GEM fills
   `Start/EndState/Province` far more often than `Start/EndLocation`. Only *foreign*
   countries score on the country component: inside a country-scoped run, "both are in
   Iraq" discriminates nothing.

Re-run (2026-07-28, same 52 features): **8 overlaps**, 44 unmatched — and the acceptance
test, [way/1494626715](https://www.openstreetmap.org/way/1494626715), now resolves to
**P5855 Iran-Iraq Gas Pipeline** on `geo-foreign 1/1 (iran); geo-admin1 Diyala=endpoint`,
footprint `Iraq/Diyala; Iran/Kermanshah`. It lands at composite 0.4324 — still just under
threshold, filed `ROUTE_FOR_EXISTING` rather than forced over the line, because nothing
physical corroborates it (P5855 has blank Diameter, `LengthKnownKm='--'`, `no route`). That
is the correct outcome: candidate geometry for a human, not a claimed match.

Iraq oil (`oil_iq`, 246 features — the richest OSM extract we hold, still only 5 named)
had **never been run at all**: 71 overlaps, 175 unmatched (84 DISCOVERY_CANDIDATE / 61
FRAGMENT_OF_EXISTING / 21 ROUTE_FOR_EXISTING / 9 NEAR_MISS).

Two standing cautions survive the fix. **Five of the eight gas overlaps are `partial`
coverage** — a 0.1–0.5 km stub matched to a 100 km row corroborates *location* and nothing
else; never read one as length or extent evidence. And Iraq's binding constraint on every
source's matchability is still **missing GEM geometry**, the same lesson as GulfPub Iraq
(`notes/escalation-2026-07-28-gulfpub-iraq-match-quality.md`).

## Coverage reality check — Egypt, 2026-07-29

**Between Libya's null and Iraq's thin-but-usable, and the worst name coverage yet.** The
`--substance gas --iso EG` pull returns **21 features from 24 ways, 476.6 km total**, all
`lifecycle=operating`. Eleven carry real length (106.7 / 77.6 / 69.1 / 61.8 / 61.5 / 52.8 /
28.5 / 11.6 / 3.5 / 1.5 / 0.7 km) and 10 are <0.5 km stubs — so unlike Libya there is real
trunk geometry here. But the attributes are empty: **0 of 21 named, 0 with diameter, 0 with
operator.**

The run returned **0 overlaps** and raised both `MATCH_QUALITY` escalations, which is the
expected reading, not a defect: 0.0% of reference records are named and only 39.5% of GEM
Egypt gas rows have a drawn route (49 of 78 are `no route`, 13 more `very low`), so the
name and geometry axes are both dead and the admin-area signal — live on 52.4% of records,
via `geoarea_weight: 0.30` on `gas_eg`, the same override `gas_iq`/`oil_iq` carry — is
alone. Top composite reached 0.4094 against the 0.45 threshold.

**The threshold was NOT lowered and the weight was not tuned past the documented 0.30.**
The 21 unmatched features are triaged by disposition instead, which is what the disposition
model is for: **9 `ROUTE_FOR_EXISTING`** (candidate geometry for routeless GEM rows — the
run's real value, and a human routes-repo PR, never an auto-replacement), **2
`FRAGMENT_OF_EXISTING`**, **10 `DISCOVERY_CANDIDATE`** (each still needs matching to an
existing row under another name before it is treated as a miss). Do not read the 0 overlaps
as "GEM is missing all 21".

## `_collect_lines()` fed relation-member ways to the stitch TWICE — Egypt oil, 2026-08-27

**The second identity defect in `fetch_overpass.py` in two days, and a different one.**
Yesterday's (`osm_id_key` non-unique, below/above per file order) was a *keying* bug —
distinct geometry colliding on one key. This one is a *duplication* bug: the same geometry
emitted twice as two features.

**Symptom.** The first `--substance oil --iso EG` pull returned **39 features but only 36
unique `osm_id_key`** — on a brand-new fetch, i.e. *after* `_disambiguate_keys()` was in
place. The discriminator is derived from geometry, so two features with byte-identical
geometry hash identically and no suffix can separate them. The collision was the symptom;
the duplication was the disease.

**Cause.** Overpass returns a way that is both independently tagged and a member of a route
relation **twice** — once as a `way` element, once inside the relation's `members`.
`_collect_lines()` appended both, so `linemerge` received the same coordinate string twice
and emitted the shared part twice. Egypt oil's SUMED route relation sits over ways that also
carry their own `man_made=pipeline` tags, which is why it showed up here first.

**Fix.** `_collect_lines()` now indexes ways by OSM way id as it collects them, and a
relation member whose `ref` is already in that index is **not** re-added; instead the
relation's tags fill any key the way lacks (`setdefault`), so a name carried only on the
relation still survives. Separately, `_stitch()` no longer takes the *first* contributing
way's tags as the merged part's sample — it prefers a contributing way that actually carries
a `name`, because a merged part spans several ways and only some are named.

**A/B, verified.** `39 feats / 872.6 km` → `32 feats / 544.5 km`, with the **vertex set
identical: 0 lost, 0 gained**. Nothing but 328 km of double-counted mileage left. Unique
keys went 36/39 → **32/32**.

**Named features dropped 12 → 5, and that is the fix working, not a regression.** The
duplicate inputs were fragmenting the SUMED corridor into more, shorter parts, several of
which independently carried a name. With the duplication gone the parts merge into five
longer strings (`sumed 1`, `sumed 7`, `sumed 8.1/8.2/8.3`) — fewer named *features*, the
same named *pipe*. No name string was lost from the extract.

**Blast radius: Egypt oil only.** All 12 registered extracts were checked for exact-duplicate
features (identical geometry) at the time of the fix; only `oil_eg` had any (3 features /
83.3 km), and it had no committed recon run, so **no committed finding is falsified and no
re-run is owed**. As with yesterday's fix, every other extract keeps its current features and
keys until it is next re-fetched. A duplicated reference record would be a phantom
counterpart in every recon that reads the extract, so the dedup belongs here, at the source,
not in `ingest.py`.

## Coverage reality check — Egypt oil, 2026-08-27

**32 features / 40 ways, 544.5 km, all `lifecycle=operating` + `substance=oil`.** Attributes
are thin but not empty: **5 named** (all SUMED strings), 5 with a diameter, 7 with an
operator — better than Egypt gas's 0/0/0.

**No `geoarea_weight` override, deliberately — Pakistan's reasoning, not Egypt gas's.** The
geometry axis is *alive* on the GEM side here: **45 of 46 GEM Egypt oil rows are routed** (23
`medium`, 7 `low`, 6 `high`, 6 `very low`, 3 `very high`; only P7326 is `no route`), so the
dead-both-axes condition that justifies the admin-area fallback on `gas_eg`/`gas_iq`/`oil_iq`
does not hold. The temptation is real and must be resisted: `StartCountryOrArea` and
`EndCountryOrArea` are filled on all 46 rows and only 2 rows have both state/province cells
blank, so the geoarea axis would score *freely* — and that is exactly the failure mode
measured on Uzbekistan, where a weighted geoarea manufactured overlaps from stubs that were
merely in the right province.
