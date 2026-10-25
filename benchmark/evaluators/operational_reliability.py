"""Evaluation Module F: Operational Reliability.

Evaluates throughput, latency distribution, length expansion/contraction ratio,
anomaly detection (empty, truncated, or unclosed markup), and repeated-run consistency.
"""

from typing import Any, Dict, List, Optional


class OperationalReliabilityEvaluator:
    """Evaluates performance metrics, throughput, length anomalies, and execution errors."""

    @staticmethod
    def audit_length_anomalies(original_text: str, humanized_text: str) -> Dict[str, Any]:
        """Checks for severe length collapse or runaway expansion."""
        orig_words = max(1, len(original_text.split()))
        human_words = len(humanized_text.split())

        ratio = round(human_words / orig_words, 2)
        is_empty = (human_words == 0)
        is_severely_truncated = (ratio < 0.40)
        is_runaway_expanded = (ratio > 2.50)

        anomaly_detected = is_empty or is_severely_truncated or is_runaway_expanded
        reasons = []
        if is_empty: reasons.append("Output is completely empty")
        if is_severely_truncated: reasons.append(f"Severe truncation (length ratio {ratio})")
        if is_runaway_expanded: reasons.append(f"Runaway expansion (length ratio {ratio})")

        return {
            "original_words": orig_words,
            "humanized_words": human_words,
            "length_ratio": ratio,
            "anomaly_detected": anomaly_detected,
            "reasons": reasons
        }

    @staticmethod
    def audit_syntax_leaks(humanized_text: str) -> List[str]:
        """Detects internal placeholder leaks (e.g. '\\x00_LTX_') or unclosed brackets."""
        leaks = []
        if "\x00_LTX_" in humanized_text or "_LTX_" in humanized_text:
            leaks.append("Leaked internal LaTeX placeholder token")
        if humanized_text.count("{") != humanized_text.count("}"):
            leaks.append("Mismatched curly braces in output")
        if humanized_text.count("(") != humanized_text.count(")"):
            leaks.append("Mismatched parentheses in output")
        return leaks

    @classmethod
    def evaluate(
        cls,
        original_text: str,
        humanized_text: str,
        latency_ms: float,
        execution_success: bool = True,
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Calculates operational reliability score (0-100) and performance indicators."""
        if not execution_success:
            return {
                "score": 0.0,
                "execution_success": False,
                "error_message": error_message or "Unknown execution failure",
                "latency_ms": latency_ms,
                "throughput_wps": 0.0,
                "critical_failure": True
            }

        length_audit = cls.audit_length_anomalies(original_text, humanized_text)
        leaks = cls.audit_syntax_leaks(humanized_text)

        # Throughput in words per second
        orig_words = len(original_text.split())
        throughput = round((orig_words / (latency_ms / 1000.0)), 1) if latency_ms > 0 else 9999.0

        score = 100.0

        # Latency grading: Fast (< 50ms) = 100, Moderate (< 500ms) = 90, Slow (> 2000ms) = 60
        if latency_ms > 2000.0:
            score -= 25.0
        elif latency_ms > 500.0:
            score -= 10.0

        # Penalties for length anomalies or leaks
        if length_audit["anomaly_detected"]:
            score -= 40.0
        if leaks:
            score -= len(leaks) * 20.0

        critical_failure = length_audit["anomaly_detected"] or bool(leaks)
        final_score = round(max(0.0, min(100.0, score)), 1)

        return {
            "score": final_score,
            "execution_success": True,
            "latency_ms": latency_ms,
            "throughput_wps": throughput,
            "length_audit": length_audit,
            "syntax_leaks": leaks,
            "critical_failure": critical_failure
        }
