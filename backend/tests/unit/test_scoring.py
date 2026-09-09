from __future__ import annotations

import pytest

from backend.app.analysis.scoring import ScoringAnalyzer
from backend.app.domain.confidence import Confidence, ConfidenceLevel
from backend.app.domain.job import JobProfile
from backend.app.domain.matching import (
    JobRequirement,
    JobRequirementCategory,
    JobRequirementType,
    MatchingResult,
    RequirementAlignment,
    RequirementMatchStatus,
    SkillMatch,
    MatchRelationship,
)
from backend.app.domain.skill import Skill


def make_requirement(
    *,
    requirement_id: str,
    text: str,
    requirement_type: JobRequirementType = JobRequirementType.REQUIRED,
    category: JobRequirementCategory = JobRequirementCategory.SKILL,
) -> JobRequirement:
    return JobRequirement(
        requirement_id=requirement_id,
        text=text,
        requirement_type=requirement_type,
        category=category,
        confidence=Confidence(
            score=0.90,
            level=ConfidenceLevel.HIGH,
        ),
    )


def make_alignment(
    *,
    requirement_id: str,
    status: RequirementMatchStatus,
    confidence: float = 0.90,
) -> RequirementAlignment:
    return RequirementAlignment(
        requirement_id=requirement_id,
        status=status,
        confidence=Confidence(
            score=confidence,
            level=(
                ConfidenceLevel.HIGH
                if confidence >= 0.85
                else ConfidenceLevel.MEDIUM
            ),
        ),
        rationale=f"test alignment: {status.value}",
    )


def make_skill(
    *,
    skill_id: str,
    canonical_name: str,
) -> Skill:
    return Skill(
        skill_id=skill_id,
        canonical_name=canonical_name,
        display_name=canonical_name.title(),
    )


def make_job_profile(
    *,
    domain_skills: list[str] | None = None,
) -> JobProfile:
    return JobProfile(
        profile_id="job-profile-1",
        document_id="job-1",
        job_title="Data Engineer",
        domain_skills=domain_skills or [],
    )


def make_matching(
    *,
    alignments: list[RequirementAlignment] | None = None,
    skill_matches: list[SkillMatch] | None = None,
) -> MatchingResult:
    return MatchingResult(
        requirement_alignments=alignments or [],
        skill_matches=skill_matches or [],
        confidence=Confidence(
            score=0.90,
            level=ConfidenceLevel.HIGH,
        ),
    )


def test_scoring_weights_are_explicit_and_sum_to_one() -> None:
    analyzer = ScoringAnalyzer()

    assert analyzer._WEIGHTS == {
        "required_skills": 0.50,
        "preferred_skills": 0.15,
        "experience": 0.15,
        "education": 0.10,
        "domain": 0.10,
    }
    assert sum(analyzer._WEIGHTS.values()) == pytest.approx(1.0)


def test_alignment_values_follow_phase6_policy() -> None:
    analyzer = ScoringAnalyzer()

    assert (
        analyzer._ALIGNMENT_VALUES[RequirementMatchStatus.MATCHED]
        == 1.0
    )
    assert (
        analyzer._ALIGNMENT_VALUES[RequirementMatchStatus.PARTIAL]
        == 0.5
    )
    assert (
        analyzer._ALIGNMENT_VALUES[RequirementMatchStatus.UNMATCHED]
        == 0.0
    )
    assert RequirementMatchStatus.UNKNOWN not in analyzer._ALIGNMENT_VALUES


def test_required_skill_score_uses_matched_partial_and_unmatched_values() -> None:
    analyzer = ScoringAnalyzer()

    requirements = [
        make_requirement(
            requirement_id="r1",
            text="Python",
        ),
        make_requirement(
            requirement_id="r2",
            text="SQL",
        ),
        make_requirement(
            requirement_id="r3",
            text="Docker",
        ),
    ]

    matching = make_matching(
        alignments=[
            make_alignment(
                requirement_id="r1",
                status=RequirementMatchStatus.MATCHED,
            ),
            make_alignment(
                requirement_id="r2",
                status=RequirementMatchStatus.PARTIAL,
            ),
            make_alignment(
                requirement_id="r3",
                status=RequirementMatchStatus.UNMATCHED,
            ),
        ]
    )

    result = analyzer.score(
        job_profile=make_job_profile(),
        requirements=requirements,
        matching=matching,
        resume_skills=[],
        job_skills=[],
    )

    assert result.required_skill_score == pytest.approx(50.0)
    assert result.preferred_skill_score == 0.0
    assert result.overall_score == pytest.approx(50.0)
    assert result.skill_score == pytest.approx(50.0)


