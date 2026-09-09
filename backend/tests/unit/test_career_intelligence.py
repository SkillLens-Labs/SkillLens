from dataclasses import replace

from backend.app.analysis.career_catalog import (
    CAREER_TAXONOMY_VERSION,
    CAREER_ROLE_CATALOG,
    get_career_role,
)
from backend.app.analysis.career_intelligence import (
    ENGINE_VERSION,
    CareerIntelligenceAnalyzer,
)
from backend.app.domain.career import (
    CareerDirection,
    CareerSeniorityLevel,
)
from backend.app.domain.confidence import ConfidenceLevel
from backend.app.domain.evidence import Evidence, EvidenceSourceType
from backend.app.domain.resume import (
    Contact,
    Education,
    Experience,
    Project,
    ResumeProfile,
    Skill,
)
from backend.app.analysis.resume_structure import (
    ResumeSection,
    ResumeSectionType,
    StructuredResume,
)
from backend.app.infrastructure.parsers.models import (
    DocumentBlock,
    DocumentBlockType,
    SourceLocation,
)


def _skill(
    name: str,
    *,
    category: str | None = None,
    evidence_text: str | None = None,
    relevance: float = 0.95,
    confidence: float = 0.95,
) -> Skill:
    evidence = []

    if evidence_text is not None:
        evidence.append(
            Evidence(
                evidence_id=f"evidence-{name.replace(' ', '-')}",
                source_type=EvidenceSourceType.RESUME,
                source_document_id="resume-test",
                section="skills",
                text=evidence_text,
                evidence_type="skill_mention",
                extractor="test",
                relevance=relevance,
                confidence=confidence,
            )
        )

    return Skill(
        skill_id=f"skill-{name.replace(' ', '-')}",
        canonical_name=name,
        display_name=name,
        category=category,
        evidence=evidence,
    )


def _profile(
    skills: list[Skill],
    *,
    total_experience: float | None = None,
) -> ResumeProfile:
    return ResumeProfile(
        profile_id="profile-test",
        document_id="resume-test",
        candidate_summary="Software and data professional.",
        contact=Contact(),
        skills=skills,
        skill_categories=[],
        total_experience=total_experience,
    )


def _block(
    text: str,
    *,
    section: str = "experience",
    block_type: DocumentBlockType = DocumentBlockType.PARAGRAPH,
) -> DocumentBlock:
    return DocumentBlock(
        text=text,
        block_type=block_type,
        source=SourceLocation(block_index=0),
        section=section,
    )


def _structured(
    *texts: str,
    section: str = "experience",
) -> StructuredResume:
    return StructuredResume(
        document_id="resume-test",
        sections=(
            # ResumeSection is deliberately constructed through the public
            # StructuredResume contract in the analyzer-facing tests.
        ),
    )


def _analyze(
    *,
    skills: list[Skill],
    profile: ResumeProfile | None = None,
    blocks: list[DocumentBlock] | None = None,
):
    analyzer = CareerIntelligenceAnalyzer()

    structured_resume = StructuredResume(
        document_id="resume-test",
        sections=(),
    )

    if blocks:
        from backend.app.analysis.resume_structure import ResumeSection, ResumeSectionType

        structured_resume = StructuredResume(
            document_id="resume-test",
            sections=(
                ResumeSection(
                    section_type=ResumeSectionType.EXPERIENCE,
                    heading="Experience",
                    blocks=tuple(blocks),
                ),
            ),
        )

    return analyzer.analyze(
        resume_profile=profile or _profile(skills),
        structured_resume=structured_resume,
    )


def test_taxonomy_contract():
    assert CAREER_TAXONOMY_VERSION == "career-taxonomy-v1"
    assert len(CAREER_ROLE_CATALOG) == 15

    titles = [role.title for role in CAREER_ROLE_CATALOG]
    assert len(titles) == len(set(titles))

    for role in CAREER_ROLE_CATALOG:
        assert role.title
        assert role.aliases
        assert role.core_skills
        assert role.supporting_skills
        assert role.domain
        assert role.typical_seniority
        assert role.taxonomy_version == CAREER_TAXONOMY_VERSION
        assert get_career_role(role.title) == role


def test_engine_contract():
    assert ENGINE_VERSION == "phase7-career-intelligence-v1"


def test_role_lookup_is_case_insensitive():
    assert get_career_role("Software Developer") is not None
    assert get_career_role("SOFTWARE DEVELOPER") is not None


def test_role_lookup_supports_aliases():
    role = get_career_role("Software Engineer")
    assert role is not None
    assert role.title == "Software Developer"


def test_role_lookup_unknown_returns_none():
    assert get_career_role("Imaginary Career Role") is None


