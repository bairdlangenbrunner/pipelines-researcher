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
| India — gas | PNGRB `pngrb.gov.in` — monthly **NGPL MIS report** (see note below) |
| Pakistan — gas | OGRA `ogra.org.pk`; and SNGPL's own audited asset register (see the Pakistan country note) |
| Kazakhstan — legal/orders | `adilet.zan.kz` (official legal database) — see the Kazakhstan note below |
| Kazakhstan — gas operator | QazaqGaz `qazaqgaz.kz`; Intergas Central Asia `intergas.kz`; KazMunayGas `kmg.kz` + `ar<YYYY>.kmg.kz` |
| (others) | search `"<country>" "energy regulator" OR "petroleum regulator"`; add findings here |

**Kazakhstan — there is NO public line-wise gas-pipeline register** (surveyed 2026-08-11).
Three things to know before spending time on it:
- **`adilet.zan.kz` serves an incomplete TLS chain.** `url_verifier` retries with verification
  off and returns `insecure_tls: True` — that verdict means the page IS live. Never class it
  `DEAD_LINK` or drop an adilet ref over it.
- **The tracker's dominant Kazakh gas ref is Order of the Minister of Energy №350** (29.09.2023,
  "General Gasification Scheme of Kazakhstan 2023–2030", `adilet.zan.kz/rus/docs/G23JVM00350`) —
  about half of all Kazakhstan gas `[ref]` cells. It is **prose planning with no line-wise
  register**; its 12 tables are gas-processing plants, forecasts and consumption segments, and
  the `#z250` anchor most cells use lands in the **appendices, where 5–7 are графические схемы
  (MAPS)**. So a full-text miss is not evidence the ref fails — judge it against the graphics
  too (the Egypt/GASCO lesson). Prose facts it does carry: ¶95 Sarybulak–Zimunay 92.5 km;
  ¶44 Kazakhstan–China A/B/C "до 1300 км" / "до 55 млрд м³/год"; ¶165 Beineu-Bozoy-Shymkent
  commissioned 2013 at 10 bcm/y; ¶36/91/93 Saryarka Phase I ">1,000 km", 25 mcm/d by 2030;
  ¶94 Kartaly–Rudny expansion feeding the new Aktobe–Kostanay MGP; ¶47 2022 transit 71.8 bcm.
- **Best line-wise source: the KazMunayGas Annual Report** "Gas Transportation and Marketing"
  section, table `Company | Trunk gas pipeline | Length, km | Capacity, bln m³/y`, at
  `ar2021.kmg.kz/pdf/ar/en/strategic-report_operating-review_gas-transportation-and-marketing.pdf`
  (also `ar2020`/`ar2019` under `…strategic-report_operating_gas-transportation.pdf`). It itemises
  **only the 8 major systems** — roughly half the network by length; ~17 named Intergas lines are
  never itemised anywhere. **Vintage warning:** AR2019/2020 differ materially from AR2021 (Central
  Asia–Centre 5,306 → 4,149.2 km; Bukhara–Ural 2,382 → 1,567.8; BGR-TBA+Gazli–Shymkent 2,462 →
  1,903.4; Soyuz+Orenburg–Novopskov 1,147 → 805) — a scope redefinition, not a correction, and
  **two vintages of one publisher are ONE origin**. Say which vintage a citation used.
- **Confirmed non-registers, don't re-hunt:** QazaqGaz "IGO 2024" (name-only list of 25 Intergas
  lines + citable *aggregates* — ICA 21,316 km incl. 7,007 km third-party, diameters 57–1,420 mm,
  203.5 bcm/y; AGP 3,915.5 km; BSGP 1,449.50 km); the KASE/KZTG 2023 prospectus; Government
  Postanovleniye 463/2025 and 488/2022 (forward-looking project tables); Order 182-Н/Қ (content is
  a single embedded JPEG map per `pdfimages -list`); Law Z1200000020; stat.gov.kz (aggregates).
  Genuinely deleted (HTTP 404): `gurk.kz`, `kazazot.kz`.

**PNGRB monthly NGPL MIS report — India's authorised-pipeline register.** URL pattern
`https://pngrb.gov.in/data-bank/<YYYYMMDD>-NGPL-MIS-Report.pdf` (month-end stamped;
`20260531` is the May-2026 edition). The "Physical Progress Report of Natural Gas
Pipeline" page carries a **line-wise register of every authorised common-carrier gas
pipeline** in three sections — operational, partially commissioned, under construction —
each row giving authorised / operating / under-construction length, authorised and design
capacity in MMSCMD, authorisation date, target completion and states traversed. Parse it
with `scripts/parse_pngrb_ngpl_mis.py`, which extracts on the PDF's own ruling lines and
**refuses to emit unless the parsed sections reconcile to the report's printed TOTALs**.
- **It settles** length, capacity, authorisation date, and the operating-vs-under-construction
  split. **It does not settle diameter** (no such column) and its *authorisation date is
  NOT a commissioning year* — the two can be a decade apart.
