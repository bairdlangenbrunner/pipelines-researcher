# Dispatch addendum — US gas slice 2 (read this together with your row prompt)

## The FILL rule (rule 4(e), non-negotiable)

A sourced value for a cell the sheet leaves BLANK is a **FILL** —
`class_out="REFS_ADDED"` carrying the new value in `values`. It is NEVER
`UNRESOLVED`. `UNRESOLVED` means **nothing was found**; it never means something
was found and you declined to stage it. If you write a value or a number into
`researcher_notes` or into `summary`, that value belongs in `values` with
`class_out="REFS_ADDED"`.

Likewise, a source that agrees within rounding, or that disagrees but is credible,
is a **ref**: stage `REFS_ADDED` with the sheet's value retained (or the sourced
value if it is clearly better), and note the delta. A 3% length difference is a
ref with a noted delta, not an `UNRESOLVED`.

Do not withhold an Operator/Owner value "because it belongs on another tab" — the
worklist joins that tab; stage it here.

## Source ladder for US interstate gas systems — work it in this order

1. **FERC** — eLibrary (`elibrary.ferc.gov`), docket numbers (CP##-###), orders,
   annual Form 2 / Form 2-A filings. The authoritative record for certificated
   capacity, mileage, in-service dates, and cost for any interstate system.
2. **EIA** — the dated Natural Gas Pipeline Projects workbooks, tracked locally at
   `sources/eia_pipeline_projects/raw/`. **Read the local file, then cite the dated
   release URL.** Cite the sheet name and the Excel row in your note.
   URL form: `https://www.eia.gov/naturalgas/pipelines/EIA-NaturalGasPipelineProjects_<Mon><Year>.xlsx`
   — **with an underscore for every release EXCEPT Aug 2026**, which is the lone
   un-underscored file: `EIA-NaturalGasPipelineProjectsAug2026.xlsx`. Every other
   spelling 404s. Never cite the undated `EIA-NaturalGasPipelineProjects.xlsx` and
   never cite the `data.php` navigation page.
   Also useful: EIA's state profiles and the Natural Gas Annual.
3. **PHMSA** — operator annual reports and the National Pipeline Mapping System
   public viewer for mileage and diameter by operator.
4. **The operator itself** — SEC 10-K/S-1 filings (`sec.gov/edgar`), investor
   presentations, the system's own tariff/informational postings (EBB) page.
5. **State regulators** — Texas RRC, Oklahoma Corporation Commission, etc.
6. **Trade press with a named reporter and a date** — S&P Global/Platts, Argus,
   Reuters, Natural Gas Intelligence. One wire story republished in five outlets
   is ONE source.

**All EIA releases are ONE origin.** Two EIA workbooks agreeing never makes a unit
`high` — it is one source. `high` needs two genuinely independent hosts.

## Sourcing failures found in slice 2 — do not repeat any of these

**1. The landing page is not a ref.** `https://www.eia.gov/naturalgas/data.php`
(with or without `#pipelines`) is a navigation page. It states no value about any
pipeline. Citing it is the same defect as citing the undated
`EIA-NaturalGasPipelineProjects.xlsx`: the reviewer cannot get from the URL to the
number. 61 units across slice 2 were staged this way and all had to be re-grounded.
A ref to EIA is ALWAYS a dated release URL plus, in the note, the **sheet name and
the Excel row** — e.g. "EIA Aug 2026 release, sheet 'Historical Projects
(1996-2024)', Excel row 1001". Read the workbooks locally from
`sources/eia_pipeline_projects/raw/` (or the flattened
`sources/eia_pipeline_projects/data/eia_projects_long.csv`, which carries
`release, sheet, excel_row` for every row of every release) and cite the dated URL.

**2. EIA carries PROJECTS, never SYSTEMS.** The workbook's unit of record is one
project — an expansion, a lateral, a compressor station — with a Miles and an
Additional Capacity for THAT project. It has no system mileage, no system capacity,
and no founding year. So for a row whose SegmentName is `Main Line`, or that
otherwise describes a whole trunk system, **EIA cannot support Length, Capacity or
StartYear**, and attaching it to those values is fabricated attribution (its
`Pipeline Operator Name` can still ref Operator/Owner — rule 5). P2579 (Northern Natural
Gas, 14,300 mi / 6,300 MMcf/d / 1930) had all ten of its units staged this way; the
notes themselves said "EIA *and pipeline industry sources* confirm", which is the
tell — the value came from somewhere else and EIA was attached afterwards. For
system-level US attributes go to PHMSA / NPMS, FERC Form 2, the operator's own site,
or the parent's SEC filings.

**3. Match the row's SegmentName, not the PipelineName.** P2564's SegmentName is
`Midwest Market Access Project` and EIA carries exactly that row; the prior pass
searched on "Southern Star" and wrote up a different project entirely. P5113's EIA
row is titled `DTE LEAP Project`, not "Louisiana Energy Access Project". Search the
workbook on the segment/project name and its variants before concluding EIA is silent.

**4. Never stage a value your own verification note contradicts.** Three P2564 fills
shipped as `REFS_ADDED` while their notes read "EIA status shows 'On Hold' not
'Cancelled'", "EIA database does not show cancellation", and "field not populated".
If the source says something different from the sheet, that is a **concern** (and an
`UNRESOLVED` for that unit), never a confirmation.

**5. EIA's `Pipeline Operator Name` refs BOTH Operator and Owner.** GEM uses the
operator name interchangeably with the owner (Baird, 2026-09-14), so a dated EIA
release whose `Pipeline Operator Name` names the same company as the sheet's Owner is
a valid `Owner` ref — cite the release, sheet and Excel row as for any EIA ref. Do not
leave an Owner unit `UNRESOLVED`, or reject its ref, because EIA's field is labelled
"operator". It is still ONE origin: EIA alone is `medium`; `high` needs a second
independent host (the parent's SEC 10-K, a FERC order, the operator's own page).
It refs **Owner1 only**: on a multi-owner row (JV partners, equity splits), Owner2+
and any percentages still need their own source (the parent's SEC filing, a FERC
order). If the sheet's Owner1 differs from EIA's operator name, that is a concern to
note, not a confirmation.

**6. A blocked fetch is a tooling failure, not evidence — and SEC EDGAR is never
blocked.** A repair pass on P2579 reported PHMSA, FERC, the operator's site and SEC
EDGAR as all inaccessible, then substituted Wikipedia for the lot. EDGAR was not
inaccessible: it 403s undeclared clients by policy and answers normally the moment
the request sends an identifying User-Agent, e.g.
`-H 'User-Agent: <name> <email>'`. With that one header the parent's 10-K series
resolved eight of that row's units outright. Before you call any source unreachable,
escalate: `curl -sL` with a real User-Agent; the other host form; Wayback
(`web.archive.org/web/<ts>/<url>`, or the CDX API
`archive.org/wayback/available?url=...`); `curl -o` then `pdftotext -layout` for PDFs.
Then say *what you tried*. Two things never follow from a failed fetch: that the
resource is gone, and that a weaker source may stand in for it. Wikipedia is not a
fallback for a primary source — and "the company was founded in YYYY" is a corporate
event, not the pipeline's `StartYear1`.

**7. Watch the substring you hand `url_verifier`.** SEC and other filers write
`14,300&#160;miles`, so `"14,300 miles"` misses on raw HTML while the document plainly
states the value. A verifier miss on a page you have read is a bad expected-string, not
an unsupported value. Pick a short distinctive phrase you have actually seen in the
fetched bytes.


## Hard prohibitions

- **Never cite GEM** — no gem.wiki, no globalenergymonitor.org, in any ref or note.
- **Never fabricate a URL.** Every URL you stage must have been fetched and returned
  200. Record the check in `verifications[]` with `ok`, `contains_value`, and
  `name_found`.
- **Banned hosts:** `abarrelfull.wikidot.com`, `abarrelfull.co.uk`, `theodora.com`,
  `yingdodo.com`. Never, not even alongside a corroborating source.
- `name_found` is **true** when the document names the pipeline — including by its
  SegmentName, an acronym, or a project-title variant. A page about one terminus or
  about the parent trunk only is `name_found=false`.

## Before you finish

Run `python scripts/check_shard_coverage.py --staging <staging dir> --pid <PID>`
and fix anything it reports. Every worklist unit must be reported on.
## Recommending that a cell be CLEARED

Some corrections empty a cell rather than fill it — most often a status flip to
`operating`/`proposed` on a row still carrying `CancelledYear`, `ShelvedYear` or
`ShelvedCancelledType`. A row cannot be operating and carry a cancellation year.

**A clearing is not a fill, and cannot be staged as one.** `check_shard_coverage`
rejects a sourced `class_out` whose `values` is empty (`UNMERGEABLE`), so
`values={"CancelledYear": ""}` with `class_out="REFS_ADDED"` will not merge. Do not
work around this by editing the shared script.

Stage it this way instead:

- The **fill** keeps the honest ref record for the cell as it stands — `REVERIFIED`
  with the recorded value, if a ref really does state it — and its `researcher_notes`
  say plainly that the clearing is recommended and where the recommendation lives.
- The **recommendation** goes in `validity[].contested` and, for a status change, in
  `status_reviews[].proposed_changes`, as `{"CancelledYear": "", ...}`. Those are the
  surfaces for recommended edits; `contested` holds values, never prose.
- Clear the cell's **`[ref]`** along with its value — a cleared value must never leave
  an orphan `[ref]` behind. Say so in the note.

Worked example: P4070 (North Brooklyn Pipeline), whose 2023 `CancelledYear` documents
the withdrawal of the project's fifth phase, not the cancellation of the pipe — which
was built and in service by the 2020-21 heating season.

## Never stage a Status your own status_review contradicts

If `status_reviews[0].proposed_changes` proposes a new `Status`, the `Status [ref]` fill
must NOT stage the sheet's old one. Four slice-2 shards (P5405, P2574, P3199, P0171) did
exactly that: `fills[0]` carried the old value as `REVERIFIED`/`REFS_ADDED` while the
row's own status review proposed the opposite. That is ADDENDUM failure mode 4 applied to
the Status cell, and on a duplicate pair it leaves two rows asserting opposite statuses
for one physical pipe.

The coherent shape is one of these two, never a mix:

- **You found the flip.** `fills[Status]` stages the NEW value with the refs that state
  it, and `status_reviews[].proposed_changes` says the same thing. The two agree.
- **You could not establish the flip.** `fills[Status]` keeps the recorded value as an
  honest `REVERIFIED` ref record, and the status review's verdict is `confirm` (or the
  concern goes in `validity[]` with the evidence you do have). No silent contradiction.

