from __future__ import annotations

from backend.app.analysis.gaps import GapAnalyzer
from backend.app.domain.confidence import Confidence, ConfidenceLevel
from backend.app.domain.evidence import Evidence, EvidenceSourceType
from backend.app.domain.gaps import SkillAnalysis
from backend.app.domain.job import JobProfile
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
from backend.app.domain.skill import Skill


def _confidence(score: float = 0.90) -> Confidence:
    return Confidence(
        score=score,
        level=(
            ConfidenceLevel.HIGH
            if score >= 0.85
            else ConfidenceLevel.MEDIUM
        ),
    )


def _evidence(
    evidence_id: str,
    text: str,
    source_type: EvidenceSourceType = EvidenceSourceType.JOB_DESCRIPTION,
) -> Evidence:
    return Evidence(
        evidence_id=evidence_id,
        source_type=source_type,
        source_document_id=(
            "job-1"
            if source_type == EvidenceSourceType.JOB_DESCRIPTION
            else "resume-1"
        ),
        section="Skills",
        text=text,
        evidence_type="skill_mention",
        confidence=0.90,
    )


def _requirement(
    requirement_id: str,
    text: str,
    *,
    requirement_type: JobRequirementType = JobRequirementType.REQUIRED,
    skill_id: str | None = None,
    canonical_name: str | None = None,
) -> JobRequirement:
    return JobRequirement(
        requirement_id=requirement_id,
        text=text,
        requirement_type=requirement_type,
        category=JobRequirementCategory.SKILL,
        skill_id=skill_id,
        canonical_name=canonical_name,
        evidence=[_evidence(f"job-{requirement_id}", text)],
        confidence=_confidence(),
    )


def _alignment(
    requirement_id: str,
    status: RequirementMatchStatus,
    *,
    evidence: list[Evidence] | None = None,
    confidence: float = 0.90,
    rationale: str = "phase5-alignment",
) -> RequirementAlignment:
    return RequirementAlignment(
        requirement_id=requirement_id,
        status=status,
        evidence=evidence or [],
        confidence=_confidence(confidence),
        rationale=rationale,
    )


def _skill(
    skill_id: str,
    name: str,
    *,
    evidence: list[Evidence] | None = None,
) -> Skill:
    return Skill(
        skill_id=skill_id,
        canonical_name=name,
        display_name=name,
        evidence=evidence or [],
        confidence=_confidence(),
    )


def _matching(
    *,
    alignments: list[RequirementAlignment],
    skill_matches: list[SkillMatch] | None = None,
) -> MatchingResult:
    return MatchingResult(
        requirement_alignments=alignments,
        skill_matches=skill_matches or [],
        confidence=_confidence(),
    )


def _job_profile() -> JobProfile:
    return JobProfile(
        profile_id="job-profile-1",
        document_id="job-1",
        job_title="Data Engineer",
    )


def test_matched_skill_is_not_reported_as_a_gap() -> None:
    job_skill = _skill("job-python", "Python")
    resume_skill = _skill("resume-python", "Python")

    requirement = _requirement(
        "req-python",
        "Python",
        skill_id=job_skill.skill_id,
        canonical_name="Python",
    )

    match = SkillMatch(
        resume_skill_id=resume_skill.skill_id,
        job_skill_id=job_skill.skill_id,
        relationship=MatchRelationship.EXACT,
        similarity=1.0,
        confidence=_confidence(),
        evidence=[
            *resume_skill.evidence,
            _evidence(
                "job-python-evidence",
                "Python",
            ),
        ],
    )

    matching = _matching(
        alignments=[
            _alignment(
                "req-python",
                RequirementMatchStatus.MATCHED,
            )
        ],
        skill_matches=[match],
    )

    result = GapAnalyzer().analyze(
        requirements=[requirement],
        matching=matching,
        resume_skills=[resume_skill],
        job_skills=[job_skill],
    )

    assert result.matched_skills == ["Python"]
    assert result.gaps == []
    assert result.partial_matches == []
    assert result.missing_skills == []


