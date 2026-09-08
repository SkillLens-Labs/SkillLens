PHASE 5 --- JD INTELLIGENCE & RESUME--JD MATCHING
==============================================

Status
------

**Phase 5: COMPLETE AND FROZEN**

Phase 5 extends the existing SkillLens resume intelligence architecture with Job Description (JD) intelligence and structured Resume--JD matching.

The implementation preserves the Phase 1--4 architecture and reuses the existing document processing, skill normalization, ESCO mapping, evidence, confidence, orchestration, and analysis-result infrastructure.

Phase 5 does **not** implement final candidate-job scoring or XAI explanations. Those responsibilities remain explicitly reserved for Phase 6.

* * * * *

Phase 5 Objective
-----------------

The objective of Phase 5 was to introduce a complete JD intelligence and Resume--JD comparison layer capable of:

-   Processing job-description documents

-   Interpreting JD structure

-   Extracting job requirements

-   Classifying requirements as required or preferred

-   Classifying requirement categories

-   Extracting JD skills

-   Reusing the existing skill normalization system

-   Reusing ESCO mapping

-   Building a structured `JobProfile`

-   Matching resume skills against JD skills

-   Supporting exact and semantic relationships

-   Aligning non-skill requirements

-   Preserving evidence and confidence

-   Producing a structured `MatchingResult`

-   Integrating matching into the canonical `AnalysisResult`

-   Exposing Resume--JD analysis through the API

-   Maintaining complete resume-only backward compatibility

-   Establishing a clean Phase 5 → Phase 6 boundary

* * * * *

Architectural Principle
-----------------------

Phase 5 does not create a second resume analysis pipeline.

The existing architecture remains:

```
DocumentProcessor
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
ResumeQualityAnalyzer
        ↓
ATSIntelligenceAnalyzer
        ↓
AnalysisResult

```

Phase 5 extends the architecture with a parallel JD intelligence path:

```
Resume Document
      ↓
DocumentProcessor
      ↓
Resume Intelligence Pipeline
      ↓
ResumeProfile
      │
      │
      ├───────────────┐
      │               │
      ↓               ↓
Job Description   Resume--JD Matching
      ↓               ↑
DocumentProcessor    │
      ↓               │
JDStructureInterpreter
      ↓               │
JDRequirementExtractor
      ↓               │
JDSkillExtractor
      ↓               │
JDSkillNormalizer
      ↓               │
ESCOMapper
      ↓               │
JDProfileBuilder
      ↓               │
JobProfile ──────────┘
                      ↓
                MatchingResult
                      ↓
                AnalysisResult

```

The existing `ConcreteAnalysisOrchestrator` remains the central integration point.

* * * * *

5.1 JD Document Processing
==========================

Job descriptions are processed through the existing `DocumentProcessor`.

The implementation does not introduce a separate document parser.

The same document-processing infrastructure is reused for:

-   File validation

-   File-type detection

-   Document parsing

-   Document blocks

-   Document identifiers

-   Source provenance

This ensures that resume and JD documents follow the same low-level document-processing contract.

* * * * *

5.2 JD Structure Interpretation
===============================

A new JD structure interpreter was introduced:

```
backend/app/analysis/jd_structure.py

```

The interpreter provides structured JD sections using:

```
JDSectionType
JDSection
StructuredJobDescription
JDStructureInterpreter

```

Supported section types include:

-   HEADER

-   SUMMARY

-   RESPONSIBILITIES

-   REQUIRED_QUALIFICATIONS

-   PREFERRED_QUALIFICATIONS

-   SKILLS

-   EXPERIENCE

-   EDUCATION

-   CERTIFICATIONS

-   UNKNOWN

The interpreter relies on actual document heading blocks rather than treating arbitrary paragraph text as a section heading.

This preserves the structural semantics of the parsed document and avoids unreliable text-based section inference.

* * * * *

5.3 JD Requirement Extraction
=============================

A dedicated requirement extractor was introduced:

```
backend/app/analysis/jd_requirement_extractor.py

```

Requirements are represented using the existing domain contracts in `matching.py`.

Each requirement contains:

-   Requirement ID

-   Requirement text

-   Requirement type

-   Requirement category

-   Optional linked skill ID

-   Optional canonical skill name

-   Evidence

-   Confidence

-   Metadata

Requirement types:

```
REQUIRED
PREFERRED

```

Requirement categories:

```
SKILL
EXPERIENCE
EDUCATION
CERTIFICATION

```

The extractor identifies requirements from requirement-oriented JD sections.

Required requirements are primarily sourced from:

-   Required qualifications

-   Experience

-   Education

-   Certifications

-   Skills

Preferred requirements are sourced from:

-   Preferred qualifications

The extractor also applies deterministic heuristics for identifying experience, education, and certification requirements.

* * * * *

5.4 Required vs Preferred Classification
========================================

Phase 5 explicitly distinguishes mandatory requirements from preferred requirements.

This distinction is represented through:

```
JobRequirementType.REQUIRED
JobRequirementType.PREFERRED

```

The distinction is preserved through:

```
JobRequirement
RequirementAlignment
MatchingResult
AnalysisResult

```

This allows downstream phases to reason about requirement importance without embedding final scoring logic into Phase 5.

* * * * *

5.5 Evidence and Confidence
===========================

JD requirements preserve structured evidence.

Each requirement records evidence associated with the source JD document.

The implementation uses:

```
EvidenceSource.JOB_DESCRIPTION

```

Confidence is also retained.

The requirement extractor uses deterministic high-confidence extraction for directly identified requirements.

JD skill extraction distinguishes between:

```
EXPLICIT
CONTEXTUAL

```

evidence.

Explicit JD skill mentions receive higher confidence than contextual mentions.

Phase 5 preserves evidence and confidence but does not convert them into final candidate-job scores.

* * * * *

5.6 JD Skill Extraction
=======================

A dedicated JD skill extractor was introduced:

```
backend/app/analysis/jd_skill_extractor.py

```

The extractor produces:

```
JDSkillMention
JDSkillExtractionResult

```

JD skills are identified from:

### Explicit sections

-   Skills

-   Required Qualifications

-   Preferred Qualifications

### Contextual sections

-   Summary

-   Responsibilities

-   Experience

The implementation uses the existing canonical skill vocabulary rather than introducing a second independent skill dictionary.

The extractor records:

-   Raw skill text

-   JD section type

-   Evidence type

-   Source document block

-   Character offsets

-   Extractor identifier

-   Confidence

-   Metadata

* * * * *

5.7 Reuse of Existing Skill Normalization
=========================================

A dedicated adapter was introduced:

```
backend/app/analysis/jd_skill_normalizer.py

```

The JD normalizer reuses the existing `SkillNormalizer`.

It does not create a second normalization vocabulary.

JD skill mentions are adapted into the existing resume-compatible skill mention contract and passed through the existing normalization pipeline.

This ensures that:

-   Resume skills

-   JD skills

share the same canonicalization behavior.

JD provenance is preserved through metadata including:

```
source = job_description
jd_section_type = ...

```

* * * * *

5.8 ESCO Mapping Reuse
======================

Phase 5 continues to use the existing ESCO mapping layer.

JD skills are normalized first and then mapped through the existing ESCO mapper.

No duplicate taxonomy mapping system was introduced.

This allows Resume--JD matching to use:

-   Canonical skill identity

-   ESCO identity

-   Existing normalization behavior

-   Existing evidence

-   Existing confidence

The ESCO version is recorded as:

```
1.2.1

```

* * * * *

5.9 JobProfile Construction
===========================

A dedicated JD profile builder was introduced:

```
backend/app/analysis/jd_profile_builder.py

```

The builder creates the existing domain-level:

```
JobProfile

```

The builder extracts and organizes:

-   Job title

-   Company

-   Summary

-   Responsibilities

-   Required skills

-   Preferred skills

-   Technical skills

-   Soft skills

-   Domain skills

-   Experience requirements

-   Education requirements

-   Seniority

-   Metadata

The builder also retains the underlying normalized skill objects and requirements internally for downstream matching.

No final candidate-job score is generated by the profile builder.

* * * * *

5.10 Resume--JD Skill Matching
=============================

A dedicated skill matcher was introduced:

```
backend/app/analysis/skill_matcher.py

```

The matcher compares normalized resume skills against normalized JD skills.

Supported relationships include:

```
EXACT
STRONG_SEMANTIC
PARTIAL
RELATED
UNMATCHED

```

The matcher preserves:

-   Resume skill ID

-   JD skill ID

-   Relationship

-   Similarity

-   Confidence

-   Evidence

-   Rationale

Similarity is bounded between:

