from __future__ import annotations

from backend.app.domain.analysis import AnalysisResult


class ResumeImprovementPromptGenerator:
    """
    Deterministically generates a plain-text prompt that can be copied into
    an external GenAI tool to improve or customize a resume.

    This component is presentation/orchestration logic only. It consumes the
    canonical AnalysisResult and does not perform independent analysis or
    call an LLM.
    """

    ENGINE_VERSION = "phase9-resume-improvement-prompt-v2"

    def generate(self, result: AnalysisResult) -> str:
        sections: list[str] = []

        sections.extend(self._task_section(result))
        sections.extend(self._candidate_section(result))
        sections.extend(self._quality_section(result))
        sections.extend(self._ats_section(result))
        sections.extend(self._language_section(result))
        sections.extend(self._career_section(result))
        sections.extend(self._job_match_section(result))
        sections.extend(self._recommendations_section(result))
        sections.extend(self._xai_section(result))
        sections.extend(self._factuality_section())
        sections.extend(self._output_section(result))

        return "\n".join(sections).strip() + "\n"

    def _task_section(self, result: AnalysisResult) -> list[str]:
        if result.job_profile is not None:
            return [
                "TASK",
                (
                    "Improve and tailor the candidate's resume for the target "
                    "job using the verified resume evidence and job-match "
                    "analysis below."
                ),
                (
                    "Prioritize the highest-impact requirements and gaps while "
                    "preserving factual accuracy."
                ),
                "",
            ]

        return [
            "TASK",
            (
                "Improve the candidate's resume using the verified resume "
                "evidence and analysis below."
            ),
            (
                "Prioritize resume quality, ATS compatibility, language "
                "clarity, and career positioning while preserving factual "
                "accuracy."
            ),
            "",
        ]

    def _candidate_section(self, result: AnalysisResult) -> list[str]:
        resume = result.resume_profile
        contact = resume.contact

        lines = ["CANDIDATE FACTS"]

        self._append_value(lines, "Candidate name", contact, "name")
        self._append_value(lines, "Candidate email", contact, "email")
        self._append_nonempty(lines, "Candidate summary", resume.candidate_summary)
        self._append_nonempty(lines, "Seniority", resume.seniority)
        if resume.total_experience is not None:
            lines.append(f"Total experience: {resume.total_experience}")
        self._append_joined(lines, "Domains", resume.domains)
        self._append_skills(lines, resume.skills)

        if resume.education:
            lines.append("Education:")
            for item in resume.education:
                degree = self._attr(item, "degree")
                field = self._attr(item, "field_of_study")
                institution = self._attr(item, "institution")

                education_parts = [
                    str(value)
                    for value in (degree, field, institution)
                    if value not in (None, "")
                ]

                if education_parts:
                    lines.append(f"- {' in '.join(education_parts[:2])}"
                                 + (
                                     f" at {institution}"
                                     if institution not in (None, "")
                                     else ""
                                 ))

        if resume.experience:
            lines.append("Experience:")
            for item in resume.experience:
                role = self._attr(item, "role")
                company = self._attr(item, "company")
                description = self._attr(item, "description")

                label = self._combine(role, company, separator=" at ")
                if description:
                    label = f"{label}: {description}" if label else str(description)

                if label:
                    lines.append(f"- {label}")

        if resume.projects:
            lines.append("Projects:")
            for item in resume.projects:
                name = self._attr(item, "name")
                description = self._attr(item, "description")
                technologies = self._attr(item, "technologies", [])

                parts: list[str] = []
                if name:
                    parts.append(str(name))
                if description:
                    parts.append(str(description))
                if technologies:
                    parts.append(
                        f"technologies: {self._join(technologies, fallback='')}"
                    )

                if parts:
                    lines.append(f"- {'; '.join(parts)}")

        if resume.certifications:
            lines.append("Certifications:")
            for item in resume.certifications:
                name = self._attr(item, "name")
                issuer = self._attr(item, "issuer")

                if name and issuer:
                    lines.append(f"- {name} ({issuer})")
                elif name:
                    lines.append(f"- {name}")

        lines.append("")
        return lines

    def _quality_section(self, result: AnalysisResult) -> list[str]:
        quality = result.resume_quality
        if quality is None:
            return []

        lines = [
            "RESUME QUALITY",
            f"Overall score: {quality.overall_score:.1f}/100",
        ]

        for finding in quality.findings:
            lines.append(
                f"- [{finding.severity}] {finding.title}: "
                f"{finding.explanation}"
            )
            if finding.recommendation:
                lines.append(f"  Action: {finding.recommendation}")

        lines.append("")
        return lines

    def _ats_section(self, result: AnalysisResult) -> list[str]:
        ats = result.ats_intelligence
        if ats is None:
            return []

        lines = [
            "ATS COMPATIBILITY",
            f"Overall score: {ats.overall_score:.1f}/100",
        ]

        for finding in ats.findings:
            lines.append(
                f"- [{finding.severity}] {finding.title}: "
                f"{finding.explanation}"
            )
            if finding.recommendation:
                lines.append(f"  Action: {finding.recommendation}")

        lines.append("")
        return lines

    def _language_section(self, result: AnalysisResult) -> list[str]:
        language = result.language_quality
        if language is None:
            return []

        heuristic = language.authorship_heuristic

        lines = [
            "LANGUAGE QUALITY",
            f"Overall score: {language.overall_score:.1f}/100",
            (
                "AI writing-style estimate: "
                f"{heuristic.score:.1f}/100 ({heuristic.level})"
            ),
            f"Disclaimer: {heuristic.disclaimer}",
        ]

        for issue in language.issues:
            lines.append(
                f"- [{issue.severity}] {issue.issue_type}: "
                f"{issue.title} — {issue.explanation}"
            )

            if issue.original_text:
                lines.append(f"  Original: {issue.original_text}")

            if issue.suggested_text:
                lines.append(f"  Suggested: {issue.suggested_text}")

            if issue.recommendation:
                lines.append(f"  Action: {issue.recommendation}")

        lines.append("")
        return lines

    def _career_section(self, result: AnalysisResult) -> list[str]:
        career = result.career_intelligence
        if career is None:
            return []

        lines = ["CAREER POSITIONING"]

        self._append_nonempty(
            lines,
            "Inferred profile",
            career.inferred_profile,
        )

        if career.experience_level:
            lines.append(f"Experience level: {career.experience_level}")

        self._append_joined(
            lines,
            "Primary domains",
            career.primary_domains,
        )
        self._append_joined(
            lines,
            "Secondary domains",
            career.secondary_domains,
        )
        self._append_joined(
            lines,
            "Transferable skills",
            career.transferable_skills,
        )

        if career.role_fit:
            lines.append("Role fit:")
            for role in career.role_fit:
                lines.append(
                    f"- {role.role}: {role.fit_score:.1f}/100 "
                    f"({role.direction}) — {role.rationale}"
                )

        if career.limitations:
            lines.append("Limitations:")
            for limitation in career.limitations:
                lines.append(f"- {limitation}")

        if career.risks:
            lines.append("Risks:")
            for risk in career.risks:
                lines.append(f"- {risk}")

        lines.append("")
        return lines

    def _job_match_section(self, result: AnalysisResult) -> list[str]:
        job = result.job_profile
        if job is None:
            return []

        analysis = result.skill_analysis
        lines = ["TARGET JOB"]

        self._append_nonempty(lines, "Role", job.job_title)
        self._append_nonempty(lines, "Company", job.company)
        self._append_nonempty(lines, "Summary", job.summary)

        if result.scoring is not None:
            scoring = result.scoring
            lines.extend(
                [
                    "",
                    "MATCH AND SCORING",
                    f"Overall fit score: {scoring.overall_score:.1f}/100",
                    f"Skill score: {scoring.skill_score:.1f}/100",
                    (
                        "Required skill score: "
                        f"{scoring.required_skill_score:.1f}/100"
                    ),
                    (
                        "Preferred skill score: "
                        f"{scoring.preferred_skill_score:.1f}/100"
                    ),
                    f"Experience alignment: {scoring.experience_score:.1f}/100",
                    f"Education alignment: {scoring.education_score:.1f}/100",
                    f"Domain alignment: {scoring.domain_score:.1f}/100",
                ]
            )

        self._append_joined(
            lines,
            "Required skills",
            job.required_skills,
        )
        self._append_joined(
            lines,
            "Preferred skills",
            job.preferred_skills,
        )
        self._append_joined(
            lines,
            "Matched skills",
            analysis.matched_skills,
        )
        self._append_joined(
            lines,
            "Partial matches",
            analysis.partial_matches,
        )
        self._append_joined(
            lines,
            "Missing skills",
            analysis.missing_skills,
        )
        self._append_joined(
            lines,
            "Transferable skills",
            analysis.transferable_skills,
        )

        if result.matching is not None and result.matching.requirement_alignments:
            lines.append("Requirement alignment:")
            for alignment in result.matching.requirement_alignments:
                rationale = (
                    f" — {alignment.rationale}"
                    if alignment.rationale
                    else ""
                )
                lines.append(
                    f"- {alignment.status}{rationale}"
                )

        if result.scoring is not None:
            if result.scoring.penalties:
                lines.append("Score penalties:")
                for penalty in result.scoring.penalties:
                    lines.append(
                        f"- {penalty.reason}: {penalty.value:+.1f}"
                    )

            if result.scoring.bonuses:
                lines.append("Score bonuses:")
                for bonus in result.scoring.bonuses:
                    lines.append(
                        f"- {bonus.reason}: {bonus.value:+.1f}"
                    )

        lines.append("")
        return lines

    def _recommendations_section(
        self,
        result: AnalysisResult,
    ) -> list[str]:
        if not result.recommendations:
            return []

        lines = ["RECOMMENDATIONS"]

        ordered = sorted(
            result.recommendations,
            key=lambda recommendation: (
                -recommendation.priority_score,
                recommendation.recommendation_id,
            ),
        )

        for recommendation in ordered:
            target = (
                f" | Target skill: {recommendation.target_skill}"
                if recommendation.target_skill
                else ""
            )

            lines.append(
                f"- [{recommendation.priority}] "
                f"{recommendation.type}: "
                f"{recommendation.title}{target}"
            )
            lines.append(f"  Rationale: {recommendation.rationale}")

            if recommendation.expected_impact is not None:
                lines.append(
                    f"  Expected impact: {recommendation.expected_impact}"
                )

            if recommendation.effort is not None:
                lines.append(f"  Effort: {recommendation.effort}")

        lines.append("")
        return lines

    def _xai_section(self, result: AnalysisResult) -> list[str]:
        xai = result.xai
        if xai is None:
            return []

        lines = ["EVIDENCE AND REASONING"]

        if xai.overall_explanation:
            lines.append(
                f"Overall: {xai.overall_explanation}"
            )

        if xai.score_explanation:
            lines.append(
                f"Scoring: {xai.score_explanation}"
            )

        if xai.strengths:
            lines.append(
                f"Strengths: {self._join(xai.strengths)}"
            )

        if xai.weaknesses:
            lines.append(
                f"Weaknesses: {self._join(xai.weaknesses)}"
            )

        for explanation in xai.matched_skill_explanations:
            lines.append(
                f"- Matched skill {explanation.skill_id}: "
                f"{explanation.explanation}"
            )

        for explanation in xai.partial_match_explanations:
            lines.append(
                f"- Partial skill {explanation.skill_id}: "
                f"{explanation.explanation}"
            )

        for explanation in xai.missing_skill_explanations:
            lines.append(
                f"- Missing skill {explanation.skill_id}: "
                f"{explanation.explanation}"
            )

        lines.append("")
        return lines

    def _factuality_section(self) -> list[str]:
        return [
            "STRICT FACTUALITY RULES",
            "Do not invent employers.",
            "Do not invent job titles.",
            "Do not invent dates.",
            "Do not invent skills or technologies.",
            "Do not invent achievements, responsibilities, or metrics.",
            "Do not invent certifications.",
            "Do not invent education or experience.",
            "Do not claim the candidate performed work that is not evidenced.",
            (
                "Preserve all verified factual information from the source "
                "resume."
            ),
            "Clearly distinguish suggestions from verified facts.",
            (
                "Only strengthen wording when the underlying claim is "
                "supported by the resume."
            ),
            (
                "If important information is missing, identify it for the "
                "candidate instead of fabricating it."
            ),
            "",
        ]

    def _output_section(self, result: AnalysisResult) -> list[str]:
        lines = [
            "EXPECTED OUTPUT",
            "Produce the following:",
            "1. A revised resume preserving all verified facts.",
            "2. Clear, concise, ATS-compatible wording.",
            (
                "3. Stronger achievement-oriented wording only where the "
                "source supports the claim."
            ),
            (
                "4. A short list of missing information the candidate should "
                "provide if it would materially strengthen the resume."
            ),
        ]

        if result.job_profile is not None:
            lines.extend(
                [
                    (
                        "5. JD-specific tailoring that prioritizes relevant "
                        "required skills and responsibilities."
                    ),
                    (
                        "6. A concise list of the most important JD-related "
                        "changes made."
                    ),
                ]
            )
        else:
            lines.extend(
                [
                    (
                        "5. Career-positioning improvements where supported "
                        "by the evidence."
                    ),
                    "6. A concise list of the most important changes made.",
                ]
            )

        lines.extend(
            [
                "",
                (
                    "Do not treat the SkillLens scores or heuristic estimates "
                    "as facts beyond what they explicitly represent."
                ),
            ]
        )

        return lines

    @staticmethod
    def _attr(
        obj: object,
        name: str,
        default: object = None,
    ) -> object:
        return getattr(obj, name, default)

    @classmethod
    def _append_value(
        cls,
        lines: list[str],
        label: str,
        obj: object,
        name: str,
    ) -> None:
        value = cls._attr(obj, name)
        cls._append_nonempty(lines, label, value)

    @staticmethod
    def _append_nonempty(
        lines: list[str],
        label: str,
        value: object,
    ) -> None:
        if value is None or value == "":
            return
        lines.append(f"{label}: {value}")

    @staticmethod
    def _append_joined(
        lines: list[str],
        label: str,
        values: object,
    ) -> None:
        if not values:
            return

        rendered = ", ".join(str(value) for value in values)
        if rendered:
            lines.append(f"{label}: {rendered}")

    @classmethod
    def _append_skills(
        cls,
        lines: list[str],
        skills: object,
    ) -> None:
        if not skills:
            return

        names: list[str] = []
        for skill in skills:
            display_name = getattr(skill, "display_name", None)
            canonical_name = getattr(skill, "canonical_name", None)
            value = display_name or canonical_name or skill
            if value:
                names.append(str(value))

        if names:
            lines.append(f"Skills: {', '.join(names)}")

    @staticmethod
    def _join(
        values: object,
        fallback: str = "Not provided",
    ) -> str:
        if not values:
            return fallback
        return ", ".join(str(value) for value in values)

    @staticmethod
    def _combine(
        first: object,
        second: object,
        *,
        separator: str,
    ) -> str:
        if first and second:
            return f"{first}{separator}{second}"
        if first:
            return str(first)
        if second:
            return str(second)
        return ""
