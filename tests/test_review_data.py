"""review_data.build against the review_fixture scope."""
from collections import Counter

import pytest

import review_data as rd
from build_ref_workbook import _annotate_kept_refs, _ref_cell_text
from review_fixture import OWN_NAME, SNAP_NAME, make_scope


@pytest.fixture
def built(tmp_path):
    s = make_scope(tmp_path)
    data, stats = rd.build([s["qc"], s["deep"]], "Russia", "gas", data_dir=s["data"], root=s["root"])
    return data, stats, s


def _all(data):
    return [(p, o, g) for p in data["pipelines"] for g, objs in (("line", p["lines"]), ("item", p["items"]))
            for o in objs]


def _find(data, pid, kind, **kw):
    hits = [o for p, o, _ in _all(data) if p["pid"] == pid and o["kind"] == kind
            and all(o.get(k) == v for k, v in kw.items())]
    return hits


def test_every_kind_once_with_the_right_key(built):
    data, stats, s = built
    kinds = Counter(o["kind"] for _, o, _ in _all(data))
    for k in rd.LINE_KINDS + rd.ITEM_KINDS:
        assert kinds[k] >= 1, k
    # the lone record that fits no kind is kept and counted, not dropped
    assert kinds["other"] == 1
    keys = [o["key"] for _, o, _ in _all(data)]
    assert len(keys) == len(set(keys))
    ref = _find(data, "P9001", "ref")[0]
    assert ref["key"] == "batches/russia-gas/staging/deepsweep-x::P9001|4|Status [ref]" or \
        ref["key"].endswith("::P9001|4|Status [ref]")
    assert _find(data, "P9002", "status")[0]["key"].endswith("::P9002|5|__STATUS__")
    assert _find(data, "P9004", "route")[0]["key"].endswith("|__ROUTE__")
    assert _find(data, "P9004", "wikidiff", field="Status")[0]["key"].endswith("|__WIKIDIFF__:Status")
    assert _find(data, "P9004", "routeqc", check="length_ratio")
    assert _find(data, "P9001", "concern")[0]["key"].endswith("|__VALIDITY__:duplicate")
    assert _find(data, "scope", "escalation")[0]["key"].split("::")[1].startswith("scope|")
    assert _find(data, "P9002", "flag")


def test_dedupe_puts_qc_dir_in_also_in(built):
    data, stats, s = built
    ref = _find(data, "P9001", "ref")[0]
    assert ref["dir"].endswith("deepsweep-x")            # primary is the non-assembled dir
    assert any(d.endswith("/qc") for d in ref["also_in"])
    # extras only the handoff carries stay with the qc dir
    extra = _find(data, "P9001", "wikidiff", field="Owner")[0]
    assert extra["dir"].endswith("/qc") and extra["also_in"] == []
    assert _find(data, "P9004", "routeqc", check="null_geometry")[0]["dir"].endswith("/qc")
    assert stats["deduped"] >= 4


def test_prior_and_actions_files_ignored(built):
    data, stats, s = built
    pids = {p["pid"] for p in data["pipelines"]}
    assert "P9099" not in pids and "P9098" not in pids


def test_na_row_dropped(tmp_path):
    s = make_scope(tmp_path)
    import json
    f = s["deep"] / "staged_resolutions.json"
    d = json.loads(f.read_text())
    d["resolutions"].append(dict(d["resolutions"][0], project_id="P9003", sheet_row=6))
    f.write_text(json.dumps(d))
    data, stats = rd.build([s["deep"], s["qc"]], "Russia", "gas", data_dir=s["data"], root=s["root"])
    assert "P9003" not in {p["pid"] for p in data["pipelines"]}
    assert stats["dropped_na"] == 1


def test_multi_row_pid_is_one_card_with_two_segments(built):
    data, _, _ = built
    cards = [p for p in data["pipelines"] if p["pid"] == "P9004"]
    assert len(cards) == 1
    assert [s["sheet_row"] for s in cards[0]["segments"]] == [7, 8]
    assert [s["segment"] for s in cards[0]["segments"]] == ["Seg A", "Seg B"]


def test_sheet_row_re_resolved(built):
    data, stats, _ = built
    fill = _find(data, "P9002", "fill")[0]
    assert fill["sheet_row"] == 5 and fill["sheet_row_moved"] is True   # staged as 99
    assert _find(data, "P9001", "ref")[0]["sheet_row_moved"] is False
    assert stats["moved"] >= 1
    # the key carries the re-resolved row, so a stale staged number cannot fork it
    assert "|5|" in fill["key"]


def test_in_backend_for_already_applied_line(built):
    data, _, _ = built
    applied = _find(data, "P9005", "fill")[0]
    assert applied["in_backend"] is True
    assert _find(data, "P9002", "fill")[0]["in_backend"] is False
    assert _find(data, "P9001", "ref")[0]["in_backend"] is False


