from backend.app.analysis.ats_intelligence import ATSIntelligenceAnalyzer
from backend.app.analysis.resume_profile_builder import ResumeProfileBuilder
from backend.app.analysis.skill_extractor import SkillExtractor
from backend.app.analysis.skill_normalizer import SkillNormalizer
from backend.app.analysis.esco_mapper import ESCOMapper
from backend.app.analysis.resume_structure import ResumeStructureInterpreter
from backend.app.domain.resume import Skill
from backend.app.infrastructure.parsers.models import (
    DocumentBlock,
    DocumentBlockType,
    ParsedDocument,
    SourceLocation,
)
from backend.app.domain.ats_intelligence import ATSIntelligenceDimension


def block(text, block_type=DocumentBlockType.PARAGRAPH, index=0, section=None):
    return DocumentBlock(
        text=text,
        block_type=block_type,
        source=SourceLocation(block_index=index),
        section=section,
    )


def build_resume(blocks):
    document = ParsedDocument(
        document_id="ats-test-document",
        document_type="pdf",
        blocks=blocks,
        metadata={},
    )
    structured = ResumeStructureInterpreter().interpret(document)
    extracted = SkillExtractor().extract(structured)
    normalized = SkillNormalizer().normalize_many(extracted.mentions)
    mapped = ESCOMapper().map_many(normalized)
    profile = ResumeProfileBuilder().build(structured, normalized, mapped)
    return document, structured, profile


def test_ats_result_has_bounded_score_and_all_dimensions():
    blocks = [
        block("John Doe john@example.com +91 9876543210", DocumentBlockType.HEADING, 0),
        block("Summary", DocumentBlockType.HEADING, 1),
        block("Software engineer with Python and SQL experience.", index=2),
        block("Experience", DocumentBlockType.HEADING, 3),
        block("Software Engineer | ABC | 2024 - 2026", index=4),
        block("Built backend services and automated data processing workflows.", index=5),
        block("Skills", DocumentBlockType.HEADING, 6),
        block("Python, SQL, FastAPI", index=7),
        block("Education", DocumentBlockType.HEADING, 8),
        block("B.E. Computer Science 2021 - 2025", index=9),
    ]

    document, structured, profile = build_resume(blocks)
    result = ATSIntelligenceAnalyzer().analyze(document, structured, profile)

    assert 0 <= result.overall_score <= 100
    assert {
        item.dimension
        for item in result.dimension_scores
    } == set(ATSIntelligenceDimension)


def test_ats_analysis_is_deterministic():
    blocks = [
        block("John Doe john@example.com", DocumentBlockType.HEADING, 0),
        block("Skills", DocumentBlockType.HEADING, 1),
        block("Python SQL", index=2),
    ]

    document, structured, profile = build_resume(blocks)
    analyzer = ATSIntelligenceAnalyzer()

    first = analyzer.analyze(document, structured, profile).model_dump()
    second = analyzer.analyze(document, structured, profile).model_dump()

    assert first == second


def test_unknown_section_reduces_section_detectability():
    blocks = [
        block("John Doe", DocumentBlockType.HEADING, 0),
        block("Professional Summary", DocumentBlockType.HEADING, 1),
        block("Developer", index=2),
        block("My Journey", DocumentBlockType.HEADING, 3),
        block("Interesting professional work history.", index=4),
    ]

    document, structured, profile = build_resume(blocks)
    result = ATSIntelligenceAnalyzer().analyze(document, structured, profile)

    dimension = next(
        item
        for item in result.dimension_scores
        if item.dimension == ATSIntelligenceDimension.SECTION_DETECTABILITY
    )

    assert dimension.score < 100
    assert any("Unrecognized section" in finding.title for finding in result.findings)


def test_contact_detectability_uses_header_text_without_fabricating_fields():
    blocks = [
        block(
            "Jane Doe jane@example.com +91 9876543210 linkedin.com/in/janedoe",
            DocumentBlockType.PARAGRAPH,
            0,
        ),
        block("Skills", DocumentBlockType.HEADING, 1),
        block("Python SQL", index=2),
    ]

    document, structured, profile = build_resume(blocks)
    result = ATSIntelligenceAnalyzer().analyze(document, structured, profile)

    dimension = next(
        item
        for item in result.dimension_scores
        if item.dimension == ATSIntelligenceDimension.CONTACT_DETECTABILITY
    )

    assert dimension.score >= 75


def test_table_layout_produces_formatting_risk_signal():
    blocks = [
        block("John Doe", DocumentBlockType.HEADING, 0),
        DocumentBlock(
            text="Python",
            block_type=DocumentBlockType.TABLE_CELL,
            source=SourceLocation(block_index=1, table_index=0, row_index=0, column_index=0),
        ),
        DocumentBlock(
            text="SQL",
            block_type=DocumentBlockType.TABLE_CELL,
            source=SourceLocation(block_index=2, table_index=0, row_index=0, column_index=1),
        ),
    ]

    document, structured, profile = build_resume(blocks)
    result = ATSIntelligenceAnalyzer().analyze(document, structured, profile)

    assert any(
        finding.category == "formatting_risk"
        and "Table-based layout" in finding.title
        for finding in result.findings
    )


def test_duplicate_content_produces_redundancy_signal():
    repeated = "Built scalable backend services using Python and FastAPI for production workflows."
    blocks = [
        block("John Doe", DocumentBlockType.HEADING, 0),
        block("Experience", DocumentBlockType.HEADING, 1),
        block(repeated, index=2),
        block(repeated, index=3),
    ]

    document, structured, profile = build_resume(blocks)
    result = ATSIntelligenceAnalyzer().analyze(document, structured, profile)

    assert any(
        finding.category == "content_redundancy"
        for finding in result.findings
    )


def test_weak_extraction_generates_warning_and_finding():
    blocks = [
        block("John Doe", DocumentBlockType.HEADING, 0),
        block("�� corrupted text", index=1),
    ]

    document, structured, profile = build_resume(blocks)
    result = ATSIntelligenceAnalyzer().analyze(document, structured, profile)

    assert result.warnings
    assert any(
        finding.category == "text_extraction"
        for finding in result.findings
    )


def test_normal_text_does_not_trigger_extraction_corruption_finding():
    blocks = [
        block("John Doe", DocumentBlockType.HEADING, 0),
        block("Software engineer with Python and SQL experience.", index=1),
    ]
    document, structured, profile = build_resume(blocks)
    result = ATSIntelligenceAnalyzer().analyze(document, structured, profile)

    assert not any(
        finding.title == "Suspicious extraction characters detected"
        for finding in result.findings
    )


def test_no_skills_produces_skill_detectability_finding():
    blocks = [
        block("John Doe", DocumentBlockType.HEADING, 0),
        block("Experience", DocumentBlockType.HEADING, 1),
        block("Worked at a company.", index=2),
    ]

    document, structured, profile = build_resume(blocks)
    result = ATSIntelligenceAnalyzer().analyze(document, structured, profile)

    assert any(
        finding.category == "skill_detectability"
        for finding in result.findings
    )
