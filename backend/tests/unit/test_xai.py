from __future__ import annotations

import pytest

from backend.app.analysis.xai import XAIAnalyzer
from backend.app.domain.confidence import Confidence, ConfidenceLevel
from backend.app.domain.evidence import Evidence, EvidenceSourceType
from backend.app.domain.gaps import SkillAnalysis, SkillGap
from backend.app.domain.matching import MatchRelationship, SkillMatch
from backend.app.domain.scoring import (
    DimensionScore,
    ScoreContribution,
    ScoringResult,
)
from backend.app.domain.skill import Skill


def _confidence(score: float = 0.90) -> Confidence:
    return Confidence(
        score=score,
        level=(
            ConfidenceLevel.HIGH
            if score >= 0.85
            else ConfidenceLevel.MEDIUM
            if score >= 0.65
            else ConfidenceLevel.LOW
        ),
        rationale="test confidence",
    )


def _evidence(
    evidence_id: str,
    text: str,
    source_type: EvidenceSourceType = EvidenceSourceType.RESUME,
) -> Evidence:
    return Evidence(
        evidence_id=evidence_id,
        source_type=source_type,
        source_document_id=(
            "resume-1"
            if source_type == EvidenceSourceType.RESUME
            else "job-1"
        ),
        section="Skills",
        text=text,
        evidence_type="skill_mention",
        confidence=0.90,
    )


def _skill(skill_id: str, name: str) -> Skill:
    return Skill(
        skill_id=skill_id,
        canonical_name=name,
        display_name=name,
        evidence=[_evidence(f"evidence-{skill_id}", name)],
        confidence=_confidence(),
    )


def _scoring() -> ScoringResult:
    return ScoringResult(
        overall_score=75.0,
        skill_score=80.0,
        required_skill_score=80.0,
        preferred_skill_score=60.0,
        experience_score=100.0,
        education_score=50.0,
        domain_score=0.0,
        dimension_scores=[
            DimensionScore(
                dimension="required_skills",
                score=80.0,
                weight=0.50,
            ),
            DimensionScore(
                dimension="preferred_skills",
                score=60.0,
                weight=0.15,
            ),
            DimensionScore(
                dimension="experience",
                score=100.0,
                weight=0.15,
            ),
            DimensionScore(
                dimension="education",
                score=50.0,
                weight=0.10,
            ),
        ],
        weights={
            "required_skills": 0.50,
            "preferred_skills": 0.15,
            "experience": 0.15,
            "education": 0.10,
            "domain": 0.10,
        },
        contributions=[
            ScoreContribution(
                contribution_id="contrib-required-python",
                dimension="required_skills",
                source_type="requirement",
                source_id="req-python",
                score=1.0,
                weight=0.50,
                contribution=0.50,
                rationale="matched requirement",
                requirement_type="required",
            ),
            ScoreContribution(
                contribution_id="contrib-required-sql",
                dimension="required_skills",
                source_type="requirement",
                source_id="req-sql",
                score=0.50,
                weight=0.50,
                contribution=0.25,
                rationale="partial requirement",
                requirement_type="required",
            ),
        ],
        confidence=_confidence(0.85),
    )


def _gap(
    *,
    gap_id: str,
    requirement_id: str,
    skill_id: str,
    skill_name: str,
    gap_type: str,
    match_status: str,
    similarity: float | None,
) -> SkillGap:
    return SkillGap(
        gap_id=gap_id,
        requirement_id=requirement_id,
        requirement_type="required",
        target_skill_id=skill_id,
        target_skill_name=skill_name,
        match_status=match_status,
        gap_type=gap_type,
        severity=(
            "medium"
            if gap_type == "partial"
            else "high"
            if gap_type == "unmatched"
            else "unknown"
        ),
        similarity=similarity,
        rationale=f"{gap_type} requirement",
        evidence=[
            _evidence(
                f"evidence-{gap_id}",
                skill_name,
                EvidenceSourceType.JOB_DESCRIPTION,
            )
        ],
        confidence=_confidence(0.80),
    )


def test_xai_has_phase6_engine_version() -> None:
    assert XAIAnalyzer.ENGINE_VERSION == "phase6-xai-v1"


def test_xai_explains_existing_score_without_recalculating_it() -> None:
    scoring = _scoring()

    result = XAIAnalyzer().explain(
        scoring=scoring,
        skill_analysis=SkillAnalysis(),
        matching=None,
    )

    assert result.score_explanation is not None
    assert "75.0" in result.score_explanation
    assert "required_skills" in result.score_explanation


def test_score_explanation_uses_existing_contributions() -> None:
    scoring = _scoring()

    result = XAIAnalyzer().explain(
        scoring=scoring,
        skill_analysis=SkillAnalysis(),
        matching=None,
    )

    assert result.score_explanation is not None
    assert "req-python" in result.score_explanation
    assert "req-sql" in result.score_explanation
    assert "matched requirement" in result.score_explanation


def test_matched_skill_explanation_preserves_existing_evidence() -> None:
    skill = _skill("resume-python", "Python")

    matching = type(
        "MatchingStub",
        (),
        {
            "skill_matches": [
                SkillMatch(
                    resume_skill_id="resume-python",
                    job_skill_id="job-python",
                    relationship=MatchRelationship.EXACT,
                    similarity=1.0,
                    confidence=_confidence(),
                    evidence=skill.evidence,
                    rationale="exact canonical match",
                )
            ]
        },
    )()

    skill_analysis = SkillAnalysis(
        extracted_skills=["Python"],
        matched_skills=["Python"],
    )

    result = XAIAnalyzer().explain(
        scoring=None,
        skill_analysis=skill_analysis,
        matching=matching,
        resume_skills=[skill],
        job_skills=[],
    )

    assert len(result.matched_skill_explanations) == 1

    explanation = result.matched_skill_explanations[0]
    assert explanation.skill_id == "resume-python"
    assert explanation.evidence == skill.evidence
    assert explanation.confidence is not None
    assert "exact" in explanation.explanation


