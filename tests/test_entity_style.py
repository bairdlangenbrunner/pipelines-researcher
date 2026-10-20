"""entity_style.style() — the ownership team's entity-name conventions, as rules.

Each case pins one rule from docs/reference/owner_style.md (team examples where the guide
gives one). Gazetteer-dependent cases (`exact`/`alias`/`stem` bases) read the committed
data/owner_gazetteer.csv + data/owner_aliases.json, so they also pin the adoption policy:
adopt on exact / confirmed alias, flag everything fuzzier.
"""
import pytest

import entity_style as ES


def s(name, **kw):
    return ES.style(name, **kw)


# --- sentinels / passthrough ---------------------------------------------------------------

@pytest.mark.parametrize("raw,want", [
    ("Unknown", "unknown"), ("UNKNOWN", "unknown"), ("Small shareholders", "small shareholder(s)"),
    ("natural persons", "natural person(s)"),
])
def test_sentinels(raw, want):
    r = s(raw)
    assert r.styled == want and r.basis == "sentinel" and r.confidence == "high"


def test_non_latin_passes_through():
    r = s("Газпром")
    assert r.styled == "Газпром" and r.basis == "passthrough" and "non_latin" in r.flags


# --- legal forms -------------------------------------------------------------------------------

@pytest.mark.parametrize("raw,want", [
    ("Chubu Steel Plate Co., Ltd.", "Chubu Steel Plate Co Ltd"),          # the guide's own example
    ("Acme Pipeline Corporation", "Acme Pipeline Corp"),
    ("Acme Pipeline Company Limited", "Acme Pipeline Co Ltd"),
    ("Acme Pipeline Incorporated", "Acme Pipeline Inc"),
    ("Acme Energia S.p.A.", "Acme Energia SpA"),
    ("Acme Energia S.A.", "Acme Energia SA"),
    ("Acme Pipeline, L.L.C.", "Acme Pipeline LLC"),
])
def test_long_forms_shortened_and_punctuation_removed(raw, want):
    assert s(raw).styled == want


def test_company_kept_when_form_is_llc():
    # "Company" stays when the legal form is LLC (team rule); only the form is canonicalized
    assert s("Acme Pipeline Company, L.L.C.").styled == "Acme Pipeline Co LLC"


def test_integral_punctuation_kept():
    assert s("E.ON SE").styled == "E.ON SE"


def test_dotted_abbreviation_loses_dots():
    r = s("Chevron U.S.A. Inc.")
    assert r.styled == "Chevron USA Inc" and "dots_stripped" in r.flags


# --- Russian / CIS forms ----------------------------------------------------------------------

@pytest.mark.parametrize("raw,want", [
    ("PAO Gazprom", "Gazprom PJSC"),
    ("OOO Gazprom Transgaz Moskva", "Gazprom Transgaz Moskva LLC"),
    ("AO Transneft-Sibir", "Transneft-Sibir JSC"),
    ("TOO QazaqGaz Pipelines", "QazaqGaz Pipelines LLP"),
    ("Public Joint Stock Company Transneft", "Transneft PJSC"),
])
def test_cis_forms_move_to_trailing_english_short_form(raw, want):
    r = s(raw)
    assert r.styled == want and "form_moved" in r.flags


def test_defunct_cis_forms_flag_registration_check():
    r = s("OAO Tatneft")
    assert r.styled == "Tatneft OJSC"
    assert "form_check_registration" in r.flags
    # same stem exists in the gazetteer under another form → candidate, never adopted
    assert "form_conflict" in r.flags
    assert any(c["name"] == "Tatneft PJSC" for c in r.candidates)


def test_pt_prefix_kept_and_mid_name_parenthetical_kept():
    assert s("PT Pertamina (Persero)").styled == "PT Pertamina (Persero)"
    assert s("Mettiki Coal (WV) LLC").styled == "Mettiki Coal (WV) LLC"
    assert s("GAIL (India) Ltd").styled == "GAIL Ltd"      # confirmed alias → canonical


# --- acronyms -----------------------------------------------------------------------------------

def test_trailing_acronym_dropped_and_kept_as_alias():
    r = s("Yacimientos Petrolíferos Fiscales Bolivianos (YPFB)")
    assert "(YPFB)" not in r.styled
    assert "acronym_dropped" in r.flags
    assert "YPFB" in r.aliases
    assert "YPFB" in r.note


