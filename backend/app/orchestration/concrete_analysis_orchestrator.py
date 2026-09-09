from __future__ import annotations

from time import perf_counter
from uuid import uuid4

from backend.app.analysis.ats_intelligence import ATSIntelligenceAnalyzer
from backend.app.analysis.career_intelligence import (
    ENGINE_VERSION as CAREER_INTELLIGENCE_ENGINE_VERSION,
    CareerIntelligenceAnalyzer,
)
from backend.app.analysis.gaps import GapAnalyzer
from backend.app.analysis.scoring import ScoringAnalyzer
from backend.app.analysis.xai import XAIAnalyzer
from backend.app.analysis.esco_mapper import ESCOMapper
from backend.app.analysis.jd_profile_builder import JDProfileBuilder
from backend.app.analysis.jd_requirement_extractor import JDRequirementExtractor
from backend.app.analysis.jd_skill_extractor import JDSkillExtractor
from backend.app.analysis.jd_skill_normalizer import JDSkillNormalizer
from backend.app.analysis.jd_structure import JDStructureInterpreter
from backend.app.analysis.resume_profile_builder import ResumeProfileBuilder
from backend.app.analysis.requirement_aligner import RequirementAligner
from backend.app.analysis.resume_quality import ResumeQualityAnalyzer
from backend.app.analysis.resume_structure import ResumeStructureInterpreter
from backend.app.analysis.skill_extractor import SkillExtractor
from backend.app.analysis.skill_matcher import SkillMatcher
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
    JobDescriptionDocumentInput,
    ResumeAnalysisRequest,
    ResumeDocumentInput,
    ResumeJDAnalysisRequest,
)
from backend.app.orchestration.analysis_orchestrator import AnalysisOrchestrator


