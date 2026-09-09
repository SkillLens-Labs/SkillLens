SkillLens --- Architecture
========================

1\. Architecture Overview
-------------------------

SkillLens is designed as a modular monolith with clear separation between API, orchestration, analysis/domain logic, and infrastructure.

The primary dependency direction is:

```
API
 ↓
Analysis Orchestrator
 ↓
Analysis / Domain Engines
 ↓
Infrastructure

```

The architecture deliberately avoids unnecessary distributed-system complexity.

The system is designed to remain modular while being simple enough for an academic project and extensible toward future production use.

The architecture is implemented incrementally through controlled development phases.

### Phase Architecture Progress

```
Phase 1
Foundation + Contracts
        ↓
Phase 2
Document Processing
        ↓
Phase 3
Resume Intelligence
        ↓
Phase 4+
Matching + Scoring + XAI + Career Intelligence + Recommendations

```

Phase boundaries are intentional. Functionality belonging to a later phase must not be prematurely implemented inside an earlier phase.

* * * * *

2\. Architectural Layers
========================

API Layer
---------

Location:

```
backend/app/api/

```

Responsibilities:

-   HTTP endpoints

-   Request handling

-   Response serialization

-   HTTP status codes

-   API-level validation

-   API error handling

The API layer must not contain analytical business logic.

API routes communicate with the `AnalysisOrchestrator` rather than directly invoking individual analytical engines.

* * * * *

Orchestration Layer
-------------------

Location:

```
backend/app/orchestration/

```

The `AnalysisOrchestrator` is the single workflow coordinator.

Its responsibility is to coordinate the complete analysis workflow according to the active analysis mode and available analytical capabilities.

Responsibilities include:

-   Accepting analysis requests

-   Coordinating document processing

-   Coordinating resume structure interpretation

-   Coordinating skill extraction

-   Coordinating skill normalization

-   Coordinating ESCO mapping

-   Coordinating evidence construction

-   Coordinating confidence estimation

-   Coordinating future matching

-   Coordinating future gap analysis

-   Coordinating future scoring

-   Coordinating future explainability

-   Coordinating future career intelligence

-   Coordinating future recommendations

-   Producing the canonical `AnalysisResult`

Individual analytical engines must not become workflow orchestrators.

### Important Phase 3 Boundary

Phase 3 implements the resume-intelligence pipeline independently of the public analysis orchestration flow.

The implemented Phase 3 processing chain is:

```
ParsedDocument
      ↓
ResumeStructureInterpreter
      ↓
StructuredResume
      ↓
SkillExtractor
      ↓
SkillNormalizer
      ↓
ESCOMapper
      ↓
ResumeProfileBuilder
      ↓
Canonical ResumeProfile

```

The Phase 3 engines do not implement job-description analysis, matching, scoring, XAI scoring explanations, or recommendations.

* * * * *

Domain Layer
------------

Location:

```
backend/app/domain/

```

The domain layer contains the canonical business models and analytical contracts.

Current domain contracts include:

-   `AnalysisResult`

-   `AnalysisInput`

-   `ResumeProfile`

-   `Contact`

-   `Education`

-   `Experience`

-   `Project`

-   `Certification`

-   `JobProfile`

-   `Skill`

-   `Evidence`

-   `Confidence`

-   `SkillMatch`

-   `SkillGap`

-   `SkillAnalysis`

-   `ScoringResult`

-   `XAIResult`

-   `CareerIntelligence`

-   `Recommendation`

The domain layer must remain independent of API implementation details.

The domain layer also remains independent of document-parser implementation details.

* * * * *

Infrastructure Layer
--------------------

Location:

```
backend/app/infrastructure/

```

Infrastructure contains implementation details required by document processing and future analytical capabilities.

Current responsibilities include:

-   Document validation

-   PDF parsing

-   DOCX parsing

-   Normalized parsed-document construction

Future responsibilities may include:

-   Persistence

-   Machine-learning infrastructure

-   Transformer model loading

-   External taxonomy integrations

-   Embedding infrastructure

-   Repository implementations

Infrastructure must not become the owner of business workflow.

* * * * *

3\. Canonical Analysis Components
=================================

Each major responsibility has a canonical owner.

The current architecture distinguishes between **implemented components** and **planned components**.

DocumentProcessor
-----------------

Status: **Implemented --- Phase 2**

Responsible for:

-   Validating incoming documents

-   Determining document type

-   Selecting the appropriate parser

-   Generating or accepting a document identifier

