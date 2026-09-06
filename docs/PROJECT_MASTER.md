# SkillLens — Project Master

## 1. Project Identity

**Project Name:** SkillLens

**Project Title:** XAI-Driven Semantic Skill Gap Analysis using Transformer-Based Language Models

**Project Type:** Academic software engineering and research project

**Primary Objective:**
Build an explainable semantic skill-gap analysis platform that compares candidate resumes with job requirements, identifies skill matches and gaps, explains analytical results, and produces actionable career recommendations.

---

## 2. Core Problem

Traditional resume screening and skill matching systems often depend heavily on exact keyword matching. This can fail when a candidate and job description express similar capabilities using different terminology.

SkillLens is designed to address this limitation through:

- Structured resume and job-profile extraction
- Skill normalization
- Semantic similarity using transformer-based representations
- Hybrid skill matching
- Explicit skill-gap identification
- Explainable analytical results
- Career intelligence
- Actionable recommendations

---

## 3. Supported Analysis Modes

### RESUME_ONLY

Analyzes a resume independently.

The system may provide:

- Resume profile
- Extracted skills
- Candidate profile
- Career signals
- Potential roles
- Skill priorities
- Recommendations
- Explainability where applicable

The system must **not fabricate job-specific information** such as:

- Job-match score
- Missing skills relative to a job
- Job-specific skill gaps
- Job-specific match explanations

### RESUME_JD

Analyzes a resume against a supplied job description.

The system may provide:

- Resume profile
- Job profile
- Extracted skills
- Matched skills
- Partial matches
- Missing skills
- Transferable skills
- Skill-gap analysis
- Scoring
- Explainability
- Career intelligence
- Recommendations

---

## 4. Approved Architecture

SkillLens uses a **modular monolith**.

The primary dependency direction is:




API
↓
Analysis Orchestrator
↓
Domain Engines
↓
Infrastructure
text
Copy

The Analysis Orchestrator is the single coordinator of the analysis workflow.

### Canonical Engines

Each responsibility has one canonical owner:

- DocumentProcessor
- SkillExtractor
- SkillNormalizer
- SemanticMatcher
- GapAnalyzer
- ScoreEngine
- XAIEngine
- CareerIntelligenceEngine
- RecommendationEngine

Engines must not directly orchestrate or call one another. Workflow coordination belongs to the Analysis Orchestrator.

## 5. Canonical Ownership Rules

**Analysis Orchestrator**
Owns workflow coordination.

**SkillExtractor**
Owns skill extraction from source documents.

**SkillNormalizer**
Owns canonicalization, aliases, taxonomy mapping, and normalization.

**SemanticMatcher**
Owns semantic comparison between skills or requirements.

**GapAnalyzer**
Owns identification and classification of skill gaps.

**ScoreEngine**
Is the single owner of analytical scoring.

**XAIEngine**
Explains existing analytical results.
It must not independently recalculate scores.

**CareerIntelligenceEngine**
Owns candidate-level career inference and role intelligence.

**RecommendationEngine**
Is the single owner of recommendations.

## 6. Canonical Result Contract

`AnalysisResult` is the single source of truth for frontend analytical data.

It contains:
- analysis metadata
- input references
- resume profile
- optional job profile
- skill analysis
- scoring
- XAI results
- career intelligence
- recommendations
- processing metadata

The frontend must consume stable API/domain contracts rather than backend implementation details.

## 7. Canonical Scoring Rules

Public scores use a 0–100 scale.

Internal calculations may use normalized values such as 0–1.

Scoring dimensions include:
- Overall score
- Skill score
- Required-skill score
- Preferred-skill score
- Experience score
- Education score
- Domain score

Confidence is represented canonically on a 0–1 scale with:
- score
- level
- components
- rationale

## 8. Explainability Principles

Explainability is a first-class system capability.

XAI should connect analytical outputs to supporting evidence.

Planned explainability technologies include:
- SHAP
- LIME as an alternative where appropriate

XAI explains results produced by analytical engines. It does not become a second scoring system.

## 9. Planned Technology Stack

### Backend
- Python
- FastAPI
- Pydantic
- Pydantic Settings

### Frontend
- React
- TypeScript
- Vite

### NLP / ML
Planned for later phases:
- Sentence Transformers
- all-MiniLM-L6-v2 as the initial embedding model
- Transformer-based NLP
- Hybrid semantic and lexical matching
- ESCO skill taxonomy
- SHAP
- LIME
- LLM

A locally hosted open-source LLM using Ollama is planned.

The LLM is not the semantic similarity engine.

The final model will be selected after benchmarking.

## 10. Document Support

Planned document processing includes:
- PDF
- DOCX

Document parsing belongs behind the DocumentProcessor abstraction.

## 11. API Versioning

The API base path is:
`/api/v1`

Current planned endpoints:
- `GET /api/v1/health`
- `POST /api/v1/analyses/resume`
- `POST /api/v1/analyses/resume-jd`
- `GET /api/v1/analyses/{analysis_id}`
- `DELETE /api/v1/analyses/{analysis_id}`

## 12. Testing Strategy

SkillLens uses multiple testing layers:
- Unit tests
- Integration tests
- API tests
- Evaluation tests
- Regression tests

Phase 1 establishes the initial unit and API testing infrastructure.

## 13. Development Principles

