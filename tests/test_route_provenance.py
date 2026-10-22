import json
import os
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
_gra = os.environ.get("GEM_REVIEW_APP") or str(ROOT.parent / "gem-review-app")
if _gra not in sys.path:
    sys.path.insert(0, _gra)

import route_provenance as rp  # noqa: E402

Image = pytest.importorskip("PIL.Image")


def img(path, size=(40, 30)):
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, (200, 10, 10)).save(path)


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj))


def rec(**kw):
    r = {"project_id": "P1", "class_out": "ROUTE_CANDIDATE", "method": "digitized", "start_name": "Alpha", "end_name": "Beta"}
    r.update(kw)
    return r


def test_texts_per_method_are_plain():
    cases = {
        "gis_vector": rec(method="gis_vector", source={"name": "Oil & Gas Watch, medium resolution"}),
        "digitized": rec(georef={"n_gcps": 9, "rmse_km": 0.098, "loo_rmse_km": 2.154}),
        "gulfpub_sidecar": rec(method="gulfpub_sidecar"),
        "endpoints_greatcircle": rec(method="endpoints_greatcircle"),
        "corridor_follow_osm": rec(method="corridor_follow_osm", source={"name": "OpenStreetMap way 5"}),
        "osm": rec(method="osm"),
        "none": rec(method=None),
    }
    for k, r in cases.items():
        t = rp.summary(r)["text"]
        assert t and not re.search(r"[—–→()]", t), (k, t)
    assert "medium resolution" in rp.summary(cases["gis_vector"])["text"]
    d = rp.summary(cases["digitized"])
    assert "9 control points" in d["text"] and "0.10 km" in d["text"] and "only as accurate" in d["text"]
    assert ["Georeferencing", "9 control points, fit error 0.10 km, held-out error 2.2 km"] in d["facts"]
    assert "Alpha and Beta" in rp.summary(cases["endpoints_greatcircle"])["text"]


def test_missing_method_quotes_notes():
    t = rp.summary(rec(method=None, researcher_notes="x" * 400))["text"]
    assert t.startswith("How this route was made was not recorded.")
    assert "The researcher notes say: " + "x" * 300 in t and "x" * 301 not in t
    assert rp.summary(rec(method=None))["text"] == "How this route was made was not recorded."


def test_facts():
    r = rec(source={"name": "S", "url": "https://e.org/a", "license": "ODbL", "fetched_utc": "2026-08-11T00:00:00Z"},
            proposed_sheet={"Route [ref]": "https://e.org/r"}, qc_passed=False, suggested_route_accuracy="medium")
    f = {x[0]: x for x in rp.summary(r)["facts"]}
    assert f["Source"] == ["Source", "S", "https://e.org/a"]
    assert f["Route reference"][2] == "https://e.org/r"
    assert f["Fetched"][1] == "2026-08-11" and f["Quality check"][1] == "failed" and f["License"][1] == "ODbL"
    assert f["Suggested accuracy"][1] == "medium" and f["Method"][1] == "Traced by hand from a map"


