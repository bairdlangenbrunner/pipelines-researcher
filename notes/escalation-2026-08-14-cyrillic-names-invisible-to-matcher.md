# Engine defect — the name axis was blind to Cyrillic

**Found** 2026-08-14, during the Ukraine gas §9 pass.
**Class** own-code defect (fix + re-run every affected scope; not a research finding).
**Files** `scripts/normalize.py`, `scripts/match.py`, `scripts/reconcile.py`.
**Scopes re-run** Ukraine gas OSM, Kazakhstan gas OSM. Nothing else on disk was affected.

---

## The defect

`normalize.normalize_name()` folds diacritics, lowercases, then does

```python
t = re.sub(r"[^a-z0-9]+", " ", t)
```

Every Cyrillic codepoint is outside `[a-z0-9]`, so a name written **only** in Cyrillic
normalizes to the **empty string**. The record is then not *mismatched* on the name axis —
it is **invisible** to it. `match._name_score()` returns `0.0` for an empty `ref_norm`
before it ever looks at the GEM variants, so `«Союз»` and `Soyuz Gas Pipeline` scored the
same as two unrelated pipes.

That alone would be a quiet accuracy loss. What made it undetectable was a second bug in
the health line. `reconcile._Diagnostics.note_ref()` counted

```python
if (r.get("name") or "").strip():   # the RAW name
    self.named += 1
```

so the diagnostic reported **"9.2% of reference records are named"** for a Ukraine run in
which the matcher could see a name on **effectively none** of them. `MATCH_QUALITY` fires
when the name and geometry axes are *both* mostly dead; it read the name axis as alive and
stayed silent through a run with a **0.1% overlap rate**. A diagnostic that reports the
data's view rather than the matcher's view cannot detect a blind axis — that is the
transferable lesson here.

## The fix

1. **`normalize.translit_cyrillic()`** (new) — a merged Ukrainian / Russian / Kazakh
   BGN/PCGN-flavoured romanization table, applied inside `normalize_name()` **before**
   `fold_diacritics`. It does not have to agree with any one romanization standard: both
   sides of a comparison go through it and the name axis is fuzzy (`token_set_ratio`), so
   `soyuz`/`soiuz` and `bogorodchani`/`bohorodchany` still score high. `г` is the one
   letter worth branching on — `h` in Ukrainian (Bohorodchany), `g` in Russian (Gazprom);
   the branch keys off the presence of `і ї є ґ`, which only Ukrainian has.
2. **`match.GENERIC_NAME_TOKENS`** — added the transliterated boilerplate
   (`hazoprovid`, `gazoprovod`, `mahistralnyi`, `nytka`, `vidhaluzhennia`, …). Without it,
   `Магістральний газопровід СОЮЗ` → `mahistralnyi hazoprovid soyuz` and `token_set_ratio`
   scores mostly on the two words that identify nothing: the pair scored **0.468** before
   the stoplist, **1.000** after.
3. **`reconcile._Diagnostics.note_ref()`** — counts `name_norm`, not `name`, so the health
   line reports the matcher's view and `MATCH_QUALITY` can actually see a dead name axis.

Scoring checks on real Ukraine OSM↔GEM pairs after the fix — `Роздільна - Ізмаїл` ↔
Rozdilna-Izmail **1.000**, `«Союз»` ↔ Soyuz **1.000**, `Кременчук - Ананьїв - Богородчани`
**0.984**, `Єлець - Кременчук - Кривий Ріг` **0.964**, `Диканька - Кременчук - Кривий Ріг`
**0.931**, `МГ Угерсько-Львів` **0.917**. Latin-only pairs are unchanged (Urengoy 0.957,
SOYUZ 1.000, Kobrin-Dolina 0.579), so there is no regression on the Latin corpus.

## Blast radius — bounded, and small

