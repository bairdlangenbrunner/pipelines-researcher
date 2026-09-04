# A shortened URL bypasses the source blocklist entirely

**Found:** 2026-09-04, during the US-gas deep sweep (batch 1, TX operating cohort).
**Fixed at source the same day** in `scripts/url_verifier.py`. Live-sheet findings below
are **reported, not applied** — they need Baird's authorization.

## The defect

`verify_url()` applied `GEM_HOSTS` and `BLOCKLIST_HOSTS` as substring tests against the
**submitted** URL string, then fetched with redirects followed. So any indirection walked
straight through the ban:

```
verify_url("http://bit.ly/2sYGqrY")  ->  ok=True, 200, "expected content present"
                                          (serves abarrelfull.wikidot.com/tiger-gas-pipeline)
verify_url("http://abarrelfull.wikidot.com/tiger-gas-pipeline")
                                     ->  ok=False, "blocklisted tertiary aggregator"
```

Same URL, same bytes, opposite verdicts. The ban was one 301 away from being decorative —
and this is not hypothetical exposure: **9 of the 20 shortened links in this batch's own
harvested citation pool resolve to `abarrelfull.wikidot.com`.**

## The fix

Two changes in `url_verifier.py`:

1. **`SHORTENER_HOSTS`** — `bit.ly`, `tinyurl.com`, `goo.gl`, `ow.ly`, `t.co`, `buff.ly`,
   `is.gd`, `rebrand.ly`, `cutt.ly`, `shorturl.at`, `trib.al` are rejected before the
   fetch. A shortener is never a citable address: it is an opaque, revocable indirection
   whose target can be repointed after we cite it. (Already the standing reading — the
   Egypt 2026-08-27 pass ruled `bit.ly/2oFzXCm` uncitable "verifies live but a shortener
   is never a citable ref — resolve it or drop it". It was a ruling, not a gate.)
2. **Post-fetch chain re-check** — `GEM_HOSTS`/`BLOCKLIST_HOSTS` are re-applied to
   `r.url` and to **every hop in `r.history`**. This is the general fix; the shortener
   list only makes the common case fail fast and legibly. A vanity domain, an
   aggregator's own 301, or a future shortener we have not listed now fails on where it
   lands, not on how it was spelled.

**Rule:** a URL ban is about the BYTES SERVED, never the string submitted. Any check that
reads a URL must also read where that URL goes.

## Blast radius

- **Staged batches: clean.** 0 `proposed_refs` on a shortener across all
  `batches/*/staging/*/staged_resolutions.json`. Nothing staged needs withdrawing.
- **The live tracker: 9 cells, and they are not benign.** Found by scanning every `[ref]`
  column of the 2026-09-02 snapshots and resolving each link:

| Tracker | ProjectID | SheetRow | Column | Shortener resolves to |
|---|---|---|---|---|
| GOIT oil | **P0020** | 1302 | `Start [ref]` | **`abarrelfull.wikidot.com/express-oil-pipeline-system`** — BANNED |
| GOIT oil | **P0020** | 1302 | `Diameter [ref]` | **same abarrelfull page** — BANNED |
| GOIT oil | **P0533** | 2035 | `Route [ref]` | **a `google.com/search?q=…` URL** — navigation surface (the Egypt defect, shortened) |
| GOIT oil | P0946 | 1565 | `Start [ref]` | `globalenergyobservatory.org/form.php?pid=40938` — tertiary aggregator |
| GOIT oil | P0951 | 1661 | `Start [ref]` | `globalenergyobservatory.org/geoid/40691` — tertiary aggregator |
| GOIT oil | P0539 | 1863 | `Route [ref]` | a LinkedIn Pulse post — self-published |
| GGIT gas | P1313 | 766 | `Route [ref]` | petroleum-economist.com article — **404** |
| GOIT oil | P0027 | 1592 | `FuelSource [ref]` | enbridge.com page — **404** |
| GOIT oil | P0531 | 329 | `Route [ref]` | researchgate.net figure — 403 (access failure, NOT a deletion) |

Resolutions for this batch's harvested pool are stored at
`batches/united-states-gas/staging/deepsweep-tx-operating/shortener_resolutions.json`.

## What the ban actually cost, in data

The bypass is not only hygiene. The US-gas ref pass hit its consequence directly on
**P0190 (Florida Gas Transmission, system-level row)**: its `Start` and `Capacity` values
trace *solely* to abarrelfull, reached through a bit.ly link in the harvested citation
pool, with no independent replacement findable after exhausting FERC, EIA, SEC, Wikipedia
and the trade press. Both units came back `UNRESOLVED` — correctly, since a value whose
only support is a banned source is an unsourced value.

Corroborating detail: P0190's `Capacity` of 1059.44 MMcf/d is a near-exact conversion of
30,000,000 m3/day, which is how that figure would have been carried over from the
aggregator rather than read off a primary document. Flagged, not asserted as wrong.

So the shortener bypass had been quietly supplying the one source the project bans, to
rows whose `[ref]` cells looked empty rather than wrong. Expect more of this as the US
cohort is worked: a blank `[ref]` on an old row is not evidence nobody looked, it may be
evidence someone looked at abarrelfull.

## What is owed

Nothing here is applied. Recommended, in order:

1. **P0020's two cells cite a banned source** and should be re-sourced, not merely
   re-pointed — abarrelfull is banned outright, so the values behind those cells are
   currently unsourced. Chase whatever primary source that page footnotes.
2. **P0533's `Route [ref]` is a Google search URL** and cannot support any value; the
   unit is owed a real document.
3. The two confirmed **404s** (P1313, P0027) may retire under the standing rule; the
   **403** (P0531) may not — that is an access failure, so add a Wayback capture
   alongside rather than dropping it.
4. The remaining three (P0946, P0951, P0539) should be de-shortened at minimum, so the
   citation says what it actually points at.

Scope note: 8 of the 9 are GOIT oil rows, outside the US-gas batch that found them.
Logged in `docs/research_backlog.md`.
