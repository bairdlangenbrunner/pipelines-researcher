# Confidence tiers

One rubric, two entry points: **research** (a human/agent judging sources for a
data point) and **reconciliation** (the engine scoring a GEM↔reference match).
Both land on the same green/yellow/red/blue cell colors.

## Research-side rubric (corroboration-driven)

For every material data point (status, capacity, length, diameter, ownership, FID,
dates, endpoints, route), **one ref that passes every validation check below is
sufficient; 2+ independent sources that agree are preferred** (Baird 2026-09-30 —
relaxed from a near-requirement, for time and efficiency). Record the tier and the
sources in `ResearcherNotes`.

### What "validated" means — the checklist a single ref must pass

Machine checks (`scripts/url_verifier.py`, run on every URL, every batch):
1. an http(s) URL — not GEM (`gem.wiki`, `globalenergymonitor`), not banned
   (abarrelfull, theodora, wikidot, yingdodo) — re-tested against every redirect hop and
   the landing URL, so a shortener can't smuggle one through;
2. not a Save-Page-Now `/save/` instruction URL (a Wayback `/web/<ts>/` snapshot is fine),
   and not navigation — a site search, tag/category listing or paginated index;
3. it loads: HTTP 200 (bot walls escalate through `fetch.py`; a self-signed TLS chain or
   SEC's UA policy retries once, labeled). 404/410 = dead; other failures are access
   failures, never deletions;
4. text is readable — a PDF or workbook with no text layer is "unreadable", not a miss;
5. the **value is on the page** (`any_of=surface_forms(value)`, whole-number matching
   against prose, not markup);
6. the page **names this pipeline** (`name=` → `name_found`; `OtherLanguage*` names too).

Judgment checks (the agent's, recorded in the verification `note` / `researcher_notes`):
7. it names THIS segment — not a terminus, not the parent trunk (corollary a);
8. the value agrees — within rounding, with unit equivalence ("6 BCM annually" = 6 bcm/y),
   status by inference (an inauguration confirms `operating`), and **a cost recorded as the
   midpoint of a range the page states** (manual, Cost: "4,5 до 13,6 млрд" supports 9.05 bn;
   `url_verifier.range_midpoint_match`, applied to `*Cost` columns only — it would misfire on
   years); a verifier miss on
   those is a screen artifact the agent overrides with the matched text. **But rounding
   only decides whether the ref counts, never which value survives:** when 2+ independent
   validated refs agree on one precise figure that differs from the sheet's uncited value,
   the unit is staged as a value change to the refs' figure (Baird 2026-09-30; Sweep SOP
   "Precise value over rounding"). Retaining the sheet value on a within-rounding ref is
   the fallback for a single ref, refs that disagree, or a rounded/unit-converted/nominal
   restatement of the same figure;
9. it is a segment figure, not a system aggregate (else `__VALIDITY__`, not a ref);
10. it is a real source — not GEM-derived, not a banned aggregator's restatement.

Merge-time and delivery gates re-enforce these: `merge_qc.relevance_qc` caps an unnamed
ref at `low`, and `sweep_gates.py` gates E (orphans), F (banned/GEM), I (relevance) and M
(prose in a pasteable cell) list whatever slipped through.

| Tier | Color | Meaning |
|---|---|---|
| **High** | green | one source that passes every validation check below (2+ independent preferred) — **sufficient; the unit is done**. Exception: a **status change** is green only on 2+ independent publishers |
| **Medium** | yellow | a usable source with a caveat the agent flags, or a status change resting on one publisher |
| **Low** | red | a single weak/secondary source, or sources partially conflict |
| **Inferred / Presumed** | (blank + note) | no verifiable source — flag in `ResearcherNotes`; for status changes set `ShelvedCancelledType = inferred`, no fabricated URL |
| **Re-verified** | blue | value unchanged from the existing GEM value but checked again this batch |

**Independent** = genuinely separate origins (company PR **and** a regulator filing
**and** an OGJ article reporting it independently). **NOT independent:** the same
wire story (Reuters/BusinessWire/PRNewswire) republished; multiple outlets tracing
to one original; anything citing GEM/gem.wiki (circular — see standing rule 1).
**Common ownership alone does not defeat independence (Baird 2026-09-30, P2227):** two
distinct organisations each publishing their own document are independent publishers even
when both are bodies of the same state — BOTAS (the operator) and the Turkish Energy
Ministry each describing the Russia–Turkey line on their own page count as two. It stops
being two when one page republishes or quotes the other, or both restate one release.
When sources conflict, prefer the one higher in `source_roster.md`, note the
conflict, and lower the tier.

**The staged `independent` field means the rubric above, not "independent of GEM."**
It is the yes/no column a researcher reads when deciding whether to paste a value, so
a wrong `yes` is worse than a missing one. It may be `true` only when the record
actually carries **2+ surviving refs** — surviving meaning after merge-time QC has
dropped the ones that failed verification, which is exactly when agents get it wrong
(the flag used to outlive its own refs). A unit that loses the claim keeps its tier
unless it is a status change (below). Enforced in
`merge_qc.independence_qc()` and applied by all three mergers, so no pass can restate
it; `scripts/repair_independence.py` applies the same invariant to dirs merged before
the fix. `scripts/repair_tiers.py` re-tiers stores merged before 2026-09-30 to the rule below
(tier + notes only; carried handoff copies read their source store's verifications).

**The tier is a separate question from the flag (Baird 2026-09-30).** One validated ref
is green: `independence_qc(..., high_min=1)` caps `high` only when no ref survives, and
`merge_qc.validated_tier` promotes a `medium` to `high` when the record carries a
surviving ref whose verification loaded and has `name_found: true` (run after
`relevance_qc`, so an unnamed ref is already capped at `low`; `low` is never promoted).
**Status changes are the exception:** a `__STATUS__` `change` verdict, or a FILL proposing
a Status different from the snapshot's, is merged with
`high_min=STATUS_CHANGE_MIN_PUBLISHERS` (2) and is never promoted — on one publisher it
is `medium`/yellow. Both halves stay unconditional on what the flag claims (until
2026-09-10 the tier half hung off `if not independent`, which rewarded an honest `false`
with a `high` the over-claimer lost). Gate B mirrors this: a `high` with no verified ref,
or a `high` status change on <2 hosts. So green = "one validated source or more";
the `independent` column is what says two origins agree. An `UNRESOLVED` record or a `__VALIDITY__` concern is never promoted — a
page naming the pipeline that does not settle the unit validates nothing.

**A single validated source is sufficient — the unit is done.** If one source passes the
checklist above (the pipeline is named and the value/status is stated on the page), that
ref **fills the `[ref]` cell at high/green and closes the unit** — no second-source
note is owed (a status change still needs 2 for green). A second source
is **preferred**: take it when the document already open or one quick search offers one
(ideally a different publisher AND document class — regulator approval ↔ operator
disclosure ↔ press ↔ EIA/acceptance notice), because it sets `independent` and is what
a status change needs for green. (This
supersedes the 2026-09-03 "second source is an obligation" rule, Baird 2026-09-30.) Only
*fail to confirm on the page* drops to red / blank+note. "Prefer blank + a note" applies
to a **single weak source that does not actually confirm** the value — not to a single
source that does. This holds regardless of the lone source's roster rank: a confirmed-
on-page single source is green even if it isn't "top-tier."

**Status is inferred from context — don't require the literal word.** A source confirms a
status when its prose *entails* it, even if the status token never appears. "Work on expanding
the line will be completed mid-year, boosting transit to <country>" **confirms `operating`**;
an inauguration, a throughput/export figure, or "carries gas to X" do too. **Make that
inference yourself** — a page is a valid status ref when a reasonable reader concludes the
status from it, not only when it prints the word. (This is why the P5984/eurasianet ref is
valid: it names the Rasht-Chelavand line and describes its expansion completing and transiting
5.5 bcm to Azerbaijan — `operating` by inference. The automated screen failed it only because
it substring-searched for the token `operating`.) The `url_verifier` "value not found" result
on a status is a **screen artifact, not a verdict** — the agent decides.

**A ref must name THIS pipeline.** Containing the right number is not enough: a page about
terminus A, or about terminus B, or about the parent trunk, is not a ref for the "A–B" segment
row unless it names that segment. Pass `name=` to `url_verifier` on every check (it records
`name_found`); a unit whose verified refs all come back `name_found: false` is capped at `low`
by `merge_qc.relevance_qc`. When the page names the line in another language, pass that name
too or encode the hand-confirmed match in the verification `note`.

**Match names fuzzily; read the full page.** Transliteration varies (Chelavend↔Chelavand,
Kordkuy↔Kordkoy) — don't reject a source because it spells the name one letter off (pass the
name to `url_verifier` via `name=`, which matches with transliteration tolerance). And never
conclude "the page doesn't support the value" from a **truncated/stub fetch** (a block page,
cookie wall, or archive interstitial): pull the **full page text** first. Asserting a negative
from a failed/partial fetch is a standing-rule-3 error.

**Harvest the GEM wiki page's own citations.** Before treating a `[ref]` cell as
un-fillable, mine the pipeline's gem.wiki reference list (captured to
`wiki_citations.json`) and, for every backend data point whose `[ref]` is blank or weak,
check whether one of those already-vetted citations confirms the value on its page. If it
does — low, medium, or high — add it (subject to the URL verifier and the no-GEM /
no-fabrication rules). Wiki citations are candidate sources, not auto-valid: a Wikipedia
URL **is citable** (policy reversed 2026-08-27 — see `source_roster.md`) but tiers as one
secondary source, so prefer the underlying source it cites and never count two language
editions as two sources; and dead/rotted links still fail the verifier.

