# Subagent brief — China / Jiangxi gas deep sweep **v3** (§3 `deep` + `status-review`, run dir `deepsweep-20260903`)

Canonical template (2026-09-03), distilled from the Jiangxi v2 brief and MZ's four review
points. Copy it to `batches/<scope>/staging/<run>/BRIEF.md`, fill the `<…>` slots and the
**Measured conditions** block, and delete nothing from the rules sections — every rule here
exists because a delivered batch lacked it. `.claude/workflows/critical-deep-sweep.js` carries
the same contract for the one-subagent-per-PID path; `args.extra_brief` takes the scope block.

You research ONE ROW and write ONE shard. Read your payload at `batches/P####.json`
(relative to this directory) and write `shards/P####.json`. Repo root is 4 levels up
(`../../../..`). v3 carries v2 forward: your payload lists only what is still OWED on the row
(`work_order` gives the priority); everything under `already_sourced` / `carried_fills` is
settled context — reuse those documents, never redo them.
Verifier: `python3 <repo>/scripts/url_verifier.py <url> [expected…] --name "<pipeline name>"`,
or `from url_verifier import verify_url, surface_forms`.

## Standing rules — these override any instinct to be helpful

1. **NEVER cite GEM.** No `gem.wiki`, no `globalenergymonitor.org`, in any `[ref]` or note. Read
   the wiki page freely; never cite it. GEM's own route geometry can inform you but can never be
   a ref — a value knowable only from GEM's map is **uncitable, not unknown**.
2. **NEVER fabricate a URL.** Cannot verify one? Describe the source in `researcher_notes` and
   mark the unit `UNRESOLVED`. A plausible URL you did not fetch is the worst output.
3. **BANNED: abarrelfull** (`abarrelfull.wikidot.com`, `abarrelfull.co.uk`) and **theodora.com** —
   never, in any output, not even alongside corroboration.
4. **2+ independent sources** is the target for EVERY unit. Two outlets running one wire story,
   or anything tracing back to GEM, is ONE source. `high` = 2+ independent; `medium`/`low` =
   single; `inferred`/`presumed` = none verifiable. **`independent: true` means the rubric's
   ≥2-agreeing — NOT "independent of GEM".**
5. **NEVER drop a once-working ref over an access failure.** Only a confirmed HTTP **404/410**
   may remove a ref. 403 / 412 / 567 / WAF / CAPTCHA / TLS error / timeout / geo-block = ACCESS
   FAILURE — keep the ref, add a Wayback capture alongside if you can get one.
6. **Never propose a route edit and never write any live sheet.** Your output is staged JSON.
7. **Wikipedia IS citable** as ONE secondary source (two language editions = one source; an
   article whose own footnote is GEM cannot corroborate). Only GEM surfaces are banned.

## The four review rules — the difference between "found refs" and "did the research"

* **RELEVANCE — a ref must name THIS pipeline.** Pass `--name` on every verification; every
  verification object carries `name_found`. A page about terminus A, or terminus B, or the parent
  trunk is NOT a ref for the "A–B" row unless it names that segment (full name, or the
  `OtherLanguage*` name from the worklist). If the name is in another script and the verifier
  misses it, read the page and encode the hand-confirmed match as `name_found: true` with the
  matched string in `note`. Unnamed = capped at `low` at merge and listed by the gates.
* **EXHAUSTION — read every document you open for EVERY column and EVERY sibling row.** One
  approval notice sources Status, Length, Diameter, SegmentCost, Construction and Start at once:
  stage all of them (`REFS_ADDED` where the value is on the sheet, a `FILL` where it is blank).
  Then check the roster — a trunk page names its branches; a segment-I page states segment II's
  numbers — and write those into `cross_row_leads` naming the other PID. Findings do not
  propagate across a fan-out by themselves. Limit: a SYSTEM figure is never a ref for a SEGMENT
  cell (aggregate-vs-segment rule) — note it and file `__VALIDITY__` instead.
* **BLANKS ARE OWED.** Every `MISSING_VALUE` unit in your payload gets a `FILL` record: a sourced
  value with a paired verified ref, or `UNRESOLVED` with what you searched. Never force a number;
  never skip a blank silently. **Operating rows first.**
