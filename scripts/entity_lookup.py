#!/usr/bin/env python3
"""Check whether an owner/operator already exists in GEM (Owner/Parent columns) before
staging a new entity — don't create duplicates. Fuzzy, case-insensitive.

    python scripts/entity_lookup.py "Saudi Aramco" --tracker oil
"""
from __future__ import annotations

import argparse
import glob
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import paths  # noqa: E402
import normalize as N  # noqa: E402


def _latest(tracker: str) -> str | None:
    pat = "GOIT_oil_ngl_snapshot_*.csv" if tracker == "oil" else "GGIT_gas_snapshot_*.csv"
    files = sorted(glob.glob(str(paths.repo_root() / "data" / pat)))
    return files[-1] if files else None


def lookup(name: str, tracker: str = "oil", threshold: int = 85) -> list[tuple[str, int]]:
    import pandas as pd
    from rapidfuzz import fuzz
    csv = _latest(tracker)
    if not csv:
        return []
    df = pd.read_csv(csv, header=2, low_memory=False,
                     keep_default_na=False, na_values=[], dtype=str).fillna("")
    seen: dict[str, str] = {}
    for col in ("Owner", "Parent", "OwnerEntityIDs"):
        if col not in df.columns or col == "OwnerEntityIDs":
            continue
        for val in df[col]:
            for part in N.parse_owners(val):
                seen.setdefault(part.lower(), part)
    q = name.lower()
    hits = [(orig, int(fuzz.token_set_ratio(q, k))) for k, orig in seen.items()]
    hits = [(o, s) for o, s in hits if s >= threshold]
    hits.sort(key=lambda x: -x[1])
    return hits[:10]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("name")
    ap.add_argument("--tracker", default="oil", choices=["oil", "gas"])
    ap.add_argument("--threshold", type=int, default=85)
    args = ap.parse_args()
    hits = lookup(args.name, args.tracker, args.threshold)
    if hits:
        print(f"possible existing entities for '{args.name}' ({args.tracker}):")
        for orig, score in hits:
            print(f"  {score:3d}  {orig}")
        print("→ reuse one of these rather than creating a duplicate, if it's the same entity.")
    else:
        print(f"no close existing entity for '{args.name}' ({args.tracker}) — likely safe to stage as new.")
    # ...and however it is staged, write it the way the ownership team does
    # (docs/reference/owner_style.md). The styled form is what goes in Owner<N>; the raw
    # spelling + any dropped acronym go in researcher_notes.
    try:
        from entity_style import style
    except ImportError:
        return
    st = style(args.name)
    print(f"\nownership-team style: {st.styled!r}  [{st.confidence}/{st.basis}"
          + (f" {st.entity_id}" if st.entity_id else "") + "]"
          + (f"  flags={','.join(st.flags)}" if st.flags else ""))
    if st.aliases:
        print(f"  aliases to keep in notes / owner_aliases.json: {st.aliases}")
    for c in st.candidates[:5]:
        print(f"  candidate NOT adopted: {c['name']!r}"
              + (f" ({c['entity_id']})" if c.get("entity_id") else "") + f" — {c.get('source', '')}")
    print(f"  {st.note}")


if __name__ == "__main__":
    main()