def test_unknown_requirements_are_excluded_not_scored_as_failures() -> None:
    analyzer = ScoringAnalyzer()

    requirements = [
        make_requirement(
            requirement_id="r1",
            text="Python",
        ),
        make_requirement(
            requirement_id="r2",
            text="SQL",
        ),
    ]

    matching = make_matching(
        alignments=[
            make_alignment(
                requirement_id="r1",
                status=RequirementMatchStatus.MATCHED,
            ),
            make_alignment(
                requirement_id="r2",
                status=RequirementMatchStatus.UNKNOWN,
            ),
        ]
    )

    result = analyzer.score(
        job_profile=make_job_profile(),
        requirements=requirements,
        matching=matching,
        resume_skills=[],
        job_skills=[],
    )

    assert result.required_skill_score == pytest.approx(100.0)
    assert result.overall_score == pytest.approx(100.0)

    contribution_ids = {
        contribution.source_id
        for contribution in result.contributions
    }
    assert "r1" in contribution_ids
    assert "r2" not in contribution_ids


def test_all_unknown_requirements_make_dimension_unavailable() -> None:
    analyzer = ScoringAnalyzer()

    requirements = [
        make_requirement(
            requirement_id="r1",
            text="Python",
        ),
        make_requirement(
            requirement_id="r2",
            text="SQL",
        ),
    ]

    matching = make_matching(
        alignments=[
            make_alignment(
                requirement_id="r1",
                status=RequirementMatchStatus.UNKNOWN,
            ),
            make_alignment(
                requirement_id="r2",
                status=RequirementMatchStatus.UNKNOWN,
            ),
        ]
    )

    result = analyzer.score(
        job_profile=make_job_profile(),
        requirements=requirements,
        matching=matching,
        resume_skills=[],
        job_skills=[],
    )

    assert result.required_skill_score == 0.0
    assert result.overall_score == 0.0
    assert result.dimension_scores == []
    assert result.contributions == []


def test_preferred_skills_use_separate_weight() -> None:
    analyzer = ScoringAnalyzer()

    requirements = [
        make_requirement(
            requirement_id="required-1",
            text="Python",
            requirement_type=JobRequirementType.REQUIRED,
        ),
        make_requirement(
            requirement_id="preferred-1",
            text="Docker",
            requirement_type=JobRequirementType.PREFERRED,
        ),
    ]

    matching = make_matching(
        alignments=[
            make_alignment(
                requirement_id="required-1",
                status=RequirementMatchStatus.MATCHED,
            ),
            make_alignment(
                requirement_id="preferred-1",
                status=RequirementMatchStatus.PARTIAL,
            ),
        ]
    )

    result = analyzer.score(
        job_profile=make_job_profile(),
        requirements=requirements,
        matching=matching,
        resume_skills=[],
        job_skills=[],
    )

    assert result.required_skill_score == pytest.approx(100.0)
    assert result.preferred_skill_score == pytest.approx(50.0)
    expected_score = round(
        ((1.0 * 0.50) + (0.5 * 0.15)) / 0.65 * 100.0,
        2,
    )

    assert result.skill_score == pytest.approx(expected_score)
    assert result.overall_score == pytest.approx(expected_score)


