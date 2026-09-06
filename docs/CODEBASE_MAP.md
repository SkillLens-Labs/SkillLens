SkillLens --- Codebase Map
========================

1\. Purpose
-----------

This document provides a structured map of the SkillLens codebase.

It explains:

-   where major application responsibilities are located

-   how backend modules are organized

-   how frontend modules are organized

-   where tests are located

-   where configuration is stored

-   which components are currently implemented

-   which components are reserved for later phases

The purpose of this document is to make the repository understandable to both human developers and AI coding assistants.

* * * * *

2\. Repository Root
===================

The project root is:

`SkillLens/`

The repository is divided into two primary application layers:

```
SkillLens/
├── backend/
├── frontend/
├── documentation files
├── .gitignore
└── skilllens/

```

The `skilllens/` directory is the local Python virtual environment and is excluded from Git.

* * * * *

3\. Backend Overview
====================

Backend location:

`backend/`

Technology:

-   Python

-   FastAPI

-   Pydantic

-   Uvicorn

The backend follows a layered modular-monolith architecture.

```
backend/
├── app/
├── tests/
└── requirements.txt

```

* * * * *

4\. Backend Application Structure
=================================

The backend application is organized into:

```
backend/app/
├── api/
├── core/
├── domain/
├── schemas/
├── orchestration/
├── analysis/
├── infrastructure/
├── utils/
└── main.py

```

Each directory has a specific responsibility.

* * * * *

5\. backend/app/main.py
=======================

File:

`backend/app/main.py`

Responsibility:

-   create the FastAPI application

-   configure application logging

-   register API routers

-   register application-level exception handling

-   configure application metadata

Current routes registered:

-   health router

-   analysis router

The file should remain focused on application composition.

It should not contain analytical algorithms.

* * * * *

6\. backend/app/api/
====================

Purpose:

Contains the HTTP/API layer.

Structure:

```
backend/app/api/
├── __init__.py
├── dependencies.py
└── routes/
    ├── __init__.py
    ├── health.py
    └── analyses.py

```

The API layer translates HTTP requests into application operations.

It must not contain domain algorithms.

* * * * *

7\. backend/app/api/routes/health.py
====================================

Purpose:

Provides the application health endpoint.

Endpoint:

`GET /api/v1/health`

Current behavior:

Returns:

-   application status

-   application name

-   application version

This endpoint is intentionally simple and independent of the analytical pipeline.

* * * * *

8\. backend/app/api/routes/analyses.py
======================================

Purpose:

Defines the analysis-related HTTP endpoints.

Current endpoints:

```
POST   /api/v1/analyses/resume
POST   /api/v1/analyses/resume-jd
GET    /api/v1/analyses/{analysis_id}
DELETE /api/v1/analyses/{analysis_id}

```

Current Phase 1 behavior:

The routes exist and validate their basic request structure, but real analysis processing is not yet implemented.

The routes currently return the controlled `ANALYSIS_NOT_IMPLEMENTED` application error.

Future implementation will connect these routes to the `AnalysisOrchestrator`.

* * * * *

9\. backend/app/api/dependencies.py
===================================

Purpose:

Reserved for FastAPI dependency definitions.

Potential future responsibilities include:

-   dependency injection

-   orchestrator construction

-   repository injection

-   authentication dependencies

-   request-level services

No analytical logic should be placed here.

* * * * *

10\. backend/app/core/
======================

Purpose:

Contains application-wide infrastructure and cross-cutting concerns.

Structure:

```
backend/app/core/
├── __init__.py
├── config.py
├── exceptions.py
└── logging.py

```

* * * * *

11\. backend/app/core/config.py
===============================

Purpose:

Central application configuration.

Current configuration includes:

-   application name

-   application version

-   environment

-   API version prefix

-   debug flag

-   maximum upload size

Configuration is managed through Pydantic Settings.

Environment variables may override configuration values.

The configuration module should remain the canonical source for application settings.

* * * * *

12\. backend/app/core/exceptions.py
===================================

