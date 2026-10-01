"""Phase 2: review_app/gas/Code.gs is a port of store.py's validation. These run the real Code.gs
under node fakes (review_app/gas_dev/) and hold it to the Python store, request by request, on the
fixture scope; then the Google-only behaviour (two reviewers, a republish, identity, the log tab).
Skipped when node is not installed. Never touches Google."""
import base64
import copy
import gzip
import json

import pytest

import gas_harness as H
import publish
import pull
import review_data
import review_fixture
import store

pytestmark = pytest.mark.skipif(H.node() is None, reason="node is not installed")

ME, THEM = "baird@globalenergymonitor.org", "aiganym@globalenergymonitor.org"
EXTRA = ("id", "scope", "batch", "snapshot", "origin", "basis", "row")     # what the Google store adds


def build(tmp_path, mutate=None, staged=None):
    s = review_fixture.make_scope(tmp_path)
    if staged:
        staged(s)
    data, _ = review_data.build([s["qc"], s["deep"]], "Russia", "gas", data_dir=s["data"], root=s["root"])
    if mutate:
        mutate(data)
    s["dataset"], s["dirs"] = data, store.dir_paths(data, tmp_path)
    s["out"] = tmp_path / "published"
    s["entry"] = H.publish_fixture(s, s["out"])
    return s


def line(data, pid, kind, col=None):
    for p in data["pipelines"]:
        if p["pid"] == pid:
            for l in p["lines"]:
                if l["kind"] == kind and (col is None or l["column"] == col):
                    return l
    raise AssertionError((pid, kind))


def concern(data, pid="P9001"):
    return next(i for p in data["pipelines"] if p["pid"] == pid for i in p["items"] if i["kind"] == "concern")


def item(data, kind):
    return next(i for p in data["pipelines"] for i in p["items"] if i["kind"] == kind)


def strip(rec):
    """Comparable shape. The reviewer compares as initials: Code.gs keeps the address in the private
    store, the Python store records initials in the committed sidecars (store.initials)."""
    out = {k: v for k, v in rec.items() if k not in EXTRA and k != "ts"}
    if "reviewer" in out:
        out["reviewer"] = store.initials(out["reviewer"])
    return out


def python_side(s, steps):
    """What the local server does: overlay, validate, write. -> [[record] | error code]."""
    out = []
    for kind, recs in steps:
        store.overlay(s["dataset"], s["dirs"])
        try:
            fn = store.record_items if kind == "item" else store.decide
            out.append([strip(r) for r in fn(copy.deepcopy(recs), s["dataset"], ME, dirs=s["dirs"])])
        except store.Invalid:
            out.append(400)
    return out


def gas_side(s, steps, user=ME):
    """The same requests through Code.gs, one node run each so the cursor can follow the answers."""
    out, sheets, cursor = [], None, s["entry"]["store_cursor"]
    for kind, recs in steps:
        fn = "recordItems" if kind == "item" else "decide"
        (res,), sheets, _ = H.run(s["out"], [H.op(user, fn, H.SID, H.VER, recs, cursor)], sheets)
        if res.get("ok") is False:
            out.append(res["code"])
        else:
            cursor = res["cursor"]
            out.append([strip(r) for r in res["saved"]])
    return out, sheets


def same(tmp_path, steps_of, mutate=None, staged=None):
    """Run one scenario through both stores, each on its own copy of the fixture."""
    a = build(tmp_path / "py", mutate, staged)
    b = build(tmp_path / "gas", mutate, staged)
    py = python_side(a, steps_of(a["dataset"]))
    gs, sheets = gas_side(b, steps_of(b["dataset"]))
    assert gs == py
    return py, sheets, b


# ---- parity with store.py ----------------------------------------------------------------

def test_hold_note_suggest_reject_and_undo_match_the_python_store(tmp_path):
    def steps(d):
        k = line(d, "P9002", "fill")["key"]
        return [("line", [{"key": k, "decision": "hold", "note": "wait"}]),
                ("line", [{"key": k, "decision": "suggest", "suggested_value": "12", "note": "per the notice"}]),
                ("line", [{"key": k, "decision": "reject"}]),
                ("line", [{"key": k, "undo": True}]),
                ("line", [{"key": k, "decision": "accept"}])]
    py, _, _ = same(tmp_path, steps)
    assert [r[0]["decision"] for r in py[:3]] == ["hold", "suggest", "reject"] and py[3][0]["undecided"] is True


