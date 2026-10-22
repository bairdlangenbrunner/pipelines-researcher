"""review_app/route_state.py: is a staged route candidate already in the routes repo and on the sheet?"""
import json

import pytest

import route_state as rs

LINE = [[30.1234567, 50.1, 7.0], [31.5, 51.7654321, 7.0]]
MAPPED_ROW = {"RouteType": rs.MAPPED, "RouteAccuracy": "medium", "RouteNotes": "", "RouteCreator": ""}
UNMAPPED_ROW = {"RouteType": "Not mapped (but could be — route or endpoints are known)", "RouteAccuracy": "no route",
                "RouteNotes": "", "RouteCreator": ""}


def _gj(coords, kind="LineString", props=None):
    return {"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": props or {}, "geometry": {"type": kind, "coordinates": coords}}]}


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """A candidate file, and a routes-repo file whose content each test sets (None: no file)."""
    cand = tmp_path / "cand.geojson"
    cand.write_text(json.dumps(_gj(LINE)))
    live = tmp_path / "routes" / "P9004.geojson"
    live.parent.mkdir()
    monkeypatch.setattr(rs.paths, "gem_route_path", lambda pid, commodity=None: live if live.exists() else None)
    monkeypatch.setattr(rs, "last_commit", lambda path: ("abc1234", "2026-10-21"))

    def put(gj):
        live.write_text(json.dumps(gj))
    return cand, put


def test_lines_ignore_z_props_order_and_tiny_float_noise():
    a = {"type": "FeatureCollection", "features": [
        {"type": "Feature", "properties": {"x": 1}, "geometry": {"type": "LineString", "coordinates": [[1, 2], [3, 4]]}},
        {"type": "Feature", "properties": {}, "geometry": {"type": "LineString", "coordinates": [[5, 6, 9], [7, 8]]}}]}
    b = {"type": "MultiLineString", "coordinates": [[[5.0000000001, 6], [7, 8]], [[1, 2], [3, 4]]]}
    assert rs.lines_of(a) == rs.lines_of(b)
    assert rs.lines_of({"type": "Point", "coordinates": [1, 2]}) is None
    assert rs.lines_of(None) is None


def test_same_geometry_and_mapped_sheet_is_applied(repo):
    cand, put = repo
    put({"type": "LineString", "coordinates": [[30.123457, 50.1], [31.5, 51.765432]]})
    j = rs.judge({"project_id": "P9004"}, cand, MAPPED_ROW, "gas")
    assert j == {"state": "same", "applied": {"by": "routes_repo", "at": "2026-10-21", "commit": "abc1234", "sheet": True},
                 "disagree": None}


def test_same_geometry_with_unmapped_sheet_disagrees_and_names_the_apply(repo):
    cand, put = repo
    put(_gj(LINE))
    j = rs.judge({"project_id": "P9004"}, cand, UNMAPPED_ROW, "gas")
    assert j["state"] == "same" and j["applied"] is None
    assert "abc1234" in j["disagree"] and "sheet half of the §8 apply" in j["disagree"]


def test_only_route_type_behind_points_at_the_backfill(repo):
    cand, put = repo
    put(_gj(LINE))
    row = dict(MAPPED_ROW, RouteType="Unavailable (cannot find route)")
    assert "--backfill-route-type" in rs.judge({"project_id": "P9004"}, cand, row, "gas")["disagree"]


def test_missing_or_different_repo_file_is_open(repo):
    cand, put = repo
    assert rs.judge({"project_id": "P9004"}, cand, UNMAPPED_ROW) == {"state": "missing", "applied": None, "disagree": None}
    put(_gj([[0, 0], [1, 1]]))
    assert rs.judge({"project_id": "P9004"}, cand, UNMAPPED_ROW) == {"state": "differs", "applied": None, "disagree": None}


def test_cb_stamped_sheet_without_matching_geometry_disagrees(repo):
    cand, put = repo
    row = dict(MAPPED_ROW, RouteNotes="CB: route traced from published map", RouteCreator="CB")
    j = rs.judge({"project_id": "P9004"}, cand, row)
    assert j["state"] == "missing" and j["applied"] is None and "has no file" in j["disagree"]
    put(_gj([[0, 0], [1, 1]]))
    assert "different geometry" in rs.judge({"project_id": "P9004"}, cand, row)["disagree"]


def test_a_replacement_that_differs_is_the_state_before_its_apply(repo):
    cand, put = repo
    put(_gj([[0, 0], [1, 1]]))
    row = dict(MAPPED_ROW, RouteNotes="CB: route traced from published map", RouteCreator="CB")
    j = rs.judge({"project_id": "P9004", "replacement": True}, cand, row)
    assert j == {"state": "differs", "applied": None, "disagree": None}


def test_staged_marker_wins_whatever_the_mirror_says(repo):
    cand, _ = repo
    rec = {"project_id": "P9004", "applied": {"date": "2026-10-22", "by": "apply_route_candidates", "commit": "def5678"}}
    j = rs.judge(rec, cand, UNMAPPED_ROW)
    assert j["applied"] == {"by": "apply_route_candidates", "at": "2026-10-22", "commit": "def5678"}


def test_snapshot_rows_reads_the_third_line_header(tmp_path):
    p = tmp_path / "snap.csv"
    p.write_text("banner,,\n1,2,3\nProjectID,RouteType,RouteAccuracy\nP1,a,b\nP1,c,d\nP2,e,f\n")
    rows = rs.snapshot_rows(p)
    assert rows["P1"] == {"ProjectID": "P1", "RouteType": "a", "RouteAccuracy": "b"} and set(rows) == {"P1", "P2"}
