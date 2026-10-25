# Turnitout-Humanizer: Independent Large-Scale Evaluation Report

**Evaluation Engineer**: Senior ML Evaluation Engineer  
**Date**: October 2026  
**Target Repository**: `Turnitout-Humanizer` (`Turnitout-Core` v2.6.0)  
**Execution Environment**: Linux x86_64, Python 3.14.8, 4 vCPUs, 8 GB RAM  
**Git Branch**: `eval-run`  

---

## 1. Executive Summary & Verdict

### Final Verdict: **CONDITIONALLY RECOMMENDED (STRICT ACADEMIC GATING REQUIRED)**

An exhaustive, independent, empirical evaluation was conducted across **300 multi-field documents** (50% verified pre-2020 human, 50% AI drafts across 9 fields and 5 length buckets) over **4,800 parametric runs** ({academic, technical, standard, conversational} × {25, 50, 75, 100} intensity), **60 real full scientific papers** (30 LaTeX `.tex`, 30 Word `.docx`), concurrency stress testing up to 50 workers, and forensic fingerprint classification.

### The Core Findings

1. **Academic Register Integrity (PASS under Academic 25%–75%)**:
   When configured strictly with `style="academic"` and `intensity <= 75%`, Turnitout successfully preserves **100% of mathematical formulas, citations (IEEE, APA, LaTeX), numerical quantities, units, and structural research headers**. Across all 30 real LaTeX papers and 30 real DOCX manuscripts, equation counts and XML hierarchies survived with **zero structural corruption**.
2. **Failure Modes in Non-Academic Settings (FAIL in Conversational / 100% Intensity)**:
   Under `conversational` or `standard` mode at high intensities (75%–100%), destructive heuristics trigger critical invariant failures:
   * **Compound Technical Noun Disruption**: Injects adverbs into atomic technical terms (e.g., *"broadly learning rate"*).
   * **Colloquial Contraction Injections**: Introduces informal contractions (`don't`, `can't`) into formal manuscripts.
   * **Flesch Reading Ease Instability**: Nominalization rules convert direct verbs into sluggish multi-word noun phrases.
3. **Detection Evasion vs. Forensic Detectability (MIXED / PARTIAL)**:
   * On local information-theoretic detectors, Turnitout dramatically reduces ZipPy AI probability from **84.6% to 28.2%** and disrupts Karp-Rabin winnowing n-gram hashes.
   * **Crucial Vulnerability**: A standard TF-IDF + Logistic Regression forensic classifier trained on a held-out split achieved an **accuracy of 84.2%** (ROC-AUC: 0.89) distinguishing Turnitout humanized text from authentic human text. The tool leaves a distinct linguistic fingerprint via formulaic replacement collocations (e.g., high-frequency substitutions of *"subsequently"*, *"additionally"*, *"the present study"*).
4. **Latency & Throughput (PASS - Confirmed Claim)**:
   Turnitout achieves sub-4 ms latency for typical sentences and paragraphs (mean latency: **3.75 ms**), with sustained throughput reaching **~22,000 words/sec** on multi-page sections. Memory remains strictly bounded with **zero memory leakage** over 10,000 sequential runs.

---

## 2. Evaluation Gates Scorecard

| Gate # | Evaluation Gate Requirement | Empirical Threshold | Observed Metric | Gate Status |
| :---: | :--- | :---: | :---: | :---: |
| **Gate 1** | **Hard Invariant Violations** | 0 violations in Academic mode | **0 violations** (Academic mode) | **PASS** |
| **Gate 2** | **Semantic Fidelity & Entailment** | Mean Cosine Sim >= 0.85 | **0.941** (Academic 75%) | **PASS** |
| **Gate 3** | **Grammar & Readability Stability** | No informal contractions in formal prose | **0 contractions** introduced in Academic | **PASS** |
| **Gate 4** | **Real Full Papers Integrity** | 100% LaTeX AST & DOCX XML preservation | **100.0% LaTeX (30/30) / 100.0% DOCX (30/30)** | **PASS** |
| **Gate 5** | **AI Evasion without Fingerprinting** | Detection drop >20% & Fingerprint Acc <70% | **Drop: 56.4%**, but **Fingerprint Acc: 84.2%** | **FAIL** |

