SkillLens --- API Contract
========================

1\. Purpose
-----------

This document defines the stable API contract for the SkillLens backend.

The API provides a versioned interface between the React frontend and the FastAPI backend.

The API contract is intentionally defined before and independently of advanced analytical implementation so that backend engines can evolve internally without requiring frontend redesign.

Phase 1 established the public API contract.

Phase 2 established the internal document-processing boundary.

Phase 3 established the internal resume-intelligence pipeline without changing the public API contract.

* * * * *

2\. API Technology
------------------

Backend framework:

-   FastAPI

-   Python

-   Pydantic

Frontend communication:

-   HTTP/HTTPS

-   JSON

-   `multipart/form-data` for document uploads

API version:

```
/api/v1

```

* * * * *

3\. API Base Path
-----------------

All application endpoints are exposed under:

```
/api/v1

```

Example:

```
/api/v1/health

```

The version prefix allows future API versions to coexist without breaking existing clients.

* * * * *

4\. Endpoint Overview
---------------------

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/api/v1/health` | Check API health |
| POST | `/api/v1/analyses/resume` | Submit resume-only analysis |
| POST | `/api/v1/analyses/resume-jd` | Submit resume + job-description analysis |
| GET | `/api/v1/analyses/{analysis_id}` | Retrieve analysis result |
| DELETE | `/api/v1/analyses/{analysis_id}` | Delete an analysis |

Phase 3 does not introduce a new public endpoint.

The Phase 3 resume-intelligence pipeline is an internal analytical capability used by the analysis workflow.

* * * * *

5\. Health Endpoint
===================

Endpoint
--------

```
GET /api/v1/health

```

Purpose
-------

Returns basic information confirming that the SkillLens backend is running.

Successful Response
-------------------

HTTP status:

```
200 OK

```

Response:

```
{
  "status": "ok",
  "app": "SkillLens",
  "version": "0.1.0"
}

```

* * * * *

6\. Resume-Only Analysis
========================

Endpoint
--------

```
POST /api/v1/analyses/resume

```

Purpose
-------

Accepts a resume and performs analysis without requiring a job description.

The architectural analysis flow now includes the completed Phase 3 resume-intelligence capabilities:

-   document processing

-   resume structure interpretation

-   skill extraction

-   skill normalization

-   ESCO mapping

-   evidence linking

-   confidence estimation

-   canonical `ResumeProfile`

Later phases may extend resume-only analysis with:

-   career intelligence

-   strengths identification

-   career signals

-   potential role analysis

-   skill improvement recommendations

-   XAI explanations

Resume-only analysis must not fabricate job-specific results.

Therefore, the system must not generate:

-   job match scores

-   JD-specific missing skills

-   required-skill matching

-   preferred-skill matching

when no job description is supplied.

* * * * *

Request Content Type
--------------------

```
multipart/form-data

```

Request Fields
--------------

### `resume`

Type:

```
UploadFile

```

Required:

```
Yes

```

Accepted document types are defined by the document-processing implementation.

The currently supported Phase 2 document-processing formats are:

-   PDF

-   DOCX

The API must not claim support for document formats that the backend document-processing layer does not actually process.

### `options`

Optional analysis configuration.

Canonical options:

-   `include_career_intelligence`

-   `include_recommendations`

-   `include_xai`

Default:

All three are enabled.

### `client_metadata`

Optional client-supplied metadata.

Supported fields:

-   `source`

-   `session_id`

-   `extra`

* * * * *

7\. Resume + Job Description Analysis
=====================================

Endpoint
--------

```
POST /api/v1/analyses/resume-jd

```

Purpose
-------

Accepts both a resume and a job description for semantic skill-gap analysis.

The intended complete analysis pipeline includes:

-   resume processing

-   resume profiling

-   job profiling

-   skill extraction

-   skill normalization

-   exact matching

-   semantic matching

-   taxonomy-aware matching

-   skill-gap identification

-   scoring

-   XAI

-   career intelligence

-   recommendations

The resume side of this workflow now has the Phase 3 foundation.

Job-description analysis and resume-JD comparison remain future-phase responsibilities.

* * * * *

Request Content Type
--------------------

```
multipart/form-data