Purpose:

Defines internal application-level exceptions.

Primary class:

`ApplicationError`

The exception contains:

-   code

-   message

-   details

-   field

These errors are converted into the stable API error contract by the application exception handler.

* * * * *

13\. backend/app/core/logging.py
================================

Purpose:

Provides centralized logging configuration.

Current responsibilities:

-   configure application-wide logging

-   provide module-specific loggers

Future analytical modules should use this logging layer instead of creating independent logging configurations.

* * * * *

14\. backend/app/domain/
========================

Purpose:

Contains canonical domain models.

Structure:

```
backend/app/domain/
├── analysis.py
├── career.py
├── confidence.py
├── evidence.py
├── gaps.py
├── job.py
├── matching.py
├── recommendations.py
├── resume.py
├── scoring.py
├── skill.py
└── xai.py

```

The domain layer represents the core concepts of SkillLens.

It should remain independent of:

-   FastAPI

-   React

-   HTTP transport

-   database-specific implementation

-   specific UI components

* * * * *

15\. backend/app/domain/analysis.py
===================================

Purpose:

Defines the canonical `AnalysisResult` structure.

This is the primary top-level domain contract.

It connects:

-   input

-   resume profile

-   job profile

-   skill analysis

-   scoring

-   XAI

-   career intelligence

-   recommendations

-   metadata

`AnalysisResult` is the single source of truth for completed analysis.

* * * * *

16\. backend/app/domain/resume.py
=================================

Purpose:

Defines resume-related domain structures.

Includes concepts such as:

-   ResumeProfile

-   education

-   experience

-   projects

-   certifications

-   contact information

It represents the structured candidate profile produced from a resume.

* * * * *

17\. backend/app/domain/job.py
==============================

Purpose:

Defines job-description domain structures.

Includes:

-   JobProfile

-   required skills

-   preferred skills

-   technical skills

-   soft skills

-   domain skills

-   experience requirements

-   education requirements

-   seniority

* * * * *

18\. backend/app/domain/skill.py
================================

Purpose:

Defines the canonical `Skill` representation.

Skill normalization is important because different textual representations may refer to the same underlying skill.

Example:

```
Python
Python Programming
Python 3

```

may ultimately map to a canonical skill representation.

* * * * *

19\. backend/app/domain/evidence.py
===================================

Purpose:

Defines evidence structures connecting analytical results to source documents.

Evidence may originate from:

-   resume

-   job description

-   generated analysis

Evidence supports:

-   skill extraction

-   matching

-   gap analysis

-   XAI

-   recommendations

* * * * *

20\. backend/app/domain/confidence.py
=====================================

Purpose:

Defines the canonical confidence structure.

Confidence uses:

`0--1`

and includes:

-   score

-   level

-   components

-   rationale

This prevents different modules from using incompatible confidence representations.

* * * * *

21\. backend/app/domain/matching.py
===================================

Purpose:

Defines skill matching structures.

Includes concepts such as:

-   SkillMatch

-   match relationship

-   similarity

-   confidence

-   evidence

-   rationale

The actual matching algorithm belongs to `SemanticMatcher`, not the domain model.

* * * * *

22\. backend/app/domain/gaps.py
===============================

Purpose:

Defines skill-gap structures.

Represents concepts such as:

-   missing skills

-   partial matches

-   insufficient proficiency

-   severity

-   importance

-   supporting evidence

The actual gap-detection algorithm belongs to `GapAnalyzer`.

* * * * *

23\. backend/app/domain/scoring.py
==================================

Purpose:

Defines scoring structures.

Includes:

-   ScoringResult

-   DimensionScore

-   ScoreAdjustment

The domain module defines the data contract.

`ScoreEngine` owns the actual scoring algorithm.

* * * * *

24\. backend/app/domain/xai.py
==============================

Purpose:

Defines explainability structures.

Includes:

-   XAIResult

-   SkillExplanation

-   EvidenceMapEntry

