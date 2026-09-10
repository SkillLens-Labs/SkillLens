SkillLens --- Data Schema
=======================

1\. Purpose
-----------

This document defines the canonical data structures and data boundaries used throughout SkillLens.

The schema provides a shared contract between:

-   document processing

-   resume analysis

-   skill extraction

-   skill normalization

-   ESCO mapping

-   evidence and confidence tracking

-   future semantic matching

-   gap analysis

-   scoring

-   explainability

-   career intelligence

-   recommendations

-   API responses

-   frontend state

The objective is to ensure that each analytical concept has one consistent representation.

* * * * *

2\. Schema Design Principles
============================

SkillLens follows these principles:

1.  Every major analytical concept has one canonical representation.

2.  Domain models are independent of API transport details.

3.  Source evidence should be preserved whenever an analytical conclusion is generated.

4.  Confidence uses a `0--1` scale.

5.  Public compatibility scores use a `0--100` scale.

6.  Optional analytical modules use explicit `null` or empty collections rather than fabricated values.

7.  Identifiers remain stable within an analysis.

8.  Resume-only analysis must not invent job-related information.

9.  Breaking schema changes require schema versioning.

10. Phase boundaries must be respected; downstream components consume established contracts rather than duplicating upstream processing.

* * * * *

3\. Schema Version
==================

`AnalysisResult` contains:

`schema_version`

Current initial schema version:

`1.0`

Schema versioning allows future breaking changes without silently changing the meaning of previously generated analysis results.

* * * * *

4\. Identifier Conventions
==========================

Canonical identifiers include:

-   `analysis_id` --- unique analysis identifier

-   `document_id` --- source document identifier

-   `profile_id` --- resume or job profile identifier

-   `skill_id` --- normalized skill identifier

-   `evidence_id` --- evidence identifier

-   `recommendation_id` --- recommendation identifier

-   `gap_id` --- skill-gap identifier

Identifiers should not depend on display names.

* * * * *

5\. AnalysisResult
==================

`AnalysisResult` is the canonical top-level analytical result.

Conceptual structure:

```
AnalysisResult
├── analysis_id
├── schema_version
├── analysis_mode
├── status
├── created_at
├── input
├── resume_profile
├── job_profile
├── skill_analysis
├── scoring
├── xai
├── career_intelligence
├── recommendations
└── metadata

```

### Core fields

`analysis_id`

Unique analysis identifier.

`schema_version`

Version of the result schema.

`analysis_mode`

Allowed values:

-   `RESUME_ONLY`

-   `RESUME_JD`

`status`

Allowed values:

-   `pending`

-   `processing`

-   `completed`

-   `failed`

`created_at`

Creation timestamp. API representations should use ISO 8601.

`input`

Information about source documents and analysis configuration.

`resume_profile`

Canonical structured representation of the resume.

`job_profile`

Canonical job-description representation.

For `RESUME_ONLY`:

`null`

For `RESUME_JD`:

A populated `JobProfile`.

`skill_analysis`

Skill-level analytical results.

`scoring`

Official scoring result.

For resume-only analysis, JD-dependent scoring is `null`.

`xai`

Explainability result when available; otherwise `null`.

`career_intelligence`

Higher-level career analysis when available.

`recommendations`

Generated recommendations. An empty list means no recommendations were generated.

`metadata`

Technical and analytical metadata.

* * * * *

6\. AnalysisInput
=================

`AnalysisInput` describes the source documents and analysis configuration.

```
AnalysisInput
├── resume_document_id
├── job_document_id
├── options
└── client_metadata

```

`resume_document_id`

Required resume document identifier.

`job_document_id`

Required only for `RESUME_JD`.

For `RESUME_ONLY`:

`null`

`options`

Analysis configuration.

`client_metadata`

Optional client-supplied metadata.

* * * * *

7\. AnalysisMetadata
====================

`AnalysisMetadata` contains technical information associated with processing.

Possible fields include:

-   processing time

-   parser information

-   extractor versions

-   taxonomy version

