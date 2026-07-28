# Escalation — the OPEC ASB is a per-pipeline table, not an aggregate: 8 Iraq "phantom" flags withdrawn

**Date:** 2026-07-28 · **Scope:** GGIT, Iraq, gas · **Ruling needed from Baird**
**Staged:** `batches/iraq-gas/staging/redundancy/staged_resolutions.json`
(19 `__VALIDITY__` records over 5 clusters; this memo covers clusters **A** and **E**)

## The finding — and it is a correction to my own earlier legs

This pass's row-by-row legs (`iraq-gas/annual`, `iraq-gas/ref-sweep-operating`)
flagged a large group of Iraq gas rows on a shared premise:

> The only citation is *"OPEC Annual Statistical Bulletin, p. 75"* — a country-level
> statistics compendium that **does not name individual pipelines**. The row may be a
> GEM construction with no external support. Candidate for deletion.

**That premise is false.** OPEC's ASB gas-pipeline table (Table 4.10 in ASB2012,
Table 9.9 in ASB2017) is a **per-pipeline table**. Its columns are:

```
Connection from/to | Owner or operator | Length | Diameter | Capacity | Throughput
```

One row per pipeline, each identified by its **endpoint pair**. It is not an
aggregate. Nine flagged rows are faithful transcriptions of named OPEC rows.

Two conclusions follow, and they run in opposite directions from the row-by-row legs:

1. **Nothing here is a phantom.** 8 existence flags are withdrawn — downgraded from
   *"possible GEM construction / deletion candidate"* to *"single-sourced, faithfully
   transcribed."* **Do not delete these rows.**
2. **But the parallel-naming duplicate theory also collapses** — OPEC lists both
   "families" as separate lines. The apparent name collision is GEM's ingest
   **truncating** the ASB name, not a double import. 4 duplicate flags withdrawn.

Net effect on the packet: 12 of the 16 duplicate/existence flags raised row-by-row
resolve to *no merge, no deletion*. One real duplicate survives (P4054 → P4066) and
one genuine aggregate/segment question stays open (P4061 vs P1852).

## Evidence 1 — the crosswalk: 13 GEM rows are 1:1 ASB rows

The full ASB2012 Iraq block, against GEM. **Nothing was matched on name similarity**
— the match is on the independent attribute pair (diameter, capacity), with length
handled per the companion length-units memo:

| ASB2012 "Connection from/to" | len | dia | cap (1,000 scm/yr) | GEM PID | GEM PipelineName | dia✓ | cap✓ |
|---|---|---|---|---|---|---|---|
| North Gas/Baiji | 90 | 24″ | 890,000 | P2231 | North Gas-Baiji | ✓ 24″ | ✓ 0.89 |
| Baiji-K3-/Al Kaem | 268 | 16″ | 2,410,000 | P1841 | Baiji-K3-Al Kaem | ✓ 16″ | ✗ 0.02 |
| Baiji/Al Mushraq | 131 | 18″ | 7,400,000 | P1842 | Baiji-Al Mushraq | ✓ 18″ | ✗ 1.64 |
| North Gas Co/K1 | 21 | 18″ | 5,264,000 | P2232 | North Gas-K1 | ✓ 18″ | ✓ 5.26 |
| North Gas Co/Taji | 272 | 16″ | 3,087,000 | P2233 | North Gas-Taji | ✓ 16″ | ✗ 1.53 |
| Taji/South Baghdad PWR St | 35 | 18″ | 2,000,000 | P1845 | Taji-South Baghdad | ✓ 18″ | ✓ 2.00 |
| Strategy/Kabesa Cement | 24 | 10″ | 671,000 | P1846 | Strategic-Kabesa Cement | ✓ 10″ | ✓ 0.67 |
| Strategy/Hilla PWR St | 45 | 16″ | 700,000 | P1847 | Strategic-Hilla | ✓ 16″ | ✓ 0.70 |
| Strategy/Najaf PWR St | 23 | 16″ | 2,100,000 | P1848 | Strategic-Najaf | ✓ 16″ | ✓ 2.10 |
| North Rumela/Khor Al-Zubair | 54 | 42″ | 10,000,000 | P2234 | North Rumela-Khor Al-Zubair | ✓ 42″ | ✓ 10.00 |
| Khor Al-Zubair/Hartha PWR St | 48 | 24″ | 4,808,000 | P1850 | Khor Al-Zubair-Hartha | ✓ 24″ | ✓ 4.80 |
| Rumela/Nasriyaha | 134 | 24″ | 10,420,000 | P1851 | Rumela-Nasriyaha | ✓ 24″ | ✓ 10.42 |
| Trans-Iraq/Nasriyaha | 292 | 42″ | 11,033,000 | P1852 | Trans-Iraq-Nasriyaha | ✓ 42″ | ✓ 11.03 |

