#!/usr/bin/env python3
"""Post-fanout merge task: re-run the name check over every `name_found: false`
verification in every shard, now that `_cjk_norm` collapses dash RUNS and treats 至 as a
dash (fixed 2026-09-09 after P4784: the verifier failed 永修——武宁——修水, a page that does
name the row, and 丰城至抚州 vs 丰城-抚州).

Read-only over the shards. Writes `name_recheck.json` + prints the flips. A `name_found:
false` is NOT automatically a defect -- BRIEF.md lets a shard record an honest negative
(the doc really does only name the trunk) -- so this reports candidates and the
orchestrator adjudicates each flip at merge.

    python3 recheck_name_found.py            # all shards
    python3 recheck_name_found.py P4794 ...  # only these
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from url_verifier import verify_many, _cjk_norm  # noqa: E402

HERE = pathlib.Path(__file__).resolve().parent
ONLY = {a.upper() for a in sys.argv[1:]}


def name_forms_for(pid):
    """Every name form the row is allowed to be named by, from its payload."""
    p = HERE / "batches" / f"{pid}.json"
    if not p.exists():
        return []
    nf = json.loads(p.read_text()).get("name_forms") or {}
    forms = []
    for v in nf.values():
        forms.extend(v if isinstance(v, list) else [v])
    # `name_forms.trunk` is a BOOLEAN flag ("is this row the parent trunk?"), not a name
    # form -- every payload carries it. `if f` drops the False ones silently but passes
    # True straight into verify_url(name=True), which crashed the 2026-09-10 run at P4934
    # (TypeError: 'bool' object is not iterable) AFTER 11 rows, losing all of them because
    # the results were only written at the end. Filter by TYPE, not truthiness.
    return [f for f in dict.fromkeys(forms) if isinstance(f, str) and f.strip()]


def walk_verifications(shard):
    for res in shard.get("resolutions") or []:
        for v in res.get("verifications") or []:
            yield res, v


todo, rows = {}, []
for sp in sorted((HERE / "shards").glob("P*.json")):
    pid = sp.stem
    if ONLY and pid not in ONLY:
        continue
    shard = json.loads(sp.read_text())
    forms = name_forms_for(pid)
    for res, v in walk_verifications(shard):
        if v.get("name_found") is not False:
            continue
        url = v.get("url")
        if not url:
            continue
        rows.append({"pid": pid, "ref_col": res.get("ref_col"), "url": url,
                     "class_out": res.get("class_out"), "note": v.get("note", "")[:160],
                     "ok": v.get("ok"), "forms": forms})
        todo.setdefault(pid, set()).add(url)

print(f"{len(rows)} name_found:false verifications across {len(todo)} rows", flush=True)

OUT = HERE / "name_recheck.json"


def flush_out(out):
    """Write after EVERY row: one bad row must not cost the whole (hours-long) pass."""
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")


out = []
if OUT.exists() and ONLY:  # a resume pass: keep rows for the PIDs we are not redoing
    out = [r for r in json.loads(OUT.read_text()) if r.get("pid") not in ONLY]
    print(f"resume: kept {len(out)} row(s) from the previous name_recheck.json", flush=True)
for pid, urls in todo.items():
    forms = name_forms_for(pid)
    if not forms:
        print(f"  {pid}: NO name_forms in payload -- skipped", flush=True)
        continue
    # verify_many takes ONE name per pass; a row's forms are alternatives, so any hit wins.
    hits = {u: [] for u in urls}
    try:
        for form in forms:
            for u, r in verify_many(sorted(urls), name=form, max_workers=3, timeout=30).items():
                if r.get("name_found"):
                    hits[u].append(form)
    except Exception as exc:  # noqa: BLE001 -- one row's failure is not the pass's
        print(f"  {pid}: ERROR {type(exc).__name__}: {exc} -- partial, re-run this PID",
              flush=True)
    for u in sorted(urls):
        rec = next(r for r in rows if r["pid"] == pid and r["url"] == u)
        rec["flips_to_true"] = bool(hits[u])
        rec["matched_forms"] = hits[u]
        out.append(rec)
    flush_out(out)
    n = sum(1 for u in urls if hits[u])
    print(f"  {pid}: {n}/{len(urls)} flip to true", flush=True)

flush_out(out)

flips = [r for r in out if r.get("flips_to_true")]
print(f"\n=== {len(flips)} FLIP to name_found:true (adjudicate each) ===")
for r in flips:
    print(f"{r['pid']:>6} {r['ref_col']:<24} {r['class_out']:<11} {r['matched_forms']}\n"
          f"       {r['url']}")
