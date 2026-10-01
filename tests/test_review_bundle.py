"""review_app/bundle.py: the one HTML file Apps Script serves. Never writes into the repo."""
import re

import bundle


def test_the_bundle_is_self_contained():
    html = bundle.bundle()
    assert html.startswith("<!doctype html>\n" + bundle.BANNER)
    assert '<base target="_top">' in html                      # links leave the sandboxed iframe
    assert not re.search(r'<script[^>]+src=', html) and '<link rel="stylesheet"' not in html
    for name in ("style.css",) + bundle.SCRIPTS:
        body = (bundle.WEB / name).read_text(encoding="utf-8").rstrip()
        assert body in html, name                               # inlined whole, unaltered
    assert html.index("GasStore") < html.index("window.ReviewApp")   # gas.js runs before app.js


def test_check_and_out(tmp_path, capsys):
    out = tmp_path / "index.html"
    assert bundle.main(["--check", "--out", str(out)]) == 1     # nothing there yet
    assert not out.exists()                                     # --check writes nothing
    assert bundle.main(["--out", str(out)]) == 0
    assert out.read_text(encoding="utf-8") == bundle.bundle()
    assert bundle.main(["--check", "--out", str(out)]) == 0
    out.write_text(out.read_text(encoding="utf-8") + "\n<!-- hand edit -->", encoding="utf-8")
    assert bundle.main(["--check", "--out", str(out)]) == 1
    assert "out of date" in capsys.readouterr().err


def test_refuses_what_an_inline_script_cannot_hold(tmp_path):
    web = tmp_path / "web"
    web.mkdir()
    for name in ("index.html", "style.css") + bundle.SCRIPTS:
        (web / name).write_text((bundle.WEB / name).read_text(encoding="utf-8"), encoding="utf-8")
    assert bundle.bundle(web) == bundle.bundle()
    (web / "app.js").write_text("var s = '</script>';\n", encoding="utf-8")
    try:
        bundle.bundle(web)
    except SystemExit as e:
        assert "app.js" in str(e)
    else:
        raise AssertionError("an inline </script> was bundled")


def test_config_gs_needs_both_ids_and_the_project_lists_every_file(tmp_path):
    assert bundle.config_gs({}) is None and bundle.config_gs({"data_folder_id": "F"}) is None
    cfg = bundle.config_gs({"data_folder_id": "F", "store_sheet_id": "S"})
    assert '"DATA_FOLDER_ID": "F"' in cfg and '"STORE_SHEET_ID": "S"' in cfg and cfg.startswith("// GENERATED")
    proj = bundle.project("<html>", cfg)
    assert [(f["name"], f["type"]) for f in proj["files"]] == \
        [("appsscript", "json"), ("Code", "server_js"), ("Config", "server_js"), ("index", "html")]
    assert [f["name"] for f in bundle.project("<html>", None)["files"]] == ["appsscript", "Code", "index"]
    assert "CONFIG_[name]" in proj["files"][1]["source"]          # Code.gs reads the generated config


def test_main_writes_and_removes_config_next_to_the_bundle(tmp_path):
    out, cfg = tmp_path / "index.html", tmp_path / "google.json"
    cfg.write_text('{"data_folder_id": "F", "store_sheet_id": "S"}')
    assert bundle.main(["--out", str(out), "--config", str(cfg), "--project", str(tmp_path / "p.json")]) == 0
    assert (tmp_path / "Config.gs").read_text() == bundle.config_gs({"data_folder_id": "F", "store_sheet_id": "S"})
    assert bundle.main(["--check", "--out", str(out), "--config", str(cfg)]) == 0
    cfg.write_text('{"data_folder_id": "", "store_sheet_id": "S"}')
    assert bundle.main(["--check", "--out", str(out), "--config", str(cfg)]) == 1      # a stale Config.gs
    assert bundle.main(["--out", str(out), "--config", str(cfg)]) == 0 and not (tmp_path / "Config.gs").exists()
