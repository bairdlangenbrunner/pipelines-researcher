# Escalation — GulfPub↔GEM matching is unreliable for Iraq; its "status conflicts" are artifacts

**Date:** 2026-07-28 · **Scope:** GulfPub reconciliation, Iraq, `--commodity both`
**Trigger:** CLAUDE.md — *"A reference disagrees on >10% of matched rows (material conflicts)"*
**Verdict:** gate tripped numerically (**13 of 39 = 33%**) but **not materially**. The
conflicts are matching errors, not data disagreements. **Do not act on the conflict list.**
**Staged follow-up:** `batches/iraq-gas/staging/recon-gulfpub-followup/`

## Why the 33% is not a data finding

**Zero of the 13 conflicts sit on a green match.** All 13 are `yellow`, composite
0.455–0.653 — and the run only produced **4 green matches out of 39 overlaps**.

Worse, matches collapse many-to-one. GEM rows absorbing multiple GulfPub records:

| GEM row | GulfPub records absorbed |
|---|---|
| **P2233** North Gas-Taji Gas Pipeline | **6** |
| **P7906** Kirkuk—Haifa Oil Pipeline | **4** |
| P3876, P5240, P1848, P7437 | 2 each |

Four demonstrably impossible matches, by inspection:

| GulfPub record | matched to | why it's wrong |
|---|---|---|
| `gas:105204` Akkas Gas Field (CPF) – Anbar CCP Plant | P7436/P7437 **Artawi** GMP | Akkas is in **Anbar** (west); Artawi is in **Basra** (south), ~500 km apart |
| `gas:105207` Erbil – Dohuk Gas Pipeline | P4047 **Khormor-Erbil** | GEM's Erbil–Duhok line is **P4053**; the right row exists and was not chosen |
| `gas:3339` Mansuriyah – Kirkuk | P2233 **North Gas-Taji** | Mansuriyah is a Diyala field; Taji is near Baghdad |
| `oil:549/550/3705/3706` four short Kirkuk gathering lines | all → P7906 **Kirkuk—Haifa** | a historic retired line to Haifa, absorbing four live local lines |

## Root cause

Two Iraq-specific properties defeat the matcher, and they compound:

1. **GEM's Iraq names are endpoint-generated and highly collinear** — "Kirkuk", "Strategic",
   "Rumaila", "Trans-Iraq", "North Gas" recur across many rows, so name-token similarity
   scores 0.6–0.7 against the *wrong* row routinely.
2. **34 of 54 Iraq gas rows have no drawn route**, so `geometry_weight` cannot
   disambiguate — several conflicts show `g_untested: true` and fall back to the
   `geometry_untested_score` floor (0.15). Name then decides the match essentially alone.

This is the same structural weakness noted for OSM Iraq (`sources/osm/NOTES.md`), from the
same cause: missing GEM geometry, not a bad source.

## Consequence that matters: false matches MASK real additions

A GulfPub record that mis-matches is reported as an *overlap with a status conflict*
instead of an **Addition**. Two probable genuine GEM gaps were hidden this way — neither
"Mansuriyah" nor "Jera Pika" appears anywhere in GEM's 54 Iraq gas rows (checked across
PipelineName, SegmentName, OtherEnglishNames, and the other-language name fields):

- `gas:3339` **Mansuriyah – Kirkuk Pipeline** (proposed)
- `gas:3837` **Jera Pika – Mansuriyah Pipeline** (proposed)

Both need the Discovery 2-independent-source test. **The reported 8 Additions therefore
understate the real gap** — treat 8 as a floor, not a count.

## Resolved by hand and staged

1. **Akkas ≡ Okaz — a transliteration gap, not a missing pipeline.** GEM spells the Anbar
   field **"Okaz"**; the dominant English spelling is **"Akkas"**, with **"Akkaz"** and
   **"Akaz"** also in independent use. Because "Akkas" and "Okaz" share no name token, the
   matcher could not reach GEM's own rows for the field and mis-matched to Artawi instead.
   Staged: add `Akkas Gas Pipeline; Akkaz; Akaz` to `OtherEnglishNames` on **P4401, P7460,
   P7466, P7467**. Also recommended (not applied): normalise the primary name to "Akkas".
   - Sources (all pass `url_verifier`): [Iraq Business News, "Work Begins on Akkas Gas
     Pipeline" (2022)](https://www.iraq-businessnews.com/2022/08/22/work-begins-on-akkas-gas-pipeline/);
     [MEES, "Anbar Power Plants To Build Case For Akkas Gas"](https://www.mees.com/2022/8/26/power-water/anbar-power-plants-to-build-case-for-akkas-gas/471db9c0-2532-11ed-9686-9f98e897bfab);
     [Power Technology, "Akaz Power Plant, Iraq"](https://www.power-technology.com/marketdata/power-plant-profile-akaz-power-plant-iraq/).
     Iraq Business News maintains both `/tag/akkas/` and `/tag/akkaz/`. Same field: عكاز,
     discovered 1992, ~5.6 Tcf, near the Syrian border, feeding the Anbar combined-cycle
     plant through a ~250 km dry-gas line (SEPCOIII).
   - **Note the staging shape:** GGIT has **no name-level `[ref]` column** (none of the 22
     ref columns covers names), so these four fills carry **no ref cell** and the
     attestation lives in `ResearcherNotes`. That is deliberate — writing a ref into an
     unrelated column would be an orphan ref.
2. **P4053 status, re-attached.** `gas:105207` "Erbil – Dohuk" (operating) belongs on
   **P4053** (GEM: `construction`), not P4047. Staged as a concern, not a flip: GulfPub is
   Tier 2 and never reaches green alone, but it independently corroborates the pre-existing
   country-note flag that P4053 should be `operating`. Route to Update for the 2-source
   test. (Separately, P4053's diameter is contested — OSM and vemak.com.tr give 36″ against
   GEM's "52″ confirmed".)

## Recommendations

1. **Do not use the Iraq GulfPub status-conflict list to drive any status change.** Use the
   4 green matches, plus manual review of Additions.
2. **Do not retune the shared `matching:` weights to fix this.** GulfPub's weights are
   global; loosening name weight or the untested-geometry floor would alter the committed
   Libya, Egypt, Saudi and Iran results. If Iraq needs different behaviour it should be a
   per-dataset override, which the manifest does not currently support — that is a
   framework change to scope deliberately, not a quick edit.
3. **The real fix is GEM-side geometry.** 34 of 54 rows with no route is the binding
   constraint; every extra drawn route improves matching for *all* sources at once.
4. **Re-run Iraq reconciliation after the Akkas aliases land** — `gas:105204` should then
   match the Okaz rows and drop off both the conflict and Addition lists.
5. Send **Mansuriyah–Kirkuk** and **Jera Pika–Mansuriyah** to Discovery.
