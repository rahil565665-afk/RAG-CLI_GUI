from app.schemas import GeminiDraft


def test_gemini_response_schema_is_compatible_with_gemini_api():
    schema = GeminiDraft.model_json_schema()

    # Gemini's response_schema endpoint rejects this Pydantic JSON Schema field.
    assert "additionalProperties" not in schema
    assert set(schema["properties"]) == {"answer", "cited_chunk_ids"}
    assert set(schema["required"]) == {"answer", "cited_chunk_ids"}
