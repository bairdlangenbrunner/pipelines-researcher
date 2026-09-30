#!/usr/bin/env python3
"""Stage the OtherLanguageSegmentName paste defect on P4785-P4790 as one sentinel per row.

THE DEFECT, proven arithmetically rather than asserted. `OtherLanguageSegmentName` on six
CONSECUTIVE rows (SheetRow 2672-2677) does not hold six segment names. It holds ONE prose
sentence, chunked at a fixed width and pasted down the column:

  P4785  len  8  目前开工建设井冈
  P4786  len 22  山支线、井开区支线；靖安支线、湘东支线、赣州
  P4787  len 22  南支线大余信丰段；于都宁都石城段、宁都广昌南
  P4788  len 22  丰段、进贤段；赣州南支线信丰瑞金段、上犹崇义
  P4789  len 22  段、樟树新干峡江段、井开区吉水永丰段、赣州南
  P4790  len 16  支线（信丰-龙南-定南段）等项目

Two independent proofs that this is one sliced string and not six names:
  (1) the four interior chunks are all EXACTLY 22 characters -- a width, not a name; and
  (2) every one of the five seams splits a word, so no chunk can stand alone:
        井冈|山支线   赣州|南支线   广昌南|丰段   上犹崇义|段   赣州南|支线（
      Reassembled, the 112 characters read as one grammatical sentence:
        目前开工建设井冈山支线、井开区支线；靖安支线、湘东支线、赣州南支线大余信丰段；
        于都宁都石城段、宁都广昌南丰段、进贤段；赣州南支线信丰瑞金段、上犹崇义段、
        樟树新干峡江段、井开区吉水永丰段、赣州南支线（信丰-龙南-定南段）等项目
      ("currently under construction: the Jinggangshan branch, the Jingkai District
      branch; the Jing'an branch, the Xiangdong branch, the Ganzhou South branch
      Dayu-Xinfeng segment; ... and other projects")

CONSEQUENCE. All six cells are wrong, including P4785's, whose chunk has no separators and
so looks less obviously broken. None of the six is the row it sits on: P4790's fragment
names 信丰-龙南-定南段 while the row IS 井开区-吉水-永丰-乐安-宜黄; P4789's begins mid-word
with 段、. Any consumer keying on OtherLanguageSegmentName -- name matching, dedup,
discovery guards -- is matching against sentence debris. It already caused one live
false positive: the 靖安 hit that made 安义-靖安支线 look like it might already be in the
tracker (see the P5862 discovery guard in normalize_cross_row_leads.py).

WHAT THIS SCRIPT DOES AND DOES NOT DO. It stages detection, not the repair. Each row's
correct Chinese name is already on the row, in `OtherLanguageAlternativePipelineNames`
as "二期工程, <name>", and the note records that <name> as the recommended replacement
(the live convention is the bare branch name in this cell -- cf. P4780 = 上高支线). But
the record proposes no `values`: which exact form belongs in the cell is a column-
semantics call for the researcher, and inventing one would be staging a value I did not
source. QC detects, Update fixes.

Idempotent: keyed on the sentinel's marker string, so re-running adds nothing.
Run with the other normalizers, BEFORE split_shards.py.
"""
import collections, json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
MARKER = "OLSN-PASTE-DEFECT-2026-09-10"

# pid -> (SheetRow, the corrupt chunk, the recommended replacement)
# The replacement is COPIED VERBATIM from this row's own OtherLanguageAlternativePipelineNames
# (the substring after '二期工程, '), never re-rendered -- so it carries the live tab's own
# punctuation, ASCII parens with a leading space, rather than a form I chose. Asserted by
# the --check pass against data/GGIT_gas_snapshot_20260910.csv.
ROWS = collections.OrderedDict([
 ("P4785", (2672, "目前开工建设井冈",                       "赣州南支线 (大余-信丰段)")),
 ("P4786", (2673, "山支线、井开区支线；靖安支线、湘东支线、赣州", "赣州南支线 (会昌-寻乌段)")),
 ("P4787", (2674, "南支线大余信丰段；于都宁都石城段、宁都广昌南", "赣州南支线 (龙南-全南段)")),
 ("P4788", (2675, "丰段、进贤段；赣州南支线信丰瑞金段、上犹崇义", "赣州南支线 (信丰-瑞金段)")),
 ("P4789", (2676, "段、樟树新干峡江段、井开区吉水永丰段、赣州南", "井冈山支线")),
 ("P4790", (2677, "支线（信丰-龙南-定南段）等项目",              "井开区-吉水-永丰-乐安-宜黄输气管道")),
])
SENTENCE = ("目前开工建设井冈山支线、井开区支线；靖安支线、湘东支线、赣州南支线大余信丰段；"
            "于都宁都石城段、宁都广昌南丰段、进贤段；赣州南支线信丰瑞金段、上犹崇义段、"
            "樟树新干峡江段、井开区吉水永丰段、赣州南支线（信丰-龙南-定南段）等项目")

