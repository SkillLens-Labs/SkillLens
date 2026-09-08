from __future__ import annotations


import pytest

from backend.app.analysis.esco_mapper import (
    ESCOCandidate,
    ESCOMapResult,
    ESCOMapStatus,
)
from backend.app.analysis.skill_matcher import (
    MatchingStrategy,
    MatchingThresholds,
    SemanticModelConfig,
    SkillMatcher,
)
from backend.app.domain.confidence import Confidence, ConfidenceLevel
from backend.app.domain.evidence import Evidence, EvidenceSourceType
from backend.app.domain.skill import Skill


def make_evidence(
    *,
    source_type: EvidenceSourceType,
    document_id: str,
    text: str,
) -> Evidence:
    return Evidence(
        evidence_id=f"evidence-{document_id}-{text.lower().replace(' ', '-')}",
        source_type=source_type,
        source_document_id=document_id,
        section="skills",
        text=text,
        start_offset=0,
        end_offset=len(text),
        evidence_type="explicit",
        extractor="test",
        relevance=0.95,
        confidence=0.95,
    )


def make_skill(
    *,
    skill_id: str,
    canonical_name: str,
    source_type: EvidenceSourceType,
    document_id: str,
) -> Skill:
    return Skill(
        skill_id=skill_id,
        canonical_name=canonical_name,
        display_name=canonical_name.title(),
        evidence=[
            make_evidence(
                source_type=source_type,
                document_id=document_id,
                text=canonical_name,
            )
        ],
        confidence=Confidence(
            score=0.95,
            level=ConfidenceLevel.HIGH,
            components={"extraction": 0.95},
        ),
    )


def make_esco(
    canonical_name: str,
    *,
    uri: str = "",
    confidence: float = 0.95,
) -> ESCOMapResult:
    return ESCOMapResult(
        raw_text=canonical_name,
        canonical_name=canonical_name,
        status=ESCOMapStatus.MAPPED,
        candidates=(
            ESCOCandidate(
                uri=uri,
                preferred_label=canonical_name,
                confidence=confidence,
            ),
        ),
    )


def test_exact_match_is_detected_without_semantic_model() -> None:
    matcher = SkillMatcher(strategy=MatchingStrategy.KEYWORD)

    resume = make_skill(
        skill_id="resume-python",
        canonical_name="python",
        source_type=EvidenceSourceType.RESUME,
        document_id="resume-1",
    )
    job = make_skill(
        skill_id="job-python",
        canonical_name="python",
        source_type=EvidenceSourceType.JOB_DESCRIPTION,
        document_id="job-1",
    )

    result = matcher.match([resume], [job])

    assert len(result.skill_matches) == 1
    match = result.skill_matches[0]
    assert match.relationship.value == "exact"
    assert match.similarity == 1.0
    assert match.resume_skill_id == "resume-python"
    assert match.job_skill_id == "job-python"


def test_keyword_strategy_does_not_create_non_exact_match() -> None:
    matcher = SkillMatcher(strategy=MatchingStrategy.KEYWORD)

    resume = make_skill(
        skill_id="resume-python",
        canonical_name="python",
        source_type=EvidenceSourceType.RESUME,
        document_id="resume-1",
    )
    job = make_skill(
        skill_id="job-java",
        canonical_name="java",
        source_type=EvidenceSourceType.JOB_DESCRIPTION,
        document_id="job-1",
    )

    result = matcher.match([resume], [job])

    assert result.skill_matches == []


def test_taxonomy_strategy_requires_real_shared_esco_uri() -> None:
    matcher = SkillMatcher(strategy=MatchingStrategy.TAXONOMY)

    resume = make_skill(
        skill_id="resume-python",
        canonical_name="python",
        source_type=EvidenceSourceType.RESUME,
        document_id="resume-1",
    )
    job = make_skill(
        skill_id="job-ml",
        canonical_name="machine learning",
        source_type=EvidenceSourceType.JOB_DESCRIPTION,
        document_id="job-1",
    )

    result = matcher.match(
        [resume],
        [job],
        resume_esco=[make_esco("python")],
        job_esco=[make_esco("machine learning")],
    )

    assert result.skill_matches == []


def test_taxonomy_strategy_matches_shared_esco_concept() -> None:
    matcher = SkillMatcher(strategy=MatchingStrategy.TAXONOMY)

    shared_uri = "https://example.org/esco/shared"

    resume = make_skill(
        skill_id="resume-a",
        canonical_name="resume-skill",
        source_type=EvidenceSourceType.RESUME,
        document_id="resume-1",
    )
    job = make_skill(
        skill_id="job-a",
        canonical_name="job-skill",
        source_type=EvidenceSourceType.JOB_DESCRIPTION,
        document_id="job-1",
    )

    result = matcher.match(
        [resume],
        [job],
        resume_esco=[
            make_esco(
                "resume-skill",
                uri=shared_uri,
                confidence=0.91,
            )
        ],
        job_esco=[
            make_esco(
                "job-skill",
                uri=shared_uri,
                confidence=0.88,
            )
        ],
    )

    assert len(result.skill_matches) == 1
    match = result.skill_matches[0]
    assert match.relationship.value == "strong_semantic"
    assert match.similarity == pytest.approx(0.88)


