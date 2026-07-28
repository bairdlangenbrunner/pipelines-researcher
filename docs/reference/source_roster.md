# Source roster (pipelines)

Quick reference for picking sources at query time, and the registry of scraped
reference datasets used by reconciliation. Tiers are operational — they feed the
confidence rubric (`confidence_tiers.md`). **No industry dataset is automatically
authoritative**; sponsor IR and primary regulatory filings take priority. When a
new useful source turns up in a batch, add it here and to the relevant
`docs/country_notes/` file.

**Standing rule:** never cite GEM / gem.wiki / globalenergymonitor.org. Wiki pages
link to original sources — use those.

## Tier 1 — Primary (stand-alone for green)

### Sponsors / operators / NOCs
- US/intl operators' IR + SEC filings (10-K/10-Q/8-K), project pages, press
  releases — e.g. Enbridge, Energy Transfer, Plains, MPLX, Kinder Morgan, TC Energy.
- State NOCs: Saudi Aramco (+ AramcoLife), ADNOC, QatarEnergy, NIOC/NIGC (Iran),
  SOMO (Iraq), Sonatrach, NNPC, Pemex, Petrobras, Transneft.
- EPC / yard direct when they name the project: Samsung E&A, KS Al-Hajri,
  Micoperi/Esta, Tecnimont, Saipem.

### Regulators / government (primary when they name the project)
| Jurisdiction | Source |
|---|---|
| US — interstate gas/LNG | FERC eLibrary `elibrary.ferc.gov` |
| US — pipeline safety / mapping | PHMSA + National Pipeline Mapping System `npms.phmsa.dot.gov` |
| US — operator registry / mileage | PHMSA operator data (OpID master list + annual reports) — see note below |
| US — deepwater ports | MARAD |
| US — offshore | BOEM `data.boem.gov`, BSEE |
| US — Texas | Texas RRC GIS viewer |
| US — Alaska | Alaska DNR State Pipeline Coordinator |
| US — data | EIA petroleum/natural-gas |
| Iran | Shana (MOP outlet) `shana.ir` |
| (others) | search `"<country>" "energy regulator" OR "petroleum regulator"`; add findings here |

Oil and Gas Watch (`oilandgaswatch.org`) — digitized routes + permit tracking,
useful as a primary-adjacent lead.

### OPEC Annual Statistical Bulletin (ASB) — the workhorse for OPEC members

The single most productive spec source for Iraq and Libya, and the origin of most of
GEM's existing citations on those rows. **It is a per-pipeline table, not a
country-aggregate compendium** — the gas-pipeline table names individual lines with
their own length/diameter/capacity. That ruling matters: a row whose only citation is
a bare `"OPEC Annual Statistical Bulletin, p. 75"` is **supported, not unsourced**.
Reading the citation as an aggregate withdrew 12 of 16 of our own duplicate/existence
flags on the Iraq pass — `notes/escalation-2026-07-28-asb-iraq-provenance.md`.

- **Table numbers move between editions**: gas pipelines = Table 4.10 (ASB2012),
  Table 9.9 (ASB2017); crude = Table 4.9 / Table 6.9. Cite the edition, not just a page.
- **Access:** live `opec.org` PDF links are dead (they 302 to the homepage). Recover
  the tables from **Wayback snapshots of the ASB PDF via `pdftotext`**. A recovered
  Wayback ASB URL that actually names the pipeline is a valid ref; the bare dead
  `opec.org` link sitting on the row is not.
- **Read the column header before using a number — then check whether the header is
  telling the truth.** Both numeric columns of the gas table have already corrupted
  GEM rows, in opposite directions:
  - **Length** is headed `"(miles)"` but the **Iraq and Libya blocks are tabulated in
    kilometres** (Qatar, Saudi and UAE are genuinely miles). The ingest converted
    anyway → 14 Libya + 19 Iraq rows are 1.609344× too long. ASB2013 fixed the source;
    ASB2012 did not. Memos: `notes/escalation-2026-07-28-asb-{libya,iraq}-length-units.md`.
  - **Capacity** is headed `"(1,000 scm/yr)"` and the ingest dropped the multiplier →
    8 rows (4 Libya, 4 Algeria) compute to zero `CapacityBcm/y`.
    `notes/escalation-2026-07-28-scm-capacity-units.md`.
