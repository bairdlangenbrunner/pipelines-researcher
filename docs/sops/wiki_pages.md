# SOP: gem.wiki pages for new pipelines

How to create wiki pages for newly added pipelines, and how to add a new segment to a pipeline that already has a page. Written from the US gas pilot (Aquila Pipeline new page, Oasis Gas Pipeline edit, 2026-11-04). The wiki template is the Google Doc "wiki pipeline template" (https://docs.google.com/document/d/1BIrEsqOkQEtsi9oFG0xELJn3EBk3ENVymSOMsvYNKmo/edit?tab=t.0). If the template and this SOP disagree, the template wins and this file gets fixed.

## Standing rules

This SOP covers hand-built pages. The prep for having the data team generate every pipeline page from the tracker (template, readiness report, example tracker file) lives in `wiki/` (see `wiki/README.md`). Once that generator exists, the layout there replaces the bullet-list layout below.

1. **Pilot first.** Post one new page and edit one existing page, and get Baird's approval before any bulk publish.
2. **Never cite GEM.** No gem.wiki or globalenergymonitor.org URL in a reference. Banned hosts (abarrelfull, theodora.com, yingdodo) are also excluded. The generator drops them.
3. **Edits to existing pages need a live-text check.** Before posting, re-read the live page and confirm it is unchanged since the draft was made. Never overwrite someone else's edit.
4. **The sheet's Wiki column is not written by this workflow.** Writing new URLs back needs Baird's explicit OK and `gws-gem-write`, like any sheet write.
5. **No deleting.** The wiki account has no delete or suppress-redirect rights, so a bad page cannot be undone by deletion. Check drafts before posting.
6. Prose follows the notes style rule: short sentences, plain words, no AI-sounding phrasing, no em-dashes. American spelling.

## Tools

- `scripts/build_wiki_pages.py --scope <scope.json> --out <dir>` writes local `.wiki` drafts for new pages and edits. It posts nothing.
- `../goit-ggit-data-ops/gem-wiki/gemwiki.py` is the one wiki client: `session(login=True)`, `page_text`, `edit_page(s, title, text=, summary=, bot=False)`. It throttles to 5 requests a second. Retry on 429. Use `bot=False` (the account lacks the bot right).
- `scripts/wiki_pdf_titles.py` downloads each PDF ref and prints its title and first-page lines. Titles go in `data/wiki_pdf_titles.json`.
- `data/wiki_backgrounds.json` holds hand-written Background prose per ProjectID, plus a `_refs` table of reusable citations.

## Steps

1. **Scope.** Pull a fresh snapshot (`./scripts/refresh_csvs.sh`). List the newly added ProjectIDs. Group them by PipelineName into `scope.json`: per name, `pids`, `wiki` (existing URL, `MISSING`, or `EXISTS:<title>`), `routes`, `oldrows`. Optional keys: `link_only` (PIDs the page already describes, so only the map is redrawn, no segment is added), `rebuild` plus `keep_background` (see Existing pages).
2. **New page or segment.** A name with no wiki page gets a new page. A pipeline that is a segment of one with an existing page is added to that page (see Existing pages). Check by searching the wiki for the name and any alias before deciding.
3. **PDF titles.** Run `scripts/wiki_pdf_titles.py` for PDF refs not yet in `data/wiki_pdf_titles.json` and add titles. Scanned PDFs with no readable text show the full URL. A ref that does not load and has no archived copy goes in `data/wiki_unreadable_refs.json` with the reason; the generator leaves it off the page and the sheet keeps it.
4. **Background prose.** Write it by hand from `ResearcherNotes`, `DataCenterNotes` and the `[ref]` columns, with `{key}` placeholders that resolve to `_refs` citations. If none is written, the Background heading still appears; it holds only the dormancy sentence where one applies.
5. **Generate drafts** and read them. Check the map, refs, status wording, units.
6. **Pilot, then approval, then bulk publish**, throttled, with the live-text check on every edit.
7. **Report** what was posted (links) and what needs a person.

## New page layout

```
{{Navbar-Global Gas Infrastructure Tracker}}
'''Name''' is a {status} natural gas pipeline in the United States.<ref>
==Location==
The pipeline is proposed to run from X to Y.<ref>
{{#display_map: ... }}        (omit if there is no route)
==Project details==
==Background==                 (always present, even if empty)
==Articles and resources==
===References===
<references />
===Additional data===          (the Global Gas Infrastructure Tracker paragraph)
[[Category:Global Gas Infrastructure Tracker]]
[[Category:Gas and Hydrogen Pipelines]]
```

- **Lead.** "'''Name''' is a {status} natural gas pipeline in the United States" with a reference.
- **Background tense (Baird 2026-11-04).** Write Background in the past tense, or at least acknowledge the timeline. Something proposed, filed or approved is stated as having happened, with its date ("Dominion Energy North Carolina proposed the T-15 Reliability Project"). What the project would have done stays conditional ("would run", "would be regulated"). Never "plans to", "proposes" or "is now" without a date, because the source may be months old.
- **Construction wording (Baird 2026-11-04).** A construction-status pipeline is "a natural gas pipeline under construction", never "a construction natural gas pipeline". The generator's `new_page` does this.
- **Null route stubs.** A routes-repo geojson with `geometry: null` (142 bytes) means no route. Leave the map off.
- **Browser check limit.** `wiki_map_check.py` runs headless Chrome under the `GEMWIKI_USER_AGENT` identity; without it Cloudflare serves a challenge page and the check reads as `no map` or `CHALLENGED`. `scripts/wiki_save.py` checks every save through `action=parse` (`prop=text|headhtml`): a page with a map div must have `maps.googleapis.com` in its head. Never check with curl: a Cloudflare challenge page has no map div and reads as "0 with a map".
- **Location verb by status.** Proposed: "is proposed to run from X to Y". Construction: "is being built from X to Y" (Baird 2026-11-05: a pipeline under construction is not just proposed). Cancelled or shelved: "was proposed to run". Operating: "runs".
- **Project Details order.** Operator, Owner, Parent, Capacity, Length, Diameter, Status, Start year, Cost. Parent is the gas tab's Parent cell as the backend has it, with no ref; a cell reading `unknown [unknown %]` takes the parent of the same Owner cell on other rows, when there is exactly one (`parent_text`, `fill_unknown_parents`; Baird 2026-11-06). Parents stay the ownership team's research; the page only shows them. Keep original units. Costs are full units shown as "US$...".
- **Single segment vs several.** A page with one segment has no subheadings in Project Details or Background, and no "Main Line" label. "Main Line" and `===<SegmentName>===` headings appear only on pages with several segments.
- **Map.** `{{#display_map:|lines=lat, lon:lat, lon|center=|width=100%|height=400|type=map|zoom=}}`. Never a fixed pixel width: a map wider than a phone screen makes the whole page pan sideways on mobile (Baird 2026-11-06). Leave the map off if a pipeline has no route. Thin long routes to about 60 points. `type=map` and `type=normal` both render the same (ROADMAP), so the type is not what matters. **Purge the page after every save** (see below).
- **Map colors (Baird 2026-11-06).** Each line takes its status color from GEM's tracker maps on the website (the `color` block of `trackers/ggit/config.js` in `GlobalEnergyMonitor/maps`, branch `gitpages-production`, read only): gas operating red `#c74a48`, construction blue `#5c62cf`, proposed green `#4c9d4f`, everything else grey `#8f8f8e`. Oil follows `trackers/GOIT/config.js`, which differs (proposed blue, cancelled and mothballed green). The colors live in `build_wiki_pages.STATUS_COLORS`, shared by both builders; the route-shape pictures in the segment table use the same colors. A page with several segments gets a legend line right under the map: a colored square and the status for each status shown, with no lead-in words.
- **Section headings are sentence case (Baird 2026-11-06).** "Project details", "Articles and resources", "Additional data". `sentence_case_headings` lowercases the later words of a level-2 or level-3 heading only when every one is a generic word, so a name in a heading a person wrote ("Opposition From Sierra Club", a segment name) keeps its capitals.
- **A blank SegmentName on a page with several segments is "Main Line".**
- **Dormancy sentence.** The template sentence is used only for shelved-inferred or cancelled-inferred rows that have a year.

## References

- Cite web format: `{{Cite web|url=|title=|website=|access-date=2026-11-04}}` (use the real access date).
- **One citation per URL.** If a URL is used twice on a page, define it once as `<ref name="rXXXXXX">...</ref>` and reuse it as `<ref name="rXXXXXX" />`. The generator's `dedupe_refs` does this.
- **Define each acronym once.** Spell it out at its first use on the page with the acronym in parentheses, such as Federal Energy Regulatory Commission (FERC), then use the bare acronym everywhere after, in the Background and in every later section. Do not spell it out again.
- **Define every named ref where it is first used.** A `<ref name="x" />` with no `<ref name="x">...</ref>` anywhere on the page renders as a red cite error. After any wiki edit, check that every reused name has a definition (MEP lost six on 2026-11-06).
- **Titles are never the bare hostname (Baird 2026-11-05).** A ref with a known document title shows it. Every other ref, web pages included, shows its full URL as the title, so the reference list says which page it is.
- **PDF titles.** When a ref is a PDF, put the document's title in the reference, for example "Western Interstates 2026 Spring SAB Meeting, 23 April 2026". Federal Register PDFs are titled by volume, issue and date. Do not title a PDF from memory; read its first page.
- Every reference loads, names the pipeline and states the value (the main sweep rules apply).

## Existing pages (adding a segment)

1. Re-read the live page and save the original beside the draft (`.orig`).
2. Add each new segment under Project details with a `===<SegmentName>===` heading. Add its Background text under Background in the same way. Add a References section if the page has none.
3. **"Expansion projects" section.** If the page has one, move the projects under it into Project details (after the new segments) and remove the empty heading.
4. Share one `seen` set across the page so refs already on the page are reused, not repeated.
5. **Redraw the route map (Baird 2026-11-04).** The routes repo is usually newer than the map on the page. Redraw the page's first `{{#display_map:...}}` from the routes repo for every PID on the page: the new PIDs plus every sheet row whose Wiki URL is this page. Lines are thinned to 100 points each. If the page has no map, add one after the Location text. If none of those PIDs has a route, leave the page alone. Maps under a sub-project heading stay as they are. `update_map` in `build_wiki_pages.py` does this. The routes repo holds `FeatureCollection` files, bare `Feature` files (P7711, P7712, P7714, P7715, P7766, P7767) and 142-byte null stubs; `coords_of` reads all three and raises on a shape it cannot parse. A page whose PID has a non-null route must come out with a map (a bare `Feature` read as an empty collection left Shedgum-Riyadh 2 and five drafts without one, 2026-11-06).
6. Do not otherwise rewrite existing content.
   **Rebuild instead of appending (2026-11-05).** A page made by this workflow with one segment, edited only by the bot account since (check `page_revisions`), is regenerated as a multi-segment page when new segments arrive: `"rebuild": true` in scope.json, with the original PID under `keep_background` so its live Background text is kept word for word. The `.orig` is saved first as usual.
7. Post with a short edit summary. Confirm from the revision history that the base text was unchanged.

## Every save goes through `scripts/wiki_save.py`

A page saved through the API is cached WITHOUT the Google Maps script tag (the saved render shows `map_google3_2`, not `_1`). The browser then shows "Your browser is not compatible with Google Maps v3" even though the markup is correct and identical to working pages. A purge right after the save re-renders it with the script. So **every save, new page or edit, one page or a bulk run, goes through `wiki_save.save(s, title, text=..., summary=...)`**, which edits, purges (`forcelinkupdate`), and checks through `action=parse` that a mapped page's head carries `maps.googleapis.com`, purging again up to three times and raising `MapBroken` otherwise. Never call `gemwiki.edit_page` or post `action=edit` by hand; the PreToolUse hook `.claude/hooks/guard-wiki-save.py` blocks a shell command that does. Then confirm a pilot page in a real browser with `python scripts/wiki_map_check.py <url>` (headless Chrome via Playwright): the map text should read "Map / Satellite / ... Terms", not the "not compatible" message.

History: on 2026-11-05 about 100 US pages lost their maps to a wording script that skipped the purge; on 2026-11-06 Idku-Abu Hummus Gas Pipeline I and Kuraimat-Al Tebbin Gas Pipeline were posted with a hand-rolled `edit_page` call and broke the same way (Baird: "make sure this never happens again"). To find and fix pages saved without a purge, run `python scripts/wiki_save.py --check --since <YYYY-MM-DD> --purge` (`scripts/wiki_map_repair.py` is the older entry point and now uses the same API check). It scans every page the account saved since that date, purges each broken one and re-checks it.

## Pages with ten or more segments

A page with ten or more tracker rows is regenerated by `wiki/scripts/generate_pages.py` (not hand-built): its Project details is one sortable segment table with a tab strip (Route, Details, Timeline, Cost, Ownership, All columns), and the row label is "Segment" (Baird 2026-11-06). The tabs are CSS from `Template:Segment table/styles.css`; run `python wiki/scripts/generate_pages.py --push-styles` after changing `SEG_CSS` in the script, and never edit the template page by hand. The map click popup is styled the same way by `Template:Pipeline map/styles.css` (`MAP_CSS`, also pushed by `--push-styles`, included by the map block; Baird 2026-11-06). Generating writes nothing; upload the `shapes/` files, then save the `.txt` (minus its first two lines) through `wiki_save.save`. Check the tabs in a real browser the first time a page gets them (the 2026-11-06 Transco check clicked every tab with Playwright and read the visible headers and `scrollY`). The anchor divs are `position: fixed` so a tab click does not scroll the page; keep that rule. Its map is `width=100%`: the old fixed 600 px map made the page 615 px wide on a 390 px phone, so the page panned and jumped on tab taps (fixed 2026-11-06; check `document.documentElement.scrollWidth` equals `innerWidth` on an iPhone 13 profile in both Chrome and WebKit). The table has a Parent column next to Owner, read from the gas tab's Parent cell. Layout detail: `wiki/template/pipeline_page_template.md`, "Pages with ten or more segments".

## Checks before publishing

- **No repetition anywhere (Baird 2026-11-04).** Re-read the live page after posting and check for duplicate headings within a section, duplicate paragraphs and repeated sentences (Oasis got its whole Clint Export section twice). `insert_segments` skips a segment whose heading is already on the page, so a re-run is safe, but still read the result.
- Every page was saved through `scripts/wiki_save.py` (its map check passed), and a pilot page with a map passes `scripts/wiki_map_check.py` in a real browser.
- Background heading present.
- No duplicate citations; PDF refs titled.
- No GEM or banned URLs.
- Single-segment pages have no "Main Line".
- Existing pages: live text unchanged since the draft; Expansion projects folded in.
- Prose reads plainly (see deslop).

## Known limits

- US gas Backgrounds were drafted 2026-11-05 by cheaper-model agents (14 batches) and posted with `scripts/patch_wiki_backgrounds.py` (fills only empty Background bodies, re-reads live text first). Drafts: `batches/united-states-gas/wiki-drafts-20261104b/background_drafts_20261105.json`. Check before posting: every number and date in a sentence appears in the page it cites, and every ref loads and names the pipeline.
- Five scanned PDFs have no readable title and show their full URL.
- Run of 2026-11-06 (non-US gas scope, `work/wiki_new_2026-11-06/`): 139 new pages and 4 edited pages (South Valley, Guangxi, New Administrative Capital–Dahshur, Xinjiang) posted through `wiki_save.py`; 181 `Wiki` cells written (`notes/sheet-write-2026-11-06-wiki-urls-new-pages.csv`). Sumed Port (P8005) was held until its sheet row was settled, then posted the same day as Sumed Port Gas Import Pipeline: the petro-mag.org viewer ref hides the issue text, but the full-issue PDF linked from the viewer page (`/Uploads/Files/<id>.pdf`) carries it, and a GASCO report there states the 32 in, 6.1 km line and the 18 June 2025 gas-in (`notes/sheet-write-2026-11-06-p8005-settled.csv`). Xinjiang's tracker row (P7448) is the page's existing Gasification of Southern Xinjiang subsection, so its details went under that heading rather than a new segment; the builder's `_insert` fails on a page with no Background or Articles and resources heading, and that case is handled by hand.
