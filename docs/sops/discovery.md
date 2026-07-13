# SOP — Discover new pipelines

Find pipeline projects **not** in GOIT/GGIT and stage them as candidate new rows.
Reconciliation `Additions` (reference-only rows) feed directly into this SOP —
**but first try to match each one to an existing GEM pipeline under a different
name** (capture as `OtherEnglishNames`); only genuine misses become discoveries.

Deep search + route-research rules live in the methodology,
`docs/GOIT_Pipeline_Research_Workflow.md` Phase 3.

## Inputs
- Region/country scope; whether to include early-stage proposals.

## Sequence
1. `scripts/refresh_csvs.sh`; build a dedup index of existing rows for the scope.
2. **Search strategies** (methodology Phase 3): operator project pages; regulators
   (FERC/PHMSA/MARAD/BOEM/Texas RRC or national equivalents); EIA / government data;
   industry news (`"<country>" new oil pipeline <year>`); offshore/subsea FIDs;
   cross-border projects.
3. **"Sufficient information to add" threshold** — a candidate qualifies only with
   (a) an identified sponsor, (b) at least country + region/endpoint, and (c) a
   concrete step (MOU, FEED award, permit applied, tender). Below threshold → a
   `monitor_list` sheet, not a new row.
4. **Route / map research** per `docs/reference/route_conventions.md`: official
   GIS first; else digitized visual maps; assign `RouteAccuracy` on the ladder;
   fill `RouteType`/`RouteNotes`/`Route [ref]`. (Capacity expansion, no new pipe →
   `no route`.)
5. Collect all GEM columns with verified `[ref]` URLs for each discovery.
6. `scripts/url_verifier.py` on all URLs; `scripts/entity_lookup.py` on every new
   owner/operator/parent.
7. Stage `batches/staging/<scope-slug>/staged_new.json`; build
   `…_<scope>_discovery.xlsx` (new rows green-tinted); `recalc.py`; present.

**Owner/operator refs on a new row have no tab home.** Owner/operator `[ref]`s live on the
ProjectID-keyed operators/owners tab, which doesn't yet have a row for a not-created discovery.
So a staged `Owner [ref]` is **dropped from the `<Cmdty>_NewRows` mirror but preserved in
`staged_new.json`** — Baird adds it to the operators/owners tab after the new row gets a ProjectID.

## Escalate
If discovery surfaces more than ~5 candidate clusters in one country (a systematic
gap), pause and discuss scope before generating many new records.