```
0.0 and 1.0

```

The matcher is responsible for relationship detection and matching evidence.

It does not calculate a final candidate-job score.

* * * * *

5.11 Semantic Matching
======================

Phase 5 introduces transformer-based semantic similarity.

The selected semantic model is:

```
all-MiniLM-L6-v2

```

The implementation uses sentence-transformers and cosine similarity.

The semantic model configuration is explicit.

The model produces 384-dimensional embeddings.

Semantic similarity is used as a matching signal rather than as a final candidate-job score.

The dependency stack added for Phase 5 includes:

```
sentence-transformers==6.0.1
torch==2.8.0
transformers==5.16.1

```

PyTorch MPS availability was verified on the development environment.

The implementation also avoids repeatedly loading the semantic model during individual matching operations.

* * * * *

5.12 Matching Relationships
===========================

Phase 5 supports multiple relationship types rather than treating all matches as simple exact string equality.

The canonical relationships are:

```
EXACT
STRONG_SEMANTIC
PARTIAL
RELATED
UNMATCHED

```

This provides the foundation for more sophisticated scoring in Phase 6.

Phase 5 deliberately stops at structured matching evidence.

* * * * *

5.13 Requirement Alignment
==========================

A dedicated requirement aligner was introduced:

```
backend/app/analysis/requirement_aligner.py

```

Requirement alignment covers more than skills.

Supported requirement categories include:

```
SKILL
EXPERIENCE
EDUCATION
CERTIFICATION

```

Each alignment contains:

-   Requirement ID

-   Match status

-   Evidence

-   Confidence

-   Optional rationale

Match statuses are:

```
MATCHED
PARTIAL
UNMATCHED
UNKNOWN

```

`UNKNOWN` is intentionally supported.

Missing evidence is not automatically interpreted as confirmed absence.

This prevents the system from making unsupported claims about a candidate.

* * * * *

5.14 MatchingResult Domain Contract
===================================

The canonical matching domain model was expanded in:

```
backend/app/domain/matching.py

```

The resulting structure contains:

```
MatchingResult
    ├── skill_matches
    ├── requirement_alignments
    ├── confidence
    ├── evidence
    └── metadata

```

The domain model explicitly excludes:

-   Final candidate-job score

-   Final match percentage

-   XAI explanation engine

-   Career intelligence

-   Recommendation engine

Those belong to later phases.

* * * * *

5.15 AnalysisResult Integration
===============================

Phase 5 integrates matching into the canonical:

```
AnalysisResult

```

The analysis mode for Resume--JD analysis is:

```
RESUME_JD

```

The result can contain:

```
resume_document_id
job_document_id
resume_profile
job_profile
matching
metadata

```

The existing resume-only mode remains:

```
RESUME_ONLY

```

The Resume--JD branch therefore extends the existing analysis architecture instead of creating a separate result format.

* * * * *

5.16 ConcreteAnalysisOrchestrator Integration
=============================================

`ConcreteAnalysisOrchestrator` was extended with:

```
analyze_resume_jd(...)

```

The Phase 5 orchestration flow is:

```
Resume Input
    ↓
DocumentProcessor
    ↓
Resume Structure
    ↓
Resume Skill Extraction
    ↓
Resume Skill Normalization
    ↓
ESCO Mapping
    ↓
ResumeProfile

Job Description Input
    ↓
DocumentProcessor
    ↓
JD Structure
    ↓
JD Requirement Extraction
    ↓
JD Skill Extraction
    ↓
JD Skill Normalization
    ↓
ESCO Mapping
    ↓
JobProfile

ResumeProfile + JobProfile
    ↓
SkillMatcher
    ↓
RequirementAligner
    ↓
MatchingResult
    ↓
AnalysisResult

```

Optional dependency injection was added for the new JD and matching components.

The existing `analyze_resume()` path remains intact.

* * * * *

5.17 API Integration
====================

The previously reserved endpoint was integrated:

```
POST /api/v1/analyses/resume-jd

```

The endpoint accepts:

```
resume
job_description
options
client_metadata

```

Both documents are read and passed into the existing orchestration layer.

The endpoint returns:

```
AnalysisResponse

```

with HTTP status:

```
200

```

Validation errors continue to use the standard API validation response.

Existing endpoints remain preserved:

```
GET /api/v1/analyses/{analysis_id}

DELETE /api/v1/analyses/{analysis_id}

```