`XAIEngine` owns explanation generation.

The domain module itself does not perform explainability calculations.

* * * * *

25\. backend/app/domain/career.py
=================================

Purpose:

Defines career intelligence structures.

Includes concepts such as:

-   CareerIntelligence

-   RoleFit

-   SkillPriority

The actual career inference logic belongs to `CareerIntelligenceEngine`.

* * * * *

26\. backend/app/domain/recommendations.py
==========================================

Purpose:

Defines recommendation structures.

Includes:

-   Recommendation

-   recommendation type

-   priority

-   rationale

-   expected impact

-   effort

-   evidence

-   related gaps

-   confidence

`RecommendationEngine` is the sole owner of recommendation generation.

* * * * *

27\. backend/app/schemas/
=========================

Purpose:

Contains API transport schemas.

Structure:

```
backend/app/schemas/
├── __init__.py
├── requests.py
├── responses.py
└── errors.py

```

These schemas define what the API accepts and returns.

They should not contain analytical algorithms.

* * * * *

28\. backend/app/schemas/requests.py
====================================

Purpose:

Defines request contracts.

Current structures include:

-   AnalysisOptions

-   ClientMetadata

-   ResumeAnalysisRequest

-   ResumeJDAnalysisRequest

These schemas validate request-level configuration.

* * * * *

29\. backend/app/schemas/responses.py
=====================================

Purpose:

Defines API response structures.

Current structures include:

-   AnalysisResponse

-   AnalysisAcceptedResponse

-   DeleteAnalysisResponse

The response layer exposes the canonical domain result through the API.

* * * * *

30\. backend/app/schemas/errors.py
==================================

Purpose:

Defines the stable API error response.

Structure:

```
ErrorResponse
├── code
├── message
├── details
├── field
└── request_id

```

This is separate from `core/exceptions.py`.

`core/exceptions.py` defines internal exceptions.

`schemas/errors.py` defines the external API error representation.

* * * * *

31\. backend/app/orchestration/
===============================

Purpose:

Contains the application-level analysis orchestrator.

Structure:

```
backend/app/orchestration/
├── __init__.py
└── analysis_orchestrator.py

```

* * * * *

32\. backend/app/orchestration/analysis_orchestrator.py
=======================================================

Purpose:

Defines the contract for the central analysis orchestrator.

The orchestrator exposes:

```
analyze_resume()
analyze_resume_jd()
get_analysis()
delete_analysis()

```

The orchestrator is the central coordination point for the analytical workflow.

Individual engines must not call one another directly.

The orchestrator controls execution order.

* * * * *

33\. backend/app/analysis/
==========================

Purpose:

Contains the analytical engines.

Planned structure:

```
backend/app/analysis/
├── document_processor.py
├── skill_extractor.py
├── skill_normalizer.py
├── semantic_matcher.py
├── gap_analyzer.py
├── score_engine.py
├── xai_engine.py
├── career_engine.py
└── recommendation_engine.py

```

At the current Phase 1 state, these analytical engine implementations have not yet been built.

Only the package structure is established.

* * * * *

34\. DocumentProcessor
======================

Planned file:

`backend/app/analysis/document_processor.py`

Responsibility:

-   validate documents

-   parse supported file formats

-   extract text

-   identify document structure

-   preserve source information

Initial planned document formats:

-   PDF

-   DOCX

DocumentProcessor should not perform skill matching or scoring.

* * * * *

35\. SkillExtractor
===================

Planned file:

`backend/app/analysis/skill_extractor.py`

Responsibility:

-   identify candidate skills from source text

-   identify job-required skills

-   associate extracted skills with evidence

-   produce extraction confidence

Potential technologies:

-   NLP

-   transformer models

-   rule-based extraction

-   taxonomy-assisted extraction

* * * * *

36\. SkillNormalizer
====================

Planned file:

`backend/app/analysis/skill_normalizer.py`

Responsibility:

-   map extracted skill phrases to canonical skill identities

-   resolve aliases

