"""Shared fixture for the review app tests: a temp scope (Russia gas) under a tmp
batches root with two staging dirs, a 6-row tracker snapshot and a tiny owners snapshot.

  batches/russia-gas/staging/deepsweep-x   primary research: every line kind + every item kind
  batches/russia-gas/staging/qc            handoff packet: carries some of them again + extras
  data/GGIT_gas_snapshot_20990101.csv      banner, banner, real header, 6 rows
  data/GEM_operators_owners_snapshot_20990101.csv

Snapshot rows (sheet_row = 1-based file record number, so the first data row is 4):
   4 P9001 Alpha        operating   Russia
   5 P9002 Beta         proposed    Russia
   6 P9003 Gamma        N/A         (dropped)
   7 P9004 Delta  seg A construction Russia   } one PID, two rows
   8 P9004 Delta  seg B construction Russia   }
   9 P9005 Epsilon      operating   Russia    (Capacity + Capacity [ref] already as proposed)
"""
import csv
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SNAP_NAME = "GGIT_gas_snapshot_20990101.csv"
OWN_NAME = "GEM_operators_owners_snapshot_20990101.csv"
SCOPE = {"country": "Russia", "tracker": "gas", "csv": SNAP_NAME, "owners_csv": OWN_NAME}

_NEW = "http://new.example/b"
_OLD = "http://old.example/a"


def _real_header(glob, idx):
    path = sorted((REPO / "data").glob(glob))[-1]
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.reader(f))[idx]


def _row(header, **kw):
    r = [""] * len(header)
    for k, v in kw.items():
        r[header.index(k.replace("__", " ").replace("_ref", " [ref]") if k.endswith("_ref") else k)] = v
    return r


