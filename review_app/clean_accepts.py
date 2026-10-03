"""
Plan a "clean accept": accept every high-confidence line that nothing asks a person to judge.

    python review_app/clean_accepts.py --country "United States" --commodity gas [--out DIR]
    for f in DIR/clean_accepts_??.json; do python review_app/ledger.py decide --records $f; done   # record them, 100 per call

Plan only: reads the dataset, writes `clean_accepts.json` (records for `ledger.py decide
--records`) and `clean_accepts_skipped.csv` (every open high line left alone, with the reason)
to --out (default work/clean_accepts/). Never writes the ledger, a staging dir or the sheet.

The rule (Baird 2026-10-02). A line is accepted only if it is high confidence, undecided, not
in the backend, major or minor, AND none of these applies:
  line level      a rival concern candidate; a failed check on any proposed ref
                  (not ok / name not found / value not stated); class STALE, REF_UNSUPPORTED,
                  REF_BLOCKED
  concern open    (no call, confirmed, or needs_research; only `dismissed` closes one) on the
                  same pipeline that is
                    - pipeline-wide: existence or duplicate, or any other concern naming no
                      column that SCOPE_PATS cannot scope (Baird 2026-10-02: status, naming,
                      route-geometry and classification concerns, and Date_logic and
                      Geo_consistency flags, block only the columns they can affect; an
                      attribution concern with no column blocks only owner/operator lines); or
                      (a classification concern that only recommends a PipelineType change to
                      gathering or distribution is scoped to the PipelineType column instead:
                      Baird 2026-10-02, that is a change to suggest, not an issue); or
                    - attribution: also blocks every owner/operator line; or
                    - on a column the line proposes (contested columns, or the ref_check
                      column), compared without the ` [ref]` suffix
  flag open       a QC flag on the pipeline other than WikiLink_health (a wiki URL's health
                  says nothing about a data value) and Existence_support (Baird 2026-10-02: a
                  flag on the pipeline is not an issue raised on the line; it stays in the
                  store and is listed in clean_accepts_flagged.csv); `noted`/`dismissed`
                  closes one
  escalation      a scope escalation whose text names the pipeline's ProjectID
An unresolved note or a `confirmed` (positive) item never blocks. Anything unclear blocks:
the point is to leave every line a person might want to judge for a person.
"""
import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "review_app"))
sys.path.insert(0, str(ROOT / "scripts"))

import review_data  # noqa: E402

NONBLOCK_FLAGS = {"WikiLink_health", "Existence_support"}   # Existence_support: Baird 2026-10-02, too constraining
WHOLE_PIPELINE = {"existence", "duplicate"}   # Baird 2026-10-02: the rest are scoped by what they affect (SCOPE_PATS)
# concern type / flag check -> columns it can affect, when it names no column of its own
SCOPE_PATS = {
    "status": r"Status|Year|Month|Shelved|Cancelled|Delay|Proposal|Construction|Start$|Stop",
    "naming": r"Name",
    "route-geometry": r"Location|State|Province|District|Country|Route|Length|Prefecture",
    "classification": r"PipelineType|Fuel",
    "Date_logic": r"Year|Month|Status|Shelved|Cancelled",
    "Geo_consistency": r"Country|State|Province|Location|District|Prefecture",
}
BLOCK_CLASSES = {"STALE", "REF_UNSUPPORTED", "REF_BLOCKED"}
CHUNK = 100
NOTE = "clean accept: high confidence, no open concern or flag"


def stem(col):
    return re.sub(r"\s*\[ref\]$", "", str(col or "")).strip()


def open_line(l):
    return (l.get("tier") == "high" and not l.get("in_backend") and not l.get("applied")
            and l.get("decision") in (None, "", "none"))


def line_cols(l):
    cols = {stem(l.get("column")), stem(l.get("ref_col"))}
    if l.get("kind") != "oo":
        cols |= {stem(c) for c in l.get("value_cols") or []}
    return {c for c in cols if c}


TYPE_ONLY = re.compile(r"gather|distribut", re.I)
TYPE_UNSURE = re.compile(r"human|confirm|consider|whether|verify", re.I)


def type_only(i):
    """A classification concern whose recommendation is just a PipelineType change to
    gathering or distribution (Baird 2026-10-02): a CHANGE to suggest, not an issue that holds
    the pipeline's other lines. Wording that asks a person to confirm stays a pipeline-wide block."""
    r = i.get("recommendation") or ""
    return (i.get("concern_type") == "classification" and "PipelineType" in r
            and bool(TYPE_ONLY.search(r)) and not TYPE_UNSURE.search(r))


def concern_cols(i):
    if type_only(i):
        return {"PipelineType"}
    cols = {stem(c) for c in (i.get("contested") or {})}
    if i.get("ref_col") and not str(i["ref_col"]).startswith("__"):
        cols.add(stem(i["ref_col"]))
    return cols


