# Owner and operator spellings in pending staged work, restyled 2026-10-17

Mode: APPLIED. Sheet snapshot: `GEM_operators_owners_snapshot_20261017.csv`.

Every pending staging dir was read. A proposed Owner or Operator value that differs from the sheet's current cell was run through the styler; the ones the policy allows (an exact gazetteer hit, a confirmed alias, a ruling, or a rules result with only mechanical flags) were rewritten, with the source's spelling kept in the researcher notes. The rest were left as they were and are listed below for a person.

- cells rewritten: 10 (5 in staged_resolutions.json files, the rest in shard rows)
- distinct re-spellings: 4
- cells left as they were (a judgment, not a spelling): 0 — 
- proposed values equal to the sheet (carried, not touched): 351

## Rewritten, by staging dir

- `batches/united-states-gas/staging/deepsweep-s2-northeast-alaska`: 6
- `batches/united-states-gas/staging/deepsweep-s2-appalachian-indev`: 4

## Re-spellings (cells)

- 'Equitrans, L.P.' -> 'Equitrans LP' (4)
- 'Brooklyn Union Gas Company d/b/a National Grid NY (KEDNY)' -> 'Brooklyn Union Gas Co' (2)
- 'National Fuel Gas Supply Corporation' -> 'National Fuel Gas Supply Corp' (2)
- 'ENSTAR Natural Gas Company' -> 'ENSTAR Natural Gas Co' (2)

## Left as they were (a person decides)


Next: the review app and the workbooks read these files on their next build; a decided line keeps its decision (the spelling moved, the entity did not).
