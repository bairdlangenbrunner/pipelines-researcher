"""push.build_plan against a FAKE live tab (push.Tab monkeypatched; nothing reads the sheet):
the value rules (fill blank / leave equal / replace the value the reviewer saw / conflict on
anything else), the already-pushed skip and the person-call-past-a-push-record rule."""
import csv
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "review_app"))
import push  # noqa: E402
import review_data  # noqa: E402
import review_fixture  # noqa: E402
import store  # noqa: E402


class FakeTab(push.Tab):
    """A push.Tab over a CSV snapshot instead of the live sheet; `edits` = {(pid, col): value}."""
    def __init__(self, path, header_idx, edits):
        with open(path, encoding="utf-8", newline="") as f:
            rows = list(csv.reader(f))
        self.title, self.header_idx, self.rows = path.name, header_idx, rows
        self.header = rows[header_idx]
        self.col = {}
        for i, c in enumerate(self.header):
            self.col.setdefault(c, i)
        pid = self.col["ProjectID"]
        self.by_pid = {}
        for i, r in enumerate(rows):
            if i > header_idx and len(r) > pid and r[pid].strip():
                self.by_pid.setdefault(r[pid].strip(), []).append(i + 1)
        for (p, c), v in edits.items():
            if c not in self.col:                       # an edit meant for the other tab
                continue
            for row in self.by_pid[p]:
                r = self.rows[row - 1]
                while len(r) <= self.col[c]:
                    r.append("")
                r[self.col[c]] = v


@pytest.fixture
def world(tmp_path, monkeypatch):
    s = review_fixture.make_scope(tmp_path)
    data, _ = review_data.build([s["qc"], s["deep"]], "Russia", "gas", data_dir=s["data"], root=s["root"])
    data["scope"]["batch"] = True
    dirs = store.dir_paths(data, tmp_path)
    edits = {}
    monkeypatch.setattr(push, "Tab", lambda title, hdr: FakeTab(
        s["data"] / (review_fixture.OWN_NAME if title == push.OO_TITLE else review_fixture.SNAP_NAME), hdr, edits))
    monkeypatch.setattr(push.scopes, "included", lambda commodity, _c: ["Russia"])
    monkeypatch.setattr(push.staged_store, "BATCHES_ROOT", s["root"])
    monkeypatch.setattr(push.review_data, "_country_dirs", lambda *a, **k: ([s["qc"], s["deep"]], None))
    real_build = push.review_data.build
    monkeypatch.setattr(push.review_data, "build", lambda dirs_, c, cm, root=None, dir_country=None, data_dir=None:
                        real_build(dirs_, c, cm, data_dir=data_dir or s["data"], root=root))
    monkeypatch.setattr(push.ledger, "scope_of", lambda ds: ("russia-gas", review_fixture.SNAP_NAME))
    s.update(dataset=data, dirs=dirs, edits=edits)
    return s