def test_default_accept_iff_high(built):
    data, _, _ = built
    lines = [o for _, o, g in _all(data) if g == "line"]
    assert lines
    for l in lines:
        assert l["default"] == ("accept" if l["tier"] == "high" else "hold"), l["key"]
    assert _find(data, "P9001", "ref")[0]["default"] == "hold"      # medium
    assert _find(data, "P9002", "fill")[0]["default"] == "accept"   # high
    for _, o, g in _all(data):
        if g == "item":
            assert o["default"] is None and o["call"] is None
        else:
            assert o["decision"] is None and o["reviewed"] is False


def test_oo_current_values_from_owners_snapshot(built):
    data, _, _ = built
    oo = _find(data, "P9001", "oo")[0]
    assert oo["tab"] == "operators_owners"
    assert oo["current"] == {"Owner1": "OldCo"}
    assert oo["current_ref"] == "http://owners-old.example/x"
    assert oo["proposed_values"] == {"Owner1": "NewCo"}
    assert oo["tracker_sheet_row"] == 4


def test_ref_cell_text_matches_workbook_composer(built):
    data, _, s = built
    import json
    recs = json.loads((s["deep"] / "staged_resolutions.json").read_text())["resolutions"]
    _annotate_kept_refs(recs, s["deep"])
    want = _ref_cell_text(recs[0])
    got = _find(data, "P9001", "ref")[0]["ref_cell_text"]
    assert got == want
    # the blocked-not-dead current URL is kept alongside the proposal
    assert "http://old.example/a" in got and "http://new.example/b" in got


def test_sort_order(built):
    data, _, _ = built
    pids = [p["pid"] for p in data["pipelines"]]
    real = [p for p in pids if p.startswith("P9")]
    assert real == sorted(real)                      # snapshot row order == pid order here
    assert pids[-2:] == ["new:new-one", "scope"] or pids[-1] == "scope"
    assert pids.index("scope") > pids.index("new:new-one") > pids.index("P9005")
    # lines follow snapshot column order (Status before Capacity), items come after lines
    p2 = next(p for p in data["pipelines"] if p["pid"] == "P9002")
    cols = [l["column"] for l in p2["lines"]]
    cidx = data["columns"].index
    assert cidx("Status") < cidx("Capacity") and cols.index("Status") < cols.index("Capacity")
    assert [i["kind"] for i in p2["items"]] == sorted((i["kind"] for i in p2["items"]),
                                                      key=rd.ITEM_KINDS.index)


def test_exclude_pids_and_cli(tmp_path):
    s = make_scope(tmp_path)
    out = tmp_path / "out.json"
    rd.main(["--country", "Russia", "--commodity", "gas", "--exclude-pids", "P9001",
             "--batches-root", str(s["root"]), "--data-dir", str(s["data"]), "--out", str(out)])
    import json
    data = json.loads(out.read_text())
    assert "P9001" not in {p["pid"] for p in data["pipelines"]}
    assert data["scope"]["snapshot"] == SNAP_NAME


# ---- one card per status call: the agreeing Status [ref] record folds into the status line ----

def _with_status_partner(tmp_path, status="construction", refs=("http://third.example/c",), ref_col="Status [ref]"):
    import json
    from review_fixture import _rec
    s = make_scope(tmp_path)
    f = s["deep"] / "staged_resolutions.json"
    doc = json.loads(f.read_text())
    doc["resolutions"].append(_rec(
        "P9002", 5, ref_col, "FILL", "REFS_ADDED", value_cols=["Status"], primary_value_col="Status",
        values={"Status": status}, proposed_refs=list(refs), tier="medium", independent=True,
        researcher_notes="refs leg note",
        verifications=[{"url": refs[0], "ok": True, "name_found": True, "note": "says it is being built"}]))
    f.write_text(json.dumps(doc))
    data, stats = rd.build([s["qc"], s["deep"]], "Russia", "gas", data_dir=s["data"], root=s["root"])
    return data, stats, s


def test_agreeing_status_ref_record_folds_into_the_status_line(tmp_path):
    data, stats, _ = _with_status_partner(tmp_path)
    (st,) = _find(data, "P9002", "status")
    assert not _find(data, "P9002", "fill", ref_col="Status [ref]")          # no card of its own
    assert stats["status_covers"] == 1 and len(st["covers"]) == 1
    c = st["covers"][0]
    assert c["key"].endswith("|5|Status") and c["key"] != st["key"]
    assert (c["kind"], c["ref_col"], c["class_out"], c["notes"]) == ("fill", "Status [ref]", "REFS_ADDED", "refs leg note")
    assert c["decision"] is None
    assert st["proposed_refs"] == ["http://new.example/b", "http://other.example/z", "http://third.example/c"]
    assert all(u in st["ref_cell_text"] for u in st["proposed_refs"])
    assert st["publishers"] == 3
    assert "http://third.example/c" in {v["url"] for v in st["verifications"]}
    assert "folded into their status line: 1" in rd.summary(data, stats)


def test_same_refs_partner_adds_no_refs(tmp_path):
    data, _, _ = _with_status_partner(tmp_path, refs=("http://new.example/b",))
    (st,) = _find(data, "P9002", "status")
    assert len(st["covers"]) == 1
    assert st["proposed_refs"] == ["http://new.example/b", "http://other.example/z"]


