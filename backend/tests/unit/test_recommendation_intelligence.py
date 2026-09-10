from backend.app.analysis.recommendation_intelligence import (
    ENGINE_VERSION,
    RecommendationIntelligence,
)
from backend.app.domain.confidence import Confidence, ConfidenceLevel
from backend.app.domain.evidence import Evidence, EvidenceSourceType
from backend.app.domain.gaps import SkillAnalysis, SkillGap
from backend.app.domain.job import JobProfile
from backend.app.domain.matching import (
    JobRequirement,
    JobRequirementCategory,
    JobRequirementType,
    MatchingResult,
    RequirementAlignment,
    RequirementMatchStatus,
)
from backend.app.domain.recommendations import (
    RecommendationPriority,
    RecommendationType,
)
from backend.app.domain.resume import ResumeProfile
from backend.app.domain.skill import Skill


def make_resume_profile(
    *,
    candidate_summary: str | None = "Experienced software engineer.",
    skills: list | None = None,
) -> ResumeProfile:
    if skills is None:
        skills = [
            Skill(
                skill_id="python",
                canonical_name="python",
                display_name="Python",
            )
        ]

    return ResumeProfile(
        profile_id="resume-profile-test",
        document_id="resume-document-test",
        candidate_summary=candidate_summary,
        skills=skills,
    )


def make_gap(
    *,
    gap_id: str,
    skill: str,
    requirement_type: str = "required",
    match_status: str = "unmatched",
    severity: str = "high",
    similarity: float | None = None,
    confidence: Confidence | None = None,
) -> SkillGap:
    return SkillGap(
        gap_id=gap_id,
        requirement_id=f"req-{gap_id}",
        requirement_type=requirement_type,
        target_skill_id=f"skill-{skill.lower().replace(' ', '-')}",
        target_skill_name=skill,
        match_status=match_status,
        gap_type=match_status,
        severity=severity,
        similarity=similarity,
        rationale=f"Gap rationale for {skill}.",
        evidence=[],
        confidence=confidence,
    )


def make_requirement(
    *,
    requirement_id: str,
    text: str,
    category: JobRequirementCategory,
    requirement_type: JobRequirementType = JobRequirementType.REQUIRED,
) -> JobRequirement:
    return JobRequirement(
        requirement_id=requirement_id,
        text=text,
        requirement_type=requirement_type,
        category=category,
        evidence=[],
        confidence=Confidence(
            score=0.90,
            level=ConfidenceLevel.HIGH,
        ),
    )


def make_alignment(
    *,
    requirement_id: str,
    status: RequirementMatchStatus,
) -> RequirementAlignment:
    return RequirementAlignment(
        requirement_id=requirement_id,
        status=status,
        evidence=[],
        confidence=Confidence(
            score=0.90,
            level=ConfidenceLevel.HIGH,
        ),
        rationale="structured requirement alignment",
    )


def test_engine_has_expected_version():
    engine = RecommendationIntelligence()

    assert engine.ENGINE_VERSION == ENGINE_VERSION
    assert ENGINE_VERSION == "recommendation-intelligence-v1"


def test_matched_gaps_do_not_generate_recommendations():
    engine = RecommendationIntelligence()

    skill_analysis = SkillAnalysis(
        gaps=[
            make_gap(
                gap_id="matched-1",
                skill="Python",
                match_status="matched",
            )
        ]
    )

    recommendations = engine.generate(
        resume_profile=make_resume_profile(),
        skill_analysis=skill_analysis,
    )

    assert all(
        recommendation.target_skill != "Python"
        for recommendation in recommendations
    )


