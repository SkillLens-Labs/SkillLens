from __future__ import annotations

from datetime import datetime, timezone

from backend.app.analysis.resume_improvement_prompt import (
    ResumeImprovementPromptGenerator,
)
from backend.app.domain.analysis import AnalysisInput, AnalysisResult
from backend.app.domain.ats_intelligence import (
    ATSIntelligenceFinding,
    ATSIntelligenceResult,
)
from backend.app.domain.career import (
    CareerDirection,
    CareerDirectionResult,
    CareerIntelligence,
    CareerSeniorityLevel,
    RoleFit,
)
from backend.app.domain.confidence import Confidence
from backend.app.domain.gaps import SkillAnalysis
from backend.app.domain.job import JobProfile
from backend.app.domain.language_quality import (
    AIAuthorshipHeuristic,
    LanguageIssue,
    LanguageIssueSeverity,
    LanguageIssueType,
    ResumeLanguageQualityResult,
)
from backend.app.domain.matching import (
    MatchingResult,
)
from backend.app.domain.recommendations import (
    Recommendation,
    RecommendationEffort,
    RecommendationImpact,
    RecommendationPriority,
    RecommendationType,
)
from backend.app.domain.resume import (
    Certification,
    Contact,
    Education,
    Experience,
    Project,
    ResumeProfile,
)
from backend.app.domain.resume_quality import (
    ResumeQualityFinding,
    ResumeQualityResult,
)
from backend.app.domain.scoring import (
    ScoreAdjustment,
    ScoringResult,
)
from backend.app.domain.skill import Skill
from backend.app.domain.xai import XAIResult


def _confidence() -> Confidence:
    return Confidence(
        score=0.9,
        level="high",
    )


def _resume_profile() -> ResumeProfile:
    return ResumeProfile(
        profile_id="resume-profile-1",
        document_id="document-1",
        candidate_summary="Computer science student focused on data analysis.",
        contact=Contact(
            name="Raghuvir Anturkar",
            email="raghuvir@example.com",
        ),
        education=[
            Education(
                institution="Example University",
                degree="B.E.",
                field_of_study="Computer Science",
                start_date=None,
                end_date=None,
                description=None,
            )
        ],
        experience=[
            Experience(
                company="Example Company",
                role="Data Intern",
                location=None,
                start_date=None,
                end_date=None,
                description="Worked on data analysis.",
                skills=[],
            )
        ],
        projects=[
            Project(
                name="SkillLens",
                description="Resume and skill-gap analysis platform.",
                technologies=["Python", "FastAPI", "React"],
                start_date=None,
                end_date=None,
            )
        ],
        certifications=[
            Certification(
                name="Example Data Certificate",
                issuer="Example Institute",
                issue_date=None,
                expiry_date=None,
                credential_id=None,
            )
        ],
        skills=[
            Skill(
                skill_id="python",
                canonical_name="Python",
                display_name="Python",
                category="programming",
                evidence=[],
                confidence=_confidence(),
            ),
            Skill(
                skill_id="sql",
                canonical_name="SQL",
                display_name="SQL",
                category="database",
                evidence=[],
                confidence=_confidence(),
            ),
        ],
        skill_categories=["programming", "database"],
        total_experience=1.0,
        seniority="entry",
        domains=["data analysis"],
        metadata={},
    )


