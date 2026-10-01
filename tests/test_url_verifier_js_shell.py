"""A JavaScript application shell is neither a content miss nor a deletion (P6011, 2026-10-01)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import url_verifier as uv  # noqa: E402

SHELL = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8"><title>EIP Oil & Gas Watch</title>
<script async src="https://www.googletagmanager.com/gtag/js?id=G-X"></script>
<script>window.dataLayer = window.dataLayer || [];</script>
<script type="module" crossorigin src="/assets/index-Dmkw508R.js"></script>
<link rel="stylesheet" crossorigin href="/assets/index-BvkmLKh7.css"></head>
<body><div id="app"></div></body></html>"""

ARTICLE = ("<html><head><title>x</title><script src='/a.js'></script></head><body><p>"
           + "Project Maple open season closed in September 2023. " * 40 + "</p></body></html>")


class _R:
    def __init__(self, text, ctype="text/html; charset=utf-8", status=200):
        self.text, self.content, self.status_code = text, text.encode("utf-8"), status
        self.headers, self.encoding, self.history, self.url = {"Content-Type": ctype}, "utf-8", [], "u"


def _serve(monkeypatch, resp, app=None):
    monkeypatch.setattr(uv, "_http_get", lambda url, timeout, headers, verify=True: resp)
    monkeypatch.setattr(uv, "_app_data", lambda url, timeout: app)


def test_shell_detection():
    assert uv._is_js_shell(SHELL, "text/html")
    assert not uv._is_js_shell(ARTICLE, "text/html")            # a bundle tag alone is not a shell
    assert not uv._is_js_shell("<html><body><p>" + "words " * 100 + "</p></body></html>", "text/html")
    assert not uv._is_js_shell('{"a": 1}', "application/json")


def test_shell_is_flagged_even_on_a_bare_reachability_check(monkeypatch):
    _serve(monkeypatch, _R(SHELL))
    v = uv.verify_url("https://example.org/pipeline/1")
    assert v["ok"] is False and v["status"] == 200 and v["js_shell"] is True
    assert "NOT a deletion" in v["reason"] and "not a content miss" in v["reason"].lower()
    v = uv.verify_url("https://example.org/pipeline/1", any_of=["2023"])
    assert v["ok"] is False and v.get("js_shell") is True


def test_a_real_article_is_still_read(monkeypatch):
    _serve(monkeypatch, _R(ARTICLE))
    assert uv.verify_url("https://example.org/a", any_of=["2023"], name="Project Maple")["ok"] is True


def test_the_data_api_record_stands_in_for_the_shell(monkeypatch):
    rec = uv._json_prose({"id": "6965", "pipeline_name": "Project Maple", "AdditionalCapacity": 750,
                          "ResearchNotes": "open season notice dated 2023-09-12 " * 60})
    _serve(monkeypatch, _R(SHELL), app=(rec, "oilandgaswatch data api https://oilandgaswatch.org/api/01-01_PIPELINES/data/6965"))
    v = uv.verify_url("https://oilandgaswatch.org/pipeline/6965", any_of=["2023"], name="Project Maple")
    assert v["ok"] is True and v["name_found"] is True and v["fetch_route"].startswith("oilandgaswatch data api")
    v = uv.verify_url("https://oilandgaswatch.org/pipeline/6965", any_of=["1999"])
    assert v["ok"] is False and "data value not found" in v["reason"] and "js_shell" not in v


def test_only_oilandgaswatch_pipeline_urls_are_resolved():
    assert uv._OGW_PIPELINE_RE.match("https://oilandgaswatch.org/pipeline/6965")
    assert uv._OGW_PIPELINE_RE.match("https://www.oilandgaswatch.org/pipeline/6965/?x=1")
    assert not uv._OGW_PIPELINE_RE.match("https://oilandgaswatch.org/d/6965")
    assert not uv._OGW_PIPELINE_RE.match("https://example.org/pipeline/6965")
    assert uv._app_data("https://example.org/pipeline/1", 5) is None


def test_a_whole_number_may_end_a_sentence():
    c = uv._contains
    assert c("open season closed in september 2023. project maple", "2023")
    assert c("capacity of 1,262 mmcf/d, or 2,023.", "1,262") and c("worth 2,023.", "2,023")
    assert not c("path d=589.126229", "1262") and not c("12,620 km", "1262") and not c("1,262 km", "262")
    assert not c("2023.09.12", "2023")                 # digits across a dot are one number
    assert c("2023-10-02t15:16", "2023")
