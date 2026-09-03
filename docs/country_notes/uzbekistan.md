# Uzbekistan

31 gas rows (GGIT) and 2 oil rows (GOIT). **First-ever full pass EXECUTED 2026-08-26 — staged, not
applied.** Nothing has been written to the sheet or the routes repo.

**THREE files to work** — the packet does NOT subsume the recons (`recon_actions = 0`):

- `deliverables/pipelines_batch_20260827_0931_ET_uzbekistan-gas_handoff-{actions,evidence}.xlsx`
- `deliverables/pipelines_batch_20260826_1350_ET_uzbekistan-gas_reconciliation-gulfpub.xlsx`
- `deliverables/pipelines_batch_20260826_1350_ET_uzbekistan-gas_reconciliation-osm.xlsx`

Packet counts: 41 open decisions, 69 backend paste units, 21 operators/owners paste units, 45 wiki
updates, 54 open flags, 120 ref-detail rows, 2 status changes, 4 fills. Ref work on the 18 in-scope
rows: **84 `REFS_ADDED` / 34 `UNRESOLVED` / 2 `DEAD_LINK`** (+38 re-verified, counts-only), plus 43
concerns (attribution 18, spec 23, existence 2) and 14 mechanical flags. The `20260826_1412_ET` and `1419_ET`
handoff builds are archived and superseded — work the `20260827_0931_ET` pair, rebuilt to carry all
13 class-level escalations.

Plan page: <https://claude.ai/code/artifact/0dffe002-b68d-4b7a-acc6-def294520a34>.

Row profile: `operating` 28, `construction` 1, `shelved` 1, `cancelled` 1. Researchers **NF** 27,
**AV** 3, **ZK** 1. Every row is `Fuel = Gas`, `PipelineType = transmission`. Routes are the best of
any scope swept so far — `RouteAccuracy` high 16 / medium 4 / low 1 / very low 8 / `no route` 2, and
29 of 31 are `Mapped route (at any accuracy)`. **Oil (2 rows) has not been swept.**

## What defines Uzbekistan: 13 of its 31 rows belong to Kazakhstan's pass

Uzbekistan is a **transit country**, and a trunk crossing two countries is **ONE row that both
`--country` scopes select**. Thirteen of the 31 gas rows are the same rows the Kazakhstan pass
already researched and staged — the Central Asia–Center, Central Asia–China, Bukhara–Ural and
Bukhara–Tashkent–Bishkek–Almaty strings:

`P0739 P0740 P1124 P2289 P2291 P2292 P2299 P2300 P3956 P5695 P5770 P5771 P5810`

Eleven of them sit in already-adjudicated Kazakhstan clusters B/C/D/E. The risk was never duplicated
effort — it was **contradiction**: two staged records against one sheet cell, and whichever workbook
is pasted last wins silently.

**Scope is therefore the 18 domestic rows** (Baird, 2026-08-26). Enforced with
`build_ref_worklist.py --exclude-pids @batches/uzbekistan-gas/carried_from_kazakhstan.txt`; the list
was **derived from Kazakhstan's `staged_resolutions.json`, not hand-typed**, and every one of the 13
was confirmed to carry a real staged record before being excluded. The run prints an `EXCLUDED …`
line. Scope: 31 rows / 283 units → **18 rows / 152 units** (78 `HAS_REF` / 74 `MISSING_REF`).

**Two consequences to carry forward:**

1. **Those 13 rows now depend on the Kazakhstan batch actually being applied.** Until it is,
   Uzbekistan has 13 rows that neither batch is actively researching and whose fixes sit in another
   country's workbook. The handoff packet must say so explicitly, or the researcher reads their
   absence as "nothing to do".
2. **The exclusion stops at the research legs** (§9 steps 1–4, 7). **The recon leg keeps all 31 GEM
   rows.** `reconcile.py` matches reference records against the in-country GEM roster; drop the
   trunks from that side and their reference counterparts re-bucket as `DISCOVERY_CANDIDATE` —
   phantom additions for pipelines GEM already tracks, on exactly the lines most likely to be
   proposed as discoveries. Leave `--country` alone in step 5.

Step 3 (cancelled review) is consequently **empty**: P0740 Caspian Coastal was the only `cancelled`
row and it is one of the 13, already swept in Kazakhstan's cancelled review. Skip it and cite that
verdict.

