#!/usr/bin/env python3
"""Make every `cross_row_leads[]` target a single real PID, or move it off the contract.

`collect_leads.py` groups leads by `project_id` and re-verifies each URL against the
TARGET row's name forms. A target that is not one PID therefore cannot route: it
becomes its own bogus group, reported `in scope: False`, name-verified against
nothing. 18 leads were in that state -- researched findings that could never reach
the row they were about. `validate_shards.py` only caught EMPTY targets, so the
whole class was invisible; it now checks the shape too.

Three transforms:

  1. COMMA LISTS -- "P4785,P4786,P4787,P4788" becomes one lead per PID, each keeping
     the full facts text plus `split_from`. Purely mechanical.

  2. RESOLVED PROSE -- a lead whose target was a prose cohort or a placeholder, but
     which names a segment identifiable in the live tab, is routed to the PID(s) it
     actually describes. Every mapping below was made by matching the segment string
     in the lead against `SegmentName` / `OtherLanguageAlternativeSegmentName` on the
     44 in-scope rows, and each carries a `resolved_by` note so the mapping is
     auditable rather than implicit.

  3. BATCH-LEVEL -- a lead addressed to a cohort with no single row (a discovery
     guard, a systematic-labelling hypothesis, a document useful to a whole phase)
     moves to a new top-level `batch_leads[]` array. Those are the ORCHESTRATOR's to
     act on, and are transcribed into orchestrator_notes.md; keeping them in
     `cross_row_leads[]` only made them look routable when they were not.

The archive.org `screenshot-*` items are a special case worth stating: their
descriptions correctly identify seven Jiangxi segments, and that is real routing
information -- but the items are GEM staff uploads, i.e. GEM surfaces, so standing
rule 1 forbids ever citing them. They are routed with a NOT-CITABLE prefix so the
receiving row uses the description as a search hint and nothing more.

Run with the other normalizers, BEFORE split_shards.py.
"""
import json, pathlib, re, sys

HERE = pathlib.Path(__file__).resolve().parent
NOT_CITABLE = ("NOT CITABLE -- archive.org screenshot-* items are GEM staff uploads, "
               "i.e. a GEM surface (standing rule 1). Use the description below as a "
               "hint toward the underlying document; never put this URL in a [ref]. ")

# (shard, lead index) -> (targets, prefix, resolved_by)   [] targets = batch-level
RESOLVE = {
 # -- the seven IA screenshot descriptions, each matched to a live segment name --
 ("P4779", 1): (["P4787"], NOT_CITABLE, "'二期工程, 赣州南支线 (龙南-全南段)' == P4787 OtherLanguageAlternativeSegmentName"),
 ("P4779", 2): (["P4784"], NOT_CITABLE, "'永修-武宁-修水支线' == P4784 'Phase I, Yongxiu-Wuning-Xiushui Branch'"),
 ("P4779", 3): (["P4792"], NOT_CITABLE, "'宜丰-铜鼓支线' == P4792 'Yifeng-Tonggu Branch' (NOT P5888, which is 万载-铜鼓)"),
 ("P4779", 4): (["P5860"], NOT_CITABLE, "'西三线于都分输站-宁都-广昌-南丰输气管线' == P5860 OtherLanguageAlternativeSegmentName verbatim"),
 ("P4779", 5): (["P5863"], NOT_CITABLE, "'干洲-奉新支线' == P5863 OtherLanguageAlternativeSegmentName"),
 ("P4779", 6): (["P5886"], NOT_CITABLE, "'一期工程, 沈贵里-彭泽支线' == P5886 'Phase I Shenguili-Pengze Branch'"),
 ("P4779", 7): (["P5889"], NOT_CITABLE, "'一期工程，蔡岭-都昌支线' == P5889 'Cailing-Duchang Branch'"),
 # -- system-level context, offered by its own author to the trunk parents --
 ("P4779", 0): (["P4657"], "", "the lead names P4657 itself ('e.g. P4657/other trunk-parent rows'); "
                              "system-level 2008 Phase I launch article, aggregate-vs-segment rule applies"),
 ("P4779", 8): ([], "", "the CCXI 2022 qixin PDF is already a kept ref on 14 rows in this run "
                        "(P4776/P4777/P4778/P4779/P4781/P4782/P4783/P4784/P4785/P4791/P4792/P5859/P5862/P5864/P5865/P5866) "
                        "-- nothing to route, and see the single-origin caveat in orchestrator_notes"),
 # -- batch-level: cohort hypotheses and discovery guards, no single row --
 ("P4791", 1): ([], "", "systematic Phase-II-label hypothesis for Jingdezhen/Shangrao prefectures -- a batch ruling"),
 ("P4791", 2): ([], "", "duplicate of the same seven IA screenshots resolved from P4779 above"),
 # NOTE the index: P5862's shard was rewritten by its own agent after this table was
 # first written, which moved this lead from #4 to #7. Keys are positional, so a stale
 # one silently falls through to the generic fallback -- hence the STALE-KEY GUARD below.
 ("P5862", 7): ([], "", "explicitly a discovery guard, and CONFIRMED against the live gas tab "
                        "(snapshot 20260910, 986 China rows, all seven name columns): 余干 = 0 hits, "
                        "安义 = 0, 安远 = 0. The two apparent hits are NOT these segments -- 靖安 "
                        "occurs only inside P4786's garbled OtherLanguageSegmentName paste fragment "
                        "(see the P4785-P4790 defect in orchestrator_notes), and 定南 only in "
                        "P4790's '赣州南支线（信丰-龙南-定南段）', a Xinfeng-Longnan-Dingnan pairing "
                        "distinct from the tendered 安远-定南段. So all three are genuinely absent "
                        "from the tracker, not present under another name; they go to the discovery "
                        "cluster. The same jxsggzy sweep also establishes P5862's negative: "
                        "奉新 = 0, 赤岗 = 0, 干洲 = 0, 石鼻 = 0 across 1,097 gas notices (2016-11 to 2025-02)."),
 ("P5866", 4): ([], "", "the 2014 DRC plan is a whole-phase ProposalYear source; routing it needs a "
                        "blank-ProposalYear scan, so it is a batch item, not one row's lead"),
 ("P5866", 5): ([], "", "the 46% holder correction is already the standing BATCH-LEVEL RULING; the lead's "
                        "own single-origin caveat (SSE 242696 + CCXI 2022 are both 中诚信国际) is the new part"),
 ("P5866", 6): ([], "", "prefecture-level FuelSource corroboration that names no branch -- supports many "
                        "Jiujiang rows, sources none of them alone"),
 # -- the jxganan safety-acceptance index: the agent mapped four itself; five more
 #    resolve against the live segment names, and the rest have no GEM row --
 ("P5866", 3): (["P4784", "P4791", "P5865", "P4795", "P4780"], "",
                "index entries matched to rows: /9746 永修－武宁－修水=P4784; /9273 乐平-德兴=P4791; "
                "/9459 樟树支线=P5865; /9535 黎川支线改线=P4795 (Linchuan-Lichuan); "
                "/9582 九昌线改线=P4780 (Jiujiang-Nanchang, 九昌线). Unmatched entries "
                "(祥符-泰达, 南城-资溪, 南城-南丰, 西二线余江-东乡联通) go to the discovery cluster."),
}