-   pipeline version

-   warnings

-   diagnostics

Metadata must not replace canonical analytical fields.

Phase 3 metadata may include:

-   builder version

-   ESCO version

-   skill count

-   extraction diagnostics

* * * * *

8\. ResumeProfile
=================

`ResumeProfile` is the canonical structured representation of a resume.

Current conceptual structure:

```
ResumeProfile
├── profile_id
├── document_id
├── candidate_summary
├── contact
├── education[]
├── experience[]
├── projects[]
├── certifications[]
├── skills[]
├── skill_categories[]
├── total_experience
├── seniority
├── domains[]
└── metadata

```

### Core fields

`profile_id`

Unique resume-profile identifier.

`document_id`

Source `ParsedDocument` identifier.

`candidate_summary`

Candidate summary when extracted.

`contact`

Contact information when available.

`education[]`

Education records.

`experience[]`

Professional experience records.

`projects[]`

Project records.

`certifications[]`

Certification records.

`skills[]`

Canonical normalized skills identified from the resume.

`skill_categories[]`

High-level skill categories.

Examples:

-   programming

-   data

-   web

-   cloud_devops

-   database

-   machine learning

`total_experience`

Experience information when it can be reliably extracted.

`seniority`

Inferred seniority when supported by evidence.

`domains[]`

Identified professional domains.

`metadata`

Additional structured processing information.

### Phase 3 status

Phase 3 establishes the resume-profile construction boundary and populates canonical skills, skill categories, evidence, confidence, and provenance.

Fields for detailed education, experience, projects, certifications, total experience, seniority, and domains remain available for future structured extraction and must not be populated with invented information.

* * * * *

9\. Contact
===========

`Contact` represents resume contact information.

Potential fields:

-   name

-   email

-   phone

-   location

-   LinkedIn

-   GitHub

-   portfolio

Contact information is optional and is not required for analytical processing.

* * * * *

10\. Education
==============

`Education` represents an educational qualification.

Potential fields:

-   institution

-   degree

-   field

-   start_date

-   end_date

-   grade

-   description

-   evidence

Extracted evidence should be preserved where possible.

* * * * *

11\. Experience
===============

`Experience` represents professional or relevant experience.

Potential fields:

-   company

-   role

-   location

-   start_date

-   end_date

-   description

-   responsibilities

-   technologies

-   achievements

-   evidence

Experience records should preserve source evidence where possible.

* * * * *

12\. Project
============

`Project` represents a project described in a resume.

Potential fields:

-   name

-   description

-   technologies

-   responsibilities

-   outcomes

-   links

-   evidence

Projects may provide important evidence for skill extraction.

* * * * *

13\. Certification
==================

`Certification` represents a professional certification.

Potential fields:

-   name

-   issuing_organization

-   issue_date

-   expiry_date

-   credential_id

-   credential_url

-   evidence

* * * * *

14\. JobProfile
===============

`JobProfile` is the canonical representation of a structured job description.

This is a planned Phase 4+ analytical structure and was not implemented as part of Phase 3.

Conceptual structure:

```
JobProfile
├── profile_id
├── document_id
├── job_title
├── company
├── summary
├── responsibilities[]
├── required_skills[]
├── preferred_skills[]
├── technical_skills[]
├── soft_skills[]
├── domain_skills[]
├── experience_requirements
├── education_requirements
├── seniority
└── metadata

```

The structure supports future JD analysis without changing the resume-analysis contract.

* * * * *

15\. Skill
==========

`Skill` is the canonical analytical representation of a normalized skill.

Conceptual structure:

```
Skill
├── skill_id
├── canonical_name
├── display_name
├── category
├── subcategory
├── aliases[]
├── proficiency
├── importance
├── evidence[]
├── confidence
└── metadata

```

### Core fields

`skill_id`

Stable skill identifier.

`canonical_name`

Normalized internal skill name.

Example:

`python`

`display_name`

Human-readable name.

Example:

`Python`

`category`

High-level skill category.

`subcategory`

Optional finer classification.