def test_experience_and_education_are_scored_as_separate_dimensions() -> None:
    analyzer = ScoringAnalyzer()

    requirements = [
        make_requirement(
            requirement_id="experience-1",
            text="3 years of experience",
            category=JobRequirementCategory.EXPERIENCE,
        ),
        make_requirement(
            requirement_id="education-1",
            text="Bachelor degree",
            category=JobRequirementCategory.EDUCATION,
        ),
    ]

    matching = make_matching(
        alignments=[
            make_alignment(
                requirement_id="experience-1",
                status=RequirementMatchStatus.MATCHED,
            ),
            make_alignment(
                requirement_id="education-1",
                status=RequirementMatchStatus.PARTIAL,
            ),
        ]
    )

    result = analyzer.score(
        job_profile=make_job_profile(),
        requirements=requirements,
        matching=matching,
        resume_skills=[],
        job_skills=[],
    )

    assert result.experience_score == pytest.approx(100.0)
    assert result.education_score == pytest.approx(50.0)

    dimensions = {
        dimension.dimension: dimension
        for dimension in result.dimension_scores
    }

    assert dimensions["experience"].weight == pytest.approx(0.15)
    assert dimensions["education"].weight == pytest.approx(0.10)


def test_overall_score_renormalizes_available_dimensions() -> None:
    analyzer = ScoringAnalyzer()

    requirements = [
        make_requirement(
            requirement_id="required-1",
            text="Python",
        ),
    ]

    matching = make_matching(
        alignments=[
            make_alignment(
                requirement_id="required-1",
                status=RequirementMatchStatus.MATCHED,
            ),
        ]
    )

    result = analyzer.score(
        job_profile=make_job_profile(),
        requirements=requirements,
        matching=matching,
        resume_skills=[],
        job_skills=[],
    )

    # Only required skills are available.
    # Therefore the 0.50 weight is renormalized to 1.00.
    assert result.required_skill_score == pytest.approx(100.0)
    assert result.overall_score == pytest.approx(100.0)


def test_contributions_sum_to_actual_dimension_weighted_contribution() -> None:
    analyzer = ScoringAnalyzer()

    requirements = [
        make_requirement(
            requirement_id="r1",
            text="Python",
        ),
        make_requirement(
            requirement_id="r2",
            text="SQL",
        ),
    ]

    matching = make_matching(
        alignments=[
            make_alignment(
                requirement_id="r1",
                status=RequirementMatchStatus.MATCHED,
            ),
            make_alignment(
                requirement_id="r2",
                status=RequirementMatchStatus.PARTIAL,
            ),
        ]
    )

    result = analyzer.score(
        job_profile=make_job_profile(),
        requirements=requirements,
        matching=matching,
        resume_skills=[],
        job_skills=[],
    )

    required_contributions = [
        contribution
        for contribution in result.contributions
        if contribution.dimension == "required_skills"
    ]

    assert sum(
        contribution.contribution
        for contribution in required_contributions
    ) == pytest.approx(0.50 * 0.75)

    assert sum(
        contribution.weight
        for contribution in required_contributions
    ) == pytest.approx(0.50)


def test_domain_dimension_is_unavailable_without_explicit_domain_skills() -> None:
    analyzer = ScoringAnalyzer()

    result = analyzer.score(
        job_profile=make_job_profile(domain_skills=[]),
        requirements=[],
        matching=make_matching(),
        resume_skills=[],
        job_skills=[],
    )

    assert result.domain_score == 0.0
    assert not any(
        dimension.dimension == "domain"
        for dimension in result.dimension_scores
    )


def test_domain_score_uses_existing_skill_match_relationship() -> None:
    analyzer = ScoringAnalyzer()

    job_skill = make_skill(
        skill_id="job-domain-1",
        canonical_name="data engineering",
    )
    resume_skill = make_skill(
        skill_id="resume-domain-1",
        canonical_name="data engineering",
    )

    match = SkillMatch(
        resume_skill_id=resume_skill.skill_id,
        job_skill_id=job_skill.skill_id,
        relationship=MatchRelationship.PARTIAL,
        similarity=0.80,
        confidence=Confidence(
            score=0.60,
            level=ConfidenceLevel.MEDIUM,
        ),
    )

    result = analyzer.score(
        job_profile=make_job_profile(
            domain_skills=["data engineering"],
        ),
        requirements=[],
        matching=make_matching(skill_matches=[match]),
        resume_skills=[resume_skill],
        job_skills=[job_skill],
    )

    assert result.domain_score == pytest.approx(50.0)

    domain_contribution = next(
        contribution
        for contribution in result.contributions
        if contribution.dimension == "domain"
    )

    assert domain_contribution.score == pytest.approx(0.5)
    assert domain_contribution.contribution == pytest.approx(0.05)


