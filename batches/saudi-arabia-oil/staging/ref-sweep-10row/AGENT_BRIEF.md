# Ref-sweep research brief — Saudi Arabia oil, 10-row batch

You research the reference cells for ONE ProjectID and stage one resolution per unit.
Repo root: `/Users/baird/Dropbox/_git_ALL/_github-repos-gem/pipelines-researcher` (cd there).

## Inputs (read these)
- Your units: `batches/staging/ref-sweep-saudi-arabia-10row/worklist.json` → filter
  `units` to `project_id == <YOUR_PID>`. Each unit has: `ref_col`, `value_cols`,
  `primary_value_col`, `values`, `primary_value`, `current_ref`, `class` (HAS_REF or
  MISSING_REF), `kind`, `tab` (present+="operators_owners" for Operator/Owner [ref]
  units), `sheet_row`, `oo_sheet_row` (OO units only), `pipeline_name`, `segment_name`,
  `wiki`.
- Candidate source pool: `batches/staging/ref-sweep-saudi-arabia-10row/wiki_citations.json`
  → the outbound external citations harvested from this row's gem.wiki page (your starting
  point; many may be dead — verify each).

## Rules (NON-NEGOTIABLE)
1. **Never cite GEM** (gem.wiki, globalenergymonitor.org), **theodora.com**, or
   **A Barrel Full / `abarrelfull.wikidot.com` (or any `wikidot.com` page)**. These are
   tertiary aggregators. You may READ them for leads but never put them in a ref.
   `url_verifier` rejects all of these.
2. **Never fabricate a URL.** If you can't verify ≥2, stage UNRESOLVED with a
   ResearcherNotes reason — no invented links.
3. **Every URL must pass the verifier** before you stage it:
   `python scripts/url_verifier.py "<url>" "<expected substring>" ["<more>"]`
   → prints `OK ... 200` only if it resolves AND contains the expected substrings.
   Use distinctive, language-agnostic tokens as expected substrings (numbers, years,
   diameters, capacities, place names). For owner/operator units use the company name.
4. **Corroborate with ≥2 independent sources** (separate origins — NOT the same wire
   story reprinted, NOT two pages both citing GEM). Tier:
   - ≥2 independent working + value-present → `tier:"high"`, `independent:true`
   - 1 strong working + value-present → `tier:"medium"`, `independent:false`
   - 1 weak / partial / conflicting → `tier:"low"`, `independent:false`
   - none verifiable → UNRESOLVED
5. **Search in Arabic too** where English is thin (Aramco Arabic press, Argaam, SPA,
   صحيفة). Foreign pages still must pass the verifier; record `source_language`.

## Per-unit procedure
- **HAS_REF** (existing ref to re-verify): run the existing `current_ref` URL(s) through
  the verifier (with the value as expected substring).
  - all live AND contain the value AND ≥2 independent → `class_out:"REVERIFIED"`,
    `proposed_refs:[]` (keep current_ref), `tier:"high"`.
  - a live link but only ONE source → find a 2nd independent one; if you reach 2 →
    REFS_ADDED with both; if not → REVERIFIED at medium (note the single-source gap).
  - any dead / value-missing link → `class_out:"DEAD_LINK"`; put a verified replacement
    in `proposed_refs` (and any still-good originals).
- **MISSING_REF** (blank ref): research from the citation pool + web search; verify; reach
  the ≥2-independent target → `class_out:"REFS_ADDED"`. If impossible → `"UNRESOLVED"`.
- **Owner/Operator units** (`tab=="operators_owners"`): the value is a company
  (Operator / Owner1). Find ≥2 independent sources confirming that company
  operates/owns THIS pipeline. Same tiers. These refs land on the operators/owners tab.

## Output (write exactly this)
Write `batches/staging/ref-sweep-saudi-arabia-10row/rows/<YOUR_PID>.json` = a JSON list,
one object per unit, each carrying ALL original unit fields PLUS:
```json
{
  "project_id": "...", "sheet_row": 277, "oo_sheet_row": 485,
  "pipeline_name": "...", "segment_name": "...", "wiki": "...",
  "ref_col": "Capacity [ref]", "value_cols": [...], "primary_value_col": "Capacity",
  "values": {...}, "primary_value": "...", "current_ref": "...",
  "tab": "operators_owners",                         // omit/null for tracker units
  "class_in": "MISSING_REF",                          // = original "class"
  "class_out": "REFS_ADDED",                          // REFS_ADDED|REVERIFIED|DEAD_LINK|UNRESOLVED
  "proposed_refs": ["https://...","https://..."],     // [] for a clean REVERIFIED
  "verifications": [ {"url":"https://...","ok":true,"contains_value":true} ],
  "tier": "high",                                     // high|medium|low (omit for UNRESOLVED)
  "independent": true,
  "source_language": "en",                            // or "ar", "en,ar"
  "researcher_notes": "what you found / why this tier / any GEM divergence"
}
```
Carry every key from the input unit. Keep `oo_sheet_row` only for owner/operator units.
Before finishing, `python -c "import json; json.load(open('.../rows/<YOUR_PID>.json'))"`
to confirm it parses. Return a 2-line summary: counts by class_out, and any UNRESOLVED.