def main(apply=False):
    batch_out, moved, split, routed = [], 0, 0, 0
    consumed = set()          # RESOLVE keys actually hit -- see the guard after the loop
    saw_nonpid = 0            # leads still needing resolution this run
    for p in sorted((HERE / "shards").glob("P*.json")):
        d = json.loads(p.read_text())
        leads = d.get("cross_row_leads") or []
        if not leads:
            continue
        keep, batch = [], list(d.get("batch_leads") or [])
        for j, L in enumerate(leads):
            if not isinstance(L, dict):
                keep.append(L); continue
            tgt = str(L.get("project_id") or "").strip()
            if re.fullmatch(r"P\d+", tgt):
                keep.append(L); continue
            saw_nonpid += 1
            # 1. comma list
            pids = [t for t in re.split(r"[,;/\s]+", tgt) if re.fullmatch(r"P\d+", t)]
            prefix, why = "", None
            if not pids and (p.stem, j) in RESOLVE:
                pids, prefix, why = RESOLVE[(p.stem, j)]
                consumed.add((p.stem, j))
            if not pids:
                note = dict(L, from_shard=p.stem, orig_target=tgt)
                note["_why_batch"] = why or "target is not a PID and no resolution was found"
                batch.append(note); batch_out.append((p.stem, j, tgt, note["_why_batch"]))
                moved += 1
                continue
            for pid in pids:
                nl = dict(L)
                nl["project_id"] = pid
                nl["facts"] = prefix + str(L.get("facts") or "")
                nl["orig_target"] = tgt
                if why:
                    nl["resolved_by"] = why
                if len(pids) > 1:
                    nl["split_from"] = tgt
                keep.append(nl)
            if why:
                routed += 1
            else:
                split += 1
            print(f"  {p.stem} lead#{j}: {tgt!r} -> {', '.join(pids)}")
        if batch:
            d["batch_leads"] = batch
        d["cross_row_leads"] = keep
        if apply:
            p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
    print(f"\n{routed} resolved lead(s), {split} comma-split lead(s), "
          f"{moved} moved to batch_leads[]")
    # STALE-KEY GUARD. RESOLVE is keyed positionally, so if a shard is re-run and its
    # leads shift, the mapping stops matching and the lead falls through to the generic
    # "no resolution was found" fallback -- a researched finding quietly demoted to an
    # unexplained batch item. That already happened once (P5862 #4 -> #7).
    #
    # An unconsumed key means one of TWO different things, and conflating them makes the
    # guard useless: after --apply every target is already a PID, so the whole table is
    # legitimately spent. Only flag keys that went unmatched while leads still needed
    # resolving -- that is the index-drift case.
    stale = sorted(set(RESOLVE) - consumed)
    if not saw_nonpid:
        print(f"\nRESOLVE table spent: every lead target is already a PID "
              f"({len(RESOLVE)} mapping(s) already applied). Nothing to check.")
    elif stale:
        print(f"\nSTALE RESOLVE KEY(S) -- {len(stale)} mapping(s) never matched a lead "
              f"while {saw_nonpid} lead(s) still needed resolving. Lead order has drifted:")
        for k in stale:
            print(f"  {k}  (re-check that shard's lead order)")
    if batch_out:
        print("\nBATCH-LEVEL (transcribe to orchestrator_notes.md):")
        for s, j, t, why in batch_out:
            print(f"  {s} lead#{j}  {t[:60]!r}\n      {why}")
    print(f"\n{'APPLIED' if apply else 'DRY RUN'}")

if __name__ == "__main__":
    main(apply="--apply" in sys.argv)
