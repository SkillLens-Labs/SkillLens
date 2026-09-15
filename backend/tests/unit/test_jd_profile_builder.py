from __future__ import annotations

from backend.app.analysis.esco_mapper import ESCOMapper
from backend.app.analysis.jd_profile_builder import JDProfileBuilder
from backend.app.analysis.jd_requirement_extractor import JDRequirementExtractor
from backend.app.analysis.jd_skill_extractor import JDSkillExtractor
from backend.app.analysis.jd_skill_normalizer import JDSkillNormalizer
from backend.app.analysis.jd_structure import (
    JDSection,
    JDSectionType,
    StructuredJobDescription,
)
from backend.app.domain.analysis import AnalysisResult
from backend.app.domain.matching import (
    JobRequirement,
    JobRequirementCategory,
    JobRequirementType,
)
from backend.app.infrastructure.parsers.models import (
    DocumentBlock,
    DocumentBlockType,
    SourceLocation,
)


def block(
    text: str,
    block_type: DocumentBlockType = DocumentBlockType.PARAGRAPH,
    index: int = 0,
    metadata: dict[str, object] | None = None,
) -> DocumentBlock:
    return DocumentBlock(
        text=text,
        block_type=block_type,
        source=SourceLocation(block_index=index),
        metadata=metadata or {},
    )


def jd_document() -> StructuredJobDescription:
    return StructuredJobDescription(
        document_id="jd-001",
        sections=(
            JDSection(
                section_type=JDSectionType.HEADER,
                heading=None,
                blocks=(
                    block("Senior Data Engineer"),
                    block(
                        "Acme Technologies",
                        metadata={"company": "Acme Technologies"},
                    ),
                ),
            ),
            JDSection(
                section_type=JDSectionType.SUMMARY,
                heading="Summary",
                blocks=(
                    block(
                        "Build scalable data platforms and machine learning systems."
                    ),
                ),
            ),
            JDSection(
                section_type=JDSectionType.RESPONSIBILITIES,
                heading="Responsibilities",
                blocks=(
                    block("Design and maintain data pipelines."),
                    block("Develop analytical services."),
                ),
            ),
            JDSection(
                section_type=JDSectionType.REQUIRED_QUALIFICATIONS,
                heading="Required Qualifications",
                blocks=(
                    block("Python"),
                    block("5+ years of experience in data engineering"),
                    block("Bachelor's degree in Computer Science"),
                ),
            ),
            JDSection(
                section_type=JDSectionType.PREFERRED_QUALIFICATIONS,
                heading="Preferred Qualifications",
                blocks=(
                    block("ReactJS"),
                ),
            ),
            JDSection(
                section_type=JDSectionType.SKILLS,
                heading="Skills",
                blocks=(
                    block("Python, SQL, Docker"),
                ),
            ),
        ),
    )


def build_inputs():
    document = jd_document()

    requirements = JDRequirementExtractor().extract(document)

    mentions = JDSkillExtractor().extract(document).mentions

    normalized = JDSkillNormalizer().normalize_many(mentions)

    mapped = ESCOMapper().map_many(normalized)

    return document, requirements, normalized, mapped


def test_builds_canonical_job_profile() -> None:
    document, requirements, normalized, mapped = build_inputs()

    profile = JDProfileBuilder().build(
        document,
        requirements,
        normalized,
        mapped,
    )

    assert profile.profile_id.startswith("job_")
    assert profile.document_id == "jd-001"
    assert profile.job_title == "Senior Data Engineer"
    assert profile.company == "Acme Technologies"


def test_build_with_skills_exposes_canonical_skills() -> None:
    document, requirements, normalized, mapped = build_inputs()

    result = JDProfileBuilder().build_with_skills(
        document,
        requirements,
        normalized,
        mapped,
    )

    assert result.profile.required_skills
    assert len(result.skills) >= 1
    assert all(skill.skill_id.startswith("job-skill-") for skill in result.skills)
    assert all(skill.canonical_name for skill in result.skills)
    assert result.requirements == tuple(requirements)


def test_build_with_skills_returns_same_profile_contract() -> None:
    document, requirements, normalized, mapped = build_inputs()

    builder = JDProfileBuilder()

    profile = builder.build(
        document,
        requirements,
        normalized,
        mapped,
    )
    result = builder.build_with_skills(
        document,
        requirements,
        normalized,
        mapped,
    )

    assert result.profile == profile
    assert result.requirements == tuple(requirements)
    assert len(result.skills) >= 1
    assert result.skills[0].canonical_name == normalized[0].canonical_name


