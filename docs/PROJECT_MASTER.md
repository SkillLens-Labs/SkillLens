SkillLens --- Project Master
==========================

1\. Project Identity
--------------------

**Project Name:** SkillLens

**Project Title:** XAI-Driven Semantic Skill Gap Analysis using Transformer-Based Language Models

**Project Type:** Academic software engineering and research project

**Primary Objective:**

Build an explainable semantic skill-gap analysis platform that analyzes candidate resumes, optionally compares them with job requirements, identifies semantic skill matches and gaps, explains analytical results, and produces actionable career recommendations.

* * * * *

2\. Core Problem
================

Traditional resume screening and skill matching systems often rely heavily on exact keyword matching.

This can fail when candidates and job descriptions describe similar capabilities using different terminology.

SkillLens is designed to address this through:

-   structured resume and job-profile extraction

-   skill normalization

-   ESCO taxonomy integration

-   transformer-based semantic representations

-   hybrid semantic and lexical matching

-   explicit skill-gap identification

-   explainable analytical results

-   career intelligence

-   actionable recommendations

* * * * *

3\. Development Phases
======================

SkillLens is developed incrementally.

Phase 1 --- Foundation and Architecture
-------------------------------------

**Status: COMPLETE**

Established:

-   project structure

-   modular-monolith architecture

-   canonical domain contracts

-   API contracts

-   frontend contracts

-   Analysis Orchestrator interface

-   testing foundation

-   documentation foundation

* * * * *

Phase 2 --- Document Processing
-----------------------------

**Status: COMPLETE / FROZEN**

Established:

-   `DocumentParser`

-   `PDFParser`

-   `DOCXParser`

-   `DocumentProcessor`

-   validation

-   `ParsedDocument`

-   normalized document blocks

-   source provenance

Phase 2 is the permanent document-processing boundary.

Later phases consume `ParsedDocument` and must not reparse PDF/DOCX files.

* * * * *

Phase 3 --- Resume Intelligence
-----------------------------

**Status: COMPLETE / VERIFIED**

Implemented:

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

Implemented modules:

```
backend/app/analysis/resume_structure.py
backend/app/analysis/skill_extractor.py
backend/app/analysis/skill_normalizer.py
backend/app/analysis/esco_mapper.py
backend/app/analysis/resume_profile_builder.py

```

Phase 3 is committed as:

```
0b73efe Complete Phase 3 resume intelligence pipeline

```

* * * * *

4\. Supported Analysis Modes
============================

RESUME_ONLY
-----------

Analyzes a resume independently.

The system may eventually provide:

-   resume profile

-   extracted skills

-   candidate profile

-   career signals

-   potential roles

-   skill priorities

-   recommendations

-   explainability where applicable

The system must not fabricate job-specific information such as:

-   job-match score

-   missing skills relative to a job

-   job-specific skill gaps

-   job-specific match explanations

* * * * *

RESUME_JD
---------

Analyzes a resume against a supplied job description.

The system may eventually provide:

-   resume profile

-   job profile

-   extracted skills

-   matched skills

-   partial matches

-   missing skills

-   transferable skills

-   skill-gap analysis

-   scoring

-   explainability

-   career intelligence

-   recommendations

Resume-JD intelligence belongs to later phases.

* * * * *

5\. Approved Architecture
=========================

SkillLens uses a **modular monolith**.

Primary dependency direction:

```
API
 ↓
Analysis Orchestrator
 ↓
Domain Engines
 ↓
Infrastructure

```

The Analysis Orchestrator is the single coordinator of analytical workflows.

Domain engines must remain focused on their individual responsibilities.

* * * * *

6\. Canonical Analytical Responsibilities
=========================================

The project has one canonical owner for each major responsibility.

### Document Processing

`DocumentProcessor`

Owns PDF/DOCX processing and produces `ParsedDocument`.

### Resume Structure

`ResumeStructureInterpreter`

Interprets the structure of an already parsed resume.

### Skill Extraction

`SkillExtractor`

Extracts skill mentions and evidence from parsed resume content.

### Skill Normalization

`SkillNormalizer`

Converts extracted mentions into canonical skill representations.

### ESCO Mapping

`ESCOMapper`

Maps canonical skills to ESCO terminology where supported.

### Resume Profile Construction

`ResumeProfileBuilder`

Builds the canonical `ResumeProfile`.

### Semantic Matching

`SemanticMatcher`

Owns future semantic comparison between skills or requirements.

### Gap Analysis

