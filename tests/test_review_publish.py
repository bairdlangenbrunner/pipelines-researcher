"""Phase 2: review_app/publish.py. Fixture staging dirs and a local mirror only; the Drive calls
are a fake `gws` that records what it was asked to do. Nothing here reaches Google."""
import gzip
import json
from pathlib import Path

import pytest

import gas_harness as H
import publish
import pull
import review_data
import review_fixture
import scopes
import store

ME = "baird@globalenergymonitor.org"


@pytest.fixture
def scope(tmp_path):
    s = review_fixture.make_scope(tmp_path)
    data, _ = review_data.build([s["qc"], s["deep"]], "Russia", "gas", data_dir=s["data"], root=s["root"])
    s["dataset"], s["dirs"] = data, store.dir_paths(data, tmp_path)
    return s


def lines(data):
    return [l for p in data["pipelines"] for l in p["lines"]]


def first(data, pid, kind):
    return next(l for p in data["pipelines"] if p["pid"] == pid for l in p["lines"] if l["kind"] == kind)


def gas_record(l, basis, reviewer=ME, **kw):
    """A line record as the Google store writes it (and pull mirrors it)."""
    return dict({"key": l["key"], "dir": l["dir"], "pid": "P9002", "sheet_row": l.get("sheet_row"),
                 "ref_col": l.get("ref_col") or "", "kind": l["kind"], "decision": "accept", "suggested_value": "",
                 "note": "", "reviewer": reviewer, "ts": "2099-01-01T01:00:00-05:00", "undecided": False,
                 "basis": basis, "id": "id-" + l["key"], "scope": "russia-gas", "batch": "b1",
                 "snapshot": "GGIT_gas_snapshot_20981231.csv", "origin": "gas"}, **kw)


# ---- parts -------------------------------------------------------------------------------

def test_parts_never_split_a_pipeline_and_reassemble(scope):
    d = scope["dataset"]
    one = publish.split_parts(d)
    assert len(one) == 1 and one[0] == d
    many = publish.split_parts(d, target=1500)
    assert len(many) > 1 and set(many[0]) == set(d) and all(list(p) == ["pipelines"] for p in many[1:])
    assert all(p["pipelines"] for p in many)
    assert [p["pid"] for part in many for p in part["pipelines"]] == [p["pid"] for p in d["pipelines"]]
    assert dict(many[0], pipelines=[p for part in many for p in part["pipelines"]]) == d


def test_write_scope_files_and_entry(scope, tmp_path):
    out = tmp_path / "out"
    e = H.publish_fixture(scope, out, target=1500)
    d = scope["dataset"]
    assert e["id"] == "russia-gas" and e["ver"] == H.VER and e["store_cursor"] == 1 and e["snapshot"] == d["scope"]["snapshot"]
    assert e["counts"] == {"pipelines": len(d["pipelines"]), "lines": len(lines(d)),
                           "items": sum(len(p["items"]) for p in d["pipelines"])}
    assert all(n.startswith("russia-gas.%s." % H.VER) for n in e["parts"] + [e["index"]])
    assert H.read_parts(out, e) == json.loads(json.dumps(d))
    (out / e["index"]).read_text(encoding="ascii")                     # the index is plain ASCII
    body = json.loads((out / "scopes.json").read_text())
    assert [s["id"] for s in body["scopes"]] == ["russia-gas"]
    with pytest.raises(SystemExit, match="scope id"):
        publish.write_scope(d, out, "Russia Gas", 1, tmp_path)


def test_geo_bundle_only_takes_files_inside_batches(scope, tmp_path):
    d = scope["dataset"]
    l = lines(d)[0]
    assert publish.geo_bundle(d, tmp_path) is None
    geo = {"type": "FeatureCollection", "features": []}
    (scope["dirs"][l["dir"]] / "P9001.geojson").write_text(json.dumps(geo))
    (tmp_path / "outside.geojson").write_text(json.dumps(geo))
    l["geometry_file"] = "P9001.geojson"
    assert publish.geo_bundle(d, tmp_path) == {l["dir"] + "/P9001.geojson": geo}
    l["geometry_file"] = "../../../../outside.geojson"
    assert publish.geo_bundle(d, tmp_path) is None


