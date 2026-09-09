PHASE 7 --- CAREER INTELLIGENCE
=============================

Status
------

**COMPLETE --- IMPLEMENTED, INTEGRATED, TESTED, VERIFIED, DOCUMENTED, AND READY TO FREEZE**

Phase 7 of **SkillLens --- XAI-Driven Semantic Skill Gap Analysis using Transformer-Based Language Models** implements the Career Intelligence layer.

The phase extends the existing deterministic analysis pipeline with evidence-backed career-role intelligence while preserving the existing Phase 1--6 architecture and API contracts.

Phase 7 does **not** introduce a second analysis orchestrator or a dedicated career endpoint.

The canonical architecture remains:

```
API
 ↓
ConcreteAnalysisOrchestrator
 ↓
Domain / Analysis Engines
 ↓
Infrastructure

```

* * * * *

1\. Phase 7 Objective
=====================

The objective of Phase 7 was to introduce deterministic Career Intelligence capable of analyzing a candidate's resume and producing:

-   Career-role suitability

-   Career-role fit scores

-   Evidence-backed role rationale

-   Role-fit confidence

-   Seniority intelligence

-   Domain classification

-   Primary and secondary career directions

-   Insufficient-evidence handling

-   Transferable skills

-   Strengths

-   Evidence limitations

-   Career signals

-   Resume-only career analysis

-   Resume + Job Description compatible career analysis

The Career Intelligence system is intentionally deterministic and explainable.

Phase 7 does not introduce:

-   LLM-based career decisions

-   Local Ollama inference

-   Job scraping

-   Recommendation generation

-   Learning recommendations

-   Certification recommendations

-   Project recommendations

-   Recruiter features

-   Job tracking

-   Database-backed career intelligence

-   Dedicated career API endpoints

-   Major frontend redesign

Those capabilities remain outside the Phase 7 scope.

* * * * *

2\. Implementation Strategy
===========================

Phase 7 followed the required development sequence:

```
READ
 ↓
INSPECT
 ↓
REPORT
 ↓
PLAN
 ↓
IMPLEMENT
 ↓
TEST
 ↓
INTEGRATE
 ↓
VERIFY
 ↓
FREEZE

```

Implementation was performed against the actual SkillLens codebase rather than treating previous documentation as the source of truth.

Existing architecture, domain models, orchestrator behavior, API contracts, evidence structures, confidence structures, skill normalization, and Phase 5--6 scoring behavior were inspected before implementation.

* * * * *

3\. Career Domain Contract
==========================

The previous career domain model was replaced with the Phase 7 Career Intelligence contract.

Implemented module:

```
backend/app/domain/career.py

```

CareerSenioriyLevel
-------------------

The supported seniority levels are:

```
ENTRY
JUNIOR
MID
SENIOR
LEAD
UNKNOWN

```

These are represented using the `CareerSeniorityLevel` enum.

The system does not infer seniority from protected attributes.

* * * * *

4\. Career Directions
=====================

Phase 7 defines:

```
PRIMARY
SECONDARY
INSUFFICIENT_EVIDENCE

```

These directions represent the strength of a candidate's evidence-backed suitability for a career role.

They are intentionally distinct from:

-   confidence

-   Phase 6 candidate-vs-JD score

-   skill matching status

A role can therefore have a strong or weak fit independently of the confidence attached to that conclusion.

* * * * *

5\. Role Fit Contract
=====================

Each evaluated role produces a `RoleFit` representation containing:

-   Role title

-   Fit score

-   Career direction

-   Rationale

-   Evidence

-   Confidence

Fit scores are constrained to:

```
0--100

```

The role-fit contract is separate from Phase 6's job-description matching/scoring system.

* * * * *

6\. Career Intelligence Result
==============================

`CareerIntelligence` contains the following major information:

-   Inferred profile

-   Experience level

-   Seniority confidence

-   Seniority evidence

-   Seniority rationale

-   Primary domains

-   Secondary domains

-   Strengths

-   Limitations