-   reduce duplicate representations

-   integrate taxonomy information

Planned taxonomy:

ESCO or another validated skills taxonomy.

* * * * *

37\. SemanticMatcher
====================

Planned file:

`backend/app/analysis/semantic_matcher.py`

Responsibility:

-   compare normalized resume skills with job skills

-   calculate semantic similarity

-   classify relationships

-   produce match confidence

-   preserve supporting evidence

Planned initial embedding candidate:

`all-MiniLM-L6-v2`

The exact model will be validated during implementation and evaluation.

* * * * *

38\. GapAnalyzer
================

Planned file:

`backend/app/analysis/gap_analyzer.py`

Responsibility:

-   identify missing skills

-   identify partial matches

-   identify insufficient proficiency

-   determine gap severity

-   connect gaps to job requirements

-   preserve evidence

GapAnalyzer does not own official scoring.

* * * * *

39\. ScoreEngine
================

Planned file:

`backend/app/analysis/score_engine.py`

Responsibility:

-   calculate official compatibility scores

-   calculate scoring dimensions

-   apply explicit weights

-   apply bonuses and penalties

-   calculate score confidence

ScoreEngine is the sole owner of official scoring.

Public score:

`0--100`

Internal calculations may use:

`0--1`

* * * * *

40\. XAIEngine
==============

Planned file:

`backend/app/analysis/xai_engine.py`

Responsibility:

-   explain analytical outputs

-   explain score contributions

-   explain strengths and weaknesses

-   explain skill matches

-   explain skill gaps

-   map conclusions to evidence

Primary planned explainability approach:

SHAP

Possible alternative:

LIME

XAIEngine must not independently redefine the official score.

* * * * *

41\. CareerIntelligenceEngine
=============================

Planned file:

`backend/app/analysis/career_engine.py`

Responsibility:

-   infer candidate experience level

-   identify professional domains

-   identify career signals

-   identify strengths

-   identify potential roles

-   estimate role fit

-   identify career transition opportunities

-   prioritize skills for development

* * * * *

42\. RecommendationEngine
=========================

Planned file:

`backend/app/analysis/recommendation_engine.py`

Responsibility:

-   generate actionable recommendations

-   prioritize recommendations

-   connect recommendations to skill gaps

-   estimate impact and effort

-   preserve evidence

-   provide recommendation confidence

This engine is the sole owner of recommendations.

* * * * *

43\. backend/app/infrastructure/
================================

Purpose:

Contains integrations with external technical systems.

Structure:

```
backend/app/infrastructure/
├── models/
├── repositories/
├── parsers/
└── ml/

```

Infrastructure must implement technical details without becoming the owner of domain decisions.

* * * * *

44\. backend/app/infrastructure/parsers/
========================================

Purpose:

Reserved for document parser implementations.

Potential parser responsibilities:

-   PDF text extraction

-   DOCX text extraction

-   document metadata extraction

-   section detection

These parsers are infrastructure implementations used by DocumentProcessor.

* * * * *

45\. backend/app/infrastructure/ml/
===================================

Purpose:

Reserved for machine-learning infrastructure.

Potential responsibilities:

-   loading embedding models

-   model configuration

-   inference utilities

-   model caching

-   transformer integration

The infrastructure layer should provide model capabilities to analytical engines without taking ownership of business logic.

* * * * *

46\. backend/app/infrastructure/repositories/
=============================================

Purpose:

Reserved for persistence implementations.

Potential responsibilities:

-   storing analyses

-   retrieving analyses

-   deleting analyses

-   storing documents

-   managing analysis metadata

Repositories should abstract persistence from the analytical domain.

* * * * *

47\. backend/app/infrastructure/models/
=======================================

Purpose:

Reserved for persistence-specific models.

These models should represent database/storage concerns and should not replace the canonical domain models.

* * * * *

48\. backend/app/utils/
=======================

Purpose:

Contains small reusable utilities that do not belong to a specific domain responsibility.

Utilities should remain lightweight.