def blockers(pipes):
    """pid -> {"whole": [reasons], "cols": {col: reason}, "oo": [reasons]} from open items."""
    out = {}
    esc = [i for p in pipes for i in p["items"] if i["kind"] == "escalation"]
    for p in pipes:
        b = out.setdefault(p["pid"], {"whole": [], "cols": {}, "oo": [], "pats": []})
        for i in p["items"]:
            k = i["kind"]
            if k == "concern" and i.get("call") != "dismissed":
                t = i.get("concern_type") or ""
                cols = concern_cols(i)
                why = f"concern:{t}:{i.get('call') or 'open'}"
                if t in WHOLE_PIPELINE and not type_only(i):
                    b["whole"].append(why)
                elif not cols and t == "attribution":
                    b["oo"].append(why)
                elif not cols and t in SCOPE_PATS:
                    b["pats"].append((SCOPE_PATS[t], why))
                elif not cols:
                    b["whole"].append(why)
                else:
                    if t == "attribution":
                        b["oo"].append(why)
                    for c in cols:
                        b["cols"].setdefault(c, why)
            elif k == "flag" and i.get("call") not in ("dismissed", "noted") and i.get("check") not in NONBLOCK_FLAGS:
                chk = i.get("check")
                m = re.match(r"\s*(?:orphan ref: )?(\w+)", i.get("detail") or "")
                if chk in SCOPE_PATS:
                    b["pats"].append((SCOPE_PATS[chk], f"flag:{chk}"))
                elif chk in ("OtherVocab", "BroadSweep_Misc") and m and m.group(1)[:1].isupper():
                    b["pats"].append((re.escape(m.group(1)), f"flag:{chk}"))
                else:
                    b["whole"].append(f"flag:{chk}")
        for e in esc:
            if p["pid"] in f"{e.get('title', '')} {e.get('summary', '')}":
                b["whole"].append("escalation")
    return out


def skip_reason(p, l, blk):
    if l.get("rival"):
        return "rival concern candidate"
    if l.get("class_out") in BLOCK_CLASSES:
        return f"class {l['class_out']}"
    for v in l.get("verifications") or []:
        if not (v.get("ok") and v.get("name_found") is not False and v.get("contains_value") is not False):
            return "a proposed ref failed its check"
    b = blk.get(p["pid"], {})
    if b.get("whole"):
        return "pipeline-wide: " + b["whole"][0]
    if l.get("kind") == "oo" and b.get("oo"):
        return "owner/operator: " + b["oo"][0]
    for pat, why in b.get("pats", []):
        for c in sorted(line_cols(l)):
            if re.search(pat, c):
                return f"column {c}: {why}"
    hit = line_cols(l) & set(b.get("cols", {}))
    if hit:
        c = sorted(hit)[0]
        return f"column {c}: {b['cols'][c]}"
    return ""


def plan(ds):
    pipes = ds["pipelines"]
    blk = blockers(pipes)
    take, skip = [], []
    for p in pipes:
        for l in p["lines"]:
            if not open_line(l):
                continue
            why = skip_reason(p, l, blk)
            (skip if why else take).append((p, l, why))
    return take, skip


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--country", action="append", default=[])
    ap.add_argument("--commodity", default="gas", choices=("gas", "oil"))
    ap.add_argument("--out", default=str(ROOT / "work" / "clean_accepts"))
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "dataset.json"
    argv2 = ["--commodity", a.commodity, "--out", str(tmp)]
    for c in a.country:
        argv2 += ["--country", c]
    review_data.main(argv2)
    ds = json.loads(tmp.read_text(encoding="utf-8"))
    take, skip = plan(ds)
    recs = [{"key": l["key"], "decision": "accept", "note": NOTE} for _, l, _ in take]
    (out / "clean_accepts.json").write_text(json.dumps(recs, indent=1), encoding="utf-8")
    # one gws call per ledger append: ~1,100 records in one call overflows the argument limit
    for i in range(0, len(recs), CHUNK):
        (out / f"clean_accepts_{i // CHUNK:02d}.json").write_text(json.dumps(recs[i:i + CHUNK]), encoding="utf-8")
    flagged = {p["pid"] for p in ds["pipelines"] for i in p["items"]
               if i["kind"] == "flag" and i.get("check") == "Existence_support" and i.get("call") not in ("dismissed", "noted")}
    with open(out / "clean_accepts_flagged.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["pid", "kind", "column", "key"])
        for p, l, _ in take:
            if p["pid"] in flagged:
                w.writerow([p["pid"], l["kind"], l.get("column"), l["key"]])
    with open(out / "clean_accepts_skipped.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["pid", "kind", "severity", "column", "reason", "key"])
        for p, l, why in skip:
            w.writerow([p["pid"], l["kind"], l.get("severity"), l.get("column"), why, l["key"]])
    print(f"\naccept {len(take)} lines on {len({p['pid'] for p, _, _ in take})} pipelines; "
          f"leave {len(skip)} open high lines alone")
    print("  accept by severity:", dict(Counter(l["severity"] for _, l, _ in take)))
    print("  accept by kind:    ", dict(Counter(l["kind"] for _, l, _ in take)))
    print("  accept by dir:     ", dict(Counter(Path(l["dir"]).name for _, l, _ in take)))
    print("  skip reasons:      ", dict(Counter(w.split(":")[0] if w.startswith(("pipeline-wide", "column", "owner")) else w
                                               for _, _, w in skip).most_common()))
    print(f"wrote {out}/clean_accepts.json and clean_accepts_skipped.csv")


if __name__ == "__main__":
    main()