def test_source_json_layout_overlay_and_residuals(tmp_path):
    st = tmp_path / "stage"
    m = st / "maps" / "P1"
    img(m / "a.png"), img(m / "b.png", (50, 20))
    (m / "doc.pdf").write_bytes(b"%PDF-1.4")
    dump(m / "source.json", {"files": [
        {"file": "doc.pdf", "source_url": "https://e.org/doc.pdf", "document_title": "Doc", "page": "3", "date_read": "2026-10-20"},
        {"file": "a.png", "source_url": "https://e.org/doc.pdf", "document_title": "Doc", "page": "3", "date_read": "2026-10-20"},
        {"file": "b.png", "document_title": "Doc"},
        {"file": "missing.png"}]})
    img(st / "traces" / "P1" / "overlay_trace.png")
    dump(st / "traces" / "P1" / "gcps.json", [
        {"px": [1, 2], "lonlat": [-100.1, 30.2], "name": "A", "source_ref": "r"}, {"px": [3, 4], "lonlat": [-101, 31]}])
    dump(st / "traces" / "P1" / "georef_report.json", {"residuals_km": [0.123456, 0.5]})
    out = rp.files(rec(georef={"residuals_km": [9, 9]}), st, tmp_path)
    ims = out["images"]
    assert [i["role"] for i in ims] == ["map", "map", "overlay"]
    assert ims[0]["caption"] == "Map from Doc, page 3, read 2026-10-20"
    assert ims[0]["source_url"] == "https://e.org/doc.pdf" and "source_url" not in ims[1]
    assert ims[0]["path"] == "stage/maps/P1/a.png" and ims[0]["width"] == 40
    assert (tmp_path / "work" / "review_assets" / ims[0]["asset"]).is_file()
    assert ims[2]["caption"] == "The traced route drawn over the map"
    cp = out["control_points"]
    assert cp[0] == {"name": "A", "px": [1, 2], "lon": -100.1, "lat": 30.2, "ref": "r", "residual_km": 0.12}
    assert cp[1]["residual_km"] == 0.5 and "name" not in cp[1]


def test_residuals_fall_back_to_record(tmp_path):
    st = tmp_path / "stage"
    dump(st / "traces" / "P1" / "gcps.json", [{"px": [1, 2], "lonlat": [1, 2]}])
    out = rp.files(rec(georef={"residuals_km": [0.777]}), st, tmp_path)
    assert out["control_points"][0]["residual_km"] == 0.78 and out["images"] == []


def test_flat_single_pid_layout(tmp_path):
    st = tmp_path / "stage"
    dump(st / "staged_resolutions.json", {"resolutions": [rec()]})
    img(st / "map.jpg")
    dump(st / "traces" / "gcps.json", [{"px": [1, 2], "lonlat": [1, 2], "name": "Z"}])
    out = rp.files(rec(), st, tmp_path)
    assert len(out["images"]) == 1 and out["images"][0]["role"] == "map"
    assert out["control_points"][0]["name"] == "Z"
    # two candidates in the dir: the flat files are not this record's
    dump(st / "staged_resolutions.json", {"resolutions": [rec(), rec(project_id="P2")]})
    out = rp.files(rec(), st, tmp_path)
    assert out == {"images": [], "control_points": []}


def test_route_provenance_json_local_copy(tmp_path):
    st = tmp_path / "stage"
    img(st / "maps" / "yuma.jpg")
    dump(st / "route_provenance.json", {"P1": {
        "root_source": {"name": "FERC map", "page_url": "https://e.org/p", "local_copy": "maps/yuma.jpg"},
        "georef": {"gcps": [{"px": [5, 6], "lonlat": [7, 8], "name": "G"}]}}})
    out = rp.files(rec(), st, tmp_path)
    assert out["images"][0]["caption"] == "Map the route was traced from, FERC map"
    assert out["images"][0]["source_url"] == "https://e.org/p"
    assert out["control_points"] == [{"name": "G", "px": [5, 6], "lon": 7, "lat": 8}]


def test_georef_image_fallback(tmp_path):
    st = tmp_path / "stage"
    img(st / "traces" / "P1" / "pg-19.png")
    out = rp.files(rec(georef={"image": "pg-19.png (PDF page 19 rendered at 300 dpi)"}), st, tmp_path)
    assert len(out["images"]) == 1


def test_describe(tmp_path):
    st = tmp_path / "stage"
    st.mkdir()
    assert rp.describe(rec(method="osm"), st, tmp_path)["text"].startswith("The route was copied")
    stamped = rec(provenance={"text": "Stamped text.", "facts": [["Method", "X"]]})
    d = rp.describe(stamped, st, tmp_path)
    assert d == {"text": "Stamped text.", "facts": [["Method", "X"]]}