## The wiki-ref trap: 18 rows, 11 pages

The wiki is organised by **pipeline**; the tracker by **segment**. So "fill the refs in from the
wiki page" cannot mean stamping a page's citation list onto every row that points at it — that
manufactures precisely the false corroboration Kazakhstan's cluster B is a record of, one
system-level figure restated on every string, now with a footnote on each, which is worse than a
blank.

**A harvested URL is a candidate for the unit *(ProjectID × ref column)*, and earns that cell only
when the page names that segment's own value.** Otherwise it goes in `ResearcherNotes` and the unit
stays `UNRESOLVED`.

The exclusion made one case **sharper, not safer**. P6933 / P6934 / P6935 are
`SegmentName = Mubarek-Zirabulak I/II/III` carried under `PipelineName =
Bukhara-Tashkent-Bishkek-Almaty Gas Pipeline`, and they point at the BTBA wiki page — **whose own
parent rows P0739 (segment I) and P5810 (segment II) are two of the 13 now excluded**. So that
page's citations are overwhelmingly about the parent trunk, and almost none is evidence about a
Mubarek-Zirabulak string's own length or diameter. This is the row set where naive page-to-row ref
copying does the most damage.

Gazli–Kagan is the other multi-row page (P2290, P3983, P3984); Ahangaran–Pungan, Yangiyer–Ahangaran
and Mubarek–Kagan back two rows each.

### The pool was a worklist and we treated it as a lookup table (measured 2026-08-27)

The harvest pulled **127 unique citations**; the legs used 21 and **never opened 88**. That is a
design flaw, not an oversight: each leg was contracted to satisfy an owed unit, so a subagent
stopped at the first sufficient source and never came back for the rest of the page's citations —
and nothing reported the shortfall, so an `UNRESOLVED` reads as *no source exists* when for some
cells it means *a candidate was never opened*. 83 of the 88 sit on rows still reporting
`UNRESOLVED`, but 72 of those are on the two parent-trunk pages (49 Central Asia–China, 23 BTBA),
where declining is right per the rule above — so only **~11 are real untested yield**. **Rule: a ref
leg must report how many harvested citations it opened; an unopened citation on a row with an owed
cell is an open item.**

All 90 full URLs were then screened: **55 live / 35 failed, and only 12 of the failures are
confirmed 404/410** (the other 23 are 401/403/412/429/521 and timeouts — access failures, never
deletions). **16 of the 55 live sit off the parent-trunk pages** and are the real reading list.

**But a reachability screen is not a read.** `utg.uz`'s `/ru/press-service/novosti/…` section serves
a **soft 404**: the Yangiyer–Akhangaran press release returns 200 with 139,482 bytes and a nonsense
sibling slug returns 200 with 139,384, neither carrying an article body — while `/ru/invest/` 404s
honestly, so the behaviour is *section-specific and cannot be inferred from the host*. Prove a
suspected soft 404 by fetching a nonsense sibling slug and diffing the bodies. Nothing needs
un-staging (these were candidates, never filled cells), but the page that might have settled
**P6963/P6964** is unreadable at the origin, Wayback timed out again, and the WebSearch budget is
spent — so that conflict needs a fresh session. The one page from the pool that *was* readable,
`utg.uz/ru/invest/aktsii-i-dividendy/`, is genuine and dated (share capital at 01.04.2024: Ministry
of Economy and Finance 51.7%, Uzbekneftegaz 46.78%, 625,777,072 shares total) and is **declined on
the unit rule** — it names who owns the *company*, and every owed cell asks about a *pipeline*. It
does corroborate the sourcing chain behind the medium-tier operator attributions.

## Link rot, measured two ways

- **Existing sheet refs** (18-row scope, `--verify-existing`): of 78 filled cells, **39 carry a dead
  or missing link — exactly half.** The pass is as much repair as it is filling.
- **Harvested wiki candidates**: 234 citation instances → **118 distinct URLs** → 80 live, **14 true
  404/410**, 14 blocked (401/403/412/429 — *not* deletions), 8 timeout/DNS/5xx, 2 live-but-content-
  screen-missed (a screen, not a verdict). Of the 19 true deaths across all 31 rows, 15 have a
  Wayback capture; the archive snapshot is **added alongside** the dead URL, never swapped in.