The project follows these principles:
- Prefer modularity over premature distributed architecture.
- Maintain one canonical owner for each responsibility.
- Keep domain contracts stable.
- Keep API contracts explicit.
- Avoid circular dependencies.
- Avoid duplicate analytical implementations.
- Do not introduce unnecessary infrastructure.
- Do not implement advanced features before their designated phase.
- Validate each phase before progressing.
- Keep frontend independent of backend implementation details.
- Use Git/GitHub for version control.

## 14. Infrastructure Constraints

The initial architecture deliberately avoids unnecessary infrastructure such as:
- Redis
- Celery
- Kafka
- Kubernetes
- Service mesh
- Microservices
- Distributed workflow systems

These may only be introduced later if an explicit requirement justifies them.

## 15. Project Phases

### Phase 1 — Foundation
**Scope:**
- Project structure
- Backend foundation
- Frontend foundation
- Canonical domain schemas
- API contracts
- Orchestrator interface
- Frontend state/data contracts
- Testing infrastructure
- Architecture validation
- Project documentation

### Phase 2 — Document Processing and Skill Extraction
**Planned scope:**
- Resume parsing
- Job-description parsing
- Section extraction
- Skill extraction
- Evidence generation

### Phase 3 — Skill Normalization and Taxonomy
**Planned scope:**
- Skill canonicalization
- Alias handling
- Taxonomy mapping
- ESCO integration

### Phase 4 — Semantic Matching and Gap Analysis
**Planned scope:**
- Embeddings
- Similarity computation
- Hybrid matching
- Partial matches
- Transferable skills
- Skill-gap analysis

### Phase 5 — Scoring and Explainability
**Planned scope:**
- ScoreEngine implementation
- Confidence computation
- XAI
- Evidence mapping

### Phase 6 — Career Intelligence and Recommendations
**Planned scope:**
- Career intelligence
- Role-fit analysis
- Skill priorities
- Recommendation engine

### Phase 7 — Frontend Product Integration
**Planned scope:**
- Complete analysis workflow
- Visualization
- Explainability UI
- Career insights
- Recommendations

### Phase 8 — Evaluation and Finalization
**Planned scope:**
- Evaluation datasets
- Regression testing
- Benchmarking
- Performance validation
- Documentation
- Final academic evaluation

## 16. Current Phase
**Current Phase:** Phase 1 — Foundation

Phase 1 must be completed and verified before Phase 2 begins.
Phase 2 is intentionally not started.

## 17. Phase 1 Completion Standard

Phase 1 is complete only when:
- Required project structure exists.
- Canonical schemas are implemented.
- API contracts are defined.
- Orchestrator interface exists.
- Frontend contracts exist.
- State contract exists.
- Backend tests pass.
- Frontend lint passes.
- Frontend build passes.
- Backend compiles.
- API routes are exposed correctly.
- Backend/frontend contracts agree.
- Circular dependency checks pass.
- Duplicate responsibility checks pass.
- Required documentation is updated.

Phase 2 --- Document Processing
-----------------------------

Phase 2 implements the document-processing foundation required by the downstream SkillLens analytical pipeline.

### Phase 2 Scope

Phase 2 is strictly limited to document processing.

Implemented capabilities:

-   PDF document validation

-   DOCX document validation

-   File extension validation

-   MIME/content-type validation

-   File signature validation

-   Empty-document detection

-   Maximum document-size enforcement

-   PDF text extraction

-   DOCX paragraph extraction

-   DOCX heading detection

-   DOCX bullet/list detection

-   DOCX table extraction

-   Normalized document blocks

-   Source provenance preservation

-   Page-level provenance for PDF content

-   Paragraph/table/row/column provenance for DOCX content

-   Stable document identifiers

-   Unified `DocumentProcessor` abstraction

-   Parser abstraction allowing future document types

### Phase 2 Boundary

Phase 2 does not perform:

-   Resume profile extraction

-   Job-description profile extraction

-   Skill extraction

-   Transformer-based embeddings

-   Semantic similarity

-   Lexical/keyword matching

-   Hybrid matching

-   Skill-gap calculation

-   Candidate-job scoring

-   XAI analysis

-   Career intelligence

-   Recommendations

-   LLM-based analysis

The output of Phase 2 is a normalized `ParsedDocument` containing document blocks and source provenance. This representation is intended to become the input to downstream extraction and analytical stages in later phases.

### Architectural Flow

```
Document bytes
      ↓
DocumentProcessor
      ↓
Document validation
      ↓
PDFParser / DOCXParser
      ↓
Normalized document blocks
      ↓
Source provenance
      ↓
ParsedDocument

```

The `DocumentProcessor` remains an infrastructure component and does not perform analytical interpretation, skill matching, scoring, or recommendations.

### Phase 2 Completion Status

Phase 2 --- Document Processing is implemented and verified.

Verification completed:

-   Backend test suite: 70 passed

-   Parsed-document contract tests: 8 passed

-   Python compilation: passed

-   API route inspection: passed

-   OpenAPI verification: passed

-   Frontend TypeScript verification: passed

-   Frontend production build: passed

-   Git repository hygiene review: completed

-   Temporary `tmp/` directory removed

-   PyMuPDF dependency declared

-   python-docx dependency declared

Phase 2 is considered complete only after the final repository verification and freeze are performed.

**Current Phase:** Phase 2 --- Document Processing

**Next Phase:** Not started

