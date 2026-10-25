"""Unit tests for Evaluation Modules A through F."""

import pytest
from benchmark.evaluators.language_quality import LanguageQualityEvaluator
from benchmark.evaluators.semantic_preservation import SemanticPreservationEvaluator
from benchmark.evaluators.factual_integrity import FactualIntegrityEvaluator
from benchmark.evaluators.academic_quality import AcademicQualityEvaluator
from benchmark.evaluators.detector_adapter import AIDetectorEvaluator, ZipPyDetectorAdapter
from benchmark.evaluators.operational_reliability import OperationalReliabilityEvaluator


def test_language_quality_evaluator():
    orig = "The experiment was conducted by researchers in 2023. The data was clean and clear."
    human = "Researchers conducted the experiment in 2023. The data was evidently clean and transparent."

    res = LanguageQualityEvaluator.evaluate(orig, human)
    assert 0.0 <= res["score"] <= 100.0
    assert "readability" in res
    assert "sentence_variety" in res
    assert "lexical_diversity" in res


def test_semantic_preservation_numerical_loss():
    orig = "We onboarded 45 new clients and revenue grew by 18.5%."
    # Humanized text drops the percentage 18.5%
    corrupted = "We onboarded 45 new clients and revenue grew significantly."

    res = SemanticPreservationEvaluator.evaluate(
        original_text=orig,
        humanized_text=corrupted,
        expected_entities=["clients"],
        expected_numbers=["45", "18.5%"],
        expected_negations=[]
    )
    assert res["critical_failure"] is True
    assert "18.5%" in res["numerical_preservation"]["missing"]


def test_semantic_preservation_negation_inversion():
    orig = "The algorithm does not converge when the rate is above 0.1."
    # Corrupted text drops "not"
    inverted = "The algorithm converges when the rate is above 0.1."

    res = SemanticPreservationEvaluator.evaluate(
        original_text=orig,
        humanized_text=inverted,
        expected_entities=["algorithm"],
        expected_numbers=["0.1"],
        expected_negations=["not"]
    )
    assert res["critical_failure"] is True
    assert "not" in res["negation_preservation"]["missing"]


def test_factual_integrity_invented_number():
    orig = "The model was trained on ImageNet."
    # Humanized text invents a number
    human = "The model was trained on 42 ImageNet clusters."

    res = FactualIntegrityEvaluator.evaluate(orig, human)
    assert "42" in res["invented_numbers"]


def test_academic_quality_citations():
    orig = "Self-attention models were introduced by Vaswani et al. (Vaswani et al., 2017)."
    human = "Self-attention models were introduced by Vaswani et al. (Vaswani et al., 2017)."

    res = AcademicQualityEvaluator.evaluate(orig, human, expected_citations=["(Vaswani et al., 2017)"])
    assert res["critical_failure"] is False
    assert res["citation_audit"]["citations_present"] == 1


def test_operational_reliability_latency_and_empty():
    orig = "Sample input text"
    empty = ""

    res_empty = OperationalReliabilityEvaluator.evaluate(orig, empty, latency_ms=15.0)
    assert res_empty["critical_failure"] is True
    assert res_empty["length_audit"]["anomaly_detected"] is True

    valid = "Sample modified output text"
    res_valid = OperationalReliabilityEvaluator.evaluate(orig, valid, latency_ms=8.5)
    assert res_valid["critical_failure"] is False
    assert res_valid["score"] >= 90.0


def test_ai_detector_adapter():
    evaluator = AIDetectorEvaluator(adapter=ZipPyDetectorAdapter())
    orig = "Furthermore, it is important to delve into the comprehensive tapestry of modern neural networks."
    human = "Neural networks represent complex layered architectures requiring systematic optimization."

    res = evaluator.evaluate_pair(orig, human)
    assert res["detector_id"] == "ZipPy-LocalEntropy-v2.6"
    assert "ai_probability_before" in res
    assert "ai_probability_after" in res