* **THE SECOND SOURCE IS OWED.** After the first source lands, search for a second from a
  different publisher AND a different document class (regulator approval ↔ operator disclosure ↔
  press ↔ EIA / acceptance notice). A single-source unit is fillable at `medium`, but its notes
  must say what you searched for the second and why none was found.

## The comprehensiveness bar

* **Source-diversity floor: no row ships with fewer than 2 distinct origin HOSTS** unless your
  notes say in prose why not.
* **A document already carrying much of this batch cannot be the second source** for a `high`.
  A plan and a restatement of the plan are ONE origin — `medium`, not `high`.
* **The harvest pool is a WORKLIST, not a lookup table.** `harvest_pool_live` holds URLs already
  screened live. **Report `harvest_opened`** — the count you actually opened. An unopened pool URL
  on a row with an owed cell is an open item, not a silent pass.
* **Original search is a separate obligation from candidate verification.** Do both; say in
  `researcher_notes` what you searched, not just what you found.
* **Findings do not propagate across a fan-out.** Before filing any `existence`, duplicate or
  "retire this row" concern, grep this run's other shards and payloads for the row's name and
  endpoints.

## The document ladder — search these classes, in this order

Search in **Chinese**: 管道, 天然气, 输气管道, 干线, 支线, 全长, 管径, 输气能力, 设计压力,
总投资, 建成投产, 核准, 批复, 竣工环境保护验收, 业主单位, 建设单位. Search on the segment's
endpoints joined (`丰城-抚州`, `丰城至抚州`) — `name_forms.segment` in your payload lists the forms.

1. **江西省能源局 / 省发改委 核准批复 and 核准变更批复** (`jiangxi.gov.cn/art/…`) — per-project
   approvals carrying length, diameter, investment, schedule, and the 建设单位 (Owner).
2. **环境影响评价 (EIA) 拟批准公示** and especially **竣工环境保护验收** — a completion
   environmental acceptance is close to dispositive for `operating`, and carries as-built
   lengths and 设计压力. Best class for the `status-review` leg and for Pressure.
3. **市/县 政务公开 + 人大代表建议答复** — municipal replies naming the segment and its schedule.
4. **招投标 / 中标公示 / 评标结果** — tender awards, which date construction starts.
5. **江西省天然气集团 / 江西省投资集团 disclosures and bond prospectuses** (SSE, CCXI, 中诚信) —
   NOTE the SSE tracking report already in the batch names the network only at SYSTEM level.
6. **PipeChina (国家管网) / CNPC / Sinopec project and commissioning disclosures** — the ladder
   for the NATIONAL TRUNK rows (P4657, P4934, P4947); the provincial DRC plan does not serve them.
7. **江西省能源发展"十四五"规划 / 统计年鉴** — programme-level totals (system-level only).

## Measured conditions — 2026-09-04, do not burn budget re-testing

* Harvest pool screened this morning: **111 live / 76 failed of 187; 26 confirmed 404/410**
  (the rest are access failures). Your payload separates them (`harvest_pool_live` /
  `harvest_pool_failed`); 18 Save-Page-Now citation forms were resolved to their origins
  (`spn_origins`) — cite the ORIGIN or a real `/web/<ts>/` capture, never the `/save/` URL.
* **Two v2 documents are CONFIRMED DEAD** and their 17 units were demoted to `UNRESOLVED` with the
  old evidence attached (`owed_ref_units[].prior_evidence`): `trqi.sinopec.com/trqi/cqds/jcxx/
  20191205/news_20191205_840069053975.shtml` (HTTP 404; host moved to `/trqi/`; no Wayback
  capture) and `thepaper.cn/newsDetail_forward_1543492` (404 at the page AND at
  `api.thepaper.cn/contentapi/contentdetail/1543492`; no capture). Find the relocated Sinopec
  天然气分公司 disclosure or another source; if you find a live page, archive it via
  `https://web.archive.org/save/<url>` (path form; verify the 302 target) before citing.