def _base_result(
    *,
    job_profile=None,
    skill_analysis=None,
    matching=None,
    scoring=None,
) -> AnalysisResult:
    return AnalysisResult(
        analysis_id="analysis-1",
        analysis_mode="resume_jd" if job_profile else "resume_only",
        status="completed",
        created_at=datetime.now(timezone.utc),
        input=AnalysisInput(
            resume_document_id="document-1",
            job_description_document_id=(
                "job-document-1" if job_profile else None
            ),
        ),
        resume_profile=_resume_profile(),
        job_profile=job_profile,
        skill_analysis=(
            skill_analysis
            if skill_analysis is not None
            else SkillAnalysis(
                extracted_skills=["Python", "SQL"],
                matched_skills=[],
                partial_matches=[],
                missing_skills=[],
                transferable_skills=["Problem solving"],
                gaps=[],
            )
        ),
        resume_quality=ResumeQualityResult(
            overall_score=82.0,
            dimension_scores=[],
            findings=[
                ResumeQualityFinding(
                    finding_id="rq-1",
                    category="content_quality",
                    severity="medium",
                    title="Weak achievement wording",
                    explanation="Several bullets describe duties without measurable outcomes.",
                    recommendation="Use evidence-backed outcome-oriented wording.",
                    evidence=[],
                    confidence=_confidence(),
                )
            ],
            confidence=_confidence(),
            warnings=[],
        ),
        ats_intelligence=ATSIntelligenceResult(
            overall_score=88.0,
            dimension_scores=[],
            findings=[
                ATSIntelligenceFinding(
                    finding_id="ats-1",
                    category="skill_detectability",
                    severity="low",
                    title="Skills could be more explicit",
                    explanation="Important technical skills are not consistently explicit in experience bullets.",
                    recommendation="Use accurate skill names where supported by the resume.",
                    evidence=[],
                    confidence=_confidence(),
                )
            ],
            confidence=_confidence(),
            warnings=[],
        ),
        language_quality=ResumeLanguageQualityResult(
            overall_score=91.0,
            issues=[
                LanguageIssue(
                    issue_id="lang-1",
                    issue_type=LanguageIssueType.WORDING,
                    severity=LanguageIssueSeverity.LOW,
                    title="Generic wording",
                    explanation="Some resume statements use generic wording.",
                    recommendation="Use more specific wording supported by actual experience.",
                    original_text="Worked on data",
                    suggested_text="Analyzed data",
                    evidence=[],
                    confidence=_confidence(),
                )
            ],
            confidence=_confidence(),
            authorship_heuristic=AIAuthorshipHeuristic(
                score=20.0,
                level="low_style_signal",
            ),
            warnings=[],
        ),
        matching=matching,
        scoring=scoring,
        xai=XAIResult(
            overall_explanation="The strongest evidence comes from Python and SQL experience.",
            score_explanation="The fit is reduced by missing required analytics tooling.",
            strengths=["Python experience", "Data analysis project"],
            weaknesses=["Missing required analytics tooling"],
            matched_skill_explanations=[],
            missing_skill_explanations=[],
            partial_match_explanations=[],
            evidence_map=[],
            confidence=_confidence(),
        ),
        career_intelligence=CareerIntelligence(
            inferred_profile="Entry-level data-oriented candidate",
            experience_level=CareerSeniorityLevel.ENTRY,
            seniority_confidence=_confidence(),
            seniority_evidence=[],
            seniority_rationale="Resume evidence indicates entry-level experience.",
            primary_domains=["data analysis"],
            secondary_domains=[],
            strengths=["Python", "SQL"],
            limitations=["Limited professional experience"],
            transferable_skills=["Problem solving", "Data analysis"],
            career_directions=[
                CareerDirectionResult(
                    role="Data Analyst",
                    direction=CareerDirection.PRIMARY,
                    fit_score=84.0,
                    rationale="Strong overlap with data analysis skills.",
                    evidence=[],
                    confidence=_confidence(),
                )
            ],
            potential_roles=["Data Analyst"],
            role_fit=[
                RoleFit(
                    role="Data Analyst",
                    fit_score=84.0,
                    direction=CareerDirection.PRIMARY,
                    rationale="Strong overlap with data analysis skills.",
                    evidence=[],
                    confidence=_confidence(),
                )
            ],
            career_signals=["Data-oriented skill profile"],
            transition_analysis=None,
            skill_priorities=[],
            risks=[],
            confidence=_confidence(),
            taxonomy_version="career-taxonomy-v1",
            engine_version="phase7-career-intelligence-v1",
        ),
        recommendations=[
            Recommendation(
                recommendation_id="rec-1",
                type=RecommendationType.LEARNING,
                title="Strengthen analytics tooling",
                target_skill="Power BI",
                priority=RecommendationPriority.HIGH,
                rationale="The target role requires analytics tooling not currently evidenced.",
                expected_impact=RecommendationImpact.HIGH,
                effort=RecommendationEffort.MEDIUM,
                evidence=[],
                related_gap_ids=[],
                confidence=_confidence(),
                priority_score=80.0,
                impact_score=80.0,
                source_engine="recommendation-intelligence-v1",
            )
        ],
        metadata={},
    )


def test_resume_only_prompt_contains_verified_resume_facts():
    result = _base_result()

    prompt = ResumeImprovementPromptGenerator().generate(result)

    assert "Raghuvir Anturkar" in prompt
    assert "Data Intern" in prompt
    assert "Example Company" in prompt
    assert "Python" in prompt
    assert "SQL" in prompt
    assert "SkillLens" in prompt


