"""Unit Tests for ZipPy Entropy Checker & Winnowing Similarity."""

import pytest
from turnitout.core.checker import ZipPyChecker
from turnitout.core.winnowing import WinnowingEngine


def test_shannon_entropy():
    """Verify that Shannon entropy calculation works correctly."""
    low_entropy = "aaaaaaaaaa"
    high_entropy = "The empirical observations reveal non-trivial variance across distributed topologies."
    
    ent_low = ZipPyChecker.calculate_shannon_entropy(low_entropy)
    ent_high = ZipPyChecker.calculate_shannon_entropy(high_entropy)
    assert ent_low == 0.0
    assert ent_high > 4.0


def test_ai_marker_auditor():
    """Verify detection of overused AI discourse clichés."""
    text_with_cliches = "It is important to delve into the comprehensive tapestry of modern AI."
    markers = ZipPyChecker.audit_ai_markers(text_with_cliches)
    found = {m["marker"] for m in markers}
    assert "delve into" in found
    assert "comprehensive tapestry" in found


def test_winnowing_similarity_reduction():
    """Verify that Winnowing k=5, w=4 detects similarity and shows reduction."""
    engine = WinnowingEngine(k=5, w=4)
    text_orig = "we analyze the heat equation using finite difference schemes and compute the stability criteria across grid domains"
    text_identical = "we analyze the heat equation using finite difference schemes and compute the stability criteria across grid domains"
    text_humanized = "the heat equation was scrutinized through finite difference modalities, thereby establishing stability criteria across grid domains"

    sim_100, _, _ = engine.calculate_similarity(text_orig, text_identical)
    assert sim_100 == 100.0

    sim_reduced, _, _ = engine.calculate_similarity(text_orig, text_humanized)
    assert sim_reduced < 40.0, f"Expected similarity < 40%, got {sim_reduced}%"
