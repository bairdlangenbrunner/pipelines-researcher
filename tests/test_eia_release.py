"""eia_release: EIA values come from the newest pipeline-projects release (Baird 2026-10-08)."""
import eia_release as er

B = er.BASE_URL
NEW = B + "EIA-NaturalGasPipelineProjectsAug2026.xlsx"
OLD = B + "EIA-NaturalGasPipelineProjects_Jan2021.xlsx"


def test_release_of_irregular_file_names():
    assert er.release_of_file("EIA-NaturalGasPipelineProjectsAug2026.xlsx") == "2026-08"
    assert er.release_of_file("EIA-NaturalGasPipelineProjects_July2019.xlsx") == "2019-07"
    assert er.release_of_file("EIA-NaturalGasPipelineProjects_March2020.xlsx") == "2020-03"
    assert er.release_of_file("EIA-NaturalGasPipelineProjects.xlsx") is None
    assert er.release_of_url("https://web.archive.org/web/2024/" + OLD) == "2021-01"
    assert er.release_of_url("https://www.eia.gov/naturalgas/data.php#pipelines") is None


def test_latest_is_the_newest_recorded_release():
    lt = er.latest()
    assert lt["release"] == max(r["release"] for r in er.local_releases())
    assert lt["url"].startswith(B)


def test_older_release_alone_is_stale_beside_the_newest_is_fine(monkeypatch):
    monkeypatch.setattr(er, "latest", lambda: {"file": NEW.rsplit("/", 1)[-1], "release": "2026-08",
                                               "url": NEW, "label": "August 2026"})
    assert er.stale_refs({"proposed_refs": [OLD]}) == [OLD]
    assert "August 2026" in er.stale_reason({"proposed_refs": [OLD, "http://ferc.example/x"]})
    assert er.stale_refs({"proposed_refs": [NEW, OLD]}) == []          # history beside the newest
    assert er.stale_refs({"proposed_refs": [NEW]}) == []
    assert er.stale_refs({"proposed_refs": ["http://ferc.example/x"]}) == []
    # the newest release does not list the project, and the note says so in words
    note = "The project is not listed in the August 2026 EIA release. The January 2021 release gives 36 in."
    assert er.stale_refs({"proposed_refs": [OLD], "researcher_notes": note}) == []
    assert er.stale_refs({"proposed_refs": [OLD], "researcher_notes": "The August 2026 release gives 36 in."}) == [OLD]