`aliases[]`

Known alternative forms.

`proficiency`

Only populated when sufficient evidence exists.

`importance`

Primarily relevant to job-description skills.

`evidence[]`

Evidence supporting the skill.

`confidence`

Confidence that the skill was correctly identified and normalized.

`metadata`

Additional extraction or taxonomy information.

* * * * *

16\. NormalizedSkill
====================

Phase 3 introduces an explicit normalization representation:

```
NormalizedSkill
├── canonical_name
├── raw_text
└── extraction_confidence

```

The normalization layer:

-   applies Unicode normalization

-   normalizes whitespace and case

-   resolves known aliases

-   produces a canonical skill identity

-   preserves the original extracted text

-   preserves extraction confidence

Examples:

```
Python Programming → python
Python 3           → python
ReactJS            → react
Postgres           → postgresql
ML                 → machine learning

```

Normalization does not perform semantic matching.

* * * * *

17\. Evidence
=============

`Evidence` connects an analytical result to its source.

Conceptual structure:

```
Evidence
├── evidence_id
├── source_type
├── source_document_id
├── section
├── text
├── start_offset
├── end_offset
├── evidence_type
├── extractor
├── relevance
└── confidence

```

### Source information

`source_type`

Identifies the source of evidence.

Examples:

-   `resume`

-   `job_description`

-   `generated_analysis`

`source_document_id`

Source document identifier.

`section`

Logical section containing the evidence.

Examples:

-   Skills

-   Experience

-   Projects

-   Education

-   Requirements

`text`

Source text associated with the evidence.

`start_offset` / `end_offset`

Character offsets when available.

`evidence_type`

Examples:

-   `explicit_skill`

-   `contextual_skill`

-   `experience`

-   `project`

-   `requirement`

-   `achievement`

`extractor`

Component responsible for identifying the evidence.

`relevance`

Optional relevance value.

`confidence`

Confidence in the evidence interpretation.

* * * * *

18\. SkillMention
=================

Phase 3 introduces `SkillMention` as the intermediate extraction representation.

Conceptual structure:

```
SkillMention
├── raw_text
├── skill_name
├── evidence_type
├── block
├── start_offset
├── end_offset
└── confidence

```

A `SkillMention` represents a detected occurrence before normalization and profile construction.

It preserves:

-   original text

-   source block

-   offsets

-   evidence type

-   extraction confidence

`SkillMention` is an intermediate analysis structure and is not the final canonical profile skill.

* * * * *

19\. Confidence
===============

`Confidence` provides a standardized confidence representation.

Conceptual structure:

```
Confidence
├── score
├── level
├── components
└── rationale

```

`score`

Range:

`0--1`

`level`

Allowed values:

-   `low`

-   `medium`

-   `high`

`components`

Contributing signals, such as:

-   extraction confidence

-   semantic confidence

-   evidence confidence

-   taxonomy confidence

`rationale`

Human-readable explanation when required.

Phase 3 uses confidence during skill extraction, ESCO mapping, and final profile construction.

* * * * *

20\. ESCO Mapping
=================

Phase 3 introduces ESCO mapping as a separate analytical boundary.

Conceptual structure:

```
ESCOMapResult
├── input_name
├── status
├── candidates[]
└── mapping_method

```

Mapping status:

-   `MAPPED`

-   `AMBIGUOUS`

-   `UNMAPPED`

An ESCO candidate may contain:

-   canonical name

-   URI

-   confidence

-   description

The implementation currently uses a deterministic adapter vocabulary and ESCO version metadata.

Current ESCO version:

`1.2.1`

A missing ESCO URI must remain empty rather than being replaced with a fabricated identifier.

The architecture allows the official ESCO dataset or API to be connected later through the mapper boundary.

* * * * *

21\. Resume Profile Skill Construction
======================================

Phase 3 establishes the following data flow:

```
ParsedDocument
      ↓
Resume Structure
      ↓
SkillMention[]
      ↓
NormalizedSkill[]
      ↓
ESCO Mapping
      ↓
Evidence + Confidence
      ↓
ResumeProfile

```