# ---- the index ---------------------------------------------------------------------------

def test_index_knows_every_key_and_packs_without_loss(scope):
    d = scope["dataset"]
    publish.stamp_basis(d, scope["dirs"])
    idx = publish.make_index(d)["keys"]
    assert set(idx) == {o["key"] for p in d["pipelines"] for g in ("lines", "items") for o in p[g]}
    status = next(l for p in d["pipelines"] if p["pid"] == "P9001" for l in p["lines"]
                  if l["kind"] == "ref" and l["column"] == "Status")
    concern = next(i for p in d["pipelines"] if p["pid"] == "P9001" for i in p["items"] if i["kind"] == "concern")
    assert idx[status["key"]]["lock"] == [{"c": concern["key"], "held": ["Status"], "res": []}]
    assert idx[status["key"]]["basis"] == status["basis"] and idx[concern["key"]] == \
        {"g": "i", "kind": "concern", "dir": concern["dir"], "pid": "P9001", "call0": ""}
    packed = publish.pack_index({"keys": idx})
    assert packed["v"] == 2 and len(packed["dirs"]) == len(packed["keys"]) == len({e["dir"] for e in idx.values()})
    assert sum(len(g) for g in packed["keys"]) == len(idx)
    for key, e in idx.items():
        dlabel, _, rest = key.partition("::")
        c = packed["keys"][packed["dirs"].index(dlabel)][rest]
        if e["g"] == "i":
            assert (c["i"], c["p"], c.get("c0", "")) == (e["kind"], e["pid"], e["call0"])
        else:
            assert (c["k"], c["p"], c.get("r"), c.get("c", ""), c.get("d", "accept"), c["b"]) == \
                (e["kind"], e["pid"], e["sheet_row"], e["ref_col"], e["def"], e["basis"])
            assert [x[0] for x in c.get("l", [])] == [x["c"] for x in e.get("lock", [])]
    with pytest.raises(SystemExit, match="does not start with its dir"):
        publish.pack_index({"keys": {"elsewhere::P1|4|x": dict(idx[status["key"]])}})


def test_an_item_already_called_is_published_as_called(scope):
    d = scope["dataset"]
    concern = next(i for p in d["pipelines"] for i in p["items"] if i["kind"] == "concern")
    store.record_items([{"key": concern["key"], "call": "dismissed"}], d, "Baird", dirs=scope["dirs"])
    store.overlay(d, scope["dirs"])
    assert publish.make_index(d)["keys"][concern["key"]]["call0"] == "dismissed"


# ---- basis, drift, orphans ---------------------------------------------------------------

def test_basis_follows_the_backend_cells_only(scope):
    l = dict(first(scope["dataset"], "P9002", "fill"))
    b = publish.basis(l)
    assert len(b) == 12 and publish.basis(dict(l, note="x", decision="accept", proposed="9")) == b
    for f in publish.BASIS_FIELDS:
        assert publish.basis(dict(l, **{f: "changed"})) != b


def test_drift_flags_a_persons_call_made_against_other_cells(scope):
    d, dirs = scope["dataset"], scope["dirs"]
    l = first(d, "P9002", "fill")
    assert publish.stamp_basis(d, dirs) == [] and l["basis"] == publish.basis(l) and "drift" not in l
    store.append_records([gas_record(l, l["basis"])], dirs)
    assert publish.stamp_basis(d, dirs) == []                          # decided against these very cells
    l["current"] = "something a colleague typed since"
    (hit,) = publish.stamp_basis(d, dirs)
    assert hit is l and l["drift"]["decided_snapshot"] == "GGIT_gas_snapshot_20981231.csv"
    assert l["drift"]["decided_basis"] != l["basis"] and len(l["drift"]["decided_basis"]) == 12
    l["in_backend"] = True                                             # the sheet now holds the proposal: nothing to redo
    assert publish.stamp_basis(d, dirs) == [] and "drift" not in l
    l["in_backend"] = False
    store.append_records([gas_record(l, "0" * 12, id="undo", undecided=True)], dirs)
    assert publish.stamp_basis(d, dirs) == []                          # an undone call cannot be stale


