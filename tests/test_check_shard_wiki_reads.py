"""check_wiki_reads: every citation harvested from the row's gem.wiki page is opened and
accounted for in `wiki_citations_read` (Baird 2026-10-17, P1451)."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import check_shard_coverage as c  # noqa: E402

CITES = [
    {"url": "https://eegas.com/ukr_090115e.htm", "cite_id": "n1", "link_text": "Dispute"},
    {"url": "https://example.org/a?trk=x", "cite_id": "n2", "link_text": "A"},
    {"url": "https://example.org/b", "cite_id": "n3", "link_text": "B"},
    {"url": "https://web.archive.org/web/2021/https://example.org/b", "cite_id": "n3", "link_text": "Archived"},
]


def staging(tmp_path):
    (tmp_path / "wiki_citations.json").write_text(json.dumps({"pages": {"P1": {"citations": CITES}}}))
    (tmp_path / "worklist.json").write_text(json.dumps({"units": []}))
    c.load_wiki_citations.cache_clear()
    return tmp_path


def shard(reads, refs=()):
    return {"wiki_citations_read": reads, "fills": [{"ref_col": "Capacity [ref]", "proposed_refs": list(refs)}]}


GOOD = [
    {"url": "https://eegas.com/ukr_090115e.htm", "outcome": "used",
     "read_via": "https://web.archive.org/web/20090122061413/http://eegas.com:80/ukr_090115e.htm"},
    {"url": "https://example.org/a", "outcome": "not_this_row", "note": "company page"},
    {"url": "https://web.archive.org/web/2021/https://example.org/b", "outcome": "dead",
     "tried": ["scripts/fetch.py: 404", "wayback CDX: none"]},
]


def test_all_accounted_passes(tmp_path):
    st = staging(tmp_path)
    gaps, enforced = c.check_wiki_reads(st, "P1", shard(GOOD, ["https://web.archive.org/web/20090122061413/http://eegas.com:80/ukr_090115e.htm"]))
    assert enforced and gaps == []


def test_unread_used_without_ref_and_short_ladder_block(tmp_path):
    st = staging(tmp_path)
    reads = [GOOD[0], dict(GOOD[2], tried=["curl"])]
    gaps, _ = c.check_wiki_reads(st, "P1", shard(reads))
    why = " | ".join(g["why"] for g in gaps)
    assert "never opened" in why and "no record carries it" in why and "full ladder" in why


def test_legacy_shard_is_not_enforced(tmp_path):
    st = staging(tmp_path)
    gaps, enforced = c.check_wiki_reads(st, "P1", {"fills": []})
    assert not enforced and len(gaps) == 3
