from __future__ import annotations

import json
from dataclasses import dataclass

from backend.app.domain.recommendations import Recommendation
from backend.app.infrastructure.llm.base import LocalLLMClient


@dataclass(frozen=True)
class RecommendationEnhancement:
    """
    Natural-language enhancement returned by the optional LLM layer.

    Only title and rationale are eligible for enhancement.
    """

    title: str
    rationale: str


class RecommendationLLMEnhancer:
    """
    Optional natural-language enhancement layer for recommendations.

    The deterministic RecommendationIntelligence engine remains the
    authority for recommendation selection, classification, priority,
    impact, confidence, evidence, ranking, and target skills.

    The LLM may only improve the wording of the recommendation title
    and rationale.
    """

    ENGINE_VERSION = "recommendation-llm-enhancer-v1"

    def __init__(self, client: LocalLLMClient) -> None:
        self.client = client

    def enhance(
        self,
        recommendation: Recommendation,
    ) -> Recommendation:
        """
        Enhance a recommendation without changing analytical fields.

        If the LLM fails or returns invalid content, the original
        deterministic recommendation is returned unchanged.
        """

        prompt = self._build_prompt(recommendation)

        try:
            result = self.client.generate(prompt)
            enhancement = self._parse_response(result.text)

            return recommendation.model_copy(
                update={
                    "title": enhancement.title,
                    "rationale": enhancement.rationale,
                }
            )

        except (RuntimeError, ValueError, TypeError, json.JSONDecodeError):
            return recommendation

    @classmethod
    def _build_prompt(
        cls,
        recommendation: Recommendation,
    ) -> str:
        """
        Build a constrained prompt containing only information necessary
        for natural-language improvement.
        """

        payload = {
            "title": recommendation.title,
            "rationale": recommendation.rationale,
            "type": recommendation.type.value,
            "target_skill": recommendation.target_skill,
        }

        return (
            "You are a technical career recommendation editor.\n"
            "Improve the wording of the supplied recommendation.\n\n"
            "STRICT RULES:\n"
            "1. Return JSON only.\n"
            "2. Return exactly two string fields: title and rationale.\n"
            "3. Do not invent skills, qualifications, evidence, scores, "
            "requirements, experience, certifications, or career facts.\n"
            "4. Preserve the original recommendation meaning.\n"
            "5. Do not change priority, impact, effort, confidence, "
            "evidence, ranking, or recommendation type.\n"
            "6. Make the rationale concise, specific, and actionable.\n"
            "7. Do not use markdown.\n\n"
            f"Recommendation:\n{json.dumps(payload, ensure_ascii=False)}\n\n"
            "Required output format:\n"
            '{"title":"...","rationale":"..."}'
        )

    @staticmethod
    def _parse_response(
        response_text: str,
    ) -> RecommendationEnhancement:
        """Parse and validate the constrained LLM response."""

        text = response_text.strip()

        if not text:
            raise ValueError("LLM response is empty.")

        data = json.loads(text)

        if not isinstance(data, dict):
            raise ValueError("LLM response must be a JSON object.")

        title = data.get("title")
        rationale = data.get("rationale")

        if not isinstance(title, str) or not title.strip():
            raise ValueError("LLM response contains an invalid title.")

        if not isinstance(rationale, str) or not rationale.strip():
            raise ValueError("LLM response contains an invalid rationale.")

        return RecommendationEnhancement(
            title=title.strip(),
            rationale=rationale.strip(),
        )