def test_drift_ignores_machine_records_and_records_without_a_basis(scope):
    d, dirs = scope["dataset"], scope["dirs"]
    a, b = first(d, "P9002", "fill"), first(d, "P9001", "ref")
    store.append_records([gas_record(a, "0" * 12, reviewer=store.SYNC_REVIEWER)], dirs)
    store.decide([{"key": b["key"], "decision": "hold"}], d, "Baird", dirs=dirs)      # a phase 1 record: no basis
    assert publish.stamp_basis(d, dirs) == []


def test_orphans_are_person_decisions_whose_key_is_gone(scope):
    d, dirs = scope["dataset"], scope["dirs"]
    l = first(d, "P9002", "fill")
    assert publish.orphans(d, dirs) == []
    moved = l["key"].replace("|5|", "|6|")
    assert moved != l["key"]
    store.append_records([gas_record(l, "b", key=moved, id="1"),
                          gas_record(l, "b", key=moved + "x", id="2", reviewer=store.SYNC_REVIEWER),
                          gas_record(l, "b", key=moved + "y", id="3", undecided=True)], dirs)
    assert [r["key"] for r in publish.orphans(d, dirs)] == [moved]


def test_a_renumbered_row_carries_the_decision_to_the_new_key(scope):
    d, dirs = scope["dataset"], scope["dirs"]
    l = first(d, "P9002", "fill")
    old = l["key"].replace("|5|", "|4|")                      # decided when the pipeline sat one row up
    assert old != l["key"]
    store.append_records([gas_record(l, "b", key=old, id="s1", sheet_row=4)], dirs)
    assert [r["key"] for r in publish.orphans(d, dirs)] == [old]
    got = publish.carry_forward(d, dirs)
    assert [(r["key"], r["rekeyed_from"], r["sheet_row"], r["id"], r["reviewer"], r["ts"]) for r in got] == \
        [(l["key"], old, 5, "s1~rekey", ME, "2099-01-01T01:00:00-05:00")]
    log = store.read_log(dirs[l["dir"]])
    assert log[-2]["key"] == old and log[-1]["key"] == l["key"]            # the old record is still there
    store.overlay(d, dirs)
    assert (l["decision"], l["decided_by"], l["reviewed"]) == ("accept", ME, True)
    assert publish.orphans(d, dirs) == [] and publish.carry_forward(d, dirs) == []      # once
    store.decide([{"key": l["key"], "decision": "hold"}], d, "Baird", dirs=dirs)         # a later call on the new key
    assert publish.orphans(d, dirs) == [] and publish.carry_forward(d, dirs) == []


def test_carry_forward_leaves_the_doubtful_ones_as_orphans(scope):
    d, dirs = scope["dataset"], scope["dirs"]
    l = first(d, "P9002", "fill")
    a, b = l["key"].replace("|5|", "|4|"), l["key"].replace("|5|", "|3|")
    store.append_records([gas_record(l, "b", key=a, id="1"), gas_record(l, "b", key=b, id="2"),      # two want one key
                          gas_record(l, "b", key=a + "x", id="3"),                                     # another column
                          gas_record(l, "b", key=a + "y", id="4", reviewer=store.SYNC_REVIEWER)], dirs)
    assert publish.carry_forward(d, dirs) == []
    assert sorted(r["key"] for r in publish.orphans(d, dirs)) == sorted([a, b, a + "x"])
    m = first(d, "P9001", "ref")
    gone = m["key"].replace("|%s|" % m["sheet_row"], "|999|")
    store.append_records([gas_record(m, "b", key=gone, id="5"),
                          gas_record(m, "b", id="6", reviewer=store.SYNC_REVIEWER)], dirs)     # the new key already holds a record
    assert publish.carry_forward(d, dirs) == [] and gone in [r["key"] for r in publish.orphans(d, dirs)]


