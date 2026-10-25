# Turnitout Evaluation: Blockers & Unexecutable Components Log

This document records tools, models, APIs, and metrics that could not be run, along with the concrete technical reason and fallback strategy.

---

## Blocker 1: Commercial AI Detector APIs
* **Target Services**: GPTZero, Originality.ai, Copyleaks, Sapling
* **Status**: **NOT RUN**
* **Technical Reason**: Requires paid API credentials. User instructions mandate: *"Official APIs (GPTZero, Originality.ai, Copyleaks, Sapling) only if I provide keys; otherwise mark them NOT RUN. Do not create accounts on, scrape, or try to bypass any commercial detector."* No API keys were supplied.
* **Fallback Strategy**: Local open-source proxies (ZipPy information-theoretic compression/entropy detector, Karp-Rabin winnowing overlap, and a trained TF-IDF forensic fingerprint classifier).

---

## Blocker 2: PDFLaTeX / Latexmk Binary
* **Target Operation**: Direct visual PDF compilation of 30 LaTeX papers.
* **Status**: **NOT RUN**
* **Technical Reason**: `pdflatex`, `latexmk`, `xelatex`, and `lualatex` binaries are not installed on the host system.
* **Fallback Strategy**: In-depth structural syntax auditing: parsing equation environments, verbatim brace-depth verification, citation key sets, cross-reference labels, and macro integrity.

---

## Blocker 3: Local Large LLM Runtimes (Ollama / Llama.cpp)
* **Target Operation**: Dynamic on-device LLM text generation.
* **Status**: **NOT RUN**
* **Technical Reason**: Neither `ollama` nor `llama-cli` binary is installed on the host environment.
* **Fallback Strategy**: Utilization of public, peer-reviewed AI-labeled corpora (RAID, HC3, M4) with established ground truth.