## Gotchas

- **`utg.uz` (Uztransgaz) is the most-cited host and its history page is dead.** 10 URLs, 5 of them
  404, the repeat offender being `/about/history/` in Russian, English and print variants. The live
  origin 404 is confirmed. A Wayback capture **exists and is unread**:

  ```
  http://web.archive.org/web/20260314231446/https://www.utg.uz/ru/about/history/
  ```

  This is the shape Ukraine's VNIPItransgaz table had — dead at the origin, whole in the archive, and
  the one place line-wise detail exists. **Probe it before assuming anything about its contents.**
  Repeated attempts on 2026-08-26 timed out: `archive.org` (the availability API host) answered in
  0.5 s while `web.archive.org` content serving was unreachable — DNS clean, single A record,
  IPv4-forced fetch still timing out at 60 s. That is a transient network condition, **not evidence
  about the source**, and the 4-of-19 with "no capture" may simply need re-checking too.
- **Uzbekistan is the THIRD Cyrillic scope**, after Ukraine and Kazakhstan. Do not assume otherwise
  because the country writes Uzbek in Latin script — OSM's two named features are **Russian**
  (`Средняя Азия - Центр`, `Газопровот УППГ Кувачи Алат - УППГ Северные Шады`), so the 2026-08-14
  `translit_cyrillic` fix is load-bearing here: without it the name axis sees the empty string on the
  only two features that have anything to say.
- **`Operator` is not on the GGIT gas tab.** It lives on the ProjectID-keyed "Pipeline
  operators/owners" tab (GID 1489950650, `header=1`) — filled on 13 of 31 rows, with
  `Operator [ref]` filled on **0**.
- Read with `keep_default_na=False, na_values=[]` as everywhere, and select countries with
  `normalize.country_matches()` — **never a bare `==`**, and note `split_countries()` returns
  lowercased strings.

## What the pass found

**The operator question is resolved for 8 of 9 rows, at medium — deliberately not high.** No document
names any of these pipelines *together with* its operator, so the per-line attribution is inference
from a sourced national sole-operator regime plus endpoints that are directorate seats. Three
verified sources carry it: Uztransgaz's own org-structure page naming the MGQB directorates with
their seats and the function *"Magistral gaz quvurlari, inshoot va qurilmalarini ekspluatatsiya
qilish"*; its history page recording **Decree 4388 of 9 July 2019** splitting Uztransgaz out of
Uzbekneftegaz into transmission + Hududgaztaminot and calling it *"yagona operator"* (sole
operator); and gazeta.uz independently reporting a 1020 mm trunk *"belonging to the Gazli Directorate
of Main Gas Pipelines."* Staged as 4 upgrades off `UNRESOLVED` (P2290, P6934, P6936, P6937) and 6 new
fills (P3983, P3984, P6965, P6966 at medium; **P4073 and P5870 left `UNRESOLVED` at low** — Nukus is
the seat of no listed branch, and Sarymay CS could not be located).

**P2698 is the row to not guess at.** Two independent signals converge on it as the odd one out:
Uztransgaz publishes no directorate for Surxondaryo/Sherobod/Termiz/Denov/Qarshi, *and* the row's own
`Owner1` is `Uzbekneftegaz`, not Uztransgaz. Left `UNRESOLVED` on purpose — **do NOT default it to
Uztransgaz.**

**The Cyrillic/Latin `Operator` split is the sheet's, not ours.** P6933–P6937 genuinely carry
`Узтрансгаз` in `Operator` while their own `Owner1` says Latin `Uztransgaz`, and
`OperatorLocalLanguage` — the column that exists for exactly this — is empty on all five. Our staged
values faithfully mirror the sheet. Staged as 5 attribution concerns with a mechanical
recommendation, **not auto-applied**: P6937's multi-party string needs a human split decision.

**Both border flags resolved deterministically, and neither is a country-column change.** P4071's
Tajik crossing is a **2-vertex-chord artifact** — a straight line between two Uzbek endpoints clips
Tajik territory; redraw, do not add a country. P6936 (Afghan vertex 36.09 km inside AF / 19.65 km
from TM) and P6937 (Afghan vertices at 35.83 / 16.34 / 0.77 / 14.54 km, plus a Tajik vertex 49.40 km
in) are **too deep for Amu Darya river slop** — only the 0.77 km vertex is plausible slop. Both
readings (mis-drawn schematic vs. genuine transit) stay open. **Do NOT add Afghanistan to either
row** on this evidence.

