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
| gas (Libya) | `osm-ly-gas.geojson` | 6 | 2026-07-28 |
| (reference) all Libya | `osm-ly-all.geojson` | 545 | 2026-07-28 |

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
