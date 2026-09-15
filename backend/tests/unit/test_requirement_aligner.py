from dataclasses import dataclass

from backend.app.analysis.requirement_aligner import RequirementAligner
from backend.app.analysis.resume_structure import (
    ResumeSection,
    ResumeSectionType,
    StructuredResume,
)
from backend.app.domain.confidence import Confidence, ConfidenceLevel
from backend.app.domain.evidence import Evidence, EvidenceSourceType
from backend.app.domain.matching import (
    JobRequirement,
    JobRequirementCategory,
    JobRequirementType,
    MatchRelationship,
    RequirementMatchStatus,
    SkillMatch,
)
from backend.app.domain.skill import Skill
from backend.app.infrastructure.parsers.models import (
    DocumentBlock,
    DocumentBlockType,
    SourceLocation,
)


def _confidence() -> Confidence:
    return Confidence(
        score=0.9,
        level=ConfidenceLevel.HIGH,
        rationale="Strong evidence.",
    )


def _job_evidence(text: str) -> Evidence:
    return Evidence(
        evidence_id=f"job-{text.lower()}",
        source_type=EvidenceSourceType.JOB_DESCRIPTION,
        source_document_id="job-1",
        section="Required Qualifications",
        text=text,
        evidence_type="requirement_mention",
        confidence=0.95,
    )


def _resume_evidence(text: str) -> Evidence:
    return Evidence(
        evidence_id=f"resume-{text.lower()}",
        source_type=EvidenceSourceType.RESUME,
        source_document_id="resume-1",
        section="Skills",
        text=text,
        evidence_type="skill_mention",
        confidence=0.95,
    )


def _skill(skill_id: str, name: str) -> Skill:
    return Skill(
        skill_id=skill_id,
        canonical_name=name,
        display_name=name,
        evidence=[_resume_evidence(name)],
        confidence=_confidence(),
    )


def _resume_structure(
    sections: tuple[ResumeSection, ...],
) -> StructuredResume:
    return StructuredResume(
        document_id="resume-1",
        sections=sections,
    )


def _resume_block(text: str, section: ResumeSectionType) -> DocumentBlock:
    return DocumentBlock(
        text=text,
        block_type=DocumentBlockType.PARAGRAPH,
        source=SourceLocation(block_index=1),
        section=section.value,
    )


def _skill_requirement(
    requirement_id: str,
    text: str,
    canonical_name: str | None = None,
) -> JobRequirement:
    return JobRequirement(
        requirement_id=requirement_id,
        text=text,
        requirement_type=JobRequirementType.REQUIRED,
        category=JobRequirementCategory.SKILL,
        canonical_name=canonical_name,
        evidence=[_job_evidence(text)],
        confidence=_confidence(),
    )


def test_skill_requirement_exact_match_is_matched() -> None:
    python = _skill("resume-python", "Python")
    job_python = _skill("job-python", "Python")

    requirement = _skill_requirement(
        "req-python",
        "Python",
        canonical_name="Python",
    )

    skill_match = SkillMatch(
        resume_skill_id=python.skill_id,
        job_skill_id=job_python.skill_id,
        relationship=MatchRelationship.EXACT,
        similarity=1.0,
        confidence=_confidence(),
        evidence=[
            *python.evidence,
            _job_evidence("Python"),
        ],
    )

    result = RequirementAligner().align(
        [requirement],
        [skill_match],
        [python],
        [job_python],
        _resume_structure(()),
    )

    assert len(result) == 1
    assert result[0].status == RequirementMatchStatus.MATCHED
    assert result[0].requirement_id == "req-python"
    assert result[0].evidence
    assert result[0].confidence is not None


def test_skill_requirement_semantic_partial_match_is_partial() -> None:
    python = _skill("resume-python", "Python")
    job_python = _skill("job-python", "Python")

    requirement = _skill_requirement(
        "req-python",
        "Python",
        canonical_name="Python",
    )

    skill_match = SkillMatch(
        resume_skill_id=python.skill_id,
        job_skill_id=job_python.skill_id,
        relationship=MatchRelationship.PARTIAL,
        similarity=0.70,
        confidence=_confidence(),
        evidence=[*python.evidence, _job_evidence("Python")],
    )

    result = RequirementAligner().align(
        [requirement],
        [skill_match],
        [python],
        [job_python],
        _resume_structure(()),
    )

    assert result[0].status == RequirementMatchStatus.PARTIAL