def test_partial_gap_explanation_preserves_gap_evidence() -> None:
    gap = _gap(
        gap_id="gap-sql",
        requirement_id="req-sql",
        skill_id="job-sql",
        skill_name="SQL",
        gap_type="partial",
        match_status="partial",
        similarity=0.72,
    )

    result = XAIAnalyzer().explain(
        scoring=None,
        skill_analysis=SkillAnalysis(
            partial_matches=["SQL"],
            gaps=[gap],
        ),
        matching=None,
    )

    assert len(result.partial_match_explanations) == 1

    explanation = result.partial_match_explanations[0]
    assert explanation.skill_id == "job-sql"
    assert explanation.evidence == gap.evidence
    assert explanation.confidence == gap.confidence
    assert "partial" in explanation.explanation


def test_unmatched_gap_becomes_missing_skill_explanation() -> None:
    gap = _gap(
        gap_id="gap-docker",
        requirement_id="req-docker",
        skill_id="job-docker",
        skill_name="Docker",
        gap_type="unmatched",
        match_status="unmatched",
        similarity=None,
    )

    result = XAIAnalyzer().explain(
        scoring=None,
        skill_analysis=SkillAnalysis(
            missing_skills=["Docker"],
            gaps=[gap],
        ),
        matching=None,
    )

    assert len(result.missing_skill_explanations) == 1

    explanation = result.missing_skill_explanations[0]
    assert explanation.skill_id == "job-docker"
    assert explanation.evidence == gap.evidence
    assert "unmatched" in explanation.explanation


def test_unknown_gap_is_not_presented_as_missing_skill() -> None:
    gap = _gap(
        gap_id="gap-kubernetes",
        requirement_id="req-kubernetes",
        skill_id="job-kubernetes",
        skill_name="Kubernetes",
        gap_type="unknown",
        match_status="unknown",
        similarity=None,
    )

    result = XAIAnalyzer().explain(
        scoring=None,
        skill_analysis=SkillAnalysis(
            gaps=[gap],
        ),
        matching=None,
    )

    assert result.missing_skill_explanations == []
    assert result.partial_match_explanations == []
    assert not any(
        "Kubernetes" in weakness
        for weakness in result.weaknesses
    )


def test_evidence_map_contains_gap_evidence() -> None:
    gap = _gap(
        gap_id="gap-docker",
        requirement_id="req-docker",
        skill_id="job-docker",
        skill_name="Docker",
        gap_type="unmatched",
        match_status="unmatched",
        similarity=None,
    )

    result = XAIAnalyzer().explain(
        scoring=None,
        skill_analysis=SkillAnalysis(gaps=[gap]),
        matching=None,
    )

    entries = {
        entry.result_id: entry
        for entry in result.evidence_map
    }

    assert "gap-docker" in entries
    assert entries["gap-docker"].result_type == "skill_gap"
    assert entries["gap-docker"].evidence == gap.evidence


def test_strengths_and_weaknesses_are_based_on_existing_results() -> None:
    gaps = [
        _gap(
            gap_id="gap-docker",
            requirement_id="req-docker",
            skill_id="job-docker",
            skill_name="Docker",
            gap_type="unmatched",
            match_status="unmatched",
            similarity=None,
        )
    ]

    result = XAIAnalyzer().explain(
        scoring=_scoring(),
        skill_analysis=SkillAnalysis(
            matched_skills=["Python"],
            missing_skills=["Docker"],
            gaps=gaps,
        ),
        matching=None,
    )

    assert result.strengths
    assert any("Python" in strength for strength in result.strengths)

    assert result.weaknesses
    assert any("Docker" in weakness for weakness in result.weaknesses)


def test_xai_confidence_does_not_use_similarity_as_confidence() -> None:
    gap = _gap(
        gap_id="gap-sql",
        requirement_id="req-sql",
        skill_id="job-sql",
        skill_name="SQL",
        gap_type="partial",
        match_status="partial",
        similarity=0.99,
    )

    gap.confidence = _confidence(0.40)

    result = XAIAnalyzer().explain(
        scoring=None,
        skill_analysis=SkillAnalysis(gaps=[gap]),
        matching=None,
    )

    assert result.confidence is not None
    assert result.confidence.score == pytest.approx(0.40)


def test_xai_is_deterministic_for_identical_inputs() -> None:
    scoring = _scoring()

    skill_analysis = SkillAnalysis(
        matched_skills=["Python"],
        partial_matches=["SQL"],
        missing_skills=["Docker"],
        gaps=[
            _gap(
                gap_id="gap-sql",
                requirement_id="req-sql",
                skill_id="job-sql",
                skill_name="SQL",
                gap_type="partial",
                match_status="partial",
                similarity=0.72,
            ),
            _gap(
                gap_id="gap-docker",
                requirement_id="req-docker",
                skill_id="job-docker",
                skill_name="Docker",
                gap_type="unmatched",
                match_status="unmatched",
                similarity=None,
            ),
        ],
    )

    analyzer = XAIAnalyzer()

    first = analyzer.explain(
        scoring=scoring,
        skill_analysis=skill_analysis,
        matching=None,
    )

    second = analyzer.explain(
        scoring=scoring,
        skill_analysis=skill_analysis,
        matching=None,
    )

    assert first.model_dump(mode="json") == second.model_dump(mode="json")
