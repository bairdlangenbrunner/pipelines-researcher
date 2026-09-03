# Route-geometry findings — measured in the main loop, 2026-08-15

Computed directly from the merged geojsons in `../GOIT-GGIT-pipeline-routes` against the
`GGIT_gas_snapshot_20260812` sheet values. These are INDEPENDENT of the cluster agents'
source research and should be folded in alongside it.

## Read this before using any of it

**Most Ukrainian gas routes are 2–5 vertex schematics, not digitized traces.** Vertex counts:
P0777 2, P0787 2, P1485 2, P5989 2, P7817 2, P7818 2; P0775/P0776/P0783/P1460/P1481/P1457/
P1488/P1480 3; P0784/P0786 5; P3381/P3382 7; P3484/P5938 15. A schematic bounds the CORRIDOR
EXTENT and nothing finer — it cannot settle a length dispute, and a drawn-vs-stated gap of a
few tens of km on a 3-vertex line is meaningless. Where a gap is cited below it is because it
is LARGE ENOUGH that even the schematic minimum contradicts the stated value.

`LengthEstimateKm` on the sheet is the computed route length and reproduces these
measurements, so the sheet already exposes every gap below.

## Findings

### D — P3381 / P3382 share one route that is ~3x the documented corridor
Both rows carry a **byte-identical 7-vertex trace** (md5 of the coordinate array matches),
drawn length **214.9 km**, end-to-end straight-line span 134.8 km. The trace runs
49.500,36.042 → SE to 48.638,37.571 → then **doubles back ~53 km WEST** to 48.420,36.878, a
V-shape that accounts for the 215 vs 135 km gap. Nearest approach to Shebelinka is
**22.0 km** and to Slovyansk **22.7 km** — it misses both of its own named endpoints.

Against the cluster's own sourcing (Ministry of Energy Order No.445, 2013: the corridor is
km 1.1–68.6, ~67 km), the drawn route is **3.1x too long**. Both rows are graded
`RouteAccuracy = medium`, which this geometry does not earn.

This CORROBORATES the agent's double-count finding from a second direction and adds a
separate defect: **the route is wrong on both rows**, so `LengthEstimateKm = 215.35` should
not be read as evidence for or against either stated length. Route work is out of scope for
this pass — route to §8, and re-grade the accuracy.

### G — P3484 / P5938 also share a byte-identical trace (this one is legitimate)
15 vertices, 480.29 km, Ivatsevichy (52.708,25.335) → Dolyna (48.976,23.990). Sharing one
corridor trace across parallel strings is the documented convention (six Kazakh multi-string
systems do it) and is **not** evidence of duplication. ~188 km of this corridor lies in
**Belarus**, which makes the stated 292.00 km plausible as the Ukrainian-territory portion —
a hypothesis to source, not a finding.

### B — P0784's stated length is contradicted by its own corridor
Drawn **759.1 km** Shebelinka (49.452,36.519) → Izmail (45.346,28.844) against a stated
`LengthKnownKm = 164.00`. Even as a 5-vertex schematic this is a **4.6x** gap and the
schematic is a LOWER bound on the true corridor, so 164.00 km cannot be the length of the
extent this row names. Strong internal support for the data-entry-artifact hypothesis.
Compare P0786 (289.1 drawn / 257.00 stated) and P0787 (193.3 / 230.00), both unremarkable.

### H — P0775 / P0776 are genuinely different lines
They share a 189.3 km prefix from Yelets and **diverge at 51.711,36.157 — Kursk**, after
which P0775 runs 239.0 km to Dykanka and P0776 runs 417.5 km to Kyiv. Two different
destinations several hundred km apart, exactly as their names say. The near-identical stated
lengths (298.00 / 297.00) are therefore NOT explained by the rows being the same line. The
Ukrainian-territory hypothesis is not obviously right either: from the border to Dykanka is
roughly 170 km and to Kyiv roughly 380 km, so neither is ~297. Leave to sourcing.

### F — the P0783 = P0775 + P1460 concatenation test FAILS
Only 1 of 3 P0775 vertices and **0 of 3** P1460 vertices lie within 0.5 km of P0783's trace.
There is no aggregate-vs-segment geometric identity here (contrast Kazakh cluster A, where
the concatenation was exact). The three rows also carry **three different diameters** —
P0783 1420 mm, P0775 1220 mm, P1460 700 mm — which is the signature of distinct parallel
pipes sharing a corridor, not of one pipe recorded three times. Note the endpoint coincidence
that P0775 ends and P1460 begins at the same Dykanka node (49.825,34.525), and both P0783 and
P1460 end at the same Kryvyi Rih node — shared nodes, not shared pipe.

### Three-way sync — 2 violations, finding A
`python scripts/audit_route_sync.py --country Ukraine --commodity gas` → A=2, B=0, C=0, D=0.
**P7817** and **P7818** have live geometry but `RouteType = 'Not mapped (but could be — route
or endpoints are known)'`. Repairable with `apply_route_candidates.py --backfill-route-type`.
That is a SHEET WRITE and is NOT authorized — staged as a finding for Baird.
