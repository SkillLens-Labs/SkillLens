from __future__ import annotations

from backend.app.domain.analysis import AnalysisResult


class ResumeImprovementPromptGenerator:
    """
    Deterministically generates a plain-text prompt that can be copied into
    an external GenAI tool to improve/customize a resume.

    This component is presentation/orchestration logic only. It does not
    perform independent resume analysis and does not call an LLM.
    """

    ENGINE_VERSION = "phase9-resume-improvement-prompt-v1"

    def generate(self, result: AnalysisResult) -> str:
        sections: list[str] = []

        sections.extend(self._candidate_section(result))
        sections.extend(self._quality_section(result))
        sections.extend(self._ats_section(result))
        sections.extend(self._language_section(result))
        sections.extend(self._career_section(result))
        sections.extend(self._job_match_section(result))
        sections.extend(self._recommendations_section(result))
        sections.extend(self._xai_section(result))
        sections.extend(self._factuality_section())
        sections.extend(self._output_section())

        return "\n".join(sections).strip() + "\n"

    def _candidate_section(self, result: AnalysisResult) -> list[str]:
        resume = result.resume_profile
        contact = resume.contact

        lines = [
            "CANDIDATE FACTS",
            f"Candidate name: {self._value(contact, 'name')}",
            f"Candidate email: {self._value(contact, 'email')}",
            f"Candidate summary: {resume.candidate_summary or 'Not provided'}",
            f"Seniority: {resume.seniority or 'Not provided'}",
            (
                "Total experience: "
                f"{resume.total_experience if resume.total_experience is not None else 'Not provided'}"
            ),
            f"Domains: {self._join(resume.domains)}",
            f"Skills: {self._skills(resume.skills)}",
        ]

        if resume.education:
            lines.append("Education:")
            for item in resume.education:
                lines.append(
                    "- "
                    f"{self._value(item, 'degree')} "
                    f"in {self._value(item, 'field_of_study')} "
                    f"at {self._value(item, 'institution')}"
                )

        if resume.experience:
            lines.append("Experience:")
            for item in resume.experience:
                lines.append(
                    "- "
                    f"{self._value(item, 'role')} at "
                    f"{self._value(item, 'company')}: "
                    f"{self._value(item, 'description')}"
                )

        if resume.projects:
            lines.append("Projects:")
            for item in resume.projects:
                lines.append(
                    "- "
                    f"{self._value(item, 'name')}: "
                    f"{self._value(item, 'description')}; "
                    f"technologies: {self._join(self._attr(item, 'technologies', []))}"
                )

        if resume.certifications:
            lines.append("Certifications:")
            for item in resume.certifications:
                lines.append(
                    "- "
                    f"{self._value(item, 'name')} "
                    f"({self._value(item, 'issuer')})"
                )

        lines.append("")
        return lines

    def _quality_section(self, result: AnalysisResult) -> list[str]:
        quality = result.resume_quality
        if quality is None:
            return []

        lines = [
            "CURRENT RESUME QUALITY",
            f"Overall score: {quality.overall_score:.1f}/100",
        ]

        for finding in quality.findings:
            lines.append(
                f"- [{finding.severity}] {finding.title}: "
                f"{finding.explanation}"
            )
            if finding.recommendation:
                lines.append(f"  Recommendation: {finding.recommendation}")

        lines.append("")
        return lines

    def _ats_section(self, result: AnalysisResult) -> list[str]:
        ats = result.ats_intelligence
        if ats is None:
            return []

        lines = [
            "ATS ANALYSIS",
            f"Overall score: {ats.overall_score:.1f}/100",
        ]

        for finding in ats.findings:
            lines.append(
                f"- [{finding.severity}] {finding.title}: "
                f"{finding.explanation}"
            )
            if finding.recommendation:
                lines.append(f"  Recommendation: {finding.recommendation}")

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
                lines.append(f"  Recommendation: {issue.recommendation}")

        lines.append("")
        return lines

    def _career_section(self, result: AnalysisResult) -> list[str]:
        career = result.career_intelligence
        if career is None:
            return []

        lines = [
            "CAREER FIT",
            f"Inferred profile: {career.inferred_profile or 'Not provided'}",
            f"Experience level: {career.experience_level}",
            f"Primary domains: {self._join(career.primary_domains)}",
            f"Secondary domains: {self._join(career.secondary_domains)}",
            f"Transferable skills: {self._join(career.transferable_skills)}",
        ]

        if career.role_fit:
            lines.append("Role fit:")
            for role in career.role_fit:
                lines.append(
                    f"- {role.role}: {role.fit_score:.1f}/100 "
                    f"({role.direction}) — {role.rationale}"
                )

        if career.career_directions:
            lines.append("Career directions:")
            for direction in career.career_directions:
                lines.append(
                    f"- {direction.role}: {direction.fit_score:.1f}/100 "
                    f"({direction.direction}) — {direction.rationale}"
                )

        if career.limitations:
            lines.append(f"Limitations: {self._join(career.limitations)}")

        if career.risks:
            lines.append(f"Risks: {self._join(career.risks)}")

        lines.append("")
        return lines

    def _job_match_section(self, result: AnalysisResult) -> list[str]:
        job = result.job_profile
        if job is None:
            return []

        analysis = result.skill_analysis

        lines = [
            "JOB MATCH ANALYSIS",
            f"Target job: {job.job_title or 'Not provided'}",
            f"Target company: {job.company or 'Not provided'}",
        ]

        if result.scoring is not None:
            lines.append(
                f"Overall fit score: {result.scoring.overall_score:.1f}/100"
            )
            lines.append(
                f"Skill score: {result.scoring.skill_score:.1f}/100"
            )
            lines.append(
                "Required skill score: "
                f"{result.scoring.required_skill_score:.1f}/100"
            )
            lines.append(
                "Preferred skill score: "
                f"{result.scoring.preferred_skill_score:.1f}/100"
            )
            lines.append(
                f"Experience alignment: "
                f"{result.scoring.experience_score:.1f}/100"
            )
            lines.append(
                f"Education alignment: "
                f"{result.scoring.education_score:.1f}/100"
            )
            lines.append(
                f"Domain alignment: "
                f"{result.scoring.domain_score:.1f}/100"
            )

        lines.extend(
            [
                f"Required skills: {self._join(job.required_skills)}",
                f"Preferred skills: {self._join(job.preferred_skills)}",
                f"Matched skills: {self._join(analysis.matched_skills)}",
                f"Partial matches: {self._join(analysis.partial_matches)}",
                f"Missing skills: {self._join(analysis.missing_skills)}",
                (
                    "Transferable skills: "
                    f"{self._join(analysis.transferable_skills)}"
                ),
            ]
        )

        if result.matching is not None:
            lines.append("Requirement alignments:")
            for alignment in result.matching.requirement_alignments:
                lines.append(
                    f"- {alignment.requirement_id}: {alignment.status}"
                    + (
                        f" — {alignment.rationale}"
                        if alignment.rationale
                        else ""
                    )
                )

        if result.scoring is not None:
            if result.scoring.penalties:
                lines.append("Scoring penalties:")
                for penalty in result.scoring.penalties:
                    lines.append(
                        f"- {penalty.reason}: {penalty.value:+.1f}"
                    )

            if result.scoring.bonuses:
                lines.append("Scoring bonuses:")
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

        for recommendation in result.recommendations:
            target = (
                f" — target skill: {recommendation.target_skill}"
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

        lines = [
            "EVIDENCE-BACKED EXPLANATIONS",
            f"Overall explanation: {xai.overall_explanation}",
            f"Score explanation: {xai.score_explanation}",
        ]

        if xai.strengths:
            lines.append(f"Strengths: {self._join(xai.strengths)}")

        if xai.weaknesses:
            lines.append(f"Weaknesses: {self._join(xai.weaknesses)}")

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
            "Do not invent skills.",
            "Do not invent achievements or metrics.",
            "Do not invent certifications.",
            "Do not invent education or experience.",
            "Preserve all verified factual information from the source resume.",
            "Clearly distinguish suggestions from verified facts.",
            "Only strengthen wording when the underlying claim is supported by the resume.",
            "",
        ]

    def _output_section(self) -> list[str]:
        return [
            "OUTPUT",
            (
                "Improve and customize the resume using the evidence above. "
                "Preserve factual accuracy, prioritize the highest-impact "
                "issues, improve clarity and ATS compatibility, and tailor "
                "wording to the target role when a job description is "
                "available."
            ),
        ]

    @staticmethod
    def _attr(obj: object, name: str, default: object = None) -> object:
        return getattr(obj, name, default)

    @classmethod
    def _value(cls, obj: object, name: str) -> str:
        value = cls._attr(obj, name)
        if value is None or value == "":
            return "Not provided"
        return str(value)

    @staticmethod
    def _join(values: object) -> str:
        if not values:
            return "Not provided"
        return ", ".join(str(value) for value in values)

    @staticmethod
    def _skills(skills: object) -> str:
        if not skills:
            return "Not provided"

        names: list[str] = []
        for skill in skills:
            display_name = getattr(skill, "display_name", None)
            canonical_name = getattr(skill, "canonical_name", None)
            names.append(str(display_name or canonical_name or skill))

        return ", ".join(names)
