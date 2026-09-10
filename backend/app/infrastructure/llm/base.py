from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class LLMGenerationResult:
    """Infrastructure-level result returned by a local LLM provider."""

    text: str
    model: str
    provider: str
    latency_ms: float | None = None


class LocalLLMClient(ABC):
    """
    Narrow contract for optional local language-model generation.

    This interface is intentionally independent of SkillLens analytical
    domain models. The LLM must not become the authority for skills,
    matching, gaps, scoring, confidence, priority, impact, or ranking.
    """

    @abstractmethod
    def generate(self, prompt: str) -> LLMGenerationResult:
        """Generate natural-language text from a prompt."""
        raise NotImplementedError