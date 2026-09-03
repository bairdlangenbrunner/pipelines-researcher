# Ukraine gas — a 3.29% citation base, and the bottom-tier cohort it belongs to

**Raised:** 2026-08-15, during the Ukraine gas §9 full pass.
**Scope:** GGIT gas. Ukraine = the 47 rows whose `CountriesOrAreas` /
`StartCountryOrArea` / `EndCountryOrArea` include Ukraine, read off
`data/GGIT_gas_snapshot_20260812.csv`. Tracker-wide figures are the whole gas tab.
**Status:** read-and-flag. This is a *scope-level* finding — no single row action carries
it, which is why it is a memo.

---

## The number

**34 of 1,034 `[ref]` cells are filled — 3.29%** — against **18.49% tracker-wide**
(17,729 / 95,876). 22 ref columns × 47 rows.

Where the 34 sit:

| Ref column | Rows filled (of 47) |
|---|---|
| `Route [ref]` | 8 |
| `Status [ref]` | 7 |
| `Diameter [ref]` | 5 |
| `Fuel [ref]` | 4 |
| `PipelineType [ref]` | 4 |
| `Construction [ref]` | 2 |
| `Start [ref]` | 2 |
| `Capacity [ref]` | **1** |
| `Length [ref]` | **1** |
| every other ref column | 0 |

**That last pair is the finding.** `Length [ref]` and `Capacity [ref]` are filled on
exactly one row each — and length and capacity are precisely what this pass found wrong,
repeatedly and independently: two rows carrying an unsourced 292.00 km against sourced
357.7 / 366.7 km strings (cluster G), 29.00 bcm/y restated on both of them as a system
total, 24.00 bcm/y on P0784 that is verbatim an aggregate over three threads (cluster B),
a 333.00 km that cannot span its own corridor (cluster C), and neither of the two КЗУ
lengths supported by anything (cluster A). The cells the country cannot cite are the cells
the country gets wrong. That is not a coincidence and it is the argument for treating
Ukraine's ref gap as a data-integrity problem rather than a tidiness one.

Separately, of the 22 refs sitting on operating rows, **17 resolve to dead links** — so
the *effective* live-citation rate is lower than 3.29% again.

## It is a cohort, not a Ukraine defect

**Correction to this pass's own earlier wording:** an intermediate draft called Ukraine
"the worst-cited scope in the tracker". It is not. Ranked across the **52 country scopes
with 20 or more gas rows**, Ukraine is **2nd from the bottom**:

| Rank | Scope | Rows | Ref-cell fill |
|---|---|---|---|
| 1 | Netherlands | 39 | 3.03% |
| **2** | **Ukraine** | **47** | **3.29%** |
| 3 | Bangladesh | 62 | 3.30% |
| 4 | Indonesia | 50 | 4.27% |
| 5 | Thailand | 34 | 4.28% |

For calibration against the scopes worked recently: Pakistan 5.58%, India 9.03%,
Kazakhstan 19.84%, Egypt 32.42%.

So the useful escalation is **not** "Ukraine is uniquely bad" but "there is a bottom-tier
cohort of five scopes at 3–4%, covering ~230 gas rows, none of which has been swept" —
and Ukraine is the first of them to get a §9 pass. The other four are candidates for the
same treatment and belong in the triage queue.

## Why a blank cell here is not evidence the fact is unpublished

This is the calibration rule the Leg-3 protocol carries, and it is worth keeping:

- In **Kazakhstan** an `UNRESOLVED` on a per-string spec is frequently the *correct*
  outcome — the country has no line-wise public register, so the number may not exist.
- In **Ukraine** a blank is far more often evidence that **nobody has looked**. The pipe
  is Soviet-era and some per-string specs genuinely will not resolve, but the operator
  question — 22 of the 30 Leg-3 worklist rows — is squarely documented, and the sweep
  legs moved a large block of cells off `UNRESOLVED` once they were actually worked.

Do not import Kazakhstan's tolerance for `UNRESOLVED` into Ukraine.

## Two access facts that shaped this pass and will shape the next

Both are **blocks, not deletions**, and under the standing rules neither may cause a ref
to be dropped:

1. **`utg.ua` and `tsoua.com` return HTTP 403** to `url_verifier` (operator WAF, checked
   2026-08-15). Between them they hold the Ukrtransgaz historical chronology, which is the
   single source that would settle clusters A and C. Read them through Wayback.
2. **`moldovatransgaz.md` fails TLS** (SSLError + ConnectionError, both with and without
   certificate verification). The **`mtg.md` mirror** serves the same content and
   verifies 200; it is what this pass staged.

## What this means for the deliverable

Ref work dominates the Ukraine packet by design: the assembled staging reports
**231 `REFS_ADDED`, 126 `UNRESOLVED` and 19 `DEAD_LINK`** ref units against only
**11 fills** and 110 concerns. A researcher working the actions workbook should expect
most of their time in `[ref]` cells rather than value cells, and should read the 126
`UNRESOLVED` as *unfinished*, not as *unavailable*.
