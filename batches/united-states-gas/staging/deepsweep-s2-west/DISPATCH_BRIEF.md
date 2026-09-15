# Deep-sweep dispatch brief (read this in full before researching)

You are researching **one row** of a US gas deep sweep. Three documents govern you:

1. `prompts/<PID>.md` in this staging dir — your row's self-contained brief: its inputs,
   the full 42-row batch roster (for duplicate detection), the shard schema, the finish gate.
2. `ADDENDUM.md` in this staging dir — the rules this slice's defects taught. Read every
   section; several exist because an agent on an earlier row got exactly this wrong.
3. This file.

Read all three **in full** before your first search.

## TIER DISCIPLINE — the dominant defect class in this slice

`tier: "high"` and `independent: true` require **2+ distinct publishers**, counted over refs
that actually verify the value (`ok: true` AND `contains_value: true`). These each count as
**ONE origin**:

- every EIA release, all of them together (Jan2021 + Aug2026 + any other = one origin);
- multiple EDGAR filings by one filer;
- multiple Federal Register / govinfo notices;
- multiple documents in one FERC docket;
- multiple PHMSA documents;
- multiple RCA (or any single state-PUC) filings;
- an agency page **plus** an applicant document that agency hosts in the same record;
- multiple Wayback captures of the same site;
- our own geojson measurement — which never counts as a publisher at all.

If nothing verifies, the record is `tier: "low"`, `independent: false`, `proposed_refs: []`.

### A `validity` record's tier is counted over its OWN `proposed_refs`

This is the single most-repeated defect in the slice, so it gets its own heading. A `validity`
record carries **no `verifications`** by repo convention — the schema block has no place for
them. So there is nothing else its tier can be counted over: **the publishers behind its
`proposed_refs` list ARE its evidence.** Which means:

| what you wrote | what it says | verdict |
|---|---|---|
| `tier: "high"`, `proposed_refs: []` | "two independent publishers agree", backed by zero URLs | **contradiction — always wrong** |
| `independent: true`, `proposed_refs: []` | "independent of" nothing | **contradiction — always wrong** |
| `tier: "high"`, one publisher (or two URLs from one origin) | overclaimed by one publisher | wrong — it is `medium` |
| `tier: "low"`, `independent: false`, `proposed_refs: []` | "I found nothing; here is what I searched" | **correct**, and a perfectly good finding |

A validity record with an empty `proposed_refs` list is **normal and often right** — an existence
concern, a duplicate suspicion, or a negative finding legitimately proposes no URL. What is never
right is pairing that empty list with a tier that claims corroboration. The strength of the
*writing* is not the tier; the tier is an arithmetic fact about the list directly above it. Count
the distinct publishers in `proposed_refs`, apply the one-origin table above, and write that
number's tier — 0 or 1 → `medium` at best and `independent: false`, 2+ → `high` is available.

Hit four times in slice 2 (P7863, P5101, P7782 and one earlier) and invisible to the coverage
gate, which is why the finish gate below now runs a second script.

Corollary, same root: **do not stage a URL in `proposed_refs` that your own finding is
rejecting.** A negative finding ("this page supports nothing") proposes nothing — name the URL
in the prose and leave the list empty.

## OTHER STANDING RULES

- **Never cite GEM** — no `gem.wiki`, no `globalenergymonitor.org`, in any `proposed_refs`,
  verification `url`, or `cross_row_leads[].url`. (Naming gem.wiki in prose to say what a
  carried citation claims is fine; a GEM URL in a ref field is not.)
- **Never fabricate a URL.** Every URL goes through
  `python3 scripts/url_verifier.py <url> --name "<pipeline name>"` — one URL per invocation;
  extra positional args are expected substrings. Known false negative: a bare numeric
  substring like `1961` fails when the prose writes `1961,`.