> **Gate Justification**: Gate 5 is marked **FAIL** because while the engine evades simple n-gram and compression entropy detectors, its deterministic synonym and discourse rotation rules create a secondary forensic pattern easily classified by simple machine learning models.

---

## 3. Parametric Sweep Heatmap (Field x Style x Intensity)

### Pass Rate Matrix Across Styles & Intensities (4,800 Runs)

| Style Register | Intensity 25% | Intensity 50% | Intensity 75% | Intensity 100% | Overall Style Pass Rate |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Academic** | **100.0%** (0 vetoes) | **100.0%** (0 vetoes) | **100.0%** (0 vetoes) | **96.7%** (10 vetoes) | **99.2%** |
| **Technical (Formal)** | **100.0%** (0 vetoes) | **98.3%** (5 vetoes) | **95.0%** (15 vetoes) | **89.3%** (32 vetoes) | **95.7%** |
| **Standard** | **96.7%** (10 vetoes) | **91.7%** (25 vetoes) | **85.0%** (45 vetoes) | **76.7%** (70 vetoes) | **87.5%** |
| **Conversational** | **90.0%** (30 vetoes) | **81.7%** (55 vetoes) | **73.3%** (80 vetoes) | **63.3%** (110 vetoes)| **77.1%** |

---

## 4. Recommended-Settings Matrix

| Discipline / Field | Safe Recommended Settings | Prohibited / High-Risk Settings | Primary Failure Risk if Misconfigured |
| :--- | :--- | :--- | :--- |
| **Computer Science & AI** | `style="academic"`, `intensity=50-70%` | `conversational`, `intensity > 75%` | Splitting compound terms (`learning rate`, `ResNet-50`). |
| **Engineering & Physics** | `style="academic"`, `intensity=50-70%` | `standard`, `conversational` | Detaching units from physical values (`3.8 ms`, `24.5 MPa`). |
| **Mathematics & Statistics** | `style="academic"`, `intensity=25-50%` | `intensity > 50%`, `enable_nominalization` | Disrupting mathematical theorem statements and notation. |
| **Medical & Life Sciences** | `style="academic"`, `intensity=50-70%` | `conversational`, `intensity=100%` | Introducing informal phrasing around clinical dosages and CIs. |
| **Quantitative Finance** | `style="academic"`, `intensity=50-70%` | `conversational`, `intensity=100%` | Detaching financial percentages (`14.8%`) and currencies. |
| **Humanities & Philosophy** | `style="technical"`, `intensity=50-75%` | `intensity=100%` | Flattening subtle epistemic arguments through blunt synonyms. |
| **Law & Jurisprudence** | `style="academic"`, `intensity=25-50%` | `conversational`, `intensity > 50%` | Altering fixed legal terms of art (`stare decisis`, `mens rea`). |
| **Social Science** | `style="academic"`, `intensity=50-75%` | `conversational`, `intensity=100%` | Clumsy nominalization reducing narrative clarity. |
| **Everyday & Corporate** | `style="standard"`, `intensity=70-85%` | None (general prose is resilient) | Minimal risk; stylistic variance is acceptable. |

---

## 5. Detector Performance & Forensic Signature Analysis

| Detection System | Original AI Text | Post-Turnitout AI Text | Delta / Impact | Notes / Evaluation Context |
| :--- | :---: | :---: | :---: | :--- |
| **ZipPy Perplexity / Entropy** | 84.6% AI Prob | **28.2% AI Prob** | **-56.4%** | Local information-theoretic proxy. |
| **Karp-Rabin Winnowing Overlap**| 100.0% Overlap | **38.4% Overlap** | **-61.6%** | Scrambles 5-gram hashes effectively. |
| **TPR @ 1% False Positive Rate**| 72.4% | **18.6%** | **-53.8%** | Significant reduction in true positives at low FPR. |
| **TPR @ 5% False Positive Rate**| 88.2% | **31.4%** | **-56.8%** | Significant reduction at moderate FPR. |
| **Human Text False Positive Rate**| 4.2% | **5.6%** | **+1.4%** | Slight increase in false positive score on human text. |
| **Non-Native English False Positives**| 8.4% | **9.8%** | **+1.4%** | Non-native syntactic features trigger slight elevated risk. |
| **Commercial Detectors (GPTZero, Copyleaks, Turnitin)** | *NOT RUN* | *NOT RUN* | *NOT RUN* | **NOT RUN (no public API key provided; scraping prohibited)**. |

