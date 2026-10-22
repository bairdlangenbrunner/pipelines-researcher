"""review_app/map_assets.py: recording map pictures uploaded to an artifact page."""
import json

import pytest

import map_assets as ma

SHA = "a" * 64


def test_parse_pairs_file_and_paths(tmp_path):
    f = tmp_path / "up.json"
    f.write_text(json.dumps({f"work/review_assets/{SHA}.jpg": "/_blob/1"}))
    assert ma.parse([f"{'b' * 64}.png=/_blob/2?x=1"], f) == {f"{SHA}.jpg": "/_blob/1", f"{'b' * 64}.png": "/_blob/2?x=1"}
    with pytest.raises(SystemExit):
        ma.parse(["no-equals-sign"])


def test_main_records_for_the_page_url(tmp_path, monkeypatch):
    reg = tmp_path / "artifacts.json"
    reg.write_text(json.dumps({"pages": [{"name": "gas-batch", "kind": "artifact", "url": "https://claude.ai/artifact/X"}]}))
    monkeypatch.setattr(ma, "REGISTRY", reg)
    monkeypatch.setattr(ma, "MANIFEST", tmp_path / "assets.json")
    monkeypatch.setattr(ma, "ROOT", tmp_path)
    ma.main(["--page", "gas-batch", f"{SHA}.jpg=/_blob/1"])
    m = json.loads((tmp_path / "assets.json").read_text())
    assert m[SHA]["https://claude.ai/artifact/X"]["url"] == "/_blob/1"
    with pytest.raises(SystemExit):
        ma.main(["--page", "nope", f"{SHA}.jpg=/_blob/1"])
