"""Persistence Layer for Benchmark Results.

Stores full test case records, before-and-after document pairs, module evaluation metrics,
and decision verdicts in structured JSON files and a local SQLite database.
"""

from dataclasses import asdict
import json
from pathlib import Path
import sqlite3
import time
from typing import Any, Dict, List, Optional


class BenchmarkPersistence:
    """Manages persistent disk storage and SQLite querying for benchmark test runs."""

    def __init__(self, storage_dir: Optional[str] = None):
        self.storage_dir = Path(storage_dir) if storage_dir else Path(__file__).resolve().parent.parent / "results"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.storage_dir / "benchmark.db"
        self._init_sqlite()

    def _init_sqlite(self) -> None:
        """Initializes SQLite database schema for structured benchmark querying."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_runs (
                    run_id TEXT PRIMARY KEY,
                    timestamp REAL,
                    total_tests INTEGER,
                    passed INTEGER,
                    conditional INTEGER,
                    failed INTEGER,
                    avg_composite_score REAL,
                    avg_latency_ms REAL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_cases (
                    id TEXT PRIMARY KEY,
                    run_id TEXT,
                    level INTEGER,
                    domain TEXT,
                    topic TEXT,
                    verdict TEXT,
                    composite_score REAL,
                    language_score REAL,
                    semantic_score REAL,
                    factual_score REAL,
                    academic_score REAL,
                    reliability_score REAL,
                    detector_score REAL,
                    latency_ms REAL,
                    original_text TEXT,
                    humanized_text TEXT,
                    critical_failures TEXT,
                    failed_checks TEXT,
                    FOREIGN KEY(run_id) REFERENCES test_runs(run_id)
                )
            """)
            conn.commit()

    def save_run(
        self,
        run_id: str,
        run_metadata: Dict[str, Any],
        results: List[Dict[str, Any]]
    ) -> Path:
        """Saves complete benchmark run data into a JSON artifact and SQLite tables."""
        # 1. Save Full Detailed JSON Artifact
        json_path = self.storage_dir / f"{run_id}.json"
        payload = {
            "run_id": run_id,
            "timestamp": time.time(),
            "metadata": run_metadata,
            "summary": {
                "total_cases": len(results),
                "passed": sum(1 for r in results if r.get("verdict", {}).get("verdict") == "PASS"),
                "conditional": sum(1 for r in results if r.get("verdict", {}).get("verdict") == "CONDITIONAL"),
                "failed": sum(1 for r in results if r.get("verdict", {}).get("verdict") == "FAIL"),
                "avg_composite": round(sum(r.get("verdict", {}).get("composite_score", 0.0) for r in results) / max(1, len(results)), 1),
                "avg_latency_ms": round(sum(r.get("latency_ms", 0.0) for r in results) / max(1, len(results)), 2)
            },
            "cases": results
        }

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        # 2. Save into SQLite for Fast Filtering
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO test_runs VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run_id,
                payload["timestamp"],
                payload["summary"]["total_cases"],
                payload["summary"]["passed"],
                payload["summary"]["conditional"],
                payload["summary"]["failed"],
                payload["summary"]["avg_composite"],
                payload["summary"]["avg_latency_ms"]
            ))

            for item in results:
                case = item.get("case", {})
                verdict = item.get("verdict", {})
                comp_scores = verdict.get("component_scores", {})
                cursor.execute("""
                    INSERT OR REPLACE INTO test_cases VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    case.get("id"),
                    run_id,
                    case.get("level"),
                    case.get("domain"),
                    case.get("topic"),
                    verdict.get("verdict"),
                    verdict.get("composite_score"),
                    comp_scores.get("language_quality"),
                    comp_scores.get("semantic_preservation"),
                    comp_scores.get("factual_integrity"),
                    comp_scores.get("academic_quality"),
                    comp_scores.get("operational_reliability"),
                    comp_scores.get("detector_evasion"),
                    item.get("latency_ms"),
                    item.get("original_text"),
                    item.get("humanized_text"),
                    json.dumps(verdict.get("critical_failures", [])),
                    json.dumps(verdict.get("failed_checks", []))
                ))
            conn.commit()

        return json_path

    def load_latest_run(self) -> Optional[Dict[str, Any]]:
        """Loads the most recent benchmark run JSON."""
        json_files = sorted(self.storage_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not json_files:
            return None
        with open(json_files[0], "r", encoding="utf-8") as f:
            return json.load(f)