def test_partner_with_another_status_or_another_cell_stays_its_own_card(tmp_path):
    data, stats, _ = _with_status_partner(tmp_path, status="proposed")        # supports the CURRENT status
    (st,) = _find(data, "P9002", "status")
    assert "covers" not in st and stats["status_covers"] == 0
    assert len(_find(data, "P9002", "fill", ref_col="Status [ref]")) == 1
    (tmp_path / "b").mkdir()
    data, stats, _ = _with_status_partner(tmp_path / "b", ref_col="StartYear1 [ref]")
    assert stats["status_covers"] == 0 and "covers" not in _find(data, "P9002", "status")[0]


def test_multi_country_tags_cards_and_splits_scope_card(tmp_path):
    s = make_scope(tmp_path)
    one, _ = rd.build([s["qc"], s["deep"]], "Russia", "gas", data_dir=s["data"], root=s["root"])
    data, _ = rd.build([s["qc"], s["deep"]], ["Russia", "United States"], "gas", data_dir=s["data"],
                       root=s["root"], dir_country={s["deep"]: "United States", s["qc"]: "Russia"})
    assert data["scope"]["countries"] == ["Russia", "United States"]
    assert all(p["scope_countries"] for p in data["pipelines"])
    assert {c for p in data["pipelines"] for c in p["scope_countries"]} <= {"Russia", "United States"}
    # same keys as the single-country build: decisions made before stay attached
    keys = lambda d: sorted(o["key"] for p, o, _ in _all(d))
    assert keys(data) == keys(one)
    esc = [p for p in data["pipelines"] if p["pid"] == "scope"
           and any(i["kind"] == "escalation" for i in p["items"])]
    assert len(esc) == 1 and esc[0]["scope_countries"] == ["United States"]
    assert all(p["scope_countries"] == ["Russia"] for p in rd.build(
        [s["qc"], s["deep"]], "Russia", "gas", data_dir=s["data"], root=s["root"])[0]["pipelines"])


def test_country_status_drops_only_all_decided_countries(tmp_path):
    import json
    s = make_scope(tmp_path)
    dc = {s["deep"]: "United States", s["qc"]: "Russia"}
    kw = dict(data_dir=s["data"], root=s["root"], dir_country=dc)
    data, _ = rd.build([s["qc"], s["deep"]], ["Russia", "United States"], "gas", **kw)
    cs = {c["country"]: c for c in data["scope"]["country_status"]}
    assert not cs["Russia"]["done"] and not cs["United States"]["done"]
    assert cs["Russia"]["open_lines"] + cs["Russia"]["open_items"] > 0
    # a person decides every United States (deep dir) line and asked item
    recs = [{"key": o["key"], "dir": o["dir"], "reviewer": "Baird",
             **({"decision": "reject"} if g == "line" else {"call": "dismissed"})}
            for p, o, g in _all(data) if o["dir"].endswith("deepsweep-x") and o["kind"] not in rd.INFO_KINDS]
    (s["deep"] / "review_log.jsonl").write_text("".join(json.dumps(r) + "\n" for r in recs))
    kept, stats = rd.build([s["qc"], s["deep"]], ["Russia", "United States"], "gas", drop_done=True, **kw)
    cs = {c["country"]: c for c in kept["scope"]["country_status"]}
    assert cs["United States"]["done"] and cs["United States"]["hidden"] and not cs["Russia"]["hidden"]
    assert stats["done_dropped"] >= 1
    # US-only cards go; a card Russia shares stays whole
    assert kept["pipelines"] and all("Russia" in p["scope_countries"] for p in kept["pipelines"])
    # without drop_done nothing goes; status is still reported
    full, _ = rd.build([s["qc"], s["deep"]], ["Russia", "United States"], "gas", **kw)
    assert len(full["pipelines"]) == len(kept["pipelines"]) + stats["done_dropped"]
    assert not any(c["hidden"] for c in full["scope"]["country_status"])


def test_fill_key_names_every_proposed_column(built):
    # P9002 proposes Capacity AND CapacityUnits -> both in the key; P9005 proposes Capacity alone.
    data, _, _ = built
    assert _find(data, "P9002", "fill")[0]["key"].endswith("::P9002|5|Capacity+CapacityUnits")
    assert _find(data, "P9005", "fill")[0]["key"].endswith("::P9005|9|Capacity")
    # the column with the ONLY changed value is in the key even when it is not the primary one
    r = {"ref_col": "Proposal [ref]", "value_cols": ["ProposalYear", "ProposalMonth"],
         "primary_value_col": "ProposalYear", "values": {"ProposalYear": "", "ProposalMonth": "9"}}
    assert rd._colid(r, "fill") == "ProposalMonth"
    r["values"]["ProposalYear"] = "2023"
    assert rd._colid(r, "fill") == "ProposalYear+ProposalMonth"
    assert rd._colid(dict(r, class_in="FILL"), "unresolved") == "ProposalYear+ProposalMonth"
    assert rd._colid(dict(r, values={}), "fill") == "ProposalYear"       # nothing proposed: the primary, as before