- **Independence caveat:** GEM's India `Capacity` already matches PNGRB authorised MMSCMD
  at two decimals wherever the two agree, so PNGRB is the de facto *origin* of that
  column. Citing it is the correct primary citation but does **not** by itself make two
  independent sources.
- **Scope:** common-carrier only. Dedicated and tie-in lines sit inside the grand totals
  but are not itemised, so absence from the line-wise table is not evidence against a row.
- `url_verifier` reports a content FAIL on this PDF (large-PDF false negative); confirm
  values locally with `pdftotext -layout` and say so in the ref note.
- **The register is a TIME SERIES, and diffing two editions dates a rename or re-scope.**
  Older editions live at a different, un-dated pattern — `.../data-bank/NGPL-<DDMMYYYY>.pdf`
  and `.../data-bank/NGPL-<YYYYMMDD>.pdf` both occur (`NGPL-25062021.pdf`,
  `NGPL-20240626.pdf`). Because the **authorisation number, sponsor and authorisation date
  stay fixed across editions while the project NAME changes**, two editions either side of
  an amendment prove that two differently-named GEM rows are one authorisation. That is how
  the Kanai Chhata duplicate was settled: row `5.11.NGPL`, sponsor HPPL, auth `08.07.2019`,
  317 km / 19.20 MMSCMD is "Kanai Chhata – Shrirampur" in the 2021 edition and "Kanai –
  Chhata – Panitar" in the 2024 one. Prefer this over name similarity — it is dispositive.
- **Per-project PNGRB letters and bid maps carry facts the register omits**, under
  `/pdf/ngp/...`: grant/amendment letters (`.../Govt-Authorization/<NAME>-<DDMMYYYY>.pdf`),
  bidding route maps (`.../bid/bid<N>/Map-<CODE>-Bidding.pdf`, which have a text layer
  giving both endpoints and intermediate towns) and ERDMP certification audits
  (`.../pdf/ngp-audit-report/<YYYYMMDD>_<NAME>.pdf`, valve-station chainage = evidence of
  real operating pipe). Amendment letters are often **image-only scans with no text layer**,
  so `url_verifier`'s substring check cannot see their contents — render to PNG and read it
  rather than concluding the document does not support the value.

Where a country's rows trace to a bulk load off an operator or regulator artifact, look
for that body's own audited register before dispatching per-row research — it is usually
cheaper and better than anything per-row search will find (Pakistan/SNGPL 2026-08-10,
India/PNGRB 2026-08-10).

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

### Wayback Machine — how to reach it, and the `/save/` trap

Wayback is the standard recovery path for dead/blocked origins (the ASB PDFs and PHMSA
above, plus any geo-blocked or WAF'd page — and remember a blocked origin gets its
snapshot *added* alongside the original, never swapped in).

- **A `[ref]` must be a snapshot URL, `web.archive.org/web/<timestamp>/<url>` — never
  `web.archive.org/save/<url>`.** `/save/` is Save Page Now's *instruction* endpoint: it
  triggers a fresh capture of the live origin instead of serving the archive, so it is
  worthless as evidence and dies with the origin. 348 such cells had accumulated in the
  backend and were repaired 2026-08-05 (`notes/wayback-save-repair-20260805/`).
- **Use the playback endpoint, not the APIs.** The availability API
  (`archive.org/wayback/available`) and CDX server (`web.archive.org/cdx/search/cdx`)
  rate-limit hard — a modestly concurrent run got 429s that persisted through minutes of
  backoff, while the playback host kept serving fine. SPN2 (programmatic `/save/`) needs
  an API key we don't have.
- **`https://web.archive.org/web/<ts>/<url>` redirects to the capture nearest `<ts>`, so
  the final URL after redirects IS the verified snapshot link** — one request, no quota.
  A partial or far-future stamp works (`/web/2026/…`, `/web/29991231235959/…`). No
  captures at all → HTTP 404, which cleanly separates "nothing archived" from "archived".
- **HTTP 200 is not enough** — Wayback serves failure pages at 200 ("Got an HTTP 404
  response at crawl time", "has not archived that URL"). Screen the body for those
  markers. And a **5xx is often a property of that one capture** (a poisoned WARC record),
  not an outage: walk back to older captures before concluding anything.

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
  wall, and that is now the norm rather than the exception (anonymous access to work documents
  is being withdrawn deliberately). Read it authenticated: `gws-gem sheets spreadsheets values
  get` per tab, or Google Drive MCP `download_file_content` (`exportMimeType=text/csv`) if it
  is single-tab. Sheet ID + on-disk geojson paths are in the
  `datasets-registry-and-gulfpub-identity` memory. Large geojsons (19 MB) can't go through
  context via Drive MCP — `find` them on local disk instead.

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
