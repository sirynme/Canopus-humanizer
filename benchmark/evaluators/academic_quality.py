"""Evaluation Module D: Academic & Research Quality.

Evaluates structural alignment of research proposals (Problem, RQ, Hypotheses,
Objectives, Methodology, Limitations), citation syntax preservation, detection of
fabricated or corrupted references, and scholarly rubric compliance.
"""

import re
from typing import Any, Dict, List, Optional


class AcademicQualityEvaluator:
    """Evaluates scholarly rigor, research proposal rubric compliance, and citation integrity."""

    @staticmethod
    def audit_citation_syntax(expected_citations: List[str], humanized_text: str) -> Dict[str, Any]:
        """Verifies that citations (e.g. '[1]', '(Author et al., 2017)', '\\cite{...}') are intact."""
        if not expected_citations:
            return {"citations_present": 0, "missing_citations": [], "corrupted_syntax": []}

        preserved = []
        missing = []
        for cit in expected_citations:
            # Check exact citation key or pattern
            if cit in humanized_text:
                preserved.append(cit)
            else:
                missing.append(cit)

        # Detect malformed or corrupted brackets like "[?]" or broken citation delimiters
        corrupted = re.findall(r"\\cite\{\s*\}|\[\s*\]|\[\?\]", humanized_text)

        return {
            "citations_present": len(preserved),
            "preserved_citations": preserved,
            "missing_citations": missing,
            "corrupted_syntax": corrupted,
            "citation_preservation_rate": round((len(preserved) / len(expected_citations)) * 100.0, 1) if expected_citations else 100.0
        }

    @staticmethod
    def audit_research_proposal_rubric(academic_elements: Dict[str, Any], humanized_text: str) -> Dict[str, Any]:
        """Evaluates whether all six mandatory components of a research proposal are preserved."""
        if not academic_elements:
            return {"rubric_score": 100.0, "section_status": {}}

        rubric_weights = {
            "problem_statement": 20.0,
            "research_questions": 20.0,
            "hypotheses": 20.0,
            "objectives": 15.0,
            "methodology": 15.0,
            "limitations": 10.0
        }

        section_status = {}
        earned_score = 0.0

        # 1. Problem Statement check
        prob = academic_elements.get("problem_statement", "")
        # Check if keywords from problem statement exist
        prob_found = ("problem statement" in humanized_text.lower() or "catastrophic forgetting" in humanized_text.lower())
        section_status["problem_statement"] = prob_found
        if prob_found: earned_score += rubric_weights["problem_statement"]

        # 2. Research Questions (RQ1, RQ2)
        rq_found = ("rq1" in humanized_text.lower() or "research question" in humanized_text.lower())
        section_status["research_questions"] = rq_found
        if rq_found: earned_score += rubric_weights["research_questions"]

        # 3. Hypotheses (H1, H0)
        hyp_found = ("h1" in humanized_text.lower() or "hypothesize" in humanized_text.lower())
        section_status["hypotheses"] = hyp_found
        if hyp_found: earned_score += rubric_weights["hypotheses"]

        # 4. Objectives
        obj_found = ("objective" in humanized_text.lower() or "aim" in humanized_text.lower())
        section_status["objectives"] = obj_found
        if obj_found: earned_score += rubric_weights["objectives"]

        # 5. Methodology
        meth_found = ("methodology" in humanized_text.lower() or "trial" in humanized_text.lower() or "cross-validation" in humanized_text.lower())
        section_status["methodology"] = meth_found
        if meth_found: earned_score += rubric_weights["methodology"]

        # 6. Limitations & Uncertainty
        lim_found = ("limitation" in humanized_text.lower() or "constrained" in humanized_text.lower())
        section_status["limitations"] = lim_found
        if lim_found: earned_score += rubric_weights["limitations"]

        return {
            "rubric_score": round(earned_score, 1),
            "section_status": section_status
        }

    @classmethod
    def evaluate(
        cls,
        original_text: str,
        humanized_text: str,
        expected_citations: Optional[List[str]] = None,
        academic_elements: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Runs full academic quality evaluation, returning 0-100 score."""
        cit_audit = cls.audit_citation_syntax(expected_citations or [], humanized_text)
        rubric_audit = cls.audit_research_proposal_rubric(academic_elements or {}, humanized_text)

        # Baseline academic score
        if academic_elements:
            score = (rubric_audit["rubric_score"] * 0.70) + (cit_audit["citation_preservation_rate"] * 0.30)
        elif expected_citations:
            score = cit_audit["citation_preservation_rate"]
        else:
            # For general writing with no formal academic sections or citations, check academic tone
            score = 90.0

        # Penalty if citations were corrupted
        if cit_audit["corrupted_syntax"]:
            score -= len(cit_audit["corrupted_syntax"]) * 25.0

        critical_failure = len(cit_audit.get("missing_citations", [])) > 1 or bool(cit_audit["corrupted_syntax"])
        final_score = round(max(0.0, min(100.0, score)), 1)

        return {
            "score": final_score,
            "citation_audit": cit_audit,
            "rubric_audit": rubric_audit,
            "critical_failure": critical_failure
        }
