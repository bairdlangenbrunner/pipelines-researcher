#!/usr/bin/env python3
"""Regenerate narrative counts from the staged JSON stores (the canonical
pending-state). Country notes / CLAUDE.md quote these numbers instead of
hand-maintaining them — when the artifacts and the narrative disagree, THIS
output wins (it is derived, never edited).

    python scripts/staged_summary.py --country Egypt --commodity gas
    python scripts/staged_summary.py --all --format md
    python scripts/staged_summary.py --country Iran --commodity gas --format json

Formats:
  text  (default) per-dir + rolled-up counts, human-readable
  md    same, fenced in <!-- staged-summary:start scope=<slug> --> markers for
        idempotent splicing into docs/country_notes/<country>.md
  json  machine-readable (per-dir + rollup)
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import normalize as N  # noqa: E402
from staged_store import (  # noqa: E402
    STAGING_ROOT, _STATUS_PENDING, _dir_mode, _dir_scope, discover_staging_dirs,
    load_staged_context,
)


def _dir_summary(d: Path) -> dict:
    ctx = load_staged_context([d])
    concerns = [c for cs in ctx["concerns"].values() for c in cs]
    status = [r for rs in ctx["status_changes"].values() for r in rs]
    return {
        "dir": d.name,
        "researched_pids": len(ctx["researched_pids"]),
        "concerns_by_type": dict(Counter(c["concern_type"] for c in concerns)),
        "status_verdicts": dict(Counter(r.get("verdict", "") for r in status)),
        "status_changes_pending": sum(
            1 for r in status if r.get("verdict", "") in _STATUS_PENDING),
        "fills": len(ctx["fills"]),
        "ref_work_by_class": dict(ctx["ref_counts"]),
        "route_suggestions": len(ctx["route_staged"]),
        "new_rows_by_class": dict(
            Counter(c.get("class", "") for c in ctx["new_rows"])),
    }


def _rollup(per_dir: list[dict]) -> dict:
    roll: dict = {"dirs": [s["dir"] for s in per_dir]}
    for key in ("concerns_by_type", "status_verdicts", "ref_work_by_class",
                "new_rows_by_class"):
        total: Counter = Counter()
        for s in per_dir:
            total.update(s[key])
        roll[key] = dict(total)
    for key in ("status_changes_pending", "fills", "route_suggestions"):
        roll[key] = sum(s[key] for s in per_dir)
    return roll


def _fmt_counts(d: dict) -> str:
    return ", ".join(f"{k}={v}" for k, v in sorted(d.items())) if d else "none"


def _text_block(scope_label: str, per_dir: list[dict], roll: dict,
                md: bool = False) -> list[str]:
    b = "- " if md else "  "
    lines = [f"## Staged summary — {scope_label}" if md
             else f"=== {scope_label} ==="]
    lines += [
        f"{b}staging dirs: {', '.join(roll['dirs'])}",
        f"{b}concerns: {_fmt_counts(roll['concerns_by_type'])}",
        f"{b}status verdicts: {_fmt_counts(roll['status_verdicts'])} "
        f"({roll['status_changes_pending']} pending changes)",
        f"{b}fills (corroborated): {roll['fills']}",
        f"{b}ref work: {_fmt_counts(roll['ref_work_by_class'])}",
        f"{b}route suggestions: {roll['route_suggestions']}",
        f"{b}discovery: {_fmt_counts(roll['new_rows_by_class'])}",
    ]
    for s in per_dir:
        lines.append(f"{b}[{s['dir']}] rows={s['researched_pids']} "
                     f"concerns({_fmt_counts(s['concerns_by_type'])}) "
                     f"status({_fmt_counts(s['status_verdicts'])}) "
                     f"fills={s['fills']} refs({_fmt_counts(s['ref_work_by_class'])}) "
                     f"routes={s['route_suggestions']} "
                     f"new({_fmt_counts(s['new_rows_by_class'])})")
    return lines


def _scope_slug(country: str, commodity: str) -> str:
    return f"{N.normalize_country(country).lower().replace(' ', '-')}-{commodity}"


def _all_scopes(root: Path) -> dict[tuple, list[Path]]:
    """Every (country, commodity) with primary staged work, depth-1."""
    scopes: dict[tuple, list[Path]] = {}
    if not root.is_dir():
        return scopes
    for d in sorted(root.iterdir()):
        if not d.is_dir():
            continue
        scope = _dir_scope(d)
        if scope is None or _dir_mode(d) in ("qc", "handoff"):
            continue
        scopes.setdefault(scope, []).append(d)
    return scopes


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--country")
    ap.add_argument("--commodity", choices=["gas", "oil"])
    ap.add_argument("--all", action="store_true",
                    help="every (country, commodity) scope with staged work")
    ap.add_argument("--format", default="text", choices=["text", "md", "json"])
    ap.add_argument("--root", default=str(STAGING_ROOT))
    args = ap.parse_args()

    if not args.all and not (args.country and args.commodity):
        ap.error("--country + --commodity, or --all")

    root = Path(args.root)
    if args.all:
        scopes = _all_scopes(root)
    else:
        dirs = discover_staging_dirs(args.country, args.commodity, root=root)
        scopes = {(N.normalize_country(args.country), args.commodity): dirs}

    out_json = {}
    for (country, commodity), dirs in sorted(scopes.items()):
        per_dir = [_dir_summary(d) for d in dirs]
        roll = _rollup(per_dir)
        slug = _scope_slug(country, commodity)
        label = f"{country} ({commodity})"
        if args.format == "json":
            out_json[slug] = {"country": country, "commodity": commodity,
                              "rollup": roll, "per_dir": per_dir}
        elif args.format == "md":
            print(f"<!-- staged-summary:start scope={slug} -->")
            print("\n".join(_text_block(label, per_dir, roll, md=True)))
            print(f"<!-- staged-summary:end scope={slug} -->")
            print()
        else:
            print("\n".join(_text_block(label, per_dir, roll)))
            print()
    if args.format == "json":
        print(json.dumps(out_json, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
