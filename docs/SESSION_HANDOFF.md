SkillLens --- Session Handoff
===========================

1\. Purpose
-----------

This document provides the minimum context required to continue SkillLens development in a new development or AI-assisted coding session.

It is intended to prevent loss of project context between sessions.

The next development session must read this document together with:

-   `PROJECT_MASTER.md`

-   `PROJECT_STATUS.md`

-   `ARCHITECTURE.md`

-   `API_CONTRACT.md`

-   `DATA_SCHEMA.md`

-   `CODEBASE_MAP.md`

-   `CHANGELOG.md`

These documents together form the project's persistent development context.

* * * * *

2\. Project Identity
====================

Project name:

`SkillLens`

Project title:

`XAI-Driven Semantic Skill Gap Analysis using Transformer-Based Language Models`

Project type:

Academic software engineering and AI/NLP project.

Primary objective:

Build an explainable AI system that analyzes a candidate resume, optionally compares it against a job description, identifies semantic skill matches and gaps, evaluates candidate-job compatibility, explains the results, provides career intelligence, and generates actionable recommendations.

* * * * *

3\. Current Development Phase
=============================

Current phase:

`Phase 1 --- Foundation and Architecture`

Phase 1 is complete.

The project has intentionally not yet implemented the advanced NLP, machine-learning, semantic matching, XAI, or recommendation pipeline.

Do not skip directly into advanced implementation without establishing the next phase's requirements.

* * * * *

4\. Current Repository Location
===============================

Project root:

`/Users/raghuviranturkar/SkillLens`

Backend:

`/Users/raghuviranturkar/SkillLens/backend`

Frontend:

`/Users/raghuviranturkar/SkillLens/frontend`

Python virtual environment:

`/Users/raghuviranturkar/SkillLens/skilllens`

* * * * *

5\. Python Environment
======================

Python environment was created using:

`/opt/homebrew/bin/python3.12`

Verified Python version:

`Python 3.12.13`

The active project Python executable is:

`/Users/raghuviranturkar/SkillLens/skilllens/bin/python`

The virtual environment directory is excluded from Git.

Do not create a second project virtual environment unless there is a documented reason.

* * * * *

6\. Frontend Environment
========================

Current Node.js version:

`22.14.0`

Current npm version:

`10.9.2`

Frontend stack:

-   React

-   TypeScript

-   Vite

Current frontend dependencies were installed successfully.

* * * * *

7\. Git Status and Repository
=============================

Git version:

`2.50.1`

Current branch:

`main`

Remote repository:

`https://github.com/raghuviranturkar/SkillLens.git`

The GitHub repository was created and the remote was configured.

At the current recorded state, the repository has not yet been pushed with the complete Phase 1 implementation.

Before committing or pushing, inspect:

-   `git status`

-   `.gitignore`

-   generated files

-   project documentation

-   dependency files

* * * * *

8\. Backend Architecture
========================

Backend follows a modular monolith.

Primary dependency direction:

`API → Orchestration → Domain → Infrastructure`

The backend must not evolve into a collection of unrelated services.

The Analysis Orchestrator is the central workflow coordinator.

* * * * *

9\. Canonical Analytical Engines
================================

The project has one canonical engine for each major analytical responsibility:

1.  `DocumentProcessor`

2.  `SkillExtractor`

3.  `SkillNormalizer`

4.  `SemanticMatcher`

5.  `GapAnalyzer`

6.  `ScoreEngine`

7.  `XAIEngine`

8.  `CareerIntelligenceEngine`

9.  `RecommendationEngine`

These responsibilities must not be duplicated across multiple modules.

* * * * *

10\. Engine Interaction Rule
============================

Analytical engines must not directly call one another.

Incorrect:

`SkillExtractor → SkillNormalizer → SemanticMatcher → GapAnalyzer`

Correct architectural pattern:

`AnalysisOrchestrator`

coordinates:

`DocumentProcessor`

then:

`SkillExtractor`

then:

`SkillNormalizer`

then:

`SemanticMatcher`

then:

`GapAnalyzer`

then:

`ScoreEngine`

then:

`XAIEngine`

then:

`CareerIntelligenceEngine`

then:

`RecommendationEngine`

The exact execution path may vary by analysis mode and available data, but the orchestrator remains responsible for coordination.

* * * * *

11\. Analysis Modes
===================

