# discovery-tmng-map (israel gas)

Discovery leg of the INGL/TMNG-map ground-truth batch (2026-07-23). Two map lines
confirmed as genuine GEM misses after the Phase-1 crosswalk + match-to-existing check:

- **P8001 — Mari-B–Ashdod Gas Pipeline** (operating). The pre-existing 30-inch
  Mari-B / Yam Tethys export line (2002 licence, first gas Feb 2004) that Tamar
  hot-tapped into in 2013. The map's "Tamar→Ashdod" and "Mari-B→Ashkelon" lines are
  the SAME physical pipe → one row, not two. **Geometry deferred** (`RouteAccuracy =
  not mapped`): the map suggests Ashkelon but the licence + engineering sources say
  **Ashdod**, and length (~42 km) is single-lineage/unverified. Owner/parent open.
- **P8003 — Karish–Tanin FPSO Gas Export Pipeline** (operating, first gas 26 Oct
  2022). 90.3 km, dual 30/24 in, 8 bcm/y, Energean Israel Ltd 100%. Route candidate
  staged in `../route-creation-tmng-map/candidate_routes/P8003.geojson` (traced,
  medium; ends ~9.7 km short of Dor — nearshore/onshore is INGL's). Flag: check for a
  pre-existing gem.wiki "Karish and Tanin Fields Gas Sales Pipeline" page.

## Files
- `staged_new.json` — canonical pending state (full GGIT-schema rows, keyed by column name).
- `build_discovery.py` — rebuilds the deliverables from `staged_new.json`,
  `../validation-tmng-map/staged_edits.json`, the P8003 geojson, and the gas-tab
  snapshot header (maps by column NAME for drift-safety).

## Deliverables (batches/israel-gas/deliverables/)
- `pipelines_batch_20260723_1606_ET_israel-gas_discovery.xlsx` — two tabs:
  `Gas_NewRows` (131-col backend mirror, no leading SheetRow, paste-at-bottom;
  ref cells tier-colored green ≥2 independent / yellow single) and `Gas_EditFlags`
  (the 5 Phase-4 validation candidates, one flag per change — route through Update,
  never auto-apply).
- `pipelines_batch_20260723_1606_ET_israel-gas_p8001-mari-b-ashdod-wiki.txt`
- `pipelines_batch_20260723_1606_ET_israel-gas_p8003-karish-tanin-wiki.txt`
  (includes a `{{#display_map}}` block from the P8003 route candidate).

All URLs passed `scripts/url_verifier.py` 2026-07-23; three bot-walled/timeout URLs
(chevron.com, gascompressionmagazine.com, businesswire.com) were dropped — each
affected data point retains other 200-verified corroboration.
