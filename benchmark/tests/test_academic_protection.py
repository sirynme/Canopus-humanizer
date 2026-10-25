"""Automated Regression & Protection Suite for Mathematical and Academic Documents.

Tests compliance with Task 6:
- Inline and display mathematics
- Nested and multiline LaTeX environments
- Fractions, integrals, derivatives, subscripts and superscripts
- Numerical quantities and physical units
- p-values and confidence intervals
- Citation markers (IEEE, APA, LaTeX)
- Research questions, hypotheses, and structural proposal headings
- Multi-Word Technical Units (MWUs)
- Exact restoration and fail-closed rollback
"""

import pytest
from turnitout.core.protection import ConservativeProtectionLayer
from turnitout.core.modifier import DocumentModifier
from turnitout.config import ConfigNamespace


@pytest.fixture
def modifier():
    cfg = ConfigNamespace()
    # Enable safe stages
    cfg.ENABLE_PHRASE_REWRITE = True
    cfg.ENABLE_SYNONYMS = True
    cfg.ENABLE_DETERMINER_SWAP = True
    cfg.ENABLE_DISCOURSE_ROTATE = True
    return DocumentModifier(config=cfg, seed=42)


def test_nested_multiline_latex_protection(modifier):
    """Verify that complex nested and multiline LaTeX environments are strictly preserved."""
    raw_latex = (
        r"\begin{equation}" + "\n"
        r"  \frac{\partial^2 \psi}{\partial x^2} + \frac{8\pi^2 m}{h^2}(E - V)\psi = 0" + "\n"
        r"\end{equation}"
    )
    result = modifier.modify_document(raw_latex)
    assert raw_latex == result or r"\frac{\partial^2 \psi}{\partial x^2}" in result
    assert r"\begin{equation}" in result
    assert r"\end{equation}" in result


def test_fractions_integrals_and_matrices(modifier):
    """Verify mathematical operators, integrals, and fractions remain untampered."""
    math_text = (
        r"The normal distribution integral evaluates to "
        r"$\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}$, "
        r"which conforms to the fraction $\frac{1}{\sqrt{2\pi}\sigma}$."
    )
    result = modifier.modify_document(math_text)
    assert r"\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}" in result
    assert r"\frac{1}{\sqrt{2\pi}\sigma}" in result


def test_numerical_quantities_and_physical_units(modifier):
    """Verify numerical values, currencies, percentages, and units are preserved."""
    quantities_text = (
        "The server latency decreased to 3.8 ms while processing 120 queries per second. "
        "The intervention generated $4.5 million in revenue with a 14.8% margin at 25 °C."
    )
    result = modifier.modify_document(quantities_text)
    assert "3.8 ms" in result
    assert "120 queries per second" in result
    assert "$4.5 million" in result
    assert "14.8%" in result
    assert "25 °C" in result


def test_p_values_and_confidence_intervals(modifier):
    """Verify statistical significance indicators and confidence intervals are intact."""
    stats_text = (
        "The treatment effect was statistically significant with p < 0.001 and t = 2.45. "
        "The observed risk ratio was 1.34 with a 95% confidence interval [1.12, 1.61]."
    )
    result = modifier.modify_document(stats_text)
    assert "p < 0.001" in result
    assert "95% confidence interval" in result


def test_citation_markers_integrity(modifier):
    """Verify IEEE and APA in-text citation markers are not split or corrupted."""
    cite_text = (
        "Modern deep neural architectures rely on transformer mechanisms (Vaswani et al., 2017). "
        "Prior findings also confirmed algorithmic convergence [1, 2]."
    )
    result = modifier.modify_document(cite_text)
    assert "(Vaswani et al., 2017)" in result
    assert "[1, 2]" in result


def test_multi_word_technical_units_mwu(modifier):
    """Verify that multi-word compound technical terms are never split or corrupted."""
    mwu_text = (
        "The learning rate was optimized during stochastic gradient descent. "
        "Distributed consensus protocols prevent Byzantine failures in deep learning."
    )
    result = modifier.modify_document(mwu_text)
    assert "learning rate" in result
    assert "stochastic gradient descent" in result
    assert "distributed consensus" in result.lower()
    assert "deep learning" in result
    assert "broadly learning rate" not in result


def test_research_proposal_structural_headings(modifier):
    """Verify that research questions, hypotheses, and structured headings are never fused."""
    proposal_text = (
        "1. Problem Statement: Transformer models exhibit high memory complexity.\n\n"
        "RQ1: Does parameter pruning reduce memory consumption?\n\n"
        "H1: Quantization maintains accuracy within 2% margin."
    )
    result = modifier.modify_document(proposal_text)
    assert "1. Problem Statement:" in result
    assert "RQ1:" in result
    assert "H1:" in result
    assert ", which consequently RQ1:" not in result


def test_fail_closed_rollback_on_tampering():
    """Verify that if placeholder validation fails, the layer rolls back safely to original text."""
    layer = ConservativeProtectionLayer()
    original = "The equation $E = mc^2$ governs energy equivalence."
    protected, count = layer.protect(original)
    
    # Simulate destructive downstream mutation corrupting the placeholder
    corrupted = protected.replace("PROT_INL", "DAMAGED")
    restored, ok = layer.restore(corrupted, original_raw_text=original)
    
    assert ok is False
    assert restored == original
