# Wayback `/save/` link repair — 2026-08-05

## The defect

348 cells in the backend held a `web.archive.org/save/<target>` URL. `/save/` is Save
Page Now's *instruction* endpoint, not a snapshot address: clicking one triggers a fresh
capture attempt rather than serving the archived page. As a reference it is broken in two
ways — it never resolves to stable evidence, and each click hits the live origin, so if
that origin has since died the reader gets nothing.

Distribution (fresh pull, `*_snapshot_20260805.csv`):

| Tab | Occurrences |
|---|---|
| Gas pipelines | 347 |
| Pipeline operators/owners | 1 (`Wiki`) |
| Oil/NGL pipelines | 0 |

343 sat in `[ref]` columns (`Status [ref]` 113, `Route [ref]` 47, `SegmentCost [ref]` 27,
`PipelineType [ref]` 21, `Diameter [ref]` 20, `FuelSource [ref]` 20, then a tail across
most other ref columns). 5 sat elsewhere: gas `Wiki` r2437, gas `ResearcherNotes` r3006,
gas `RouteNotes` r3080 and r3921, plus the operators/owners `Wiki` r3392.

214 unique targets underlie the 348 occurrences (54 targets repeat). They are
overwhelmingly Chinese-language sources — `toutiao.com` (33), `sohu.com` (9),
`ccpc360.com`, `doc88.com`, `mp.weixin.qq.com`, and many provincial `.gov.cn` pages —
consistent with one researcher's China workflow pasting the "save this page" URL instead
of the resulting snapshot URL.

Screened before any repair: **0 targets were GEM surfaces** (standing rule 1) and **0 were
blocklisted sources** (abarrelfull / wikidot / theodora). So every occurrence was safe to
repair rather than remove.

## Method

`extract_targets.py` → every occurrence + the unique target list. All 348 tokens had the
same clean shape (`https://web.archive.org/save/<https://target>`), one per cell.

`resolve_snapshots.py` → one verified snapshot per unique target.

Notably this uses **only the Wayback playback endpoint**, not the availability or CDX
APIs. Both APIs 429'd hard and stayed blocked for many minutes after a first (too
concurrent) attempt; the playback host did not. `https://web.archive.org/web/<ts>/<url>`
redirects to the capture nearest `<ts>`, so the **final URL after redirects _is_ the
working snapshot link** — one request per target instead of two, and no API quota. A
target with no captures at all returns HTTP 404, which distinguishes "nothing archived"
from "archived but broken" for free.

Per target the resolver walks a ladder — newest capture first
(`/web/29991231235959/`), then `2024`, `2021`, `2017` — and accepts the first candidate
that returns HTTP 200 whose body is not a Wayback failure page ("Got an HTTP 4xx response
at crawl time", "has not archived that URL", etc.). It reads only the first 32 KB, enough
to clear Wayback's injected banner and reach real page body. Requests are strictly
sequential with a 2 s floor and exponential backoff; the run is resumable through
`resolved.jsonl`.

Buckets: `RESOLVED` (verified snapshot), `NO_CAPTURE` (nothing archived — the origin is
also probed for liveness), `CAPTURES_BUT_UNVERIFIED` (captures exist but every ladder
candidate was a failure page), `LOOKUP_ERROR` (every rung errored; retried on re-run).

**Ladder bug, found and fixed mid-run:** the first version bailed to `LOOKUP_ERROR` as
soon as a candidate returned 5xx. But a 5xx is usually a property of *that capture* (a
poisoned WARC record), not an outage — `chenghai.gov.cn`'s newest capture
(`20250929162253`) 500s persistently while its 2024 capture is perfectly fine. The
resolver now keeps walking the ladder and only calls `LOOKUP_ERROR` when *every* rung
errored.

One target was corrected rather than resolved as-given:
`https://www.doc88.com/p-59759701226314.htmll` (double `l`) has no captures; the
corrected `.html` — same doc88 document ID — verifies at `20260508005033`. Logged
explicitly as `target_corrected_to` in `resolved.json`, not silently rewritten.

`apply_save_repair.py` → the sheet write. It swaps only the `/save/`-prefixed token,
preserving everything around it: a leading `(`, trailing punctuation, co-references in the
same cell, and prose. Verified against all 348 real cell values with a synthetic mapping
before any live write — 0 leftover `/save/` tokens, 0 lost co-references, 0 altered prose.

Write protocol per CLAUDE.md hard requirements: FORMULA-render pre-read (abort on any
formula cell, exclude any cell that drifted from the snapshot), before/after backup CSVs
in this directory, `valueInputOption: RAW`, cell-scoped ranges only, post-write re-read
verified against the plan.

## Result (applied 2026-08-05)

| | |
|---|---|
| Unique targets resolved to a verified snapshot | 211 of 214 (incl. 1 corrected target) |
| Nothing archived (`NO_CAPTURE`) | 3 |
| Cells written | **344** |
| Cells skipped | 4 |
| Formula cells hit / drifted cells excluded | 0 / 0 |

`plan: 344 cells to rewrite; 4 skipped` → `pre-verify OK: 344 cells confirmed live ==
snapshot, no formulas` → `batchUpdate 344/344` → `post-verify OK: all 344 cells match
plan.` Independently re-verified from a fresh `refresh_csvs.sh` pull: 3 `/save/`
occurrences remain sheet-wide (exactly the expected ones, below), 0 on the Oil/NGL and
operators/owners tabs, and the gas tab now holds 888 `web.archive.org/web/` links.

**The FORMULA pre-read gate earned its keep**: it aborted the first dry run on
operators/owners `E3392`, which turned out to be
`=iferror(xlookup(F3392,'Gas pipelines'!…), …)` — columns A–E of that tab are ProjectID
xlookups mirroring the tracker tabs, not data. Repairing Gas row 2437 fixed the mirror's
display for free. Recorded in `docs/reference/gem_schema.md`.

## Open items (deliberately left for a human)

- gas `Status [ref]` r2735 — `haishu.gov.cn`: nothing archived, and the origin now 404s.
  The value it supports has no recoverable source.
- gas `Status [ref]` r3032 — `ggzy.neijiang.gov.cn`: nothing archived, origin
  ConnectTimeout. Same problem.
- gas `RouteNotes` r3921 — prose, not a ref cell. CB's own note quotes the broken URL
  with an elided path while describing this very defect, and recommends swapping that
  row's `[ref]` to the plain `sthj.qdn.gov.cn` original. Left untouched; the recommendation
  still stands.

## Files

- `extract_targets.py`, `occurrences.json`, `raw_targets.json` — the survey
- `resolve_snapshots.py`, `resolved.jsonl`, `resolved.json`, `resolve.log` — resolution
- `apply_save_repair.py` — the authorized sheet write
- `before.csv` / `after.csv` — backups (before holds both old and new values)
- `skipped.csv` — occurrences deliberately left alone, with reasons

## Separate issues surfaced, NOT fixed here

These are misplacements, not link defects; the repair only made their URLs resolve.

- gas `Wiki` r2437 and operators/owners `Wiki` r3392 both hold the *same* weixin article
  URL. `Wiki` is meant to hold the gem.wiki page URL — a source URL there is misfiled.
- gas `ResearcherNotes` r3006 is a bare URL with no accompanying note.
- gas `RouteNotes` r3080 is a bare URL plus a stray token `600617`.
