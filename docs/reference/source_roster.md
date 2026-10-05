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
| US — data | EIA petroleum/natural-gas; **gas project workbooks archived locally** — see note below |
| Iran | Shana (MOP outlet) `shana.ir` |
| India — gas | PNGRB `pngrb.gov.in` — monthly **NGPL MIS report** (see note below) |
| Pakistan — gas | OGRA `ogra.org.pk`; and SNGPL's own audited asset register (see the Pakistan country note) |
| Kazakhstan — legal/orders | `adilet.zan.kz` (official legal database) — see the Kazakhstan note below |
| Kazakhstan — gas operator | QazaqGaz `qazaqgaz.kz`; Intergas Central Asia `intergas.kz`; KazMunayGas `kmg.kz` + `ar<YYYY>.kmg.kz` |
| Egypt — ministry | Ministry of Petroleum & Mineral Resources `petroleum.gov.eg` — news pages `/ar-eg/media-center/news/news-pages/Pages/Mop_<DDMMYYYY>_NN.aspx` **and its `/Documents/*.pdf` library** (see note below) |
| Egypt — gas transmission operator | GASCO `www.gasco.com.eg` — note the **`www.` is required** (the bare host has no A record) and its uploads keep **spaces in filenames**; the project register is described below |
| (others) | search `"<country>" "energy regulator" OR "petroleum regulator"`; add findings here |

**Kazakhstan — there is NO public line-wise gas-pipeline register** (surveyed 2026-08-11).
Three things to know before spending time on it:
- **`adilet.zan.kz` serves an incomplete TLS chain.** `url_verifier` retries with verification
  off and returns `insecure_tls: True` — that verdict means the page IS live. Never class it
  `REF_BLOCKED`/`DEAD_LINK` or drop an adilet ref over it.
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

Oil and Gas Watch (`oilandgaswatch.org`, Environmental Integrity Project) — digitized routes +
permit tracking, useful as a primary-adjacent lead; 85 `/pipeline/<id>` refs across both
trackers. The site is a JavaScript app: every page is the same empty shell and the record comes
from `https://oilandgaswatch.org/api/01-01_PIPELINES/data/<id>` (JSON; answers only to a
same-origin-looking request — browser UA, `Accept: application/json`, `Referer`/`Origin` on the
site, `Sec-Fetch-Site: same-origin`, `Sec-Fetch-Mode: cors`, `Sec-Fetch-Dest: empty`).
`url_verifier` reads that record for you (`fetch_route: oilandgaswatch data api …`); to read it
by hand, `python scripts/fetch.py` on the page URL shows only the shell.

**Egypt — GASCO publishes a machine-readable project register, and GEM's link to it is
mistyped** (found 2026-08-27). **"National Natural Gas Grid Expansion Projects"**, 1 page,
generated from Excel 18 Dec 2024, English, extracts cleanly with `pdftotext -layout`:

> `https://www.gasco.com.eg/wp-content/uploads/2024/12/National%20Natural%20Gas%20Grid%20Expansion%20Projects.pdf`

Per project it gives **length (km), diameter (in), governorate, cost in BOTH EGP and USD
millions, status, and completion date** — better structured than the news pages this project
normally works from, and it is the transmission operator's own. It underpins at least four GEM
rows (P8005, P8006/P8007, P8055, P6685), and P8055 and P6685 were clearly entered *from* it:
their `ProjectLevelCost` values reproduce its USD column exactly.

**Three traps, all live:**
- **The filename uses spaces (`%20`), not hyphens.** Eight `[ref]` cells cite a hyphenated
  variant that returns an honest 404. That 404 is about the *spelling*, not the document.
- **`gasco.com.eg` without `www.` does not resolve at all** — a `ConnectionError`, which the
  standing rule does not treat as a deletion. Do not read one as the other.
- **`url_verifier` returns `insecure_tls: True`** here (incomplete cert chain, same signature as
  `adilet.zan.kz`) — that means the page **is live**, identity merely unconfirmed.

