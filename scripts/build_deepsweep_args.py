#!/usr/bin/env python3
"""Derive the `args` payload for the `critical-deep-sweep` workflow from a ref-sweep worklist.

The workflow itself has no filesystem access, so the in-scope ProjectID list and the
duplicate-detection roster must be passed in as `args`. This reads the worklist (for the
authoritative in-scope PIDs + the snapshot it was built from) and the GEM snapshot CSV
(for the per-pipeline spec descriptors), and prints a JSON object ready to hand to the
Workflow tool as `args`:

    { repo, staging, commodity, country, pids: [...], roster: ["P#### | name | a->b | len/dia/cap | status", ...] }

Usage:
    python scripts/build_deepsweep_args.py --staging batches/saudi-arabia-gas/staging/ref-sweep/
    # optionally --out batches/<scope>/staging/.../deepsweep_args.json

Lean pass (docs/sops/lean_pass.md) — everything the orchestrator used to hand-bake into a
one-off copy of the workflow, compiled here so the args file IS the dispatch:
    python scripts/build_deepsweep_args.py --staging <dir> --status-review --lean \
        --groups auto [--max-group 4] [--max-group-units 60] \
        --brief <dir>/BRIEF.md --model sonnet --out <dir>/deepsweep_args.json
`--groups auto` proposes family groups (rows sharing a PipelineName, then rows sharing a
leading hub name); REVIEW the printed grouping and hand-edit `groups` in the JSON where the
heuristic is wrong (e.g. two unrelated lines that both start at a big hub). `--groups FILE`
takes a JSON list of PID lists instead.
"""
import argparse, json, math, os, re, sys
from collections import Counter, OrderedDict
import pandas as pd

BRIEF_WARN_CHARS = 20000   # lean_pass.md: a batch brief over this is paying for background


def _hub(name: str) -> str:
    """Leading endpoint of an 'A-B-C Gas Pipeline' name, lowercased; '' if none."""
    base = re.sub(r"\s+(gas|oil|ngl)?\s*pipeline.*$", "", name or "", flags=re.I).strip()
    head = re.split(r"\s*[-\u2013\u2014]\s*", base)[0].strip().lower()
    return head if head and head != base.lower() else ""


