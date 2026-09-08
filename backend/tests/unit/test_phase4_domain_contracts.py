from backend.app.domain.analysis import AnalysisResult
from backend.app.domain.ats_intelligence import (
    ATSIntelligenceDimension,
    ATSIntelligenceDimensionScore,
    ATSIntelligenceResult,
)
from backend.app.domain.confidence import Confidence, ConfidenceLevel
from backend.app.domain.matching import MatchingResult
from backend.app.domain.resume import ResumeProfile
from backend.app.domain.resume_quality import (
    ResumeQualityDimension,
    ResumeQualityDimensionScore,
    ResumeQualityResult,
)


def _confidence() -> Confidence:
    return Confidence(
        score=0.9,
        level=ConfidenceLevel.HIGH,
        rationale="Deterministic Phase 4 analysis.",
    )


def _profile() -> ResumeProfile:
    return ResumeProfile(
        profile_id="profile-1",
        document_id="document-1",
    )


def test_resume_quality_contract_has_bounded_scores():
    result = ResumeQualityResult(
        overall_score=82.5,
        dimension_scores=[
            ResumeQualityDimensionScore(
                dimension=ResumeQualityDimension.STRUCTURE,
                score=90.0,
                weight=0.2,
            )
        ],
        confidence=_confidence(),
    )

    assert result.overall_score == 82.5
    assert result.dimension_scores[0].dimension == ResumeQualityDimension.STRUCTURE
    assert result.confidence.score == 0.9


def test_ats_intelligence_contract_has_bounded_scores():
    result = ATSIntelligenceResult(
        overall_score=76.0,
        dimension_scores=[
            ATSIntelligenceDimensionScore(
                dimension=ATSIntelligenceDimension.MACHINE_READABILITY,
                score=80.0,
                weight=0.2,
            )
        ],
        confidence=_confidence(),
    )

    assert result.overall_score == 76.0
    assert (
        result.dimension_scores[0].dimension
        == ATSIntelligenceDimension.MACHINE_READABILITY
    )


def test_analysis_result_exposes_phase4_results_without_forcing_them():
    result = AnalysisResult(
        analysis_id="analysis-1",
        analysis_mode="resume_only",
        status="completed",
        input={"resume_document_id": "document-1"},
        resume_profile=_profile(),
    )

    assert result.resume_quality is None
    assert result.ats_intelligence is None


def test_analysis_result_can_carry_phase4_results():
    quality = ResumeQualityResult(
        overall_score=80.0,
        confidence=_confidence(),
    )
    ats = ATSIntelligenceResult(
        overall_score=75.0,
        confidence=_confidence(),
    )

    result = AnalysisResult(
        analysis_id="analysis-1",
        analysis_mode="resume_only",
        status="completed",
        input={"resume_document_id": "document-1"},
        resume_profile=_profile(),
        resume_quality=quality,
        ats_intelligence=ats,
    )

    assert result.resume_quality is quality
    assert result.ats_intelligence is ats


def test_analysis_result_phase4_fields_are_optional_and_canonical():
    result = AnalysisResult(
        analysis_id="analysis-1",
        analysis_mode="resume_only",
        status="completed",
        input={"resume_document_id": "document-1"},
        resume_profile=_profile(),
    )

    assert result.resume_quality is None
    assert result.ats_intelligence is None


def test_analysis_result_serializes_phase4_fields():
    quality = ResumeQualityResult(
        overall_score=84.0,
        confidence=_confidence(),
    )
    ats = ATSIntelligenceResult(
        overall_score=79.0,
        confidence=_confidence(),
    )

    result = AnalysisResult(
        analysis_id="analysis-1",
        analysis_mode="resume_only",
        status="completed",
        input={"resume_document_id": "document-1"},
        resume_profile=_profile(),
        resume_quality=quality,
        ats_intelligence=ats,
    )

    payload = result.model_dump()

    assert payload["resume_quality"]["overall_score"] == 84.0
    assert payload["ats_intelligence"]["overall_score"] == 79.0
    assert payload["resume_quality"]["confidence"]["score"] == 0.9
    assert payload["ats_intelligence"]["confidence"]["score"] == 0.9


def test_analysis_result_phase5_matching_is_optional_for_resume_only():

    result = AnalysisResult(

        analysis_id="analysis-1",

        analysis_mode="resume_only",

        status="completed",

        input={"resume_document_id": "document-1"},

        resume_profile=_profile(),

    )

    assert result.matching is None

    assert result.scoring is None

    assert result.xai is None


def test_analysis_result_can_carry_phase5_matching():

    matching = MatchingResult(

        skill_matches=[],

        requirement_alignments=[],

        confidence=_confidence(),

    )

    result = AnalysisResult(

        analysis_id="analysis-1",

        analysis_mode="resume_jd",

        status="completed",

        input={

            "resume_document_id": "document-1",

            "job_description_document_id": "job-1",

        },

        resume_profile=_profile(),

        matching=matching,

    )

    assert result.matching is matching

    assert result.scoring is None

    assert result.xai is None


def test_analysis_result_serializes_phase5_matching():

    matching = MatchingResult(

        skill_matches=[],

        requirement_alignments=[],

        confidence=_confidence(),

    )

    result = AnalysisResult(

        analysis_id="analysis-1",

        analysis_mode="resume_jd",

        status="completed",

        input={

            "resume_document_id": "document-1",

            "job_description_document_id": "job-1",

        },

        resume_profile=_profile(),

        matching=matching,

    )

    payload = result.model_dump()

    assert payload["matching"]["skill_matches"] == []

    assert payload["matching"]["requirement_alignments"] == []

    assert payload["matching"]["confidence"]["score"] == 0.9

    assert payload["scoring"] is None

    assert payload["xai"] is None
