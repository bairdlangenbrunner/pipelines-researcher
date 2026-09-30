# GEM naming conventions — countries, territories, subdivisions

GEM-wide authority for country / territory / subnational naming, used across all trackers:
Google Sheet **"GEM Naming Conventions - Regions, countries & subdivisions"**
`1mtlwSJfWy1gbIwXVgpP3d6CcUEWo2OM0IvPD6yztGXI`
(<https://docs.google.com/spreadsheets/d/1mtlwSJfWy1gbIwXVgpP3d6CcUEWo2OM0IvPD6yztGXI/edit?gid=0#gid=0>).
Read it through `gws-gem` (Sheets `values.get`, tabs by title) — never an anonymous export URL.

The CSVs here are a snapshot of every tab, pulled 2026-09-30. **The live sheet wins** — re-pull
before relying on a snapshot value for a ruling, and refresh this folder when it changes.

| file | tab | what it is |
|---|---|---|
| `countries.csv` | Countries | ISO 3166 name → **GEM Standard Country Name**, ISO codes, `Territory` / `Territory of` |
| `country_subdivisions.csv` | Country subdivisions | ISO alpha-3 → GEM subnat code, **Subnational name**, name variations, category |
| `subdivision_iso_3166_2_names_not_in_gem_standard.csv` | Subdivision ISO 3166-2 names not in GEM standard | where GEM's name deviates from ISO, with notes |
| `regions_subregions.csv` | Regions & subregions | UN M49 regions / sub-regions |
| `region_comparisons.csv` | Region comparisons | GEM vs UN / IEA / IRENA region definitions |
| `notes.csv` | Notes | the policy text (below) |
| `changelog.csv` | Changelog | dated changes |

## Rules that decide research questions

- **Russian-occupied Ukraine is Ukraine.** GEM treats Crimea, Sevastopol and the Donbas
  (Donetsk, Luhansk — and by the same rule Zaporizhzhia/Kherson) as part of **Ukraine, not
  Russia**. The subdivisions sit under `UKR`: `UA-43 Avtonomna Respublika Krym`,
  `UA-40 Sevastopol`, `UA-14 Donetska`, `UA-09 Luhanska`, `UA-23 Zaporizka`, `UA-65 Khersonska`.
  A Krasnodar–Crimea line is a Russia–Ukraine cross-border line.
- **Abkhazia is Georgia** (`GE-AB`); South Ossetia has no subdivision of its own — it falls in
  Georgia's `GE-SK Shida Kartli` / neighbouring regions.
- **GEM recognizes the autonomy of Kosovo, Palestine, Taiwan and Western Sahara** — each is its
  own country (`Territory = yes`, `Territory of = Disputed / <state>`).
- Country names follow ISO 3166-1 with GEM shortenings (`Russia`, `Moldova`, `Taiwan`,
  `Palestine`, `Türkiye` since 2022-12-01) and additions (`Kosovo`, code `XK`/`XXK`).
- Subdivisions follow ISO 3166-2 (highest commonly used level), standardized as of April 2026
  and **being rolled into the database** — the GEM `Subnational name` (e.g. `Yamal-Nenets`,
  `Khanty-Mansi`, `Sakha`, `Komi`, `Adygeya`) can differ from strings currently on the tracker
  sheets. Exceptions: Monaco, Norway, Western Sahara.
- 2026-08-06 correction: Russian `Krasnodar` and `Krasnoyarsk` had been swapped; fixed in the sheet.