def test_resume_only_prompt_contains_quality_ats_language_career_and_recommendations():
    prompt = ResumeImprovementPromptGenerator().generate(_base_result())

    assert "RESUME QUALITY" in prompt
    assert "82.0/100" in prompt
    assert "ATS COMPATIBILITY" in prompt
    assert "88.0/100" in prompt
    assert "LANGUAGE QUALITY" in prompt
    assert "91.0/100" in prompt
    assert "CAREER POSITIONING" in prompt
    assert "Data Analyst" in prompt
    assert "RECOMMENDATIONS" in prompt
    assert "Power BI" in prompt


def test_prompt_contains_ai_authorship_heuristic_disclaimer():
    prompt = ResumeImprovementPromptGenerator().generate(_base_result())

    assert "heuristic writing-style estimate" in prompt
    assert "not proof of AI authorship" in prompt


def test_prompt_contains_strict_factuality_rules():
    prompt = ResumeImprovementPromptGenerator().generate(_base_result())

    assert "STRICT FACTUALITY RULES" in prompt
    assert "Do not invent employers." in prompt
    assert "Do not invent job titles." in prompt
    assert "Do not invent dates." in prompt
    assert "Do not invent skills or technologies." in prompt
    assert "Do not invent achievements, responsibilities, or metrics." in prompt
    assert "Do not invent certifications." in prompt
    assert "Do not invent education or experience." in prompt


def test_prompt_does_not_dump_entire_analysis_result_as_json():
    result = _base_result()

    prompt = ResumeImprovementPromptGenerator().generate(result)

    assert '"analysis_id"' not in prompt
    assert '"resume_profile"' not in prompt
    assert '"career_intelligence"' not in prompt


def test_prompt_is_deterministic():
    generator = ResumeImprovementPromptGenerator()
    result = _base_result()

    assert generator.generate(result) == generator.generate(result)


def test_resume_jd_prompt_contains_target_job_and_matching_information():
    job_profile = JobProfile(
        profile_id="job-profile-1",
        document_id="job-document-1",
        job_title="Data Analyst",
        company="Target Analytics",
        summary="Data analysis role.",
        responsibilities=[],
        required_skills=["Python", "Power BI"],
        preferred_skills=["Tableau"],
        technical_skills=["Python", "Power BI", "Tableau"],
        soft_skills=[],
        domain_skills=["Data analysis"],
        experience_requirements=None,
        education_requirements=None,
        seniority="entry",
        metadata={},
    )

    skill_analysis = SkillAnalysis(
        extracted_skills=["Python", "SQL"],
        matched_skills=["Python"],
        partial_matches=["SQL"],
        missing_skills=["Power BI"],
        transferable_skills=["Data analysis"],
        gaps=[],
    )

    scoring = ScoringResult(
        overall_score=72.0,
        skill_score=70.0,
        required_skill_score=65.0,
        preferred_skill_score=50.0,
        experience_score=80.0,
        education_score=90.0,
        domain_score=75.0,
        dimension_scores=[],
        weights={},
        contributions=[],
        penalties=[
            ScoreAdjustment(
                reason="Missing required skill: Power BI",
                value=-10.0,
            )
        ],
        bonuses=[],
        confidence=_confidence(),
    )

    prompt = ResumeImprovementPromptGenerator().generate(
        _base_result(
            job_profile=job_profile,
            skill_analysis=skill_analysis,
            scoring=scoring,
        )
    )

    assert "TARGET JOB" in prompt
    assert "Data Analyst" in prompt
    assert "Target Analytics" in prompt
    assert "72.0/100" in prompt
    assert "Required skills: Python, Power BI" in prompt
    assert "Preferred skills: Tableau" in prompt
    assert "Matched skills: Python" in prompt
    assert "Partial matches: SQL" in prompt
    assert "Missing skills: Power BI" in prompt
    assert "Missing required skill: Power BI" in prompt


def test_prompt_handles_missing_optional_components():
    result = _base_result()

    result.resume_quality = None
    result.ats_intelligence = None
    result.language_quality = None
    result.career_intelligence = None
    result.recommendations = []
    result.xai = None

    prompt = ResumeImprovementPromptGenerator().generate(result)

    assert "CANDIDATE FACTS" in prompt
    assert "STRICT FACTUALITY RULES" in prompt
    assert "RESUME QUALITY" not in prompt
    assert "ATS COMPATIBILITY" not in prompt
    assert "LANGUAGE QUALITY" not in prompt
    assert "CAREER FIT" not in prompt
    assert "RECOMMENDATIONS" not in prompt


def test_generator_exposes_stable_engine_version():
    assert (
        ResumeImprovementPromptGenerator.ENGINE_VERSION
        == "phase9-resume-improvement-prompt-v2"
    )