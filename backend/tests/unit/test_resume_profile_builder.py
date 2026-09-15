from backend.app.analysis.esco_mapper import ESCOMapper
from backend.app.analysis.resume_profile_builder import ResumeProfileBuilder
from backend.app.analysis.resume_structure import (
    ResumeSection,
    ResumeSectionType,
    StructuredResume,
)
from backend.app.analysis.skill_extractor import (
    SkillEvidenceType,
    SkillMention,
)
from backend.app.analysis.skill_normalizer import SkillNormalizer
from backend.app.domain.confidence import ConfidenceLevel
from backend.app.infrastructure.parsers.models import (
    DocumentBlock,
    DocumentBlockType,
    SourceLocation,
)


def _block(text: str, index: int = 0) -> DocumentBlock:
    return DocumentBlock(
        block_type=DocumentBlockType.PARAGRAPH,
        text=text,
        source=SourceLocation(
            page_number=1,
            block_index=index,
        ),
    )


def _mention(
    *,
    raw_text: str,
    section_type: ResumeSectionType,
    block: DocumentBlock,
    confidence: float = 0.95,
) -> SkillMention:
    start = block.text.lower().index(raw_text.lower())

    return SkillMention(
        raw_text=raw_text,
        section_type=section_type,
        evidence_type=SkillEvidenceType.EXPLICIT,
        block=block,
        start_offset=start,
        end_offset=start + len(raw_text),
        extractor="test_extractor",
        confidence=confidence,
    )


def _resume(*sections: ResumeSection) -> StructuredResume:
    return StructuredResume(
        document_id="doc-123",
        sections=sections,
    )


def test_builds_canonical_resume_profile():
    block = _block("Python, Docker", 0)

    resume = _resume(
        ResumeSection(
            section_type=ResumeSectionType.SKILLS,
            heading="Skills",
            blocks=(block,),
        )
    )

    mentions = (
        _mention(
            raw_text="Python",
            section_type=ResumeSectionType.SKILLS,
            block=block,
        ),
        _mention(
            raw_text="Docker",
            section_type=ResumeSectionType.SKILLS,
            block=block,
        ),
    )

    normalized = SkillNormalizer().normalize_many(mentions)
    mapped = ESCOMapper().map_many(normalized)

    profile = ResumeProfileBuilder().build(resume, normalized, mapped)

    assert profile.document_id == "doc-123"
    assert profile.profile_id.startswith("resume_")
    assert len(profile.skills) == 2
    assert profile.skills[0].canonical_name == "python"
    assert profile.skills[1].canonical_name == "docker"


def test_preserves_summary_without_inventing_other_resume_facts():
    block = _block("Data analyst with Python experience.", 0)

    resume = _resume(
        ResumeSection(
            section_type=ResumeSectionType.SUMMARY,
            heading="Summary",
            blocks=(block,),
        )
    )

    profile = ResumeProfileBuilder().build(resume, [], [])

    assert profile.candidate_summary == block.text
    assert profile.education == []
    assert profile.experience == []
    assert profile.projects == []
    assert profile.certifications == []
    assert profile.total_experience is None
    assert profile.seniority is None
    assert profile.domains == []


def test_creates_evidence_with_resume_provenance():
    block = _block("Python", 0)

    resume = _resume(
        ResumeSection(
            section_type=ResumeSectionType.SKILLS,
            heading="Skills",
            blocks=(block,),
        )
    )

    mention = _mention(
        raw_text="Python",
        section_type=ResumeSectionType.SKILLS,
        block=block,
    )

    normalized = SkillNormalizer().normalize(mention)
    mapped = ESCOMapper().map(normalized)

    profile = ResumeProfileBuilder().build(resume, [normalized], [mapped])

    evidence = profile.skills[0].evidence[0]

    assert evidence.source_document_id == "doc-123"
    assert evidence.source_type.value == "resume"
    assert evidence.section == "skills"
    assert evidence.text == "Python"
    assert evidence.start_offset == 0
    assert evidence.end_offset == 6
    assert evidence.evidence_type == "explicit"
    assert evidence.extractor == "test_extractor"


def test_creates_confidence_from_extraction_and_mapping():
    block = _block("Python", 0)

    resume = _resume(
        ResumeSection(
            section_type=ResumeSectionType.SKILLS,
            heading="Skills",
            blocks=(block,),
        )
    )

    mention = _mention(
        raw_text="Python",
        section_type=ResumeSectionType.SKILLS,
        block=block,
        confidence=0.95,
    )

    normalized = SkillNormalizer().normalize(mention)
    mapped = ESCOMapper().map(normalized)

    profile = ResumeProfileBuilder().build(resume, [normalized], [mapped])

    confidence = profile.skills[0].confidence

    assert confidence is not None
    assert confidence.score == 0.97
    assert confidence.level == ConfidenceLevel.HIGH
    assert confidence.components["extraction"] == 0.95
    assert confidence.components["esco_mapping"] == 0.99