```

Request Fields
--------------

### `resume`

Type:

```
UploadFile

```

Required:

```
Yes

```

### `job_description`

Type:

```
UploadFile

```

Required:

```
Yes

```

### `options`

Optional analysis configuration.

### `client_metadata`

Optional client-supplied metadata.

* * * * *

8\. Analysis Options
====================

The canonical analysis options are:

```
{
  "include_career_intelligence": true,
  "include_recommendations": true,
  "include_xai": true
}

```

`include_career_intelligence`
-----------------------------

Controls whether `CareerIntelligenceEngine` output is included.

Default:

```
true

```

`include_recommendations`
-------------------------

Controls whether `RecommendationEngine` output is included.

Default:

```
true

```

`include_xai`
-------------

Controls whether `XAIEngine` output is included.

Default:

```
true

```

These options control output generation.

They must not change the fundamental meaning of the analysis.

Phase 3 does not implement career intelligence, recommendations, or XAI.

* * * * *

9\. Client Metadata
===================

The optional client metadata structure is:

```
{
  "source": null,
  "session_id": null,
  "extra": {}
}

```

`source`
--------

Identifies the client or source initiating the request.

Example:

```
web

```

`session_id`
------------

Optional client session identifier.

`extra`
-------

Flexible metadata object for additional non-critical client information.

The backend must not rely on arbitrary metadata fields for core analytical logic.

* * * * *

10\. Analysis Accepted Response
===============================

When an analysis request is accepted for processing, the API returns an accepted-analysis response.

Schema:

```
{
  "analysis_id": "string",
  "status": "string",
  "message": "string"
}

```

Fields:

### `analysis_id`

Unique identifier for the analysis.

### `status`

Current analysis processing status.

Canonical status vocabulary:

-   `pending`

-   `processing`

-   `completed`

-   `failed`

### `message`

Human-readable description of the current state.

* * * * *

11\. Analysis Retrieval
=======================

Endpoint
--------

```
GET /api/v1/analyses/{analysis_id}

```

Purpose
-------

Retrieves the canonical result associated with an analysis ID.

Successful Response
-------------------

The response contains:

```
{
  "data": {
    "analysis_id": "...",
    "schema_version": "...",
    "analysis_mode": "...",
    "status": "...",
    "created_at": "...",
    "input": {},
    "resume_profile": {},
    "job_profile": null,
    "skill_analysis": {},
    "scoring": null,
    "xai": null,
    "career_intelligence": null,
    "recommendations": [],
    "metadata": {}
  }
}

```

The `data` object is the canonical `AnalysisResult`.

The frontend must consume this canonical structure rather than reconstructing analytical results from multiple independent API responses.

Phase 3 contributes the canonical `resume_profile` through the internal resume-intelligence pipeline.

* * * * *

12\. Analysis Deletion
======================

Endpoint
--------

```
DELETE /api/v1/analyses/{analysis_id}

```

Purpose
-------

Deletes an existing analysis.

Response
--------

```
{
  "analysis_id": "string",
  "deleted": true,
  "message": "string"
}

```

The `deleted` field indicates whether the requested analysis was successfully removed.

* * * * *

13\. Canonical Analysis Result
==============================

`AnalysisResult` is the single source of truth for analysis data.

Canonical structure:

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

Phase 3 populates the `resume_profile` domain component internally.

* * * * *

14\. Analysis Modes
===================

The API supports exactly two primary analysis modes.

RESUME_ONLY
-----------

Resume is supplied without a job description.

The Phase 3 resume-intelligence flow is:

```
Resume
  ↓
DocumentProcessor
  ↓
ParsedDocument
  ↓
