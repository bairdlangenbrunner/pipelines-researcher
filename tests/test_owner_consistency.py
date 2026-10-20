"""owner_consistency: the keys that join two spellings into one company, and the ones that must not."""
import pytest

import owner_consistency as OC


@pytest.mark.parametrize("name,want", [
    ("Transcontinental Gas Pipe Line Company, LLC", "transcontinental gas pipeline"),
    ("Transcontinental Gas Pipeline", "transcontinental gas pipeline"),
    ("Kuwait Petroleum Corp", "kuwait petroleum"),
    ("Kuwait Petroleum Co", "kuwait petroleum"),
    ("Texas Gas Transmission LLC", "texas gas transmission"),
    ("Texas Gas Transmission", "texas gas transmission"),
    ("The Pacific Gas and Electric Co", "pacific gas and electric"),
])
def test_stem_key(name, want):
    assert OC.stem_key(name) == want


@pytest.mark.parametrize("short,full,want", [
    ("Transco", "Transcontinental Gas Pipe Line Co LLC", True),       # clipped first word
    ("SNGPL", "Sui Northern Gas Pipelines Ltd", True),                # initials
    ("Transneft", "Transneft-Sibir JSC", False),                      # parent and subsidiary
    ("ADNOC", "ADNOC Gas plc", False),
    ("Tra", "Transcontinental Gas Pipe Line Co LLC", False),          # too short to be a clip
    ("Kinder Morgan", "Kinder Morgan Louisiana Pipeline LLC", False), # two words: not a short name
])
def test_is_short_name(short, full, want):
    assert OC.is_short_name(short, full) is want
