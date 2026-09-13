from backend.app.analysis.resume_language_quality import (
    ResumeLanguageQualityAnalyzer,
)
from backend.app.analysis.resume_structure import StructuredResume
from backend.app.domain.language_quality import (
    LanguageIssueSeverity,
    LanguageIssueType,
)
from backend.app.infrastructure.parsers.models import (
    DocumentBlock,
    DocumentBlockType,
    DocumentType,
    ParsedDocument,
    SourceLocation,
)


def make_document(text: str) -> ParsedDocument:
    return ParsedDocument(
        document_id="language-quality-test",
        document_type=DocumentType.DOCX,
        blocks=[
            DocumentBlock(
                text=text,
                block_type=DocumentBlockType.PARAGRAPH,
                source=SourceLocation(
                    paragraph_index=0,
                    block_index=0,
                ),
            )
        ],
        metadata={},
    )


def make_structure() -> StructuredResume:
    return StructuredResume(
        document_id="language-quality-test",
        sections=[],
    )


def analyze(text: str):
    analyzer = ResumeLanguageQualityAnalyzer()
    return analyzer.analyze(
        parsed_document=make_document(text),
        structured_resume=make_structure(),
    )


def test_clean_resume_produces_no_language_findings():
    result = analyze(
        """
        Software Engineer

        Developed Python applications and REST APIs.
        Built data processing workflows and automated testing.
        """
    )

    assert result.issues == []
    assert result.overall_score == 100.0
    assert result.authorship_heuristic.disclaimer == (
        "This is a heuristic writing-style estimate, not proof of AI authorship."
    )


def test_common_spelling_error_is_detected():
    result = analyze(
        "Experiance building Python applications."
    )

    spelling = [
        issue
        for issue in result.issues
        if issue.issue_type == LanguageIssueType.SPELLING
    ]

    assert len(spelling) == 1
    assert spelling[0].original_text == "Experiance"
    assert spelling[0].suggested_text == "experience"
    assert spelling[0].severity == LanguageIssueSeverity.MEDIUM


def test_repeated_word_is_detected():
    result = analyze(
        "Built built a resume analysis application."
    )

    grammar = [
        issue
        for issue in result.issues
        if issue.issue_type == LanguageIssueType.GRAMMAR
    ]

    assert len(grammar) == 1
    assert grammar[0].original_text == "Built built"
    assert grammar[0].suggested_text == "Built"


def test_generic_resume_wording_is_detected():
    result = analyze(
        "I am a quick learner and a team player."
    )

    wording = [
        issue
        for issue in result.issues
        if issue.issue_type == LanguageIssueType.WORDING
    ]

    assert len(wording) == 2
    assert {issue.original_text for issue in wording} == {
        "quick learner",
        "team player",
    }


def test_technical_terminology_signal_is_detected():
    result = analyze(
        "Developed applications using node js, reactjs and mongo db."
    )

    terminology = [
        issue
        for issue in result.issues
        if issue.issue_type == LanguageIssueType.TERMINOLOGY
    ]

    assert len(terminology) == 3

    suggestions = {
        issue.original_text: issue.suggested_text
        for issue in terminology
    }

    assert suggestions["node js"] == "Node.js"
    assert suggestions["reactjs"] == "React"
    assert suggestions["mongo db"] == "MongoDB"


def test_excessive_punctuation_is_detected():
    result = analyze(
        "Built scalable systems!!! Improved performance...."
    )

    formatting = [
        issue
        for issue in result.issues
        if issue.issue_type == LanguageIssueType.FORMATTING
    ]

    assert len(formatting) == 1


def test_findings_have_evidence_and_confidence():
    result = analyze(
        "Experiance with Python."
    )

    assert result.issues

    for issue in result.issues:
        assert issue.evidence
        assert issue.confidence.score > 0.0
        assert issue.confidence.level.value in {
            "low",
            "medium",
            "high",
        }


def test_overall_score_is_bounded():
    result = analyze(
        """
        Experiance experiAnce managment recieve sucess
        built built built built
        quick learner team player hardworking worked on
        node js reactjs mongo db!!!
        """
    )

    assert 0.0 <= result.overall_score <= 100.0


def test_empty_resume_returns_warning():
    result = analyze("")

    assert result.issues == []
    assert result.overall_score == 100.0
    assert result.warnings
    assert any(
        "No resume text was available" in warning
        for warning in result.warnings
    )


def test_authorship_estimate_is_explicitly_heuristic():
    result = analyze(
        """
        Software Engineer

        Developed backend services using Python.
        Built REST APIs and automated data-processing workflows.
        Designed database integrations and improved application reliability.
        """
    )

    heuristic = result.authorship_heuristic

    assert 0.0 <= heuristic.score <= 100.0
    assert heuristic.level
    assert (
        heuristic.disclaimer
        == "This is a heuristic writing-style estimate, not proof of AI authorship."
    )
    assert "proof" in heuristic.disclaimer.lower()


def test_analyzer_version_is_stable():
    assert (
        ResumeLanguageQualityAnalyzer.ENGINE_VERSION
        == "phase9-language-quality-v1"
    )
