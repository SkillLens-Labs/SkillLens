# SkillLens --- Data Schema

## 1\. Purpose

This document defines the canonical data structures used throughout SkillLens.

The data schema provides a shared contract between:

- document processing

- skill extraction

- skill normalization

- semantic matching

- gap analysis

- scoring

- explainability

- career intelligence

- recommendations

- API responses

- frontend state

The objective is to ensure that every layer uses consistent representations of the same analytical concepts.

---

# 2\. Schema Design Principles

The SkillLens data model follows these principles:

1.  Every major analytical concept has one canonical representation.

2.  Domain models are independent of API transport details.

3.  Evidence should be preserved whenever an analytical conclusion is generated.

4.  Confidence uses a consistent 0--1 scale.

5.  Public scores use a 0--100 scale.

6.  Resume-only analysis must support a null job profile.

7.  Analysis results must be serializable for API responses and persistence.

8.  Optional analytical modules must be represented explicitly rather than through fabricated values.

9.  Identifiers should remain stable within an analysis.

10. Schema changes should be versioned when they are breaking.

---

# 3\. Schema Version

Every `AnalysisResult` contains:

`schema_version`

Initial schema version:

`1.0`

The schema version allows future versions of the data contract to be introduced without silently changing the meaning of existing analysis results.

---

# 4\. Identifier Conventions

The following identifiers are used throughout the system:

- `analysis_id` --- unique analysis identifier

- `document_id` --- unique uploaded document identifier

- `profile_id` --- unique resume or job profile identifier

- `skill_id` --- unique normalized skill identifier

- `evidence_id` --- unique evidence identifier

- `recommendation_id` --- unique recommendation identifier

Identifiers should be unique within their respective entity scope and should not depend on display names.

---

# 5\. AnalysisResult

`AnalysisResult` is the canonical top-level data structure.

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

## Fields

### analysis_id

Unique identifier for the analysis.

Type:

`string`

### schema_version

Version of the analysis schema.

Type:

`string`

### analysis_mode

Analysis mode.

Allowed values:

- `RESUME_ONLY`

- `RESUME_JD`

### status

Current analysis status.

Allowed values:

- `pending`

- `processing`

- `completed`

- `failed`

### created_at

Timestamp representing when the analysis was created.

Type:

`datetime`

The API representation should use an ISO 8601 compatible string.

### input

Contains information about the documents and analysis configuration used as input.

### resume_profile

Canonical parsed and inferred resume representation.

### job_profile

Canonical job-description representation.

For `RESUME_ONLY`:

`null`

For `RESUME_JD`:

A populated `JobProfile`.

### skill_analysis

Contains extracted skills, matches, gaps, and related analytical information.

### scoring

Contains official scoring output.

For `RESUME_ONLY`:

`null` for JD-dependent scoring.

### xai

Contains explainability results when XAI is enabled and available.

Otherwise:

`null`

### career_intelligence

Contains career-level inference.

For example:

- experience level

- domains

- strengths

- potential roles

- career signals

### recommendations

List of generated recommendations.

### metadata

Technical and analytical metadata associated with the analysis.

---

# 6\. AnalysisInput

`AnalysisInput` describes the source documents and analysis configuration.

Conceptual structure:

```
AnalysisInput
├── resume_document_id
├── job_document_id
├── options
└── client_metadata

```

## resume_document_id

Identifier of the resume document.

Required:

Yes

## job_document_id

Identifier of the job-description document.

Required:

Only for `RESUME_JD`.

For `RESUME_ONLY`:

`null`

## options

Contains analysis options.

## client_metadata

Optional metadata supplied by the client.

---

# 7\. AnalysisMetadata

`AnalysisMetadata` contains technical information that does not belong directly to the analytical domain.

Potential fields include:

- processing time

- parser information

- model information

- extractor versions

- taxonomy version

- pipeline version

- warnings

- diagnostic information

Metadata should not replace canonical analytical fields.

---

# 8\. ResumeProfile

`ResumeProfile` represents the structured interpretation of a resume.

Conceptual structure:

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

## profile_id

