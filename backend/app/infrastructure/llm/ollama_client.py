from __future__ import annotations

import time

import httpx

from backend.app.infrastructure.llm.base import (
    LLMGenerationResult,
    LocalLLMClient,
)


class OllamaClient(LocalLLMClient):
    """HTTP client for a locally running Ollama server."""

    PROVIDER = "ollama"

    def __init__(
        self,
        base_url: str,
        model: str,
        timeout_seconds: float = 30.0,
        client: httpx.Client | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout_seconds = timeout_seconds
        self._client = client

    def generate(self, prompt: str) -> LLMGenerationResult:
        """Generate text using Ollama's local /api/generate endpoint."""

        if not prompt.strip():
            raise ValueError("Prompt must not be empty.")

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        owns_client = self._client is None
        client = self._client or httpx.Client(timeout=self.timeout_seconds)

        started = time.perf_counter()

        try:
            response = client.post(
                f"{self.base_url}/api/generate",
                json=payload,
            )
            response.raise_for_status()

            data = response.json()

            generated_text = data.get("response")
            if not isinstance(generated_text, str):
                raise ValueError(
                    "Ollama response does not contain a valid 'response' field."
                )

            latency_ms = (time.perf_counter() - started) * 1000

            return LLMGenerationResult(
                text=generated_text,
                model=data.get("model", self.model),
                provider=self.PROVIDER,
                latency_ms=latency_ms,
            )

        except httpx.HTTPError as exc:
            raise RuntimeError(
                f"Ollama request failed: {exc}"
            ) from exc

        finally:
            if owns_client:
                client.close()