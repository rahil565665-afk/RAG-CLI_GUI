from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SourceCitation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    chunk_id: str
    section_id: str
    section_title: str
    subsection: str
    source_document: str
    source_pages: list[int]
    relevance_score: float = Field(ge=0.0, le=1.0)


class QueryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answer: str
    sources: list[SourceCitation]
    confidence_score: float = Field(ge=0.0, le=100.0)
    answerable: bool

    @field_validator("answer")
    @classmethod
    def answer_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("answer must not be blank")
        return value


class GeminiDraft(BaseModel):
    """Small schema requested from Gemini; sources are attached by trusted code."""

    model_config = ConfigDict(extra="ignore")

    answer: str
    cited_chunk_ids: list[str]

    @field_validator("answer")
    @classmethod
    def answer_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("answer must not be blank")
        return value


class QueryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1, max_length=2000)

    @field_validator("query")
    @classmethod
    def normalize_query(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("query must not be blank")
        return value


class HealthResponse(BaseModel):
    status: str
    service: str
    knowledge_base_chunks: int
    gemini_configured: bool