def test_role_fit_is_generalized_and_not_phase6_jd_score():
    skills = [
        _skill(
            "python",
            evidence_text="Python development in software projects.",
        ),
        _skill(
            "sql",
            evidence_text="SQL used for application data access.",
        ),
        _skill(
            "git",
            evidence_text="Git used for version control.",
        ),
    ]

    result = _analyze(skills=skills)

    software_role = next(
        item
        for item in result.role_fit
        if item.role == "Software Developer"
    )

    assert 0.0 <= software_role.fit_score <= 100.0
    assert software_role.fit_score > 0.0
    assert software_role.confidence.score >= 0.0
    assert software_role.confidence.score <= 1.0
    assert software_role.fit_score != software_role.confidence.score


def test_role_fit_uses_core_and_supporting_skill_coverage():
    core_only = _analyze(
        skills=[
            _skill("python", evidence_text="Python"),
            _skill("git", evidence_text="Git"),
        ]
    )

    stronger = _analyze(
        skills=[
            _skill("python", evidence_text="Python"),
            _skill("git", evidence_text="Git"),
            _skill("sql", evidence_text="SQL"),
            _skill("docker", evidence_text="Docker"),
        ]
    )

    core_score = next(
        item.fit_score
        for item in core_only.role_fit
        if item.role == "Software Developer"
    )
    stronger_score = next(
        item.fit_score
        for item in stronger.role_fit
        if item.role == "Software Developer"
    )

    assert stronger_score >= core_score


def test_evidence_is_preserved_on_role_fit():
    result = _analyze(
        skills=[
            _skill(
                "python",
                evidence_text="Built Python services.",
            ),
            _skill(
                "git",
                evidence_text="Used Git in production projects.",
            ),
        ]
    )

    role = next(
        item
        for item in result.career_directions
        if item.role == "Software Developer"
    )

    assert role.evidence
    assert all(
        evidence.source_type == EvidenceSourceType.RESUME
        for evidence in role.evidence
    )
    assert all(evidence.text for evidence in role.evidence)


def test_confidence_is_separate_and_has_components():
    result = _analyze(
        skills=[
            _skill(
                "python",
                evidence_text="Built Python services.",
            ),
        ]
    )

    role = next(
        item
        for item in result.career_directions
        if item.role == "Software Developer"
    )

    assert 0.0 <= role.confidence.score <= 1.0
    assert role.confidence.level in {
        ConfidenceLevel.LOW,
        ConfidenceLevel.MEDIUM,
        ConfidenceLevel.HIGH,
    }
    assert role.confidence.components


def test_seniority_from_total_experience():
    expectations = [
        (0.5, CareerSeniorityLevel.ENTRY),
        (2.0, CareerSeniorityLevel.JUNIOR),
        (5.0, CareerSeniorityLevel.MID),
        (8.0, CareerSeniorityLevel.SENIOR),
        (12.0, CareerSeniorityLevel.LEAD),
    ]

    for years, expected in expectations:
        result = _analyze(
            skills=[_skill("python", evidence_text="Python")],
            profile=_profile(
                [_skill("python", evidence_text="Python")],
                total_experience=years,
            ),
        )
        assert result.experience_level == expected


def test_seniority_unknown_without_reliable_evidence():
    result = _analyze(
        skills=[
            _skill(
                "python",
                evidence_text="Python development.",
            )
        ]
    )

    assert result.experience_level == CareerSeniorityLevel.UNKNOWN
    assert result.seniority_confidence.score < 0.65
    assert result.seniority_rationale


def test_seniority_explicit_role_title_is_used():
    result = _analyze(
        skills=[_skill("python", evidence_text="Python")],
        blocks=[
            _block(
                "Senior Software Engineer | Example Corp",
            )
        ],
    )

    assert result.experience_level == CareerSeniorityLevel.SENIOR
    assert result.seniority_evidence


def test_seniority_does_not_promote_generic_references():
    result = _analyze(
        skills=[_skill("python", evidence_text="Python")],
        blocks=[
            _block(
                "Worked with a senior engineer and engineering manager."
            )
        ],
    )

    assert result.experience_level == CareerSeniorityLevel.UNKNOWN


def test_domain_classification_uses_normalized_skills():
    result = _analyze(
        skills=[
            _skill("python", category="programming"),
            _skill("sql", category="database"),
            _skill("pandas", category="data"),
        ]
    )

    assert result.primary_domains
    assert "data_analytics" in result.primary_domains or \
        "data_science" in result.primary_domains


def test_domains_are_deterministically_ordered():
    skills = [
        _skill("python"),
        _skill("sql"),
        _skill("pandas"),
    ]

    first = _analyze(skills=skills)
    second = _analyze(skills=skills)

    assert first.primary_domains == second.primary_domains
    assert first.secondary_domains == second.secondary_domains


