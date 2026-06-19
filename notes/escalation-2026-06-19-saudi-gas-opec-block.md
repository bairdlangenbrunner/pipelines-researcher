# Escalation — Saudi gas "P1897–P1925" block traces to a single non-pipeline source

**Date:** 2026-06-19 (ET) · **Tracker:** GGIT (gas) · **Scope:** Saudi Arabia
**Origin:** critical deep sweep `batches/pipelines_batch_20260619_1202_ET_saudi-arabia-gas-critical_deepsweep.xlsx`
**Decision owner:** Baird · **Engine never auto-applies — this is a flag, not an edit.**

## The systemic problem (escalation gate: "a whole class of GEM values looks systematically wrong")

29 consecutive gas rows — **P1897 through P1925** — are a single bulk-imported block, and
**starting from the sources the sheet itself cites**, the citations do not support the rows:

- **All 29 rows cite the OPEC Annual Statistical Bulletin** and almost nothing else
  (harvested from the gem.wiki pages): **29× ASB2012 p.75**, 10× ASB2013 p.79, 9× ASB2017
  p.136. Only **3 of 29** rows carry any non-OPEC citation at all (one Aramco history page,
  one link-rotted steel-network.com page).
- **The OPEC ASB is a country-level aggregate statistics table, not a pipeline inventory.**
  Its Saudi gas figures are total network length/counts — it does **not** name individual
  pipelines or list per-line length/diameter. Re-fetching ASB2012.pdf and running
  `url_verifier` for the pipeline tokens ("Abu Ali", "Berri", "Haradh", "Hawiyah",
  "pipeline") returns 200 but the tokens are **absent from the document body**. So the
  cited source cannot be where these names/lengths/diameters came from.
- **The names themselves betray a different, uncited origin.** Many are machine/GIS
  kilometer-post labels, not names any independent source uses:
  `UBTG-1-km0-UBTG-1-km56` (P1910/P1911), `UBTG-km56-AY-1 KP916` (P1900),
  `AY-1 KP 943-Riyadh` (P1903), `UA-1-km199-Uthmaniya` (P1908). These read as segments
  sliced out of an underlying route/GIS dataset whose identity is **not recorded** on the
  rows — the OPEC citation was attached on top of a different ingest.

**Conclusion:** this is not 29 independent sourcing failures — it is one import where a
generic OPEC statistic was pinned as the citation for rows whose real (unstated) source is
a route/segment table. Per-row ref-filling will keep failing because the rows were never
independently sourced to begin with. This needs a **provenance decision**, not row-by-row
patching.

## What IS real vs. what is synthetic

The sweep started from the sheet's refs, then corroborated against independent industry
sources (MEED, OGJ, Fluor, Saipem, offshore-technology, Saudipedia, Aramco). The corridors
are largely real; many of the **discrete rows** are not:

- **Real, correctly classified (keep — re-cite to working sources):** P1905
  Haradh–Uthmaniya (= MEED's "HDUG-1"), P1907 Haradh-3–Uthmaniya (OGJ ×2), P1913
  Abqaiq-B–Shedgum (OPEC ASB *does* list this one by name — re-cite to Wayback), P1915
  Hawiyah–Uthmaniyah (= MEED's "HUG-1"), P1916 Qatif North–Berri (OGJ/offshore-tech),
  P1920 Tinat–Haradh.
- **Real corridor, but the discrete km-post row is synthetic / GEM-only (no independent
  trace — pull the originating dataset before citing any spec):** P1900, P1903, P1906,
  P1908, P1910, P1911, P1912, P1918, P1922, P1924, P1925.
- **Likely duplicate / segment double-count (one physical right-of-way split into
  near-identical rows):** P1898/P1899 (UBTG-1-Berri ×2, same diameter set, ±2 km);
  P1910/P1911/P1912 (one km0→km56 corridor split by diameter); P1917/P1918/P1919 (three
  identical 43 km/30 in "Haradh Khuff–Hawiyah" rows, all citing only OPEC p.75);
  P1921/P7768 (two "Abu Ali–Berri" rows → one gem.wiki page with two infoboxes);
  P1922/P1923 (Berri↔Abu Ali, same 39 km split 8 in / 10 in).
- **Misclassified commodity (NGL/ethane/condensate recorded as dry gas):** P1897
  (Abqaiq–Yanbu NGL line, ties to the P3962/P3966 East–West finding); P1909 (ethane
  product line); P1921/P1922/P1923 (independent sources describe crude/condensate, not dry
  gas, for Abu Ali↔Berri).
- **Wrong province (mechanical Makkah→Eastern Province error across the block):** P1915,
  P1917, P1918, P1919 — Hawiyah/Haradh sit in the Ghawar complex (Eastern Province), the
  rows say Makkah.

## Decision requested

1. **Provenance.** Can you (or Aramco/GIS source-holders) identify the underlying
   dataset these km-post rows were ingested from? Everything downstream hinges on it.
2. **Disposition of the synthetic km-post rows** (P1900/P1903/P1908/P1910/P1911/P1912/
   P1922/P1925 etc.): re-source from the real dataset, or fold into their parent corridor
   as segments / `OtherEnglishNames`?
3. **Duplicate merges:** approve the merge candidates above (each is a single physical
   line split into multiple rows) — these are human merges, not engine edits.
4. **Re-citation:** for the ~6 confirmed-real rows, replace the dead/mis-attributed OPEC
   citations with the working independent sources the sweep already staged (in `Gas_Backend`).

Full per-row findings, recommendations, and staged sources: the `Gas_Validity` tab of the
deliverable. No edits have been applied to the live sheet.
