# Note — 68 of the 99 wiki-alignment records are ONE thing, and it is not a Pakistan defect

**Date:** 2026-08-10
**Scope:** Pakistan gas (GGIT), but the underlying pattern is tracker-wide.
**Severity:** low — a **read-this-first** note for the packet's wiki surface, not a finding.
Raised because the count is alarming and the explanation is not visible from the tab.

## What you will see

The wiki-alignment leg was re-run on 2026-08-10 after the gem.wiki Cloudflare block was
solved (`notes/escalation-2026-08-07-gem-wiki-cloudflare-403.md`), replacing 70
all-`UNPARSED` records with **99 real ones**:

| class | n |
|---|---|
| `SHEET_SUSPECT` | 69 |
| `WIKI_UPDATE` | 24 |
| `WIKI_STALE_VS_STAGED` | 6 |
| `UNPARSED` | 0 |

**68 of the 69 `SHEET_SUSPECT` records are the same field: `Operator`.** The wiki page
displays an operator, the backend's operators/owners tab has the cell blank, so the leg
flags the *sheet* as the suspect side — which is what it is designed to do.

## Why it is not a defect

**A blank `Operator` is the GGIT norm, not a Pakistan gap.** On the live operators/owners
tab (2026-08-10 pull): `Operator` is populated on **1,464 of 6,462 rows — 22.7%**. Pakistan
is at 0 of 70, which is unusual only in being complete; three quarters of the tracker looks
the same. `Owner1`, by contrast, is filled on **70 of 70** Pakistan rows.

So do **not** work these as 68 flags. There is one decision here.

## The one decision

**Should Pakistan's `Operator` column be populated at all?** If yes, it is a single bulk
edit, not 68 research tasks — the country is a two-company system and the operator is the
owner:

- 52 rows `Sui Northern Gas Pipelines Ltd (SNGPL)`
- 12 rows `Sui Southern Gas Co (SSGC)`
- 6 transnational/proposed rows with their own owners (Iran Ministry of Petroleum ×2,
  Turkmengaz, Government of Pakistan, Interstate Gas Systems, Gazprom PJSC) — these are
  the ones where operator ≠ owner is actually plausible, so treat them individually.

Two constraints if it goes ahead:

1. **The wiki value is a lead, never the ref** (standing rule 1). Each `Operator` fill
   needs an independent source. For the SNGPL cohort the SNGPL asset register already
   staged in `staging/register-crosswalk/` is that source — it is SNGPL's own audited
   statement of the transmission system it owns and runs.
2. **No orphan refs**: `Operator` and `Operator [ref]` land together, on the
   ProjectID-keyed operators/owners tab (GID 1489950650), where the `[ref]` precedes its
   values.

## The remaining 31 records are the real content

Worth reading properly, since these are the first wiki findings this country has ever
produced: 24 `WIKI_UPDATE` (6 Owner, 6 Parent, 3 StartYear1, 3 LengthKnownKm, 2 Status,
2 Diameter, 1 StartCountryOrArea, 1 EndCountryOrArea) and 6 `WIKI_STALE_VS_STAGED`
(4 Status, 2 Diameter) — the latter meaning the wiki matches the *old* value and this
packet already stages a correction, so the wiki edit follows the sheet edit. The single
non-Operator `SHEET_SUSPECT` is a `StartYear1` (P3173, wiki says 2018 against a blank
sheet) and is a genuine fill candidate — it needs its own non-GEM source.
