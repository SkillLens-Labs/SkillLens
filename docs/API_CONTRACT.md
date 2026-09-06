SkillLens --- API Contract
========================

1\. Purpose
-----------

This document defines the stable API contract for the SkillLens backend.

The API provides a versioned interface between the React frontend and the FastAPI backend.

The API contract is intentionally defined before advanced analytical implementation so that backend engines can evolve internally without requiring frontend redesign.

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

-   multipart/form-data for document uploads

API version:

`/api/v1`

* * * * *

3\. API Base Path
-----------------

All application endpoints are exposed under:

`/api/v1`

Example:

`/api/v1/health`

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

* * * * *

5\. Health Endpoint
===================

Endpoint
--------

`GET /api/v1/health`

Purpose
-------

Returns basic information confirming that the SkillLens backend is running.

Successful Response
-------------------

HTTP status:

`200 OK`

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

`POST /api/v1/analyses/resume`

Purpose
-------

Accepts a resume and performs analysis without requiring a job description.

This mode is designed for:

-   resume profiling

-   skill extraction

-   skill normalization

-   career intelligence

-   strengths identification

-   career signals

-   potential role analysis

-   skill improvement recommendations

-   XAI explanations where applicable

Resume-only analysis must not fabricate job-specific results.

Therefore, the system must not generate:

-   job match scores

-   JD-specific missing skills

-   required-skill matching

-   preferred-skill matching

when no job description is supplied.

Request Content Type
--------------------

`multipart/form-data`

Request Fields
--------------

### resume

Type:

`UploadFile`

Required:

Yes

Accepted document types are defined by the document-processing implementation.

The initial planned formats are:

-   PDF

-   DOCX

### options

Optional analysis configuration.

The canonical options are:

-   `include_career_intelligence`

-   `include_recommendations`

-   `include_xai`

Default:

All three are enabled.

### client_metadata

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

`POST /api/v1/analyses/resume-jd`

Purpose
-------

Accepts both a resume and a job description for semantic skill-gap analysis.

This mode enables:

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

Request Content Type
--------------------

`multipart/form-data`

Request Fields
--------------

### resume

Type:

`UploadFile`

Required:

Yes

### job_description

Type:

`UploadFile`

Required:

Yes

### options

Optional analysis configuration.

### client_metadata

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

include_career_intelligence
---------------------------

Controls whether CareerIntelligenceEngine output is included.

Default:

`true`

include_recommendations
-----------------------

Controls whether RecommendationEngine output is included.

Default:

`true`

include_xai
-----------

Controls whether XAIEngine output is included.

Default:

`true`

These options control output generation. They must not change the fundamental meaning of the analysis.

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

source
------

Identifies the client or source initiating the request.

Example:

`web`

session_id
----------

Optional client session identifier.

extra
-----

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

### analysis_id

Unique identifier for the analysis.

### status

Current analysis processing status.

The canonical status vocabulary is:

-   `pending`

-   `processing`

-   `completed`

-   `failed`

### message

Human-readable description of the current state.

* * * * *

11\. Analysis Retrieval
=======================

Endpoint
--------

`GET /api/v1/analyses/{analysis_id}`

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

* * * * *

12\. Analysis Deletion
======================

Endpoint
--------

`DELETE /api/v1/analyses/{analysis_id}`

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

* * * * *

14\. Analysis Modes
===================

The API supports exactly two primary analysis modes.

RESUME_ONLY
-----------

Resume is supplied without a job description.

Expected analytical scope:

```
Resume
  ↓
Resume Profile
  ↓
Skills
  ↓
Career Intelligence
  ↓
Recommendations
  ↓
XAI

```

Job-specific scoring is unavailable in this mode.

RESUME_JD
---------

Resume and job description are supplied.

Expected analytical scope:

```
Resume ───────┐
              ├── Analysis
Job ──────────┘

```

This mode enables semantic comparison and skill-gap analysis.

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

