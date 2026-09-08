from backend.app.domain.confidence import Confidence, ConfidenceLevel
from backend.app.domain.evidence import Evidence, EvidenceSourceType
from backend.app.domain.matching import (
    JobRequirement,
    JobRequirementCategory,
    JobRequirementType,
    MatchRelationship,
    MatchingResult,
    RequirementAlignment,
    RequirementMatchStatus,
    SkillMatch,
)


def _confidence() -> Confidence:
    return Confidence(
        score=0.9,
        level=ConfidenceLevel.HIGH,
        rationale="Strong structured evidence.",
    )


def _resume_evidence() -> Evidence:
    return Evidence(
        evidence_id="evidence-resume-1",
        source_type=EvidenceSourceType.RESUME,
        source_document_id="resume-1",
        section="Skills",
        text="Python",
        evidence_type="skill_mention",
        confidence=0.95,
    )


def _job_evidence() -> Evidence:
    return Evidence(
        evidence_id="evidence-job-1",
        source_type=EvidenceSourceType.JOB_DESCRIPTION,
        source_document_id="job-1",
        section="Requirements",
        text="Python",
        evidence_type="requirement_mention",
        confidence=0.95,
    )


def test_job_requirement_contract_supports_required_and_preferred() -> None:
    required = JobRequirement(
        requirement_id="requirement-1",
        text="Python",
        requirement_type=JobRequirementType.REQUIRED,
        category=JobRequirementCategory.SKILL,
        evidence=[_job_evidence()],
        confidence=_confidence(),
    )

    preferred = JobRequirement(
        requirement_id="requirement-2",
        text="Docker",
        requirement_type=JobRequirementType.PREFERRED,
        category=JobRequirementCategory.SKILL,
    )

    assert required.requirement_type == JobRequirementType.REQUIRED
    assert required.category == JobRequirementCategory.SKILL
    assert preferred.requirement_type == JobRequirementType.PREFERRED


def test_job_requirement_supports_non_skill_categories() -> None:
    categories = [
        JobRequirementCategory.EXPERIENCE,
        JobRequirementCategory.EDUCATION,
        JobRequirementCategory.CERTIFICATION,
    ]

    requirements = [
        JobRequirement(
            requirement_id=f"requirement-{index}",
            text=f"Requirement {index}",
            requirement_type=JobRequirementType.REQUIRED,
            category=category,
        )
        for index, category in enumerate(categories, start=1)
    ]

    assert [requirement.category for requirement in requirements] == categories


def test_requirement_alignment_preserves_unknown_state() -> None:
    alignment = RequirementAlignment(
        requirement_id="requirement-education-1",
        status=RequirementMatchStatus.UNKNOWN,
        evidence=[],
        confidence=None,
        rationale="No structured education evidence is available.",
    )

    assert alignment.status == RequirementMatchStatus.UNKNOWN
    assert alignment.evidence == []
    assert alignment.confidence is None


def test_requirement_alignment_supports_evidence_and_confidence() -> None:
    alignment = RequirementAlignment(
        requirement_id="requirement-python-1",
        status=RequirementMatchStatus.MATCHED,
        evidence=[_resume_evidence(), _job_evidence()],
        confidence=_confidence(),
        rationale="The resume contains explicit Python evidence.",
    )

    assert alignment.status == RequirementMatchStatus.MATCHED
    assert len(alignment.evidence) == 2
    assert alignment.confidence is not None
    assert alignment.confidence.score == 0.9


def test_skill_match_existing_contract_remains_usable() -> None:
    match = SkillMatch(
        resume_skill_id="skill:resume-1:python",
        job_skill_id="skill:job-1:python",
        relationship=MatchRelationship.EXACT,
        similarity=1.0,
        confidence=_confidence(),
        evidence=[_resume_evidence(), _job_evidence()],
        rationale="Canonical skill names match exactly.",
    )

    assert match.relationship == MatchRelationship.EXACT
    assert match.similarity == 1.0
    assert len(match.evidence) == 2


def test_skill_match_similarity_is_bounded() -> None:
    valid = SkillMatch(
        resume_skill_id="resume-python",
        job_skill_id="job-python",
        relationship=MatchRelationship.STRONG_SEMANTIC,
        similarity=0.87,
    )

    assert 0.0 <= valid.similarity <= 1.0


def test_matching_result_contains_matches_without_phase6_score() -> None:
    skill_match = SkillMatch(
        resume_skill_id="skill:resume-1:python",
        job_skill_id="skill:job-1:python",
        relationship=MatchRelationship.EXACT,
        similarity=1.0,
    )

    alignment = RequirementAlignment(
        requirement_id="requirement-1",
        status=RequirementMatchStatus.MATCHED,
    )

    result = MatchingResult(
        skill_matches=[skill_match],
        requirement_alignments=[alignment],
        confidence=_confidence(),
    )

    assert result.skill_matches == [skill_match]
    assert result.requirement_alignments == [alignment]
    assert result.confidence is not None

    payload = result.model_dump()
    assert "score" not in payload
    assert "overall_score" not in payload
    assert "xai" not in payload


def test_matching_result_serializes_canonical_nested_contracts() -> None:
    result = MatchingResult(
        skill_matches=[
            SkillMatch(
                resume_skill_id="resume-python",
                job_skill_id="job-python",
                relationship=MatchRelationship.EXACT,
                similarity=1.0,
            )
        ],
        requirement_alignments=[
            RequirementAlignment(
                requirement_id="requirement-python",
                status=RequirementMatchStatus.MATCHED,
            )
        ],
        confidence=_confidence(),
    )

    payload = result.model_dump()

    assert payload["skill_matches"][0]["relationship"] == "exact"
    assert payload["skill_matches"][0]["similarity"] == 1.0
    assert (
        payload["requirement_alignments"][0]["status"]
        == "matched"
    )
    assert payload["confidence"]["score"] == 0.9
