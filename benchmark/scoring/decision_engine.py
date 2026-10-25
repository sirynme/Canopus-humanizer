"""Scoring and Decision Engine with Critical Failure Vetoes.

Produces independent 0-100 scores across six evaluation dimensions and renders
strict PASS, CONDITIONAL, or FAIL verdicts. Critical factual, semantic, or citation
defects trigger non-negotiable FAIL verdicts regardless of high scores elsewhere.
"""

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ScoringThresholds:
    """Configurable acceptance thresholds for benchmark decision rendering."""
    min_language_quality: float = 70.0
    min_semantic_preservation: float = 75.0
    min_factual_integrity: float = 80.0
    min_academic_quality: float = 70.0
    min_operational_reliability: float = 90.0
    min_detector_score: float = 60.0  # Optional detector threshold


@dataclass
class DecisionVerdict:
    """Represents the multi-dimensional evaluation verdict for a test document."""
    verdict: str  # "PASS", "CONDITIONAL", or "FAIL"
    composite_score: float
    component_scores: Dict[str, Optional[float]]
    critical_failures: List[str]
    failed_checks: List[str]
    warnings: List[str]
    reasons: List[str]
    supporting_evidence: Dict[str, Any]
    uncertainties: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class BenchmarkDecisionEngine:
    """Evaluates multi-dimensional module scores and enforces critical veto rules."""

    def __init__(self, thresholds: Optional[ScoringThresholds] = None):
        self.thresholds = thresholds or ScoringThresholds()

    def evaluate_case(
        self,
        lang_eval: Dict[str, Any],
        sem_eval: Dict[str, Any],
        fact_eval: Dict[str, Any],
        acad_eval: Dict[str, Any],
        rel_eval: Dict[str, Any],
        det_eval: Optional[Dict[str, Any]] = None
    ) -> DecisionVerdict:
        """Evaluates results from all modules and renders an uncompromised verdict."""
        # 1. Collect Scores
        s_lang = lang_eval.get("score", 0.0)
        s_sem = sem_eval.get("score", 0.0)
        s_fact = fact_eval.get("score", 0.0)
        s_acad = acad_eval.get("score", 0.0)
        s_rel = rel_eval.get("score", 0.0)
        s_det = det_eval.get("score") if det_eval else None

        component_scores = {
            "language_quality": s_lang,
            "semantic_preservation": s_sem,
            "factual_integrity": s_fact,
            "academic_quality": s_acad,
            "operational_reliability": s_rel,
            "detector_evasion": s_det
        }

        # 2. Weighted Composite (For statistical tracking only - NEVER overrides vetoes)
        weights = {"lang": 0.20, "sem": 0.25, "fact": 0.25, "acad": 0.15, "rel": 0.15}
        composite = (
            (s_lang * weights["lang"]) +
            (s_sem * weights["sem"]) +
            (s_fact * weights["fact"]) +
            (s_acad * weights["acad"]) +
            (s_rel * weights["rel"])
        )
        composite = round(composite, 1)

        # 3. Critical Failure Veto Audit
        critical_failures: List[str] = []
        failed_checks: List[str] = []
        warnings: List[str] = []
        reasons: List[str] = []
        evidence: Dict[str, Any] = {}
        uncertainties: List[str] = []

        # Policy Rule 1: Infrastructure or Execution Failure
        if not rel_eval.get("execution_success", True):
            critical_failures.append("Execution error or timeout")
            reasons.append(f"Pipeline crashed with error: {rel_eval.get('error_message')}")

        if rel_eval.get("critical_failure"):
            critical_failures.append("Operational anomaly (length collapse, runaway expansion, or leaked tokens)")
            reasons.append(f"Operational anomaly detected: {rel_eval.get('syntax_leaks')} {rel_eval.get('length_audit', {}).get('reasons')}")
            evidence["operational_anomalies"] = rel_eval.get("syntax_leaks")

        # Policy Rule 2: Critical Factual Change
        if fact_eval.get("critical_failure"):
            critical_failures.append("Critical factual integrity violation")
            if fact_eval.get("fact_corruption_detected"):
                reasons.append("Ground-truth verified reference facts were corrupted or altered.")
            if fact_eval.get("invented_numbers"):
                reasons.append(f"Newly introduced/hallucinated numerical values detected: {fact_eval.get('invented_numbers')}")
            evidence["factual_violations"] = fact_eval.get("reference_verifications")

        # Policy Rule 3: Critical Meaning / Negation / Numerical Loss
        if sem_eval.get("critical_failure"):
            critical_failures.append("Critical semantic preservation violation")
            reasons.extend(sem_eval.get("critical_reasons", []))
            evidence["semantic_violations"] = {
                "missing_numbers": sem_eval.get("numerical_preservation", {}).get("missing"),
                "missing_negations": sem_eval.get("negation_preservation", {}).get("missing")
            }

        # Policy Rule 4: Materially Corrupted or Fabricated Citations
        if acad_eval.get("critical_failure"):
            critical_failures.append("Critical academic citation violation")
            cit_audit = acad_eval.get("citation_audit", {})
            reasons.append(f"Missing or corrupted scholarly citations: {cit_audit.get('missing_citations')} {cit_audit.get('corrupted_syntax')}")
            evidence["citation_violations"] = cit_audit

        # 4. Threshold & Quality Regression Checks
        if s_lang < self.thresholds.min_language_quality:
            failed_checks.append(f"Language Quality score ({s_lang}) fell below threshold ({self.thresholds.min_language_quality})")
        if s_sem < self.thresholds.min_semantic_preservation:
            failed_checks.append(f"Semantic Preservation score ({s_sem}) fell below threshold ({self.thresholds.min_semantic_preservation})")
        if s_fact < self.thresholds.min_factual_integrity:
            failed_checks.append(f"Factual Integrity score ({s_fact}) fell below threshold ({self.thresholds.min_factual_integrity})")
        if s_acad < self.thresholds.min_academic_quality:
            failed_checks.append(f"Academic Quality score ({s_acad}) fell below threshold ({self.thresholds.min_academic_quality})")
        if s_rel < self.thresholds.min_operational_reliability:
            failed_checks.append(f"Operational Reliability score ({s_rel}) fell below threshold ({self.thresholds.min_operational_reliability})")

        # Warnings & Uncertainties
        syntax_issues = lang_eval.get("syntax_issues", [])
        if syntax_issues:
            warnings.append(f"{len(syntax_issues)} syntax/grammar anomaly warnings flagged")
            evidence["syntax_warnings"] = syntax_issues

        if not fact_eval.get("is_verified_ground_truth"):
            uncertainties.append("Non-reference facts evaluated via lexical heuristic; human domain expert review recommended for nuanced claims.")

        # 5. Render Final Verdict (Invariant: Critical failures VETO everything)
        if critical_failures:
            verdict = "FAIL"
        elif failed_checks:
            verdict = "CONDITIONAL"
            reasons.append("Document passed critical safety checks but triggered quality threshold warnings requiring human review.")
        else:
            verdict = "PASS"
            reasons.append("Document satisfied all semantic, factual, academic, and reliability criteria without regressions.")

        return DecisionVerdict(
            verdict=verdict,
            composite_score=composite,
            component_scores=component_scores,
            critical_failures=critical_failures,
            failed_checks=failed_checks,
            warnings=warnings,
            reasons=reasons,
            supporting_evidence=evidence,
            uncertainties=uncertainties
        )
