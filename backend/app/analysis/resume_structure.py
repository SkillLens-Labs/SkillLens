from __future__ import annotations

import re

from dataclasses import dataclass, field

from backend.app.infrastructure.parsers.models import (
    DocumentBlock,
    DocumentBlockType,
    DocumentType,
    ParsedDocument,
)


from enum import StrEnum


class ResumeSectionType(StrEnum):
    HEADER = "header"
    SUMMARY = "summary"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    PROJECTS = "projects"
    CERTIFICATIONS = "certifications"
    SKILLS = "skills"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ResumeSection:
    section_type: str
    heading: str | None
    blocks: tuple[DocumentBlock, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class StructuredResume:
    document_id: str
    sections: tuple[ResumeSection, ...] = field(default_factory=tuple)

    def sections_of(
        self,
        section_type: ResumeSectionType,
    ) -> tuple[ResumeSection, ...]:
        return tuple(
            section
            for section in self.sections
            if section.section_type == section_type
        )


class ResumeStructureInterpreter:
    """
    Reconstruct the semantic section structure of a resume.

    The raw parser order is not assumed to be semantically correct.

    DOCX:
        Native document order is preserved because the DOCX parser already
        provides a meaningful logical sequence.

    PDF:
        Spatial information is used to reconstruct a stable reading order.
        The algorithm deliberately avoids a naive global Y sort because that
        breaks two-column resumes.
    """

    _SECTION_ALIASES: dict[str, str] = {
        # Header
        "contact": ResumeSectionType.HEADER,
        "contact information": ResumeSectionType.HEADER,
        "personal information": ResumeSectionType.HEADER,
        "personal details": ResumeSectionType.HEADER,

        # Summary
        "summary": ResumeSectionType.SUMMARY,
        "professional summary": ResumeSectionType.SUMMARY,
        "career summary": ResumeSectionType.SUMMARY,
        "profile": ResumeSectionType.SUMMARY,
        "professional profile": ResumeSectionType.SUMMARY,
        "career profile": ResumeSectionType.SUMMARY,
        "objective": ResumeSectionType.SUMMARY,
        "career objective": ResumeSectionType.SUMMARY,
        "professional objective": ResumeSectionType.SUMMARY,

        # Experience
        "experience": ResumeSectionType.EXPERIENCE,
        "work experience": ResumeSectionType.EXPERIENCE,
        "professional experience": ResumeSectionType.EXPERIENCE,
        "employment": ResumeSectionType.EXPERIENCE,
        "employment history": ResumeSectionType.EXPERIENCE,
        "work history": ResumeSectionType.EXPERIENCE,
        "professional history": ResumeSectionType.EXPERIENCE,

        # Education
        "education": ResumeSectionType.EDUCATION,
        "educational background": ResumeSectionType.EDUCATION,
        "academic background": ResumeSectionType.EDUCATION,
        "academic qualifications": ResumeSectionType.EDUCATION,
        "qualifications": ResumeSectionType.EDUCATION,

        # Projects
        "projects": ResumeSectionType.PROJECTS,
        "selected projects": ResumeSectionType.PROJECTS,
        "academic projects": ResumeSectionType.PROJECTS,
        "personal projects": ResumeSectionType.PROJECTS,
        "professional projects": ResumeSectionType.PROJECTS,
        "project experience": ResumeSectionType.PROJECTS,
        "selected works": ResumeSectionType.PROJECTS,
        "works": ResumeSectionType.PROJECTS,

        # Certifications
        "certifications": ResumeSectionType.CERTIFICATIONS,
        "certificates": ResumeSectionType.CERTIFICATIONS,
        "professional certifications": ResumeSectionType.CERTIFICATIONS,
        "licenses and certifications": ResumeSectionType.CERTIFICATIONS,
        "licenses & certifications": ResumeSectionType.CERTIFICATIONS,

        # Skills
        "skills": ResumeSectionType.SKILLS,
        "technical skills": ResumeSectionType.SKILLS,
        "core skills": ResumeSectionType.SKILLS,
        "key skills": ResumeSectionType.SKILLS,
        "professional skills": ResumeSectionType.SKILLS,
        "competencies": ResumeSectionType.SKILLS,
        "technical competencies": ResumeSectionType.SKILLS,
    }

    _HEADING_NORMALIZATION_REPLACEMENTS = {
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
        ":": " ",
        "/": " ",
        "|": " ",
    }

    def interpret(self, document: ParsedDocument) -> StructuredResume:
        blocks = self._reconstruct_reading_order(document)
        sections: list[ResumeSection] = []
        current_type = ResumeSectionType.HEADER
        current_heading: str | None = None
        current_blocks: list[DocumentBlock] = []

        for block in blocks:
            heading_type = self._classify_heading(block)

            if heading_type is not None:
                preceding_blocks = []

                if document.document_type == DocumentType.PDF:
                    preceding_blocks = self._extract_heading_row_blocks(
                        current_blocks,
                        block,
                    )

                if preceding_blocks:
                    current_blocks = current_blocks[
                        : len(current_blocks) - len(preceding_blocks)
                    ]

                self._flush_section(
                    sections,
                    current_type,
                    current_heading,
                    current_blocks,
                )

                current_type = heading_type
                current_heading = block.text.strip()
                current_blocks = list(preceding_blocks)
                continue

            current_blocks.append(block)

        self._flush_section(
            sections,
            current_type,
            current_heading,
            current_blocks,
        )

        return StructuredResume(
            document_id=document.document_id,
            sections=tuple(sections),
        )

    # ------------------------------------------------------------------
    # Reading-order reconstruction
    # ------------------------------------------------------------------

    def _reconstruct_reading_order(self, document):
        if not document.blocks:
            return ()

        if document.document_type == DocumentType.PDF:
            if not self._has_spatial_information(document.blocks):
                return tuple(document.blocks)
            return tuple(self._order_pdf_blocks(document.blocks))

        if document.document_type == DocumentType.DOCX:
            return tuple(self._reconstruct_docx_order(document.blocks))

        return tuple(document.blocks)

    # ------------------------------------------------------------------
    # DOCX semantic reconstruction
    # ------------------------------------------------------------------

    def _reconstruct_docx_order(
        self,
        blocks: list[DocumentBlock],
    ) -> list[DocumentBlock]:
        """
        Conservatively repair DOCX documents whose semantic sections were
        serialized in an unusual paragraph order.

        DOCX does not provide reliable spatial coordinates in the parsed
        representation, so reconstruction is based only on strong semantic
        evidence.

        The algorithm specifically handles orphan groups that appear before
        their section heading:

        - summary prose before PROFESSIONAL SUMMARY
        - education material before EDUCATION
        - contact/header material stranded after another section

        All unrelated content keeps its original relative order.
        """

        if not blocks:
            return []

        headings = [
            (index, self._classify_heading(block))
            for index, block in enumerate(blocks)
            if self._classify_heading(block) is not None
        ]

        if not headings:
            return list(blocks)

        summary_heading = self._first_heading(
            headings,
            ResumeSectionType.SUMMARY,
        )

        education_heading = self._first_heading(
            headings,
            ResumeSectionType.EDUCATION,
        )

        summary_orphan = self._find_summary_orphan(
            blocks,
            summary_heading,
        )

        education_orphan = self._find_education_orphan(
            blocks,
            summary_heading,
            education_heading,
        )

        header_blocks = self._find_orphan_header_blocks(
            blocks,
            headings,
            summary_orphan,
            education_orphan,
        )

        if not summary_orphan and not education_orphan and not header_blocks:
            return list(blocks)

        moved_indices = (
            set(summary_orphan)
            | set(education_orphan)
            | set(header_blocks)
        )

        remaining = [
            block
            for index, block in enumerate(blocks)
            if index not in moved_indices
        ]

        summary_blocks = [
            blocks[index]
            for index in summary_orphan
        ]

        education_blocks = [
            blocks[index]
            for index in education_orphan
        ]

        header = [
            blocks[index]
            for index in header_blocks
        ]

        result = list(remaining)

        result = self._insert_docx_content_after_heading(
            result,
            ResumeSectionType.SUMMARY,
            summary_blocks,
        )

        result = self._insert_docx_content_after_heading(
            result,
            ResumeSectionType.EDUCATION,
            education_blocks,
        )

        if header:
            result = header + result

        return result

    @staticmethod
    def _first_heading(
        headings: list[tuple[int, str]],
        section_type: str,
    ) -> int | None:
        for index, heading_type in headings:
            if heading_type == section_type:
                return index
        return None

    def _find_summary_orphan(
        self,
        blocks: list[DocumentBlock],
        summary_heading: int | None,
    ) -> list[int]:
        """
        Detect a contiguous prose group immediately preceding the first
        summary heading.

        The group is evaluated as a whole because DOCX may split one
        logical paragraph into multiple physical blocks.
        """

        if summary_heading is None or summary_heading == 0:
            return []

        candidate_indices: list[int] = []

        for index in range(summary_heading):
            text = blocks[index].text.strip()

            if not text:
                continue

            # A heading before the summary means this is not an orphan
            # summary group.
            if self._classify_heading(blocks[index]) is not None:
                return []

            candidate_indices.append(index)

        if not candidate_indices:
            return []

        combined_text = " ".join(
            blocks[index].text.strip()
            for index in candidate_indices
        )

        if not self._looks_like_summary_group(combined_text):
            return []

        return candidate_indices

    def _find_education_orphan(
        self,
        blocks: list[DocumentBlock],
        summary_heading: int | None,
        education_heading: int | None,
    ) -> list[int]:
        """
        Detect education material appearing between the summary heading and
        education heading.

        The complete group is evaluated together because DOCX may split
        dates, degree, institution, score, and other education information
        across multiple physical blocks.
        """

        if education_heading is None:
            return []

        start = (
            0
            if summary_heading is None
            else summary_heading + 1
        )

        if start >= education_heading:
            return []

        candidate_indices: list[int] = []

        for index in range(start, education_heading):
            text = blocks[index].text.strip()

            if not text:
                continue

            if self._classify_heading(blocks[index]) is not None:
                return []

            candidate_indices.append(index)

        if not candidate_indices:
            return []

        combined_text = " ".join(
            blocks[index].text.strip()
            for index in candidate_indices
        )

        if not self._looks_like_education_group(combined_text):
            return []

        return candidate_indices

    def _find_orphan_header_blocks(
        self,
        blocks: list[DocumentBlock],
        headings: list[tuple[int, str]],
        summary_orphan: list[int],
        education_orphan: list[int],
    ) -> list[int]:
        """
        Detect contact/header content stranded outside the header section.

        A real email or phone number is the strongest signal. Once found,
        adjacent short name/contact paragraphs are included.

        Generic words such as GitHub, LinkedIn, or Portfolio alone are not
        sufficient evidence for header classification.
        """

        excluded = (
            set(summary_orphan)
            | set(education_orphan)
        )

        contact_indices = [
            index
            for index, block in enumerate(blocks)
            if (
                index not in excluded
                and self._classify_heading(block) is None
                and self._has_contact_signal(block.text.strip())
            )
        ]

        if not contact_indices:
            return []

        header_indices: set[int] = set()

        for contact_index in contact_indices:
            header_indices.add(contact_index)

            # Include an adjacent name-like block.
            for neighbor in (
                contact_index - 1,
                contact_index + 1,
            ):
                if neighbor < 0 or neighbor >= len(blocks):
                    continue

                if neighbor in excluded:
                    continue

                if self._classify_heading(blocks[neighbor]) is not None:
                    continue

                neighbor_text = blocks[neighbor].text.strip()

                if self._looks_like_docx_header_name(neighbor_text):
                    header_indices.add(neighbor)

                elif self._has_contact_signal(neighbor_text):
                    header_indices.add(neighbor)

                elif self._looks_like_docx_contact_metadata(neighbor_text):
                    header_indices.add(neighbor)

        return sorted(header_indices)

    @staticmethod
    def _has_contact_signal(text: str) -> bool:
        """
        Return True when a block contains a recognizable email address or
        phone number.
        """

        has_email = bool(
            re.search(
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
                text,
            )
        )

        has_phone = bool(
            re.search(
                r"(?<!\w)\+?\d[\d ()-]{7,}\d(?!\w)",
                text,
            )
        )

        return has_email or has_phone

    @staticmethod
    def _looks_like_docx_header_name(text: str) -> bool:
        """
        Detect a short name-like paragraph without depending on a specific
        candidate name.
        """

        if not text or len(text.split()) > 8:
            return False

        if re.search(r"[@\d]", text):
            return False

        if any(
            marker in text.lower()
            for marker in (
                "linkedin",
                "github",
                "portfolio",
                "email",
                "phone",
            )
        ):
            return False

        words = re.findall(
            r"[A-Za-z][A-Za-z.'-]*",
            text,
        )

        if not words or len(words) < 2:
            return False

        return all(
            word[0].isupper()
            for word in words
            if word
        )

    @staticmethod
    def _looks_like_docx_contact_metadata(text: str) -> bool:
        """
        Detect short contact/profile metadata that commonly accompanies an
        email/phone block.
        """

        if not text:
            return False

        lower = text.lower()

        markers = (
            "linkedin",
            "github",
            "portfolio",
            "location",
            "india",
            "maharashtra",
        )

        return any(marker in lower for marker in markers)

    def _insert_docx_content_after_heading(
        self,
        blocks: list[DocumentBlock],
        section_type: str,
        content: list[DocumentBlock],
    ) -> list[DocumentBlock]:
        if not content:
            return list(blocks)

        result = list(blocks)

        for index, block in enumerate(result):
            if self._classify_heading(block) != section_type:
                continue

            return (
                result[: index + 1]
                + content
                + result[index + 1 :]
            )

        return result

    @staticmethod
    def _looks_like_summary_group(text: str) -> bool:
        """
        Detect a summary when multiple physical DOCX blocks together form
        one coherent prose group.
        """

        if not text:
            return False

        words = text.split()

        if len(words) < 25:
            return False

        lower = text.lower()

        prose_markers = (
            "student",
            "experience",
            "interested",
            "passionate",
            "focused",
            "seeking",
            "building",
            "developing",
            "working",
            "growing",
            "software engineer",
            "real-world",
        )

        marker_count = sum(
            marker in lower
            for marker in prose_markers
        )

        sentence_like = bool(
            re.search(r"[.!?—]$", text)
        )

        return marker_count >= 2 or sentence_like

    @staticmethod
    def _looks_like_summary_content(text: str) -> bool:
        """
        Backward-compatible single-block summary predicate.
        """

        return ResumeStructureInterpreter._looks_like_summary_group(text)

    @classmethod
    def _looks_like_education_group(cls, text: str) -> bool:
        """
        Detect an education group using combined semantic evidence.
        """

        if not text:
            return False

        lower = text.lower()

        degree_markers = (
            "bachelor",
            "master",
            "doctorate",
            "b.e.",
            "b.tech",
            "m.e.",
            "m.tech",
            "b.s.",
            "m.s.",
            "ph.d",
        )

        education_markers = (
            "university",
            "college",
            "institute",
            "sgpa",
            "cgpa",
            "computer science",
            "engineering",
            "academic",
        )

        degree_signal = any(
            marker in lower
            for marker in degree_markers
        )

        education_signal_count = sum(
            marker in lower
            for marker in education_markers
        )

        date_signal = bool(
            re.search(
                r"\b(?:19|20)\d{2}\b\s*[-–—]\s*"
                r"(?:\b(?:19|20)\d{2}\b|present|current)",
                lower,
            )
        )

        return (
            degree_signal
            or education_signal_count >= 2
            or (
                education_signal_count >= 1
                and date_signal
            )
        )

    @classmethod
    def _looks_like_education_content(cls, text: str) -> bool:
        """
        Backward-compatible single-block education predicate.
        """

        return cls._looks_like_education_group(text)

    # ------------------------------------------------------------------
    # PDF spatial reconstruction
    # ------------------------------------------------------------------

    @staticmethod
    def _has_spatial_information(blocks: tuple[DocumentBlock, ...]) -> bool:
        return any(
            block.source.bbox is not None
            for block in blocks
        )

    def _order_pdf_blocks(
        self,
        blocks: tuple[DocumentBlock, ...],
    ) -> list[DocumentBlock]:
        """
        Order PDF blocks page-by-page.

        For each page:
          1. identify likely columns from block X positions
          2. keep blocks belonging to the same column together
          3. sort blocks vertically inside each column
          4. retain page order

        This is intentionally conservative. It is not attempting to recreate
        the exact visual rendering engine of the PDF. Its purpose is to give
        semantic extraction a substantially better logical sequence.
        """

        by_page: dict[int, list[DocumentBlock]] = {}

        for block in blocks:
            page_number = block.source.page_number or 1
            by_page.setdefault(page_number, []).append(block)

        ordered: list[DocumentBlock] = []

        for page_number in sorted(by_page):
            page_blocks = by_page[page_number]

            if len(page_blocks) <= 1:
                ordered.extend(page_blocks)
                continue

            columns = self._detect_columns(page_blocks)

            if len(columns) == 1:
                ordered.extend(
                    sorted(
                        page_blocks,
                        key=self._vertical_position_key,
                    )
                )
                continue

            # Blocks that span a large part of the page are treated as
            # page-level blocks. These commonly include a resume header or
            # full-width section heading.
            full_width: list[DocumentBlock] = []
            column_blocks: list[list[DocumentBlock]] = [
                [] for _ in columns
            ]

            page_width = self._estimate_page_width(page_blocks)

            for block in page_blocks:
                bbox = block.source.bbox

                if bbox is None:
                    column_blocks[0].append(block)
                    continue

                x0, _, x1, _ = bbox
                width = max(0.0, x1 - x0)

                if page_width > 0 and width >= page_width * 0.65:
                    full_width.append(block)
                    continue

                column_index = self._nearest_column(x0, columns)
                column_blocks[column_index].append(block)

            # If there are page-level blocks, keep them at their vertical
            # position before/among the columns. Otherwise use normal
            # column-major reading order.
            if full_width:
                ordered.extend(
                    self._merge_full_width_and_columns(
                        full_width,
                        column_blocks,
                    )
                )
            else:
                ordered.extend(
                    self._merge_same_row_column_blocks(
                        column_blocks,
                    )
                )

        return ordered

    def _detect_columns(
        self,
        blocks: list[DocumentBlock],
    ) -> list[float]:
        """
        Detect one or two likely columns using block X coordinates.

        We intentionally cap the result at two columns because the resume
        domain overwhelmingly uses one- or two-column layouts.
        """

        starts: list[float] = []

        for block in blocks:
            bbox = block.source.bbox
            if bbox is not None:
                starts.append(float(bbox[0]))

        if len(starts) < 4:
            return [self._median(starts)] if starts else [0.0]

        starts.sort()

        # Find the largest horizontal gap between block starts.
        gaps = [
            starts[index + 1] - starts[index]
            for index in range(len(starts) - 1)
        ]

        if not gaps:
            return [self._median(starts)]

        largest_gap_index = max(
            range(len(gaps)),
            key=lambda index: gaps[index],
        )
        largest_gap = gaps[largest_gap_index]

        min_gap = max(
            45.0,
            (max(starts) - min(starts)) * 0.18,
        )

        if largest_gap < min_gap:
            return [self._median(starts)]

        left = starts[: largest_gap_index + 1]
        right = starts[largest_gap_index + 1 :]

        if len(left) < 2 or len(right) < 2:
            return [self._median(starts)]

        return [
            self._median(left),
            self._median(right),
        ]

    @staticmethod
    def _nearest_column(
        x0: float,
        columns: list[float],
    ) -> int:
        return min(
            range(len(columns)),
            key=lambda index: abs(x0 - columns[index]),
        )

    def _merge_same_row_column_blocks(
        self,
        columns: list[list[DocumentBlock]],
    ) -> list[DocumentBlock]:
        """
        Merge visually aligned cross-column blocks only when the secondary
        block does not belong to an independently headed section.

        This preserves ordinary two-column reading order while allowing
        right-aligned metadata to remain adjacent to the content it visually
        accompanies.

        The decision is based on spatial alignment and existing heading
        semantics.
        """
        if len(columns) <= 1:
            return [
                block
                for column in columns
                for block in sorted(
                    column,
                    key=self._vertical_position_key,
                )
            ]

        sorted_columns = [
            sorted(
                column,
                key=self._vertical_position_key,
            )
            for column in columns
        ]

        primary_column = sorted_columns[0]
        secondary_columns = sorted_columns[1:]

        result: list[DocumentBlock] = []
        emitted_ids: set[int] = set()

        for primary_block in primary_column:
            result.append(primary_block)
            emitted_ids.add(id(primary_block))

            # A heading is an independent semantic anchor. Never pull
            # cross-column content into a heading's section merely because
            # the blocks happen to share the same visual row.
            if self._classify_heading(primary_block) is not None:
                continue

            for secondary_column in secondary_columns:
                for secondary_block in secondary_column:
                    if id(secondary_block) in emitted_ids:
                        continue

                    # Independent section headings always remain in their
                    # own column flow.
                    if self._classify_heading(secondary_block) is not None:
                        continue

                    # If the secondary block already belongs to a section
                    # introduced by a heading in its own column, it is not
                    # metadata belonging to the primary-column block.
                    if self._has_preceding_heading(
                        secondary_column,
                        secondary_block,
                    ):
                        continue

                    if self._same_visual_row(
                        primary_block,
                        secondary_block,
                    ):
                        result.append(secondary_block)
                        emitted_ids.add(id(secondary_block))

        # Preserve any remaining secondary-column blocks in their original
        # top-to-bottom order.
        for secondary_column in secondary_columns:
            for secondary_block in secondary_column:
                if id(secondary_block) not in emitted_ids:
                    result.append(secondary_block)
                    emitted_ids.add(id(secondary_block))

        return result

    def _has_preceding_heading(
        self,
        column: list[DocumentBlock],
        block: DocumentBlock,
    ) -> bool:
        """
        Return True when a semantic section heading occurs before the block
        within the same column.

        A block with no preceding heading is treated as unsectioned metadata,
        making it eligible for same-row association with content in another
        column.
        """
        for candidate in column:
            if candidate is block:
                return False

            if self._classify_heading(candidate) is not None:
                return True

        return False

    @classmethod
    def _same_visual_row(
        cls,
        first: DocumentBlock,
        second: DocumentBlock,
    ) -> bool:
        """
        Return True when two spatially positioned blocks substantially
        overlap vertically.

        A minimum 50% overlap relative to the shorter block prevents nearby
        but distinct lines from being incorrectly grouped into one row.
        """
        first_bbox = first.source.bbox
        second_bbox = second.source.bbox

        if first_bbox is None or second_bbox is None:
            return False

        first_y0 = float(first_bbox[1])
        first_y1 = float(first_bbox[3])
        second_y0 = float(second_bbox[1])
        second_y1 = float(second_bbox[3])

        overlap = max(
            0.0,
            min(first_y1, second_y1)
            - max(first_y0, second_y0),
        )

        first_height = max(1.0, first_y1 - first_y0)
        second_height = max(1.0, second_y1 - second_y0)

        return (
            overlap / min(first_height, second_height)
        ) >= 0.5

    def _merge_full_width_and_columns(
        self,
        full_width: list[DocumentBlock],
        columns: list[list[DocumentBlock]],
    ) -> list[DocumentBlock]:
        """
        Merge page-level blocks with column content.

        A full-width block is placed before the first column content below it.
        This is particularly useful for headers and section headings.
        """

        column_order: list[DocumentBlock] = []

        for column in columns:
            column_order.extend(
                sorted(
                    column,
                    key=self._vertical_position_key,
                )
            )

        full_width_sorted = sorted(
            full_width,
            key=self._vertical_position_key,
        )

        if not full_width_sorted:
            return self._merge_same_row_column_blocks(columns)

        result: list[DocumentBlock] = []
        remaining_columns = list(column_order)

        for full_block in full_width_sorted:
            full_y = self._top_y(full_block)

            while remaining_columns:
                next_block = remaining_columns[0]

                if self._top_y(next_block) >= full_y:
                    break

                result.append(remaining_columns.pop(0))

            result.append(full_block)

        result.extend(remaining_columns)

        # Reconstruct same-row relationships after page-level blocks have
        # been positioned. This is required for layouts where a full-width
        # section heading causes the page to enter this code path, while
        # right-aligned metadata still visually accompanies left-column
        # content.
        return self._merge_adjacent_same_row_metadata(
            result,
            columns,
        )

    def _merge_adjacent_same_row_metadata(
        self,
        ordered: list[DocumentBlock],
        columns: list[list[DocumentBlock]],
    ) -> list[DocumentBlock]:
        """
        Reinsert unsectioned secondary-column blocks beside visually aligned
        primary-column content.

        Full-width blocks are already positioned before this method runs.
        Only blocks that are not semantic section headings and do not have a
        preceding heading in their own column are eligible.

        The method is text-agnostic and relies only on spatial alignment and
        existing heading semantics.
        """
        if len(columns) <= 1:
            return ordered

        column_lookup: dict[int, tuple[int, int]] = {}

        for column_index, column in enumerate(columns):
            sorted_column = sorted(
                column,
                key=self._vertical_position_key,
            )

            for position, block in enumerate(sorted_column):
                column_lookup[id(block)] = (
                    column_index,
                    position,
                )

        primary_column = sorted(
            columns[0],
            key=self._vertical_position_key,
        )

        secondary_columns = [
            sorted(column, key=self._vertical_position_key)
            for column in columns[1:]
        ]

        result: list[DocumentBlock] = []
        emitted: set[int] = set()

        for block in ordered:
            block_id = id(block)

            if block_id in emitted:
                continue

            result.append(block)
            emitted.add(block_id)

            if block not in primary_column:
                continue

            if self._classify_heading(block) is not None:
                continue

            for secondary_column in secondary_columns:
                for candidate in secondary_column:
                    candidate_id = id(candidate)

                    if candidate_id in emitted:
                        continue

                    if self._classify_heading(candidate) is not None:
                        continue

                    if self._has_preceding_heading(
                        secondary_column,
                        candidate,
                    ):
                        continue

                    if self._same_visual_row(block, candidate):
                        result.append(candidate)
                        emitted.add(candidate_id)

        return result


    @staticmethod
    def _vertical_position_key(
        block: DocumentBlock,
    ) -> tuple[float, float, int]:
        bbox = block.source.bbox

        if bbox is None:
            return (
                float(block.source.block_index or 0),
                0.0,
                int(block.source.block_index or 0),
            )

        x0, y0, _, _ = bbox

        return (
            float(y0),
            float(x0),
            int(block.source.block_index or 0),
        )

    @staticmethod
    def _top_y(block: DocumentBlock) -> float:
        bbox = block.source.bbox

        if bbox is None:
            return float(block.source.block_index or 0)

        return float(bbox[1])

    @staticmethod
    def _estimate_page_width(
        blocks: list[DocumentBlock],
    ) -> float:
        x1_values = [
            float(block.source.bbox[2])
            for block in blocks
            if block.source.bbox is not None
        ]

        return max(x1_values, default=0.0)

    @staticmethod
    def _median(values: list[float]) -> float:
        if not values:
            return 0.0

        ordered = sorted(values)
        middle = len(ordered) // 2

        if len(ordered) % 2:
            return ordered[middle]

        return (ordered[middle - 1] + ordered[middle]) / 2.0

    # ------------------------------------------------------------------
    # Heading detection
    # ------------------------------------------------------------------

    def _classify_heading(
        self,
        block: DocumentBlock,
    ) -> str | None:
        normalized = self._normalize_heading(block.text)

        if not normalized:
            return None

        section_type = self._SECTION_ALIASES.get(normalized)

        if section_type is not None:
            return section_type

        # DOCX provides native heading semantics. Preserve the distinction
        # between an unknown heading and ordinary paragraph content.
        if block.block_type == DocumentBlockType.HEADING:
            return ResumeSectionType.UNKNOWN

        return None

    def _normalize_heading(self, text: str) -> str:
        normalized = text.strip().lower()

        for source, replacement in self._HEADING_NORMALIZATION_REPLACEMENTS.items():
            normalized = normalized.replace(source, replacement)

        return " ".join(normalized.split())

    # ------------------------------------------------------------------
    # Section handling
    # ------------------------------------------------------------------

    @classmethod
    def _extract_heading_row_blocks(
        cls,
        blocks: list[DocumentBlock],
        heading: DocumentBlock,
    ) -> list[DocumentBlock]:
        """
        Identify blocks immediately preceding a heading that visually occupy
        the same row as that heading.

        This handles layouts where section metadata is right-aligned beside
        the heading, which can cause PDF column reconstruction to place the
        metadata immediately before the heading in reading order.

        The method is deliberately text-agnostic: it uses only spatial
        relationships and never assumes that the block is a date, GPA,
        location, or any other particular content type.
        """
        if not blocks:
            return []

        heading_bbox = heading.source.bbox
        if heading_bbox is None:
            return []

        heading_page = heading.source.page_number
        heading_y0 = float(heading_bbox[1])
        heading_y1 = float(heading_bbox[3])
        heading_height = max(1.0, heading_y1 - heading_y0)

        extracted: list[DocumentBlock] = []

        for candidate in reversed(blocks):
            candidate_bbox = candidate.source.bbox

            if candidate_bbox is None:
                break

            if (
                heading_page is not None
                and candidate.source.page_number != heading_page
            ):
                break

            candidate_y0 = float(candidate_bbox[1])
            candidate_y1 = float(candidate_bbox[3])

            overlap = max(
                0.0,
                min(candidate_y1, heading_y1)
                - max(candidate_y0, heading_y0),
            )

            candidate_height = max(1.0, candidate_y1 - candidate_y0)
            overlap_ratio = overlap / min(
                candidate_height,
                heading_height,
            )

            if overlap_ratio < 0.5:
                break

            extracted.insert(0, candidate)

        return extracted

    @staticmethod
    def _flush_section(
        sections: list[ResumeSection],
        section_type: str,
        heading: str | None,
        blocks: list[DocumentBlock],
    ) -> None:
        if not blocks and heading is None:
            return

        sections.append(
            ResumeSection(
                section_type=section_type,
                heading=heading,
                blocks=tuple(blocks),
            )
        )