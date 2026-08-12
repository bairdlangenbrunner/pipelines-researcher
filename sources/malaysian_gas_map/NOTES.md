# Malaysian Gas Map (2022 edition) — source notes

Registered 2026-08-12. **Read this before trusting anything this source says about a
pipeline's identity.** The geometry is good; the labels are not.

## What it is

| | |
|---|---|
| Document | *Malaysian Gas Map*, 2022 edition |
| Publisher | Malaysian Gas Association / Maps & Globe Specialist Sdn Bhd (`malaysiangas.com`) |
| Form | single-page **vector** PDF, 2880 × 2016 pt |
| Obtained | 2026-08-11 |
| Digitized | 2026-08-11, delivered as `extraction/` (GeoJSON + workbook + QA viewer + zip) |
| `source_tier` | **3** — see "Why tier 3" |

Not a scrape, not an API: a one-off digitization of a published industry wall map.
The as-delivered artifacts are tracked in `extraction/`; `prepare.py` re-derives the
ingest input into the gitignored `data/`. If `data/` is missing, run:

```bash
python sources/malaysian_gas_map/prepare.py
```

## Contents

**683 features** in the delivered extraction, split by `prepare.py`:

- **67 pipeline LineStrings** → `data/mgm-pipelines.geojson` — the reconcilable dataset.
  **5,273 km** geodesic total (37 Borneo / 30 peninsular), shortest 4.3 km, longest
  389.4 km, **no stubs** (contrast the OSM Malaysia extract, which has five sub-500 m
  fragments).
- **616 field polygons** → `data/mgm-fields.geojson` — **not** registered in
  `datasets[]`. These are oil/gas field outlines, useful as an endpoint-anchor
  gazetteer during §8 route work, never a reconciliation input and never a `[ref]`.

Two independently georeferenced insets:

| inset | GCPs | mean residual | max residual |
|---|---|---|---|
| Peninsular Malaysia | 11 | **6.7 km** | 9.9 km |
| Borneo (Sarawak/Sabah) | 5 | **1.9 km** | 4.0 km |

That residual is why `buffer_km_for_overlap` is **12.0 km** rather than the 2 km
survey-grade default — a perfectly digitized peninsular trace can sit 10 km off truth.
The buffer is the digitization's own error budget, not matcher slack.

## Coverage gap: the onshore PGU backbone is NOT in this extraction

The map draws the offshore gathering/trunk network in the stroke style the digitizer
followed; the onshore **Peninsular Gas Utilisation (PGU)** backbone is drawn
differently and did not come through. So the extraction is essentially *offshore
Terengganu + offshore/onshore Sarawak + Sabah*, plus the two cross-border trunks.

**Consequence for reconciliation:** a GEM row for the PGU system (P1065) reading as
unmatched against this source is a **coverage gap in the source**, never evidence
against the GEM row. Do not let a non-match here weaken a PGU finding.

## The class labels are wrong — this is the load-bearing caveat

The extraction carries `feature_class` and `candidate_name` per segment. Both are
**nearest-label-in-this-inset artifacts**: the digitizer attached whatever map text was
closest in pixel space. They are not per-segment identities, and they are wrong at
scale:

- **37 of 67** segments carry the literal string *"Sabah–Sarawak Gas Pipeline (SSGP)"* —
  which is **every single feature in the Borneo inset**, 37 of 37. They total
  **2,566 km** and span lon 112.02–116.71 / lat 3.17–6.73, i.e. the entire offshore
  Sarawak + Sabah gathering network. The real SSGP (GEM P1066) is a **512 km** onshore
  line. The label is the inset's most prominent caption, applied to everything in it.
- **14** carry *"Thai–Malaysia Gas Pipeline"*, including one running
  98.32,6.45 → 101.39,7.41 (**Andaman Sea**, the wrong side of the peninsula) and one
  103.39,6.53 → 103.56,4.62 (offshore Terengganu down to Kerteh). Neither is TTM
  (GEM P1068).
- The extraction's own **Read Me contradicts its data**: it states that all non-trunk
  segments are labeled "unnamed segment", yet **51 of 67 carry a trunk name**.
- The **16 genuinely unnamed** segments have `candidate_name`s that are **offshore field
  names** — Bedong, Duyong Barat, Serok, Berantai, Anding, Melor, Abu, Telok, Permatang,
  Tiong Pendera, East Piatu, Peta Kiri, Kerteh 2 CG. Good endpoint anchors; not
  pipeline identities.

**Therefore `manifest.yml` maps no `name`.** Mapping it would make a single GEM row a
magnet for a whole inset's worth of geometry and manufacture 37 false corroborations of
one 512 km line. Both raw strings survive verbatim in `description` (which the matcher
never scores) and in `_raw`, so a reviewer sees the label without the engine trusting
it. Treat every reference record here as **unnamed geometry**, exactly like OSM.

Same reasoning for **`status`**: the map states no per-segment status, so nothing is
mapped and this source raises **zero** `Status_Conflicts` by design. A blank is honest.

## No attribute length — the unit proof is N/A, not skipped

The map carries no length, diameter, operator, owner or date columns. Every length this
source contributes is **geodesic, computed from the trace**. The standing SOP check
(`geodesic_km / declared length_km ≈ 1.0`, the check that caught GulfPub's gas
miles-as-km defect) has **nothing to test here** — there is no declared unit to be
wrong. Stated explicitly so a future session doesn't record it as an unrun check.
`units.length_units: km` in the manifest is inert.

## Why tier 3

The *map* is industry-grade — published by the national gas association, and the sole
public source for much of the offshore gathering network. The *digitization* is not:
2–10 km georeferencing error, machine-inferred labels that are provably wrong on 51 of
67 features, and a documented coverage gap. Tier 3 puts it alongside OSM: real evidence
of where pipe runs, never authoritative on what a pipe **is**. It corroborates
**location**; on its own it never turns a cell green.

## Matching configuration

Geometry-dominant (`geometry_weight: 0.75`), name near-zero, diameter off — the same
shape as OSM's block, for the same reason (dead name axis), but with a wider buffer.

**No `geoarea_weight` override**, deliberately. The `MATCH_QUALITY` dead-axes condition
(unnamed reference features × routeless GEM rows) does **not** hold for Malaysia: 4 of
the 5 GEM gas rows are routed, two at `very high (within meters)`, and every reference
trace is trunk- or gathering-scale. Geometry is genuinely live on both sides, so an
admin-area fallback would only blur it. Same call as India and Kazakhstan.

## Re-digitization renumbers everything

`oid_field: shape_id` (`MGM-P-001`…) is positional, assigned by `prepare.py`, and
matches the workbook's Shape ID column 67/67. It is stable **within** this extraction
only. A future edition or re-digitization renumbers from scratch — that is an
OID-unstable re-scrape and, per CLAUDE.md, an escalation: cross-extraction identity
needs a human decision, not a re-run.
