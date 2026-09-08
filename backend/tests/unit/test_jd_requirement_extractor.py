from backend.app.analysis.jd_requirement_extractor import JDRequirementExtractor
from backend.app.analysis.jd_structure import (
    JDSection,
    JDSectionType,
    StructuredJobDescription,
)
from backend.app.domain.confidence import ConfidenceLevel
from backend.app.domain.evidence import EvidenceSourceType
from backend.app.domain.matching import (
    JobRequirementCategory,
    JobRequirementType,
)
from backend.app.infrastructure.parsers.models import (
    DocumentBlock,
    DocumentBlockType,
    SourceLocation,
)


def _block(
    text: str,
    block_type: DocumentBlockType = DocumentBlockType.BULLET,
    block_index: int = 0,
) -> DocumentBlock:
    return DocumentBlock(
        text=text,
        block_type=block_type,
        source=SourceLocation(block_index=block_index),
    )


def _document(*sections: JDSection) -> StructuredJobDescription:
    return StructuredJobDescription(
        document_id="jd-test-001",
        sections=sections,
    )


def test_extracts_required_and_preferred_requirements() -> None:
    document = _document(
        JDSection(
            section_type=JDSectionType.REQUIRED_QUALIFICATIONS,
            heading="Requirements",
            blocks=(
                _block("Python"),
                _block("SQL"),
            ),
        ),
        JDSection(
            section_type=JDSectionType.PREFERRED_QUALIFICATIONS,
            heading="Preferred Qualifications",
            blocks=(
                _block("Docker"),
            ),
        ),
    )

    requirements = JDRequirementExtractor().extract(document)

    assert [item.text for item in requirements] == ["Python", "SQL", "Docker"]
    assert [item.requirement_type for item in requirements] == [
        JobRequirementType.REQUIRED,
        JobRequirementType.REQUIRED,
        JobRequirementType.PREFERRED,
    ]


def test_classifies_experience_requirement() -> None:
    document = _document(
        JDSection(
            section_type=JDSectionType.EXPERIENCE,
            heading="Experience",
            blocks=(
                _block("3+ years of experience in software development"),
            ),
        )
    )

    requirements = JDRequirementExtractor().extract(document)

    assert len(requirements) == 1
    assert requirements[0].category == JobRequirementCategory.EXPERIENCE
    assert requirements[0].requirement_type == JobRequirementType.REQUIRED


def test_classifies_education_requirement() -> None:
    document = _document(
        JDSection(
            section_type=JDSectionType.EDUCATION,
            heading="Education",
            blocks=(
                _block("Bachelor's degree in Computer Science"),
            ),
        )
    )

    requirements = JDRequirementExtractor().extract(document)

    assert len(requirements) == 1
    assert requirements[0].category == JobRequirementCategory.EDUCATION


def test_classifies_certification_requirement() -> None:
    document = _document(
        JDSection(
            section_type=JDSectionType.CERTIFICATIONS,
            heading="Certifications",
            blocks=(
                _block("AWS Certified Solutions Architect"),
            ),
        )
    )

    requirements = JDRequirementExtractor().extract(document)

    assert len(requirements) == 1
    assert requirements[0].category == JobRequirementCategory.CERTIFICATION


def test_preserves_job_description_evidence() -> None:
    document = _document(
        JDSection(
            section_type=JDSectionType.REQUIRED_QUALIFICATIONS,
            heading="Requirements",
            blocks=(
                _block("Python"),
            ),
        )
    )

    requirements = JDRequirementExtractor().extract(document)

    evidence = requirements[0].evidence[0]

    assert evidence.source_type == EvidenceSourceType.JOB_DESCRIPTION
    assert evidence.source_document_id == "jd-test-001"
    assert evidence.section == JDSectionType.REQUIRED_QUALIFICATIONS.value
    assert evidence.text == "Python"
    assert evidence.evidence_type == "job_requirement"
    assert evidence.extractor == "jd_requirement_extractor"


def test_requirement_has_high_confidence() -> None:
    document = _document(
        JDSection(
            section_type=JDSectionType.REQUIRED_QUALIFICATIONS,
            heading="Requirements",
            blocks=(
                _block("Python"),
            ),
        )
    )

    requirements = JDRequirementExtractor().extract(document)

    assert requirements[0].confidence is not None
    assert requirements[0].confidence.score == 0.95
    assert requirements[0].confidence.level == ConfidenceLevel.HIGH


def test_unknown_sections_are_not_promoted_to_requirements() -> None:
    document = _document(
        JDSection(
            section_type=JDSectionType.SUMMARY,
            heading="Summary",
            blocks=(
                _block("We build data products with Python."),
            ),
        ),
        JDSection(
            section_type=JDSectionType.UNKNOWN,
            heading="Company Culture",
            blocks=(
                _block("We value curiosity and ownership."),
            ),
        ),
    )

    requirements = JDRequirementExtractor().extract(document)

    assert requirements == []


def test_requirement_ids_are_deterministic() -> None:
    document = _document(
        JDSection(
            section_type=JDSectionType.REQUIRED_QUALIFICATIONS,
            heading="Requirements",
            blocks=(
                _block("Python"),
                _block("SQL"),
            ),
        )
    )

    extractor = JDRequirementExtractor()

    first = extractor.extract(document)
    second = extractor.extract(document)

    assert [item.requirement_id for item in first] == [
        item.requirement_id for item in second
    ]


def test_requirement_order_is_preserved() -> None:
    document = _document(
        JDSection(
            section_type=JDSectionType.REQUIRED_QUALIFICATIONS,
            heading="Requirements",
            blocks=(
                _block("Python"),
                _block("SQL"),
                _block("FastAPI"),
            ),
        )
    )

    requirements = JDRequirementExtractor().extract(document)

    assert [item.text for item in requirements] == [
        "Python",
        "SQL",
        "FastAPI",
    ]


def test_bullet_prefix_is_removed_without_changing_requirement_text() -> None:
    document = _document(
        JDSection(
            section_type=JDSectionType.REQUIRED_QUALIFICATIONS,
            heading="Requirements",
            blocks=(
                _block("• Python"),
                _block("- SQL"),
            ),
        )
    )

    requirements = JDRequirementExtractor().extract(document)

    assert [item.text for item in requirements] == ["Python", "SQL"]


def test_skill_requirement_defaults_to_skill_category() -> None:
    document = _document(
        JDSection(
            section_type=JDSectionType.SKILLS,
            heading="Technical Skills",
            blocks=(
                _block("Python"),
            ),
        )
    )

    requirements = JDRequirementExtractor().extract(document)

    assert len(requirements) == 1
    assert requirements[0].category == JobRequirementCategory.SKILL
    assert requirements[0].requirement_type == JobRequirementType.REQUIRED
