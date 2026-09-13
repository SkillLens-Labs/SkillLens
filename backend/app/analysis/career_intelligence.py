from __future__ import annotations

from collections import Counter
from hashlib import sha256
from typing import Iterable

from backend.app.domain.career import (
    CareerDirection,
    CareerDirectionResult,
    CareerIntelligence,
    CareerSeniorityLevel,
    RoleFit,
)
from backend.app.domain.confidence import Confidence, ConfidenceLevel
from backend.app.domain.evidence import Evidence, EvidenceSourceType
from backend.app.domain.resume import ResumeProfile
from backend.app.analysis.career_catalog import (
    CAREER_ROLE_CATALOG,
    CAREER_TAXONOMY_VERSION,
    CareerRoleProfile,
)

ENGINE_VERSION = "phase7-career-intelligence-v1"


class CareerIntelligenceAnalyzer:
    """
    Deterministic generalized career-intelligence engine.

    This engine evaluates career-role suitability independently from
    candidate-vs-job-description scoring. A job description may provide
    contextual evidence, but it never replaces generalized role matching.
    """

    def analyze(
        self,
        resume_profile: ResumeProfile,
        structured_resume,
        job_profile=None,
    ) -> CareerIntelligence:
        skill_names = self._normalized_skill_names(resume_profile)
        evidence_by_skill = self._skill_evidence(resume_profile)

        seniority, seniority_confidence, seniority_evidence, seniority_rationale = (
            self._infer_seniority(
                resume_profile,
                structured_resume,
            )
        )

        domains = self._classify_domains(
            skill_names,
            resume_profile,
            structured_resume,
        )

        role_results = [
            self._evaluate_role(
                role=role,
                skill_names=skill_names,
                evidence_by_skill=evidence_by_skill,
                seniority=seniority,
                seniority_confidence=seniority_confidence,
                structured_resume=structured_resume,
            )
            for role in CAREER_ROLE_CATALOG
        ]

        role_results.sort(
            key=lambda result: (
                -result.fit_score,
                -result.confidence.score,
                result.role.casefold(),
            )
        )

        career_directions = self._classify_directions(role_results)

        strengths = self._identify_strengths(
            skill_names,
            evidence_by_skill,
            domains,
            structured_resume,
        )

        limitations = self._identify_limitations(
            skill_names,
            domains,
            seniority,
            structured_resume,
        )

        transferable_skills = self._identify_transferable_skills(
            skill_names,
            evidence_by_skill,
        )

        overall_confidence = self._overall_confidence(
            skill_names=skill_names,
            evidence_by_skill=evidence_by_skill,
            structured_resume=structured_resume,
            seniority_confidence=seniority_confidence,
            role_results=role_results,
        )

        primary_domains = [domain for domain, _ in domains[:3]]
        secondary_domains = [domain for domain, _ in domains[3:6]]

        primary_roles = [
            result.role
            for result in career_directions
            if result.direction == CareerDirection.PRIMARY
        ]

        potential_roles = [
            result.role
            for result in career_directions
            if result.direction != CareerDirection.INSUFFICIENT_EVIDENCE
        ]

        inferred_profile = self._inferred_profile(
            primary_domains=primary_domains,
            seniority=seniority,
            primary_roles=primary_roles,
        )

        career_signals = self._career_signals(
            skill_names=skill_names,
            domains=domains,
            seniority=seniority,
            structured_resume=structured_resume,
        )

        return CareerIntelligence(
            inferred_profile=inferred_profile,
            experience_level=seniority,
            seniority_confidence=seniority_confidence,
            seniority_evidence=seniority_evidence,
            seniority_rationale=seniority_rationale,
            primary_domains=primary_domains,
            secondary_domains=secondary_domains,
            strengths=strengths,
            limitations=limitations,
            transferable_skills=transferable_skills,
            career_directions=career_directions,
            potential_roles=potential_roles,
            role_fit=[
                self._to_role_fit(result)
                for result in career_directions
                if result.direction != CareerDirection.INSUFFICIENT_EVIDENCE
            ],
            career_signals=career_signals,
            transition_analysis=self._transition_analysis(career_directions),
            skill_priorities=[],
            risks=[],
            confidence=overall_confidence,
            taxonomy_version=CAREER_TAXONOMY_VERSION,
            engine_version=ENGINE_VERSION,
        )

    # ------------------------------------------------------------------
    # Skill preparation
    # ------------------------------------------------------------------

    @staticmethod
    def _normalized_skill_names(resume_profile: ResumeProfile) -> tuple[str, ...]:
        """
        ResumeProfile skills are already normalized by Phase 3.

        Preserve source ordering while removing duplicates.
        """
        seen: set[str] = set()
        result: list[str] = []

        for skill in resume_profile.skills:
            name = skill.canonical_name.strip().casefold()
            if not name or name in seen:
                continue
            seen.add(name)
            result.append(name)

        return tuple(result)

    @staticmethod
    def _skill_evidence(
        resume_profile: ResumeProfile,
    ) -> dict[str, tuple[Evidence, ...]]:
        result: dict[str, tuple[Evidence, ...]] = {}

        for skill in resume_profile.skills:
            name = skill.canonical_name.strip().casefold()
            if not name:
                continue

            existing = list(result.get(name, ()))
            existing.extend(skill.evidence)

            # Deterministic evidence ordering.
            existing.sort(
                key=lambda evidence: (
                    -(evidence.relevance or 0.0),
                    -(evidence.confidence or 0.0),
                    evidence.evidence_id,
                )
            )

            result[name] = tuple(existing)

        return result

    # ------------------------------------------------------------------
    # Role matching
    # ------------------------------------------------------------------

    def _evaluate_role(
        self,
        role: CareerRoleProfile,
        skill_names: tuple[str, ...],
        evidence_by_skill: dict[str, tuple[Evidence, ...]],
        seniority: CareerSeniorityLevel,
        seniority_confidence: Confidence,
        structured_resume,
    ) -> CareerDirectionResult:
        skill_set = set(skill_names)

        matched_core = [
            skill for skill in role.core_skills if skill in skill_set
        ]
        matched_supporting = [
            skill for skill in role.supporting_skills if skill in skill_set
        ]

        core_coverage = (
            len(matched_core) / len(role.core_skills)
            if role.core_skills
            else 0.0
        )

        supporting_coverage = (
            len(matched_supporting) / len(role.supporting_skills)
            if role.supporting_skills
            else 0.0
        )

        evidence_strength = self._role_evidence_strength(
            matched_core + matched_supporting,
            evidence_by_skill,
        )

        context_strength = self._context_strength(
            structured_resume,
            matched_core + matched_supporting,
        )

        seniority_alignment = (
            1.0
            if seniority == CareerSeniorityLevel.UNKNOWN
            else (
                1.0
                if seniority in role.typical_seniority
                else 0.65
            )
        )

        # Generalized role fit:
        #
        # Core skill coverage is deliberately dominant.
        # Supporting skills improve discrimination.
        # Evidence/context measure whether matched skills are actually
        # substantiated in the source material.
        #
        # This is NOT the Phase 6 candidate-vs-JD score.
        fit_score = (
            core_coverage * 60.0
            + supporting_coverage * 20.0
            + evidence_strength * 10.0
            + context_strength * 5.0
            + seniority_alignment * 5.0
        )

        fit_score = round(min(100.0, max(0.0, fit_score)), 2)

        confidence = self._role_confidence(
            matched_core=matched_core,
            matched_supporting=matched_supporting,
            evidence_strength=evidence_strength,
            context_strength=context_strength,
            fit_score=fit_score,
        )

        evidence = self._role_evidence(
            role=role,
            matched_skills=matched_core + matched_supporting,
            evidence_by_skill=evidence_by_skill,
        )

        rationale = self._role_rationale(
            role=role,
            matched_core=matched_core,
            matched_supporting=matched_supporting,
            core_coverage=core_coverage,
            supporting_coverage=supporting_coverage,
            seniority=seniority,
        )

        return CareerDirectionResult(
            role=role.title,
            direction=CareerDirection.SECONDARY,
            fit_score=fit_score,
            rationale=rationale,
            evidence=evidence,
            confidence=confidence,
        )

    @staticmethod
    def _role_evidence_strength(
        matched_skills: Iterable[str],
        evidence_by_skill: dict[str, tuple[Evidence, ...]],
    ) -> float:
        skills = list(matched_skills)

        if not skills:
            return 0.0

        strengths: list[float] = []

        for skill in skills:
            evidence = evidence_by_skill.get(skill, ())
            if not evidence:
                strengths.append(0.0)
                continue

            strengths.append(
                max(
                    (
                        (
                            evidence_item.relevance
                            if evidence_item.relevance is not None
                            else 0.0
                        )
                        * 0.5
                        + (
                            evidence_item.confidence
                            if evidence_item.confidence is not None
                            else 0.0
                        )
                        * 0.5
                    )
                    for evidence_item in evidence
                )
            )

        return sum(strengths) / len(strengths)

    @staticmethod
    def _context_strength(
        structured_resume,
        matched_skills: Iterable[str],
    ) -> float:
        """
        Determine whether matched skills appear in meaningful resume
        context beyond the normalized skill list.

        This remains deterministic and intentionally conservative.
        """
        if structured_resume is None:
            return 0.0

        matched = {skill.casefold() for skill in matched_skills}

        if not matched:
            return 0.0

        contextual_hits = 0
        contextual_blocks = 0

        for section in getattr(structured_resume, "sections", ()):
            section_name = getattr(section.section_type, "value", "")
            if section_name not in {
                "summary",
                "experience",
                "projects",
                "education",
            }:
                continue

            for block in section.blocks:
                text = block.text.casefold()
                contextual_blocks += 1

                if any(skill in text for skill in matched):
                    contextual_hits += 1

        if contextual_blocks == 0:
            return 0.0

        return min(1.0, contextual_hits / max(1, len(matched)))

    @staticmethod
    def _role_confidence(
        matched_core: list[str],
        matched_supporting: list[str],
        evidence_strength: float,
        context_strength: float,
        fit_score: float,
    ) -> Confidence:
        core_count = len(matched_core)
        supporting_count = len(matched_supporting)

        coverage_signal = min(
            1.0,
            (core_count * 0.20) + (supporting_count * 0.05),
        )

        score_signal = fit_score / 100.0

        confidence_score = round(
            min(
                1.0,
                coverage_signal * 0.35
                + evidence_strength * 0.35
                + context_strength * 0.15
                + score_signal * 0.15,
            ),
            3,
        )

        return Confidence(
            score=confidence_score,
            level=CareerIntelligenceAnalyzer._confidence_level(
                confidence_score
            ),
            components={
                "skill_coverage": round(coverage_signal, 3),
                "evidence_strength": round(evidence_strength, 3),
                "context_strength": round(context_strength, 3),
                "fit_score_signal": round(score_signal, 3),
            },
            rationale=(
                "Confidence reflects matched-skill coverage and evidence "
                "strength; it is separate from role-fit score."
            ),
        )

    # ------------------------------------------------------------------
    # Seniority
    # ------------------------------------------------------------------

    def _infer_seniority(
        self,
        resume_profile: ResumeProfile,
        structured_resume,
    ) -> tuple[
        CareerSeniorityLevel,
        Confidence,
        list[Evidence],
        str,
    ]:
        experience_years = resume_profile.total_experience

        if experience_years is not None:
            level = self._seniority_from_years(experience_years)
            evidence = self._synthetic_evidence(
                source_type=EvidenceSourceType.RESUME,
                source_document_id=resume_profile.document_id,
                section="experience",
                text=f"Reported total experience: {experience_years:g} years.",
                evidence_type="seniority_experience",
            )

            confidence_score = 0.85
            return (
                level,
                self._simple_confidence(
                    confidence_score,
                    "Structured total experience provides direct seniority evidence.",
                ),
                [evidence],
                f"Seniority inferred from reported total experience of {experience_years:g} years.",
            )

        experience_sections = []
        if structured_resume is not None:
            experience_sections = [
                section
                for section in getattr(structured_resume, "sections", ())
                if getattr(section.section_type, "value", "")
                == "experience"
            ]

        if experience_sections:
            experience_blocks = [
                block
                for section in experience_sections
                for block in section.blocks
            ]

            if experience_blocks:
                level = self._seniority_from_experience_text(experience_blocks)

                evidence = self._evidence_from_blocks(
                    resume_profile.document_id,
                    "experience",
                    experience_blocks[:3],
                    "seniority_experience_context",
                )

                if level == CareerSeniorityLevel.UNKNOWN:
                    return (
                        level,
                        self._simple_confidence(
                            0.45,
                            "Experience evidence is available, but it does not establish a reliable explicit seniority level.",
                        ),
                        evidence,
                        "Seniority remains unknown because the available experience-section evidence does not contain reliable role-level seniority wording.",
                    )

                return (
                    level,
                    self._simple_confidence(
                        0.70,
                        "Explicit role-level seniority wording is available in the experience section.",
                    ),
                    evidence,
                    "Seniority inferred from explicit role-level wording in the available experience-section evidence.",
                )

        summary_blocks = []
        if structured_resume is not None:
            summary_blocks = [
                block
                for section in getattr(structured_resume, "sections", ())
                if getattr(section.section_type, "value", "") == "summary"
                for block in section.blocks
            ]

        if summary_blocks:
            evidence = self._evidence_from_blocks(
                resume_profile.document_id,
                "summary",
                summary_blocks[:2],
                "seniority_summary_context",
            )

            return (
                CareerSeniorityLevel.UNKNOWN,
                self._simple_confidence(
                    0.40,
                    "Only summary-level evidence is available; seniority is not reliably established.",
                ),
                evidence,
                "Seniority remains unknown because reliable experience-duration evidence is unavailable.",
            )

        return (
            CareerSeniorityLevel.UNKNOWN,
            self._simple_confidence(
                0.20,
                "Insufficient structured evidence to infer seniority.",
            ),
            [],
            "Seniority remains unknown because the available resume evidence is insufficient.",
        )

    @staticmethod
    def _seniority_from_years(years: float) -> CareerSeniorityLevel:
        if years < 1.0:
            return CareerSeniorityLevel.ENTRY
        if years < 3.0:
            return CareerSeniorityLevel.JUNIOR
        if years < 6.0:
            return CareerSeniorityLevel.MID
        if years < 10.0:
            return CareerSeniorityLevel.SENIOR
        return CareerSeniorityLevel.LEAD

    @staticmethod
    def _seniority_from_experience_text(blocks) -> CareerSeniorityLevel:
        """
        Infer seniority from explicit candidate role-title evidence.

        Seniority wording is accepted when it appears in a plausible
        role-title position, such as the beginning of an experience block or
        immediately after a common resume title separator. Generic prose
        referring to another person's seniority must not affect the result.
        """

        lead_titles = (
            "lead developer",
            "lead software developer",
            "lead backend developer",
            "lead frontend developer",
            "lead full stack developer",
            "lead engineer",
            "lead software engineer",
            "lead backend engineer",
            "lead frontend engineer",
            "lead data engineer",
            "lead machine learning engineer",
            "principal engineer",
            "principal software engineer",
            "principal developer",
            "engineering manager",
            "development manager",
            "technical lead",
            "team lead",
            "head of engineering",
            "head of development",
            "software architect",
            "solutions architect",
            "solution architect",
            "technical architect",
            "enterprise architect",
            "data architect",
        )

        senior_titles = (
            "senior developer",
            "senior software developer",
            "senior backend developer",
            "senior frontend developer",
            "senior full stack developer",
            "senior engineer",
            "senior software engineer",
            "senior backend engineer",
            "senior frontend engineer",
            "senior data engineer",
            "senior machine learning engineer",
            "senior analyst",
            "senior data analyst",
            "senior business analyst",
            "senior cybersecurity analyst",
            "senior scientist",
            "senior data scientist",
            "senior machine learning engineer",
            "senior ai engineer",
            "senior consultant",
            "sr. developer",
            "sr. engineer",
            "sr developer",
            "sr engineer",
        )

        junior_titles = (
            "junior developer",
            "junior software developer",
            "junior backend developer",
            "junior frontend developer",
            "junior engineer",
            "junior software engineer",
            "junior backend engineer",
            "junior frontend engineer",
            "junior analyst",
            "junior data analyst",
            "junior business analyst",
            "junior cybersecurity analyst",
            "junior scientist",
            "junior data scientist",
            "junior machine learning engineer",
            "junior ai engineer",
            "jr. developer",
            "jr. engineer",
            "jr developer",
            "jr engineer",
            "intern",
            "trainee",
            "graduate engineer",
        )

        separators = (
            "|",
            " - ",
            " — ",
            " – ",
            ": ",
        )

        def candidate_title_regions(text: str) -> tuple[str, ...]:
            normalized = " ".join(text.casefold().split())
            regions = [normalized]

            for separator in separators:
                parts = normalized.split(separator)
                if len(parts) > 1:
                    regions.extend(part.strip() for part in parts)

            return tuple(region for region in regions if region)

        def is_explicit_title(text: str, titles: tuple[str, ...]) -> bool:
            normalized = " ".join(text.casefold().split())

            # A candidate role title must occur at the beginning of the
            # original experience block or at the beginning of a
            # separator-delimited region. This prevents prose such as
            # "worked with a senior engineer" from being treated as the
            # candidate's own title.
            for region in candidate_title_regions(normalized):
                for title in titles:
                    if region == title or region.startswith(title + " "):
                        return True

            return False

        normalized_blocks = [
            " ".join(block.text.casefold().split())
            for block in blocks
            if block.text.strip()
        ]

        for text in normalized_blocks:
            if is_explicit_title(text, lead_titles):
                return CareerSeniorityLevel.LEAD

        for text in normalized_blocks:
            if is_explicit_title(text, senior_titles):
                return CareerSeniorityLevel.SENIOR

        for text in normalized_blocks:
            if is_explicit_title(text, junior_titles):
                return CareerSeniorityLevel.JUNIOR

        return CareerSeniorityLevel.UNKNOWN

    # ------------------------------------------------------------------
    # Domain intelligence
    # ------------------------------------------------------------------

    def _classify_domains(
        self,
        skill_names: tuple[str, ...],
        resume_profile: ResumeProfile,
        structured_resume,
    ) -> list[tuple[str, float]]:
        """
        Classify career domains from normalized skills and structured resume
        context.

        Domain inference does not perform arbitrary substring keyword
        matching. Normalized skills provide the primary signal; existing
        Phase 3 skill categories and the presence of relevant structured
        sections provide bounded contextual support.
        """
        skill_set = set(skill_names)
        scores: Counter[str] = Counter()

        for role in CAREER_ROLE_CATALOG:
            core_hits = len(skill_set.intersection(role.core_skills))
            supporting_hits = len(skill_set.intersection(role.supporting_skills))
            if core_hits or supporting_hits:
                scores[role.domain] += core_hits * 3 + supporting_hits

        category_domain_map = {
            "programming": "software_engineering",
            "web": "software_engineering",
            "data": "data_science",
            "cloud_devops": "devops",
            "tooling": "software_engineering",
        }

        for category in resume_profile.skill_categories:
            category_value = category.casefold().strip()
            domain = category_domain_map.get(category_value)
            if domain:
                scores[domain] += 1

        section_types = {
            getattr(section.section_type, "value", "")
            for section in getattr(structured_resume, "sections", ())
        } if structured_resume is not None else set()

        # Structured sections provide contextual support only. They do not
        # create a domain in the absence of normalized-skill evidence.
        if "projects" in section_types:
            for role in CAREER_ROLE_CATALOG:
                if skill_set.intersection(
                    set(role.core_skills).union(role.supporting_skills)
                ):
                    scores[role.domain] += 0.25

        if "experience" in section_types:
            for role in CAREER_ROLE_CATALOG:
                if skill_set.intersection(
                    set(role.core_skills).union(role.supporting_skills)
                ):
                    scores[role.domain] += 0.50

        if "education" in section_types:
            for role in CAREER_ROLE_CATALOG:
                if skill_set.intersection(
                    set(role.core_skills).union(role.supporting_skills)
                ):
                    scores[role.domain] += 0.25

        if "certifications" in section_types:
            for role in CAREER_ROLE_CATALOG:
                if skill_set.intersection(
                    set(role.core_skills).union(role.supporting_skills)
                ):
                    scores[role.domain] += 0.25

        return sorted(
            (
                (domain, round(float(score), 3))
                for domain, score in scores.items()
                if score > 0
            ),
            key=lambda item: (-item[1], item[0]),
        )

    # ------------------------------------------------------------------
    # Strengths / limitations / transferable skills
    # ------------------------------------------------------------------

    @staticmethod
    def _identify_strengths(
        skill_names: tuple[str, ...],
        evidence_by_skill: dict[str, tuple[Evidence, ...]],
        domains: list[tuple[str, float]],
        structured_resume,
    ) -> list[str]:
        strengths: list[str] = []

        evidenced_skills = [
            skill
            for skill in skill_names
            if evidence_by_skill.get(skill)
        ]

        if evidenced_skills:
            top_skills = evidenced_skills[:5]
            strengths.append(
                "Demonstrated technical skills: "
                + ", ".join(top_skills)
                + "."
            )

        if domains:
            strengths.append(
                "Strongest evidenced domain signal: "
                + domains[0][0].replace("_", " ")
                + "."
            )

        if structured_resume is not None:
            section_types = {
                getattr(section.section_type, "value", "")
                for section in getattr(structured_resume, "sections", ())
            }

            if "projects" in section_types:
                strengths.append(
                    "Project evidence is available to support practical skill application."
                )

            if "experience" in section_types:
                strengths.append(
                    "Experience-section evidence is available to support applied capability."
                )

        return strengths[:5]

    @staticmethod
    def _identify_limitations(
        skill_names: tuple[str, ...],
        domains: list[tuple[str, float]],
        seniority: CareerSeniorityLevel,
        structured_resume,
    ) -> list[str]:
        limitations: list[str] = []

        if not skill_names:
            limitations.append(
                "The resume provides insufficient normalized skill evidence for reliable career-role inference."
            )

        if not domains:
            limitations.append(
                "The available normalized skills do not provide sufficient evidence for domain classification."
            )

        if seniority == CareerSeniorityLevel.UNKNOWN:
            limitations.append(
                "Seniority is not reliably established from the available experience evidence."
            )

        section_types = {
            getattr(section.section_type, "value", "")
            for section in getattr(structured_resume, "sections", ())
        } if structured_resume is not None else set()

        if "experience" not in section_types:
            limitations.append(
                "No structured experience section is available, limiting evidence for applied seniority."
            )

        if "projects" not in section_types:
            limitations.append(
                "No structured project section is available, limiting evidence for practical application."
            )

        return limitations[:5]

    @staticmethod
    def _identify_transferable_skills(
        skill_names: tuple[str, ...],
        evidence_by_skill: dict[str, tuple[Evidence, ...]],
    ) -> list[str]:
        """
        Identify skills appearing across multiple generalized career profiles.

        These are transferable capabilities already evidenced by the resume,
        not missing skills and not recommendations.
        """
        skill_role_counts: Counter[str] = Counter()

        for role in CAREER_ROLE_CATALOG:
            role_skills = set(role.core_skills).union(role.supporting_skills)

            for skill in skill_names:
                if skill in role_skills:
                    skill_role_counts[skill] += 1

        transferable = [
            skill
            for skill in skill_names
            if skill_role_counts[skill] >= 2
            and evidence_by_skill.get(skill)
        ]

        transferable.sort(
            key=lambda skill: (
                -skill_role_counts[skill],
                skill,
            )
        )

        return transferable[:10]

    # ------------------------------------------------------------------
    # Career directions
    # ------------------------------------------------------------------

    @staticmethod
    def _classify_directions(
        role_results: list[CareerDirectionResult],
    ) -> list[CareerDirectionResult]:
        if not role_results:
            return []

        enriched: list[CareerDirectionResult] = []

        for index, result in enumerate(role_results):
            if result.fit_score < 20.0:
                direction = CareerDirection.INSUFFICIENT_EVIDENCE
            elif index < 3 and result.fit_score >= 55.0:
                direction = CareerDirection.PRIMARY
            elif index < 6 and result.fit_score >= 35.0:
                direction = CareerDirection.SECONDARY
            else:
                direction = CareerDirection.INSUFFICIENT_EVIDENCE

            enriched.append(
                result.model_copy(update={"direction": direction})
            )

        return enriched[:10]

    @staticmethod
    def _to_role_fit(result: CareerDirectionResult) -> RoleFit:
        return RoleFit(
            role=result.role,
            fit_score=result.fit_score,
            direction=result.direction,
            rationale=result.rationale,
            evidence=result.evidence,
            confidence=result.confidence,
        )

    # ------------------------------------------------------------------
    # Overall confidence / profile / signals
    # ------------------------------------------------------------------

    def _overall_confidence(
        self,
        skill_names: tuple[str, ...],
        evidence_by_skill: dict[str, tuple[Evidence, ...]],
        structured_resume,
        seniority_confidence: Confidence,
        role_results: list[CareerDirectionResult],
    ) -> Confidence:
        skill_evidence_ratio = (
            sum(bool(evidence_by_skill.get(skill)) for skill in skill_names)
            / len(skill_names)
            if skill_names
            else 0.0
        )

        section_count = len(
            getattr(structured_resume, "sections", ())
            if structured_resume is not None
            else ()
        )

        structure_signal = min(1.0, section_count / 5.0)

        role_signal = (
            role_results[0].confidence.score
            if role_results
            else 0.0
        )

        score = round(
            min(
                1.0,
                skill_evidence_ratio * 0.35
                + structure_signal * 0.20
                + seniority_confidence.score * 0.20
                + role_signal * 0.25,
            ),
            3,
        )

        return Confidence(
            score=score,
            level=self._confidence_level(score),
            components={
                "skill_evidence": round(skill_evidence_ratio, 3),
                "resume_structure": round(structure_signal, 3),
                "seniority": round(seniority_confidence.score, 3),
                "top_role_confidence": round(role_signal, 3),
            },
            rationale=(
                "Overall career-intelligence confidence reflects evidence "
                "coverage, resume structure, seniority evidence, and top-role "
                "confidence."
            ),
        )

    @staticmethod
    def _inferred_profile(
        primary_domains: list[str],
        seniority: CareerSeniorityLevel,
        primary_roles: list[str],
    ) -> str | None:
        if not primary_domains and not primary_roles:
            return None

        domain_text = (
            primary_domains[0].replace("_", " ")
            if primary_domains
            else "technical"
        )

        seniority_text = (
            seniority.value
            if seniority != CareerSeniorityLevel.UNKNOWN
            else "undetermined"
        )

        if primary_roles:
            return (
                f"{seniority_text.title()} profile with strongest alignment "
                f"to {primary_roles[0]} in {domain_text}."
            )

        return (
            f"{seniority_text.title()} profile with strongest evidence "
            f"in {domain_text}."
        )

    @staticmethod
    def _career_signals(
        skill_names: tuple[str, ...],
        domains: list[tuple[str, float]],
        seniority: CareerSeniorityLevel,
        structured_resume,
    ) -> list[str]:
        signals: list[str] = []

        if skill_names:
            signals.append(f"{len(skill_names)} normalized skills identified.")

        if domains:
            signals.append(
                f"{len(domains)} career domain signals identified."
            )

        if seniority != CareerSeniorityLevel.UNKNOWN:
            signals.append(
                f"Seniority signal classified as {seniority.value}."
            )

        section_types = {
            getattr(section.section_type, "value", "")
            for section in getattr(structured_resume, "sections", ())
        } if structured_resume is not None else set()

        if "experience" in section_types:
            signals.append("Structured experience evidence is available.")

        if "projects" in section_types:
            signals.append("Structured project evidence is available.")

        return signals

    @staticmethod
    def _transition_analysis(
        career_directions: list[CareerDirectionResult],
    ) -> str | None:
        primary = [
            result.role
            for result in career_directions
            if result.direction == CareerDirection.PRIMARY
        ]

        secondary = [
            result.role
            for result in career_directions
            if result.direction == CareerDirection.SECONDARY
        ]

        if not primary and not secondary:
            return (
                "Available evidence is insufficient to establish a reliable "
                "career direction."
            )

        if primary and secondary:
            return (
                "Evidence is strongest for "
                + ", ".join(primary[:2])
                + "; adjacent directions include "
                + ", ".join(secondary[:3])
                + "."
            )

        if primary:
            return (
                "Evidence is concentrated around "
                + ", ".join(primary[:3])
                + "."
            )

        return (
            "Evidence points toward adjacent career directions, including "
            + ", ".join(secondary[:3])
            + "."
        )

    # ------------------------------------------------------------------
    # Evidence helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _role_evidence(
        role: CareerRoleProfile,
        matched_skills: list[str],
        evidence_by_skill: dict[str, tuple[Evidence, ...]],
    ) -> list[Evidence]:
        evidence: list[Evidence] = []

        for skill in matched_skills:
            evidence.extend(evidence_by_skill.get(skill, ()))

        evidence.sort(
            key=lambda item: (
                -(item.relevance or 0.0),
                -(item.confidence or 0.0),
                item.evidence_id,
            )
        )

        return evidence[:8]

    @staticmethod
    def _evidence_from_blocks(
        document_id: str,
        section: str,
        blocks,
        evidence_type: str,
    ) -> list[Evidence]:
        result = []

        for block in blocks:
            result.append(
                CareerIntelligenceAnalyzer._synthetic_evidence(
                    source_type=EvidenceSourceType.RESUME,
                    source_document_id=document_id,
                    section=section,
                    text=block.text,
                    evidence_type=evidence_type,
                )
            )

        return result

    @staticmethod
    def _synthetic_evidence(
        source_type: EvidenceSourceType,
        source_document_id: str,
        section: str,
        text: str,
        evidence_type: str,
    ) -> Evidence:
        normalized = " ".join(text.split())

        digest = sha256(
            "|".join(
                (
                    source_type.value,
                    source_document_id,
                    section,
                    evidence_type,
                    normalized,
                )
            ).encode("utf-8")
        ).hexdigest()

        return Evidence(
            evidence_id=f"career-{digest[:24]}",
            source_type=source_type,
            source_document_id=source_document_id,
            section=section,
            text=normalized,
            evidence_type=evidence_type,
            extractor=ENGINE_VERSION,
            relevance=0.85,
            confidence=0.80,
        )

    # ------------------------------------------------------------------
    # Formatting helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _role_rationale(
        role: CareerRoleProfile,
        matched_core: list[str],
        matched_supporting: list[str],
        core_coverage: float,
        supporting_coverage: float,
        seniority: CareerSeniorityLevel,
    ) -> str:
        if matched_core:
            core_text = ", ".join(matched_core)
            core_statement = (
                f"Matched core skills: {core_text} "
                f"({core_coverage:.0%} core coverage)."
            )
        else:
            core_statement = "No core skills were matched."

        if matched_supporting:
            supporting_text = ", ".join(matched_supporting)
            supporting_statement = (
                f"Supporting skills include {supporting_text} "
                f"({supporting_coverage:.0%} supporting coverage)."
            )
        else:
            supporting_statement = "No supporting skills were matched."

        seniority_statement = (
            f"Observed seniority signal: {seniority.value}."
        )

        return (
            f"{role.title}: {core_statement} "
            f"{supporting_statement} {seniority_statement}"
        )

    @staticmethod
    def _simple_confidence(score: float, rationale: str) -> Confidence:
        return Confidence(
            score=score,
            level=CareerIntelligenceAnalyzer._confidence_level(score),
            components={"evidence_strength": score},
            rationale=rationale,
        )

    @staticmethod
    def _confidence_level(score: float) -> ConfidenceLevel:
        if score >= 0.85:
            return ConfidenceLevel.HIGH
        if score >= 0.65:
            return ConfidenceLevel.MEDIUM
        return ConfidenceLevel.LOW
