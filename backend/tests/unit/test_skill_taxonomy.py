"""Unit tests for the V2 shared skill taxonomy."""

from __future__ import annotations

import pytest

from backend.app.analysis.skill_taxonomy import Taxonomy


class TestTaxonomyConsistency:
    def test_hardcoded_skills_still_exist(self) -> None:
        """Every skill the V1 lexicon knew must remain in the taxonomy."""
        legacy = {
            "python", "java", "javascript", "typescript", "c++", "c#",
            "rust", "sql", "nosql", "html", "css", "react", "angular",
            "vue.js", "node.js", "fastapi", "django", "flask", "spring boot",
            "rest api", "graphql", "git", "github", "docker", "kubernetes",
            "aws", "azure", "gcp", "linux", "postgresql", "mysql", "mongodb",
            "redis", "pandas", "numpy", "scikit-learn", "tensorflow",
            "pytorch", "xgboost", "machine learning", "deep learning",
            "natural language processing", "transformers", "hugging face",
            "data analysis", "data science", "statistics", "power bi",
            "tableau", "excel",
        }
        unresolvable = {
            name
            for name in legacy
            if name != "go"
            and name not in Taxonomy.canonical_names
            and Taxonomy.resolve(name) is None
        }
        assert not unresolvable, f"Legacy skills lost from taxonomy: {unresolvable}"

    def test_legacy_go_skill_resolves(self) -> None:
        """'Go' was a V1 skill; V2 resolves it to golang."""
        assert Taxonomy.resolve("Go") == "golang"
        assert Taxonomy.resolve("golang") == "golang"

    def test_no_duplicate_aliases(self) -> None:
        seen: dict[str, str] = {}
        for name in Taxonomy.canonical_names:
            assert name not in seen, f"Duplicate canonical: {name}"
            seen[name] = name


class TestResolve:
    @pytest.mark.parametrize(
        ("raw_text", "expected"),
        [
            ("Python", "python"),
            ("python3", "python"),
            ("JS", "javascript"),
            ("sklearn", "scikit-learn"),
            ("postgres", "postgresql"),
            ("PowerBi", "power bi"),
            ("Go", "golang"),
            ("golang", "golang"),
            ("AI", "artificial intelligence"),
            ("ms excel", "excel"),
        ],
    )
    def test_known_resolutions(self, raw_text: str, expected: str) -> None:
        assert Taxonomy.resolve(raw_text) == expected

    def test_unknown_text_is_none(self) -> None:
        assert Taxonomy.resolve("quantum blockchain farming") is None

    def test_case_sensitive_alias_is_case_sensitive(self) -> None:
        assert Taxonomy.case_sensitive_alias_to_canonical.get("Go") == "golang"
        assert "go" not in Taxonomy.case_sensitive_alias_to_canonical