def auto_groups(pids, names, units_per_pid, max_group, max_units):
    """PipelineName siblings first, then shared leading hub; chunk evenly under both caps."""
    buckets = OrderedDict()
    name_count = Counter(names[p] for p in pids)
    hub_count = Counter(_hub(names[p]) for p in pids if name_count[names[p]] == 1)
    for p in pids:
        n = names[p]
        if name_count[n] > 1:
            key = "name:" + n
        elif _hub(n) and hub_count[_hub(n)] > 1:
            key = "hub:" + _hub(n)
        else:
            key = "solo:" + p
        buckets.setdefault(key, []).append(p)
    groups = []
    for members in buckets.values():
        total = sum(units_per_pid.get(p, 0) for p in members)
        k = max(math.ceil(len(members) / max_group), math.ceil(total / max_units) if max_units else 1, 1)
        size = math.ceil(len(members) / k)
        groups += [members[i:i + size] for i in range(0, len(members), size)]
    return groups

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _col(cols, *names):
    """First column in `cols` matching one of `names` (case-insensitive exact)."""
    low = {c.lower(): c for c in cols}
    for n in names:
        if n.lower() in low:
            return low[n.lower()]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--staging", required=True, help="ref-sweep staging dir (has worklist.json)")
    ap.add_argument("--out", help="also write the JSON here (default: stdout only)")
    ap.add_argument("--status-review", action="store_true",
                    help="annual-update mode: subagents also stage a per-segment status verdict "
                         "(confirm/change/stale/unclear) as status_reviews in each shard")
    ap.add_argument("--lean", action="store_true",
                    help="worklist was cut by lean_worklist.py; agents work the owed set only")
    ap.add_argument("--groups", help="'auto' or a JSON file holding a list of PID lists")
    ap.add_argument("--max-group", type=int, default=4)
    ap.add_argument("--max-group-units", type=int, default=60,
                    help="cap on owed worklist units per family agent (context budget)")
    ap.add_argument("--brief", help="BRIEF.md to inline as extra_brief (never pass a path to agents)")
    ap.add_argument("--model", help="dispatch-time model choice (recorded in the args)")
    args = ap.parse_args()

    staging = args.staging.rstrip("/")
    wl = json.load(open(os.path.join(staging, "worklist.json")))
    scope = wl["scope"]
    country = scope.get("country", "")
    csv_name = scope["csv"]
    commodity = "gas" if "GGIT" in csv_name else ("oil" if "GOIT" in csv_name else "")

    # in-scope PIDs, in worklist order, deduped. A lean worklist can leave a row with no owed
    # units at all; it still gets its status review + validity record, so read the full list.
    full_path = os.path.join(staging, "worklist_full.json")
    pid_units = json.load(open(full_path))["units"] if wl["scope"].get("lean") and os.path.exists(full_path) else wl["units"]
    pids, seen = [], set()
    for u in pid_units:
        pid = u.get("project_id")
        if pid and pid not in seen:
            seen.add(pid); pids.append(pid)

    # enrich a duplicate-detection roster from the snapshot the worklist was built on
    df = pd.read_csv(os.path.join(REPO, "data", csv_name), header=2, low_memory=False)
    C = df.columns
    c_pid = _col(C, "ProjectID")
    c_name = _col(C, "PipelineName")
    c_len = _col(C, "LengthKnown")
    c_dia = _col(C, "Diameter")
    c_cap = _col(C, "Capacity")
    c_stat = _col(C, "Status")
    c_upd = _col(C, "LastUpdated")
    c_sloc = _col(C, "StartLocation", "StartState/Province", "StartCountryOrArea")
    c_eloc = _col(C, "EndState/Province", "EndCountryOrArea")
    by_pid = {str(r[c_pid]): r for _, r in df.iterrows()}

    def cell(r, c):
        if not c:
            return "?"
        v = r.get(c, "")
        if pd.isna(v) or v == "":
            return "?"
        return str(v).strip()

    roster = []
    for pid in pids:
        r = by_pid.get(pid)
        if r is None:
            roster.append(f"{pid} | (not in snapshot) | ?->? | ? | ?")
            continue
        roster.append(
            f"{pid} | {cell(r, c_name)} | {cell(r, c_sloc)}->{cell(r, c_eloc)} | "
            f"len={cell(r, c_len)} dia={cell(r, c_dia)} cap={cell(r, c_cap)} | "
            f"status={cell(r, c_stat)} | updated={cell(r, c_upd)}"
        )

    payload = {
        "repo": REPO,
        "staging": staging,
        "commodity": commodity,
        "country": country,
        "pids": pids,
        "roster": roster,
    }
    if args.status_review:
        payload["status_review"] = True
    if args.lean:
        if not wl.get("scope", {}).get("lean"):
            sys.exit("--lean but worklist.json was not cut by scripts/lean_worklist.py")
        payload["lean"] = True
    if args.model:
        payload["model"] = args.model
    if args.brief:
        brief = open(args.brief).read()
        payload["extra_brief"] = brief
        if len(brief) > BRIEF_WARN_CHARS:
            print(f"WARN brief is {len(brief):,} chars (> {BRIEF_WARN_CHARS:,}); every agent pays for "
                  f"all of it — cut Russia-/country-wide background to what THIS batch needs",
                  file=sys.stderr)
    if args.groups:
        units_per_pid = Counter(u.get("project_id") for u in wl["units"])
        names = {}
        for u in pid_units:
            names.setdefault(u.get("project_id"), u.get("pipeline_name") or "")
        for pid in pids:
            r = by_pid.get(pid)
            if r is not None and c_name:
                names[pid] = cell(r, c_name)
        if args.groups == "auto":
            groups = auto_groups(pids, names, units_per_pid, args.max_group, args.max_group_units)
        else:
            groups = json.load(open(args.groups))
        flat = [p for g in groups for p in g]
        if sorted(flat) != sorted(pids):
            sys.exit(f"groups do not cover the pids exactly once: missing {sorted(set(pids) - set(flat))}, "
                     f"extra/dup {sorted(p for p in set(flat) if flat.count(p) > 1 or p not in pids)}")
        payload["groups"] = groups
        for g in groups:
            if len(g) > 1:
                print(f"GROUP {'+'.join(g)}  ({sum(units_per_pid.get(p, 0) for p in g)} owed units): "
                      + " | ".join(names.get(p, '?') for p in g), file=sys.stderr)
        print(f"# {len(groups)} agents for {len(pids)} pids", file=sys.stderr)
    out = json.dumps(payload, indent=1)
    if args.out:
        open(args.out, "w").write(out)
    print(out)
    print(f"\n# {len(pids)} pids, commodity={commodity}, country={country!r}", file=sys.stderr)


if __name__ == "__main__":
    main()
