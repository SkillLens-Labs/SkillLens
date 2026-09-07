from __future__ import annotations

from collections import Counter
import re

from backend.app.analysis.resume_structure import (
    ResumeSectionType,
    StructuredResume,
)
from backend.app.domain.confidence import Confidence, ConfidenceLevel
from backend.app.domain.evidence import Evidence, EvidenceSourceType
from backend.app.domain.resume import ResumeProfile
from backend.app.domain.resume_quality import (
    ResumeQualityDimension,
    ResumeQualityDimensionScore,
    ResumeQualityFinding,
    ResumeQualityResult,
    ResumeQualitySeverity,
)
class ResumeQualityAnalyzer:
    """Deterministic resume-quality analysis over Phase 3 canonical structures."""

    ENGINE_VERSION = "phase4-quality-v1"

    _WEIGHTS = {
        ResumeQualityDimension.STRUCTURE: 0.15,
        ResumeQualityDimension.COMPLETENESS: 0.20,
        ResumeQualityDimension.SKILLS_PRESENTATION: 0.15,
        ResumeQualityDimension.EXPERIENCE: 0.12,
        ResumeQualityDimension.EDUCATION: 0.10,
        ResumeQualityDimension.PROJECTS: 0.10,
        ResumeQualityDimension.CONTENT_QUALITY: 0.10,
        ResumeQualityDimension.CONSISTENCY: 0.08,
    }

    _STANDARD_SECTIONS = (
        ResumeSectionType.SUMMARY,
        ResumeSectionType.EXPERIENCE,
        ResumeSectionType.EDUCATION,
        ResumeSectionType.PROJECTS,
        ResumeSectionType.CERTIFICATIONS,
        ResumeSectionType.SKILLS,
    )

    def analyze(
        self,
        resume: StructuredResume,
        profile: ResumeProfile,
    ) -> ResumeQualityResult:
        findings: list[ResumeQualityFinding] = []
        scores: dict[ResumeQualityDimension, float] = {}

        scores[ResumeQualityDimension.STRUCTURE] = self._analyze_structure(
            resume, findings
        )
        scores[ResumeQualityDimension.COMPLETENESS] = self._analyze_completeness(
            resume, profile, findings
        )
        scores[ResumeQualityDimension.SKILLS_PRESENTATION] = (
            self._analyze_skills(resume, profile, findings)
        )
        scores[ResumeQualityDimension.EXPERIENCE] = self._analyze_experience(
            resume, profile, findings
        )
        scores[ResumeQualityDimension.EDUCATION] = self._analyze_education(
            resume, profile, findings
        )
        scores[ResumeQualityDimension.PROJECTS] = self._analyze_projects(
            resume, profile, findings
        )
        scores[ResumeQualityDimension.CONTENT_QUALITY] = (
            self._analyze_content_quality(resume, findings)
        )
        scores[ResumeQualityDimension.CONSISTENCY] = self._analyze_consistency(
            resume, findings
        )

        overall = sum(
            scores[dimension] * weight
            for dimension, weight in self._WEIGHTS.items()
        )

        confidence = self._analysis_confidence(resume, findings)

        return ResumeQualityResult(
            overall_score=round(overall, 2),
            dimension_scores=[
                ResumeQualityDimensionScore(
                    dimension=dimension,
                    score=round(scores[dimension], 2),
                    weight=weight,
                )
                for dimension, weight in self._WEIGHTS.items()
            ],
            findings=findings,
            confidence=confidence,
            warnings=self._warnings(resume),
        )

    def _analyze_structure(
        self,
        resume: StructuredResume,
        findings: list[ResumeQualityFinding],
    ) -> float:
        sections = resume.sections
        if not sections:
            self._add_finding(
                findings,
                resume,
                ResumeQualityDimension.STRUCTURE,
                ResumeQualitySeverity.HIGH,
                "No recognizable resume structure",
                "No structural sections were detected in the parsed resume.",
                "Ensure the resume uses clear, recognizable section headings.",
            )
            return 20.0

        recognized = sum(
            section.section_type != ResumeSectionType.UNKNOWN
            for section in sections
        )
        score = 60.0 + min(30.0, recognized / max(len(sections), 1) * 30.0)

        unknown_sections = [
            section for section in sections
            if section.section_type == ResumeSectionType.UNKNOWN
        ]
        if unknown_sections:
            score -= min(20.0, len(unknown_sections) * 5.0)
            self._add_finding(
                findings,
                resume,
                ResumeQualityDimension.STRUCTURE,
                ResumeQualitySeverity.LOW,
                "Ambiguous section structure",
                f"{len(unknown_sections)} section heading(s) could not be classified.",
                "Use conventional, descriptive section headings.",
                evidence_sections=unknown_sections,
            )

        return max(0.0, min(100.0, score))

    def _analyze_completeness(
        self,
        resume: StructuredResume,
        profile: ResumeProfile,
        findings: list[ResumeQualityFinding],
    ) -> float:
        present = {
            section.section_type
            for section in resume.sections
            if section.section_type in self._STANDARD_SECTIONS
            and self._section_has_content(section)
        }

        score = 100.0
        missing = []

        for section_type in self._STANDARD_SECTIONS:
            if section_type not in present:
                missing.append(section_type)

        for section_type in missing:
            score -= 100.0 / len(self._STANDARD_SECTIONS)
            if section_type in {
                ResumeSectionType.SUMMARY,
                ResumeSectionType.SKILLS,
            }:
                severity = ResumeQualitySeverity.MEDIUM
            else:
                severity = ResumeQualitySeverity.LOW

            self._add_finding(
                findings,
                resume,
                ResumeQualityDimension.COMPLETENESS,
                severity,
                f"Missing {section_type.value} section",
                f"No non-empty {section_type.value} section was detected.",
                f"Consider adding a clear {section_type.value} section when applicable.",
                evidence_sections=list(resume.sections),
            )

        if profile.contact is None:
            self._add_finding(
                findings,
                resume,
                ResumeQualityDimension.COMPLETENESS,
                ResumeQualitySeverity.MEDIUM,
                "Contact/header information not available",
                "No header content was available in the canonical resume profile.",
                "Place clear contact information in the resume header.",
            )
            score -= 10.0
        elif not self._header_has_text(resume):
            score -= 10.0

        return max(0.0, min(100.0, score))

    def _analyze_skills(
        self,
        resume: StructuredResume,
        profile: ResumeProfile,
        findings: list[ResumeQualityFinding],
    ) -> float:
        skills_sections = resume.sections_of(ResumeSectionType.SKILLS)

        if not skills_sections:
            if profile.skills:
                self._add_finding(
                    findings,
                    resume,
                    ResumeQualityDimension.SKILLS_PRESENTATION,
                    ResumeQualitySeverity.INFO,
                    "Skills are detectable without an explicit skills section",
                    "Skills were preserved in the canonical profile even though no dedicated skills section was detected.",
                    "Use a clearly labeled skills section to improve organization and detectability.",
                )
                return 65.0

            self._add_finding(
                findings,
                resume,
                ResumeQualityDimension.SKILLS_PRESENTATION,
                ResumeQualitySeverity.MEDIUM,
                "No identifiable skills presentation",
                "No explicit skills section or extracted skills were available.",
                "Present relevant skills in a dedicated, clearly labeled section.",
            )
            return 35.0

        score = 80.0

        # ResumeProfileBuilder intentionally deduplicates canonical skills.
        # Repeated mentions therefore have to be detected from preserved
        # Skill.evidence rather than from profile.skills itself.
        repeated_skills = [
            skill for skill in profile.skills
            if len(skill.evidence) > 1
        ]

        if repeated_skills:
            score -= min(10.0, len(repeated_skills) * 2.0)
            evidence = [
                item
                for skill in repeated_skills
                for item in skill.evidence
            ]

            finding = self._finding(
                resume,
                ResumeQualityDimension.SKILLS_PRESENTATION,
                ResumeQualitySeverity.LOW,
                "Repeated skills detected",
                (
                    f"{len(repeated_skills)} canonical skill(s) have multiple "
                    "preserved source mentions in the resume."
                ),
                "Consolidate duplicate skill mentions where appropriate.",
                evidence_sections=skills_sections,
            )

            # Prefer the precise preserved skill evidence over whole-section
            # evidence for this finding.
            finding.evidence = evidence
            findings.append(finding)

        if not profile.skills:
            score -= 20.0
            self._add_finding(
                findings,
                resume,
                ResumeQualityDimension.SKILLS_PRESENTATION,
                ResumeQualitySeverity.MEDIUM,
                "Skills section contains no extracted skills",
                "An explicit skills section was detected, but no skills were extracted by the existing deterministic skill pipeline.",
                "Use explicit, recognizable skill names and avoid relying only on graphics or decorative formatting.",
                evidence_sections=skills_sections,
            )

        explicit_skill_evidence = sum(
            1
            for skill in profile.skills
            for evidence in skill.evidence
            if evidence.section == ResumeSectionType.SKILLS.value
        )
        contextual_skill_evidence = sum(
            1
            for skill in profile.skills
            for evidence in skill.evidence
            if evidence.section != ResumeSectionType.SKILLS.value
        )

        if profile.skills and not explicit_skill_evidence:
            score -= 5.0
            self._add_finding(
                findings,
                resume,
                ResumeQualityDimension.SKILLS_PRESENTATION,
                ResumeQualitySeverity.INFO,
                "Skills are primarily contextually detected",
                "Extracted skills are supported by resume content, but no preserved skill evidence originates from the explicit skills section.",
                "Keep important skills explicitly listed as well as demonstrated in experience or project evidence.",
                evidence_sections=skills_sections,
            )

        if profile.skills and contextual_skill_evidence == 0:
            self._add_finding(
                findings,
                resume,
                ResumeQualityDimension.SKILLS_PRESENTATION,
                ResumeQualitySeverity.INFO,
                "Limited contextual skill evidence",
                "The canonical skill profile contains skills without additional preserved contextual evidence outside the skills section.",
                "Where applicable, demonstrate important skills through experience or project evidence.",
                evidence_sections=skills_sections,
            )

        return max(0.0, min(100.0, score))

    def _analyze_experience(
        self,
        resume: StructuredResume,
        profile: ResumeProfile,
        findings: list[ResumeQualityFinding],
    ) -> float:
        sections = resume.sections_of(ResumeSectionType.EXPERIENCE)
        if not sections:
            return 75.0

        score = 80.0
        content_blocks = [
            block
            for section in sections
            for block in section.blocks
            if block.text.strip()
        ]

        if not content_blocks:
            self._add_finding(
                findings,
                resume,
                ResumeQualityDimension.EXPERIENCE,
                ResumeQualitySeverity.MEDIUM,
                "Experience section is empty",
                "An experience heading was detected without supporting content.",
                "Add role, organization, dates, and concise evidence-based descriptions where applicable.",
                evidence_sections=sections,
            )
            return 40.0

        descriptive_blocks = [
            block for block in content_blocks
            if len(block.text.split()) >= 8
        ]
        date_blocks = [
            block for block in content_blocks
            if re.search(
                r"\b(?:19|20)\d{2}\b|"
                r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)",
                block.text.lower(),
            )
        ]

        if len(content_blocks) == 1 and len(content_blocks[0].text.strip()) < 40:
            score -= 20.0
            self._add_finding(
                findings,
                resume,
                ResumeQualityDimension.EXPERIENCE,
                ResumeQualitySeverity.LOW,
                "Limited experience detail",
                "The detected experience content is very short.",
                "Add concise, evidence-based descriptions of responsibilities or outcomes.",
                evidence_sections=sections,
            )

        if not descriptive_blocks:
            score -= 10.0
            self._add_finding(
                findings,
                resume,
                ResumeQualityDimension.EXPERIENCE,
                ResumeQualitySeverity.LOW,
                "Limited experience descriptions",
                "No sufficiently descriptive experience block was detected.",
                "Use concise descriptions that communicate responsibilities, contributions, or outcomes.",
                evidence_sections=sections,
            )

        if not date_blocks:
            score -= 5.0
            self._add_finding(
                findings,
                resume,
                ResumeQualityDimension.EXPERIENCE,
                ResumeQualitySeverity.INFO,
                "Experience dates not clearly detected",
                "No recognizable year or month pattern was detected in the experience section.",
                "Include consistent employment dates where applicable.",
                evidence_sections=sections,
            )

        if not profile.experience:
            findings.append(
                self._finding(
                    resume,
                    ResumeQualityDimension.EXPERIENCE,
                    ResumeQualitySeverity.INFO,
                    "Experience structure is not yet available",
                    "An experience section is present, but Phase 3 does not currently populate structured experience entries.",
                    "Do not infer missing employment facts from this limitation.",
                    evidence_sections=sections,
                )
            )

        return max(0.0, min(100.0, score))

    def _analyze_education(
        self,
        resume: StructuredResume,
        profile: ResumeProfile,
        findings: list[ResumeQualityFinding],
    ) -> float:
        sections = resume.sections_of(ResumeSectionType.EDUCATION)
        if not sections:
            return 75.0

        score = 80.0
        content_blocks = [
            block
            for section in sections
            for block in section.blocks
            if block.text.strip()
        ]

        if not content_blocks:
            self._add_finding(
                findings,
                resume,
                ResumeQualityDimension.EDUCATION,
                ResumeQualitySeverity.MEDIUM,
                "Education section is empty",
                "An education heading was detected without supporting content.",
                "Add institution, degree or qualification, and dates where applicable.",
                evidence_sections=sections,
            )
            return 40.0

        degree_like = [
            block for block in content_blocks
            if re.search(
                r"\b(?:b\.?e\.?|b\.?tech\.?|m\.?e\.?|m\.?tech\.?|"
                r"bachelor|master|ph\.?d|diploma|degree|bsc|msc)\b",
                block.text.lower(),
            )
        ]
        date_like = [
            block for block in content_blocks
            if re.search(r"\b(?:19|20)\d{2}\b", block.text)
        ]

        if not degree_like:
            score -= 10.0
            self._add_finding(
                findings,
                resume,
                ResumeQualityDimension.EDUCATION,
                ResumeQualitySeverity.LOW,
                "Education qualification not clearly detected",
                "The education section is present, but no common degree or qualification pattern was detected.",
                "State the degree or qualification clearly.",
                evidence_sections=sections,
            )

        if not date_like:
            score -= 5.0
            self._add_finding(
                findings,
                resume,
                ResumeQualityDimension.EDUCATION,
                ResumeQualitySeverity.INFO,
                "Education dates not clearly detected",
                "No recognizable year pattern was detected in the education section.",
                "Include consistent dates where applicable.",
                evidence_sections=sections,
            )

        if not profile.education:
            findings.append(
                self._finding(
                    resume,
                    ResumeQualityDimension.EDUCATION,
                    ResumeQualitySeverity.INFO,
                    "Education structure is not yet available",
                    "An education section is present, but Phase 3 does not currently populate structured education entries.",
                    "Do not interpret this as proof that education information is absent.",
                    evidence_sections=sections,
                )
            )

        return max(0.0, min(100.0, score))

    def _analyze_projects(
        self,
        resume: StructuredResume,
        profile: ResumeProfile,
        findings: list[ResumeQualityFinding],
    ) -> float:
        sections = resume.sections_of(ResumeSectionType.PROJECTS)
        if not sections:
            return 75.0

        score = 80.0
        content_blocks = [
            block
            for section in sections
            for block in section.blocks
            if block.text.strip()
        ]

        if not content_blocks:
            self._add_finding(
                findings,
                resume,
                ResumeQualityDimension.PROJECTS,
                ResumeQualitySeverity.LOW,
                "Projects section is empty",
                "A projects heading was detected without supporting content.",
                "Add project titles, descriptions, and technologies where applicable.",
                evidence_sections=sections,
            )
            return 40.0

        description_blocks = [
            block for block in content_blocks
            if len(block.text.split()) >= 8
        ]

        if not description_blocks:
            score -= 10.0
            self._add_finding(
                findings,
                resume,
                ResumeQualityDimension.PROJECTS,
                ResumeQualitySeverity.LOW,
                "Project descriptions are limited",
                "Project content was detected, but no sufficiently descriptive project text was found.",
                "Add concise descriptions explaining what was built or accomplished.",
                evidence_sections=sections,
            )

        technology_like = [
            block for block in content_blocks
            if re.search(
                r"\b(?:python|java|javascript|typescript|react|sql|"
                r"docker|kubernetes|aws|azure|tensorflow|pytorch)\b",
                block.text.lower(),
            )
        ]

        if not technology_like:
            self._add_finding(
                findings,
                resume,
                ResumeQualityDimension.PROJECTS,
                ResumeQualitySeverity.INFO,
                "Project technologies not clearly detected",
                "No common technology pattern was detected in the project section.",
                "Name relevant technologies or skills when applicable.",
                evidence_sections=sections,
            )

        if not profile.projects:
            findings.append(
                self._finding(
                    resume,
                    ResumeQualityDimension.PROJECTS,
                    ResumeQualitySeverity.INFO,
                    "Project structure is not yet available",
                    "A projects section is present, but Phase 3 does not currently populate structured project entries.",
                    "Do not interpret this as proof that projects are absent.",
                    evidence_sections=sections,
                )
            )

        return max(0.0, min(100.0, score))

    def _analyze_content_quality(
        self,
        resume: StructuredResume,
        findings: list[ResumeQualityFinding],
    ) -> float:
        text = "\n".join(
            block.text.strip()
            for section in resume.sections
            for block in section.blocks
            if block.text.strip()
        )

        if not text:
            self._add_finding(
                findings,
                resume,
                ResumeQualityDimension.CONTENT_QUALITY,
                ResumeQualitySeverity.HIGH,
                "Very little resume text detected",
                "The parsed resume contains no meaningful body text.",
                "Ensure the document contains selectable, machine-readable text.",
            )
            return 20.0

        word_count = len(text.split())
        if word_count < 80:
            self._add_finding(
                findings,
                resume,
                ResumeQualityDimension.CONTENT_QUALITY,
                ResumeQualitySeverity.LOW,
                "Very short resume content",
                f"Only approximately {word_count} words were detected.",
                "Add relevant evidence and detail without unnecessary filler.",
            )
            return 65.0

        if word_count > 2500:
            self._add_finding(
                findings,
                resume,
                ResumeQualityDimension.CONTENT_QUALITY,
                ResumeQualitySeverity.MEDIUM,
                "Very long resume content",
                f"Approximately {word_count} words were detected.",
                "Remove redundant or low-value content and prioritize relevant evidence.",
            )
            return 65.0

        return 90.0

    def _analyze_consistency(
        self,
        resume: StructuredResume,
        findings: list[ResumeQualityFinding],
    ) -> float:
        headings = [
            section.heading.strip()
            for section in resume.sections
            if section.heading and section.heading.strip()
        ]
        normalized = [" ".join(heading.lower().split()) for heading in headings]

        duplicates = {
            heading
            for heading, count in Counter(normalized).items()
            if count > 1
        }

        aliases = {
            "summary": "summary",
            "professional summary": "summary",
            "profile": "summary",
            "professional profile": "summary",
            "experience": "experience",
            "work experience": "experience",
            "employment": "experience",
            "education": "education",
            "academic background": "education",
            "projects": "projects",
            "project experience": "projects",
            "skills": "skills",
            "technical skills": "skills",
            "certifications": "certifications",
            "certificates": "certifications",
        }

        canonical_groups = [
            aliases[heading]
            for heading in normalized
            if heading in aliases
        ]

        conflicting_aliases = {
            group
            for group, count in Counter(canonical_groups).items()
            if count > 1 and group not in duplicates
        }

        score = 95.0

        if duplicates:
            score -= 20.0
            self._add_finding(
                findings,
                resume,
                ResumeQualityDimension.CONSISTENCY,
                ResumeQualitySeverity.LOW,
                "Repeated section headings detected",
                "The same normalized section heading appears more than once.",
                "Consolidate repeated sections when they represent the same information.",
            )

        if conflicting_aliases:
            score -= min(15.0, len(conflicting_aliases) * 5.0)
            self._add_finding(
                findings,
                resume,
                ResumeQualityDimension.CONSISTENCY,
                ResumeQualitySeverity.INFO,
                "Multiple equivalent section names detected",
                "Multiple headings appear to represent the same standard section using different naming conventions.",
                "Use consistent section naming throughout the resume.",
            )

        return max(0.0, min(100.0, score))

    @staticmethod
    def _section_has_content(section) -> bool:
        return any(block.text.strip() for block in section.blocks)

    @staticmethod
    def _header_has_text(resume: StructuredResume) -> bool:
        return any(
            block.text.strip()
            for section in resume.sections_of(ResumeSectionType.HEADER)
            for block in section.blocks
        )

    def _add_finding(
        self,
        findings: list[ResumeQualityFinding],
        resume: StructuredResume,
        category: ResumeQualityDimension,
        severity: ResumeQualitySeverity,
        title: str,
        explanation: str,
        recommendation: str | None,
        evidence_sections=None,
    ) -> None:
        findings.append(
            self._finding(
                resume,
                category,
                severity,
                title,
                explanation,
                recommendation,
                evidence_sections=evidence_sections,
            )
        )

    def _finding(
        self,
        resume: StructuredResume,
        category: ResumeQualityDimension,
        severity: ResumeQualitySeverity,
        title: str,
        explanation: str,
        recommendation: str | None,
        evidence_sections=None,
    ) -> ResumeQualityFinding:
        evidence = self._section_evidence(resume, evidence_sections)

        return ResumeQualityFinding(
            finding_id=self._finding_id(
                resume.document_id,
                category,
                title,
            ),
            category=category,
            severity=severity,
            title=title,
            explanation=explanation,
            recommendation=recommendation,
            evidence=evidence,
            confidence=self._finding_confidence(evidence),
        )

    @staticmethod
    def _section_evidence(resume, sections) -> list[Evidence]:
        if not sections:
            return []

        evidence: list[Evidence] = []
        for section in sections:
            for block in section.blocks:
                text = block.text.strip()
                if not text:
                    continue
                source = block.source
                evidence.append(
                    Evidence(
                        evidence_id=(
                            f"quality-evidence-{resume.document_id}-"
                            f"{source.block_index if source.block_index is not None else len(evidence)}"
                        ),
                        source_type=EvidenceSourceType.RESUME,
                        source_document_id=resume.document_id,
                        section=section.section_type.value,
                        text=text,
                        evidence_type="resume_quality",
                        extractor="resume_quality_analyzer",
                        relevance=1.0,
                        confidence=1.0,
                    )
                )
        return evidence

    @staticmethod
    def _finding_id(
        document_id: str,
        category: ResumeQualityDimension,
        title: str,
    ) -> str:
        import hashlib

        digest = hashlib.sha256(
            f"{document_id}:{category.value}:{title}".encode("utf-8")
        ).hexdigest()[:16]
        return f"quality_{digest}"

    @staticmethod
    def _finding_confidence(evidence: list[Evidence]) -> Confidence:
        score = 0.95 if evidence else 0.80
        return Confidence(
            score=score,
            level=(
                ConfidenceLevel.HIGH
                if score >= 0.85
                else ConfidenceLevel.MEDIUM
            ),
            components={
                "source_evidence": 1.0 if evidence else 0.0,
                "rule_determinism": 1.0,
            },
            rationale=(
                "Confidence reflects deterministic rule evaluation and "
                "availability of source evidence."
            ),
        )

    @staticmethod
    def _analysis_confidence(
        resume: StructuredResume,
        findings: list[ResumeQualityFinding],
    ) -> Confidence:
        block_count = sum(
            len(section.blocks) for section in resume.sections
        )

        if block_count >= 8:
            score = 0.95
        elif block_count >= 3:
            score = 0.90
        elif block_count > 0:
            score = 0.80
        else:
            score = 0.60

        return Confidence(
            score=score,
            level=(
                ConfidenceLevel.HIGH
                if score >= 0.85
                else ConfidenceLevel.MEDIUM
                if score >= 0.65
                else ConfidenceLevel.LOW
            ),
            components={
                "structural_coverage": min(block_count / 8.0, 1.0),
                "rule_determinism": 1.0,
            },
            rationale=(
                "Analytical confidence is separate from Phase 3 extraction "
                "and ESCO-mapping confidence."
            ),
        )

    @staticmethod
    def _warnings(resume: StructuredResume) -> list[str]:
        warnings: list[str] = []

        block_count = sum(len(section.blocks) for section in resume.sections)
        if block_count == 0:
            warnings.append("No resume content blocks were available.")

        if len(resume.sections) > 20:
            warnings.append("Unusually fragmented resume structure detected.")

        return warnings
