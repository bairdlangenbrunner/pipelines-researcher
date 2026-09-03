# Subagent brief — `<Country>` / `<scope>` `<commodity>` deep sweep (§3 `deep`[ + `status-review`])

Canonical template (2026-09-03), distilled from the Jiangxi v2 brief and MZ's four review
points. Copy it to `batches/<scope>/staging/<run>/BRIEF.md`, fill the `<…>` slots and the
**Measured conditions** block, and delete nothing from the rules sections — every rule here
exists because a delivered batch lacked it. `.claude/workflows/critical-deep-sweep.js` carries
the same contract for the one-subagent-per-PID path; `args.extra_brief` takes the scope block.

You research ONE batch and write ONE shard. Read your payload at `batches/batch_NN.json`
(relative to this directory) and write `shards/batch_NN.json`. Repo root is `<N>` levels up.
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

## The document ladder — `<scope-specific: source classes in priority order, in the country's language(s)>`

`<e.g. regulator approvals → EIA / completion-acceptance notices → municipal disclosures →
tender awards → operator bond prospectuses / annual reports → national-operator commissioning
notices → programme-level plans / statistical yearbooks. List the search vocabulary.>`

## Measured conditions — `<date>`, do not burn budget re-testing

`<Harvest pool screen: N live / N failed / N confirmed 404. Per-host access failures (WAF,
CAPTCHA-200s, NXDOMAIN, TLS). Wayback health today. What IS reachable. Soft-404 sections and how
to prove one (fetch a nonsense sibling slug, diff the bodies).>`

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

`<Citation base %, provenance (bulk load vs incremental research), and therefore whether an
UNRESOLVED is the expected outcome (Pakistan) or an unfinished one (India, Jiangxi). Name the
parent-trunk rows and restate the aggregate-vs-segment rule for them.>`

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

`{"batch": NN, "harvest_opened": N, "resolutions": [ … ],
  "cross_row_leads": [{"project_id":"P####","url":"https://…","facts":"…"}]}`

Write it even if partly unresolved — an honest `UNRESOLVED` with notes is a valid result.
**No orphan refs in either direction.**
