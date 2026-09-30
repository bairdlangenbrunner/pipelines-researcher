#!/usr/bin/env python3
"""Canonicalise the batch's FuelSource spellings, and rule on P4789.

WHY THIS EXISTS. After the Ganzhou South Branch ruling landed
(stage_fuelsource_ruling.py), an inventory of every staged FuelSource value in
this store against the live snapshot found the same handful of upstream systems
spelled nine different ways -- '川气东送 (Sichuan-East Gas Transmission
Project)', '川气东送 (Sichuan-to-East Gas Transmission Project)', 'West-East Gas
Pipeline II (西气东输二线)', 'West-East Gas Pipeline Line 2', and so on. Each
spelling was defensible where it was written; together they make the column
unusable for the one thing a FuelSource cell is for, which is saying WHICH
upstream system feeds this pipe in a form that resolves.

THE CANONICAL FORM, and it is the tracker's own, not an invention. GGIT's
PipelineName vocabulary spells these systems:

    Sichuan–Shanghai Gas Pipeline            (19 rows; EN DASH U+2013)
    Sichuan–Shanghai Parallel Gas Pipeline   (20 rows; the 复线/二线, NOT this)
    West-East Gas Pipeline 1 / 2 / 3         (10 / 27 / 15 rows; ASCII hyphen,
                                              arabic numeral, no CJK gloss)

So: arabic numerals not roman, ASCII hyphen in 'West-East' and an EN DASH in
'Sichuan–Shanghai', title case, ', ' between multiple sources. 川气东送 is
'Sichuan–Shanghai Gas Pipeline' -- that is GEM's English name for the Sinopec
Puguang->Shanghai trunk, and P4649/P4657 are those very rows, so a FuelSource
cell reading 'Sichuan–Shanghai Gas Pipeline' now resolves to a pipeline the
tracker actually holds, which '川气东送 (Sichuan-East Gas Transmission Project)'
never did.

NO CJK GLOSS IN THE CELL. This is a deliberate style call and it goes the way
the Ganzhou ruling already went: the four Ganzhou rows carry a bare
'West-East Gas Pipeline 2, West-East Gas Pipeline 3', P4944/P4946 carry a bare
'West-East Gas Pipeline 2', and the batch cannot have one half of its
FuelSource cells glossed and the other half not. The Chinese identifier is not
lost -- it stays in each record's verification notes (where a re-verifier needs
it, against Chinese-language sources) and in the row's own
OtherLanguageAlternativePipelineNames. Note this decides FuelSource only; the
separate English-vs-CJK Owner1 inconsistency (P4934/P4947 CJK vs P4944/P4946
English) is still open and is NOT pre-empted here.

WHAT A SPELLING CHANGE DOES TO A VERIFICATION FLAG -- read this before
re-verifying any of these rows. `contains_value` on these records was set by a
human reading a Chinese-language document and finding it state the source; it
was never a substring test against the English cell. Rewriting the cell from
'川气东送 (Sichuan-East Gas Transmission Project)' to 'Sichuan–Shanghai Gas
Pipeline' therefore does not weaken any flag -- the referent is identical and
the note quotes the sentence -- but it does mean a mechanical re-check with
--expected 'Sichuan–Shanghai Gas Pipeline' will come back FALSE on every one of
these refs, because the pages are in Chinese and say 川气东送. That is a false
negative, not a lost ref. `name_found` is untouched by any of this: it is a
statement about the PIPELINE name (the row), not about the FuelSource value.

GROUP A -- canonicalised here (13 records, spelling only, referent unchanged):
    P4776 P4778 P4781 P5859   川气东送 (Sichuan-East ...)        -> Sichuan–Shanghai Gas Pipeline
    P4780 P4782               川气东送 (Sichuan-to-East ...)     -> Sichuan–Shanghai Gas Pipeline
    P4783 P4784 P5889         Puguang Gas Field / ... (川气东送)  -> Puguang Gas Field, Sichuan–Shanghai Gas Pipeline
    P4790                     West-East Gas Pipeline II (西气东输二线)  -> West-East Gas Pipeline 2
    P5860                     West-East Gas Pipeline III (西气东输三线) -> West-East Gas Pipeline 3
    P5866                     West-East Gas Pipeline Line 2 and Sichuan-to-East Gas Transmission
                                                                 -> West-East Gas Pipeline 2, Sichuan–Shanghai Gas Pipeline
    P5887                     West-East Gas Pipeline Line 2      -> West-East Gas Pipeline 2
The Puguang rows keep BOTH the field and the trunk: gem_schema.md defines
FuelSource as the upstream field/plant feeding the line, the same DRC plan that
sources the trunk names 普光气田 as its origin, and dropping either half would
lose sourced information. Only the '/' becomes ', ' and the name becomes the
tracker's.

Eleven of these thirteen have a BLANK live cell (P4776 P4778 P4780 P4781 P4782
P4783 P4784 P4790 P5859 P5860 P5889), so their staged string is our own new
value and canonicalising it changes nothing for the reviewer. Only P5866 and
P5887 rewrite a live cell, and both are unambiguous: 'Line 2' and '2' are the
same line, 'Sichuan-to-East Gas Transmission' and 'Sichuan–Shanghai Gas
Pipeline' are the same trunk.

GROUP B -- the P4789 narrowing, which is a RULING, not orthography. P4789
(二期工程 井冈山支线, Jizhou->Jinggangshan, 129 km) carries the live three-part
value 'West-East Gas Pipeline 2, West-East Gas Pipeline 3, Sichuan-Shanghai Gas
Pipeline' and its record delivered UNRESOLVED/low with both refs flagged
contains_value=false -- which means merge_qc would strip both and the row would
ship a value with no ref at all. Its own note says why: two independent sources
confirm West-East 2 and nothing anywhere confirms the other two parts. That is
precisely the shape rule 4(e) forbids -- UNRESOLVED means nothing was found,
never that something narrower was found. So the ruling:

  VALUE -> 'West-East Gas Pipeline 2'. class UNRESOLVED -> REFS_ADDED,
  tier low -> medium, independent -> True, both refs' contains_value -> true.

  (1) jxgajc.com (Wayback 2022-10-02), 江西赣安检测技术有限公司 completion-
      acceptance disclosure, names 井冈山支线 -- THIS row -- and names its inlet
      as 西气东输二线吉安分输清管站. Segment-level, names the row, states the
      feed. Same publisher and document class as the segment-level ref that
      carries P5866.
  (2) CCXI 2022 credit report footnote 1: '管道分公司承接西气东输二线气源的
      二期管网工程' -- the whole Phase II network, which this branch belongs to,
      is fed from 西气东输二线. Network-level, different publisher and class.
  (3) NEGATIVE, and it is what licenses dropping two thirds of the cell:
      no document opened for this row (china5e, sohu, SSE, qianzhan, CCXI,
      jxgajc) attributes West-East 3 or 川气东送 to 井冈山支线. West-East 3 is
      not absurd in Jiangxi -- the Ganzhou ruling establishes 瑞金分输清管站
      承接西气东输三线来气 -- but that is the Ganzhou south branch's feed point,
      340 km away, and Jinggangshan's is 吉安 off West-East 2. 川气东送 belongs
      to PHASE I under CCXI's own operator split (天然气管道公司), and this is a
      Phase II row (管道分公司). The three-part string is a network-wide
      FuelSource list mechanically carried onto a branch row, exactly as this
      record's __VALIDITY__ already suspected.

  Both contains_value flags flip to true. They were false because they were
  judged against the THREE-part value, which neither source supports; against
  the narrowed value both notes state the value in as many words. The question
  changed, not the reading -- and the notes below record that so nobody reads
  the flip as a hand-edit. Tier medium rather than high because only ref (1)
  names the segment; ref (2) is network-level. That is the same convention
  P4776 and P4783 state on their own records.

  This also disposes of an orthography defect for free: the dropped third part
  was spelled 'Sichuan-Shanghai Gas Pipeline' with an ASCII hyphen, which the
  tracker spells with an EN DASH nowhere else.

GROUP C -- P4777, one romanisation fix. Both P4777 and P4779 carry the same
live prose about the 九江 terminal of the 黄梅 branch; P4779's staged value
already corrects the sheet's 'Jiujian' to 'Jiujiang', P4777's does not. 九江 is
Jiujiang; 'Jiujian' is not a place. One letter, and it makes the two rows agree.

GROUP D -- one sentinel on P4779, recording a cross-row evidentiary tension
that no record currently holds. See P4779_NOTE.

DELIBERATELY NOT TOUCHED, and each for a reason:
  P4785 P4786 P4787 P4788  already canonical (the Ganzhou ruling set them).
  P4944 P4946              already canonical, high, branch-level refs.
  P4649                    already canonical ('Sichuan–Shanghai Gas Pipeline',
                           EN DASH, 3 refs, high). NOT self-referential: the row
                           is the 川气东送江西支线 (Huangmei-Jiujiang), a BRANCH,
                           and a branch fed off its parent trunk is what the
                           cell says.
  P4793 P4794 P4795 P4796 P4797  bare 'West-East Gas Pipeline'. It LOOKS like
                           an under-specification an orthography pass should fix
                           by adding the '2' -- and that would be wrong. Every
                           one of these five rows carries a __VALIDITY__ record
                           disputing whether it is a West-East 2 branch at all
                           rather than a Phase-I 川气东送-fed provincial branch;
                           P4794's own note says 'NOT changing this value here',
                           P4795 declines to propose any value, and P4796 is
                           capped low partly because the 2014 DRC plan states
                           West-East 2's Jiangxi footprint covers '除景德镇外的
                           10个设区市' -- all ten prefectures EXCEPT Jingdezhen,
                           which is this row's endpoint. Adding the '2' would
                           harden the contested attribution under cover of a
                           spelling fix. The trailing space the live cells carry
                           is already stripped in the staged values, so nothing
                           is owed here.
  P5861                    retired into P4778 by the retirement ruling.
  P5862                    'West-East Gas Pipeline', but the row is
                           一期工程 奉新支线 -- PHASE I, which CCXI maps to
                           川气东送, not West-East. Its record already logs that
                           as a live conflict and its existence is separately in
                           question (赤岗-奉新 attested nowhere). A spelling pass
                           must not settle either.
  P4657 P4661              prose / 'Sichuan Basin'. A basin and a supply-mix
                           sentence are legitimate FuelSource contents; the
                           column carries plenty of both tracker-wide.
  P4777 P4779 (values)     prose kept. The Phase-I trunk decomposition ruling
                           (qianzhan vs SSE 2023) is owed on P4777 and a phase
                           check on P4779; converting either to a bare name
                           before those land would destroy sourced detail
                           (P4779's jdzmc ref names the 黄梅——九江 branch at
                           segment level) and pre-empt the ruling.
  P4928 P4931 P4934 P4947  Central-Asia prose. These rows' upstream genuinely
                           is imported gas plus Xinjiang coal-to-gas, not a
                           pipeline name -- there is nothing to canonicalise TO.

Runs BEFORE split_shards.py: it rewrites shards/, which split_shards.py
regenerates ref_shards/ and rows/ from. None of the records it touches exists in
ref_shards_recovery/ (only P4787 and P4934 have FuelSource records there, and
neither is in scope), so unlike the Ganzhou ruling this needs no recovery-store
copy -- checked, not assumed, and the check is re-run below so a future recovery
pass that adds one cannot silently win the merge.

Not named normalize_*.py on purpose: the normalize_* scripts in scripts/ are
generic and run against any store, this one is batch-specific and marker-keyed.

    python3 stage_fuelsource_orthography.py            # dry run
    python3 stage_fuelsource_orthography.py --apply
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
MARKER = "JIANGXI-FUELSOURCE-ORTHOGRAPHY-2026-09-10"
COL = "FuelSource [ref]"

CQDS = "Sichuan–Shanghai Gas Pipeline"   # EN DASH, the tracker's own spelling
WEP2 = "West-East Gas Pipeline 2"
WEP3 = "West-East Gas Pipeline 3"

# old -> new, keyed on the exact staged string so the script no-ops the moment a
# record is already canonical (and so a record whose value drifted is reported
# rather than silently rewritten).
SPELLINGS = {
    "川气东送 (Sichuan-East Gas Transmission Project)": CQDS,
    "川气东送 (Sichuan-to-East Gas Transmission Project)": CQDS,
    "Puguang Gas Field / Sichuan-East Gas Transmission Project "
    "(川气东送)": f"Puguang Gas Field, {CQDS}",
    "West-East Gas Pipeline II (西气东输二线)": WEP2,
    "West-East Gas Pipeline III (西气东输三线)": WEP3,
    "West-East Gas Pipeline Line 2 and Sichuan-to-East Gas Transmission":
        f"{WEP2}, {CQDS}",
    "West-East Gas Pipeline Line 2": WEP2,
}

GROUP_A = ["P4776", "P4778", "P4780", "P4781", "P4782", "P4783", "P4784",
           "P4790", "P5859", "P5860", "P5866", "P5887", "P5889"]

ORTHO_NOTE = (
    f"  [{MARKER}] SPELLING CANONICALISED, referent unchanged: {{old!r}} -> "
    "{new!r}. The target is the tracker's own PipelineName vocabulary "
    "(Sichuan–Shanghai Gas Pipeline with an EN DASH, 19 rows; West-East Gas "
    "Pipeline 1/2/3 with arabic numerals, 10/27/15 rows), so the cell now names a "
    "system the tracker actually holds. CJK glosses are deliberately out of the "
    "CELL and stay in these notes -- the batch's other FuelSource cells (the four "
    "Ganzhou rows, P4944, P4946) carry bare English and the column cannot be half "
    "glossed. NOTHING about the evidence changed: contains_value on the refs below "
    "was set by reading a Chinese-language document, never by substring-matching "
    "the English cell, so a mechanical re-check with --expected on the new value "
    "will come back FALSE against these Chinese pages. That is a false negative, "
    "not a lost ref. name_found is unaffected -- it is a claim about the PIPELINE "
    "name, not the FuelSource value.")

P4789_NOTE = (
    f"[{MARKER}] ORCHESTRATOR RULING: FuelSource NARROWED to '{WEP2}' and the "
    "record moved UNRESOLVED/low -> REFS_ADDED/medium, independent. This record "
    "reasoned correctly and then stopped one step short of what rule 4(e) "
    "requires: it found two independent sources confirming West-East 2, found "
    "nothing for the other two parts of the sheet's three-part value, and filed "
    "UNRESOLVED -- but UNRESOLVED means nothing was found, never that something "
    "narrower was found. Left as it stood, merge_qc strips both refs "
    "(contains_value=false on each) and the row ships a value with no citation at "
    "all, which is the orphan the no-orphan rule exists to prevent. THE EVIDENCE, "
    "all of it already on this record: (1) jxgajc.com via Wayback 2022-10-02, "
    "江西赣安检测技术有限公司's "
    "completion-acceptance disclosure, names 井冈山支线 -- THIS "
    "row -- and names its inlet as "
    "西气东输二线吉安分输清管站, "
    "i.e. West-East 2's Ji'an pigging station. Segment-level, names the row, "
    "states the feed; same publisher and document class as the segment-level ref "
    "carrying P5866. (2) CCXI 2022 credit report footnote 1, "
    "'管道分公司承接西气东输二"
    "线气源的二期管网工程' -- the entire "
    "Phase II network, which this branch is part of, is fed from West-East 2. "
    "Network-level, different publisher and class. (3) THE NEGATIVE, which is what "
    "licenses dropping two thirds of the cell: no document opened for this row "
    "(china5e, sohu, SSE, qianzhan, CCXI, jxgajc) attributes West-East 3 or "
    "川气东送 to 井冈山支线. West-East 3 is "
    "real in Jiangxi -- the Ganzhou South Branch ruling establishes "
    "瑞金分输清管站 taking West-East 3 gas -- but that "
    "is a feed point 340 km away serving a different branch, and this branch's own "
    "inlet is 吉安 off West-East 2. 川气东送 belongs to "
    "PHASE I under CCXI's own operator split "
    "(天然气管道公司), and this is a Phase II row "
    "(管道分公司). So the three-part string is a network-wide "
    "FuelSource list mechanically carried onto a branch row -- which is what this "
    "row's own __VALIDITY__ record already suspected. THE contains_value FLIP IS "
    "NOT A HAND-EDIT: both flags were false because they were judged against the "
    "THREE-part value, which neither source supports. Against the narrowed value "
    "both verification notes state the value in as many words. The question "
    "changed; neither source's reading did, and both readings stand verbatim "
    "below. TIER medium, not high, because only ref (1) names the segment -- ref "
    "(2) is network-level; that is the convention P4776 and P4783 state on their "
    "own records. Incidentally disposes of an orthography defect: the dropped "
    "third part was spelled 'Sichuan-Shanghai Gas Pipeline' with an ASCII hyphen, "
    "which the tracker uses nowhere. --- SUPERSEDED PRIOR NOTE: ")

P4777_NOTE = (
    f"  [{MARKER}] ROMANISATION FIX: 'Jiujian' -> 'Jiujiang' in the FuelSource "
    "prose. 九江 is Jiujiang; 'Jiujian' is not a place, and P4779 -- which "
    "carries the same sentence off the same sheet -- already staged the correction, "
    "so the two rows disagreed on the spelling of the same terminal. Value "
    "otherwise untouched: the prose is deliberately NOT converted to a bare "
    "pipeline name, because the Phase-I trunk decomposition ruling (qianzhan's "
    "南昌-丰城 + 高安-新余 against SSE 2023's "
    "南昌-新余 + 高安-丰城) is still owed on this "
    "row, and because this record's own note already flags that the sheet's extra "
    "specificity -- gas arriving via the 九江 terminal of the "
    "黄梅支线 -- is unsourced by any of its three refs. Both of "
    "those are rulings, not spellings.")

P4779_NOTE = (
    f"[{MARKER}] FLAGGED, NOT STAGED: this row's own second ref names a SECOND "
    "feed that the FuelSource cell omits, and it collides with P4796's finding. "
    "jdzmc.com 2009 (already cited on this record) reads "
    "'九江——景德镇输气管线工"
    "程的资源基础主要是川气东"
    "送江西支线黄梅——九江管"
    "线工程和西气东输二线' -- the "
    "九江-景德镇 line's resource base is BOTH the "
    "川气东送 Jiangxi branch (Huangmei-Jiujiang) AND West-East 2. "
    "The cell names only the first. The record used the West-East 2 half as "
    "corroboration and did not record it as an omission, so it would otherwise be "
    "lost. THE COLLISION worth a human eye: P4796 "
    "(余江-景德镇, the OTHER pipeline into the same city) is "
    "capped at tier low partly because the 2014 provincial DRC plan states "
    "West-East 2's Jiangxi footprint covers "
    "'途经除景德镇外的10个设区市' "
    "-- all ten prefecture-level cities EXCEPT Jingdezhen, which is P4796's own "
    "endpoint. A 2009 segment-level "
    "source putting West-East 2 gas into Jingdezhen and a 2014 provincial plan "
    "excluding Jingdezhen from West-East 2's footprint cannot both be describing "
    "the same thing -- most likely the 2009 document means West-East 2 gas "
    "reaching the city THROUGH the provincial network rather than a West-East 2 "
    "pipe entering it, which is exactly the Phase-I/Phase-II attribution question "
    "P4793-P4797 are all stuck on. NOT staged as a value: adding West-East 2 to "
    "this cell asserts a resolution of that question, and this record's job was "
    "the ref, not the ruling. Route with the Phase I/II per-segment "
    "reconciliation.")


def find(recs, ref_col, pid):
    hits = [r for r in recs if r.get("ref_col") == ref_col]
    if len(hits) != 1:
        sys.exit(f"{pid}: expected exactly 1 {ref_col!r} record, found {len(hits)}")
    return hits[0]


def sentinel(pid, sheet_row, note):
    # value-less, refs-less, tier medium / independent False -- same shape and same
    # reasoning as the retirement ruling's sentinels: the evidence lives on the
    # records this one points at, and a value-less record verifies to zero refs
    # under the strict basis, so independence_qc would demote a `high` anyway.
    return {"project_id": pid, "sheet_row": sheet_row, "ref_col": "__VALIDITY__",
            "value_col": None, "value_cols": [], "values": {}, "proposed_value": None,
            "class_out": "CONFIRMED", "kind": None, "tier": "medium",
            "independent": False, "proposed_refs": [], "verifications": [],
            "researcher_notes": note}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    # guard: if a later recovery pass ever stages a FuelSource record for a row in
    # scope, the recovery copy WINS the merge (merge_ref_shards.py is
    # last-writer-wins and run_merge_chain.sh passes ref_shards then
    # ref_shards_recovery), and rewriting only shards/ would change nothing in the
    # deliverable -- the failure mode the Ganzhou ruling hit. Fail loudly instead.
    scope = set(GROUP_A) | {"P4789", "P4777", "P4779"}
    for p in sorted((HERE / "ref_shards_recovery").glob("P*.json")):
        if p.stem not in scope:
            continue
        recs = json.loads(p.read_text()).get("resolutions") or []
        if any(r.get("ref_col") == COL for r in recs):
            sys.exit(f"{p}: has a {COL} record and is in scope -- the recovery store "
                     "wins the merge, so this script must write it too. Stopping "
                     "rather than staging a change the deliverable would not show.")

    touched, changes = {}, []

    def load(pid):
        if pid not in touched:
            path = HERE / "shards" / f"{pid}.json"
            touched[pid] = (path, json.loads(path.read_text()))
        return touched[pid][1]

    if MARKER in (find(load("P4776")["resolutions"], COL, "P4776")
                  .get("researcher_notes") or ""):
        print("already applied (marker present in shards/P4776.json) -- nothing to do")
        return

    # --- Group A: spelling only -------------------------------------------------
    for pid in GROUP_A:
        rec = find(load(pid)["resolutions"], COL, pid)
        old = (rec.get("values") or {}).get("FuelSource")
        if old not in SPELLINGS:
            sys.exit(f"{pid}: staged FuelSource {old!r} is not one of the spellings "
                     "this script was written against -- the store drifted; re-run "
                     "the inventory before normalising.")
        new = SPELLINGS[old]
        rec["values"] = {**rec["values"], "FuelSource": new}
        if rec.get("proposed_value") is not None:
            rec["proposed_value"] = new
        rec["researcher_notes"] = ((rec.get("researcher_notes") or "")
                                   + ORTHO_NOTE.format(old=old, new=new))
        changes.append(f"{pid} {COL}: {old!r} -> {new!r}")

    # --- Group B: the P4789 narrowing ------------------------------------------
    rec = find(load("P4789")["resolutions"], COL, "P4789")
    old = (rec.get("values") or {}).get("FuelSource")
    rec["values"] = {**rec["values"], "FuelSource": WEP2}
    rec["value_cols"] = ["FuelSource"]
    rec["proposed_value"] = WEP2
    rec["kind"] = "REF"          # live cell carries a value, [ref] is empty
    rec["class_out"] = "REFS_ADDED"
    rec["tier"] = "medium"
    rec["independent"] = True
    for v in rec.get("verifications") or []:
        v["contains_value"] = True
        v["note"] = ((v.get("note") or "") + f"  [{MARKER}] contains_value false -> "
                     "true: judged against the row's THREE-part value, which this "
                     "source does not support; against the narrowed "
                     f"'{WEP2}' it states the value in as many words, above. "
                     "Reading unchanged.")
    rec["researcher_notes"] = P4789_NOTE + (rec.get("researcher_notes") or "")
    changes.append(f"P4789 {COL}: UNRESOLVED/low {old!r} -> REFS_ADDED/medium "
                   f"{WEP2!r}, 2 refs kept (contains_value flipped), independent")

    # --- Group C: P4777 romanisation -------------------------------------------
    rec = find(load("P4777")["resolutions"], COL, "P4777")
    old = (rec.get("values") or {}).get("FuelSource") or ""
    if "Jiujian " in old:
        rec["values"] = {**rec["values"],
                         "FuelSource": old.replace("Jiujian ", "Jiujiang ")}
        rec["researcher_notes"] = (rec.get("researcher_notes") or "") + P4777_NOTE
        changes.append("P4777 FuelSource: 'Jiujian terminal' -> 'Jiujiang terminal'")
    else:
        changes.append("P4777 FuelSource: no 'Jiujian' to fix -- skipped")

    # --- Group D: the P4779 sentinel -------------------------------------------
    recs = load("P4779")["resolutions"]
    row = find(recs, COL, "P4779").get("sheet_row")
    recs.append(sentinel("P4779", row, P4779_NOTE))
    changes.append("P4779: +1 __VALIDITY__ sentinel (omitted West-East 2 feed; "
                   "collides with P4796's Jingdezhen exclusion)")

    for c in changes:
        print("  " + c)
    if not args.apply:
        print("\ndry run -- re-run with --apply")
        return
    for pid, (path, doc) in sorted(touched.items()):
        path.write_text(json.dumps(doc, ensure_ascii=False, indent=1),
                        encoding="utf-8")
    print("\napplied to " + ", ".join(f"shards/{p}.json" for p in sorted(touched)))


if __name__ == "__main__":
    main()