Business logic should not be moved into generic utility modules simply to avoid creating a proper domain component.

* * * * *

49\. Backend Tests
==================

Test location:

`backend/tests/`

Structure:

```
backend/tests/
├── api/
├── evaluation/
├── integration/
├── unit/
└── fixtures/

```

* * * * *

50\. backend/tests/unit/
========================

Purpose:

Unit tests for isolated components.

Current unit coverage includes domain contract validation.

Future unit tests should cover:

-   document processing

-   skill extraction

-   normalization

-   semantic matching

-   gap analysis

-   scoring

-   XAI

-   career intelligence

-   recommendations

* * * * *

51\. backend/tests/integration/
===============================

Purpose:

Tests interactions between multiple backend components.

Examples:

-   orchestrator + engines

-   document processor + parser

-   engine + repository

-   complete analysis pipeline

* * * * *

52\. backend/tests/api/
=======================

Purpose:

Tests HTTP/API behavior.

Current API tests cover the Phase 1 analysis endpoints and health behavior.

Future tests should cover:

-   valid uploads

-   invalid files

-   file-size limits

-   completed analysis retrieval

-   deletion

-   API error contracts

-   mode-specific behavior

* * * * *

53\. backend/tests/evaluation/
==============================

Purpose:

Reserved for analytical evaluation.

This is important because SkillLens is an academic project involving NLP, semantic matching, and explainability.

Evaluation should eventually measure:

-   skill extraction quality

-   normalization accuracy

-   semantic matching quality

-   gap detection quality

-   scoring consistency

-   explanation quality

-   recommendation usefulness

Evaluation datasets should be kept separate from normal unit-test fixtures.

* * * * *

54\. backend/tests/fixtures/
============================

Purpose:

Contains controlled test inputs.

Potential fixtures:

-   sample resumes

-   sample job descriptions

-   expected skill sets

-   expected matches

-   expected gaps

-   expected scoring results

Fixtures should be deterministic and reproducible.

* * * * *

55\. backend/requirements.txt
=============================

Purpose:

Defines Python dependencies.

Current Phase 1 dependencies include:

-   FastAPI

-   Uvicorn

-   Pydantic

-   Pydantic Settings

-   python-multipart

-   pytest

-   pytest-asyncio

-   httpx

Advanced NLP/ML dependencies are intentionally deferred until the relevant implementation phase.

* * * * *

56\. Frontend Overview
======================

Frontend location:

`frontend/`

Technology:

-   React

-   TypeScript

-   Vite

Current structure:

```
frontend/
├── src/
├── tests/
├── package.json
├── package-lock.json
├── vite.config.ts
├── tsconfig.json
├── tsconfig.app.json
├── tsconfig.node.json
└── eslint.config.js

```

* * * * *

57\. frontend/src/
==================

Primary frontend source directory.

Structure:

```
frontend/src/
├── app/
├── pages/
├── components/
├── features/
├── hooks/
├── services/
├── state/
├── types/
├── utils/
└── styles/

```

Some directories are currently reserved for later implementation.

* * * * *

58\. frontend/src/app/
======================

Purpose:

Application-level React setup.

Current file:

`frontend/src/app/App.tsx`

Responsibility:

-   application root component

-   initial application shell

Current Phase 1 implementation is intentionally minimal.

* * * * *

59\. frontend/src/main.tsx
==========================

Purpose:

React application entry point.

Responsibilities:

-   locate root DOM element

-   render the React application

-   enable React Strict Mode

It renders:

`App`

* * * * *

60\. frontend/src/pages/
========================

Purpose:

Reserved for route-level page components.

Planned pages may include:

-   dashboard

-   upload

-   analysis

-   visualizations

-   skills

-   matching

-   career intelligence

-   XAI

-   recommendations

-   settings

Pages should compose feature components rather than contain analytical logic.

* * * * *

61\. frontend/src/components/
=============================

Purpose:

Reserved for reusable UI components.

Examples:

-   cards

-   tables

-   charts

