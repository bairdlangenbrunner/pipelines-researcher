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


def test_only_a_value_change_on_an_older_release_alone_is_stale(monkeypatch):
    monkeypatch.setattr(er, "latest", lambda: {"file": NEW.rsplit("/", 1)[-1], "release": "2026-08",
                                               "url": NEW, "label": "August 2026"})
    assert er.stale_refs({"proposed_refs": [OLD]}) == [OLD]
    assert "August 2026" in er.stale_reason({"proposed_refs": [OLD, "http://ferc.example/x"]})
    assert er.stale_refs({"proposed_refs": [NEW, OLD]}) == []          # history beside the newest
    assert er.stale_refs({"proposed_refs": [NEW]}) == []
    assert er.stale_refs({"proposed_refs": ["http://ferc.example/x"]}) == []
    # a ref on the sheet's own value: an older release that states it is fine, the newest not owed
    assert er.stale_refs({"proposed_refs": [OLD]}, changes_value=False) == []
    # a note does not excuse a change: the newest release no longer listing it means no change
    note = "The project is not listed in the August 2026 EIA release."
    assert er.stale_refs({"proposed_refs": [OLD], "researcher_notes": note}) == [OLD]


def test_dropped_skips_renamed_split_and_docket_successors():
    row = lambda k, n, rel, st="TX", dk="": {"project_key": k, "project_name": n, "last_release": rel,
                                             "state_s": st, "docket_number": dk}
    lat = [row("a", "Hugh Brinson Pipeline (formerly Warrior Pipeline) Phase I & II", "2026-08"),
           row("b", "Warrior Pipeline", "2024-10"),                                   # renamed
           row("c", "Kosciusko Junction Pipeline Project", "2026-08", "MS"),
           row("d", "Kosci Junction Project", "2025-07", "MS", "PF25-6-000"),         # respelled
           row("e", "Evangeline Pass Expansion Project (Phase 1)", "2026-08", "LA", "CP20-50-000"),
           row("f", "Evangeline Pass Expansion Project", "2024-01", "LA", "CP20-50"),  # split, same docket
           row("g", "Project Maple", "2026-01", "NY,MA"),                             # gone
           row("h", "Magnum Gas Storage Project", "2026-05", "UT", "CP25-233-000")]   # gone
    assert er.dropped(lat) == {"g": "2026-01", "h": "2026-05"}