def test_restore_reviewers_puts_the_address_back_for_the_private_dataset(scope):
    d, dirs = scope["dataset"], scope["dirs"]
    l, m = first(d, "P9002", "fill"), first(d, "P9001", "ref")
    store.append_records([gas_record(l, "b", id="s1", reviewer="B"),
                          gas_record(m, "b", id="s2~rekey", reviewer="A"),
                          ], dirs)
    store.overlay(d, dirs)
    assert publish.restore_reviewers(d, dirs, {}) == 0 and l["decided_by"] == "B"
    n = publish.restore_reviewers(d, dirs, {"s1": ME, "s2": "aiganym@globalenergymonitor.org", "s9": "x@y.org"})
    assert n == 2 and l["decided_by"] == ME and m["decided_by"] == "aiganym@globalenergymonitor.org"
    assert store.read_log(dirs[l["dir"]])[-2]["reviewer"] == "B"      # the log keeps the initials


# ---- scopes.json and the Drive plan --------------------------------------------------------

def entry(sid, ver, label=None, geo=False):
    return {"id": sid, "label": label or sid, "ver": ver, "published": "t-" + ver,
            "parts": [f"{sid}.{ver}.part0.json.gz", f"{sid}.{ver}.part1.json.gz"],
            "index": f"{sid}.{ver}.index.json", "geo": f"{sid}.{ver}.geo.json.gz" if geo else None}


def test_merge_scopes_replaces_only_its_own_scope():
    a, b = entry("russia-gas", "v1"), entry("egypt-gas", "v1")
    body = publish.merge_scopes({"scopes": [a, b]}, entry("russia-gas", "v2"))
    assert [(s["id"], s["ver"]) for s in body["scopes"]] == [("egypt-gas", "v1"), ("russia-gas", "v2")]
    assert body["updated"] == "t-v2" and publish.merge_scopes(None, a)["scopes"] == [a]


def test_plan_upload_keeps_one_version_back_and_other_scopes():
    new = entry("russia-gas", "v3", geo=True)
    names = ["scopes.json", "russia-gas.v1.part0.json.gz", "russia-gas.v1.index.json", "russia-gas.v2.part0.json.gz",
             "russia-gas.v2.index.json", "russia-gas.v3.part0.json.gz", "russia-gas-north.v1.part0.json.gz",
             "egypt-gas.v1.part0.json.gz", "notes.txt"]
    files = [{"id": "f%d" % i, "name": n} for i, n in enumerate(names)]
    create, trash = publish.plan_upload(new, files, "v2")
    assert create == ["russia-gas.v3.part1.json.gz", "russia-gas.v3.index.json", "russia-gas.v3.geo.json.gz"]
    assert [f["name"] for f in trash] == ["russia-gas.v1.part0.json.gz", "russia-gas.v1.index.json"]
    assert [f["name"] for f in publish.plan_upload(new, files, None)[1]] == \
        ["russia-gas.v1.part0.json.gz", "russia-gas.v1.index.json", "russia-gas.v2.part0.json.gz", "russia-gas.v2.index.json"]


class FakeGws:
    """Stands in for pull.gws: a Drive folder as a list of files, every call recorded."""

    def __init__(self, files=(), scopes_body=None):
        self.files, self.calls, self.scopes_body = list(files), [], scopes_body

    def __call__(self, profile, *args, parse=True):
        self.calls.append((profile, args))
        verb = args[2]
        if verb == "list":
            return {"files": self.files}
        if verb == "get":
            return json.dumps(self.scopes_body)      # real gws prints an alt=media body to stdout
        return {"id": "new", "name": "x"}

    def writes(self):
        return [(p, a) for p, a in self.calls if a[2] not in ("list", "get")]


