from __future__ import annotations

from backend.app.analysis.ats_intelligence import ATSIntelligenceAnalyzer
from backend.app.analysis.esco_mapper import ESCOMapper
from backend.app.analysis.jd_structure import JDSectionType
from backend.app.analysis.resume_profile_builder import ResumeProfileBuilder
from backend.app.analysis.resume_quality import ResumeQualityAnalyzer
from backend.app.analysis.resume_structure import ResumeSectionType, ResumeStructureInterpreter
from backend.app.analysis.skill_extractor import SkillExtractor
from backend.app.analysis.skill_normalizer import SkillNormalizer
from backend.app.analysis.resume_language_quality import ResumeLanguageQualityAnalyzer
from backend.app.domain.analysis import AnalysisMode, AnalysisStatus
from backend.app.domain.career import (
    CareerDirection,
    CareerIntelligence,
    CareerSeniorityLevel,
    RoleFit,
)
from backend.app.domain.confidence import Confidence, ConfidenceLevel
from backend.app.domain.recommendations import RecommendationType
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


class StubCareerIntelligenceAnalyzer:
    """Deterministic career analyzer for recommendation integration tests."""

    ENGINE_VERSION = "phase7-career-intelligence-v1"

    def analyze(self, *, resume_profile, structured_resume) -> CareerIntelligence:
        confidence = Confidence(
            score=0.95,
            level=ConfidenceLevel.HIGH,
            components={"test_fixture": 0.95},
            rationale="Deterministic test fixture confidence.",
        )

        role_fit = RoleFit(
            role="Data Engineer",
            fit_score=85.0,
            direction=CareerDirection.PRIMARY,
            rationale="Strong deterministic fit for integration testing.",
            confidence=confidence,
        )

        return CareerIntelligence(
            inferred_profile="Data-focused software engineering profile",
            experience_level=CareerSeniorityLevel.JUNIOR,
            seniority_confidence=confidence,
            seniority_rationale="Deterministic test fixture.",
            primary_domains=["Data Engineering"],
            strengths=["Python", "Data Analysis"],
            limitations=[],
            transferable_skills=["Python"],
            career_directions=[],
            potential_roles=["Data Engineer"],
            role_fit=[role_fit],
            career_signals=["Strong data engineering alignment"],
            transition_analysis=None,
            skill_priorities=[],
            risks=[],
            confidence=confidence,
            taxonomy_version="career-taxonomy-v1",
            engine_version=self.ENGINE_VERSION,
        )


class StubRecommendationLLMEnhancer:
    """Deterministic LLM enhancer for orchestrator integration tests."""

    ENGINE_VERSION = "recommendation-llm-enhancer-test-v1"

    def __init__(self) -> None:
        self.calls = 0

    def enhance(self, recommendation):
        self.calls += 1
        return recommendation.model_copy(
            update={
                "title": f"LLM: {recommendation.title}",
                "rationale": f"LLM: {recommendation.rationale}",
            }
        )


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


