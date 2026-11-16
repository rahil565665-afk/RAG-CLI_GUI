from __future__ import annotations

import re
from typing import Protocol

from .retrieval import BM25Retriever, KnowledgeBase, RetrievedChunk
from .schemas import QueryResponse, SourceCitation, GeminiDraft

EMERGENCY_PATTERNS = [
    re.compile(r"\b(difficulty|trouble|unable|cannot|can't)\s+(breathing|breathe|swallowing|swallow)\b", re.I),
    re.compile(r"\b(rapidly|quickly)\s+(spreading\s+)?(facial\s+|face\s+|neck\s+)?swelling\b", re.I),
    re.compile(r"\b(swelling|swollen)\b.{0,50}\b(spreading|spreads|getting worse quickly|rapidly worsening)\b", re.I),
    re.compile(r"\b(uncontrolled|heavy|severe)\s+bleeding\b", re.I),
    re.compile(r"\bbleeding\b.{0,45}\b(won't stop|will not stop|uncontrolled)\b", re.I),
    re.compile(r"\b(severe|serious)\s+facial\s+(trauma|injury)\b", re.I),
    re.compile(r"\b(loss of consciousness|lost consciousness|unconscious|passed out|altered awareness|fainted)\b", re.I),
]
MIN_QUERY_COVERAGE = 0.60

class AnswerGenerator(Protocol):
    def generate(self, query: str, retrieved: list[dict]) -> GeminiDraft: ...


def is_emergency_query(query: str) -> bool:
    return any(pattern.search(query) for pattern in EMERGENCY_PATTERNS)


def _confidence_score(item: RetrievedChunk) -> float:
    """Return a 0-100 retrieval-support score, not a calibrated probability."""
    if item.raw_score == float("inf"):
        return 100.0

    bm25_strength = item.raw_score / (item.raw_score + 1.0)
    score = 100.0 * item.query_coverage * (0.75 + 0.25 * bm25_strength)
    return round(max(0.0, min(score, 100.0)), 1)


def _citation(item: RetrievedChunk) -> SourceCitation:
    chunk = item.chunk
    return SourceCitation(
        chunk_id=chunk["chunk_id"],
        section_id=chunk["section_id"],
        section_title=chunk["section_title"],
        subsection=chunk["subsection"],
        source_document=chunk["source_document"],
        source_pages=chunk["source_pages"],
        relevance_score=round(item.relevance_score, 4),
    )


class RAGService:
    def __init__(self, kb: KnowledgeBase, retriever: BM25Retriever, generator: AnswerGenerator | None,
                 min_relevance: float = 0.12, top_k: int = 4):
        self.kb = kb
        self.retriever = retriever
        self.generator = generator
        self.min_relevance = min_relevance
        self.top_k = max(1, min(top_k, 5))

    def answer(self, query: str) -> QueryResponse:
        normalized_query = query.strip()
        if not normalized_query:
            raise ValueError("Query must not be empty")
        if len(normalized_query) > 2000:
            raise ValueError("Query must be 2,000 characters or fewer")

        # Deterministic safety backstop runs before normal generation and does not wait for Gemini.
        if is_emergency_query(normalized_query):
            emergency = self.retriever.by_id("NSDC-07-001")
            sources = [_citation(emergency)] if emergency else []
            return QueryResponse(
                answer=("This may be an emergency. Contact your local emergency services immediately. "
                        "Do not wait for a routine dental appointment or continue this CLI workflow. "
                        "This is a fictional demo and does not determine the cause of symptoms."),
                sources=sources,
                confidence_score=100.0 if emergency else 0.0,
                answerable=True,
            )

        if self.generator is None:
            raise RuntimeError("GEMINI_API_KEY is not configured. Set it in your local .env file or environment; this CLI requires Gemini to generate answers.")

        retrieved_all = self.retriever.search(normalized_query, top_k=self.top_k)
        retrieved = [
            r for r in retrieved_all
            if r.relevance_score >= self.min_relevance
            and r.query_coverage >= MIN_QUERY_COVERAGE
        ]

        # Call Gemini even when no chunk clears the relevance threshold. The prompt
        # distinguishes clinic-specific unknowns from general educational questions.
        # Weakly related chunks are deliberately withheld instead of being treated as facts.
        raw_chunks = [r.chunk for r in retrieved]
        draft = self.generator.generate(normalized_query, raw_chunks)
        retrieved_by_id = {r.chunk["chunk_id"]: r for r in retrieved}
        cited_ids = list(dict.fromkeys(draft.cited_chunk_ids))
        valid_cited = [retrieved_by_id[cid] for cid in cited_ids if cid in retrieved_by_id]

        if not draft.answer.strip():
            raise RuntimeError("Gemini returned an empty answer. Please retry the question.")

        if not valid_cited:
            # A useful response can still be returned, but it is marked as
            # unsupported by the local clinic knowledge base.
            return QueryResponse(
                answer=draft.answer,
                sources=[],
                confidence_score=0.0,
                answerable=False,
            )

        # Build citations exclusively from retrieved KB records; model-provided metadata is never trusted.
        confidence = max(_confidence_score(item) for item in valid_cited)
        return QueryResponse(
            answer=draft.answer,
            sources=[_citation(item) for item in valid_cited],
            confidence_score=round(confidence, 4),
            answerable=True,
        )

    # Compatibility name for the secondary HTTP API.
    def query(self, query: str) -> QueryResponse:
        return self.answer(query)