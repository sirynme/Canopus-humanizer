"""Unit tests for Decision Engine, critical failure vetoes, and end-to-end pipeline."""

import pytest
from benchmark.dataset.generator import BenchmarkDatasetGenerator
from benchmark.pipeline.runner import BenchmarkPipelineRunner
from benchmark.scoring.decision_engine import BenchmarkDecisionEngine, ScoringThresholds


def test_decision_engine_critical_veto():
    engine = BenchmarkDecisionEngine()

    # Lang: 95, Sem: 95, Acad: 95, Rel: 95, BUT Factual has critical failure
    lang_eval = {"score": 95.0, "syntax_issues": []}
    sem_eval = {"score": 95.0, "critical_failure": False}
    fact_eval = {"score": 30.0, "critical_failure": True, "fact_corruption_detected": True, "invented_numbers": []}
    acad_eval = {"score": 95.0, "critical_failure": False}
    rel_eval = {"score": 100.0, "execution_success": True, "critical_failure": False}

    verdict = engine.evaluate_case(lang_eval, sem_eval, fact_eval, acad_eval, rel_eval)
    # INVARIANT: Critical failure MUST trigger FAIL verdict
    assert verdict.verdict == "FAIL"
    assert "Critical factual integrity violation" in verdict.critical_failures


def test_decision_engine_pass():
    engine = BenchmarkDecisionEngine()

    lang_eval = {"score": 85.0, "syntax_issues": []}
    sem_eval = {"score": 88.0, "critical_failure": False}
    fact_eval = {"score": 95.0, "critical_failure": False, "fact_corruption_detected": False, "invented_numbers": []}
    acad_eval = {"score": 85.0, "critical_failure": False}
    rel_eval = {"score": 98.0, "execution_success": True, "critical_failure": False}

    verdict = engine.evaluate_case(lang_eval, sem_eval, fact_eval, acad_eval, rel_eval)
    assert verdict.verdict == "PASS"


def test_pipeline_smoke_run(tmp_path):
    generator = BenchmarkDatasetGenerator(seed=42)
    # Run 1 test case per level = 5 test cases
    cases = generator.generate_suite(count_per_level=1)

    runner = BenchmarkPipelineRunner()
    run_data = runner.run_suite(cases=cases, run_name="SMOKE_TEST")

    assert run_data["summary"]["total_cases"] == 5
    assert len(run_data["cases"]) == 5
    for item in run_data["cases"]:
        assert "verdict" in item
        assert item["verdict"]["verdict"] in ("PASS", "CONDITIONAL", "FAIL")
        assert "evaluations" in item
