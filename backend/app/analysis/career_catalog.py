from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType

from backend.app.domain.career import CareerSeniorityLevel


CAREER_TAXONOMY_VERSION = "career-taxonomy-v1"


@dataclass(frozen=True)
class CareerRoleProfile:
    """Versioned deterministic profile for one generalized career role."""

    title: str
    aliases: tuple[str, ...]
    domain: str
    core_skills: tuple[str, ...]
    supporting_skills: tuple[str, ...]
    typical_seniority: tuple[CareerSeniorityLevel, ...]
    esco_uri: str | None = None
    taxonomy_version: str = CAREER_TAXONOMY_VERSION


def _role(
    title: str,
    aliases: tuple[str, ...],
    domain: str,
    core_skills: tuple[str, ...],
    supporting_skills: tuple[str, ...],
    typical_seniority: tuple[CareerSeniorityLevel, ...],
    esco_uri: str | None = None,
) -> CareerRoleProfile:
    return CareerRoleProfile(
        title=title,
        aliases=aliases,
        domain=domain,
        core_skills=core_skills,
        supporting_skills=supporting_skills,
        typical_seniority=typical_seniority,
        esco_uri=esco_uri,
    )


# The catalogue intentionally contains only skills that already exist in
# SkillLens' canonical SkillNormalizer vocabulary. No second skill vocabulary
# is introduced here.
CAREER_ROLE_CATALOG: tuple[CareerRoleProfile, ...] = (
    _role(
        "Software Developer",
        ("software engineer", "software developer"),
        "software_engineering",
        ("python", "java", "javascript"),
        ("git", "sql", "rest api", "docker"),
        (
            CareerSeniorityLevel.ENTRY,
            CareerSeniorityLevel.JUNIOR,
            CareerSeniorityLevel.MID,
            CareerSeniorityLevel.SENIOR,
            CareerSeniorityLevel.LEAD,
        ),
    ),
    _role(
        "Backend Developer",
        ("backend engineer", "backend developer"),
        "software_engineering",
        ("python", "java", "node.js", "rest api"),
        ("sql", "postgresql", "mysql", "docker", "git", "fastapi", "django", "flask"),
        (
            CareerSeniorityLevel.ENTRY,
            CareerSeniorityLevel.JUNIOR,
            CareerSeniorityLevel.MID,
            CareerSeniorityLevel.SENIOR,
            CareerSeniorityLevel.LEAD,
        ),
    ),
    _role(
        "Frontend Developer",
        ("frontend engineer", "front end developer", "frontend developer"),
        "software_engineering",
        ("javascript", "typescript", "react"),
        ("html", "css", "angular", "vue.js", "git"),
        (
            CareerSeniorityLevel.ENTRY,
            CareerSeniorityLevel.JUNIOR,
            CareerSeniorityLevel.MID,
            CareerSeniorityLevel.SENIOR,
            CareerSeniorityLevel.LEAD,
        ),
    ),
    _role(
        "Full Stack Developer",
        ("full-stack developer", "full stack engineer", "fullstack developer"),
        "software_engineering",
        ("javascript", "react", "node.js", "rest api"),
        ("typescript", "html", "css", "sql", "python", "docker", "git"),
        (
            CareerSeniorityLevel.ENTRY,
            CareerSeniorityLevel.JUNIOR,
            CareerSeniorityLevel.MID,
            CareerSeniorityLevel.SENIOR,
            CareerSeniorityLevel.LEAD,
        ),
    ),
    _role(
        "Data Analyst",
        ("data analyst", "business data analyst"),
        "data_analytics",
        ("sql", "data analysis", "excel"),
        ("python", "pandas", "numpy", "statistics", "power bi", "tableau"),
        (
            CareerSeniorityLevel.ENTRY,
            CareerSeniorityLevel.JUNIOR,
            CareerSeniorityLevel.MID,
            CareerSeniorityLevel.SENIOR,
        ),
    ),
    _role(
        "Data Scientist",
        ("data scientist", "data science specialist"),
        "data_science",
        ("python", "data science", "statistics", "machine learning"),
        ("pandas", "numpy", "scikit-learn", "sql", "xgboost", "tensorflow", "pytorch"),
        (
            CareerSeniorityLevel.ENTRY,
            CareerSeniorityLevel.JUNIOR,
            CareerSeniorityLevel.MID,
            CareerSeniorityLevel.SENIOR,
            CareerSeniorityLevel.LEAD,
        ),
    ),
    _role(
        "Machine Learning Engineer",
        ("ml engineer", "machine learning engineer"),
        "machine_learning",
        ("python", "machine learning", "scikit-learn"),
        ("pytorch", "tensorflow", "xgboost", "numpy", "pandas", "docker", "kubernetes"),
        (
            CareerSeniorityLevel.ENTRY,
            CareerSeniorityLevel.JUNIOR,
            CareerSeniorityLevel.MID,
            CareerSeniorityLevel.SENIOR,
            CareerSeniorityLevel.LEAD,
        ),
    ),
    _role(
        "AI Engineer",
        ("artificial intelligence engineer", "ai engineer"),
        "artificial_intelligence",
        ("python", "machine learning", "deep learning"),
        (
            "pytorch",
            "tensorflow",
            "natural language processing",
            "transformers",
            "hugging face",
            "docker",
        ),
        (
            CareerSeniorityLevel.ENTRY,
            CareerSeniorityLevel.JUNIOR,
            CareerSeniorityLevel.MID,
            CareerSeniorityLevel.SENIOR,
            CareerSeniorityLevel.LEAD,
        ),
    ),
    _role(
        "Data Engineer",
        ("data engineer", "data platform engineer"),
        "data_engineering",
        ("python", "sql"),
        ("pandas", "postgresql", "mysql", "mongodb", "docker", "kubernetes", "aws"),
        (
            CareerSeniorityLevel.ENTRY,
            CareerSeniorityLevel.JUNIOR,
            CareerSeniorityLevel.MID,
            CareerSeniorityLevel.SENIOR,
            CareerSeniorityLevel.LEAD,
        ),
    ),
    _role(
        "DevOps Engineer",
        ("devops engineer", "devops specialist"),
        "devops",
        ("docker", "kubernetes", "linux", "git"),
        ("aws", "azure", "gcp", "redis", "python"),
        (
            CareerSeniorityLevel.JUNIOR,
            CareerSeniorityLevel.MID,
            CareerSeniorityLevel.SENIOR,
            CareerSeniorityLevel.LEAD,
        ),
    ),
    _role(
        "Cloud Engineer",
        ("cloud engineer", "cloud infrastructure engineer"),
        "cloud_engineering",
        ("aws", "azure", "gcp", "linux"),
        ("docker", "kubernetes", "python", "git"),
        (
            CareerSeniorityLevel.JUNIOR,
            CareerSeniorityLevel.MID,
            CareerSeniorityLevel.SENIOR,
            CareerSeniorityLevel.LEAD,
        ),
    ),
    _role(
        "QA / Test Engineer",
        ("qa engineer", "test engineer", "quality assurance engineer"),
        "quality_engineering",
        ("python", "java"),
        ("javascript", "git", "sql", "rest api"),
        (
            CareerSeniorityLevel.ENTRY,
            CareerSeniorityLevel.JUNIOR,
            CareerSeniorityLevel.MID,
            CareerSeniorityLevel.SENIOR,
            CareerSeniorityLevel.LEAD,
        ),
    ),
    _role(
        "Database Developer",
        ("database developer", "database engineer"),
        "data_engineering",
        ("sql", "postgresql", "mysql"),
        ("mongodb", "nosql", "python", "redis"),
        (
            CareerSeniorityLevel.ENTRY,
            CareerSeniorityLevel.JUNIOR,
            CareerSeniorityLevel.MID,
            CareerSeniorityLevel.SENIOR,
            CareerSeniorityLevel.LEAD,
        ),
    ),
    _role(
        "Cybersecurity Analyst",
        ("security analyst", "cybersecurity analyst"),
        "cybersecurity",
        ("linux", "python"),
        ("sql", "git", "aws", "azure", "gcp"),
        (
            CareerSeniorityLevel.ENTRY,
            CareerSeniorityLevel.JUNIOR,
            CareerSeniorityLevel.MID,
            CareerSeniorityLevel.SENIOR,
        ),
    ),
    _role(
        "Business Analyst",
        ("business analyst", "data business analyst"),
        "business_analysis",
        ("data analysis", "excel", "sql"),
        ("power bi", "tableau", "statistics"),
        (
            CareerSeniorityLevel.ENTRY,
            CareerSeniorityLevel.JUNIOR,
            CareerSeniorityLevel.MID,
            CareerSeniorityLevel.SENIOR,
        ),
    ),
)


CAREER_ROLE_CATALOG_BY_TITLE = MappingProxyType(
    {role.title: role for role in CAREER_ROLE_CATALOG}
)


def get_career_role_catalog() -> tuple[CareerRoleProfile, ...]:
    """Return the immutable ordered career-role catalogue."""

    return CAREER_ROLE_CATALOG


def get_career_role(title: str) -> CareerRoleProfile | None:
    """Return a role by canonical title or alias, case-insensitively."""

    normalized = title.strip().casefold()

    for role in CAREER_ROLE_CATALOG:
        if role.title.casefold() == normalized:
            return role

        if normalized in {alias.casefold() for alias in role.aliases}:
            return role

    return None
