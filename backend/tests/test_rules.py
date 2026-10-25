"""Unit Tests for Rules & Taxonomy Loader."""

import pytest
from turnitout.core.rules import (
    ACADEMIC_TAXONOMY,
    APPOSITIVES,
    CONJUNCTIONS,
    DETERMINERS,
    DISCOURSE_MARKERS,
    HEDGE_WORDS,
    NOMINALIZATIONS,
    PHRASES,
    PROTECTED_TERMS,
    SYNONYMS,
    clean_rule_data,
)


def test_clean_rule_data():
    """Verify that __prompt__ metadata is stripped from dictionaries and lists."""
    raw_dict = {"__prompt__": "Instructions...", "analyze": ["scrutinize"]}
    cleaned_dict = clean_rule_data(raw_dict)
    assert "__prompt__" not in cleaned_dict
    assert "analyze" in cleaned_dict

    raw_list = [{"__prompt__": "Instructions..."}, ["\\bpattern\\b", "replacement"]]
    cleaned_list = clean_rule_data(raw_list)
    assert len(cleaned_list) == 1
    assert cleaned_list[0] == ["\\bpattern\\b", "replacement"]


def test_static_rules_loaded():
    """Verify all static JSON rules are loaded and populated."""
    assert len(SYNONYMS) > 20
    assert len(PHRASES) > 20
    assert len(HEDGE_WORDS) > 10
    assert len(DETERMINERS) > 5
    assert len(CONJUNCTIONS) > 10
    assert len(PROTECTED_TERMS) > 20
    assert len(NOMINALIZATIONS) > 15
    assert len(APPOSITIVES) > 15
    assert len(DISCOURSE_MARKERS) > 10


def test_academic_taxonomy_hierarchy():
    """Verify all 5 disciplines exist and have valid subfields."""
    expected_disciplines = [
        "computer_science",
        "engineering_physics",
        "mathematics_statistics",
        "quantitative_finance",
        "medical_life_sciences"
    ]
    for disc in expected_disciplines:
        assert disc in ACADEMIC_TAXONOMY, f"Missing discipline: {disc}"
        assert len(ACADEMIC_TAXONOMY[disc]) > 0