## `contested` holds VALUES, keyed by real backend columns

`build_ref_workbook._contested_cols()` reads `contested` to decide which cell on the
Backend mirror gets tinted and what the reviewer's cell comment says. Two ways to lose a
finding there, both found in slice 2:

- **A key that is not a backend column tints nothing.** `'Length'` is not a column
  (`LengthKnown` is); `'RouteType/RouteAccuracy (routes repo)'` is not a column. A bare
  boolean or a string instead of a dict is discarded outright. Copy the column name from
  the worklist unit's `value_cols`, exactly.
- **A value must be in that cell's own unit.** P2600's record proposed EIA's `35.8`
  (miles) for a `LengthKnown` cell whose `LengthKnownUnits` is `km` — pasting it would
  have shortened the pipe by 40%. Convert first, and say so in the note.

Values, not prose: `''` is the correct value when the finding disputes a cell without
proposing a replacement. Put the reasoning in `researcher_notes`, where it is read.
Never tint an empty cell — omit a column the sheet leaves blank.

## Tier and `independent` can never exceed the record's own verified refs

`tier` and `independent` are counted over the refs on **that record** that actually
verified — `ok: true` AND `contains_value: true`. A ref that 404s, or that resolves but
does not state the value, contributes nothing to the count no matter how good the
publisher is. And **all EIA releases are one publisher**: twenty-eight dated workbooks
agreeing is one origin, exactly as one wire story in five outlets is one origin.