-   Transferable skills

-   Career directions

-   Potential roles

-   Role fit

-   Career signals

-   Transition analysis

-   Skill priorities

-   Risks

-   Overall confidence

-   Taxonomy version

-   Engine version

The structure remains compatible with the existing `AnalysisResult` model.

* * * * *

7\. Versioned Career Taxonomy
=============================

New module:

```
backend/app/analysis/career_catalog.py

```

The taxonomy version is:

```
career-taxonomy-v1

```

The taxonomy is deterministic and versioned.

Each role profile contains:

-   Role title

-   Aliases

-   Domain

-   Core skills

-   Supporting skills

-   Typical seniority

-   ESCO identifier where verified and justified

-   Taxonomy version

The role catalogue is represented using immutable role profiles.

* * * * *

8\. Career Role Catalogue
=========================

Phase 7 currently contains 15 deterministic role profiles:

1.  Software Developer

2.  Backend Developer

3.  Frontend Developer

4.  Full Stack Developer

5.  Data Analyst

6.  Data Scientist

7.  Machine Learning Engineer

8.  AI Engineer

9.  Data Engineer

10. DevOps Engineer

11. Cloud Engineer

12. QA / Test Engineer

13. Database Developer

14. Cybersecurity Analyst

15. Business Analyst

Each role belongs to a defined career domain.

The catalogue is intentionally bounded and versioned rather than attempting to create an unbounded role ontology.

* * * * *

9\. Role Aliases
================

The catalogue supports deterministic alias resolution.

For example, equivalent role terminology can resolve to the same canonical role.

Lookup is case-insensitive and normalized.

The implementation does not create arbitrary roles dynamically.

This provides deterministic and reproducible role matching.

* * * * *

10\. ESCO Handling
==================

ESCO identifiers are included only where they are verified and justified.

Phase 7 deliberately avoids fabricated ESCO identifiers.

If an ESCO identifier cannot be justified, the role profile leaves the ESCO URI unset.

This prevents false ontology claims from entering the analysis output.

* * * * *

11\. Career Intelligence Engine
===============================

New module:

```
backend/app/analysis/career_intelligence.py

```

Engine version:

```
phase7-career-intelligence-v1

```

Primary analyzer:

```
CareerIntelligenceAnalyzer

```

The analyzer consumes existing normalized resume intelligence and structured resume information.

It does not create a second orchestration layer.

* * * * *

12\. Input Sources
==================

Career Intelligence uses evidence available from:

-   Normalized resume skills

-   Skill evidence

-   Resume summary

-   Experience

-   Projects

-   Education

-   Certifications

-   Structured resume sections

-   Existing resume profile information

For resume + JD analysis, the existing job-description analysis remains available, but Career Intelligence remains a candidate-career analysis rather than becoming another implementation of Phase 6 job matching.

* * * * *

13\. Skill Normalization
========================

Career Intelligence operates on normalized skills.

The existing deterministic normalization pipeline is preserved.

The system does not perform arbitrary raw-string keyword counting as its primary career classification mechanism.

Skills are normalized before career-role evaluation.

Existing evidence attached to skills is preserved and used in confidence calculations.

* * * * *

14\. Role Fit Calculation
=========================

Role suitability is calculated deterministically.

The Phase 7 role-fit formula is:

```
core skill coverage       × 60
supporting skill coverage × 20
evidence strength         × 10
context strength          × 5
seniority alignment       × 5

```

Therefore:

```
fit_score =
    core_coverage * 60
    + supporting_coverage * 20
    + evidence_strength * 10
    + context_strength * 5
    + seniority_alignment * 5

```

The final score is rounded to two decimal places and constrained to the range:

```
0--100

```

This scoring system is intentionally separate from Phase 6's candidate-vs-job-description score.

* * * * *

15\. Confidence
===============

Role fit and confidence are separate concepts.

Confidence incorporates evidence and contextual factors rather than simply copying the fit score.

The existing confidence model is reused:

```
LOW
MEDIUM
HIGH

```

