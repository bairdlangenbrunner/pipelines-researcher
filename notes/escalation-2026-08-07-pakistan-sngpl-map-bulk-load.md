# Escalation (RESOLVED) — 51 of 70 Pakistan gas rows are one July-2023 map bulk-load

**Date:** 2026-08-07 · **resolved 2026-08-10**
**Scope:** Pakistan, gas (GGIT). Surfaced by the operating deep sweep (63 rows, one skeptical subagent each).
**Severity:** structural. Not a data-corruption finding — a **sourcing-model** finding that
determines how the whole country should be worked, and it changes what the 16 `existence`
concerns in the deliverable actually mean.

> **STATUS — read this first.** The primary-source acquisition this memo recommended was
> carried out on 2026-08-10 and it worked. SNGPL's own audited asset register
> (Annual Report 2018, *"TRANSMISSION SYSTEM As at June 30, 2018"*) accounts for **49 of the
> 51-row cohort at two-decimal precision**, closing **all five** residual existence questions
> and **all three** redundancy clusters. Two items remain: **P4074** (the only numeric
> disagreement) and **P5486** (the only unaccounted row). Detail in
> "RESOLVED 2026-08-10" below. What the register does *not* fix: the 8 SSGC rows, and every
> commissioning-year question — it carries no dates.

## The finding

73% of GEM's Pakistan gas rows (51 of 70) are a single bulk load. Every one of them:

- was last updated in **July 2023** (all 51, within a 5-day window 07-07 → 07-11),
- is owned **SNGPL 100%**, and
- carries **exactly the same two refs, and only those two**:
  - `https://www.sngpl.com.pk/images/transmission/TransmissionMap042022L.jpg` — a **JPG map**
  - `https://www.pepl.com.pk/assets/images/downloads/Energy-MapA4-2020.pdf` — a **PDF map**

A further 8 rows are the SSGC equivalent (`ssgc.com.pk` + the same PEPL map). Only 4 rows in
the whole country are sourced to news/industry reporting.

Both source artifacts are **cartographic, not textual**. They show the pipeline network; they
do not publish a named asset register with lengths, diameters and capacities per segment. So
the row-level values (LengthKnown, Diameter, Capacity, endpoints) were **digitized or inferred
from a map**, and there is no text anywhere — in the ref or on the open web — that a
researcher can quote back to confirm any individual segment.

## What that means for the 16 `existence` concerns

The sweep flagged 16 rows `concern_type=existence`. **Read them as "unverifiable by text
search", not "probably fake."** They are a sample of the 51-row cohort, not a distinct
problem set — the subagents that happened to draw a small, obscure Punjab/KP segment could
find no independent naming source, while the ones that drew Sui–Multan or Qadirpur could,
because those appear in reporting. The flag is tracking **segment obscurity**, not existence.

Concretely, the same cohort produced all three outcome classes:
- P4090 Sui–Multan — existence *confirmed* off SNGPL's own province-wise transmission breakdown.
- P4106, P4133, P4141, P4157/P4158, P4164, P4177/P4178 … — no source names the segment at all.
- P4105 / P4181 / P5486 — flagged `duplicate`, which is exactly the failure mode of digitizing a
  map: the same physical line read twice under two labels.

**Do not delete rows off these flags.** The correct next action for the cohort is a single
primary-source acquisition, not 16 row-by-row research tasks.

### The GulfPub cross-check narrows it to five rows

