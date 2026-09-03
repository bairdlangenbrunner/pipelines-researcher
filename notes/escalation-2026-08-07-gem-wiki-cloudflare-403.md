# Escalation (RESOLVED) — gem.wiki returned HTTP 403 to all automated fetches (Cloudflare)

**Date:** 2026-08-07 · **resolved 2026-08-10**
**Scope:** tracker-wide, not Pakistan-specific. Surfaced during the Pakistan gas pass.
**Severity:** degraded two committed workflow legs; no data was wrong as a result.

> **STATUS — read this first.** Fixed 2026-08-10; Under Attack Mode itself was switched
> off by 2026-08-11 (any UA passes again), but keep the `baird-wiki` UA — it is the
> firewall identity and the bypass if UAM returns. During the incident the gem.wiki zone
> ran Cloudflare in Under Attack Mode, and a WAF rule keyed on a leading **`baird-wiki`**
> User-Agent token was what let a script through — no allowlist or token needed, just the
> right UA. Added
> as `url_verifier.WIKI_UA` and wired into `harvest_wiki_citations.py` and
> `wiki_alignment.py` (deliberately byte-identical to `goit-ggit-data-ops`'s
> `gem-wiki/gemwiki.py` USER_AGENT so both repos present as one client in the firewall
> logs — **keep them in sync**). Both legs were then re-run for Pakistan:
> `wiki_alignment` went from **70 all-`UNPARSED`** to **99 real records** (24
> `WIKI_UPDATE` · 6 `WIKI_STALE_VS_STAGED` · 69 `SHEET_SUSPECT` · 0 `UNPARSED`), and the
> citation harvest from **0 pages** to **63/63 fetched**. The packet at
> `20260810_1057_ET` carries the re-run; anything stamped earlier does not.
>
> **What the re-run showed about the cost of the blackout:** on the *refs* side, almost
> nothing — all 63 pages together cite only **10 distinct external URLs**, 8 of them
> already known, so the "harvested leads" the sweep lost were a thin vein here (a
> map-bulk-load country cites the map). On the *alignment* side the cost was real: 69
> `SHEET_SUSPECT` records that the packet would otherwise never have shown, 68 of them
> one systemic finding — see
> `notes/escalation-2026-08-10-pakistan-operator-blank-68-rows.md`.

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

## Recommended next steps (Baird's call) — item 3 still stands

1. ~~**Confirm whether this is intentional.**~~ **Answered:** it is deliberate (Under
   Attack Mode), and the sanctioned way through is the `baird-wiki` UA token, already
   in use by the sibling `goit-ggit-data-ops` repo. No allowlist request needed.
2. ~~Authenticated MediaWiki API fallback~~ — not needed.
3. **Still worth doing: make both scripts fail loudly.** A well-formed all-`UNPARSED`
   artifact that reads like a successful run is the real trap here, and it is a one-line
   guard in each script. The Pakistan packet shipped once with an empty wiki surface
   precisely because nothing shouted.

## Original recommendations (superseded)

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
