SkillLens --- Architecture
========================

1\. Architecture Overview
-------------------------

SkillLens is designed as a modular monolith with clear separation between API, orchestration, domain logic, and infrastructure.

The primary dependency direction is:

API → Analysis Orchestrator → Domain Engines → Infrastructure

The architecture deliberately avoids unnecessary distributed-system complexity.

The system is designed to remain modular while being simple enough for an academic project and future production evolution.

2\. Architectural Layers
------------------------

### API Layer

Location:

backend/app/api/

Responsibilities:

-   HTTP endpoints
-   Request handling
-   Response serialization
-   HTTP status codes
-   API-level validation
-   API error handling

The API layer must not contain analytical business logic.

### Orchestration Layer

Location:

backend/app/orchestration/

The Analysis Orchestrator is the single workflow coordinator.

Responsibilities:

-   Accept analysis requests
-   Coordinate document processing
-   Coordinate skill extraction
-   Coordinate normalization
-   Coordinate matching
-   Coordinate gap analysis
-   Coordinate scoring
-   Coordinate explainability
-   Coordinate career intelligence
-   Coordinate recommendations
-   Produce the canonical AnalysisResult

Individual engines must not become workflow orchestrators.

### Domain Layer

Location:

backend/app/domain/

The domain layer contains the canonical business models and analytical contracts.

Current domain contracts include:

-   AnalysisResult
-   ResumeProfile
-   JobProfile
-   Skill
-   Evidence
-   Confidence
-   SkillMatch
-   SkillGap
-   SkillAnalysis
-   ScoringResult
-   XAIResult
-   CareerIntelligence
-   Recommendation

The domain layer must remain independent of API and infrastructure implementation details.

### Infrastructure Layer

Location:

backend/app/infrastructure/

Infrastructure contains implementation details required by the domain and analytical engines.

Planned responsibilities include:

-   Document parsers
-   Persistence
-   Machine-learning infrastructure
-   External taxonomy integrations
-   Model loading
-   Repository implementations

Infrastructure must not become the owner of business workflow.

3\. Canonical Analysis Engines
------------------------------

The following engines are defined as the canonical owners of their respective responsibilities.

### DocumentProcessor

Responsible for:

-   Reading supported documents
-   Extracting document text
-   Identifying document structure
-   Preserving source evidence
-   Producing normalized document content

Planned document support:

-   PDF
-   DOCX

### SkillExtractor

Responsible for:

-   Identifying skills from documents
-   Producing extracted skill candidates
-   Attaching evidence
-   Producing extraction confidence

### SkillNormalizer

Responsible for:

-   Canonical skill names
-   Alias resolution
-   Skill normalization
-   Taxonomy mapping
-   Skill categorization

Planned taxonomy:

ESCO

### SemanticMatcher

Responsible for:

-   Semantic similarity
-   Skill-to-skill comparison
-   Hybrid matching
-   Match relationship classification

Planned matching strategy:

-   Exact matching
-   Keyword matching
-   Transformer embeddings
-   Cosine similarity
-   Taxonomy-aware matching

### GapAnalyzer

Responsible for:

-   Identifying missing skills
-   Identifying partial matches
-   Identifying transferable skills
-   Classifying skill gaps
-   Assigning gap severity

### ScoreEngine

Responsible for all public analytical scoring.

No other engine may become a second scoring authority.

Public scores use a 0--100 scale.

Internal calculations may use normalized 0--1 values.

### XAIEngine

Responsible for explaining analytical results.

XAI must explain existing results rather than independently recalculating them.

Planned technologies:

-   SHAP
-   LIME where appropriate

Explanations should be connected to supporting evidence.

### CareerIntelligenceEngine

Responsible for:

-   Candidate profile inference
-   Experience-level inference
-   Domain inference
-   Potential career roles
-   Role-fit analysis
-   Career transition analysis
-   Skill priorities
-   Career risks

### RecommendationEngine

Responsible for all recommendations.

Potential recommendation categories include:

-   Learning
-   Projects
-   Certifications
-   Resume improvements
-   Career actions

Recommendations should reference the analytical evidence and relevant skill gaps.

4\. Analysis Workflow
---------------------

The intended high-level workflow is:

User uploads resume

↓

DocumentProcessor

↓

Resume Profile Construction

↓

SkillExtractor

↓

SkillNormalizer

↓

Optional Job Description Processing

↓

SemanticMatcher

↓

GapAnalyzer

↓

ScoreEngine

↓

XAIEngine

↓

CareerIntelligenceEngine

↓

RecommendationEngine

↓

AnalysisResult

The Analysis Orchestrator controls this workflow.

The engines do not directly orchestrate one another.

5\. Resume-Only Workflow
------------------------

For RESUME_ONLY:

Resume

↓

DocumentProcessor

↓

SkillExtractor

↓

SkillNormalizer

↓

CareerIntelligenceEngine

↓

RecommendationEngine

↓

XAIEngine where applicable

↓

AnalysisResult

No job-specific matching should be fabricated.

Therefore:

job_profile = None

