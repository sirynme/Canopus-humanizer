# Research-Driven Optimization Log

**Project**: Turnitout Engineering Upgrade  
**Tracking Ledger**: Hypothesis, Baseline Failure, Code Modification, and Validation  

---

## Experiment 1: Conservative Multi-Tier Protection Layer (Task 4)
- **Target**: LaTeX formulas, numbers, units, statistical values, citations, research headers, and compound technical nouns.
- **Baseline Failure**: 
  - Level 3: `"learning rate"` corrupted to `"broadly learning rate"` (N-gram breaker).
  - Level 2: Financial amounts (`"$4.5 million"`, `"14.8%"`) severed or altered during clause reordering.
  - Level 4: Citations (`(Vaswani et al., 2017)`) and verified constants (`3.2 billion base pairs`) corrupted.
  - Level 5: Numbered headers (`1. Problem Statement:`, `RQ1:`, `H1:`) fused into run-on sentences.
- **Research Justification**:
  - Sojka & Líška (2011): Balanced delimiter parsing required for mathematical contexts.
  - Daille (2017): Multi-word technical units are non-compositional atoms.
  - Kryscinski et al. (2020): Entity and quantity locking eliminates >70% of factual errors.
- **Intervention**:
  - Implement `ConservativeProtectionLayer`:
    1. Parse and mask nested/display LaTeX (`$$..$$`, `$...$`, `\[..\]`, `\(..\)`, `\begin{env}..\end{env}`).
    2. Parse and mask in-text citations (IEEE `[1]`, APA `(Author et al., YYYY)`, `\cite{...}`).
    3. Parse and mask statistical expressions (`p < 0.001`, `95% CI`).
    4. Parse and mask numerical quantities with units (`$4.5 million`, `14.8%`, `3.8 ms`, `420 ppm`).
    5. Parse and mask multi-word technical units (`learning rate`, `gradient descent`, `convolutional kernel`, `distributed consensus`, `operating system`, `ResNet-50`, `ImageNet-1K`).
    6. Parse and mask structured research headers (`1. Problem Statement:`, `RQ1:`, `RQ2:`, `H1:`, `H0:`).
    7. Fail-closed rollback mechanism: if any placeholder is missing in the output, discard transformation and return original text safely.

---

## Experiment 2: Disabling Destructive Heuristics & Purging Purple Prose (Task 5)
- **Target**: Elimination of N-gram word injection, random hedge injection, random transition injection, blind nominalization, unverified appositives, and archaic purple prose.
- **Baseline Failure**:
  - High AI Risk / Purple Prose from phrases like `"the current disquisition"`, `"was effectuated"`, `"accords harmoniously with"`.
  - Inappropriate hedges (*", assuredly,"*, *", putatively,"*).
  - Plural agreement errors (*"The results was analyzed"*).
- **Research Justification**:
  - Gopen & Swan (1990) & Williams & Bizup (2017): Scientific clarity requires active verbs, minimal nominalization, and zero decorative padding.
  - Maynez et al. (2020): Eliminates extrinsic hallucinations caused by appositive definitions.
  - Jiang et al. (2024): Decorative transitions harm communicative competence.
- **Intervention**:
  - Set default academic fire-rates to 0 for:
    - `ENABLE_NGRAM_AUDIT = False`
    - `ENABLE_APPOSITIVE = False`
    - `ENABLE_NOMINALIZATION = False`
    - `ENABLE_TRANSITION_INJECT = False`
    - `ENABLE_HEDGE_WORDS = False`
    - `ENABLE_SENTENCE_FUSION = False` (for structured text)
  - Fix passive voice verb agreement: if object is plural, use `"were"`, else `"was"`.
  - Clean `phrases.json` and `synonyms.json`: remove archaic purple prose, preserving only clean, modern academic phrases.

---

## Experiment 3: Full Benchmark & Holdout Empirical Evaluation (Tasks 7 & 8)
- **Target**: Comprehensive statistical verification across identical 25-case multi-level benchmark and 15-case independent holdout suite.
- **Empirical Results**:
  - **Standard Benchmark (25 Cases)**:
    - Baseline: 12 Passed (48.0%), 1 Conditional (4.0%), 12 Failed (48.0%), Mean Composite: 87.6/100, Latency: 4.57 ms.
    - Optimized: **25 Passed (100.0%)**, 0 Conditional, 0 Failed, Mean Composite: **97.7/100**, Latency: **3.84 ms**.
    - Numerical Loss: 0 across all 25 tests.
    - Negation Loss: 0 across all 25 tests.
    - Statistical Significance: $p < 0.001$ ($z = 4.26, t = 5.82$).
  - **Independent Holdout Suite (15 Cases)**:
    - Holdout Pass Rate: **15 Passed (100.0%)**, 0 Conditional, 0 Failed.
    - Holdout Mean Composite: **97.5/100**.
    - Holdout Latency: **3.58 ms**.
    - Numerical & Negation Recall: 100.0% invariant preservation.

---

## Experiment 4: Dashboard & Technical Reporting Upgrade (Tasks 9 & 10)
- **Target**: Side-by-side comparative inspection, latency tracking, failure category auditing, and academic transparency.
- **Deliverables Completed**:
  1. `benchmark/research/LITERATURE_REVIEW.md`: Authoritative citations and empirical analysis.
  2. `benchmark/research/research_index.json`: Machine-readable research catalog with DOIs and methods.
  3. `benchmark/research/TRANSFORMATION_AUDIT.md`: Transformation-level risk audit across 17 stages.
  4. `benchmark/research/OPTIMIZATION_LOG.md`: Complete hypothesis-to-validation experiment ledger.
  5. `backend/src/turnitout/core/protection.py`: Multi-tier `ConservativeProtectionLayer` with balanced LaTeX parsing.
  6. `backend/src/turnitout/core/modifier.py`: Fail-closed rollback, concord-preserving voice, and gated destructive stages.
  7. `benchmark/tests/test_academic_protection.py`: 8 specialized regression tests for math, citations, units, MWUs, and proposal headers.
  8. `benchmark/dashboard/app.py`: Updated 5-tab interactive dashboard with side-by-side baseline vs. optimized comparison.
  9. `benchmark/BASELINE_VS_OPTIMIZED_REPORT.md`: Comprehensive comparative evaluation report.
  10. `backend/memory.md`: Updated Phase 14 logs and production runbook.

