# canopus-humanizer

canopus-humanizer is a deterministic text humanization engine that applies rule-based linguistic variations while preserving technical formatting, numbers, in-text citations, and mathematical formulas (LaTeX).

## Backend Installation & Run

```bash
# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the API server (default: http://127.0.0.1:8080)
python backend/run_api.py
```

API documentation is available at `http://127.0.0.1:8080/docs`.

## Frontend

The user interface is served directly at `http://127.0.0.1:8080` once the backend is running. You can also open `docs/index.html` directly in any web browser.

## Example API Usage

**Request:**

```bash
curl -X POST http://127.0.0.1:8080/v1/humanize \
  -H "Content-Type: application/json" \
  -d '{"text": "Furthermore, it is important to examine the algorithm."}'
```

**Response:**

```json
{
  "success": true,
  "humanized_text": "Also, it is important to examine the algorithm.",
  "words_processed": 9,
  "modifications_count": 1,
  "latency_ms": 1.45,
  "telemetry": {
    "total_modifications": 1,
    "word_count": 9,
    "stages_applied": ["phrase_rewrite"]
  }
}
```

## License

All rights reserved.
