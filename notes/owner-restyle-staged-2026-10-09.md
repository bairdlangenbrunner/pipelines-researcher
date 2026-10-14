# Owner and operator spellings in pending staged work, restyled 2026-10-09

Mode: APPLIED. Sheet snapshot: `GEM_operators_owners_snapshot_20261009.csv`.

Every pending staging dir was read. A proposed Owner or Operator value that differs from the sheet's current cell was run through the styler; the ones the policy allows (an exact gazetteer hit, a confirmed alias, a ruling, or a rules result with only mechanical flags) were rewritten, with the source's spelling kept in the researcher notes. The rest were left as they were and are listed below for a person.

- cells rewritten: 12 (7 in staged_resolutions.json files, the rest in shard rows)
- distinct re-spellings: 3
- cells left as they were (a judgment, not a spelling): 30 — acronym_not_initials 16, fuzzy_candidates 8, alias_candidate 6
- proposed values equal to the sheet (carried, not touched): 3812

## Rewritten, by staging dir

- `batches/united-states-gas/staging/deepsweep-appalachian-operating`: 6
- `batches/united-states-gas/staging/deepsweep-west-operating`: 4
- `batches/united-states-gas/staging/deepsweep-s2-gulf-indev`: 1
- `batches/united-states-gas/staging/deepsweep-s2-west`: 1

## Re-spellings (cells)

- 'Tallgrass Energy' -> 'Tallgrass Energy LP' (10)
- 'Cheniere Energy' -> 'Cheniere Energy Inc' (1)
- 'Williams Companies' -> 'Williams Companies Inc' (1)

## Left as they were (a person decides)

- 'H-Energy Private Limited' -> 'H-Energy Pvt Ltd'? fuzzy_candidates (4)
- 'Equitrans, L.P.' -> 'Equitrans LP'? alias_candidate (4)
- 'GASCO (Egyptian Natural Gas Company)' -> 'Egyptian Natural Gas Co'? acronym_not_initials (2)
- 'Egyptian Natural Gas Company (Gasco)' -> 'Egyptian Natural Gas Co'? acronym_not_initials (2)
- 'Egyptian Natural Gas Company (GASCO)' -> 'Egyptian Natural Gas Co'? acronym_not_initials (2)
- 'Pipeline Infrastructure Limited' -> 'Pipeline Infrastructure Ltd'? fuzzy_candidates (2)
- 'Indian Oil Corp (IOCL)' -> 'Indian Oil Corp'? acronym_not_initials (2)
- 'Brooklyn Union Gas Company d/b/a National Grid NY (KEDNY)' -> 'Brooklyn Union Gas Company d/b/a National Grid NY'? acronym_not_initials (2)
- 'National Fuel Gas Supply Corporation' -> 'National Fuel Gas Supply Corp'? alias_candidate (2)
- 'NextEra Energy, Inc. (affiliate)' -> 'NextEra Energy Inc'? acronym_not_initials (2)
- 'Con Edison Gas Pipeline and Storage, LLC (affiliate)' -> 'Con Edison Gas Pipeline and Storage LLC'? acronym_not_initials (2)
- 'AltaGas Ltd. / RGC Resources, Inc. (affiliates)' -> 'AltaGas Ltd. / RGC Resources Inc'? acronym_not_initials (2)
- 'ENSTAR Natural Gas Company' -> 'ENSTAR Natural Gas Co'? fuzzy_candidates (2)

Next: the review app and the workbooks read these files on their next build; a decided line keeps its decision (the spelling moved, the entity did not).
