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
| US — deepwater ports | MARAD |
| US — offshore | BOEM `data.boem.gov`, BSEE |
| US — Texas | Texas RRC GIS viewer |
| US — Alaska | Alaska DNR State Pipeline Coordinator |
| US — data | EIA petroleum/natural-gas |
| Iran | Shana (MOP outlet) `shana.ir` |
| (others) | search `"<country>" "energy regulator" OR "petroleum regulator"`; add findings here |

Oil and Gas Watch (`oilandgaswatch.org`) — digitized routes + permit tracking,
useful as a primary-adjacent lead.

## Tier 2 — Trade press & analytics (good leads; pair with a primary for green)
Oil & Gas Journal (OGJ), Pipeline & Gas Journal, Pipeline Technology Journal,
Offshore / Offshore Technology, Rigzone, MEED, Hart Energy, S&P Global Commodity
Insights / Platts, Argus Media, Kpler, RBN Energy, East Daley, Wood Mackenzie,
Interfax, Reuters/Bloomberg energy.

## Tier 3 — Regional / specialized press (corroborators, not standalone)
Tehran Times, Mehr News Agency, Saudipedia, country business press; conference
press (ADIPEC, Gastech); NGO/opposition research (Earthjustice, Sierra Club,
Earthworks) for opposition data only.

## Reference-dataset registry (scraped route DBs for reconciliation)

Each entry is a `sources/<name>/` registry folder (manifest + optional adapter).

| Dataset | `source_tier` | Commodities | Coverage | Has route geometry | Manifest |
|---|---|---|---|---|---|
| **GulfPub** (PE World Map) | 2 | oil, gas | global | yes (WKT/GeoJSON) | `sources/gulfpub/manifest.yml` |

To add a dataset, see `sources/README.md`. A scraped dataset is cited by a non-URL
`report_citation` (name + scrape date), never by a GEM URL.

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