The `ResumeProfileBuilder` is responsible for converting these intermediate results into the canonical resume representation.

The builder:

-   deduplicates canonical skills

-   merges evidence

-   preserves provenance

-   aggregates confidence

-   assigns deterministic skill categories

-   records processing metadata

-   does not invent unsupported candidate information

* * * * *

22\. SkillMatch
===============

`SkillMatch` represents a relationship between a resume skill and a job skill.

This is a future semantic-matching structure.

```
SkillMatch
├── resume_skill_id
├── job_skill_id
├── relationship
├── similarity
├── confidence
├── evidence[]
└── rationale

```

Possible relationships:

-   `exact`

-   `strong_semantic`

-   `partial`

-   `related`

-   `unmatched`

Similarity and confidence use the `0--1` internal scale.

Skill matching is not implemented in Phase 3.

* * * * *

23\. SkillGap
=============

`SkillGap` represents a candidate-job skill gap.

Future structure:

```
SkillGap
├── gap_id
├── skill
├── gap_type
├── severity
├── importance
├── evidence[]
├── related_matches[]
├── rationale
└── confidence

```

Possible gap types:

-   `missing`

-   `partial`

-   `insufficient_proficiency`

-   `contextual_gap`

Skill-gap analysis is not implemented in Phase 3.

* * * * *

24\. SkillAnalysis
==================

`SkillAnalysis` combines skill-level analytical results.

```
SkillAnalysis
├── resume_skills[]
├── job_skills[]
├── skill_matches[]
├── skill_gaps[]
└── summary

```

For `RESUME_ONLY`:

-   `resume_skills` is populated when skills are found

-   `job_skills` is empty

-   `skill_matches` is empty

-   JD-specific skill gaps are not generated

For `RESUME_JD`, applicable fields may be populated after JD analysis and matching are implemented.

* * * * *

25\. ScoringResult
==================

`ScoringResult` is the future canonical representation of candidate-job compatibility scoring.

Conceptual structure:

```
ScoringResult
├── overall_score
├── skill_score
├── required_skill_score
├── preferred_skill_score
├── experience_score
├── education_score
├── domain_score
├── dimension_scores[]
├── weights[]
├── penalties[]
├── bonuses[]
└── confidence

```

Public score range:

`0--100`

ScoreEngine is the sole owner of official score calculation.

Scoring is not implemented in Phase 3.

* * * * *

26\. XAIResult
==============

`XAIResult` represents explanations derived from existing analytical outputs.

Conceptual structure:

```
XAIResult
├── overall_explanation
├── score_explanation
├── strengths[]
├── weaknesses[]
├── matched_skill_explanations[]
├── missing_skill_explanations[]
├── partial_match_explanations[]
├── evidence_map[]
└── confidence

```

XAIEngine does not own official scores. It explains outputs produced by canonical analytical engines.

XAI is not implemented in Phase 3.

* * * * *

27\. EvidenceMapEntry
=====================

`EvidenceMapEntry` connects an analytical conclusion to supporting evidence.

Potential fields:

-   `result_type`

-   `result_id`

-   `evidence_ids[]`

-   `explanation`

-   `confidence`

This structure supports future frontend explanations and traceability.

* * * * *

28\. CareerIntelligence
=======================

`CareerIntelligence` represents higher-level career analysis.

Potential areas include:

-   inferred profile

-   experience level

-   primary domains

-   secondary domains

-   strengths

-   career signals

-   potential roles

-   role fit

-   transition analysis

-   skill priorities

-   risks

-   confidence

Career intelligence may eventually operate in both resume-only and resume-JD modes.

It is not implemented in Phase 3.

* * * * *

29\. Recommendation
===================

`Recommendation` represents an actionable recommendation generated from analytical results.

Conceptual structure:

```
Recommendation
├── recommendation_id
├── type
├── title
├── target_skill
├── priority
├── rationale
├── expected_impact
├── effort
├── evidence[]
├── related_gap_ids[]
└── confidence

```

