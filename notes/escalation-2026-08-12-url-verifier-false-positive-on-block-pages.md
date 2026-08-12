# Engine defect — `url_verifier.py` passed a geo-block interstitial as verified

**Found** 2026-08-12 by a cancelled-review subagent working Ukraine gas P0793, which
did the right thing: it distrusted a green verdict, fetched the page two other ways, and
reported the tool rather than the ref. **Fixed** the same day. Sibling defect found the
same day in the reference-side country filter —
`escalation-2026-08-12-multicountry-reference-filter-dropped-transit-trunks.md`.

## What was wrong

```
$ python scripts/url_verifier.py "https://energybase.ru/pipeline/stavropol-moskva" "1262"
OK   https://energybase.ru/pipeline/stavropol-moskva  — 200 + expected content present
```

The page is not a pipeline page. It is a 13,560-char IP/geo-block interstitial —
*«Доступ ограничен… использование VPN или прокси…»* — containing no pipeline content
whatsoever. Three independent faults lined up to make that read as verified:

1. **The match surface was raw HTML.** `text = body.lower()` meant markup counted as
   page content. The *only* occurrence of `1262` on the page was inside the SVG path
   coordinate `589.126229`, part of the block page's decorative graphic.
2. **A numeric needle was matched as a bare substring.** `"1262" in text` also matches
   inside `589.126229`, inside `41262`, inside a build hash or a timestamp. Digits are
   the shape most refs are checked on — lengths, diameters, capacities, years — so this
   is the highest-traffic path in the tool.
3. **Block-page detection was length-gated.** The `stub` heuristic only fires below
   `_MIN_BODY_CHARS = 1500`. A block page padded with an inline SVG is not short, so
   nothing fired and the verdict came back clean rather than caveated.

Individually each is survivable. Together they invert the tool's purpose: the gate that
exists to stop unverified URLs entering a workbook actively certified one.

## The fix

Three narrow changes in `verify_url`, unit-tested:

- **`_match_surface(body)`** strips `<svg>`, `<style>` and `<template>` blocks before any
  content match. `<script>` is deliberately **kept** — real values do live in JSON-LD.
- **`_contains(text, needle)`** gives a *purely numeric* needle whole-number semantics
  (`(?<![\d.,])…(?![\d.,])`) instead of substring semantics. Alphabetic needles keep
  plain substring matching on purpose: Russian and Ukrainian case endings mean a
  word-boundary test would create false negatives on exactly the sources Ukraine needs.
  `surface_forms()` already emits both `1000` and `1,000`, so separator variants are
  unaffected.
- **`_BLOCK_PHRASES`** detects access-denied / bot-challenge / geo-block interstitials at
  **any** body length, in Russian and English.

The block verdict is deliberately worded to prevent the obvious wrong reaction:

> NOT a deletion: keep the ref and ADD a Wayback snapshot alongside; only a confirmed
> 404/410 may drop a ref.

That is the standing rule, and a blocked-origin verdict is precisely where it gets
violated. The verdict dict also carries `blocked: True` for programmatic callers.

Post-fix, the same command returns:

```
FAIL … — 200 but this is an access-block/challenge interstitial (matched 'доступ
ограничен'), not the page — anything 'found' on it is a false positive. NOT a
deletion: keep the ref and ADD a Wayback snapshot alongside; …
```

`_name_present` now also reads the stripped surface, so a *name* cannot verify against
an svg/style block either.

## Exposure in already-shipped work — not yet re-verified

Every batch's refs were checked through the buggy gate, so some past `[ref]` cells may
rest on a false positive. The family is narrow — it needs a 200-returning block page
**and** the expected token to appear in its markup — but it is not hypothetical, since
the first place anyone looked turned one up.

**Not attempted here, and logged in `docs/research_backlog.md` as its own item:** a
re-verification sweep over the refs in *pending, not-yet-applied* staged batches. That is
the bounded set that would actually ship wrong, and it is a workstream, not a footnote to
a country pass. Countries whose sources skew toward geo-blocking hosts (`energybase.ru`
and the Russian trade press generally — so Ukraine, Kazakhstan, Russia, Central Asia) are
where it should start.

## The generalisable lesson

**A verifier that matches markup is not verifying the page.** Two rules follow, and they
generalise past this tool:

1. A content check must run against **prose**, and a **numeric** check must respect
   number boundaries. Digits are where collisions live, because markup is full of them.
2. **HTTP 200 is not evidence of content.** A block page, a cookie wall and a challenge
   are all 200s, and length is not a reliable tell once they carry inline graphics. Any
   "is this page really there" test needs a positive block-signal check, not just a size
   heuristic.

And the process lesson, which is the reason this was caught at all: **a subagent that
distrusts a green verdict and reports the tool is doing the job correctly.** That finding
arrived as a `spec` concern on P0793 rather than as a quietly-accepted ref.
