# Confidence tiers

One rubric, two entry points: **research** (a human/agent judging sources for a
data point) and **reconciliation** (the engine scoring a GEM↔reference match).
Both land on the same green/yellow/red/blue cell colors.

## Research-side rubric (corroboration-driven)

For every material data point (status, capacity, length, diameter, ownership, FID,
dates, endpoints, route), **try to find 2+ independent sources that agree** before
treating it as settled. Record the tier and the corroborating sources in
`ResearcherNotes`.

| Tier | Color | Meaning |
|---|---|---|
| **High** | green | 2+ **independent** sources agree, or one primary/regulatory source |
| **Medium** | yellow | a single strong source (company filing, regulator, top-tier trade press), no contradictions |
| **Low** | red | a single weak/secondary source, or sources partially conflict |
| **Inferred / Presumed** | (blank + note) | no verifiable source — flag in `ResearcherNotes`; for status changes set `ShelvedCancelledType = inferred`, no fabricated URL |
| **Re-verified** | blue | value unchanged from the existing GEM value but checked again this batch |

**Independent** = genuinely separate origins (company PR **and** a regulator filing
**and** an OGJ article reporting it independently). **NOT independent:** the same
wire story (Reuters/BusinessWire/PRNewswire) republished; multiple outlets tracing
to one original; anything citing GEM/gem.wiki (circular — see standing rule 1).
When sources conflict, prefer the one higher in `source_roster.md`, note the
conflict, and lower the tier.

**The staged `independent` field means the rubric above, not "independent of GEM."**
It is the yes/no column a researcher reads when deciding whether to paste a value, so
a wrong `yes` is worse than a missing one. It may be `true` only when the record
actually carries **2+ surviving refs** — surviving meaning after merge-time QC has
dropped the ones that failed verification, which is exactly when agents get it wrong
(the flag used to outlive its own refs). A unit that loses the claim cannot stay at
tier `high`; a single source is `medium` at best. Enforced in
`merge_qc.independence_qc()` and applied by all three mergers, so no pass can restate
it; `scripts/repair_independence.py` applies the same invariant to dirs merged before
the fix.

**Single-source-that-confirms is fillable, not blank.** The 2+ target governs when a
value is *settled* (green); it does **not** mean a lone source is discarded. If exactly
one source can be found but its page **verifiably contains the precise data point**
(the pipeline is named and the value/status is stated on the page), that ref is
**sufficient to fill the `[ref]` cell at medium/yellow** — fill it, don't leave the cell
blank. **The hunt for the second source is an obligation, not a suggestion:** a single-
source unit's notes must say what was searched for the second and why it was not found
(researcher feedback 2026-09-03 — the sweeps were reading as "limited range of sources").
Aim for a different publisher AND a different document class (regulator approval ↔
operator disclosure ↔ press ↔ EIA/acceptance notice). Only *fail to confirm on the page*
drops to red / blank+note. "Prefer blank + a note" applies
to a **single weak source that does not actually confirm** the value — not to a single
source that does. This holds regardless of the lone source's roster rank: a confirmed-
on-page single source is yellow even if it isn't "top-tier."

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
