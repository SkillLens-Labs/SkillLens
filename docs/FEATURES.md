SkillLens --- Features
====================

1\. Document Purpose
--------------------

This document is the canonical feature inventory for SkillLens.

It records:

-   Features implemented in each development phase

-   Features currently available in the codebase

-   Known limitations of implemented features

-   Features intentionally deferred to later phases

-   The current boundary between completed and planned functionality

The feature status described here reflects the current repository implementation and should be updated whenever a phase introduces or changes functionality.

* * * * *

2\. Project Feature Overview
============================

SkillLens is an explainable semantic skill-gap analysis platform designed to process resumes and, in later phases, compare candidate skills against job requirements.

The planned end-to-end system is:

Resume / Job Description\
→ Document Processing\
→ Structure Interpretation\
→ Skill Extraction\
→ Skill Normalization\
→ ESCO Mapping\
→ Evidence Linking\
→ Confidence Estimation\
→ Canonical ResumeProfile\
→ JobProfile\
→ Semantic Matching\
→ Skill Gap Analysis\
→ Scoring\
→ XAI\
→ Career Intelligence\
→ Recommendations

The current implementation has completed the document-processing layer and the resume-intelligence layer.

Resume-to-job matching and downstream intelligence remain deferred.

* * * * *

3\. Feature Status Legend
=========================

IMPLEMENTED\
Feature is implemented and covered by the current codebase/tests.

IMPLEMENTED WITH LIMITATIONS\
Feature is implemented, but has a documented scope or technical limitation.

DEFERRED\
Feature is planned but intentionally not implemented in the current phase.

NOT STARTED\
Feature is part of the long-term architecture but development has not yet begun.

* * * * *

4\. Phase 1 --- Project Foundation
================================

Implemented
-----------

### Project Architecture

-   Modular monolith architecture

-   Backend/frontend separation

-   Layered backend structure

-   Domain-oriented analysis package

-   API route structure

-   Infrastructure package

-   Configuration foundation

-   Environment configuration foundation

### Backend Foundation

-   FastAPI application foundation

-   Application entry point

-   API versioning structure

-   Health-check endpoint

-   Error-handling foundation

-   Logging/configuration foundation

### Frontend Foundation

-   React application

-   Vite-based frontend

-   Routing foundation

-   API service layer

-   Authentication page structure

-   Dashboard/page scaffolding

-   Reusable UI/component structure

### Analysis Foundation

The initial analysis architecture established the planned locations and contracts for:

-   Resume analysis

-   Job-description analysis

-   Skill representation

-   Matching

-   Gap analysis

-   Scoring

-   Explainability

-   Career intelligence

-   Recommendations

The downstream analytical engines were reserved for later phases rather than implemented prematurely.

### Data and Domain Foundation

-   Canonical domain package structure

-   Resume domain model foundation

-   Job domain model foundation

-   Skill domain model foundation

-   Analysis result foundation

-   Evidence model foundation

-   Confidence model foundation

-   Matching model foundation

-   Scoring model foundation

-   XAI model foundation

* * * * *

5\. Phase 2 --- Document Processing
=================================

Implemented
-----------

### File Validation

-   PDF upload-content validation

-   DOCX upload-content validation

-   File type detection

-   MIME/content-type validation

-   File signature validation

-   File size validation

-   Empty document detection

### PDF Processing

-   PDF text extraction

-   PDF page provenance

-   PDF document identification

-   PDF block generation

### DOCX Processing

-   DOCX paragraph extraction

-   DOCX heading recognition

-   DOCX list/bullet recognition

-   DOCX table extraction

-   DOCX paragraph provenance

-   DOCX table provenance

-   DOCX document identification

### Normalized Document Representation

-   `ParsedDocument`

-   `DocumentBlock`

-   `SourceLocation`

-   Document type representation

-   Document metadata

-   Document block classification

-   Source provenance

### Parser Architecture

-   Abstract `DocumentParser` interface

-   PDF parser

-   DOCX parser

-   Parser validation layer

-   Unified `DocumentProcessor`

-   Parser selection based on document type

-   Consistent normalized output across supported document formats

Phase 2 Boundary
----------------

Phase 2 establishes the frozen document-processing boundary:

`Uploaded File → DocumentProcessor → ParsedDocument`

Later analysis phases consume `ParsedDocument` rather than reparsing PDF or DOCX files.

* * * * *

6\. Phase 3 --- Resume Intelligence
=================================

Phase 3 extends the Phase 2 normalized document representation into a canonical resume representation.

The implemented pipeline is:

`ParsedDocument`\
→ `ResumeStructureInterpreter`\
→ `SkillExtractor`\
→ `SkillNormalizer`\
→ `ESCOMapper`\
→ `ResumeProfileBuilder`\
→ `ResumeProfile`

* * * * *

6.1 Resume Structure Interpretation
-----------------------------------

### Implemented

-   Resume section interpretation

-   Section type classification

-   Heading alias recognition

-   Section grouping

-   Preservation of document block order

-   Preservation of source provenance

-   Resume document identity preservation

Supported semantic section types include:

-   Header

-   Summary

-   Experience

-   Education

-   Projects

-   Certifications

-   Skills

-   Unknown

### Implementation

`backend/app/analysis/resume_structure.py`

### Limitation

Structure interpretation operates on the semantic information already exposed by `ParsedDocument`.

For example, DOCX heading metadata can be interpreted as resume section headings. The current frozen PDF parser does not infer arbitrary visual headings from PDF text blocks, so PDFs whose headings are parsed only as paragraphs may not receive semantic section classification.

This limitation belongs to the current Phase 2 PDF parsing boundary and is not addressed by reparsing documents in Phase 3.

* * * * *

6.2 Skill Extraction
====================

### Implemented

-   Deterministic skill extraction

-   Known skill vocabulary

-   Explicit skill extraction from Skills sections

-   Skill extraction from Certifications sections

-   Contextual skill extraction from:

    -   Summary

    -   Experience

    -   Projects

    -   Education

-   Duplicate skill mentions

-   Raw skill mention preservation

-   Source block provenance

-   Character offsets

-   Extraction confidence

-   Evidence type classification

### Skill Evidence Types

-   Explicit

-   Contextual

### Implementation

`backend/app/analysis/skill_extractor.py`

### Scope

The current implementation is deterministic and vocabulary-based.

Transformer-based extraction has not yet been introduced.

* * * * *

6.3 Skill Normalization
=======================

### Implemented

-   Unicode NFKC normalization

-   Whitespace normalization

-   Case normalization

-   Canonical skill names

-   Alias resolution

-   Raw mention preservation

-   Extraction-confidence preservation

-   Duplicate canonical-name handling

Examples of normalized aliases include:

-   Py → Python

-   python programming → Python

-   python3 → Python

-   JS → JavaScript

-   ReactJS → React

-   React.js → React

-   Postgres → PostgreSQL

-   Mongo → MongoDB

-   sklearn → scikit-learn

-   ML → Machine Learning

-   PowerBI → Power BI

### Implementation

`backend/app/analysis/skill_normalizer.py`

### Purpose

Normalization ensures that equivalent skill mentions can be represented using a single canonical skill identity before downstream mapping and analysis.

* * * * *

6.4 ESCO Mapping
================

### Implemented

-   ESCO mapping abstraction

-   ESCO version tracking

-   Candidate generation

-   MAPPED status

-   AMBIGUOUS status

-   UNMAPPED status

-   Mapping confidence

-   Mapping method metadata

-   Ordered batch mapping

### Current ESCO Version

ESCO version used by the Phase 3 adapter:

`1.2.1`

### Current Mapping Scope

The current implementation contains a small deterministic adapter vocabulary for selected normalized skills.

Known mapped examples include:

-   Python

-   Java

-   JavaScript

-   SQL

-   React

-   Docker

-   Kubernetes

-   Machine Learning

-   Data Analysis

Some skills, such as FastAPI, currently remain unmapped.

### Important Boundary

The current ESCO mapper is an adapter abstraction and not a complete local copy of the ESCO skills dataset.

The architecture is designed so that the mapper can later be connected to the official ESCO dataset/API without changing the downstream resume-profile contract.

No fabricated ESCO identifiers are used for currently unmapped skills.

### Implementation

`backend/app/analysis/esco_mapper.py`

* * * * *

6.5 Evidence Linking
====================

### Implemented

Skill evidence is retained throughout the Phase 3 pipeline.

Each extracted skill can retain:

-   Raw mention

-   Canonical skill name

-   Evidence type

-   Source document

-   Source location

-   Block provenance

-   Character offsets

-   Extraction confidence

-   Mapping information

-   Mapping confidence

Evidence identifiers are generated deterministically using the skill identity, mention offsets, and source information so that separate mentions in different document blocks remain distinguishable.

Evidence is therefore available for future explainability and skill-gap analysis.

* * * * *

6.6 Confidence Estimation
=========================

### Implemented

Phase 3 combines extraction and ESCO mapping confidence into a normalized skill confidence.

Confidence levels are represented as:

-   HIGH

-   MEDIUM

-   LOW

The current confidence behavior distinguishes between:

-   Successfully mapped skills

-   Ambiguous mappings

