SkillLens --- Codebase Map
========================

1\. Purpose
-----------

This document provides a practical map of the SkillLens repository.

It identifies:

-   where major responsibilities are implemented

-   where domain and API contracts are defined

-   where document processing is located

-   where Phase 3 resume intelligence is implemented

-   where frontend code is located

-   where tests and fixtures are stored

-   which components are implemented

-   which components are reserved for future phases

The purpose is to make the repository understandable to both human developers and AI coding assistants.

* * * * *

2\. Repository Root
===================

```
SkillLens/
├── backend/
├── frontend/
├── docs/
├── .gitignore
└── skilllens/

```

`skilllens/` is the local Python virtual environment and is excluded from Git.

* * * * *

3\. Backend
===========

Backend location:

`backend/`

Technology:

-   Python

-   FastAPI

-   Pydantic

-   Uvicorn

The backend follows a modular-monolith architecture.

```
backend/
├── app/
├── tests/
└── requirements.txt

```

* * * * *

4\. Backend Application Structure
=================================

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

Responsibilities:

| Directory | Responsibility |
| --- | --- |
| `api/` | HTTP/API layer |
| `core/` | Configuration, logging, exceptions |
| `domain/` | Canonical domain models |
| `schemas/` | API transport schemas |
| `orchestration/` | Analysis workflow coordination |
| `analysis/` | Analytical engines |
| `infrastructure/` | Parsers, ML, persistence integrations |
| `utils/` | Small reusable utilities |

* * * * *

5\. Application Entry Point
===========================

File:

`backend/app/main.py`

Responsibilities:

-   create the FastAPI application

-   configure logging

-   register routers

-   configure application metadata

-   register application-level exception handling

Current API routers include:

-   health

-   analyses

`main.py` must remain an application-composition layer and must not contain analytical algorithms.

* * * * *

6\. API Layer
=============

Location:

`backend/app/api/`

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

It does not own analytical logic.

* * * * *

7\. API Routes
==============

`health.py`
-----------

File:

`backend/app/api/routes/health.py`

Endpoint:

`GET /api/v1/health`

Provides basic application health information.

* * * * *

`analyses.py`
-------------

File:

`backend/app/api/routes/analyses.py`

Analysis endpoints:

```
POST   /api/v1/analyses/resume
POST   /api/v1/analyses/resume-jd
GET    /api/v1/analyses/{analysis_id}
DELETE /api/v1/analyses/{analysis_id}

```

The routes define the public analysis API contract.

The analysis endpoints currently use controlled application behavior rather than exposing a completed end-to-end public analysis workflow.

Future API integration will connect these routes to the central analysis orchestration layer.

* * * * *

8\. Core Layer
==============

Location:

`backend/app/core/`

```
backend/app/core/
├── __init__.py
├── config.py
├── exceptions.py
└── logging.py

```

### `config.py`

Central application configuration.

Includes settings such as:

-   application name

-   application version

-   environment

-   API prefix

-   debug configuration

-   upload limits

### `exceptions.py`

Defines application-level exceptions, including:

`ApplicationError`

### `logging.py`

Provides centralized application logging.

* * * * *

9\. Domain Layer
================

Location:

`backend/app/domain/`

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

The domain layer contains canonical analytical data structures.

It must remain independent of:

-   FastAPI

-   React

-   HTTP transport

-   UI implementation

-   database-specific implementation

Important domain ownership:

| File | Main responsibility |
| --- | --- |
| `analysis.py` | `AnalysisResult` |
| `resume.py` | Resume structures |
| `job.py` | Job structures |
| `skill.py` | Skill structures |
| `evidence.py` | Evidence structures |
| `confidence.py` | Confidence structures |
| `matching.py` | Match structures |
| `gaps.py` | Gap structures |
| `scoring.py` | Scoring structures |
| `xai.py` | Explainability structures |
| `career.py` | Career structures |
| `recommendations.py` | Recommendation structures |

Domain models define data contracts; analytical algorithms belong elsewhere.

* * * * *

10\. API Schemas
================