* `m.qcc.com` (企查查): WAF HTTP `567` — **access failure, not dead**. `gas.in-en.com` 403 ·
  `fgw.hubei.gov.cn`, `sthjt.hubei.gov.cn`, `cnpc.com.cn` `412` (WAF precondition) ·
  `reuters.com` 401 · `bidcenter.com.cn` HTTP-200 CAPTCHA interstitial (the verifier catches it) ·
  `baike.baidu.com` 403 · `hraes.cn`, `jxgajc.com`, `cx.jxgzwztb.com`, `hps.mee.gov.cn`
  connection failures · `gov.cn`/`ndrc.gov.cn`/`xinhuanet` old paths 404 (check Wayback).
* **`web.archive.org` is HEALTHY today** (availability API and capture fetches answer in ~2 s).
  Still keep Wayback access SERIAL with a ≥2 s pause; a `429` is a rate-limit signature, retry,
  never link rot.
* China at large IS reachable: baidu, sina, sohu, `gov.cn`, `jiangxi.gov.cn`. Chinese search works.
* **PDFs:** `url_verifier` now extracts PDF text (pypdf → `pdftotext`), so `--name`/value checks
  work on PDFs; a "200 PDF but no text could be extracted" result means read it with
  `pdftotext -layout` yourself, not that the value is absent.
* **`www.quannan.gov.cn` answers `403` over IPv6 and `200` over IPv4** — the morning screen and
  the v2 carry saw the 403. Use `curl -4`; in Python force IPv4
  (`urllib3.util.connection.allowed_gai_family = lambda: socket.AF_INET`). Its 2024 PDF is the
  Jiangxi Natural Gas Group pipeline company's emergency plan for the four Ganzhou-south branches
  (321 pp; local text + digest in your payload) — an OPERATOR disclosure, live. Its 2021 page
  `t20210830_2028305.shtml` is a **SOFT 404**: 200 with the county homepage, no article, no
  Wayback capture — not citable; the unit it carried (P4787) needs a new source.
* **Suspected soft 404?** Prove it: fetch a nonsense sibling slug and diff the bodies.

## Verification policy

Run the verifier on **every** URL you propose, with `--name`. A `proposed_ref` needs a
verification that is `ok && contains_value`, with documented exceptions you apply as judgment:

* **STATUS is inferred, never matched literally.** A page describing the line carrying gas, being
  commissioned or expanded CONFIRMS `operating` though the word never appears.
* **"value not found" on a large PDF, a CJK PDF, or a blocked body is not evidence.** Re-read it
  (`pdftotext -layout`) before ruling against it. A report is not "unsupported" until its MAPS
  have been read, not just its text.
* **Encode a hand-confirmed false negative as `ok: true, contains_value: true`** (and
  `name_found: true` where you confirmed the name) with the evidence in `note`. Prose inside an
  `ok: false` record is STRIPPED downstream and the unit is honestly downgraded to `UNRESOLVED`.

## Calibration for this scope

**Jiangxi's citation base is 3.7% filled and its provenance is incremental human research,
not a bulk load — a blank means nobody looked yet. An `UNRESOLVED` here is a WEAK result, not
the expected one.** Push on the sources. **241 blank cells are OWED this run** (`owed_fills`;
171 on operating rows) — the fill order is Length → Diameter → Capacity → Start → Construction
→ SegmentCost → Owner → FuelSource → Pressure. Pressure is owed but low-yield unless an EIA
states 设计压力 — do not force it.

**Exhaustion assignments (read FIRST, before any new search).** Your payload's
`dominant_documents` lists the v2 documents that already serve this row or its wiki family,
with what is known about each. Read each once for EVERY column of this row and file sibling
facts as `cross_row_leads`. Known yields: the Sina 2011 article staged on P4776 states P4777's
Length 825 km / SegmentCost 3.1 bn RMB / Construction Oct 2008 (MZ's example — stage it on
P4777); the qianzhan DRC-plan PDF lists grid segments with length/diameter/schedule (ONE origin;
huaon restates it — same origin); the SSE tracking report names the network only at system
level (Phase I/II totals) and cannot name a segment — for segment rows it is at most the
system-operator context beside a segment-naming source; the quannan 2024 emergency plan names
the four Ganzhou-south branches (赣州南支线 信丰-瑞金段 340.3 km · 龙南-全南段 56.7 km ·
会昌-寻乌段 97.5 km, DN250/400/450, 设计压力) — read its `digest` for P4785–P4788 and route
what it says about any other row. Every document in `documents_naming_this_row` is one you
MUST open for this row.

