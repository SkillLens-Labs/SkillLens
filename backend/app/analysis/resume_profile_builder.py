from __future__ import annotations

from hashlib import sha256

from backend.app.analysis.esco_mapper import ESCOMapResult, ESCOMapStatus
from backend.app.analysis.resume_structure import (
    ResumeSectionType,
    StructuredResume,
)
from backend.app.analysis.skill_normalizer import NormalizedSkill
from backend.app.domain.confidence import Confidence, ConfidenceLevel
from backend.app.domain.evidence import Evidence, EvidenceSourceType
from backend.app.domain.resume import Contact, ResumeProfile
from backend.app.domain.skill import Skill


class ResumeProfileBuilder:
    """Build the canonical ResumeProfile from Phase 3 analysis outputs."""

    BUILDER_VERSION = "phase3-v1"

    def build(
        self,
        resume: StructuredResume,
        normalized_skills: tuple[NormalizedSkill, ...] | list[NormalizedSkill],
        esco_results: tuple[ESCOMapResult, ...] | list[ESCOMapResult],
    ) -> ResumeProfile:
        """Construct one canonical ResumeProfile without inventing resume facts."""

        normalized_skills = tuple(normalized_skills)
        esco_results = tuple(esco_results)

        if len(normalized_skills) != len(esco_results):
            raise ValueError(
                "normalized_skills and esco_results must contain the same number "
                "of items"
            )

        skills: list[Skill] = []
        seen_skill_ids: set[str] = set()

        for normalized_skill, esco_result in zip(
            normalized_skills,
            esco_results,
            strict=True,
        ):
            skill = self._build_skill(
                document_id=resume.document_id,
                normalized_skill=normalized_skill,
                esco_result=esco_result,
            )

            if skill.skill_id in seen_skill_ids:
                existing_index = next(
                    index
                    for index, existing in enumerate(skills)
                    if existing.skill_id == skill.skill_id
                )
                skills[existing_index] = self._merge_skill(
                    skills[existing_index],
                    skill,
                )
                continue

            seen_skill_ids.add(skill.skill_id)
            skills.append(skill)

        skill_categories = self._derive_skill_categories(skills)

        candidate_summary = self._extract_summary(resume)

        return ResumeProfile(
            profile_id=self._profile_id(resume.document_id),
            document_id=resume.document_id,
            candidate_summary=candidate_summary,
            contact=self._build_contact(resume),
            education=[],
            experience=[],
            projects=[],
            certifications=[],
            skills=skills,
            skill_categories=skill_categories,
            total_experience=None,
            seniority=None,
            domains=[],
            metadata={
                "builder": self.__class__.__name__,
                "builder_version": self.BUILDER_VERSION,
                "esco_version": "1.2.1",
                "skill_count": len(skills),
            },
        )

    def _build_skill(
        self,
        *,
        document_id: str,
        normalized_skill: NormalizedSkill,
        esco_result: ESCOMapResult,
    ) -> Skill:
        mention = normalized_skill.mention
        evidence = self._build_evidence(
            document_id=document_id,
            normalized_skill=normalized_skill,
            esco_result=esco_result,
        )

        confidence = self._build_confidence(
            normalized_skill=normalized_skill,
            esco_result=esco_result,
        )

        metadata: dict[str, object] = {
            "source_section": mention.section_type.value,
            "source_evidence_type": mention.evidence_type,
            "normalization_method": normalized_skill.metadata.get(
                "normalization_method"
            ),
            "esco_status": esco_result.status.value,
            "esco_version": esco_result.esco_version,
            "esco_mapping_method": esco_result.mapping_method,
        }

        if esco_result.candidates:
            metadata["esco_preferred_label"] = (
                esco_result.candidates[0].preferred_label
            )

            if esco_result.candidates[0].uri:
                metadata["esco_uri"] = esco_result.candidates[0].uri

        return Skill(
            skill_id=self._skill_id(document_id, normalized_skill.canonical_name),
            canonical_name=normalized_skill.canonical_name,
            display_name=self._display_name(
                normalized_skill=normalized_skill,
                esco_result=esco_result,
            ),
            category=self._skill_category(normalized_skill.canonical_name),
            aliases=self._aliases(normalized_skill),
            evidence=evidence,
            confidence=confidence,
            metadata=metadata,
        )

    def _build_evidence(
        self,
        *,
        document_id: str,
        normalized_skill: NormalizedSkill,
        esco_result: ESCOMapResult,
    ) -> list[Evidence]:
        mention = normalized_skill.mention

        evidence_id = self._evidence_id(
            document_id,
            normalized_skill.canonical_name,
            mention.block.source,
            mention.start_offset,
            mention.end_offset,
        )

        return [
            Evidence(
                evidence_id=evidence_id,
                source_type=EvidenceSourceType.RESUME,
                source_document_id=document_id,
                section=mention.section_type.value,
                text=mention.block.text,
                start_offset=mention.start_offset,
                end_offset=mention.end_offset,
                evidence_type=mention.evidence_type,
                extractor=mention.extractor,
                relevance=1.0,
                confidence=mention.confidence,
            )
        ]

    def _build_confidence(
        self,
        *,
        normalized_skill: NormalizedSkill,
        esco_result: ESCOMapResult,
    ) -> Confidence:
        extraction_confidence = normalized_skill.mention.confidence
        mapping_confidence = (
            max(candidate.confidence for candidate in esco_result.candidates)
            if esco_result.candidates
            else 0.0
        )

        if esco_result.status == ESCOMapStatus.MAPPED:
            score = (extraction_confidence + mapping_confidence) / 2
        elif esco_result.status == ESCOMapStatus.AMBIGUOUS:
            score = extraction_confidence * 0.75
        else:
            score = extraction_confidence * 0.70

        level = self._confidence_level(score)

        return Confidence(
            score=score,
            level=level,
            components={
                "extraction": extraction_confidence,
                "esco_mapping": mapping_confidence,
            },
            rationale=(
                f"Skill confidence derived from extraction confidence "
                f"({extraction_confidence:.2f}) and ESCO mapping status "
                f"({esco_result.status.value})."
            ),
        )

    @staticmethod
    def _confidence_level(score: float) -> ConfidenceLevel:
        if score >= 0.85:
            return ConfidenceLevel.HIGH
        if score >= 0.65:
            return ConfidenceLevel.MEDIUM
        return ConfidenceLevel.LOW

    @staticmethod
    def _display_name(
        *,
        normalized_skill: NormalizedSkill,
        esco_result: ESCOMapResult,
    ) -> str:
        if esco_result.candidates:
            return esco_result.candidates[0].preferred_label

        return normalized_skill.canonical_name

    @staticmethod
    def _aliases(normalized_skill: NormalizedSkill) -> list[str]:
        aliases: list[str] = []

        if normalized_skill.raw_text.lower() != normalized_skill.canonical_name:
            aliases.append(normalized_skill.raw_text)

        if normalized_skill.matched_alias:
            if normalized_skill.matched_alias not in aliases:
                aliases.append(normalized_skill.matched_alias)

        return aliases

    @staticmethod
    def _skill_category(canonical_name: str) -> str | None:
        programming = {
            "python",
            "java",
            "javascript",
            "typescript",
            "c++",
            "c#",
            "go",
            "rust",
        }

        web = {
            "html",
            "css",
            "react",
            "angular",
            "vue.js",
            "node.js",
            "fastapi",
            "django",
            "flask",
            "spring boot",
            "rest api",
            "graphql",
        }

        data = {
            "sql",
            "nosql",
            "postgresql",
            "mysql",
            "mongodb",
            "redis",
            "pandas",
            "numpy",
            "scikit-learn",
            "machine learning",
            "deep learning",
            "natural language processing",
            "transformers",
            "data analysis",
            "data science",
            "statistics",
            "power bi",
            "tableau",
            "excel",
        }

        cloud_devops = {
            "docker",
            "kubernetes",
            "aws",
            "azure",
            "gcp",
            "linux",
        }

        tooling = {
            "git",
            "github",
        }

        if canonical_name in programming:
            return "programming"
        if canonical_name in web:
            return "web"
        if canonical_name in data:
            return "data"
        if canonical_name in cloud_devops:
            return "cloud_devops"
        if canonical_name in tooling:
            return "tooling"

        return None

    @staticmethod
    def _derive_skill_categories(skills: list[Skill]) -> list[str]:
        categories = {
            skill.category
            for skill in skills
            if skill.category is not None
        }
        return sorted(categories)

    @staticmethod
    def _extract_summary(resume: StructuredResume) -> str | None:
        sections = resume.sections_of(ResumeSectionType.SUMMARY)

        for section in sections:
            texts = [
                block.text.strip()
                for block in section.blocks
                if block.text.strip()
            ]

            if texts:
                return "\n".join(texts)

        return None

    @staticmethod
    def _build_contact(resume: StructuredResume) -> Contact | None:
        header_sections = resume.sections_of(ResumeSectionType.HEADER)

        if not header_sections:
            return None

        texts = [
            block.text.strip()
            for section in header_sections
            for block in section.blocks
            if block.text.strip()
        ]

        if not texts:
            return None

        # Contact-field parsing is intentionally deferred. The current
        # structural layer does not provide validated contact entities.
        return Contact()

    @staticmethod
    def _profile_id(document_id: str) -> str:
        digest = sha256(
            f"resume-profile:{document_id}".encode("utf-8")
        ).hexdigest()[:16]

        return f"resume_{digest}"

    @staticmethod
    def _skill_id(document_id: str, canonical_name: str) -> str:
        digest = sha256(
            f"skill:{document_id}:{canonical_name}".encode("utf-8")
        ).hexdigest()[:16]

        return f"skill_{digest}"

    @staticmethod
    def _evidence_id(
        document_id: str,
        canonical_name: str,
        source: object,
        start_offset: int,
        end_offset: int,
    ) -> str:
        digest = sha256(
            (
                f"evidence:{document_id}:{canonical_name}:"
                f"{source!r}:{start_offset}:{end_offset}"
            ).encode("utf-8")
        ).hexdigest()[:16]

        return f"evidence_{digest}"

    @staticmethod
    def _merge_skill(existing: Skill, duplicate: Skill) -> Skill:
        evidence_by_id = {
            evidence.evidence_id: evidence
            for evidence in existing.evidence
        }

        for evidence in duplicate.evidence:
            evidence_by_id[evidence.evidence_id] = evidence

        aliases = list(existing.aliases)

        for alias in duplicate.aliases:
            if alias not in aliases:
                aliases.append(alias)

        confidence = existing.confidence

        if (
            duplicate.confidence is not None
            and (
                confidence is None
                or duplicate.confidence.score > confidence.score
            )
        ):
            confidence = duplicate.confidence

        return existing.model_copy(
            update={
                "aliases": aliases,
                "evidence": list(evidence_by_id.values()),
                "confidence": confidence,
            }
        )