Unique resume profile identifier.

## document_id

Source resume document identifier.

## candidate_summary

Structured or extracted candidate summary.

## contact

Contact information extracted from the resume.

## education

List of education records.

## experience

List of professional experience records.

## projects

List of projects.

## certifications

List of certifications.

## skills

Normalized candidate skills.

## skill_categories

High-level grouping of candidate skills.

Examples:

- programming

- data

- cloud

- database

- machine learning

- software engineering

- soft skills

## total_experience

Estimated or extracted total professional experience.

The exact representation will be defined by the domain implementation.

## seniority

Inferred or extracted experience level.

Examples:

- student

- entry

- junior

- mid

- senior

- lead

## domains

Candidate's identified professional domains.

Examples:

- data science

- software engineering

- machine learning

- web development

## metadata

Additional structured information.

---

# 9\. Contact

`Contact` represents contact information extracted from a resume.

Potential fields:

- name

- email

- phone

- location

- LinkedIn

- GitHub

- portfolio

Sensitive information should be handled according to the application's privacy requirements.

Contact information should not be required for analytical processing.

---

# 10\. Education

`Education` represents an educational qualification.

Potential fields:

- institution

- degree

- field

- start_date

- end_date

- grade

- description

- evidence

The model should preserve extracted evidence where possible.

---

# 11\. Experience

`Experience` represents professional or relevant work experience.

Potential fields:

- company

- role

- location

- start_date

- end_date

- description

- responsibilities

- technologies

- achievements

- evidence

Experience records should preserve source evidence when possible.

---

# 12\. Project

`Project` represents a project described in the resume.

Potential fields:

- name

- description

- technologies

- responsibilities

- outcomes

- links

- evidence

Projects can provide important evidence for skill extraction even when formal work experience is limited.

---

# 13\. Certification

`Certification` represents a professional certification.

Potential fields:

- name

- issuing_organization

- issue_date

- expiry_date

- credential_id

- credential_url

- evidence

---

# 14\. JobProfile

`JobProfile` represents a structured interpretation of a job description.

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

## job_title

Job title extracted from the job description.

## company

Company or organization name when available.

## summary

Structured job summary.

## responsibilities

List of responsibilities extracted from the job description.

## required_skills

Skills explicitly required by the job.

## preferred_skills

Skills described as preferred, desirable, or optional.

## technical_skills

Technical requirements.

## soft_skills

Behavioral and interpersonal requirements.

## domain_skills

Domain-specific requirements.

## experience_requirements

Required experience information.

## education_requirements

Required educational qualifications.

## seniority

Expected job seniority.

## metadata

Additional job-processing information.

---

# 15\. Skill

`Skill` is the canonical representation of a skill throughout SkillLens.

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

## skill_id

Stable skill identifier.

## canonical_name

Normalized internal skill name.

Example:

`python`

## display_name

Human-readable name.

Example:

`Python`

## category

Broad skill category.

Example:

`Programming Language`

## subcategory

More specific classification where available.

## aliases

Known alternative names.

Example:

```
["Python Programming", "Python 3"]

```

## proficiency

Estimated proficiency when sufficient evidence exists.

This should not be fabricated when the resume does not provide adequate evidence.

## importance

Importance of the skill in its source context.

This is particularly relevant for job-description skills.

## evidence

Source evidence supporting the skill.

## confidence

Confidence that the skill was correctly identified and normalized.

## metadata

Additional taxonomy or extraction information.

---

# 16\. Evidence

`Evidence` connects an analytical result to its source text.

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

## source_type

Identifies where the evidence originated.

Possible values include:

- resume

- job_description

- generated_analysis

The final enum should be defined centrally rather than duplicated across modules.

## source_document_id

Document from which the evidence originated.

## section

Document section containing the evidence.

Examples:

- Skills

- Experience

- Projects

- Education

- Requirements

## text

Relevant source text.

## start_offset

Character or token offset where the evidence begins, when available.

## end_offset

Character or token offset where the evidence ends, when available.

## evidence_type

Type of supporting evidence.

Examples:

- explicit_skill

