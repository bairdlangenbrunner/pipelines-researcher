# Russia gas discovery — Step 0 seed list (2026-09-30)

Built by `build_seeds.py` (run from repo root) from the OSM §2 recon `recon-osm-20260930`, the GulfPub recon
`recon-gulfpub-20260914`, the 20260930 GGIT snapshot, and `store_leads.json` (hand-curated from the R1–R7
validity stores). `district_join.py` is the state audit's Natural Earth district join (largest length share).

## Method
- OSM: DISCOVERY_CANDIDATE additions only (3,078), **named** only (864 → 282 name groups), stubs merged by
  normalized name, total length ≥ 25 km → `seed`, else `monitor`. Length = summed geodesic (OSM carries no
  `length_km`); `largest_component_km` / `n_components` show how connected the merged pieces are.
- Match-to-existing first → `matched_existing` (not a seed): ≥ 60% of the group within 1.5 km of a drawn roster
  route, or name similarity ≥ 90 with ≥ 25% coverage, or ≥ 95 name match (multi-token names only).
  Weaker name hits stay seeds with `name_hint` for the consolidator.
- `kind_hint` (regex on the name): `spur (otvod/GRS)`, `field/gathering`, `distribution`, `trunk/other` — a hint,
  not a ruling; the ≥ 25 km rule does not exclude spurs.
- Slices: D1 Far Eastern · D2 Siberian · D3 Ural · D4 Northwestern · D5 Volga + Central · D6 Southern + North Caucasian.

## Counts by slice
| slice | seed | seed, length unknown | monitor | already tracked | seed km |
|---|---|---|---|---|---|
| D1 Far Eastern | 1 | 1 | 3 | 0 | 84 |
| D2 Siberian | 3 | 0 | 1 | 2 | 257 |
| D3 Ural | 33 | 1 | 65 | 11 | 3,025 |
| D4 Northwestern | 17 | 1 | 22 | 16 | 1,396 |
| D5 Volga + Central | 32 | 0 | 54 | 23 | 2,951 |
| D6 South + N. Caucasus | 2 | 0 | 3 | 1 | 392 |
| **all** | **88** | **3** | **148** | **53** | |

Seeds are features/merged groups, not clusters — the consolidator clusters them; per the soft gate, stop only if a
slice produces > ~15 clusters (D3 and D5 are the ones to watch; 15 of D3's 33 are field/gathering links).

## Things to know
- **The GulfPub "Siberian" candidates are not Siberian.** The two DISCOVERY_CANDIDATEs' "nearest P3982 / P6684" was
  length arithmetic; the traces are *Tuchevo–Tver–Mikulimo* (84 km, Central → D5) and *Valday–Borovichi* (64 km,
  Novgorod/Tver → D4). The FRAGMENT (*Pochinki–Arzamas*, 90 km, Volga) is 100% inside P0756 → `matched_existing`.
- **Far Eastern OSM coverage is thin:** one named OSM discovery group in D1, so D1 rests on the store leads + search.
- **Unnamed OSM candidates are not seeded (ruling): 2,214 features / 9,274 km, 74 of them ≥ 25 km.** Real pipe by
  the standing rule; they are the pool to revisit if the named seeds look too clean.
- `МГ "Омск-Новосибирск"` (D2, name ≈ P2362 at 91) and a few other seeds carry a high `name_hint` but little
  geometry coverage: probably existing rows GEM has drawn loosely — consolidator matches them first.
- `Краснодарський край - Крим` (D6, 135 km) is the Krasnodar–Crimea line; GGIT has no row (RU–UA cross-border per ruling 2).
- Store leads resolved as NOT discovery: Vytegra–Pudozh stage IV is P4210 (exists); the 2010 Saransk-routed
  Pochinki–Penza duplicate (P2371 note) is out of window. Store leads kept: Nizhnyaya Tura–Perm III (D3), Nevinnomyssk–Mozdok
  sibling string (D6), ВНХК branch (D1), Kysyl-Syr 84 km (D1, likely P3365), Gryazovets–Vyborg loops (D4, 2017 — likely out of
  window), plus two sub-25 km spurs (monitor).
