# Code — reference implementation

This directory contains a sanitised reference implementation of the AI
price-quotation pipeline that was prototyped during the demonstration
project. It is intentionally **domain-agnostic**: no real credentials,
cluster names, business field names or company data are included.

See the repository root [README](../README.md#technical-implementation)
for the technical overview that describes how these modules fit together.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in your own keys / URI
```

## Layout

| Path | Purpose |
| :--- | :--- |
| `src/config.py` | `.env` loading |
| `src/openai_helpers.py` | OpenAI client + embedding call with exponential-backoff retry |
| `src/mongo_helpers.py` | MongoDB Atlas connection helpers (URI from env) |
| `src/document_utils.py` | Dictionary cleaning, JSON→YAML conversion, PDF text extraction |
| `src/vector_search.py` | Generic Atlas `$vectorSearch` and metadata-`$match` helpers |
| `src/assistants_pipeline.py` | Four-step OpenAI Assistants pipeline for markup estimation |
| `app/app.py` | Flask UI that polls a long-running background pipeline |
| `app/templates/`, `app/static/` | Minimal front-end (HTML/JS/CSS) |
| `ollama/Modelfile` | Local-LLM (Llama 3.1) Modelfile used during evaluation |

## Running the demo UI

```bash
export PYTHONPATH="$(pwd)"
python app/app.py
```

The shipped `run_pipeline()` is a placeholder generator — replace it with
your own generator that yields `(step_number, message)` tuples to wire in
the real pipeline.
