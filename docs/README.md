SkillLens
=========

XAI-Driven Semantic Skill Gap Analysis using Transformer-Based Language Models
------------------------------------------------------------------------------

SkillLens is an explainable AI platform designed to analyze resumes, extract and normalize professional skills, compare candidate capabilities with job requirements, identify semantic skill gaps, explain analytical results, provide career intelligence, and generate actionable recommendations.

The project combines Natural Language Processing, transformer-based semantic representations, skill taxonomies, explainable AI, and structured analytical pipelines into a modular system.

* * * * *

1\. Project Objective
=====================

The primary objective of SkillLens is to build an intelligent and explainable skill-gap analysis system that can understand professional documents beyond simple keyword matching.

The system is designed to answer questions such as:

-   What skills does a candidate possess?

-   What skills are required for a particular role?

-   Which skills match semantically?

-   Which skills are missing or insufficient?

-   How well does the candidate match the target role?

-   Why was a particular score assigned?

-   What are the candidate's strongest areas?

-   What career directions may fit the candidate?

-   Which skills should the candidate prioritize?

-   What actions can improve the candidate's profile?

The system is designed to provide evidence-backed results rather than unexplained predictions.

* * * * *

2\. Core Workflow
=================

The intended high-level workflow is:

Resume / Job Description

↓

Document Processing

↓

Skill Extraction

↓

Skill Normalization

↓

Semantic Matching

↓

Skill Gap Analysis

↓

Scoring

↓

Explainability

↓

Career Intelligence

↓

Recommendations

↓

Analysis Result

The workflow is coordinated by a single Analysis Orchestrator.

Individual analytical engines do not directly call one another.

* * * * *

3\. Analysis Modes
==================

SkillLens supports two primary modes.

Resume-Only Analysis
--------------------

Input:

-   Resume

The system analyzes the candidate independently.

Possible outputs include:

-   candidate profile

-   extracted skills

-   normalized skills

-   experience level

-   professional domains

-   strengths

-   career signals

-   potential roles

-   skill priorities

-   recommendations

Resume-only mode must not generate fabricated job-specific:

-   compatibility scores

-   missing job skills

-   job-specific skill gaps

-   candidate-job conclusions

* * * * *

Resume + Job Description Analysis
---------------------------------

Input:

-   Resume

-   Job description

The system performs candidate-job comparison.

Possible outputs include:

-   resume profile

-   job profile

-   skill matches

-   semantic relationships

-   skill gaps

-   compatibility score

-   scoring dimensions

-   evidence

-   explanations

-   career intelligence

-   recommendations

* * * * *

4\. Key Features
================

Document Understanding
----------------------

Process professional documents and extract structured information from resumes and job descriptions.

Planned initial document formats:

-   PDF

-   DOCX

* * * * *

Skill Extraction
----------------

Identify technical, professional, domain, and soft skills from unstructured text.

The extraction pipeline may combine:

-   NLP techniques

-   transformer models

-   rules

-   contextual information

-   taxonomy information

* * * * *

Skill Normalization
-------------------

Convert different textual representations into canonical skill identities.

For example:

-   Python

-   Python Programming

-   Python 3

may be normalized to a common canonical skill representation.

* * * * *

Semantic Skill Matching
-----------------------

SkillLens is designed to go beyond exact keyword matching.

Semantic representations allow related concepts to be compared based on meaning.

The planned approach uses transformer-based embeddings combined with other matching signals.

Initial embedding candidate:

`all-MiniLM-L6-v2`

The final model will be selected through evaluation.

* * * * *

Hybrid Matching
---------------

The intended matching system combines multiple signals, including:

-   exact matching

-   normalized matching

-   semantic similarity

-   taxonomy relationships

-   contextual evidence

The objective is to reduce false negatives caused by different terminology describing related capabilities.

* * * * *

Skill Gap Analysis
------------------

The system identifies:

-   missing skills

-   partial matches

-   related skills

-   insufficient proficiency

-   high-priority gaps

Each important gap should be supported by evidence.

* * * * *

Compatibility Scoring
---------------------

The scoring engine calculates an overall compatibility score and supporting dimensions.

The public score uses:

`0--100`

Internal calculations may use:

`0--1`

Possible scoring dimensions include:

-   required skills

-   preferred skills

-   experience

-   education

-   domain alignment

The exact scoring formula will be validated during implementation and evaluation.

* * * * *

Explainable AI
--------------

SkillLens is designed to explain its analytical conclusions.

Explanations may cover:

-   overall score

-   score contributions

-   matched skills

-   missing skills

-   partial matches

-   strengths

-   weaknesses

-   source evidence

Primary planned explainability technology:

`SHAP`

Possible alternative:

`LIME`

Explainability must explain existing analytical outputs rather than independently changing them.