-   Unmapped skills

The implementation intentionally does not treat an unmapped skill as nonexistent. An extracted skill can remain part of the canonical resume profile even when no ESCO mapping is available.

* * * * *

6.7 ResumeProfile Construction
==============================

### Implemented

The Phase 3 pipeline constructs a canonical resume profile from the normalized analysis results.

The profile can contain:

-   Resume/profile identifier

-   Skills

-   Canonical skill names

-   Skill categories

-   Skill evidence

-   Skill confidence

-   ESCO mapping metadata

-   Document metadata

-   Builder metadata

-   ESCO version metadata

### Duplicate Handling

Repeated mentions of the same canonical skill are merged into one canonical skill entry while preserving separate evidence records.

Example:

Python mentioned in two different resume locations

→ one canonical `python` skill

→ two evidence records

### Important Principle

The profile builder does not invent resume facts that were not extracted.

Fields requiring richer semantic interpretation, such as detailed employment history, total experience, seniority, or domain inference, remain unset when sufficient evidence is unavailable.

### Implementation

`backend/app/analysis/resume_profile_builder.py`

* * * * *

7\. Phase 3 Testing
===================

Phase 3 includes dedicated unit and integration tests.

Unit Tests
----------

Covered components include:

-   Resume structure interpretation

-   Skill extraction

-   Skill normalization

-   ESCO mapping

-   Resume profile construction

Integration Testing
-------------------

The Phase 3 integration pipeline verifies:

`ParsedDocument`\
→ Structure Interpretation\
→ Skill Extraction\
→ Normalization\
→ ESCO Mapping\
→ ResumeProfile

Real Document Verification
--------------------------

Real PDF and DOCX fixtures are included for verification.

DOCX verification covers the complete Phase 3 resume pipeline.

PDF verification confirms real PDF parsing and document extraction, while semantic section interpretation remains limited by the current PDF parser's block classification behavior.

Regression Status
-----------------

Current backend test suite:

`115 passed, 7 warnings`

Command:

`PYTHONPATH=. pytest backend/tests -q`

The warnings are dependency deprecation warnings and do not represent test failures.

* * * * *

8\. Frontend Features
=====================

Phase 1 established the frontend foundation and page structure.

Current frontend structure includes pages/components for areas such as:

-   Dashboard

-   Upload

-   Analysis

-   Visualizations

-   Models

-   Explainability

-   AI Insights

-   Assistant

-   Reports

-   Settings

-   Profile

-   Workspaces

-   Login

-   Register

The frontend structure is intended to support the complete SkillLens product.

However, the completed Phase 3 work is primarily backend resume intelligence. The frontend has not yet been redesigned or fully integrated with the Phase 3 analysis pipeline.

Frontend analytical experiences should therefore be considered planned/integration-stage functionality rather than evidence that the corresponding backend analytical engine is complete.

* * * * *

9\. Public API Feature Status
=============================

Implemented
-----------

-   Health-check endpoint

-   API routing foundation

-   Versioned API structure

Defined but Not Yet Implemented
-------------------------------

The following analysis API contracts exist architecturally but are not yet backed by the completed analysis orchestration layer:

-   Resume analysis

-   Resume + job-description analysis

-   Analysis retrieval

-   Analysis deletion

The public analysis routes must not be considered production-ready until the Phase 3/Phase 4+ engines are connected through the canonical `AnalysisOrchestrator`.

* * * * *

10\. Features Intentionally Deferred
====================================

The following capabilities are not part of the completed Phase 3 scope.

Job Description Intelligence
----------------------------

-   Job-description structure interpretation

-   Job-description skill extraction

-   JobProfile construction

-   Job requirement normalization

-   Job requirement ESCO mapping

Semantic Matching
-----------------

-   Resume-JD semantic similarity

-   Transformer embeddings

-   Embedding generation

-   Semantic skill matching

-   Hybrid lexical + semantic matching

-   Skill equivalence detection

-   Match explanation

Skill Gap Analysis
------------------

-   Required-skill vs candidate-skill comparison

-   Missing skill detection

-   Partial skill detection

-   Skill-gap categorization

-   Skill-gap severity

-   Skill-gap scoring

Candidate Scoring
-----------------

-   Overall match score

-   Skill coverage score

-   Experience score

-   Education score

-   Weighted candidate-job scoring

-   Ranking

Explainable AI
--------------

-   XAI scoring engine

-   Feature contribution analysis

-   Match-score explanations

-   Skill-gap explanations

-   Evidence-based final explanations

-   SHAP or equivalent model explanations where appropriate

Career Intelligence
-------------------

-   Career trajectory analysis

-   Role recommendations