def test_compound_skill_requirement_is_partial_when_one_skill_is_missing() -> None:
    python = _skill("resume-python", "Python")
    react = _skill("resume-react", "React")
    job_python = _skill("job-python", "Python")
    job_react = _skill("job-react", "React")
    job_javascript = _skill("job-javascript", "JavaScript")

    requirement = _skill_requirement(
        "req-web-stack",
        "Knowledge of React, JavaScript, and Python",
    )

    skill_matches = [
        SkillMatch(
            resume_skill_id=python.skill_id,
            job_skill_id=job_python.skill_id,
            relationship=MatchRelationship.EXACT,
            similarity=1.0,
            confidence=_confidence(),
            evidence=[*python.evidence, _job_evidence("Python")],
        ),
        SkillMatch(
            resume_skill_id=react.skill_id,
            job_skill_id=job_react.skill_id,
            relationship=MatchRelationship.EXACT,
            similarity=1.0,
            confidence=_confidence(),
            evidence=[*react.evidence, _job_evidence("React")],
        ),
    ]

    result = RequirementAligner().align(
        [requirement],
        skill_matches,
        [python, react],
        [job_python, job_react, job_javascript],
        _resume_structure(()),
    )

    assert result[0].status == RequirementMatchStatus.PARTIAL


def test_compound_skill_requirement_is_matched_when_all_skills_match() -> None:
    python = _skill("resume-python", "Python")
    react = _skill("resume-react", "React")
    javascript = _skill("resume-javascript", "JavaScript")

    job_python = _skill("job-python", "Python")
    job_react = _skill("job-react", "React")
    job_javascript = _skill("job-javascript", "JavaScript")

    requirement = _skill_requirement(
        "req-web-stack",
        "Knowledge of React, JavaScript, and Python",
    )

    skill_matches = [
        SkillMatch(
            resume_skill_id=python.skill_id,
            job_skill_id=job_python.skill_id,
            relationship=MatchRelationship.EXACT,
            similarity=1.0,
            confidence=_confidence(),
            evidence=[*python.evidence, _job_evidence("Python")],
        ),
        SkillMatch(
            resume_skill_id=react.skill_id,
            job_skill_id=job_react.skill_id,
            relationship=MatchRelationship.EXACT,
            similarity=1.0,
            confidence=_confidence(),
            evidence=[*react.evidence, _job_evidence("React")],
        ),
        SkillMatch(
            resume_skill_id=javascript.skill_id,
            job_skill_id=job_javascript.skill_id,
            relationship=MatchRelationship.EXACT,
            similarity=1.0,
            confidence=_confidence(),
            evidence=[
                *javascript.evidence,
                _job_evidence("JavaScript"),
            ],
        ),
    ]

    result = RequirementAligner().align(
        [requirement],
        skill_matches,
        [python, react, javascript],
        [job_python, job_react, job_javascript],
        _resume_structure(()),
    )

    assert result[0].status == RequirementMatchStatus.MATCHED

def test_skill_requirement_without_linked_match_is_unknown() -> None:
    python = _skill("resume-python", "Python")
    job_python = _skill("job-python", "Python")

    requirement = _skill_requirement(
        "req-docker",
        "Docker",
        canonical_name="Docker",
    )

    result = RequirementAligner().align(
        [requirement],
        [],
        [python],
        [job_python],
        _resume_structure(()),
    )

    assert result[0].status == RequirementMatchStatus.UNKNOWN
    assert result[0].evidence == requirement.evidence


def test_experience_requirement_without_resume_experience_is_unknown() -> None:
    requirement = JobRequirement(
        requirement_id="req-experience",
        text="3+ years of Python experience",
        requirement_type=JobRequirementType.REQUIRED,
        category=JobRequirementCategory.EXPERIENCE,
        evidence=[_job_evidence("3+ years of Python experience")],
        confidence=_confidence(),
    )

    result = RequirementAligner().align(
        [requirement],
        [],
        [],
        [],
        _resume_structure(()),
    )

    assert result[0].status == RequirementMatchStatus.UNKNOWN