Job-specific missing skills and match scores must not be generated without a job description.

6\. Resume + Job Description Workflow
-------------------------------------

For RESUME_JD:

Resume + Job Description

↓

DocumentProcessor

↓

Resume Profile + Job Profile

↓

SkillExtractor

↓

SkillNormalizer

↓

SemanticMatcher

↓

GapAnalyzer

↓

ScoreEngine

↓

XAIEngine

↓

CareerIntelligenceEngine

↓

RecommendationEngine

↓

AnalysisResult

7\. Canonical Data Flow
-----------------------

The frontend does not directly access individual backend engines.

The frontend communicates through the API.

The canonical data flow is:

React Frontend

↓

HTTP API

↓

FastAPI Routes

↓

Analysis Orchestrator

↓

Domain Engines

↓

Infrastructure

The final analytical response is represented by AnalysisResult.

AnalysisResult is the single source of truth for frontend analytical data.

8\. Dependency Rules
--------------------

The following dependency direction is enforced:

API → Orchestration → Domain → Infrastructure

The following reverse dependencies are prohibited:

-   Domain → API
-   Domain → Orchestration
-   Domain → Infrastructure
-   Orchestration → API
-   Infrastructure → API
-   Infrastructure → Orchestration

These rules prevent circular architectural dependencies.

Phase 1 static verification produced:

Dependency violations: NONE

9\. Responsibility Ownership
----------------------------

Each major responsibility has exactly one canonical owner.

| Responsibility | Owner |
| --- | --- |
| Document parsing | DocumentProcessor |
| Skill extraction | SkillExtractor |
| Skill normalization | SkillNormalizer |
| Semantic matching | SemanticMatcher |
| Skill-gap analysis | GapAnalyzer |
| Scoring | ScoreEngine |
| Explainability | XAIEngine |
| Career intelligence | CareerIntelligenceEngine |
| Recommendations | RecommendationEngine |
| Workflow coordination | Analysis Orchestrator |
| HTTP interface | API layer |
| Canonical data contracts | Domain layer |

Duplicate implementations of these responsibilities should not be introduced.

10\. Frontend Architecture
--------------------------

Frontend technology:

-   React
-   TypeScript
-   Vite

Frontend structure:

frontend/src/

The main architectural areas are:

-   app
-   pages
-   components
-   features
-   hooks
-   services
-   state
-   types
-   utils
-   styles

Feature areas include:

-   analysis
-   skills
-   matching
-   career
-   xai
-   recommendations

The frontend consumes stable API contracts.

It must not import backend Python modules or depend on backend internal implementation.

11\. Frontend State Architecture
--------------------------------

The analysis state contract currently supports:

-   idle
-   submitting
-   loading
-   success
-   error

The state stores:

-   Current AnalysisResult
-   Structured error information
-   Last request ID
-   Current operation status

The state contract is defined in:

frontend/src/state/analysisState.ts

12\. API Architecture
---------------------

API version:

/api/v1

Current endpoints:

GET /api/v1/health

POST /api/v1/analyses/resume

POST /api/v1/analyses/resume-jd

GET /api/v1/analyses/{analysis_id}

DELETE /api/v1/analyses/{analysis_id}

Analysis endpoints currently expose Phase 1 contracts only.

They intentionally return HTTP 501 until the corresponding analytical functionality is implemented in later phases.

13\. Error Architecture
-----------------------

Internal application errors use:

ApplicationError

Location:

backend/app/core/exceptions.py

External API errors use:

ErrorResponse

Location:

backend/app/schemas/errors.py

These are intentionally separate responsibilities.

ErrorResponse contains:

-   code
-   message
-   details
-   field
-   request_id

14\. Configuration Architecture
-------------------------------

Application configuration is centralized in:

backend/app/core/config.py

Configuration is represented through Pydantic Settings.

Current configuration includes:

-   application name
-   application version
-   environment
-   API version prefix
-   debug setting
-   maximum upload size

Environment variables may override configuration values.

15\. Logging Architecture
-------------------------

Application logging is centralized through:

backend/app/core/logging.py

The logging foundation provides:

-   configure_logging()
-   get_logger()

Individual modules should use module-level loggers rather than configuring logging independently.

16\. Testing Architecture
-------------------------

Testing is separated into:

backend/tests/unit/

backend/tests/integration/

backend/tests/api/

backend/tests/evaluation/

backend/tests/fixtures/

Current Phase 1 tests cover:

-   Domain contracts
-   API contracts
-   Health endpoint
-   Analysis endpoint error contracts

Current result:

9 tests passed

17\. Infrastructure Strategy
----------------------------

SkillLens intentionally uses a modular-monolith architecture.

The following infrastructure is not currently required:

-   Redis
-   Celery
-   Kafka
-   Kubernetes
-   Service mesh
-   Microservices
-   Distributed workflow engines

Additional infrastructure should only be introduced when a concrete requirement justifies it.

18\. Model Architecture
-----------------------

Transformer models are planned for later phases.

Initial semantic embedding candidate:

all-MiniLM-L6-v2

The embedding model is intended for semantic similarity and matching.

The LLM is not the semantic similarity engine.

A local open-source LLM using Ollama may be introduced for suitable language-generation tasks after benchmarking.

19\. Explainability Architecture
--------------------------------

Explainability is designed as a separate analytical layer.

The architecture separates:

-   analytical calculation
-   explanation generation
-   evidence mapping

XAI must consume existing analytical results.

It must not become an alternative scoring engine.

20\. Persistence Architecture
-----------------------------

Persistence is not implemented in Phase 1.

The architecture leaves room for:

-   Analysis repositories
-   Document repositories
-   Future database models
-   Persistent analysis history

Persistence implementation will be introduced only when required by the corresponding project phase.

21\. Current Phase Boundary
---------------------------

Phase 1 establishes architecture and contracts.

The following are intentionally outside Phase 1:

-   PDF parsing implementation
-   DOCX parsing implementation
-   Transformer inference
-   Skill extraction
-   ESCO integration
-   Semantic embeddings
-   Skill matching
-   Gap calculation
-   Score calculation
-   SHAP
-   LIME
-   Career intelligence implementation
-   Recommendation generation
-   Production persistence

These belong to later phases.

22\. Architectural Validation
-----------------------------

Phase 1 architecture has been checked for:

-   Python compilation
-   Application importability
-   OpenAPI route registration
-   Backend/frontend contract alignment
-   Dependency direction
-   Duplicate module names
-   Backend tests
-   Frontend linting
-   Frontend production build

Current architecture validation result:

PASS

23\. Architectural Invariants
-----------------------------

The following principles are considered frozen unless explicitly revised:

1.  Analysis Orchestrator remains the single workflow coordinator.
2.  Each analytical responsibility has one canonical owner.
3.  AnalysisResult remains the canonical frontend result contract.
4.  ScoreEngine remains the sole scoring authority.
5.  RecommendationEngine remains the sole recommendation authority.
6.  XAI explains existing results and does not recalculate them.
7.  Resume-only mode must not fabricate job-specific analysis.
8.  Public scores remain on a 0--100 scale.
9.  Confidence remains canonical on a 0--1 scale.
10. Frontend remains independent from backend implementation details.
11. API versioning remains under /api/v1.
12. Unnecessary distributed infrastructure is avoided.
13. Circular dependencies are prohibited.
14. Advanced analytical implementation remains phase-controlled.

Document Processing Architecture --- Phase 2
------------------------------------------

Phase 2 implements the document-processing infrastructure defined by the Phase 1 architecture.

### Location

```
backend/app/infrastructure/parsers/
├── __init__.py
├── base.py
├── models.py
├── validation.py
├── pdf_parser.py
├── docx_parser.py
└── document_processor.py

```

### Responsibilities

#### `DocumentProcessor`

`DocumentProcessor` is the entry point for document processing.

Responsibilities:

-   Validate the incoming document

-   Determine the document type

-   Select the appropriate parser

-   Generate or accept a document identifier

-   Return a normalized `ParsedDocument`

It does not:

-   Extract skills

-   Perform semantic matching

-   Calculate scores

-   Generate recommendations

-   Execute XAI logic

#### `DocumentParser`

`DocumentParser` defines the parser abstraction.

Each concrete parser implements:

```
parse(content, document_id) → ParsedDocument

```

This allows additional document formats to be introduced without changing downstream consumers.

#### `PDFParser`

The PDF parser uses PyMuPDF to extract text blocks from each page.

The parser preserves page and positional provenance where available.

#### `DOCXParser`

The DOCX parser uses python-docx.

It processes document body content while preserving paragraph/table ordering.

Supported structures include:

-   Paragraphs

-   Headings

-   Lists/bullets

-   Tables

-   Table cells

### Normalized Representation

All supported document types are converted into the common:

```
ParsedDocument
    └── DocumentBlock[]
          ├── text
          ├── block_type
          ├── source
          ├── style_name
          ├── section
          └── metadata

```

This creates a stable boundary between document ingestion and future analytical processing.

### Architectural Boundary

The Phase 2 architecture is:

```
                    ┌──────────────────┐
                    │ Document Bytes   │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │ DocumentProcessor│
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │   Validation     │
                    └────────┬─────────┘
                             │
                 ┌───────────┴───────────┐
                 ▼                       ▼
          ┌─────────────┐         ┌─────────────┐
          │  PDFParser  │         │ DOCXParser  │
          └──────┬──────┘         └──────┬──────┘
                 │                       │
                 └───────────┬───────────┘
                             ▼
                    ┌──────────────────┐
                    │  ParsedDocument  │
                    │ + provenance     │
                    └────────┬─────────┘
                             │
                             ▼
                 Future extraction layer

```

The parser layer terminates at `ParsedDocument`.

No Phase 2 parser directly invokes:

-   SkillExtractor

-   SemanticMatcher

-   ScoreEngine

-   XAIEngine

-   RecommendationEngine

-   LLM services

This preserves the dependency direction established during Phase 1.