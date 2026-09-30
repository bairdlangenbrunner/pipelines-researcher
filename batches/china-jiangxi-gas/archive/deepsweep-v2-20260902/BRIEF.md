# Subagent brief — China / Jiangxi gas deep sweep **v2** (§3 `deep` + `status-review`)

You research ONE batch and write ONE shard. Read your payload at
`batches/batch_NN.json` (relative to this directory) and write `shards/batch_NN.json`.

Repo root is four levels up. Run `python3 <repo>/scripts/url_verifier.py <url> [expected…]`,
or `from url_verifier import verify_url, surface_forms`.

**This is the SECOND pass on this scope.** The first (2026-08-26) was judged not
comprehensive enough, and the diagnosis was specific: it verified a small closed set of
wiki-supplied candidate URLs instead of searching for new sources. **Your payload's
candidate lists are a FLOOR to clear, not a ceiling to verify.** A shard that only
confirms what the wiki already cited has repeated the failure.

## Standing rules — these override any instinct to be helpful

1. **NEVER cite GEM.** No `gem.wiki`, no `globalenergymonitor.org`, in any `[ref]` or note.
   Read the wiki page freely; never cite it. The point is to find what *independent*
   sources exist. This also means GEM's own route geometry can inform you but can never
   be a ref — a value knowable only from GEM's map is **uncitable, not unknown**.
2. **NEVER fabricate a URL.** Cannot verify one? Describe the source in `researcher_notes`
   and mark the unit `UNRESOLVED`. A plausible URL you did not fetch is the worst output.
3. **BANNED SOURCE: abarrelfull** (`abarrelfull.wikidot.com`, `abarrelfull.co.uk`) — never,
   in any output, not even alongside corroboration.
4. **2+ independent sources** is the target. Two outlets running one wire story, or anything
   tracing back to GEM, is ONE source. `high` = 2+ independent; `medium`/`low` = single;
   `inferred`/`presumed` = none verifiable. **`independent: true` means the rubric's
   ≥2-agreeing — NOT "independent of GEM".** Setting it true on a single-source unit is a
   defect; it renders as the yes/no column a researcher trusts when deciding to paste.
5. **NEVER drop a once-working ref over an access failure.** Only a confirmed HTTP
   **404/410** may remove a ref. A 403, a `567`, a `412`, a WAF/CAPTCHA page, a TLS error,
   a timeout or a geo-block is an ACCESS FAILURE — keep the ref, add a Wayback capture
   alongside it if you can get one.
6. **Never propose a route edit and never write any live sheet.** Your output is staged JSON.
7. **Wikipedia IS citable** (policy settled 2026-08-27); only *GEM* surfaces are banned. Treat
   it as ONE secondary source; two language editions of one article are still one source; an
   article whose own footnote is GEM cannot corroborate.

## The comprehensiveness bar — this is what makes v2 different

* **Source-diversity floor: no row ships with fewer than 2 distinct origin HOSTS** unless
  your notes say in prose why not. v1 failed this on 4 of 18 rows.
* **A document already carrying a lot of this batch cannot be the second source.** Three
  documents carried 71 of v1's 98 units. If your only two refs for a unit are the Jiangxi
  DRC plan and a restatement of it, that is ONE origin — tier `medium`, not `high`.
* **The harvest pool is a WORKLIST, not a lookup table.** `harvest_pool_live` holds URLs
  already screened live (v1 left 18 readable ones unopened). **Report `harvest_opened`: the
  count you actually opened.** An unopened pool URL on a row with an owed cell is an open
  item, not a silent pass.
* **Original search is a separate obligation from candidate verification.** Do both. Say in
  `researcher_notes` what you searched, not just what you found.
* **Findings do not propagate across a fan-out.** Before you file any `existence`,
  duplicate or "retire this row" concern, grep this run's other shards and payloads for the
  row's name and endpoints. Two Egypt agents recommended destroying real rows because each
  had tested the wrong document while a sibling was reading the right one.