def test_taxonomy_does_not_match_unmapped_skills() -> None:
    matcher = SkillMatcher(strategy=MatchingStrategy.TAXONOMY)

    resume = make_skill(
        skill_id="resume-a",
        canonical_name="python",
        source_type=EvidenceSourceType.RESUME,
        document_id="resume-1",
    )
    job = make_skill(
        skill_id="job-a",
        canonical_name="machine learning",
        source_type=EvidenceSourceType.JOB_DESCRIPTION,
        document_id="job-1",
    )

    result = matcher.match(
        [resume],
        [job],
        resume_esco=[
            ESCOMapResult(
                raw_text="python",
                canonical_name="python",
                status=ESCOMapStatus.UNMAPPED,
            )
        ],
        job_esco=[
            ESCOMapResult(
                raw_text="machine learning",
                canonical_name="machine learning",
                status=ESCOMapStatus.UNMAPPED,
            )
        ],
    )

    assert result.skill_matches == []


def test_semantic_matching_uses_cached_encoder(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    class FakeEncoder:
        def encode(self, texts, normalize_embeddings=True):
            assert normalize_embeddings is True
            assert len(texts) == 2
            return (
                [1.0, 0.0],
                [0.8, 0.6],
            )

    def fake_get_encoder(model_name: str):
        calls.append(model_name)
        return FakeEncoder()

    monkeypatch.setattr(
        SkillMatcher,
        "_get_encoder",
        staticmethod(fake_get_encoder),
    )

    matcher = SkillMatcher(
        strategy=MatchingStrategy.SEMANTIC,
        semantic_model=SemanticModelConfig(
            model_name="all-MiniLM-L6-v2",
        ),
    )

    resume = make_skill(
        skill_id="resume-a",
        canonical_name="python",
        source_type=EvidenceSourceType.RESUME,
        document_id="resume-1",
    )
    job = make_skill(
        skill_id="job-a",
        canonical_name="data analysis",
        source_type=EvidenceSourceType.JOB_DESCRIPTION,
        document_id="job-1",
    )

    result = matcher.match([resume], [job])

    assert len(result.skill_matches) == 1
    assert result.skill_matches[0].similarity == pytest.approx(0.8)
    assert result.skill_matches[0].relationship.value == "strong_semantic"
    assert calls == ["all-MiniLM-L6-v2"]


def test_semantic_thresholds_control_relationship_classification(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeEncoder:
        def encode(self, texts, normalize_embeddings=True):
            return (
                [1.0, 0.0],
                [0.72, (1.0 - 0.72**2) ** 0.5],
            )

    monkeypatch.setattr(
        SkillMatcher,
        "_get_encoder",
        staticmethod(lambda _: FakeEncoder()),
    )

    matcher = SkillMatcher(
        strategy=MatchingStrategy.SEMANTIC,
        thresholds=MatchingThresholds(
            strong_semantic=0.80,
            partial=0.70,
            related=0.50,
        ),
    )

    resume = make_skill(
        skill_id="resume-a",
        canonical_name="python",
        source_type=EvidenceSourceType.RESUME,
        document_id="resume-1",
    )
    job = make_skill(
        skill_id="job-a",
        canonical_name="data science",
        source_type=EvidenceSourceType.JOB_DESCRIPTION,
        document_id="job-1",
    )

    result = matcher.match([resume], [job])

    assert result.skill_matches[0].relationship.value == "partial"


def test_semantic_low_similarity_is_recorded_as_unmatched(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeEncoder:
        def encode(self, texts, normalize_embeddings=True):
            return (
                [1.0, 0.0],
                [0.1, (1.0 - 0.1**2) ** 0.5],
            )

    monkeypatch.setattr(
        SkillMatcher,
        "_get_encoder",
        staticmethod(lambda _: FakeEncoder()),
    )

    matcher = SkillMatcher(strategy=MatchingStrategy.SEMANTIC)

    resume = make_skill(
        skill_id="resume-a",
        canonical_name="python",
        source_type=EvidenceSourceType.RESUME,
        document_id="resume-1",
    )
    job = make_skill(
        skill_id="job-a",
        canonical_name="unrelated",
        source_type=EvidenceSourceType.JOB_DESCRIPTION,
        document_id="job-1",
    )

    result = matcher.match([resume], [job])

    assert len(result.skill_matches) == 1
    assert result.skill_matches[0].relationship.value == "unmatched"


def test_matching_preserves_both_sides_evidence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeEncoder:
        def encode(self, texts, normalize_embeddings=True):
            return (
                [1.0, 0.0],
                [0.9, (1.0 - 0.9**2) ** 0.5],
            )

    monkeypatch.setattr(
        SkillMatcher,
        "_get_encoder",
        staticmethod(lambda _: FakeEncoder()),
    )

    matcher = SkillMatcher(strategy=MatchingStrategy.SEMANTIC)

    resume = make_skill(
        skill_id="resume-a",
        canonical_name="python",
        source_type=EvidenceSourceType.RESUME,
        document_id="resume-1",
    )
    job = make_skill(
        skill_id="job-a",
        canonical_name="data analysis",
        source_type=EvidenceSourceType.JOB_DESCRIPTION,
        document_id="job-1",
    )

    result = matcher.match([resume], [job])

    evidence = result.skill_matches[0].evidence

    assert len(evidence) == 2
    assert {
        item.source_type
        for item in evidence
    } == {
        EvidenceSourceType.RESUME,
        EvidenceSourceType.JOB_DESCRIPTION,
    }


def test_matching_metadata_contains_strategy_and_thresholds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeEncoder:
        def encode(self, texts, normalize_embeddings=True):
            return (
                [1.0, 0.0],
                [0.9, (1.0 - 0.9**2) ** 0.5],
            )

    monkeypatch.setattr(
        SkillMatcher,
        "_get_encoder",
        staticmethod(lambda _: FakeEncoder()),
    )

    matcher = SkillMatcher(
        strategy=MatchingStrategy.HYBRID,
        thresholds=MatchingThresholds(
            strong_semantic=0.81,
            partial=0.66,
            related=0.51,
        ),
    )

    resume = make_skill(
        skill_id="resume-a",
        canonical_name="python",
        source_type=EvidenceSourceType.RESUME,
        document_id="resume-1",
    )
    job = make_skill(
        skill_id="job-a",
        canonical_name="data analysis",
        source_type=EvidenceSourceType.JOB_DESCRIPTION,
        document_id="job-1",
    )

    result = matcher.match([resume], [job])

    assert result.metadata["strategy"] == "hybrid"
    assert result.metadata["thresholds"] == {
        "strong_semantic": 0.81,
        "partial": 0.66,
        "related": 0.51,
    }
    assert result.metadata["semantic_model"] == "all-MiniLM-L6-v2"


def test_empty_inputs_produce_empty_matching_result() -> None:
    matcher = SkillMatcher(strategy=MatchingStrategy.HYBRID)

    result = matcher.match([], [])

    assert result.skill_matches == []
    assert result.requirement_alignments == []
    assert result.metadata["candidate_count"] == 0
    assert result.metadata["job_skill_count"] == 0


def test_matching_result_contains_no_phase6_score_or_xai_fields() -> None:
    matcher = SkillMatcher(strategy=MatchingStrategy.KEYWORD)

    resume = make_skill(
        skill_id="resume-python",
        canonical_name="python",
        source_type=EvidenceSourceType.RESUME,
        document_id="resume-1",
    )
    job = make_skill(
        skill_id="job-python",
        canonical_name="python",
        source_type=EvidenceSourceType.JOB_DESCRIPTION,
        document_id="job-1",
    )

    result = matcher.match([resume], [job])

    assert not hasattr(result, "score")
    assert not hasattr(result, "xai")
    assert not hasattr(result, "ranking")


def test_invalid_threshold_order_is_rejected() -> None:
    with pytest.raises(ValueError):
        MatchingThresholds(
            strong_semantic=0.60,
            partial=0.70,
            related=0.50,
        )


def test_semantic_similarity_is_bounded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeEncoder:
        def encode(self, texts, normalize_embeddings=True):
            return (
                [2.0, 0.0],
                [2.0, 0.0],
            )

    monkeypatch.setattr(
        SkillMatcher,
        "_get_encoder",
        staticmethod(lambda _: FakeEncoder()),
    )

    matcher = SkillMatcher(strategy=MatchingStrategy.SEMANTIC)

    resume = make_skill(
        skill_id="resume-a",
        canonical_name="python",
        source_type=EvidenceSourceType.RESUME,
        document_id="resume-1",
    )
    job = make_skill(
        skill_id="job-a",
        canonical_name="java",
        source_type=EvidenceSourceType.JOB_DESCRIPTION,
        document_id="job-1",
    )

    result = matcher.match([resume], [job])

    assert 0.0 <= result.skill_matches[0].similarity <= 1.0