The §2 GulfPub reconciliation, run the same day, settles most of this and the sweep subagents
could not have known it — they researched rows one at a time and never saw the recon output.
GulfPub (Petroleum Economist's World Map) is an **independent cartographic source with no
relationship to SNGPL's own map**, and it matched 82 of its 94 Pakistan gas features to GEM
rows, covering **11 of the 16 existence-flagged rows**:

> P4124, P4129, P4133, P4135, P4139, P4157, P4158, P4164, P4170, P4178, P4181

A second, unrelated cartographer drawing the same line is real corroboration **of existence and
location** — though per the standing partial-coverage rule it says nothing about length,
diameter or capacity, so the `spec` concerns on these rows stand.

That left **five rows with neither a text source nor an independent trace** — P4089, P4106,
P4137, P4141, P4177. **All five are now closed.** See the next section.

### RESOLVED 2026-08-10 — the asset register exists, and it accounts for every SNGPL row

The recommended acquisition below was carried out, and it succeeded. **SNGPL publishes the
register in its own audited annual report**, and it is live:

> `https://www.sngpl.com.pk/download/AnnualReport-2018/SNGPLAR-2018.pdf`
> — *"TRANSMISSION SYSTEM As at June 30, 2018"*, printed pp. 32–37.

It is a **270-row, line-wise, text-searchable inventory**: section name, diameter in inches,
and mainline / loopline kilometres for every SNGPL transmission asset. It is the operator's own
audited statement of what it owns — categorically stronger than the JPG map, and a different
kind of document (textual, itemised, auditor-attested).

**Control on the extraction:** the parse of all 270 sections reconciles to the register's own
printed grand total — mainline **4,685.92 km**, loopline **4,190.05 km**. The numbers below are
not eyeballed off a PDF.

**Crosswalk result — 49 of the 51-row SNGPL cohort are accounted for:**

- **45 rows match a single register section on name AND length AND diameter**, at the
  register's own two-decimal precision (e.g. P4100 = Sr. 46 `N2 - SAHIWAL (RLNG LINE)`, 24 in,
  77.296 km).
- **4 rows are exact arithmetic composites** — GEM aggregates where the register itemises.
  Each sums to the sheet's `LengthKnown` to the centimetre and its multi-value `Diameter`
  matches the register's per-section diameters: P4101 (Sr. 14+15+16+17 = 130.77), P4107
  (Sr. 82+83+84 = 129.95), P4136 (Sr. 113+115 = 112.51), P4162 (Sr. 160+162 = 151.92).
  That is a granularity difference, not an error, and must not be "fixed".
- **All five residual existence questions are CONFIRMED EXISTING** — each is a named line in
  the operator's own register, matching on both length and diameter:
  P4089 → Sr. 21 `QADIRPUR LINE (LNG PHASE-II)` 42 in 53.14 km ·
  P4106 → Sr. 81 `SIDHNAI - FAISALABAD` 18 in 163.58 km ·
  P4137 → Sr. 123 `SHEIKHUPURA - GUJRANWALA (1)` 10 in 59.44 km ·
  P4141 → Sr. 144 `D/S HEAD BALLOKI TO MP-59.9` 18 in 52.34 km ·
  P4177 → Sr. 247 `KHARAPPA - MANJOWAL` 12 in 84.42 km.
- **All three redundancy clusters resolve as NOT duplicates.** In every case the register
  lists both pipes separately at *different diameters* — the ordinary SNGPL mainline/loopline
  pattern, which is exactly what produces two rows with near-identical totals:
  P4105 (36 in, Sr. 74) vs P4099+P4100 (24 in, Sr. 45+46 = 145.456) ·
  P4079 (24 in, Sr. 11) vs P4101 (42 in loop chain, Sr. 14–17) ·
  P4181 (Sr. 267) and P4179 (Sr. 254) are separate register entries.

**What the crosswalk did NOT resolve — the two remaining open items:**

1. **P4074 Kandhkot** — the *only* numeric disagreement across 49 matched rows. Register
   Sr. 18 `KAND KOT LINE` is 16 in (agrees) / **52.23 km** against the sheet's **55.23 km**.
   A one-digit slip in the same position, direction unknown. That it is the sole exception
   across 49 rows is itself evidence it is a typo rather than a real divergence.
2. **P5486 Mardan–Swat** — the one SNGPL row the register does not account for at all.
   104.89 km at 12 in matches no section and no combination of the 12-inch Mardan-area
   sections (Sr. 256 `NOWSHERA - MARDAN` 19.76; Sr. 257 `MARDAN - PALAI` 56.00). Now that the
   register accounts for every other row to two decimals, an unaccounted row is a far sharper
   signal than it was before.