with the established thresholds:

```
HIGH   >= 0.85
MEDIUM >= 0.65
LOW    < 0.65

```

Confidence includes component-level information and a rationale.

This allows the system to distinguish:

```
high role suitability

```

from:

```
high certainty that the available evidence supports that suitability

```

* * * * *

16\. Seniority Intelligence
===========================

Phase 7 determines:

```
ENTRY
JUNIOR
MID
SENIOR
LEAD
UNKNOWN

```

The system uses evidence in the following general order:

1.  Existing structured experience information

2.  Explicit role-title seniority indicators

3.  Structured experience duration

4.  Summary evidence

5.  Unknown when evidence is insufficient

Where total experience is available, deterministic experience thresholds are used:

```
< 1 year   → ENTRY
< 3 years  → JUNIOR
< 6 years  → MID
< 10 years → SENIOR
>= 10 years → LEAD

```

Explicit seniority terms in actual role titles are handled separately.

Generic mentions such as:

```
"senior systems"
"manager"
"architect"

```

inside unrelated prose are not automatically interpreted as the candidate's seniority.

This prevents false seniority inference.

* * * * *

17\. Seniority Evidence
=======================

Seniority output contains:

-   Seniority level

-   Confidence

-   Evidence

-   Rationale

When evidence is insufficient, the system reports:

```
UNKNOWN

```

rather than fabricating a seniority level.

Evidence limitations are explicitly communicated.

The system does not claim that a candidate is incapable of operating at a particular seniority level merely because the resume lacks sufficient evidence.

* * * * *

18\. Domain Classification
==========================

Career domains are inferred using normalized skills together with available contextual evidence.

Relevant evidence includes:

-   Skills

-   Experience

-   Projects

-   Education

-   Certifications

-   Structured resume context

The system avoids arbitrary keyword-counting as the sole domain classifier.

The strongest domains become:

```
primary_domains

```

and additional supported domains become:

```
secondary_domains

```

The current implementation returns the strongest three primary domains and the next three secondary domains where evidence exists.

* * * * *

19\. Career Direction Classification
====================================

Roles are evaluated and deterministically ranked.

Ranking considers:

1.  Fit score

2.  Confidence

3.  Stable alphabetical role ordering as a deterministic tie-breaker

Direction classification uses the resulting ranking and score thresholds.

The current classification rules are:

```
fit_score < 20
    → INSUFFICIENT_EVIDENCE

top 3 roles with fit_score >= 55
    → PRIMARY

next roles with fit_score >= 35
    → SECONDARY

otherwise
    → INSUFFICIENT_EVIDENCE

```

Only the strongest supported directions are exposed as career directions.

Insufficient-evidence roles are preserved in the analysis logic rather than incorrectly promoted to career recommendations.

* * * * *

20\. Primary and Secondary Career Directions
============================================

The system identifies:

```
PRIMARY
SECONDARY
INSUFFICIENT_EVIDENCE

```

Primary directions represent the strongest evidence-backed career paths.

Secondary directions represent plausible alternatives with meaningful evidence.

Insufficient-evidence directions explicitly communicate that the available resume evidence does not justify a stronger career conclusion.

* * * * *

21\. Transferable Skills
========================

The engine identifies transferable skills from the normalized skill evidence and role/domain context.

Transferable skills are represented independently from role fit.

This prevents the system from treating every detected skill as a role recommendation.

* * * * *

22\. Strengths
==============

Strengths are derived from supported skill and contextual evidence.

Examples include strong concentrations of relevant skills and evidence-backed domain strengths.

Strengths are not generated from unsupported assumptions.

* * * * *

23\. Limitations
================

Career limitations are framed as limitations of available evidence.

The engine does not make absolute claims such as:

```
candidate cannot perform role X

```

when the actual issue is simply:

```
insufficient evidence in the resume

```

This distinction is important for explainability and responsible career analysis.

* * * * *

24\. Evidence Model
===================

Career Intelligence reuses the existing evidence architecture.

Evidence includes:

-   Evidence ID

-   Source type

-   Source document ID

-   Section

-   Optional offsets

-   Evidence type

-   Extractor

-   Relevance

-   Confidence

Synthetic career evidence uses deterministic SHA-256-derived identifiers.

The career engine identifies itself through:

```
phase7-career-intelligence-v1

```

This preserves traceability and reproducibility.

* * * * *

25\. Resume-Only Support
========================

Career Intelligence is available through the existing resume-only analysis flow.

The canonical endpoint remains:

```
/api/v1/analyses/resume

```

No career-specific endpoint was introduced.

The default analysis option enables Career Intelligence:

```
include_career_intelligence = true

```

The feature can explicitly be disabled through the existing analysis options.

When disabled:

```
career_intelligence = null

```

and the career engine version is omitted from the engine-version metadata rather than represented as an invalid null string.

* * * * *

26\. Resume + Job Description Support
=====================================

Career Intelligence is also integrated into:

```
/api/v1/analyses/resume-jd

```

The existing Phase 5/6 matching, gap analysis, scoring, and XAI pipeline remains intact.

Career Intelligence does not replace or recalculate:

-   Skill matching

-   Requirement alignment

-   Candidate-vs-JD scoring

-   Gap analysis

-   XAI

It operates as an additional analysis capability within the same canonical orchestrator.

* * * * *

27\. Orchestrator Integration
=============================

Career Intelligence is integrated into:

```
backend/app/orchestration/concrete_analysis_orchestrator.py

```

The existing:

```
ConcreteAnalysisOrchestrator

```

remains the single canonical analysis orchestrator.

No second orchestrator was introduced.

The orchestrator now conditionally executes Career Intelligence according to:

```
request.options.include_career_intelligence

```

The existing API and analysis pipeline remain backward-compatible.

* * * * *

28\. API Contract
=================

The existing analysis API was preserved.

Available analysis endpoints remain:

```
/api/v1/analyses/resume
/api/v1/analyses/resume-jd
/api/v1/analyses/{analysis_id}

```

No dedicated career endpoint exists.

OpenAPI verification confirmed:

```
OpenAPI version: 3.1.0

```

The generated schema exposes:

```
CareerDirection
CareerDirectionResult
CareerIntelligence
CareerSeniorityLevel

```

through the existing analysis response contract.

* * * * *

29\. Test Coverage
==================

New unit-test module:

```
backend/tests/unit/test_career_intelligence.py

```

The test suite covers:

-   Taxonomy versioning

-   Role catalogue integrity

-   Role lookup

-   Alias normalization

-   Role matching

-   Role-fit scoring

-   Confidence

-   Evidence

-   Seniority

-   Seniority edge cases

-   Domain classification

-   Career directions

-   Transferable skills

-   Strengths

-   Evidence limitations

-   Insufficient evidence

-   Determinism

-   Resume-only analysis

-   Resume + JD compatibility

-   Edge cases

Orchestrator tests were expanded to verify:

-   Career Intelligence integration

-   Resume-only behavior

-   Resume + JD behavior

-   Career Intelligence disabling

-   Engine metadata behavior

API tests were updated to verify the Phase 7 career result.

* * * * *

30\. Verification Results
=========================

Career Intelligence + Orchestrator Tests
----------------------------------------

```
44 passed
5 warnings

```

API Tests
---------

```
14 passed
7 warnings

```

Full Regression
---------------

```
311 passed
7 warnings

```

No test failures remain.

The warnings are existing dependency/deprecation warnings and are not Phase 7 functional failures.

* * * * *

31\. Compilation Verification
=============================

The orchestrator was compiled using:

```
python -m compileall -q

```

Compilation completed successfully.

* * * * *

32\. Diff Verification
======================

The repository was checked using:

```
git diff --check

```

No whitespace errors were reported.

* * * * *

33\. OpenAPI Verification
=========================

OpenAPI generation was executed successfully.

Verified:

```
OpenAPI 3.1.0

```

Existing analysis routes remain intact.

