"""Client Interface to Local Turnitout Humanizer.

Provides flexible invocation via either direct Python library execution (DocumentModifier)
or local FastAPI REST API (http://127.0.0.1:8080/v1/humanize), capturing latency and errors.
"""

import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Auto-resolve backend/src
src_dir = Path(__file__).resolve().parent.parent.parent / "backend" / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from turnitout.config import ConfigNamespace
from turnitout.core.modifier import DocumentModifier


class HumanizerClient:
    """Client wrapper for submitting text to Turnitout with performance and error capture."""

    def __init__(
        self,
        use_rest_api: bool = False,
        api_base: str = "http://127.0.0.1:8080",
        default_intensity: float = 75.0,
        default_style: str = "academic"
    ):
        self.use_rest_api = use_rest_api
        self.api_base = api_base
        self.default_intensity = default_intensity
        self.default_style = default_style

    def transform(
        self,
        text: str,
        seed: Optional[int] = 42,
        intensity: Optional[float] = None,
        style: Optional[str] = None,
        protected_terms: Optional[List[str]] = None,
        enable_citations: bool = False,
        citation_format: str = "IEEE [1]",
        max_citations: int = 0
    ) -> Dict[str, Any]:
        """Transforms text and captures outputs, latency, and operational telemetry."""
        intensity = intensity or self.default_intensity
        style = style or self.default_style
        protected_set = set(protected_terms or [])

        start_time = time.perf_counter()

        # 1. Option A: Local REST API Call
        if self.use_rest_api:
            try:
                import urllib.request
                import json

                url = f"{self.api_base}/v1/humanize"
                payload = {
                    "text": text,
                    "intensity": intensity,
                    "style": style,
                    "protected_terms": list(protected_set),
                    "seed": seed,
                    "enable_citations": enable_citations,
                    "max_citations": max_citations,
                    "citation_format": citation_format
                }
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode("utf-8"),
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    res_data = json.loads(response.read().decode("utf-8"))
                    latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
                    return {
                        "success": True,
                        "humanized_text": res_data.get("humanized_text", ""),
                        "latency_ms": latency_ms,
                        "modifications_count": res_data.get("modifications_count", 0),
                        "telemetry": res_data.get("telemetry", {}),
                        "channel": "REST_API",
                        "error": None
                    }
            except Exception as e:
                latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
                return {
                    "success": False,
                    "humanized_text": "",
                    "latency_ms": latency_ms,
                    "modifications_count": 0,
                    "telemetry": {},
                    "channel": "REST_API",
                    "error": str(e)
                }

        # 2. Option B: Direct Python Library Invocation (High performance & deterministic)
        try:
            cfg = ConfigNamespace()
            cfg.INTENSITY = intensity
            cfg.STYLE = style
            
            modifier = DocumentModifier(config=cfg, seed=seed)
            out_text = modifier.modify_document(
                text=text,
                protected_terms=protected_set,
                enable_citations=enable_citations,
                citation_format=citation_format,
                max_citations=max_citations
            )
            latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

            return {
                "success": True,
                "humanized_text": out_text,
                "latency_ms": latency_ms,
                "modifications_count": modifier.total_transforms,
                "telemetry": {
                    "total_transforms": modifier.total_transforms,
                    "seed": seed,
                    "intensity": intensity,
                    "style": style
                },
                "channel": "DIRECT_LIBRARY",
                "error": None
            }
        except Exception as e:
            latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
            return {
                "success": False,
                "humanized_text": "",
                "latency_ms": latency_ms,
                "modifications_count": 0,
                "telemetry": {},
                "channel": "DIRECT_LIBRARY",
                "error": str(e)
            }
