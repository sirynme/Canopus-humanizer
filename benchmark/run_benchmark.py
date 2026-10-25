"""Command-Line Benchmark Runner & Automated Trust Evaluator.

Executes multi-level benchmark test suite against Turnitout Humanizer,
evaluates linguistic quality, semantic preservation, and academic rigor,
and generates JSON, CSV, and standalone HTML reports.
"""

import argparse
from pathlib import Path
import sys

# Auto-resolve paths
benchmark_dir = Path(__file__).resolve().parent
project_root = benchmark_dir.parent
backend_src = project_root / "backend" / "src"

for p in [str(project_root), str(backend_src)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from benchmark.dataset.generator import BenchmarkDatasetGenerator
from benchmark.dataset.holdout import HoldoutDatasetGenerator
from benchmark.pipeline.client import HumanizerClient
from benchmark.pipeline.persistence import BenchmarkPersistence
from benchmark.pipeline.runner import BenchmarkPipelineRunner
from benchmark.reporting.export import BenchmarkExporter
from benchmark.reporting.html_report import BenchmarkHtmlReportGenerator
from benchmark.trust.assessment import TrustAssessmentEngine


def main():
    parser = argparse.ArgumentParser(description="Turnitout Automated Benchmark & Trust Evaluation System")
    parser.add_argument("--cases-per-level", type=int, default=5, help="Number of test cases per difficulty level (default: 5, total 25)")
    parser.add_argument("--seed", type=int, default=42, help="Reproducible random seed (default: 42)")
    parser.add_argument("--run-name", type=str, default="STANDARD_EVAL", help="Identifier tag for this benchmark run")
    parser.add_argument("--use-rest-api", action="store_true", help="Submit text to local FastAPI endpoint (port 8080) instead of direct library invocation")
    parser.add_argument("--holdout", action="store_true", help="Run against the independent holdout validation dataset")
    parser.add_argument("--html-out", type=str, default="benchmark/results/latest_report.html", help="Path for generated HTML report")
    parser.add_argument("--csv-out", type=str, default="benchmark/results/latest_summary.csv", help="Path for generated CSV summary")

    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("🛡️  TURNITOUT AUTOMATED BENCHMARK & TRUST EVALUATION SYSTEM")
    print("=" * 70)
    print(f"• Dataset Mode:     {'Independent Holdout Set' if args.holdout else 'Standard 5-Level Benchmark'}")
    print(f"• Cases per Level:  {args.cases_per_level} (Total: {args.cases_per_level * 5} test documents)")
    print(f"• Channel:          {'Local REST API (127.0.0.1:8080)' if args.use_rest_api else 'Direct Python Library (DocumentModifier)'}")
    print(f"• Random Seed:      {args.seed}")
    print("=" * 70)

    # 1. Generate Dataset
    if args.holdout:
        print("\n[Phase 2] Generating isolated holdout dataset...")
        cases = HoldoutDatasetGenerator.generate_holdout_suite(count_per_level=args.cases_per_level)
    else:
        print("\n[Phase 2] Generating multi-dimensional benchmark suite across Levels 1-5...")
        generator = BenchmarkDatasetGenerator(seed=args.seed)
        cases = generator.generate_suite(count_per_level=args.cases_per_level)

    print(f"✓ Generated {len(cases)} test cases with ground-truth metadata.")

    # 2. Run Pipeline
    print("\n[Phase 3 & 4] Executing before-and-after evaluations on local humanizer...")
    client = HumanizerClient(use_rest_api=args.use_rest_api)
    persistence = BenchmarkPersistence()
    runner = BenchmarkPipelineRunner(client=client, persistence=persistence)

    run_data = runner.run_suite(cases=cases, run_name=args.run_name)
    summary = run_data["summary"]

    # 3. Print Results Summary
    print("\n" + "-" * 70)
    print(f"BENCHMARK RESULTS SUMMARY (Run ID: {run_data['run_id']})")
    print("-" * 70)
    print(f"Total Cases:            {summary['total_cases']}")
    print(f"Passed:                 {summary['passed']} ({summary['pass_rate']}%)")
    print(f"Conditional (Review):   {summary['conditional']} ({summary['conditional_rate']}%)")
    print(f"Failed (Critical Veto): {summary['failed']} ({summary['fail_rate']}%)")
    print(f"Average Composite Score: {summary['avg_composite_score']} / 100")
    print(f"Average Latency:        {summary['avg_latency_ms']} ms")
    print("-" * 70)

    # 4. Generate Trust Assessment
    print("\n[Phase 7] Synthesizing Automated Trust Assessment Report...")
    trust = TrustAssessmentEngine.generate_trust_report(run_data)
    questions = trust.get("questions", {})

    print("\n--- TRUST EVALUATION CORE FINDINGS ---")
    for q_name, q_val in questions.items():
        import re
        clean_title = re.sub(r"^q\d+_", "", q_name).replace("_", " ").title()
        verdict = q_val.get("verdict", "")
        summary_text = q_val.get("summary", "")
        print(f"\n▶ {clean_title} [{verdict}]")
        print(f"  {summary_text}")

    # 5. Export Artifacts
    print("\n[Phase 6] Exporting reports...")
    html_path = project_root / args.html_out
    csv_path = project_root / args.csv_out

    BenchmarkHtmlReportGenerator.generate_report(run_data, output_path=str(html_path))
    BenchmarkExporter.export_csv(run_data, output_path=str(csv_path))

    print(f"✓ Standalone Interactive HTML Report: {html_path}")
    print(f"✓ Tabular CSV Summary:                 {csv_path}")
    print(f"✓ Structured JSON Database Record:     {run_data['json_path']}")
    print("\n" + "=" * 70)
    print("✅ Benchmark & Trust Evaluation Complete.")
    print("=" * 70)


if __name__ == "__main__":
    main()