Career schemas are included in the canonical analysis API.

No dedicated career route was introduced.

* * * * *

34\. Files Added
================

Phase 7 introduces:

```
backend/app/analysis/career_catalog.py
backend/app/analysis/career_intelligence.py
backend/tests/unit/test_career_intelligence.py

```

* * * * *

35\. Files Modified
===================

Phase 7 modifies:

```
backend/app/domain/career.py
backend/app/orchestration/concrete_analysis_orchestrator.py
backend/tests/api/test_analysis_api.py
backend/tests/unit/test_analysis_orchestrator.py

```

* * * * *

36\. Architectural Integrity
============================

Phase 7 preserves the established architecture.

The final dependency direction remains:

```
API
 ↓
ConcreteAnalysisOrchestrator
 ↓
CareerIntelligenceAnalyzer
 ↓
Career Taxonomy / Domain / Evidence / Confidence

```

Career Intelligence does not bypass the orchestrator.

It does not create a parallel analysis pipeline.

It does not introduce a second scoring system for candidate-vs-JD analysis.

* * * * *

37\. Determinism
================

Phase 7 is deterministic.

The same normalized resume input produces the same:

-   Role catalogue

-   Role matching

-   Fit scores

-   Career directions

-   Seniority classification

-   Domain classification

-   Evidence identifiers

-   Confidence calculations

-   Ordering

Stable sorting and deterministic identifiers prevent output instability.

* * * * *

38\. Explicit Phase 7 Boundaries
================================

The following are intentionally deferred:

-   Career learning recommendations

-   Certification recommendations

-   Project recommendations

-   Resume improvement recommendations

-   Job recommendations

-   Local LLM / Ollama decisions

-   Job scraping

-   Job database

-   Recruiter features

-   Authentication changes

-   Application tracking

-   PDF career reports

-   Markdown career reports

-   Major frontend redesign

-   Redis

-   Celery

-   Background workers

-   Microservices

These capabilities are not considered missing Phase 7 work.

They are intentionally outside the Phase 7 scope and may be addressed in later phases.

* * * * *

39\. Phase 7 Completion Criteria
================================

Phase 7 is considered complete when all of the following are satisfied:

-   Versioned career taxonomy implemented

-   Deterministic role catalogue implemented

-   Role aliases implemented

-   Core/supporting skills defined

-   Typical seniority defined

-   ESCO handling restricted to verified identifiers

-   Deterministic generalized role-fit scoring implemented

-   Role confidence implemented separately from fit

-   Evidence-backed rationale implemented

-   Seniority intelligence implemented

-   Evidence-based UNKNOWN handling implemented

-   Domain classification implemented

-   Transferable skills implemented

-   Strengths implemented

-   Evidence limitations implemented

-   Primary directions implemented

-   Secondary directions implemented

-   Insufficient-evidence handling implemented

-   Resume-only support implemented

-   Resume + JD support implemented

-   Existing ConcreteAnalysisOrchestrator integrated

-   No second orchestrator introduced

-   No dedicated career endpoint introduced

-   API contract verified

-   OpenAPI verified

-   Unit tests implemented

-   Orchestrator tests updated

-   API tests updated

-   Full regression passed

-   Compilation verified

-   Diff check passed

-   Documentation prepared

* * * * *

40\. Final Phase 7 State
========================

Phase 7 provides SkillLens with a deterministic Career Intelligence layer capable of answering:

```
What career domains are supported by this resume?
Which career roles have the strongest evidence?
How strong is the fit?
How confident is that conclusion?
What seniority level is supported by the evidence?
Which skills are transferable?
What are the candidate's evidence-backed strengths?
Where is evidence insufficient?
What are the primary and secondary career directions?

```

The implementation remains:

```
Deterministic
Evidence-backed
Versioned
Explainable
Tested
API-compatible
Architecturally integrated

```

Phase 7 is therefore **implementation-complete and verification-complete**.

The final Git commit and clean-tree verification are the remaining repository-freeze operations.