# P8062 — null route placeholder (China gas)

Staged 2026-08-10 at Baird's instruction ("for MZ's P8062, just add a null route").

| | |
|---|---|
| ProjectID | P8062 |
| SheetRow | 4324 |
| Pipeline | Liaoning Gas Pipeline Network — *Dalian–Shenyang Gas Pipeline Dalian Branch* |
| Length / bore | 17 km / 610 mm, `operating` |
| Endpoints | Songlan → Dalian (Liaoning) |
| Current `RouteType` | `Not mapped (but could be — route or endpoints are known)` |
| Current `RouteAccuracy` | `no route` |

`candidate_routes/P8062.geojson` is a `geometry: null` feature — byte-for-byte the
routes repo's own `data/example-empty-route.geojson` convention, the same shape
`liquid-pipelines/P7326.geojson` already uses in production.

**No sheet write goes with this one.** Under the three-way-sync rule a null
placeholder is *not* mapped geometry, so `RouteType` must stay off `Mapped route (at
any accuracy)` and `RouteAccuracy` must stay `no route` — which is exactly what the
row already says. MZ's `RouteNotes`, `RouteCreator` and `Route [ref]` are already
populated and are left untouched; `RouteCreator` stays `MZ`, not `CB`, because no
geometry was created.

Destination on authorization: `data/individual-routes/gas-pipelines/P8062.geojson`
in `GOIT-GGIT-pipeline-routes`. Nothing else.