-   badges

-   dialogs

-   navigation

-   layout components

Reusable components should remain domain-agnostic where practical.

* * * * *

62\. frontend/src/features/
===========================

Purpose:

Organizes UI by business capability.

Planned feature areas:

```
frontend/src/features/
├── analysis/
├── skills/
├── matching/
├── career/
├── xai/
└── recommendations/

```

Feature modules should contain presentation and interaction logic related to their respective capabilities.

They should not implement backend analytical algorithms.

* * * * *

63\. frontend/src/hooks/
========================

Purpose:

Reserved for reusable React hooks.

Potential responsibilities:

-   analysis loading

-   API state

-   upload state

-   UI state

-   feature-specific behavior

* * * * *

64\. frontend/src/services/
===========================

Purpose:

Contains frontend service integrations.

Planned structure:

```
frontend/src/services/
└── api/

```

API service modules should centralize backend communication.

Components should not repeatedly construct API requests themselves.

* * * * *

65\. frontend/src/state/
========================

Purpose:

Contains frontend application state.

Current file:

`frontend/src/state/analysisState.ts`

It defines:

-   analysis status

-   current analysis

-   error state

-   last request ID

The state model corresponds to the canonical backend analysis contract.

* * * * *

66\. frontend/src/types/
========================

Purpose:

Contains TypeScript contracts.

Current files:

```
frontend/src/types/
├── analysis.ts
└── api.ts

```

* * * * *

67\. frontend/src/types/analysis.ts
===================================

Purpose:

Contains the canonical frontend representation of analysis-domain types.

It mirrors the backend contract for:

-   AnalysisResult

-   ResumeProfile

-   JobProfile

-   Skill

-   Evidence

-   SkillMatch

-   SkillGap

-   ScoringResult

-   XAIResult

-   CareerIntelligence

-   Recommendation

This file allows the frontend to use strongly typed analytical data.

* * * * *

68\. frontend/src/types/api.ts
==============================

Purpose:

Contains API request and response interfaces.

Includes:

-   AnalysisOptions

-   ClientMetadata

-   ResumeAnalysisRequest

-   ResumeJDAnalysisRequest

-   AnalysisResponse

-   AnalysisAcceptedResponse

-   DeleteAnalysisResponse

-   ErrorResponse

These types should remain synchronized with the backend API contract.

* * * * *

69\. frontend/src/utils/
========================

Purpose:

Reserved for generic frontend utilities.

Examples may include:

-   formatting

-   date handling

-   score formatting

-   validation helpers

Business-specific analytical logic should remain within the appropriate feature or backend engine.

* * * * *

70\. frontend/src/styles/
=========================

Purpose:

Reserved for global styling and design-system definitions.

Potential responsibilities:

-   global CSS

-   theme variables

-   typography

-   layout primitives

-   design tokens

* * * * *

71\. Frontend Tests
===================

Location:

`frontend/tests/`

Purpose:

Reserved for frontend testing.

Future tests should cover:

-   component rendering

-   feature behavior

-   API state transitions

-   error states

-   analysis visualization

-   user interaction

* * * * *

72\. Documentation Files
========================

The repository documentation is divided into dedicated files.

Planned documentation set:

```
PROJECT_MASTER.md
PROJECT_STATUS.md
ARCHITECTURE.md
API_CONTRACT.md
DATA_SCHEMA.md
CODEBASE_MAP.md
CHANGELOG.md
SESSION_HANDOFF.md

```

Each document has a distinct purpose.

* * * * *

73\. PROJECT_MASTER.md
======================

Purpose:

Defines the permanent project specification.

Contains:

-   project identity

-   objective

-   scope

-   architecture principles

-   technology stack

-   major features

-   development rules

-   non-negotiable constraints

This document should change infrequently.

* * * * *

74\. PROJECT_STATUS.md
======================

Purpose:

Tracks the current implementation state.

Contains:

-   completed work

-   verified checks

-   known issues

-   current phase

-   next tasks