def test_upload_is_plan_only_without_yes_and_ordered_with_it(scope, tmp_path):
    out = tmp_path / "out"
    old = H.publish_fixture(scope, out, ver="20990101T000000")
    e = H.publish_fixture(scope, out, ver="20990102T000000")
    folder = [{"id": "s", "name": "scopes.json", "modifiedTime": "1"},
              {"id": "o1", "name": "russia-gas.20981231T000000.part0.json.gz"}] + \
             [{"id": "p%d" % i, "name": n} for i, n in enumerate(old["parts"] + [old["index"]])]
    other = entry("egypt-gas", "v1")
    with pytest.raises(SystemExit, match="data_folder_id"):
        publish.upload(out, e, {"data_folder_id": ""}, gws=FakeGws())

    g, said = FakeGws(folder, {"scopes": [other, old]}), []
    body = publish.upload(out, e, {"data_folder_id": "F"}, gws=g, say=said.append)
    assert g.writes() == [] and {p for p, _ in g.calls} == {pull.READ_PROFILE}
    assert any("plan only" in x for x in said) and {s["id"] for s in body["scopes"]} == {"egypt-gas", "russia-gas"}
    assert sum("CREATE" in x for x in said) == len(e["parts"]) + 1 and sum("TRASH" in x for x in said) == 1

    g = FakeGws(folder, {"scopes": [other, old]})
    publish.upload(out, e, {"data_folder_id": "F"}, yes=True, gws=g, say=said.append)
    w = g.writes()
    assert {p for p, _ in w} == {pull.WRITE_PROFILE}
    verbs = [a[2] for _, a in w]
    n = len(e["parts"]) + 1
    assert verbs == ["create"] * n + ["update", "update"]             # files, then the switch, then the trash
    switch, trash = w[n][1], w[n + 1][1]
    assert json.loads(switch[switch.index("--params") + 1])["fileId"] == "s" and "--upload" in switch
    assert json.loads(trash[trash.index("--json") + 1]) == {"trashed": True}
    assert json.loads(trash[trash.index("--params") + 1])["fileId"] == "o1"
    live = json.loads((out / "scopes.json").read_text())
    assert {(s["id"], s["ver"]) for s in live["scopes"]} == {("egypt-gas", "v1"), ("russia-gas", "20990102T000000")}


# ---- the whole run -------------------------------------------------------------------------

def test_publish_builds_from_disk_and_reports(scope, tmp_path):
    d, dirs = scope["dataset"], scope["dirs"]
    l = first(d, "P9002", "fill")
    store.append_records([gas_record(l, "0" * 12), gas_record(l, "b", key=l["key"] + "-gone", id="g")], dirs)
    out = tmp_path / "out"
    e, rep = publish.publish(["Russia"], "gas", out, dirs=[scope["qc"], scope["deep"]], batches_root=scope["root"],
                             data_dir=scope["data"], cursor=7, ver="20990105T000000")
    assert (e["id"], e["label"], e["store_cursor"], e["build"]["batch"]) == ("russia-gas", "Russia gas", 7, False)
    assert [x["key"] for x in rep["drift"]] == [l["key"]] and [r["key"] for r in rep["orphans"]] == [l["key"] + "-gone"]
    assert rep["decided"] == 1 and set(rep["files"]) == set(e["parts"] + [e["index"]]) and rep["carried"] == []
    got = next(x for x in lines(H.read_parts(out, e)) if x["key"] == l["key"])
    assert got["decision"] == "accept" and got["decided_by"] == ME and got["drift"]["decided_basis"] == "0" * 12
    text = publish.report(e, rep)
    assert "drift" in text and l["key"] in text and "orphans" in text


