from backend.app.domain.analysis import (
    AnalysisInput,
    AnalysisMode,
    AnalysisResult,
    AnalysisStatus,
)
from backend.app.domain.confidence import Confidence, ConfidenceLevel
from backend.app.domain.evidence import Evidence, EvidenceSourceType
from backend.app.domain.gaps import SkillAnalysis
from backend.app.domain.resume import ResumeProfile
from backend.app.schemas.errors import ErrorResponse


def make_resume_profile() -> ResumeProfile:
    return ResumeProfile(
        profile_id="profile-1",
        document_id="document-1",
    )


def test_confidence_contract() -> None:
    confidence = Confidence(
        score=0.85,
        level=ConfidenceLevel.HIGH,
        components={"evidence_strength": 0.9},
        rationale="Strong evidence.",
    )

    assert confidence.score == 0.85
    assert confidence.level == ConfidenceLevel.HIGH


def test_evidence_contract() -> None:
    evidence = Evidence(
        evidence_id="evidence-1",
        source_type=EvidenceSourceType.RESUME,
        source_document_id="document-1",
        text="Python and FastAPI",
        evidence_type="skill_mention",
    )

    assert evidence.source_type == EvidenceSourceType.RESUME
    assert evidence.text == "Python and FastAPI"


def test_analysis_result_resume_only_contract() -> None:
    result = AnalysisResult(
        analysis_id="analysis-1",
        analysis_mode=AnalysisMode.RESUME_ONLY,
        status=AnalysisStatus.COMPLETED,
        input=AnalysisInput(
            resume_document_id="document-1",
        ),
        resume_profile=make_resume_profile(),
        skill_analysis=SkillAnalysis(),
    )

    assert result.analysis_mode == AnalysisMode.RESUME_ONLY
    assert result.job_profile is None
    assert result.scoring is None
    assert result.xai is None
    assert result.career_intelligence is None
    assert result.recommendations == []


def test_error_response_contract() -> None:
    error = ErrorResponse(
        code="TEST_ERROR",
        message="Test error",
        details=None,
        field=None,
        request_id="request-1",
    )

    assert error.code == "TEST_ERROR"
    assert error.request_id == "request-1"