## Reconciliation-side mapping (composite score → color)

`reconcile.py` combines per-signal scores (name, endpoints, diameter, length, and
route geometry) into a composite `S ∈ [0,1]` over the signals actually present
(missing signals are dropped and weights renormalized — a pipeline with no route is
not penalized for it). Default thresholds (overridable per source in the manifest):

| Composite `S` | Color | Reconciliation meaning |
|---|---|---|
| `≥ 0.75` | green | strong corroboration across signals |
| `0.45 – 0.75` | yellow | plausible match, needs human eyes |
| `< 0.45` or ambiguous | red | weak / ambiguous (e.g. top-2 candidates within 10%) |
| agree & unchanged | blue | reference agrees with GEM; re-verified, nothing to change |

**Geometry's role:** when both routes exist, the route-geometry signal
(buffer-IoU, endpoint distance, Hausdorff, length ratio) participates with its
manifest weight and can lift a name-weak match to green, or expose a name-strong
"match" as a different corridor. When a route is missing on either side, geometry
is simply absent from the score.

**Match confidence vs value adoption.** The `Overlaps` color above is *match*
confidence — how sure we are these two records are the **same pipeline**. A strong
name + geometry + attribute agreement is green regardless of source tier (this is
what the POC's green meant). The **source-tier ceiling** governs a *separate*
question — *value adoption*: when an overlap's value disagreement routes to Update, a
single **Tier-2** source (GulfPub) keeps the adopted value at medium/yellow until a
second independent source corroborates it ("GulfPub is one source, never
authoritative"). So a row can be a green *match* whose GulfPub-sourced *value* is
still only yellow-confidence to apply. Tier-1 reference data (e.g. a regulator's own
GIS) can settle a value on its own. A **Tier-3** dataset (OSM — crowd-sourced, so
per-feature provenance is unverifiable) never adopts a value at all: it is a lead, or
a second voice beside a real source, and a match against it alone stays red.

The human-readable reason string (e.g. `name match (0.75); endpoints (1.00);
diameter ✓; route IoU 0.71`) is built from the present signals and written to the
`Match reason / notes` column so a reviewer can see *why* a row got its color.