Generalising: **before calling an Egyptian source deleted, vary the URL** — spaces vs hyphens,
`www.` vs bare — and query Wayback **host-wide** (`matchType=domain`), not by exact URL. The
capture of this file was invisible to an exact-URL CDX query and surfaced immediately in a
domain listing. Worked example: `notes/escalation-2026-08-27-egypt-gas-trans-sinai-cluster-and-p3931.md`.

**Egypt — the ministry's `/Documents/` PDF library is a separate surface from its news pages,
and it is under-used** (found 2026-08-27). The news pages under
`/ar-eg/media-center/news/news-pages/Pages/` are what the tracker already cites heavily; the
document library at
`/ar-eg/gas-and-petrol/distribution-marketing-transporting/Documents/` is not. Its
**"2020 خطوط الشبكة القومية للغازات الطبيعية"** ("2020 National Natural Gas Network Lines",
2 pp, live 200, Wayback capture `20260730181015`) is an official narrative of the national grid
programme and names individual projects:
- grid length, mains + branches, end FY2021/22: **~86,000 km**;
- **executed FY2014/15 → Jan 2023: 1,234 km total, ~19.5 bn EGP** incl. compressor stations —
  named: the feeders to the New Administrative Capital, Burullus and Beni Suef power stations
  (Siemens); **خط غاز العامرية/العلمين** (Ameriya/El Alamein, to New Alamein City); and
  **خط التينة غرب/ميت نما** (El-Tina West / Mit Nama, carrying Zohr gas);
- **under construction: ~75 km total, ~7.5 bn EGP** — named: **خط السليمانية/شمال الجيزة**
  (Suleimaniya / North Giza), the Fayoum old-expansions feeder project (Hayah Karima),
  **خط ازدواج عبر سيناء** (the Trans-Sinai *duplication* line), and Dahshour compressor units 5 & 6.

It is Arabic, RTL, and extracts cleanly with `pdftotext` (~4.2k chars) — no visual read needed.
It is a **status and existence** source, not a spec source: it gives no per-line diameter or
capacity, and its lengths are programme totals, never per-line. Search the library by browsing
the `/Documents/` path rather than by site search — and note that `egyptoil-gas.com/?s=` and
`/reports_category/…/page/N/`, which 16 Egypt rows were resting on, are navigation surfaces that
`url_verifier` now rejects outright.

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

**EIA Natural Gas Pipeline Projects (every release, tracked):** EIA's quarterly
project workbook is the single best public table of US gas project cost, capacity,
miles, diameter, in-service year, status and FERC docket. **Every release from May
2018 on is checked into `sources/eia_pipeline_projects/raw/`** — don't re-download
the undated `EIA-NaturalGasPipelineProjects.xlsx` per row; read the local file and
cite the *dated* release URL that states the value, with sheet + Excel row in the
note. `prepare.py` builds a long table plus a latest-with-history table (the release
a project first shows `Completed`/`Cancelled` bounds its year), and
`scripts/eia_crosswalk.py` pre-matches GEM US gas rows to EIA projects and lists the
value disagreements — run it at the start of each US gas batch. **All releases are
ONE origin**, so EIA never supplies rule 4's second source on its own. Quirks,
file-name irregularities and the EIA→GEM status map: `sources/eia_pipeline_projects/NOTES.md`.

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

## China (zh) — verified hosts, seeded from Guangxi 2026-07-29 + Jiangxi v3 2026-09-10

**Search and cite in Chinese** — `OtherLanguagePrimaryPipelineName` is the search key.
80 hosts verified live across the Jiangxi v3 sweep; these are the productive ones, and the
tier is the usual test (who is making the statement), not the domain suffix.

