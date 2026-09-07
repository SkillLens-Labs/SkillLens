from __future__ import annotations

import hashlib
import re
from collections import Counter
from typing import Iterable

from backend.app.domain.ats_intelligence import (
    ATSIntelligenceDimension,
    ATSIntelligenceDimensionScore,
    ATSIntelligenceFinding,
    ATSIntelligenceResult,
    ATSIntelligenceSeverity,
)
from backend.app.domain.confidence import Confidence, ConfidenceLevel
from backend.app.domain.evidence import Evidence, EvidenceSourceType
from backend.app.domain.resume import ResumeProfile
from backend.app.infrastructure.parsers.models import (
    DocumentBlock,
    DocumentBlockType,
    ParsedDocument,
)
from backend.app.analysis.resume_structure import (
    ResumeSectionType,
    StructuredResume,
)


class ATSIntelligenceAnalyzer:
    """Deterministic ATS-oriented analysis over canonical document structures."""

    ENGINE_VERSION = "phase4-ats-v1"

    _WEIGHTS = {
        ATSIntelligenceDimension.MACHINE_READABILITY: 0.15,
        ATSIntelligenceDimension.SECTION_DETECTABILITY: 0.15,
        ATSIntelligenceDimension.TEXT_EXTRACTION: 0.15,
        ATSIntelligenceDimension.HEADING_CLARITY: 0.10,
        ATSIntelligenceDimension.SKILL_DETECTABILITY: 0.15,
        ATSIntelligenceDimension.CONTACT_DETECTABILITY: 0.10,
        ATSIntelligenceDimension.FORMATTING_RISK: 0.10,
        ATSIntelligenceDimension.CONTENT_REDUNDANCY: 0.05,
        ATSIntelligenceDimension.STANDARD_INFORMATION: 0.05,
    }

    _STANDARD_SECTIONS = {
        ResumeSectionType.SUMMARY,
        ResumeSectionType.EXPERIENCE,
        ResumeSectionType.EDUCATION,
        ResumeSectionType.PROJECTS,
        ResumeSectionType.CERTIFICATIONS,
        ResumeSectionType.SKILLS,
    }

    _SECTION_ALIASES = {
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

    _REPLACEMENT_CHARS = ("�",)
    _DECORATIVE_CHARS = set("★☆◆◇●○■□►▸➤✦✧")
    _DATE_PATTERN = re.compile(
        r"\b(?:19|20)\d{2}\b|\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|"
        r"oct|nov|dec)[a-z]*\b",
        re.IGNORECASE,
    )

    def analyze(
        self,
        document: ParsedDocument,
        resume: StructuredResume,
        profile: ResumeProfile,
    ) -> ATSIntelligenceResult:
        findings: list[ATSIntelligenceFinding] = []

        scores = {
            ATSIntelligenceDimension.MACHINE_READABILITY: self._machine_readability(
                document, findings
            ),
            ATSIntelligenceDimension.SECTION_DETECTABILITY: self._section_detectability(
                resume, findings
            ),
            ATSIntelligenceDimension.TEXT_EXTRACTION: self._text_extraction(
                document, findings
            ),
            ATSIntelligenceDimension.HEADING_CLARITY: self._heading_clarity(
                resume, findings
            ),
            ATSIntelligenceDimension.SKILL_DETECTABILITY: self._skill_detectability(
                resume, profile, findings
            ),
            ATSIntelligenceDimension.CONTACT_DETECTABILITY: self._contact_detectability(
                resume, profile, findings
            ),
            ATSIntelligenceDimension.FORMATTING_RISK: self._formatting_risk(
                document, findings
            ),
            ATSIntelligenceDimension.CONTENT_REDUNDANCY: self._content_redundancy(
                document, resume, findings
            ),
            ATSIntelligenceDimension.STANDARD_INFORMATION: self._standard_information(
                resume, profile, findings
            ),
        }

        dimension_scores = [
            ATSIntelligenceDimensionScore(
                dimension=dimension,
                score=max(0.0, min(100.0, score)),
                weight=weight,
            )
            for dimension, weight in self._WEIGHTS.items()
            for score in [scores[dimension]]
        ]

        overall_score = sum(
            item.score * item.weight for item in dimension_scores
        )

        confidence = self._analysis_confidence(document, resume)

        return ATSIntelligenceResult(
            overall_score=round(overall_score, 2),
            dimension_scores=dimension_scores,
            findings=findings,
            confidence=confidence,
            warnings=self._warnings(document, resume),
        )

    def _machine_readability(
        self,
        document: ParsedDocument,
        findings: list[ATSIntelligenceFinding],
    ) -> float:
        blocks = list(document.blocks)

        if not blocks:
            self._add_finding(
                findings,
                document.document_id,
                "machine_readability",
                ATSIntelligenceSeverity.HIGH,
                "No readable document blocks",
                "The parsed document contains no readable blocks for ATS-style processing.",
                "Provide a text-readable PDF or DOCX document.",
                [],
            )
            return 20.0

        non_empty = [block for block in blocks if block.text.strip()]
        score = 100.0 * len(non_empty) / len(blocks)

        if len(non_empty) < 3:
            score -= 30
            self._add_finding(
                findings,
                document.document_id,
                "machine_readability",
                ATSIntelligenceSeverity.MEDIUM,
                "Very limited readable content",
                "Only a small amount of non-empty document content was extracted.",
                "Use a text-based resume with clearly extractable content.",
                non_empty,
            )

        if not any(
            block.block_type
            in {
                DocumentBlockType.PARAGRAPH,
                DocumentBlockType.HEADING,
                DocumentBlockType.BULLET,
                DocumentBlockType.TABLE_CELL,
            }
            for block in non_empty
        ):
            score -= 20

        return max(0.0, score)

    def _section_detectability(
        self,
        resume: StructuredResume,
        findings: list[ATSIntelligenceFinding],
    ) -> float:
        recognized = [
            section
            for section in resume.sections
            if section.section_type != ResumeSectionType.UNKNOWN
            and any(block.text.strip() for block in section.blocks)
        ]

        unknown = [
            section
            for section in resume.sections
            if section.section_type == ResumeSectionType.UNKNOWN
        ]

        score = 100.0

        if not recognized:
            score = 35.0
            self._add_finding(
                findings,
                resume.document_id,
                "section_detectability",
                ATSIntelligenceSeverity.HIGH,
                "Standard sections are not clearly detectable",
                "No recognized standard resume sections were identified by the existing structure interpreter.",
                "Use clear, conventional section headings.",
                [block for section in resume.sections for block in section.blocks],
            )
        else:
            missing = self._STANDARD_SECTIONS - {
                section.section_type for section in recognized
            }
            score -= min(45.0, len(missing) * 7.5)

        if unknown:
            score -= min(25.0, len(unknown) * 5.0)
            self._add_finding(
                findings,
                resume.document_id,
                "section_detectability",
                ATSIntelligenceSeverity.LOW,
                "Unrecognized section headings detected",
                f"{len(unknown)} section(s) could not be classified as standard resume sections.",
                "Prefer conventional section names when possible.",
                [block for section in unknown for block in section.blocks],
            )

        return max(0.0, score)

    def _text_extraction(
        self,
        document: ParsedDocument,
        findings: list[ATSIntelligenceFinding],
    ) -> float:
        blocks = list(document.blocks)
        if not blocks:
            return 20.0

        texts = [block.text for block in blocks]
        non_empty = [text.strip() for text in texts if text.strip()]
        score = 100.0

        empty_ratio = 1.0 - (len(non_empty) / len(texts))
        score -= min(30.0, empty_ratio * 40.0)

        replacement_count = sum(
            text.count(char)
            for text in texts
            for char in self._REPLACEMENT_CHARS
        )
        if replacement_count:
            score -= min(35.0, replacement_count * 5.0)
            self._add_finding(
                findings,
                document.document_id,
                "text_extraction",
                ATSIntelligenceSeverity.MEDIUM,
                "Suspicious extraction characters detected",
                "Replacement characters were found in extracted text, indicating possible extraction corruption.",
                "Verify the source document's text layer and export it again if necessary.",
                blocks,
            )

        repeated = [
            text
            for text, count in Counter(
                self._normalize_text(text) for text in non_empty
            ).items()
            if text and count > 1
        ]
        if repeated:
            score -= min(20.0, len(repeated) * 4.0)

        table_cells = sum(
            block.block_type == DocumentBlockType.TABLE_CELL for block in blocks
        )
        if table_cells:
            score -= min(10.0, table_cells * 0.5)

        return max(0.0, score)

    def _heading_clarity(
        self,
        resume: StructuredResume,
        findings: list[ATSIntelligenceFinding],
    ) -> float:
        headings = [
            section.heading.strip()
            for section in resume.sections
            if section.heading and section.heading.strip()
        ]

        if not headings:
            self._add_finding(
                findings,
                resume.document_id,
                "heading_clarity",
                ATSIntelligenceSeverity.HIGH,
                "No section headings detected",
                "The structured resume contains no usable section headings.",
                "Use short, conventional headings such as Experience, Education, Skills, and Projects.",
                [],
            )
            return 30.0

        score = 100.0
        normalized = [self._normalize_heading(heading) for heading in headings]
        counts = Counter(normalized)

        repeated = [heading for heading, count in counts.items() if count > 1]
        if repeated:
            score -= min(30.0, len(repeated) * 10.0)
            self._add_finding(
                findings,
                resume.document_id,
                "heading_clarity",
                ATSIntelligenceSeverity.LOW,
                "Repeated section headings detected",
                "The same normalized section heading appears more than once.",
                "Consolidate repeated sections where practical.",
                [
                    block
                    for section in resume.sections
                    if self._normalize_heading(section.heading or "") in repeated
                    for block in section.blocks
                ],
            )

        long_headings = [heading for heading in headings if len(heading) > 60]
        if long_headings:
            score -= min(20.0, len(long_headings) * 5.0)
            self._add_finding(
                findings,
                resume.document_id,
                "heading_clarity",
                ATSIntelligenceSeverity.LOW,
                "Unusually long section heading detected",
                "A section heading is substantially longer than a typical resume heading.",
                "Prefer concise section headings.",
                [
                    block
                    for section in resume.sections
                    if section.heading in long_headings
                    for block in section.blocks
                ],
            )

        return max(0.0, score)

    def _skill_detectability(
        self,
        resume: StructuredResume,
        profile: ResumeProfile,
        findings: list[ATSIntelligenceFinding],
    ) -> float:
        skill_sections = resume.sections_of(ResumeSectionType.SKILLS)
        skill_evidence = [
            evidence
            for skill in profile.skills
            for evidence in skill.evidence
        ]

        if not profile.skills:
            if skill_sections:
                self._add_finding(
                    findings,
                    resume.document_id,
                    "skill_detectability",
                    ATSIntelligenceSeverity.MEDIUM,
                    "Skills section has no canonically detected skills",
                    "A skills section exists, but Phase 3 did not produce canonical skill records from it.",
                    "Use explicit, recognizable skill names and verify extraction quality.",
                    [block for section in skill_sections for block in section.blocks],
                )
                return 45.0

            self._add_finding(
                findings,
                resume.document_id,
                "skill_detectability",
                ATSIntelligenceSeverity.MEDIUM,
                "No canonically detected skills",
                "No canonical skills are available from the existing skill intelligence pipeline.",
                "Present relevant skills using explicit and recognizable names.",
                [],
            )
            return 35.0

        score = 75.0

        explicit = [
            evidence
            for evidence in skill_evidence
            if evidence.section == ResumeSectionType.SKILLS.value
        ]
        contextual = [
            evidence
            for evidence in skill_evidence
            if evidence.section != ResumeSectionType.SKILLS.value
        ]

        if explicit:
            score += 15.0
        else:
            self._add_finding(
                findings,
                resume.document_id,
                "skill_detectability",
                ATSIntelligenceSeverity.INFO,
                "Skills are primarily contextually detected",
                "Canonical skills were detected, but no evidence was linked to an explicit Skills section.",
                "An explicit Skills section can improve direct skill detectability.",
                [
                    block
                    for section in resume.sections_of(ResumeSectionType.SKILLS)
                    for block in section.blocks
                ],
            )

        if contextual:
            score += 5.0

        if len(skill_evidence) >= 20:
            self._add_finding(
                findings,
                resume.document_id,
                "skill_detectability",
                ATSIntelligenceSeverity.LOW,
                "High volume of skill evidence",
                "Many skill evidence entries were detected across the resume.",
                "Avoid unnecessary repetition of the same skill across sections.",
                [],
            )

        return min(100.0, score)

    def _contact_detectability(
        self,
        resume: StructuredResume,
        profile: ResumeProfile,
        findings: list[ATSIntelligenceFinding],
    ) -> float:
        headers = resume.sections_of(ResumeSectionType.HEADER)
        header_blocks = [block for section in headers for block in section.blocks]
        header_text = "\n".join(block.text for block in header_blocks).strip()

        if not header_text:
            self._add_finding(
                findings,
                resume.document_id,
                "contact_detectability",
                ATSIntelligenceSeverity.HIGH,
                "Contact/header information is not detectable",
                "No usable header content was found in the parsed resume.",
                "Include clearly extractable name and contact information near the top of the resume.",
                header_blocks,
            )
            return 25.0

        score = 55.0

        email = re.search(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", header_text, re.I)
        phone = re.search(r"(?:\+?\d[\d\s().-]{7,}\d)", header_text)
        linkedin = re.search(r"linkedin\.com", header_text, re.I)
        github = re.search(r"github\.com", header_text, re.I)

        detected = sum(bool(value) for value in (email, phone, linkedin, github))
        score += min(40.0, detected * 10.0)

        if not detected:
            self._add_finding(
                findings,
                resume.document_id,
                "contact_detectability",
                ATSIntelligenceSeverity.MEDIUM,
                "Contact fields are not clearly detectable",
                "Header content exists, but common contact patterns were not detected.",
                "Use standard, text-readable email, phone, and professional profile formats.",
                header_blocks,
            )

        if profile.contact is None:
            score -= 10.0

        return max(0.0, min(100.0, score))

    def _formatting_risk(
        self,
        document: ParsedDocument,
        findings: list[ATSIntelligenceFinding],
    ) -> float:
        blocks = list(document.blocks)
        if not blocks:
            return 30.0

        score = 100.0
        table_cells = [
            block for block in blocks if block.block_type == DocumentBlockType.TABLE_CELL
        ]

        if table_cells:
            table_count = len({block.source.table_index for block in table_cells if block.source.table_index is not None})
            score -= min(35.0, table_count * 10.0)
            self._add_finding(
                findings,
                document.document_id,
                "formatting_risk",
                ATSIntelligenceSeverity.LOW,
                "Table-based layout detected",
                "Table cells are present in the parsed document and may introduce reading-order or layout risks for some ATS systems.",
                "Prefer simple linear layouts for critical resume information.",
                table_cells,
            )

        decorative = [
            block
            for block in blocks
            if any(char in block.text for char in self._DECORATIVE_CHARS)
        ]
        if decorative:
            score -= min(20.0, len(decorative) * 3.0)
            self._add_finding(
                findings,
                document.document_id,
                "formatting_risk",
                ATSIntelligenceSeverity.LOW,
                "Decorative symbols detected",
                "Decorative Unicode symbols appear in extracted resume content.",
                "Use restrained formatting and avoid relying on decorative symbols to convey structure.",
                decorative,
            )

        fragmented = [
            block
            for block in blocks
            if block.block_type == DocumentBlockType.PARAGRAPH
            and len(block.text.strip()) <= 2
        ]
        if len(fragmented) >= 5:
            score -= 15.0
            self._add_finding(
                findings,
                document.document_id,
                "formatting_risk",
                ATSIntelligenceSeverity.LOW,
                "Highly fragmented text blocks detected",
                "Many very short paragraph blocks may indicate a layout that fragments extracted text.",
                "Prefer straightforward text flow and avoid layout-dependent positioning.",
                fragmented,
            )

        return max(0.0, score)

    def _content_redundancy(
        self,
        document: ParsedDocument,
        resume: StructuredResume,
        findings: list[ATSIntelligenceFinding],
    ) -> float:
        texts = [
            self._normalize_text(block.text)
            for block in document.blocks
            if block.text.strip()
        ]

        counts = Counter(text for text in texts if len(text) >= 30)
        duplicates = {text: count for text, count in counts.items() if count > 1}

        score = 100.0
        if duplicates:
            duplicate_occurrences = sum(count - 1 for count in duplicates.values())
            score -= min(60.0, duplicate_occurrences * 15.0)

            duplicate_blocks = [
                block
                for block in document.blocks
                if self._normalize_text(block.text) in duplicates
            ]

            self._add_finding(
                findings,
                document.document_id,
                "content_redundancy",
                ATSIntelligenceSeverity.MEDIUM,
                "Repeated content detected",
                "One or more substantive extracted text blocks appear more than once.",
                "Remove duplicated descriptions or repeated content where it does not add information.",
                duplicate_blocks,
            )

        return max(0.0, score)

    def _standard_information(
        self,
        resume: StructuredResume,
        profile: ResumeProfile,
        findings: list[ATSIntelligenceFinding],
    ) -> float:
        present = {
            section.section_type
            for section in resume.sections
            if any(block.text.strip() for block in section.blocks)
        }

        missing = self._STANDARD_SECTIONS - present
        score = 100.0 - (len(missing) * 12.0)

        if ResumeSectionType.HEADER not in present:
            score -= 20.0

        if missing:
            self._add_finding(
                findings,
                resume.document_id,
                "standard_information",
                ATSIntelligenceSeverity.MEDIUM,
                "Standard resume information is missing",
                "One or more standard resume sections were not detected in the parsed document.",
                "Include applicable standard sections with clear headings.",
                [block for section in resume.sections for block in section.blocks],
            )

        if ResumeSectionType.HEADER in present and profile.contact is None:
            self._add_finding(
                findings,
                resume.document_id,
                "standard_information",
                ATSIntelligenceSeverity.INFO,
                "Header exists but contact structure is unavailable",
                "Header content is present, but the canonical Phase 3 profile does not contain a structured contact object.",
                "This is a structural availability limitation, not evidence that contact information is absent.",
                [
                    block
                    for section in resume.sections
                    if section.section_type == ResumeSectionType.HEADER
                    for block in section.blocks
                ],
            )

        return max(0.0, score)

    def _add_finding(
        self,
        findings: list[ATSIntelligenceFinding],
        document_id: str,
        category: str,
        severity: ATSIntelligenceSeverity,
        title: str,
        explanation: str,
        recommendation: str,
        blocks: Iterable[DocumentBlock],
    ) -> None:
        evidence = [
            self._evidence(document_id, block, category)
            for block in blocks
        ]

        findings.append(
            ATSIntelligenceFinding(
                finding_id=self._finding_id(document_id, category, title),
                category=category,
                severity=severity,
                title=title,
                explanation=explanation,
                recommendation=recommendation,
                evidence=evidence,
                confidence=self._finding_confidence(evidence),
            )
        )

    def _evidence(
        self,
        document_id: str,
        block: DocumentBlock,
        category: str,
    ) -> Evidence:
        return Evidence(
            evidence_id=hashlib.sha256(
                f"{document_id}:{category}:{block.source.block_index}:{block.text}".encode(
                    "utf-8"
                )
            ).hexdigest()[:16],
            source_type=EvidenceSourceType.RESUME,
            source_document_id=document_id,
            section=block.section,
            text=block.text,
            start_offset=None,
            end_offset=None,
            evidence_type="ats_intelligence",
            extractor="ats_intelligence_analyzer",
            relevance=1.0,
            confidence=0.95,
        )

    def _finding_id(self, document_id: str, category: str, title: str) -> str:
        return hashlib.sha256(
            f"{document_id}:{category}:{title}".encode("utf-8")
        ).hexdigest()[:16]

    def _finding_confidence(self, evidence: list[Evidence]) -> Confidence:
        score = 0.95 if evidence else 0.85
        level = (
            ConfidenceLevel.HIGH
            if score >= 0.9
            else ConfidenceLevel.MEDIUM
        )
        return Confidence(
            score=score,
            level=level,
            components={"evidence_support": score},
            rationale="Deterministic ATS rule supported by parsed resume structure."
            if evidence
            else "Deterministic ATS rule based on canonical resume structures.",
        )

    def _analysis_confidence(
        self,
        document: ParsedDocument,
        resume: StructuredResume,
    ) -> Confidence:
        block_count = len(document.blocks)
        section_count = len(resume.sections)

        if block_count >= 8:
            score = 0.95
        elif block_count >= 3:
            score = 0.90
        elif block_count > 0:
            score = 0.80
        else:
            score = 0.60

        if section_count == 0:
            score = min(score, 0.75)

        level = (
            ConfidenceLevel.HIGH
            if score >= 0.9
            else ConfidenceLevel.MEDIUM
            if score >= 0.75
            else ConfidenceLevel.LOW
        )

        return Confidence(
            score=score,
            level=level,
            components={
                "document_block_coverage": score,
                "section_structure": 0.95 if section_count else 0.60,
            },
            rationale="Analytical confidence reflects the amount of parsed and structured resume evidence available; it is distinct from extraction and mapping confidence.",
        )

    def _warnings(
        self,
        document: ParsedDocument,
        resume: StructuredResume,
    ) -> list[str]:
        warnings: list[str] = []

        if not document.blocks:
            warnings.append("ATS analysis is limited because no parsed document blocks are available.")

        if len(document.blocks) < 3:
            warnings.append("Very short extracted content may make ATS signals unreliable.")

        if len(document.blocks) > 250:
            warnings.append("Very large block count may reflect complex formatting or a long resume.")

        if len(resume.sections) > 20:
            warnings.append("Unusually high section count may indicate fragmented document structure.")

        warnings.append(
            "ATS intelligence is an analytical estimate and does not guarantee acceptance by any commercial ATS."
        )

        return warnings

    @staticmethod
    def _normalize_text(value: str) -> str:
        return re.sub(r"\s+", " ", value.strip().lower())

    @classmethod
    def _normalize_heading(cls, value: str) -> str:
        normalized = cls._normalize_text(value)
        return cls._SECTION_ALIASES.get(normalized, normalized)
