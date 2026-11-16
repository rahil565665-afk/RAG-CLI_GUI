from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

TOKEN_RE = re.compile(r"[a-z0-9]+(?:'[a-z]+)?", re.IGNORECASE)
# Remove only low-information function words. Negation, urgency, and symptom terms stay.
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "been", "by", "can", "could",
    "did", "do", "does", "for", "from", "have", "how", "i", "much", "if", "in", "is",
    "it", "me", "my", "of", "on", "or", "please", "should", "the", "their",
    "there", "this", "to", "was", "we", "what", "when", "where", "which", "who",
    "would", "you", "your", "our", "we", "they", "he", "she", "them", "us", "have", "has",
}
PRESERVE = {"no", "not", "without", "never", "cannot", "can't", "worsening", "difficulty", "bleeding", "swelling"}
TOKEN_ALIASES = {
    "adress": "address",
    "addres": "address",
    "adres": "address",
    "adddress": "address",
    "addr": "address",
}


def _normalize_token(token: str) -> str:
    token = TOKEN_ALIASES.get(token, token)
    if token in PRESERVE:
        return token
    if len(token) > 5 and token.endswith("ies"):
        return token[:-3] + "y"
    if len(token) > 5 and token.endswith("ing"):
        stem = token[:-3]
        if len(stem) > 2 and stem[-1] == stem[-2]:
            stem = stem[:-1]
        return stem
    if len(token) > 4 and token.endswith("s") and not token.endswith(("ss", "us", "is")):
        return token[:-1]
    return token


def tokenize(text: str) -> list[str]:
    tokens = [_normalize_token(t.lower()) for t in TOKEN_RE.findall(text)]
    return [t for t in tokens if t not in STOPWORDS or t in PRESERVE]


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: dict[str, Any]
    relevance_score: float
    raw_score: float
    query_coverage: float = 1.0


class KnowledgeBase:
    def __init__(self, chunks: list[dict[str, Any]], metadata: dict[str, Any] | None = None):
        if not chunks:
            raise ValueError("Knowledge base contains no chunks")
        ids = [c.get("chunk_id") for c in chunks]
        if any(not item for item in ids) or len(ids) != len(set(ids)):
            raise ValueError("Knowledge-base chunk IDs must be present and unique")
        self.chunks = chunks
        self.metadata = metadata or {}
        self.by_id = {c["chunk_id"]: c for c in chunks}

    @classmethod
    def load(cls, path: str | Path) -> "KnowledgeBase":
        file_path = Path(path)
        try:
            data = json.loads(file_path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise FileNotFoundError(f"Knowledge base file not found: {file_path}") from exc
        if not isinstance(data, dict) or not isinstance(data.get("chunks"), list):
            raise ValueError("Knowledge base JSON must contain a 'chunks' array")
        return cls(data["chunks"], data.get("document_metadata", {}))


class BM25Retriever:
    """Transparent BM25 keyword retrieval with a normalized relevance heuristic."""

    def __init__(self, kb: KnowledgeBase, k1: float = 1.5, b: float = 0.75, normalization_constant: float = 3.0):
        self.kb = kb
        self.k1 = k1
        self.b = b
        self.normalization_constant = normalization_constant
        self.documents: list[list[str]] = []
        self.term_frequencies: list[Counter[str]] = []
        self.document_frequencies: Counter[str] = Counter()
        for chunk in kb.chunks:
            searchable = " ".join([
                chunk.get("section_title", ""),
                chunk.get("subsection", ""),
                " ".join(chunk.get("keywords", [])),
                chunk.get("content", ""),
            ])
            terms = tokenize(searchable)
            self.documents.append(terms)
            self.term_frequencies.append(Counter(terms))
            self.document_frequencies.update(set(terms))
        self.avg_doc_length = sum(map(len, self.documents)) / max(len(self.documents), 1)

    def search(self, query: str, top_k: int = 4) -> list[RetrievedChunk]:
        q_terms = list(dict.fromkeys(tokenize(query)))
        if not q_terms:
            return []
        total_docs = len(self.documents)
        results: list[RetrievedChunk] = []
        for index, chunk in enumerate(self.kb.chunks):
            tf_map = self.term_frequencies[index]
            doc_len = len(self.documents[index])
            raw = 0.0
            matched = 0
            for term in q_terms:
                frequency = tf_map.get(term, 0)
                if frequency <= 0:
                    continue
                matched += 1
                df = self.document_frequencies[term]
                idf = math.log(1.0 + (total_docs - df + 0.5) / (df + 0.5))
                denominator = frequency + self.k1 * (1.0 - self.b + self.b * doc_len / max(self.avg_doc_length, 1.0))
                raw += idf * (frequency * (self.k1 + 1.0)) / denominator
            if raw <= 0:
                continue
            coverage = matched / len(q_terms)
            normalized = (raw / (raw + self.normalization_constant)) * coverage
            results.append(RetrievedChunk(chunk=chunk, relevance_score=max(0.0, min(normalized, 1.0)), raw_score=raw, query_coverage=coverage))
        results.sort(key=lambda item: (item.relevance_score, item.raw_score), reverse=True)
        return results[: max(1, min(int(top_k), 5))]

    def by_id(self, chunk_id: str) -> RetrievedChunk | None:
        chunk = self.kb.by_id.get(chunk_id)
        if not chunk:
            return None
        return RetrievedChunk(chunk=chunk, relevance_score=1.0, raw_score=float("inf"))