SkillLens supports two analysis modes.

RESUME_ONLY
-----------

Input:

-   resume

Purpose:

Understand and analyze the candidate profile.

Resume-only analysis may produce:

-   candidate profile

-   extracted skills

-   normalized skills

-   experience information

-   domains

-   career signals

-   strengths

-   potential roles

-   skill priorities

-   recommendations

Resume-only analysis must not fabricate:

-   job-specific match scores

-   missing job skills

-   candidate-job compatibility

-   job-specific skill gaps

* * * * *

RESUME_JD
---------

Input:

-   resume

-   job description

Purpose:

Compare the candidate against a specific role.

May produce:

-   resume profile

-   job profile

-   skill matches

-   skill gaps

-   compatibility score

-   dimension scores

-   explanations

-   career intelligence

-   recommendations

* * * * *

12\. Canonical AnalysisResult
=============================

`AnalysisResult` is the single source of truth for a completed analysis.

It contains:

-   analysis ID

-   schema version

-   analysis mode

-   status

-   creation timestamp

-   input

-   resume profile

-   optional job profile

-   skill analysis

-   scoring

-   XAI

-   career intelligence

-   recommendations

-   metadata

The frontend must ultimately consume this canonical result through the API.

* * * * *

13\. Scoring Ownership
======================

`ScoreEngine` owns official scoring.

No other engine should independently calculate an alternative official compatibility score.

Public score:

`0--100`

Internal calculations may use:

`0--1`

Scoring should be deterministic, transparent, configurable, and testable.

* * * * *

14\. XAI Ownership
==================

`XAIEngine` owns explainability.

XAI explains existing analytical outputs.

It must not independently redefine:

-   skill matches

-   gaps

-   official scores

-   recommendations

Primary planned explainability approach:

`SHAP`

Possible alternative:

`LIME`

* * * * *

15\. Recommendation Ownership
=============================

`RecommendationEngine` owns recommendation generation.

Recommendations should be connected to:

-   detected gaps

-   evidence

-   priorities

-   expected impact

-   effort

-   confidence

Other engines may provide information used by the recommendation engine but must not create competing recommendation systems.

* * * * *

16\. Confidence Standard
========================

Canonical confidence score:

`0--1`

Confidence includes:

-   score

-   level

-   components

-   rationale

The same convention should be maintained throughout the backend and frontend.

* * * * *

17\. Current Backend Files
==========================

Current backend foundation includes:

`backend/app/main.py`

`backend/app/api/routes/health.py`

`backend/app/api/routes/analyses.py`

`backend/app/core/config.py`

`backend/app/core/exceptions.py`

`backend/app/core/logging.py`

`backend/app/domain/analysis.py`

`backend/app/domain/career.py`

`backend/app/domain/confidence.py`

`backend/app/domain/evidence.py`

`backend/app/domain/gaps.py`

`backend/app/domain/job.py`

`backend/app/domain/matching.py`

`backend/app/domain/recommendations.py`

`backend/app/domain/resume.py`

`backend/app/domain/scoring.py`

`backend/app/domain/skill.py`

`backend/app/domain/xai.py`

`backend/app/schemas/requests.py`

`backend/app/schemas/responses.py`

`backend/app/schemas/errors.py`

`backend/app/orchestration/analysis_orchestrator.py`

* * * * *

18\. Important Current Backend Limitation
=========================================

The analytical engine implementations are not yet complete.

The following files are planned but not yet implemented:

-   `document_processor.py`

-   `skill_extractor.py`

-   `skill_normalizer.py`

-   `semantic_matcher.py`

-   `gap_analyzer.py`

-   `score_engine.py`

-   `xai_engine.py`

-   `career_engine.py`

-   `recommendation_engine.py`

Do not state that these engines are already functional.

* * * * *

19\. Current API
================

API prefix:

`/api/v1`

Current endpoints:

`GET /api/v1/health`

`POST /api/v1/analyses/resume`

`POST /api/v1/analyses/resume-jd`

`GET /api/v1/analyses/{analysis_id}`

`DELETE /api/v1/analyses/{analysis_id}`

* * * * *

20\. Current API Behavior
=========================

The health endpoint is functional.

The analysis endpoints currently exist as contracts but do not execute the real analytical pipeline.

They currently return:

`ANALYSIS_NOT_IMPLEMENTED`

