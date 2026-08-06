# Digitization packet — Bahr Essalam ↔ Mellitah corridor (P1855 gas 36″ / P6457 condensate 10″)

**Verdict: the Fanack / PetroGas Libya map CANNOT be georeferenced.** It is an
infographic, not a map to scale. Registration fails the §8 gate by 2×, and the
digitized geometry is demonstrably worse than what GEM already holds for P1855.
Packet retained because the *attribute* content of the map is usable and because
the exercise surfaced a real defect in **P6457** (see "Finding" below).

Source map (verified 2026-08-06, `url_verifier.py` → 200):
<https://petrogaslibya.com/wp-content/uploads/2026/01/Fanack_Libya_gas-production_Map_02.webp>
(local copy: `Fanack_Libya_gas-production_Map_02.webp`, 1471×1627 px)

## What was done

Rung ladder walked top-down (`docs/sops/route_creation.md`):

| Rung | Attempt | Result |
|---|---|---|
| 1 `sidecar` | GulfPub recon sidecars, Libya gas | no match for this corridor |
| 2 `osm` | Overpass `man_made=pipeline`, bbox `11.6,32.5,13.4,34.2` | **no offshore pipe** Mellitah→Bahr Essalam. Greenstream (w310845241, 500 km) and the onshore lines are present; the platform tie-back is not mapped in OSM |
| 3 `traced` | this packet | **FAIL** — see below |
| 4 `endpoints` | blocked: no *citable* public coordinate found for the Sabratha platform (OSM has Bouri DP3/DP4/SPM seamarks but no Sabratha node; NGA Pub. 113 List of Lights 2019 lists Bouri Oilfield SPM #21700 + E/W platform RACONs, no Sabratha entry; MarineTraffic port 25956 is 403; operator page gives distance only) |

### Rung 3 method

Map features were extracted **by colour segmentation, not by eye** — yellow
node discs, red town dots (intensity-weighted centroids), and the green
pipeline stroke's centreline sampled every 20 px. Legend box and locator inset
were masked out. GCP lon/lat come from OSM Nominatim geocoding of the *named
place*, never off the image (`gcps.json` carries a `source_ref` each).

- `gcps.json` — 9 GCPs: Tripoli, Misrata, Surt, Gela, Mellitah, Ras Ajdir
  (Libya/Tunisia border landfall, taken as the NW corner of the Libya fill
  polygon), Isola delle Correnti, Malta, Gozo. Condition number 1.06 — spread
  is good, so the failure is the map's, not the GCP layout's.
- `trace.json` — 15-vertex pixel polyline, Bahr Essalam node → Mellitah node.
  The drawn line is straight to within ~2 px (≈1 km) of its chord.
- `georef_report_order{1,2}.json`, `P6457_traced_order{1,2}.geojson`.

## Why it fails

| Fit | RMSE | LOO RMSE | max residual | gate |
|---|---|---|---|---|
| order 1 (affine) | **10.35 km** | 16.71 km | 19.39 km (Mellitah) | ≤5 km → **FAIL** |
| order 2 (quadratic) | 7.20 km | **36.10 km** | 14.54 km (Mellitah) | **FAIL** (LOO shows overfit) |

Gate = `max(5 km, 2% × 109 km)` = 5 km.

Three independent confirmations that the map has no consistent scale:

1. **Pairwise scale varies ~2×.** Ras Ajdir→Mellitah 0.377 km/px;
   Mellitah→Tripoli 0.734; Tripoli→Misrata 0.599; Misrata→Surt 0.537. The map
   draws Ras Ajdir→Mellitah 1.5× *longer* than Mellitah→Tripoli when reality is
   0.77×.
2. **The trace contradicts the map's own label.** Digitized length is
   **162.8 km** (order 1) / 163.0 km (order 2) against the map's own
   "110km" annotation and GEM's `LengthKnownKm` 109 — +48%.
3. **The Bahr Essalam node is on the wrong side of Mellitah.** Real azimuth
   Mellitah→field is **022°** (NNE; field lon ≈12.66 E, east of Mellitah's
   12.22 E — corroborated by the OSM Bouri seamarks at 12.61–12.68 E, the
   adjacent field). The map draws it at **−025°** (NNW). The traced terminus
   lands 101–106 km from the actual field.

Do not re-attempt this map. A different published source (or a citable platform
coordinate enabling rung 4) is the only way forward.

## What the map IS good for — attributes, not geometry

Corroborated independently by the operator, Mellitah Oil & Gas
(<https://mellitahog.ly/en/sites/sabratha-platform/>, verified 200):

- **Two pipelines in one corridor**, platform → Mellitah: gas **ø36″** and
  oil & condensates **ø10″**. Map: "110km / Gas pipeline ø36" / Oil &
  condensates ø10"". Operator: "36'' pipeline to Mellitah plant" and "A 10-inch
  condensate pipeline … to Mellitah for further treatment and export".
- Sabratha platform 110 km from the Libyan coast, 190 m water depth, Bahr
  Essalam field (Block NC-41).
- → 2 independent sources agree ⇒ **high** confidence on the 36″/10″ pairing
  and the ~110 km length for both P1855 and P6457.

## Finding — P6457 route geometry is wrong (name collision)

`P6457.geojson` ("Sabratha-Mellitah Condensate Pipeline", `LengthKnownKm` 107):

```
[[12.463719, 32.792894], [12.24166, 32.855794]]   # 2 vtx, geodesic 21.9 km
```

- Length ratio **0.20** — far outside the integrity band `[0.75, 1.33]`.
- Its start point is **2.2 km from the Roman ruins of Sabratha**
  (OSM node 1207279002 "Museo Romano Sabratha", 12.4832, 32.8037) and
  **109.9 km from the Sabratha *platform***. The route was drawn to the ancient
  city, not the offshore facility — a "Sabratha" name collision.

By contrast **P1855** (same corridor, gas 36″) is sound: 3 vtx, geodesic
105.5 km vs `LengthKnownKm` 109 (ratio 0.97), starting offshore at
12.6906, 33.7238 in the Bahr Essalam field.

**Proposed fix (needs Baird's decision — NOT staged):** P6457 should follow the
P1855 corridor, since the operator states both the 36″ gas line and the 10″
condensate line run platform→Mellitah. That means reusing P1855's geometry for
P6457 — the same "reuse an existing PID's geometry" review pattern as China
P3894, so it is a human call, not an auto-replacement. It would be a
`--replace` candidate (existing accuracy is `very low (straight line/schematic)`,
not `high`/`very high`, so replacement is permitted rather than an escalation),
and `RouteAccuracy` would rise to match whatever P1855 earns.
