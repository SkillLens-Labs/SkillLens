from __future__ import annotations

import itertools
import re
from hashlib import sha256

from backend.app.analysis.esco_mapper import ESCOMapResult, ESCOMapStatus
from backend.app.analysis.resume_structure import (
    ResumeSectionType,
    StructuredResume,
)
from backend.app.analysis.skill_normalizer import NormalizedSkill
from backend.app.domain.confidence import Confidence, ConfidenceLevel
from backend.app.domain.evidence import Evidence, EvidenceSourceType
from backend.app.domain.resume import (
    Certification,
    Contact,
    Education,
    Experience,
    Project,
    ResumeProfile,
)
from backend.app.domain.skill import Skill


class ResumeProfileBuilder:
    """Build the canonical ResumeProfile from Phase 3 analysis outputs."""

    BUILDER_VERSION = "phase3-v2"

    _DATE_RANGE_PATTERN = re.compile(
        r"(?P<start>"
        r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|"
        r"Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|"
        r"Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}|"
        r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|"
        r"\d{4}"
        r")"
        r"\s*(?:-|–|—|to)\s*"
        r"(?P<end>"
        r"(?:Present|Current|"
        r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|"
        r"Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|"
        r"Nov(?:ember)?|Dec(?:ember)?)\s+\d{4}|"
        r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|"
        r"\d{4})"
        r")",
        re.IGNORECASE,
    )

    _EXPOSURE_PATTERN = re.compile(
        r"^\s*Exposure\s*:\s*(?P<technologies>.+?)\s*$",
        re.IGNORECASE,
    )

    _DEGREE_PATTERN = re.compile(
        r"^\s*(?P<degree>"
        r"(?:Bachelor(?:'s)?|Master(?:'s)?|Doctor(?:ate)?|"
        r"B\.?\s*E\.?|B\.?\s*Tech\.?|M\.?\s*E\.?|M\.?\s*Tech\.?|"
        r"B\.?\s*S\.?|M\.?\s*S\.?|Ph\.?D\.?)"
        r"(?:\s+of)?(?:\s+in)?"
        r".*?)\s*$",
        re.IGNORECASE,
    )

    _FIELD_SEPARATOR_PATTERN = re.compile(r"\s+[–—-]\s+")

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

        education = self._extract_education(resume)
        experience = self._extract_experience(resume)
        projects = self._extract_projects(resume)
        certifications = self._extract_certifications(resume)

        return ResumeProfile(
            profile_id=self._profile_id(resume.document_id),
            document_id=resume.document_id,
            candidate_summary=candidate_summary,
            contact=self._build_contact(resume),
            education=education,
            experience=experience,
            projects=projects,
            certifications=certifications,
            skills=skills,
            skill_categories=skill_categories,
            total_experience=self._derive_total_experience(experience),
            seniority=self._derive_seniority(experience),
            domains=[],
            metadata={
                "builder": self.__class__.__name__,
                "builder_version": self.BUILDER_VERSION,
                "esco_version": "1.2.1",
                "skill_count": len(skills),
                "education_count": len(education),
                "experience_count": len(experience),
                "project_count": len(projects),
                "certification_count": len(certifications),
            },
        )

    @staticmethod
    def _section_texts(
        resume: StructuredResume,
        section_type: ResumeSectionType,
    ) -> list[str]:
        texts: list[str] = []

        for section in resume.sections_of(section_type):
            for block in section.blocks:
                text = block.text.strip()
                if text:
                    texts.append(text)

        return texts

    def _extract_projects(
        self,
        resume: StructuredResume,
    ) -> list[Project]:
        projects: list[Project] = []

        for section in resume.sections_of(ResumeSectionType.PROJECTS):
            blocks = [
                block.text.strip()
                for block in section.blocks
                if block.text.strip()
            ]

            if not blocks:
                continue

            # First try the normal sequential resume structure.
            sequential_projects = self._extract_sequential_projects(blocks)

            # If every project has a description, the source already has
            # usable project ordering. Do not alter it.
            if (
                sequential_projects
                and all(project.description for project in sequential_projects)
            ):
                projects.extend(sequential_projects)
                continue

            # Some DOCX resumes flatten multi-column project descriptions:
            #
            #   Project A + tech
            #   Project B + tech
            #   Project C + tech
            #   links
            #   descriptions for A
            #   descriptions for B
            #   descriptions for C
            #
            # In that case reconstruct descriptions from semantic evidence.
            reconstructed = self._extract_flattened_project_layout(blocks)

            if reconstructed:
                projects.extend(reconstructed)
            else:
                projects.extend(sequential_projects)

        return projects

    def _extract_sequential_projects(
        self,
        blocks: list[str],
    ) -> list[Project]:
        projects: list[Project] = []

        current_name: str | None = None
        current_description: list[str] = []
        current_technologies: list[str] = []
        current_start: str | None = None
        current_end: str | None = None

        for text in blocks:
            exposure_match = self._EXPOSURE_PATTERN.match(text)

            if exposure_match and current_name is not None:
                current_technologies = self._split_technologies(
                    exposure_match.group("technologies")
                )
                continue

            if self._is_project_link_marker(text):
                continue

            if self._looks_like_project_title(text):
                if current_name is not None:
                    projects.append(
                        Project(
                            name=current_name,
                            description=self._join_description(
                                current_description
                            ),
                            technologies=current_technologies,
                            start_date=current_start,
                            end_date=current_end,
                        )
                    )

                current_name = text
                current_description = []
                current_technologies = []
                current_start, current_end = self._extract_date_range(text)
                continue

            if current_name is not None:
                date_start, date_end = self._extract_date_range(text)

                if (
                    date_start
                    and date_end
                    and not current_description
                ):
                    current_start = date_start
                    current_end = date_end
                else:
                    current_description.append(text)

        if current_name is not None:
            projects.append(
                Project(
                    name=current_name,
                    description=self._join_description(
                        current_description
                    ),
                    technologies=current_technologies,
                    start_date=current_start,
                    end_date=current_end,
                )
            )

        return projects

    def _extract_flattened_project_layout(
        self,
        blocks: list[str],
    ) -> list[Project] | None:
        project_headers: list[dict[str, object]] = []
        description_blocks: list[str] = []

        current_project: dict[str, object] | None = None
        link_count = 0

        for text in blocks:
            exposure_match = self._EXPOSURE_PATTERN.match(text)

            if exposure_match and current_project is not None:
                current_project["technologies"] = (
                    self._split_technologies(
                        exposure_match.group("technologies")
                    )
                )
                continue

            if self._is_project_link_marker(text):
                link_count += 1
                continue

            if self._looks_like_project_title(text):
                current_project = {
                    "name": text,
                    "technologies": [],
                    "description": [],
                    "start_date": None,
                    "end_date": None,
                }
                project_headers.append(current_project)
                continue

            if project_headers:
                if current_project is not None:
                    description = current_project["description"]

                    if isinstance(description, list):
                        description.append(text)

        if len(project_headers) < 2:
            return None

        # The sequential parser is preferable whenever the document is
        # already correctly ordered.
        if all(
            isinstance(project["description"], list)
            and project["description"]
            for project in project_headers
        ):
            return None

        # Only apply reconstruction when the document has multiple project
        # headers followed by link markers and then prose. This is the
        # characteristic flattened DOCX pattern we are correcting.
        if link_count < len(project_headers):
            return None

        # The project descriptions are the prose blocks that occur after
        # all project headers/technologies/link markers.
        first_description_index = self._find_flattened_description_start(
            blocks,
            len(project_headers),
        )

        if first_description_index is None:
            return None

        description_blocks = [
            text
            for text in blocks[first_description_index:]
            if not self._is_project_link_marker(text)
            and not self._EXPOSURE_PATTERN.match(text)
            and text.strip()
        ]

        if not description_blocks:
            return None

        assignments = self._assign_project_description_blocks(
            project_headers,
            description_blocks,
        )

        if assignments is None:
            return None

        reconstructed: list[Project] = []

        for project, assigned in zip(project_headers, assignments):
            name = project["name"]
            technologies = project["technologies"]

            if not isinstance(name, str):
                return None

            if not isinstance(technologies, list):
                technologies = []

            reconstructed.append(
                Project(
                    name=name,
                    description=self._join_description(assigned),
                    technologies=technologies,
                    start_date=project["start_date"],
                    end_date=project["end_date"],
                )
            )

        return reconstructed

    def _find_flattened_description_start(
        self,
        blocks: list[str],
        project_count: int,
    ) -> int | None:
        project_header_count = 0
        link_count = 0
        seen_all_headers = False

        for index, text in enumerate(blocks):
            if self._looks_like_project_title(text):
                project_header_count += 1

                if project_header_count >= project_count:
                    seen_all_headers = True

                continue

            if not seen_all_headers:
                continue

            if self._is_project_link_marker(text):
                link_count += 1
                continue

            # Once all expected project links have appeared, the next
            # ordinary prose block begins the flattened descriptions.
            if link_count >= project_count:
                return index

        return None

    def _assign_project_description_blocks(
        self,
        projects: list[dict[str, object]],
        description_blocks: list[str],
    ) -> list[list[str]] | None:
        """
        Reconstruct flattened DOCX project descriptions.

        Some DOCX files preserve visually wrapped lines as separate paragraph
        blocks. The description stream can therefore contain several physical
        blocks for one logical paragraph, followed by contiguous description
        groups for the declared projects.

        Strategy:
        1. Reconstruct logical paragraphs from consecutive physical blocks.
        2. Build semantic profiles from project names and technologies.
        3. Score every logical paragraph against every project.
        4. Identify strong semantic anchors for each project.
        5. Split the paragraph stream into contiguous project clusters.
        6. Require every assigned project cluster to contain its own anchor.
        7. Find the best one-to-one mapping using paragraph-level evidence.
        8. Preserve paragraph order within every project.

        No project names, technologies, paragraph numbers, or
        candidate-specific ordering are hardcoded here.
        """

        if not projects or not description_blocks:
            return None

        project_count = len(projects)

        if project_count < 2:
            return None

        # ---------------------------------------------------------------
        # Step 1: reconstruct logical paragraphs
        # ---------------------------------------------------------------

        logical_blocks: list[str] = []
        current: list[str] = []

        sentence_end_pattern = re.compile(
            r"[.!?…:;)]$"
        )

        for raw_text in description_blocks:
            text = " ".join(raw_text.split())

            if not text:
                continue

            current.append(text)

            if sentence_end_pattern.search(text):
                logical_blocks.append(" ".join(current))
                current = []

        if current:
            logical_blocks.append(" ".join(current))

        if len(logical_blocks) < project_count:
            return None

        # ---------------------------------------------------------------
        # Step 2: build project semantic profiles
        # ---------------------------------------------------------------

        profiles = [
            self._build_project_semantic_profile(project)
            for project in projects
        ]

        # ---------------------------------------------------------------
        # Step 3: calculate paragraph-level project scores
        # ---------------------------------------------------------------

        paragraph_scores: list[list[float]] = []

        for paragraph in logical_blocks:
            tokens = self._semantic_tokens(paragraph)

            paragraph_scores.append(
                [
                    self._project_similarity_score(
                        tokens,
                        profile,
                    )
                    for profile in profiles
                ]
            )

        # ---------------------------------------------------------------
        # Step 4: identify strong semantic anchors
        # ---------------------------------------------------------------

        #
        # A project anchor is its strongest paragraph-level evidence.
        # Anchors are based entirely on the observed semantic scores and
        # therefore remain generic across resumes.
        #
        anchors: list[int] = []

        for project_index in range(project_count):
            best_index = max(
                range(len(logical_blocks)),
                key=lambda paragraph_index: (
                    paragraph_scores[paragraph_index][project_index],
                    -paragraph_index,
                ),
            )

            best_score = paragraph_scores[best_index][project_index]

            # A zero-score paragraph provides no usable evidence and cannot
            # serve as a semantic anchor.
            if best_score <= 0:
                return None

            anchors.append(best_index)

        # Each project needs a distinct anchor. If two projects have exactly
        # the same strongest paragraph, semantic evidence is insufficient for
        # safe reconstruction.
        if len(set(anchors)) != project_count:
            return None

        # ---------------------------------------------------------------
        # Step 5: enumerate contiguous segmentations
        # ---------------------------------------------------------------

        best_boundaries: list[int] | None = None
        best_mapping: tuple[int, ...] | None = None
        best_score = float("-inf")

        for boundaries in itertools.combinations(
            range(1, len(logical_blocks)),
            project_count - 1,
        ):
            starts = [0, *boundaries]
            ends = [*boundaries, len(logical_blocks)]

            clusters = [
                list(range(start, end))
                for start, end in zip(starts, ends)
            ]

            if any(not cluster for cluster in clusters):
                continue

            # -----------------------------------------------------------
            # Step 6: calculate cluster scores
            # -----------------------------------------------------------

            cluster_scores: list[list[float]] = []

            for cluster in clusters:
                scores: list[float] = []

                for project_index in range(project_count):
                    score = sum(
                        paragraph_scores[
                            paragraph_index
                        ][project_index]
                        for paragraph_index in cluster
                    )

                    scores.append(score)

                cluster_scores.append(scores)

            # -----------------------------------------------------------
            # Step 7: solve one-to-one cluster/project assignment
            # -----------------------------------------------------------

            for project_order in itertools.permutations(
                range(project_count)
            ):
                total_score = 0.0
                valid_assignment = True

                for cluster_index, project_index in enumerate(
                    project_order
                ):
                    cluster = clusters[cluster_index]

                    # The cluster must contain the strongest semantic
                    # paragraph for the project it is assigned to.
                    if anchors[project_index] not in cluster:
                        valid_assignment = False
                        break

                    score = cluster_scores[
                        cluster_index
                    ][project_index]

                    if score <= 0:
                        valid_assignment = False
                        break

                    total_score += score

                if not valid_assignment:
                    continue

                if total_score > best_score:
                    best_score = total_score
                    best_boundaries = list(boundaries)
                    best_mapping = project_order

        if (
            best_boundaries is None
            or best_mapping is None
            or best_score <= 0
        ):
            return None

        # ---------------------------------------------------------------
        # Step 8: materialize selected contiguous clusters
        # ---------------------------------------------------------------

        starts = [0, *best_boundaries]
        ends = [*best_boundaries, len(logical_blocks)]

        clusters = [
            logical_blocks[start:end]
            for start, end in zip(starts, ends)
        ]

        if len(clusters) != project_count:
            return None

        # ---------------------------------------------------------------
        # Step 9: return assignments in project-header order
        # ---------------------------------------------------------------

        assignments: list[list[str]] = [
            []
            for _ in range(project_count)
        ]

        for cluster_index, project_index in enumerate(best_mapping):
            assignments[project_index] = clusters[cluster_index]

        if any(not assignment for assignment in assignments):
            return None

        return assignments

    @staticmethod
    def _build_project_semantic_profile(
        project: dict[str, object],
    ) -> set[str]:
        """Build generic semantic tokens from project name and technologies."""
        values: list[str] = []

        name = project.get("name")
        if isinstance(name, str):
            values.append(name)

        technologies = project.get("technologies")
        if isinstance(technologies, list):
            values.extend(
                technology
                for technology in technologies
                if isinstance(technology, str)
            )

        return ResumeProfileBuilder._semantic_tokens(" ".join(values))

    @staticmethod
    def _semantic_tokens(text: str) -> set[str]:
        normalized = text.lower()

        # Split camelCase / PascalCase terms so names such as
        # "TradeBook" contribute both "trade" and "book".
        normalized = re.sub(
            r"([a-z])([A-Z])",
            r"\1 \2",
            normalized,
        )

        words = re.findall(
            r"[a-z][a-z0-9+#.-]{2,}",
            normalized,
        )

        stop_words = {
            "the",
            "and",
            "for",
            "with",
            "using",
            "used",
            "from",
            "into",
            "that",
            "this",
            "through",
            "across",
            "built",
            "designed",
            "implemented",
            "developed",
            "integrated",
            "supporting",
            "system",
            "application",
            "platform",
            "project",
        }

        return {
            word.strip(".-")
            for word in words
            if word not in stop_words
        }

    def _project_similarity_score(
        self,
        block_tokens: set[str],
        project_tokens: set[str],
    ) -> float:
        if not block_tokens or not project_tokens:
            return 0.0

        exact_matches = block_tokens & project_tokens

        score = float(len(exact_matches))

        # Give a small bonus for morphological overlap. This lets generic
        # metadata such as "trade" contribute to "trading" without
        # depending on any particular project name.
        for block_token in block_tokens:
            for project_token in project_tokens:
                if (
                    len(block_token) >= 5
                    and len(project_token) >= 5
                    and (
                        block_token.startswith(project_token[:5])
                        or project_token.startswith(block_token[:5])
                    )
                ):
                    score += 0.25

        return score

    @staticmethod
    def _is_project_link_marker(text: str) -> bool:
        if not (text.startswith("[") and text.endswith("]")):
            return False

        marker = " ".join(text[1:-1].strip().lower().split())

        return marker in {
            "github",
            "github repo",
            "github repository",
            "repository",
            "repo",
        }

    @staticmethod
    def _looks_like_project_title(text: str) -> bool:
        if not text:
            return False

        if ResumeProfileBuilder._EXPOSURE_PATTERN.match(text):
            return False

        normalized = " ".join(text.strip().lower().split())

        if normalized.startswith("[github"):
            return False

        if normalized.startswith("github"):
            return False

        if normalized.startswith("http://") or normalized.startswith("https://"):
            return False

        # Description fragments in resumes commonly begin with
        # action-oriented verbs. Treat these as prose rather than
        # project-title candidates.
        description_starters = {
            "built",
            "created",
            "designed",
            "developed",
            "implemented",
            "integrated",
            "engineered",
            "configured",
            "automated",
            "analyzed",
            "deployed",
            "optimized",
            "used",
            "leveraged",
            "established",
            "constructed",
            "tracked",
            "maintained",
            "delivered",
            "supported",
            "enabled",
            "reduced",
            "improved",
        }

        first_word = normalized.split(maxsplit=1)[0]

        if first_word in description_starters:
            return False

        # A project title should be a compact standalone label.
        words = text.split()

        if len(words) > 12:
            return False

        if len(words) == 1 and len(text) > 60:
            return False

        if text.endswith((".", ",", ":", ";", "—", "–", "-")):
            return False

        # Longer prose fragments containing sentence-like connectors
        # are unlikely to be project titles.
        sentence_markers = {
            " the ",
            " a ",
            " an ",
            " using ",
            " with ",
            " to ",
            " for ",
            " by ",
            " that ",
            " which ",
            " supporting ",
            " across ",
            " through ",
        }

        padded = f" {normalized} "

        if len(words) >= 6 and any(
            marker in padded for marker in sentence_markers
        ):
            return False

        return True
    
    @staticmethod
    def _split_technologies(value: str) -> list[str]:
        return [
            item.strip()
            for item in value.split(",")
            if item.strip()
        ]

    @staticmethod
    def _join_description(parts: list[str]) -> str | None:
        if not parts:
            return None

        return "\n".join(parts)

    @classmethod
    def _extract_education(
        cls,
        resume: StructuredResume,
    ) -> list[Education]:
        entries: list[Education] = []

        for section in resume.sections_of(ResumeSectionType.EDUCATION):
            blocks = [
                block.text.strip()
                for block in section.blocks
                if block.text.strip()
            ]

            if not blocks:
                continue

            current_degree: str | None = None
            current_field: str | None = None
            current_institution: str | None = None
            current_start: str | None = None
            current_end: str | None = None
            description: list[str] = []

            for text in blocks:
                start, end = cls._extract_date_range(text)

                if start and end:
                    current_start = start
                    current_end = end

                    remaining = cls._remove_date_range(text).strip()
                    if remaining:
                        description.append(remaining)
                    continue

                if current_degree is None:
                    degree, field = cls._extract_degree_and_field(text)

                    if degree:
                        current_degree = degree
                        current_field = field

                        lines = [
                            line.strip()
                            for line in text.splitlines()
                            if line.strip()
                        ]

                        if len(lines) > 1:
                            remaining_lines = lines[1:]

                            if remaining_lines:
                                current_institution = remaining_lines[0]

                                if len(remaining_lines) > 1:
                                    description.extend(
                                        remaining_lines[1:]
                                    )

                        continue

                if current_institution is None:
                    current_institution = text
                    continue

                description.append(text)

            if (
                current_degree is not None
                or current_institution is not None
                or current_start is not None
                or current_end is not None
                or description
            ):
                entries.append(
                    Education(
                        institution=current_institution,
                        degree=current_degree,
                        field_of_study=current_field,
                        start_date=current_start,
                        end_date=current_end,
                        description=cls._join_description(description),
                    )
                )

        return entries

    @classmethod
    def _extract_degree_and_field(
        cls,
        text: str,
    ) -> tuple[str | None, str | None]:
        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        if not lines:
            return None, None

        first_line = lines[0]

        parts = cls._FIELD_SEPARATOR_PATTERN.split(first_line, maxsplit=1)

        if len(parts) == 2:
            degree_part, field_part = parts

            if cls._DEGREE_PATTERN.match(degree_part):
                return degree_part.strip(), field_part.strip()

        match = cls._DEGREE_PATTERN.match(first_line)

        if not match:
            return None, None

        degree = match.group("degree").strip()

        field: str | None = None
        lower_degree = degree.lower()

        marker = re.search(r"\b(?:of|in)\s+(.+)$", degree, re.IGNORECASE)

        if marker:
            field = marker.group(1).strip()

        elif "computer science" in lower_degree:
            field = "Computer Science"

        return degree, field

    @classmethod
    def _extract_experience(
        cls,
        resume: StructuredResume,
    ) -> list[Experience]:
        entries: list[Experience] = []

        for section in resume.sections_of(ResumeSectionType.EXPERIENCE):
            blocks = [
                block.text.strip()
                for block in section.blocks
                if block.text.strip()
            ]

            if not blocks:
                continue

            # Experience layouts vary considerably. We preserve the raw
            # section content conservatively rather than guessing employer,
            # role, or dates when the structure is insufficient.
            current: list[str] = []

            for text in blocks:
                start, end = cls._extract_date_range(text)

                if start and end and current:
                    current.append(text)
                    continue

                if current and cls._looks_like_experience_heading(text):
                    entries.append(cls._experience_from_blocks(current))
                    current = [text]
                else:
                    current.append(text)

            if current:
                entries.append(cls._experience_from_blocks(current))

        return entries

    @staticmethod
    def _looks_like_experience_heading(text: str) -> bool:
        if len(text.split()) > 10:
            return False

        if ResumeProfileBuilder._EXPOSURE_PATTERN.match(text):
            return False

        return not text.endswith((".", ":", ";"))

    @classmethod
    def _experience_from_blocks(
        cls,
        blocks: list[str],
    ) -> Experience:
        if not blocks:
            return Experience()

        first = blocks[0]
        start, end = cls._extract_date_range(first)

        description_parts = blocks[1:] if not (start and end) else []

        if start and end:
            first_without_date = cls._remove_date_range(first).strip()
            if first_without_date:
                description_parts.insert(0, first_without_date)

        return Experience(
            description=cls._join_description(description_parts),
            start_date=start,
            end_date=end,
        )

    @staticmethod
    def _extract_certifications(
        resume: StructuredResume,
    ) -> list[Certification]:
        entries: list[Certification] = []

        for section in resume.sections_of(ResumeSectionType.CERTIFICATIONS):
            for block in section.blocks:
                text = block.text.strip()

                if not text:
                    continue

                entries.append(Certification(name=text))

        return entries

    @classmethod
    def _extract_date_range(
        cls,
        text: str,
    ) -> tuple[str | None, str | None]:
        match = cls._DATE_RANGE_PATTERN.search(text)

        if not match:
            return None, None

        return (
            match.group("start").strip(),
            match.group("end").strip(),
        )

    @classmethod
    def _remove_date_range(cls, text: str) -> str:
        return cls._DATE_RANGE_PATTERN.sub("", text).strip(" |-–—")

    @staticmethod
    def _derive_total_experience(
        experience: list[Experience],
    ) -> float | None:
        # Only derive this when at least one complete numeric year range is
        # explicitly present. "Present" is intentionally not converted into
        # an assumed duration here.
        durations: list[float] = []

        for entry in experience:
            if not entry.start_date or not entry.end_date:
                continue

            start_match = re.search(r"\b(19|20)\d{2}\b", entry.start_date)
            end_match = re.search(r"\b(19|20)\d{2}\b", entry.end_date)

            if not start_match or not end_match:
                continue

            start_year = int(start_match.group(0))
            end_year = int(end_match.group(0))

            if end_year >= start_year:
                durations.append(float(end_year - start_year))

        if not durations:
            return None

        return round(sum(durations), 2)

    @staticmethod
    def _derive_seniority(
        experience: list[Experience],
    ) -> str | None:
        total_years = ResumeProfileBuilder._derive_total_experience(experience)

        if total_years is None:
            return None

        if total_years < 1:
            return "entry"

        if total_years < 3:
            return "junior"

        if total_years < 6:
            return "mid"

        if total_years < 10:
            return "senior"

        return "lead"

    @staticmethod
    def _build_skill(
        *,
        document_id: str,
        normalized_skill: NormalizedSkill,
        esco_result: ESCOMapResult,
    ) -> Skill:
        mention = normalized_skill.mention

        evidence = ResumeProfileBuilder._build_evidence(
            document_id=document_id,
            normalized_skill=normalized_skill,
            esco_result=esco_result,
        )

        confidence = ResumeProfileBuilder._build_confidence(
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
            skill_id=ResumeProfileBuilder._skill_id(
                document_id,
                normalized_skill.canonical_name,
            ),
            canonical_name=normalized_skill.canonical_name,
            display_name=ResumeProfileBuilder._display_name(
                normalized_skill=normalized_skill,
                esco_result=esco_result,
            ),
            category=ResumeProfileBuilder._skill_category(
                normalized_skill.canonical_name
            ),
            aliases=ResumeProfileBuilder._aliases(normalized_skill),
            evidence=evidence,
            confidence=confidence,
            metadata=metadata,
        )

    @staticmethod
    def _build_evidence(
        *,
        document_id: str,
        normalized_skill: NormalizedSkill,
        esco_result: ESCOMapResult,
    ) -> list[Evidence]:
        mention = normalized_skill.mention

        evidence_id = ResumeProfileBuilder._evidence_id(
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

    @staticmethod
    def _build_confidence(
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

        level = ResumeProfileBuilder._confidence_level(score)

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

        if (
            normalized_skill.raw_text.lower()
            != normalized_skill.canonical_name
        ):
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

        header_text = "\n".join(texts)

        email_match = re.search(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
            header_text,
        )

        phone_match = re.search(
            r"(?<!\w)(?:\+?\d[\d ()-]{7,}\d)(?!\w)",
            header_text,
        )

        lines = [
            line.strip()
            for line in header_text.splitlines()
            if line.strip()
        ]

        name: str | None = None
        if lines:
            candidate = lines[0].strip()
            name_pattern = re.compile(
                r"^[A-Z][A-Za-z.'-]*(?:\s+[A-Z][A-Za-z.'-]*){1,5}$"
            )
            if name_pattern.fullmatch(candidate):
                name = candidate

        location: str | None = None

        location_pattern = re.compile(
            r"(?P<location>"
            r"[^|\n]*"
            r"(?:,\s*[A-Za-z .'-]+){1,}"
            r")$"
        )

        for line in lines:
            if "," not in line:
                continue

            parts = [
                part.strip()
                for part in line.split("|")
                if part.strip()
            ]

            for part in reversed(parts):
                if "@" in part or re.search(r"\d", part):
                    continue

                if re.search(
                    r"\b(?:linkedin|github|portfolio)\b",
                    part,
                    re.IGNORECASE,
                ):
                    continue

                match = location_pattern.search(part)
                if match:
                    location = match.group("location").strip()
                    break

            if location:
                break

        urls = re.findall(
            r"https?://[^\s|]+",
            header_text,
            flags=re.IGNORECASE,
        )

        linkedin = next(
            (url for url in urls if "linkedin." in url.lower()),
            None,
        )

        github = next(
            (url for url in urls if "github." in url.lower()),
            None,
        )

        portfolio = next(
            (
                url
                for url in urls
                if "linkedin." not in url.lower()
                and "github." not in url.lower()
            ),
            None,
        )

        contact = Contact(
            name=name,
            email=email_match.group(0) if email_match else None,
            phone=phone_match.group(0).strip() if phone_match else None,
            location=location,
            linkedin=linkedin,
            github=github,
            portfolio=portfolio,
        )

        if not any(
            (
                contact.name,
                contact.email,
                contact.phone,
                contact.location,
                contact.linkedin,
                contact.github,
                contact.portfolio,
            )
        ):
            return None

        return contact

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