This is intentional because Phase 1 established the API contract before implementing the analytical system.

Do not replace the API contract with an ad-hoc design.

* * * * *

21\. Current Frontend Files
===========================

Current important frontend files include:

`frontend/src/main.tsx`

`frontend/src/app/App.tsx`

`frontend/src/state/analysisState.ts`

`frontend/src/types/analysis.ts`

`frontend/src/types/api.ts`

The frontend currently contains a minimal application shell.

The production UI will be implemented in later phases.

* * * * *

22\. Frontend Type Contract
===========================

The frontend already contains TypeScript representations of the canonical backend analysis structures.

Important types include:

-   `AnalysisResult`

-   `ResumeProfile`

-   `JobProfile`

-   `Skill`

-   `Evidence`

-   `SkillMatch`

-   `SkillGap`

-   `ScoringResult`

-   `XAIResult`

-   `CareerIntelligence`

-   `Recommendation`

Do not create a second incompatible analysis-result structure for individual pages.

* * * * *

23\. Current Frontend State
===========================

`frontend/src/state/analysisState.ts`

Current state statuses:

-   idle

-   submitting

-   loading

-   success

-   error

The state stores:

-   current analysis

-   error information

-   request ID

Future state management should preserve the canonical API contract.

* * * * *

24\. Backend Dependencies
=========================

Current backend dependencies are intentionally minimal:

-   FastAPI

-   Uvicorn

-   Pydantic

-   Pydantic Settings

-   python-multipart

-   pytest

-   pytest-asyncio

-   httpx

Advanced ML/NLP dependencies have not yet been installed.

These include:

-   transformers

-   sentence-transformers

-   torch

-   spaCy

-   SHAP

-   LIME

-   scikit-learn

-   NumPy

-   pandas

-   PyMuPDF

-   python-docx

Install advanced dependencies only when required by the corresponding implementation phase.

* * * * *

25\. Planned NLP/ML Stack
=========================

The planned analytical stack includes:

-   transformer-based NLP

-   Sentence Transformers

-   semantic embeddings

-   ESCO or another validated skills taxonomy

-   hybrid keyword + semantic + taxonomy matching

-   SHAP-based explainability

-   optional LIME alternative

-   local/open-source LLM through Ollama or an equivalent approach

Initial semantic embedding candidate:

`all-MiniLM-L6-v2`

The final model should be selected through evaluation rather than assumed to be optimal.

* * * * *

26\. LLM Boundary
=================

The LLM must not become the primary semantic similarity engine.

Semantic similarity should be handled through a deterministic embedding/matching pipeline.

The LLM may later be used for tasks such as:

-   natural-language explanation

-   summarization

-   recommendation phrasing

-   conversational assistance

The LLM should not silently replace the canonical analytical engines.

* * * * *

27\. Document Processing Plan
=============================

Planned supported document types:

-   PDF

-   DOCX

The DocumentProcessor should provide a normalized representation to downstream components.

Document parsing must preserve evidence and source information wherever possible.

* * * * *

28\. Evidence Requirement
=========================

Important analytical conclusions should be traceable to source evidence.

Evidence may include:

-   source document

-   section

-   extracted text

-   offsets

-   evidence type

-   extractor

-   relevance

-   confidence

Evidence is important for both XAI and academic evaluation.

* * * * *

29\. Testing Strategy
=====================

Testing is divided into:

-   unit tests

-   integration tests

-   API tests

-   evaluation tests

-   regression tests

The project should not rely only on manual testing.

Analytical components require both functional tests and quality evaluation.

* * * * *

30\. Current Backend Test Status
================================

Command:

`python -m pytest backend/tests -q`

Current recorded result:

`9 passed`

There are two non-blocking dependency-related warnings associated with the current test setup.

Do not change dependency versions solely to eliminate warnings without checking compatibility.

* * * * *

31\. Current Frontend Verification
==================================

Lint:

`npm run lint`

Result:

PASS

Build:

`npm run build`

Result:

PASS

The frontend currently compiles successfully.

* * * * *

32\. Current Backend Compilation
================================

Command:

`python -m compileall -q backend`

Result:

PASS

* * * * *

33\. Architecture Verification
==============================

Dependency-direction verification:

`NONE`

Duplicate module-name verification:

`NONE`

These checks should remain clean after future modifications.

* * * * *