def test_extracts_summary_and_responsibilities() -> None:
    document, requirements, normalized, mapped = build_inputs()

    profile = JDProfileBuilder().build(
        document,
        requirements,
        normalized,
        mapped,
    )

    assert profile.summary == (
        "Build scalable data platforms and machine learning systems."
    )
    assert profile.responsibilities == [
        "Design and maintain data pipelines.",
        "Develop analytical services.",
    ]


def test_builds_required_and_preferred_skills() -> None:
    document, requirements, normalized, mapped = build_inputs()

    profile = JDProfileBuilder().build(
        document,
        requirements,
        normalized,
        mapped,
    )

    assert "python" in profile.required_skills
    assert "sql" in profile.required_skills
    assert "docker" in profile.required_skills
    assert "react" in profile.preferred_skills


def test_builds_experience_requirements() -> None:
    document, requirements, normalized, mapped = build_inputs()

    profile = JDProfileBuilder().build(
        document,
        requirements,
        normalized,
        mapped,
    )

    assert profile.experience_requirements is not None
    assert profile.experience_requirements.minimum_years == 5.0
    assert "5+ years" in profile.experience_requirements.description


def test_builds_education_requirements() -> None:
    document, requirements, normalized, mapped = build_inputs()

    profile = JDProfileBuilder().build(
        document,
        requirements,
        normalized,
        mapped,
    )

    assert profile.education_requirements is not None
    assert "bachelor" in profile.education_requirements.degrees
    assert "Computer Science" in profile.education_requirements.description


def test_builds_skill_metadata_and_esco_information() -> None:
    document, requirements, normalized, mapped = build_inputs()
    profile = JDProfileBuilder().build(
        document,
        requirements,
        normalized,
        mapped,
    )

    assert "python" in profile.required_skills
    assert profile.metadata["esco_version"] == "1.2.1"
    assert profile.metadata["skill_count"] >= 1
    assert any(
        requirement["text"] == "Python"
        and requirement["requirement_type"] == "required"
        for requirement in profile.metadata["requirements"]
    )


def test_deduplicates_canonical_skills() -> None:
    document, requirements, normalized, mapped = build_inputs()
    profile = JDProfileBuilder().build(
        document,
        requirements,
        normalized,
        mapped,
    )

    assert profile.required_skills.count("python") == 1


def test_builder_metadata_is_canonical_and_deterministic() -> None:
    document, requirements, normalized, mapped = build_inputs()

    builder = JDProfileBuilder()

    first = builder.build(
        document,
        requirements,
        normalized,
        mapped,
    )
    second = builder.build(
        document,
        requirements,
        normalized,
        mapped,
    )

    assert first.profile_id == second.profile_id
    assert first.metadata["builder"] == "JDProfileBuilder"
    assert first.metadata["builder_version"] == "phase5-v1"
    assert first.metadata["esco_version"] == "1.2.1"
    assert first.metadata["skill_count"] == len(set(
        first.required_skills
        + first.preferred_skills
        + first.technical_skills
    ))
    assert first.metadata["requirement_count"] == len(requirements)


def test_rejects_misaligned_normalized_and_esco_results() -> None:
    document, requirements, normalized, mapped = build_inputs()

    try:
        JDProfileBuilder().build(
            document,
            requirements,
            normalized,
            mapped[:-1],
        )
    except ValueError as exc:
        assert "same number" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError for misaligned skill and ESCO inputs"
        )


def test_missing_requirements_do_not_create_fake_alignment() -> None:
    document = StructuredJobDescription(
        document_id="jd-empty",
        sections=(
            JDSection(
                section_type=JDSectionType.SUMMARY,
                heading="Summary",
                blocks=(block("Build useful software."),),
            ),
        ),
    )

    profile = JDProfileBuilder().build(
        document,
        [],
        [],
        [],
    )

    assert profile.required_skills == []
    assert profile.preferred_skills == []
    assert profile.experience_requirements is None
    assert profile.education_requirements is None


def test_job_profile_contains_no_phase6_analysis_fields() -> None:
    document, requirements, normalized, mapped = build_inputs()

    profile = JDProfileBuilder().build(
        document,
        requirements,
        normalized,
        mapped,
    )

    assert not hasattr(profile, "score")
    assert not hasattr(profile, "scoring")
    assert not hasattr(profile, "xai")
    assert not hasattr(profile, "match_score")


def test_analysis_result_keeps_phase6_slots_empty() -> None:
    document, requirements, normalized, mapped = build_inputs()

    profile = JDProfileBuilder().build(
        document,
        requirements,
        normalized,
        mapped,
    )

    result = AnalysisResult(
        analysis_id="analysis-001",
        analysis_mode="resume_jd",
        status="completed",
        input={
            "resume_document_id": "resume-001",
            "job_description_document_id": document.document_id,
        },
        resume_profile={
            "profile_id": "resume-001",
            "document_id": "resume-001",
        },
        job_profile=profile,
    )

    assert result.scoring is None
    assert result.xai is None


