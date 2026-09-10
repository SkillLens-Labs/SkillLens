from dataclasses import dataclass

from backend.app.analysis.recommendation_llm_enhancer import (
    RecommendationLLMEnhancer,
)
from backend.app.domain.recommendations import (
    Recommendation,
    RecommendationEffort,
    RecommendationImpact,
    RecommendationPriority,
    RecommendationType,
)
from backend.app.infrastructure.llm.base import LLMGenerationResult


@dataclass
class StubLLMClient:
    response: str

    def generate(self, prompt: str) -> LLMGenerationResult:
        assert "STRICT RULES" in prompt
        assert "title" in prompt
        assert "rationale" in prompt

        return LLMGenerationResult(
            text=self.response,
            model="test-model",
            provider="ollama",
            latency_ms=1.0,
        )


class FailingLLMClient:
    def generate(self, prompt: str) -> LLMGenerationResult:
        raise RuntimeError("LLM unavailable")


def _recommendation() -> Recommendation:
    return Recommendation(
        recommendation_id="rec-test-001",
        type=RecommendationType.LEARNING,
        title="Learn Kubernetes",
        target_skill="Kubernetes",
        priority=RecommendationPriority.HIGH,
        rationale="Kubernetes is an identified skill gap.",
        expected_impact=RecommendationImpact.HIGH,
        effort=RecommendationEffort.MEDIUM,
        related_gap_ids=["gap-001"],
        priority_score=85.0,
        impact_score=90.0,
        source_engine="recommendation-intelligence-v1",
    )


def test_enhancer_updates_only_title_and_rationale() -> None:
    recommendation = _recommendation()

    client = StubLLMClient(
        response=(
            '{"title":"Build Kubernetes proficiency",'
            '"rationale":"Develop hands-on Kubernetes skills through a '
            'small deployment project and document the result."}'
        )
    )

    enhanced = RecommendationLLMEnhancer(client).enhance(recommendation)

    assert enhanced.title == "Build Kubernetes proficiency"
    assert enhanced.rationale.startswith("Develop hands-on Kubernetes")

    assert enhanced.recommendation_id == recommendation.recommendation_id
    assert enhanced.type == recommendation.type
    assert enhanced.target_skill == recommendation.target_skill
    assert enhanced.priority == recommendation.priority
    assert enhanced.expected_impact == recommendation.expected_impact
    assert enhanced.effort == recommendation.effort
    assert enhanced.evidence == recommendation.evidence
    assert enhanced.related_gap_ids == recommendation.related_gap_ids
    assert enhanced.confidence == recommendation.confidence
    assert enhanced.priority_score == recommendation.priority_score
    assert enhanced.impact_score == recommendation.impact_score
    assert enhanced.source_engine == recommendation.source_engine


def test_enhancer_fails_closed_when_llm_is_unavailable() -> None:
    recommendation = _recommendation()

    enhanced = RecommendationLLMEnhancer(
        FailingLLMClient()
    ).enhance(recommendation)

    assert enhanced == recommendation


def test_enhancer_fails_closed_for_invalid_json() -> None:
    recommendation = _recommendation()

    client = StubLLMClient(
        response="This is not JSON."
    )

    enhanced = RecommendationLLMEnhancer(client).enhance(recommendation)

    assert enhanced == recommendation


def test_enhancer_fails_closed_for_missing_fields() -> None:
    recommendation = _recommendation()

    client = StubLLMClient(
        response='{"title":"Improved title"}'
    )

    enhanced = RecommendationLLMEnhancer(client).enhance(recommendation)

    assert enhanced == recommendation


def test_enhancer_rejects_empty_llm_fields() -> None:
    recommendation = _recommendation()

    client = StubLLMClient(
        response='{"title":"","rationale":"Useful rationale"}'
    )

    enhanced = RecommendationLLMEnhancer(client).enhance(recommendation)

    assert enhanced == recommendation