34\. Phase 1 Completion Criteria
================================

Phase 1 successfully established:

-   repository structure

-   backend architecture

-   frontend architecture

-   domain contracts

-   API contracts

-   frontend type contracts

-   orchestrator interface

-   test structure

-   configuration

-   exception handling

-   logging

-   documentation

-   validation workflow

Phase 1 does not include the complete AI/NLP analytical pipeline.

* * * * *

35\. Immediate Next Step
========================

The next development phase should begin by defining the implementation boundary and tests for the first real analytical capability.

Before writing advanced implementation code:

1.  Read the project documentation.

2.  Inspect the current repository.

3.  Confirm the Phase 1 validation results.

4.  Identify the exact next phase objective.

5.  Define the relevant interfaces.

6.  Define tests before or alongside implementation.

7.  Implement only the agreed scope.

8.  Run validation.

9.  Update `PROJECT_STATUS.md`.

10. Update `CHANGELOG.md`.

11. Update `SESSION_HANDOFF.md`.

Do not implement unrelated future features during the phase.

* * * * *

36\. AI-Assisted Development Protocol
=====================================

When continuing development with an AI coding assistant, provide this context before requesting implementation.

The AI should understand:

-   this is SkillLens

-   Phase 1 is complete

-   architecture is frozen unless explicitly changed

-   implementation is incremental

-   no duplicate engines

-   no direct engine-to-engine calls

-   AnalysisOrchestrator coordinates workflow

-   AnalysisResult is canonical

-   ScoreEngine owns scoring

-   XAIEngine owns explainability

-   RecommendationEngine owns recommendations

-   evidence must be preserved

-   resume-only must not fabricate job-specific results

The AI must inspect existing files before creating new ones.

* * * * *

37\. Rules for Future Changes
=============================

Before creating a new module, ask:

`Does an existing canonical module already own this responsibility?`

If yes:

Modify or extend the existing module.

Do not create a second implementation.

Before adding a dependency, ask:

`Is this dependency necessary for the current phase?`

If no:

Do not add it yet.

Before changing a domain structure, check:

-   `DATA_SCHEMA.md`

-   backend domain models

-   frontend TypeScript models

-   `API_CONTRACT.md`

Before changing an API endpoint, check:

-   API contract

-   backend route

-   frontend API types

-   tests

* * * * *

38\. What Must Not Happen
=========================

Do not:

-   introduce microservices

-   introduce Redis without a real requirement

-   introduce Celery without a real requirement

-   introduce Kafka

-   introduce Kubernetes

-   create duplicate scoring logic

-   create duplicate recommendation logic

-   allow engines to directly call each other

-   put analytical algorithms inside API routes

-   put backend algorithms inside React components

-   fabricate job-specific results in resume-only mode

-   use an LLM as a replacement for semantic matching

-   add large dependencies without justification

-   implement multiple future phases simultaneously

-   rewrite working architecture unnecessarily

* * * * *

39\. Expected Development Style
===============================

Development should be incremental and verifiable.

Preferred sequence:

`Design → Contract → Implementation → Test → Verification → Documentation`

Each phase should end with a known, reproducible repository state.

Avoid large uncontrolled changes across backend, frontend, ML, and infrastructure simultaneously.

* * * * *

40\. Documentation Update Rule
==============================

Whenever a meaningful implementation change is completed, update the appropriate documentation.

At minimum:

`PROJECT_STATUS.md`

`CHANGELOG.md`

If architecture or contracts change, also update:

`ARCHITECTURE.md`

`API_CONTRACT.md`

`DATA_SCHEMA.md`

If repository structure changes, update:

`CODEBASE_MAP.md`

At the end of a development session, update:

`SESSION_HANDOFF.md`

* * * * *

41\. Current Known Warnings
===========================

Backend tests currently produce two non-blocking warnings related to the test client/dependency ecosystem.

These warnings do not currently cause test failure.

They should be reviewed during dependency maintenance rather than treated as Phase 1 blockers.

* * * * *

42\. Current Known Limitations
==============================

The following limitations are expected at this stage:

-   no real document parsing

-   no real skill extraction

-   no semantic embedding pipeline

-   no ESCO integration

-   no skill matching implementation

-   no gap-analysis implementation

-   no scoring implementation

-   no XAI implementation

-   no career intelligence implementation

-   no recommendation implementation