-   implementation status

This document should be updated regularly.

* * * * *

75\. ARCHITECTURE.md
====================

Purpose:

Defines the system architecture.

Contains:

-   layers

-   dependencies

-   engine responsibilities

-   data flow

-   API architecture

-   frontend architecture

-   infrastructure strategy

-   architectural invariants

* * * * *

76\. API_CONTRACT.md
====================

Purpose:

Defines the HTTP/API interface.

Contains:

-   endpoints

-   request contracts

-   response contracts

-   error contracts

-   status codes

-   API invariants

* * * * *

77\. DATA_SCHEMA.md
===================

Purpose:

Defines canonical domain data structures.

Contains:

-   AnalysisResult

-   ResumeProfile

-   JobProfile

-   Skill

-   Evidence

-   SkillMatch

-   SkillGap

-   ScoringResult

-   XAIResult

-   CareerIntelligence

-   Recommendation

* * * * *

78\. CODEBASE_MAP.md
====================

Purpose:

This document.

It explains where each responsibility belongs in the repository.

* * * * *

79\. CHANGELOG.md
=================

Purpose:

Tracks meaningful project changes.

Entries should describe:

-   architectural changes

-   feature additions

-   bug fixes

-   dependency changes

-   schema changes

-   important refactoring

Minor generated files should not create unnecessary changelog entries.

* * * * *

80\. SESSION_HANDOFF.md
=======================

Purpose:

Provides context for continuing development in a new AI-assisted coding session.

It should contain:

-   current phase

-   completed work

-   verified commands

-   current repository state

-   active task

-   next task

-   important architectural constraints

-   known issues

This file is especially important when development is split across multiple AI chat sessions.

* * * * *

81\. Dependency Direction
=========================

The intended backend dependency direction is:

```
API
 ↓
Orchestration
 ↓
Domain
 ↓
Infrastructure

```

Analytical engines operate within the application/domain boundary and must follow the established dependency rules.

The following is prohibited:

```
Engine A → Engine B → Engine C

```

Instead:

```
Orchestrator
 ├── Engine A
 ├── Engine B
 └── Engine C

```

The orchestrator determines execution order.

* * * * *

82\. Frontend Dependency Direction
==================================

The frontend follows:

```
Pages
 ↓
Features / Components
 ↓
Hooks / State
 ↓
API Services
 ↓
Backend API

```

Frontend components must not contain backend analytical algorithms.

* * * * *

83\. Canonical Ownership Map
============================

| Responsibility | Canonical Location |
| --- | --- |
| Application startup | `backend/app/main.py` |
| Configuration | `backend/app/core/config.py` |
| Internal exceptions | `backend/app/core/exceptions.py` |
| Logging | `backend/app/core/logging.py` |
| HTTP routes | `backend/app/api/routes/` |
| API request schemas | `backend/app/schemas/requests.py` |
| API response schemas | `backend/app/schemas/responses.py` |
| API errors | `backend/app/schemas/errors.py` |
| Domain models | `backend/app/domain/` |
| Workflow coordination | `backend/app/orchestration/` |
| Document processing | `backend/app/analysis/document_processor.py` |
| Skill extraction | `backend/app/analysis/skill_extractor.py` |
| Skill normalization | `backend/app/analysis/skill_normalizer.py` |
| Semantic matching | `backend/app/analysis/semantic_matcher.py` |
| Gap analysis | `backend/app/analysis/gap_analyzer.py` |
| Scoring | `backend/app/analysis/score_engine.py` |
| Explainability | `backend/app/analysis/xai_engine.py` |
| Career intelligence | `backend/app/analysis/career_engine.py` |
| Recommendations | `backend/app/analysis/recommendation_engine.py` |
| Persistence | `backend/app/infrastructure/repositories/` |
| Parsing | `backend/app/infrastructure/parsers/` |
| ML infrastructure | `backend/app/infrastructure/ml/` |
| Backend tests | `backend/tests/` |
| Frontend application | `frontend/src/app/` |
| Frontend pages | `frontend/src/pages/` |
| UI components | `frontend/src/components/` |
| Feature modules | `frontend/src/features/` |
| Frontend state | `frontend/src/state/` |
| API services | `frontend/src/services/api/` |
| Frontend types | `frontend/src/types/` |
| Frontend tests | `frontend/tests/` |

