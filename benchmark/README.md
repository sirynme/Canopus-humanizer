# Turnitout Automated AI Humanizer Benchmarking & Trust Evaluation System

An empirical, fully automated benchmarking and trust evaluation framework built around the **Turnitout Core 2.6.0** AI Humanizer.

The system tests the humanizer across **five difficulty levels** to determine whether it is reliable, whether it improves writing quality, whether it preserves the original meaning and numbers, whether it preserves research logic, and whether it is safe for high-stakes academic and professional writing.

---

## 1. Architecture Overview

```
benchmark/
├── dataset/
│   ├── generator.py          # 5-Level configurable dataset generator (Levels 1 to 5)
│   ├── holdout.py            # Independent holdout dataset generator for bias-free validation
│   └── reference_data.py     # Verified real-world ground-truth facts and citations
├── evaluators/
│   ├── language_quality.py   # Module A: Readability (FRE, FKGL, Fog), variety, TTR, syntax
│   ├── semantic_preservation.py # Module B: Entity recall, numbers, negation polarity, cosine TF-IDF
│   ├── factual_integrity.py  # Module C: Numerical/entity changes, verified reference checks
│   ├── academic_quality.py   # Module D: Research proposal rubric (RQ, H1/H0), citation integrity
│   ├── detector_adapter.py   # Module E: Pluggable AI detector adapters (ZipPy + external stubs)
│   └── operational_reliability.py # Module F: Latency, throughput, length anomalies, syntax leaks
├── scoring/
│   └── decision_engine.py    # 0-100 scoring engine with non-negotiable critical failure vetoes
├── trust/
│   └── assessment.py         # Automated Trust Assessment answering all 9 trust questions
├── pipeline/
│   ├── client.py             # Humanizer client (Direct Library & FastAPI REST API)
│   ├── runner.py             # End-to-end before-and-after benchmark pipeline
│   └── persistence.py        # Structured JSON artifacts and SQLite database storage
├── reporting/
│   ├── html_report.py        # Standalone interactive HTML report with side-by-side inspector
│   └── export.py             # CSV and JSON exporters
├── dashboard/
│   └── app.py                # Interactive local Streamlit dashboard
├── tests/                    # Automated test suite (13 unit & integration tests)
├── TECHNICAL_ASSESSMENT.md   # Initial codebase inspection and architecture audit
└── run_benchmark.py          # Command-line benchmark execution runner
```

---

## 2. Quick Start & Execution Commands

### A. Run Full Benchmark (CLI)
Runs 25 test cases (5 cases per level across 5 difficulty levels):
```bash
python3 benchmark/run_benchmark.py --cases-per-level 5
```

### B. Run Against Isolated Holdout Dataset
Evaluates generalization on an independent, holdout validation suite:
```bash
python3 benchmark/run_benchmark.py --holdout --cases-per-level 3
```

### C. Run via Local REST API (Port 8080)
Executes benchmark over HTTP against the active FastAPI server:
```bash
python3 benchmark/run_benchmark.py --use-rest-api --cases-per-level 2
```

### D. Launch Interactive Local Dashboard
Launches the Streamlit benchmark inspection dashboard:
```bash
backend/.venv/bin/streamlit run benchmark/dashboard/app.py --server.port 8502
```

### E. Run Automated Unit & Integration Tests
```bash
PYTHONPATH=.:backend/src pytest benchmark/tests
```

---

## 3. Five Difficulty Levels

| Level | Level Name | Key Characteristics | Target Domains |
| :---: | :--- | :--- | :--- |
| **Level 1** | **Basic Everyday Writing** | Short paragraphs, simple coordination, daily planning, basic negations. | Everyday, Personal |
| **Level 2** | **Informational & Professional** | Executive summaries, stakeholder emails, corporate KPIs, financial percentages. | Economics, Business |
| **Level 3** | **Analytical & Technical** | Technical explanations, CAP theorem, distributed systems, compound nouns (*"learning rate"*). | Computer Science |
| **Level 4** | **Academic Writing** | Literature reviews, scholarly synthesis, verified scientific facts, formal citations (*APA/IEEE*). | Biomedicine, Life Sciences |
| **Level 5** | **Research Proposals** | Formal academic structure: Problem Statement, Research Questions (RQ1/2), Hypotheses (H1/H0), Objectives, Methodology, Limitations. | CS / Machine Learning |

---

## 4. Evaluation Modules & Critical Veto Rules

### Module A: Language Quality
- **Readability**: Flesch Reading Ease, Flesch-Kincaid Grade Level, Gunning Fog Index.
- **Variety & Burstiness**: Coefficient of variation of sentence lengths.
- **Lexical Diversity**: Type-Token Ratio (TTR) and repetition rates.
- **Syntax Auditing**: Flags repeated words, double punctuation, and awkward adverb-in-compound injections (e.g., *"broadly learning rate"*).

### Module B: Semantic Preservation
- **Named Entity Recall**: Checks preservation of proper nouns, organizations, and acronyms.
- **Numerical Value Preservation**: Strict check that percentages, dates, and currency are retained.
- **Negation Polarity**: Verifies that truth-functional negations (*"not"*, *"never"*, *"cannot"*, *"fails to"*) were not dropped.

### Module C: Factual Integrity
- Compares claims against source and ground-truth verified reference facts.
- Detects newly introduced (hallucinated) numbers.

### Module D: Academic & Research Quality
- Proposal Rubric: Evaluates preservation of Problem Statement, RQs, Hypotheses, Methodology, and Limitations.
- Citation Integrity: In-text citations must remain uncorrupted (*IEEE `[1]`*, *APA*, *`\cite{}`*).

### Module E: AI Detector Evasion
- Measures before-and-after AI probability, Shannon entropy, and compression ratios using `ZipPyChecker`.

### Module F: Operational Reliability
- Measures throughput (wps), latency (ms), length expansion/truncation ratios, and placeholder leaks.

---

## 5. Strict Decision Verdicts

- **PASS**: All module scores $\ge$ thresholds, zero critical failures.
- **CONDITIONAL**: Minor quality regressions or non-critical threshold warnings. Flagged for human review.
- **FAIL**: Triggered automatically if:
  1. A verified ground-truth fact or number is altered or lost.
  2. A negation word is dropped or meaning inverted.
  3. In-text citations are corrupted or broken.
  4. Execution crashes or produces an empty/truncated document.
  
> ⚠️ **Invariant**: A weighted average composite score **NEVER** overrides a critical failure!

---

## 6. Generated Reports

- **Interactive Standalone HTML Report**: `benchmark/results/latest_report.html` (includes side-by-side document diffs and embedded trust findings).
- **Tabular CSV Summary**: `benchmark/results/latest_summary.csv`.
- **Structured JSON Run Archive**: `benchmark/results/RUN_*.json`.
- **SQLite Database**: `benchmark/results/benchmark.db`.
