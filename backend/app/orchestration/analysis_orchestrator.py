from abc import ABC, abstractmethod

from backend.app.domain.analysis import AnalysisResult
from backend.app.schemas.requests import (
    ResumeAnalysisRequest,
    ResumeDocumentInput,
    JobDescriptionDocumentInput,
    ResumeJDAnalysisRequest,
)

class AnalysisOrchestrator(ABC):
    """Contract for the single SkillLens analysis orchestrator."""

    @abstractmethod
    def analyze_resume(
        self,
        document_input: ResumeDocumentInput,
        request: ResumeAnalysisRequest,
    ) -> AnalysisResult:
        """Run a resume-only analysis."""
        raise NotImplementedError

    @abstractmethod
    def analyze_resume_jd(
        self,
        resume_input: ResumeDocumentInput,
        job_description_input: JobDescriptionDocumentInput,
        request: ResumeJDAnalysisRequest,
    ) -> AnalysisResult:
        """Run a resume + job-description analysis."""
        raise NotImplementedError

    @abstractmethod
    def get_analysis(
        self,
        analysis_id: str,
    ) -> AnalysisResult | None:
        """Retrieve an existing analysis result."""
        raise NotImplementedError

    @abstractmethod
    def delete_analysis(
        self,
        analysis_id: str,
    ) -> bool:
        """Delete an existing analysis."""
        raise NotImplementedError
