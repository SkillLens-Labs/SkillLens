from pydantic import BaseModel, Field

from backend.app.domain.skill import Skill


class Education(BaseModel):
    """Structured education entry."""

    institution: str | None = None
    degree: str | None = None
    field_of_study: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None


class Experience(BaseModel):
    """Structured professional experience entry."""

    company: str | None = None
    role: str | None = None
    location: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None
    skills: list[Skill] = Field(default_factory=list)


class Project(BaseModel):
    """Structured project entry."""

    name: str
    description: str | None = None
    technologies: list[str] = Field(default_factory=list)
    start_date: str | None = None
    end_date: str | None = None


class Certification(BaseModel):
    """Structured certification entry."""

    name: str
    issuer: str | None = None
    issue_date: str | None = None
    expiry_date: str | None = None
    credential_id: str | None = None


class Contact(BaseModel):
    """Candidate contact information."""

    name: str | None = None
    email: str | None = None
    phone: str | None = None
    location: str | None = None
    linkedin: str | None = None
    github: str | None = None
    portfolio: str | None = None


class ResumeProfile(BaseModel):
    """Canonical structured representation of a resume."""

    profile_id: str
    document_id: str

    candidate_summary: str | None = None
    contact: Contact | None = None

    education: list[Education] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    certifications: list[Certification] = Field(default_factory=list)

    skills: list[Skill] = Field(default_factory=list)
    skill_categories: list[str] = Field(default_factory=list)

    total_experience: float | None = Field(default=None, ge=0.0)
    seniority: str | None = None
    domains: list[str] = Field(default_factory=list)

    metadata: dict[str, object] = Field(default_factory=dict)