**Primary — approvals, filings, acceptance:**
`mee.gov.cn` (环评/审批 announcements — the single most productive class),
`ndrc.gov.cn` + `nea.gov.cn` (+ `zjb.nea.gov.cn`), `drc.jiangxi.gov.cn`, and the
**county/prefecture portals**, which carry the documents nothing else does:
`quannan.gov.cn`, `swj.jiujiang.gov.cn`, `wuning.gov.cn`, `sthjj.quanzhou.gov.cn`,
`jxsggzy.cn` (public-resources tendering), `jxganan.com` (安全验收评价 filings).
`static.sse.com.cn` (SSE bond disclosures) and `chinamoney.com.cn` are the best owner /
capex / phase sources — a prospectus **enumerates** completions, so an omission there is
evidence, not silence. `qxb-pdf-osscache.qixin.com` serves corporate-registry extracts
(entity/ownership only).

**Operators:** `pipechina.com.cn` (its 公平开放 inventories are exhaustive enough that an
omission is a finding), `cnpc.com.cn`, `sinopec.com` / `trqi.sinopec.com`, `sasac.gov.cn`.

**Press (corroborators):** `xinhuanet.com` / `news.cn`, `paper.people.com.cn`, `cnr.cn`,
`chinanews.com.cn`, `thepaper.cn` (澎湃), `jxnews.com.cn`, `cpnn.com.cn` (中国电力报),
`china5e.com`, `chndaqi.com`, `news.bjx.com.cn` (北极星), `sina`/`sohu` rehosts of official
releases. Republications of ONE original are ONE source (standing rule 4).

**Gotchas, all measured:**
- **`quannan.gov.cn` 403s over IPv6 and 200s over IPv4** — `curl --ipv4` +
  `pdftotext -layout`. `url_verifier` has no IPv4 retry, so its FAIL there is a tooling
  artifact, never a deletion.
- **`chinanews.com.cn` needs lenient decoding** — strict `gb18030` *and* `utf-8` both
  reject its mixed bytes; `errors='replace'` reads cleanly.
- **`fgw.gxzf.gov.cn` (Guangxi DRC) ConnectTimeouts on both schemes** (overseas
  geo-blocking) — cite a Wayback snapshot, note the original, never drop the source.
- Government hosts link-rot fast: Jiangxi's citable DRC plan (江西省天然气利用规划
  2013–2020, 赣发改规划 2014 325号) survives only as `img9.qianzhan.com/policy/…pdf`,
  a **rehosted primary** — citable, but a 2014 planning document is thin support for 2026
  operating status.
- **`fzggw.jiangsu.gov.cn` is Jiangsu, not Jiangxi.** The wiki harvest keeps offering it;
  it is always a false lead.
- **Banned:** `yingdodo.com` (see Forbidden below) — and it arrives via gem.wiki's own
  citation list, so it is blocked in `BLOCKLIST_HOSTS` rather than left to recognition.

## Reference-dataset registry (scraped route DBs for reconciliation)

Each entry is a `sources/<name>/` registry folder (manifest + optional adapter).

| Dataset | `source_tier` | Commodities | Coverage | Has route geometry | Manifest |
|---|---|---|---|---|---|
| **GulfPub** (PE World Map) | 2 | oil, gas | global | yes (WKT/GeoJSON) | `sources/gulfpub/manifest.yml` |
| **OpenStreetMap** (Overpass) | 3 | oil, gas | per-country pulls (Libya gas today) | yes (ODbL) | `sources/osm/manifest.yml` |
| **Malaysian Gas Map** (MGA, 2022 ed.) | 3 | gas | Malaysia only | yes (digitized) | `sources/malaysian_gas_map/manifest.yml` |
| **Seala gas map** (seala.ru, divergent lines only) | 4 | gas | Russia only, 31 lines | rights not established; never a ref | `sources/seala/manifest.yml` |
| **PPIS Energy Infrastructure Map 2025** (DGPC/PPIS/LMK) | 3 | gas, oil | Pakistan only | yes (digitized) | `sources/pakistan/manifest.yml` |

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
- **Malaysian Gas Map is the registry's first *digitized document*** rather than a scrape
  or an API pull — a vector PDF wall map (Malaysian Gas Association, 2022 ed.,
  `malaysiangas.com`) traced into 67 pipeline LineStrings + 616 field polygons.
  Registered 2026-08-12. Three things make it unlike the other two, all in
  `sources/malaysian_gas_map/NOTES.md`: (1) its per-segment **labels are provably
  wrong** — 37 of 67 read "Sabah–Sarawak Gas Pipeline (SSGP)", i.e. every feature in
  the Borneo inset — so the manifest maps **no `name` and no `status`** and it is
  matched as unnamed geometry; (2) `buffer_km_for_overlap` is **12 km**, which is the
  georeferencing residual (11 GCPs, mean 6.7 km on the peninsular inset), not matcher
  slack; (3) it carries **no attribute length**, so the standing `geodesic ÷ declared`
  unit proof is N/A rather than unrun. Ingest input is re-derived by
  `sources/malaysian_gas_map/prepare.py`; the as-delivered artifacts are tracked in
  `extraction/`. Note GEM's P1065/P1066 already cite this same publication in
  `Route [ref]`, so it is **not fully independent** of those two rows' geometry.