**Relevance re-reads.** `relevance_rereads` lists carried refs whose name check came back
`unnamed` / `system-only` / `unchecked` (each entry carries a `task`). A ref that names only
the parent trunk (西气东输三线, 川气东送, 江西省天然气管网) is NOT a ref for the "A–B" row:
find the segment-naming source, or say in prose why a system-level source is the right
evidence for THAT cell (e.g. one integrated network operator for `Operator`) — the merge caps
such units at `low` unless the notes carry that reasoning.

The three **national trunk parents** (P4657, P4934, P4947) are trunk rows — for them a
system-level name IS the row's name (`name_forms.trunk: true`). A spec sourced for a MAINLINE
does not source a SECTION, and vice versa — the aggregate-vs-segment rule; when a source gives
a system figure for a segment cell, say so and file `__VALIDITY__`, don't stage the figure.
Owner/Operator units go on the operators/owners tab (`"tab": "operators_owners"`).

## Record contract — one object per owed unit, in `resolutions`

```json
{"project_id":"P####","sheet_row":0,"ref_col":"Status [ref]",
 "value_cols":["Status"],"values":{"Status":"operating"},
 "tab":"operators_owners",                     // ONLY for Operator/Owner units; else omit
 "proposed_refs":["https://…"],                // [] when unresolved
 "verifications":[{"url":"https://…","ok":true,"contains_value":true,"name_found":true,
                   "note":"the phrase on the page that states the value AND names the line"}],
 "class_out":"REFS_ADDED",                     // REFS_ADDED | REVERIFIED | UNRESOLVED | DEAD_LINK
                                               // EXACTLY these four; anything else is DROPPED
                                               // silently by build_ref_workbook. "CONFIRMED" is
                                               // valid ONLY on a __VALIDITY__/__REDUNDANCY__/
                                               // __STATUS__ sentinel.
 "tier":"high",                                // high | medium | low | inferred | presumed
 "independent":true,                           // ≥2 AGREEING independent sources — rule 4
 "researcher_notes":"what you searched (incl. for the 2nd source), what you found, what you rejected and why, which OTHER cells/rows this document served"}
```

Also emit:

* **`FILL`** — one per `MISSING_VALUE` unit in your payload (owed): same shape plus
  `"kind":"FILL","proposed_value":"…","value_col":"<col>"`; `class_out: UNRESOLVED` with notes when
  not found. **Expansion with no new physical pipe → `LengthKnown = 0`, `Diameter` blank.**
* **`__VALIDITY__`** — one per row where existence / duplication / classification is in question.
  Never recommend deleting a row off obscurity alone.
* **`__REDUNDANCY__`** — a suspected double count between two named PIDs.
* **`__STATUS__`** — required for every non-`operating` row in your payload when the
  `status-review` leg is on; verdict in `researcher_notes`: `confirm` / `change` (name the new
  status) / `stale` / `unclear`.

Controlled vocabulary is LOCKED and lowercase: `Status`, `RouteAccuracy`, `PipelineType`,
`DelayType`, `ShelvedCancelledType`, `Delayed`, `Opposition`. Only `FIDStatus` is capitalized
(`Pre-FID`, `FID`). `*CostUnits` is a bare currency code — magnitude goes in the number.

## Shard shape

`{"batch": "P####", "harvest_opened": N, "resolutions": [ … ],
  "cross_row_leads": [{"project_id":"P####","url":"https://…","facts":"…"}]}`

`harvest_opened` is an integer (the count of pool URLs you actually opened). Write the shard to
`shards/P####.json` with `json.dump(..., ensure_ascii=False)`.

Write it even if partly unresolved — an honest `UNRESOLVED` with notes is a valid result.
**No orphan refs in either direction.**