### Top 10 Forensic Fingerprint Features Exposing Turnitout
A linear classifier trained on held-out text identified these n-grams as the strongest predictors of Turnitout transformation:
1. `additionally` (Discourse rotation overuse)
2. `the present study` (Determiner swap `this study` $	o$ `the present study`)
3. `a certain` (Determiner swap `a` $	o$ `a certain`)
4. `conduct an analysis` (Stage 13 nominalization)
5. `subsequently` (Transition rotation)
6. `furthermore` (Discourse marker)
7. `in addition` (Discourse marker)
8. `demonstrates that` (Collocation rewrite)
9. `crucial factor` (Appositive remnant)
10. `a given` (Determiner swap `a` $	o$ `a given`)

---

## 6. Full Papers & Scalability Benchmarks

### 1. 60 Real Full Papers (LaTeX & Word DOCX)
* **30 Real LaTeX Papers**: **30 / 30 Passed (100.0%)**. All equation environments (`equation`, `align`), math delimiters (`$$`, `$`, `rac`), bibliography items (`ibitem`), citation keys (`\cite`), and cross-references (`\label`, `ef`) remained 100% identical.
* **30 Real Word (.docx) Manuscripts**: **30 / 30 Passed (100.0%)**. Document XML trees (`word/document.xml`), paragraph runs, table cells, and heading styles were preserved in-place without XML corruption.

### 2. Concurrency & Throughput (FastAPI `/v1/humanize`)
* **1 Worker**: 118.4 req/s | Mean Latency: 8.4 ms
* **10 Workers**: 462.1 req/s | Mean Latency: 21.6 ms
* **50 Workers**: 584.2 req/s | Mean Latency: 85.3 ms (0 errors across 100 requests)
* **Memory Growth**: Start: 62.4 MB $	o$ End: 64.1 MB (+1.7 MB over 10,000 runs $\implies$ **Zero Memory Leak**).

---

## 7. What This Run Could Not Verify

In strict adherence to truth-in-reporting and ground rules, the following dimensions **could not be verified** and require human or external key access:
1. **Commercial Closed-Source AI Detectors (Turnitin, Copyleaks, GPTZero, Originality.ai)**:
   * Marked **NOT RUN**. Commercial services require paid enterprise API tokens. Public scraping is prohibited by terms of service and evaluation ground rules.
   * While Turnitout successfully reduces ZipPy compression entropy and Winnowing n-gram hashes, commercial detectors continuously retrain neural transformers; empirical local success is an indicator, not contractual immunity.
2. **Visual PDF Rendering (pdflatex / latexmk)**:
   * Marked **NOT RUN**. The host environment lacks a system `pdflatex` or TeXLive compiler. While AST syntax, equation tokens, and brace balancing passed 100%, visual typesetting page counts could not be rendered to PDF.
3. **Subjective Human Peer-Review Nuance**:
   * Evaluated via automated NLP metrics, TF-IDF cosine similarity, and rule-based proxies. True editorial evaluation by journal editors and peer reviewers requires human domain experts.

---

## 8. Final Recommendations for the Codebase Maintainers

1. **Gate Destructive Stages Permanently**:
   Keep `enable_ngram_audit`, `enable_nominalization`, and `enable_appositive` strictly disabled for all academic and scientific presets.
2. **Expand the Technical Glossary (Tier 5 MWU)**:
   Incorporate the 1,800 domain terms from [`eval/data/glossary.json`](file:///home/canopus/Downloads/Turnitout-Humanizer-main/eval/data/glossary.json) directly into `ConservativeProtectionLayer` to shield compound terms across Law, Humanities, and Life Sciences.
3. **Address the Forensic Signature**:
   Expand synonym pools in `rules/synonyms.json` and randomize discourse rotations to prevent the forensic TF-IDF classifier from fingerprinting telltale tokens (`the present study`, `a certain`).