def test_main_defaults_to_the_review_app_batch(scope, tmp_path, capsys):
    manifest = tmp_path / "manifest.json"
    scopes.save({"scopes": [{"country": "Russia", "commodity": "gas", "state": "included", "decided": "2099-01-01"},
                            {"country": "Egypt", "commodity": "gas", "state": "included", "decided": "2099-01-01"},
                            {"country": "India", "commodity": "gas", "state": "declined", "decided": "2099-01-01"}]}, manifest)
    args = ["--manifest", str(manifest), "--batches-root", str(scope["root"]), "--data-dir", str(scope["data"]),
            "--out", str(tmp_path / "out"), "--no-pull"]
    e, _ = publish.main(args)
    assert e["id"] == "review-app-gas" and e["build"]["country"] == ["Russia"] and e["build"]["batch"] is True
    assert e["label"] == "review batch: gas (1 country)" and e["counts"]["pipelines"] > 0
    assert H.read_parts(tmp_path / "out", e)["scope"]["batch"] is True
    e2, _ = publish.main(["--country", "Russia", "--commodity", "gas"] + args[2:])
    assert e2["id"] == "russia-gas" and e2["build"]["batch"] is False
    assert {s["id"] for s in json.loads((tmp_path / "out" / "scopes.json").read_text())["scopes"]} == {"russia-gas", "review-app-gas"}
    with pytest.raises(SystemExit, match="includes no oil"):
        publish.main(["--commodity", "oil"] + args)
    with pytest.raises(SystemExit, match="--yes only"):
        publish.main(args + ["--yes"])


def test_publish_carries_a_renumbered_decision_and_restores_the_address(scope, tmp_path):
    d, dirs = scope["dataset"], scope["dirs"]
    l = first(d, "P9002", "fill")
    old = l["key"].replace("|5|", "|4|")
    store.append_records([gas_record(l, publish.basis(l), key=old, id="s1", reviewer=store.initials(ME))], dirs)
    out = tmp_path / "out"
    e, rep = publish.publish(["Russia"], "gas", out, dirs=[scope["qc"], scope["deep"]], batches_root=scope["root"],
                             data_dir=scope["data"], ver="20990106T000000", emails={"s1": ME})
    assert [r["rekeyed_from"] for r in rep["carried"]] == [old] and rep["orphans"] == [] and rep["drift"] == []
    got = next(x for x in lines(H.read_parts(out, e)) if x["key"] == l["key"])
    assert (got["decision"], got["decided_by"], got["reviewed"]) == ("accept", ME, True)
    assert "carried forward" in publish.report(e, rep) and old in publish.report(e, rep)
    assert ME not in (dirs[l["dir"]] / "review_log.jsonl").read_text()


def test_a_fill_decided_under_its_first_column_alone_carries_to_the_multi_column_key(scope):
    # before 2026-10-01 a fill's key named its first value column only (`…|Capacity`); the
    # decision made under that key moves to `…|Capacity+CapacityUnits`, once, by dir + pid + column
    d, dirs = scope["dataset"], scope["dirs"]
    l = first(d, "P9002", "fill")
    assert l["key"].endswith("|Capacity+CapacityUnits")
    old = l["key"].replace("|Capacity+CapacityUnits", "|Capacity")
    store.append_records([gas_record(l, "b", key=old, id="legacy1")], dirs)
    assert [r["key"] for r in publish.orphans(d, dirs)] == [old]
    got = publish.carry_forward(d, dirs)
    assert [(r["key"], r["rekeyed_from"], r["id"]) for r in got] == [(l["key"], old, "legacy1~rekey")]
    store.overlay(d, dirs)
    assert (l["decision"], l["reviewed"]) == ("accept", True)
    assert publish.orphans(d, dirs) == [] and publish.carry_forward(d, dirs) == []
    # a legacy key naming a column that no multi-column fill of this pid carries stays an orphan
    store.append_records([gas_record(l, "b", key=old.replace("|Capacity", "|Length"), id="legacy2")], dirs)
    assert publish.carry_forward(d, dirs) == [] and len(publish.orphans(d, dirs)) == 1