Possible types:

-   `skill_development`

-   `project`

-   `certification`

-   `resume_improvement`

-   `career_direction`

RecommendationEngine is the sole recommendation owner.

Recommendations are not implemented in Phase 3.

* * * * *

30\. Resume-Only Schema Rules
=============================

When:

`analysis_mode = RESUME_ONLY`

the system must enforce:

```
job_profile = null
scoring = null
job_skills = []
skill_matches = []
JD-specific skill gaps = not generated

```

Resume-only analysis may produce:

-   resume profile

-   skills

-   evidence

-   confidence

-   career intelligence

-   strengths

-   career signals

-   potential roles

-   recommendations

The system must never invent a job description to produce a match score.

* * * * *

31\. Resume + JD Schema Rules
=============================

When:

`analysis_mode = RESUME_JD`

the system may eventually populate:

-   resume profile

-   job profile

-   resume skills

-   job skills

-   skill matches

-   skill gaps

-   scoring

-   XAI

-   career intelligence

-   recommendations

JD-specific outputs must remain traceable to the supplied job description and candidate evidence.

* * * * *

32\. Empty and Optional Values
==============================

SkillLens distinguishes between:

-   unavailable

-   not applicable

-   empty collection

-   `null`

Examples:

```
job_profile = null

```

means a job profile is not applicable.

```
recommendations = []

```

means the analysis completed but produced no recommendations.

Optional analytical modules should use `null` when unavailable or disabled.

Collections should generally use empty lists when the concept exists but contains no items.

* * * * *

33\. Evidence Preservation
==========================

Evidence is a core architectural requirement.

Preferred relationship:

```
Source Document
      ↓
Evidence
      ↓
Skill / Match / Gap / Explanation / Recommendation

```

The system should be able to answer:

-   What source text caused this skill to be extracted?

-   Why was this skill considered relevant?

-   Why was a skill considered missing?

-   Why did a skill affect a score?

-   Why was a recommendation generated?

Phase 3 preserves document provenance through `DocumentBlock`, `SkillMention`, and final skill evidence.

* * * * *

34\. Confidence Propagation
===========================

Confidence uses one canonical external scale:

`0--1`

Conceptually:

```
Document Evidence
      ↓
Extraction Confidence
      ↓
Normalization / Mapping Signals
      ↓
Analytical Confidence
      ↓
Future Matching / Gap / Scoring Confidence

```

Individual engines may use different internal signals, but exposed confidence remains standardized.

* * * * *

35\. Numeric Scales
===================

SkillLens uses two primary numeric scales.

### Public compatibility scores

Range:

`0--100`

Used for:

-   overall compatibility

-   dimension scores

-   user-facing scoring

### Internal values

Range:

`0--1`

Used for:

-   confidence

-   semantic similarity

-   model-level similarity

-   mapping confidence

The two scales must never be silently mixed.

* * * * *

36\. Domain, API, and Frontend Ownership
========================================

The domain layer is the canonical owner of analytical data structures.

Architecture:

```
Domain Models
      ↓
API Schemas
      ↓
JSON Response
      ↓
Frontend TypeScript Types

```

The frontend must not become the source of truth for domain definitions.

API schemas represent transport contracts and may differ from internal domain models when necessary.

* * * * *

37\. Phase 1 Schema Foundation
==============================

Phase 1 established the initial canonical domain model modules under:

`backend/app/domain/`

Including:

-   `analysis.py`

-   `resume.py`

-   `job.py`

-   `skill.py`

-   `evidence.py`

-   `confidence.py`

-   `matching.py`

-   `gaps.py`

-   `scoring.py`

-   `xai.py`

-   `career.py`

-   `recommendations.py`

Frontend analysis types were established under:

`frontend/src/types/analysis.ts`

API contracts are defined under:

`backend/app/schemas/`

Phase 1 established the schema foundation without implementing the advanced analytical engines.

* * * * *

38\. Phase 2 Document Processing Schema
=======================================

