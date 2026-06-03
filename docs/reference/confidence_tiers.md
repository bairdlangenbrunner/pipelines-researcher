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
| **Inferred / Presumed** | (blank + note) | no verifiable source — flag in `ResearcherNotes`; for status changes set `ShelvedCancelledType = Presumed`, no fabricated URL |
| **Re-verified** | blue | value unchanged from the existing GEM value but checked again this batch |

**Independent** = genuinely separate origins (company PR **and** a regulator filing
**and** an OGJ article reporting it independently). **NOT independent:** the same
wire story (Reuters/BusinessWire/PRNewswire) republished; multiple outlets tracing
to one original; anything citing GEM/gem.wiki (circular — see standing rule 1).
When sources conflict, prefer the one higher in `source_roster.md`, note the
conflict, and lower the tier.

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
GIS) can settle a value on its own.

The human-readable reason string (e.g. `name match (0.75); endpoints (1.00);
diameter ✓; route IoU 0.71`) is built from the present signals and written to the
`Match reason / notes` column so a reviewer can see *why* a row got its color.
