from backend.app.analysis.esco_mapper import ESCOMapper
from backend.app.analysis.resume_profile_builder import ResumeProfileBuilder
from backend.app.analysis.resume_structure import (
    ResumeSection,
    ResumeSectionType,
    StructuredResume,
)
from backend.app.analysis.skill_extractor import (
    SkillEvidenceType,
    SkillMention,
)
from backend.app.analysis.skill_normalizer import SkillNormalizer
from backend.app.domain.confidence import ConfidenceLevel
from backend.app.infrastructure.parsers.models import (
    DocumentBlock,
    DocumentBlockType,
    SourceLocation,
)


def _block(text: str, index: int = 0) -> DocumentBlock:
    return DocumentBlock(
        block_type=DocumentBlockType.PARAGRAPH,
        text=text,
        source=SourceLocation(
            page_number=1,
            block_index=index,
        ),
    )


def _mention(
    *,
    raw_text: str,
    section_type: ResumeSectionType,
    block: DocumentBlock,
    confidence: float = 0.95,
) -> SkillMention:
    start = block.text.lower().index(raw_text.lower())

    return SkillMention(
        raw_text=raw_text,
        section_type=section_type,
        evidence_type=SkillEvidenceType.EXPLICIT,
        block=block,
        start_offset=start,
        end_offset=start + len(raw_text),
        extractor="test_extractor",
        confidence=confidence,
    )


def _resume(*sections: ResumeSection) -> StructuredResume:
    return StructuredResume(
        document_id="doc-123",
        sections=sections,
    )


def test_builds_canonical_resume_profile():
    block = _block("Python, Docker", 0)

    resume = _resume(
        ResumeSection(
            section_type=ResumeSectionType.SKILLS,
            heading="Skills",
            blocks=(block,),
        )
    )

    mentions = (
        _mention(
            raw_text="Python",
            section_type=ResumeSectionType.SKILLS,
            block=block,
        ),
        _mention(
            raw_text="Docker",
            section_type=ResumeSectionType.SKILLS,
            block=block,
        ),
    )

    normalized = SkillNormalizer().normalize_many(mentions)
    mapped = ESCOMapper().map_many(normalized)

    profile = ResumeProfileBuilder().build(resume, normalized, mapped)

    assert profile.document_id == "doc-123"
    assert profile.profile_id.startswith("resume_")
    assert len(profile.skills) == 2
    assert profile.skills[0].canonical_name == "python"
    assert profile.skills[1].canonical_name == "docker"


def test_preserves_summary_without_inventing_other_resume_facts():
    block = _block("Data analyst with Python experience.", 0)

    resume = _resume(
        ResumeSection(
            section_type=ResumeSectionType.SUMMARY,
            heading="Summary",
            blocks=(block,),
        )
    )

    profile = ResumeProfileBuilder().build(resume, [], [])

    assert profile.candidate_summary == block.text
    assert profile.education == []
    assert profile.experience == []
    assert profile.projects == []
    assert profile.certifications == []
    assert profile.total_experience is None
    assert profile.seniority is None
    assert profile.domains == []


def test_creates_evidence_with_resume_provenance():
    block = _block("Python", 0)

    resume = _resume(
        ResumeSection(
            section_type=ResumeSectionType.SKILLS,
            heading="Skills",
            blocks=(block,),
        )
    )

    mention = _mention(
        raw_text="Python",
        section_type=ResumeSectionType.SKILLS,
        block=block,
    )

    normalized = SkillNormalizer().normalize(mention)
    mapped = ESCOMapper().map(normalized)

    profile = ResumeProfileBuilder().build(resume, [normalized], [mapped])

    evidence = profile.skills[0].evidence[0]

    assert evidence.source_document_id == "doc-123"
    assert evidence.source_type.value == "resume"
    assert evidence.section == "skills"
    assert evidence.text == "Python"
    assert evidence.start_offset == 0
    assert evidence.end_offset == 6
    assert evidence.evidence_type == "explicit"
    assert evidence.extractor == "test_extractor"