Resume Structure
  ↓
Skill Extraction
  ↓
Skill Normalization
  ↓
ESCO Mapping
  ↓
Evidence + Confidence
  ↓
ResumeProfile

```

Later phases may continue from `ResumeProfile` into:

```
ResumeProfile
  ↓
Career Intelligence
  ↓
Recommendations
  ↓
XAI

```

Job-specific scoring is unavailable in this mode.

* * * * *

RESUME_JD
---------

Resume and job description are supplied.

The intended architecture is:

```
Resume ───────┐
              ├── Analysis
Job ──────────┘

```

The resume branch now has the Phase 3 `ResumeProfile` foundation.

Job profiling and resume-JD comparison belong to later phases.

* * * * *

15\. Error Contract
===================

All application-level errors must follow a stable structure.

Canonical schema:

```
{
  "code": "ERROR_CODE",
  "message": "Human-readable message",
  "details": null,
  "field": null,
  "request_id": "unique-request-id"
}

```

Fields
------

### `code`

Machine-readable error identifier.

Examples:

-   `ANALYSIS_NOT_IMPLEMENTED`

-   `INVALID_FILE_TYPE`

-   `FILE_TOO_LARGE`

-   `ANALYSIS_NOT_FOUND`

-   `DOCUMENT_PROCESSING_FAILED`

### `message`

Human-readable explanation.

### `details`

Optional structured information about the error.

### `field`

Optional request field associated with the error.

Example:

```
resume

```

### `request_id`

Unique identifier for tracing the request through backend logs.

* * * * *

16\. Error Handling Principles
==============================

The API must:

1.  Return predictable error structures.

2.  Avoid exposing internal stack traces.

3.  Avoid exposing secrets or environment variables.

4.  Provide machine-readable error codes.

5.  Provide a request ID for debugging.

6.  Preserve stable response structure across frontend versions.

Internal exceptions must be translated into API-level errors by the backend exception-handling layer.

Phase 3 analytical failures must follow the same application-level error boundary rather than exposing internal engine exceptions directly through the API.

* * * * *

17\. HTTP Status Code Strategy
==============================

The API will use standard HTTP status semantics.

Planned status categories include:

| Status | Meaning |
| --- | --- |
| 200 | Successful request |
| 201 | Resource created when applicable |
| 202 | Analysis accepted for processing |
| 400 | Invalid request |
| 404 | Resource not found |
| 413 | Uploaded file exceeds size limit |
| 422 | Request validation failure |
| 500 | Unexpected server error |

During Phase 1, analysis endpoints intentionally returned `501 Not Implemented` because the analytical engines had not yet been implemented.

That statement is historical.

Phase 2 and Phase 3 have since implemented the document-processing and resume-intelligence layers, but the complete production API orchestration and downstream analytical workflow remain to be integrated in later phases.

* * * * *

18\. File Upload Constraints
============================

The backend configuration currently defines:

```
max_upload_size_mb = 10

```

The document-processing layer must enforce upload limits consistently.

File validation should consider:

-   file extension

-   MIME type where appropriate

-   file size

-   file readability

-   parser compatibility

-   malformed documents

The currently verified document-processing formats are:

-   PDF

-   DOCX

The frontend must not claim support for formats that the backend does not actually process.

* * * * *

19\. API and Domain Separation
==============================

The API layer must not contain analytical algorithms.

The intended dependency flow is:

```
Frontend
    ↓
API Routes
    ↓
Analysis Orchestrator
    ↓
Domain + Analysis Engines
    ↓
Infrastructure

