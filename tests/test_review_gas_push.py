"""review_app/gas_push.py: the Apps Script project as a Drive import. A fake `gws` stands in for
Drive; nothing here reaches Google."""
import json

import pytest

import bundle
import gas_push

CFG = {"data_folder_id": "F", "store_sheet_id": "S", "script_id": "SCRIPT"}


class FakeDrive:
    def __init__(self, files):
        self.files, self.calls = files, []

    def __call__(self, profile, *args, parse=True):
        self.calls.append((profile, args[:3]))
        if args[:3] == ("drive", "files", "export"):
            open(args[args.index("-o") + 1], "w", encoding="utf-8").write(json.dumps({"files": self.files}))
            return ""
        assert args[:3] == ("drive", "files", "update") and profile == "gws-gem-write"
        assert args[args.index("--upload-content-type") + 1] == bundle.PROJECT_MIME
        self.files = json.loads(open(args[args.index("--upload") + 1], encoding="utf-8").read())["files"]
        return {"id": "SCRIPT"}


def repo_files():
    return bundle.project(bundle.bundle(), bundle.config_gs(CFG))["files"]


def test_plan_matches_by_name_keeps_ids_and_ignores_how_drive_rewrites_the_manifest():
    new = {"files": repo_files()}
    cur = {"files": [dict(f, id="id-" + f["name"]) for f in new["files"]]}
    cur["files"][0]["source"] = json.dumps(dict(json.loads(cur["files"][0]["source"]), dependencies={}), indent=4)
    body, states = gas_push.plan(cur, new)
    assert {st for _, st in states} == {"same"} and [f["id"] for f in body["files"]] == ["id-" + f["name"] for f in new["files"]]
    cur["files"][1]["source"] += "\n// edited in the browser"
    cur["files"] = cur["files"][:2] + cur["files"][3:] + [{"id": "x", "name": "Scratch", "type": "server_js", "source": ""}]
    body, states = gas_push.plan(cur, new)
    assert dict(states) == {"appsscript": "same", "Code": "changed", "Config": "new", "index": "same", "Scratch": "removed"}
    assert "id" not in next(f for f in body["files"] if f["name"] == "Config")


def test_push_is_plan_only_without_yes_and_reads_back_with_it(tmp_path):
    drive, said = FakeDrive([dict(f, id="i%d" % i) for i, f in enumerate(repo_files())]), []
    assert {st for _, st in gas_push.push(CFG, tmp_path, yes=True, gws=drive, say=said.append)} == {"same"}
    assert all(c[1][2] == "export" for c in drive.calls) and "nothing to push" in said[-1]
    drive.files[1]["source"] = "// old"
    drive.calls.clear()
    gas_push.push(CFG, tmp_path, gws=drive, say=said.append)
    assert "plan only" in said[-1] and drive.files[1]["source"] == "// old" and all(p == "gws-gem" for p, _ in drive.calls)
    gas_push.push(CFG, tmp_path, yes=True, gws=drive, say=said.append)
    assert drive.files[1]["source"] != "// old" and drive.files[1]["id"] == "i1" and "deploy a new version" in said[-1]


def test_push_refuses_without_a_project_or_the_ids(tmp_path):
    with pytest.raises(SystemExit, match="no script_id"):
        gas_push.push({"data_folder_id": "F", "store_sheet_id": "S"}, tmp_path, gws=None)
    with pytest.raises(SystemExit, match="needs data_folder_id"):
        gas_push.push({"script_id": "X"}, tmp_path, gws=None)


def test_ref_write_additive_only_while_the_value_stays():
    import push
    rw = push.ref_write
    assert rw("a", ["a", "b"], [], [], ["V"]) == "a, b"          # same value: append
    assert rw("a", ["a"], [], [], ["V"]) is None
    assert rw("a, b", [], ["Cap"], [], []) == ""                  # cleared, nothing left: refs go
    assert rw("a, b", [], ["Cap"], [], ["Units"]) is None         # cluster still has a value
    assert rw("", [], ["Cap"], [], []) is None
    assert rw("old", ["new"], [], ["Cap"], ["Cap"]) == "new"      # changed: replace
    assert rw("old", [], [], ["Cap"], ["Cap"])[0] == "skip"