def _write_snapshot(data_dir):
    h = _real_header("GGIT_gas_snapshot_*.csv", 2)
    c = lambda **kw: _row(h, **kw)  # noqa: E731
    rows = [
        c(ProjectID="P9001", PipelineName="Alpha Pipeline", Status="operating", CountriesOrAreas="Russia",
          Wiki="https://www.gem.wiki/Alpha", Status_ref=_OLD, Capacity="10"),
        c(ProjectID="P9002", PipelineName="Beta Pipeline", Status="proposed", CountriesOrAreas="Russia"),
        c(ProjectID="P9003", PipelineName="Gamma Pipeline", Status="N/A", CountriesOrAreas="Russia"),
        c(ProjectID="P9004", PipelineName="Delta Pipeline", SegmentName="Seg A", Status="construction",
          CountriesOrAreas="Russia"),
        c(ProjectID="P9004", PipelineName="Delta Pipeline", SegmentName="Seg B", Status="construction",
          CountriesOrAreas="Russia"),
        c(ProjectID="P9005", PipelineName="Epsilon Pipeline", Status="operating", CountriesOrAreas="Russia",
          Capacity="500", Capacity_ref="http://already.example/cap"),
    ]
    with open(data_dir / SNAP_NAME, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["don't forget a filter view :)"] + [""] * (len(h) - 1))
        w.writerow([str(i + 1) for i in range(len(h))])
        w.writerow(h)
        w.writerows(rows)
    oh = _real_header("GEM_operators_owners_snapshot_*.csv", 1)
    with open(data_dir / OWN_NAME, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow([""] * len(oh))
        w.writerow(oh)
        for pid, nm, owner in (("P9001", "Alpha Pipeline", "OldCo"), ("P9002", "Beta Pipeline", "")):
            r = [""] * len(oh)
            r[oh.index("ProjectID")], r[oh.index("PipelineName")] = pid, nm
            r[oh.index("Owner1")] = owner
            r[oh.index("Owner [ref]")] = "http://owners-old.example/x" if owner else ""
            w.writerow(r)


def _rec(pid, row, ref_col, class_in, class_out, **kw):
    r = {"project_id": pid, "sheet_row": row, "pipeline_name": pid, "segment_name": "",
         "ref_col": ref_col, "value_cols": [], "primary_value_col": None, "values": {},
         "primary_value": "", "current_ref": "", "class_in": class_in, "class_out": class_out,
         "proposed_refs": [], "verifications": [], "tier": "", "independent": False,
         "source_language": "en", "researcher_notes": ""}
    r.update(kw)
    return r


def _deepsweep_records():
    v = [{"url": _NEW, "ok": True, "contains_value": True, "name_found": True}]
    return [
        # LINES
        _rec("P9001", 4, "Status [ref]", "HAS_REF", "REFS_ADDED", value_cols=["Status"],
             primary_value_col="Status", values={"Status": "operating"}, current_ref=_OLD,
             proposed_refs=[_NEW], verifications=v, tier="medium", link_live=True),
        _rec("P9002", 99, "Capacity [ref]", "FILL", "REFS_ADDED",          # row 99 is stale -> re-resolved to 5
             value_cols=["Capacity", "CapacityUnits"], primary_value_col="Capacity",
             values={"Capacity": "7.5", "CapacityUnits": "bcm/y"}, proposed_refs=[_NEW],
             verifications=v, tier="high", independent=True),
        _rec("P9002", 5, "__STATUS__", "STATUS", "CHANGE_PROPOSED", value_cols=["Status"],
             primary_value_col="Status", values={"Status": "construction"},
             current_status="proposed", proposed_status="construction", verdict="change",
             evidence_date="2026-08", staleness_rule="", proposed_refs=[_NEW, "http://other.example/z"],
             verifications=v, tier="high"),
        _rec("P9001", 4, "Owner [ref]", "MISSING_REF", "REFS_ADDED", tab="operators_owners",
             value_cols=["Owner1"], primary_value_col="Owner1", values={"Owner1": "NewCo"},
             proposed_refs=["http://owners-new.example/y"], verifications=v, tier="high"),
        _rec("P9004", 7, "__ROUTE__", "ROUTE", "ROUTE_CANDIDATE", geometry_file="candidate_routes/P9004.geojson",
             length_km=54.1, sheet_length_km=65.0, length_ratio=0.83, suggested_route_accuracy="low",
             qc_passed=True, current_route_accuracy="no route"),
        _rec("P9005", 9, "Capacity [ref]", "FILL", "REFS_ADDED",            # already applied on the sheet
             value_cols=["Capacity"], primary_value_col="Capacity", values={"Capacity": "500"},
             proposed_refs=["http://already.example/cap"], verifications=v, tier="high"),
        # ITEMS
        _rec("P9001", 4, "__VALIDITY__", "VALIDITY", "UNRESOLVED", verdict="concern", concern_type="duplicate",
             recommendation="check", contested={"Status": ""}),
        _rec("P9004", 7, "__WIKIDIFF__", "WIKIDIFF", "WIKI_UPDATE", field="Status", sheet_value="construction"),
        _rec("P9004", 8, "__ROUTEQC__", "ROUTEQC", "ROUTE_FLAG", check="length_ratio", detail="0.2"),
        _rec("P9004", 8, "__ROUTE__", "ROUTE", "ROUTE_SUGGESTED", start_name="A", end_name="B"),
        _rec("P9005", 9, "Length [ref]", "MISSING_REF", "UNRESOLVED", value_cols=["Length"]),
        _rec("P9005", 9, "__STATUS__", "STATUS", "CONFIRMED", current_status="operating", verdict="confirm"),
        _rec("P9005", 9, "Weird [ref]", "SOMETHING_NEW", "MYSTERY"),       # fits no kind -> "other"
    ]


def _write(d, name, obj):
    (d / name).write_text(json.dumps(obj))


def make_scope(tmp_path):
    """-> dict(root=<batches root>, data=<data dir>, deep=<dir>, qc=<dir>)."""
    root, data = tmp_path / "batches", tmp_path / "data"
    deep = root / "russia-gas" / "staging" / "deepsweep-x"
    qc = root / "russia-gas" / "staging" / "qc"
    for d in (deep, qc, data):
        d.mkdir(parents=True)
    _write_snapshot(data)

    recs = _deepsweep_records()
    _write(deep, "staged_resolutions.json", {"meta": {"mode": "deepsweep", "commodity": "gas",
           "scope": SCOPE, "generated": "2099-01-01"}, "resolutions": recs})
    # worklist: the existing Status [ref] URL is kept alongside the proposed one (never dropped)
    _write(deep, "worklist.json", {"units": [{"project_id": "P9001", "sheet_row": 4, "ref_col": "Status [ref]",
           "current_ref": _OLD, "existing_ref_checks": [{"url": _OLD, "status": 403}]}]})
    _write(deep, "staged_new.json", {"meta": {"scope": SCOPE, "mode": "discovery"}, "candidates": [
        {"slug": "new-one", "class": "new_row", "name": "New One Pipeline", "matched_project_id": "",
         "values": {"PipelineName": "New One Pipeline", "Status": "proposed"},
         "refs": {"Status [ref]": [_NEW]}, "tier": "high", "independent": False, "verifications": []},
        {"slug": "watch", "class": "monitor", "name": "Watch Pipeline", "matched_project_id": "",
         "values": {}, "refs": {}, "monitor_reason": "no sponsor"},
        {"slug": "alias", "class": "matched_existing", "name": "Alpha Alias", "matched_project_id": "P9001",
         "values": {"OtherEnglishNames": "Alpha Alias"}, "refs": {}, "tier": "medium"}]})
    _write(deep, "qc_flags.json", {"meta": {"mode": "qc_flags"}, "flags": [
        {"check": "Date_logic", "project_id": "P9002", "sheet_row": 5, "pipeline_name": "Beta",
         "detail": "Status=proposed but has StartYear1"}]})
    _write(deep, "escalations.json", [{"title": "a scope-level question", "summary": "s", "memo": "m"}])
    # both of these must be ignored
    _write(deep, "staged_resolutions.prior.json", {"meta": {"scope": SCOPE}, "resolutions": [
        _rec("P9099", 4, "Status [ref]", "HAS_REF", "REFS_ADDED", proposed_refs=[_NEW], tier="high")]})
    _write(deep, "staged_actions.json", {"meta": {"mode": "handoff_actions"}, "fills": [
        _rec("P9098", 4, "Capacity [ref]", "FILL", "REFS_ADDED", proposed_refs=[_NEW], tier="high")]})

    carried = [dict(recs[0], sheet_row=4), dict(recs[1]), dict(recs[6]), dict(recs[7])]   # ref, fill, concern, wikidiff
    extra = [
        _rec("P9001", 4, "__WIKIDIFF__", "WIKIDIFF", "SHEET_SUSPECT", field="Owner", sheet_value=""),
        _rec("P9004", 7, "__ROUTEQC__", "ROUTEQC", "ROUTE_FLAG", check="null_geometry", detail="none"),
    ]
    _write(qc, "staged_resolutions.json", {"meta": {"mode": "handoff", "commodity": "gas", "scope": SCOPE},
           "resolutions": carried + extra})
    return {"root": root, "data": data, "deep": deep, "qc": qc, "tmp": tmp_path}