def test_experience_requirement_with_relevant_resume_evidence_is_matched() -> None:
    block = _resume_block(
        "Software Engineer — 4 years of Python development experience.",
        ResumeSectionType.EXPERIENCE,
    )

    resume = _resume_structure(
        (
            ResumeSection(
                section_type=ResumeSectionType.EXPERIENCE,
                heading="Experience",
                blocks=(block,),
            ),
        )
    )

    requirement = JobRequirement(
        requirement_id="req-experience",
        text="3+ years of Python experience",
        requirement_type=JobRequirementType.REQUIRED,
        category=JobRequirementCategory.EXPERIENCE,
        evidence=[_job_evidence("3+ years of Python experience")],
        confidence=_confidence(),
    )

    result = RequirementAligner().align(
        [requirement],
        [],
        [],
        [],
        resume,
    )

    assert result[0].status in {
        RequirementMatchStatus.MATCHED,
        RequirementMatchStatus.PARTIAL,
    }
    assert any(
        evidence.source_type == EvidenceSourceType.RESUME
        for evidence in result[0].evidence
    )


def test_education_requirement_without_education_evidence_is_unknown() -> None:
    resume = _resume_structure(())

    requirement = JobRequirement(
        requirement_id="req-education",
        text="Bachelor's degree in Computer Science",
        requirement_type=JobRequirementType.REQUIRED,
        category=JobRequirementCategory.EDUCATION,
        evidence=[_job_evidence("Bachelor's degree in Computer Science")],
        confidence=_confidence(),
    )

    result = RequirementAligner().align(
        [requirement],
        [],
        [],
        [],
        resume,
    )

    assert result[0].status == RequirementMatchStatus.UNKNOWN


def test_certification_requirement_uses_certification_section() -> None:
    block = _resume_block(
        "AWS Certified Solutions Architect",
        ResumeSectionType.CERTIFICATIONS,
    )

    resume = _resume_structure(
        (
            ResumeSection(
                section_type=ResumeSectionType.CERTIFICATIONS,
                heading="Certifications",
                blocks=(block,),
            ),
        )
    )

    requirement = JobRequirement(
        requirement_id="req-certification",
        text="AWS certification",
        requirement_type=JobRequirementType.REQUIRED,
        category=JobRequirementCategory.CERTIFICATION,
        evidence=[_job_evidence("AWS certification")],
        confidence=_confidence(),
    )

    result = RequirementAligner().align(
        [requirement],
        [],
        [],
        [],
        resume,
    )

    assert result[0].status in {
        RequirementMatchStatus.MATCHED,
        RequirementMatchStatus.PARTIAL,
    }


def test_requirement_alignment_does_not_create_phase6_score_or_xai() -> None:
    requirement = _skill_requirement(
        "req-python",
        "Python",
        canonical_name="Python",
    )

    result = RequirementAligner().align(
        [requirement],
        [],
        [],
        [],
        _resume_structure(()),
    )

    alignment = result[0]

    assert not hasattr(alignment, "score")
    assert not hasattr(alignment, "xai")
    assert not hasattr(alignment, "ranking")


# ---------------------------------------------------------------------------
# Experience requirement concept coverage tests
# ---------------------------------------------------------------------------


def _experience_requirement(
    requirement_id: str,
    text: str,
) -> JobRequirement:
    return JobRequirement(
        requirement_id=requirement_id,
        text=text,
        requirement_type=JobRequirementType.REQUIRED,
        category=JobRequirementCategory.EXPERIENCE,
        evidence=[_job_evidence(text)],
        confidence=_confidence(),
    )


def _sections_with(
    section_type: ResumeSectionType,
    heading: str,
    *texts: str,
) -> ResumeSection:
    return ResumeSection(
        section_type=section_type,
        heading=heading,
        blocks=tuple(
            _resume_block(text, section_type)
            for text in texts
        ),
    )


def test_project_evidence_covers_all_concepts_is_matched() -> None:
    """
    A. Project evidence.

    The requirement mentions ETL/ELT, data pipelines, and data validation.
    A single PROJECTS block evidences all three concepts, so the requirement
    must be MATCHED and the rationale must attribute the evidence to the
    project section rather than to professional experience or skills.
    """
    resume = _resume_structure(
        (
            _sections_with(
                ResumeSectionType.PROJECTS,
                "Projects",
                (
                    "Built an ETL pipeline with data validation "
                    "for the analytics team."
                ),
            ),
        )
    )

    requirement = _experience_requirement(
        "req-data-eng",
        "Experience with ETL/ELT, data pipelines, and data validation.",
    )

    result = RequirementAligner().align(
        [requirement],
        [],
        [],
        [],
        resume,
    )

    alignment = result[0]

    assert alignment.status == RequirementMatchStatus.MATCHED
    assert "project_experience" in alignment.rationale
    assert any(
        evidence.source_type == EvidenceSourceType.RESUME
        for evidence in alignment.evidence
    )