All 43 `canonical_records.json` on disk were scanned for Cyrillic. Exactly **two** scopes
carry any: **Ukraine gas OSM** (91 of 92 named records — the name axis was ~100% dead) and
**Kazakhstan gas OSM** (4 of 4 named records). Every GulfPub scope in the repo is fully
Latin. The **GEM side is fully Latin too** — zero Cyrillic in `PipelineName`,
`SegmentName`, `PipelineNetworkGrouping`, `OtherEnglishNames`, `StartLocation` or
`EndLocation` across both the gas and the oil/NGL snapshots — so the defect only ever hit
the reference side.

`name_norm` is computed at **ingest** time (`adapter_base.py`), so both scopes needed a
re-ingest, not just a re-reconcile.

## What actually changed (A/B, old workbook vs re-run)

**Ukraine gas OSM** — 1,004 reference records, joined 1,006 rows old↔new:

| | before | after |
|---|---|---|
| overlaps / additions / gem_only | 1 / 1003 / 46 | 1 / 1003 / 46 |
| dispositions | FRAGMENT 298, DISCOVERY 705 | NEAR_MISS 3, FRAGMENT 298, DISCOVERY 702 |
| "closest GEM (best guess)" changed | — | **49 records** |
| composite score rose | — | 94 records, mean **+0.071** |

**Kazakhstan gas OSM** — 112 reference records, joined 110:

| | before | after |
|---|---|---|
| overlaps / additions / gem_only | 2 / 110 / 50 | 2 / 110 / 50 |
| dispositions | FRAGMENT 55, DISCOVERY 55 | FRAGMENT 54, DISCOVERY 56 |
| best guess changed | — | **2 records** |

**No committed finding is falsified.** The bucket counts are identical in both countries;
what moved is the *attribution* column — which GEM row a reference trace is nearest to.
Those corrections are real and in the right direction:

- `Магістральний газопровід СОЮЗ` → was **Hust–Satu Mare**, now **Soyuz Gas Pipeline**
- `«Союз»` → was **Odessa-Chisinau**, now **Soyuz Gas Pipeline**
- `Холодна труба` → was **Yelets-Kursk-Kyiv**, now **Tula-Shostka-Kiev**
- `месторождение Шагырлы-Шомышты - компрессорная …` → was **Central Asia–Center**, now
  **Shagyrly-Shomyshty–Beineu** (Kazakhstan)

The reason the buckets barely moved is worth recording so nobody re-litigates it: the OSM
manifest's `gas_ua` / `gas_kz` blocks weight `name` at **0.10** against `geometry` 0.45 and
`endpoint` 0.30. A perfect name can lift a composite by at most 0.10, and the Ukraine
composite ceiling is 0.4949 against a 0.75 green threshold. Geometry was already carrying
these runs. **This is the correct reading, not a reason to retune the weights** — a 1,004-
fragment OSM extract against 51 GEM rows is a granularity problem, and the per-dataset
weights are the documented lever only when a *shared* block would move committed runs in
other countries.

## Deliverables

Re-run and re-issued at `20260814_0120_ET`; the predecessors moved to `archive/`:

- `batches/ukraine-gas/deliverables/pipelines_batch_20260814_0120_ET_ukraine-gas_reconciliation-osm.xlsx`
  (supersedes `…20260812_1409_ET…`)
- `batches/kazakhstan-gas/deliverables/pipelines_batch_20260814_0120_ET_kazakhstan-gas_reconciliation-osm.xlsx`
  (supersedes `…20260811_1043_ET…`)

The Ukraine and Kazakhstan **GulfPub** workbooks are untouched — both extracts are 100%
Latin.

## Rule to carry forward

**A health-line diagnostic must report the matcher's view of the data, never the data's
own.** `pct_reference_named` on the raw string is the reason a 0.1%-overlap run passed
without escalation. And when a reference extract is in a non-Latin script, the first thing
to check is whether `name_norm` survived the normalizer — an empty `name_norm` is silent,
and looks exactly like a source that simply has no names.
