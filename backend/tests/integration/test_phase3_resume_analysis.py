from backend.app.analysis.esco_mapper import ESCOMapStatus, ESCOMapper
from backend.app.analysis.resume_profile_builder import ResumeProfileBuilder
from backend.app.analysis.resume_structure import (
    ResumeSectionType,
    ResumeStructureInterpreter,
)
from backend.app.analysis.skill_extractor import SkillEvidenceType, SkillExtractor
from backend.app.analysis.skill_normalizer import SkillNormalizer
from backend.app.infrastructure.parsers.models import (
    DocumentBlock,
    DocumentBlockType,
    DocumentType,
    ParsedDocument,
    SourceLocation,
)


def _block(text: str, block_type: DocumentBlockType, index: int) -> DocumentBlock:
    return DocumentBlock(
        text=text,
        block_type=block_type,
        source=SourceLocation(page_number=1, block_index=index),
    )


def test_phase3_resume_analysis_pipeline() -> None:
    document = ParsedDocument(
        document_id="integration-resume-001",
        document_type=DocumentType.PDF,
        blocks=[
            _block("Raghuvir Anturkar", DocumentBlockType.PARAGRAPH, 0),
            _block("Professional Summary", DocumentBlockType.HEADING, 1),
            _block(
                "Computer science student with experience in Python and data analysis.",
                DocumentBlockType.PARAGRAPH,
                2,
            ),
            _block("Technical Skills", DocumentBlockType.HEADING, 3),
            _block(
                "Python, React, Docker, FastAPI",
                DocumentBlockType.PARAGRAPH,
                4,
            ),
        ],
    )

    structured_resume = ResumeStructureInterpreter().interpret(document)

    assert structured_resume.document_id == document.document_id
    assert [
        section.section_type
        for section in structured_resume.sections
    ] == [
        ResumeSectionType.HEADER,
        ResumeSectionType.SUMMARY,
        ResumeSectionType.SKILLS,
    ]

    extraction_result = SkillExtractor().extract(structured_resume)

    assert extraction_result.document_id == document.document_id
    assert [mention.raw_text for mention in extraction_result.mentions] == [
        "Python",
        "data analysis",
        "Python",
        "React",
        "Docker",
        "FastAPI",
    ]
    assert extraction_result.mentions[0].evidence_type == SkillEvidenceType.CONTEXTUAL
    assert extraction_result.mentions[2].evidence_type == SkillEvidenceType.EXPLICIT

    normalized_skills = SkillNormalizer().normalize_many(
        extraction_result.mentions
    )

    assert [skill.canonical_name for skill in normalized_skills] == [
        "python",
        "data analysis",
        "python",
        "react",
        "docker",
        "fastapi",
    ]

    esco_results = ESCOMapper().map_many(normalized_skills)

    assert [result.status for result in esco_results] == [
        ESCOMapStatus.MAPPED,
        ESCOMapStatus.MAPPED,
        ESCOMapStatus.MAPPED,
        ESCOMapStatus.MAPPED,
        ESCOMapStatus.MAPPED,
        ESCOMapStatus.UNMAPPED,
    ]

    profile = ResumeProfileBuilder().build(
        structured_resume,
        normalized_skills,
        esco_results,
    )

    assert profile.profile_id.startswith("resume_")
    assert profile.document_id == document.document_id
    assert profile.candidate_summary == (
        "Computer science student with experience in Python and data analysis."
    )

    assert [skill.canonical_name for skill in profile.skills] == [
        "python",
        "data analysis",
        "react",
        "docker",
        "fastapi",
    ]

    python_skill = next(
        skill for skill in profile.skills if skill.canonical_name == "python"
    )

    assert len(python_skill.evidence) == 2
    assert python_skill.confidence is not None
    assert python_skill.confidence.score > 0.0

    assert profile.skill_categories == [
        "cloud_devops",
        "data",
        "programming",
        "web",
    ]
    assert profile.metadata["builder_version"] == "phase3-v1"
    assert profile.metadata["esco_version"] == "1.2.1"
    assert profile.metadata["skill_count"] == 5