Phase 2 introduced the normalized document-processing boundary between raw documents and analytical extraction.

DocumentType
------------

Supported types:

```
pdf
docx

```

DocumentBlockType
-----------------

Supported normalized block types:

```
paragraph
heading
bullet
table_cell

```

SourceLocation
--------------

`SourceLocation` preserves the origin of a normalized block.

Fields:

```
page_number
paragraph_index
table_index
row_index
column_index
block_index
bbox

```

All provenance fields are optional because available information depends on the source format.

DocumentBlock
-------------

`DocumentBlock` represents one normalized document block.

Fields:

```
text
block_type
source
style_name
section
metadata

```

ParsedDocument
--------------

`ParsedDocument` is the frozen Phase 2 boundary object.

Fields:

```
document_id
document_type
blocks[]
metadata

```

Downstream Phase 3 components consume `ParsedDocument` directly.

They must not reparse PDF or DOCX files.

* * * * *

39\. Phase 2 → Phase 3 Data Boundary
====================================

The frozen architecture is:

```
Raw PDF / DOCX
      ↓
DocumentProcessor
      ↓
ParsedDocument
      ↓
ResumeStructureInterpreter
      ↓
SkillExtractor
      ↓
SkillNormalizer
      ↓
ESCOMapper
      ↓
ResumeProfileBuilder
      ↓
ResumeProfile

```

`ParsedDocument` is an infrastructure-level representation.

It is not:

-   a resume profile

-   a job profile

-   a skill graph

-   a match result

-   a score

-   an explanation

-   a recommendation

* * * * *

40\. Schema Validation Rules
============================

Implementations must validate:

-   identifier presence

-   enum values

-   numeric ranges

-   required fields

-   nullable fields

-   relationship types

-   confidence ranges

-   score ranges

-   analysis-mode-specific constraints

Invalid domain states should not be silently accepted.

* * * * *

41\. Data Schema Invariants
===========================

The following are architectural invariants:

1.  `AnalysisResult` is the canonical top-level result.

2.  `analysis_id` identifies an analysis.

3.  `schema_version` identifies the result schema version.

4.  `analysis_mode` determines whether a job profile is expected.

5.  Resume-only analysis does not generate JD-specific scoring.

6.  Public scores use `0--100`.

7.  Internal similarity and confidence use `0--1`.

8.  Confidence has one canonical structure.

9.  Evidence is the preferred mechanism for supporting analytical conclusions.

10. Skill normalization produces canonical skill identities.

11. `ParsedDocument` is the frozen document-processing boundary.

12. Phase 3 consumes normalized document blocks rather than reparsing source files.

13. ESCO mapping is owned by `ESCOMapper`.

14. `ResumeProfileBuilder` is responsible for canonical resume-profile construction.

15. ScoreEngine owns official scoring.

16. XAIEngine explains existing analytical outputs.

17. RecommendationEngine owns recommendations.

18. Domain structures remain independent of frontend implementation details.

19. API schemas must remain compatible with frontend contracts.

20. Breaking schema changes require schema versioning.

21. Analytical components must not invent unsupported candidate or job facts.

* * * * *

42\. Current Implementation Status
==================================

### Implemented

Phase 1:

-   canonical domain schema foundation

-   API schema foundation

-   frontend analysis types

Phase 2:

-   `DocumentType`

-   `DocumentBlockType`

-   `SourceLocation`

-   `DocumentBlock`

-   `ParsedDocument`

-   normalized document-processing boundary

Phase 3:

-   `ResumeSection`

-   `StructuredResume`

-   `SkillMention`

-   `NormalizedSkill`

-   `ESCOMapResult`

-   evidence preservation

-   confidence handling

-   canonical `ResumeProfile` construction

### Planned

Future phases:

-   JobProfile construction

-   semantic skill matching

-   skill-gap analysis

-   scoring

-   XAI

-   career intelligence

-   recommendations

-   full ESCO dataset integration

-   broader resume structure extraction