def test_deduplicates_same_canonical_skill_and_merges_evidence():
    first = _block("Python", 0)
    second = _block("Python", 1)

    resume = _resume(
        ResumeSection(
            section_type=ResumeSectionType.SKILLS,
            heading="Skills",
            blocks=(first, second),
        )
    )

    mentions = (
        _mention(
            raw_text="Python",
            section_type=ResumeSectionType.SKILLS,
            block=first,
        ),
        _mention(
            raw_text="Python",
            section_type=ResumeSectionType.SKILLS,
            block=second,
        ),
    )

    normalized = SkillNormalizer().normalize_many(mentions)
    mapped = ESCOMapper().map_many(normalized)

    profile = ResumeProfileBuilder().build(resume, normalized, mapped)

    assert len(profile.skills) == 1
    assert len(profile.skills[0].evidence) == 2


def test_skill_categories_are_derived_deterministically():
    first = _block("Python", 0)
    second = _block("Docker", 1)

    resume = _resume(
        ResumeSection(
            section_type=ResumeSectionType.SKILLS,
            heading="Skills",
            blocks=(first, second),
        )
    )

    mentions = (
        _mention(
            raw_text="Python",
            section_type=ResumeSectionType.SKILLS,
            block=first,
        ),
        _mention(
            raw_text="Docker",
            section_type=ResumeSectionType.SKILLS,
            block=second,
        ),
    )

    normalized = SkillNormalizer().normalize_many(mentions)
    mapped = ESCOMapper().map_many(normalized)

    profile = ResumeProfileBuilder().build(resume, normalized, mapped)

    assert profile.skill_categories == ["cloud_devops", "programming"]


def test_unmapped_skill_does_not_receive_fabricated_esco_uri():
    block = _block("FastAPI", 0)

    resume = _resume(
        ResumeSection(
            section_type=ResumeSectionType.SKILLS,
            heading="Skills",
            blocks=(block,),
        )
    )

    mention = _mention(
        raw_text="FastAPI",
        section_type=ResumeSectionType.SKILLS,
        block=block,
    )

    normalized = SkillNormalizer().normalize(mention)
    mapped = ESCOMapper().map(normalized)

    profile = ResumeProfileBuilder().build(resume, [normalized], [mapped])

    skill = profile.skills[0]

    assert mapped.status.value == "unmapped"
    assert "esco_uri" not in skill.metadata
    assert skill.confidence is not None
    assert skill.confidence.level == ConfidenceLevel.MEDIUM


def test_rejects_mismatched_skill_and_mapping_lengths():
    resume = _resume()

    try:
        ResumeProfileBuilder().build(
            resume,
            [],
            [
                ESCOMapper().map(
                    SkillNormalizer().normalize(
                        _mention(
                            raw_text="Python",
                            section_type=ResumeSectionType.SKILLS,
                            block=_block("Python"),
                        )
                    )
                )
            ],
        )
    except ValueError as exc:
        assert "same number" in str(exc)
    else:
        raise AssertionError("Expected ValueError")



def test_extracts_structured_education_entry() -> None:
    degree_block = _block(
        "Bachelor of Engineering – Computer Science",
        0,
    )
    institution_block = _block(
        "Prof. Ram Meghe College of Engineering & Management, SGBAU",
        1,
    )
    date_block = _block(
        "Aug 2023 - May 2027",
        2,
    )

    resume = _resume(
        ResumeSection(
            section_type=ResumeSectionType.EDUCATION,
            heading="Education",
            blocks=(degree_block, institution_block, date_block),
        )
    )

    profile = ResumeProfileBuilder().build(resume, [], [])

    assert len(profile.education) == 1

    education = profile.education[0]

    assert education.degree == "Bachelor of Engineering"
    assert education.field_of_study == "Computer Science"
    assert education.institution.startswith(
        "Prof. Ram Meghe College"
    )
    assert education.start_date == "Aug 2023"
    assert education.end_date == "May 2027"