* * * * *

84\. Current Implementation State
=================================

At the completion of Phase 1:

Implemented:

-   backend package structure

-   FastAPI application

-   API routing

-   configuration

-   logging

-   exception handling

-   API schemas

-   domain model structure

-   orchestrator interface

-   frontend Vite application

-   frontend TypeScript contracts

-   frontend analysis state

-   backend tests

-   frontend linting

-   frontend production build

Not yet implemented:

-   document processing

-   PDF parsing

-   DOCX parsing

-   skill extraction

-   skill normalization

-   transformer embeddings

-   semantic matching

-   ESCO integration

-   gap analysis

-   scoring engine

-   XAI engine

-   career intelligence engine

-   recommendation engine

-   persistence implementation

-   production frontend feature pages

* * * * *

85\. Validation Status
======================

Backend validation:

`python -m compileall -q backend`

Status:

PASS

Backend tests:

`python -m pytest backend/tests -q`

Status:

PASS

Current result:

`9 passed`

Frontend lint:

`npm run lint`

Status:

PASS

Frontend build:

`npm run build`

Status:

PASS

OpenAPI route verification confirms the expected API endpoints are registered.

Dependency-direction verification:

`NONE`

Duplicate module-name verification:

`NONE`

* * * * *

86\. Codebase Invariants
========================

The following rules must remain true:

1.  There is one canonical implementation for each analytical responsibility.

2.  The orchestrator controls analytical workflow execution.

3.  Engines do not directly call other engines.

4.  Domain models are independent of API and UI implementation.

5.  API routes do not contain analytical algorithms.

6.  Frontend does not implement backend analytical logic.

7.  `AnalysisResult` remains the canonical analysis result.

8.  ScoreEngine owns official scoring.

9.  XAIEngine explains existing results.

10. RecommendationEngine owns recommendations.

11. Evidence should be preserved for analytical conclusions.

12. Resume-only analysis does not fabricate job-specific results.

13. New dependencies must have a clear architectural justification.

14. Infrastructure must not become a second source of domain logic.

15. Tests must remain organized according to their testing responsibility.

* * * * *

87\. AI Development Rule
========================

Any AI-assisted modification to the repository must first determine:

1.  Which responsibility is being changed.

2.  Which canonical module owns that responsibility.

3.  Whether an existing implementation already exists.

4.  Whether the proposed change creates duplicate logic.

5.  Whether the change violates dependency direction.

6.  Whether domain/API/frontend contracts need updating.

7.  Which tests must be updated.

AI-generated code must fit the existing architecture rather than introducing an alternative architecture.

* * * * *

Document Processing Infrastructure
----------------------------------

Actual Phase 2 implementation:

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

### Module Responsibilities

| Module | Responsibility |
| --- | --- |
| `base.py` | Abstract document parser contract |
| `models.py` | Normalized document models and provenance structures |
| `validation.py` | File/document validation |
| `pdf_parser.py` | PDF text/block extraction using PyMuPDF |
| `docx_parser.py` | DOCX paragraph/table extraction using python-docx |
| `document_processor.py` | Validation, parser selection, and normalized processing entry point |
| `__init__.py` | Public parser-layer exports |

### Phase 2 Processing Flow

```
Input bytes
    ↓
DocumentProcessor
    ↓
validate_document()
    ↓
PDFParser / DOCXParser
    ↓
ParsedDocument

```

### Important Boundary

The parser layer performs document processing only.

It does not perform:

-   Skill extraction

-   Semantic matching

-   Scoring

-   Explainability

-   Recommendations

-   Career intelligence

Those responsibilities remain assigned to downstream components and future phases.