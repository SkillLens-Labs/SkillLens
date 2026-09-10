import httpx
import pytest

from backend.app.infrastructure.llm import OllamaClient


def test_ollama_client_generates_text_without_real_server() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST"
        assert str(request.url) == "http://testserver/api/generate"

        payload = request.read()
        assert b'"model":"test-model"' in payload
        assert b'"prompt":"Explain skill gaps."' in payload
        assert b'"stream":false' in payload

        return httpx.Response(
            200,
            json={
                "model": "test-model",
                "response": "A skill gap is a difference between required and demonstrated capability.",
            },
        )

    transport = httpx.MockTransport(handler)

    with httpx.Client(transport=transport) as client:
        ollama = OllamaClient(
            base_url="http://testserver",
            model="test-model",
            client=client,
        )

        result = ollama.generate("Explain skill gaps.")

    assert result.text.startswith("A skill gap is")
    assert result.model == "test-model"
    assert result.provider == "ollama"
    assert result.latency_ms is not None


def test_ollama_client_rejects_empty_prompt() -> None:
    ollama = OllamaClient(
        base_url="http://testserver",
        model="test-model",
    )

    with pytest.raises(ValueError, match="Prompt must not be empty"):
        ollama.generate("   ")


def test_ollama_client_raises_for_http_failure() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            500,
            json={"error": "model unavailable"},
        )

    transport = httpx.MockTransport(handler)

    with httpx.Client(transport=transport) as client:
        ollama = OllamaClient(
            base_url="http://testserver",
            model="test-model",
            client=client,
        )

        with pytest.raises(RuntimeError, match="Ollama request failed"):
            ollama.generate("Generate an explanation.")


def test_ollama_client_rejects_invalid_response_shape() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "model": "test-model",
            },
        )

    transport = httpx.MockTransport(handler)

    with httpx.Client(transport=transport) as client:
        ollama = OllamaClient(
            base_url="http://testserver",
            model="test-model",
            client=client,
        )

        with pytest.raises(
            ValueError,
            match="valid 'response' field",
        ):
            ollama.generate("Generate an explanation.")