def test_required_unmatched_gap_generates_high_priority_learning_recommendation():
    engine = RecommendationIntelligence()

    skill_analysis = SkillAnalysis(
        gaps=[
            make_gap(
                gap_id="gap-1",
                skill="Docker",
                requirement_type="required",
                match_status="unmatched",
                severity="high",
            )
        ]
    )

    recommendations = engine.generate(
        resume_profile=make_resume_profile(),
        skill_analysis=skill_analysis,
    )

    assert len(recommendations) == 1

    recommendation = recommendations[0]

    assert recommendation.type == RecommendationType.LEARNING
    assert recommendation.target_skill == "Docker"
    assert recommendation.priority == RecommendationPriority.CRITICAL
    assert recommendation.related_gap_ids == ["gap-1"]
    assert recommendation.priority_score == 100.0
    assert recommendation.impact_score == 90.0
    assert recommendation.source_engine == ENGINE_VERSION
    assert recommendation.confidence is not None


def test_preferred_gap_ranks_below_required_gap():
    engine = RecommendationIntelligence()

    skill_analysis = SkillAnalysis(
        gaps=[
            make_gap(
                gap_id="preferred-gap",
                skill="Kubernetes",
                requirement_type="preferred",
                match_status="unmatched",
                severity="medium",
            ),
            make_gap(
                gap_id="required-gap",
                skill="Docker",
                requirement_type="required",
                match_status="unmatched",
                severity="medium",
            ),
        ]
    )

    recommendations = engine.generate(
        resume_profile=make_resume_profile(),
        skill_analysis=skill_analysis,
    )

    gap_order = [
        recommendation.related_gap_ids[0]
        for recommendation in recommendations
        if recommendation.related_gap_ids
    ]

    assert gap_order.index("required-gap") < gap_order.index("preferred-gap")


def test_partial_gap_generates_recommendation():
    engine = RecommendationIntelligence()

    skill_analysis = SkillAnalysis(
        gaps=[
            make_gap(
                gap_id="partial-1",
                skill="SQL",
                requirement_type="required",
                match_status="partial",
                severity="medium",
                similarity=0.72,
            )
        ]
    )

    recommendations = engine.generate(
        resume_profile=make_resume_profile(),
        skill_analysis=skill_analysis,
    )

    assert len(recommendations) == 1

    recommendation = recommendations[0]

    assert recommendation.target_skill == "SQL"
    assert "partially aligned" in recommendation.rationale
    assert recommendation.priority_score == 83.0
    assert recommendation.impact_score == 83.0
    assert recommendation.confidence is not None
    assert recommendation.confidence.score == 0.72
    assert recommendation.confidence.level == ConfidenceLevel.MEDIUM


def test_existing_gap_confidence_is_reused():
    engine = RecommendationIntelligence()

    confidence = Confidence(
        score=0.91,
        level=ConfidenceLevel.HIGH,
        components={"upstream": 0.91},
        rationale="Existing upstream confidence.",
    )

    skill_analysis = SkillAnalysis(
        gaps=[
            make_gap(
                gap_id="confidence-1",
                skill="Python",
                confidence=confidence,
            )
        ]
    )

    recommendations = engine.generate(
        resume_profile=make_resume_profile(),
        skill_analysis=skill_analysis,
    )

    assert len(recommendations) == 1
    assert recommendations[0].confidence == confidence


def test_recommendation_ids_are_deterministic():
    engine = RecommendationIntelligence()

    skill_analysis = SkillAnalysis(
        gaps=[
            make_gap(
                gap_id="stable-1",
                skill="Docker",
            )
        ]
    )

    first = engine.generate(
        resume_profile=make_resume_profile(),
        skill_analysis=skill_analysis,
    )

    second = engine.generate(
        resume_profile=make_resume_profile(),
        skill_analysis=skill_analysis,
    )

    assert first[0].recommendation_id == second[0].recommendation_id
    assert first[0].model_dump() == second[0].model_dump()