# ---------------------------------------------------------------------------
# Regression tests for company / experience-range / education-field fixes
# ---------------------------------------------------------------------------


def _empty_document() -> StructuredJobDescription:
    return StructuredJobDescription(
        document_id="jd-regression",
        sections=(),
    )


def test_extracts_company_from_header_text() -> None:
    document = StructuredJobDescription(
        document_id="jd-company",
        sections=(
            JDSection(
                section_type=JDSectionType.HEADER,
                heading=None,
                blocks=(
                    block("Data Engineer"),
                    block("Company: NovaTech Solutions"),
                ),
            ),
        ),
    )

    profile = JDProfileBuilder().build(
        document,
        [],
        [],
        [],
    )

    assert profile.company == "NovaTech Solutions"


def test_extracts_experience_range_with_minimum_and_maximum() -> None:
    requirements = [
        JobRequirement(
            requirement_id="req-exp",
            requirement_type=JobRequirementType.REQUIRED,
            category=JobRequirementCategory.EXPERIENCE,
            canonical_name="experience",
            text="Experience: 0–2 years",
        )
    ]

    profile = JDProfileBuilder().build(
        _empty_document(),
        requirements,
        [],
        [],
    )

    assert profile.experience_requirements is not None
    assert profile.experience_requirements.minimum_years == 0.0
    assert profile.experience_requirements.maximum_years == 2.0


def test_extracts_education_fields_of_study() -> None:
    requirements = [
        JobRequirement(
            requirement_id="req-edu",
            requirement_type=JobRequirementType.REQUIRED,
            category=JobRequirementCategory.EDUCATION,
            canonical_name="education",
            text=(
                "Bachelor's degree in Computer Science, Engineering, "
                "or related field."
            ),
        )
    ]

    profile = JDProfileBuilder().build(
        _empty_document(),
        requirements,
        [],
        [],
    )

    assert profile.education_requirements is not None
    assert profile.education_requirements.degrees == ["bachelor"]
    assert profile.education_requirements.fields_of_study == [
        "Computer Science",
        "Engineering",
    ]


# ---------------------------------------------------------------------------
# Additional coverage for range-first and multi-degree parsing
# ---------------------------------------------------------------------------


def test_experience_range_takes_priority_over_plus_pattern() -> None:
    """
    When both a range ("0–2 years") and an unrelated "+" value appear in
    the combined experience text, the range must win and populate both
    minimum_years and maximum_years. The plus pattern is only a fallback.
    """
    requirements = [
        JobRequirement(
            requirement_id="req-exp-range-only",
            requirement_type=JobRequirementType.REQUIRED,
            category=JobRequirementCategory.EXPERIENCE,
            canonical_name="experience",
            text="0–2 years of experience",
        )
    ]

    profile = JDProfileBuilder().build(
        _empty_document(),
        requirements,
        [],
        [],
    )

    assert profile.experience_requirements is not None
    assert profile.experience_requirements.minimum_years == 0.0
    assert profile.experience_requirements.maximum_years == 2.0


def test_education_fields_of_study_ignores_related_field_phrase() -> None:
    """
    "or related field" is a catch-all phrase, not a literal field of study.
    It must be stripped before splitting, and only the explicit fields
    must be preserved in original casing.
    """
    requirements = [
        JobRequirement(
            requirement_id="req-edu-related",
            requirement_type=JobRequirementType.REQUIRED,
            category=JobRequirementCategory.EDUCATION,
            canonical_name="education",
            text=(
                "Bachelor's degree in Computer Science, "
                "Engineering, or related field."
            ),
        )
    ]

    profile = JDProfileBuilder().build(
        _empty_document(),
        requirements,
        [],
        [],
    )

    assert profile.education_requirements is not None
    assert profile.education_requirements.degrees == ["bachelor"]
    assert profile.education_requirements.fields_of_study == [
        "Computer Science",
        "Engineering",
    ]

def test_job_title_prefers_header_heading_over_metadata_blocks() -> None:
    document = StructuredJobDescription(
        document_id="jd-header-title",
        sections=(
            JDSection(
                section_type=JDSectionType.HEADER,
                heading="Data Engineer",
                blocks=(
                    block("Company: NovaTech Solutions"),
                    block("Location: Remote — India"),
                    block("Experience: 0–2 years"),
                ),
            ),
        ),
    )

    profile = JDProfileBuilder().build(
        document,
        requirements=(),
        normalized_skills=[],
        esco_results=[],
    )

    assert profile.job_title == "Data Engineer"
    assert profile.company == "NovaTech Solutions"