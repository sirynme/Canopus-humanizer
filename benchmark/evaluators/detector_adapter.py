"""Evaluation Module E: AI Detector Evaluation Adapter.

Provides a pluggable adapter interface for evaluating AI detection risk.
Features built-in ZipPy perplexity & entropy detection alongside an explicit
interface for external detectors, strictly prohibiting simulated or fabricated scores.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
import sys
from pathlib import Path

# Auto-resolve backend/src
src_dir = Path(__file__).resolve().parent.parent.parent / "backend" / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from turnitout.core.checker import ZipPyChecker


class BaseDetectorAdapter(ABC):
    """Abstract base class for AI detector evaluation adapters."""

    @property
    @abstractmethod
    def detector_id(self) -> str:
        """Unique identifier for the detector (e.g. 'ZipPy-v1.0', 'GPTZero-API')."""
        pass

    @abstractmethod
    def evaluate(self, text: str) -> Dict[str, Any]:
        """Runs detector on text and returns standardized evaluation dictionary."""
        pass


class ZipPyDetectorAdapter(BaseDetectorAdapter):
    """Built-in local detector evaluating Shannon entropy, compression ratio, and AI clichés."""

    @property
    def detector_id(self) -> str:
        return "ZipPy-LocalEntropy-v2.6"

    def evaluate(self, text: str) -> Dict[str, Any]:
        """Evaluates text using standard-library Shannon entropy and zlib compression."""
        if not text.strip():
            return {
                "detector_id": self.detector_id,
                "ai_probability": 0.0,
                "human_score": 100.0,
                "shannon_entropy": 0.0,
                "compression_ratio": 1.0,
                "markers_count": 0,
                "detected_markers": [],
                "status": "COMPLETED"
            }

        res = ZipPyChecker.evaluate(text)
        comp_ratio = res.get("zlib_compression_ratio", 1.0)
        return {
            "detector_id": self.detector_id,
            "ai_probability": res["ai_probability"],
            "human_score": res["human_score"],
            "shannon_entropy": res["shannon_entropy"],
            "compression_ratio": comp_ratio,
            "markers_count": len(res.get("detected_markers", [])),
            "detected_markers": res.get("detected_markers", []),
            "status": "COMPLETED"
        }


class ExternalDetectorAdapter(BaseDetectorAdapter):
    """Pluggable adapter interface for commercial external AI detectors.
    
    IMPORTANT: Follows Phase 4E invariant: Never invent or simulate API responses.
    If external API key or connection is unconfigured, marks status as NOT_CONFIGURED.
    """

    def __init__(self, provider_name: str = "QuillBot", api_key: Optional[str] = None):
        self._provider = provider_name
        self._api_key = api_key

    @property
    def detector_id(self) -> str:
        return f"{self._provider}-ExternalAPI"

    def evaluate(self, text: str) -> Dict[str, Any]:
        """Evaluates text against external service, or explicitly marks unconfigured."""
        if not self._api_key:
            return {
                "detector_id": self.detector_id,
                "status": "NOT_CONFIGURED",
                "message": f"External detector '{self._provider}' API key not provided. Manual review or QuillBot web verification recommended.",
                "ai_probability": None,
                "human_score": None
            }

        # Actual API integration would execute here if credentials exist
        return {
            "detector_id": self.detector_id,
            "status": "ERROR_UNIMPLEMENTED",
            "message": "Custom network driver not configured."
        }


class AIDetectorEvaluator:
    """Orchestrates comparative before-and-after AI detector evaluation."""

    def __init__(self, adapter: Optional[BaseDetectorAdapter] = None):
        self.adapter = adapter or ZipPyDetectorAdapter()

    def evaluate_pair(self, original_text: str, humanized_text: str) -> Dict[str, Any]:
        """Runs the detector on both original and humanized text and measures evasion delta."""
        orig_res = self.adapter.evaluate(original_text)
        human_res = self.adapter.evaluate(humanized_text)

        orig_ai = orig_res.get("ai_probability")
        human_ai = human_res.get("ai_probability")

        if orig_ai is not None and human_ai is not None:
            # Score reflects human confidence (100 - human_ai)
            score = round(max(0.0, min(100.0, 100.0 - human_ai)), 1)
            delta = round(orig_ai - human_ai, 1)  # Positive delta = AI probability reduced
        else:
            score = None
            delta = None

        return {
            "detector_id": self.adapter.detector_id,
            "original_result": orig_res,
            "humanized_result": human_res,
            "ai_probability_before": orig_ai,
            "ai_probability_after": human_ai,
            "evasion_delta": delta,
            "score": score
        }