def test_bad_requests_are_refused_the_same_way(tmp_path):
    def steps(d):
        k, c = line(d, "P9002", "fill")["key"], concern(d)["key"]
        w = item(d, "wikidiff")["key"]
        return [("line", []), ("line", [{"key": "nope", "decision": "hold"}]), ("line", [{"key": k}]),
                ("line", [{"key": k, "decision": "maybe"}]), ("line", [{"key": k, "decision": "suggest"}]),
                ("line", [{"key": c, "decision": "hold"}]),
                ("item", []), ("item", [{"key": k, "call": "noted"}]), ("item", [{"key": c, "call": "noted"}]),
                ("item", [{"key": w, "call": "confirmed"}]), ("item", [{"key": w}]),
                ("item", [{"key": "nope", "call": "noted"}])]
    py, sheets, _ = same(tmp_path, steps)
    assert py == [400] * 12
    assert len((sheets.get("log") or {}).get("rows") or []) <= 1          # nothing but the header


def test_a_contested_line_and_its_concern_are_independent_in_both_stores(tmp_path):
    def steps(d):
        k, c = line(d, "P9001", "ref", "Status")["key"], concern(d)["key"]
        return [("line", [{"key": k, "decision": "accept"}]),              # never held: the concern has no candidate
                ("line", [{"key": k, "decision": "hold"}]),
                ("item", [{"key": c, "call": "dismissed", "note": "checked"}]),
                ("line", [{"key": k, "decision": "accept"}]),
                ("item", [{"key": c, "undo": True}]),
                ("line", [{"key": k, "decision": "accept"}]),
                ("item", [{"key": c, "call": "confirmed"}]),
                ("line", [{"key": k, "decision": "accept"}])]
    py, _, _ = same(tmp_path, steps)
    assert [len(r) for r in py] == [1] * 8 and py[0][0]["decision"] == "accept"


def test_a_bulk_with_a_contested_line_saves_both(tmp_path):
    def steps(d):
        return [("line", [{"key": line(d, "P9002", "fill")["key"], "decision": "accept"},
                          {"key": line(d, "P9001", "ref", "Status")["key"], "decision": "accept"}])]
    py, sheets, _ = same(tmp_path, steps)
    assert [r["decision"] for r in py[0]] == ["accept", "accept"]


def contest(d):
    concern(d)["contested"] = {"Status": "operating", "Owner1": "OldCo"}
    review_fixture.relink(d)


def test_self_resolving_accept_dismisses_the_concern_in_the_same_write(tmp_path):
    def steps(d):
        st, ow = line(d, "P9001", "ref", "Status")["key"], line(d, "P9001", "oo")["key"]
        return [("line", [{"key": ow, "decision": "accept"}]),             # Owner1 differs: no call either way
                ("line", [{"key": st, "decision": "hold"}]),               # a hold dismisses nothing
                ("line", [{"key": st, "decision": "accept"}, {"key": line(d, "P9002", "fill")["key"], "decision": "accept"}]),
                ("line", [{"key": ow, "decision": "accept"}]),
                ("line", [{"key": st, "decision": "accept"}])]             # not dismissed twice
    py, _, _ = same(tmp_path, steps, mutate=contest)
    assert len(py[0]) == 1 and len(py[1]) == 1
    assert [r.get("call") for r in py[2]] == [None, None, "dismissed"]
    assert py[2][2]["note"] == "resolved by accepted Status fill"
    assert len(py[3]) == 1 and len(py[4]) == 1


def test_accept_candidate_matches_the_python_store(tmp_path):
    def steps(d):
        st, ow, c = line(d, "P9001", "ref", "Status")["key"], line(d, "P9001", "oo")["key"], concern(d)["key"]
        return [("line", [{"key": ow, "rival": c, "decision": "accept"}]),          # 400: recorded as suggest only
                ("line", [{"key": ow, "rival": "nope"}]),                             # 400
                ("line", [{"key": st, "rival": c}]),                                  # 400: it agrees, no candidate
                ("line", [{"key": ow, "rival": c}]),                                  # suggest OldCo + confirmed
                ("line", [{"key": st, "decision": "accept"}]),                        # confirmed already: no dismissal
                ("line", [{"key": ow, "rival": c, "note": "again"}]),                 # line only
                ("line", [{"key": ow, "undo": True}])]
    py, _, _ = same(tmp_path, steps, mutate=contest)
    assert py[:3] == [400, 400, 400]
    assert [(r.get("decision"), r.get("call")) for r in py[3]] == [("suggest", None), (None, "confirmed")]
    assert (py[3][0]["suggested_value"], py[3][0]["rival"], py[3][1]["note"]) == ("OldCo", py[3][1]["key"], "candidate accepted on Owner1")
    assert len(py[4]) == 1 and len(py[5]) == 1 and py[5][0]["note"] == "again" and py[6][0]["undecided"] is True


