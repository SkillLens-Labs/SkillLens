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