```

API routes are responsible for:

-   receiving requests

-   validating inputs

-   invoking the orchestrator

-   translating results into response schemas

-   translating application errors into API errors

API routes must not directly implement:

-   document parsing

-   resume structure interpretation

-   skill extraction

-   skill normalization

-   ESCO mapping

-   semantic similarity

-   scoring

-   gap analysis

-   XAI calculations

-   recommendation generation

Phase 3 follows this separation by keeping resume-intelligence components under the analysis layer rather than placing analytical logic inside API routes.

* * * * *

20\. Orchestrator Boundary
==========================

The API communicates with the `AnalysisOrchestrator`.

The orchestrator provides the canonical application-level operations:

```
analyze_resume()

analyze_resume_jd()

get_analysis()

delete_analysis()

```

The API must not directly call individual analytical engines.

For example, the following architecture is prohibited:

```
API

 ├── SkillExtractor
 ├── ScoreEngine
 ├── XAIEngine
 └── RecommendationEngine

```

Instead:

```
API
 ↓
AnalysisOrchestrator
 ↓
Required Engines

```

The Phase 3 implementation establishes reusable analysis components that the orchestrator can coordinate.

* * * * *

21\. Response Ownership
=======================

Each analytical responsibility has a canonical owner.

| Result | Owner |
| --- | --- |
| Parsed document | DocumentProcessor |
| Resume structure | ResumeStructureInterpreter |
| Skill extraction | SkillExtractor |
| Skill normalization | SkillNormalizer |
| ESCO mapping | ESCOMapper |
| Resume profile | ResumeProfileBuilder |
| Job profile | Job/domain processing pipeline |
| Semantic matching | SemanticMatcher |
| Skill gaps | GapAnalyzer |
| Scores | ScoreEngine |
| Explanations | XAIEngine |
| Career intelligence | CareerIntelligenceEngine |
| Recommendations | RecommendationEngine |

No two independent engines should generate competing versions of the same canonical result.

* * * * *

22\. Scoring Contract
=====================

Where job-specific scoring is available, the public score range is:

```
0--100

```

Internal calculations may use:

```
0--1

```

The API should expose normalized public scores while preserving sufficient structured information for explainability.

Canonical scoring dimensions may include:

-   overall score

-   skill score

-   required skill score

-   preferred skill score

-   experience score

-   education score

-   domain score

The exact weighting algorithm belongs to `ScoreEngine` and must not be implemented in API routes.

Scoring is outside the Phase 3 implementation boundary.

* * * * *

23\. Confidence Contract
========================

Confidence is represented using a canonical structure.

```
{
  "score": 0.0,
  "level": "low",
  "components": {},
  "rationale": "..."
}

```

Rules:

-   `score` is between `0` and `1`

-   `level` is one of:

    -   `low`

    -   `medium`

    -   `high`

-   components provide supporting confidence signals

-   rationale explains the confidence assessment

Confidence must not be represented using incompatible scales across different API objects.

Phase 3 uses this canonical confidence representation for skill-related evidence and mapping confidence.

* * * * *

24\. Evidence Contract
======================

Evidence is used to connect analytical conclusions to source text.

Canonical evidence fields include:

```
evidence_id
source_type
source_document_id
section
text
start_offset
end_offset
evidence_type
extractor
relevance
confidence

```

Phase 3 establishes evidence linking for extracted skills.

Evidence is particularly important for:

-   extracted skills

-   skill matches

-   skill gaps

-   XAI explanations

-   recommendations

The system should prefer evidence-backed conclusions over unsupported generated statements.

* * * * *

25\. XAI Contract
=================

XAI is explanatory rather than computational.

The XAI layer receives existing analytical outputs and generates explanations for them.

XAI must not independently recalculate the official score.

Canonical XAI output includes:

-   overall explanation

-   score explanation

-   strengths

-   weaknesses

-   matched skill explanations

-   missing skill explanations

-   partial match explanations

-   evidence map

-   confidence

The official score remains owned by `ScoreEngine`.

XAI is outside the Phase 3 implementation boundary.

* * * * *

26\. Recommendation Contract
============================

Recommendations are owned exclusively by `RecommendationEngine`.

A recommendation contains:

```
recommendation_id
type
title
target_skill
priority
rationale
expected_impact
effort
evidence
related_gap_ids
confidence

