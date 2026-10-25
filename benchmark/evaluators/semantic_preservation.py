"""Evaluation Module B: Semantic Preservation.

Measures whether the humanized text preserves core arguments, named entities,
numerical quantities, dates, units, negation polarity, and technical terminology.
"""

import collections
import math
import re
from typing import Any, Dict, List, Set, Tuple


class SemanticPreservationEvaluator:
    """Evaluates semantic fidelity, entity recall, numerical integrity, and negation polarity."""

    @staticmethod
    def _extract_tokens(text: str) -> List[str]:
        return [w.lower() for w in re.findall(r"\b[a-zA-Z0-9']+\b", text)]

    @classmethod
    def calculate_jaccard_similarity(cls, text_a: str, text_b: str) -> float:
        """Calculates token-level Jaccard similarity."""
        set_a = set(cls._extract_tokens(text_a))
        set_b = set(cls._extract_tokens(text_b))
        if not set_a or not set_b:
            return 0.0
        intersection = set_a & set_b
        union = set_a | set_b
        return round((len(intersection) / len(union)) * 100.0, 2)

    @classmethod
    def calculate_cosine_tfidf(cls, text_a: str, text_b: str) -> float:
        """Calculates bag-of-words cosine similarity between two texts."""
        tokens_a = cls._extract_tokens(text_a)
        tokens_b = cls._extract_tokens(text_b)
        if not tokens_a or not tokens_b:
            return 0.0

        vec_a = collections.Counter(tokens_a)
        vec_b = collections.Counter(tokens_b)

        all_keys = set(vec_a.keys()) | set(vec_b.keys())
        dot_product = sum(vec_a.get(k, 0) * vec_b.get(k, 0) for k in all_keys)
        mag_a = math.sqrt(sum(v ** 2 for v in vec_a.values()))
        mag_b = math.sqrt(sum(v ** 2 for v in vec_b.values()))

        if mag_a == 0 or mag_b == 0:
            return 0.0
        cosine = dot_product / (mag_a * mag_b)
        return round(cosine * 100.0, 2)

    @staticmethod
    def audit_entity_preservation(expected_entities: List[str], humanized_text: str) -> Dict[str, Any]:
        """Checks whether named entities and technical acronyms were preserved."""
        if not expected_entities:
            return {"entity_recall": 100.0, "preserved": [], "missing": []}

        preserved = []
        missing = []
        for ent in expected_entities:
            # Case-insensitive substring or word boundary match
            if re.search(rf"\b{re.escape(ent)}\b", humanized_text, flags=re.IGNORECASE):
                preserved.append(ent)
            else:
                missing.append(ent)

        recall = (len(preserved) / len(expected_entities)) * 100.0 if expected_entities else 100.0
        return {
            "entity_recall": round(recall, 1),
            "preserved": preserved,
            "missing": missing
        }

    @staticmethod
    def audit_numerical_preservation(expected_numbers: List[str], humanized_text: str) -> Dict[str, Any]:
        """Strictly audits numerical values, percentages, currencies, and metrics."""
        if not expected_numbers:
            return {"number_recall": 100.0, "preserved": [], "missing": [], "critical_loss": False}

        preserved = []
        missing = []
        for num in expected_numbers:
            # Match number exactly, allowing trailing sentence/list period punctuation while forbidding decimal digits
            if re.search(rf"(?<![\d.]){re.escape(num)}(?![\d]|\.\d)", humanized_text):
                preserved.append(num)
            else:
                missing.append(num)

        recall = (len(preserved) / len(expected_numbers)) * 100.0 if expected_numbers else 100.0
        critical_loss = len(missing) > 0

        return {
            "number_recall": round(recall, 1),
            "preserved": preserved,
            "missing": missing,
            "critical_loss": critical_loss
        }

    @staticmethod
    def audit_negation_polarity(expected_negations: List[str], humanized_text: str) -> Dict[str, Any]:
        """Verifies that truth-functional negation words were not dropped."""
        if not expected_negations:
            return {"negation_recall": 100.0, "preserved": [], "missing": [], "critical_loss": False}

        preserved = []
        missing = []
        for neg in expected_negations:
            if re.search(rf"\b{re.escape(neg)}\b", humanized_text, flags=re.IGNORECASE):
                preserved.append(neg)
            else:
                missing.append(neg)

        recall = (len(preserved) / len(expected_negations)) * 100.0 if expected_negations else 100.0
        critical_loss = len(missing) > 0

        return {
            "negation_recall": round(recall, 1),
            "preserved": preserved,
            "missing": missing,
            "critical_loss": critical_loss
        }

    @classmethod
    def evaluate(
        cls,
        original_text: str,
        humanized_text: str,
        expected_entities: List[str],
        expected_numbers: List[str],
        expected_negations: List[str]
    ) -> Dict[str, Any]:
        """Executes full semantic evaluation and calculates semantic preservation score (0-100)."""
        jaccard = cls.calculate_jaccard_similarity(original_text, humanized_text)
        cosine = cls.calculate_cosine_tfidf(original_text, humanized_text)

        ent_audit = cls.audit_entity_preservation(expected_entities, humanized_text)
        num_audit = cls.audit_numerical_preservation(expected_numbers, humanized_text)
        neg_audit = cls.audit_negation_polarity(expected_negations, humanized_text)

        # Base semantic score computed from component recalls
        # Cosine weight: 30%, Entity: 30%, Number: 25%, Negation: 15%
        score = (
            (cosine * 0.30) +
            (ent_audit["entity_recall"] * 0.30) +
            (num_audit["number_recall"] * 0.25) +
            (neg_audit["negation_recall"] * 0.15)
        )

        critical_failure = False
        critical_reasons = []

        if num_audit["critical_loss"]:
            critical_failure = True
            critical_reasons.append(f"Critical numerical loss: {num_audit['missing']}")
            score = min(score, 45.0)

        if neg_audit["critical_loss"]:
            critical_failure = True
            critical_reasons.append(f"Critical negation inversion: {neg_audit['missing']}")
            score = min(score, 35.0)

        final_score = round(max(0.0, min(100.0, score)), 1)

        return {
            "score": final_score,
            "cosine_similarity": cosine,
            "jaccard_similarity": jaccard,
            "entity_preservation": ent_audit,
            "numerical_preservation": num_audit,
            "negation_preservation": neg_audit,
            "critical_failure": critical_failure,
            "critical_reasons": critical_reasons
        }