def test_confirmed_wins_over_dismissed_in_one_request_in_both_stores(tmp_path):
    def steps(d):
        st, ow, c = line(d, "P9001", "ref", "Status")["key"], line(d, "P9001", "oo")["key"], concern(d)["key"]
        return [("line", [{"key": st, "decision": "accept"}, {"key": ow, "rival": c}])]
    py, _, _ = same(tmp_path, steps, mutate=contest)
    assert [r.get("call") for r in py[0]] == [None, None, "confirmed"]


def test_covered_records_fan_out_with_via(tmp_path):
    def staged(s):
        f = s["deep"] / "staged_resolutions.json"
        doc = json.loads(f.read_text())
        doc["resolutions"].append(review_fixture._rec(
            "P9002", 5, "Status [ref]", "FILL", "REFS_ADDED", value_cols=["Status"], primary_value_col="Status",
            values={"Status": "construction"}, proposed_refs=["http://third.example/c"], tier="medium"))
        f.write_text(json.dumps(doc))

    def steps(d):
        k = line(d, "P9002", "status")["key"]
        return [("line", [{"key": k, "decision": "accept"}]), ("line", [{"key": k, "undo": True}])]
    py, _, b = same(tmp_path, steps, staged=staged)
    st = line(b["dataset"], "P9002", "status")
    assert [r["key"] for r in py[0]] == [st["key"], st["covers"][0]["key"]]
    assert py[0][1]["via"] == st["key"] and [r["undecided"] for r in py[1]] == [True, True]


# ---- what only the Google store does -----------------------------------------------------

@pytest.fixture
def pub(tmp_path):
    return build(tmp_path)


def test_records_are_stamped_server_side_and_the_log_tab_holds_them(pub):
    d = pub["dataset"]
    l = line(d, "P9002", "fill")
    recs = [{"key": l["key"], "decision": "accept", "reviewer": "someone else", "ts": "1999", "note": "=SUM(A1)"}]
    (res,), sheets, _ = H.run(pub["out"], [H.op(ME, "decide", H.SID, H.VER, recs, 1)])
    (r,) = res["saved"]
    assert (r["reviewer"], r["scope"], r["origin"], r["snapshot"], r["basis"]) == \
        (ME, H.SID, "gas", d["scope"]["snapshot"], l["basis"])
    assert r["ts"] == "2099-01-01T01:00:00-05:00" and r["id"] and r["batch"] and r["row"] == 2 and res["cursor"] == 2
    rows = sheets["log"]["rows"]
    head = rows[0]
    assert head[:3] == ["ts", "reviewer", "rec"] and head[-3:] == ["id", "scope", "json"] and len(rows) == 2
    row = dict(zip(head, rows[1]))
    assert (row["reviewer"], row["rec"], row["decision"], row["pid"], row["key"], row["scope"]) == \
        (ME, "line", "accept", "P9002", l["key"], H.SID)
    assert row["note"] == "'=SUM(A1)"                                  # a display cell is never a formula
    stored = json.loads(row["json"])
    assert stored["note"] == "=SUM(A1)" and stored == {k: v for k, v in r.items() if k != "row"}


def test_one_request_is_one_batch_id(pub):
    d = pub["dataset"]
    keys = [l["key"] for p in d["pipelines"] for l in p["lines"] if p["pid"] == "P9002" and not l.get("in_backend")][:2]
    assert len(keys) == 2
    ops = [H.op(ME, "decide", H.SID, H.VER, [{"key": k, "decision": "hold"} for k in keys], 1),
           H.op(ME, "decide", H.SID, H.VER, [{"key": keys[0], "decision": "reject"}], 3)]
    (a, b), _, _ = H.run(pub["out"], ops)
    assert len({r["batch"] for r in a["saved"]}) == 1 and b["saved"][0]["batch"] != a["saved"][0]["batch"]
    assert len({r["id"] for r in a["saved"] + b["saved"]}) == 3