- **PPIS map is the registry's second digitized document**, and the first where the
  **source PDF itself is tracked** — page 6 of the Pakistan Petroleum Information
  Service *Investment Brochure 2025* (`ppisonline.com`, DGPC/PPIS/LMK Resources), a
  vector page, so `sources/pakistan/prepare.py` re-derives all 412 LineStrings
  (21,460 km) from the PDF deterministically; nothing is hand-traced. Registered
  2026-08-26. Four things to know, all in `sources/pakistan/NOTES.md`: (1) the map's
  **own drawn graticule is not the control** — it carries a +12.3 km north bias, so
  the transform is fitted to 57 city GCPs (LCC, median 3.3 km, p90 14.7 km) and the
  graticule is only a cross-check; (2) `buffer_km_for_overlap` is **12 km**, the
  stacked error budget of this extraction plus GEM's own schematic Pakistani
  geometry, not matcher slack; (3) the legend **conflates two GEM statuses** on
  "OIL PIPELINE UNDER CONST./PLANNED", so those 12 features carry a **blank**
  status rather than a coin flip — `ingest.py` reporting `UNMAPPED status (12)` is
  expected; (4) it maps **no name, diameter, length or operator** — the page labels
  cities and fields, not segments — so it is matched as classified geometry and
  corroborates **corridors and existence only**, never a spec. (5) **No dashed line in
  the PDF carries a dash array** — dashes are separate primitives, either filled polygons
  (the import corridors) or 0.035 pt hairline strokes (every dashed line in the map body),
  and both are stitched into ONE LineString per dashed run, so a dashed pipeline is never
  emitted as a string of fragments. Those hairlines sit in the operators' EXISTING colour
  and are separated from solid pipe **only by stroke width**; the legend pairs a solid
  EXISTING and a dashed PLANNED entry in the identical colour, so the 21 stitched runs are
  `sngpl_gas_planned` / `ssgcl_gas_planned` at `proposed`, not operating. The 86
  SSGCL-planned filled marks stay unextracted — all inside the differently-scaled
  Hyderabad-Badin inset.
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

## Wikipedia — citable (policy reversed, Baird 2026-08-27)
**Wikipedia is an acceptable `[ref]`**, and the distinction that matters is
**Wikipedia is not gem.wiki**: rule 1 forbids self-citation, not encyclopedias. The
prior roster line ("never cite directly") is withdrawn — it was never enforced by
`url_verifier` and had left ~36 live Wikipedia `[ref]` cells in the tracker in a
permanent grey zone (mentions by scope, 2026-08-27: Ukraine 141 / Iran 72 / Libya 47 /
Kazakhstan 40 / Saudi gas 38 / Egypt 26 / India 19 / Pakistan 16). Treat it as any other secondary source:

- **Tier it as one secondary source** — one validated Wikipedia ref is green like any other
  (rule 4, 2026-09-30), but it counts as ONE origin for the `independent` flag and for a
  status change's 2+. Two language editions of the same article
  are ONE source, not two — the interwiki text is usually a translation. This is now
  *enforced*, not just stated: `normalize_independence.py` collapses every
  `*.wikipedia.org` ref to a single `WIKIPEDIA-INTERWIKI` origin. It had to be, because
  a P4947 recovery record counted en: and zh: as two independent sources for the same
  9,102 km figure and its report said so in as many words (2026-09-10).
- **Prefer the underlying citation when the article carries one** — it is nearly always
  the better `[ref]` and often primary. Citing Wikipedia is allowed, not preferred.
- **A Wikipedia statement whose own footnote is GEM cannot corroborate anything.**
  Rule 1 exists to surface what *other* sources say; a GEM figure that has been copied
  into Wikipedia and cited back is still GEM. Check the article's footnote before
  counting it toward the 2-independent-source tier.
- The `[ref]` should point at the specific article, not a category or portal page.

## Forbidden / cautioned
- **GEM.wiki / globalenergymonitor.org** — never self-cite (standing rule 1). This is
  the one wiki that stays forbidden; `url_verifier` rejects it by host.
- **A Barrel Full (`abarrelfull.wikidot.com`) and any `wikidot.com` page** — tertiary
  aggregators that restate other sources with no editorial trail and no footnotes to
  chase. Never cite; read only to reach the underlying source. `url_verifier` rejects
  them. (They are NOT "the same class as Wikipedia" — that comparison is withdrawn
  along with the Wikipedia ban.)
- **theodora.com** — never an acceptable reference (`url_verifier` rejects it).
- **yingdodo.com (小柱工程)** — a commercial construction-**leads** database; banned
  2026-09-10 off the Jiangxi v3 sweep, `url_verifier` rejects it. The page it keeps
  serving for Jiangxi (`/html/news/201852592751.html`) is an explicit marketing
  **sample**: `项目样例1类`, `备注：以下样例非最新项目，仅表示内容格式`, redacted owner
  phone numbers, and no attribution line of any kind (来源/转载/出处/责任编辑/数据来源/
  信息来源 all absent). Same class as A Barrel Full — it restates someone else's filing
  without saying whose. **It reaches agents from GEM's own gem.wiki citation list** (27
  Jiangxi PIDs, link text `乐平-德兴-婺源支线工程`), which is why the ban lives in
  `BLOCKLIST_HOSTS`: `harvest_wiki_citations.py` imports that tuple and now drops it
  before it is ever offered as a seed. Its figures (97 km, 德兴境内 9.9 km, DN200,
  6.3 MPa, 投资2亿元, 开工 2018-06-13) are plainly lifted from a Jiangxi 立项备案
  filing — chase that filing, cite it, never cite the aggregator.
- **URL shorteners** (`bit.ly`, `tinyurl.com`, `goo.gl`, `t.co`, `ow.ly`, `buff.ly`,
  `is.gd`, `rebrand.ly`, `cutt.ly`, `shorturl.at`, `trib.al`) — never a citable address:
  an opaque, revocable indirection whose target can be repointed after we cite it.
  Resolve it and cite the target document. `url_verifier` rejects them pre-fetch, and
  re-applies the GEM + blocklist bans to the final URL **and every redirect hop** —
  because a ban is about the bytes served, never the string submitted. Until
  2026-09-04 it was a string test on the submitted URL only, so `bit.ly/2sYGqrY`
  verified clean while serving abarrelfull; nine such cells are live in the tracker.
  `notes/escalation-2026-09-04-shortened-urls-bypass-the-blocklist.md`.
- A scraped dataset alone never reaches green (Tier-2 ceiling).

## Most productive search patterns
- Decompose a stuck pipeline ID into components: trunk line + KP reference +
  commodity + receiving facility, rather than the exact string.
- Add contract/procurement keywords — year ranges, `tender`, `EPC`, `award`,
  `construction` — which beat route-based queries alone.
- `"<country>" new oil pipeline <year>`, `"<operator>" "<pipeline>" status`,
  `site:<regulator-domain> "<project name>"`, `"<project>" "FID"`.