`GapAnalyzer`

Owns future skill-gap identification and classification.

### Scoring

`ScoreEngine`

Is the single owner of analytical scoring.

### Explainability

`XAIEngine`

Explains existing analytical results.

It must not independently recalculate scores.

### Career Intelligence

`CareerIntelligenceEngine`

Owns candidate-level career inference and role intelligence.

### Recommendations

`RecommendationEngine`

Is the single owner of recommendations.

* * * * *

7\. Canonical Ownership Rules
=============================

Each analytical responsibility must have one canonical implementation.

No duplicate:

-   skill extractors

-   skill normalizers

-   resume models

-   matching engines

-   scoring engines

-   recommendation engines

-   document parsers

-   analysis orchestrators

The Analysis Orchestrator coordinates workflow.

Individual domain engines must not become independent workflow orchestrators.

* * * * *

8\. Phase 3 Resume Intelligence Contract
========================================

The canonical Phase 3 contract is:

```
ParsedDocument
        ↓
StructuredResume
        ↓
SkillMention
        ↓
NormalizedSkill
        ↓
ESCOMapResult
        ↓
Evidence + Confidence
        ↓
ResumeProfile

```

The final output is the domain-level:

```
ResumeProfile

```

This profile becomes the canonical resume representation for later phases.

* * * * *

9\. ResumeProfile
=================

The canonical `ResumeProfile` contains:

-   `profile_id`

-   `document_id`

-   `candidate_summary`

-   `contact`

-   `education`

-   `experience`

-   `projects`

-   `certifications`

-   `skills`

-   `skill_categories`

-   `total_experience`

-   `seniority`

-   `domains`

-   `metadata`

Later phases may enrich the profile, but they must preserve its canonical ownership.

* * * * *

10\. Skill Representation
=========================

The canonical `Skill` model supports:

-   skill identity

-   canonical name

-   display name

-   category

-   subcategory

-   aliases

-   proficiency

-   importance

-   evidence

-   confidence

-   metadata

Phase 3 adds deterministic extraction, normalization, evidence, confidence, and ESCO metadata without introducing a competing skill model.

* * * * *

11\. Evidence and Provenance
============================

Evidence is a first-class system capability.

Evidence must retain its relationship to the source document.

The canonical `Evidence` model supports:

-   evidence ID

-   source type

-   source document ID

-   section

-   source text

-   start offset

-   end offset

-   evidence type

-   extractor

-   relevance

-   confidence

Future XAI components should use this provenance rather than reconstructing evidence independently.

* * * * *

12\. Confidence
===============

Confidence uses the canonical representation:

```
0--1 score

```

with:

-   confidence level

-   component scores

-   rationale

Phase 3 estimates confidence for extracted and mapped skills.

Confidence is not the same thing as analytical matching score.

* * * * *

13\. ESCO Integration
=====================

SkillLens uses ESCO as the planned external skill taxonomy.

Current Phase 3 ESCO version:

```
1.2.1

```

Current implementation provides an adapter boundary with a deterministic representative vocabulary.

The implementation does not contain the complete ESCO dataset.

No fabricated ESCO identifiers are permitted.

A future infrastructure implementation may connect the mapper to the official ESCO dataset/API while preserving the `ESCOMapper` ownership boundary.

* * * * *

14\. Document Processing Contract
=================================

Document processing belongs exclusively to the Phase 2 infrastructure layer.

The flow is:

```
PDF / DOCX
    ↓
DocumentProcessor
    ↓
ParsedDocument

```

Phase 3 and later phases consume:

```
ParsedDocument

```

They must not:

-   reopen PDF files

-   reopen DOCX files

-   duplicate parser logic

-   create competing document models

The Phase 2 boundary is frozen.

* * * * *

15\. API Versioning
===================

API base path:

```
/api/v1

```

Current endpoint contracts include:

```
GET    /api/v1/health
POST   /api/v1/analyses/resume
POST   /api/v1/analyses/resume-jd
GET    /api/v1/analyses/{analysis_id}
DELETE /api/v1/analyses/{analysis_id}

```

The complete production analysis workflow will be integrated progressively through later phases.

* * * * *

16\. Canonical Analysis Result
==============================

`AnalysisResult` is the single source of truth for frontend analytical data.

It contains or will contain:

-   analysis metadata

-   input references

-   resume profile

-   optional job profile

-   skill analysis

-   scoring

-   XAI results

-   career intelligence

-   recommendations

-   processing metadata

