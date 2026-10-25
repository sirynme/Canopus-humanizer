# ⚡ Turnitout Core Backend Engine (v2.6.0)

> **Deterministic, Privacy-First AI Footprint Removal & Academic Citation Engine**  
> *Zero Generative AI Hallucinations • Winnowing Hash Disruption • Sub-150ms Latency • In-Place DOCX & LaTeX Preservation*

---

## 1. Architectural Overview

Turnitout Core is a 100% programmatic, zero-retention document humanization and detection evasion system. Unlike commercial tools that use generative LLM paraphrasers (which leave new statistical AI footprints and hallucinate citations), Turnitout uses a **17-stage deterministic transformation pipeline** targeting both:
1. **Plagiarism Similarity**: Breaks Turnitin's Winnowing algorithm ($k=5, w=4$ Karp-Rabin rolling hashes) ensuring no 8-word sequence survives intact.
2. **AI Detection**: Disrupts Perplexity, Burstiness, Token Probability, Entropy, and Stylometric Uniformity used by Turnitin, GPTZero, CopyLeaks, and ZeroGPT.

---

## 2. Directory Layout

```
backend/
├── configs/
│   └── global_config.json        # Central source of truth (whitelist, offload, pipeline defaults)
├── rules/                        # Decoupled linguistic assets (Strictly no hardcoded words in code)
│   ├── synonyms.json             # Rare academic synonyms
│   ├── phrases.json              # Multi-word phrase rewrite patterns
│   ├── hedge_words.json          # Entropy injection adverbs
│   ├── determiners.json          # High-frequency determiner substitutions
│   ├── conjunctions.json         # Clause split & reorder triggers
│   ├── transitions.json          # Categorized discourse transitions
│   ├── nominalizations.json      # Verb ↔ noun structural mutations
│   ├── appositives.json          # Technical definition entropy bombs
│   ├── discourse_markers.json    # Anti-repetition discourse rotators
│   ├── protected_terms.json      # Mathematical entities & frameworks safety net
│   └── academic/taxonomy/        # 5 Disciplines (CS, Physics, Math, Finance, Medicine)
├── src/turnitout/
│   ├── config.py                 # Configuration namespace loader
│   ├── core/
│   │   ├── __init__.py           # Invariant: clean docstring only
│   │   ├── rules.py              # Dynamic rule & taxonomy loader (__prompt__ stripper)
│   │   ├── modifier.py           # Unified 17-stage mathematical transformation engine
│   │   ├── citation_engine.py    # Contextual citation matcher & BibTeX/JSON generator
│   │   ├── doc_processor.py      # In-place DOCX, LaTeX, TXT, and in-memory ZIP bundler
│   │   ├── checker.py            # ZipPy zlib/lzma entropy & perplexity AI detector
│   │   └── winnowing.py          # Karp-Rabin & Winnowing k=5, w=4 similarity engine
│   ├── api/
│   │   ├── schemas.py            # Pydantic schemas matching ENTERPRISE_API.md
│   │   └── routes.py             # Enterprise REST endpoints (/v1/humanize, /v1/citations)
│   ├── cli.py                    # Production command-line orchestrator
│   └── ui/                       # Streamlit multi-page interface views
├── streamlit_app.py              # Streamlit web application entry point
├── run_api.py                    # FastAPI ASGI uvicorn launcher
└── tests/                        # 100% passing automated test suite
```

---

## 3. Quick Start & Execution

### A. Run CLI Tool
```bash
# Transform direct text with verbose breakdown
python3 src/turnitout/cli.py --text "In conclusion, this research paper plays a pivotal role in finite difference modeling." --verbose

# Run with maximum aggressiveness and citation insertion
python3 src/turnitout/cli.py --file input.docx --output output.docx --max-aggressiveness --citations 2
```

### B. Launch FastAPI Enterprise REST Service
```bash
python3 run_api.py
```
- Interactive Swagger API Documentation: **http://localhost:8000/docs**
- Health Probe: `GET http://localhost:8000/v1/health`
- Humanize Endpoint: `POST http://localhost:8000/v1/humanize`

### C. Launch Interactive Streamlit Web UI
```bash
streamlit run streamlit_app.py --server.port 8501
```

---

## 4. Production REST API Endpoints

### `POST /v1/humanize`
Request:
```json
{
  "text": "Furthermore, our experimental findings demonstrate that deep learning models introduce formulaic syntax.",
  "intensity": 75.0,
  "style": "academic",
  "protected_terms": ["ResNet-50", "PyTorch"],
  "enable_citations": true,
  "max_citations": 1,
  "citation_format": "IEEE [1]"
}
```
Response (`200 OK`):
```json
{
  "success": true,
  "humanized_text": "Additionally, our experimental findings attest that deep learning models frequently introduce formulaic syntax. [1]",
  "words_processed": 14,
  "modifications_count": 5,
  "latency_ms": 32.14,
  "citation_count": 1,
  "bib_text": "% === AI AUTO-FILL INSTRUCTIONS ===\n@article{...}",
  "telemetry": {
    "total_modifications": 5,
    "stages_applied": ["phrase_rewrite", "synonyms", "transition_inject"]
  }
}
```

---

## 5. Running the Test Suite
```bash
PYTHONPATH=src pytest tests/
```
All tests validate prompt metadata stripping, all 17 transformation stages, citation formatting, in-place document preservation, and sub-150ms latency.