So: two distinct publishers among the record's verified refs → `high` /
`independent: true`. One → `medium` / `independent: false`. **None → `low`**, and that
includes every `UNRESOLVED`: a record with `proposed_refs: []` is `tier: "low"`,
`independent: false`, always. There is no such thing as a well-sourced UNRESOLVED.

### What counts as ONE origin (found the hard way in slice 2)

The publisher count is over *origins*, not documents. Every one of these is **one**:

- **All EIA pipeline-projects releases together** — twenty-eight dated workbooks
  agreeing is one origin.
- **Multiple SEC/EDGAR filings by the same filer** — an operator's 10-K, 8-K and S-1
  are one company speaking three times (P5835 Owner: two Enbridge filings = medium).
- **Multiple Federal Register or govinfo notices** — the Federal Register is one
  publisher however many notices carry the docket (P5832, P4454, P0212 ProposalYear).
- **Multiple FERC documents in one docket**, multiple PHMSA documents, multiple RCA
  orders, multiple state-PUC filings — one publisher each. This includes **an agency
  page plus the applicant's own document that the agency hosts inside that same
  record** (e.g. the Alaska DNR CIGGS pipeline page and `CIGGS_Application_*.pdf` on
  `dog.dnr.alaska.gov`): one agency record is one origin, however many files it serves.