### code

Machine-readable error identifier.

Examples:

-   `ANALYSIS_NOT_IMPLEMENTED`

-   `INVALID_FILE_TYPE`

-   `FILE_TOO_LARGE`

-   `ANALYSIS_NOT_FOUND`

-   `DOCUMENT_PROCESSING_FAILED`

### message

Human-readable explanation.

### details

Optional structured information about the error.

### field

Optional request field associated with the error.

Example:

`resume`

### request_id

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

During Phase 1, analysis endpoints intentionally return `501 Not Implemented` because the analytical engines have not yet been implemented.

This is a temporary Phase 1 state and is not the final production behavior.

* * * * *

18\. File Upload Constraints
============================

The backend configuration currently defines:

`max_upload_size_mb = 10`

The final document-processing layer must enforce upload limits consistently.

File validation should consider:

-   file extension

-   MIME type where appropriate

-   file size

-   file readability

-   parser compatibility

-   malformed documents

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

-   skill extraction

-   semantic similarity

-   scoring

-   gap analysis

-   XAI calculations

-   recommendation generation

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

* * * * *

21\. Response Ownership
=======================

Each analytical responsibility has a canonical owner.

| Result | Owner |
| --- | --- |
| Resume profile | Resume/domain model + processing pipeline |
| Job profile | Job/domain model + processing pipeline |
| Skill extraction | SkillExtractor |
| Skill normalization | SkillNormalizer |
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

`0--100`

Internal calculations may use:

`0--1`

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

* * * * *

29\. Current Phase 1 API State
==============================

Phase 1 establishes the API contract and routing structure.

Currently implemented:

-   FastAPI application

-   API version prefix

-   health endpoint

-   analysis routes

-   request schemas

-   response schemas

-   stable error schema

-   application exception handling

-   orchestrator interface

-   OpenAPI route registration

Currently not implemented:

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

Therefore, Phase 1 API endpoints intentionally do not perform real analysis.

* * * * *

30\. API Contract Invariants
============================

The following rules are architectural invariants:

1.  API version prefix remains `/api/v1`.

2.  `AnalysisResult` remains the canonical analysis response structure.

3.  Resume-only mode never fabricates JD-specific results.

4.  ScoreEngine owns official scoring.

5.  XAIEngine explains results but does not redefine them.

6.  RecommendationEngine owns recommendations.

7.  API routes do not contain analytical algorithms.

8.  API routes communicate with the orchestrator rather than individual engines.

9.  Application errors use the stable error contract.

10. Confidence uses the canonical 0--1 scale.

11. Public scores use the 0--100 scale.

12. Frontend integration depends on stable contracts rather than internal backend implementation details.

* * * * *

31\. Phase 1 Validation Status
==============================

The following API routes have been registered and verified through the generated OpenAPI schema:

```
GET    /api/v1/health
POST   /api/v1/analyses/resume
POST   /api/v1/analyses/resume-jd
GET    /api/v1/analyses/{analysis_id}
DELETE /api/v1/analyses/{analysis_id}

```

The API contract is therefore established as the baseline for subsequent implementation phases.

Phase 2 Document Processing Boundary
------------------------------------

Phase 2 implements the internal document-processing infrastructure without changing the public analysis API contract.

The existing analysis endpoints remain unchanged:

```
POST /api/v1/analyses/resume
POST /api/v1/analyses/resume-jd
GET  /api/v1/analyses/{analysis_id}

```

The endpoints remain intentionally non-implemented until the downstream analytical pipeline is introduced.

Phase 2 introduces:

```
DocumentProcessor
    ↓
ParsedDocument

```

This is an internal infrastructure boundary and is not exposed as a new public API response.

The document parser output must not be substituted for `AnalysisResult`, because `ParsedDocument` represents normalized document content while `AnalysisResult` represents the complete analytical result contract.

Therefore, no public API contract change is required for Phase 2.