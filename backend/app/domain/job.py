from pydantic import BaseModel, Field


class ExperienceRequirements(BaseModel):
    """Structured experience requirements for a job."""

    minimum_years: float | None = Field(default=None, ge=0.0)
    maximum_years: float | None = Field(default=None, ge=0.0)
    description: str | None = None


class EducationRequirements(BaseModel):
    """Structured education requirements for a job."""

    degrees: list[str] = Field(default_factory=list)
    fields_of_study: list[str] = Field(default_factory=list)
    description: str | None = None


class JobProfile(BaseModel):
    """Canonical structured representation of a job description."""

    profile_id: str
    document_id: str

    job_title: str
    company: str | None = None
    summary: str | None = None

    responsibilities: list[str] = Field(default_factory=list)

    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)

    technical_skills: list[str] = Field(default_factory=list)
    soft_skills: list[str] = Field(default_factory=list)
    domain_skills: list[str] = Field(default_factory=list)

    experience_requirements: ExperienceRequirements | None = None
    education_requirements: EducationRequirements | None = None

    seniority: str | None = None

    metadata: dict[str, object] = Field(default_factory=dict)