Location:

`backend/app/schemas/`

```
backend/app/schemas/
├── __init__.py
├── requests.py
├── responses.py
└── errors.py

```

### `requests.py`

Defines API request contracts such as:

-   `AnalysisOptions`

-   `ClientMetadata`

-   `ResumeAnalysisRequest`

-   `ResumeJDAnalysisRequest`

### `responses.py`

Defines API response contracts such as:

-   `AnalysisResponse`

-   `AnalysisAcceptedResponse`

-   `DeleteAnalysisResponse`

### `errors.py`

Defines the external API error representation.

API schemas are transport contracts and must not contain analytical algorithms.

* * * * *

11\. Orchestration Layer
========================

Location:

`backend/app/orchestration/`

```
backend/app/orchestration/
├── __init__.py
└── analysis_orchestrator.py

```

The orchestrator is the central workflow coordinator.

It is responsible for controlling analysis execution order.

Conceptually:

```
API
 ↓
AnalysisOrchestrator
 ↓
Analysis Components
 ↓
Canonical Domain Result

```

There must be one canonical analysis orchestrator.

* * * * *

12\. Analysis Layer
===================

Location:

`backend/app/analysis/`

Current Phase 3 structure:

```
backend/app/analysis/
├── __init__.py
├── esco_mapper.py
├── resume_profile_builder.py
├── resume_structure.py
├── skill_extractor.py
└── skill_normalizer.py

```

Phase 3 implemented the resume-intelligence pipeline in this directory.

Future analytical components will be added here without duplicating existing responsibilities.

* * * * *

13\. Phase 3 Resume Structure
=============================

File:

`backend/app/analysis/resume_structure.py`

Responsibility:

-   interpret resume section structure

-   classify recognized headings

-   preserve block order

-   preserve source document identity

-   produce structured resume sections

Primary structures:

-   `ResumeSectionType`

-   `ResumeSection`

-   `StructuredResume`

-   `ResumeStructureInterpreter`

This component consumes `ParsedDocument`.

It does not parse PDF/DOCX files directly.

* * * * *

14\. Phase 3 Skill Extraction
=============================

File:

`backend/app/analysis/skill_extractor.py`

Responsibility:

-   identify skill mentions

-   distinguish explicit and contextual evidence

-   preserve source block provenance

-   preserve offsets

-   attach extraction confidence

Primary structures:

-   `SkillEvidenceType`

-   `SkillMention`

-   `SkillExtractionResult`

-   `SkillExtractor`

Current extraction is deterministic and vocabulary-assisted.

It does not perform normalization, ESCO mapping, matching, or scoring.

* * * * *

15\. Phase 3 Skill Normalization
================================

File:

`backend/app/analysis/skill_normalizer.py`

Responsibility:

-   normalize skill text

-   resolve known aliases

-   produce canonical skill names

-   preserve raw extracted text

-   preserve extraction confidence

Primary structure:

-   `NormalizedSkill`

Examples:

```
Python Programming → python
Python 3           → python
ReactJS            → react
Postgres           → postgresql
ML                 → machine learning

```

Normalization is separate from extraction and semantic matching.

* * * * *

16\. Phase 3 ESCO Mapping
=========================

File:

`backend/app/analysis/esco_mapper.py`

Responsibility:

-   map normalized skills toward ESCO concepts

-   classify mapping status

-   preserve candidate confidence

-   preserve mapping metadata

Primary structures:

-   `ESCOMapStatus`

-   `ESCOCandidate`

-   `ESCOMapResult`

-   `ESCOMapper`

Current supported mapping states:

-   `MAPPED`

-   `AMBIGUOUS`

-   `UNMAPPED`

Current implementation uses a deterministic adapter vocabulary.

ESCO version metadata:

`1.2.1`

The mapper must never fabricate ESCO identifiers.

* * * * *

17\. Phase 3 Resume Profile Builder
===================================

File:

`backend/app/analysis/resume_profile_builder.py`

Responsibility:

-   construct the canonical `ResumeProfile`