def test_extracts_multiple_projects_with_exposure_and_description() -> None:
    blocks = (
        _block(
            "DataBridge – End-to-End Data Intelligence Pipeline",
            0,
        ),
        _block("[GitHub Repo]", 1),
        _block(
            "Exposure: Python, FastAPI, React, Pandas, SQL, Docker",
            2,
        ),
        _block(
            "Built an end-to-end data intelligence pipeline.",
            3,
        ),
        _block(
            "TradeBook – High-Performance Order Matching Engine",
            4,
        ),
        _block("[GitHub Repo]", 5),
        _block(
            "Exposure: C++, STL, OOP, Data Structures, Algorithms",
            6,
        ),
        _block(
            "Implemented a high-performance matching engine.",
            7,
        ),
    )

    resume = _resume(
        ResumeSection(
            section_type=ResumeSectionType.PROJECTS,
            heading="Selected Works",
            blocks=blocks,
        )
    )

    profile = ResumeProfileBuilder().build(resume, [], [])

    assert len(profile.projects) == 2

    first = profile.projects[0]

    assert first.name == (
        "DataBridge – End-to-End Data Intelligence Pipeline"
    )
    assert first.technologies == [
        "Python",
        "FastAPI",
        "React",
        "Pandas",
        "SQL",
        "Docker",
    ]
    assert "end-to-end data intelligence pipeline" in (
        first.description or ""
    )
    assert "[GitHub Repo]" not in (first.description or "")

    second = profile.projects[1]

    assert second.name == (
        "TradeBook – High-Performance Order Matching Engine"
    )
    assert second.technologies == [
        "C++",
        "STL",
        "OOP",
        "Data Structures",
        "Algorithms",
    ]
    assert "[GitHub Repo]" not in (second.description or "")

def test_does_not_treat_short_description_fragments_as_project_titles() -> None:
    blocks = (
        _block(
            "Example Project – Data Intelligence Platform",
            0,
        ),
        _block(
            "Exposure: Python, FastAPI, Pandas, SQL",
            1,
        ),
        _block(
            "Designed a shared-state pipeline coordinating 12 analysis modules",
            2,
        ),
        _block(
            "Implemented parallel response processing with Python workers",
            3,
        ),
        _block(
            "Developed a web application for batch submission and tracking",
            4,
        ),
        _block(
            "Another Project – Order Matching Engine",
            5,
        ),
        _block(
            "Exposure: C++, STL, OOP, Algorithms",
            6,
        ),
        _block(
            "Built a high-performance order matching engine",
            7,
        ),
    )

    resume = _resume(
        ResumeSection(
            section_type=ResumeSectionType.PROJECTS,
            heading="Selected Works",
            blocks=blocks,
        )
    )

    profile = ResumeProfileBuilder().build(resume, [], [])

    assert len(profile.projects) == 2

    first = profile.projects[0]

    assert first.name == "Example Project – Data Intelligence Platform"
    assert first.technologies == [
        "Python",
        "FastAPI",
        "Pandas",
        "SQL",
    ]
    assert first.description is not None
    assert "Designed a shared-state pipeline" in first.description
    assert "Implemented parallel response processing" in first.description
    assert "Developed a web application" in first.description

    second = profile.projects[1]

    assert second.name == "Another Project – Order Matching Engine"
    assert second.technologies == [
        "C++",
        "STL",
        "OOP",
        "Algorithms",
    ]
    assert "Built a high-performance order matching engine" in (
        second.description or ""
    )

def test_does_not_fabricate_absent_resume_sections() -> None:
    blocks = (
        _block(
            "Bachelor of Engineering – Computer Science",
            0,
        ),
        _block("Example University", 1),
    )

    resume = _resume(
        ResumeSection(
            section_type=ResumeSectionType.EDUCATION,
            heading="Education",
            blocks=blocks,
        )
    )

    profile = ResumeProfileBuilder().build(resume, [], [])

    assert profile.education
    assert profile.experience == []
    assert profile.projects == []
    assert profile.certifications == []
    assert profile.total_experience is None
    assert profile.seniority is None


def test_builder_is_deterministic_for_structured_entries() -> None:
    education_blocks = (
        _block(
            "Bachelor of Engineering – Computer Science",
            0,
        ),
        _block("Example University", 1),
        _block("Aug 2023 - May 2027", 2),
    )

    project_blocks = (
        _block(
            "DataBridge – Data Intelligence Pipeline",
            3,
        ),
        _block("Exposure: Python, SQL", 4),
        _block("Built a data pipeline.", 5),
    )

    resume = _resume(
        ResumeSection(
            section_type=ResumeSectionType.EDUCATION,
            heading="Education",
            blocks=education_blocks,
        ),
        ResumeSection(
            section_type=ResumeSectionType.PROJECTS,
            heading="Projects",
            blocks=project_blocks,
        ),
    )

    builder = ResumeProfileBuilder()

    first = builder.build(resume, [], [])
    second = builder.build(resume, [], [])

    assert first.model_dump() == second.model_dump()