def test_a_second_reviewer_with_a_stale_page_is_refused_then_may_overrule(pub):
    d = pub["dataset"]
    k, other = line(d, "P9002", "fill")["key"], line(d, "P9001", "ref", "Status")["key"]
    ops = [H.op(ME, "decide", H.SID, H.VER, [{"key": k, "decision": "accept"}], 1),
           H.op(THEM, "decide", H.SID, H.VER, [{"key": other, "decision": "hold"}, {"key": k, "decision": "reject"}], 1),
           H.op(THEM, "decide", H.SID, H.VER, [{"key": other, "decision": "hold"}], 1),       # a different line: fine
           H.op(THEM, "getDecisions", H.SID, H.VER, 1),
           H.op(THEM, "decide", H.SID, H.VER, [{"key": k, "decision": "reject"}], 3),         # having seen it: allowed
           H.op(ME, "decide", H.SID, H.VER, [{"key": k, "decision": "hold"}], 1)]             # own rows never clash
    (mine, clash, fine, seen, over, again), sheets, _ = H.run(pub["out"], ops)
    assert mine["cursor"] == 2
    assert (clash["ok"], clash["code"], clash["stale"], clash["cursor"]) == (False, 409, True, 2)
    assert [r["key"] for r in clash["records"]] == [k] and ME in clash["error"]
    assert [r["key"] for r in fine["others"]] == [k] and fine["cursor"] == 3
    assert [(r["key"], r["reviewer"]) for r in seen["records"]] == [(k, ME), (other, THEM)] and seen["cursor"] == 3
    assert over["saved"][0]["decision"] == "reject" and over["cursor"] == 4
    assert again["ok"] is False and again["stale"] is True             # THEM overruled it since ME's page synced
    assert len(sheets["log"]["rows"]) == 4                             # the two refusals stored nothing


def test_a_republished_scope_refuses_writes_and_reads_until_the_page_reloads(pub):
    k = line(pub["dataset"], "P9002", "fill")["key"]
    old = pub["entry"]
    H.publish_fixture(pub, pub["out"], ver="20990102T000000")
    ops = [H.op(ME, "decide", H.SID, H.VER, [{"key": k, "decision": "hold"}], 1),
           H.op(ME, "getPart", H.SID, H.VER, old["parts"][0]),
           H.op(ME, "getDecisions", H.SID, H.VER, 1),
           H.op(ME, "decide", H.SID, "20990102T000000", [{"key": k, "decision": "hold"}], 1)]
    (w, part, dec, ok), _, _ = H.run(pub["out"], ops)
    assert (w["code"], w["reload"], w["ver"]) == (409, True, "20990102T000000")
    assert (part["code"], part["reload"]) == (409, True)      # a page mid-load starts over on the new version
    assert dec["ver"] == "20990102T000000"            # the page compares this with what it loaded and reloads
    assert ok["saved"][0]["decision"] == "hold"


def test_identity_scope_and_file_guards(pub):
    k = line(pub["dataset"], "P9002", "fill")["key"]
    ops = [H.op("", "whoami"), H.op("", "decide", H.SID, H.VER, [{"key": k, "decision": "hold"}], 1),
           H.op(ME.upper(), "whoami"), H.op(ME, "decide", "no-such-scope", H.VER, [{"key": k, "decision": "hold"}], 1),
           H.op(ME, "getPart", H.SID, H.VER, "scopes.json"), H.op(ME, "getPart", H.SID, H.VER, "../x.json.gz"),
           H.op(ME, "getPart", H.SID, H.VER, pub["entry"]["index"])]
    (anon, anon_w, who, noscope, p1, p2, p3), sheets, _ = H.run(pub["out"], ops)
    assert anon["code"] == 403 and anon_w["code"] == 403 and not sheets.get("log")
    assert who["reviewer"] == ME and who["caps"] == {"decide": True, "refresh": False, "push": False}
    assert [s["id"] for s in who["scopes"]] == [H.SID]
    assert noscope["ok"] is False and noscope["code"] in (400, 404)
    assert all(p["ok"] is False for p in (p1, p2, p3))        # only the scope's own parts and geo are served


def test_parts_reassemble_to_the_published_dataset(tmp_path):
    s = build(tmp_path)
    entry = H.publish_fixture(s, s["out"], ver="20990103T000000", target=2000)
    assert len(entry["parts"]) > 1
    (who, *parts), _, _ = H.run(s["out"], [H.op(ME, "whoami")] + [H.op(ME, "getPart", H.SID, entry["ver"], n) for n in entry["parts"]])
    got = None
    for p in parts:
        body = json.loads(gzip.decompress(base64.b64decode(p["b64"])))
        if got is None:
            got = body
        else:
            assert list(body) == ["pipelines"]
            got["pipelines"] += body["pipelines"]
    assert got == json.loads(json.dumps(s["dataset"]))