-   no persistent analysis storage

-   minimal frontend UI

These are planned development tasks, not architectural failures.

* * * * *

43\. Session Continuation Checklist
===================================

At the beginning of a new session:

-   Read `PROJECT_MASTER.md`

-   Read `PROJECT_STATUS.md`

-   Read `ARCHITECTURE.md`

-   Read `API_CONTRACT.md`

-   Read `DATA_SCHEMA.md`

-   Read `CODEBASE_MAP.md`

-   Read this file

-   Inspect Git status

-   Inspect current repository structure

-   Confirm current phase

-   Confirm the exact task before coding

Before ending the session:

-   Run backend compilation

-   Run backend tests

-   Run frontend lint

-   Run frontend build

-   Review changed files

-   Update project status

-   Update changelog

-   Update session handoff

-   Record unresolved issues

-   Record the exact next task

* * * * *

44\. Current Handoff State
==========================

Project:

`SkillLens`

Phase:

`Phase 1 --- Foundation and Architecture`

Status:

`Complete`

Architecture:

`Established and frozen`

Backend:

`Foundation complete`

Frontend:

`Foundation complete`

API:

`Contracts established`

Domain:

`Canonical structures established`

Analytical engines:

`Planned, not yet implemented`

Testing:

`Passing`

Documentation:

`Foundation documentation established`

Immediate direction:

`Begin the next implementation phase incrementally, starting with the first approved analytical capability.`

* * * * *

SkillLens --- Phase 2 Session Handoff
===================================

Current State
-------------

**Project:** SkillLens

**Phase:** Phase 2 --- Document Processing

**Phase 1:** Complete and frozen

**Phase 2:** Implementation complete; final freeze pending

Phase 2 Completed
-----------------

The document-processing infrastructure is implemented under:

`backend/app/infrastructure/parsers/`

Implemented:

-   Parser abstraction

-   PDF parser

-   DOCX parser

-   Document validation

-   Document processor

-   Normalized document models

-   Source provenance

-   Parser contract tests

Supported Formats
-----------------

-   PDF

-   DOCX

Normalized Output
-----------------

The parser layer produces:

`ParsedDocument`

containing:

-   document identifier

-   document type

-   normalized blocks

-   document metadata

Each block contains source-location information where available.

Verification
------------

Latest verification:

-   Backend: **70 passed**

-   Parsed-document contract tests: **8 passed**

-   Python compilation: **passed**

-   API route inspection: **passed**

-   OpenAPI verification: **passed**

-   Frontend TypeScript: **passed**

-   Frontend production build: **passed**

-   `git diff --check`: **passed**

-   Temporary `tmp/` directory: **removed**

API Boundary
------------

The Phase 1 analysis API remains unchanged.

The following endpoints remain intentionally non-implemented:

```
POST /api/v1/analyses/resume
POST /api/v1/analyses/resume-jd
GET  /api/v1/analyses/{analysis_id}

```

They continue to return the controlled Phase 1 `501 Not Implemented` behavior.

Phase 2 does not wire the parser directly into these endpoints because doing so would cross the Phase 2 boundary into downstream resume/JD extraction and analytical processing.

Important Architectural Rule
----------------------------

Do not make the parser layer perform:

-   Skill extraction

-   Semantic matching

-   Scoring

-   XAI

-   Recommendations

-   Career intelligence

-   LLM analysis

The parser output is the handoff boundary for future phases.

Next Phase
----------

The next phase has **not started**.

Before starting the next phase:

1.  Complete final Phase 2 repository verification.

2.  Create the initial Git baseline/freeze commit.

3.  Review the Phase 2 documentation.

4.  Create the next-phase development plan.

5.  Begin implementation only after the next phase is explicitly authorized.

Development Workflow
--------------------

All future implementation must follow:

```
READ
→ INSPECT
→ PLAN
→ IMPLEMENT
→ TEST
→ INTEGRATE
→ VERIFY
→ FREEZE

```

Do not begin the next analytical phase automatically.

 Final Instruction for the Next AI Session
==============================================

Do not assume that planned components are already implemented.

First inspect the actual repository.

Treat the documented architecture and contracts as the source of truth.

Do not redesign the system unless explicitly instructed.

Do not jump ahead to later phases.

Implement only the current approved task, verify it thoroughly, and update the project documentation before moving forward.