**A tool blocker bounded the pass, and it is a measured fact, not an excuse.** The session-wide
WebSearch quota was exhausted (200/200) — re-tested independently, identical result — so the last
two questions could not be closed: **P2698's operator** and **P6936's `StartYear1`** (with the
Afghan-transit question). Both need a fresh session. Everything else was closed by direct fetches to
known origins.

**Wayback content is unreadable from this session by both available paths.** `archive.org`'s CDX API
answers in ~0.5s while `web.archive.org` content serving times out from this machine *and* is refused
to the harness fetcher. Capture existence is provable here; capture content is not. 11 staged units
cite a capture; **5 rest on one alone** (P3983 Status, P3984 Length, P6964 Status/Fuel/PipelineType) —
re-fetch those before pasting. Per the access-failure rule none of this is a deletion and no live ref
was dropped for it. One self-correction belongs here: P6933 `Owner [ref]` was staged claiming a clean
read of capture `20260314231446` at tier high with "Independent? yes", while the escalation recorded
that same capture as unread; corrected to existence-only, support now resting on its live
`lex.uz/docs/537622` leg, tier high retained because lex.uz is primary/regulatory.

**A schema misuse was caught across 13 units.** `independent` means the rubric's *"≥2 independent
sources agree"* and renders as an "Independent? yes/no" column, but it had been set `True` on 13
single-source units whose own notes said "single independent source" — i.e. read as "this source is
independent of GEM". All 13 corrected to `False`; two (P2290 Fuel, P2698 Fuel) also dropped
high → medium, since high needs 2+ agreeing sources *or* a single primary/regulatory one and a news
outlet is neither. Classes did not move (84/34/2 before and after) — only the tier colors and that
column, which is exactly the surface a researcher trusts when deciding whether to paste.

## Reconciliation results

- **GulfPub — both gates crossed on paper, and the conflict gate is EMPTY in fact.** 48 overlaps, 26
  additions, 13 near-misses, 10 `gem_only`, **9 status conflicts = 18.75%** of matched rows, over the
  >10% gate. But all 9 are the same two rows (P6963/P6964) and the same disagreement,
  `construction → operating`; excluding them the rate is **0/33 = 0.00%**. Root cause is P6964's
  off-corridor route inflating `LengthEstimateKm` to 111.29 km (redundancy cluster E, which now has
  four corroborations) — **fix cluster E and the gate dissolves.** Additions at 26 sit just *under*
  the >30 gate, but the 74-records-vs-31-rows scope question below is the same question in another
  form.
- **OSM — 124 additions crosses the >30 gate on volume alone, and it is a scope mismatch, not a
  discovery signal.** 0 overlaps, 31 `gem_only`. 69 of 124 features are sub-1 km distribution stubs
  and 52.6% of total mileage lies within 2 km of an existing GEM vertex. `MATCH_QUALITY` fires on the
  name axis, and that is a **true report**: only 2 of 124 features are named, both in Russian. It is
  *not* a tuning signal — 29 of 31 GEM rows are routed, 16 at `high`, so the dead-axes condition does
  not hold.
- **A `geoarea_weight` override was REFUSED on measured evidence, not by policy.** An A/B at 0.30
  yields 4 overlaps of which **3 are manufactured**: a 1.625 km stub and a 0.036 km stub each
  "corroborating" the same ~350 km row at route IoU 0.029 / 0.027, clearing the gate on
  `s_geoarea = 1.0` alone. Contrast `gas_iq` / `gas_pk`, where stubs sit *on* the corridor. Geoarea is
  untestable on 9 of the 18 domestic rows (P2290, P2698, P3983, P3984, P6933–P6935, P6965, P6966).
  `gas_uz` therefore ships with **no override** — recorded as a comment in `sources/osm/manifest.yml`.

## Reference datasets

