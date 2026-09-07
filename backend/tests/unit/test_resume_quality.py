from backend.app.analysis.resume_quality import ResumeQualityAnalyzer
from backend.app.analysis.resume_structure import (
    ResumeSectionType,
    ResumeStructureInterpreter,
)
from backend.app.domain.resume import ResumeProfile
from backend.app.infrastructure.parsers.models import (
    DocumentBlock,
    DocumentBlockType,
    DocumentType,
    ParsedDocument,
    SourceLocation,
)


def _block(text, block_type, index):
    return DocumentBlock(
        text=text,
        block_type=block_type,
        source=SourceLocation(page_number=1, block_index=index),
    )


def _profile(document_id):
    return ResumeProfile(
        profile_id="profile-1",
        document_id=document_id,
    )


def test_quality_analyzer_returns_bounded_result():
    document = ParsedDocument(
        document_id="quality-001",
        document_type=DocumentType.PDF,
        blocks=[
            _block("Candidate Name", DocumentBlockType.PARAGRAPH, 0),
            _block("Professional Summary", DocumentBlockType.HEADING, 1),
            _block(
                "Computer science student with practical experience.",
                DocumentBlockType.PARAGRAPH,
                2,
            ),
            _block("Technical Skills", DocumentBlockType.HEADING, 3),
            _block("Python, SQL, Docker", DocumentBlockType.PARAGRAPH, 4),
        ],
    )

    structured = ResumeStructureInterpreter().interpret(document)
    result = ResumeQualityAnalyzer().analyze(
        structured,
        _profile(document.document_id),
    )

    assert 0.0 <= result.overall_score <= 100.0
    assert len(result.dimension_scores) == 8
    assert result.confidence.score > 0.0


def test_quality_analyzer_preserves_source_evidence():
    document = ParsedDocument(
        document_id="quality-002",
        document_type=DocumentType.PDF,
        blocks=[
            _block("Candidate Name", DocumentBlockType.PARAGRAPH, 0),
            _block("Technical Skills", DocumentBlockType.HEADING, 1),
            _block("Python and SQL", DocumentBlockType.PARAGRAPH, 2),
        ],
    )

    structured = ResumeStructureInterpreter().interpret(document)
    result = ResumeQualityAnalyzer().analyze(
        structured,
        _profile(document.document_id),
    )

    findings = [
        finding
        for finding in result.findings
        if finding.category == "completeness"
    ]

    assert findings
    assert any(
        evidence.source_document_id == document.document_id
        for finding in findings
        for evidence in finding.evidence
    )


def test_quality_does_not_penalize_unstructured_phase3_fields_as_absent():
    document = ParsedDocument(
        document_id="quality-003",
        document_type=DocumentType.PDF,
        blocks=[
            _block("Candidate Name", DocumentBlockType.PARAGRAPH, 0),
            _block("Education", DocumentBlockType.HEADING, 1),
            _block(
                "B.E. Computer Science",
                DocumentBlockType.PARAGRAPH,
                2,
            ),
        ],
    )

    structured = ResumeStructureInterpreter().interpret(document)
    result = ResumeQualityAnalyzer().analyze(
        structured,
        _profile(document.document_id),
    )

    education_findings = [
        finding
        for finding in result.findings
        if finding.category == "education"
    ]

    assert any(
        finding.severity == "info"
        and "not yet available" in finding.title.lower()
        for finding in education_findings
    )


def test_quality_detects_repeated_skill_mentions_from_preserved_evidence():
    from backend.app.domain.evidence import Evidence, EvidenceSourceType
    from backend.app.domain.resume import Skill

    document = ParsedDocument(
        document_id="quality-004",
        document_type=DocumentType.PDF,
        blocks=[
            _block("Candidate Name", DocumentBlockType.PARAGRAPH, 0),
            _block("Technical Skills", DocumentBlockType.HEADING, 1),
            _block("Python, SQL", DocumentBlockType.PARAGRAPH, 2),
        ],
    )

    structured = ResumeStructureInterpreter().interpret(document)

    evidence_one = Evidence(
        evidence_id="evidence-1",
        source_type=EvidenceSourceType.RESUME,
        source_document_id=document.document_id,
        section="skills",
        text="Python",
        start_offset=0,
        end_offset=6,
        evidence_type="skill_extraction",
        confidence=0.95,
    )

    evidence_two = Evidence(
        evidence_id="evidence-2",
        source_type=EvidenceSourceType.RESUME,
        source_document_id=document.document_id,
        section="experience",
        text="Python",
        start_offset=0,
        end_offset=6,
        evidence_type="skill_extraction",
        confidence=0.90,
    )

    profile = ResumeProfile(
        profile_id="profile-4",
        document_id=document.document_id,
        skills=[
            Skill(
                skill_id="skill-python",
                canonical_name="Python",
                display_name="Python",
                evidence=[evidence_one, evidence_two],
            )
        ],
    )

    result = ResumeQualityAnalyzer().analyze(structured, profile)

    findings = [
        finding
        for finding in result.findings
        if finding.title == "Repeated skills detected"
    ]

    assert findings
    assert len(findings[0].evidence) == 2
    assert all(
        evidence.source_document_id == document.document_id
        for evidence in findings[0].evidence
    )