- contextual_skill

- experience

- project

- requirement

- achievement

## extractor

Component responsible for identifying the evidence.

## relevance

Relevance score for the evidence.

## confidence

Confidence in the evidence interpretation.

---

# 17\. Confidence

`Confidence` provides a standardized representation of analytical confidence.

Structure:

```
Confidence
├── score
├── level
├── components
└── rationale

```

## score

Numeric confidence.

Range:

`0--1`

## level

Allowed values:

- `low`

- `medium`

- `high`

## components

Breakdown of contributing confidence signals.

Examples:

- extraction_confidence

- semantic_confidence

- evidence_confidence

- taxonomy_confidence

## rationale

Human-readable explanation of the confidence assessment.

---

# 18\. SkillMatch

`SkillMatch` represents a relationship between a resume skill and a job skill.

Conceptual structure:

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

## relationship

Allowed relationship types:

- `exact`

- `strong_semantic`

- `partial`

- `related`

- `unmatched`

The relationship describes the semantic relationship rather than simply storing a binary match.

## similarity

Semantic similarity score.

Internal range:

`0--1`

## confidence

Confidence in the match decision.

## evidence

Evidence supporting the relationship.

## rationale

Explanation of why the relationship was assigned.

---

# 19\. SkillGap

`SkillGap` represents an identified gap between the candidate and job requirements.

Conceptual structure:

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

## gap_type

Examples:

- missing

- partial

- insufficient_proficiency

- contextual_gap

## severity

Represents the importance of the identified gap.

## importance

Importance of the skill to the target job.

## evidence

Evidence supporting the gap.

## related_matches

Matching information related to the gap.

## rationale

Explanation of why the gap was identified.

## confidence

Confidence in the gap classification.

---

# 20\. SkillAnalysis

`SkillAnalysis` combines the skill-level analytical results.

Conceptual structure:

```
SkillAnalysis
├── resume_skills[]
├── job_skills[]
├── skill_matches[]
├── skill_gaps[]
└── summary

```

For `RESUME_ONLY`:

- `resume_skills` is populated

- `job_skills` is empty

- `skill_matches` is empty

- JD-specific `skill_gaps` are not generated

For `RESUME_JD`:

all applicable skill-analysis fields may be populated.

---

# 21\. ScoringResult

`ScoringResult` contains the official candidate-job scoring output.

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

## overall_score

Public overall compatibility score.

Range:

`0--100`

## skill_score

Overall skill compatibility.

Range:

`0--100`

## required_skill_score

Compatibility with required skills.

Range:

`0--100`

## preferred_skill_score

Compatibility with preferred skills.

Range:

`0--100`

## experience_score

Experience compatibility.

Range:

`0--100`

## education_score

Education compatibility.

Range:

`0--100`

## domain_score

Domain compatibility.

Range:

`0--100`

## dimension_scores

Structured scoring information for individual dimensions.

## weights

Weights used by ScoreEngine.

## penalties

Applied score penalties.

## bonuses

Applied score bonuses.

## confidence

Confidence in the scoring result.

ScoreEngine is the sole owner of official score calculation.

---

# 22\. DimensionScore

`DimensionScore` represents one scoring dimension.

Potential fields:

- dimension

- score

- weight

- contribution

- rationale

- confidence

Example dimensions:

- skills

- experience

- education

- domain

---

# 23\. ScoreAdjustment

A score adjustment represents an explicit penalty or bonus.

Potential fields:

- type

- amount

- reason

- related_skill_ids

- evidence

- confidence

Adjustments must be transparent enough for XAIEngine to explain them.

---

# 24\. XAIResult

`XAIResult` represents explainability information derived from existing analytical results.

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

XAIEngine does not own the official score.

It explains the outputs produced by other canonical engines.

---

# 25\. SkillExplanation

`SkillExplanation` provides an explanation for an individual skill-related result.

Potential fields:

- skill_id

- explanation

- relationship

- contribution

- evidence

- confidence

---

# 26\. EvidenceMapEntry

`EvidenceMapEntry` connects an analytical conclusion to supporting evidence.

