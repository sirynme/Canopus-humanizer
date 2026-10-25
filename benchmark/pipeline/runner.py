"""Benchmark Pipeline Runner Orchestrator.

Coordinates dataset generation, execution through the humanizer client,
multi-dimensional evaluation, critical failure scoring, repeated-run consistency,
and persistent result logging.
"""

from datetime import datetime
import time
from typing import Any, Dict, List, Optional

from benchmark.dataset.generator import BenchmarkCase, BenchmarkDatasetGenerator
from benchmark.evaluators.language_quality import LanguageQualityEvaluator
from benchmark.evaluators.semantic_preservation import SemanticPreservationEvaluator
from benchmark.evaluators.factual_integrity import FactualIntegrityEvaluator
from benchmark.evaluators.academic_quality import AcademicQualityEvaluator
from benchmark.evaluators.detector_adapter import AIDetectorEvaluator
from benchmark.evaluators.operational_reliability import OperationalReliabilityEvaluator
from benchmark.pipeline.client import HumanizerClient
from benchmark.pipeline.persistence import BenchmarkPersistence
from benchmark.scoring.decision_engine import BenchmarkDecisionEngine, DecisionVerdict


class BenchmarkPipelineRunner:
    """End-to-end benchmark execution and evaluation orchestrator."""

    def __init__(
        self,
        client: Optional[HumanizerClient] = None,
        persistence: Optional[BenchmarkPersistence] = None,
        decision_engine: Optional[BenchmarkDecisionEngine] = None
    ):
        self.client = client or HumanizerClient()
        self.persistence = persistence or BenchmarkPersistence()
        self.decision_engine = decision_engine or BenchmarkDecisionEngine()
        self.detector_evaluator = AIDetectorEvaluator()

    def run_single_case(self, case: BenchmarkCase, repeat_consistency: bool = False) -> Dict[str, Any]:
        """Executes before-and-after evaluation on a single benchmark test case."""
        # 1. Transform text via client
        transform_res = self.client.transform(
            text=case.original_text,
            seed=42,
            style=case.formality if case.formality in ("academic", "technical", "conversational") else "academic",
            enable_citations=bool(case.expected_citations),
            max_citations=len(case.expected_citations)
        )

        humanized_text = transform_res.get("humanized_text", "")
        latency_ms = transform_res.get("latency_ms", 0.0)
        success = transform_res.get("success", False)
        error = transform_res.get("error")

        # 2. Run Module A: Language Quality
        lang_eval = LanguageQualityEvaluator.evaluate(case.original_text, humanized_text)

        # 3. Run Module B: Semantic Preservation
        sem_eval = SemanticPreservationEvaluator.evaluate(
            original_text=case.original_text,
            humanized_text=humanized_text,
            expected_entities=case.expected_entities,
            expected_numbers=case.expected_numbers,
            expected_negations=case.expected_negations
        )

        # 4. Run Module C: Factual Integrity
        fact_eval = FactualIntegrityEvaluator.evaluate(
            original_text=case.original_text,
            humanized_text=humanized_text,
            expected_facts=case.expected_facts,
            is_verified_fact=case.is_verified_fact
        )

        # 5. Run Module D: Academic Quality
        acad_eval = AcademicQualityEvaluator.evaluate(
            original_text=case.original_text,
            humanized_text=humanized_text,
            expected_citations=case.expected_citations,
            academic_elements=case.academic_elements
        )

        # 6. Run Module E: AI Detector Evasion
        det_eval = self.detector_evaluator.evaluate_pair(case.original_text, humanized_text)

        # 7. Run Module F: Operational Reliability
        rel_eval = OperationalReliabilityEvaluator.evaluate(
            original_text=case.original_text,
            humanized_text=humanized_text,
            latency_ms=latency_ms,
            execution_success=success,
            error_message=error
        )

        # 8. Repeated-Run Consistency Verification
        consistency_report = None
        if repeat_consistency and success:
            run2 = self.client.transform(text=case.original_text, seed=42)
            run3 = self.client.transform(text=case.original_text, seed=42)
            is_identical = (run2.get("humanized_text") == humanized_text == run3.get("humanized_text"))
            consistency_report = {
                "deterministic_equality": is_identical,
                "trials": 3,
                "all_runs_matched": is_identical
            }

        # 9. Scoring and Decision Rendering
        verdict: DecisionVerdict = self.decision_engine.evaluate_case(
            lang_eval=lang_eval,
            sem_eval=sem_eval,
            fact_eval=fact_eval,
            acad_eval=acad_eval,
            rel_eval=rel_eval,
            det_eval=det_eval
        )

        return {
            "test_id": case.id,
            "case": case.to_dict(),
            "original_text": case.original_text,
            "humanized_text": humanized_text,
            "latency_ms": latency_ms,
            "success": success,
            "error": error,
            "evaluations": {
                "language_quality": lang_eval,
                "semantic_preservation": sem_eval,
                "factual_integrity": fact_eval,
                "academic_quality": acad_eval,
                "detector_evasion": det_eval,
                "operational_reliability": rel_eval
            },
            "consistency": consistency_report,
            "verdict": verdict.to_dict()
        }

    def run_suite(
        self,
        cases: List[BenchmarkCase],
        run_name: Optional[str] = None,
        repeat_sample_rate: float = 0.20
    ) -> Dict[str, Any]:
        """Runs the entire benchmark suite and persists structured results."""
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_id = f"RUN_{run_name or 'STANDARD'}_{timestamp_str}"

        results: List[Dict[str, Any]] = []
        for i, case in enumerate(cases):
            # Check repeated consistency on selected cases
            should_repeat = (i % int(1.0 / max(0.01, repeat_sample_rate)) == 0)
            res = self.run_single_case(case, repeat_consistency=should_repeat)
            results.append(res)

        metadata = {
            "run_id": run_id,
            "date": datetime.now().isoformat(),
            "client_channel": "REST_API" if self.client.use_rest_api else "DIRECT_LIBRARY",
            "model_version": "Core 2.6.0 (Deterministic 17-Stage)",
            "total_cases": len(cases),
            "repeat_sample_rate": repeat_sample_rate
        }

        json_path = self.persistence.save_run(run_id=run_id, run_metadata=metadata, results=results)

        # Summary calculations
        passed = sum(1 for r in results if r["verdict"]["verdict"] == "PASS")
        conditional = sum(1 for r in results if r["verdict"]["verdict"] == "CONDITIONAL")
        failed = sum(1 for r in results if r["verdict"]["verdict"] == "FAIL")

        return {
            "run_id": run_id,
            "json_path": str(json_path),
            "metadata": metadata,
            "summary": {
                "total_cases": len(cases),
                "passed": passed,
                "conditional": conditional,
                "failed": failed,
                "pass_rate": round((passed / len(cases)) * 100.0, 1) if cases else 0.0,
                "conditional_rate": round((conditional / len(cases)) * 100.0, 1) if cases else 0.0,
                "fail_rate": round((failed / len(cases)) * 100.0, 1) if cases else 0.0,
                "avg_composite_score": round(sum(r["verdict"]["composite_score"] for r in results) / max(1, len(results)), 1),
                "avg_latency_ms": round(sum(r["latency_ms"] for r in results) / max(1, len(results)), 2)
            },
            "cases": results
        }
