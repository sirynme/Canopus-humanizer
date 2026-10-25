"""Benchmark Dataset Package."""

from benchmark.dataset.generator import BenchmarkCase, BenchmarkDatasetGenerator
from benchmark.dataset.holdout import HoldoutDatasetGenerator
from benchmark.dataset.reference_data import (
    DOMAIN_METADATA,
    VERIFIED_REFERENCE_FACTS,
    VERIFIED_SCHOLARLY_CITATIONS,
)

__all__ = [
    "BenchmarkCase",
    "BenchmarkDatasetGenerator",
    "HoldoutDatasetGenerator",
    "DOMAIN_METADATA",
    "VERIFIED_REFERENCE_FACTS",
    "VERIFIED_SCHOLARLY_CITATIONS",
]