The schema is designed so these capabilities can be added without breaking the Phase 2 document boundary or Phase 3 resume-profile contract.
---

## Phase 4 — Resume Quality & ATS Intelligence — Completed

Phase 4 has been completed through the implementation and integration of Resume Quality Intelligence, ATS Intelligence, canonical `AnalysisResult` integration, the centralized Analysis Orchestrator, and the Resume Analysis API.

The complete Phase 4 workflow is:

`Resume Upload → Document Processing → StructuredResume → Skill Extraction → Normalization → ESCO Mapping → ResumeProfile → Resume Quality → ATS Intelligence → AnalysisResult → API Response`

Completed Phase 4 stages:

- Phase 4B — Resume Quality Intelligence
- Phase 4C — ATS Intelligence
- Phase 4D — Canonical AnalysisResult Integration
- Phase 4E — Analysis Orchestrator
- Phase 4F — Analysis API Integration
- Phase 4G — End-to-End Integration & Regression
- Phase 4H — Documentation, Verification & Freeze

Phase 4 preserves the frozen Phase 2 document-processing boundary and reuses the Phase 3 resume-intelligence pipeline without introducing duplicate parsing, skill extraction, normalization, or ESCO mapping systems.

Resume + Job Description analysis, semantic matching, scoring, XAI, recommendations, career intelligence, LLM-based analysis, background workers, Redis, Celery, and other Phase 5 functionality remain explicitly out of scope.

Final verification:

- Focused Phase 4 integration tests: **28 passed**
- Full regression suite: **160 passed**
- Warnings: **7 dependency/deprecation warnings**
- Python compilation: **passed**
- `git diff --check`: **passed**

The complete Phase 4 implementation history is documented in:

`docs/PHASE_4.md`

Phase 4 is now considered the frozen Resume Quality & ATS Intelligence baseline for the next project phase.

PHASE 5 --- COMPLETE & FROZEN ✅
=============================

Phase 5 of **SkillLens --- XAI-Driven Semantic Skill Gap Analysis using Transformer-Based Language Models** has been fully **implemented, integrated, tested, verified, documented, committed, and frozen**.

Phase 5 introduced the complete **JD Intelligence & Resume--JD Matching** layer, including:

-   Job Description document processing

-   JD structure interpretation

-   JD requirement extraction

-   Required vs Preferred classification

-   Skill / Experience / Education / Certification requirements

-   JD skill extraction

-   Reuse of the existing SkillNormalizer

-   Reuse of the existing ESCOMapper

-   JobProfile construction

-   Exact skill matching

-   Semantic skill matching using `all-MiniLM-L6-v2`

-   Cosine similarity

-   Match relationship classification

-   Requirement alignment

-   Evidence and confidence preservation

-   MatchingResult integration

-   AnalysisResult integration

-   Resume--JD orchestration

-   `POST /api/v1/analyses/resume-jd` API integration

-   OpenAPI verification

-   Resume-only backward-compatibility verification

-   Dedicated Phase 5 unit/API tests

-   Full regression testing

-   Compilation verification

-   Git diff verification

Final verification:

`245 tests passed, 7 dependency-level warnings`

Git commit:

`2045b40 Complete Phase 5 JD intelligence and resume-JD matching`

Full commit:

`2045b408a1fdfcc02edb0408dcf1d2a0aa4fc02e`

Working tree is clean.

### Important Phase Boundary

Phase 5 intentionally stops at structured Resume--JD matching evidence.

Final candidate-job scoring, skill-gap scoring, and XAI are **NOT part of Phase 5** and remain reserved for **Phase 6 --- Scoring & XAI**.

### Documentation

A dedicated and comprehensive Phase 5 document has been created:

`docs/PHASE_5.md`

This file contains the **complete Phase 5 implementation history, architecture, components, data flow, API integration, semantic matching, requirement alignment, tests, verification, and freeze status**.

Only the relevant central documentation files were updated with the necessary current-state information. The complete Phase 5 details should **not be reconstructed from the older documentation**.

