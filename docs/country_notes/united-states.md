# United States

Crude + NGL (GOIT) and a very large gas network (GGIT). Richest regulatory data of
any country — use it for both attributes and routes.

## Regulators / official data
- **FERC** eLibrary (`elibrary.ferc.gov`) — interstate gas/LNG.
- **PHMSA** — safety + the National Pipeline Mapping System (`npms.phmsa.dot.gov`)
  for routes.
- **MARAD** — deepwater ports (export terminals).
- **BOEM** (`data.boem.gov`) / **BSEE** — offshore/OCS pipelines + permits.
- **Texas RRC** GIS viewer; **Alaska DNR** State Pipeline Coordinator.
- **EIA** — petroleum & natural-gas project tracking.

## Routing / GIS tips
- NPMS, Texas RRC, and BOEM give traceable routes (`high`/`medium`).
- Gulf of Mexico subsea lines: use OCS block coordinates for `low`-accuracy
  endpoints (e.g. Green Canyon 19 ≈ 27.88°N, 89.17°W). Offshore Magazine's annual
  GoM map and the Enbridge interactive map help.

## Gotchas
- **Deepwater crude export terminals** — four competing projects (SPOT, Texas
  GulfLink, Blue Marlin, Bluewater Texas): track MARAD license, EPA CAA permits, and
  FID *separately*; the pipeline component may have no new onshore pipe.
- **GoM deepwater 2024 FIDs** (Canyon Oil, Rome, Oceanus) — subsea, limited route
  data; low-accuracy routing from block coords.
- **Conversions** (e.g. Double H → Hiland Express): note as a conversion in
  `RouteNotes`; the existing route may already be in PHMSA/GEM.

## Open items
- Keep deepwater-export terminal pipeline components distinct from the terminal
  records (LengthKnown often 0 — onshore expansion only).
- **Staged, NOT applied (oil):** Delaware Express update batch (P7995 Targa NGL +
  P0354 Medallion→Plains Oryx — same name, NOT duplicates: different commodities/
  owners/vintages; researched 2026-06-12, `batches/united-states-oil/staging/update-delaware-express/`) and
  Permian Express I–IV batch (P0113/P2581/P2660/P2661 — Parent split 87.7/12.3,
  Operator = Sunoco Pipeline L.P., PE1 capacity 200k→150k bpd, PE2 StartLocation
  Wichita Falls→Midland, PE4 zeroed as expansion; researched 2026-06-11,
  `batches/united-states-oil/staging/update-permian-express/`).
