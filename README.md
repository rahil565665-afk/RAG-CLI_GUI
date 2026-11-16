# Demo

A minimal web interface for the RAG assistant. Ask a question, receive an AI-generated response, and inspect any supporting source passages.

> Demo only. The included knowledge base is fictional. Do not enter personal or sensitive information.

## Run locally

Requirements: Python 3.11+ and a Gemini API key.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
```

Add your key to `.env`, then start the app:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open http://127.0.0.1:8000.

## Deploy with Docker

Build and run locally:

```bash
docker build -t rag-demo .
docker run --rm -p 8000:8000 --env-file .env rag-demo
```

To deploy, connect this repository to a host that supports Docker builds, select the included `Dockerfile`, and configure `GEMINI_API_KEY` as a secret environment variable. Set `GEMINI_MODEL` only when you need a model other than the default. The app listens on the host-provided `PORT` (or 8000 locally) and exposes `/health` for health checks.

No deployment has been configured or performed.

## How it works

The browser sends a question to `POST /api/chat`. FastAPI validates the request, BM25 searches the local JSON knowledge base, and Gemini generates a structured answer from the question and selected passages. The server validates the model output and attaches trusted source metadata.

The JSON response includes `answer`, `sources`, `confidence_score`, and `answerable`. The score is a retrieval-support indicator, not a probability of correctness. Questions without supporting local material can still receive a Gemini-generated answer, but have no sources and a score of zero.

## Configuration

Copy `.env.example` to `.env` and set:

- `GEMINI_API_KEY` — required.
- `GEMINI_MODEL` — optional; defaults to the model in the example file.
- `TOP_K` — optional number of retrieved passages (1–5).
- `MIN_RELEVANCE` — optional BM25 relevance threshold.
- `RATE_LIMIT_PER_MINUTE` — optional per-process request limit.

Keep `.env` private. Do not commit API keys.

## Tests

```bash
python -m pytest -q
```

Tests use mocked model responses and do not call the live Gemini API.

## Stack

FastAPI, Uvicorn, Google Gen AI SDK, Pydantic, python-dotenv, plain HTML/CSS/JavaScript, and pytest.

This is a small demo, not a production clinical system. The rate limiter is process-local; a multi-instance deployment should use a shared rate limiter. Do not use it with real patient information.
