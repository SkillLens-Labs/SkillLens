"""Unit tests for the V2 learning catalog."""

from __future__ import annotations

from backend.app.analysis.learning_catalog import LearningCatalogInstance
from backend.app.analysis.skill_taxonomy import Taxonomy


class TestLookup:
    def test_resolves_alias(self) -> None:
        resources = LearningCatalogInstance.resources_for_skill("powerbi")
        assert resources
        assert any(r.kind == "certification" for r in resources)

    def test_resolves_canonical(self) -> None:
        assert len(LearningCatalogInstance.resources_for_skill("aws")) >= 2

    def test_unknown_skill_is_empty(self) -> None:
        assert LearningCatalogInstance.resources_for_skill("interstellar astrology") == ()

    def test_never_raises_for_any_taxonomy_skill(self) -> None:
        for name in Taxonomy.canonical_names:
            LearningCatalogInstance.resources_for_skill(name)

    def test_resource_fields_are_valid(self) -> None:
        for resource in LearningCatalogInstance.resources_for_skill("python"):
            assert resource.title
            assert resource.provider
            assert resource.kind in {"certification", "course"}
            assert resource.level in {"entry", "intermediate", "advanced"}
            assert resource.url.startswith("https://")
