"""Discover which GEM data columns each `X [ref]` column sources — dynamically,
from the fresh header every batch (the schema drifts; never hard-code offsets).

The pairing is a **group-walk**: a `[ref]` column sources the run of value columns
that precede it (since the previous `[ref]`), minus identity/derived/no-ref columns.
But a long gap between two `[ref]`s (e.g. gas `H2RepurposedKmOr% [ref]` … `QCCOwner
[ref]`) would let a ref swallow unrelated columns, so when the ref's stripped name
matches a column in the run (exact or prefix — `Capacity`→`Capacity`, `Length`→
`LengthKnown`), the cluster *starts* at that column and drops the leading junk.
When no name matches (gas `Location [ref]` covers BOTH endpoints; `H2RepurposedKmOr%
[ref]`), we keep the whole run and flag `irregular=True` for reviewer sanity.

`Owner`/`Parent` have **no** `[ref]` column on the tracker tab — `discover_ref_pairs`
emits a synthetic `kind='owner'` placeholder pair (kept for the QC BroadSweep). The real
owner/operator source URLs live in a **separate backend tab, "Pipeline operators/owners"**
(GID 1489950650, header at CSV row index 1, **ProjectID-keyed**) whose `Operator [ref]` /
`Owner [ref]` columns the reference sweep fills. On that tab the `[ref]` column **PRECEDES**
its values (opposite of the trackers) — `discover_owner_ref_pairs` handles it with a forward
group-walk.

Pure stdlib, no pandas/I-O at import. Shared by build_ref_worklist.py and the
BroadSweep check in build_qc_workbook.py (single source of truth for ref pairing).

    python scripts/ref_pairs.py data/GOIT_oil_ngl_snapshot_<date>.csv   # print the pairs
"""
from __future__ import annotations

REF_SUFFIX = " [ref]"

# Identity / admin / names / derived-normalized / notes / IDs: never their own [ref],
# always excluded from a cluster. (Derived cols are computed from sourced values, so
# they are never independently cited.)
NON_REF_VALUE_COLS = {
    # identity & names
    "PipelineNetworkGrouping", "AltPipelineNetworkGrouping", "PipelineNetworkGroupingAlt",
    "PipelineName", "SegmentName", "Wiki", "ProjectID", "Researcher", "LastUpdated",
    "OtherEnglishNames", "OtherLanguagePrimaryPipelineName",
    "OtherLanguageAlternativePipelineNames", "OtherLanguageSegmentName",
    "CountriesOrAreas", "NumberOfCountries",
    # notes
    "ResearcherNotes", "ESJNotes", "H2Notes", "CCSNotes", "ChineseClassificationNotes",
    # IDs / codes
    "OwnerEntityIDs", "ParentEntityIDs", "AlternateRouteProjectIDs", "OtherIDs",
    "PCI345ID", "PCI6ID", "PCI6ProjectCode", "DraftPCI6List", "SciGridNames",
    # derived / normalized (computed from sourced values)
    "LengthKnownKm", "LengthEstimateKm", "LengthMergedKm", "LengthDoubleCounting",
    "DiameterInMm", "CapacityBOEd", "CapacityBcm/y", "CostUSD", "CostEuro",
    "CostUSDPerKm", "CostEuroPerKm", "StartYearEarliest", "WKTFormat",
    "StartRegion", "StartSubRegion", "EndRegion", "EndSubRegion",
}