def test_trailing_trade_name_dropped_and_flagged_when_not_derivable():
    # a one-word trade name that is part of the name is an abbreviation of it
    r = s("Acme Petroleum Corporation (Acme)")
    assert r.styled == "Acme Petroleum Corp" and "acronym_dropped" in r.flags
    assert "Acme" in r.aliases and "acronym_not_initials" not in r.flags
    # one that is not derivable from the name is still dropped, but flagged for a look
    r = s("Acme Petroleum Corporation (Zephyr)")
    assert r.styled == "Acme Petroleum Corp"
    assert "acronym_dropped" in r.flags and "acronym_not_initials" in r.flags


@pytest.mark.parametrize("raw", [
    "Sinopec Marketing (Hong Kong)",            # geography
    "Enbridge Energy Company (Private) Ltd",    # legal-name element, not trailing
    "Ministry of Oil (Iraq)",                   # state body's country
])
def test_parentheticals_that_are_not_trade_names_are_kept(raw):
    assert "(" in s(raw).styled


# --- state bodies -------------------------------------------------------------------------------

@pytest.mark.parametrize("raw,want", [
    ("Iraq Ministry of Oil", "Ministry of Oil (Iraq)"),
    ("Iraqi Ministry of Oil", "Ministry of Oil (Iraq)"),
    ("Ministry of Oil of Iraq", "Ministry of Oil (Iraq)"),
    ("Ministry of Energy of the Republic of Kazakhstan", "Ministry of Energy (Kazakhstan)"),
    ("Republic of Iraq", "Government of Iraq"),
    ("Government of the Republic of Türkiye", "Government of Türkiye"),
    ("State of Qatar", "Government of Qatar"),
])
def test_state_bodies(raw, want):
    r = s(raw)
    assert r.styled == want
    assert "state_body" in r.flags or r.basis in ("exact", "alias")


# --- suffixes the sheet carries ------------------------------------------------------------

def test_former_tail_kept_and_flagged():
    r = s("Acme Pipeline Corporation [former]")
    assert r.styled == "Acme Pipeline Corp [former]" and "former" in r.flags


def test_percent_tail_stripped():
    r = s("Acme Pipeline Corporation [55%]")
    assert r.styled == "Acme Pipeline Corp" and "percent_stripped" in r.flags


def test_multi_owner_cell_styled_part_by_part_low_confidence():
    r = s("Energy Transfer; Enbridge")
    assert r.styled == "Energy Transfer LP; Enbridge Inc"
    assert "multi_owner" in r.flags and r.confidence == "low"


# --- adoption policy against the team's gazetteer --------------------------------------------

def test_exact_gazetteer_hit_adopts_team_spelling_and_entity_id():
    r = s("Kuwait Oil Company Limited")
    assert r.styled == "Kuwait Oil Company Ltd"        # the team keeps "Company" here
    assert r.basis == "exact" and r.confidence == "high"
    assert r.entity_id and r.entity_id.startswith("E")


def test_confirmed_alias_adopts_canonical():
    r = s("Saudi Aramco")
    assert r.styled == "Saudi Arabian Oil Co" and r.basis == "alias" and r.confidence == "high"
    assert r.entity_id == "E100000000888"


def test_candidate_alias_is_flagged_not_adopted():
    # subsidiary ≈ parent: the SPV ruling says Owner1 holds the SPV, never the parent
    r = s("Kinder Morgan Freedom Pipeline LLC")
    assert r.styled == "Kinder Morgan Freedom Pipeline LLC"
    assert "alias_candidate" in r.flags
    assert any("Kinder Morgan" in c["name"] for c in r.candidates)


def test_stem_match_adopts_form_only_when_unambiguous():
    r = s("Petroleum Development Oman")
    assert r.basis == "stem" and r.confidence == "medium"
    assert r.styled.startswith("Petroleum Development Oman ") and "form_from_gazetteer" in r.flags
    assert "no_legal_form" not in r.flags


def test_unknown_name_without_form_is_low_and_flagged():
    r = s("Zxqv Pipeline Partners")
    assert r.styled == "Zxqv Pipeline Partners"
    assert "no_legal_form" in r.flags and r.confidence == "low"


def test_changed_and_to_dict():
    r = s("PAO Gazprom")
    assert r.changed is True
    d = r.to_dict()
    assert d["raw"] == "PAO Gazprom" and d["styled"] == "Gazprom PJSC"
    assert s("Gazprom PJSC").changed is False


# --- leading acronym, rulings, adoption policy (2026-10-05) -----------------------------------

