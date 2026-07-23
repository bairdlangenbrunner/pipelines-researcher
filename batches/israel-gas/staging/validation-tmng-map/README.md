# validation-tmng-map (israel gas)

Phase-4 targeted validation of rows the INGL/TMNG-map crosswalk flagged as conflicted
or thin (2026-07-23). **All findings are candidate edits for the Update SOP — none is
auto-applied.** Canonical pending state: `staged_edits.json`. Findings surface in the
`Gas_EditFlags` tab of `../../deliverables/pipelines_batch_20260723_1606_ET_israel-gas_discovery.xlsx`.

- **P7604** Leviathan Subsea III — Status **construction→operating** (completed ~3 Mar
  2026; field capacity ~12→14 Bcm/yr). High confidence + ResearcherNotes flag.
- **P7606** Leviathan Subsea IV — Status **no_change** (proposed; Phase 1B Stage 2,
  pre-FID) + flag.
- **P0479** Israel–Cyprus — Status no_change (proposed; distinct from EastMed);
  **EndLocation "Energean Power FPSO"→"Vassiliko"** (mislabel); Capacity 4 bcm/y flagged
  for re-verification; OtherEnglishNames add.
- **P5276** Gas for Gaza — Status no_change (proposed; war-suspended since Oct 2023);
  **route do-NOT-auto-replace** flag (GEM's mid-Strip alignment is better supported by
  the Wadi Gaza EIA than the schematic INGL map).
- **P0462** El Arish–Ashkelon (EMG) — Status/locations/years no_change (reversed flow
  already correct). **Parent relabel** (Egyptian Natural Gas Co→East Gas Company; Chevron
  33.54%→9.75%; resolve unknown block→legacy EMG shareholders); Diameter value_add 26 in
  / 660 mm (needs 1 more source); ResearcherNotes cleanup (replace garbled OCR text).

All URLs passed `scripts/url_verifier.py` 2026-07-23. businesswire.com timed out and is
noted in the P0462 Parent ref list with a "verify against primary" caveat (that edit is
a candidate routed to Update anyway).