* * * * *

Career Intelligence
-------------------

The system may infer:

-   experience level

-   professional domains

-   career signals

-   strengths

-   potential roles

-   role fit

-   career transition opportunities

-   skill-development priorities

-   potential risks

* * * * *

Personalized Recommendations
----------------------------

Recommendations are generated from identified gaps and candidate context.

Recommendations may include:

-   skills to learn

-   skills to strengthen

-   project suggestions

-   experience-building actions

-   career-development priorities

Each recommendation should have a clear rationale and supporting evidence where available.

* * * * *

5\. Architecture
================

SkillLens uses a modular monolith architecture.

Primary dependency direction:

API

↓

Orchestration

↓

Domain

↓

Infrastructure

The architecture avoids unnecessary distributed-system complexity.

The project does not currently require:

-   microservices

-   Redis

-   Celery

-   Kafka

-   Kubernetes

-   service mesh

Additional infrastructure should only be introduced when justified by an actual requirement.

* * * * *

6\. Canonical Analytical Engines
================================

SkillLens defines one canonical engine for each major responsibility:

-   DocumentProcessor

-   SkillExtractor

-   SkillNormalizer

-   SemanticMatcher

-   GapAnalyzer

-   ScoreEngine

-   XAIEngine

-   CareerIntelligenceEngine

-   RecommendationEngine

The Analysis Orchestrator controls the workflow.

Engines must not directly invoke other engines.

* * * * *

7\. Canonical Analysis Result
=============================

The complete analysis is represented by:

`AnalysisResult`

It contains:

-   analysis ID

-   schema version

-   analysis mode

-   status

-   creation timestamp

-   input information

-   resume profile

-   optional job profile

-   skill analysis

-   scoring

-   XAI

-   career intelligence

-   recommendations

-   metadata

`AnalysisResult` is the single source of truth for the frontend.

* * * * *

8\. Technology Stack
====================

Backend
-------

-   Python

-   FastAPI

-   Pydantic

-   Uvicorn

Frontend
--------

-   React

-   TypeScript

-   Vite

NLP / AI
--------

Planned:

-   Sentence Transformers

-   Transformer models

-   NLP processing

-   ESCO or another validated skill taxonomy

-   SHAP

-   optional LIME

Machine Learning
----------------

Planned:

-   semantic embeddings

-   machine-learning-assisted analysis where justified

-   evaluation and benchmarking

LLM
---

A local or open-source LLM may be integrated later for selected language-generation tasks.

Potential infrastructure:

-   Ollama

-   open-source language models

The LLM is not intended to replace the semantic matching engine.

* * * * *

9\. Repository Structure
========================

```
SkillLens/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── domain/
│   │   ├── schemas/
│   │   ├── orchestration/
│   │   ├── analysis/
│   │   ├── infrastructure/
│   │   └── utils/
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   ├── api/
│   │   ├── evaluation/
│   │   └── fixtures/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── features/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── state/
│   │   ├── types/
│   │   ├── utils/
│   │   └── styles/
│   └── tests/
│
├── PROJECT_MASTER.md
├── PROJECT_STATUS.md
├── ARCHITECTURE.md
├── API_CONTRACT.md
├── DATA_SCHEMA.md
├── CODEBASE_MAP.md
├── CHANGELOG.md
└── SESSION_HANDOFF.md

```

The repository structure represents both currently established modules and planned implementation areas. A directory appearing in the architecture does not necessarily mean that its full implementation already exists.

* * * * *

10\. API
========

Base API path:

`/api/v1`

Current endpoints:

-   `GET /api/v1/health`

-   `POST /api/v1/analyses/resume`

-   `POST /api/v1/analyses/resume-jd`

-   `GET /api/v1/analyses/{analysis_id}`

-   `DELETE /api/v1/analyses/{analysis_id}`

The analysis endpoints currently establish the API contract but do not yet execute the complete analytical pipeline.

* * * * *

11\. Development Status
=======================

Current phase:

`Phase 1 --- Foundation and Architecture`

Phase 1 has established:

-   repository structure

-   backend foundation

-   frontend foundation

-   domain contracts

-   API contracts

-   orchestrator interface

-   testing structure

-   documentation

-   dependency boundaries

Advanced analytical functionality remains planned for subsequent phases.

* * * * *

12\. Validation Status
======================

Backend compilation:

`PASS`

Backend tests:

`9 passed`

Frontend lint:

`PASS`

Frontend build:

`PASS`

OpenAPI route verification:

`PASS`

Dependency-direction verification:

`NONE`

Duplicate module-name verification:

`NONE`

* * * * *

13\. Development Principles
===========================

SkillLens follows these principles:

Single Responsibility
---------------------