**Diameter 13/13. Capacity 10/13, and all three misses are findings already on the
books, not evidence against the mapping:**

- **P1841** stores the right *number* (2.41) under the wrong *unit label* (`MMcf/d`
  instead of `bcm/y`), so the computed `CapacityBcm/y` reads 0.02 — already staged in
  the length memo. On the ASB **figure**, the match is 11/13.
- **P1842** and **P2233** carry an `iraqenergy.org` capacity ref — they were
  deliberately re-sourced. Ordinary two-source value conflict, left to Update triage.

**The naming rule is mechanical**, which is what makes the mapping certain rather than
merely plausible: GEM's name is the ASB connection string with `/` rewritten as `-`.
`Strategy/Hilla PWR St` → `Strategic-Hilla Gas Pipeline`. The clincher is
**`Baiji-K3-/Al Kaem` → `Baiji-K3-Al Kaem Gas Pipeline`** — the odd doubled hyphen in
OPEC's original survives verbatim into GEM. That is a transcription fingerprint; it
cannot arise by coincidence.

## Evidence 2 — two flags were `url_verifier` artefacts, not absences

Two rows were flagged after `url_verifier.py` failed to find their name token in the
ASB PDF. **The tokens are there.** `pdftotext` finds both:

```
asb2012_fresh.txt:6045  Strategy/Kabesa Cement   OPC   24   10   671,000      → P1846
asb2017.txt:8528        Strategic pipeline/Kabesa cement   OPC   24   10
asb2012_fresh.txt       Strategy/Najaf PWR St    OPC   23   16   2,100,000    → P1848
asb2017.txt             Strategic pipeline/Al-Najaf PWR St
```

**P1846 was called "a strong candidate for deletion."** It is a 10-inch line to a
cement plant, named in *both* ASB editions with a diameter and capacity GEM carries
exactly. It should not be deleted.

This is the **large-PDF limit** already documented in `docs/reference/source_roster.md`
biting a second time — the verifier cannot read deep into these files and returns a
content miss that reads like a content absence. Worth generalising: **a `url_verifier`
content miss on a large PDF is not evidence the value is unsourced.** The Libya pass hit
the same wall on the same publication.

Related: P1852 was flagged because *"every web trace of the exact name resolves back to
GEM itself."* True of the web — and the correct inference is the reverse of the one
drawn: the name is unusual on the web **because it is OPEC's internal connection
string**, not a name the trade press uses.

## Evidence 3 — cluster A: the two "families" are OPEC's, and GEM truncated the names

The other big row-by-row theory was that Iraq's gas rows contain a double import,
because two families of names target the same cities and were stamped in different
batches (2023-09-09 vs 2022-07-25). ASB2017's Iraq block lists them as **separate
rows, off two different trunks, at different diameters**:

| ASB2017 row | len | dia | GEM |
|---|---|---|---|
| Strategic pipeline/Hilla PWR St | 45 | 16″ | P1847 |
| Branch from Trans-Iraq dry gas pipeline/**Hilla-2** PWR St | 25 | 24″ | P4062 |
| Strategic pipeline/Al-Najaf PWR St | 23 | 16″ | P1848 |
| Trans-Iraqi dry gas pipeline/Najaf PWR St | 74 | 24″ | P4064 |

Two real trunk systems — the 1970s–80s **Strategic Pipeline** (tracked in GOIT as
P0542/P5244/P3876, "Iraq Strategic Pipeline" Pipelines 1/2/3, 42–48″) and the later
**Trans-Iraq dry gas pipeline** — each with its own branch to the same city, at its own
diameter.

**GEM's own oil tracker already models it this way**, which is the cleanest internal
precedent: GOIT carries P6256/P6257 (Strategic Pipeline–Daura Refinery, 18″/26″),
P6258 (–Al-Khairat Power Station, 14″), P6254 (–Musaiab Power Station, 16″) and P6255
(–Dhi Qar Refinery, 20″) as **separate rows**, one per branch, under exactly the
`Strategic Pipeline-<destination>` convention. Branches off a shared trunk are distinct
entities in GEM's practice, not duplicates of it. Note P6256/P6257 also confirm that a
*Daura* branch off the Strategic Pipeline exists on the oil side — a further reason not
to conflate Daura rows across trunks (relevant to cluster B).

The batch-date split is real but it
reflects **two ASB editions**: the P40xx rows appear for the first time in ASB2017.
They are *new lines added by OPEC between editions* — the opposite of a re-entry.

**The name collision has a mechanical cause, and it is a genuine defect worth fixing:**

```
ASB2017:  "Branch from Trans-Iraq dry gas pipeline/Hilla-2 PWR St"
GEM:      "Trans-Iraq-Hilla-Gas Pipeline"
                              ^^^^^  the "-2" and "Branch from" are gone
```

Hilla PWR St and **Hilla-2** PWR St are two different generating stations at Hilla
(Babil). With the "-2" dropped, a 25 km/24″ branch and a 45 km/16″ branch to "Hilla"
read as one pipeline entered twice. **Restoring the name is what stops a future pass
re-opening this merge** — it is the highest-value single edit in the cluster set. Staged
as `PipelineName → "Trans-Iraqi-Hilla-2 PWR St Gas Pipeline"`, matching sibling P4064's
existing style, with the old name to `OtherEnglishNames`.

## What is being asked for

| | rows | ruling |
|---|---|---|
| **Withdraw existence flag** (cluster E) | P1841, P1845, P1846, P1848, P1852, P2232, P2233, P4062 | do not delete; re-classify as single-sourced |
| **Withdraw duplicate flag** (cluster A) | P1847, P1848, P4062, P4064 | do not merge |
| **Fix the truncated name** (cluster A) | P4062 | one-cell rename, staged |
| **Confirmed duplicate** (cluster B) | P4054 → P4066 | merge; see caveat below |
| **Still open** (clusters C, D) | P4061/P1852, P4058 | human review, no edit staged |

The cluster-B and cluster-C/D items are not part of this correction; they are in the
same staging file and summarised there. Two things not to lose:

- **P4054's `Capacity` = 94 MMcf/d** has no counterpart in either ASB edition and none
  in its own map source. Carry it into P4066 only if it can be sourced — otherwise drop
  it deliberately, not silently.
- **P4058** (Eastern Iraq, 48″, 350 MMcf/d) is the one row where "single-sourced" really
  does shade into "unverified entity": blank endpoints, one presentation slide, and —
  unlike the 13 above — **absent from both ASB editions**, so this memo's argument does
  not rescue it.

## What stays true: single-sourced is still a real problem

Withdrawing "phantom" is not a clean bill of health. Every one of these rows rests on
**one source — the operator's own statistical return** — which fails the ≥2-independent
standard in `docs/reference/confidence_tiers.md`. Two concrete follow-ups:

1. **Re-point the dead citations.** The `opec.org` URLs now 404. The Wayback URLs below
   work and are already the established citation form from the length memo. This is
   part of the 41 `DEAD_LINK` re-pass, and it means several of those "dead links" have
   a known-good replacement rather than needing fresh research.
2. **Seek a second source per row** — Ministry of Oil, North Gas Company, or South Gas
   Company. Realistically low-yield for 10-inch branch lines to cement plants; the
   honest outcome for some of these is a documented single-source medium tier.

Note also that these rows and the 19 length-defect rows are **largely the same rows**.
Both memos describe the same ingest event: a 2022–23 bulk import of the ASB Iraq block
that transcribed the table accurately on diameter and capacity, mis-converted the
length column, and truncated some of the names.

## Sources

- ASB2012 (Table 4.10, Iraq block, p. 75) —
  `http://web.archive.org/web/20250110032615/https://opec.org/opec_web/static_files_project/media/downloads/publications/ASB2012.pdf`
- ASB2017 (Table 9.9, Iraq block) —
  `http://web.archive.org/web/20250206233526/https://www.opec.org/opec_web/static_files_project/media/downloads/publications/ASB2017_13062017.pdf`

Both return HTTP 206 `application/pdf` on a ranged fetch; **neither validates through
`url_verifier.py`** (large-PDF limit — see Evidence 2). Table text extracted locally
with `pdftotext` to `scratch/asb2012_fresh.txt` and `scratch/asb2017.txt`.

## Companion memos

- `notes/escalation-2026-07-28-asb-iraq-length-units.md` — the mi→km defect on 19 of
  these same rows.
- `notes/escalation-2026-07-28-asb-libya-length-units.md` — the same defect in Libya.
- The Libya redundancy pass (`batches/libya-gas/staging/redundancy/`) — same
  cluster-adjudication pattern; its cluster A is the aggregate-capacity-lower-than-its-
  own-segment signature that recurs here as Iraq cluster C.