-   Returning a normalized `ParsedDocument`

It does not:

-   Extract skills

-   Normalize skills

-   Perform semantic matching

-   Calculate scores

-   Generate recommendations

-   Execute XAI logic

* * * * *

ResumeStructureInterpreter
--------------------------

Status: **Implemented --- Phase 3**

Location:

```
backend/app/analysis/resume_structure.py

```

Responsible for interpreting the structural organization of a parsed resume.

Responsibilities:

-   Identifying resume sections

-   Classifying recognized headings

-   Grouping document blocks into logical sections

-   Preserving original block ordering

-   Preserving the source document identifier

-   Representing unknown sections without inventing meaning

The interpreter operates on the Phase 2 `ParsedDocument` abstraction.

It does not reparse PDF or DOCX content.

* * * * *

SkillExtractor
--------------

Status: **Implemented --- Phase 3**

Location:

```
backend/app/analysis/skill_extractor.py

```

Responsible for:

-   Identifying skill mentions in structured resume content

-   Extracting skills from explicit skill-oriented sections

-   Extracting contextual skills from resume sections

-   Producing skill evidence

-   Preserving raw skill text

-   Preserving block provenance

-   Recording character offsets

-   Producing extraction confidence

The Phase 3 implementation uses deterministic skill vocabulary matching.

It does not perform canonical normalization or semantic matching.

* * * * *

SkillNormalizer
---------------

Status: **Implemented --- Phase 3**

Location:

```
backend/app/analysis/skill_normalizer.py

```

Responsible for:

-   Unicode normalization

-   Whitespace normalization

-   Case normalization

-   Alias resolution

-   Canonical skill-name generation

-   Preserving original raw skill text

-   Preserving extraction confidence

Examples of normalization include:

```
Py
Python 3
python programming
        ↓
python

ReactJS
React.js
React JS
        ↓
react

Postgres
        ↓
postgresql

ML
        ↓
machine learning

```

Skill normalization is deterministic.

The normalizer does not perform semantic similarity matching.

* * * * *

ESCOMapper
----------

Status: **Implemented --- Phase 3 adapter**

Location:

```
backend/app/analysis/esco_mapper.py

```

Responsible for:

-   Mapping normalized skills toward the ESCO taxonomy

-   Representing mapping status

-   Producing mapping candidates

-   Preserving mapping confidence

-   Preserving the ESCO version used by the adapter

The current implementation uses a deterministic adapter vocabulary rather than embedding the complete ESCO dataset.

The configured ESCO version is:

```
1.2.1

```

The current adapter intentionally does not fabricate ESCO identifiers.

Where an official identifier is not available through the current adapter, the URI remains empty rather than using an invented identifier.

The architecture leaves the mapper behind a stable abstraction so that the official ESCO dataset/API can be integrated later without changing downstream consumers.

* * * * *

ResumeProfileBuilder
--------------------

Status: **Implemented --- Phase 3**

Location:

```
backend/app/analysis/resume_profile_builder.py

```

Responsible for constructing the canonical domain-level `ResumeProfile`.

Responsibilities include:

-   Combining normalized skill information

-   Combining ESCO mapping results

-   Creating canonical `Skill` objects

-   Deduplicating canonical skills

-   Merging skill evidence

-   Preserving confidence information

-   Deriving skill categories

-   Constructing deterministic profile identifiers

-   Constructing deterministic skill identifiers

-   Constructing deterministic evidence identifiers

-   Preserving the source document identifier

-   Avoiding unsupported factual inference

The builder is the boundary between Phase 3 processing results and the canonical domain `ResumeProfile`.

* * * * *

SemanticMatcher
---------------

Status: **Planned --- Later Phase**

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

Semantic matching is explicitly outside Phase 3.

* * * * *

GapAnalyzer
-----------

Status: **Planned --- Later Phase**

Responsible for:

-   Identifying missing skills

-   Identifying partial matches

-   Identifying transferable skills

-   Classifying skill gaps

-   Assigning gap severity

Gap analysis is explicitly outside Phase 3.

* * * * *

ScoreEngine
-----------

Status: **Planned --- Later Phase**

Responsible for all official analytical scoring.

No other engine may become a second scoring authority.

Public scores use a:

```
0--100

```

scale.

Internal calculations may use normalized:

```
0--1

```

values.

Scoring is explicitly outside Phase 3.

* * * * *

XAIEngine
---------

Status: **Planned --- Later Phase**

Responsible for explaining analytical results.

