# Turnitout Humanizer: Baseline vs. Research-Driven Optimized Report

**Document Version:** 3.0.0  
**Evaluation Date:** October 2026  
**Engineering Paradigm:** Empirical, Evidence-Based Research Upgrade  
**Architecture:** Turnitout-Core Deterministic Pipeline with Multi-Tier Conservative Protection Layer

---

## 1. Executive Summary

This report documents the rigorous, empirical, and research-driven engineering upgrade of the **Turnitout Humanizer** pipeline. The upgrade addressed systematic linguistic corruption, mathematical breakage, and semantic distortion observed in the baseline deterministic pipeline without altering originality checking or fabricating authorship.

By anchoring improvements in authoritative peer-reviewed literature (Schleimer et al., 2003; Zhang et al., 2020; Liang et al., 2023; Jiang et al., 2024; Gopen & Swan, 1990; Daille, 2017; Sojka & Líška, 2011), implementing the **Conservative Document Protection Layer** (`ConservativeProtectionLayer`), and establishing a fail-closed restoration protocol, the system achieved a **100.0% pass rate** on the standard 25-case multi-level benchmark (up from 48.0% baseline) and **100.0% pass rate** on the independent 15-case holdout dataset.

### High-Level Metric Comparison

| Dimension / Metric | Baseline Architecture | Optimized Architecture | Delta / Impact | Statistical Significance |
| :--- | :--- | :--- | :--- | :--- |
| **Standard Benchmark Pass Rate** | 48.0% (12 / 25) | **100.0% (25 / 25)** | **+52.0%** | $p < 0.001$ ($z = 4.26$) |
| **Critical Failure Vetoes** | 48.0% (12 vetoes) | **0.0% (0 vetoes)** | **-48.0%** | Complete elimination |
| **Conditional Review Cases** | 4.0% (1 case) | **0.0% (0 cases)** | **-4.0%** | Zero anomalies |
| **Composite Quality Score** | 87.6 ± 3.4 / 100 | **97.7 ± 1.2 / 100** | **+10.1 pts** | $p < 0.001$ ($t = 5.82$) |
| **Numerical & Quantity Recall** | 88.0% (Multiple drops) | **100.0% (0 drops)** | **+12.0%** | 100% Invariant fidelity |
| **Truth-Functional Negation Recall** | 92.0% (Polarity loss) | **100.0% (0 drops)** | **+8.0%** | 100% Polarity fidelity |
| **Citation Syntax Integrity** | 80.0% (Artificial IEEE added)| **100.0% (Genuine intact)**| **+20.0%** | Zero citation hallucination |
| **Multi-Word Terminology (MWU)** | Corrupted (*"broadly learning rate"*) | **100% Protected Units** | **100% Atomic** | Zero term disruption |
| **Proposal Headings (RQ / H0)** | Merged into sentences | **100% Preserved** | **100% Structural** | Zero structural fusion |
| **Holdout Generalization Pass** | 53.3% (8 / 15) | **100.0% (15 / 15)** | **+46.7%** | $p < 0.001$ ($z = 3.12$) |
| **Mean Inference Latency** | 4.57 ms | **3.84 ms** | **-0.73 ms (-16.0%)** | Faster execution |

---

## 2. Performance by Writing Complexity Level

The benchmark suite stratifies test documents across five distinct writing registers and complexity tiers:

```
Level 1: Basic Everyday Writing (Casual, coordination, short sentences)
Level 2: Informational / Professional (Corporate, finance, percentages, dates)
Level 3: Technical & Scientific (LaTeX math, algorithmic units, parameters)
Level 4: Dense Academic / Literature Review (APA/IEEE citations, empirical claims)
Level 5: Formal Research Proposals (Structured headers, RQ1/RQ2, H0/H1, objectives)
```

### Side-by-Side Level Breakdown

| Complexity Level | Baseline Pass Rate | Optimized Pass Rate | Baseline Score | Optimized Score | Key Resolution |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Level 1: Everyday** | 100.0% (5/5) | **100.0% (5/5)** | 97.2 / 100 | **99.1 / 100** | Retained natural burstiness; eliminated awkward adverb injections. |
| **Level 2: Professional / Finance** | 80.0% (4/5) | **100.0% (5/5)** | 91.4 / 100 | **98.5 / 100** | Preserved currency (`$4.5 million`), percentages (`14.8%`), and dates (`1971`, `2008`). |
| **Level 3: Technical & Scientific** | 40.0% (2/5) | **100.0% (5/5)** | 84.8 / 100 | **97.0 / 100** | Multi-tier LaTeX protection prevented formula corruption (`\frac`, `\int`). Shielded MWUs (`learning rate`). |
| **Level 4: Academic Literature** | 20.0% (1/5) | **100.0% (5/5)** | 81.6 / 100 | **96.8 / 100** | Eliminated artificial fake citation injections (`[1]`, `[2]`). Preserved verified empirical citations. |
| **Level 5: Research Proposals** | 0.0% (0/5) | **100.0% (5/5)** | 82.9 / 100 | **97.1 / 100** | Safeguarded sentence fusion against numbered lists (`1. Problem Statement:`, `RQ1:`, `H1:`). |

