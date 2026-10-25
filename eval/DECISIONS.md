# Turnitout Independent Evaluation: Architectural Decisions Log

This document records all methodological, architectural, and runtime decisions made during the autonomous end-to-end evaluation.

---

## Decision 1: Hardware-Calibrated Sampling Tier (Host Profile Adaptation)
* **Context**: The evaluation is executing on an Intel Core i5-6300U dual-core CPU with 8 GB RAM and no dedicated GPU.
* **Decision**: We calibrate the evaluation corpus to **300 diverse documents** (150 human, 150 AI) spanning all 9 required disciplines and 5 length buckets, plus **60 real full papers** (30 real `.tex` LaTeX papers and 30 real `.docx` manuscripts).
* **Rationale**: Running the full 16-condition matrix ({academic, technical, standard, conversational} × {25, 50, 75, 100}) on 300 documents yields **4,800 full pipeline runs**. On this dual-core machine (~3.8 ms/run), this completes in minutes while maintaining statistical significance ($N=300 \implies \pm 5.6\%$ margin of error at 95% confidence).

---

## Decision 2: AI Text Source Policy (No Paid APIs / Public Ground Truth)
* **Context**: User instructions mandate: *"No API keys: use only public datasets and free local models. Do not generate AI text through paid APIs. If a local LLM runtime such as Ollama or llama.cpp is available, use it to generate AI text. Otherwise rely only on the AI-labelled public datasets (RAID, M4, HC3, MAGE)."*
* **Decision**: Neither Ollama nor llama.cpp is installed on the host. We rely strictly on verified public datasets with labeled AI outputs (RAID, HC3, M4, and curated pre-2020 arXiv/PubMed/S2ORC human ground-truth texts).
* **Rationale**: Eliminates synthetic generation bias, guarantees zero API expenditure, and provides known, peer-reviewed ground-truth labels.

---

## Decision 3: Commercial Detectors & LaTeX Compiler Handling
* **Context**: Commercial detector APIs (GPTZero, Originality.ai, Copyleaks, Sapling) require paid authentication keys, and `pdflatex`/`latexmk` binaries are not installed on this host environment.
* **Decision**:
  1. Mark commercial detectors as **NOT RUN (no public API key provided; scraping prohibited by ground rules)**.
  2. Mark PDF visual rendering as **NOT RUN (no pdflatex compiler binary on host)**.
  3. Perform exhaustive AST, macro-level, and balance verification for LaTeX files: verify equation count and string invariance, citation keys, cross-references (`\label`/`\ref`), and environment closures (`\begin{...}`/`\end{...}`).
  4. Perform deep XML round-trip diffing on all 30 DOCX files (`word/document.xml`, `word/styles.xml`).

---

## Decision 4: Automated Quality Judging & Local Proxy
* **Context**: Human evaluation is replaced with automated metrics.
* **Decision**: We run:
  1. Hard Invariant checks (numbers, LaTeX formulas, citations, negations, units, technical glossary terms).
  2. TF-IDF and N-gram cosine semantic similarity.
  3. Word-sense validity checks against WordNet / vocabulary distributions.
  4. Grammar, readability, and burstiness deltas.
  5. An automated rule-based proxy evaluator for the 300-pair stratified sample (explicitly labeled *"automated proxy, not human evaluation"*).
