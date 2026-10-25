"""Export Utility for Benchmark Results in JSON and CSV Formats."""

import csv
import io
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class BenchmarkExporter:
    """Exports benchmark test run results to CSV and JSON formats."""

    @staticmethod
    def export_json(run_data: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """Serializes benchmark run to formatted JSON string or writes to file."""
        content = json.dumps(run_data, indent=2, ensure_ascii=False)
        if output_path:
            p = Path(output_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(content)
        return content

    @staticmethod
    def export_csv(run_data: Dict[str, Any], output_path: Optional[str] = None) -> str:
        """Flattens benchmark test cases into standard tabular CSV."""
        cases = run_data.get("cases", [])
        output = io.StringIO()
        fieldnames = [
            "test_id",
            "level",
            "level_name",
            "domain",
            "topic",
            "formality",
            "verdict",
            "composite_score",
            "language_quality",
            "semantic_preservation",
            "factual_integrity",
            "academic_quality",
            "operational_reliability",
            "detector_evasion",
            "latency_ms",
            "critical_failures_count",
            "failed_checks_count",
            "is_challenging_case"
        ]

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for item in cases:
            case = item.get("case", {})
            verdict = item.get("verdict", {})
            scores = verdict.get("component_scores", {})
            row = {
                "test_id": case.get("id"),
                "level": case.get("level"),
                "level_name": case.get("level_name"),
                "domain": case.get("domain"),
                "topic": case.get("topic"),
                "formality": case.get("formality"),
                "verdict": verdict.get("verdict"),
                "composite_score": verdict.get("composite_score"),
                "language_quality": scores.get("language_quality"),
                "semantic_preservation": scores.get("semantic_preservation"),
                "factual_integrity": scores.get("factual_integrity"),
                "academic_quality": scores.get("academic_quality"),
                "operational_reliability": scores.get("operational_reliability"),
                "detector_evasion": scores.get("detector_evasion"),
                "latency_ms": item.get("latency_ms"),
                "critical_failures_count": len(verdict.get("critical_failures", [])),
                "failed_checks_count": len(verdict.get("failed_checks", [])),
                "is_challenging_case": case.get("is_challenging_case", False)
            }
            writer.writerow(row)

        content = output.getvalue()
        if output_path:
            p = Path(output_path)
            p.parent.mkdir(parents=True, exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                f.write(content)

        return content
