from __future__ import annotations

from dataclasses import dataclass, field
import re
import unicodedata

from backend.app.analysis.skill_extractor import SkillMention


@dataclass(frozen=True)
class NormalizedSkill:
    """A skill mention resolved to a deterministic canonical name."""

    raw_text: str
    canonical_name: str
    mention: SkillMention
    matched_alias: str | None = None
    confidence: float = 1.0
    metadata: dict[str, object] = field(default_factory=dict)


class SkillNormalizer:
    """Normalize extracted skill mentions deterministically."""

    _CANONICAL_SKILLS: dict[str, str] = {
        "python": "python",
        "java": "java",
        "javascript": "javascript",
        "typescript": "typescript",
        "c++": "c++",
        "c#": "c#",
        "go": "go",
        "rust": "rust",
        "sql": "sql",
        "nosql": "nosql",
        "html": "html",
        "css": "css",
        "react": "react",
        "angular": "angular",
        "vue.js": "vue.js",
        "node.js": "node.js",
        "fastapi": "fastapi",
        "django": "django",
        "flask": "flask",
        "spring boot": "spring boot",
        "rest api": "rest api",
        "graphql": "graphql",
        "git": "git",
        "github": "github",
        "docker": "docker",
        "kubernetes": "kubernetes",
        "aws": "aws",
        "azure": "azure",
        "gcp": "gcp",
        "linux": "linux",
        "postgresql": "postgresql",
        "mysql": "mysql",
        "mongodb": "mongodb",
        "redis": "redis",
        "pandas": "pandas",
        "numpy": "numpy",
        "scikit-learn": "scikit-learn",
        "tensorflow": "tensorflow",
        "pytorch": "pytorch",
        "xgboost": "xgboost",
        "machine learning": "machine learning",
        "deep learning": "deep learning",
        "natural language processing": "natural language processing",
        "nlp": "natural language processing",
        "transformers": "transformers",
        "hugging face": "hugging face",
        "data analysis": "data analysis",
        "data science": "data science",
        "statistics": "statistics",
        "power bi": "power bi",
        "tableau": "tableau",
        "excel": "excel",
    }

    _ALIASES: dict[str, str] = {
        "py": "python",
        "python programming": "python",
        "python programming language": "python",
        "python 3": "python",
        "python3": "python",
        "js": "javascript",
        "javascript programming": "javascript",
        "ts": "typescript",
        "reactjs": "react",
        "react js": "react",
        "react.js": "react",
        "vue": "vue.js",
        "vuejs": "vue.js",
        "node": "node.js",
        "nodejs": "node.js",
        "fast api": "fastapi",
        "postgres": "postgresql",
        "postgres sql": "postgresql",
        "mongo": "mongodb",
        "scikit learn": "scikit-learn",
        "sklearn": "scikit-learn",
        "ml": "machine learning",
        "machine-learning": "machine learning",
        "deep-learning": "deep learning",
        "natural-language-processing": "natural language processing",
        "powerbi": "power bi",
        "ms excel": "excel",
        "microsoft excel": "excel",
    }

    def normalize(
        self,
        mention: SkillMention,
    ) -> NormalizedSkill:
        """Normalize one extracted skill mention."""
        raw_text = mention.raw_text
        normalized = self._normalize_text(raw_text)

        canonical_name = self._CANONICAL_SKILLS.get(normalized)

        if canonical_name is not None:
            return NormalizedSkill(
                raw_text=raw_text,
                canonical_name=canonical_name,
                mention=mention,
                confidence=mention.confidence,
                metadata={
                    "normalization_method": "canonical_lookup",
                },
            )

        canonical_name = self._ALIASES.get(normalized)

        if canonical_name is not None:
            return NormalizedSkill(
                raw_text=raw_text,
                canonical_name=canonical_name,
                mention=mention,
                matched_alias=normalized,
                confidence=mention.confidence,
                metadata={
                    "normalization_method": "alias_lookup",
                },
            )

        # The extractor should normally prevent this path. Keeping it
        # deterministic makes the normalizer safe when used independently.
        return NormalizedSkill(
            raw_text=raw_text,
            canonical_name=normalized,
            mention=mention,
            confidence=mention.confidence,
            metadata={
                "normalization_method": "normalized_fallback",
            },
        )

    def normalize_many(
        self,
        mentions: tuple[SkillMention, ...] | list[SkillMention],
    ) -> tuple[NormalizedSkill, ...]:
        """Normalize multiple extracted skill mentions in source order."""
        return tuple(self.normalize(mention) for mention in mentions)

    @staticmethod
    def _normalize_text(text: str) -> str:
        """Apply deterministic text normalization."""
        normalized = unicodedata.normalize("NFKC", text)
        normalized = normalized.strip().lower()
        normalized = re.sub(r"\s+", " ", normalized)

        # Normalize common typographic separators without changing
        # meaningful skill punctuation such as C++, C#, or Node.js.
        normalized = normalized.replace("–", "-")
        normalized = normalized.replace("—", "-")

        return normalized