@pytest.mark.parametrize("raw,want,alias", [
    ("TGS (Transportadora de Gas del Sur SA)", "Transportadora de Gas del Sur SA", "TGS"),
    ("NTS (Nova Transportadora do Sudeste SA)", "Nova Transportadora do Sudeste SA", "NTS"),
])
def test_leading_acronym_keeps_the_legal_name(raw, want, alias):
    r = s(raw)
    assert r.styled == want and "acronym_lead" in r.flags and r.aliases[0] == alias
    assert ")" not in r.styled and "(" not in r.styled
    assert ES.adoptable(r)


def test_parenthetical_form_token_is_not_rewritten():
    assert s("Acme (Private) Ltd").styled == "Acme (Private) Ltd"
    assert s("US (Acme Pipelines Inc)").styled == "US (Acme Pipelines Inc)"      # a kept parenthetical lead


def test_ruling_wins_and_is_adoptable():
    r = s("Kuwait Oil Co (KOC)")
    assert r.basis == "ruling" and r.styled == "Kuwait Oil Company Ltd" and "KOC" in r.aliases
    assert ES.adoptable(r)
    m = s("Enterprise Products Partners; Enbridge")
    assert m.basis == "ruling" and m.styled == "Enterprise Products Partners LP; Enbridge Inc"
    assert ES.cell_ruling("P1321", "Owner2", ) == ES.rulings()["cells"]["P1321/Owner2"]
    assert ES.cell_ruling("P1321", "Owner9") is None


def test_adoptable_policy():
    assert ES.adoptable(s("Chubu Steel Plate Co., Ltd."))                 # punctuation only
    lst = s("Enbridge Inc., Kinder Morgan, Inc.")
    assert lst.changed and not ES.adoptable(lst)                        # a comma list
    nf = s("Acme  Zeta Pipelines")
    assert nf.changed and "no_legal_form" in nf.flags and not ES.adoptable(nf)   # no legal form, no hit
    assert ES.adoptable(s("Acme Zeta Pipelines"))                        # unchanged is always fine
    cl = s("Acme Zeta Gas Transmission Company, LLC")         # a name no ruling covers (FGT has one, 2026-10-14)
    assert cl.styled == "Acme Zeta Gas Transmission Co LLC" and "form_punctuation" in cl.flags and ES.adoptable(cl)
    af = s("NextEra Energy, Inc. (affiliate)")
    assert "owner_qualifier" in af.flags and not ES.adoptable(af)        # a qualifier, not an acronym: a person reads it


@pytest.mark.parametrize("raw,want", [
    ("NextEra Energy, Inc. (affiliate)", "NextEra Energy Inc"),
    ("Con Edison Gas Pipeline and Storage, LLC (affiliate)", "Con Edison Gas Pipeline and Storage LLC"),
    ("EQT Corporation (via Midstream Joint Venture)", "EQT Corp"),
    ("Acme Pipeline Corp (parent)", "Acme Pipeline Corp"),
    ("Acme Pipeline Corp (indirectly, through Acme Holdings LLC)", "Acme Pipeline Corp"),
])
def test_stake_qualifier_stripped_and_held(raw, want):
    # P7829 MVP (2026-10-14): a note on how the stake is held is not part of the name, and it
    # usually means the cell names a parent rather than the immediate owner, so a person decides
    r = s(raw)
    assert r.styled == want and "owner_qualifier" in r.flags
    assert not ES.adoptable(r) and ES.needs_person(r)


def test_spaced_slash_is_several_owners():
    r = s("AltaGas Ltd. / RGC Resources, Inc. (affiliates)")
    assert r.styled == "AltaGas Ltd; RGC Resources Inc" and "multi_owner" in r.flags
    assert ES.needs_person(r)
    for name in ("A/S Norske Shell", "HMN Naturgas I/S", "Deutsch/Dänische Erdgastransport-Gesellschaft mbH"):
        assert "multi_owner" not in s(name).flags                      # an unspaced slash is part of the name


def test_needs_person_and_held_names():
    assert not ES.needs_person(s("Mountain Valley Pipeline LLC"))
    assert not ES.needs_person(s("Chubu Steel Plate Co., Ltd."))       # the styler re-spells it on its own
    assert ES.needs_person(s("Enbridge Inc., Kinder Morgan, Inc."))
    ruled = s("Enterprise Products Partners; Enbridge").styled
    assert not ES.needs_person(s(ruled))                               # a ruled list re-checks clean
    held = ES.held_names({"Owner1": "Mountain Valley Pipeline LLC", "Owner1%": "1",
                          "Owner3": "NextEra Energy, Inc. (affiliate)", "Operator": ""})
    assert [(c, st) for c, _, st, _ in held] == [("Owner3", "NextEra Energy Inc")]