def _document_without_summary() -> ParsedDocument:
    return ParsedDocument(
        document_id="orchestrator-resume-no-summary-001",
        document_type=DocumentType.PDF,
        blocks=(
            _block("Raghuvir Anturkar", DocumentBlockType.PARAGRAPH, 0),
            _block("Technical Skills", DocumentBlockType.HEADING, 1),
            _block(
                "Python, React, Docker, FastAPI",
                DocumentBlockType.PARAGRAPH,
                2,
            ),
            _block("Experience", DocumentBlockType.HEADING, 3),
            _block(
                "Software Developer — ABC Technologies — 2025-2026",
                DocumentBlockType.PARAGRAPH,
                4,
            ),
            _block(
                "Built data analysis tools using Python and FastAPI.",
                DocumentBlockType.PARAGRAPH,
                5,
            ),
            _block("Education", DocumentBlockType.HEADING, 6),
            _block(
                "B.E. Computer Science Engineering",
                DocumentBlockType.PARAGRAPH,
                7,
            ),
            _block("Projects", DocumentBlockType.HEADING, 8),
            _block(
                "SkillLens — Resume intelligence platform using Python and React.",
                DocumentBlockType.PARAGRAPH,
                9,
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


def _job_document_with_missing_skill() -> ParsedDocument:
    return ParsedDocument(
        document_id="orchestrator-job-missing-skill-001",
        document_type=DocumentType.PDF,
        blocks=(
            _block("Data Engineer", DocumentBlockType.PARAGRAPH, 0),
            _block("About the Role", DocumentBlockType.HEADING, 1),
            _block(
                "Build scalable data systems using Python and Kubernetes.",
                DocumentBlockType.PARAGRAPH,
                2,
            ),
            _block("Responsibilities", DocumentBlockType.HEADING, 3),
            _block(
                "Develop and maintain data infrastructure.",
                DocumentBlockType.BULLET,
                4,
            ),
            _block("Required Qualifications", DocumentBlockType.HEADING, 5),
            _block(
                "Kubernetes experience",
                DocumentBlockType.BULLET,
                6,
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


def _orchestrator_without_summary() -> ConcreteAnalysisOrchestrator:
    return ConcreteAnalysisOrchestrator(
        document_processor=StubDocumentProcessor(
            _document_without_summary(),
        ),
    )


def _orchestrator_with_stubbed_career() -> ConcreteAnalysisOrchestrator:
    return ConcreteAnalysisOrchestrator(
        document_processor=StubDocumentProcessor(_document()),
        career_intelligence_analyzer=StubCareerIntelligenceAnalyzer(),
    )


def _orchestrator_with_llm_enhancer() -> tuple[
    ConcreteAnalysisOrchestrator,
    StubRecommendationLLMEnhancer,
]:
    enhancer = StubRecommendationLLMEnhancer()

    orchestrator = ConcreteAnalysisOrchestrator(
        document_processor=StubDocumentProcessor(
            _document_without_summary(),
        ),
        career_intelligence_analyzer=StubCareerIntelligenceAnalyzer(),
        recommendation_llm_enhancer=enhancer,
    )

    return orchestrator, enhancer


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

    assert result.language_quality is not None
    assert result.language_quality.overall_score >= 0.0
    assert result.language_quality.overall_score <= 100.0



def test_resume_analysis_integrates_resume_improvement_prompt() -> None:
    result = _orchestrator().analyze_resume(
        _document_input(),
        ResumeAnalysisRequest(),
    )

    assert result.resume_improvement_prompt is not None
    assert result.resume_improvement_prompt.strip()
    assert "CANDIDATE FACTS" in result.resume_improvement_prompt
    assert "RESUME QUALITY" in result.resume_improvement_prompt
    assert "LANGUAGE QUALITY" in result.resume_improvement_prompt
    assert "STRICT FACTUALITY RULES" in result.resume_improvement_prompt
    assert result.metadata.engine_versions[
        "resume_improvement_prompt"
    ] == "phase9-resume-improvement-prompt-v2"


def test_resume_jd_analysis_integrates_resume_improvement_prompt() -> None:
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

    assert result.resume_improvement_prompt is not None
    assert result.resume_improvement_prompt.strip()
    assert "TARGET JOB" in result.resume_improvement_prompt
    assert "Required skills:" in result.resume_improvement_prompt
    assert "Preferred skills:" in result.resume_improvement_prompt
    assert "Matched skills:" in result.resume_improvement_prompt
    assert "Partial matches:" in result.resume_improvement_prompt
    assert "Transferable skills:" in result.resume_improvement_prompt
    assert "STRICT FACTUALITY RULES" in result.resume_improvement_prompt
    assert result.metadata.engine_versions[
        "resume_improvement_prompt"
    ] == "phase9-resume-improvement-prompt-v2"


def test_resume_analysis_integrates_language_quality() -> None:
    result = _orchestrator().analyze_resume(
        _document_input(),
        ResumeAnalysisRequest(),
    )

    assert result.language_quality is not None
    assert result.metadata.engine_versions["language_quality"] == (
        ResumeLanguageQualityAnalyzer.ENGINE_VERSION
    )
    assert result.language_quality.confidence is not None
    assert result.language_quality.authorship_heuristic is not None
    assert result.language_quality.authorship_heuristic.disclaimer == (
        "This is a heuristic writing-style estimate, not proof of AI authorship."
    )


def test_orchestrator_preserves_phase3_structure_and_skill_pipeline() -> None:
    result = _orchestrator().analyze_resume(
        _document_input(),
        ResumeAnalysisRequest(),
    )

    assert result.resume_profile.document_id == "orchestrator-resume-001"
    assert result.resume_profile.skill_categories

    assert result.resume_profile.metadata["builder_version"] == "phase3-v2"
    assert result.resume_profile.metadata["esco_version"] == "1.2.1"


def test_orchestrator_populates_engine_metadata() -> None:
    orchestrator = _orchestrator()

    result = orchestrator.analyze_resume(
        _document_input(),
        ResumeAnalysisRequest(),
    )

    versions = result.metadata.engine_versions

    assert versions["orchestrator"] == orchestrator.ENGINE_VERSION
    assert versions["profile_builder"] == "phase3-v2"
    assert versions["resume_quality"] == ResumeQualityAnalyzer.ENGINE_VERSION
    assert versions["ats_intelligence"] == ATSIntelligenceAnalyzer.ENGINE_VERSION
    assert (
        versions["language_quality"]
        == ResumeLanguageQualityAnalyzer.ENGINE_VERSION
    )


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

    assert result.language_quality is not None
    assert result.language_quality.overall_score >= 0.0
    assert result.language_quality.overall_score <= 100.0


def test_resume_jd_analysis_integrates_language_quality() -> None:
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

    assert result.language_quality is not None
    assert result.metadata.engine_versions["language_quality"] == (
        ResumeLanguageQualityAnalyzer.ENGINE_VERSION
    )
    assert result.language_quality.confidence is not None
    assert result.language_quality.authorship_heuristic is not None


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


def test_resume_analysis_populates_recommendations_by_default() -> None:
    result = _orchestrator_without_summary().analyze_resume(
        ResumeDocumentInput(
            filename="resume.pdf",
            content=b"test-document",
            content_type="application/pdf",
        ),
        ResumeAnalysisRequest(),
    )

    assert result.recommendations
    assert any(
        recommendation.type == RecommendationType.RESUME
        for recommendation in result.recommendations
    )
    assert all(
        recommendation.recommendation_id
        for recommendation in result.recommendations
    )
    assert all(
        recommendation.rationale
        for recommendation in result.recommendations
    )


def test_resume_analysis_can_disable_recommendations() -> None:
    from backend.app.schemas.requests import AnalysisOptions

    result = _orchestrator().analyze_resume(
        _document_input(),
        ResumeAnalysisRequest(
            options=AnalysisOptions(
                include_recommendations=False,
            )
        ),
    )

    assert result.recommendations == []
    assert "recommendation_intelligence" not in result.metadata.engine_versions


def test_resume_analysis_records_recommendation_engine_version() -> None:
    result = _orchestrator().analyze_resume(
        _document_input(),
        ResumeAnalysisRequest(),
    )

    assert (
        result.metadata.engine_versions["recommendation_intelligence"]
        == "recommendation-intelligence-v1"
    )


def test_resume_analysis_career_recommendations_flow_through() -> None:
    result = _orchestrator_with_stubbed_career().analyze_resume(
        _document_input(),
        ResumeAnalysisRequest(),
    )

    career_recommendations = [
        recommendation
        for recommendation in result.recommendations
        if recommendation.type == RecommendationType.CAREER
    ]

    assert career_recommendations
    assert any(
        recommendation.title == "Explore Data Engineer career path"
        for recommendation in career_recommendations
    )
    assert all(
        recommendation.source_engine == "recommendation-intelligence-v1"
        for recommendation in career_recommendations
    )


def test_resume_jd_analysis_populates_recommendations() -> None:
    orchestrator = ConcreteAnalysisOrchestrator(
        document_processor=StubResumeJDDocumentProcessor(
            _document(),
            _job_document_with_missing_skill(),
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

    assert result.recommendations
    assert any(
        recommendation.type == RecommendationType.LEARNING
        for recommendation in result.recommendations
    )
    assert all(
        recommendation.recommendation_id
        for recommendation in result.recommendations
    )
    assert all(
        recommendation.rationale
        for recommendation in result.recommendations
    )
    assert (
        result.metadata.engine_versions["recommendation_intelligence"]
        == "recommendation-intelligence-v1"
    )


def test_orchestrator_keeps_llm_disabled_by_default() -> None:
    orchestrator = _orchestrator_without_summary()

    result = orchestrator.analyze_resume(
        _document_input(),
        ResumeAnalysisRequest(),
    )

    assert result.recommendations
    assert "recommendation_llm_enhancer" not in result.metadata.engine_versions

    for recommendation in result.recommendations:
        assert not recommendation.title.startswith("LLM:")
        assert not recommendation.rationale.startswith("LLM:")


def test_orchestrator_applies_optional_llm_enhancement() -> None:
    orchestrator, enhancer = _orchestrator_with_llm_enhancer()

    result = orchestrator.analyze_resume(
        _document_input(),
        ResumeAnalysisRequest(),
    )

    assert result.recommendations
    assert enhancer.calls == len(result.recommendations)

    assert (
        result.metadata.engine_versions["recommendation_llm_enhancer"]
        == StubRecommendationLLMEnhancer.ENGINE_VERSION
    )

    for recommendation in result.recommendations:
        assert recommendation.title.startswith("LLM:")
        assert recommendation.rationale.startswith("LLM:")


def test_orchestrator_llm_enhancement_preserves_deterministic_fields() -> None:
    baseline_orchestrator = ConcreteAnalysisOrchestrator(
        document_processor=StubDocumentProcessor(
            _document_without_summary(),
        ),
        career_intelligence_analyzer=StubCareerIntelligenceAnalyzer(),
    )
    baseline = baseline_orchestrator.analyze_resume(
        _document_input(),
        ResumeAnalysisRequest(),
    )

    orchestrator, _ = _orchestrator_with_llm_enhancer()

    enhanced = orchestrator.analyze_resume(
        _document_input(),
        ResumeAnalysisRequest(),
    )

    assert len(enhanced.recommendations) == len(
        baseline.recommendations
    )

    baseline_by_id = {
        recommendation.recommendation_id: recommendation
        for recommendation in baseline.recommendations
    }

    assert set(baseline_by_id) == {
        recommendation.recommendation_id
        for recommendation in enhanced.recommendations
    }

    for recommendation in enhanced.recommendations:
        original = baseline_by_id[recommendation.recommendation_id]

        assert recommendation.recommendation_id == original.recommendation_id
        assert recommendation.type == original.type
        assert recommendation.target_skill == original.target_skill
        assert recommendation.priority == original.priority
        assert recommendation.expected_impact == original.expected_impact
        assert recommendation.effort == original.effort
        assert recommendation.evidence == original.evidence
        assert recommendation.related_gap_ids == original.related_gap_ids
        assert recommendation.confidence == original.confidence
        assert recommendation.priority_score == original.priority_score
        assert recommendation.impact_score == original.impact_score
        assert recommendation.source_engine == original.source_engine