**For all new/current Phase 5 information, implementation details, verification evidence, and decisions, refer to:**

`docs/PHASE_5.md`

Phase 5 is officially **COMPLETE & FROZEN 🔒**

Next phase:

**PHASE 6 --- SCORING & XAI**

Phase 6 --- Scoring, Gap and XAI Schema Extensions
------------------------------------------------

**Status: COMPLETE / FROZEN**

Phase 6 extends the canonical analytical domain with:

```
SkillGap
SkillAnalysis
DimensionScore
ScoreAdjustment
ScoreContribution
ScoringResult

```

The existing XAI domain contract is reused:

```
SkillExplanation
EvidenceMapEntry
XAIResult

```

### SkillGap

A `SkillGap` is requirement-linked and preserves:

```
requirement_id
requirement_type
target_skill_id
target_skill_name
match_status
gap_type
similarity
rationale
evidence
confidence

```

### ScoringResult

`ScoringResult` contains:

```
overall_score
skill_score
required_skill_score
preferred_skill_score
experience_score
education_score
domain_score
dimension_scores
weights
contributions
penalties
bonuses
confidence

```

### ScoreContribution

A `ScoreContribution` contains:

```
contribution_id
dimension
source_type
source_id
score
weight
contribution
rationale
requirement_type

```

### Scale

Internal scoring:

```
0.0 - 1.0

```

Public scoring:

```
0.0 - 100.0

```

### Design Rules

-   UNKNOWN is distinct from UNMATCHED.

-   Similarity is distinct from confidence.

-   Evidence and confidence are preserved.

-   Required and preferred requirements remain distinct.

-   XAI explains existing results rather than redefining them.

The complete Phase 6 schema changes are documented in:

`docs/PHASE_6.md`

PHASE 7 --- COMPLETION NOTICE
===========================

Phase 7 --- Career Intelligence
-----------------------------

Phase 7 has been fully implemented, integrated, tested, and verified.

The phase introduces the deterministic Career Intelligence layer, including:

-   Versioned career-role taxonomy

-   Deterministic role matching and generalized role-fit scoring

-   Evidence-backed role fit and confidence

-   Seniority intelligence

-   Domain classification

-   Primary and secondary career directions

-   Insufficient-evidence handling

-   Transferable skills

-   Strengths and evidence limitations

-   Resume-only Career Intelligence

-   Resume + Job Description compatibility

-   Integration into the existing `ConcreteAnalysisOrchestrator`

-   Existing API compatibility

-   Comprehensive unit, orchestrator, API, and regression testing

Phase 7 does **not** introduce a dedicated career endpoint or a second orchestrator.

### Verification

```
44 targeted Career Intelligence + orchestrator tests passed
14 API tests passed
311 full regression tests passed
OpenAPI 3.1.0 verified
compileall passed
git diff --check passed

```

The remaining warnings are existing dependency/deprecation warnings and do not represent Phase 7 functional failures.

### Authoritative Phase 7 Documentation

For the complete implementation details, architecture decisions, taxonomy, scoring methodology, evidence handling, seniority logic, API integration, test coverage, verification results, boundaries, and completion criteria, refer to:

```
docs/PHASE_7.md

```

`docs/PHASE_7.md` is the authoritative detailed record for Phase 7.

This document should not duplicate the complete Phase 7 implementation history. Future development should refer to `docs/PHASE_7.md` for detailed Phase 7 information.

PHASE 8 STATUS

Phase 8 --- Recommendation Intelligence & Local LLM Integration is COMPLETE, TESTED, COMMITTED, VERIFIED, and FROZEN.

The phase introduced deterministic recommendation generation, structured requirement recommendations, optional Local LLM/Ollama enhancement, controlled LLM fallback behavior, and integration with the existing Analysis Orchestrator.

Verification:

- Phase 8 focused tests: 52 passed

- Full backend suite: 345 passed

- Working tree clean

- Commit: 176ed73

For complete Phase 8 implementation details, testing evidence, architectural decisions, and file-level changes, refer to:

docs/PHASE_8.md