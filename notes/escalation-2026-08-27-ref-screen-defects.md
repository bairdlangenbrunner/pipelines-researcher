# Four defects in our own ref-verification chain (Egypt gas + oil pass, 2026-08-27)

All four are **ours, not the data's**, and all four were found the same way: by
reconciling counts, never by an error message. Each is fixed and every affected
worklist re-screened. Per the standing rule, a bug in our own config/code gets fixed
and every affected country re-run — not a caveat in a workbook.

---

## 1. A site-search URL and an archive index passed as citations

**The finding.** 104 of Egypt's 560 filled `[ref]` units (18.6%), on 16 rows across
BOTH trackers, rested on exactly two URLs — and **81 of them scored `ok`** in our
verifier:

- `https://egyptoil-gas.com/?s=Gas+Pipelines+Egypt` — a WordPress site search.
  Gas rows P8013, P8014, P8015, P8016, P8018, P8019, P8021, P8024, P8076, P8084.
- `https://egyptoil-gas.com/reports_category/monthly/page/7/` — a paginated archive
  index, titled "Monthly Reports - Part 7".
  Oil rows P7341, P7975, P7976, P7977, P7978, P7979.

**Why they can never be refs.** Their content is whatever the site published most
recently, so a value "found" there today is gone next month. Proved empirically:
`?s=zzqqnonsenseslug12345` returns HTTP 200 with 172,314 bytes of the same chrome.
They pass a naive substring screen whenever the digits happen to land in a result
snippet — which is precisely how 81 of them scored `ok`.

**Fix.** `_NON_CITATION_RE` + a check in `url_verifier.verify_url`, returning
`ok: False` with reason *"search/index page, not a document"*. The pattern is
deliberately narrow, after two false positives in the first draft:

- `/topic/<slug>` is **NOT** matched — Britannica uses it as its ARTICLE path
  (8 Saudi oil refs cite `britannica.com/topic/Trans-Arabian-Pipeline`, all legitimate).
- A bare `?q=` is **NOT** matched — only the search engines' own wrappers
  (`google|bing|duckduckgo|yandex`), since sites use `q=` for plenty besides search.
- Category/tag matching requires the path to END at the listing (or at `/page/N/`), so
  a real article living under `/category/<x>/<slug>` is untouched.

**Blast radius, repo-wide: 114 of 2,906 filled ref units (3.9%).**

| scope | non-citation units | of filled |
|---|---|---|
| egypt-gas | 53 | 263 (20.2%) |
| egypt-oil | 51 | 297 (17.2%) |
| uzbekistan-gas / ref-sweep-operating | 8 | 78 (10.3%) — `liting.uz/page/4` |
| iraq-gas / ref-sweep-operating | 1 | 99 |
| libya-gas / annual | 1 | 37 |

`scripts/repair_noncitation_screen.py --all --apply` re-screened every built worklist:
**91 url checks flipped, 89 units newly owed.** It touches only `existing_ref_checks` —
no value, class, or proposed ref — so an affected unit simply becomes owed again.
`ref_gap_worklist.py` gained a `NON_CITATION` bucket so the class is visible, not
folded into `LIVE_NO_VALUE`.

**Uzbekistan's 8 sit in a DELIVERED, staged-not-applied batch.** Its workbook will not
reflect this until rebuilt — logged in `docs/research_backlog.md`.

**A candidate replacement was chased and REJECTED.** The oil cluster's index page links
`egyptoil-gas.com/reports/egypts-annual-review-for-petroleum-transportation/`, a
plausible source for the PPC trunk lines. It was rendered and read **visually** (the PDF
is Illustrator artwork with outlined text — `pdftotext` yields 0 characters; rendered at
170 dpi against a 150 ppi native raster, so no upsampling). It carries **aggregate
transport statistics only** — crude 22.5 mmt / 39.2% share, diesel 15.1 / 26.3, gasoline
6.8 / 11.8, LPG 4.2 / 7.4 — and names no line, length, diameter or capacity. It is NOT
the source for those 51 units; they genuinely need new sources.

*(Aside worth keeping: that PDF is served as `application/pdf` bytes **concatenated with
an HTML page** — 683,544 bytes served against `/L 506968` declared, ending `</html>`.
`pdftotext` fails with "Couldn't find trailer dictionary" until you cut at the last
`%%EOF`.)*

---

## 2. `link_live` was dead code — the amber/red distinction never fired

`seed_resolutions_from_worklist._verifications()` projected `status` away when copying
`existing_ref_checks`, and `link_live` is computed off `status`. So the flag was **always
False**, and the workbook's amber ("page is live, the value just isn't on it — go read
it") vs red ("genuinely gone") distinction never appeared on a single record.

Fixed by carrying `status` through, plus: a `non_citation` verification forces
`link_live = False`, because amber would say *"re-read this page"* — wrong advice when
the URL is a site search.

**Effect after the fix:** gas 21 of 68 DEAD_LINK records are amber, oil 26 of 101. Those
47 units are re-read work, not re-source work.

---

## 3. The merge silently preferred a stale snapshot

`merge_deepsweep_shards.py` merges onto `staged_resolutions.prior.json`, a snapshot
taken on the FIRST merge run. Re-seeding rewrites `staged_resolutions.json`, which the
merge then **ignores**. This is how defect #2's fix survived a `--force` re-seed and
three merges completely unnoticed: the seeder was correct and the merged output was not.

Fixed with an explicit warning when `staged_resolutions.json` is newer than the
snapshot. Re-seeding is the normal way to pick up a worklist repair, so the merge now
says it is merging the older file rather than silently preferring it.

**Rule:** after any worklist or seeder repair, refresh the baseline
(`cp staged_resolutions.json staged_resolutions.prior.json`) before merging — and only
when no `ref_shards/` research has been folded into it, or that research is lost.

---

## 4. (previously filed) `independent` outlived its refs

See `notes/escalation-2026-08-27-independent-flag-outlived-its-refs.md`.

---

## The shape of all four

None of these produced an error. Every one produced a *plausible number* — 81 URLs
scoring `ok`, a `link_live` flag that was uniformly False, a merge that reported success
against the wrong baseline. **The only thing that caught them was reconciling counts
that should have matched and didn't.** That is the method lesson, and it is the same one
the China/Jiangxi and Uzbekistan passes recorded independently.