- **Multiple Wayback captures of the same site** — one origin, the site itself.
- **Our own measurement of the repo geojson.** Computing a route's extent is not a
  published figure and never contributes a second origin; say in the note that the
  comparison figure is our own measurement.

Corollary already implied by the rule above, stated plainly because it was got wrong:
**a ref whose verification is `ok: true, contains_value: false` is not a ref for that
value.** Keep it in `verifications` as the record of what was searched; do **not** put
it in `proposed_refs`. A record whose only refs are of that kind is `tier: "low"`,
`independent: false`, with `proposed_refs: []`.

And the inverse, so `UNRESOLVED` is not overused: a source that states a *different but
comparable* value for the same quantity **IS** a ref (rule 4(e)) — stage it at
medium/high with the discrepancy noted and the recorded value in `contested`. A source
stating a figure for a *different scope* (a per-docket cost against a whole-system cost
cell) is genuinely "nothing found" and `UNRESOLVED` is correct there.

## Every `ok: true` verification MUST carry `name_found`

`check_shard_coverage` rejects the shard with
`[UNMERGEABLE] an ok verification lacks name_found` if any verification has
`ok: true` and no `name_found` key. It is not optional and it has no default.

Set it `true` or `false` explicitly, and **quote the matched name in the `note`** so a
reviewer can see what matched (`"names 'DTE LEAP Project'"`). This bites hardest when
copying `verifications` from `status_reviews[]` onto a fill — status-review
verifications carry no `name_found`, so every copied entry needs one added. Copy the
URL, not the whole dict.

## EDGAR search feeds are navigation surfaces, not citations

`https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&...` is a company-search
**feed**. Its contents change as EDGAR's index changes, so it states nothing durable
about any pipeline — the same defect as `data.php` and the undated EIA workbook. Cite
the **filing document itself** (the `Archives/edgar/data/<cik>/...` URL for that 10-K,
S-1 or 8-K), with the form type and filing date in the note.

EDGAR 403s undeclared clients by SEC fair-access policy; `url_verifier` already retries
with an identifying User-Agent. A 403 from EDGAR is never evidence the filing is gone.

## The bare NPMS root URL is a navigation surface too