- **GulfPub** — 74 gas records ingested to `staging/recon-gulfpub-20260826/`, all `operating`, 74/74
  with geometry. **74 records against 31 GEM rows is an open scope question** (Malaysia's shape); the
  inclusion rule is Baird's call, not the agent's. In the event the additions landed at 26, just under
  the >30 gate — the volume question is real regardless of which side of the threshold it fell on.
- **OSM** — `sources/osm/data/osm-uz-gas.geojson`, registered as dataset `gas_uz` (2026-08-26). 124
  features / 420 ways, all `operating`, **6,314.6 km** — structurally the richest gas extract in the
  registry by length: eight features exceed 400 km and carry 5,379 km between them, i.e. OSM has
  drawn the Central Asian trunk corridors. But 69 of 124 are sub-1 km stubs (Ukraine's
  scope-mismatch shape), and attributes are all but absent: 2 named, 2 with a diameter, **zero**
  operator or owner. No `osm_pressure` either — the tag is carried through since 2026-08-16 but no
  Uzbek feature has it; `usage=transmission` on 7 of 124 is the only transmission signal. **No `geoarea_weight` override**, deliberately — that override exists for the
  dead-axes condition and it does not hold here (29 of 31 GEM rows routed, 16 `high`). With 2 named
  features the name axis genuinely is near-dead, so `MATCH_QUALITY` firing on that alone is a true
  report, not a tuning signal.

### Fixed here: `osm_id_key` was not unique

Uzbekistan's extract was the worst-affected in the registry by distance — **6 features / 865.8 km
sharing a non-unique id**, one key covering three disjoint pieces of 618.01, 144.95 and 25.49 km.
Cause: the key was built from *which source ways touch this part*, so disconnected parts of one way
group all got the same key. `ingest.py` had been papering over it with order-dependent `#2`/`#3`
suffixes, which cannot support cross-scrape identity. Fixed in `fetch_overpass.py`
(`_disambiguate_keys`, geometry-derived discriminator), touching **only** keys that actually
collide; Uzbekistan re-fetched the same day (it had no committed run to move) — 124 features,
geometry set identical, 113 of 124 keys unchanged, warning gone. Every other extract keeps its
current keys until it is next re-fetched, and no committed run in any country is owed a re-run.
Registry-wide counts and the fix itself live in `sources/osm/NOTES.md`.

### Open engine item: `name:en` is fetched and discarded

The CAC feature carries `name:en = 'Central Asia-Center'` — a clean English name that would match
GEM's own name directly — and **no manifest maps it, so the matcher never sees it.** The canonical
record's `aliases` field exists for this and is declared-but-dead (`adapter_base.py` never populates
it; `match.py` scores `name_norm` alone). Registry-wide it costs **4 features**, all with a non-Latin
primary name, including Iraq oil's Arabic Kirkuk–Ceyhan trace for which `name:en` is the *only*
possible name signal. Full writeup and the three-line change: `sources/osm/NOTES.md`.

**It does not block this pass** — Uzbekistan's one affected feature is the CAC trunk, whose GEM rows
are among the 13 excluded from the research legs. Fixing it would move the committed `gas_kz` and
`oil_iq` runs, so it is Baird's call.

## Open calls for Baird

1. GulfPub's 74-vs-31 inclusion rule (above) — if the answer is "out of scope", write the inclusion
   rule into this note.
2. Research-language capability for Russian and Uzbek (both Latin *and* Cyrillic).
3. Whether to add the recoverable Wayback snapshots to the sheet — a sheet write, so it needs
   explicit per-batch authorization. Note the caveat above: their existence is proven, their content
   is unread from this session, and 5 staged units rest on a capture alone.
4. **Wikipedia policy — SETTLED 2026-08-27** (Baird): gem.wiki is never a source, **Wikipedia is
   citable**. The rules and the tracker-wide consequences live in `docs/reference/source_roster.md`
   → "Wikipedia — citable"; no code change was needed. For this batch: the one Wikipedia citation the
   harvest declined on principle is eligible, and any future pass may cite Wikipedia directly.
5. Re-run in a fresh session once the WebSearch budget resets: **P2698's operator**, **P6936's
   `StartYear1`** + the Afghan-transit question, and a retry of the `utg.uz` capture
   `20260314231446`.
6. The 13 carried rows **depend on the Kazakhstan batch being applied.** Until it is, neither batch
   researches them.