XAI must explain existing analytical outputs rather than independently recalculating official scores.

Planned technologies include:

-   SHAP

-   LIME where appropriate

XAI is explicitly outside Phase 3.

* * * * *

CareerIntelligenceEngine
------------------------

Status: **Planned --- Later Phase**

Responsible for:

-   Candidate profile inference

-   Experience-level inference

-   Domain inference

-   Potential career roles

-   Role-fit analysis

-   Career transition analysis

-   Skill priorities

-   Career risks

Career intelligence is explicitly outside Phase 3.

* * * * *

RecommendationEngine
--------------------

Status: **Planned --- Later Phase**

Responsible for all recommendations.

Potential recommendation categories include:

-   Learning

-   Projects

-   Certifications

-   Resume improvements

-   Career actions

Recommendations are explicitly outside Phase 3.

* * * * *

4\. Document Processing Architecture --- Phase 2
==============================================

Phase 2 implements the document-processing infrastructure defined by the Phase 1 architecture.

Location:

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

DocumentProcessor
-----------------

`DocumentProcessor` is the entry point for document processing.

Responsibilities:

-   Validate the incoming document

-   Determine document type

-   Select the appropriate parser

-   Generate or accept a document identifier

-   Return a normalized `ParsedDocument`

It does not:

-   Extract skills

-   Perform semantic matching

-   Calculate scores

-   Generate recommendations

-   Execute XAI logic

-   Perform career intelligence

* * * * *

DocumentParser
--------------

`DocumentParser` defines the parser abstraction.

Each concrete parser implements the parsing boundary:

```
parse(content, document_id) → ParsedDocument

```

This allows additional document formats to be introduced without changing downstream consumers.

* * * * *

PDFParser
---------

The PDF parser uses PyMuPDF to extract text blocks from each page.

The parser preserves page and positional provenance where available.

The current Phase 2 PDF parser primarily provides normalized text blocks and provenance.

It does not guarantee semantic heading classification for every PDF layout.

This is an important architectural distinction: downstream Phase 3 processing consumes the parser's actual `DocumentBlock` representation rather than reparsing the PDF.

* * * * *

DOCXParser
----------

The DOCX parser uses `python-docx`.

It processes document body content while preserving paragraph/table ordering.

Supported structures include:

-   Paragraphs

-   Headings

-   Lists/bullets

-   Tables

-   Table cells

* * * * *

Normalized Representation
-------------------------

All supported document types are converted into:

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

This creates a stable boundary between document ingestion and analytical processing.

* * * * *

5\. Phase 3 Resume Intelligence Architecture
============================================

Phase 3 builds the first analytical layer on top of the frozen Phase 2 document-processing boundary.

The Phase 3 objective is:

```
ParsedDocument
      ↓
Resume Structure Interpretation
      ↓
ResumeProfile Construction
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
Canonical ResumeProfile

```

The implementation is divided into focused components rather than placing all logic inside a single resume-analysis module.

* * * * *

Phase 3 Component Locations
---------------------------

```
backend/app/analysis/

├── resume_structure.py
├── skill_extractor.py
├── skill_normalizer.py
├── esco_mapper.py
└── resume_profile_builder.py

```

Tests are organized as:

```
backend/tests/unit/

├── test_resume_structure.py
├── test_skill_extractor.py
├── test_skill_normalizer.py
├── test_esco_mapper.py
└── test_resume_profile_builder.py

backend/tests/integration/

└── test_phase3_resume_analysis.py

```

Real document fixtures are maintained under:

```
backend/tests/fixtures/

├── phase3_sample_resume.pdf
└── phase3_sample_resume.docx

```

* * * * *

6\. Phase 3 Resume Processing Flow
==================================

The implemented Phase 3 flow is:

```
Document Bytes
      ↓
DocumentProcessor
      ↓
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

The flow preserves evidence and confidence information throughout the processing chain.

* * * * *

7\. Resume Structure Interpretation
===================================

The `ResumeStructureInterpreter` consumes `ParsedDocument`.

It identifies logical resume sections using recognized heading patterns and aliases.

Current recognized section categories include:

-   Summary

-   Experience

-   Education

-   Projects

-   Certifications

-   Skills

-   Header

-   Unknown

The interpreter preserves:

-   Document ID

-   Original block order

-   Source provenance

-   Original text

Unknown headings remain unknown rather than being assigned an unsupported semantic meaning.

This avoids fabricated structure.

* * * * *

8\. Skill Extraction Architecture
=================================

`SkillExtractor` operates on `StructuredResume`.

The extractor distinguishes between explicit and contextual skill evidence.

Current evidence categories include:

-   Explicit skills

-   Certification-related skills

-   Summary/contextual skills

-   Experience/contextual skills

-   Project/contextual skills

-   Education/contextual skills

The extractor produces:

```
SkillExtractionResult
    └── SkillMention[]
          ├── raw_text
          ├── evidence_type
          ├── block
          ├── start_offset
          ├── end_offset
          └── confidence

