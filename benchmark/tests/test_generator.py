"""Unit tests for the Benchmark Dataset Generator and Holdout Generator."""

import pytest
from benchmark.dataset.generator import BenchmarkCase, BenchmarkDatasetGenerator
from benchmark.dataset.holdout import HoldoutDatasetGenerator


def test_generator_all_levels():
    generator = BenchmarkDatasetGenerator(seed=42)
    suite = generator.generate_suite(count_per_level=2)

    # 5 levels * 2 cases = 10 cases
    assert len(suite) == 10

    levels = [c.level for c in suite]
    assert set(levels) == {1, 2, 3, 4, 5}

    for case in suite:
        assert isinstance(case, BenchmarkCase)
        assert case.id.startswith("BENCH-L")
        assert len(case.original_text.strip()) > 20
        assert case.level_name is not None
        assert case.domain is not None


def test_generator_deterministic_seed():
    gen1 = BenchmarkDatasetGenerator(seed=123)
    gen2 = BenchmarkDatasetGenerator(seed=123)

    suite1 = gen1.generate_suite(count_per_level=1)
    suite2 = gen2.generate_suite(count_per_level=1)

    assert suite1[0].original_text == suite2[0].original_text
    assert suite1[0].expected_numbers == suite2[0].expected_numbers


def test_holdout_generator_isolation():
    holdout_suite = HoldoutDatasetGenerator.generate_holdout_suite(count_per_level=1)
    assert len(holdout_suite) == 5
    for case in holdout_suite:
        assert case.id.startswith("HOLDOUT-L")
        assert case.metadata.get("is_holdout_set") is True
