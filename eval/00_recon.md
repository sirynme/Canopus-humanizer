# Turnitout-Humanizer: Phase 0 Reconnaissance & Architectural Baseline

**Evaluation Engineer**: Senior ML Evaluation Engineer  
**Date**: 2026-10-25  
**Target Repository**: `Turnitout-Humanizer` (`Turnitout-Core` v2.6.0)  
**Execution Environment**: Linux (Fedora 44, Kernel 7.2.11), Python 3.14.8, x86_64, 4 vCPUs, 8 GB RAM  
**Git Branch**: `eval-run`  

---

## 1. Baseline Test Suite & Latency Verification

We executed the official test suite and benchmark runners directly in `backend/.venv` using `PYTHONPATH=backend/src:.`:

### A. Official Test Suite (`backend/tests/` + `benchmark/tests/`)
* **Total Tests**: **45 tests** (24 backend core/API/rules/checker tests + 21 benchmark evaluator/generator/regression tests)
* **Result**: **45 passed, 0 failed, 0 errors** in **0.83 seconds**
* **Raw Artifact**: [`eval/results/baseline/pytest_output.txt`](file:///home/canopus/Downloads/Turnitout-Humanizer-main/eval/results/baseline/pytest_output.txt)

### B. Standard 5-Level Benchmark Suite (25 Test Cases)
* **Cases**: 25 (5 cases across Levels 1–5: Everyday, Professional, Technical, Academic, Proposals)
* **Pass Rate**: **25 / 25 passed (100.0%)**
* **Critical Vetoes**: 0
* **Average Composite Score**: **97.7 / 100**
* **Average Latency**: **4.20 ms**
* **Raw Artifact**: [`eval/results/baseline/benchmark_standard_output.txt`](file:///home/canopus/Downloads/Turnitout-Humanizer-main/eval/results/baseline/benchmark_standard_output.txt)

### C. Independent Holdout Validation Suite (15 Test Cases)
* **Cases**: 15 (3 cases across Levels 1–5)
* **Pass Rate**: **15 / 15 passed (100.0%)**
* **Critical Vetoes**: 0
* **Average Composite Score**: **97.5 / 100**
* **Average Latency**: **3.31 ms**
* **Raw Artifact**: [`eval/results/baseline/benchmark_holdout_output.txt`](file:///home/canopus/Downloads/Turnitout-Humanizer-main/eval/results/baseline/benchmark_holdout_output.txt)

> **Empirical Confirmation**: The repository's claims of **45 passing tests**, **100% benchmark pass rate**, and **~3.8 ms mean latency** (4.20 ms standard, 3.31 ms holdout = 3.75 ms average) are **verified and replicated**.

---

## 2. Inventory of Entry Points

The repository exposes five programmatic and user-facing entry points:

### 1. Command-Line Interface (CLI)
* **File**: [`backend/src/turnitout/cli.py`](file:///home/canopus/Downloads/Turnitout-Humanizer-main/backend/src/turnitout/cli.py)
* **Invocation**: `backend/.venv/bin/python backend/src/turnitout/cli.py [OPTIONS]`
* **Capabilities**:
  * In-place file processing (`.txt`, `.md`, `.tex`, `.docx`, `.py`).
  * Direct string processing via `--text`.
  * Batch directory & in-memory ZIP package creation.
  * Arguments: `--style`, `--intensity`, `--protected`, `--seed`, `--citations`, `--discipline`.

### 2. Enterprise REST API (FastAPI)
* **Server Launcher**: [`backend/run_api.py`](file:///home/canopus/Downloads/Turnitout-Humanizer-main/backend/run_api.py) (default port `8080`)
* **Router**: [`backend/src/turnitout/api/routes.py`](file:///home/canopus/Downloads/Turnitout-Humanizer-main/backend/src/turnitout/api/routes.py)
* **Endpoints**:
  * `POST /v1/humanize`: Full 17-stage transformation on raw text payloads up to 50,000 characters.
  * `POST /v1/citations`: Dynamic academic citation & BibTeX generation.
  * `GET /v1/quota`: API key rate limits and request counters.
  * `GET /v1/health`: Uptime, engine status, and active configuration.
* **Documentation**: Interactive OpenAPI Swagger UI at `http://127.0.0.1:8080/docs`.

### 3. Multi-Module Streamlit Web Application
* **File**: [`backend/streamlit_app.py`](file:///home/canopus/Downloads/Turnitout-Humanizer-main/backend/streamlit_app.py)
* **Invocation**: `backend/.venv/bin/streamlit run backend/streamlit_app.py --server.port 8501`
* **Modules**:
  * `⚡ Plagiarism & AI Remover`: Text & multi-file document humanization.
  * `📜 Citation & Reference Generator`: In-text citation injector & `.bib` exporter.
  * `🔍 AI Pattern & Signature Checker`: ZipPy entropy, compression ratio, and Winnowing similarity.
  * `💬 Feature Request & Bug Reporter`: User issue templates.

### 4. Interactive Benchmark & Trust Evaluation Dashboard
* **File**: [`benchmark/dashboard/app.py`](file:///home/canopus/Downloads/Turnitout-Humanizer-main/benchmark/dashboard/app.py)
* **Invocation**: `backend/.venv/bin/streamlit run benchmark/dashboard/app.py --server.port 8502`
* **Tabs**:
  1. Executive Summary & Health Cards.
  2. Level-by-Level Breakdown (Levels 1–5).
  3. Failure Analysis & Veto Inspector.
  4. Latency & Operational Telemetry.
  5. Baseline vs. Optimized Side-by-Side Comparison.

### 5. Static Web Workspace (GitHub Pages / Local Web Server)
* **Files**: [`docs/index.html`](file:///home/canopus/Downloads/Turnitout-Humanizer-main/docs/index.html), [`docs/script.js`](file:///home/canopus/Downloads/Turnitout-Humanizer-main/docs/script.js), [`docs/style.css`](file:///home/canopus/Downloads/Turnitout-Humanizer-main/docs/style.css)
* **Invocation**: `python3 -m http.server 8000 --directory docs`
* **Features**: Ultra-clean dual-pane editor communicating asynchronously with the local REST API on `http://127.0.0.1:8080`, supporting live word counts, writing mode selectors, intensity sliders, and copy/download.

---

## 3. Configuration Knobs & Parameter Surface

All transformations are driven by [`TransformationConfig`](file:///home/canopus/Downloads/Turnitout-Humanizer-main/backend/src/turnitout/core/modifier.py#L29) and [`backend/configs/global_config.json`](file:///home/canopus/Downloads/Turnitout-Humanizer-main/backend/configs/global_config.json):

### A. High-Level Macro Controls
* **`style` (Writing Register)**:
  * `academic`: Strict conservative gating. Completely disables destructive heuristics (N-gram auditor, appositive insertion, blind nominalization, random transition injection, and hedge words). Enforces passive voice number concord (`was` vs `were`).
  * `technical` (Formal): Restricts informal contractions while permitting technical synonyms and structural bridges.
  * `standard`: Balanced general-purpose rewriting.
  * `conversational` (Casual): Permits colloquial phrase rewrites, contractions, and relaxed sentence structures.
* **`intensity` (Transformation Strength)**: Float range `25.0` to `100.0` (default: `70.0`). Dynamically scales probabilistic fire-rates across all non-gated linguistic stages.
* **`seed`**: Integer seed (e.g. `42`) to enforce 100% deterministic, byte-for-byte reproducible transformations.
* **`protected_terms`**: List of user-supplied domain strings that are shielded from synonym replacement or word boundary splitting.

### B. Micro-Stage Toggles & Rate Knobs
```python
TransformationConfig(
    style="academic",                 # ["academic", "technical", "standard", "conversational"]
    intensity=70.0,                   # 25.0 to 100.0
    enable_synonyms=True,             # Stage 5
    synonym_alignment=0.85,           # Contextual alignment threshold
    random_alignment=False,           # Disable blind randomized substitutions
    enable_phrase_rewrite=True,       # Stage 6
    enable_determiner_swap=True,      # Stage 4
    enable_voice_transform=False,     # Stage 9 (disabled by default in academic)
    enable_sentence_fusion=True,      # Stage 10 (gated against section headers)
    enable_transition_inject=False,   # Stage 11 (disabled by default in academic)
    enable_clause_reorder=False,      # Stage 12 (disabled by default in academic)
    enable_nominalization=False,      # Stage 13 (disabled by default in academic)
    enable_appositive=False,          # Stage 14 (disabled by default in academic)
    enable_discourse_rotate=True,     # Stage 7
    enable_contraction=False,         # Stage 3
    enable_ngram_audit=False,         # Stage 8 (disabled by default in academic)
    enable_split_compound=False,      # Stage 15
    enable_ai_tell_scrubber=True,     # Stage 2
    protected_terms=[]                # Tier 5 multi-word technical units
)
```

---

## 4. Map of the 17 Transformation Stages

The transformation pipeline in [`DocumentModifier.modify_text()`](file:///home/canopus/Downloads/Turnitout-Humanizer-main/backend/src/turnitout/core/modifier.py#L42) executes sequentially across 17 distinct stages:

| Stage # | Stage Name | Target Linguistic / Syntactic Function | Academic Default Status | Risk Profile & Mitigation |
| :---: | :--- | :--- | :---: | :--- |
| **Stage 1** | **Conservative Protection Layer** | Shields LaTeX math (`$...$`, `$$...$$`, `\frac{}{}`), in-text citations (IEEE `[1]`, APA `(Author et al., 2020)`), numbers, quantities with units, statistical expressions (`p < 0.001`), 35+ MWUs, and section headers (`RQ1:`, `H1:`). | **Active (Mandatory)** | **Zero Risk**: Replaced by alphanumeric zero-byte tokens `__TOT_MATH_x__`, `__TOT_CITE_x__`, etc. |
| **Stage 2** | **AI-Tell & Metadata Scrubber** | Strips Anthropic Claude / Google SynthID tracking artifacts, zero-width Unicode characters (`U+200B`, `U+200C`, `U+200D`), and C2PA markers. | **Active** | **Zero Risk**: Pure character cleanup. |
| **Stage 3** | **Contraction Management** | Expands or contracts modal auxiliaries (`do not` $\leftrightarrow$ `don't`). | **Gated Off** (Disabled in Academic) | Prevents informal tone in formal papers. |
| **Stage 4** | **Determiner & Quantifier Swapping** | Contextually substitutes non-restrictive determiners (`a` $\leftrightarrow$ `a given`, `this` $\leftrightarrow$ `the present`). | **Active** (Gated by intensity) | Low risk; preserves noun-phrase semantics. |
| **Stage 5** | **Synonym Alignment** | Substitutes words using clean, curated academic dictionaries in `rules/synonyms.json`. | **Active** | Filtered to modern academic register; archaic purple prose purged. |
| **Stage 6** | **Phrase & Collocation Rewriting** | Replaces formulaic cliches (`in order to` $\to$ `to`, `due to the fact that` $\to$ `because`). | **Active** | Improves brevity and natural rhythm. |
| **Stage 7** | **Discourse Marker Rotation** | Rotates sentence-initial transitions (`Furthermore` $\to$ `Additionally`, `Moreover` $\to$ `In addition`). | **Active** | Breaks repetitious transition sequences. |
| **Stage 8** | **Winnowing N-Gram Auditor** | Injects adverbs every 6 words to break 5-gram hashes. | **Gated Off** (Disabled in Academic) | **High Risk**: Disrupted MWUs in baseline; gated off in academic mode. |
| **Stage 9** | **Active-to-Passive Voice Inversion** | Converts active clauses to passive constructions. | **Gated Off** (Disabled in Academic) | Enforces concord detection (`was` vs `were`) for plural subjects. |
| **Stage 10** | **Sentence Fusion** | Merges short adjacent sentences using causal coordinators. | **Active (Conditioned)** | Gated against numbered lists, research questions, and hypotheses. |
| **Stage 11** | **Transitional Adverb Injection** | Injects rhetorical connectors (`consequently`, `accordingly`). | **Gated Off** (Disabled in Academic) | Prevents decorative padding. |
| **Stage 12** | **Clause & Information Reordering** | Swaps dependent and independent clause order. | **Gated Off** (Disabled in Academic) | Prevents detachment of numerical values. |
| **Stage 13** | **Nominalization of Verb Phrases** | Converts verbs into abstract noun phrases (`analyze` $\to$ `conduct an analysis of`). | **Gated Off** (Disabled in Academic) | Prevents dense, sluggish readability. |
| **Stage 14** | **Appositive & Parenthetical Injection** | Injects rhetorical parentheticals (`", a crucial factor,"`). | **Gated Off** (Disabled in Academic) | Prevents extrinsic qualitative assertions. |
| **Stage 15** | **Compound Sentence Splitting** | Splits run-on clauses into separate sentences. | **Gated Off** (Disabled in Academic) | Preserves original structural architecture. |
| **Stage 16** | **Hedge Word Injection** | Injects epistemic qualifiers (`putatively`, `broadly`). | **Gated Off** (Disabled in Academic) | Prevents weakening of empirical assertions. |
| **Stage 17** | **Restoration & Fail-Closed Rollback** | Restores all masked tokens from Stage 1. Validates placeholder count. | **Active (Mandatory)** | **Fail-Closed**: If even 1 placeholder is missing, entire output is discarded and original text returned safely. |

---

## 5. Architectural Evaluation Plan & Sample Size Strategy

Given our host compute profile (Intel Core i5-6300U, 4 logical cores, 8 GB RAM, 127 GB disk, Python 3.14.8), running heavy neural networks (e.g., DeBERTa-v3-large + Binoculars + Fast-DetectGPT) across 2,000 full documents × 16 conditions = 32,000 runs would take >120 CPU hours and risk system OOM.

To adhere strictly to Ground Rule 4 (*"If compute is limited, scale sample sizes down in tiers (target, minimum) and state which tier you ran"*), we define two rigorous tiers:

### Sample Size Tiers

| Dimension | Target Tier (HPC / Multi-GPU) | **Executed Tier (Calibrated for Host i5/8GB)** | Rationale |
| :--- | :---: | :---: | :--- |
| **Total Corpus Documents** | 2,000 docs | **300 documents** | Statistically significant ($N=300 \implies \pm 5.6\%$ margin of error at 95% CI). |
| **Domain Coverage** | 9 fields | **9 fields** (CS, Eng/Phys, Math/Stat, Med/Life, Quant Finance, Humanities, Law, SocSci, Everyday) | 100% field representation preserved (~33 docs/field). |
| **Human vs AI Balance** | 50% / 50% | **50% Human (pre-2020) / 50% AI** | 150 Human / 150 AI docs across all fields. |
| **Special Test Sets** | Non-native, mixed, heavy-math | **Included** (20 non-native, 20 mixed, 20 heavy math/code) | Full representation of edge conditions. |
| **Full Papers (LaTeX & DOCX)** | 50 papers (30 TeX, 30 DOCX) | **60 papers** (30 real LaTeX `.tex`, 30 real `.docx`) | 100% of required real paper count evaluated. |
| **Length Buckets** | Sentence, para, section, long, full | **All 5 length buckets** | Stratified across all length regimes. |
| **Matrix Sweep (Phase 2)** | 16 combinations (4 styles × 4 intensities) | **Full 16 combinations on 300 docs** = **4,800 runs** | Complete parametric matrix evaluated. |
| **Local Detectors (Phase 3)** | Binoculars, Fast-DetectGPT, RoBERTa, ZipPy | **ZipPy + TF-IDF Logistic Classifier + HF open-source detector** | Binoculars requires 2 large causal LLMs (Falcon-7B / Llama-3-8B) needing 32GB GPU VRAM (impossible on 8GB CPU). ZipPy, HF detector, and TF-IDF fingerprint run on CPU. Commercial detectors provided via manual pack. |
| **Human Review Pack** | 150 stratified + 50 worst | **150 stratified + 50 worst (200 HTML diffs)** | 100% compliance with review pack deliverables. |
| **Manual Detector Pack** | 60 anonymized samples | **60 anonymized samples + ingestion script** | 100% compliance with manual pack deliverables. |

---

## 6. Phase Execution Roadmap

1. **Phase 1: Corpus Construction & Manifest Creation**:
   * Gather pre-2020 human text from public archives and AI-generated texts across the 9 fields and 5 formats (`.txt`, `.md`, `.tex`, `.docx`, `.py`).
   * Assemble 30 real LaTeX papers and 30 real DOCX papers.
   * Generate `eval/data/manifest.csv` with columns: `id, source, field, label, length_bucket, format, license`.
2. **Phase 2: Quality and Fidelity Sweep (4,800 runs)**:
   * Execute style × intensity matrix.
   * Evaluate Hard Invariants (numbers, citations, LaTeX, negations, glossary preservation).
   * Evaluate semantic & fluency metrics (cosine similarity, grammar error delta, perplexity, register check).
   * Generate `eval/review/` human review pack (200 side-by-side HTML diffs + scoring sheet).
3. **Phase 3: Detector Evaluation & Fingerprint Audit**:
   * Run local detector suite + train TF-IDF signature classifier to test for telltale humanizer patterns.
   * Generate `eval/manual_detector_pack/` with 60 anonymized samples and CSV evaluation script.
4. **Phase 4: Scale, Robustness, Security & Claims Audit**:
   * Concurrency & latency profiling (1, 10, 50 concurrent requests on `/v1/humanize`).
   * Malformed input fuzzing (unbalanced LaTeX, corrupt DOCX, Unicode/RTL, zip-slip).
   * Network & disk monitoring to verify zero-retention / 100% in-memory claim.
   * Claims verification matrix across `README.md`, `AGENTS.md`, and technical reports.
5. **Phase 5: End-to-End Full-Paper Tests**:
   * Compile 30 LaTeX papers before/after; check equation counts, bib references, float positions.
   * Round-trip 30 DOCX files; compare XML document structures.
6. **Phase 6: Verdict & Master Deliverables**:
   * Go/no-go gate evaluation.
   * Produce `eval/REPORT.md`, `eval/report.html`, `eval/BUGS.md`, and `eval/run_all.py` reproduction script.