Potential fields:

- result_type

- result_id

- evidence_ids[]

- explanation

- confidence

This structure allows the frontend to show users why a conclusion was produced.

---

# 27\. CareerIntelligence

`CareerIntelligence` represents higher-level career analysis.

Conceptual structure:

```
CareerIntelligence
├── inferred_profile
├── experience_level
├── primary_domains[]
├── secondary_domains[]
├── strengths[]
├── career_signals[]
├── potential_roles[]
├── role_fit[]
├── transition_analysis
├── skill_priorities[]
├── risks[]
└── confidence

```

This component may operate in both analysis modes.

For `RESUME_ONLY`, it focuses on the candidate's profile.

For `RESUME_JD`, it can additionally consider the target job and identified gaps.

---

# 28\. RoleFit

`RoleFit` represents compatibility between a candidate profile and a potential career role.

Potential fields:

- role

- fit_score

- supporting_skills

- missing_skills

- rationale

- confidence

The exact scoring mechanism will be defined during the Career Intelligence implementation phase.

---

# 29\. SkillPriority

`SkillPriority` represents a skill that should receive attention for career development.

Potential fields:

- skill

- priority

- reason

- expected_impact

- related_gap_ids

- confidence

---

# 30\. Recommendation

`Recommendation` represents an actionable recommendation generated by RecommendationEngine.

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

## type

Recommendation category.

Examples may include:

- skill_development

- project

- certification

- resume_improvement

- career_direction

## target_skill

Skill associated with the recommendation when applicable.

## priority

Priority level.

## rationale

Why the recommendation is relevant.

## expected_impact

Expected benefit.

## effort

Estimated effort.

## evidence

Supporting evidence.

## related_gap_ids

Skill gaps addressed by the recommendation.

## confidence

Confidence in the recommendation.

RecommendationEngine is the sole recommendation owner.

---

# 31\. Resume-Only Schema Rules

When:

`analysis_mode = RESUME_ONLY`

the following rules apply:

```
job_profile = null
scoring = null
job_skills = []
skill_matches = []
JD-specific skill gaps = not generated

```

The system may still produce:

- resume skills

- candidate profile

- career intelligence

- strengths

- career signals

- potential roles

- recommendations

- XAI where applicable

The system must never invent a job description in order to produce a job match score.

---

# 32\. Resume + JD Schema Rules

When:

`analysis_mode = RESUME_JD`

the system may populate:

- resume profile

- job profile

- resume skills

- job skills

- skill matches

- skill gaps

- scoring

- XAI

- career intelligence

- recommendations

All JD-specific outputs must be traceable to the supplied job description and/or candidate evidence.

---

# 33\. Empty and Optional Values

The schema distinguishes between:

- unavailable

- not applicable

- empty collection

- null

Examples:

`job_profile = null`

means a job profile is not applicable because the analysis is resume-only.

An empty:

`recommendations = []`

means the analysis completed but no recommendations were generated.

Optional analytical sections should use `null` when the corresponding module was intentionally unavailable or disabled.

Collections should generally use empty lists rather than `null` when the concept exists but contains no items.

---

# 34\. Evidence Preservation

Evidence should be preserved as close to the source as practical.

The preferred relationship is:

```
Source Document
      ↓
Evidence
      ↓
Skill / Match / Gap / Explanation / Recommendation

```

This allows the system to answer:

- What text caused this skill to be extracted?

- Why was this skill considered a match?

- Why was this skill identified as missing?

- Why did this skill affect the score?

- Why was this recommendation generated?

Evidence is therefore a core part of the explainability architecture.

---

# 35\. Confidence Propagation

Confidence should be propagated through the analytical pipeline without changing its canonical scale.

Example:

```
Document Evidence
      ↓
Extraction Confidence
      ↓
Normalization Confidence
      ↓
Matching Confidence
      ↓
Gap Confidence
      ↓
Scoring Confidence
      ↓
Explanation Confidence

```

Each engine may use different internal signals, but the externally exposed confidence representation remains:

`0--1`

with:

- level

- components

- rationale

---

