SkillLens --- Changelog
=====================

All notable changes to the SkillLens project are documented in this file.

The changelog follows a chronological development history and focuses on meaningful architectural, functional, testing, and documentation changes.

* * * * *

[Unreleased]
============

Phase 1 --- Foundation and Architecture
-------------------------------------

### Added

-   Established the SkillLens project repository structure.

-   Created the backend application structure using a modular monolith architecture.

-   Created the frontend application using React, TypeScript, and Vite.

-   Established the `API → Orchestration → Domain → Infrastructure` dependency direction.

-   Established the single Analysis Orchestrator as the central workflow coordinator.

-   Defined canonical domain models for:

    -   Analysis

    -   Resume

    -   Job

    -   Skill

    -   Evidence

    -   Confidence

    -   Matching

    -   Skill gaps

    -   Scoring

    -   XAI

    -   Career intelligence

    -   Recommendations

-   Defined stable API request and response contracts.

-   Defined the stable API error contract.

-   Defined frontend TypeScript representations of backend analysis contracts.

-   Added the initial analysis state model to the frontend.

-   Added backend health endpoint.

-   Added analysis API endpoint definitions.

-   Added application configuration using Pydantic Settings.

-   Added centralized logging configuration.

-   Added centralized application exception handling.

-   Added Python test structure.

-   Added frontend testing structure.

-   Added project documentation structure.

### Backend

Created the initial backend modules:

-   `backend/app/main.py`

-   `backend/app/api/`

-   `backend/app/core/`

-   `backend/app/domain/`

-   `backend/app/schemas/`

-   `backend/app/orchestration/`

-   `backend/app/analysis/`

-   `backend/app/infrastructure/`

-   `backend/app/utils/`

Implemented:

-   FastAPI application initialization.

-   API router registration.

-   `/api/v1/health`.

-   Analysis route contracts.

-   `ApplicationError`.

-   Stable `ErrorResponse`.

-   Analysis request schemas.

-   Analysis response schemas.

-   `AnalysisOrchestrator` abstract contract.

### Frontend

Created the initial frontend foundation:

-   React application entry point.

-   Application root component.

-   Vite configuration.

-   TypeScript configuration.

-   Canonical analysis types.

-   API types.

-   Analysis state model.

The frontend currently provides a minimal application shell and does not yet contain the production analysis interface.

### API

Established the API version prefix:

`/api/v1`

Established the following endpoints:

-   `GET /api/v1/health`

-   `POST /api/v1/analyses/resume`

-   `POST /api/v1/analyses/resume-jd`

-   `GET /api/v1/analyses/{analysis_id}`

-   `DELETE /api/v1/analyses/{analysis_id}`

Analysis endpoints currently return a controlled not-implemented response because analytical processing is outside the Phase 1 implementation boundary.

### Testing

Added backend tests for:

-   API endpoint contracts.

-   Domain contracts.

-   Error behavior.

-   Basic application behavior.

Current backend verification:

-   `9 passed`

Added frontend validation through:

-   ESLint

-   TypeScript compilation

-   Vite production build

Current frontend verification:

-   lint: PASS

-   build: PASS

### Architecture

Established the following canonical analytical responsibilities:

-   `DocumentProcessor`

-   `SkillExtractor`

-   `SkillNormalizer`

-   `SemanticMatcher`

-   `GapAnalyzer`

-   `ScoreEngine`

-   `XAIEngine`

-   `CareerIntelligenceEngine`

-   `RecommendationEngine`

These engines are currently architectural responsibilities and interfaces rather than completed analytical implementations.

### Documentation

Created and established:

-   `PROJECT_MASTER.md`

-   `PROJECT_STATUS.md`

-   `ARCHITECTURE.md`

-   `API_CONTRACT.md`

-   `DATA_SCHEMA.md`

-   `CODEBASE_MAP.md`

-   `CHANGELOG.md`

-   `SESSION_HANDOFF.md`

The documentation set is intended to provide persistent project context across development sessions and AI-assisted development phases.

* * * * *

Phase 1 Verification
====================

The following checks were completed successfully:

### Backend compilation

`python -m compileall -q backend`

Result:

PASS

### Backend tests

`python -m pytest backend/tests -q`

Result:

PASS

`9 passed`

### Frontend lint

`npm run lint`

Result:

PASS

### Frontend build

`npm run build`

Result:

PASS

### API verification

OpenAPI verification confirmed:

-   `/api/v1/health`

-   `/api/v1/analyses/resume`

-   `/api/v1/analyses/resume-jd`

-   `/api/v1/analyses/{analysis_id}` GET

-   `/api/v1/analyses/{analysis_id}` DELETE

Result:

PASS

### Dependency-direction verification

Result:

`NONE`

No dependency-direction violations were detected.

### Duplicate module-name verification

Result:

`NONE`

No duplicate Python module names remain in the backend structure.

* * * * *

Architectural Decisions Recorded in Phase 1
===========================================

Single Orchestrator
-------------------

The Analysis Orchestrator is the central coordinator of the analytical workflow.

Analytical engines must not directly call one another.

* * * * *

Single Source of Truth
----------------------

`AnalysisResult` is the canonical representation of an analysis.

