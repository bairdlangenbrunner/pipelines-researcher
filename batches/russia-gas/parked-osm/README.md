# Parked: Russia gas OSM reconciliation

Parked on 2026-10-02 at Baird's direction. OpenStreetMap is not a reliable reference
for pipelines, so no more OSM reconciliation is planned. These files are kept for a
possible later look. They are not part of any deliverable.

- `deliverables/pipelines_batch_20260930_1504_ET_russia-gas_reconciliation-osm.xlsx`: the
  standalone OSM reconciliation workbook (5,520 features, 135 overlaps, 5,385 additions,
  224 GEM-only rows, 8 status conflicts, 4 route-replacement candidates).
- `staging/recon-osm-20260930/`: the staged match output behind the workbook. The health
  line was `MATCH_CONCENTRATION`: one routeless row, P3894, was the nearest row for 1,822
  records, so every "nearest PID" there is arithmetic, not geography.
- `staging/osm_ru_fetch.log`: the log from the Overpass pull.

This folder sits outside `staging/`, so the review app, `staged_summary.py` and the
batch index do not read it. To bring it back, move `staging/recon-osm-20260930` back
under `batches/russia-gas/staging/` and the workbook back into `deliverables/`.

The Russia discovery seeds (`staging/discovery-seeds-20260930/`) were partly built from
this recon's unmatched OSM features. The discovery results were not changed.