- The operator string in the tables is often the pipeline company (Iraq: **OPC**, Oil
  Pipelines Company) — which does *not* corroborate a ministry-level `Owner` value.
- A `url_verifier` token FAIL on a large ASB PDF is **not** evidence the source lacks
  the value (see the false-negative families in `docs/sops/sweep.md`).

**PHMSA operator data (pulled 2026-07-20):** `www.phmsa.dot.gov` and its OBIEE
portal (`portalpublic.phmsa.dot.gov`) block non-browser clients (Akamai 403 /
login wall) — fetch the static files **via the Wayback Machine** instead
(`web.archive.org/web/2026/<phmsa url>` works; direct curl does not). Local
snapshots: `data/PHMSA_pipeline_operators_opids_20260508.csv` (OpID master list,
~17.2k operators, per-program flags) and `working_files/phmsa/` (raw xlsx + the
2010–present annual-report ZIPs for gas transmission/gathering and hazardous
liquid — operator-level mileage by state, commodity, decade of install).
Upstream index: phmsa.dot.gov → Data & Statistics → "Pipeline Operators - OpIDs"
and "Distribution, Transmission & Gathering, LNG, and Liquid Annual Data".

## Tier 2 — Trade press & analytics (good leads; pair with a primary for green)
Oil & Gas Journal (OGJ), Pipeline & Gas Journal, Pipeline Technology Journal,
Offshore / Offshore Technology, Rigzone, MEED, Hart Energy, S&P Global Commodity
Insights / Platts, Argus Media, Kpler, RBN Energy, East Daley, Wood Mackenzie,
Interfax, Reuters/Bloomberg energy.

## Tier 3 — Regional / specialized press (corroborators, not standalone)
Tehran Times, Mehr News Agency, Saudipedia, country business press; conference
press (ADIPEC, Gastech); NGO/opposition research (Earthjustice, Sierra Club,
Earthworks) for opposition data only.

**Iraq / Kurdistan (verified productive; some Arabic/FA-only):** Iraq Oil Report, MEES,
Rudaw (Arabic), Shafaq, `attaqa.net`, `al-mirbad.com`, Wattan News (`wattaennews.net`),
thenewregion, kurdistan24. Cross-border lines (Iran/Turkey/Jordan/Syria) usually need
non-English search — seed from the row's `OtherLanguage*` names.

## Reference-dataset registry (scraped route DBs for reconciliation)

Each entry is a `sources/<name>/` registry folder (manifest + optional adapter).

| Dataset | `source_tier` | Commodities | Coverage | Has route geometry | Manifest |
|---|---|---|---|---|---|
| **GulfPub** (PE World Map) | 2 | oil, gas | global | yes (WKT/GeoJSON) | `sources/gulfpub/manifest.yml` |
| **OpenStreetMap** (Overpass) | 3 | oil, gas | per-country pulls (Libya gas today) | yes (ODbL) | `sources/osm/manifest.yml` |

To add a dataset, see `sources/README.md`. A scraped dataset is cited by a non-URL
`report_citation` (name + scrape date), never by a GEM URL.

- **GulfPub ≡ "PE World Map" ≡ Petroleum Economist.** Gas source repointed 2025-12-11 to the
  fuller SDE scrape (`SDE.NG_Pipelines_Global.geojson`, 5,346 feats incl. Iraq; the old 2024
  export was 1,000 feats / no Iraq). **`Capacity_mmcfd` is a constant `300` placeholder — never
  a capacity corroborator.**