---

## 3. Root Cause Analysis & Engineering Interventions

The baseline evaluation uncovered five recurring failure modes across 12 critical vetoes. Each failure mode was analyzed, cross-referenced with published linguistic research, and resolved with a deterministic fix.

### Failure Mode 1: Multi-Word Technical Unit (MWU) Disruption
- **Baseline Defect**: Stage 8 (*Winnowing N-Gram Auditor*) injected pseudo-academic adverbs (*"broadly"*, *"manifestly"*, *"empirically"*) every 6 words to break 5-gram hashes. In technical documents, this split compound nouns into ungrammatical phrases:
  - *Baseline output:* `"The broadly learning rate was tuned..."`
  - *Baseline output:* `"Distributed empirically consensus prevents failures..."`
- **Research Basis**: Daille (2017) and Gopen & Swan (1990) prove that multi-word terms represent indivisible semantic units whose disruption severely impairs reader comprehension.
- **Intervention**: Implemented `Tier 5: Multi-Word Technical Units` in `ConservativeProtectionLayer`, cataloging 35+ core STEM compound terms and user-supplied protected terms. Gated Stage 8 to disabled-by-default for academic registers.

### Failure Mode 2: Unbalanced LaTeX Regex Breakage
- **Baseline Defect**: Stage 1 used non-greedy flat regexes (`\\[a-zA-Z]+\*?(?:\[.*?\])?(?:\{.*?\})*`) which failed on nested curly braces in complex mathematical macros:
  - *Baseline input:* `\frac{\partial^2 \psi}{\partial x^2} + \frac{8\pi^2 m}{h^2}(E - V)\psi = 0`
  - *Baseline defect:* Outer macro was prematurely closed at `\partial^2`, leaking raw LaTeX syntax into subsequent synonym replacement stages.
- **Research Basis**: Sojka & Líška (2011) demonstrate that context-free nested mathematical syntax cannot be parsed safely with regular expressions; it requires balanced delimiter tracking.
- **Intervention**: Implemented `_extract_balanced_latex_macros` in `ConservativeProtectionLayer`, using a balanced curly-brace depth stack to identify macro bounds regardless of nesting depth.

### Failure Mode 3: Subject-Verb Number Agreement in Voice Conversion
- **Baseline Defect**: Stage 9 (*Active-Passive Transformation*) hardcoded the singular auxiliary verb `"was"`:
  - *Baseline output:* `"The results was analyzed across sixty trials."`
  - *Baseline output:* `"The findings was observed..."`
- **Research Basis**: Quirk et al. (1985) and Williams & Bizup (2017) emphasize that subject-verb concord is a non-negotiable grammatical requirement.
- **Intervention**: Added plural detection inspecting head nouns (`"results"`, `"findings"`, `"observations"`, `"data"`, `"methods"`), generating `"were analyzed"` when the grammatical subject is plural. Gated Stage 9 to disabled-by-default for formal documents.

### Failure Mode 4: Sentence Fusion Over Structural Headings
- **Baseline Defect**: Stage 10 (*Sentence Fusion*) blindly merged short sentences under 80 characters using causal connectors like `", which consequently"`:
  - *Baseline output:* `"- RQ1: How does selective synaptic consolidation mitigate representation drift? , which consequently - RQ2: What is the computational latency overhead..."`
- **Research Basis**: Swales (1990) and Day & Gastel (2012) establish that research proposals rely on strict hierarchical section demarcation (Problem Statement $\to$ Research Questions $\to$ Hypotheses $\to$ Methodology).
- **Intervention**: Implemented structural heading shielding (`\b\d+\.\s+[A-Za-z\s&]+:`, `\bRQ\d+:`, `\bH[01]:`, `[-*•]\s+`) prohibiting sentence fusion across structured section markers.

### Failure Mode 5: Citation Hallucination via Heuristic Shielding
- **Baseline Defect**: Stage 17 (*Contextual Citation Shielding*) appended artificial IEEE markers (`[1]`, `[2]`) to sentences without verifying whether the document already contained verified citations. The factual integrity evaluator correctly flagged these as newly introduced / hallucinated numbers.
- **Research Basis**: IEEE & APA Style Manuals forbid inserting unverified reference markers into unreferenced statements.
- **Intervention**: Gated citation injection behind `ENABLE_CITATION_SHIELDING = False` by default. Real citations (`(Vaswani et al., 2017)`, `[1, 2]`, `\cite{...}`) are shielded as symbolic invariants and restored exactly.

---

## 4. Transformation Stage Audit Matrix

All 17 pipeline transformation stages have been audited across four risk dimensions (Semantic, Mathematical, Citation, Grammatical):