# Real data values that legitimately carry NO paired [ref] in the schema. Excluded
# from clusters and never flagged MISSING_REF — BUT only when no same-named `<col>
# [ref]` exists (oil HAS `Opposition [ref]` so oil Opposition stays in its cluster;
# gas has none, so gas Opposition is a true orphan).
ORPHAN_OK_VALUE_COLS = {
    "Disrupted", "ShelvedCancelledType", "AssociatedEthyleneCrackerRMI",
    "EuropeTracker", "PCI3", "PCI4", "PCI5", "PCI6", "DraftPCI7", "Opposition",
    "PipelineDirectionality", "H2PipelineType", "H2%", "H2ProposedYear", "H2StartYear",
    "H2Cost", "H2CostUnits", "AssociatedWithUSLNGExports", "AssociatedLNGTerminal",
    "ImpactedByRussiaUkraineInvasion", "EGTImport", "ChinesePipelineType",
    "ChineseNetworkPrimary", "ChineseNetworkSecondary",
}

# Owner cluster: no [ref] column exists. Handled as a synthetic pair.
OWNER_VALUE_COLS = ["Owner", "Parent"]

# Route / geometry cluster: deliberately OUT OF SCOPE for the reference sweep. Pipeline
# geometry is reconciled against the GOIT-GGIT-pipeline-routes repo (a separate human
# branch + PR) and is not corroborated from media `[ref]` URLs — so we neither fill nor
# re-verify `Route [ref]`. The value cols are excluded from every cluster and the
# `Route [ref]` column itself emits no pair (see SKIP_REF_COLS in discover_ref_pairs).
ROUTE_VALUE_COLS = {"RouteType", "RouteAccuracy", "RouteNotes"}
SKIP_REF_COLS = {"Route [ref]"}

_UNIT_SUFFIXES = ("Units",)


def _excluded(col: str, columns_set: set) -> bool:
    """True if `col` should never be part of a cluster."""
    if col in NON_REF_VALUE_COLS or col in OWNER_VALUE_COLS or col in ROUTE_VALUE_COLS:
        return True
    # orphan-ok only when it has no [ref] of its own
    if col in ORPHAN_OK_VALUE_COLS and (col + REF_SUFFIX) not in columns_set:
        return True
    return False


def _pick_primary(stripped: str, run: list[str]) -> tuple[str | None, str]:
    """Return (primary_value_col, match_kind) where match_kind ∈ exact|prefix|fallback."""
    if not run:
        return None, "fallback"
    if stripped in run:
        return stripped, "exact"
    pref = [c for c in run if c.startswith(stripped)]
    if pref:
        return pref[0], "prefix"
    # fallback: first column that isn't a *Units sibling
    non_unit = [c for c in run if not c.endswith(_UNIT_SUFFIXES)]
    return (non_unit or run)[0], "fallback"


def discover_ref_pairs(columns: list[str]) -> list[dict]:
    """Return ordered list of pair dicts, one per `[ref]` column plus one synthetic
    owner pair:
        {ref_col, value_cols, primary_value_col, kind: 'cluster'|'owner',
         match_kind: 'exact'|'prefix'|'fallback', irregular: bool}
    """
    columns_set = set(columns)
    pairs: list[dict] = []
    run: list[str] = []
    for c in columns:
        if c.endswith(REF_SUFFIX):
            if c in SKIP_REF_COLS:   # geometry is out of scope — drop the run, emit no pair
                run = []
                continue
            stripped = c[: -len(REF_SUFFIX)]
            primary, match_kind = _pick_primary(stripped, run)
            if match_kind in ("exact", "prefix") and primary in run:
                # name matched → cluster starts at the matched column (drop leading junk)
                value_cols = run[run.index(primary):]
            else:
                value_cols = list(run)
            if value_cols:
                pairs.append({
                    "ref_col": c,
                    "value_cols": value_cols,
                    "primary_value_col": primary,
                    "kind": "cluster",
                    "match_kind": match_kind,
                    "irregular": match_kind == "fallback",
                })
            run = []
        elif not _excluded(c, columns_set):
            run.append(c)
    # synthetic owner pair (no [ref] column in the schema)
    own = [v for v in OWNER_VALUE_COLS if v in columns_set]
    if own:
        pairs.append({
            "ref_col": None,
            "value_cols": own,
            "primary_value_col": "Owner",
            "kind": "owner",
            "match_kind": "fallback",
            "irregular": True,
        })
    return pairs