class ConcreteAnalysisOrchestrator(AnalysisOrchestrator):
    """Concrete Phase 6 orchestrator for resume and job-description analysis."""

    ENGINE_VERSION = "phase7-orchestrator-v1"

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
        career_intelligence_analyzer: CareerIntelligenceAnalyzer | None = None,
        jd_structure_interpreter: JDStructureInterpreter | None = None,
        jd_requirement_extractor: JDRequirementExtractor | None = None,
        jd_skill_extractor: JDSkillExtractor | None = None,
        jd_skill_normalizer: JDSkillNormalizer | None = None,
        jd_profile_builder: JDProfileBuilder | None = None,
        skill_matcher: SkillMatcher | None = None,
        requirement_aligner: RequirementAligner | None = None,
        gap_analyzer: GapAnalyzer | None = None,
        scoring_analyzer: ScoringAnalyzer | None = None,
        xai_analyzer: XAIAnalyzer | None = None,
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
        self._career_intelligence_analyzer = (
            career_intelligence_analyzer or CareerIntelligenceAnalyzer()
        )
        self._jd_structure_interpreter = (
            jd_structure_interpreter or JDStructureInterpreter()
        )
        self._jd_requirement_extractor = (
            jd_requirement_extractor or JDRequirementExtractor()
        )
        self._jd_skill_extractor = jd_skill_extractor or JDSkillExtractor()
        self._jd_skill_normalizer = jd_skill_normalizer or JDSkillNormalizer()
        self._jd_profile_builder = jd_profile_builder or JDProfileBuilder()
        self._skill_matcher = skill_matcher or SkillMatcher()
        self._requirement_aligner = requirement_aligner or RequirementAligner()
        self._gap_analyzer = gap_analyzer or GapAnalyzer()
        self._scoring_analyzer = scoring_analyzer or ScoringAnalyzer()
        self._xai_analyzer = xai_analyzer or XAIAnalyzer()
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


        career_intelligence = None
        if request.options.include_career_intelligence:
            career_intelligence = self._career_intelligence_analyzer.analyze(
                resume_profile=resume_profile,
                structured_resume=structured_resume,
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

        if career_intelligence is not None:
            engine_versions["career_intelligence"] = (
                CAREER_INTELLIGENCE_ENGINE_VERSION
            )

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
            career_intelligence=career_intelligence,
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
        resume_input: ResumeDocumentInput,
        job_description_input: JobDescriptionDocumentInput,
        request: ResumeJDAnalysisRequest,
    ) -> AnalysisResult:
        """Run the Phase 5 resume + job-description analysis pipeline."""
        started = perf_counter()

        resume_document = self._document_processor.process(
            filename=resume_input.filename,
            content=resume_input.content,
            content_type=resume_input.content_type,
        )
        structured_resume = self._structure_interpreter.interpret(resume_document)
        resume_extraction = self._skill_extractor.extract(structured_resume)
        resume_normalized_skills = self._skill_normalizer.normalize_many(
            resume_extraction.mentions
        )
        resume_esco_results = self._esco_mapper.map_many(
            resume_normalized_skills
        )
        resume_profile = self._profile_builder.build(
            structured_resume,
            resume_normalized_skills,
            resume_esco_results,
        )

        career_intelligence = None
        if request.options.include_career_intelligence:
            career_intelligence = self._career_intelligence_analyzer.analyze(
                resume_profile=resume_profile,
                structured_resume=structured_resume,
            )

        job_document = self._document_processor.process(
            filename=job_description_input.filename,
            content=job_description_input.content,
            content_type=job_description_input.content_type,
        )
        structured_job = self._jd_structure_interpreter.interpret(job_document)
        requirements = tuple(
            self._jd_requirement_extractor.extract(structured_job)
        )
        jd_extraction = self._jd_skill_extractor.extract(structured_job)
        jd_normalized_skills = self._jd_skill_normalizer.normalize_many(
            jd_extraction.mentions
        )
        jd_esco_results = self._esco_mapper.map_many(jd_normalized_skills)
        jd_build = self._jd_profile_builder.build_with_skills(
            structured_job,
            requirements,
            jd_normalized_skills,
            jd_esco_results,
        )

        matching = self._skill_matcher.match(
            resume_profile.skills,
            jd_build.skills,
            resume_esco=resume_esco_results,
            job_esco=jd_esco_results,
        )
        requirement_alignments = self._requirement_aligner.align(
            requirements,
            matching.skill_matches,
            resume_profile.skills,
            jd_build.skills,
            structured_resume,
        )
        matching = matching.model_copy(
            update={
                "requirement_alignments": requirement_alignments,
            }
        )

        skill_analysis = self._gap_analyzer.analyze(
            requirements=requirements,
            matching=matching,
            resume_skills=resume_profile.skills,
            job_skills=jd_build.skills,
        )

        scoring = self._scoring_analyzer.score(
            job_profile=jd_build.profile,
            requirements=requirements,
            matching=matching,
            resume_skills=resume_profile.skills,
            job_skills=jd_build.skills,
        )

        xai = self._xai_analyzer.explain(
            scoring=scoring,
            skill_analysis=skill_analysis,
            matching=matching,
            resume_skills=resume_profile.skills,
            job_skills=jd_build.skills,
        )

        processing_time_ms = max(
            0,
            round((perf_counter() - started) * 1000),
        )

        analysis_id = str(uuid4())
        result = AnalysisResult(
            analysis_id=analysis_id,
            analysis_mode=AnalysisMode.RESUME_JD,
            status=AnalysisStatus.COMPLETED,
            input=AnalysisInput(
                resume_document_id=resume_document.document_id,
                job_description_document_id=job_document.document_id,
            ),
            resume_profile=resume_profile,
            job_profile=jd_build.profile,
            matching=matching,
            skill_analysis=skill_analysis,
            scoring=scoring,
            xai=xai,
            career_intelligence=career_intelligence,
            metadata=AnalysisMetadata(
                engine_versions={
                    "orchestrator": self.ENGINE_VERSION,
                    "profile_builder": self._profile_builder.BUILDER_VERSION,
                    "jd_profile_builder": self._jd_profile_builder.BUILDER_VERSION,
                    "skill_matcher": self._skill_matcher.ENGINE_VERSION,
                    "requirement_aligner": self._requirement_aligner.ENGINE_VERSION,
                    "gap_analyzer": self._gap_analyzer.ENGINE_VERSION,
                    "scoring_analyzer": self._scoring_analyzer.ENGINE_VERSION,
                    "xai_analyzer": self._xai_analyzer.ENGINE_VERSION,
                    **(
                        {
                            "career_intelligence": CAREER_INTELLIGENCE_ENGINE_VERSION,
                        }
                        if career_intelligence is not None
                        else {}
                    ),
                },
                processing_time_ms=processing_time_ms,
                warnings=(),
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
                    "job_requirement_count": len(requirements),
                    "job_skill_count": len(jd_build.skills),
                },
            ),
        )

        self._analyses[analysis_id] = result
        return result

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