def note(pid):
    row, chunk, rec = ROWS[pid]
    others = "; ".join(f"{p}={ROWS[p][1]!r}" for p in ROWS if p != pid)
    return (
      f"[{MARKER}] OtherLanguageSegmentName ON THIS ROW IS NOT A SEGMENT NAME. It is a "
      f"{len(chunk)}-character slice of one prose sentence that was chunked at a fixed width "
      f"and pasted down six consecutive rows, SheetRow 2672-2677 (P4785-P4790). This row "
      f"holds {chunk!r}. The siblings hold {others}. "
      f"Two proofs it is one sliced string, not six names: the four interior chunks are all "
      f"exactly 22 characters (a width, not a name), and all five seams split a word "
      f"(井冈|山支线, 赣州|南支线, 广昌南|丰段, 上犹崇义|段, 赣州南|支线（) so no chunk stands "
      f"alone. Reassembled the 112 characters are one grammatical sentence: {SENTENCE!r} "
      f"-- a 'currently under construction' branch list. "
      f"So the cell is corrupt on all six rows, including P4785's, whose chunk carries no "
      f"separators and so looks less obviously broken; and the fragment does not even "
      f"describe its own row (P4790's names 信丰-龙南-定南段 while the row is "
      f"井开区-吉水-永丰-乐安-宜黄). Anything keying on this column -- name matching, dedup, "
      f"discovery guards -- is matching sentence debris; it already produced one false "
      f"positive, the 靖安 hit that made the tendered 安义-靖安支线 look like it might "
      f"already be tracked. "
      f"RECOMMENDED for this row: {rec!r}, taken from the row's own "
      f"OtherLanguageAlternativePipelineNames ('二期工程, {rec}'), the live convention in this "
      f"cell being the bare branch name (cf. P4780 = 上高支线). Deliberately staged as "
      f"detection only, with no proposed `values`: the exact form the cell should take is a "
      f"column-semantics call, and the corrupt text is evidence of a paste, not of any "
      f"research finding, so nothing here changes a sourced value. Verified against "
      f"data/GGIT_gas_snapshot_20260910.csv."
    )

def main(apply=False):
    added, present = [], []
    for pid in ROWS:
        f = HERE / "shards" / f"{pid}.json"
        if not f.exists():
            sys.exit(f"missing shard: {f}")
        d = json.load(open(f), object_pairs_hook=collections.OrderedDict)
        res = d.setdefault("resolutions", [])
        if any(MARKER in (r.get("researcher_notes") or "") for r in res):
            present.append(pid); continue
        res.append(collections.OrderedDict([
            ("project_id", pid),
            ("sheet_row", ROWS[pid][0]),
            ("ref_col", "__VALIDITY__"),
            ("value_cols", []),
            ("values", {}),
            ("proposed_refs", []),
            ("verifications", []),
            ("class_out", "CONFIRMED"),
            ("tier", None),
            ("independent", None),
            ("verdict", "concern"),
            ("researcher_notes", note(pid)),
        ]))
        added.append(pid)
        if apply:
            f.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n")
    for p in added:   print(f"  + {p}  __VALIDITY__ sentinel staged")
    for p in present: print(f"    {p}  already present (idempotent)")
    print(f"\n{'APPLIED' if apply else 'DRY RUN'}: {len(added)} sentinel(s) added, "
          f"{len(present)} already present")

if __name__ == "__main__":
    main(apply="--apply" in sys.argv)