def test_extracts_education_from_combined_degree_institution_block():
    blocks = [
        DocumentBlock(
            text=(
                "Bachelor of Engineering – Computer Science\n"
                "Prof. Ram Meghe College of Engineering & Management, "
                "SGBAU, Amravati, Maharashtra"
            ),
            block_type=DocumentBlockType.PARAGRAPH,
            source=SourceLocation(block_index=0),
        ),
        DocumentBlock(
            text="Aug 2023 - May 2027",
            block_type=DocumentBlockType.PARAGRAPH,
            source=SourceLocation(block_index=1),
        ),
        DocumentBlock(
            text=(
                "Average SGPA: 7.53/10 (67.61%)\n"
                "Leadership: Final-Year Capstone Project Leader, "
                "responsible for project planning, architecture, and "
                "technical coordination."
            ),
            block_type=DocumentBlockType.PARAGRAPH,
            source=SourceLocation(block_index=2),
        ),
    ]

    resume = _resume(
        ResumeSection(
            section_type=ResumeSectionType.EDUCATION,
            heading="EDUCATION",
            blocks=blocks,
        )
    )

    profile = ResumeProfileBuilder().build(
        resume,
        normalized_skills=[],
        esco_results=[],
    )

    assert len(profile.education) == 1

    education = profile.education[0]

    assert education.degree == "Bachelor of Engineering"
    assert education.field_of_study == "Computer Science"
    assert (
        education.institution
        == "Prof. Ram Meghe College of Engineering & Management, "
        "SGBAU, Amravati, Maharashtra"
    )
    assert education.start_date == "Aug 2023"
    assert education.end_date == "May 2027"
    assert education.description is not None
    assert "Average SGPA: 7.53/10" in education.description
    assert "Final-Year Capstone Project Leader" in education.description


def test_extracts_contact_fields_from_header() -> None:
    header = _block(
        "RAGHUVIR V. ANTURKAR\n"
        "raghuanturkar8@gmail.com | +91 74473 29517\n"
        "LinkedIn | GitHub | Portfolio | Chandrapur, Maharashtra",
        0,
    )

    resume = _resume(
        ResumeSection(
            section_type=ResumeSectionType.HEADER,
            heading=None,
            blocks=(header,),
        )
    )

    profile = ResumeProfileBuilder().build(resume, [], [])

    assert profile.contact is not None
    assert profile.contact.name == "RAGHUVIR V. ANTURKAR"
    assert profile.contact.email == "raghuanturkar8@gmail.com"
    assert profile.contact.phone == "+91 74473 29517"
    assert profile.contact.location == "Chandrapur, Maharashtra"
    assert profile.contact.linkedin is None
    assert profile.contact.github is None
    assert profile.contact.portfolio is None


def test_extracts_profile_urls_from_header() -> None:
    header = _block(
        "Jane Doe\n"
        "jane@example.com | +1 555 123 4567\n"
        "https://linkedin.com/in/janedoe | "
        "https://github.com/janedoe | "
        "https://janedoe.dev | Austin, Texas",
        0,
    )

    resume = _resume(
        ResumeSection(
            section_type=ResumeSectionType.HEADER,
            heading=None,
            blocks=(header,),
        )
    )

    profile = ResumeProfileBuilder().build(resume, [], [])

    assert profile.contact is not None
    assert profile.contact.name == "Jane Doe"
    assert profile.contact.email == "jane@example.com"
    assert profile.contact.phone == "+1 555 123 4567"
    assert profile.contact.location == "Austin, Texas"
    assert profile.contact.linkedin == "https://linkedin.com/in/janedoe"
    assert profile.contact.github == "https://github.com/janedoe"
    assert profile.contact.portfolio == "https://janedoe.dev"


def test_contact_extraction_preserves_missing_fields_as_none() -> None:
    header = _block(
        "Jane Doe\n"
        "jane@example.com",
        0,
    )

    resume = _resume(
        ResumeSection(
            section_type=ResumeSectionType.HEADER,
            heading=None,
            blocks=(header,),
        )
    )

    profile = ResumeProfileBuilder().build(resume, [], [])

    assert profile.contact is not None
    assert profile.contact.name == "Jane Doe"
    assert profile.contact.email == "jane@example.com"
    assert profile.contact.phone is None
    assert profile.contact.location is None
    assert profile.contact.linkedin is None
    assert profile.contact.github is None
    assert profile.contact.portfolio is None


def test_returns_no_contact_when_header_contains_no_contact_data() -> None:
    header = _block(
        "A short header without contact metadata.",
        0,
    )

    resume = _resume(
        ResumeSection(
            section_type=ResumeSectionType.HEADER,
            heading=None,
            blocks=(header,),
        )
    )

    profile = ResumeProfileBuilder().build(resume, [], [])

    assert profile.contact is None


def test_contact_extraction_is_deterministic() -> None:
    header = _block(
        "Jane Doe\n"
        "jane@example.com | +1 555 123 4567\n"
        "https://linkedin.com/in/janedoe | Austin, Texas",
        0,
    )

    resume = _resume(
        ResumeSection(
            section_type=ResumeSectionType.HEADER,
            heading=None,
            blocks=(header,),
        )
    )

    builder = ResumeProfileBuilder()

    first = builder.build(resume, [], [])
    second = builder.build(resume, [], [])

    assert first.contact == second.contact
