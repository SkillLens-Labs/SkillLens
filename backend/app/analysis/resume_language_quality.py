from __future__ import annotations

import re
from backend.app.analysis.resume_structure import StructuredResume
from backend.app.domain.confidence import Confidence, ConfidenceLevel
from backend.app.domain.evidence import Evidence, EvidenceSourceType
from backend.app.domain.language_quality import (
    AIAuthorshipHeuristic,
    LanguageIssue,
    LanguageIssueSeverity,
    LanguageIssueType,
    ResumeLanguageQualityResult,
)
from backend.app.infrastructure.parsers.models import ParsedDocument


class ResumeLanguageQualityAnalyzer:
    """
    Deterministic and conservative resume language-quality analyzer.

    This analyzer is intentionally heuristic. It does not attempt to replace
    a full grammar checker or claim factual AI-authorship detection.
    """

    ENGINE_VERSION = "phase9-language-quality-v1"

    COMMON_MISSPELLINGS = {
        "acheived": "achieved",
        "accomodate": "accommodate",
        "adress": "address",
        "analisis": "analysis",
        "calender": "calendar",
        "comming": "coming",
        "dependancy": "dependency",
        "enviroment": "environment",
        "experiance": "experience",
        "improvment": "improvement",
        "independant": "independent",
        "managment": "management",
        "occurence": "occurrence",
        "recieve": "receive",
        "seperated": "separated",
        "succesful": "successful",
        "sucess": "success",
        "teh": "the",
        "tommorow": "tomorrow",
        "treshold": "threshold",
        "wich": "which",
        "writting": "writing",
    }

    GENERIC_PHRASES = {
        "hard working",
        "hardworking",
        "team player",
        "quick learner",
        "responsible for",
        "worked on",
        "good communication skills",
        "excellent communication skills",
        "highly motivated",
        "self motivated",
        "detail oriented",
        "passionate about technology",
    }

    TERMINOLOGY_PATTERNS = {
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "node js": "Node.js",
        "nodejs": "Node.js",
        "reactjs": "React",
        "react js": "React",
        "postgres": "PostgreSQL",
        "mongo db": "MongoDB",
        "power bi": "Power BI",
        "machine learning": "Machine Learning",
        "artificial intelligence": "Artificial Intelligence",
    }

    def analyze(
        self,
        parsed_document: ParsedDocument,
        structured_resume: StructuredResume,
    ) -> ResumeLanguageQualityResult:
        text = parsed_document.text or ""

        issues: list[LanguageIssue] = []

        issues.extend(self._detect_spelling(text, parsed_document))
        issues.extend(self._detect_repeated_words(text, parsed_document))
        issues.extend(self._detect_generic_wording(text, parsed_document))
        issues.extend(self._detect_terminology(text, parsed_document))
        issues.extend(self._detect_formatting(text, parsed_document))

        authorship = self._build_authorship_heuristic(
            text=text,
            issue_count=len(issues),
            structured_resume=structured_resume,
        )

        overall_score = self._calculate_score(issues)

        confidence = self._build_confidence(
            text=text,
            issue_count=len(issues),
            structured_resume=structured_resume,
        )

        warnings: list[str] = []

        if not text.strip():
            warnings.append("No resume text was available for language-quality analysis.")

        warnings.append(
            "Language-quality findings are heuristic signals and should be reviewed "
            "before making edits."
        )

        return ResumeLanguageQualityResult(
            overall_score=overall_score,
            issues=issues,
            confidence=confidence,
            authorship_heuristic=authorship,
            warnings=warnings,
        )

    def _detect_spelling(
        self,
        text: str,
        parsed_document: ParsedDocument,
    ) -> list[LanguageIssue]:
        issues: list[LanguageIssue] = []
        lower_text = text.lower()

        for misspelling, correction in self.COMMON_MISSPELLINGS.items():
            pattern = rf"\b{re.escape(misspelling)}\b"
            match = re.search(pattern, lower_text)

            if not match:
                continue

            original = text[match.start() : match.end()]

            issues.append(
                self._issue(
                    issue_id=f"spelling-{misspelling}",
                    issue_type=LanguageIssueType.SPELLING,
                    severity=LanguageIssueSeverity.MEDIUM,
                    title=f"Possible spelling error: {original}",
                    explanation=f"'{original}' appears to be a common spelling error.",
                    recommendation=f"Consider replacing it with '{correction}'.",
                    original_text=original,
                    suggested_text=correction,
                    parsed_document=parsed_document,
                    evidence_type="spelling_signal",
                )
            )

        return issues

    def _detect_repeated_words(
        self,
        text: str,
        parsed_document: ParsedDocument,
    ) -> list[LanguageIssue]:
        issues: list[LanguageIssue] = []

        pattern = re.compile(r"\b([A-Za-z][A-Za-z'-]*)\s+\1\b", re.IGNORECASE)

        for index, match in enumerate(pattern.finditer(text), start=1):
            repeated = match.group(1)

            issues.append(
                self._issue(
                    issue_id=f"grammar-repeated-word-{index}",
                    issue_type=LanguageIssueType.GRAMMAR,
                    severity=LanguageIssueSeverity.MEDIUM,
                    title="Repeated consecutive word",
                    explanation=f"The word '{repeated}' appears consecutively.",
                    recommendation="Remove the unintended repeated word.",
                    original_text=match.group(0),
                    suggested_text=re.sub(
                        r"\s+",
                        " ",
                        repeated,
                    ),
                    parsed_document=parsed_document,
                    evidence_type="repeated_word",
                )
            )

        return issues

    def _detect_generic_wording(
        self,
        text: str,
        parsed_document: ParsedDocument,
    ) -> list[LanguageIssue]:
        issues: list[LanguageIssue] = []
        lower_text = text.lower()

        for phrase in sorted(self.GENERIC_PHRASES, key=len, reverse=True):
            if phrase not in lower_text:
                continue

            issues.append(
                self._issue(
                    issue_id=f"wording-{re.sub(r'[^a-z0-9]+', '-', phrase).strip('-')}",
                    issue_type=LanguageIssueType.WORDING,
                    severity=LanguageIssueSeverity.LOW,
                    title="Generic resume wording",
                    explanation=(
                        f"The phrase '{phrase}' is common in resumes and may provide "
                        "limited evidence of specific impact."
                    ),
                    recommendation=(
                        "Consider replacing generic wording with a concrete action, "
                        "technology, outcome, or measurable result where truthful."
                    ),
                    original_text=phrase,
                    parsed_document=parsed_document,
                    evidence_type="generic_resume_phrase",
                )
            )

        return issues

    def _detect_terminology(
        self,
        text: str,
        parsed_document: ParsedDocument,
    ) -> list[LanguageIssue]:
        issues: list[LanguageIssue] = []
        lower_text = text.lower()

        for variant, preferred in self.TERMINOLOGY_PATTERNS.items():
            if variant not in lower_text:
                continue

            issues.append(
                self._issue(
                    issue_id=f"terminology-{re.sub(r'[^a-z0-9]+', '-', variant).strip('-')}",
                    issue_type=LanguageIssueType.TERMINOLOGY,
                    severity=LanguageIssueSeverity.LOW,
                    title="Technology terminology formatting",
                    explanation=(
                        f"'{variant}' is commonly represented as '{preferred}' "
                        "in professional technical writing."
                    ),
                    recommendation=f"Consider using '{preferred}' consistently.",
                    original_text=variant,
                    suggested_text=preferred,
                    parsed_document=parsed_document,
                    evidence_type="technology_terminology",
                )
            )

        return issues

    def _detect_formatting(
        self,
        text: str,
        parsed_document: ParsedDocument,
    ) -> list[LanguageIssue]:
        issues: list[LanguageIssue] = []

        lines = [line.strip() for line in text.splitlines() if line.strip()]

        if not lines:
            return issues

        excessive_punctuation = re.search(r"[!?]{2,}|\.{4,}", text)
        if excessive_punctuation:
            issues.append(
                self._issue(
                    issue_id="formatting-excessive-punctuation",
                    issue_type=LanguageIssueType.FORMATTING,
                    severity=LanguageIssueSeverity.LOW,
                    title="Excessive punctuation",
                    explanation="Repeated punctuation can reduce professional readability.",
                    recommendation="Use standard punctuation consistently.",
                    original_text=excessive_punctuation.group(0),
                    parsed_document=parsed_document,
                    evidence_type="punctuation_pattern",
                )
            )

        return issues

    def _build_authorship_heuristic(
        self,
        text: str,
        issue_count: int,
        structured_resume: StructuredResume,
    ) -> AIAuthorshipHeuristic:
        """
        Estimate writing-style signals only.

        The score is deliberately not presented as an AI detector.
        """

        signals: list[str] = []
        score = 0.0

        sentences = [
            sentence.strip()
            for sentence in re.split(r"[.!?]+", text)
            if sentence.strip()
        ]

        if sentences:
            lengths = [len(sentence.split()) for sentence in sentences]
            average_length = sum(lengths) / len(lengths)

            if 14 <= average_length <= 24:
                score += 15
                signals.append("Relatively uniform professional sentence length.")

        lower_text = text.lower()

        generic_count = sum(
            1 for phrase in self.GENERIC_PHRASES if phrase in lower_text
        )

        if generic_count >= 2:
            score += 15
            signals.append("Multiple generic resume phrases detected.")

        if issue_count == 0 and len(text.split()) > 150:
            score += 10
            signals.append(
                "Longer text contains few detected surface-level language issues."
            )

        section_count = len(
            [
                section
                for section in structured_resume.sections
                if section.blocks
            ]
        )

        if section_count >= 5:
            score += 5
            signals.append("Resume uses a highly structured multi-section format.")

        score = min(score, 100.0)

        if score >= 60:
            level = "higher_style_signal"
        elif score >= 30:
            level = "moderate_style_signal"
        else:
            level = "lower_style_signal"

        return AIAuthorshipHeuristic(
            score=score,
            level=level,
            signals=signals,
        )

    def _calculate_score(self, issues: list[LanguageIssue]) -> float:
        penalties = {
            LanguageIssueSeverity.INFO: 0.5,
            LanguageIssueSeverity.LOW: 2.0,
            LanguageIssueSeverity.MEDIUM: 5.0,
            LanguageIssueSeverity.HIGH: 10.0,
        }

        penalty = sum(penalties[issue.severity] for issue in issues)

        return round(max(0.0, min(100.0, 100.0 - penalty)), 2)

    def _build_confidence(
        self,
        text: str,
        issue_count: int,
        structured_resume: StructuredResume,
    ) -> Confidence:
        word_count = len(text.split())

        # A minimum amount of text is sufficient for these deterministic
        # surface-level checks. Confidence should not collapse merely because
        # a test fixture or short resume is small.
        text_coverage = min(1.0, word_count / 120.0)

        structure_count = len(
            [
                section
                for section in structured_resume.sections
                if section.blocks
            ]
        )
        structure_signal = min(1.0, structure_count / 5.0)

        deterministic_signal = 0.9 if issue_count > 0 else 0.8

        score = round(
            (text_coverage * 0.25)
            + (structure_signal * 0.20)
            + (deterministic_signal * 0.55),
            3,
        )

        if score >= 0.75:
            level = ConfidenceLevel.HIGH
        elif score >= 0.45:
            level = ConfidenceLevel.MEDIUM
        else:
            level = ConfidenceLevel.LOW

        return Confidence(
            score=score,
            level=level,
            components={
                "text_coverage": round(text_coverage, 3),
                "resume_structure": round(structure_signal, 3),
                "deterministic_signal": deterministic_signal,
            },
            rationale=(
                "Confidence reflects text availability, recognized resume structure, "
                "and the deterministic nature of the detected language signals. "
                "It does not represent certainty that every heuristic finding is "
                "correct."
            ),
        )

    def _issue(
        self,
        *,
        issue_id: str,
        issue_type: LanguageIssueType,
        severity: LanguageIssueSeverity,
        title: str,
        explanation: str,
        recommendation: str | None = None,
        original_text: str | None = None,
        suggested_text: str | None = None,
        parsed_document: ParsedDocument,
        evidence_type: str,
    ) -> LanguageIssue:
        evidence = Evidence(
            evidence_id=f"{issue_id}-evidence",
            source_type=EvidenceSourceType.RESUME,
            source_document_id=parsed_document.document_id,
            section=None,
            text=original_text or title,
            offsets=None,
            evidence_type=evidence_type,
            extractor=self.ENGINE_VERSION,
            relevance=1.0,
            confidence=0.9,
        )

        return LanguageIssue(
            issue_id=issue_id,
            issue_type=issue_type,
            severity=severity,
            title=title,
            explanation=explanation,
            recommendation=recommendation,
            original_text=original_text,
            suggested_text=suggested_text,
            evidence=[evidence],
            confidence=Confidence(
                score=0.9,
                level=ConfidenceLevel.HIGH,
                components={"deterministic_signal": 0.9},
                rationale="Finding is based on a deterministic text-pattern heuristic.",
            ),
        )