# ── Operators/owners tab (GID 1489950650) ───────────────────────────────────────
# Separate ProjectID-keyed backend tab where owner/operator refs actually live. Unlike
# the trackers, the `[ref]` column PRECEDES its value run, so we forward-walk. Header is
# at CSV row index 1 (not 2). Two ref clusters: Operator [ref] → Operator block,
# Owner [ref] → Owner1..Owner11(+%) block.
OO_HEADER_INDEX = 1
# identity / derived / summary columns on the OO tab that never belong to a ref cluster
OO_NON_VALUE_COLS = {
    "PipelineNetworkContainer", "PipelineName", "SegmentName", "Countries", "Wiki",
    "ProjectID", "Researcher", "LastUpdated", "StartRegion", "EndRegion",
    "LengthMergedKm", "Fuel", "Status", "PCI6", "AggregateOwners", "Notes/Links",
    "Percentage Verification",
}
# canonical primary value col per OO ref (the human-readable name to verify against)
OO_PRIMARY = {"Operator [ref]": "Operator", "Owner [ref]": "Owner1"}


def discover_owner_ref_pairs(columns: list[str]) -> list[dict]:
    """Pairs for the operators/owners tab — the `[ref]` column PRECEDES its values, so a
    ref governs the FORWARD run of value cols until the next `[ref]` (or end), minus
    identity/derived/summary cols. Returns the same pair-dict shape as discover_ref_pairs
    plus `ref_leads: True` and `tab: 'operators_owners'`. `kind` ∈ 'operator'|'owner'."""
    cols = list(columns)
    n = len(cols)
    pairs: list[dict] = []
    for i, c in enumerate(cols):
        if not c.endswith(REF_SUFFIX):
            continue
        value_cols = []
        j = i + 1
        while j < n and not cols[j].endswith(REF_SUFFIX):
            if cols[j] not in OO_NON_VALUE_COLS:
                value_cols.append(cols[j])
            j += 1
        if not value_cols:
            continue
        primary = OO_PRIMARY.get(c)
        if primary not in value_cols:
            primary = value_cols[0]
        kind = "owner" if c == "Owner [ref]" else "operator"
        pairs.append({
            "ref_col": c,
            "value_cols": value_cols,
            "primary_value_col": primary,
            "kind": kind,
            "match_kind": "ref_leads",
            "irregular": False,
            "ref_leads": True,
            "tab": "operators_owners",
        })
    return pairs


def _main() -> None:
    import csv
    import sys
    if len(sys.argv) not in (2, 3):
        sys.exit("usage: python scripts/ref_pairs.py <GEM_csv> [--owners]")
    if len(sys.argv) == 3 and sys.argv[2] == "--owners":
        with open(sys.argv[1], newline="") as f:
            header = list(csv.reader(f))[OO_HEADER_INDEX]   # OO header at row index 1
        pairs = discover_owner_ref_pairs(header)
        print(f"{len(header)} cols → {len(pairs)} operators/owners pairs:\n")
        for p in pairs:
            print(f"  {p['ref_col']:16s} [{p['kind']}] primary={p['primary_value_col']}")
            print(f"      values: {p['value_cols']}")
        return
    with open(sys.argv[1], newline="") as f:
        header = list(csv.reader(f))[2]   # header at row index 2
    pairs = discover_ref_pairs(header)
    print(f"{len(header)} cols → {len(pairs)} pairs "
          f"({sum(p['irregular'] for p in pairs)} irregular):\n")
    for p in pairs:
        ref = p["ref_col"] or "(owner — no ref col)"
        flag = "  IRREGULAR" if p["irregular"] else ""
        print(f"  {ref:28s} [{p['match_kind']:8s}] primary={p['primary_value_col']}{flag}")
        print(f"      values: {p['value_cols']}")


if __name__ == "__main__":
    _main()
