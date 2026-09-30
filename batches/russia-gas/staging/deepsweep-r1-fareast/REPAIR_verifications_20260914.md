# Repair pass: verification objects (R1 Far Eastern pilot, 2026-09-14)

## What went wrong
`merge_deepsweep_shards.py` keeps a proposed ref only when its verification object says
`ok: true` AND `contains_value: true` (`merge_qc.verified_refs`). Ten R1 shards wrote sourced
records whose verifications either do not exist (P3361, P6694) or carry `ok` without
`contains_value` (P3364, P3365, P4111, P6690, P6691, P6695, P6710, P2334 one record). The merge
stripped every ref on those records and downgraded ~110 of them to UNRESOLVED with a `[QC]`
note. The research was done; the encoding was not. `check_shard_coverage.py` now flags this
shape as UNMERGEABLE.

## The task (one agent per PID, repair only — no new research)
Repo: `/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher` (run everything from
there). Staging: `batches/russia-gas/staging/deepsweep-r1-fareast`. Shard:
`<staging>/rows/<PID>.json`. Start with
`python scripts/check_shard_coverage.py --staging <staging> --pid <PID>` — every `[UNMERGEABLE]`
line is one record to repair.

For EACH flagged `fills[]` record (class_out REFS_ADDED / REVERIFIED / DEAD_LINK with non-empty
`proposed_refs`), for EACH URL in `proposed_refs`, produce one verification object:

```json
{"url": "<exactly the proposed_refs string>", "ok": true|false, "status": 200,
 "contains_value": true|false, "name_found": true|false, "name_matched": "<string on the page>",
 "note": "<what the page states, quoted, and how you checked>"}
```

How to fill the flags — from EVIDENCE, never from the old note alone:
1. Run the verifier as a screen:
   `python scripts/url_verifier.py "<url>" "<token>" ["<token2>"] --name "<Cyrillic name>" --name "<English name>"`
   Tokens are the record's `values` in the form a Russian page prints them: decimal comma
   (`3,2`), `84 км`, `530 мм`, `1420`, a year `2024`, `млрд куб. м`, `млн куб. м в сутки`,
   an owner's Cyrillic name (`Сахатранснефтегаз`, `АЛРОСА-Газ`, `Газпром`). Try the natural
   forms; an `OK` on content = `contains_value: true`.
2. A verifier content FAIL is a screen result, not a verdict. Fetch the page yourself
   (`curl -sL --max-time 30 -A "Mozilla/5.0"`; `pdftotext -layout` for PDFs; a Wayback capture
   for a blocked host — `web.archive.org/web/<ts>/<url>`) and READ it. `contains_value: true`
   only if the page states the value for THIS pipeline — prose and unit equivalents count
   (`4,2 млн м3/сутки` supports 1.5 bcm/y with the conversion in the note; a date range
   supports a year; "в эксплуатации" supports operating). If you cannot read the document
   (an image with no OCR, a broken PDF) and cannot confirm the value another way, write
   `ok: true, contains_value: false` and say why. NEVER write true for a value you did not see.
   For an IMAGE (jpg/png table) use the Read tool on the downloaded file — it renders images —
   and quote the row you read.
3. `name_found: true` only when the page names this pipeline: its Cyrillic name, the segment
   name, an alias, or the endpoint-pair as a named line ("газопровод Мастах – Берге"). A page
   about only one terminus, the parent system, or a sibling string is `false`. Put the matched
   string in `name_matched`.
4. `ok` = the document resolved and you read it (200, or a readable Wayback capture). A 403/
   timeout you could not get around at all → `ok: false` with the status and what you tried.
5. Keep the existing note's substance (it records what the researcher saw); append your
   check. Keep `researcher_notes` intact.

Encoding rules that the pilot got wrong (fix these too when you meet them):
- `contains_value` means the page STATES the value in any equivalent form — NOT "the literal
  substring is present". "1,200 km" supports 1202 km (rounding, say so in the note);
  "7.5 million tonnes a year" supports 1071 MMcf/d (conversion, show it); "late 1960s"
  supports StartYear 1967. A verification whose note says the value is supported but whose
  flag says `false` is a defect: set it `true`.
- `ok` means YOU read the document. A verifier "name mismatch"/fuzzy-matcher FAIL on a
  Korean/Cyrillic page that you then read by hand is `ok: true` (with `status: 200`), not
  `ok: false`. `ok: false` is only for a document nobody could open.
- `null` is not a value for `contains_value` or `name_found`. Encode true or false.

Do NOT change `values`, `tier`, `independent`, `sheet_row`, `ref_col`, `value_cols`.
Two exceptions on `class_out` / `proposed_refs`:
- If after reading NO proposed ref states the value: set `class_out` to `"UNRESOLVED"`, set
  `proposed_refs` to `[]`, keep the `verifications` you wrote, and append to
  `researcher_notes`: `[repair 2026-09-14] <url> read: does not state <col>=<value>`.
- If the note says the source CONTRADICTS the sheet value (e.g. sources say 1967, record says
  2014): do not touch that record at all. List it in your summary; the orchestrator resolves
  it.

## Saving
Write the repaired record(s) to a JSON file (one object, or a list) and upsert:
`python scripts/shard_upsert.py --staging <staging> --pid <PID> --fill @/path/to/records.json`
The helper REPLACES the record with the same `ref_col` + `sheet_row` (so pass the FULL record,
all keys, not just verifications). Do not edit the shard file by hand. Upsert as you go, not at
the end.

## Finish
`python scripts/check_shard_coverage.py --staging <staging> --pid <PID>` must print no
`[UNMERGEABLE]` lines. Return a 4-line summary: records repaired; verification objects
written; how many `contains_value: true` / `false`; how many `name_found: true` / `false`;
anything you could not read.

## Cyrillic names (from the tracker; use these with `--name`)
- P3361 Kysyl-Syr – Mastakh III: "Кысыл-Сыр – Мастах", "СВ ГКМ-Мастах", "третья нитка", "3-я нитка"
- P6694 Mastakh–Yakutsk III: "Мастах-Берге-Якутск", "Средневилюйское ГКМ – Якутск", "Мастах – Якутск"
- P3364 Mastakh–Berge I: "Мастах-Берге", "1-ая нитка"
- P6691 Mastakh–Berge II: "Мастах-Берге", "2-ая нитка"
- P3365 Kysyl-Syr – Mastakh I: "СВ ГКМ-Мастах", "Кысыл-Сыр – Мастах"
- P6695 Kysyl-Syr – Mastakh II: "СВ ГКМ-Мастах", "Кысыл-Сыр – Мастах"
- P2334 Taas-Tumus – Yakutsk I: "Таас-Тумус-Якутск", "Таас-Тумус"
- P4111 Bolshoy Kamen – Vrangel: "Большой Камень", "Врангель"
- P6690 Zapadno-Ozernoye – Anadyr: "Западно-Озерное", "Анадырь"
- P6710 Srednetyungskoye – Nakyn: "Накынский поток", "Среднетюнгское", "Накын"