def test_career_directions_are_controlled():
    result = _analyze(
        skills=[
            _skill("python", evidence_text="Python"),
            _skill("sql", evidence_text="SQL"),
            _skill("git", evidence_text="Git"),
        ]
    )

    directions = {
        item.direction
        for item in result.career_directions
    }

    assert directions
    assert directions <= {
        CareerDirection.PRIMARY,
        CareerDirection.SECONDARY,
        CareerDirection.INSUFFICIENT_EVIDENCE,
    }


def test_primary_and_secondary_roles_are_not_empty_for_strong_evidence():
    result = _analyze(
        skills=[
            _skill("python", evidence_text="Python"),
            _skill("sql", evidence_text="SQL"),
            _skill("git", evidence_text="Git"),
            _skill("docker", evidence_text="Docker"),
        ]
    )

    assert result.potential_roles
    assert result.role_fit
    assert result.career_directions


def test_insufficient_evidence_is_explicit_for_sparse_resume():
    result = _analyze(
        skills=[]
    )

    assert result.career_directions

    assert any(
        item.direction == CareerDirection.INSUFFICIENT_EVIDENCE
        for item in result.career_directions
    ) or not result.role_fit


def test_transferable_skills_are_not_recommendations():
    result = _analyze(
        skills=[
            _skill("python", evidence_text="Python"),
            _skill("sql", evidence_text="SQL"),
            _skill("git", evidence_text="Git"),
        ]
    )

    assert all(isinstance(item, str) for item in result.transferable_skills)
    assert "learn python" not in [
        item.casefold() for item in result.transferable_skills
    ]


def test_strengths_are_evidence_backed():
    result = _analyze(
        skills=[
            _skill(
                "python",
                evidence_text="Built Python services.",
            ),
            _skill(
                "sql",
                evidence_text="Designed SQL queries.",
            ),
            _skill(
                "git",
                evidence_text="Used Git for source control.",
            ),
        ]
    )

    assert isinstance(result.strengths, list)
    assert all(isinstance(item, str) for item in result.strengths)


def test_limitations_are_evidence_limitations():
    result = _analyze(
        skills=[
            _skill(
                "python",
                evidence_text="Built Python services.",
            )
        ]
    )

    assert isinstance(result.limitations, list)

    for limitation in result.limitations:
        lowered = limitation.casefold()
        assert "cannot" not in lowered
        assert "unable" not in lowered
        assert "incapable" not in lowered


def test_resume_only_analysis_is_supported():
    result = _analyze(
        skills=[
            _skill(
                "python",
                evidence_text="Python development.",
            ),
            _skill(
                "git",
                evidence_text="Git version control.",
            ),
        ]
    )

    assert result.taxonomy_version == CAREER_TAXONOMY_VERSION
    assert result.engine_version == ENGINE_VERSION
    assert result.seniority_confidence
    assert result.confidence


def test_analysis_is_deterministic_for_same_input():
    skills = [
        _skill("python", evidence_text="Python"),
        _skill("sql", evidence_text="SQL"),
        _skill("git", evidence_text="Git"),
        _skill("docker", evidence_text="Docker"),
    ]

    first = _analyze(skills=skills)
    second = _analyze(skills=skills)

    assert first.model_dump() == second.model_dump()


def test_role_fit_order_is_deterministic():
    result = _analyze(
        skills=[
            _skill("python", evidence_text="Python"),
            _skill("sql", evidence_text="SQL"),
        ]
    )

    ordering = [
        (-item.fit_score, -item.confidence.score, item.role.casefold())
        for item in result.role_fit
    ]

    assert ordering == sorted(ordering)


def test_seniority_title_boundaries():
    analyzer = CareerIntelligenceAnalyzer()

    class Block:
        def __init__(self, text: str):
            self.text = text

    cases = [
        ("Lead Software Engineer | Company", CareerSeniorityLevel.LEAD),
        ("Senior Data Analyst | Company", CareerSeniorityLevel.SENIOR),
        ("Junior Developer: Company", CareerSeniorityLevel.JUNIOR),
        ("Worked with a senior engineer", CareerSeniorityLevel.UNKNOWN),
        ("Collaborated with an engineering manager", CareerSeniorityLevel.UNKNOWN),
    ]

    for text, expected in cases:
        actual = analyzer._seniority_from_experience_text(
            [Block(text)]
        )
        assert actual == expected


def test_jd_is_not_required_for_career_intelligence():
    result = _analyze(
        skills=[
            _skill(
                "python",
                evidence_text="Python development.",
            )
        ]
    )

    assert result is not None
    assert result.career_directions is not None
