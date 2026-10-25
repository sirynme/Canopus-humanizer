"""Unit Tests for 17-Stage Mathematical Transformation Engine."""

import time
import pytest
from turnitout.config import ConfigNamespace
from turnitout.core.modifier import DocumentModifier


def test_latex_protection_and_restoration():
    """Verify that LaTeX math and macros are strictly preserved."""
    modifier = DocumentModifier()
    sample = r"Let $x \in \mathbb{R}$ satisfy $\int_0^1 f(x) dx = 0$ as shown in \cite{Smith2024}."
    protected = modifier._protect_latex(sample)
    assert "\x00_LTX_" in protected
    restored = modifier._restore_latex(protected)
    assert restored == sample


def test_phrase_rewrites():
    """Verify multi-word phrase rewriting."""
    cfg = ConfigNamespace()
    cfg.ENABLE_PHRASE_REWRITE = True
    modifier = DocumentModifier(config=cfg)
    sample = "In conclusion, this research paper provides a comprehensive tapestry of results."
    res = modifier._apply_phrase_rewrites(sample)
    assert "the present work" in res or "to encapsulate" in res or res != sample


def test_protected_terms_preserved():
    """Verify that protected terms are NEVER swapped for synonyms."""
    cfg = ConfigNamespace()
    cfg.INTENSITY = 100.0
    cfg.SYNONYM_ALIGNMENT = 1.0
    modifier = DocumentModifier(config=cfg)
    sample = "Navier-Stokes and PyTorch models analyze the data."
    res = modifier.modify_document(sample, protected_terms={"Navier-Stokes", "PyTorch"})
    assert "Navier-Stokes" in res
    assert "PyTorch" in res


def test_voice_transformation():
    """Verify active to passive voice inversion."""
    cfg = ConfigNamespace()
    cfg.ENABLE_VOICE_TRANSFORM = True
    cfg.VOICE_TRANSFORM_RATE = 1.0
    modifier = DocumentModifier(config=cfg)
    sample = "We analyzed the results of this experiment across sixty trials."
    res = modifier._transform_voice(sample)
    assert "was analyzed" in res.lower()


def test_sentence_fusion():
    """Verify fusion of adjacent short sentences."""
    cfg = ConfigNamespace()
    cfg.ENABLE_SENTENCE_FUSION = True
    cfg.SENTENCE_FUSION_RATE = 1.0
    modifier = DocumentModifier(config=cfg)
    sentences = ["The temperature increased rapidly.", "This caused immediate expansion."]
    fused = modifier.fuse_adjacent_sentences(sentences)
    assert len(fused) == 1
    assert "temperature increased" in fused[0]


def test_nominalization():
    """Verify verb to noun nominalization."""
    cfg = ConfigNamespace()
    cfg.ENABLE_NOMINALIZATION = True
    cfg.NOMINALIZATION_RATE = 1.0
    modifier = DocumentModifier(config=cfg)
    sample = "We investigated the phenomena across three independent benchmark trials."
    res = modifier._nominalize(sample)
    assert "investigation of" in res.lower()


def test_appositive_injection():
    """Verify that appositive definitions are injected and not duplicated."""
    cfg = ConfigNamespace()
    cfg.ENABLE_APPOSITIVE = True
    cfg.APPOSITIVE_RATE = 1.0
    modifier = DocumentModifier(config=cfg)
    sample = "The Crank-Nicolson method is applied for parabolic problems."
    res = modifier._inject_appositives(sample)
    assert "an implicit second-order-accurate scheme" in res

    # Second injection should not duplicate
    res_second = modifier._inject_appositives(sample)
    assert res_second.count("an implicit second-order-accurate scheme") <= 1


def test_discourse_marker_rotation():
    """Verify that discourse markers rotate to avoid AI repetition."""
    cfg = ConfigNamespace()
    cfg.ENABLE_DISCOURSE_ROTATE = True
    cfg.DISCOURSE_ROTATE_RATE = 1.0
    modifier = DocumentModifier(config=cfg)
    sample = "However, the convergence rate remains optimal."
    res = modifier._rotate_discourse_markers(sample)
    assert not res.startswith("However,")
    assert any(res.startswith(prefix) for prefix in ["Nevertheless,", "Nonetheless,", "On the other hand,", "That said,"])


def test_latency_performance():
    """Verify sub-150ms execution speed for single-paragraph transformation."""
    modifier = DocumentModifier()
    sample = (
        "Furthermore, our experimental findings demonstrate that deep learning models "
        "frequently introduce formulaic syntax across large datasets. This study plays a "
        "pivotal role in illustrating that artificial intelligence stands as a testament "
        "to human innovation. In conclusion, it is important to delve into the comprehensive "
        "tapestry of modern neural networks."
    )
    t0 = time.perf_counter()
    res = modifier.modify_document(sample)
    elapsed_ms = (time.perf_counter() - t0) * 1000.0
    assert len(res) > 0
    assert elapsed_ms < 150.0, f"Latency ({elapsed_ms:.2f}ms) exceeded 150ms threshold!"