-   deduplicate normalized skills

-   merge evidence

-   preserve provenance

-   aggregate confidence

-   assign skill categories

-   attach processing metadata

Primary structure:

-   `ResumeProfileBuilder`

The builder is the final Phase 3 transformation from intermediate resume-analysis data into the canonical resume profile.

It must not invent unsupported candidate information.

* * * * *

18\. Phase 3 Resume Intelligence Flow
=====================================

The current implemented Phase 3 flow is:

```
ParsedDocument
      ↓
ResumeStructureInterpreter
      ↓
StructuredResume
      ↓
SkillExtractor
      ↓
SkillMention[]
      ↓
SkillNormalizer
      ↓
NormalizedSkill[]
      ↓
ESCOMapper
      ↓
ESCOMapResult[]
      ↓
ResumeProfileBuilder
      ↓
ResumeProfile

```

Evidence and confidence are preserved throughout the pipeline.

* * * * *

19\. Infrastructure Layer
=========================

Location:

`backend/app/infrastructure/`

```
backend/app/infrastructure/
├── models/
├── repositories/
├── parsers/
└── ml/

```

Infrastructure contains technical integrations.

It should not become a second source of domain logic.

* * * * *

20\. Document Processing Infrastructure
=======================================

Location:

`backend/app/infrastructure/parsers/`

Current implementation:

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

| File | Responsibility |
| --- | --- |
| `base.py` | Parser interface |
| `models.py` | `ParsedDocument`, `DocumentBlock`, provenance models |
| `validation.py` | Document validation |
| `pdf_parser.py` | PDF extraction |
| `docx_parser.py` | DOCX extraction |
| `document_processor.py` | Validation, parser selection, normalized processing |

* * * * *

21\. Document Processing Boundary
=================================

Phase 2 established the frozen document-processing boundary:

```
Raw PDF / DOCX
      ↓
DocumentProcessor
      ↓
ParsedDocument
      ↓
Phase 3 Analysis

```

Phase 3 consumes `ParsedDocument`.

Phase 3 must not:

-   reparse PDF files

-   reparse DOCX files

-   duplicate parser logic

-   bypass `DocumentProcessor`

* * * * *

22\. Infrastructure ML
======================

Location:

`backend/app/infrastructure/ml/`

Reserved for technical ML infrastructure such as:

-   transformer model loading

-   embedding models

-   inference utilities

-   model caching

-   model configuration

ML infrastructure provides technical capabilities to analysis components; it does not own analytical business rules.

* * * * *

23\. Infrastructure Repositories
================================

Location:

`backend/app/infrastructure/repositories/`

Reserved for persistence implementations.

Potential responsibilities:

-   storing analyses

-   retrieving analyses

-   deleting analyses

-   storing documents

-   storing metadata

Repositories should abstract persistence from the domain layer.

* * * * *

24\. Infrastructure Models
==========================

Location:

`backend/app/infrastructure/models/`

Reserved for persistence-specific models.

These models must not replace canonical domain models.

* * * * *

25\. Future Analysis Components
===============================

The following responsibilities are planned but are not Phase 3 implementations:

| Component | Responsibility |
| --- | --- |
| `SemanticMatcher` | Resume/JD semantic matching |
| `GapAnalyzer` | Skill-gap detection |
| `ScoreEngine` | Official compatibility scoring |
| `XAIEngine` | Explainability |
| `CareerIntelligenceEngine` | Career analysis |
| `RecommendationEngine` | Recommendations |

These components must consume existing contracts rather than creating duplicate representations.

* * * * *

26\. Future Semantic Matcher
============================

Planned responsibility:

-   compare normalized resume and job skills

-   calculate semantic similarity

-   classify relationships

-   preserve evidence and confidence

Semantic matching is not implemented in Phase 3.

* * * * *

27\. Future Gap Analyzer
========================

Planned responsibility:

-   identify missing skills

-   identify partial matches

-   evaluate proficiency gaps

-   determine gap severity

-   connect gaps to job requirements

Gap analysis is not implemented in Phase 3.