```

Skill extraction remains separate from normalization.

A raw mention such as:

```
ReactJS

```

is not changed into:

```
react

```

until it reaches `SkillNormalizer`.

* * * * *

9\. Skill Normalization Architecture
====================================

`SkillNormalizer` converts extracted skill mentions into canonical normalized skills.

The normalization flow is:

```
Raw Skill Mention
      ↓
Unicode Normalization
      ↓
Whitespace Normalization
      ↓
Case Normalization
      ↓
Alias Resolution
      ↓
Canonical Skill

```

Normalization preserves:

-   Raw text

-   Canonical name

-   Extraction confidence

-   Original evidence context

Multiple raw mentions may resolve to the same canonical skill.

For example:

```
Python
python programming
Py
Python 3

```

may all resolve to:

```
python

```

* * * * *

10\. ESCO Mapping Architecture
==============================

ESCO mapping occurs after skill normalization.

The flow is:

```
Normalized Skill
      ↓
ESCOMapper
      ↓
ESCOMapResult
      ├── status
      ├── candidates
      ├── confidence
      ├── mapping method
      └── taxonomy version

```

Current statuses include:

```
MAPPED
AMBIGUOUS
UNMAPPED

```

The Phase 3 implementation provides a deterministic adapter vocabulary.

It is intentionally not treated as a complete local copy of the ESCO taxonomy.

The mapper abstraction is designed so that a complete official ESCO dataset integration can replace or extend the adapter later.

No fabricated taxonomy identifiers are permitted.

* * * * *

11\. Evidence Architecture
==========================

Evidence is preserved from the source document through the analytical pipeline.

The canonical domain evidence model contains:

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

Phase 3 uses evidence to connect extracted and normalized skills back to their source document blocks.

Evidence identifiers are deterministic and incorporate source information so that distinct source occurrences are not incorrectly collapsed into a single evidence record.

This enables future matching, gap analysis, XAI, and recommendation components to consume evidence-backed analytical results.

* * * * *

12\. Confidence Architecture
============================

Phase 3 preserves confidence at multiple processing boundaries.

The canonical domain confidence contract is:

```
Confidence
├── score
├── level
├── components
└── rationale

```

The score remains within:

```
0--1

```

The confidence level is one of:

```
LOW
MEDIUM
HIGH

```

The Phase 3 profile-building process derives confidence from available extraction and ESCO mapping signals.

Confidence is evidence about analytical certainty.

It is not the same as the eventual candidate-job match score.

* * * * *

13\. Canonical ResumeProfile Construction
=========================================

`ResumeProfileBuilder` converts Phase 3 processing results into the canonical domain model:

```
ResumeProfile

```

The builder is responsible for creating canonical `Skill` objects and merging repeated canonical skill mentions.

The resulting structure includes:

```
ResumeProfile
├── profile_id
├── document_id
├── candidate_summary
├── contact
├── education
├── experience
├── projects
├── certifications
├── skills
├── skill_categories
├── total_experience
├── seniority
├── domains
└── metadata

```

Phase 3 does not invent resume facts that are not reliably represented by the current processing components.

Therefore, fields that require dedicated extraction logic remain empty or unset rather than being inferred without sufficient evidence.

* * * * *

14\. Canonical Skill Construction
=================================

The canonical domain `Skill` model remains the single skill representation consumed by downstream analysis.

Phase 3 populates the skill model from:

```
SkillMention
      +
NormalizedSkill
      +
ESCOMapResult
      +
Evidence
      +
Confidence

```

The resulting skill contains canonical information such as:

```
skill_id
canonical_name
display_name
category
subcategory
aliases
proficiency
importance
evidence
confidence
metadata

