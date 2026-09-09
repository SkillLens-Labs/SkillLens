from __future__ import annotations

from backend.app.analysis.ats_intelligence import ATSIntelligenceAnalyzer
from backend.app.analysis.esco_mapper import ESCOMapper
from backend.app.analysis.jd_structure import JDSectionType
from backend.app.analysis.resume_profile_builder import ResumeProfileBuilder
from backend.app.analysis.resume_quality import ResumeQualityAnalyzer
from backend.app.analysis.resume_structure import ResumeSectionType, ResumeStructureInterpreter
from backend.app.analysis.skill_extractor import SkillExtractor
from backend.app.analysis.skill_normalizer import SkillNormalizer
from backend.app.domain.analysis import AnalysisMode, AnalysisStatus
from backend.app.infrastructure.parsers.models import (
    DocumentBlock,
    DocumentBlockType,
    DocumentType,
    ParsedDocument,
    SourceLocation,
)
from backend.app.orchestration.analysis_orchestrator import AnalysisOrchestrator
from backend.app.orchestration.concrete_analysis_orchestrator import (
    ConcreteAnalysisOrchestrator,
)
from backend.app.schemas.requests import (
    JobDescriptionDocumentInput,
    ResumeAnalysisRequest,
    ResumeDocumentInput,
    ResumeJDAnalysisRequest,
)


class StubDocumentProcessor:
    """Test adapter that returns an already-constructed ParsedDocument."""

    def __init__(self, document: ParsedDocument) -> None:
        self.document = document

    def process(
        self,
        filename: str,
        content: bytes,
        content_type: str | None = None,
        document_id: str | None = None,
    ) -> ParsedDocument:
        return self.document


def _block(
    text: str,
    block_type: DocumentBlockType,
    index: int,
) -> DocumentBlock:
    return DocumentBlock(
        text=text,
        block_type=block_type,
        source=SourceLocation(page_number=1, block_index=index),
    )


def _document() -> ParsedDocument:
    return ParsedDocument(
        document_id="orchestrator-resume-001",
        document_type=DocumentType.PDF,
        blocks=(
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
            _block("Experience", DocumentBlockType.HEADING, 5),
            _block(
                "Software Developer — ABC Technologies — 2025-2026",
                DocumentBlockType.PARAGRAPH,
                6,
            ),
            _block(
                "Built data analysis tools using Python and FastAPI.",
                DocumentBlockType.PARAGRAPH,
                7,
            ),
            _block("Education", DocumentBlockType.HEADING, 8),
            _block(
                "B.E. Computer Science Engineering",
                DocumentBlockType.PARAGRAPH,
                9,
            ),
            _block("Projects", DocumentBlockType.HEADING, 10),
            _block(
                "SkillLens — Resume intelligence platform using Python and React.",
                DocumentBlockType.PARAGRAPH,
                11,
            ),
        ),
    )



class StubResumeJDDocumentProcessor:
    """Test adapter that returns distinct resume and JD documents."""

    def __init__(
        self,
        resume_document: ParsedDocument,
        job_document: ParsedDocument,
    ) -> None:
        self.resume_document = resume_document
        self.job_document = job_document

    def process(
        self,
        filename: str,
        content: bytes,
        content_type: str | None = None,
        document_id: str | None = None,
    ) -> ParsedDocument:
        if filename == "resume.pdf":
            return self.resume_document
        if filename == "job.pdf":
            return self.job_document
        raise AssertionError(f"Unexpected filename: {filename}")


def _job_document() -> ParsedDocument:
    return ParsedDocument(
        document_id="orchestrator-job-001",
        document_type=DocumentType.PDF,
        blocks=(
            _block("Data Engineer", DocumentBlockType.PARAGRAPH, 0),
            _block("About the Role", DocumentBlockType.HEADING, 1),
            _block(
                "Build scalable data systems using Python and SQL.",
                DocumentBlockType.PARAGRAPH,
                2,
            ),
            _block("Responsibilities", DocumentBlockType.HEADING, 3),
            _block(
                "Develop data pipelines and analytical services.",
                DocumentBlockType.BULLET,
                4,
            ),
            _block("Required Qualifications", DocumentBlockType.HEADING, 5),
            _block(
                "Python and SQL",
                DocumentBlockType.BULLET,
                6,
            ),
            _block("Preferred Qualifications", DocumentBlockType.HEADING, 7),
            _block(
                "Docker experience",
                DocumentBlockType.BULLET,
                8,
            ),
        ),
    )



def _document_input() -> ResumeDocumentInput:
    return ResumeDocumentInput(
        filename="resume.pdf",
        content=b"test-document",
        content_type="application/pdf",
    )


def _orchestrator() -> ConcreteAnalysisOrchestrator:
    return ConcreteAnalysisOrchestrator(
        document_processor=StubDocumentProcessor(_document()),
    )