def test_partial_skill_creates_partial_gap() -> None:
    job_skill = _skill("job-python", "Python")

    requirement = _requirement(
        "req-python",
        "Python",
        skill_id=job_skill.skill_id,
        canonical_name="Python",
    )

    match = SkillMatch(
        resume_skill_id="resume-python",
        job_skill_id=job_skill.skill_id,
        relationship=MatchRelationship.PARTIAL,
        similarity=0.70,
        confidence=_confidence(0.80),
        evidence=[_evidence("match-python", "Python")],
    )

    matching = _matching(
        alignments=[
            _alignment(
                "req-python",
                RequirementMatchStatus.PARTIAL,
                evidence=[
                    _evidence("alignment-python", "Python alignment")
                ],
            )
        ],
        skill_matches=[match],
    )

    result = GapAnalyzer().analyze(
        requirements=[requirement],
        matching=matching,
        resume_skills=[],
        job_skills=[job_skill],
    )

    assert result.partial_matches == ["Python"]
    assert result.missing_skills == []
    assert len(result.gaps) == 1

    gap = result.gaps[0]
    assert gap.requirement_id == "req-python"
    assert gap.requirement_type == "required"
    assert gap.target_skill_id == "job-python"
    assert gap.target_skill_name == "Python"
    assert gap.match_status == "partial"
    assert gap.gap_type == "partial"
    assert gap.severity == "medium"
    assert gap.similarity == 0.70
    assert gap.confidence is not None
    assert gap.rationale == "phase5-alignment"
    assert gap.evidence


def test_unmatched_skill_creates_missing_skill_gap() -> None:
    job_skill = _skill("job-docker", "Docker")

    requirement = _requirement(
        "req-docker",
        "Docker",
        skill_id=job_skill.skill_id,
        canonical_name="Docker",
    )

    matching = _matching(
        alignments=[
            _alignment(
                "req-docker",
                RequirementMatchStatus.UNMATCHED,
                evidence=[
                    _evidence("alignment-docker", "Docker alignment")
                ],
            )
        ]
    )

    result = GapAnalyzer().analyze(
        requirements=[requirement],
        matching=matching,
        resume_skills=[],
        job_skills=[job_skill],
    )

    assert result.missing_skills == ["Docker"]
    assert result.partial_matches == []
    assert len(result.gaps) == 1

    gap = result.gaps[0]
    assert gap.match_status == "unmatched"
    assert gap.gap_type == "unmatched"
    assert gap.severity == "high"
    assert gap.similarity is None


def test_unknown_skill_is_not_classified_as_missing() -> None:
    requirement = _requirement(
        "req-kubernetes",
        "Kubernetes",
        canonical_name="Kubernetes",
    )

    requirement_evidence = requirement.evidence

    matching = _matching(
        alignments=[
            _alignment(
                "req-kubernetes",
                RequirementMatchStatus.UNKNOWN,
                evidence=requirement_evidence,
            )
        ]
    )

    result = GapAnalyzer().analyze(
        requirements=[requirement],
        matching=matching,
        resume_skills=[],
        job_skills=[],
    )

    assert result.missing_skills == []
    assert result.partial_matches == []
    assert len(result.gaps) == 1

    gap = result.gaps[0]
    assert gap.match_status == "unknown"
    assert gap.gap_type == "unknown"
    assert gap.severity == "unknown"
    assert gap.similarity is None
    assert gap.evidence == requirement_evidence


def test_preferred_requirement_type_is_preserved() -> None:
    job_skill = _skill("job-docker", "Docker")

    requirement = _requirement(
        "req-docker",
        "Docker",
        requirement_type=JobRequirementType.PREFERRED,
        skill_id=job_skill.skill_id,
        canonical_name="Docker",
    )

    matching = _matching(
        alignments=[
            _alignment(
                "req-docker",
                RequirementMatchStatus.UNMATCHED,
            )
        ]
    )

    result = GapAnalyzer().analyze(
        requirements=[requirement],
        matching=matching,
        resume_skills=[],
        job_skills=[job_skill],
    )

    assert len(result.gaps) == 1
    assert result.gaps[0].requirement_type == "preferred"