```

Duplicate mentions of the same canonical skill are merged.

Evidence from separate source occurrences is preserved.

* * * * *

15\. Deterministic Identity Strategy
====================================

Phase 3 uses deterministic identifiers for analytical objects where appropriate.

Identifiers are derived from stable input information rather than random values.

This provides:

-   Repeatable test results

-   Stable deduplication

-   Reproducible profile construction

-   Stable evidence merging

-   Easier debugging

Distinct source occurrences must remain distinguishable even when their textual offsets are identical.

* * * * *

16\. Resume-Only Architecture
=============================

The resume-only mode is the first analysis mode supported by the Phase 3 resume intelligence layer.

The Phase 3 analytical scope is:

```
Resume
   ↓
DocumentProcessor
   ↓
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
   ↓
ResumeProfile

```

Phase 3 does not produce:

-   Job match scores

-   JD-specific missing skills

-   Required-skill matching

-   Preferred-skill matching

-   Skill-gap scores

-   Candidate-job compatibility scores

Those responsibilities belong to later phases.

* * * * *

17\. Resume + Job Description Architecture
==========================================

The API and domain architecture continue to support:

```
RESUME_JD

```

However, Phase 3 does not implement the job-description analytical pipeline.

The planned later workflow is:

```
Resume
   ↓
Resume Intelligence
   ↓
ResumeProfile

Job Description
   ↓
Job Intelligence
   ↓
JobProfile

ResumeProfile + JobProfile
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

```

This separation prevents Phase 3 resume intelligence from becoming coupled to future matching and scoring logic.

* * * * *

18\. Canonical Data Flow
========================

The frontend does not directly access individual backend engines.

The canonical data flow remains:

```
React Frontend
      ↓
HTTP API
      ↓
FastAPI Routes
      ↓
Analysis Orchestrator
      ↓
Analysis / Domain Engines
      ↓
Infrastructure

```

The final analytical response is represented by:

```
AnalysisResult

```

`AnalysisResult` remains the single source of truth for frontend analytical data.

The Phase 3 `ResumeProfile` is one canonical component of the eventual `AnalysisResult`.

* * * * *

19\. Dependency Rules
=====================

The intended dependency direction is:

```
API
 ↓
Orchestration
 ↓
Analysis / Domain
 ↓
Infrastructure

```

The following reverse dependencies are prohibited:

-   Domain → API

-   Domain → Orchestration

-   Domain → Infrastructure

-   Orchestration → API

-   Infrastructure → API

-   Infrastructure → Orchestration

Phase 3 analytical components must not introduce circular dependencies.

The frozen Phase 2 parser boundary must not be bypassed.

Phase 3 must consume:

```
ParsedDocument

```

rather than directly reparsing PDF or DOCX bytes.

* * * * *

20\. Responsibility Ownership
=============================

Each major responsibility has exactly one canonical owner.

| Responsibility | Owner | Status |
| --- | --- | --- |
| Document parsing | `DocumentProcessor` / parser implementations | Implemented --- Phase 2 |
| Resume structure interpretation | `ResumeStructureInterpreter` | Implemented --- Phase 3 |
| Skill extraction | `SkillExtractor` | Implemented --- Phase 3 |
| Skill normalization | `SkillNormalizer` | Implemented --- Phase 3 |
| ESCO mapping | `ESCOMapper` | Implemented --- Phase 3 adapter |
| Resume profile construction | `ResumeProfileBuilder` | Implemented --- Phase 3 |
| Semantic matching | `SemanticMatcher` | Planned |
| Skill-gap analysis | `GapAnalyzer` | Planned |
| Scoring | `ScoreEngine` | Planned |
| Explainability | `XAIEngine` | Planned |
| Career intelligence | `CareerIntelligenceEngine` | Planned |
| Recommendations | `RecommendationEngine` | Planned |
| Workflow coordination | `AnalysisOrchestrator` | Architectural owner |
| HTTP interface | API layer | Implemented |
| Canonical data contracts | Domain layer | Implemented |

Duplicate implementations of these responsibilities must not be introduced.

* * * * *

21\. Frontend Architecture
==========================

Frontend technology:

-   React

-   TypeScript

-   Vite

Frontend structure:

```
frontend/src/

```

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

-   XAI

-   recommendations

The frontend consumes stable API contracts.

It must not import backend Python modules or depend on backend internal implementation details.

* * * * *

22\. Frontend State Architecture
================================

The analysis state contract currently supports:

-   idle

-   submitting

-   loading

-   success

-   error

The state stores:

-   Current `AnalysisResult`

-   Structured error information

-   Last request ID

-   Current operation status

The state contract is defined in:

```
frontend/src/state/analysisState.ts