def test_the_store_round_trips_through_pull_into_the_staging_dirs(pub):
    d = pub["dataset"]
    l, c = line(d, "P9002", "fill"), concern(d)
    ops = [H.op(THEM, "decide", H.SID, H.VER, [{"key": l["key"], "decision": "accept", "note": "ok"}], 1),
           H.op(ME, "recordItems", H.SID, H.VER, [{"key": c["key"], "call": "dismissed"}], 2)]
    _, sheets, _ = H.run(pub["out"], ops)
    cells = H.json_cells(sheets)
    res = pull.pull({"store_sheet_id": "x"}, root=pub["tmp"], reader=lambda sheet: cells)
    assert (res["cursor"], res["rows"], res["new"], res["bad_rows"], res["skipped"]) == (3, 2, 2, [], {})
    again = pull.pull({"store_sheet_id": "x"}, root=pub["tmp"], reader=lambda sheet: cells)
    assert again["new"] == 0 and again["cursor"] == 3                 # idempotent
    store.overlay(d, pub["dirs"])
    assert (l["decision"], l["decided_by"], l["reviewed"]) == ("accept", store.initials(THEM), True)     # the committed log holds the initials
    assert (c["call"], c["decided_by"]) == ("dismissed", store.initials(ME))
    assert publish.restore_reviewers(d, pub["dirs"], res["emails"]) == 2                              # the private dataset, the address
    assert (l["decided_by"], c["decided_by"]) == (THEM, ME)
    log = store.read_log(pub["dirs"][l["dir"]])
    assert {r["origin"] for r in log} == {"gas"} and all(r["id"] and r["batch"] and "row" not in r for r in log)
    assert [r["note"] for r in log if r["key"] == l["key"]] == ["ok"]


def _backend(pub, mutate=None, shift=0):
    """A fake backend tracker tab built from the published watch list (so it matches the dataset
    exactly), optionally mutated; `shift` rows are inserted above the data."""
    w = json.loads((pub["out"] / pub["entry"]["index"]).read_text(encoding="utf-8"))["w"]["tracker"]
    cols = sorted({c for _, _, cells in w for c in cells})
    rows = [[""] * len(cols) for _ in range(3)] + [["x"] * (len(cols) + 1) for _ in range(shift)]
    rows[2] = ["ProjectID"] + cols
    body = {}
    for pid, r, cells in w:
        body[pid] = ["" if c not in cells else cells[c] for c in cols]
    for pid, vals in body.items():
        rows.append([pid] + vals)
    # the recorded rows are only honoured when they line up; the check matches on ProjectID either way
    if mutate:
        mutate(rows, cols)
    oo = json.loads((pub["out"] / pub["entry"]["index"]).read_text(encoding="utf-8"))["w"]["oo"]
    ocols = sorted({c for _, _, cells in oo for c in cells})
    orows = [[""] * (len(ocols) + 1), ["ProjectID"] + ocols] + [[pid] + [cells.get(c, "") for c in ocols] for pid, _, cells in oo]
    return {"id": "backend-sheet", "gids": {"gas": 1020144097, "oil": 456134080, "oo": 1489950650},
            "header_row": {"tracker": 3, "oo": 2}, "tabs": {"1020144097": rows, "1489950650": orows}}, w


def test_live_check_flags_changed_cells_by_pid(pub):
    be, w = _backend(pub)
    assert w, "publish wrote no watch list"
    ok = H.run(pub["out"], [H.op(ME, "liveCheck", H.SID, H.VER)], backend=be)[0][0]
    assert ok["ok"], ok
    assert ok["checked"] >= len(w) and not ok["changed"] and not ok["gone"], ok

    def edit(rows, cols):
        i = next(i for i, r in enumerate(rows) if i > 2 and any(r[1:]))
        j = next(j for j, v in enumerate(rows[i][1:], 1) if v != "")
        rows[i][j] = rows[i][j] + " (edited)"
        edit.hit = (rows[i][0], cols[j - 1])
    be2, _ = _backend(pub, mutate=edit)
    got = H.run(pub["out"], [H.op(ME, "liveCheck", H.SID, H.VER)], backend=be2)[0][0]
    assert [(c["pid"], c["cols"][0][0]) for c in got["changed"] if c["cols"]] == [edit.hit]

    be3, _ = _backend(pub, shift=5)        # rows inserted above: matched by ProjectID, nothing changed
    moved = H.run(pub["out"], [H.op(ME, "liveCheck", H.SID, H.VER)], backend=be3)[0][0]
    assert moved["ok"] and not [c for c in moved["changed"] if c["cols"]]

    stale = H.run(pub["out"], [H.op(ME, "liveCheck", H.SID, "19990101T000000")], backend=be)[0][0]
    assert stale["ok"] is False and stale["code"] == 409
    anon = H.run(pub["out"], [H.op("", "liveCheck", H.SID, H.VER)], backend=be)[0][0]
    assert anon["ok"] is False and anon["code"] == 403
