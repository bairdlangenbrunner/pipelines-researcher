# Subagent brief — China / Jiangxi gas deep sweep (§3 `deep`)

You research ONE batch file and write ONE shard. Read your batch payload at
`batches/batch_NN.json` (paths relative to this directory) and write
`shards/batch_NN.json`.

Repo root is four levels up from here. Run scripts as
`python3 <repo>/scripts/url_verifier.py <url> [expected...]`, or import
`from url_verifier import verify_url, surface_forms`.

## Standing rules — these override any instinct to be helpful

1. **NEVER cite GEM.** No `gem.wiki`, no `globalenergymonitor.org`, in any `[ref]` or note.
   You may READ the gem.wiki page (it is your starting point); you may never cite it.
   The whole point is to find what *independent* sources exist.
2. **NEVER fabricate a URL.** If you cannot verify one, describe the source in
   `researcher_notes` and mark the unit `UNRESOLVED`. A plausible-looking URL you did not
   fetch is the worst possible output.
3. **BANNED SOURCE: abarrelfull** (`abarrelfull.wikidot.com`, `abarrelfull.co.uk`) — never,
   in any output, not even alongside corroboration.
4. **2+ independent sources** is the target. Two outlets running the same wire story, or
   anything tracing to GEM, is ONE source. Record the tier: `high` = 2+ independent,
   `medium`/`low` = single, `inferred`/`presumed` = none verifiable.
5. **NEVER drop a once-working ref over an access failure.** Only a confirmed HTTP
   **404/410** may remove a ref. A 403, a `567`, a WAF page, a TLS error, a timeout, or a
   geo-block is an ACCESS FAILURE: keep the ref and ADD a Wayback capture alongside it.
6. **Never propose an applied edit to a route, and never write any live sheet.** Your output
   is staged JSON that a human reviews.

## What we already established — do not re-derive it

* All 18 rows share one wiki page: `Jiangxi_Natural_Gas_Pipeline_Network`, one `h3` per
  segment, each with field-labeled bullets carrying their own superscripts. Your payload
  already contains the wiki's stated value + the citation URL(s) + OUR verdict per unit.
* **Host reachability from here (measured 2026-08-26 — don't burn budget re-testing):**
  * `m.qcc.com` (企查查 registry — the citation behind most Operator/Owner units): WAF,
    intermittent, usually HTTP `567` + a Chinese block page. **ACCESS FAILURE, not dead.**
  * `nc.gov.cn`, `cx.jxgzwztb.com`: **NXDOMAIN** — the domain no longer resolves.
  * `jxgajc.com`, `strq.jxngh.com`: DNS resolves, all ports shut — server decommissioned.
  * `jndsb.jxnews.com.cn` TLS-fails; `zhaoqt.net` refuses; `gas.in-en.com` 403s;
    `skxox.com` serves a stub.
  * **Confirmed 404 (the only droppable class):** `m.xinhuanet.com/jx/2019-07/...`,
    `cnlng.com/bencandy.php?fid=2&id=19075`,
    `pipechina.com.cn/img/web/a5a6d9b8...xls`.
  * China at large IS reachable: baidu, sina, sohu, `gov.cn`, `jiangxi.gov.cn`,
    `wuning.gov.cn` all answer. So a Chinese-language search IS worth doing.
  * **`web.archive.org` is rate-limiting us right now.** Keep archive.org access SERIAL
    with a >=1.5s pause, and never fan it out. A burst of Wayback failures is a
    rate-limit signature, NOT link rot (sweep SOP).
* One wiki citation is `https://web.archive.org/save/...` — the Save-Page-Now INSTRUCTION
  endpoint, never evidence. Do not propose it. Cite
  `web.archive.org/web/<timestamp>/<url>` instead.

## Verification policy

Run `url_verifier` on **every** URL you propose. A `proposed_ref` must have a verification
that is `ok && contains_value`, with two documented exceptions you must apply as judgment:

* **STATUS is inferred, never matched literally.** A page describing the line carrying gas,
  being commissioned, or being expanded CONFIRMS `operating` though the word never appears.
* **A "value not found" on a large PDF or a stub/blocked body is not evidence.** Re-read the
  document (`pdftotext -layout`) before ruling against it.

Search in **Chinese** — 管道, 天然气, 输气管道, 全长, 管径, 输气能力, 总投资, 建成投产 — and
prefer Jiangxi provincial/municipal government, provincial DRC (发改委), and company
disclosures over news aggregators.

## Record contract — one object per owed unit, in `resolutions`

```json
{"project_id":"P4776","sheet_row":2667,"ref_col":"Status [ref]",
 "value_cols":["Status"],"values":{"Status":"operating"},
 "tab":"operators_owners",                     // ONLY for Operator/Owner units; else omit
 "proposed_refs":["https://..."],              // [] when unresolved
 "verifications":[{"url":"https://...","ok":true,"contains_value":true,
                   "note":"states 全长138公里"}],
 "class_out":"REFS_ADDED",                     // REFS_ADDED | CONFIRMED | UNRESOLVED | DEAD_LINK
 "tier":"high",                                // high | medium | low | inferred | presumed
 "researcher_notes":"..."}
```

Also emit, when you find them:

* **`FILL`** units — a sourced value for a BLANK cell. Same shape plus
  `"kind":"FILL","proposed_value":"138","value_col":"LengthKnown"`.
* **`__VALIDITY__`** sentinel — one per row where existence / duplication /
  classification is in question. `ref_col:"__VALIDITY__"`, `class_out:"UNRESOLVED"`,
  and put the reasoning in `researcher_notes`. These are the highest-value findings in
  the batch; the aggregate and romanization questions in `open_questions` belong here.
* **`__REDUNDANCY__`** sentinel — a suspected double-count between two named PIDs.

Shard file shape: `{"batch": NN, "resolutions": [ ... ]}`. Write it even if partly
unresolved — an honest `UNRESOLVED` with notes is a valid, useful result. But note the
calibration: **Jiangxi's citation base is 4.2% filled and its provenance is incremental
human research by two people, not a bulk load — so a blank usually means nobody looked
yet, and an UNRESOLVED here is a WEAK result, not the expected one.** Push on the sources.