def test_orchestrator_implements_abstract_contract() -> None:
    orchestrator = _orchestrator()

    assert isinstance(orchestrator, AnalysisOrchestrator)


def test_resume_document_analysis_runs_complete_pipeline() -> None:
    result = _orchestrator().analyze_resume(
        _document_input(),
        ResumeAnalysisRequest(),
    )

    assert result.analysis_id
    assert result.analysis_mode == AnalysisMode.RESUME_ONLY
    assert result.status == AnalysisStatus.COMPLETED

    assert result.input.resume_document_id == "orchestrator-resume-001"
    assert result.input.job_description_document_id is None

    assert result.resume_profile.document_id == "orchestrator-resume-001"
    assert result.resume_profile.candidate_summary is not None
    assert result.resume_profile.skills

    assert result.resume_quality is not None
    assert result.ats_intelligence is not None


def test_orchestrator_preserves_phase3_structure_and_skill_pipeline() -> None:
    result = _orchestrator().analyze_resume(
        _document_input(),
        ResumeAnalysisRequest(),
    )

    assert result.resume_profile.document_id == "orchestrator-resume-001"
    assert result.resume_profile.skill_categories

    assert result.resume_profile.metadata["builder_version"] == "phase3-v1"
    assert result.resume_profile.metadata["esco_version"] == "1.2.1"


def test_orchestrator_populates_engine_metadata() -> None:
    orchestrator = _orchestrator()

    result = orchestrator.analyze_resume(
        _document_input(),
        ResumeAnalysisRequest(),
    )

    versions = result.metadata.engine_versions

    assert versions["orchestrator"] == orchestrator.ENGINE_VERSION
    assert versions["profile_builder"] == "phase3-v1"
    assert versions["resume_quality"] == ResumeQualityAnalyzer.ENGINE_VERSION
    assert versions["ats_intelligence"] == ATSIntelligenceAnalyzer.ENGINE_VERSION


def test_orchestrator_records_processing_time() -> None:
    result = _orchestrator().analyze_resume(
        _document_input(),
        ResumeAnalysisRequest(),
    )

    assert result.metadata.processing_time_ms is not None
    assert result.metadata.processing_time_ms >= 0


def test_orchestrator_stores_and_retrieves_analysis() -> None:
    orchestrator = _orchestrator()

    result = orchestrator.analyze_resume(
        _document_input(),
        ResumeAnalysisRequest(),
    )

    assert orchestrator.get_analysis(result.analysis_id) is result


def test_missing_analysis_returns_none() -> None:
    assert _orchestrator().get_analysis("does-not-exist") is None


def test_orchestrator_deletes_analysis() -> None:
    orchestrator = _orchestrator()

    result = orchestrator.analyze_resume(
        _document_input(),
        ResumeAnalysisRequest(),
    )

    assert orchestrator.delete_analysis(result.analysis_id) is True
    assert orchestrator.get_analysis(result.analysis_id) is None


def test_deleting_missing_analysis_returns_false() -> None:
    assert _orchestrator().delete_analysis("does-not-exist") is False


def test_resume_only_result_has_no_jd_analysis() -> None:
    result = _orchestrator().analyze_resume(
        _document_input(),
        ResumeAnalysisRequest(),
    )

    assert result.analysis_mode == AnalysisMode.RESUME_ONLY
    assert result.job_profile is None
    assert result.input.job_description_document_id is None


def test_analyze_resume_uses_canonical_document_input_contract() -> None:
    orchestrator = _orchestrator()

    result = orchestrator.analyze_resume(
        _document_input(),
        ResumeAnalysisRequest(),
    )

    assert result.analysis_mode == AnalysisMode.RESUME_ONLY
    assert result.status == AnalysisStatus.COMPLETED


def test_phase3_components_remain_single_source_of_truth() -> None:
    assert ResumeStructureInterpreter is not None
    assert SkillExtractor is not None
    assert SkillNormalizer is not None
    assert ESCOMapper is not None
    assert ResumeProfileBuilder is not None

    structured = ResumeStructureInterpreter().interpret(_document())

    assert [section.section_type for section in structured.sections] == [
        ResumeSectionType.HEADER,
        ResumeSectionType.SUMMARY,
        ResumeSectionType.SKILLS,
        ResumeSectionType.EXPERIENCE,
        ResumeSectionType.EDUCATION,
        ResumeSectionType.PROJECTS,
    ]


