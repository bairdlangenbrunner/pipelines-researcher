# Map ↔ GEM crosswalk — INGL transmission map vs GGIT Israel rows

Map: INGL "Transmission Map" (https://www.ingl.co.il/en/holancha/), full-res
`maps/ingl_big_map_fullres.jpg` (https://www.ingl.co.il/wp-content/uploads/2024/04/big-map.jpg,
fetched 2026-07-23; WP upload dated 2024-04; base map © Survey of Israel 2018).
Georeference: `georef_params.json` (ITM grid comb fit, ~92.5 m/px, anchors verified
against margin labels + landmarks). Overlays: `overlays/overlay_all.png` (+ per-PID).
The sheet's own disclaimer marks it schematic → traced geometry caps at medium.

GGIT snapshot: `(local snapshot) GGIT_gas_snapshot_20260723.csv` (22 Israel rows).

| # | Map system (label) | Map status | GEM row(s) | Verdict |
|---|---|---|---|---|
| 1 | Leviathan field line, fields→platform off Dor (קו משדה לויתן) | active supplier line | P7602/P7603 (I/II operating), P7604 (III construction), P7606 (IV proposed) | MATCH, **no geometry in routes repo → digitize (Phase 2)** |
| 2 | Karish–Tanin FPSO→INGL OOAT Dor (קו FPSO כריש-תנין) | active supplier line | — | **MISSING → discovery D3** |
| 3 | Tamar field→Ashdod (קו משדה תמר) | active supplier line | — | **MISSING → discovery D1** |
| 4 | Tamar/Mari-B→Ashkelon (קו משדה תמר/מרי B, Mari-B platform symbol) | active supplier line | — | **MISSING → discovery D2** (Yam Tethys system) |
| 5 | EMG Ashkelon–El Arish (אשקלון-אל עריש EMG) | active | P0462 (RouteAccuracy low, 27-pt) | MATCH — existing geometry tracks the drawn line; map corroborates; no redraw needed; Phase 4 flag on direction/status |
| 6 | Ashdod–Ashkelon marine + onshore tie (קו משדה תמר/מרי B area) | active | P3657/P3620 (applied 2026-07-23) | MATCH GOOD; P3620 Ashkelon 2.4 km gap NOT resolvable at 92 m/px (corridor corroborated only) |
| 7 | INGL onshore network: coastal, Jezreel/north, Jerusalem lateral, south to Sdom incl. Dead Sea Works crossing to Jordan | active / under construction | P3658 (network row, high) | MATCH GOOD — geometry covers all trunks incl. Sdom→Jordanian Dead Sea Works export; validate-only |
| 8 | Eastern trunk Elyakim/Hagit↔Ramle (via Regavim…Natbag) | active | P2197 (2-point straight chord!) | MATCH, **improve: real alignment exists inside P3658's network geometry → extract (Phase 2)** |
| 9 | Jordan Valley spur + border connection to Arab Gas line (עמק הירדן; חיבור לקו הגז הערבי dashed) | active + neighboring-country continuation | P0480 (2-point chord drawn as sea-crossing diagonal — wrong) | MATCH, **improve: redraw real alignment (Phase 2)**; P3658 red stops short of this spur — consistent if spur = P0480 |
| 10 | Land route to Egypt via Ashalim–Nitzana (תוואי יבשתי למצרים, pre-planning) | planned | P7864 (medium) | MATCH GOOD — corridor corroborated, no action |
| 11 | Gaza supply (planned light-blue via Tzalim–Gvulot–Kerem Shalom; Gaza PP symbol) | statutory planning | P5276 (medium; current geometry enters mid-strip near Re'im) | MATCH with **routing conflict → Phase 4 flag** |
| 12 | Jenin/West Bank planned spur (near ג'נין power symbol) | statutory planning | — | **MISSING → discovery D4** (planned; apply inclusion criteria) |
| 13 | Hadera LNG buoy line (מצוף ימי LNG→shore) | active | — | note-only: FSRU-buoy connection, short; likely out of GGIT pipeline scope |
| 14 | Future export route under gov't review (תוואי עתידי… ליצוא לאירופה, dotted Karish/Alon D→OOAT) | concept | P0479 Israel–Cyprus? | **Phase 4 flag**: verify what P0479 actually is (its 5-pt route passes Karish heading NW) |
| 15 | (off-map SW: Leviathan→Egypt subsea) | not drawn | P8000 (cancelled, staged) | consistent — no action |
| 16 | Misc short statutory-planning laterals (Tzalim, Gvulot, Kerem Shalom, ports) | planning | part of INGL future works | note-only |

GEM rows with no map presence (fine): EastMed P0827/P3206/P6889–P6894 (off-sheet
west/paper), P0479 (see #14), P7906-era history n/a.

## Work queues emitted

- **Phase 2 digitize/improve**: P7602+P7603 (trace map, medium; III/IV note-only),
  P0480 (redraw), P2197 (extract from P3658), [P0462/P3658: no-action, corroboration notes]
- **Phase 3 discovery**: D1 Tamar→Ashdod, D2 Yam Tethys/Mari-B→Ashkelon,
  D3 Karish→Dor, D4 Jenin spur (all confirmed absent from GGIT under
  PipelineName/SegmentName/OtherEnglishNames search 2026-07-23)
- **Phase 4 validation flags**: P5276 (Gaza routing/status), P0479 (identity/liveness),
  P7604/P7606 (construction/proposed progress), P0462 (reversal direction/status),
  P2197↔P3658 overlap bookkeeping (segment-vs-network note)