def test_similarity_and_confidence_remain_separate() -> None:
    analyzer = ScoringAnalyzer()

    job_skill = make_skill(
        skill_id="job-domain-1",
        canonical_name="data engineering",
    )
    resume_skill = make_skill(
        skill_id="resume-domain-1",
        canonical_name="data engineering",
    )

    match = SkillMatch(
        resume_skill_id=resume_skill.skill_id,
        job_skill_id=job_skill.skill_id,
        relationship=MatchRelationship.EXACT,
        similarity=0.73,
        confidence=Confidence(
            score=0.41,
            level=ConfidenceLevel.LOW,
        ),
    )

    result = analyzer.score(
        job_profile=make_job_profile(
            domain_skills=["data engineering"],
        ),
        requirements=[],
        matching=make_matching(skill_matches=[match]),
        resume_skills=[resume_skill],
        job_skills=[job_skill],
    )

    # Domain scoring follows the existing Phase 5 relationship.
    # It does not substitute similarity or confidence for that result.
    assert result.domain_score == pytest.approx(100.0)

    domain_contribution = next(
        contribution
        for contribution in result.contributions
        if contribution.dimension == "domain"
    )

    assert domain_contribution.score == pytest.approx(1.0)


def test_certification_requirement_does_not_create_independent_score_dimension() -> None:
    analyzer = ScoringAnalyzer()

    requirements = [
        make_requirement(
            requirement_id="cert-1",
            text="AWS certification",
            category=JobRequirementCategory.CERTIFICATION,
        ),
    ]

    matching = make_matching(
        alignments=[
            make_alignment(
                requirement_id="cert-1",
                status=RequirementMatchStatus.MATCHED,
            ),
        ]
    )

    result = analyzer.score(
        job_profile=make_job_profile(),
        requirements=requirements,
        matching=matching,
        resume_skills=[],
        job_skills=[],
    )

    assert result.overall_score == 0.0
    assert result.dimension_scores == []
    assert result.contributions == []


def test_scores_remain_on_public_zero_to_hundred_scale() -> None:
    analyzer = ScoringAnalyzer()

    requirements = [
        make_requirement(
            requirement_id="r1",
            text="Python",
        ),
    ]

    for status in RequirementMatchStatus:
        matching = make_matching(
            alignments=[
                make_alignment(
                    requirement_id="r1",
                    status=status,
                )
            ]
        )

        result = analyzer.score(
            job_profile=make_job_profile(),
            requirements=requirements,
            matching=matching,
            resume_skills=[],
            job_skills=[],
        )

        assert 0.0 <= result.overall_score <= 100.0
        assert 0.0 <= result.required_skill_score <= 100.0


def test_scoring_is_deterministic_for_identical_inputs() -> None:
    analyzer = ScoringAnalyzer()

    requirements = [
        make_requirement(
            requirement_id="r1",
            text="Python",
        ),
        make_requirement(
            requirement_id="r2",
            text="SQL",
            requirement_type=JobRequirementType.PREFERRED,
        ),
    ]

    matching = make_matching(
        alignments=[
            make_alignment(
                requirement_id="r1",
                status=RequirementMatchStatus.MATCHED,
            ),
            make_alignment(
                requirement_id="r2",
                status=RequirementMatchStatus.PARTIAL,
            ),
        ]
    )

    first = analyzer.score(
        job_profile=make_job_profile(),
        requirements=requirements,
        matching=matching,
        resume_skills=[],
        job_skills=[],
    )

    second = analyzer.score(
        job_profile=make_job_profile(),
        requirements=requirements,
        matching=matching,
        resume_skills=[],
        job_skills=[],
    )

    assert first.model_dump(mode="json") == second.model_dump(mode="json")
