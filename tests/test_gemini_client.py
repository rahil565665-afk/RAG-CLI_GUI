from app.gemini_client import GeminiProviderError


class FakeSdkError(Exception):
    def __init__(self, code, status=None):
        super().__init__("simulated provider failure; no credentials are included")
        self.code = code
        self.status = status


def test_rate_limit_error_is_distinguished_from_generic_provider_failure():
    error = GeminiProviderError.from_exception(FakeSdkError(429, "RESOURCE_EXHAUSTED"))
    assert error.error_code == "GEMINI_RATE_LIMITED"
    assert error.status_code == 429
    assert "quota" in str(error).lower()


def test_temporary_unavailable_error_has_retry_guidance():
    error = GeminiProviderError.from_exception(FakeSdkError(503, "UNAVAILABLE"))
    assert error.error_code == "GEMINI_TEMPORARILY_UNAVAILABLE"
    assert error.status_code == 503
    assert "automatic retries" in str(error).lower()


def test_invalid_request_is_not_mislabelled_as_transient():
    error = GeminiProviderError.from_exception(FakeSdkError(400, "INVALID_ARGUMENT"))
    assert error.error_code == "GEMINI_INVALID_REQUEST"
    assert error.status_code == 400


def test_timeout_is_reported_as_network_error():
    error = GeminiProviderError.from_exception(TimeoutError("request timed out"))
    assert error.error_code == "GEMINI_NETWORK_ERROR"


def test_gemini_client_is_reused_and_has_bounded_retry_policy(monkeypatch):
    from google import genai
    from app.gemini_client import GeminiAnswerGenerator

    made = []

    class FakeClient:
        def __init__(self, *, api_key, http_options):
            self.api_key = api_key
            self.http_options = http_options
            self.closed = False
            made.append(self)

        def close(self):
            self.closed = True

    monkeypatch.setattr(genai, "Client", FakeClient)

    generator = GeminiAnswerGenerator("test-only-key")
    first_client, types = generator._get_client()
    second_client, second_types = generator._get_client()

    assert first_client is second_client
    assert types is second_types
    assert len(made) == 1

    retry = first_client.http_options.retry_options
    assert retry.attempts == 5
    assert retry.initial_delay == 1.0
    assert retry.max_delay == 8.0
    assert retry.http_status_codes == [408, 429, 500, 502, 503, 504]

    generator.close()
    assert first_client.closed is True
