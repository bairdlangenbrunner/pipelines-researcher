# Recovered cell values — P8017 / P8020 (Egypt gas), backend revision of 2026-08-14

Both rows were entered by `NA` (P8017 on 2026-07-28, P8020 on 2026-07-29) and cleared
from the gas tab on 2026-08-14 19:26 UTC (backend revision `345949`), with no entry on
the `Removed oil/NGL/gas pipelines` tab. Their ProjectIDs were then reused for two
Iraq `Baiji-Mosul Gas Pipeline` segments (`AL`, 2026-08-24).

Values below are the verbatim hand-entered cells as of revision `345873` (2026-08-14
17:46 UTC, the last clean state), read through the authenticated Drive revision export.
**Drive keeps revisions ~14 days, so this table is the only remaining copy after roughly
2026-08-28.** Formula/computed columns are omitted — they regenerate.

- **P8017 has been restored** as `P8084` (2026-08-27, 26 cells; backup CSV:
  `notes/backup-2026-08-27-p8084-restore-p8017-p8020-route-reset.csv`). Its route geojson
  moved with it (`P8017.geojson` → `P8084.geojson`, routes merge `1ccf6cfa`).
- **P8020 has NOT been restored** — no ProjectID assigned. Its geometry is now a null
  placeholder in the routes repo. Restore it from the table below if wanted.

## P8017

| Cell | Column | Value |
|---|---|---|
| `C` | PipelineName | Suez-Cairo Ring Gas Pipeline |
| `F` | ProjectID | P8017 |
| `H` | Status | operating |
| `I` | Status [ref] | https://egyptoil-gas.com/?s=Gas+Pipelines+Egypt |
| `J` | Researcher | NA |
| `K` | LastUpdated | 2026-07-28 |
| `L` | Fuel | Gas |
| `M` | Fuel [ref] | https://egyptoil-gas.com/?s=Gas+Pipelines+Egypt |
| `N` | PipelineType | transmission |
| `O` | PipelineType [ref] | https://egyptoil-gas.com/?s=Gas+Pipelines+Egypt |
| `S` | CountriesOrAreas | Egypt |
| `AX` | Capacity | 90.0 |
| `AY` | CapacityUnits | MMcf/d |
| `AZ` | Capacity [ref] | https://egyptoil-gas.com/?s=Gas+Pipelines+Egypt |
| `BF` | LengthKnown | 150.0 |
| `BG` | LengthKnownUnits | km |
| `BI` | Length [ref] | https://egyptoil-gas.com/?s=Gas+Pipelines+Egypt |
| `BU` | StartState/Province |  Suez |
| `BV` | StartCountryOrArea | Egypt |
| `CA` | EndState/Province | Cairo |
| `CB` | EndCountryOrArea | Egypt |
| `CF` | Location [ref] | https://egyptoil-gas.com/?s=Gas+Pipelines+Egypt |
| `DC` | RouteType | Mapped route (at any accuracy) |
| `DD` | RouteAccuracy | medium |
| `DE` | RouteNotes | CB: route from gulfpub — GulfPub 'Suez - Dahshour Pipeline' (135.8 km vs sheet 150). Name mismatch: GEM calls this Suez-Cairo Ring; Dahshour is the SW-Cairo ring terminus so the identity is plausible but single-source — accuracy capped at medium. |
| `DF` | RouteCreator | CB |

## P8020

| Cell | Column | Value |
|---|---|---|
| `C` | PipelineName | Cairo Ring-Port Said Gas Pipeline  |
| `F` | ProjectID | P8020 |
| `H` | Status | operating |
| `I` | Status [ref] | https://egyptoil-gas.com/?s=Gas+Pipelines+Egypt |
| `J` | Researcher | NA |
| `K` | LastUpdated | 2026-07-29 |
| `L` | Fuel | Gas |
| `M` | Fuel [ref] | https://egyptoil-gas.com/?s=Gas+Pipelines+Egypt |
| `N` | PipelineType | transmission |
| `O` | PipelineType [ref] | https://egyptoil-gas.com/?s=Gas+Pipelines+Egypt |
| `S` | CountriesOrAreas | Egypt |
| `AX` | Capacity | 230.3 |
| `AY` | CapacityUnits | MMcf/d |
| `AZ` | Capacity [ref] | https://egyptoil-gas.com/?s=Gas+Pipelines+Egypt |
| `BF` | LengthKnown | 130.0 |
| `BG` | LengthKnownUnits | km |
| `BI` | Length [ref] | https://egyptoil-gas.com/?s=Gas+Pipelines+Egypt |
| `BU` | StartState/Province | Cairo |
| `BV` | StartCountryOrArea | Egypt |
| `CA` | EndState/Province | Port Said |
| `CB` | EndCountryOrArea | Egypt |
| `CF` | Location [ref] | https://egyptoil-gas.com/?s=Gas+Pipelines+Egypt |
| `DC` | RouteType | Mapped route (at any accuracy) |
| `DD` | RouteAccuracy | very low (straight line/schematic) |
| `DE` | RouteNotes | CB: route guessed from endpoints — Never previously routed. OPEN and material: the 186 km chord between GEM's own Cairo Ring node (start of the applied P8017 route) and Port Said is far longer than the 130 km the sheet states, so either the length is wrong or 'Cairo Ring' here denotes a different, more northerly node than P8017's. Geometry is directionally right, length unresolved. |
| `DF` | RouteCreator | NA; CB |
| `DG` | Route [ref] | https://www.openstreetmap.org/node/27564975 |

