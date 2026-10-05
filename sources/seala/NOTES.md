# Seala gas map (seala.ru) - source notes

**Tier 4, Russia gas, 31 lines only.** Registered 2026-10-02 (Baird: register it for the
lines that diverge from GEM). Read this file before trusting any run.

## What it is

Seala's "Карта газовой отрасли" at `seala.ru/lng/rossiyaeksport` iframes a public Yandex
DataLens dashboard. `scrape_seala_datalens.py` re-pulls the layer from the anonymous render
payload every visitor's browser gets (185 Russia gas LineStrings; tooltips carry name, owner,
status only: no capacity, diameter, dates). The scrape lives in `work/seala-20260917/`
(gitignored) with its own README. Aiganym supplied the lead.

## Why only 31 lines

147 of the 185 lines (79%) are GEM's own GGIT geometry, vertex for vertex, and the English
names follow GGIT naming. Reconciling those would echo GEM back at GEM. Each feature was
tagged against the routes repo (`gem_overlap_class`); `prepare.py` keeps only class D
("diverges": p90 more than 5 km from the nearest GEM route) into
`data/seala-ru-gas-divergent.geojson`. Dataset `gas_ru_divergent`.

## Rules for using it

- **Never a `[ref]`, never a second source, never corroboration.** Under standing rules 1 and
  4 a layer that is mostly GEM's own data is circular, and the scraped tooltips cite nothing.
  A match is a lead for a human, same as OSM.
- **Most divergent traces are cruder than GEM's, not better.** Power of Siberia is 21 vertices
  at a 62 km median offset; Blue Stream 8; Makat-N. Caucasus 3. A divergence is not a better
  route. Only four traces are dense and differ from GEM's current route: Nizhnevartovsk-
  Parabel-Kuzbass (P2350, 165 vertices), Bovanenkovo-Ukhta 3/6 (P5403, 139), Gorky-Cherepovets
  (P2372, 70), Nadym-Punga I-V (P2348, 49). Whether those are independent or an older GEM
  revision is **unchecked**: look at the routes repo history for those PIDs before treating
  any as a second opinion. That check is what would move this source off tier 4.
- **Rights are not established.** The owner has export switched off (`dataExportForbidden`,
  `DISABLED_EXPORT_CONNECTION`, `PROHIBITED_EXPORT_TENANT`) and the data is the commercial
  Терминал Сиала product. Keep `data/` and `work/` gitignored; do not commit the geometry or
  put it in a deliverable beyond what a reviewer needs to compare.
- **Unstable ids.** `seala_id` is the layer index in a live response; a re-pull may renumber.
- **Names:** 22 of the 31 have no English name (Cyrillic is used; the matcher romanizes it) and
  several are generic ("Pipeline 2", "Phase I"), so the name axis is weak on those.

## Smoke test (2026-10-02, Russia gas)

31 reference, 31 overlaps (22 green, 9 yellow), 0 additions, 4 status conflicts, 10 ambiguous,
2 route-replacement candidates. P4146 absorbs 5 of the 31 (the Nadym-Punga I-V family, one
trace repeated five times), which is expected, not a catch-all. Not run for a deliverable.