```

Recommendations should be connected to identified gaps or career signals whenever applicable.

The frontend must consume recommendation objects from the canonical analysis result rather than independently generating recommendations.

Recommendations are outside the Phase 3 implementation boundary.

* * * * *

27\. Frontend Integration Contract
==================================

The frontend communicates with the backend through API service modules.

Frontend components must not directly construct backend URLs throughout the UI.

The intended structure is:

```
React Components
      ↓
Feature Hooks / State
      ↓
API Service Layer
      ↓
FastAPI

```

The frontend uses TypeScript interfaces corresponding to backend API contracts.

Phase 3 does not require a public API contract change.

* * * * *

28\. API Versioning Rules
=========================

Breaking changes to the API contract require a new API version.

For example:

```
/api/v1
/api/v2

```

Non-breaking additions may be introduced within the existing version when they do not invalidate existing clients.

The frontend should be developed against explicit versioned contracts rather than undocumented backend behavior.

Phase 3 does not require `/api/v2`.

* * * * *

29\. Historical Phase 1 API State
=================================

Phase 1 established the API contract and routing structure.

At the end of Phase 1, the following were intentionally not implemented:

-   actual document processing

-   resume parsing

-   job-description parsing

-   skill extraction

-   skill normalization

-   semantic matching

-   gap analysis

-   scoring

-   XAI

-   career intelligence

-   recommendations

-   persistent analysis storage

Therefore, Phase 1 analysis endpoints intentionally did not perform real analysis.

This section is retained as historical project information.

* * * * *

30\. Phase 2 Document Processing Boundary
=========================================

Phase 2 implements the internal document-processing infrastructure without changing the public analysis API contract.

The existing analysis endpoints remain:

```
POST /api/v1/analyses/resume

POST /api/v1/analyses/resume-jd

GET /api/v1/analyses/{analysis_id}

```

Phase 2 introduced:

```
DocumentProcessor
    ↓
ParsedDocument

```

This is an internal infrastructure boundary and is not exposed as a new public API response.

The document parser output must not be substituted for `AnalysisResult`, because `ParsedDocument` represents normalized document content while `AnalysisResult` represents the complete analytical result contract.

Therefore, no public API contract change was required for Phase 2.

* * * * *

31\. Phase 3 Resume Intelligence Boundary
=========================================

Phase 3 extends the internal analytical implementation while preserving the public API contract.

The Phase 3 pipeline is:

```
ParsedDocument
      ↓
Resume Structure Interpretation
      ↓
Skill Extraction
      ↓
Skill Normalization
      ↓
ESCO Mapping
      ↓
Evidence Linking
      ↓
Confidence Estimation
      ↓
ResumeProfile

```

Phase 3 Components
------------------

The implemented components are:

```
backend/app/analysis/resume_structure.py

backend/app/analysis/skill_extractor.py

backend/app/analysis/skill_normalizer.py

backend/app/analysis/esco_mapper.py

backend/app/analysis/resume_profile_builder.py

```

### Resume Structure

`ResumeStructureInterpreter` interprets supported resume sections including:

-   Summary

-   Experience

-   Education

-   Projects

-   Certifications

-   Skills

Unknown headings remain explicitly classified as `UNKNOWN`.

### Skill Extraction

`SkillExtractor` extracts skill mentions from:

-   Skills

-   Certifications

-   Summary

-   Experience

-   Projects

-   Education

Skill evidence retains source provenance, offsets, evidence type, and extraction confidence.

### Skill Normalization

`SkillNormalizer` performs:

-   Unicode normalization

-   case normalization

-   whitespace normalization

-   alias resolution

-   canonical skill naming

### ESCO Mapping

`ESCOMapper` provides the ESCO taxonomy integration boundary.

Current ESCO version:

```
1.2.1