```

Phase 3 does not require a frontend architecture redesign.

* * * * *

23\. API Architecture
=====================

API version:

```
/api/v1

```

Current endpoints:

```
GET    /api/v1/health
POST   /api/v1/analyses/resume
POST   /api/v1/analyses/resume-jd
GET    /api/v1/analyses/{analysis_id}
DELETE /api/v1/analyses/{analysis_id}

```

The public API contract remains stable across Phase 1, Phase 2, and Phase 3.

Phase 3 adds internal analytical capability without introducing a new public parser endpoint or replacing `AnalysisResult` with `ParsedDocument`.

* * * * *

24\. Error Architecture
=======================

Internal application errors use:

```
ApplicationError

```

Location:

```
backend/app/core/exceptions.py

```

External API errors use:

```
ErrorResponse

```

Location:

```
backend/app/schemas/errors.py

```

These are intentionally separate responsibilities.

`ErrorResponse` contains:

-   code

-   message

-   details

-   field

-   request_id

* * * * *

25\. Configuration Architecture
===============================

Application configuration is centralized in:

```
backend/app/core/config.py

```

Configuration is represented through Pydantic Settings.

Current configuration includes:

-   application name

-   application version

-   environment

-   API version prefix

-   debug setting

-   maximum upload size

Environment variables may override configuration values.

* * * * *

26\. Logging Architecture
=========================

Application logging is centralized through:

```
backend/app/core/logging.py

```

The logging foundation provides:

-   `configure_logging()`

-   `get_logger()`

Individual modules should use module-level loggers rather than configuring logging independently.

* * * * *

27\. Testing Architecture
=========================

Testing is separated into:

```
backend/tests/unit/
backend/tests/integration/
backend/tests/api/
backend/tests/evaluation/
backend/tests/fixtures/

```

Phase 1 established the initial testing architecture.

Phase 2 added document-processing verification.

Phase 3 added unit and integration coverage for resume intelligence.

### Phase 3 Testing Coverage

Unit tests cover:

-   Resume structure interpretation

-   Skill extraction

-   Skill normalization

-   ESCO mapping

-   Resume profile construction

Integration testing covers:

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

Real-file verification includes:

-   PDF

-   DOCX

The Phase 3 regression suite was verified with:

```
115 passed
7 warnings

```

The warnings are dependency deprecation warnings and do not represent test failures.

* * * * *

28\. Real Document Verification
===============================

Phase 3 verification included real PDF and DOCX fixtures.

The DOCX fixture successfully demonstrated the complete Phase 3 flow from document processing through canonical `ResumeProfile` construction.

The PDF fixture successfully demonstrated real PDF parsing and `ParsedDocument` construction.

The current PDF parser does not infer semantic headings from the tested PDF layout. Consequently, the synthetic PDF fixture does not demonstrate the complete semantic resume-section extraction path.

This is an expected limitation of the current Phase 2 parser behavior and does not justify bypassing the frozen Phase 2 boundary.

Future improvements to PDF semantic interpretation should be handled through an explicitly planned architecture change rather than undocumented reparsing inside Phase 3.

* * * * *

29\. Infrastructure Strategy
============================

SkillLens intentionally uses a modular-monolith architecture.

The following infrastructure is not currently required:

-   Redis

-   Celery

-   Kafka

-   Kubernetes

-   Service mesh

-   Microservices

-   Distributed workflow engines

Additional infrastructure should only be introduced when a concrete project requirement justifies it.

Phase 3 does not introduce distributed infrastructure.

* * * * *

30\. Model Architecture
=======================

Transformer models are planned for later phases.

Initial semantic embedding candidate:

```
all-MiniLM-L6-v2

```

The embedding model is intended for semantic similarity and matching.

The LLM is not the semantic similarity engine.

A local open-source LLM using Ollama may be introduced for suitable language-generation tasks after benchmarking.

Phase 3 does not require transformer inference or LLM inference.

* * * * *

31\. Explainability Architecture
================================

Explainability is designed as a separate analytical layer.

The architecture separates:

-   analytical calculation

-   explanation generation

-   evidence mapping

XAI must consume existing analytical results.

It must not become an alternative scoring engine.

Phase 3 establishes evidence and confidence foundations that can later support the XAI layer.

Actual XAI implementation remains outside Phase 3.

* * * * *

32\. Persistence Architecture
=============================

Persistence was not implemented as part of Phase 1 or Phase 3 resume intelligence.

The architecture leaves room for:

-   Analysis repositories

-   Document repositories

-   Future database models

-   Persistent analysis history

-   Resume-profile persistence

Persistence implementation will be introduced only when required by the corresponding project phase.

* * * * *

33\. Phase 1 Architectural Boundary
===================================

Phase 1 established the permanent project foundation.

It introduced:

-   Backend structure

-   Frontend structure

-   Core configuration

-   Canonical domain models

-   API contracts

-   Analysis Orchestrator contract

-   Error architecture

-   Testing architecture

-   Documentation structure

-   Dependency rules

Advanced analytical implementation was intentionally excluded from Phase 1.

* * * * *

34\. Phase 2 Architectural Boundary
===================================

Phase 2 introduced the document-processing layer.

The frozen boundary is:

```
Document Bytes
      ↓