`https://www.npms.phmsa.dot.gov/` is the National Pipeline Mapping System's landing
page: PIMMA login, Public Map Viewer link, About/FAQ/Contact. It contains **no
pipeline-specific content**, so it supports no value on any row — same defect class as
the EDGAR company-search feed and the undated EIA workbook. It returns HTTP 200, so it
is not a dead link; it is **effectively UNCITED**, which is worse, because the 200 makes
it look checked.

It is already the sole `current_ref` for **44 worklist units across 11 rows** in the
northeast-alaska batch alone (P7450, P7453, P7454, P7455, P7456, P7458, P7461, P7462,
P7463, P7464, P7465) — a tracker-wide pattern, not a one-row slip. So:

- Never carry it forward as a `[ref]` and never place it in `proposed_refs`.
- Replace it with something that actually states the value. NPMS itself is usable if you
  reach a **specific** artifact — a state/county map PDF or an operator-specific viewer
  export — not the root.
- If nothing replaces it, the honest outcome is `UNRESOLVED`, not a citation to the root.
- A **negative finding proposes nothing**: if your `validity` record's whole point is that
  a URL supports nothing, name it in the prose and leave `proposed_refs` empty. Staging the
  rejected URL as a proposed ref at `tier: "high"` contradicts the finding itself.

## "Blocked" is a claim you must be able to reproduce

A blocked fetch is a tooling failure, never evidence about the source — and a *wrong*
blocked-source claim is worse than a thin note, because the next reader trusts it and
stops looking. Two false claims were caught in A6 (P7464), both driving units to
UNRESOLVED:

- "Alaska DNR ... 403 behind a DataDome bot-challenge" — **untrue**. `dog.dnr.alaska.gov`
  returns 200 and other rows in this same batch sourced real findings from it. The agent
  had hit `https://dog.dnr.alaska.gov/Services/Pipeline` (no pipeline name), which 404s.
  A 404 on a guessed path is a bad path, not a block.