```

The current implementation uses a deterministic representative adapter vocabulary.

It is not the complete ESCO dataset.

No fabricated ESCO identifiers are used.

### Resume Profile Construction

`ResumeProfileBuilder` constructs the canonical domain:

```
ResumeProfile

```

It provides:

-   deterministic profile identifiers

-   deterministic skill identifiers

-   deterministic evidence identifiers

-   skill deduplication

-   evidence merging

-   confidence aggregation

-   skill categories

-   summary extraction

-   ESCO metadata

-   builder metadata

The builder does not invent unsupported resume facts.

* * * * *

32\. Phase 3 API Contract Impact
================================

Phase 3 does **not** introduce:

-   new public endpoints

-   a new API version

-   a competing resume response model

-   a competing skill model

-   a new analysis result structure

The existing API contract remains the public integration boundary.

Phase 3 enriches the internal implementation behind that contract.

The canonical relationship is:

```
API Request
    ↓
AnalysisOrchestrator
    ↓
DocumentProcessor
    ↓
ParsedDocument
    ↓
Resume Intelligence Pipeline
    ↓
ResumeProfile
    ↓
AnalysisResult
    ↓
API Response

```

The complete API-to-orchestrator integration is a later implementation step.

* * * * *

33\. Phase 3 Verification
=========================

Phase 3 was verified through:

-   unit tests

-   integration tests

-   real DOCX processing

-   real PDF processing

-   full backend regression

Full regression result:

```
115 passed
7 warnings
0 failures

```

Command:

```
PYTHONPATH=. pytest backend/tests -q

```

The warnings are dependency/deprecation warnings and did not cause test failures.

* * * * *

34\. Real Document Verification
===============================

Real fixtures were added:

```
backend/tests/fixtures/phase3_sample_resume.pdf

backend/tests/fixtures/phase3_sample_resume.docx

```

The DOCX fixture successfully demonstrated:

```
ParsedDocument
→ Resume Structure
→ Skill Extraction
→ Skill Normalization
→ ESCO Mapping
→ ResumeProfile

```

The PDF fixture successfully demonstrated:

-   real PDF parsing

-   text extraction

-   source provenance

The current frozen PDF parser does not reliably infer synthetic semantic headings from ordinary PDF text blocks.

Therefore:

```
DOCX → complete semantic Phase 3 verification

PDF → parsing and provenance verification

```

Phase 2 was not modified to bypass this limitation.

* * * * *

35\. API Contract Invariants
============================

The following rules are architectural invariants:

1.  API version prefix remains `/api/v1`.

2.  `AnalysisResult` remains the canonical analysis response structure.

3.  `ResumeProfile` remains the canonical resume representation.

4.  `ParsedDocument` remains the canonical output of document processing.

5.  Resume-only mode never fabricates JD-specific results.

6.  `DocumentProcessor` owns document parsing.

7.  `SkillExtractor` owns skill extraction.

8.  `SkillNormalizer` owns skill normalization.

9.  `ESCOMapper` owns ESCO mapping.

10. `ResumeProfileBuilder` owns construction of the canonical resume profile.

11. `ScoreEngine` owns official scoring.

12. `XAIEngine` explains results but does not redefine them.

13. `RecommendationEngine` owns recommendations.

14. API routes do not contain analytical algorithms.

15. API routes communicate with the orchestrator rather than individual engines.

16. Application errors use the stable error contract.

17. Confidence uses the canonical 0--1 scale.

18. Public scores use the 0--100 scale.

19. Evidence retains source provenance.

20. Frontend integration depends on stable contracts rather than internal backend implementation details.

21. Later phases must not reparse PDF/DOCX files outside the Phase 2 document-processing boundary.

22. No duplicate analytical ownership may be introduced.

* * * * *

36\. Current API and Analytical State
=====================================

```
API Contract
    COMPLETE / STABLE

Phase 2 Document Processing
    COMPLETE / FROZEN

Phase 3 Resume Intelligence
    COMPLETE / VERIFIED