def test_recommendation_order_is_deterministic():
    engine = RecommendationIntelligence()

    skill_analysis = SkillAnalysis(
        gaps=[
            make_gap(
                gap_id="gap-b",
                skill="Kubernetes",
                requirement_type="preferred",
            ),
            make_gap(
                gap_id="gap-a",
                skill="Docker",
                requirement_type="required",
            ),
        ]
    )

    first = engine.generate(
        resume_profile=make_resume_profile(),
        skill_analysis=skill_analysis,
    )

    reversed_input = SkillAnalysis(
        gaps=list(reversed(skill_analysis.gaps))
    )

    second = engine.generate(
        resume_profile=make_resume_profile(),
        skill_analysis=reversed_input,
    )

    assert [
        recommendation.recommendation_id
        for recommendation in first
    ] == [
        recommendation.recommendation_id
        for recommendation in second
    ]


def test_missing_resume_summary_generates_resume_recommendation():
    engine = RecommendationIntelligence()

    recommendations = engine.generate(
        resume_profile=make_resume_profile(candidate_summary=None),
    )

    resume_recommendations = [
        recommendation
        for recommendation in recommendations
        if recommendation.type == RecommendationType.RESUME
    ]

    assert len(resume_recommendations) == 1
    assert resume_recommendations[0].target_skill is None
    assert resume_recommendations[0].title == "Add a professional summary"


def test_missing_resume_skills_generates_resume_recommendation():
    engine = RecommendationIntelligence()

    recommendations = engine.generate(
        resume_profile=make_resume_profile(skills=[]),
    )

    resume_recommendations = [
        recommendation
        for recommendation in recommendations
        if recommendation.type == RecommendationType.RESUME
    ]

    assert any(
        recommendation.title == "Strengthen the skills section"
        for recommendation in resume_recommendations
    )


def test_engine_can_generate_without_optional_upstream_results():
    engine = RecommendationIntelligence()

    recommendations = engine.generate(
        resume_profile=make_resume_profile(
            candidate_summary="Software engineer.",
            skills=[],
        ),
    )

    assert isinstance(recommendations, list)
    assert all(
        recommendation.type == RecommendationType.RESUME
        for recommendation in recommendations
    )


def test_unmatched_certification_requirement_generates_certification_recommendation():
    engine = RecommendationIntelligence()

    requirement = make_requirement(
        requirement_id="req-aws-cert",
        text="AWS Certified Solutions Architect",
        category=JobRequirementCategory.CERTIFICATION,
    )

    matching = MatchingResult(
        requirement_alignments=[
            make_alignment(
                requirement_id="req-aws-cert",
                status=RequirementMatchStatus.UNMATCHED,
            )
        ]
    )

    recommendations = engine.generate(
        resume_profile=make_resume_profile(),
        matching=matching,
        requirements=[requirement],
    )

    assert len(recommendations) == 1

    recommendation = recommendations[0]

    assert recommendation.type == RecommendationType.CERTIFICATION
    assert recommendation.target_skill is None
    assert "AWS Certified Solutions Architect" in recommendation.title
    assert recommendation.related_gap_ids == []
    assert recommendation.evidence == []
    assert recommendation.source_engine == ENGINE_VERSION


def test_unmatched_experience_requirement_generates_project_recommendation():
    engine = RecommendationIntelligence()

    requirement = make_requirement(
        requirement_id="req-experience",
        text="3 years of cloud engineering experience",
        category=JobRequirementCategory.EXPERIENCE,
    )

    matching = MatchingResult(
        requirement_alignments=[
            make_alignment(
                requirement_id="req-experience",
                status=RequirementMatchStatus.UNMATCHED,
            )
        ]
    )

    recommendations = engine.generate(
        resume_profile=make_resume_profile(),
        matching=matching,
        requirements=[requirement],
    )

    assert len(recommendations) == 1

    recommendation = recommendations[0]

    assert recommendation.type == RecommendationType.PROJECT
    assert recommendation.target_skill is None
    assert "Build experience" in recommendation.title