def test_creates_confidence_from_extraction_and_mapping():
    block = _block("Python", 0)

    resume = _resume(
        ResumeSection(
            section_type=ResumeSectionType.SKILLS,
            heading="Skills",
            blocks=(block,),
        )
    )

    mention = _mention(
        raw_text="Python",
        section_type=ResumeSectionType.SKILLS,
        block=block,
        confidence=0.95,
    )

    normalized = SkillNormalizer().normalize(mention)
    mapped = ESCOMapper().map(normalized)

    profile = ResumeProfileBuilder().build(resume, [normalized], [mapped])

    confidence = profile.skills[0].confidence

    assert confidence is not None
    assert confidence.score == 0.97
    assert confidence.level == ConfidenceLevel.HIGH
    assert confidence.components["extraction"] == 0.95
    assert confidence.components["esco_mapping"] == 0.99


def test_deduplicates_same_canonical_skill_and_merges_evidence():
    first = _block("Python", 0)
    second = _block("Python", 1)

    resume = _resume(
        ResumeSection(
            section_type=ResumeSectionType.SKILLS,
            heading="Skills",
            blocks=(first, second),
        )
    )

    mentions = (
        _mention(
            raw_text="Python",
            section_type=ResumeSectionType.SKILLS,
            block=first,
        ),
        _mention(
            raw_text="Python",
            section_type=ResumeSectionType.SKILLS,
            block=second,
        ),
    )

    normalized = SkillNormalizer().normalize_many(mentions)
    mapped = ESCOMapper().map_many(normalized)

    profile = ResumeProfileBuilder().build(resume, normalized, mapped)

    assert len(profile.skills) == 1
    assert len(profile.skills[0].evidence) == 2


def test_skill_categories_are_derived_deterministically():
    first = _block("Python", 0)
    second = _block("Docker", 1)

    resume = _resume(
        ResumeSection(
            section_type=ResumeSectionType.SKILLS,
            heading="Skills",
            blocks=(first, second),
        )
    )

    mentions = (
        _mention(
            raw_text="Python",
            section_type=ResumeSectionType.SKILLS,
            block=first,
        ),
        _mention(
            raw_text="Docker",
            section_type=ResumeSectionType.SKILLS,
            block=second,
        ),
    )

    normalized = SkillNormalizer().normalize_many(mentions)
    mapped = ESCOMapper().map_many(normalized)

    profile = ResumeProfileBuilder().build(resume, normalized, mapped)

    assert profile.skill_categories == ["cloud_devops", "programming"]


def test_unmapped_skill_does_not_receive_fabricated_esco_uri():
    block = _block("FastAPI", 0)

    resume = _resume(
        ResumeSection(
            section_type=ResumeSectionType.SKILLS,
            heading="Skills",
            blocks=(block,),
        )
    )

    mention = _mention(
        raw_text="FastAPI",
        section_type=ResumeSectionType.SKILLS,
        block=block,
    )

    normalized = SkillNormalizer().normalize(mention)
    mapped = ESCOMapper().map(normalized)

    profile = ResumeProfileBuilder().build(resume, [normalized], [mapped])

    skill = profile.skills[0]

    assert mapped.status.value == "unmapped"
    assert "esco_uri" not in skill.metadata
    assert skill.confidence is not None
    assert skill.confidence.level == ConfidenceLevel.MEDIUM


def test_rejects_mismatched_skill_and_mapping_lengths():
    resume = _resume()

    try:
        ResumeProfileBuilder().build(
            resume,
            [],
            [
                ESCOMapper().map(
                    SkillNormalizer().normalize(
                        _mention(
                            raw_text="Python",
                            section_type=ResumeSectionType.SKILLS,
                            block=_block("Python"),
                        )
                    )
                )
            ],
        )
    except ValueError as exc:
        assert "same number" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
