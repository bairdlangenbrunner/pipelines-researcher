#!/usr/bin/env python3
"""Adjudicate the `name_found` recheck (rule 4(a) relevance flags) — 14 flips, 1 accepted.

WHY THIS PASS EXISTS
--------------------
`recheck_name_found.py` re-ran `url_verifier --name` over the 27 verifications in this
store that carry `name_found: false`, to catch flags that were honest at the time but
are wrong now (a name form the original check missed, a page that changed, a fetch that
had failed). 14 of the 27 came back `true`. `merge_qc.relevance_qc` caps a unit at `low`
when EVERY verified ref on it says `name_found: false`, so each accepted flip lifts a
tier cap — which is exactly why every one of the 14 is adjudicated by hand here rather
than written back by the recheck script.

Verdict: **13 REJECTED, 1 ACCEPTED.** Two distinct false-positive mechanisms, both
reproduced before ruling. This file is the record so neither is re-litigated.

REJECTED CLASS 1 — the parent/system name form (11 flips, 9 rows)
-----------------------------------------------------------------
  P4781 Owner x2, P4782 Owner, P5859 FuelSource, P5861 Proposal/Start/Length,
  P5862 Length, P5865 Owner, P5866 FuelSource, P5886 Owner

Every one matched on a NETWORK-level name — `江西省天然气管网` (9) or `西气东输二线` (3) —
never on the row's own segment form. The cause is `recheck_name_found.py::name_forms_for`,
which pulls EVERY value out of the payload's `name_forms` dict, so the parent trunk's
name is fed in as "the row's name". But rule 4(a) is precisely that a page about the
parent trunk is NOT a ref for the "A–B" row, and these rows are branches and segments of
that network. So `name_found: false` was the CORRECT reading and stays: it means "this
document does not name THIS SEGMENT", which is what the flag is for. Several of the notes
already say so in as many words — P5865 and P5886 both call their ref "System-level
(company-wide) ownership-structure disclosure, not segment-naming", and P5861's Proposal
ref is a WEP2 progress story "with no mention of 新余, 高安 or any Jiangxi branch".

P5859 is worth spelling out, because its negative is not merely correct, it is EVIDENCE.
The qianzhan 2014 provincial plan names Phase I's six trunks — 九江-南昌、九江-沙河、
九江-景德镇、南昌-丰城、高安-新余、丰城-抚州 — and P5859 is 高安-丰城, which is not among
them. That absence is the qianzhan-vs-SSE-2023 Phase I decomposition conflict (qianzhan:
南昌-丰城 + 高安-新余; SSE 2023 bond disclosure: 南昌-新余 + 高安-丰城) still open at
P4777. Flipping this flag to `true` would have erased the datum.

REJECTED CLASS 2 — `url_verifier` matches Latin names against raw markup (2 flips)
----------------------------------------------------------------------------------
  P4752 __STATUS__, P4752 Operator [ref]

Both claimed `name_matched: 'Jiangxi-Fujian'` on Chinese-language government pages
(mee.gov.cn, jiangxi.gov.cn). Reproduced: a spy on `url_verifier.verify_url` shows the
name is matched against a surface of `len=61306`, `folded_tokens=7691`, beginning
`'<!doctype html>\n<html>\n<head>...'` — i.e. RAW HTML. `_match_surface` strips only
`<svg|style|template>` blocks; every tag, attribute and URL survives, and both
`'jiangxi'` and `'fujian'` appear as tokens there (host names, path segments, script
strings). On the tag-stripped PROSE of the same pages: 342 distinct Latin tokens, neither
`jiangxi` nor `fujian` among them, difflib >= 0.86 empty. So the Latin fuzzy path
(`_name_present`, per-token difflib) is matching markup, not text — a false positive by
construction on any name whose tokens collide with a hostname. Both P4752 notes had
already recorded the name as "correctly absent", one of them explicitly as a CORRECTION
to an earlier `name_found: true`. Flags stay `false`.

The verifier defect is filed as a defect, NOT fixed here: `scripts/url_verifier.py` is
shared by every batch and a mid-batch edit would move tiers in stores nobody is looking
at. It is written up in the run's report alongside the other owed verifier fix (retry
once over IPv4 on a 403 — `www.quannan.gov.cn` serves 403 over IPv6 and 200 over IPv4).

ACCEPTED — 1 flip
-----------------
  P5862 `Location [ref]`, matched `奉新支线` on the Wayback capture of Fengxin County's
  own 《奉新县碳达峰实施方案》.

This is a genuine correction, and the only flip that matched the row's OWN segment form
rather than its parent's. The record's own note already says `url_verifier --name
'奉新支线' OK 2026-09-10` while the stored flag reads `false` — the note was written from
a check the flag never received. The county government naming its own branch line is
exactly the identity rule 4(a) asks for.

Tier moves `low` -> `medium`, not `high`: the `low` was the relevance cap that this flip
lifts, and with one surviving publisher the independence half of the invariant caps the
unit at `medium` anyway. `independent` stays `False` for the same reason. `contains_value`
is untouched (already `True`) — a name check and a value check are separate questions.

Not in `ref_shards_recovery/` (checked, and asserted below): the recovery store wins the
merge, so a record there would have to be written too or the edit would not reach the
deliverable.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MARKER = "JIANGXI-NAME-FOUND-RECHECK-2026-09-10"

PID = "P5862"
COL = "Location [ref]"
URL = ("https://web.archive.org/web/20250124223928/http://www.fengxin.gov.cn/"
       "fxxrmzf/zcwj1b/202306/db62554375b54853a84e825920d67ef2.shtml")
FORM = "奉新支线"

VERIF_NOTE = (
    f"  [{MARKER}] name_found false -> true, name_matched '{FORM}': re-ran "
    f"url_verifier --name '{FORM}' 2026-09-10 and the county notice names its own branch "
    "line. The stored false was inconsistent with this record's own note, which already "
    "reported that check as OK. Reading of the document unchanged."
)

REC_NOTE = (
    f"\n\n[{MARKER}] RELEVANCE FLAG CORRECTED, tier low -> medium. The `low` on this "
    "unit was merge_qc's relevance cap (no verified ref names the pipeline), and it was "
    f"wrong: the ref -- Fengxin County's own 《奉新县碳达峰实施方案》 -- names {FORM}, the "
    "segment this row IS, not its parent network. Re-verified 2026-09-10. Medium and not "
    "high because one publisher survives on this unit, so the independence half of the "
    "invariant caps it at medium; independent stays no. This was the ONLY accepted flip "
    "of the 14 the name_found recheck produced -- 11 others matched only a parent/system "
    "name form (江西省天然气管网, 西气东输二线), which for a branch row is the correct "
    "negative, and 2 (P4752) were a url_verifier false positive on raw markup. See "
    "stage_name_found_recheck.py for the full adjudication."
)


def find(recs, ref_col):
    return [r for r in recs if r.get("ref_col") == ref_col]


def main(apply_it):
    # The recovery store wins the merge (run_merge_chain.sh step 2 passes ref_shards
    # then ref_shards_recovery), so a record for this unit there would silently
    # overwrite the flag this script sets. Stop rather than stage an invisible edit.
    rp = HERE / "ref_shards_recovery" / f"{PID}.json"
    if rp.exists():
        recs = json.loads(rp.read_text()).get("resolutions") or []
        if find(recs, COL):
            sys.exit(f"{rp}: has a {COL} record -- the recovery store wins the merge, so "
                     "this script must write it too. Stopping rather than staging a "
                     "change the deliverable would not show.")

    sp = HERE / "shards" / f"{PID}.json"
    payload = json.loads(sp.read_text())
    recs = payload.get("resolutions") or []

    if MARKER in sp.read_text():
        print(f"already applied (marker present in {sp.name}) -- nothing to do")
        return

    hits = find(recs, COL)
    if len(hits) != 1:
        sys.exit(f"{sp}: expected exactly 1 {COL} record, found {len(hits)} -- the store "
                 "drifted; re-read the recheck before adjudicating.")
    rec = hits[0]

    vs = [v for v in (rec.get("verifications") or []) if v.get("url") == URL]
    if len(vs) != 1:
        sys.exit(f"{sp}: expected exactly 1 verification for the Fengxin URL, found "
                 f"{len(vs)} -- the store drifted.")
    v = vs[0]
    if v.get("name_found") is not False:
        sys.exit(f"{sp}: name_found is already {v.get('name_found')!r}, not False -- "
                 "somebody else adjudicated this flip; stopping.")
    if rec.get("tier") != "low":
        sys.exit(f"{sp}: tier is {rec.get('tier')!r}, not 'low' -- this script was "
                 "written against the relevance cap it is lifting; re-read the record.")

    v["name_found"] = True
    v["name_matched"] = FORM
    v["note"] = (v.get("note") or "") + VERIF_NOTE
    rec["tier"] = "medium"
    rec["researcher_notes"] = (rec.get("researcher_notes") or "") + REC_NOTE

    print(f"  {PID} {COL}: name_found False -> True (name_matched '{FORM}'), "
          "tier low -> medium, independent unchanged (False)")
    print("  rejected, flags left False: P4752 __STATUS__ + Operator [ref] "
          "(url_verifier raw-markup false positive); P4781 Owner x2, P4782 Owner, "
          "P5859 FuelSource, P5861 Proposal/Start/Length, P5862 Length, P5865 Owner, "
          "P5866 FuelSource, P5886 Owner (parent/system name form -- correct negatives)")

    if apply_it:
        sp.write_text(json.dumps(payload, ensure_ascii=False, indent=1) + "\n")
        print(f"  wrote {sp}")
    else:
        print("  (dry run -- pass --apply to write)")


if __name__ == "__main__":
    main("--apply" in sys.argv)
