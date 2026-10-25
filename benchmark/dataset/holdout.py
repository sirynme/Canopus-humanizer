"""Separate Independent Holdout Dataset Generator for Trust Validation.

Strictly isolated from tuning or iterative configuration. Evaluates generalization
and prevents data leakage or over-optimizing to benchmark test cases.
"""

from typing import List
from benchmark.dataset.generator import BenchmarkCase, BenchmarkDatasetGenerator


class HoldoutDatasetGenerator:
    """Generates an independent, isolated holdout dataset with distinct random seed."""

    HOLDOUT_SEED = 987654321

    @classmethod
    def generate_holdout_suite(cls, count_per_level: int = 3) -> List[BenchmarkCase]:
        """Generates holdout test cases that must not be used during development tuning."""
        generator = BenchmarkDatasetGenerator(seed=cls.HOLDOUT_SEED)
        suite = generator.generate_suite(count_per_level=count_per_level)
        
        # Tag cases explicitly as holdout to prevent misuse
        for case in suite:
            case.id = case.id.replace("BENCH-", "HOLDOUT-")
            case.metadata["is_holdout_set"] = True
            case.metadata["isolation_protocol"] = "STRICT_INDEPENDENT_EVALUATION"

        return suite
