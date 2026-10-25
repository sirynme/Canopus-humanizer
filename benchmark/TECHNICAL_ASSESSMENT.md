# Turnitout Humanizer: Technical Assessment & Codebase Inspection

**Date**: 2026-10-25  
**Version**: Core v2.6.0  
**Evaluator**: Automated AI Humanizer Benchmarking and Trust Evaluation System  

---

## 1. Executive Summary & Architecture Overview

Turnitout is a **deterministic, rule-based text transformation pipeline** designed to evade plagiarism detection (specifically Karp-Rabin Winnowing algorithms such as Turnitin) and heuristic AI detection models. 

Unlike generative AI humanizers (e.g., fine-tuned LLaMA or GPT-based paraphrasers), Turnitout executes **zero LLM inference** at runtime. Instead, it processes text through a sequential 17-stage linguistic heuristic pipeline implemented in Python using regular expressions, lookup tables, and stochastic rule triggers.

### Architectural Component Map
```
┌────────────────────────────────────────────────────────┐
│               Input Interfaces                         │
│  - REST API: POST /v1/humanize (FastAPI on Port 8080)   │
│  - CLI: turnitout.cli (--text, --file, --intensity)     │
│  - Python Library: turnitout.core.modifier.DocumentModifier
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│           17-Stage Deterministic Pipeline              │
│  1. LaTeX / Code / HTML Protection (\x00_LTX_...)       │
│  2. Phrase Rewriting (Curated JSON substitutions)       │
│  3. Synonym Replacement (Aligned confidence scoring)    │
│  4. Clause Reordering (Subordinate & relative clauses)  │
│  5. Determiner Swapping (the <-> this/that)             │
│  6. Compound Splitting (Splits sentences on 'and/but')  │
│  7. Hedge Words Injection ("evidently", "reliably")    │
│  8. 5-Gram Winnowing Chain Breakers                     │
│  9. Voice Inversion (Active <-> Passive heuristic)      │
│ 10. Sentence Fusion (Adjacent sentence merging)         │
│ 11. Transition Injection ("Furthermore", "Crucially")  │
│ 12. Clause Word Reordering                              │
│ 13. Nominalization (Verb <-> Noun phrase)               │
│ 14. Appositive Injection (Academic parentheticals)      │
│ 15. Discourse Marker Rotation (However -> Conversely)   │
│ 16. LaTeX / Formatting Restoration                      │
│ 17. Contextual Citation Injection (IEEE/APA/LaTeX)      │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│               Output & Telemetry                       │
│  - Transformed Text                                    │
│  - Latency (ms)                                        │
│  - Modifications Counter                               │
│  - Optional BibTeX Package (citations.bib)             │
└────────────────────────────────────────────────────────┘
```

---

## 2. Model & Inference Engine Identification

| Dimension | Implementation Details |
| :--- | :--- |
| **Model Type** | **Rule-Based Heuristic / Deterministic Regex Engine** (No Neural Weights) |
| **Model Version** | Core 2.6.0 |
| **Prompts** | JSON rule sets (`backend/rules/*.json`) contain `__prompt__` metadata headers used during dataset generation; runtime engine strips these via `clean_rule_data()` and performs direct dictionary/regex lookups. |
| **Inference Engine** | Pure Python standard library (`re`, `random`, `json`, `math`, `collections`, `zlib`, `lzma`). |
| **Token Usage** | **0 tokens** (No external or local LLM tokens consumed). |
| **Execution Latency** | **Sub-millisecond to ~15ms** per document. |
| **Determinism** | Fully deterministic when `seed` is fixed (`DocumentModifier(seed=42)`). Semi-stochastic when seed is unspecified. |

---

## 3. Input & Output Interfaces

The humanizer can be invoked via three independent channels:

1. **Direct Python Library Invocation**:
   ```python
   from turnitout.core.modifier import DocumentModifier
   modifier = DocumentModifier(config=config, seed=seed)
   humanized_text = modifier.modify_document(
       text=input_text,
       protected_terms=set(["PyTorch", "CRISPR"]),
       enable_citations=False
   )
   ```
2. **FastAPI REST Service (`backend/run_api.py`)**:
   - Running locally at `http://127.0.0.1:8080/v1/humanize`.
   - Payload: `{"text": str, "intensity": float, "style": str, "protected_terms": list, "seed": int}`.
   - Response: `{"success": bool, "humanized_text": str, "latency_ms": float, "modifications_count": int, "telemetry": dict}`.
3. **Command Line Interface (`backend/src/turnitout/cli.py`)**:
   ```bash
   python3 backend/src/turnitout/cli.py --text "Input sentence" --intensity 75 --style academic
   ```

---

## 4. Existing Evaluation & Quality Tools in Codebase

1. **`ZipPyChecker` (`backend/src/turnitout/core/checker.py`)**:
   - Calculates **Shannon Entropy** ($H(X) = -\sum p(x) \log_2 p(x)$).
   - Computes **zlib and lzma compression ratios** ($\frac{\text{compressed bytes}}{\text{raw bytes}}$).
   - Audits 9 formulaic AI phrases (*"delve into"*, *"comprehensive tapestry"*, *"stands as a testament"*).
   - Produces an heuristic `ai_probability` (0.0 to 98.0%) and `human_score`.
2. **`WinnowingEngine` (`backend/src/turnitout/core/winnowing.py`)**:
   - Extracts Karp-Rabin hashes of sliding $k$-grams ($k=5, w=4$).
   - Calculates Jaccard similarity index between original and transformed documents.

---

## 5. Technical Assessment: Verified Capabilities & Critical Risks

### ✅ Verified Working Capabilities:
- **High throughput & ultra-low latency**: Processes standard paragraphs in < 10ms.
- **5-Gram Plagiarism Disruption**: Systematically alters word sequences to drop exact Winnowing fingerprint matches.
- **LaTeX Math Shielding**: Equations inside `$..$`, `$$..$$`, and `\[..\]` are shielded from string replacement.
- **Protected Terms**: Honor list of user-specified terms to prevent synonym substitution on known keywords.

### ⚠️ Critical Architectural Risks & Known Flaws:
1. **Unnatural Adverb Injections in Technical Phrases**:
   - *Evidence*: Heuristic hedge injection inserts adverbs like `"broadly"` or `"reliably"` into compound technical nouns (e.g., transforming `"learning rate"` into `"broadly learning rate"`).
2. **Grammar & Syntax Corruption**:
   - Rule-based passive/active voice inversion relies on regex patterns that do not parse dependency trees. Complex verb tenses or subordinate clauses can produce ungrammatical sentences.
3. **Potential Meaning Inversion / Hallucination**:
   - Nominalization and appositive injection introduce synthetic qualifiers (`", a crucial factor,"`) that were not asserted in the original text.
4. **Citation Fabrication**:
   - Stage 17 generates synthetic citations matching keywords from predefined JSON taxonomies (e.g. inserting IEEE `[1]` linked to a generated bibliography entry) rather than verifying real scholarly sources.

---

## 6. What Needs to Be Built in the Benchmarking System

1. **5-Level Automated Benchmark Dataset Generator** (everyday writing to multi-section research proposals).
2. **Independent Holdout Dataset Generator** for bias-free final evaluation.
3. **Six Discrete Evaluator Modules** (Language Quality, Semantic Preservation, Factual Integrity, Academic Quality, AI Detection Adapter, Operational Reliability).
4. **Scoring Engine with Critical Failure Vetoes** (factual/numerical corruptions or negation inversions must automatically trigger FAIL verdicts).
5. **Interactive Dashboard & Standalone HTML/JSON/CSV Reports**.
6. **Automated Trust Assessment Generator** directly addressing all 9 trust criteria.
