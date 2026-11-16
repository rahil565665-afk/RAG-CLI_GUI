from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_KB_PATH = PROJECT_ROOT / "data" / "northside_dental_knowledge_base.json"


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str | None
    gemini_model: str
    kb_path: Path
    top_k: int
    min_relevance: float
    rate_limit_per_minute: int


def get_settings() -> Settings:
    """Load local .env values without ever printing them."""
    load_dotenv(PROJECT_ROOT / ".env", override=False)
    key = os.getenv("GEMINI_API_KEY", "").strip() or None
    model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite").strip() or "gemini-3.5-flash-lite"
    kb_path = Path(os.getenv("NORTHSIDE_KB_PATH", str(DEFAULT_KB_PATH))).expanduser()
    try:
        top_k = int(os.getenv("TOP_K", "4"))
    except ValueError:
        top_k = 4
    try:
        min_relevance = float(os.getenv("MIN_RELEVANCE", "0.22"))
    except ValueError:
        min_relevance = 0.22
    try:
        rate_limit = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))
    except ValueError:
        rate_limit = 30
    return Settings(
        gemini_api_key=key,
        gemini_model=model,
        kb_path=kb_path,
        top_k=max(1, min(top_k, 5)),
        min_relevance=max(0.0, min(min_relevance, 1.0)),
        rate_limit_per_minute=max(1, min(rate_limit, 300)),
    )