- **Banned hosts:** `abarrelfull.wikidot.com`, `abarrelfull.co.uk`, `theodora.com`, `yingdodo.com`.
- **EIA URL convention:** `https://www.eia.gov/naturalgas/pipelines/EIA-NaturalGasPipelineProjects_<Mon><Year>.xlsx`
  — underscore for every release **except Aug 2026**, which is
  `EIA-NaturalGasPipelineProjectsAug2026.xlsx`. Never cite the undated
  `EIA-NaturalGasPipelineProjects.xlsx` or the `data.php` navigation page. Cite the dated
  release + sheet name + Excel row in the note. 29 dated workbooks are cached locally under
  `sources/eia_pipeline_projects/raw/`.
- **The EIA `Historical Projects (1996-2024)` sheet** has its header at Excel row 2, columns in
  this order: `Last Updated Date, Project Name, Pipeline Operator Name, Project Type, Status,
  Completed Date, Year In Service Date, State(s), Beg_State, End_State, Region(s), Beg_Region,
  End_Region, Thru_Region, Cost (millions), Miles, Additional Capacity (MMcf/d), Pipeline
  Diameter (Inches), Pipeline Type, Authority, Docket Number, Crosses State Border, Project
  Notes, Demand Served, Website`. **Cost and Miles are adjacent** — that misread has already
  happened twice in this slice. And **EIA carries PROJECTS, never whole systems**: an EIA
  "Miles" figure is the new-construction component, not a system total.
- **`*CostUnits` is a bare currency code** (`USD`), never "USD millions" — magnitude goes in
  the number.
- **Rule 4(e):** every MISSING_REF unit ends `REFS_ADDED` or `UNRESOLVED`-with-notes.
  `UNRESOLVED` means *nothing was found* — never "something slightly different was found",
  never "not looked for". A source agreeing within rounding IS a ref (medium/high, with the
  discrepancy noted). A *different-scope* figure (system total vs per-segment; per-docket cost
  vs whole-system cost) IS genuinely "nothing found".
- **Oil is out of scope for this whole cycle.** Never fold it in, never propose it. If a row
  looks like it belongs in the oil tracker, say so in the notes and escalate — do not research it.
- **A blocked fetch is a tooling failure, never evidence about the target.** Escalate:
  `curl -sL --compressed` with a browser UA → retry → other host form → Wayback
  (`http://archive.org/wayback/available?url=…`, then FETCH the capture) → PDFs via
  `curl -o` + `pdftotext -layout`. Only after that may you call something unreachable, and
  then you say the actual status code and byte count. See the ADDENDUM section
  "**\"Blocked\" is a claim you must be able to reproduce**" — two false blocked-source claims
  were already caught in this slice.
- **`timeout` is not installed on this machine** — call `python3` directly.

## Two defect shapes caught on earlier rows — do not repeat them

- **The reused verification.** One "search record" verification block copied across several
  units with `contains_value: true`, while those units were correctly `UNRESOLVED`. The page
  named the pipeline and stated *some* facts, so it looked verified — but it carried no field
  for *that unit's* value. A page that does not state your unit's value is a search record:
  `contains_value: false`, every time.
- **The self-contradicting validity record.** A record whose whole finding was that a URL
  supports nothing, with that URL sitting in `proposed_refs` at `tier: "high"`. A negative
  finding proposes nothing: name the URL in the prose, leave `proposed_refs` empty.

## FINISH GATE (blocking — do not report done until BOTH print clean)

```
python3 scripts/check_shard_coverage.py --staging <this staging dir> --pid <PID>
python3 scripts/audit_shard.py <this staging dir>/rows/<PID>.json
```

Run both from the repo root. They check different things and neither subsumes the other:

- `check_shard_coverage.py` — "is every owed unit accounted for, and will it merge?" If it names
  an `[UNMERGEABLE]` record, the research is done — re-key the record, do not redo the research.
- `audit_shard.py` — "is what you wrote true to your own evidence?" Tier vs distinct publishers
  (the section above), standing rule 1, banned hosts, the EIA URL convention, `UNRESOLVED`
  discipline, lowercase controlled vocab. It exits non-zero on findings and prints nothing but
  findings under `--quiet`. Every line it prints is a defect in the shard, not a false positive
  to argue with — the two carve-outs it already knows about are that a Wayback capture counts as
  its origin's publisher and that two EDGAR filings by two different registrants are two origins.