**How this is staged:** `batches/pakistan-gas/staging/register-crosswalk/` — **98 ref-only
units across 49 rows** (`Length [ref]` and `Diameter [ref]`, both currently empty on all of
them; the sheet VALUES are unchanged), plus 5 validity records covering the two open items and
the three closed redundancy clusters. The register PDF and the parsed 270-row table are
committed alongside (`sngpl2018_transmission_register.json`,
`register_crosswalk.json`). **Tiering is honest about independence:** `high` where GulfPub
independently traces the same line (two origins), `medium` where the register stands alone —
SNGPL is the same *publisher* as the map ref, so the register is a far better document but not
a second independent origin.

`url_verifier.py` returns HTTP 200 but "value not found" on this PDF — the documented
large-PDF false negative (3.9 MB, 186 pp.). Values were confirmed locally with
`pdftotext -layout`.

**Still open at the cohort level:** the 8 **SSGC** rows have no equivalent register yet, and
the register is *as at 30 June 2018*, so it cannot date anything commissioned since. It also
carries no commissioning years at all — so the 60 `operating`-with-no-`StartYear1` rows are
**not** helped by it. SNGPL dropped this table from later annual reports (2019–2024 return 404
at the same URL pattern; the 2023 report has no equivalent), so 2018 is the edition to use.

## Compounding factor — the gem.wiki blackout

This sweep ran with gem.wiki returning 403 on every access path
(`notes/escalation-2026-08-07-gem-wiki-cloudflare-403.md`), so `wiki_citations.json` was empty
and **no subagent could start from the sources the row itself already cites**. For a cohort
whose only support is two map files, that removes the one lead the contract puts first. Some
share of the 16 existence flags would likely have resolved to `confirmed (caveat)` with the
wiki pages readable. Weight them accordingly.

## Ref health (both sources — keep them)

- **SNGPL map: live**, HTTP 200. Wayback `20250527234936`.
- **PEPL PDF: live**, HTTP 200 via curl. `url_verifier.py` reports FAIL/SSLError — that is a
  **Python-side certificate-chain problem, not a dead link**; curl with the system trust store
  fetches it fine. Wayback `20260731113845` (200).

Per the standing rule, neither ref may be dropped over an access failure. If the PEPL SSL
failure keeps tripping the verifier, add the Wayback URL **alongside** — never in place of it.

## Recommended next step — DONE for SNGPL, still open for SSGC

The original recommendation was:

1. **SNGPL annual report / OGRA licence register** — a text-searchable asset register to
   reconcile all 51 rows against in one pass, instead of researching them one at a time.
2. Only after that, work the residue as individual `existence` questions.

**Step 1 was done on 2026-08-10 and it worked** (see "RESOLVED 2026-08-10"). One document
retired 49 rows' worth of existence questions and all three redundancy clusters; the residue
for step 2 is now exactly two rows, P4074 and P5486.

**The method is the transferable finding, not just the Pakistan answer.** 63 subagents
researching rows one at a time could not resolve this cohort, because no source names the
individual segments; one operator asset register resolved it in a single pass. Where a country's
rows trace to a bulk load off an operator artifact, look for **that operator's audited annual
report** before dispatching per-row research.

**Remaining acquisition targets:**
- **SSGC's equivalent register** for the 8 SSGC rows (Sindh/Balochistan) — `ssgc.com.pk`
  annual reports, same shape of table.
- **Anything dated** for the 60 `operating`-with-no-`StartYear1` rows. The register carries no
  commissioning years, so it cannot help here. SNGPL annual reports' FY narrative ("commissioned
  during the year") and OGRA licence dates are the leads.
- **A post-2018 SNGPL register** for anything commissioned since 30 June 2018. Note SNGPL
  dropped this table from later reports — 2019–2024 all 404 at the same URL pattern — so a newer
  edition may not exist in this form.

## Not done here

- No row was deleted, downgraded or re-sourced off these flags — all 96 validity findings are
  staged for review, per the standing rule that QC detects and Update fixes.
- The 3 `duplicate` flags (P4105→P4099, P4181/P5486) are genuine adjudication candidates and
  are worth resolving regardless of how the cohort question lands.
