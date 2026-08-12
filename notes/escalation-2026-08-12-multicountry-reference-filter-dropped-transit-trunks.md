# Engine defect — the reference-side country filter dropped every multi-country record

**Found** 2026-08-12, mid-flight in the Ukraine gas §9 pass. **Fixed** the same day.
**Class:** our own code, not a data finding — so under the standing rule this is a fix
plus a re-run, never a decision memo or a "⚠️ ignore this column" caveat.

## What was wrong

Two independent copies of the same filter scoped **reference** records by exact string
equality against one normalized country:

```python
# scripts/ingest.py (old)
if want_country and rec.country != want_country:
    continue

# scripts/reconcile.py (old)
ref = [r for r in records
       if r["country"] == want_country and (fam is None or r["commodity"] in fam)]
```

A scraped source routinely writes a cross-border trunk as **one multi-country string**.
GulfPub's Ukraine block contains `'Russian Federation / Ukraine'` (18),
`'Ukraine / Moldova'` (13), `'Ukraine / Russian Federation'` (7),
`'Belarus / Ukraine'` (2), `'Ukraine / Hungary'` (2),
`'Russian Federation / Kazakhstan / Ukraine'` (2),
`'Georgia / Ukraine / Romania'` (1), `'Russian Federation / Belarus / Ukraine'` (1),
`'Ukraine / Belarus'` (1). None of those equals `'ukraine'`, so **all 47 were silently
dropped** and a country-scoped run saw only the segments lying wholly inside one border.

The GEM side never had this bug — `match.py`, `build_ref_worklist.py`,
`build_qc_staging.py`, `build_qc_workbook.py` and `route_integrity.py` all test
`want in N.split_countries(...)`. `split_countries` has existed the whole time. **The
reference side was the one asymmetry**, and because both halves of a recon are filtered
independently, fixing `ingest.py` alone changed nothing: the ingest reported 158 records
and `reconcile.py` still printed `reference=111`. That is the tell that caught the
second copy.

## Why it mattered most where it did

The dropped records are not a random 5% — they are **specifically the transit trunks**,
which in a transit country are the majority of what GEM tracks. Ukraine's own tracker is
31 multi-country rows out of 47. So the filter removed the reference records with the
best chance of matching, and the residue then read as GEM-only rows and unmatched
additions.

**Same shape in Kazakhstan** (`'Russian Federation / Kazakhstan / Ukraine'`,
`'Kazakhstan / China'`, …): GulfPub gas **32 → 63 records, +97%**. The Kazakhstan gas §9
pass was delivered and committed (`18cf06f`) off the narrowed set the day before this was
found, so its GulfPub recon is superseded — see the ledger below.

## The fix

One implementation, `normalize.country_matches()`, called from both filters:

```python
def country_matches(rec_country: str | None, want: str) -> bool:
    if not rec_country:
        return False
    if rec_country == want:      # FIRST: four _COUNTRY_ALIASES keys contain a comma
        return True              # ('congo, the democratic republic of the', …) and
    return want in split_countries(rec_country)   # splitting them would shred them
```

Whole-string equality is deliberately tried **before** splitting, because splitting a
comma-bearing alias key on `[;,/]` destroys it. Verified on eight cases including the
`'Congo, the Democratic Republic of the'` and `'Korea, Republic of'` round-trips.

`adapter_base.py`'s `units.length_units_by_country` override carried **the same defect
class** (`N.normalize_country(_ck) == country`) and was fixed to membership as well.
That one is a **consistency fix, not a value change**: 0 of GulfPub's 361 multi-country
records name Canada, the only country with an override. Noted in the code — if it ever
does fire on a multi-country record, verify which block the row was tabulated in rather
than trusting the first matching key.

`sources/osm/` is **unaffected**: each OSM dataset is an ISO-scoped extract carrying a
per-dataset `country_const`, so its records are single-country by construction. ENTSOG
likewise.

## Blast radius — records a scoped run gains, by country

GulfPub gas: 280 of 5,345 records are multi-country (5.2%). Oil: 81 of 1,645 (4.9%).

| Country | gas was → now | oil was → now |
|---|---|---|
| **Ukraine** | 111 → 158 (+47, **+42%**) | 14 → 25 (+11, **+79%**) |
| **Kazakhstan** | 32 → 63 (+31, **+97%**) | 35 → 44 (+9, +26%) |
| Iran | 43 → 49 (+6) | 40 → 42 (+2) |
| Iraq | 26 → 29 (+3) | 21 → 27 (+6, +29%) |
| Malaysia | 50 → 55 (+5) | — |
| Egypt | 92 → 95 (+3) | — |
| Libya | 40 → 43 (+3) | — |
| Saudi Arabia | 20 → 21 (+1) | 36 → 40 (+4) |
| Pakistan | 94 → 96 (+2) | — |
| India | 158 → 159 (+1) | — |
| China | 108 → 120 (+12) | — |

Record count is the *input* delta. Whether it changes a country's **findings** is a
separate question — the extra records still have to clear the matcher — which is what the
re-run ledger records.

## What the fix alone changed — clean A/B, every scope

The naive "new run vs committed `match_diff.json`" comparison is **confounded**: some
committed runs used `--commodity both`, every GEM tab has grown, and several matcher fixes
have landed since. So each scope was measured with snapshot, code and commodity held
constant, differing **only** in the record set — B = full ingest, A = the same ingest
filtered by the old `==` predicate. The control reproduced the committed Kazakhstan run
exactly (27/5/31/4), which validates the method.