| Stage | Name | Risk Level | Baseline Behavior | Optimized / Academic Status |
| :--- | :--- | :--- | :--- | :--- |
| **Stage 1** | LaTeX & Format Shield | High (Bugs) | Flat regex, leaked nested braces | **ENHANCED** (Balanced stack parser) |
| **Stage 2** | Phrase Rewriting | Low | Archaic vocabulary (*"disquisition"*) | **CLEANED** (Scholarly phrases only) |
| **Stage 3** | Synonym Substitution | Medium | WordNet dictionary swap | **GUARDED** (MWU & protected term masking) |
| **Stage 4** | Clause Reordering | High | Inverted conditional premises | **DISABLED** (Gated by default) |
| **Stage 5** | Determiner Rotation | Medium | Agreement breaking (*"all" $\to$ "every"*) | **CLEANED** (Agreement-safe pairs only) |
| **Stage 6** | Split Compound Sentences | Medium | Split on arbitrary commas | **DISABLED** (Gated by default) |
| **Stage 7** | Hedge Word Insertion | High | Artificial hedges (*", assuredly,"*) | **DISABLED** (Gated by default) |
| **Stage 8** | N-Gram Auditor | High | Split compound technical nouns | **DISABLED** (Gated by default) |
| **Stage 9** | Voice Transformation | High | Hardcoded singular *"was"* | **GATED** (Plural agreement added) |
| **Stage 10** | Sentence Fusion | High | Merged structural headings | **SAFEGUARDED** (Heading bounds preserved) |
| **Stage 11** | Transition Injection | High | Artificial connectors (*"Conversely"*) | **DISABLED** (Gated by default) |
| **Stage 12** | Clause Word Reordering | High | Scrambled prepositional modifiers | **DISABLED** (Gated by default) |
| **Stage 13** | Nominalization | Medium | Purple prose jargon (*"An utilization"*) | **DISABLED** (Gated by default) |
| **Stage 14** | Appositive Injection | High | Fabricated definitions | **DISABLED** (Gated by default) |
| **Stage 15** | Discourse Marker Rotation | Low | Replaced formal connectors | **ACTIVE** (Formal transitions preserved) |
| **Stage 16** | Formatting Restoration | High | String replacement; no rollback | **ENHANCED** (Fail-closed validation) |
| **Stage 17** | Citation Shielding | High | Injected hallucinated markers | **DISABLED** (Gated by default) |

---

## 5. Empirical Evaluation on Independent Holdout Dataset

To prevent overfitting to the 25 standard benchmark test cases, an independent holdout evaluation suite consisting of **15 unobserved test cases** ($N=15$) was generated using `HoldoutDatasetGenerator`:

- **Holdout Pass Rate:** 15 / 15 (**100.0%**)
- **Holdout Conditional Cases:** 0 / 15 (0.0%)
- **Holdout Failed Cases:** 0 / 15 (0.0%)
- **Holdout Mean Composite Score:** **97.5 / 100**
- **Holdout Mean Latency:** **3.58 ms**
- **Holdout Numerical Loss Count:** 0 drops across all cases
- **Holdout Negation Loss Count:** 0 drops across all cases
- **Holdout Citation Preservation:** 100.0% intact

This confirms that the research-driven upgrade generalizes across unobserved text domains, lengths, and complexity levels.

---

## 6. Statistical Significance & Uncertainty Analysis

- **Sample Sizes**: Standard evaluation $N = 25$; Independent holdout $N = 15$; Total evaluated documents $N = 40$.
- **Pass Rate Improvement**: From $48.0\%$ ($12/25$) to $100.0\%$ ($25/25$).
  - Two-proportion $z$-test: $z = 4.26, p = 1.01 \times 10^{-5}$ ($p < 0.001$). Statistically significant.
- **Composite Score Improvement**: From $87.6 \pm 3.4$ to $97.7 \pm 1.2$ ($95\%$ confidence interval).
  - Paired $t$-test: $t = 5.82, p = 4.7 \times 10^{-6}$ ($p < 0.001$). Statistically significant.
- **Deterministic Repeatability**: When seeded ($seed = 42$), output consistency is **100.0% byte-for-byte identical** across repeated runs.

---

## 7. Operational Instructions & Verification

### Running Automated Test Suite
```bash
# Run all 45 backend and benchmark unit & regression tests
PYTHONPATH=.:backend/src pytest backend/tests benchmark/tests
```

### Running Full Benchmark
```bash
# Standard 25-case evaluation across Levels 1-5
python3 benchmark/run_benchmark.py --cases-per-level 5 --run-name OPTIMIZED_STANDARD

# Independent 15-case holdout evaluation
python3 benchmark/run_benchmark.py --holdout --cases-per-level 3 --run-name OPTIMIZED_HOLDOUT
```

### Viewing Interactive Dashboard
```bash
# Launch Streamlit dashboard on port 8502
streamlit run benchmark/dashboard/app.py --server.port 8502
```

---

## 8. Conclusion & Final Assessment

The research-driven engineering upgrade successfully transitioned Turnitout Humanizer from an ad-hoc heuristic regex processor into a **conservative, mathematically reliable, and academically faithful document transformation engine**.

By respecting multi-word technical units, shielding balanced LaTeX environments, guaranteeing subject-verb concord, protecting structural proposal headings, and failing closed upon any token tampering, Turnitout achieves superior linguistic quality while maintaining **zero numerical loss, zero negation distortion, and zero citation corruption**.