* * * * *

28\. Future Score Engine
========================

Planned responsibility:

-   calculate official compatibility scores

-   calculate scoring dimensions

-   apply weights

-   apply explicit bonuses and penalties

-   produce scoring confidence

`ScoreEngine` will be the sole owner of official scoring.

Scoring is not implemented in Phase 3.

* * * * *

29\. Future XAI Engine
======================

Planned responsibility:

-   explain analytical results

-   explain score contributions

-   explain strengths and weaknesses

-   explain matches and gaps

-   connect conclusions to evidence

`XAIEngine` explains existing analytical outputs and does not own official scoring.

* * * * *

30\. Future Career Intelligence
===============================

Planned responsibility:

-   infer experience level

-   identify professional domains

-   identify career signals

-   identify strengths

-   identify potential roles

-   prioritize skills

Career intelligence is not implemented in Phase 3.

* * * * *

31\. Future Recommendation Engine
=================================

Planned responsibility:

-   generate actionable recommendations

-   prioritize recommendations

-   connect recommendations to evidence and gaps

-   estimate expected impact and effort

`RecommendationEngine` will be the sole owner of recommendations.

* * * * *

32\. Utilities
==============

Location:

`backend/app/utils/`

Contains small reusable utilities that do not belong to a specific domain responsibility.

Business logic must remain in the appropriate domain or analysis component rather than being hidden inside generic utilities.

* * * * *

33\. Backend Tests
==================

Location:

`backend/tests/`

```
backend/tests/
├── api/
├── evaluation/
├── integration/
├── unit/
└── fixtures/

```

* * * * *

34\. Unit Tests
===============

Location:

`backend/tests/unit/`

Current Phase 3 unit coverage includes:

-   resume structure interpretation

-   skill extraction

-   skill normalization

-   ESCO mapping

-   resume profile construction

Unit tests should test components independently and deterministically.

* * * * *

35\. Integration Tests
======================

Location:

`backend/tests/integration/`

Phase 3 integration coverage includes the complete resume-analysis chain:

```
ParsedDocument
      ↓
Structure
      ↓
Extraction
      ↓
Normalization
      ↓
ESCO Mapping
      ↓
ResumeProfile

```

Integration tests verify that the individual Phase 3 components work together correctly.

* * * * *

36\. Test Fixtures
==================

Location:

`backend/tests/fixtures/`

Current Phase 3 real-document fixtures include:

-   `phase3_sample_resume.docx`

-   `phase3_sample_resume.pdf`

Fixtures are used for deterministic real-file verification.

* * * * *

37\. Evaluation Tests
=====================

Location:

`backend/tests/evaluation/`

Reserved for analytical evaluation.

Future evaluation should measure areas such as:

-   skill extraction quality

-   normalization accuracy

-   semantic matching quality

-   gap detection

-   scoring consistency

-   explanation quality

-   recommendation usefulness

Evaluation datasets should remain separate from normal unit-test fixtures.

* * * * *

38\. Frontend
=============

Location:

`frontend/`

Technology:

-   React

-   TypeScript

-   Vite

Primary structure:

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

39\. Frontend Source
====================

Location:

`frontend/src/`

Conceptual organization:

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

Frontend responsibilities are limited to presentation, interaction, state, and API communication.

Backend analytical logic must not be duplicated in the frontend.

* * * * *

40\. Frontend Application
=========================

Location:

`frontend/src/app/`

Contains application-level React setup.

`frontend/src/main.tsx` is the frontend entry point.

* * * * *

41\. Frontend Pages and Components
==================================

`frontend/src/pages/`

Contains route-level page components.

`frontend/src/components/`

Contains reusable UI components.

Pages should compose components and feature modules rather than implement analytical algorithms.

* * * * *

42\. Frontend Features
======================

Location:

`frontend/src/features/`

Organizes UI by business capability.

Planned feature areas include:

-   analysis

-   skills

-   matching

-   career

-   XAI

-   recommendations

These feature modules are presentation/interaction layers, not analytical engine implementations.

* * * * *