- "Wayback CDX shows no snapshot for that host" — **untrue** for `rca.alaska.gov`;
  `http://archive.org/wayback/available?url=rca.alaska.gov` returns a 2026-08-14 capture.
  (It renders as a ~1 KB JS shell, which is a fine thing to say — it is just not "zero
  snapshots".)

So, before writing that anything is blocked:

- Reproduce it: `curl -sL -o /dev/null -w '%{http_code} %{size_download}' --compressed
  -A '<browser UA>' <url>`. Record the actual status code and byte count in the note.
- Distinguish 403/challenge (blocked) from 404 (wrong path) from 200-with-a-JS-shell
  (reachable but empty). They are three different facts and only the first is a block.
- Check Wayback for real — `http://archive.org/wayback/available?url=<host-or-url>` —
  and if a capture exists, FETCH it before concluding anything.
- Then write what is true, with the evidence: "rca.alaska.gov 403s behind DataDome to
  both WebFetch and curl-with-browser-UA; a Wayback capture of the host root exists
  (20260814171212) but renders as a JS shell carrying no filing content."

A third false claim was caught in A1–A4: a BusinessWire release staged
`ok: false, contains_value: false`, reasoned about from the search-result headline and
never read. The origin does 403 automated clients — and its **Wayback capture read fine
on the first try**, stating the value in the first paragraph. Note the ladder order:
`https://web.archive.org/web/<year>/<url>` (the **path** form, which 302s to the nearest
capture) rate-limits far later than `archive.org/wayback/available`, which returned 429
on four consecutive attempts that same minute. If the availability API throttles you, go
to the path form rather than concluding there is no capture.

**Alaska DNR pipeline registry** — the working path shape is
`https://dog.dnr.alaska.gov/Services/Pipeline/<Pipeline%20Name>`, browsable from
`https://dog.dnr.alaska.gov/`. It carries operator, diameter, construction dates and
transfer history for registered Alaska lines. Remember the one-origin rule: that page
plus any applicant document DNR hosts in the same record is ONE publisher.

## `contains_value` is the field the merge actually reads

`merge_qc.verified_refs` keeps a proposed ref **only** when some verification says
`ok: true` AND `contains_value: true` AND its `url` is **byte-identical** to the entry in
`proposed_refs`. Fail any of the three and the merge silently strips every ref off the
record and re-keys it `UNRESOLVED` — the research is done and then thrown away. **A
missing `contains_value` key reads as `false`.** There is no default, and nothing warns
you: `check_shard_coverage.py --all` is the only thing that catches it, which is why it
runs before a shard is called finished.

41 finished records across the four slice-2 A-batches were unmergeable on this, each a
different way of getting the same thing wrong:

- **The key was simply never written.** 26 verifications whose own `note` quoted the page
  stating the value carried `ok: true` and no `contains_value` at all.
- **The verification pointed at a different URL form than the ref.** A verification on
  `reuters.com/article/...` while `proposed_refs` carried the Wayback capture of it; a
  verification on the EIA **Oct-2025** release while `proposed_refs` listed only the
  **May-2026** one. It is string equality, not "the same document" — verify the URL you
  actually staged, in the form you staged it.
- **The verified URL was never added to `proposed_refs`.** The record cited the EIA
  workbook and verified a trade-press article that appeared nowhere in the ref list.

Before you finish a record, read your own `verifications` back: for every URL in
`proposed_refs`, is there an entry with that exact URL, `ok: true`, `contains_value` set
explicitly, and `name_found` set explicitly? If not, the record does not exist.

Two shapes that look like exceptions and are not. A **binary `.xlsx`** cannot be
substring-checked, so the automated verifier cannot set `contains_value` for an EIA
release — read the sheet/row by hand (or against `sources/eia_pipeline_projects/data/
eia_projects_long.csv`) and set `ok`/`contains_value`/`name_found` to what you observed,
saying so in the `note`. Same for any page you had to read by hand. **Do not leave a
hand-confirmed source recorded as a failure — the merge believes the fields, not the
prose.**

## The two verdict vocabularies are NOT interchangeable

They look alike, they sit in sibling arrays, and they are enforced separately. Ten
slice-2 records mixed them; the merge's own verdict histograms are where it surfaces.

| field | lives in | allowed values |
|---|---|---|
| `verdict` | `validity[]` | `confirmed (caveat)`, `concern` |
| `verdict` | `status_reviews[]` | `confirm`, `change`, `stale`, `unclear` |
| `concern_type` | `validity[]` | `existence`, `duplicate`, `classification`, `attribution`, `spec`, `none` |

Seen in slice 2 and repaired by hand: `change`, `confirm` and `confirmed` as a *validity*
verdict; `confirmed (caveat)` as a *status-review* verdict; `validity`, `stale` and
`misattribution` as a `concern_type`. `severity` is a third vocabulary again — it belongs
to the wiki-alignment tabs and never appears on a validity record.

Two rules follow. A validity record that disputes no cell (`contested: {}`) is
`confirmed (caveat)`, never `confirmed`. And a `concern_type` describes **what the
`contested` field disputes**: an attribute value is `spec`, a wrong owner/operator/name
is `attribution`, "this row should not exist" is `existence`, "these two rows are the
same pipeline" is `duplicate`, a wrong `PipelineType`/`Fuel` is `classification`.

## A ref that contradicts the value, or measures something else, is not a ref

`REFS_ADDED`/`REVERIFIED` asserts *this source states this value*. Eleven slice-2 records
asserted it over a source that said the opposite, or said something adjacent:

- **Contradiction.** PGJ says 255 MMcf/d against a recorded 225.00 (~13%, far outside
  rounding); EIA carries "On Hold" against a recorded `cancelled`; EIA gives in-service
  2025 against a recorded `StartYear1 = 2026`; an open-season notice describes a
  *proposed* project against a recorded `operating`.
- **Different scope.** Two sources giving the Sabal Trail **system** total, subtracted
  from each other to estimate one phase's incremental capacity. A system total is not a
  ref for a per-segment cell, and arithmetic across two sources is not corroboration.
- **Inference from an absence.** EIA leaving `miles` blank is not a statement that a
  project adds zero pipe — EIA's "Expansion" type also covers loops, which do add pipe.
- **Naming neither the value nor the row.** A parent's investor page that states neither
  the recorded entity spelling nor the recorded percentage, and never names the pipeline.

All of these are `UNRESOLVED`-with-notes: say what you searched, keep the URLs in the
note (they are leads for the next pass), and file the correction as a `validity[]`
concern with the candidate in `contested`. Rule 4(e) cuts the other way too — a figure
agreeing **within rounding** (70.7 against a recorded 71.0; EIA's $426M against
$426.666M) IS a ref, at medium with the delta noted.

The contrast that draws the line: a FERC order that enumerates a phase's facilities
exhaustively and lists no new pipe **does** state `LengthKnown = 0`, because the encoding
follows with no added assumption. EIA's blank cell does not.

## Gate artifacts and known-spurious firings

`sweep_gates.py` gates are **advisory** (the script exits 0 regardless). At delivery this
campaign requires **E, F, I' and L at zero**; the others are read and judged.

- **Gates B and D fire spuriously on `validity[]` records.** By repo-wide convention a
  `validity` record carries no `verifications` — it is an assessment, not a ref record —
  so a gate that counts verifications flags every one of them. This is gate scoping, not
  a shard defect. Note it in the run summary and move on. **Do not edit the shared
  scripts to silence it** (another session holds uncommitted changes to
  `sweep_gates.py`, `check_shard_coverage.py`, `merge_qc.py`, `url_verifier.py` and
  `harvest_sentinel_findings.py`; document here instead).
- **Do not build a gate that flags "Owner refs that are all eia.gov"** (Baird, explicit).
  That check came from the wrong rule — see failure mode 5 above: EIA's
  `Pipeline Operator Name` is a legitimate Owner ref.

## Deferred hardening — recognise these by hand, they are not coded

Checks worth running your eye over before you finish a shard, each a defect found in
this campaign that no script currently catches:

1. `validity` is a **list**, never a dict or a bare string.
2. No `data.php`, no undated `EIA-NaturalGasPipelineProjects.xlsx`, no EDGAR
   `browse-edgar` search feed anywhere in `proposed_refs`.
3. `status_reviews[].proposed_changes` is a **dict**; a verdict of `change` with an
   empty `proposed_changes` is a contradiction.
4. An `UNRESOLVED` unit carrying a verification that is `ok` **and** `contains_value` is
   a mis-class — something WAS found (rule 4(e)); it is `REFS_ADDED`.
5. A live status (`operating`, `construction`, `proposed`) left alongside a populated
   `CancelledYear` / `ShelvedYear` / `ShelvedCancelledType` — clear them via the
   P4070 pattern above.
6. A fill's `values` is a **dict** keyed by real backend columns, never a list, never a
   bare value.
7. `QCCOwner` is an open QC-workbook column, not a tracker value column — if it appears
   in a unit's `value_cols`, it is worklist leakage; report it, do not research it.
8. Every `ok: true` verification carries `contains_value` **explicitly**, and its `url` is
   byte-identical to an entry in the record's own `proposed_refs`.
9. A `validity[]` verdict is only `confirmed (caveat)` or `concern`; a `status_reviews[]`
   verdict is only `confirm`/`change`/`stale`/`unclear`; `concern_type` is only
   existence/duplicate/classification/attribution/spec/none.
10. `contested` holds candidate VALUES, never prose. A sentence of explanation inside a
    `contested` value reaches the paste surface as if it were the proposed cell content —
    move it to `researcher_notes` and leave the bare value (or `""` where the evidence
    only says the current value is wrong).
11. A third-party storage mirror is live bytes, not a citable publisher. `183 FERC
    ¶61,049` was staged off `https://us-east-1.storage.xata.sh/4oj4ue167p5a1anou7nvrf7u80`
    because ferc.gov 403s — the PDF is real and was read, but an opaque object-store URL
    names no publisher and will rot. Cite it only alongside a note naming the FERC
    accession/eLibrary locator, and never fabricate that locator to replace it.
