"""Evaluation Module C: Factual Integrity.

Audits factual claims against the source document and verified reference material.
Detects newly introduced numbers, fabricated entities, or corrupted empirical data.
"""

import re
from typing import Any, Dict, List, Optional


class FactualIntegrityEvaluator:
    """Verifies that factual claims, historical dates, and numerical constants remain uncorrupted."""

    @staticmethod
    def _extract_all_numbers(text: str) -> List[str]:
        """Extracts all numerical tokens from text."""
        return re.findall(r"\b\d+(?:,\d{3})*(?:\.\d+)?%?\b", text)

    @classmethod
    def audit_numerical_inventions(cls, original_text: str, humanized_text: str) -> List[str]:
        """Detects numbers present in humanized text that did not exist in original text."""
        orig_nums = set(cls._extract_all_numbers(original_text))
        human_nums = set(cls._extract_all_numbers(humanized_text))
        # Novel numbers introduced by the pipeline
        invented = list(human_nums - orig_nums)
        return invented

    @classmethod
    def verify_ground_truth_reference(cls, ref_fact: Dict[str, Any], humanized_text: str) -> Dict[str, Any]:
        """Verifies whether a known verified real-world reference fact was preserved intact."""
        claim_preserved = True
        missing_components = []

        # Check required entities
        for ent in ref_fact.get("entities", []):
            if not re.search(rf"\b{re.escape(ent)}\b", humanized_text, flags=re.IGNORECASE):
                claim_preserved = False
                missing_components.append(f"Missing entity: {ent}")

        # Check required numbers
        for num in ref_fact.get("numbers", []):
            if not re.search(rf"(?<![\d.]){re.escape(num)}(?!\w)", humanized_text):
                claim_preserved = False
                missing_components.append(f"Missing number: {num}")

        return {
            "fact_id": ref_fact.get("id"),
            "source": ref_fact.get("verified_source"),
            "preserved": claim_preserved,
            "missing_components": missing_components
        }

    @classmethod
    def evaluate(
        cls,
        original_text: str,
        humanized_text: str,
        expected_facts: Optional[List[Dict[str, Any]]] = None,
        is_verified_fact: bool = False
    ) -> Dict[str, Any]:
        """Runs factual integrity check, returning 0-100 score and critical failure flags."""
        invented_nums = cls.audit_numerical_inventions(original_text, humanized_text)
        
        ref_results = []
        fact_corruption_detected = False

        if expected_facts:
            for fact in expected_facts:
                res = cls.verify_ground_truth_reference(fact, humanized_text)
                ref_results.append(res)
                if not res["preserved"]:
                    fact_corruption_detected = True

        # Base factual integrity score
        score = 100.0

        # Penalize invented numbers (hallucinated data)
        if invented_nums:
            score -= len(invented_nums) * 20.0

        # Critical penalty if verified ground truth reference was corrupted
        if is_verified_fact and fact_corruption_detected:
            score = min(score, 30.0)

        critical_failure = (is_verified_fact and fact_corruption_detected) or (len(invented_nums) > 1)
        final_score = round(max(0.0, min(100.0, score)), 1)

        return {
            "score": final_score,
            "invented_numbers": invented_nums,
            "reference_verifications": ref_results,
            "fact_corruption_detected": fact_corruption_detected,
            "critical_failure": critical_failure,
            "is_verified_ground_truth": is_verified_fact
        }