The API layer remains responsible only for:

-   HTTP handling

-   File input

-   Request parsing

-   Response serialization

Matching algorithms remain inside the analysis/orchestration layers.

* * * * *

5.18 OpenAPI Verification
=========================

The final OpenAPI schema was verified using the actual global API prefix.

Verified path:

```
/api/v1/analyses/resume-jd

```

Verification confirmed:

```
METHODS: ['post']
POST STATUS: ['200', '422']
RESPONSE MODEL: AnalysisResponse

```

OpenAPI verification result:

```
OPENAPI VERIFICATION: PASS

```

* * * * *

5.19 Backward Compatibility
===========================

Resume-only analysis was explicitly regression-tested after Phase 5 integration.

The existing endpoint remains:

```
POST /api/v1/analyses/resume

```

Resume-only analysis continues to use the established Phase 1--4 pipeline.

Phase 5 does not require a JD document for resume-only analysis.

This confirms that the JD intelligence layer is an extension rather than a replacement of the existing resume intelligence architecture.

* * * * *

5.20 Testing
============

Phase 5 introduced dedicated tests for:

```
test_phase5_domain_contracts.py
test_jd_structure.py
test_jd_requirement_extractor.py
test_jd_skill_extractor.py
test_jd_skill_normalizer.py
test_jd_profile_builder.py
test_skill_matcher.py
test_requirement_aligner.py

```

Additional API and orchestrator tests were updated for Resume--JD analysis.

The JD fixture used for endpoint validation is:

```
backend/tests/fixtures/phase5_sample_job_description.docx

```

The fixture contains structured JD headings including:

-   Summary

-   Responsibilities

-   Required Qualifications

-   Preferred Qualifications

-   Certifications

* * * * *

5.21 Test Results
=================

Phase 5 focused tests were executed during implementation.

The final complete test suite was executed with:

```
PYTHONPATH=. pytest backend/tests -q

```

Final result:

```
245 passed
7 warnings
11.94s

```

The warnings are dependency-level deprecation/future warnings involving libraries such as:

-   Starlette/httpx

-   AnyIO

-   PyMuPDF/Swig

No test failures remained.

* * * * *

5.22 Compilation Verification
=============================

All changed and newly created Python modules were compiled using:

```
python -m compileall -q

```

Compilation completed successfully with no errors.

The primary Phase 5 orchestration and API modules were also individually verified using:

```
python -m py_compile

```

No syntax or compilation errors remained.

* * * * *

5.23 Diff and Repository Verification
=====================================

The implementation was checked using:

```
git diff --check

```

No whitespace errors were reported.

The changed and newly created files were reviewed to ensure that:

-   Phase 5 functionality is contained within the intended architecture

-   No duplicate resume pipeline was introduced

-   No duplicate skill vocabulary was introduced

-   No duplicate ESCO mapping layer was introduced

-   No Phase 6 scoring engine was introduced

-   No Phase 6 XAI engine was introduced

-   No unrelated architectural redesign was introduced

* * * * *

5.24 Phase Boundary --- Phase 6
=============================

Phase 5 intentionally stops before final scoring and explainability.

The output of Phase 5 is structured evidence for downstream intelligence:

```
ResumeProfile
+
JobProfile
+
MatchingResult

```

Phase 6 owns:

```
Final candidate-job scoring
Score aggregation
Weighted requirement scoring
Skill-gap scoring
XAI explanations
Explainability of score decisions
Final candidate-job intelligence

```

Therefore Phase 5 does not contain:

```
Final Match Score
Overall Candidate Score
Skill Gap Score
XAI Engine
SHAP-based Resume--JD explanation
Career Intelligence
Recommendation Engine

```

This boundary is intentional and is part of the Phase 5 architecture contract.

* * * * *

5.25 Phase 5 Files Added
========================

The following major implementation files were introduced:

```
backend/app/analysis/jd_structure.py
backend/app/analysis/jd_requirement_extractor.py
backend/app/analysis/jd_skill_extractor.py
backend/app/analysis/jd_skill_normalizer.py
backend/app/analysis/jd_profile_builder.py
backend/app/analysis/skill_matcher.py
backend/app/analysis/requirement_aligner.py

```

Phase 5 test files include:

```
backend/tests/unit/test_phase5_domain_contracts.py
backend/tests/unit/test_jd_structure.py
backend/tests/unit/test_jd_requirement_extractor.py
backend/tests/unit/test_jd_skill_extractor.py
backend/tests/unit/test_jd_skill_normalizer.py
backend/tests/unit/test_jd_profile_builder.py
backend/tests/unit/test_skill_matcher.py
backend/tests/unit/test_requirement_aligner.py

```

Fixture:

```
backend/tests/fixtures/phase5_sample_job_description.docx

```

Existing files extended include:

```
backend/app/domain/matching.py
backend/app/orchestration/analysis_orchestrator.py
backend/app/orchestration/concrete_analysis_orchestrator.py
backend/app/schemas/requests.py
backend/app/api/routes/analyses.py
backend/requirements.txt

```

* * * * *

5.26 Phase 5 Final Architecture
===============================

The resulting Phase 5 architecture is:

```
                    ┌─────────────────────┐
                    │   Resume Document   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ DocumentProcessor   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Resume Intelligence │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    ResumeProfile    │
                    └──────────┬──────────┘
                               │
                               │
                               │
                               ▼
                    ┌─────────────────────┐
                    │    SkillMatcher     │
                    └──────────┬──────────┘
                               │
                               │
┌──────────────────┐           │
│ Job Description  │           │
└────────┬─────────┘           │
         │                     │
         ▼                     │
┌──────────────────┐           │
│DocumentProcessor │           │
└────────┬─────────┘           │
         │                     │
         ▼                     │
┌──────────────────┐           │
│ JD Structure     │           │
└────────┬─────────┘           │
         │                     │
         ├──────────────────┐  │
         ▼                  ▼  │
┌──────────────────┐  ┌──────────────────┐
│ JD Requirements  │  │ JD Skill         │
│ Extractor        │  │ Extractor        │
└────────┬─────────┘  └────────┬─────────┘
         │                     │
         │                     ▼
         │            ┌──────────────────┐
         │            │ Existing Skill   │
         │            │ Normalizer       │
         │            └────────┬─────────┘
         │                     │
         │                     ▼
         │            ┌──────────────────┐
         │            │ Existing ESCO    │
         │            │ Mapper           │
         │            └────────┬─────────┘
         │                     │
         └──────────┬──────────┘
                    ▼
           ┌──────────────────┐
           │    JobProfile    │
           └────────┬─────────┘
                    │
                    ▼
           ┌──────────────────┐
           │RequirementAligner│
           └────────┬─────────┘
                    │
                    ▼
           ┌──────────────────┐
           │ MatchingResult   │
           └────────┬─────────┘
                    │
                    ▼
           ┌──────────────────┐
           │  AnalysisResult  │
           └──────────────────┘

```

* * * * *

5.27 Phase 5 Completion Criteria
================================

The following Phase 5 objectives are complete:

-   JD document processing

-   JD structure interpretation

-   JD requirement extraction

-   Required/preferred classification

-   Requirement categorization

-   JD skill extraction

-   Existing skill normalization reuse

-   Existing ESCO mapping reuse

-   JobProfile construction

-   Semantic skill matching

-   Exact/semantic relationship classification

-   Requirement alignment

-   Evidence preservation

-   Confidence preservation

-   MatchingResult integration

-   AnalysisResult integration

-   Resume--JD API integration

-   OpenAPI verification

-   Resume-only regression verification

-   Full test-suite verification

-   Compilation verification

-   Diff verification

-   Phase boundary enforcement

* * * * *

5.28 Final Phase 5 Status
=========================

Phase 5 --- **JD Intelligence & Resume--JD Matching** is fully implemented, integrated, tested, documented, and frozen.

Final verified state:

```
Resume-only analysis
        +
JD intelligence
        +
Resume--JD matching
        +
Requirement alignment
        +
Evidence and confidence
        +
Semantic similarity
        ↓
Canonical AnalysisResult

```

Final test status:

```
245 passed
7 warnings

```

The warnings are dependency-level warnings and do not represent project test failures.

Phase 5 establishes the complete structured Resume--JD evidence layer required by the next stage of SkillLens.

**Phase 6 is the designated owner of final candidate-job scoring and XAI.**

* * * * *

Freeze Declaration
------------------

```
PHASE 5 --- COMPLETE
STATUS --- FROZEN

```

No additional Phase 5 feature expansion is required unless a defect or contract violation is discovered.

Future work should proceed under the Phase 6 scope.