| Scope | refs | overlaps | gem_only | conflicts |
|---|---|---|---|---|
| **Kazakhstan gas** | 32 → 63 | 27 → **52** | 31 → **16** | 4 → 7 |
| **Ukraine gas** | 111 → 158 | 41 → **73** | 26 → **17** | 11 → 15 |
| **China gas** | 108 → 120 | 107 → **118** | 536 → 532 | 16 → 18 |
| **Kazakhstan oil** | 35 → 44 | 30 → **37** | 21 → **16** | 4 → 6 |
| **Iraq oil** | 21 → 27 | 20 → **26** | 65 → **58** | 8 → 10 |
| **Iran gas** | 43 → 49 | 29 → **34** | 23 → **19** | 3 → 4 |
| Egypt gas | 92 → 95 | 69 → 72 | 73 → 69 | 5 → 5 |
| Libya gas | 40 → 43 | 37 → 40 | 10 → 8 | 0 → 1 |
| Iraq gas | 26 → 29 | 20 → 23 | 38 → 37 | 5 → 5 |
| Saudi oil | 36 → 40 | 34 → 37 | 21 → 19 | 2 → 4 |
| Malaysia gas | 50 → 55 | 4 → 4 | 3 → 3 | 3 → 3 |
| Pakistan gas | 94 → 96 | 82 → 84 | 27 → 26 | 0 → 2 |
| Iran oil | 40 → 42 | 34 → 36 | 84 → 83 | 0 → 1 |
| India gas | 158 → 159 | 74 → 75 | 40 → 40 | 23 → 24 |
| Saudi gas | 20 → 21 | 18 → 18 | 23 → 23 | 9 → 9 |

Two properties of the delta are worth stating, because they set how much of past work is
suspect:

1. **The fix only ever *adds* matched records; it never invalidates an existing overlap.**
   So a shipped workbook's overlaps were right as far as they went — the bucket that was
   actively **wrong** is `gem_only`, every entry of which asserts "no reference counterpart
   exists". Falsified `gem_only` claims, by scope: Kazakhstan gas 15, Ukraine 9, Iraq oil 7,
   Kazakhstan oil 5, Egypt 4, Iran gas 4, China 4, Libya 2, Saudi oil 2, Iraq gas 1,
   Pakistan 1, Iran oil 1; India and Saudi gas 0.
2. **New status conflicts appear** where the newly-admitted record disagrees with GEM —
   findings that were absent from the shipped workbooks entirely (Saudi oil +2, Pakistan +2,
   China +2, Iraq oil +2, India +1, Libya +1, Iran +1 each side).

Only **Saudi gas** comes through with no finding change at all (one extra addition).

## Re-run ledger — all committed GulfPub recons regenerated 2026-08-12

Under the standing rule (our own defect ⇒ fix **and** re-run every affected country, never a
caveat), every committed GulfPub recon was re-run on the current engine and its superseded
staging dir retired **by move** to `<batch>/archive/recon-gulfpub-<date>-superseded-by-multicountry-fix`.

Re-running also picks up **every other matcher fix landed since each run was stamped**, so
the visible movement is larger than the A/B above and is *not* all attributable to this
defect. Two scopes moved for that reason more than this one: **China** (87 → 118 overlaps,
`gem_only` 925 → 532 — its GEM pool is stable at 986→988 rows, so that is engine, not data)
and **Saudi oil** (38 → 55 overlaps, `gem_only` 87 → 42, off the oldest run, 06-03).

| Batch | commodity | re-run | new workbook |
|---|---|---|---|
| ukraine-gas | gas | in-pass, nothing superseded | ships with the §9 pass |
| kazakhstan-gas | gas | ✓ | `…20260812_1344_ET…` |
| egypt-gas | gas | ✓ | `…20260812_1359_ET…` |
| iran-gas | gas | ✓ | `…20260812_1359_ET…` |
| iraq-gas | both | ✓ | `…20260812_1359_ET…` |
| iraq-oil | oil | ✓ | `…20260812_1359_ET…` (renamed to the current `reconciliation-gulfpub` convention) |
| libya-gas | both | ✓ | `…20260812_1359_ET…` |
| pakistan-gas | gas | ✓ | `…20260812_1359_ET…` |
| saudi-arabia-gas | gas | ✓ | `…20260812_1359_ET…` |
| india-gas | gas | ✓ | `…20260812_1359_ET…` |
| saudi-arabia-oil | both | ✓ | none — this batch never had a GulfPub workbook; staging is now current |
| china-trunks-gas | gas | ✓ | none — same; and see the China caveat above |
| malaysia-gas | gas | **left alone** | another session is mid-pass on this batch (deep sweep + three recons + QC all stamped 2026-08-12) and its recon was already on fixed code — findings identical before/after |

Superseded **workbooks** were retired by move to `<batch>/archive/` alongside the staging
dirs. Each affected country note carries its own retraction.

## The generalisable lesson

**A country-scope filter is a join, and a source's country field is not a scalar.**
Any filter that compares a reference record's country with `==` is wrong the moment the
source describes anything that crosses a border — which for pipelines is the interesting
half of the dataset. Two things follow:

1. Route every country scope through `N.country_matches` (reference side) or
   `N.split_countries` (GEM side). Never write a bare `==` against a country string.
2. **A thin recon is a claim about the pipeline until the input count is checked.** The
   `MATCH_QUALITY` health line covers a dead *matcher*; it says nothing about records
   that never reached the matcher. When a transit country returns a suspiciously
   GEM-only-heavy diff, compare `ingested N` against a raw grep of the source for the
   country name before concluding anything about coverage.