def test_unmatched_education_requirement_generates_career_recommendation():
    engine = RecommendationIntelligence()

    requirement = make_requirement(
        requirement_id="req-education",
        text="Bachelor degree in Computer Science",
        category=JobRequirementCategory.EDUCATION,
    )

    matching = MatchingResult(
        requirement_alignments=[
            make_alignment(
                requirement_id="req-education",
                status=RequirementMatchStatus.UNMATCHED,
            )
        ]
    )

    recommendations = engine.generate(
        resume_profile=make_resume_profile(),
        matching=matching,
        requirements=[requirement],
    )

    assert len(recommendations) == 1

    recommendation = recommendations[0]

    assert recommendation.type == RecommendationType.CAREER
    assert "education requirement" in recommendation.title.lower()


def test_matched_structured_requirement_does_not_generate_recommendation():
    engine = RecommendationIntelligence()

    requirement = make_requirement(
        requirement_id="req-cert",
        text="AWS certification",
        category=JobRequirementCategory.CERTIFICATION,
    )

    matching = MatchingResult(
        requirement_alignments=[
            make_alignment(
                requirement_id="req-cert",
                status=RequirementMatchStatus.MATCHED,
            )
        ]
    )

    recommendations = engine.generate(
        resume_profile=make_resume_profile(),
        matching=matching,
        requirements=[requirement],
    )

    assert recommendations == []


def test_preferred_structured_requirement_ranks_below_required():
    engine = RecommendationIntelligence()

    required = make_requirement(
        requirement_id="req-required-cert",
        text="AWS certification",
        category=JobRequirementCategory.CERTIFICATION,
        requirement_type=JobRequirementType.REQUIRED,
    )

    preferred = make_requirement(
        requirement_id="req-preferred-cert",
        text="Azure certification",
        category=JobRequirementCategory.CERTIFICATION,
        requirement_type=JobRequirementType.PREFERRED,
    )

    matching = MatchingResult(
        requirement_alignments=[
            make_alignment(
                requirement_id="req-preferred-cert",
                status=RequirementMatchStatus.UNMATCHED,
            ),
            make_alignment(
                requirement_id="req-required-cert",
                status=RequirementMatchStatus.UNMATCHED,
            ),
        ]
    )

    recommendations = engine.generate(
        resume_profile=make_resume_profile(),
        matching=matching,
        requirements=[preferred, required],
    )

    assert len(recommendations) == 2

    assert (
        recommendations[0].type == RecommendationType.CERTIFICATION
    )
    assert recommendations[0].priority_score > recommendations[1].priority_score


def test_structured_requirement_preserves_alignment_evidence_and_confidence():
    engine = RecommendationIntelligence()

    evidence = Evidence(
        evidence_id="alignment-cert-1",
        source_type=EvidenceSourceType.JOB_DESCRIPTION,
        source_document_id="job-1",
        section="Certifications",
        text="AWS Certified Solutions Architect",
        evidence_type="certification_requirement",
        confidence=0.95,
    )

    requirement = JobRequirement(
        requirement_id="req-cert",
        text="AWS Certified Solutions Architect",
        requirement_type=JobRequirementType.REQUIRED,
        category=JobRequirementCategory.CERTIFICATION,
        evidence=[evidence],
        confidence=Confidence(
            score=0.92,
            level=ConfidenceLevel.HIGH,
        ),
    )

    alignment_confidence = Confidence(
        score=0.88,
        level=ConfidenceLevel.HIGH,
        components={"alignment": 0.88},
        rationale="Alignment evidence confidence.",
    )

    alignment = RequirementAlignment(
        requirement_id="req-cert",
        status=RequirementMatchStatus.UNMATCHED,
        evidence=[evidence],
        confidence=alignment_confidence,
        rationale="Certification not found in resume.",
    )

    matching = MatchingResult(
        requirement_alignments=[alignment],
    )

    recommendations = engine.generate(
        resume_profile=make_resume_profile(),
        matching=matching,
        requirements=[requirement],
    )

    assert len(recommendations) == 1
    assert recommendations[0].evidence == [evidence]
    assert recommendations[0].confidence == alignment_confidence