43\. Frontend State
===================

Location:

`frontend/src/state/`

Current analysis state is maintained through the analysis state module.

State includes concepts such as:

-   analysis status

-   current analysis

-   error state

-   request information

Frontend state must represent API/domain contracts rather than create independent domain definitions.

* * * * *

44\. Frontend Services
======================

Location:

`frontend/src/services/`

Responsible for backend API communication.

API requests should be centralized in service modules instead of being repeatedly constructed inside UI components.

* * * * *

45\. Frontend Types
===================

Location:

`frontend/src/types/`

Current contracts include:

```
analysis.ts
api.ts

```

These provide TypeScript representations of backend analysis and API contracts.

They should remain synchronized with stable backend contracts.

* * * * *

46\. Frontend Tests
===================

Location:

`frontend/tests/`

Reserved for frontend testing.

Future coverage should include:

-   component behavior

-   feature behavior

-   API state transitions

-   error handling

-   analysis visualization

-   user interactions

* * * * *

47\. Documentation
==================

Documentation is located under:

`docs/`

Current documentation includes:

```
PROJECT_MASTER.md
PROJECT_STATUS.md
ARCHITECTURE.md
API_CONTRACT.md
DATA_SCHEMA.md
CODEBASE_MAP.md
FEATURES.md
CHANGELOG.md
SESSION_HANDOFF.md

```

Each document has a distinct purpose.

### Project Master

Permanent project specification and constraints.

### Project Status

Current implementation state and progress.

### Architecture

System structure, dependency direction, and component ownership.

### API Contract

HTTP endpoints and transport contracts.

### Data Schema

Canonical domain and analytical data structures.

### Codebase Map

Repository responsibility and file-location reference.

### Features

Feature-level scope and implementation status.

### Changelog

Meaningful project changes.

### Session Handoff

Context required to continue development across AI-assisted sessions.

* * * * *

48\. Canonical Ownership Map
============================

| Responsibility | Canonical Location |
| --- | --- |
| Application startup | `backend/app/main.py` |
| Configuration | `backend/app/core/config.py` |
| Exceptions | `backend/app/core/exceptions.py` |
| Logging | `backend/app/core/logging.py` |
| HTTP routes | `backend/app/api/routes/` |
| API request schemas | `backend/app/schemas/requests.py` |
| API response schemas | `backend/app/schemas/responses.py` |
| API errors | `backend/app/schemas/errors.py` |
| Domain models | `backend/app/domain/` |
| Workflow coordination | `backend/app/orchestration/` |
| Resume structure | `backend/app/analysis/resume_structure.py` |
| Skill extraction | `backend/app/analysis/skill_extractor.py` |
| Skill normalization | `backend/app/analysis/skill_normalizer.py` |
| ESCO mapping | `backend/app/analysis/esco_mapper.py` |
| Resume profile construction | `backend/app/analysis/resume_profile_builder.py` |
| Document processing | `backend/app/infrastructure/parsers/` |
| Persistence | `backend/app/infrastructure/repositories/` |
| ML infrastructure | `backend/app/infrastructure/ml/` |
| Backend tests | `backend/tests/` |
| Frontend application | `frontend/src/app/` |
| Frontend pages | `frontend/src/pages/` |
| UI components | `frontend/src/components/` |
| Frontend features | `frontend/src/features/` |
| Frontend state | `frontend/src/state/` |
| API services | `frontend/src/services/` |
| Frontend types | `frontend/src/types/` |
| Frontend tests | `frontend/tests/` |

* * * * *

49\. Dependency Direction
=========================

The intended backend flow is:

```
API
 ↓
Analysis Orchestrator
 ↓
Analysis Components
 ↓
Domain Models
 ↓
Infrastructure

```

The analysis components must not form an uncontrolled chain of direct engine-to-engine dependencies.

The orchestrator controls workflow execution.

The document-processing infrastructure is consumed through its normalized `ParsedDocument` boundary.

* * * * *

50\. Phase Boundaries
=====================

Phase 1
-------

Established:

-   project architecture

-   domain contracts

-   API contracts

-   application foundation

-   frontend foundation

-   testing foundation

Phase 2
-------

Implemented:

-   document validation

-   PDF parsing

-   DOCX parsing

-   normalized document blocks

-   provenance

-   `ParsedDocument`

Phase 2 document-processing boundary is frozen.

Phase 3
-------

Implemented:

-   resume structure interpretation

-   deterministic skill extraction

-   skill normalization

-   ESCO mapping adapter

-   evidence preservation

-   confidence handling

-   canonical resume-profile construction

-   real PDF/DOCX fixture verification

Phase 3 consumes the Phase 2 `ParsedDocument` contract.

Future Phases
-------------

Reserved for:

-   JD analysis

-   semantic matching

-   skill-gap analysis

-   scoring

-   XAI

-   career intelligence

-   recommendations

-   broader ML/transformer integration

-   production frontend analysis workflows

* * * * *

51\. Current Repository State
=============================

Phase 3 is complete and committed.

The current Phase 3 implementation is centered around:

```
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

```

Current verification includes:

-   Phase 3 unit tests

-   Phase 3 integration tests

-   full backend regression suite

-   real PDF parsing verification

-   real DOCX parsing and full Phase 3 pipeline verification

The latest Phase 3 commit is:

`0b73efe Complete Phase 3 resume intelligence pipeline`

* * * * *

52\. Codebase Invariants
========================

The following rules must remain true:

1.  Each analytical responsibility has one canonical implementation.

2.  The analysis orchestrator controls workflow execution.

3.  Analytical engines must not create duplicate engines or domain models.

4.  Domain models remain independent of API and UI implementation.

5.  API routes do not contain analytical algorithms.

6.  Frontend does not implement backend analytical logic.

7.  `AnalysisResult` remains the canonical top-level result.

8.  `ParsedDocument` remains the frozen document-processing boundary.

9.  Phase 3 consumes `ParsedDocument` rather than reparsing source files.

10. Skill normalization produces canonical skill identities.

11. Evidence should be preserved for analytical conclusions.

12. `ESCOMapper` owns ESCO mapping behavior.

13. `ResumeProfileBuilder` owns canonical resume-profile construction.

14. ScoreEngine will own official scoring.

15. XAIEngine will explain existing analytical outputs.

16. RecommendationEngine will own recommendations.

17. Infrastructure must not become a second source of domain logic.

18. New dependencies require architectural justification.

19. Tests must remain organized according to their responsibility.

20. AI-assisted changes must reuse existing canonical components instead of introducing parallel implementations.
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

Phase 6 --- New Components
------------------------

**Status: COMPLETE / FROZEN**

### Analysis Engines

```
backend/app/analysis/gaps.py

```

`GapAnalyzer`

Responsible for requirement-linked skill-gap analysis using existing Phase 5 matching and alignment results.

```
backend/app/analysis/scoring.py

```

`ScoringAnalyzer`

Responsible for deterministic candidate-job scoring, dimension weighting, UNKNOWN handling, and score contribution decomposition.

```
backend/app/analysis/xai.py

```

`XAIAnalyzer`

Responsible for deterministic explanations of existing matching, gap, and scoring results.

### Modified Domain Contracts

```
backend/app/domain/gaps.py

```

Extended `SkillGap` and `SkillAnalysis`.

```
backend/app/domain/scoring.py

```

Added score contribution and extended scoring result contracts.

### Modified Orchestration

```
backend/app/orchestration/concrete_analysis_orchestrator.py

```

Integrates:

```
GapAnalyzer
ScoringAnalyzer
XAIAnalyzer

```

into the existing Resume + JD workflow.

### Phase 6 Tests

```
backend/tests/unit/test_gaps.py
backend/tests/unit/test_scoring.py
backend/tests/unit/test_xai.py

```

Phase 6 integration coverage also exists in:

```
backend/tests/unit/test_analysis_orchestrator.py
backend/tests/api/test_analysis_api.py

```

Detailed component behavior is documented in:

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