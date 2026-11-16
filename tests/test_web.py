from fastapi.testclient import TestClient

from app.main import app, service
from app.schemas import QueryResponse, SourceCitation

client = TestClient(app)


def test_homepage_serves_minimal_demo_ui():
    response = client.get("/")
    assert response.status_code == 200
    assert "Demo" in response.text
    assert "Ask a question" in response.text
    assert "Northside" not in response.text


def test_static_assets_are_served():
    assert client.get("/static/styles.css").status_code == 200
    assert client.get("/static/app.js").status_code == 200


def test_health_reports_loaded_local_knowledge_base():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["knowledge_base_chunks"] == 31


def test_chat_rejects_blank_query():
    response = client.post("/api/chat", json={"query": "   "})
    assert response.status_code == 422


def test_chat_rejects_overlong_query():
    response = client.post("/api/chat", json={"query": "x" * 2001})
    assert response.status_code == 422


def test_chat_returns_structured_answer_and_sources(monkeypatch):
    source = SourceCitation(
        chunk_id="DEMO-01",
        section_id="01",
        section_title="Example source",
        subsection="Example subsection",
        source_document="example.json",
        source_pages=[1],
        relevance_score=0.91,
    )
    result = QueryResponse(
        answer="This is a generated demo answer.",
        sources=[source],
        confidence_score=91.0,
        answerable=True,
    )
    monkeypatch.setattr(service, "answer", lambda query: result)

    response = client.post("/api/chat", json={"query": "A test question"})
    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "This is a generated demo answer."
    assert body["sources"][0]["chunk_id"] == "DEMO-01"
    assert body["confidence_score"] == 91.0
    assert body["answerable"] is True


def test_chat_reports_missing_gemini_configuration(monkeypatch):
    monkeypatch.setattr(service, "generator", None)
    response = client.post("/api/chat", json={"query": "A normal question"})
    assert response.status_code == 503
    assert "GEMINI_API_KEY" in response.json()["detail"]