def test_quality_detects_missing_experience_dates():
    document = ParsedDocument(
        document_id="quality-005",
        document_type=DocumentType.PDF,
        blocks=[
            _block("Candidate Name", DocumentBlockType.PARAGRAPH, 0),
            _block("Experience", DocumentBlockType.HEADING, 1),
            _block(
                "Software Engineer at Example Corp",
                DocumentBlockType.PARAGRAPH,
                2,
            ),
            _block(
                "Developed backend services and improved application reliability.",
                DocumentBlockType.BULLET,
                3,
            ),
        ],
    )

    structured = ResumeStructureInterpreter().interpret(document)

    result = ResumeQualityAnalyzer().analyze(
        structured,
        _profile(document.document_id),
    )

    findings = [
        finding
        for finding in result.findings
        if finding.title == "Experience dates not clearly detected"
    ]

    assert findings
    assert findings[0].category == "experience"
    assert findings[0].evidence


def test_quality_detects_missing_education_qualification():
    document = ParsedDocument(
        document_id="quality-006",
        document_type=DocumentType.PDF,
        blocks=[
            _block("Candidate Name", DocumentBlockType.PARAGRAPH, 0),
            _block("Education", DocumentBlockType.HEADING, 1),
            _block(
                "Example University",
                DocumentBlockType.PARAGRAPH,
                2,
            ),
            _block(
                "2022 - 2026",
                DocumentBlockType.PARAGRAPH,
                3,
            ),
        ],
    )

    structured = ResumeStructureInterpreter().interpret(document)

    result = ResumeQualityAnalyzer().analyze(
        structured,
        _profile(document.document_id),
    )

    findings = [
        finding
        for finding in result.findings
        if finding.title == "Education qualification not clearly detected"
    ]

    assert findings
    assert findings[0].category == "education"
    assert findings[0].evidence


def test_quality_detects_limited_project_description_and_technology():
    document = ParsedDocument(
        document_id="quality-007",
        document_type=DocumentType.PDF,
        blocks=[
            _block("Candidate Name", DocumentBlockType.PARAGRAPH, 0),
            _block("Projects", DocumentBlockType.HEADING, 1),
            _block(
                "Portfolio website",
                DocumentBlockType.PARAGRAPH,
                2,
            ),
        ],
    )

    structured = ResumeStructureInterpreter().interpret(document)

    result = ResumeQualityAnalyzer().analyze(
        structured,
        _profile(document.document_id),
    )

    titles = {finding.title for finding in result.findings}

    assert "Project descriptions are limited" in titles
    assert "Project technologies not clearly detected" in titles


def test_quality_detects_equivalent_section_names():
    document = ParsedDocument(
        document_id="quality-008",
        document_type=DocumentType.PDF,
        blocks=[
            _block("Candidate Name", DocumentBlockType.PARAGRAPH, 0),
            _block("Skills", DocumentBlockType.HEADING, 1),
            _block("Python", DocumentBlockType.PARAGRAPH, 2),
            _block("Technical Skills", DocumentBlockType.HEADING, 3),
            _block("SQL", DocumentBlockType.PARAGRAPH, 4),
        ],
    )

    structured = ResumeStructureInterpreter().interpret(document)

    result = ResumeQualityAnalyzer().analyze(
        structured,
        _profile(document.document_id),
    )

    findings = [
        finding
        for finding in result.findings
        if finding.title == "Multiple equivalent section names detected"
    ]

    assert findings
    assert findings[0].category == "consistency"
    assert result.dimension_scores[-1].score < 95.0