## The document ladder — search these classes, in this order

Search in **Chinese**: 管道, 天然气, 输气管道, 干线, 支线, 全长, 管径, 输气能力, 设计压力,
总投资, 建成投产, 核准, 批复, 竣工环境保护验收.

1. **江西省能源局 / 省发改委 核准批复 and 核准变更批复** (`jiangxi.gov.cn/art/…`) — per-project
   approvals carrying length, diameter, investment, schedule. Two are already in your pool.
2. **环境影响评价 (EIA) 拟批准公示** and especially **竣工环境保护验收** — a completion
   environmental acceptance is close to dispositive for `operating`, and carries as-built
   lengths. This is the single best source class for the `status-review` leg.
3. **市/县 政务公开 + 人大代表建议答复** — municipal replies naming the segment and its schedule.
4. **招投标 / 中标公示 / 评标结果** — tender awards, which date construction starts.
5. **江西省天然气集团 / 江西省投资集团 disclosures and bond prospectuses** (SSE, CCXI, 中诚信).
6. **PipeChina (国家管网) / CNPC / Sinopec project and commissioning disclosures** — this is
   the ladder for the NATIONAL TRUNK rows; the provincial DRC plan does not serve them.
7. **江西省能源发展"十四五"规划 / 统计年鉴** — programme-level totals.

## Measured conditions — 2026-09-02, do not burn budget re-testing

* Harvest pool screened this morning: **100 live / 87 failed of 187**, and only **22 are
  confirmed 404** — the rest are access failures. Your payload separates them.
* `m.qcc.com` (企查查, the citation behind most Operator/Owner units): WAF, HTTP `567`.
  **Access failure, not dead.**
* `gas.in-en.com` 403 · `fgw.hubei.gov.cn` and `cnpc.com.cn` return `412` (WAF precondition)
  · `reuters.com` 401 bot-wall · `bidcenter.com.cn` and `jdzmc.com` serve HTTP-200
  **CAPTCHA interstitials** (`人机验证` / `请输入验证码`) — `url_verifier` now catches these;
  a 200 is not automatically a page.
* `nc.gov.cn`, `cx.jxgzwztb.com` NXDOMAIN · `jxgajc.com`, `strq.jxngh.com` ports shut.
* **`web.archive.org` is degraded today**: the availability API (`archive.org/wayback/
  available`) answers in ~5 s, but capture fetches return `429` or time out. So snapshot
  **existence is provable and content often is not.** Keep Wayback access SERIAL with a
  ≥2 s pause, never fan it out, and never record a capture as read when you only proved it
  exists. A burst of Wayback failures is a rate-limit signature, NOT link rot.
* China at large IS reachable: baidu, sina, sohu, `gov.cn`, `jiangxi.gov.cn`. Chinese-language
  search works — do it.
* **Suspected soft 404?** Prove it: fetch a nonsense sibling slug and diff the bodies. Some
  Chinese CMS sections return 200 + a shell for any slug.

## Verification policy

Run `url_verifier` on **every** URL you propose. A `proposed_ref` needs a verification that
is `ok && contains_value`, with documented exceptions you apply as judgment:

* **STATUS is inferred, never matched literally.** A page describing the line carrying gas,
  being commissioned or expanded CONFIRMS `operating` though the word never appears.
* **"value not found" on a large PDF, a CJK PDF, or a blocked body is not evidence.**
  Re-read it (`pdftotext -layout`) before ruling against it.
* **A report cited for a pipeline is not "unsupported" until its MAPS have been read**, not
  just its text.
* **Encode a hand-confirmed false negative as `ok: true, contains_value: true` with the
  evidence in `note`.** Prose inside an `ok: false` record is STRIPPED downstream and the
  unit is then honestly downgraded to `UNRESOLVED` — so found evidence reports as *no
  source found*. This cost v1 eleven records.

## Calibration for this scope

