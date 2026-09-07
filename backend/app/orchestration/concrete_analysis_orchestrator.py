from __future__ import annotations

from time import perf_counter
from uuid import uuid4

from backend.app.analysis.ats_intelligence import ATSIntelligenceAnalyzer
from backend.app.analysis.esco_mapper import ESCOMapper
from backend.app.analysis.resume_profile_builder import ResumeProfileBuilder
from backend.app.analysis.resume_quality import ResumeQualityAnalyzer
from backend.app.analysis.resume_structure import ResumeStructureInterpreter
from backend.app.analysis.skill_extractor import SkillExtractor
from backend.app.analysis.skill_normalizer import SkillNormalizer
from backend.app.domain.analysis import (
    AnalysisInput,
    AnalysisMetadata,
    AnalysisMode,
    AnalysisResult,
    AnalysisStatus,
)
from backend.app.infrastructure.parsers.document_processor import DocumentProcessor
from backend.app.schemas.requests import (
    ResumeAnalysisRequest,
    ResumeDocumentInput,
    ResumeJDAnalysisRequest,
)
from backend.app.orchestration.analysis_orchestrator import AnalysisOrchestrator


class ConcreteAnalysisOrchestrator(AnalysisOrchestrator):
    """Concrete Phase 4 orchestrator for resume-only analysis."""

    ENGINE_VERSION = "phase4-orchestrator-v1"

    def __init__(
        self,
        *,
        document_processor: DocumentProcessor | None = None,
        structure_interpreter: ResumeStructureInterpreter | None = None,
        skill_extractor: SkillExtractor | None = None,
        skill_normalizer: SkillNormalizer | None = None,
        esco_mapper: ESCOMapper | None = None,
        profile_builder: ResumeProfileBuilder | None = None,
        quality_analyzer: ResumeQualityAnalyzer | None = None,
        ats_analyzer: ATSIntelligenceAnalyzer | None = None,
    ) -> None:
        self._document_processor = document_processor or DocumentProcessor()
        self._structure_interpreter = (
            structure_interpreter or ResumeStructureInterpreter()
        )
        self._skill_extractor = skill_extractor or SkillExtractor()
        self._skill_normalizer = skill_normalizer or SkillNormalizer()
        self._esco_mapper = esco_mapper or ESCOMapper()
        self._profile_builder = profile_builder or ResumeProfileBuilder()
        self._quality_analyzer = quality_analyzer or ResumeQualityAnalyzer()
        self._ats_analyzer = ats_analyzer or ATSIntelligenceAnalyzer()
        self._analyses: dict[str, AnalysisResult] = {}

    def analyze_resume(
        self,
        document_input: ResumeDocumentInput,
        request: ResumeAnalysisRequest,
    ) -> AnalysisResult:
        """Run the complete Phase 4 resume-only analysis pipeline."""
        started = perf_counter()

        document = self._document_processor.process(
            filename=document_input.filename,
            content=document_input.content,
            content_type=document_input.content_type,
        )
        structured_resume = self._structure_interpreter.interpret(document)
        extraction = self._skill_extractor.extract(structured_resume)
        normalized_skills = self._skill_normalizer.normalize_many(
            extraction.mentions
        )
        esco_results = self._esco_mapper.map_many(normalized_skills)
        resume_profile = self._profile_builder.build(
            structured_resume,
            normalized_skills,
            esco_results,
        )
        resume_quality = self._quality_analyzer.analyze(
            structured_resume,
            resume_profile,
        )
        ats_intelligence = self._ats_analyzer.analyze(
            document,
            structured_resume,
            resume_profile,
        )

        processing_time_ms = max(
            0,
            round((perf_counter() - started) * 1000),
        )

        warnings = (
            *resume_quality.warnings,
            *ats_intelligence.warnings,
        )

        engine_versions = {
            "orchestrator": self.ENGINE_VERSION,
            "profile_builder": self._profile_builder.BUILDER_VERSION,
            "resume_quality": self._quality_analyzer.ENGINE_VERSION,
            "ats_intelligence": self._ats_analyzer.ENGINE_VERSION,
        }

        analysis_id = str(uuid4())

        result = AnalysisResult(
            analysis_id=analysis_id,
            analysis_mode=AnalysisMode.RESUME_ONLY,
            status=AnalysisStatus.COMPLETED,
            input=AnalysisInput(
                resume_document_id=document.document_id,
            ),
            resume_profile=resume_profile,
            resume_quality=resume_quality,
            ats_intelligence=ats_intelligence,
            metadata=AnalysisMetadata(
                engine_versions=engine_versions,
                processing_time_ms=processing_time_ms,
                warnings=warnings,
                extra={
                    "source": (
                        request.client_metadata.source
                        if request.client_metadata
                        else None
                    ),
                    "session_id": (
                        request.client_metadata.session_id
                        if request.client_metadata
                        else None
                    ),
                },
            ),
        )

        self._analyses[analysis_id] = result
        return result

    def analyze_resume_jd(
        self,
        request: ResumeJDAnalysisRequest,
    ) -> AnalysisResult:
        """JD analysis is intentionally outside the Phase 4 implementation."""
        raise NotImplementedError(
            "Resume + job-description analysis is not implemented in Phase 4."
        )

    def get_analysis(
        self,
        analysis_id: str,
    ) -> AnalysisResult | None:
        """Retrieve an in-memory analysis result."""
        return self._analyses.get(analysis_id)

    def delete_analysis(
        self,
        analysis_id: str,
    ) -> bool:
        """Delete an in-memory analysis result."""
        return self._analyses.pop(analysis_id, None) is not None