DocumentProcessor
      ↓
ParsedDocument

```

Phase 2 does not perform:

-   Skill extraction

-   Skill normalization

-   ESCO mapping

-   Semantic matching

-   Gap analysis

-   Scoring

-   XAI

-   Career intelligence

-   Recommendations

The parser layer terminates at `ParsedDocument`.

* * * * *

35\. Phase 3 Architectural Boundary
===================================

Phase 3 introduces resume intelligence on top of the frozen Phase 2 boundary.

Phase 3 implements:

-   Resume structure interpretation

-   Resume section classification

-   Skill extraction

-   Skill evidence generation

-   Skill normalization

-   Alias resolution

-   ESCO mapping adapter

-   Confidence estimation

-   Evidence linking

-   Canonical `ResumeProfile` construction

-   Canonical skill deduplication

-   Deterministic analytical identifiers

Phase 3 explicitly does not implement:

-   Job-description analysis

-   Resume-JD matching

-   Semantic matching

-   Hybrid matching

-   Skill-gap scoring

-   Final match scoring

-   ScoreEngine

-   XAI scoring/explanation engine

-   Career intelligence

-   Role recommendations

-   Learning recommendations

-   Ollama/LLM recommendation generation

-   Frontend dashboard redesign

This boundary is frozen unless explicitly revised.

* * * * *

36\. Phase 3 Canonical Processing Contract
==========================================

The Phase 3 processing contract is:

```
ParsedDocument
      ↓
Resume Structure Interpretation
      ↓
StructuredResume
      ↓
Skill Extraction
      ↓
Skill Mentions
      ↓
Skill Normalization
      ↓
Normalized Skills
      ↓
ESCO Mapping
      ↓
Mapped / Ambiguous / Unmapped Results
      ↓
Evidence + Confidence
      ↓
ResumeProfileBuilder
      ↓
Canonical ResumeProfile

```

The Phase 2 `ParsedDocument` contract is consumed as-is.

Phase 3 must not modify the Phase 2 parser model merely to simplify downstream implementation.

* * * * *

37\. Architectural Validation
=============================

Architecture validation covers:

-   Python compilation

-   Application importability

-   OpenAPI route registration

-   Backend/frontend contract alignment

-   Dependency direction

-   Duplicate responsibility detection

-   Unit tests

-   Integration tests

-   Real document verification

-   Regression testing

Phase 1 architectural validation established the baseline architecture.

Phase 2 validation established the document-processing boundary.

Phase 3 validation established the resume-intelligence processing chain.

Current Phase 3 backend regression result:

```
115 passed
7 warnings

```

Current Phase 3 implementation is committed to Git on the `main` branch.

Commit:

```
0b73efe Complete Phase 3 resume intelligence pipeline

```

* * * * *

38\. Architectural Invariants
=============================

The following principles are considered frozen unless explicitly revised:

1.  `AnalysisOrchestrator` remains the single workflow coordinator.

2.  Each analytical responsibility has one canonical owner.

3.  `AnalysisResult` remains the canonical frontend analysis result.

4.  `ResumeProfile` remains the canonical resume representation.

5.  `DocumentProcessor` remains the document-processing entry point.

6.  `ParsedDocument` remains the boundary between document processing and analytical processing.

7.  Phase 3 consumes `ParsedDocument` and does not reparse PDF/DOCX documents.

8.  `SkillExtractor` owns skill extraction.

9.  `SkillNormalizer` owns canonical skill normalization.

10. `ESCOMapper` owns ESCO taxonomy mapping.

11. `ResumeProfileBuilder` owns construction of the canonical resume profile from Phase 3 processing outputs.

12. `ScoreEngine` remains the sole scoring authority.

13. `RecommendationEngine` remains the sole recommendation authority.

14. `XAIEngine` explains existing results and does not independently recalculate official scores.

15. Resume-only mode must not fabricate job-specific analysis.

16. Public scores remain on a 0--100 scale.

17. Confidence remains canonical on a 0--1 scale.

18. Evidence should connect analytical outputs to source content.

19. Frontend remains independent from backend implementation details.

20. API versioning remains under `/api/v1`.

21. Circular dependencies are prohibited.

22. Duplicate analytical implementations are prohibited.

23. Unnecessary distributed infrastructure is avoided.

24. Advanced analytical functionality remains phase-controlled.

25. Official ESCO identifiers must never be fabricated.

26. Phase 3 must not silently expand into job matching, scoring, XAI, or recommendation generation.

* * * * *

39\. Current Architecture State
===============================

SkillLens has completed three implementation phases:

```
PHASE 1
Foundation + Architecture
        ↓