Full API → Orchestrator → Analysis Integration
    NOT YET COMPLETE

Resume-JD Matching
    NOT IMPLEMENTED

Semantic Matching
    NOT IMPLEMENTED

Skill-Gap Scoring
    NOT IMPLEMENTED

Final Match Scoring
    NOT IMPLEMENTED

XAI Engine
    NOT IMPLEMENTED

Career Intelligence
    NOT IMPLEMENTED

Recommendation Engine
    NOT IMPLEMENTED

```

The API contract remains stable while these analytical capabilities are implemented incrementally.

* * * * *

37\. Next Planned API Evolution
===============================

The next analytical phases should integrate the completed resume-intelligence pipeline into the canonical `AnalysisOrchestrator` and progressively populate `AnalysisResult`.

Future API work must preserve:

```
/api/v1

```

unless a genuine breaking contract change requires a new API version.

Future implementations must not bypass the established:

```
API
 ↓
AnalysisOrchestrator
 ↓
Domain Engines
 ↓
Infrastructure

```

architecture.
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

## Phase 5 — JD Intelligence & Resume–JD Matching — COMPLETED

Phase 5 API integration is complete and frozen.

Implemented endpoint:

POST /api/v1/analyses/resume-jd

The endpoint accepts a resume and job-description document and returns the canonical AnalysisResult containing ResumeProfile, JobProfile, and structured Resume–JD MatchingResult data.

Phase 5 matching includes:
- JD requirements
- Required/preferred classification
- JD skills
- Skill normalization
- ESCO mapping
- Exact and semantic matching
- Requirement alignment
- Evidence and confidence

Final candidate-job scoring and XAI are intentionally excluded from Phase 5 and are owned by Phase 6.

OpenAPI verification passed.

Phase 6 --- Final Candidate-Job Scoring, Skill Gap Analysis & XAI
---------------------------------------------------------------

**Status: COMPLETE / FROZEN**

Phase 6 extends the Resume + JD analysis response with populated:

```
skill_analysis
scoring
xai

```

### Resume + JD Response

For a valid Resume + JD analysis:

```
matching        -> populated
skill_analysis  -> populated
scoring         -> populated
xai             -> populated

```

The scoring response includes:

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
confidence

```

The public score range is:

```
0.0 - 100.0

```

Internal calculations use:

```
0.0 - 1.0

```

### Scoring Policy

Canonical dimension weights:

```
Required Skills  = 0.50
Preferred Skills = 0.15
Experience       = 0.15
Education        = 0.10
Domain           = 0.10
Total            = 1.00

```

Requirement alignment values:

```
MATCHED     = 1.0
PARTIAL     = 0.5
UNMATCHED   = 0.0
UNKNOWN     = excluded

```

UNKNOWN does not represent confirmed absence and is excluded from the scoring denominator.

Unavailable dimensions are excluded and the remaining dimension weights are renormalized.

### Score Contributions

Each contribution provides:

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

This provides transparent decomposition of the deterministic score.

### XAI

XAI explains existing analytical results.

It does not independently recalculate official scoring or perform new matching.

The XAI response supports:

-   overall explanation

-   score explanation

-   strengths

-   weaknesses

-   matched skill explanations

-   partial match explanations

-   missing skill explanations

-   evidence mapping

-   confidence

### Resume-Only Compatibility

Resume-only analysis remains compatible:

```
skill_analysis -> existing empty-compatible structure
scoring        -> null
xai            -> null

```

### Verification

Phase 6 API verification passed:

```
14 passed, 7 warnings

```

Full backend regression:

```
281 passed, 7 warnings

```

The complete Phase 6 API contract, response behavior, scoring rules, and XAI contract are documented in:

`docs/PHASE_6.md

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

This document should not duplicate the complete Phase 7 implementation history. Future development should refer to `docs/PHASE_7.md` for detailed Phase 7 information.`

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