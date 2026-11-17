import json

from app import cli


class FakeResponse:
    def model_dump(self):
        return {
            "answer": "This response came from the mocked LLM service.",
            "sources": [],
            "confidence_score": 0.0,
            "answerable": False,
        }


class FakeService:
    def __init__(self):
        self.last_query = None

    def answer(self, query):
        self.last_query = query
        return FakeResponse()


def test_cli_accepts_unquoted_multiword_question_and_options_after_it(monkeypatch, capsys):
    fake_service = FakeService()
    received_top_k = []

    def fake_build_service(top_k=None):
        received_top_k.append(top_k)
        return fake_service

    monkeypatch.setattr(cli, "build_service", fake_build_service)

    exit_code = cli.main([
        "--top-k", "5",
        "What", "is", "your", "adres?",
        "--compact",
    ])

    output = capsys.readouterr().out
    payload = json.loads(output)

    assert exit_code == 0
    assert received_top_k == [5]
    assert fake_service.last_query == "What is your adres?"
    assert payload["answer"] == "This response came from the mocked LLM service."