-   Career transition analysis

-   Career readiness analysis

Recommendations
---------------

-   Skill improvement recommendations

-   Learning-path recommendations

-   Course/resource recommendations

-   Personalized development plans

LLM Integration
---------------

-   Ollama integration

-   LLM-based recommendation generation

-   LLM-based explanation generation

-   LLM-based career intelligence

These capabilities remain intentionally deferred and must not be implemented as part of the frozen Phase 3 scope.

* * * * *

11\. Planned Phase 4
====================

The next planned development phase is:

`Phase 4 --- Resume Quality & ATS Intelligence`

Potential scope includes:

-   Resume quality analysis

-   ATS-oriented checks

-   Resume completeness

-   Formatting/content quality signals

-   Section completeness

-   Resume-level diagnostics

-   Quality-oriented explainability

Phase 4 should build on the canonical `ResumeProfile` and Phase 2 `ParsedDocument` boundaries rather than introducing duplicate parsing or resume representations.

Phase 4 should not begin until Phase 3 has been formally accepted and documented.

* * * * *

12\. Feature Boundaries
=======================

The following boundaries are considered architectural invariants.

Document Processing Boundary
----------------------------

`Uploaded File → DocumentProcessor → ParsedDocument`

Phase 3 does not reparse PDF/DOCX files.

Resume Intelligence Boundary
----------------------------

`ParsedDocument → Resume Structure → Skills → Normalization → ESCO → Evidence/Confidence → ResumeProfile`

Future Matching Boundary
------------------------

`ResumeProfile + JobProfile → Matching → Gap Analysis → Scoring → XAI`

Future Intelligence Boundary
----------------------------

`AnalysisResult → Career Intelligence → Recommendations`

Each boundary should have one canonical implementation.

* * * * *

13\. Current Feature State
==========================

At the completion of Phase 3:

IMPLEMENTED:

-   Project foundation

-   Backend architecture

-   Frontend foundation

-   PDF/DOCX document validation

-   PDF/DOCX document parsing

-   Normalized document representation

-   Document provenance

-   Resume structure interpretation

-   Deterministic skill extraction

-   Skill normalization

-   ESCO mapping adapter

-   Evidence linking

-   Confidence estimation

-   Canonical ResumeProfile construction

-   Phase 3 unit tests

-   Phase 3 integration tests

-   Real PDF/DOCX verification

IMPLEMENTED WITH LIMITATIONS:

-   PDF semantic section interpretation

-   Partial ESCO mapping through the current adapter vocabulary

-   Deterministic vocabulary-based skill extraction

-   Resume profile fields that require richer semantic interpretation

DEFERRED:

-   Transformer-based skill extraction

-   Complete ESCO dataset integration

-   Job-description intelligence

-   Embeddings

-   Semantic matching

-   Hybrid matching

-   Skill-gap analysis

-   Candidate-job scoring

-   XAI scoring/explanation engine

-   Career intelligence

-   Recommendations

-   LLM integration

-   Full public analysis orchestration

-   Phase 4 ATS/resume-quality intelligence

* * * * *

14\. Current Baseline
=====================

Current completed Phase 3 commit:

`0b73efe Complete Phase 3 resume intelligence pipeline`

The repository is clean after the Phase 3 commit.

The current feature baseline should be treated as the reference point for the next development phase.
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

Phase 6 --- Candidate-Job Scoring, Skill Gap Analysis & XAI
---------------------------------------------------------

**Status: COMPLETE / FROZEN**

Phase 6 adds the final deterministic analytical layer for Resume + Job Description analysis.

### Candidate-Job Scoring

The system now provides:

-   deterministic overall candidate-job scoring

-   required skill scoring

-   preferred skill scoring

-   experience scoring

-   education scoring

-   domain scoring

-   explicit dimension weights

-   UNKNOWN-aware scoring

-   score contribution decomposition

### Skill Gap Analysis

The system identifies requirement-linked:

-   matched requirements

-   partial matches

-   unmatched requirements

-   unknown requirements

Each detailed gap can preserve:

-   requirement ID

-   requirement type

-   target skill

-   match status

-   similarity

-   rationale

-   evidence

-   confidence

### Explainable AI

The system provides deterministic explanations for:

-   overall score

-   score dimensions

-   score contributions

-   matched skills

-   partial matches

-   missing skills

-   strengths

-   weaknesses

-   supporting evidence

-   confidence

### Compatibility

Phase 6 preserves:

-   Resume-only analysis

-   Resume + JD analysis

-   existing Phase 5 matching

-   existing requirement alignment

-   existing evidence/confidence contracts

Detailed implementation information is maintained in:

`docs/PHASE_6.md`