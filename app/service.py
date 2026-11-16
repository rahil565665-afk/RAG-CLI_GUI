from __future__ import annotations

from .config import get_settings
from .gemini_client import GeminiAnswerGenerator
from .rag_service import RAGService
from .retrieval import BM25Retriever, KnowledgeBase


def build_service() -> RAGService:
    settings = get_settings()
    knowledge_base = KnowledgeBase.load(settings.kb_path)
    retriever = BM25Retriever(knowledge_base)
    generator = (
        GeminiAnswerGenerator(settings.gemini_api_key, settings.gemini_model)
        if settings.gemini_api_key
        else None
    )
    return RAGService(
        kb=knowledge_base,
        retriever=retriever,
        generator=generator,
        min_relevance=settings.min_relevance,
        top_k=settings.top_k,
    )
