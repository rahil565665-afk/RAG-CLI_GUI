from __future__ import annotations

from collections import defaultdict, deque
from pathlib import Path
from time import monotonic

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import get_settings
from .gemini_client import GeminiProviderError
from .schemas import HealthResponse, QueryRequest, QueryResponse
from .service import build_service

ROOT = Path(__file__).resolve().parents[1]
settings = get_settings()
service = build_service()

app = FastAPI(
    title="Demo API",
    version="1.0.0",
    description="A minimal web interface for a retrieval-augmented generation demo.",
)
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
_requests: dict[str, deque[float]] = defaultdict(deque)


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    if request.url.path == "/api/chat":
        key = request.client.host if request.client else "unknown"
        now = monotonic()
        bucket = _requests[key]
        while bucket and now - bucket[0] > 60:
            bucket.popleft()
        if len(bucket) >= settings.rate_limit_per_minute:
            return JSONResponse(status_code=429, content={"detail": "Too many requests. Please try again shortly."})
        bucket.append(now)
    return await call_next(request)


@app.exception_handler(RequestValidationError)
async def validation_error(_: Request, __: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Enter a question of up to 2,000 characters."},
    )


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="demo-rag",
        knowledge_base_chunks=len(service.kb.chunks),
        gemini_configured=bool(settings.gemini_api_key),
    )


@app.post("/api/chat", response_model=QueryResponse)
def chat(request: QueryRequest) -> QueryResponse:
    try:
        return service.answer(request.query)
    except GeminiProviderError as exc:
        status_code = 429 if exc.status_code == 429 else 503
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    except RuntimeError as exc:
        message = str(exc)
        if "GEMINI_API_KEY" in message:
            raise HTTPException(
                status_code=503,
                detail="The demo is not configured yet. Set GEMINI_API_KEY in the server environment.",
            ) from exc
        raise HTTPException(status_code=503, detail="The answer service is temporarily unavailable.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