# 36\. Internal vs Public Numeric Scales

SkillLens uses different numeric scales for different purposes.

## Public compatibility scores

Range:

`0--100`

Used for:

- overall score

- dimension scores

- user-facing compatibility metrics

## Internal similarity values

Range:

`0--1`

Used for:

- semantic similarity

- confidence

- model-level similarity calculations

The system must not silently mix these scales.

---

# 37\. Schema Ownership

The domain layer is the canonical owner of domain data structures.

API schemas exist to represent transport contracts.

Frontend TypeScript types mirror the stable API/domain contract.

The architecture is:

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

---

# 38\. Current Phase 1 Implementation Status

The canonical domain model files have been established under:

`backend/app/domain/`

Current domain modules include:

- analysis.py

- resume.py

- job.py

- skill.py

- evidence.py

- confidence.py

- matching.py

- gaps.py

- scoring.py

- xai.py

- career.py

- recommendations.py

The corresponding frontend analysis types have also been established under:

`frontend/src/types/analysis.ts`

The API request, response, and error contracts are defined under:

`backend/app/schemas/`

Advanced analytical behavior is intentionally not implemented in Phase 1.

---

# 39\. Schema Validation Rules

Future implementations must validate:

- identifier presence

- enum values

- numeric ranges

- required fields

- nullable fields

- relationship types

- confidence range

- score range

- analysis-mode-specific constraints

Invalid domain states should not be silently accepted.

---

# 40\. Data Schema Invariants

The following rules are permanent architectural invariants:

1.  `AnalysisResult` is the canonical top-level result.

2.  `analysis_id` uniquely identifies an analysis.

3.  `schema_version` identifies the result schema version.

4.  `analysis_mode` determines whether a job profile is expected.

5.  Resume-only analysis does not generate JD-specific scoring.

6.  Public scores use 0--100.

7.  Internal similarity and confidence values use 0--1.

8.  Confidence has one canonical structure.

9.  Evidence is the preferred mechanism for supporting analytical conclusions.

10. Skill normalization produces canonical skill identities.

11. ScoreEngine owns official scoring.

12. XAIEngine explains existing analytical outputs.

13. RecommendationEngine owns recommendations.

14. Domain structures remain independent of frontend implementation details.

15. API schemas must remain compatible with frontend TypeScript contracts.

16. Breaking schema changes require schema versioning.

---

# 41\. Phase 1 Boundary

Phase 1 establishes the data contract.

It does not yet implement:

- PDF parsing

- DOCX parsing

- transformer-based extraction

- ESCO integration

- embeddings

- semantic matching algorithms

- skill-gap algorithms

- scoring algorithms

- SHAP/LIME explainability

- career inference algorithms

- recommendation algorithms

Those capabilities will be implemented in later phases while preserving the canonical schema defined in this document.

Document Processing Schema --- Phase 2
------------------------------------

Phase 2 introduces the normalized document-processing data structures used as the boundary between raw documents and future analytical extraction.

### DocumentType

Supported document types:

```
pdf
docx

```

### DocumentBlockType

Supported normalized block types:

```
paragraph
heading
bullet
table_cell

```

### SourceLocation

`SourceLocation` records the origin of a normalized document block.

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

Fields are optional because the available provenance depends on the document format and source structure.

### DocumentBlock

A `DocumentBlock` represents one normalized piece of document content.

Fields:

```
text
block_type
source
style_name
section
metadata

```

### ParsedDocument

`ParsedDocument` represents the complete normalized result of document processing.

Fields:

```
document_id
document_type
blocks
metadata

```

The object also provides reconstructed document text through its normalized blocks.

### Provenance Principle

Document processing must preserve source information wherever practical.

Downstream analytical components should be able to determine where extracted evidence originated without requiring the original parser to be executed again.

### Phase 2 Data Boundary

```
Raw document
    ↓
ParsedDocument
    ↓
Future Resume/JD extraction
    ↓
Future semantic analysis

```

`ParsedDocument` is an infrastructure-level representation. It is not itself a resume profile, job profile, skill graph, match result, score, explanation, or recommendation.