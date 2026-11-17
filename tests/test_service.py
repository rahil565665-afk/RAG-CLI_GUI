from pathlib import Path

from app.rag_service import RAGService
from app.retrieval import BM25Retriever, KnowledgeBase
from app.schemas import GeminiDraft

ROOT = Path(__file__).resolve().parents[1]
KB_PATH = ROOT / "data" / "northside_dental_knowledge_base.json"


class FakeGenerator:
    def __init__(self, cited_ids=None, answer="The sample cleaning fee is $120; confirm the current amount with the front desk."):
        self.cited_ids = cited_ids
        self.answer = answer
        self.calls = 0
        self.last_retrieved = None

    def generate(self, query, retrieved):
        self.calls += 1
        self.last_retrieved = retrieved
        ids = self.cited_ids if self.cited_ids is not None else (
            [retrieved[0]["chunk_id"]] if retrieved else []
        )
        return GeminiDraft(answer=self.answer, cited_chunk_ids=ids)


def make_service(generator, threshold=0.12):
    kb = KnowledgeBase.load(KB_PATH)
    retriever = BM25Retriever(kb)
    return RAGService(kb, retriever, generator, min_relevance=threshold, top_k=4)


def test_unknown_clinic_information_gets_helpful_fallback_without_claiming_yes_or_no():
    fake = FakeGenerator(
        cited_ids=[],
        answer="The current Northside Dental knowledge base does not specify whether tooth replacement is offered. I can't confirm that from the available clinic information; please contact the front desk.",
    )
    service = make_service(fake)
    result = service.answer("Do you do tooth replacement?")

    assert fake.calls == 1
    assert fake.last_retrieved == []
    assert "does not specify whether tooth replacement is offered" in result.answer
    assert "does not offer" not in result.answer.lower()
    assert result.answerable is False
    assert result.sources == []
    assert result.confidence_score == 0.0


def test_only_retrieved_citations_are_returned():
    kb = KnowledgeBase.load(KB_PATH)
    retriever = BM25Retriever(kb)
    retrieved = retriever.search("routine cleaning sample fee", top_k=4)
    allowed = retrieved[0].chunk["chunk_id"]
    fake = FakeGenerator(cited_ids=[allowed, "MADE-UP-999"])
    service = RAGService(kb, retriever, fake, min_relevance=0.12, top_k=4)
    result = service.answer("How much does a routine cleaning cost?")
    assert result.answerable is True
    assert "confidence_basis" not in result.model_dump()
    assert [source.chunk_id for source in result.sources] == [allowed]
    assert result.sources[0].source_pages == [6]
    assert 0.0 <= result.confidence_score <= 100.0


def test_emergency_route_precedes_gemini_and_avoids_universal_911_claim():
    fake = FakeGenerator()
    service = make_service(fake)
    result = service.answer("I am having difficulty swallowing")
    assert result.answerable is True
    assert fake.calls == 0
    assert result.sources[0].chunk_id == "NSDC-07-001"
    assert "local emergency services" in result.answer
    assert "911" not in result.answer


def test_query_validation():
    service = make_service(FakeGenerator())
    try:
        service.answer("   ")
    except ValueError as exc:
        assert "empty" in str(exc)
    else:
        raise AssertionError("Expected empty query to be rejected")

    try:
        service.answer("x" * 2001)
    except ValueError as exc:
        assert "2,000" in str(exc)
    else:
        raise AssertionError("Expected overlong query to be rejected")


def test_exact_clinic_name_query_gets_high_retrieval_support_score():
    service = make_service(FakeGenerator())
    result = service.answer("What is the clinic name?")

    assert result.answerable is True
    assert result.sources[0].chunk_id == "NSDC-01-001"
    assert 90.0 <= result.confidence_score <= 100.0



def test_fallback_answer_can_be_returned_for_general_question_without_claiming_clinic_policy():
    fallback = "General information—not confirmed Northside Dental Clinic policy or service information: tooth replacement can refer to options such as dentures, bridges, or implants."
    fake = FakeGenerator(cited_ids=[], answer=fallback)
    service = make_service(fake, threshold=1.0)

    result = service.answer("What does tooth replacement mean?")

    assert fake.calls == 1
    assert result.answer.startswith("General information")
    assert result.sources == []
    assert result.confidence_score == 0.0
    assert result.answerable is False



def test_partial_keyword_overlap_is_not_misused_as_proof_of_a_clinic_service():
    fake = FakeGenerator(
        cited_ids=[],
        answer="The current Northside Dental knowledge base does not specify whether tooth replacement is offered. I can't confirm that from the available clinic information; please contact the front desk.",
    )
    service = make_service(fake)

    result = service.answer("Do you do tooth replacement?")

    assert fake.calls == 1
    assert fake.last_retrieved == []
    assert result.sources == []
    assert result.confidence_score == 0.0
    assert result.answerable is False
    assert "does not specify whether tooth replacement is offered" in result.answer



def test_fictional_address_is_returned_with_a_source_and_high_support_score():
    service = make_service(FakeGenerator())
    result = service.answer("What is your adress?")

    assert result.answerable is True
    assert result.sources
    assert result.sources[0].chunk_id == "NSDC-01-001"
    assert "18 Cedar Lane" in service.kb.by_id["NSDC-01-001"]["content"]
    assert result.confidence_score >= 90.0



def test_missing_gemini_key_never_returns_a_predefined_answer_for_unknown_questions():
    service = make_service(None, threshold=1.0)
    try:
        service.answer("What is the clinic's annual revenue?")
    except RuntimeError as exc:
        assert "GEMINI_API_KEY" in str(exc)
    else:
        raise AssertionError("Expected a configuration error instead of a fixed fallback answer")