def test_resume_jd_analysis_runs_complete_phase5_pipeline() -> None:
    orchestrator = ConcreteAnalysisOrchestrator(
        document_processor=StubResumeJDDocumentProcessor(
            _document(),
            _job_document(),
        ),
    )

    result = orchestrator.analyze_resume_jd(
        ResumeDocumentInput(
            filename="resume.pdf",
            content=b"resume-document",
            content_type="application/pdf",
        ),
        JobDescriptionDocumentInput(
            filename="job.pdf",
            content=b"job-document",
            content_type="application/pdf",
        ),
        ResumeJDAnalysisRequest(),
    )

    assert result.analysis_id
    assert result.analysis_mode == AnalysisMode.RESUME_JD
    assert result.status == AnalysisStatus.COMPLETED

    assert result.input.resume_document_id == "orchestrator-resume-001"
    assert result.input.job_description_document_id == "orchestrator-job-001"

    assert result.resume_profile.skills

    assert result.job_profile is not None
    assert result.job_profile.document_id == "orchestrator-job-001"
    assert result.job_profile.job_title == "Data Engineer"
    assert result.job_profile.required_skills

    assert result.matching is not None
    assert result.matching.skill_matches
    assert result.matching.requirement_alignments
    assert all(
        alignment.requirement_id
        for alignment in result.matching.requirement_alignments
    )

    assert result.skill_analysis is not None
    assert result.skill_analysis.extracted_skills
    assert result.skill_analysis.matched_skills
    assert isinstance(result.skill_analysis.gaps, list)

    assert result.scoring is not None
    assert 0.0 <= result.scoring.overall_score <= 100.0
    assert result.scoring.dimension_scores
    assert result.scoring.contributions

    assert result.xai is not None
    assert result.xai.overall_explanation
    assert result.xai.score_explanation

    assert result.metadata.extra["job_requirement_count"] >= 2
    assert result.metadata.extra["job_skill_count"] >= 2


def test_resume_jd_analysis_stores_result() -> None:
    orchestrator = ConcreteAnalysisOrchestrator(
        document_processor=StubResumeJDDocumentProcessor(
            _document(),
            _job_document(),
        ),
    )

    result = orchestrator.analyze_resume_jd(
        ResumeDocumentInput(
            filename="resume.pdf",
            content=b"resume-document",
            content_type="application/pdf",
        ),
        JobDescriptionDocumentInput(
            filename="job.pdf",
            content=b"job-document",
            content_type="application/pdf",
        ),
        ResumeJDAnalysisRequest(),
    )

    assert orchestrator.get_analysis(result.analysis_id) is result


def test_resume_analysis_populates_career_intelligence() -> None:
    result = _orchestrator().analyze_resume(
        _document_input(),
        ResumeAnalysisRequest(),
    )

    assert result.career_intelligence is not None
    assert result.career_intelligence.engine_version == (
        "phase7-career-intelligence-v1"
    )
    assert result.career_intelligence.taxonomy_version == (
        "career-taxonomy-v1"
    )
    assert result.metadata.engine_versions["career_intelligence"] == (
        "phase7-career-intelligence-v1"
    )


def test_resume_analysis_can_disable_career_intelligence() -> None:
    from backend.app.schemas.requests import AnalysisOptions

    result = _orchestrator().analyze_resume(
        _document_input(),
        ResumeAnalysisRequest(
            options=AnalysisOptions(
                include_career_intelligence=False,
            )
        ),
    )

    assert result.career_intelligence is None
    assert "career_intelligence" not in result.metadata.engine_versions


def test_resume_jd_analysis_populates_career_intelligence() -> None:
    orchestrator = ConcreteAnalysisOrchestrator(
        document_processor=StubResumeJDDocumentProcessor(
            _document(),
            _job_document(),
        ),
    )

    result = orchestrator.analyze_resume_jd(
        ResumeDocumentInput(
            filename="resume.pdf",
            content=b"resume-document",
            content_type="application/pdf",
        ),
        JobDescriptionDocumentInput(
            filename="job.pdf",
            content=b"job-document",
            content_type="application/pdf",
        ),
        ResumeJDAnalysisRequest(),
    )

    assert result.career_intelligence is not None
    assert result.career_intelligence.engine_version == (
        "phase7-career-intelligence-v1"
    )
    assert result.scoring is not None
    assert result.xai is not None


def test_resume_jd_analysis_can_disable_career_intelligence() -> None:
    from backend.app.schemas.requests import AnalysisOptions

    orchestrator = ConcreteAnalysisOrchestrator(
        document_processor=StubResumeJDDocumentProcessor(
            _document(),
            _job_document(),
        ),
    )

    result = orchestrator.analyze_resume_jd(
        ResumeDocumentInput(
            filename="resume.pdf",
            content=b"resume-document",
            content_type="application/pdf",
        ),
        JobDescriptionDocumentInput(
            filename="job.pdf",
            content=b"job-document",
            content_type="application/pdf",
        ),
        ResumeJDAnalysisRequest(
            options=AnalysisOptions(
                include_career_intelligence=False,
            )
        ),
    )

    assert result.career_intelligence is None
    assert "career_intelligence" not in result.metadata.engine_versions
    assert result.scoring is not None
    assert result.xai is not None
