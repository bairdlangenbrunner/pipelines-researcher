# Finding: Save-Page-Now instruction endpoints cited as references

**Measured 2026-09-02, Jiangxi gas v2 deep sweep.** Not a blocker; input to the delivery note.

## What it is

18 of the 187 URLs the wiki harvest pulled are of the form

    https://web.archive.org/save/<origin-url>

That is Save Page Now's **instruction endpoint** — the thing you GET to *ask IA to make a
capture*. It is not a snapshot, it has no timestamp, and it does not serve archived bytes.
The citable form is `https://web.archive.org/web/<timestamp>/<origin-url>`.

`scripts/url_verifier.py` already rejects these with the correct reason string, so nothing
malformed can reach a workbook. The cost is silent: a rejected URL never enters the live
harvest pool, so **gate G is structurally blind to them** even though the underlying
document may be perfectly good.

## The documents are mostly fine — it is the citation FORM that is wrong

Origins are recoverable by splitting on `/save/`. Screened 2026-09-02:

| | count |
|---|---|
| SPN citations in the harvest pool | 18 |
| distinct origins | 18 |
| **origins live on re-verify** | **10** |
| dead (404 / 403 / 429 / connect-timeout) | 8 |

Same family as the Egypt `egyptoil-gas.com` navigation-surface defect
(`notes/escalation-2026-08-27-egypt-eog-navigation-surface-citations.md`): the document
supports the value, the *form* of the citation does not resolve to it.

Recovered pool: `spn_recovered_origins.json`. Gate **H** in `predelivery_checks.py` reports
any live recovered origin left unopened on a row that still reports `UNRESOLVED`.

## Tracker exposure is two cells, both out of this batch's scope

Scanning all three tabs of the 2026-09-02 snapshots (22 gas + 21 oil + 2 OO `[ref]` columns):

- **2** SPN-form URLs tracker-wide, both `Status [ref]`, both China gas, **neither in the 44**:
  - **P4838** → `haishu.gov.cn/art/2021/7/16/art_1229550817_58946344.htm` — origin is a
    confirmed **404**, so the fix is a Wayback snapshot, not the live URL.
  - **P5504** → `ggzy.neijiang.gov.cn/jyxx/006001/006001006/20240511/db0f58cb` — connect-timeout,
    and the URL **appears truncated in the cell** (ends mid-hash), so it may never have resolved.

Both are one-cell mechanical fixes, but they need a Wayback timestamp first and IA's
availability API was returning **429** at the time of writing — a rate limit, not evidence
about the captures. Left for a separate authorized pass; **do not** delete either ref on the
access failure (standing rule: only a confirmed 404/410 drops a ref, and P4838's replacement
must be the snapshot *added*, not the dead origin swapped in).

## Rule this generalises to

A URL the verifier rejects is not automatically a dead end — **check whether the rejection is
about the FORM or about the DOCUMENT.** Wrapper/instruction/navigation URLs carry a recoverable
origin inside them; screen those before writing the row off as unsourced.