**Jiangxi's citation base is 3.7% filled and its provenance is incremental human research,
not a bulk load — so a blank means nobody looked yet. An `UNRESOLVED` here is a WEAK
result, not the expected one.** (Contrast Pakistan, where a bulk-loaded cohort made
`UNRESOLVED` correct.) Push on the sources.

The three **national trunk parents** (P4657, P4934, P4947) carry ZERO refs on every column
and have never been swept. A spec sourced for a MAINLINE does not source a SECTION, and
vice versa — that is the aggregate-vs-segment rule, and violating it is how double counts
get created. When a source gives you a system-level figure for a segment-level cell, say so
and file a `__VALIDITY__`, don't stage the figure.

## Record contract — one object per owed unit, in `resolutions`

```json
{"project_id":"P4776","sheet_row":2665,"ref_col":"Status [ref]",
 "value_cols":["Status"],"values":{"Status":"operating"},
 "tab":"operators_owners",                     // ONLY for Operator/Owner units; else omit
 "proposed_refs":["https://…"],                // [] when unresolved
 "verifications":[{"url":"https://…","ok":true,"contains_value":true,
                   "note":"states 全长138公里"}],
 "class_out":"REFS_ADDED",                     // REFS_ADDED | REVERIFIED | UNRESOLVED | DEAD_LINK
                                               // ^ EXACTLY these four. build_ref_workbook
                                               // buckets on this list and DROPS anything
                                               // else SILENTLY -- "CONFIRMED" is NOT a ref
                                               // class and loses the record. Use REFS_ADDED
                                               // when the cell gains a ref (incl. an empty
                                               // cell you filled), REVERIFIED when an
                                               // existing ref still stands unchanged.
                                               // "CONFIRMED" is valid ONLY on a __VALIDITY__
                                               // /__REDUNDANCY__/__STATUS__ sentinel.
 "tier":"high",                                // high | medium | low | inferred | presumed
 "independent":true,                           // ≥2 AGREEING independent sources — see rule 4
 "researcher_notes":"what you searched, what you found, what you rejected and why"}
```

Also emit, when you find them:

* **`FILL`** — a sourced value for a BLANK cell: same shape plus
  `"kind":"FILL","proposed_value":"138","value_col":"LengthKnown"`. Rows flagged
  `length_is_blank` in your payload are prime candidates. **Expansion with no new physical
  pipe → `LengthKnown = 0`, `Diameter` blank.**
* **`__VALIDITY__`** — one per row where existence / duplication / classification is in
  question. `ref_col:"__VALIDITY__"`, reasoning in `researcher_notes`. Highest-value output
  in the batch. Never recommend deleting a row off obscurity alone.
* **`__REDUNDANCY__`** — a suspected double count between two named PIDs.
* **`__STATUS__`** — **required for every non-`operating` row in your payload** (the
  status-review leg). `ref_col:"__STATUS__"`, and put a verdict in `researcher_notes`:
  `confirm` (status still right) / `change` (name the new status) / `stale` (nobody has
  checked and the evidence is old) / `unclear`. Several of these rows are `construction`
  branches last verified in 2024 on ~60 km lines that commission in 18–24 months — a
  `stale` verdict with the evidence is a real finding.

Controlled vocabulary is LOCKED and lowercase: `Status`, `RouteAccuracy`, `PipelineType`,
`DelayType`, `ShelvedCancelledType`, `Delayed`, `Opposition`. Only `FIDStatus` is
capitalized (`Pre-FID`, `FID`). `*CostUnits` is a bare currency code (`CNY`), never
"CNY million" — magnitude goes in the number.

## Shard shape

`{"batch": NN, "harvest_opened": N, "resolutions": [ … ]}`

Write it even if partly unresolved — an honest `UNRESOLVED` with notes is a valid result.
**No orphan refs in either direction**: never a `[ref]` without a paired value, never a
researched value without a `[ref]`.
