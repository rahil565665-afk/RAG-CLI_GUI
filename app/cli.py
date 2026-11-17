from __future__ import annotations

import argparse
import json
import sys
from typing import Sequence

from .config import get_settings
from .gemini_client import GeminiAnswerGenerator, GeminiProviderError
from .rag_service import RAGService
from .retrieval import BM25Retriever, KnowledgeBase


def build_service(top_k: int | None = None) -> RAGService:
    settings = get_settings()
    kb = KnowledgeBase.load(settings.kb_path)
    retriever = BM25Retriever(kb)
    generator = (
        GeminiAnswerGenerator(settings.gemini_api_key, settings.gemini_model)
        if settings.gemini_api_key else None
    )
    return RAGService(
        kb=kb,
        retriever=retriever,
        generator=generator,
        min_relevance=settings.min_relevance,
        top_k=top_k or settings.top_k,
    )


def _emit(payload: dict, compact: bool) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=None if compact else 2))


def run_query(service: RAGService, query: str, compact: bool = False) -> int:
    try:
        result = service.answer(query)
        _emit(result.model_dump(), compact)
        return 0
    except GeminiProviderError as exc:
        _emit({"error": {"code": exc.error_code, "message": str(exc)}}, compact)
        return 3
    except RuntimeError as exc:
        message = str(exc)
        code = "MISSING_API_KEY" if "GEMINI_API_KEY" in message else "SERVICE_ERROR"
        _emit({"error": {"code": code, "message": message}}, compact)
        return 2
    except ValueError as exc:
        _emit({"error": {"code": "INVALID_QUERY", "message": str(exc)}}, compact)
        return 2
    except Exception:
        # Do not expose stack traces, local paths, or environment values to CLI output.
        _emit({"error": {"code": "INTERNAL_ERROR", "message": "The CLI could not complete the request."}}, compact)
        return 4


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="northside-rag",
        description="Ask the fictional Northside Dental Clinic knowledge base. Returns structured JSON.",
    )
    parser.add_argument("query", nargs="*", help="Question to ask (multiple unquoted words are accepted); omit to start interactive mode")
    parser.add_argument("--top-k", type=int, choices=range(1, 6), default=None, help="Number of chunks sent to Gemini (1-5)")
    parser.add_argument("--compact", action="store_true", help="Print compact JSON on one line")
    # Accept both a quoted query and an ordinary multi-word PowerShell command.
    # parse_intermixed_args also allows options before or after the question.
    args = parser.parse_intermixed_args(argv)

    try:
        service = build_service(args.top_k)
    except Exception:
        _emit({"error": {"code": "KNOWLEDGE_BASE_ERROR", "message": "Could not load the local knowledge base. Check NORTHSIDE_KB_PATH and the data file."}}, args.compact)
        return 4

    query = " ".join(args.query).strip()
    if query:
        return run_query(service, query, args.compact)

    print("Northside Dental RAG CLI — fictional demo data only.")
    print("Enter a question, or type 'exit' to quit. Do not enter real patient information.")
    while True:
        try:
            query = input("\nQuestion> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if query.lower() in {"exit", "quit"}:
            return 0
        if not query:
            continue
        code = run_query(service, query, args.compact)
        if code not in {0}:
            # Continue interactive use after a provider/configuration error.
            continue


if __name__ == "__main__":
    raise SystemExit(main())