The frontend should consume the stable API representation rather than reconstructing analytical results independently.

* * * * *

Scoring Ownership
-----------------

`ScoreEngine` is the sole owner of official compatibility scoring.

Other components may provide inputs to scoring but must not independently calculate competing official scores.

* * * * *

Explainability Ownership
------------------------

`XAIEngine` explains existing analytical results.

It must not independently recalculate or redefine the official score.

* * * * *

Recommendation Ownership
------------------------

`RecommendationEngine` is the sole owner of recommendation generation.

Other components may provide evidence, gaps, priorities, or signals used by the recommendation engine.

* * * * *

Resume-Only Analysis
--------------------

Resume-only analysis must not fabricate:

-   job-specific match scores

-   missing job skills

-   job-specific compatibility conclusions

Job-specific results require a job description.

* * * * *

Confidence Representation
-------------------------

Confidence is represented canonically using a `0--1` score with:

-   confidence level

-   components

-   rationale

* * * * *

Public Score Representation
---------------------------

Official user-facing scores use a:

`0--100`

range.

Internal calculations may use:

`0--1`

when mathematically appropriate.

* * * * *

Infrastructure Strategy
-----------------------

The project intentionally avoids unnecessary infrastructure during the early phases.

The following are not part of the current architecture:

-   Redis

-   Celery

-   Kafka

-   Kubernetes

-   microservices

-   service mesh

Additional infrastructure will only be introduced when there is a demonstrated architectural requirement.

* * * * *

Dependency and Ownership Rules
==============================

The following rules were established during Phase 1:

1.  API routes do not contain analytical algorithms.

2.  Engines do not directly call other engines.

3.  The orchestrator controls workflow execution.

4.  Domain models do not depend on the frontend.

5.  Domain models do not depend on HTTP transport.

6.  Frontend components do not implement backend analytical logic.

7.  There must be one canonical owner for each major responsibility.

8.  Evidence should be retained for important analytical conclusions.

9.  New dependencies require architectural justification.

10. New modules must not duplicate existing responsibilities.

* * * * *

Deferred to Future Phases
=========================

The following functionality has intentionally not been implemented during Phase 1:

-   PDF parsing

-   DOCX parsing

-   advanced NLP processing

-   transformer-based skill extraction

-   ESCO taxonomy integration

-   skill normalization implementation

-   transformer embeddings

-   semantic similarity

-   hybrid skill matching

-   skill-gap analysis

-   official scoring implementation

-   SHAP/LIME explainability

-   career intelligence

-   recommendation generation

-   persistence implementation

-   advanced frontend pages

-   production visualization components

-   LLM integration

-   model benchmarking

-   analytical evaluation datasets

These features will be implemented incrementally in later phases.

* * * * *

Change Management Rules
=======================

Future changelog entries should:

-   describe what changed

-   identify the affected subsystem

-   distinguish architectural changes from implementation changes

-   record important dependency changes

-   record schema or API contract changes

-   record significant bug fixes

-   avoid documenting insignificant generated-file changes

Every major phase should add a corresponding changelog section.

* * * * *

Versioning
==========

Current application version:

`0.1.0`

Current development status:

`Phase 1 --- Foundation and Architecture`

Next versioning changes will be made when a meaningful implementation milestone is completed.

* * * * *

Future Entry Format
===================

Future entries should generally follow this structure:

[Version or Phase]
------------------

### Added

New functionality.

### Changed

Changes to existing functionality or architecture.

### Fixed

Bug fixes.

### Removed

Removed functionality.

### Testing

Important validation results.

### Documentation

Important documentation changes.

### Architecture

Important architectural decisions or changes.

* * * * *

Phase 2 --- Document Processing
=============================

### Added

-   Implemented document-processing infrastructure.

-   Added PDF parser using PyMuPDF.

-   Added DOCX parser using python-docx.

-   Added common `DocumentParser` abstraction.

-   Added `DocumentProcessor` orchestration for document validation and parser selection.

-   Added normalized `ParsedDocument` representation.

-   Added `DocumentBlock` and `SourceLocation` provenance models.

-   Added PDF page/block provenance.

-   Added DOCX paragraph/table provenance.

-   Added PDF and DOCX structural validation.

-   Added file-size and empty-document validation.

-   Added MIME/content-type validation.

-   Added PDF and DOCX signature validation.

-   Added parser contract tests.

-   Added document reconstruction and provenance tests.

### Dependencies

-   Added `PyMuPDF>=1.24,<2.0`

-   Added `python-docx>=1.1,<2.0`

### Verification

-   Backend tests: 70 passed

-   Parsed document contract tests: 8 passed

-   Python compilation: passed

-   API route inspection: passed

-   OpenAPI verification: passed

-   Frontend TypeScript verification: passed

-   Frontend production build: passed

### Architectural Boundary

Phase 2 implements document processing only.

No semantic skill extraction, embeddings, matching, scoring, XAI, career intelligence, recommendations, or LLM analytical pipeline has been implemented.

### Repository Hygiene

-   Removed temporary `tmp/` directory.

-   Confirmed generated/cache directories are ignored by Git.

-   Prepared repository for initial project baseline commit.