def test_project_evidence_covers_some_concepts_is_partial() -> None:
    """
    B. Partial project evidence.

    The requirement mentions ETL, data pipelines, and data validation.
    The PROJECTS block only evidences ETL and data pipelines, so the
    requirement must be PARTIAL rather than MATCHED.
    """
    resume = _resume_structure(
        (
            _sections_with(
                ResumeSectionType.PROJECTS,
                "Projects",
                "Built an ETL pipeline for the analytics team.",
            ),
        )
    )

    requirement = _experience_requirement(
        "req-data-eng",
        "Experience with ETL/ELT, data pipelines, and data validation.",
    )

    result = RequirementAligner().align(
        [requirement],
        [],
        [],
        [],
        resume,
    )

    assert result[0].status == RequirementMatchStatus.PARTIAL


def test_skills_only_evidence_is_matched() -> None:
    """
    C. Skills-only evidence.

    Docker and Linux are declared only inside the SKILLS section. Concept
    coverage must still be complete, and the rationale must reflect that
    the evidence came from declared skills rather than experience or
    projects.
    """
    resume = _resume_structure(
        (
            _sections_with(
                ResumeSectionType.SKILLS,
                "Skills",
                "Docker, Linux",
            ),
        )
    )

    requirement = _experience_requirement(
        "req-platform",
        "Experience with Docker and Linux.",
    )

    result = RequirementAligner().align(
        [requirement],
        [],
        [],
        [],
        resume,
    )

    alignment = result[0]

    assert alignment.status == RequirementMatchStatus.MATCHED
    assert "declared_skill" in alignment.rationale


def test_mixed_evidence_across_sections_is_matched() -> None:
    """
    D. Mixed evidence.

    One concept is evidenced by PROJECTS, another by SKILLS. Coverage is
    complete but spans multiple section types, so the rationale must be the
    mixed-evidence variant.
    """
    resume = _resume_structure(
        (
            _sections_with(
                ResumeSectionType.PROJECTS,
                "Projects",
                "Built an ETL pipeline.",
            ),
            _sections_with(
                ResumeSectionType.SKILLS,
                "Skills",
                "Docker, Linux",
            ),
        )
    )

    requirement = _experience_requirement(
        "req-mixed",
        "Experience with ETL pipelines, Docker, and Linux.",
    )

    result = RequirementAligner().align(
        [requirement],
        [],
        [],
        [],
        resume,
    )

    alignment = result[0]

    assert alignment.status == RequirementMatchStatus.MATCHED
    assert "mixed_resume_evidence" in alignment.rationale


def test_experience_requirement_with_no_evidence_is_unknown() -> None:
    """
    E. No evidence.

    No resume section contains any of the required concepts. The status
    must remain UNKNOWN, matching the pre-existing unknown behavior.
    """
    resume = _resume_structure(
        (
            _sections_with(
                ResumeSectionType.EXPERIENCE,
                "Experience",
                "Front-end developer focused on accessibility.",
            ),
        )
    )

    requirement = _experience_requirement(
        "req-data-eng",
        "Experience with ETL/ELT, data pipelines, and data validation.",
    )

    result = RequirementAligner().align(
        [requirement],
        [],
        [],
        [],
        resume,
    )

    assert result[0].status == RequirementMatchStatus.UNKNOWN


def test_professional_experience_takes_precedence_in_rationale() -> None:
    """
    F. Professional experience takes precedence.

    Both EXPERIENCE and PROJECTS evidence the same concepts. Coverage is
    complete, but because EXPERIENCE is present, the rationale must
    attribute the evidence to professional experience rather than to
    projects or skills.
    """
    resume = _resume_structure(
        (
            _sections_with(
                ResumeSectionType.EXPERIENCE,
                "Experience",
                "Maintained an ETL pipeline with data validation.",
            ),
            _sections_with(
                ResumeSectionType.PROJECTS,
                "Projects",
                "Built an ETL pipeline.",
            ),
        )
    )

    requirement = _experience_requirement(
        "req-data-eng",
        "Experience with ETL/ELT, data pipelines, and data validation.",
    )

    result = RequirementAligner().align(
        [requirement],
        [],
        [],
        [],
        resume,
    )

    alignment = result[0]

    assert alignment.status == RequirementMatchStatus.MATCHED
    assert "professional_experience" in alignment.rationale