COMPLETE

PHASE 2
Document Processing
        ↓
COMPLETE

PHASE 3
Resume Intelligence
        ↓
COMPLETE

```

The current implemented resume-intelligence path is:

```
PDF / DOCX
    ↓
DocumentProcessor
    ↓
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
    ↓
Canonical ResumeProfile

```

The next major architectural layer is the job-intelligence and resume-JD comparison pipeline.

That work belongs to a future phase and must not be started until its phase-specific requirements and contracts are established.
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

Phase 5 extends the existing analysis architecture with Job Description intelligence and Resume–JD matching.

Implemented components:
- JDStructureInterpreter
- JDRequirementExtractor
- JDSkillExtractor
- JDSkillNormalizer
- JDProfileBuilder
- SkillMatcher
- RequirementAligner

The existing DocumentProcessor, SkillNormalizer, and ESCOMapper are reused rather than duplicated.

Semantic matching uses all-MiniLM-L6-v2 with cosine similarity.

The resulting flow is:

ResumeProfile + JobProfile
        ↓
SkillMatcher
        ↓
RequirementAligner
        ↓
MatchingResult
        ↓
AnalysisResult

Phase 5 does not introduce final candidate-job scoring or XAI. Those components remain reserved for Phase 6.

Final verification: **245 tests passed, 7 warnings**.

Phase 6 --- Final Candidate-Job Scoring, Skill Gap Analysis & XAI
---------------------------------------------------------------

**Status: COMPLETE / FROZEN**

Phase 6 extends the existing Phase 5 Resume + Job Description architecture.

The architectural flow is:

```
Resume
   |
   v
Resume Profile
   |
   |
Job Description
   |
   v
Job Profile
   |
   +--> JD Requirements
   +--> JD Skills
             |
             v
        Skill Matching
             |
             v
    Requirement Alignment
             |
       +-----+-----+
       |           |
       v           v
  GapAnalyzer  ScoringAnalyzer
       |           |
       v           v
 SkillAnalysis  ScoringResult
       |           |
       +-----+-----+
             |
             v
        XAIAnalyzer
             |
             v
       AnalysisResult

```

### Architectural Responsibilities

`GapAnalyzer`:

-   converts existing requirement-alignment results into requirement-linked skill gaps

-   preserves status, requirement type, similarity, evidence, and confidence

`ScoringAnalyzer`:

-   calculates the deterministic candidate-job score

-   applies explicit dimension weights

-   handles UNKNOWN and unavailable dimensions

-   produces transparent score contributions

`XAIAnalyzer`:

-   explains existing matching, gap, and scoring results

-   uses deterministic explanation generation

-   preserves evidence and confidence

-   does not independently recalculate official scoring

### Orchestration

Phase 6 uses the existing:

`ConcreteAnalysisOrchestrator`

No second orchestrator was introduced.

The execution order for Resume + JD analysis is:

```
Matching
   ↓
Requirement Alignment
   ↓
Gap Analysis
   ↓
Scoring
   ↓
XAI
   ↓
AnalysisResult

```

Resume-only analysis remains compatible and does not execute job-specific Phase 6 scoring/XAI.

### Design Constraints

Phase 6 preserves:

-   one workflow orchestrator

-   one authoritative matching engine

-   one authoritative requirement alignment engine

-   one authoritative scoring engine

-   similarity separate from confidence

-   UNKNOWN separate from UNMATCHED

-   evidence preservation

-   deterministic scoring

-   deterministic explainability

The complete Phase 6 architecture and implementation decisions are documented in:

`docs/PHASE_6.md`