def test_non_skill_requirements_do_not_create_skill_gaps() -> None:
    experience = JobRequirement(
        requirement_id="req-experience",
        text="3 years of experience",
        requirement_type=JobRequirementType.REQUIRED,
        category=JobRequirementCategory.EXPERIENCE,
        evidence=[_evidence("job-experience", "3 years")],
        confidence=_confidence(),
    )

    education = JobRequirement(
        requirement_id="req-education",
        text="Bachelor degree",
        requirement_type=JobRequirementType.REQUIRED,
        category=JobRequirementCategory.EDUCATION,
        evidence=[_evidence("job-education", "Bachelor degree")],
        confidence=_confidence(),
    )

    matching = _matching(
        alignments=[
            _alignment(
                "req-experience",
                RequirementMatchStatus.UNMATCHED,
            ),
            _alignment(
                "req-education",
                RequirementMatchStatus.UNKNOWN,
            ),
        ]
    )

    result = GapAnalyzer().analyze(
        requirements=[experience, education],
        matching=matching,
        resume_skills=[],
        job_skills=[],
    )

    assert isinstance(result, SkillAnalysis)
    assert result.gaps == []
    assert result.missing_skills == []
    assert result.partial_matches == []


def test_alignment_is_authoritative_and_no_new_matching_is_performed() -> None:
    job_skill = _skill("job-python", "Python")

    requirement = _requirement(
        "req-python",
        "Python",
        skill_id=job_skill.skill_id,
        canonical_name="Python",
    )

    # A SkillMatch exists, but the authoritative Phase 5 alignment says
    # UNKNOWN. Phase 6 must not reinterpret the match or change the status.
    match = SkillMatch(
        resume_skill_id="resume-python",
        job_skill_id=job_skill.skill_id,
        relationship=MatchRelationship.EXACT,
        similarity=1.0,
        confidence=_confidence(),
    )

    matching = _matching(
        alignments=[
            _alignment(
                "req-python",
                RequirementMatchStatus.UNKNOWN,
            )
        ],
        skill_matches=[match],
    )

    result = GapAnalyzer().analyze(
        requirements=[requirement],
        matching=matching,
        resume_skills=[],
        job_skills=[job_skill],
    )

    assert len(result.gaps) == 1
    assert result.gaps[0].match_status == "unknown"
    assert result.missing_skills == []
    assert result.matched_skills == []


def test_existing_similarity_is_preserved_without_using_confidence_as_similarity() -> None:
    job_skill = _skill("job-sql", "SQL")

    requirement = _requirement(
        "req-sql",
        "SQL",
        skill_id=job_skill.skill_id,
        canonical_name="SQL",
    )

    match = SkillMatch(
        resume_skill_id="resume-sql",
        job_skill_id=job_skill.skill_id,
        relationship=MatchRelationship.PARTIAL,
        similarity=0.91,
        confidence=_confidence(0.42),
    )

    matching = _matching(
        alignments=[
            _alignment(
                "req-sql",
                RequirementMatchStatus.PARTIAL,
                confidence=0.42,
            )
        ],
        skill_matches=[match],
    )

    result = GapAnalyzer().analyze(
        requirements=[requirement],
        matching=matching,
        resume_skills=[],
        job_skills=[job_skill],
    )

    gap = result.gaps[0]

    assert gap.similarity == 0.91
    assert gap.confidence is not None
    assert gap.confidence.score == 0.42


def test_missing_alignment_does_not_create_a_gap_from_absence() -> None:
    requirement = _requirement(
        "req-react",
        "React",
        canonical_name="React",
    )

    result = GapAnalyzer().analyze(
        requirements=[requirement],
        matching=_matching(alignments=[]),
        resume_skills=[],
        job_skills=[],
    )

    assert result.gaps == []
    assert result.missing_skills == []
    assert result.partial_matches == []
    assert result.matched_skills == []


def test_extracted_skills_are_preserved_without_creating_gaps() -> None:
    python = _skill("resume-python", "Python")
    react = _skill("resume-react", "React")

    result = GapAnalyzer().analyze(
        requirements=[],
        matching=_matching(alignments=[]),
        resume_skills=[python, react],
        job_skills=[],
    )

    assert result.extracted_skills == ["Python", "React"]
    assert result.gaps == []