def set_snapshot(world, pid, col, value):
    """Rewrite one cell of the snapshot CSV (what the reviewer saw) and rebuild the dataset over it."""
    path = world["data"] / review_fixture.SNAP_NAME
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.reader(f))
    hdr = rows[2]
    for r in rows[3:]:
        if r[hdr.index("ProjectID")] == pid:
            r[hdr.index(col)] = value
    with open(path, "w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)
    data, _ = review_data.build([world["qc"], world["deep"]], "Russia", "gas", data_dir=world["data"], root=world["root"])
    data["scope"]["batch"] = True
    world["dataset"] = data


def line(data, pid, kind, col=None):
    for p in data["pipelines"]:
        if p["pid"] == pid:
            for l in p["lines"]:
                if l["kind"] == kind and (col is None or l["column"] == col):
                    return l
    raise AssertionError((pid, kind, col))


def accept(w, l, who="BL"):
    return store.decide([{"key": l["key"], "decision": "accept"}], w["dataset"], who, dirs=w["dirs"])


def plan_for(w, key):
    plan, skipped, meta = push.build_plan("gas")
    mine = [p for p in plan if key in p["lines"]]
    why = dict(skipped).get(key)
    return mine, why, meta


def test_blank_cell_is_filled_and_nothing_pushes_without_a_person(world):
    fill = line(world["dataset"], "P9002", "fill")              # Capacity blank on P9002
    assert push.build_plan("gas")[0] == []                       # undecided: nothing
    accept(world, fill, who=store.SYNC_REVIEWER)                 # a machine accept is not a decision
    assert push.build_plan("gas")[0] == []
    accept(world, fill)
    mine, why, _ = plan_for(world, fill["key"])
    assert why is None and {p["column"] for p in mine} >= set(fill["proposed_values"]) | {fill["ref_col"]}
    assert all(not p["replaces"] for p in mine)


def test_value_the_reviewer_saw_is_replaced_but_a_moved_cell_is_stale(world):
    col = line(world["dataset"], "P9002", "fill")["column"]
    # the snapshot (what the reviewer saw) holds 7; so does the live tab -> the accepted change replaces it
    set_snapshot(world, "P9002", col, "7")
    fill = line(world["dataset"], "P9002", "fill")
    assert fill["current"][col] == "7" and str(fill["proposed_values"][col]) != "7"
    world["edits"][("P9002", col)] = "7"
    accept(world, fill)
    mine, why, _ = plan_for(world, fill["key"])
    assert why is None
    cell = next(p for p in mine if p["column"] == col)
    assert (cell["before"], str(cell["after"]), cell["replaces"]) == ("7", str(fill["proposed_values"][col]), True)
    assert not next(p for p in mine if p["column"] == fill["ref_col"])["replaces"]     # a ref cell is additive, never a replace
    # live moved to a third value since: the line is stale (the staleness check runs first), skipped whole
    world["edits"][("P9002", col)] = "8"
    mine, why, _ = plan_for(world, fill["key"])
    assert mine == [] and why == f"stale: {col} was '7', live '8'"
    # ... and only --include-stale writes over it (the accept is the authorization; the stale list names it)
    plan, skipped, meta = push.build_plan("gas", include_stale=True)
    cell = next(p for p in plan if fill["key"] in p["lines"] and p["column"] == col)
    assert (cell["before"], cell["replaces"]) == ("8", True) and fill["key"] in dict(meta["__stale__"])


def test_a_pushed_line_is_never_planned_twice_and_its_accept_still_speaks(world):
    fill = line(world["dataset"], "P9002", "fill")
    accept(world, fill)
    ts = (datetime.now(store.ET) + timedelta(minutes=1)).isoformat(timespec="seconds")   # the push came after the accept
    store.append_records([{"key": fill["key"], "dir": fill["dir"], "pid": "P9002", "sheet_row": fill["sheet_row"],
                           "ref_col": fill["ref_col"], "kind": "fill", "decision": "accept", "suggested_value": "",
                           "note": "written", "reviewer": "push", "ts": ts, "undecided": False}],
                         world["dirs"])
    store.overlay(world["dataset"], world["dirs"])
    assert (fill["reviewed"], fill["decision"], fill["decided_by"]) == (True, "accept", "BL")
    assert fill["applied"] == {"by": "push", "at": ts}
    mine, why, _ = plan_for(world, fill["key"])
    assert mine == [] and why == "already pushed " + ts
    # the person decides again after the push (undo, then accept): the newer call plans it afresh,
    # and the sheet already holding the pushed value makes that "already in the backend"
    later = (datetime.now(store.ET) + timedelta(minutes=2)).isoformat(timespec="seconds")
    store.append_records([{"key": fill["key"], "dir": fill["dir"], "pid": "P9002", "sheet_row": fill["sheet_row"],
                           "ref_col": fill["ref_col"], "kind": "fill", "decision": "accept", "suggested_value": "",
                           "note": "", "reviewer": "BL", "ts": later, "undecided": False}], world["dirs"])
    world["edits"][("P9002", fill["column"])] = str(fill["proposed_values"][fill["column"]])
    world["edits"][("P9002", "CapacityUnits")] = fill["proposed_values"]["CapacityUnits"]
    world["edits"][("P9002", fill["ref_col"])] = ", ".join(fill["proposed_refs"])
    mine, why, _ = plan_for(world, fill["key"])
    assert mine == [] and why == "already in the backend"


def test_already_in_backend_is_reported_not_planned(world):
    held = line(world["dataset"], "P9005", "fill")             # snapshot already holds value + ref
    accept(world, held)
    mine, why, _ = plan_for(world, held["key"])
    assert mine == [] and why == "already in the backend"


def suggest(w, l, value, who="BL"):
    return store.decide([{"key": l["key"], "decision": "suggest", "suggested_value": value}], w["dataset"], who, dirs=w["dirs"])


def test_suggest_writes_the_named_cell(world):
    fill = line(world["dataset"], "P9002", "fill")
    cols = [c for c in fill["proposed_values"]]
    col = cols[0]
    suggest(world, fill, f"{col}=Elsewhere")
    mine, why, meta = plan_for(world, fill["key"])
    assert why is None
    cell = next(p for p in mine if p["column"] == col)
    assert cell["after"] == "Elsewhere"
    assert not any(p["column"] in cols[1:] for p in mine)          # the proposal's other cells are not written


def test_a_bare_suggest_on_a_multi_column_line_is_skipped_not_guessed(world):
    fill = line(world["dataset"], "P9002", "fill")
    fill = dict(fill)
    multi = [l for p in world["dataset"]["pipelines"] for l in p["lines"]
             if l["kind"] in ("fill", "oo") and sum(v not in (None, "") for v in (l.get("proposed_values") or {}).values()) > 1]
    if not multi:
        pytest.skip("fixture has no multi-column line")
    suggest(world, multi[0], "Elsewhere")
    mine, why, _ = plan_for(world, multi[0]["key"])
    assert mine == [] and why and "names no cell" in why


def test_geo_concerns_flag_a_location_left_behind_by_a_state_change():
    class T:
        col = {"EndLocation": 0, "EndState/Province": 1, "EndPrefecture/District": 2, "EndCountryOrArea": 3}
        def cell(self, row, c):
            return {"EndLocation": "Westchester County", "EndState/Province": "New York"}.get(c, "")
    out = push.geo_concerns("P1", 11, {"EndState/Province": "Massachusetts"}, T())
    assert len(out) == 1 and out[0]["check"] == ["EndLocation"] and "Westchester County" in out[0]["text"]
    assert push.geo_concerns("P1", 11, {"EndLocation": "Boston"}, T()) == []     # a finer cell raises nothing


def test_a_rival_suggest_pushes_the_concerns_candidate_cell_with_the_concerns_refs(world):
    import json
    p9001 = next(p for p in world["dataset"]["pipelines"] if p["pid"] == "P9001")
    ln = next(l for l in p9001["lines"] if l["kind"] == "ref" and l["column"] == "Status")
    col = "Status"
    for d in (world["deep"], world["qc"]):
        f = d / "staged_resolutions.json"
        doc = json.loads(f.read_text())
        for r in doc["resolutions"]:
            if r.get("ref_col") == "__VALIDITY__" and r["project_id"] == "P9001":
                r["contested"] = {col: "Rival value"}
                r["proposed_refs"] = ["https://example.org/rival"]
        f.write_text(json.dumps(doc))
    data, _ = review_data.build([world["qc"], world["deep"]], "Russia", "gas", data_dir=world["data"], root=world["root"])
    data["scope"]["batch"] = True
    world["dataset"] = data
    ln = next(l for p in data["pipelines"] if p["pid"] == "P9001" for l in p["lines"] if l["key"] == ln["key"])
    rv = store.rival_of(ln, ln["rivals"][0]["key"])
    store.decide([{"key": ln["key"], "rival": rv["key"]}], data, "BL", dirs=world["dirs"])
    mine, why, _ = plan_for(world, ln["key"])
    assert why is None
    cell = next(p for p in mine if p["column"] == col)
    assert cell["after"] == "Rival value"
    assert not any(p["column"] in ln["proposed_values"] for p in mine if p["column"] not in (col, ln["ref_col"]))
    if ln.get("ref_col"):
        assert "https://example.org/rival" in next(p for p in mine if p["column"] == ln["ref_col"])["after"]


# ---------------------------------------------------------------- owner-style (tracker-wide) lines
@pytest.fixture
def style_world(world, monkeypatch):
    """The review-app batch with the tracker-wide owner-style scope included beside Russia gas."""
    s = world
    dirs = [s["qc"], s["deep"], s["style"]]
    dc = {s["qc"].resolve(): "Russia", s["deep"].resolve(): "Russia", s["style"].resolve(): "*"}
    monkeypatch.setattr(push.scopes, "included", lambda commodity, _c: ["*", "Russia"])
    monkeypatch.setattr(push.review_data, "_country_dirs", lambda *a, **k: (dirs, dc))
    real_build = review_data.build
    monkeypatch.setattr(push.review_data, "build", lambda dirs_, c, cm, root=None, dir_country=None, data_dir=None:
                        real_build(dirs_, c, cm, data_dir=s["data"], root=root, dir_country=dir_country))
    data, _ = real_build(dirs, ["Russia", "*"], "gas", data_dir=s["data"], root=s["root"], dir_country=dc)
    data["scope"]["batch"] = True
    s["dataset"], s["dirs"] = data, store.dir_paths(data, s["tmp"])
    return s


def _style_line(data, pid, col):
    for p in data["pipelines"]:
        if p["pid"].startswith("name:"):
            for l in p["lines"]:
                if l["pid"] == pid and l["column"] == col:
                    return l
    raise AssertionError((pid, col))


def test_style_line_writes_its_own_pid_row_and_stamps_lastupdated_only(style_world):
    w = style_world
    l = _style_line(w["dataset"], "P9001", "Owner1")
    assert push.build_plan("gas")[0] == []
    accept(w, l)
    plan, skipped, meta = push.build_plan("gas")
    assert dict(skipped).get(l["key"]) is None
    mine = [p for p in plan if l["key"] in p["lines"]]
    assert [(p["tabkey"], p["sheet_row"], p["ProjectID"], p["column"], p["before"], p["after"], p["replaces"]) for p in mine] == \
        [("oo", 3, "P9001", "Owner1", "OldCo", "OldCo Ltd", True)]              # the owners-tab row of P9001, the value alone
    stamps = {p["column"]: p for p in plan if p["tabkey"] == "oo" and p["sheet_row"] == 3 and not p["lines"]}
    assert "LastUpdated" in stamps and "Researcher" not in stamps               # style-only: the researcher stays
    assert meta["__style_only_rows__"] == ["oo:3:P9001"] and meta["__unstyled__"] == []
    # the clear: an accepted blank over the duplicate Owner2 empties the cell
    c = _style_line(w["dataset"], "P9002", "Owner2")
    accept(w, c)
    plan, skipped, meta = push.build_plan("gas")
    cell = next(p for p in plan if c["key"] in p["lines"])
    assert (cell["sheet_row"], cell["column"], cell["before"], cell["after"]) == (4, "Owner2", "Dup Co", "")


def test_style_line_is_stale_when_the_live_spelling_moved(style_world):
    w = style_world
    l = _style_line(w["dataset"], "P9001", "Owner1")
    accept(w, l)
    w["edits"][("P9001", "Owner1")] = "Old Company"
    plan, skipped, meta = push.build_plan("gas")
    assert not [p for p in plan if l["key"] in p["lines"]]
    assert dict(skipped)[l["key"]].startswith("stale: Owner1 was 'OldCo', live 'Old Company'")