Each major analytical responsibility has one canonical owner.

Explicit Ownership
------------------

Scoring, XAI, recommendations, and other major outputs have clearly defined owners.

Evidence-Driven Analysis
------------------------

Important conclusions should be traceable to source evidence.

Explainability
--------------

The system should provide understandable reasons for important analytical outputs.

Reproducibility
---------------

Analytical behavior should be testable and reproducible wherever practical.

Incremental Development
-----------------------

Features are implemented phase by phase rather than all at once.

Contract Stability
------------------

API and domain contracts should remain stable unless a deliberate architectural change is approved.

Minimal Infrastructure
----------------------

Infrastructure should be introduced only when justified.

* * * * *

14\. Testing Strategy
=====================

The project uses multiple testing levels.

Unit Tests
----------

Validate individual components and domain behavior.

Integration Tests
-----------------

Validate interactions between components.

API Tests
---------

Validate HTTP contracts and endpoint behavior.

Evaluation Tests
----------------

Measure the quality of NLP, matching, scoring, explainability, and recommendations.

Regression Tests
----------------

Prevent previously solved problems from returning.

Analytical quality should not be judged solely by whether the software runs successfully.

* * * * *

15\. Academic Evaluation
========================

Because SkillLens is an academic AI project, analytical components should eventually be evaluated using measurable criteria.

Potential evaluation areas include:

-   skill extraction precision

-   skill extraction recall

-   F1 score

-   normalization accuracy

-   semantic matching accuracy

-   false-positive rate

-   false-negative rate

-   gap detection quality

-   scoring consistency

-   explanation quality

-   recommendation relevance

Evaluation datasets and methodology should be documented when the analytical pipeline is implemented.

* * * * *

16\. Security and Reliability Considerations
============================================

The application will process user-provided documents.

Future implementation should consider:

-   file type validation

-   file size limits

-   safe document parsing

-   malicious file handling

-   input sanitization

-   privacy of uploaded documents

-   controlled error responses

-   secure storage

-   removal of temporary files

-   prevention of unintended data exposure

Security mechanisms should be implemented as the relevant functionality is introduced.

* * * * *

17\. AI-Assisted Development
============================

SkillLens is being developed with AI-assisted programming.

AI-generated changes must follow the existing project architecture.

Before modifying the codebase, an AI coding assistant should:

1.  inspect the current repository

2.  read the relevant project documentation

3.  identify the canonical module responsible for the requested functionality

4.  inspect existing implementations

5.  avoid duplicate responsibilities

6.  preserve API and domain contracts

7.  implement only the requested phase

8.  run validation

9.  update documentation

The AI must not assume that planned modules are already implemented.

* * * * *

18\. Phase-Based Development
============================

Development is intentionally divided into phases.

Each phase should have:

-   a defined objective

-   a limited implementation scope

-   explicit completion criteria

-   tests

-   validation

-   documentation updates

-   a session handoff

Large unrelated changes should not be combined into one phase.

* * * * *

19\. Current Phase Boundary
===========================

Phase 1 is complete.

The project should not yet be treated as a functional end-to-end AI skill-gap analyzer.

The following remain future implementation work:

-   document parsing

-   skill extraction

-   skill normalization

-   semantic embeddings

-   semantic matching

-   taxonomy integration

-   gap analysis

-   scoring

-   XAI

-   career intelligence

-   recommendations

-   persistence

-   production frontend

-   LLM integration

-   analytical evaluation

* * * * *

20\. Documentation
==================

The project maintains the following documentation:

`PROJECT_MASTER.md`

Permanent project specification and architectural rules.

`PROJECT_STATUS.md`

Current implementation status and progress.

`ARCHITECTURE.md`

System architecture and dependency rules.

`API_CONTRACT.md`

API endpoints and contracts.

`DATA_SCHEMA.md`

Canonical data structures.

`CODEBASE_MAP.md`

Repository and module responsibilities.

`CHANGELOG.md`

Historical record of significant changes.

`SESSION_HANDOFF.md`

Context required for continuing development in another session.

* * * * *

21\. Contributing
=================

Before making changes:

1.  Read the relevant documentation.

2.  Understand the current phase.

3.  Inspect the existing implementation.

4.  Identify the canonical owner of the functionality.

5.  Make the smallest appropriate change.

6.  Add or update tests.

7.  Run backend and frontend validation.

8.  Update documentation when necessary.

Do not introduce architectural changes casually.

* * * * *

22\. Current Project Goal
=========================

The immediate goal is to move from the completed architectural foundation into incremental implementation of the actual SkillLens analytical pipeline.

The next phase should be implemented deliberately and validated before progressing to subsequent capabilities.

The long-term goal is a robust, explainable, academically defensible, and practically useful semantic skill-gap analysis platform.