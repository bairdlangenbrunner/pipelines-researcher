"""The artifact page (review_app/build_static.py) and the way its decisions come back
(review_app/import_log.py): store first, sidecars second, by id, in time order."""
import base64
import gzip
import json
import re

import pytest

import build_static
import bundle
import import_log
import ledger
import publish
import review_data
import review_fixture
import store
from test_review_ledger import FakeStore, logrecs

AL = "amalia.llano@globalenergymonitor.org"


@pytest.fixture
def scope(tmp_path):
    s = review_fixture.make_scope(tmp_path)
    data, _ = review_data.build([s["qc"], s["deep"]], "Russia", "gas", data_dir=s["data"], root=s["root"])
    s["dataset"] = data
    s["dirs"] = store.dir_paths(data, tmp_path)
    return s


def some(data, grp, n=2):
    return [o for p in data["pipelines"] for o in p[grp]][:n]


def rec(o, ts, rid, who="AL", **kw):
    r = {"key": o["key"], "dir": o["key"].split("::")[0], "pid": "P", "reviewer": who, "ts": ts, "id": rid,
         "batch": "b", "snapshot": "s.csv", "origin": "artifact"}
    r.update(kw)
    return r


# ---- the page ----------------------------------------------------------------------------

def test_the_page_is_one_file_the_artifact_tool_can_wrap(scope, tmp_path):
    entry, _ = publish.publish(["Russia"], "gas", tmp_path / "out", batches_root=scope["root"],
                               data_dir=scope["data"], write=False)
    data, index = build_static.read_scope(tmp_path / "out", entry)
    assert len(data["pipelines"]) == entry["counts"]["pipelines"]
    page = build_static.render(data, index, reviewer="BL")
    assert page.startswith("<title>pipelines reviewer</title>\n<style>")
    assert not re.search(r"<!doctype|<html[ >]|<head[ >]|<body[ >]", page, re.I)
    assert not re.search(r'<script[^>]+src=', page) and '<link rel="stylesheet"' not in page
    for name in build_static.SCRIPTS:
        assert (bundle.WEB / name).read_text(encoding="utf-8").rstrip() in page, name
    assert "GasStore = " not in page
    assert page.index("window.REVIEW_STATIC") < page.index("window.StaticStore = ") < page.index("window.ReviewApp = ")
    m = re.search(r'<script type="application/octet-stream" id="review-blob">([A-Za-z0-9+/=]+)</script>', page)
    body = json.loads(gzip.decompress(base64.b64decode(m.group(1))))
    assert body["data"] == data and body["index"] == index
    assert not (scope["deep"] / store.LOG_NAME).exists()         # building the page wrote no sidecar


def test_app_js_takes_the_static_store_only_when_the_google_one_is_absent():
    js = (bundle.WEB / "app.js").read_text(encoding="utf-8")
    assert "window.GasStore || window.StaticStore ||" in js
    assert "REVIEW_STATIC" in (bundle.WEB / "static_store.js").read_text(encoding="utf-8")
    assert "static_store.js" not in bundle.bundle()               # the Google bundle is unchanged


# ---- the import --------------------------------------------------------------------------

def test_read_docs_finds_documents_in_every_wrapper(tmp_path):
    doc = {"reviewer": "AL", "email": AL, "records": [{"key": "k"}]}
    for i, body in enumerate(({"logs": [doc]}, doc, {"docs": [{"id": "logs/x", "data": doc}]}, [{"data": doc}])):
        f = tmp_path / f"{i}.json"
        f.write_text(json.dumps(body))
        assert import_log.read_docs(f) == [doc]


def test_import_goes_store_first_under_the_reviewers_address(scope):
    ds, dirs = scope["dataset"], scope["dirs"]
    l1, l2 = some(ds, "lines")
    it = some(ds, "items", 1)[0]
    docs = [{"reviewer": "AL", "email": AL, "records": [
        rec(l2, "2026-10-05T12:00:02-04:00", "id-2", decision="hold", note="check"),
        rec(l1, "2026-10-05T12:00:01-04:00", "id-1", decision="accept"),
        rec(it, "2026-10-05T12:00:03-04:00", "id-3", call="noted", kind=it["kind"])]}]
    pl = import_log.plan(docs, ds, dirs)
    assert [r["id"] for _, r in pl["new"]] == ["id-1", "id-2", "id-3"] and pl["people"] == {"AL": AL}
    assert "AL (" + AL + "): 2 line decisions, 1 item calls" in import_log.report(pl)
    fake = FakeStore()
    saved = import_log.write(pl, ds, dirs, cfg={"store_sheet_id": "S"}, gws=fake)
    srecs = fake.records()
    assert [r["id"] for r in srecs] == ["id-1", "id-2", "id-3"]
    assert all(r["reviewer"] == AL and r["origin"] == "artifact" for r in srecs)
    assert srecs[0]["ts"] == "2026-10-05T12:00:01-04:00"          # the page's time is kept
    local = [r for d in dirs.values() for r in (logrecs(d) if (d / store.LOG_NAME).exists() else [])]
    assert sorted(r["id"] for r in local) == ["id-1", "id-2", "id-3"]
    assert all(r["reviewer"] == "AL" for r in local) and len(saved) == 3
    again = import_log.plan(docs, ds, dirs)                       # a second import is a no-op
    assert not again["new"] and again["dup"] == 3


def test_import_skips_what_a_later_decision_superseded_and_refuses_what_it_cannot_place(scope):
    ds, dirs = scope["dataset"], scope["dirs"]
    l1 = some(ds, "lines", 1)[0]
    store.decide([{"key": l1["key"], "decision": "reject", "note": "n"}], ds, "BL", dirs)
    old = {"reviewer": "AL", "email": AL, "records": [rec(l1, "2020-01-01T00:00:00-04:00", "id-old", decision="accept")]}
    pl = import_log.plan([old], ds, dirs)
    assert not pl["new"] and [r["id"] for r in pl["stale"]] == ["id-old"]
    for bad, why in (({"key": "batches/nope::x"}, "not in the current"), ({"call": "noted"}, "is a line"),
                     ({"reviewer": "backend sync"}, "initials"), ({"ts": "yesterday"}, "usable time")):
        r = rec(l1, "2030-01-01T00:00:00-04:00", "id-x", decision="accept")
        r.update(bad)
        with pytest.raises(SystemExit) as e:
            import_log.plan([{"email": AL, "records": [r]}], ds, dirs)
        assert why in str(e.value)
    with pytest.raises(SystemExit) as e:
        import_log.plan([{"records": [rec(l1, "2030-01-01T00:00:00-04:00", "id-y", decision="accept")]}], ds, dirs)
    assert "--reviewer AL=EMAIL" in str(e.value)
    ok = import_log.plan([{"records": [rec(l1, "2030-01-01T00:00:00-04:00", "id-y", decision="accept")]}], ds, dirs, emails={"AL": AL})
    assert ok["people"] == {"AL": AL}


def test_a_store_failure_writes_nothing_locally(scope):
    ds, dirs = scope["dataset"], scope["dirs"]
    l1 = some(ds, "lines", 1)[0]
    pl = import_log.plan([{"email": AL, "records": [rec(l1, "2030-01-01T00:00:00-04:00", "id-z", decision="accept")]}], ds, dirs)
    with pytest.raises(ledger.StoreError):
        import_log.write(pl, ds, dirs, cfg={"store_sheet_id": "S"}, gws=FakeStore(fail=ledger.pull.GwsError))
    assert not any((d / store.LOG_NAME).exists() for d in dirs.values())