- **OSM has no global extract** — unlike GulfPub, each `datasets:` entry is one
  per-country, per-substance Overpass pull produced **before** the run
  (`fetch_overpass.py --iso LY --substance gas --include-lifecycle --out sources/osm/data/`).
  Two flags are mandatory, both learned the hard way: `--iso` (an OSM boundary's `name`
  is in the local language, so `--area "Libya"` matches nothing) and
  `--include-lifecycle` (without it Overpass returns only `man_made=pipeline`, so every
  proposed/construction GEM row falsely reads as absent). OSM also needs a wider
  `buffer_km_for_overlap` (10 km vs GulfPub's 2 km). Coverage is wildly uneven — the
  Libya gas pull is 6 features, effectively Greenstream only. Tier 3: a lead or a
  second voice, never corroboration on its own. Full quirks: `sources/osm/NOTES.md`.
- **The master dataset-registry sheet is NOT public** — a `curl` CSV export hits an HTML login
  wall. Read it via Google Drive MCP `download_file_content` (`exportMimeType=text/csv`). Sheet
  ID + on-disk geojson paths are in the `datasets-registry-and-gulfpub-identity` memory. Large
  geojsons (19 MB) can't go through context via Drive MCP — `find` them on local disk instead.

## Public GIS endpoints (route geometry — §8 route creation)

Machine-fetchable GIS layers for candidate route geometry, registered in
`sources/gis_endpoints.yml` (name, kind `arcgis`|`overpass`|`download`, url, coverage,
commodities, license, notes). Fetched by `fetch_arcgis.py` / `fetch_overpass.py`; new
endpoints found during a run get appended there + a line here.

- **Texas RRC**, **BOEM** (US onshore/offshore) — ArcGIS REST; seeded as entries with
  an empty `url` + portal/discovery notes (no guessed FeatureServer paths — standing
  rule 2). **NPMS** blocks bulk export → human cross-check only, not an entry.
- **Israel Land Registry plan store** (`israel_itur_tabot`) — statutory-plan (תמ"א/תב"ע)
  GIS bundles at `apps.land.gov.il/IturTabotData/download/<bucket>/<planID>.zip`: scanned
  blueprint JPG + JGW world file (EPSG:2039) = exact georeferencing, no GCP fit. Verified
  2026-07-23 (plan 1053432, TAMA 37/A/2/7 Ashdod–Ashkelon). Israeli **Notices to Mariners**
  (רספ"ן; official gov.il pages Cloudflare-403, mirrors work) publish pipe-lay corridors as
  coordinate polygons — a citable vector source for offshore lines (NtM 113/2024 precedent).
- **OSM (Overpass)** — `man_made=pipeline`; every feature carries ODbL provenance.
  **Caution:** ODbL is a share-alike license; whether it's acceptable for a GEM tracker
  is **Baird's review call**, surfaced end-to-end (workbook License column), never
  decided by the agent.

## Facility gazetteer (GOGET / GOGPT — internal, non-citable)

GEM's own extraction (GOGET) and oil-&-gas-plant (GOGPT) databases, snapshotted into
`data/` by `refresh_facility_gazetteer.py`, back an endpoint gazetteer
(`facility_gazetteer.py`) used **only** to resolve/snap route endpoints and note the
facility a corridor serves (§8). As GEM databases they are bound by standing rule 1:
**never written to a `[ref]` cell, never counted toward the 2-independent-source
corroboration tier.** Every hit is flagged `citable: false`; each anchored endpoint
still needs its own independent public `[ref]`.

## Forbidden / cautioned
- **GEM.wiki / globalenergymonitor.org** — never self-cite (standing rule 1).
- **Wikipedia** — never cite directly; use it only to reach original sources.
- **A Barrel Full (`abarrelfull.wikidot.com`) and any `wikidot.com` page** — tertiary
  wiki aggregators that restate other sources (same class as Wikipedia). Never cite;
  read only to reach the underlying source. `url_verifier` rejects them.
- **theodora.com** — never an acceptable reference (`url_verifier` rejects it).
- A scraped dataset alone never reaches green (Tier-2 ceiling).

## Most productive search patterns
- Decompose a stuck pipeline ID into components: trunk line + KP reference +
  commodity + receiving facility, rather than the exact string.
- Add contract/procurement keywords — year ranges, `tender`, `EPC`, `award`,
  `construction` — which beat route-based queries alone.
- `"<country>" new oil pipeline <year>`, `"<operator>" "<pipeline>" status`,
  `site:<regulator-domain> "<project name>"`, `"<project>" "FID"`.
