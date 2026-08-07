# Escalation — gem.wiki returns HTTP 403 to all automated fetches (Cloudflare)

**Date:** 2026-08-07
**Scope:** tracker-wide, not Pakistan-specific. Surfaced during the Pakistan gas pass.
**Severity:** degrades two committed workflow legs; no data is wrong as a result.

## What happened

Every automated request to `gem.wiki` returns **HTTP 403** with a ~6 KB Cloudflare
challenge body. Confirmed against four independent access paths, all with a normal
browser User-Agent:

| Path | Result |
|---|---|
| `https://www.gem.wiki/<Page>` | 403 (6.0 KB challenge) |
| `https://www.gem.wiki/api.php?action=query&prop=revisions&rvprop=content` | 403 |
| `https://www.gem.wiki/Special:Export/<Page>` | 403 |
| `https://www.gem.wiki/index.php?title=<Page>&action=raw` | 403 |
| `https://gem.wiki/<Page>` | 301 → the 403 host |

Setting a browser UA does **not** clear it, so this is a JS/TLS-fingerprint challenge,
not simple UA filtering. This is very likely the same block recorded in the Libya
commit `a80e7eb` ("wiki page moves blocked by cloudflare challenge"), i.e. it has been
in place for at least several days and is not a transient blip.

## What it breaks

Two committed legs depend on fetching gem.wiki:

1. **`harvest_wiki_citations.py`** (Country Sweep §3, every preset). For Pakistan it
   returned **0 external citations from 70 pages (0 fetched ok)**. The harvested-lead
   starting point described in the Sweep SOP §Sequence-3 simply does not exist for
   this run — research subagents had to start cold from open-web search.
2. **`wiki_alignment.py`** (Handoff packet §6 Leg 1). For Pakistan it wrote
   **70 records, all `UNPARSED`** — the leg produced zero alignment findings. The
   packet's wiki-alignment surface is empty, and that emptiness means "could not
   read", **not** "sheet and wiki agree".

## What it does NOT mean

- It is **not** evidence that any GEM row is unsourced. A row whose `[ref]` cells are
  blank is unsourced; a row whose wiki page we could not fetch is simply unread.
- The Pakistan gas rows genuinely *are* unreferenced (459/459 operating ref units came
  back `MISSING_REF`), but that was established from the **sheet**, not from the wiki
  failure. Do not let the two facts get conflated in the packet.
- Standing rule 1 is unaffected: we visit gem.wiki for leads and never cite it either
  way.

## Recommended next steps (Baird's call)

1. **Confirm whether this is intentional.** GEM controls gem.wiki; the Cloudflare bot
   rules may have been tightened deliberately. If so, ask for an allowlist for the
   researcher tooling's egress IP or a bot token — that is the clean fix and restores
   both legs unchanged.
2. **If an allowlist is not possible**, the fallback is an authenticated MediaWiki API
   path (the GEM Project Database MCP already carries a session cookie for a different
   host; gem.wiki would need its own), or routing these two scripts through a browser
   fetch that can satisfy the challenge.
3. **Until then, treat every `wiki_alignment` result as unavailable, not clean**, and
   expect the sweep's harvest step to contribute nothing. Both scripts should probably
   *fail loudly* rather than writing a well-formed all-`UNPARSED` / all-empty artifact
   that reads like a successful run — that is the real trap here, and it is a
   one-line guard in each script.

## Affected outputs shipped anyway

The Pakistan gas packet (2026-08-07) ships with its wiki-alignment leg empty and its
harvest file empty, both flagged in the workbook README. No other leg is affected:
route integrity, the mechanical checks, both reconciliations and the research fan-out
all ran normally.
