from pathlib import Path

from app.retrieval import BM25Retriever, KnowledgeBase, tokenize

ROOT = Path(__file__).resolve().parents[1]
KB_PATH = ROOT / "data" / "northside_dental_knowledge_base.json"


def make_retriever():
    kb = KnowledgeBase.load(KB_PATH)
    return kb, BM25Retriever(kb)


def test_knowledge_base_loads_with_unique_ids():
    kb, _ = make_retriever()
    ids = [chunk["chunk_id"] for chunk in kb.chunks]
    assert len(kb.chunks) == 31
    assert len(ids) == len(set(ids))


def test_cleaning_cost_retrieves_fee_chunk():
    _, retriever = make_retriever()
    results = retriever.search("How much does a routine cleaning cost?", top_k=4)
    assert results
    assert results[0].chunk["chunk_id"] == "NSDC-05-001"


def test_opening_hours_retrieves_hours_chunk():
    _, retriever = make_retriever()
    results = retriever.search("What are the clinic opening hours?", top_k=4)
    assert results
    assert results[0].chunk["chunk_id"] == "NSDC-01-003"


def test_swallowing_difficulty_retrieves_emergency_chunk():
    _, retriever = make_retriever()
    results = retriever.search("difficulty swallowing", top_k=4)
    assert results
    assert results[0].chunk["chunk_id"] == "NSDC-07-001"


def test_negative_and_safety_terms_are_preserved():
    tokens = tokenize("not without worsening pain, bleeding, or swelling")
    for term in ("not", "without", "worsening", "bleeding", "swelling"):
        assert term in tokens


def test_clinic_address_retrieves_clinic_profile():
    _, retriever = make_retriever()
    results = retriever.search("What is the clinic address?", top_k=4)
    assert results
    assert results[0].chunk["chunk_id"] == "NSDC-01-001"
    assert "18 Cedar Lane" in results[0].chunk["content"]


def test_common_address_misspelling_is_normalized():
    tokens = tokenize("what is your adress")
    assert "address" in tokens
    assert "adress" not in tokens

    _, retriever = make_retriever()
    results = retriever.search("what is your adress", top_k=4)
    assert results
    assert results[0].chunk["chunk_id"] == "NSDC-01-001"