The frontend must consume stable API/domain contracts rather than backend implementation details.

* * * * *

17\. Scoring Rules
==================

Public scores use a:

```
0--100

```

scale.

Internal calculations may use normalized values such as:

```
0--1

```

Planned scoring dimensions include:

-   overall score

-   skill score

-   required-skill score

-   preferred-skill score

-   experience score

-   education score

-   domain score

Scoring is outside the Phase 3 boundary.

* * * * *

18\. Explainability Principles
==============================

Explainability is a first-class capability.

XAI should connect analytical outputs to supporting evidence.

Planned technologies include:

-   SHAP

-   LIME where appropriate

XAI explains results produced by analytical engines.

It must not become a second scoring engine.

* * * * *

19\. Planned Technology Stack
=============================

Backend
-------

-   Python

-   FastAPI

-   Pydantic

-   Pydantic Settings

Frontend
--------

-   React

-   TypeScript

-   Vite

NLP / ML
--------

Planned:

-   Sentence Transformers

-   transformer-based NLP

-   `all-MiniLM-L6-v2` as an initial embedding candidate

-   hybrid semantic and lexical matching

-   ESCO

-   SHAP

-   LIME

-   LLM

A locally hosted open-source LLM using Ollama is planned for later recommendation/intelligence functionality.

The LLM is not the semantic similarity engine.

* * * * *

20\. Testing Strategy
=====================

Every completed phase must be verified through appropriate tests.

Required categories include:

-   unit tests

-   integration tests

-   regression tests

-   negative tests

-   real document tests where applicable

Tests must be executed before claiming completion.

Phase 3 regression baseline:

```
115 passed
7 warnings
0 failures

```

* * * * *

21\. Explicit Phase Boundaries
==============================

Phase 3 does not implement:

-   job description analysis

-   resume-JD matching

-   hybrid matching

-   semantic similarity

-   skill-gap scoring

-   final match score

-   XAI scoring engine

-   career intelligence

-   role recommendations

-   learning recommendations

-   Ollama

-   LLM recommendation generation

-   frontend dashboard redesign

These are reserved for later phases.

* * * * *

22\. Current Development State
==============================

```
Phase 1 --- Foundation
COMPLETE

Phase 2 --- Document Processing
COMPLETE / FROZEN

Phase 3 --- Resume Intelligence
COMPLETE / VERIFIED

Phase 4 --- Resume Quality & ATS Intelligence
PLANNED / NOT STARTED

```

Latest verified repository commit:

```
0b73efe Complete Phase 3 resume intelligence pipeline

```

* * * * *

23\. Next Planned Phase
=======================

The next planned development phase is:

**Phase 4 --- Resume Quality & ATS Intelligence**

Phase 4 must begin with:

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

No Phase 4 implementation should begin until its exact scope and contracts are established.
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

Phase 6 --- Final Candidate-Job Scoring, Skill Gap Analysis & XAI
---------------------------------------------------------------

**Status: COMPLETE / FROZEN**

Phase 6 extends the Phase 5 Resume--JD intelligence pipeline with deterministic candidate-job scoring, requirement-linked skill-gap analysis, transparent score contributions, and deterministic XAI.

Established:

-   deterministic candidate-job scoring

-   explicit required/preferred scoring weights

-   experience, education, and domain scoring

-   explicit UNKNOWN handling

-   available-dimension weight renormalization

-   requirement-linked skill gaps

-   matched / partial / unmatched / unknown preservation

-   evidence and confidence preservation

-   deterministic score contribution decomposition

-   deterministic XAI

-   matched, partial, and missing skill explanations

-   evidence mapping

-   Resume + JD `AnalysisResult` integration

-   Resume-only compatibility

-   Phase 6 engine versioning

-   dedicated Phase 6 tests

-   API integration verification

-   full regression verification

Canonical Phase 6 engines:

-   `GapAnalyzer`

-   `ScoringAnalyzer`

-   `XAIAnalyzer`

The existing `ConcreteAnalysisOrchestrator` remains the single workflow orchestrator. No second orchestrator was introduced.

Final verification:

-   Phase 6 targeted tests: **64 passed, 7 warnings**

-   Full backend regression: **281 passed, 7 warnings**

-   Test failures: **0**

-   `git diff --check`: **PASS**

The complete implementation, architecture decisions, scoring policy, XAI design, test evidence, scope boundaries, and verification record are documented in:

`docs/PHASE_6.md`

`docs/PHASE_6.md` is the authoritative detailed record for Phase 6.