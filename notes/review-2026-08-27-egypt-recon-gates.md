# Egypt gas + oil — reading the four recon gates (2026-08-27)

Four §2 runs shipped with the 2026-08-27 Egypt pass: GulfPub and OSM against both
trackers. One of the four crosses the >10% material-conflict gate on its face. It
dissolves on inspection, and this note records *why*, so nobody re-opens it as a
finding or — worse — "fixes" it by retuning weights.

## The headline number is a matcher artifact, not a disagreement

`egypt-oil / gulfpub` reports **23 status conflicts on 40 matched rows = 57.5%**,
far over the escalation gate. But **21 of the 23 are one GEM row**, P7326
(`El Minya-El-Tibeen-Asyut Oil Products Pipeline`, segment `El Minya Connection`),
which the matcher hands 21 different Gulf of Suez reference lines — Belayim Marine,
Ras Bakr, Shoab Ali, East Zeit, Geisum, Tawila, Ramadan, July, October, Burg El
Arab. Those are offshore and Western Desert lines; P7326 is a 20 km products
connector in Middle Egypt. None of them is a real counterpart.

The `MATCH_CONCENTRATION` diagnostic fired and named the cause exactly:

> one GEM row (P7326) is the best match for 28 of 68 reference records (41.2%), and
> 28 of those wins had **no location evidence at all** (routeless GEM row, no
> endpoint signal — diameter and a length ratio carried the match).

P7326 is the single routeless row on Egypt's oil tab. With the geometry and endpoint
axes both dead, `diameter` (0.15) and `length` (0.10) alone decide, and a 20 km
line of common diameter is a plausible-looking partner for almost anything.

## The gates, read the way the diagnostic prescribes

Excluding each run's absorbing row:

| run | overlaps | conflicts | conflict rate | additions |
|---|---|---|---|---|
| oil / GulfPub | 40 → **19** | 23 → **2** | 57.5% → **10.5%** | 28 |
| gas / GulfPub | 80 → **62** | 6 → **5** | 7.5% → **8.1%** | 15 |
| oil / OSM | 5 → 5 | 0 | 0.0% | 27 |
| gas / OSM | 1 → 1 | 0 | 0.0% | 20 |

Absorbers: P7326 (oil, both sources), P8076 (gas/GulfPub, 24 of 95 = 25.3%),
P6693 (gas/OSM, 8 of 21 = 38.1%).

**No addition gate is crossed** — all four runs sit under the >30 threshold, oil /
GulfPub closest at 28. The one conflict-gate crossing reduces to **two rows**:

- **P7315** Agroud–Ain Sokhna (segment `Wadi Hagool-Ain Sokhna`) — GEM
  `construction` vs GulfPub `operating` on `Ain Sukhna - Suez`. Geographically
  plausible; a genuine status question for Update.
- **P3689** Badr El Din–El Hamra — GEM `operating` vs GulfPub `proposed` on
  `Badr El Din - Marsa El Hamra`. The only conflict running the other direction.

The five surviving gas/GulfPub conflicts are likewise a countable list, not a rate.

## What actually fixes this

The diagnostic's own instruction, and it is the right one: **route the absorber or
fill its endpoints, then re-run. Do not lower a threshold and do not retune the
source-level weights** — those are shared, so moving them moves every committed run
for GulfPub in every other country.

Status after this pass:

- **P8076** (gas absorber) now has staged candidate geometry from the same batch
  (`route-creation-20260827`, 43.2 km, routes-repo QC PASS). Once that is applied,
  a gas/GulfPub re-run should shed the artifact.
- **P7326** (oil absorber, both runs) is staged as a corridor-only `ROUTE_PARTIAL` —
  its depot end is pinned but the trunk tie-in is unsourced, so there is nothing to
  apply and the oil runs cannot improve yet. It stays the known distortion on the
  oil side; read the oil/GulfPub conflict count as **2**, not 23, until it is routed.
- **P6693** (gas/OSM) was not part of the routeless scope — its absorption sits on a
  21-record reference pool where 0% of records are named, so the name axis is dead
  too. Low stakes: that run produced 1 overlap and 0 conflicts.
