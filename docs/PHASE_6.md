# PHASE 6 — FINAL CANDIDATE-JOB SCORING, SKILL GAP ANALYSIS & XAI

## Phase 6 Status

**COMPLETE AND FROZEN**

Phase 6 of SkillLens has been implemented, integrated into the canonical analysis orchestrator, regression-tested, and verified.

## Objective

Phase 6 consumes the structured outputs produced by Phase 5 and provides:
PHASE 6 --- FINAL CANDIDATE-JOB SCORING, SKILL GAP ANALYSIS & XAI
===============================================================

**Project:** SkillLens\
**Project Title:** XAI-Driven Semantic Skill Gap Analysis using Transformer-Based Language Models\
**Phase:** 6\
**Phase Name:** Final Candidate-Job Scoring, Skill Gap Analysis & XAI\
**Status:** COMPLETE AND FROZEN\
**Architecture:** Modular Monolith\
**Primary Integration Point:** `ConcreteAnalysisOrchestrator`

* * * * *

1\. PHASE 6 STATUS
==================

Phase 6 has been fully implemented, integrated, tested, verified, documented, and frozen.

Phase 6 extends the existing Phase 5 Resume + Job Description intelligence pipeline with:

-   deterministic candidate-job scoring

-   requirement-aware skill-gap analysis

-   required/preferred scoring separation

-   explicit UNKNOWN handling

-   transparent score contribution decomposition

-   deterministic explainability

-   evidence-preserving explanations

-   confidence-preserving explanations

-   Resume + JD `AnalysisResult` integration

-   API-level integration

-   regression compatibility with Resume-only analysis

-   dedicated Phase 6 test coverage

-   engine version registration

Phase 6 does not replace the Phase 5 matching or requirement-alignment engines.

Instead, it consumes their authoritative outputs and adds the next analytical layer.

Final verification:

```
Phase 6 targeted tests:
64 passed, 7 warnings

Full backend regression:
281 passed, 7 warnings

Test failures:
0

```

Final source validation:

```
git diff --check
PASS

```

Phase 6 is therefore considered:

**COMPLETE AND FROZEN**

* * * * *

2\. PHASE 6 OBJECTIVE
=====================

The objective of Phase 6 was to implement the final deterministic analytical layer that operates after Phase 5 Resume + JD matching and requirement alignment.

The Phase 5 pipeline established:

-   Job Description structure

-   Job requirements

-   required/preferred classification

-   JD skills

-   skill normalization

-   ESCO mapping

-   Resume skills

-   Resume--JD skill matching

-   requirement alignment

-   evidence

-   confidence

Phase 6 consumes those results and determines:

1.  how well the candidate satisfies the job requirements

2.  which requirements are matched

3.  which requirements are partially matched

4.  which requirements are unmatched

5.  which requirements remain unknown

6.  how required and preferred requirements affect the score

7.  how other available dimensions affect the score

8.  how individual results contribute to the final score

9.  why the final score has its value

10. how the existing analytical results can be explained transparently

The key architectural principle was:

> Phase 6 explains and scores existing analytical results rather than duplicating Phase 5 intelligence.

* * * * *

3\. PHASE 6 ARCHITECTURAL PRINCIPLE
===================================

Phase 6 follows the existing SkillLens modular architecture.

The canonical flow is:

```
Resume
   |
   v
Resume Processing
   |
   v
Resume Profile
   |
   |
Job Description
   |
   v
JD Processing
   |
   v
Job Profile
   |
   v
JD Requirements + JD Skills
   |
   +-----------------------------+
   |                             |
   v                             v
Skill Matching              Requirement Alignment
   |                             |
   +-------------+---------------+
                 |
                 v
        Phase 6 Gap Analysis
                 |
                 v
        Phase 6 Deterministic
             Scoring
                 |
                 v
        Phase 6 Deterministic XAI
                 |
                 v
          AnalysisResult
                 |
                 v
              API

```

The existing:

```
ConcreteAnalysisOrchestrator

```

remains the single orchestration authority.

Phase 6 does not create another orchestrator.

* * * * *

4\. SINGLE ORCHESTRATOR RULE
============================

One of the most important Phase 6 architecture constraints was preservation of the existing orchestration model.

The project already uses:

```
ConcreteAnalysisOrchestrator

```

as the implementation of the analysis workflow.

Phase 6 therefore extends that orchestrator.

It does not introduce:

```
Phase6Orchestrator
ScoringOrchestrator
XAIOrchestrator
CandidateJobOrchestrator

```

or any other second workflow authority.

The Phase 6 components are analytical engines:

```
GapAnalyzer
ScoringAnalyzer
XAIAnalyzer

```

They are not workflow orchestrators.

The resulting architecture remains:

```
API
 |
 v
ConcreteAnalysisOrchestrator
 |
 +--> Resume analysis
 |
 +--> JD analysis
 |
 +--> Skill matching
 |
 +--> Requirement alignment
 |
 +--> Gap analysis
 |
 +--> Scoring
 |
 +--> XAI
 |
 v
AnalysisResult

```

* * * * *

5\. PHASE 6 INPUT CONTRACT
==========================

Phase 6 does not independently discover whether a candidate possesses a skill.

It consumes Phase 5 outputs.

The principal Phase 5 inputs are:

```
ResumeProfile
JobProfile
MatchingResult
JobRequirement
SkillMatch
RequirementAlignment
Evidence
Confidence

```

The scoring layer uses:

```
JobProfile
JobRequirement[]
MatchingResult
ResumeSkill[]
JobSkill[]

```

The gap layer uses:

```
JobRequirement[]
MatchingResult
ResumeSkill[]
JobSkill[]

```

The XAI layer uses:

```
ScoringResult
SkillAnalysis
MatchingResult
ResumeSkill[]
JobSkill[]

```

This separation prevents Phase 6 from silently becoming a duplicate implementation of matching or requirement alignment.

* * * * *

6\. PHASE 6 OUTPUTS
===================

Phase 6 produces three primary analytical outputs:

```
SkillAnalysis
ScoringResult
XAIResult

```

These are attached to the canonical:

```
AnalysisResult

```

for Resume + JD analysis.

The resulting structure is conceptually:

```
AnalysisResult
|
+-- resume_profile
|
+-- job_profile
|
+-- matching
|
+-- skill_analysis
|
+-- scoring
|
+-- xai
|
+-- resume_quality
|
+-- ats_intelligence
|
+-- career_intelligence
|
+-- recommendations
|
+-- metadata

```

Resume-only analysis remains compatible with the existing contract.

* * * * *

7\. RESUME-ONLY COMPATIBILITY
=============================

Phase 6 must not break Resume-only analysis.

The Phase 6 engines require Job Description information.

Therefore:

```
RESUME

```

continues through the existing Resume-only pipeline.

Phase 6 scoring and XAI are not executed in Resume-only mode.

The resulting behavior remains:

```
skill_analysis = existing/default empty analysis structure
scoring = None
xai = None

```

This preserves backward compatibility.

The Phase 6 implementation therefore does not force job-specific scoring onto Resume-only requests.

* * * * *

8\. RESUME + JD EXECUTION FLOW
==============================

For Resume + JD analysis, the canonical execution flow is now:

```
1\. Parse Resume
2. Build Resume Profile
3. Parse Job Description
4. Build Job Profile
5. Extract JD Requirements
6. Extract JD Skills
7. Normalize/map skills
8. Match Resume Skills against JD Skills
9. Align requirements
10. Run GapAnalyzer
11. Run ScoringAnalyzer
12. Run XAIAnalyzer
13. Attach Phase 6 results to AnalysisResult
14. Generate metadata
15. Return API response

```

Phase 6 starts only after Phase 5 matching and alignment are available.

* * * * *

9\. PHASE 6 DOMAIN CONTRACT CHANGES
===================================

Phase 6 required domain-level contracts for:

-   score contributions

-   scoring output

-   skill gaps

-   skill analysis

The existing domain model design was extended rather than replaced.

Modified:

```
backend/app/domain/scoring.py
backend/app/domain/gaps.py

```

Existing:

```
backend/app/domain/xai.py

```

was reused as the canonical XAI result contract.

* * * * *

10\. SCORING DOMAIN MODEL
=========================

The scoring domain now contains:

```
DimensionScore
ScoreAdjustment
ScoreContribution
ScoringResult

```

* * * * *

11\. DIMENSION SCORE
====================

`DimensionScore` represents an individual scoring dimension.

Fields:

```
dimension
score
weight

```

The score is constrained to:

```
0.0 - 100.0

```

The weight is constrained to:

```
0.0 - 1.0

```

This creates a stable public representation for dimension-level scoring.

* * * * *

12\. SCORE ADJUSTMENT
=====================

`ScoreAdjustment` provides the domain representation for score adjustments:

```
reason
value

```

Phase 6 does not use arbitrary penalties or bonuses to manipulate the final candidate score.

The model exists as a domain contract for explicit adjustments if they are ever legitimately required by the scoring contract.

The implemented Phase 6 scorer does not introduce arbitrary penalty or bonus logic.

* * * * *

13\. SCORE CONTRIBUTION
=======================

Phase 6 introduces explicit score contribution decomposition.

`ScoreContribution` contains:

```
contribution_id
dimension
source_type
source_id
score
weight
contribution
rationale
requirement_type

```

This is a central XAI foundation.

Each contribution can therefore answer:

```
What contributed?
Which dimension?
Which source?
What score?
What weight?
What mathematical contribution?
Why?
Was it required or preferred?

```

* * * * *

14\. CONTRIBUTION MODEL
=======================

The conceptual contribution formula is:

```
contribution = score × weight

```

using normalized internal scores.

For example:

```
source score = 1.0
dimension weight = 0.50

contribution = 1.0 × 0.50
             = 0.50

```

The contribution is therefore mathematically traceable.

It is not a generated natural-language justification detached from the scoring calculation.

* * * * *

15\. SCORING RESULT
===================

`ScoringResult` contains:

```
overall_score
skill_score
required_skill_score
preferred_skill_score
experience_score
education_score
domain_score
dimension_scores
weights
contributions
penalties
bonuses
confidence

```

The public score range is:

```
0.0 - 100.0

```

The internal scoring calculations are normalized to:

```
0.0 - 1.0

```

* * * * *

16\. SCORING WEIGHTS
====================

The Phase 6 scoring policy is explicitly configurable and deterministic.

The canonical weights are:

```
Required Skills     = 0.50
Preferred Skills    = 0.15
Experience          = 0.15
Education           = 0.10
Domain              = 0.10
--------------------------------
Total               = 1.00

```

Therefore:

```
Required Skills + Preferred Skills = Skill influence

```

with skills contributing:

```
0.65

```

of the total available scoring weight.

* * * * *

17\. REQUIRED SKILLS
====================

Required skills have the highest individual influence.

Weight:

```
0.50

```

Required skill satisfaction is therefore treated as substantially more important than preferred skills.

This reflects the distinction between:

```
mandatory requirement

```

and:

```
preferred requirement

```

already established by Phase 5.

* * * * *

18\. PREFERRED SKILLS
=====================

Preferred skills have a separate scoring dimension.

Weight:

```
0.15

```

Preferred skills affect the score but do not have the same influence as required skills.

This preserves the semantic distinction established by the JD requirement extractor.

* * * * *

19\. EXPERIENCE
===============

Experience receives:

```
0.15

```

Experience is scored only when sufficient structured evidence exists.

The scorer does not fabricate experience evidence.

If the relevant dimension cannot be evaluated, it becomes unavailable rather than automatically becoming zero.

* * * * *

20\. EDUCATION
==============

Education receives:

```
0.10

```

Education follows the same evidence-aware availability principle.

Absence of usable structured evidence does not automatically mean:

```
education score = 0

```

Instead, the dimension can be unavailable.

* * * * *

21\. DOMAIN
===========

Domain receives:

```
0.10

```

Domain scoring uses existing `JobProfile.domain_skills` information when it is explicitly available.

It does not invent a domain classification.

Existing skill matching relationships are used rather than creating a second semantic matching implementation.

* * * * *

22\. CERTIFICATION HANDLING
===========================

Certification does not receive an independent scoring dimension in the Phase 6 weighting model.

This is intentional.

The Phase 6 scoring dimensions are:

```
required skills
preferred skills
experience
education
domain

```

Certification requirements remain part of the requirement/alignment model but are not silently converted into an additional weighted dimension.

* * * * *

23\. ALIGNMENT VALUES
=====================

Phase 6 uses the authoritative Phase 5 requirement alignment status.

The deterministic scoring mapping is:

```
MATCHED     = 1.0
PARTIAL     = 0.5
UNMATCHED   = 0.0
UNKNOWN     = excluded

```

This mapping is explicit and deterministic.

* * * * *

24\. MATCHED
============

A requirement with:

```
status = matched

```

receives:

```
1.0

```

in the normalized scoring calculation.

This means the requirement is fully satisfied according to the existing Phase 5 alignment result.

* * * * *

25\. PARTIAL
============

A requirement with:

```
status = partial

```

receives:

```
0.5

```

This represents partial satisfaction.

The value is deliberately deterministic and transparent.

* * * * *

26\. UNMATCHED
==============

A requirement with:

```
status = unmatched

```

receives:

```
0.0

```

This represents an established failure to match according to the Phase 5 alignment result.

* * * * *

27\. UNKNOWN
============

UNKNOWN is fundamentally different from UNMATCHED.

An:

```
UNKNOWN

```

result means that the available evidence is insufficient to make a reliable determination.

It does not mean:

```
candidate does not have the skill

```

Therefore UNKNOWN is excluded from the denominator.

UNKNOWN must never silently become:

```
0

```

and must never be treated as an explicit candidate failure.

* * * * *

28\. UNKNOWN DENOMINATOR RULE
=============================

For a dimension containing UNKNOWN requirements:

```
UNKNOWN requirements are excluded from both:
- numerator
- denominator

```

This prevents lack of evidence from becoming a negative score.

For example:

```
Required requirements:
A = MATCHED
B = UNKNOWN
C = UNMATCHED

```

The available requirement values are:

```
A = 1.0
C = 0.0

```

Therefore:

```
dimension score = (1.0 + 0.0) / 2
                = 0.5

```

B is not counted as zero.

* * * * *

29\. UNAVAILABLE DIMENSIONS
===========================

If every relevant requirement in a dimension is UNKNOWN, that dimension is unavailable.

For example:

```
Required skills:
all UNKNOWN

```

means:

```
required skill dimension = unavailable

```

It does not mean:

```
required skill score = 0

```

This distinction is essential for evidence-aware scoring.

* * * * *

30\. OVERALL SCORE RENORMALIZATION
==================================

If one or more dimensions are unavailable, the overall score does not blindly divide by the original total weight.

Instead:

```
overall =
sum(available_dimension_score × dimension_weight)
/
sum(available_dimension_weight)

```

This renormalizes the available dimensions.

Example:

```
Required Skills = unavailable
Preferred Skills = 0.8
Experience = 0.7
Education = 0.9
Domain = 0.6

```

The required-skill weight is excluded from the denominator.

The available weights are renormalized mathematically.

This prevents missing evidence from artificially lowering the score.

* * * * *

31\. MATCH STRENGTH VS CONFIDENCE
=================================

Phase 6 explicitly preserves the distinction between:

```
similarity / match strength

```

and:

```
confidence

```

Similarity answers:

```
How strongly do the two skills match?

```

Confidence answers:

```
How confident is the system in the analytical conclusion?

```

They are not interchangeable.

* * * * *

32\. SIMILARITY
===============

Existing Phase 5 `SkillMatch.similarity` remains authoritative for match strength.

It is constrained to:

```
0.0 - 1.0

```

Examples of matching relationships include:

```
exact
strong_semantic
partial
related
unmatched

```

Phase 6 does not reinterpret similarity as confidence.

* * * * *

33\. CONFIDENCE
===============

Existing `Confidence` remains the authoritative confidence contract.

It contains:

```
score
level
components
rationale

```

with confidence score:

```
0.0 - 1.0

```

Confidence levels are:

```
LOW
MEDIUM
HIGH

```

Phase 6 preserves these values.

* * * * *

34\. NO SILENT RE-MATCHING
==========================

The scoring engine does not independently perform:

```
exact matching
semantic matching
taxonomy matching
embedding comparison
threshold-based matching

```

Those responsibilities remain with Phase 5.

The scorer consumes:

```
SkillMatch
RequirementAlignment

```

and translates those results into deterministic score values.

This prevents two different components from producing conflicting matching decisions.

* * * * *

35\. SCORING ENGINE
===================

New file:

```
backend/app/analysis/scoring.py

```

Primary class:

```
ScoringAnalyzer

```

Engine version:

```
phase6-scoring-v1

```

The engine is deterministic.

Given the same valid Phase 5 inputs, it produces the same scoring output.

* * * * *

36\. SCORING ENGINE RESPONSIBILITIES
====================================

`ScoringAnalyzer` is responsible for:

-   applying configured scoring weights

-   separating required and preferred skills

-   translating requirement alignment status to score values

-   calculating dimension scores

-   handling UNKNOWN requirements

-   excluding unavailable dimensions

-   renormalizing available weights

-   generating contribution records

-   preserving evidence-derived rationale

-   producing the canonical `ScoringResult`

* * * * *

37\. SCORING ENGINE NON-RESPONSIBILITIES
========================================

`ScoringAnalyzer` does not:

-   extract skills

-   normalize skills

-   map skills

-   match skills

-   align requirements

-   generate recommendations

-   rewrite resumes

-   scrape jobs

-   invoke Ollama

-   invoke an LLM for deterministic score decisions

-   create another orchestrator

-   independently generate a second matching result

* * * * *

38\. GAP ANALYSIS OBJECTIVE
===========================

The second major Phase 6 capability is requirement-linked skill-gap analysis.

The purpose is to convert existing requirement alignment into explicit candidate-facing analytical gaps.

The gap analyzer answers:

```
What requirement?
Required or preferred?
Which target skill?
What status?
What type of gap?
What similarity?
What evidence?
What confidence?
Why?

```

* * * * *

39\. GAP DOMAIN MODEL
=====================

Modified:

```
backend/app/domain/gaps.py

```

The domain now contains:

```
SkillGap
SkillAnalysis

```

* * * * *

40\. SKILL GAP MODEL
====================

`SkillGap` contains:

```
gap_id
requirement_id
requirement_type
target_skill_id
target_skill_name
match_status
gap_type
severity
similarity
rationale
evidence
confidence

```

This ensures every gap can be traced back to the original requirement.

* * * * *

41\. REQUIREMENT LINKAGE
========================

Every generated gap is linked to:

```
requirement_id

```

The requirement type is preserved:

```
required
preferred

```

The target skill is preserved through:

```
target_skill_id
target_skill_name

```

This prevents a generic list of missing skills from losing the context of why the skill matters.

* * * * *

42\. GAP STATUS
===============

Gap analysis preserves the authoritative Phase 5 status:

```
matched
partial
unmatched
unknown

```

The analyzer does not replace these values with a new incompatible status vocabulary.

* * * * *

43\. GAP TYPE
=============

Gap type is used to describe non-matched situations.

The Phase 6 implementation distinguishes cases such as:

```
partial
unmatched
unknown

```

while preserving the original:

```
match_status

```

This means the original alignment result remains authoritative.

* * * * *

44\. MATCHED REQUIREMENTS
=========================

A matched requirement does not become a negative gap.

It remains represented through the overall skill analysis and matching results.

Matched skills can therefore be surfaced as strengths by XAI.

* * * * *

45\. PARTIAL REQUIREMENTS
=========================

A partial requirement is preserved as a partial gap.

The gap includes:

```
requirement
requirement type
target skill
similarity
evidence
confidence
rationale

```

This allows the XAI layer to explain why the requirement is only partially satisfied.

* * * * *

46\. UNMATCHED REQUIREMENTS
===========================

An unmatched requirement becomes an explicit skill gap.

The gap remains linked to its original requirement.

The gap does not trigger an independent matching calculation.

* * * * *

47\. UNKNOWN REQUIREMENTS IN GAP ANALYSIS
=========================================

UNKNOWN requirements are preserved as UNKNOWN.

They are not converted into:

```
unmatched
missing
failure

```

This is essential because:

```
unknown != unmatched

```

The system must communicate uncertainty rather than fabricate absence.

* * * * *

48\. GAP ANALYZER
=================

New file:

```
backend/app/analysis/gaps.py

```

Primary class:

```
GapAnalyzer

```

Engine version:

```
phase6-gap-analysis-v1

```

* * * * *

49\. GAP ANALYZER RESPONSIBILITIES
==================================

The analyzer:

-   consumes existing requirements

-   consumes existing requirement alignments

-   consumes existing skill matches

-   links gaps to requirements

-   preserves required/preferred classification

-   preserves match status

-   preserves similarity

-   preserves evidence

-   preserves confidence

-   produces `SkillAnalysis`

* * * * *

50\. GAP ANALYZER NON-RESPONSIBILITIES
======================================

The analyzer does not:

-   perform new semantic matching

-   perform new lexical matching

-   recalculate similarity

-   assign confidence independently

-   calculate the final candidate score

-   generate recommendations

-   rewrite candidate resumes

-   scrape jobs

-   invoke an LLM

-   create a second orchestrator

* * * * *

51\. SKILL ANALYSIS MODEL
=========================

`SkillAnalysis` contains:

```
extracted_skills
matched_skills
partial_matches
missing_skills
transferable_skills
gaps

```

The Phase 6 gap list is the detailed requirement-level representation.

The existing summary lists remain available for compatibility and presentation.

* * * * *

52\. EVIDENCE PRESERVATION
==========================

Evidence is a first-class requirement throughout Phase 6.

A gap preserves:

```
Evidence[]

```

A skill explanation preserves:

```
Evidence[]

```

A matching result remains evidence-backed.

This means the system can explain not only:

```
what happened

```

but also:

```
what source evidence supported the result

```

* * * * *

53\. RATIONALE PRESERVATION
===========================

Phase 6 preserves the rationale associated with existing analytical decisions.

For example:

```
RequirementAlignment.rationale

```

can be carried into:

```
SkillGap.rationale

```

and subsequently into:

```
SkillExplanation

```

This creates a traceable chain:

```
Requirement
    |
    v
Alignment
    |
    v
Gap
    |
    v
Explanation

```

* * * * *

54\. XAI OBJECTIVE
==================

The third major Phase 6 capability is deterministic explainability.

The XAI layer answers:

```
Why is the score what it is?
Why is this skill matched?
Why is this skill partial?
Why is this skill missing?
What evidence supports the conclusion?
How confident is the conclusion?
Which dimensions contributed to the result?

```

* * * * *

55\. XAI IMPLEMENTATION
=======================

New file:

```
backend/app/analysis/xai.py

```

Primary class:

```
XAIAnalyzer

```

Engine version:

```
phase6-xai-v1

```

* * * * *

56\. XAI ARCHITECTURAL RULE
===========================

The XAI layer explains existing analytical outputs.

It does not independently recalculate official results.

The rule is:

```
XAI explains.
Scoring calculates.
Matching matches.
Gap analysis structures gaps.

```

No component should silently become another authority.

* * * * *

57\. XAI INPUTS
===============

The XAI analyzer consumes:

```
ScoringResult
SkillAnalysis
MatchingResult
ResumeSkill[]
JobSkill[]

```

This gives XAI enough context to produce evidence-backed explanations.

* * * * *

58\. MATCHED SKILL EXPLANATIONS
===============================

For matched skills, XAI produces:

```
SkillExplanation

```

The explanation can include:

```
resume skill
job skill
relationship
similarity
evidence
confidence

```

Example conceptual explanation:

```
Python matches the job requirement Python with an exact
relationship and similarity 1.00.

```

The wording is generated deterministically from the existing result.

* * * * *

59\. PARTIAL MATCH EXPLANATIONS
===============================

Partial matches are explained using the existing:

```
match_status
similarity
rationale
evidence
confidence

```

The XAI layer does not invent a new partial-match reason.

It uses the analytical result already established by Phase 5 and Phase 6 gap analysis.

* * * * *

60\. MISSING SKILL EXPLANATIONS
===============================

Unmatched requirements are converted into explicit explanations.

The explanation preserves:

```
target skill
requirement type
status
similarity if available
rationale
evidence
confidence

```

This makes a missing skill explainable rather than merely displaying a keyword list.

* * * * *

61\. EVIDENCE MAP
=================

XAI produces:

```
EvidenceMapEntry

```

Each entry identifies:

```
result_type
result_id
evidence

```

Phase 6 maps relevant evidence from:

```
SkillGap
SkillMatch

```

into the XAI result.

This establishes traceability between analytical results and their supporting evidence.

* * * * *

62\. STRENGTHS
==============

XAI derives strengths from existing matched skill results.

Strong relationships such as:

```
exact
strong_semantic

```

can be identified as strong matching evidence.

The strength list therefore reflects actual matching output rather than independent LLM interpretation.

* * * * *

63\. WEAKNESSES
===============

XAI derives weaknesses from:

```
missing skills
partial matches

```

It does not invent weaknesses unrelated to the analysis.

UNKNOWN results are not silently described as confirmed weaknesses.

* * * * *

64\. SCORE EXPLANATION
======================

The XAI score explanation includes:

```
overall score
dimension scores
dimension weights
score contributions
contribution rationale

```

This is important because merely stating:

```
Candidate score = 74

```

is not explainability.

The system must be able to show the analytical basis for the score.

* * * * *

65\. CONTRIBUTION-BASED EXPLANATION
===================================

Each contribution contains a mathematical contribution and rationale.

Conceptually:

```
Dimension
    |
    +-- Source
    |
    +-- Source score
    |
    +-- Weight
    |
    +-- Contribution
    |
    +-- Rationale

```

The XAI layer can therefore describe the score using the actual contribution records.

* * * * *

66\. OVERALL EXPLANATION
========================

The overall explanation reports:

```
overall score
matched count
partial count
unmatched count

```

and explicitly explains that the score is based on existing deterministic analytical results.

The XAI layer does not recalculate the official score merely to produce an explanation.

* * * * *

67\. XAI CONFIDENCE AGGREGATION
===============================

XAI preserves the distinction between similarity and confidence.

Confidence can be aggregated from:

```
scoring confidence
gap confidence

```

The implementation does not use similarity as a substitute for confidence.

The resulting confidence level is derived from confidence scores, not match strength.

* * * * *

68\. CONFIDENCE LEVEL RULE
==========================

The Phase 6 XAI aggregation uses:

```
score >= 0.85  -> HIGH
score >= 0.65  -> MEDIUM
otherwise      -> LOW

```

The rationale explicitly communicates that:

```
similarity is not used as confidence

```

* * * * *

69\. EXISTING XAI DOMAIN CONTRACT
=================================

The existing:

```
backend/app/domain/xai.py

```

was reused.

It already contains:

```
SkillExplanation
EvidenceMapEntry
XAIResult

```

This avoided creating a duplicate XAI domain contract.

* * * * *

70\. XAI RESULT
===============

The canonical `XAIResult` includes:

```
overall_explanation
score_explanation
strengths
weaknesses
matched_skill_explanations
missing_skill_explanations
partial_match_explanations
evidence_map
confidence

```

This is sufficient to represent the Phase 6 explainability contract.

* * * * *

71\. WHY DETERMINISTIC XAI WAS USED
===================================

Phase 6 deliberately uses deterministic explainability.

The project requires the official score and analytical results to remain reproducible.

Introducing an LLM as the authority for:

```
score
matching
gap status

```

would make the deterministic analytical layer unstable and difficult to verify.

Therefore:

```
deterministic engine
        |
        v
existing result
        |
        v
deterministic explanation

```

is the canonical architecture.

* * * * *

72\. SHAP / LIME EVALUATION
===========================

SHAP and LIME were considered as possible explainability techniques.

They were not added merely for branding.

The Phase 6 scoring function is a deterministic weighted formula.

Its contribution decomposition is therefore directly available mathematically:

```
score × weight

```

For this architecture, explicit contribution decomposition is more transparent than adding SHAP/LIME solely to satisfy an "XAI" label.

Therefore the implementation uses:

```
deterministic contribution decomposition

```

as the primary explainability mechanism.

* * * * *

73\. NO LLM SCORE AUTHORITY
===========================

Phase 6 does not delegate deterministic scoring decisions to:

```
LLMs
Ollama
generative AI
external AI services

```

An LLM is not allowed to decide:

```
matched
partial
unmatched
unknown
score
weight

```

Those remain deterministic analytical decisions.

* * * * *

74\. ORCHESTRATOR INTEGRATION
=============================

The Phase 6 engines were integrated into:

```
backend/app/orchestration/concrete_analysis_orchestrator.py

```

New imports include:

```
GapAnalyzer
ScoringAnalyzer
XAIAnalyzer

```

The constructor now accepts optional analyzer instances:

```
gap_analyzer
scoring_analyzer
xai_analyzer

```

with default implementations created internally.

* * * * *

75\. ENGINE INITIALIZATION
==========================

The orchestrator initializes:

```
self._gap_analyzer
self._scoring_analyzer
self._xai_analyzer

```

using dependency injection-compatible constructor parameters.

Conceptually:

```
provided analyzer
       OR
default analyzer

```

This maintains testability and architectural consistency.

* * * * *

76\. PHASE 6 EXECUTION LOCATION
===============================

Phase 6 execution occurs only in:

```
analyze_resume_jd()

```

It does not execute in:

```
analyze_resume()

```

This is an important compatibility boundary.

* * * * *

77\. GAP ANALYSIS EXECUTION
===========================

After Phase 5 matching:

```
matching

```

is available.

Phase 6 executes:

```
skill_analysis = self._gap_analyzer.analyze(...)

```

using:

```
requirements
matching
resume_profile.skills
jd_build.skills

```

* * * * *

78\. SCORING EXECUTION
======================

After gap analysis:

```
scoring = self._scoring_analyzer.score(...)

```

The scorer receives:

```
job_profile
requirements
matching
resume_skills
job_skills

```

It therefore has access to the existing authoritative analytical results.

* * * * *

79\. XAI EXECUTION
==================

After scoring:

```
xai = self._xai_analyzer.explain(...)

```

XAI receives:

```
scoring
skill_analysis
matching
resume_skills
job_skills

```

This ordering is deliberate:

```
matching
    ↓
gap analysis
    ↓
scoring
    ↓
XAI

```

* * * * *

80\. RESULT ATTACHMENT
======================

The resulting Phase 6 objects are attached to `AnalysisResult`:

```
skill_analysis=skill_analysis
scoring=scoring
xai=xai

```

The final Resume + JD result therefore contains the complete Phase 6 analytical output.

* * * * *

81\. METADATA INTEGRATION
=========================

Phase 6 engine versions are registered in analysis metadata.

The RESUME + JD metadata includes:

```
orchestrator
skill_matcher
requirement_aligner
gap_analyzer
scoring_analyzer
xai_analyzer

```

Phase 6 engine versions:

```
phase6-orchestrator-v1
phase6-gap-analysis-v1
phase6-scoring-v1
phase6-xai-v1

```

This provides reproducibility and implementation traceability.

* * * * *

82\. RESUME-ONLY METADATA
=========================

Resume-only analysis does not incorrectly claim that Phase 6 JD-specific engines executed.

Therefore the Phase 6 engine metadata is associated with the Resume + JD path.

This preserves semantic accuracy in the execution metadata.

* * * * *

83\. API CONTRACT IMPACT
========================

Phase 6 changes the API behavior for Resume + JD analysis.

Before Phase 6:

```
scoring = null
xai = null

```

for the Phase 5 Resume + JD implementation.

After Phase 6:

```
scoring != null
xai != null

```

for valid Resume + JD analysis.

`skill_analysis` is also populated from Phase 6 gap analysis.

* * * * *

84\. RESUME-ONLY API BEHAVIOR
=============================

Resume-only behavior remains:

```
skill_analysis = existing empty-compatible structure
scoring = null
xai = null
career_intelligence = null
recommendations = []

```

This was explicitly regression-tested.

* * * * *

85\. API TESTING
================

API tests are located in:

```
backend/tests/api/test_analysis_api.py

```

The Phase 6 API tests verify:

```
Resume-only compatibility
Resume + JD scoring presence
Resume + JD XAI presence
skill analysis presence
dimension scores
score range
contributions
XAI explanations

```

Final API test suite:

```
14 passed, 7 warnings

```

* * * * *

86\. ORCHESTRATOR TESTING
=========================

Orchestrator tests are located in:

```
backend/tests/unit/test_analysis_orchestrator.py

```

The Phase 6 integration test verifies:

```
skill_analysis is not None
scoring is not None
xai is not None

```

and verifies representative output content.

Final orchestrator test suite:

```
14 passed, 5 warnings

```

* * * * *

87\. GAP TESTING
================

New test file:

```
backend/tests/unit/test_gaps.py

```

The gap tests verify requirement-linked gap behavior.

Coverage includes:

-   matched handling

-   partial handling

-   unmatched handling

-   unknown handling

-   required/preferred preservation

-   similarity preservation

-   evidence preservation

-   confidence preservation

-   requirement linkage

-   deterministic behavior

Final gap test suite:

```
10 passed

```

* * * * *

88\. SCORING TESTING
====================

New test file:

```
backend/tests/unit/test_scoring.py

```

The scoring suite contains:

```
15 tests

```

It verifies:

-   canonical weights

-   alignment values

-   UNKNOWN exclusion

-   unavailable dimensions

-   required/preferred separation

-   experience scoring

-   education scoring

-   overall renormalization

-   contribution decomposition

-   domain scoring

-   similarity/confidence separation

-   certification behavior

-   score range

-   determinism

```

Final scoring test result:

```text
15 passed

```

* * * * *

89\. XAI TESTING
================

New test file:

```
backend/tests/unit/test_xai.py

```

The XAI suite verifies:

-   matched skill explanations

-   partial explanations

-   missing explanations

-   evidence mapping

-   strengths

-   weaknesses

-   score explanation

-   contribution rationale

-   overall explanation

-   confidence aggregation

-   similarity/confidence separation

-   deterministic behavior

Final XAI test result:

```
11 passed

```

* * * * *

90\. TARGETED PHASE 6 TEST SUITE
================================

The complete targeted Phase 6 verification covered:

```
GapAnalyzer
ScoringAnalyzer
XAIAnalyzer
ConcreteAnalysisOrchestrator
Analysis API

```

Final result:

```
64 passed, 7 warnings

```

There were:

```
0 failures

```

* * * * *

91\. FULL REGRESSION TEST
=========================

Phase 6 was required to preserve all existing functionality.

The full backend test suite was executed.

Final result:

```
281 passed, 7 warnings

```

There were:

```
0 test failures

```

This verifies that Phase 6 did not introduce a regression into the existing backend test suite.

* * * * *

92\. TEST COMMAND
=================

The final full regression command is:

```
PYTHONPATH="$PWD" pytest backend/tests -q

```

Final result:

```
281 passed, 7 warnings

```

The `PYTHONPATH` setting is required in the current repository test environment because the project is being executed directly from the repository root without a package-install configuration that automatically exposes `backend`.

* * * * *

93\. API TEST COMMAND
=====================

The API test suite can be executed with:

```
PYTHONPATH="$PWD" pytest backend/tests/api/test_analysis_api.py -q

```

Final result:

```
14 passed, 7 warnings

```

* * * * *

94\. PHASE 6 TARGETED COMMAND
=============================

The targeted Phase 6 verification was executed across the Phase 6-specific test files and integration tests.

Final combined result:

```
64 passed, 7 warnings

```

* * * * *

95\. WARNING STATUS
===================

The warnings do not represent Phase 6 failures.

The final warnings originate from dependencies/deprecations including areas such as:

```
Starlette/httpx
AnyIO
SWIG dependencies

```

No Phase 6 test failed because of these warnings.

* * * * *

96\. DEVELOPMENT CORRECTION --- SCORING TESTS
===========================================

During Phase 6 implementation, the scoring implementation and tests were iteratively verified.

The final scoring suite contains 15 passing tests.

The tests were used to validate the mathematical contract rather than simply checking object existence.

This included explicit verification of:

```
weights
alignment mapping
UNKNOWN handling
renormalization
contributions
determinism

```

* * * * *

97\. DEVELOPMENT CORRECTION --- XAI SCORE EXPLANATION
===================================================

During XAI verification, one issue was identified:

The initial score explanation did not explicitly include contribution rationale.

The implementation was corrected so score explanations now include the rationale from:

```
ScoreContribution.rationale

```

The resulting explanation therefore connects:

```
score contribution
+
mathematical contribution
+
reason

```

The XAI test suite was rerun after the correction.

Final result:

```
11 passed

```

* * * * *

98\. DEVELOPMENT CORRECTION --- MATCHED SKILL EXPLANATION
=======================================================

Another XAI test exposed an overly strict assumption that a job skill object must always be available for a matched explanation.

The implementation was corrected to use available resume/job skill identifiers and names appropriately.

The explanation remains based on the existing `SkillMatch`.

No new matching logic was introduced.

The corrected implementation passed the XAI test suite.

* * * * *

99\. DEVELOPMENT CORRECTION --- ORCHESTRATOR TEST
===============================================

The first Phase 6 orchestrator test incorrectly required that:

```
result.skill_analysis.gaps

```

must always be non-empty.

The fixture legitimately contained no gaps.

The test was corrected to assert:

```
gaps is a list

```

rather than requiring at least one gap.

This is an important testing correction because a candidate with all requirements satisfied can legitimately produce:

```
gaps = []

```

The final orchestrator suite passed:

```
14 passed

```

* * * * *

100\. API REGRESSION TEST CORRECTION
====================================

The API test suite initially contained the old Phase 5 expectation:

```
data["scoring"] is None

```

for Resume + JD analysis.

That assertion was updated to reflect the Phase 6 contract:

```
data["scoring"] is not None

```

and the test now verifies:

```
overall_score
dimension_scores
contributions

```

The Resume-only test was kept separate and continues to verify:

```
scoring is None
xai is None

```

This preserved the distinction between the two API modes.

* * * * *

101\. IMPORT / COMPILE VERIFICATION
===================================

The modified orchestrator was compiled directly.

Command:

```
python -m py_compile backend/app/orchestration/concrete_analysis_orchestrator.py

```

Result:

```
PASS

```

This verified that the orchestrator integration was syntactically valid.

* * * * *

102\. SOURCE QUALITY VERIFICATION
=================================

The complete source tree was checked for whitespace errors using:

```
git diff --check

```

Final result:

```
PASS

```

No whitespace errors were detected.

* * * * *

103\. FILES ADDED
=================

Phase 6 added the following implementation files:

```
backend/app/analysis/gaps.py
backend/app/analysis/scoring.py
backend/app/analysis/xai.py

```

* * * * *

104\. TEST FILES ADDED
======================

Phase 6 added:

```
backend/tests/unit/test_gaps.py
backend/tests/unit/test_scoring.py
backend/tests/unit/test_xai.py

```

* * * * *

105\. DOMAIN FILES MODIFIED
===========================

Phase 6 modified:

```
backend/app/domain/gaps.py
backend/app/domain/scoring.py

```

The XAI domain contract was already available and reused:

```
backend/app/domain/xai.py

```

* * * * *

106\. ORCHESTRATOR FILE MODIFIED
================================

Phase 6 modified:

```
backend/app/orchestration/concrete_analysis_orchestrator.py

```

This is the canonical integration point.

No second orchestrator was created.

* * * * *

107\. API TEST FILE MODIFIED
============================

Phase 6 modified:

```
backend/tests/api/test_analysis_api.py

```

The changes update the API tests to verify the new Phase 6 Resume + JD behavior while preserving Resume-only expectations.

* * * * *

108\. ORCHESTRATOR TEST FILE MODIFIED
=====================================

Phase 6 modified:

```
backend/tests/unit/test_analysis_orchestrator.py

```

The tests now verify that Phase 6 results are attached to Resume + JD analysis.

* * * * *

109\. DOCUMENTATION FILE ADDED
==============================

The authoritative Phase 6 documentation file is:

```
docs/PHASE_6.md

```

This file is the detailed historical and technical record for Phase 6.

The project-level documentation should reference this document rather than duplicating its full contents.

* * * * *

110\. PHASE 6 ENGINE VERSION REGISTRY
=====================================

The implemented engine versions are:

```
GapAnalyzer:
phase6-gap-analysis-v1

ScoringAnalyzer:
phase6-scoring-v1

XAIAnalyzer:
phase6-xai-v1

ConcreteAnalysisOrchestrator:
phase6-orchestrator-v1

```

These versions provide explicit implementation traceability.

* * * * *

111\. PHASE 6 DATA FLOW
=======================

The final analytical data flow is:

```
Resume
  |
  v
ResumeProfile
  |
  +----------------------+
                         |
Job Description          |
  |                      |
  v                      |
JobProfile               |
  |                      |
  +--> Requirements -----+
  |
  +--> Job Skills
          |
          v
    SkillMatcher
          |
          v
    MatchingResult
          |
          v
 RequirementAligner
          |
          v
 RequirementAlignments
          |
          +-------------------+
          |                   |
          v                   v
    GapAnalyzer        ScoringAnalyzer
          |                   |
          v                   v
   SkillAnalysis        ScoringResult
          |                   |
          +---------+---------+
                    |
                    v
                XAIAnalyzer
                    |
                    v
                XAIResult
                    |
                    v
              AnalysisResult

```

* * * * *

112\. RESPONSIBILITY MATRIX
===========================

| Component | Responsibility |
| --- | --- |
| Resume parser | Parse Resume |
| JD parser | Parse Job Description |
| Resume profile builder | Build ResumeProfile |
| JD profile builder | Build JobProfile |
| Skill extractor | Extract skills |
| Skill normalizer | Normalize skills |
| ESCO mapper | Map skills |
| Skill matcher | Determine skill relationships |
| Requirement aligner | Determine requirement status |
| GapAnalyzer | Structure requirement-linked gaps |
| ScoringAnalyzer | Calculate deterministic candidate-job score |
| XAIAnalyzer | Explain existing analytical results |
| ConcreteAnalysisOrchestrator | Coordinate workflow |
| API | Expose final result |

No component has overlapping scoring authority.

* * * * *

113\. PHASE 6 DESIGN INVARIANTS
===============================

The following invariants are preserved:

```
1\. One workflow orchestrator.
2. One authoritative matching engine.
3. One authoritative requirement alignment engine.
4. One authoritative scoring engine.
5. XAI does not redefine official results.
6. UNKNOWN is not equivalent to UNMATCHED.
7. Similarity is not confidence.
8. Evidence is preserved.
9. Confidence is preserved.
10. Required and preferred requirements remain distinct.
11. Resume-only analysis remains valid.
12. Resume + JD analysis receives Phase 6 outputs.
13. Deterministic scoring remains reproducible.
14. No arbitrary score penalties or bonuses.
15. No LLM authority over deterministic results.

```

* * * * *

114\. DETERMINISM REQUIREMENT
=============================

For the same:

```
ResumeProfile
JobProfile
MatchingResult
Requirements

```

the scoring result must remain stable.

The same principle applies to:

```
GapAnalyzer
XAIAnalyzer

```

The Phase 6 test suites explicitly include determinism checks.

* * * * *

115\. EXPLAINABILITY REQUIREMENT
================================

An explanation is considered valid only when it can be traced to an existing result.

For example:

```
SkillMatch
    |
    +--> relationship
    +--> similarity
    +--> evidence
    +--> confidence

```

can produce:

```
SkillExplanation

```

Similarly:

```
ScoreContribution
    |
    +--> dimension
    +--> source
    +--> score
    +--> weight
    +--> contribution
    +--> rationale

```

can produce score explanations.

* * * * *

116\. EVIDENCE CHAIN
====================

Phase 6 preserves the following evidence chain:

```
Source Document
      |
      v
Extracted Skill / Requirement
      |
      v
Skill Match / Requirement Alignment
      |
      v
Skill Gap / Score Contribution
      |
      v
XAI Explanation

```

This is the central explainability architecture.

* * * * *

117\. NO FABRICATED ABSENCE
===========================

The system must not interpret:

```
no evidence found

```

as:

```
candidate definitely lacks the skill

```

That is why:

```
UNKNOWN

```

exists.

This rule applies to both:

```
gap analysis

```

and:

```
scoring

```

* * * * *

118\. NO DUPLICATE MATCHING
===========================

The Phase 6 engines deliberately reuse:

```
SkillMatch

```

instead of calculating another similarity score.

This prevents:

```
Phase 5 says MATCHED
Phase 6 says UNMATCHED

```

type contradictions.

* * * * *

119\. NO DUPLICATE REQUIREMENT ALIGNMENT
========================================

The Phase 6 gap analyzer consumes:

```
RequirementAlignment

```

instead of independently determining whether a requirement is satisfied.

Phase 5 remains authoritative for alignment.

* * * * *

120\. NO SCORE MANIPULATION
===========================

Phase 6 does not add arbitrary:

```
+5 bonus
-10 penalty

```

rules to make the score appear more sophisticated.

The score comes from:

```
dimension score
×
explicit dimension weight

```

with availability-aware normalization.

* * * * *

121\. API RESULT CONTRACT
=========================

For valid Resume + JD analysis, the API now exposes:

```
matching
skill_analysis
scoring
xai

```

with the Phase 6 fields populated.

At minimum, the integration tests verify:

```
scoring.overall_score
scoring.dimension_scores
scoring.contributions
xai.overall_explanation
xai.score_explanation

```

* * * * *

122\. SCORE RANGE GUARANTEE
===========================

The public score is guaranteed by the Pydantic contract to remain:

```
0.0 <= overall_score <= 100.0

```

Individual dimension scores are also constrained to:

```
0.0 <= score <= 100.0

```

This prevents invalid API scoring values.

* * * * *

123\. INTERNAL / PUBLIC SCALE
=============================

Phase 6 maintains a clean distinction:

```
Internal:
0.0 - 1.0

Public:
0.0 - 100.0

```

This keeps mathematical calculations simple while presenting a familiar percentage-style score through the API.

* * * * *

124\. WHY REQUIRED/PREFERRED ARE SEPARATE
=========================================

A candidate may satisfy:

```
many preferred skills

```

while missing:

```
a critical required skill

```

Combining all requirements into one undifferentiated average would hide this distinction.

Therefore Phase 6 explicitly calculates:

```
required_skill_score
preferred_skill_score

```

and applies different weights.

* * * * *

125\. WHY UNKNOWN MUST BE EXCLUDED
==================================

Suppose a resume provides no information about a particular requirement.

Treating it as zero would imply:

```
confirmed absence

```

which is unsupported.

Excluding UNKNOWN means:

```
insufficient evidence remains insufficient evidence

```

This makes the score more semantically defensible.

* * * * *

126\. WHY DIMENSION RENORMALIZATION IS REQUIRED
===============================================

If a dimension is unavailable, leaving its weight in the denominator would lower the candidate score merely because information is missing.

Renormalization ensures:

```
available evidence

```

determines the score.

This is consistent with the project's evidence-aware analytical architecture.

* * * * *

127\. WHY CERTIFICATION HAS NO INDEPENDENT WEIGHT
=================================================

The Phase 6 scoring policy defines five dimensions.

Adding certification as an unapproved sixth dimension would change the official scoring contract.

Certification remains available through requirement analysis and alignment but does not receive an independent score weight.

* * * * *

128\. WHY XAI DOES NOT RECALCULATE
==================================

If XAI independently recalculated the score, two problems could occur:

```
official score = 74
XAI-calculated score = 71

```

The system would then have two competing scoring authorities.

Phase 6 avoids this by making:

```
ScoringAnalyzer

```

the sole score authority.

XAI only explains the result.

* * * * *

129\. WHY CONTRIBUTION DECOMPOSITION IS SUFFICIENT
==================================================

The scoring formula is explicitly weighted.

Therefore the contribution of a source can be directly represented.

For example:

```
required skill source
score = 1.0
weight = 0.50
contribution = 0.50

```

This is inherently interpretable.

Using SHAP/LIME without a demonstrated need would add complexity without improving the transparency of the official deterministic formula.

* * * * *

130\. SECURITY / SCOPE BOUNDARY
===============================

Phase 6 does not introduce:

```
authentication changes

```

or:

```
authorization changes

```

It does not introduce:

```
job database
application tracking
recruiter accounts

```

These remain outside the Phase 6 scope.

* * * * *

131\. EXPLICITLY EXCLUDED FEATURES
==================================

Phase 6 does not implement:

-   career intelligence

-   career recommendations

-   resume rewriting

-   Ollama

-   job scraping

-   recruiter functionality

-   authentication changes

-   job database

-   application tracking

-   report-generation redesign

-   background workers

-   Redis

-   Celery

-   microservices

-   a second orchestrator

-   SHAP/LIME solely for branding

These exclusions are deliberate.

* * * * *

132\. NO CAREER RECOMMENDATION LOGIC
====================================

The Phase 6 XAI layer may identify:

```
weaknesses

```

but it does not generate:

```
career recommendations

```

or:

```
learning plans

```

Those belong to a future explicitly approved capability.

* * * * *

133\. NO RESUME REWRITING
=========================

Phase 6 explains existing resume-job analytical results.

It does not modify or rewrite the candidate's resume.

* * * * *

134\. NO JOB SCRAPING
=====================

Phase 6 assumes the Job Description is already supplied.

It does not discover or scrape jobs from external websites.

* * * * *

135\. NO BACKGROUND WORKERS
===========================

The implementation remains synchronous within the existing modular monolith.

No:

```
Redis
Celery
worker service
microservice

```

was introduced.

* * * * *

136\. NO SECOND ORCHESTRATOR
============================

The project continues using:

```
ConcreteAnalysisOrchestrator

```

as the single workflow coordinator.

* * * * *

137\. PHASE 6 REGRESSION SAFETY
===============================

Phase 6 was developed with regression safety as a primary constraint.

The existing test suite was run after implementation.

Final result:

```
281 passed

```

This confirms compatibility with the pre-existing backend behavior covered by the test suite.

* * * * *

138\. PHASE 6 TEST INVENTORY
============================

Phase 6-specific implementation coverage includes:

```
backend/tests/unit/test_gaps.py
backend/tests/unit/test_scoring.py
backend/tests/unit/test_xai.py

```

Integration coverage includes:

```
backend/tests/unit/test_analysis_orchestrator.py
backend/tests/api/test_analysis_api.py

```

* * * * *

139\. FINAL TEST SUMMARY
========================

```
GapAnalyzer tests:
10 passed

ScoringAnalyzer tests:
15 passed

XAIAnalyzer tests:
11 passed

Orchestrator tests:
14 passed

API tests:
14 passed

```

The combined targeted verification was:

```
64 passed, 7 warnings

```

* * * * *

140\. FULL BACKEND REGRESSION SUMMARY
=====================================

Final full backend suite:

```
281 passed, 7 warnings

```

Failures:

```
0

```

Errors:

```
0

```

* * * * *

141\. CODE VALIDATION
=====================

The modified orchestrator passed:

```
python -m py_compile backend/app/orchestration/concrete_analysis_orchestrator.py

```

Result:

```
PASS

```

* * * * *

142\. DIFF VALIDATION
=====================

The repository passed:

```
git diff --check

```

Result:

```
PASS

```

This confirms no whitespace errors were introduced by the Phase 6 changes.

* * * * *

143\. FINAL ENGINE INVENTORY
============================

The Phase 6 analytical engine inventory is:

```
GapAnalyzer
    backend/app/analysis/gaps.py

ScoringAnalyzer
    backend/app/analysis/scoring.py

XAIAnalyzer
    backend/app/analysis/xai.py

```

All three are integrated into:

```
ConcreteAnalysisOrchestrator

```

* * * * *

144\. FINAL DOMAIN INVENTORY
============================

Phase 6 domain contracts include:

```
SkillGap
SkillAnalysis
DimensionScore
ScoreAdjustment
ScoreContribution
ScoringResult
SkillExplanation
EvidenceMapEntry
XAIResult

```

* * * * *

145\. FINAL PHASE 6 FILE INVENTORY
==================================

Implementation:

```
backend/app/analysis/gaps.py
backend/app/analysis/scoring.py
backend/app/analysis/xai.py

```

Modified domain:

```
backend/app/domain/gaps.py
backend/app/domain/scoring.py

```

Modified orchestration:

```
backend/app/orchestration/concrete_analysis_orchestrator.py

```

Tests:

```
backend/tests/unit/test_gaps.py
backend/tests/unit/test_scoring.py
backend/tests/unit/test_xai.py
backend/tests/unit/test_analysis_orchestrator.py
backend/tests/api/test_analysis_api.py

```

Documentation:

```
docs/PHASE_6.md

```

* * * * *

146\. PHASE 6 IMPLEMENTATION CHECKLIST
======================================

Domain
------

-   Skill gap contract extended

-   Skill analysis contract extended

-   Score contribution contract added

-   Scoring result contract extended

-   Existing XAI contract reused

Gap Analysis
------------

-   GapAnalyzer implemented

-   Requirement linkage implemented

-   Required/preferred preservation implemented

-   Match status preservation implemented

-   Similarity preservation implemented

-   Evidence preservation implemented

-   Confidence preservation implemented

-   UNKNOWN handling implemented

Scoring
-------

-   ScoringAnalyzer implemented

-   Required skill weight implemented

-   Preferred skill weight implemented

-   Experience weight implemented

-   Education weight implemented

-   Domain weight implemented

-   Alignment mapping implemented

-   UNKNOWN exclusion implemented

-   Dimension availability implemented

-   Overall renormalization implemented

-   Contribution decomposition implemented

-   Deterministic scoring implemented

XAI
---

-   XAIAnalyzer implemented

-   Matched skill explanations implemented

-   Partial match explanations implemented

-   Missing skill explanations implemented

-   Score explanations implemented

-   Contribution rationale included

-   Strength extraction implemented

-   Weakness extraction implemented

-   Evidence map implemented

-   Confidence aggregation implemented

-   Similarity/confidence separation preserved

Integration
-----------

-   Existing orchestrator extended

-   No second orchestrator introduced

-   Gap analysis integrated

-   Scoring integrated

-   XAI integrated

-   AnalysisResult populated

-   Metadata versions registered

-   Resume-only compatibility preserved

-   Resume + JD compatibility verified

Testing
-------

-   Gap tests

-   Scoring tests

-   XAI tests

-   Orchestrator tests

-   API tests

-   Full backend regression

-   Compile verification

-   `git diff --check`

Documentation
-------------

-   Phase 6 documentation created

-   Implementation documented

-   Architecture documented

-   Scoring policy documented

-   XAI policy documented

-   Testing documented

-   Scope exclusions documented

-   Completion criteria documented

* * * * *

147\. PHASE 6 ACCEPTANCE CRITERIA
=================================

Phase 6 is accepted because:

```
1\. Deterministic scoring exists.
2. Required/preferred weights are explicit.
3. UNKNOWN is excluded from scoring rather than treated as failure.
4. Unavailable dimensions are handled explicitly.
5. Overall score renormalizes available dimensions.
6. Skill gaps are linked to original requirements.
7. Evidence is preserved.
8. Confidence is preserved.
9. Similarity remains separate from confidence.
10. Score contributions are mathematically traceable.
11. XAI explains existing results.
12. XAI does not recalculate official scoring.
13. Resume-only behavior remains compatible.
14. Resume + JD produces Phase 6 results.
15. Engine versions are registered.
16. API tests pass.
17. Dedicated Phase 6 tests pass.
18. Full regression passes.
19. Source validation passes.
20. No prohibited Phase 6 scope expansion was introduced.

```

* * * * *

148\. FINAL VERIFICATION EVIDENCE
=================================

The final verification evidence is:

```
Targeted Phase 6 suite:
64 passed, 7 warnings

Full backend suite:
281 passed, 7 warnings

API suite:
14 passed, 7 warnings

Orchestrator suite:
14 passed, 5 warnings

Gap suite:
10 passed

Scoring suite:
15 passed

XAI suite:
11 passed

Compile:
PASS

git diff --check:
PASS

```

Therefore:

```
0 test failures
0 test errors

```

* * * * *

149\. DOCUMENTATION POLICY FOR PHASE 6
======================================

`docs/PHASE_6.md` is the authoritative detailed record of this phase.

The large project-level documents should not duplicate all of the Phase 6 implementation details contained here.

Instead they should provide:

```
current project status
phase status
high-level architecture
high-level API state
reference to docs/PHASE_6.md

```

This follows the documentation organization adopted from Phase 4 onward.

* * * * *

150\. PHASE HISTORY REFERENCE
=============================

Phase 6 follows:

```
Phase 1 --- Foundation and Architecture
Phase 2 --- Document Processing
Phase 3 --- Resume Intelligence Pipeline
Phase 4 --- [Phase 4 documented separately]
Phase 5 --- JD Intelligence & Resume--JD Matching
Phase 6 --- Final Candidate-Job Scoring, Skill Gap Analysis & XAI

```

Phase 5 established the Resume + JD intelligence and matching foundation.

Phase 6 consumes that foundation.

* * * * *

151\. PHASE 5 → PHASE 6 BOUNDARY
================================

Phase 5 owns:

```
JD intelligence
requirement extraction
required/preferred classification
JD skill extraction
skill normalization
ESCO mapping
Resume--JD matching
requirement alignment
evidence
confidence

```

Phase 6 owns:

```
gap analysis
candidate-job scoring
score contributions
deterministic XAI

```

This boundary prevents duplicated analytical responsibilities.

* * * * *

152\. PHASE 6 ARCHITECTURAL RESULT
==================================

The resulting architecture is:

```
                    ConcreteAnalysisOrchestrator
                               |
              +----------------+----------------+
              |                |                |
              v                v                v
        Phase 5 Matching   GapAnalyzer    ScoringAnalyzer
              |                |                |
              +----------------+----------------+
                               |
                               v
                         XAIAnalyzer
                               |
                               v
                         AnalysisResult

```

Phase 6 therefore extends the existing architecture rather than replacing it.

* * * * *

153\. REPRODUCIBILITY
=====================

The implementation is reproducible through:

```
explicit weights
explicit alignment values
explicit UNKNOWN handling
deterministic formulas
engine versioning
dedicated tests
full regression tests

```

No opaque model decision is required to determine the official score.

* * * * *

154\. RESEARCH / ACADEMIC VALUE
===============================

Phase 6 strengthens the academic objective of SkillLens by making the candidate-job score explainable.

Instead of presenting only:

```
Candidate Score: 78

```

the architecture can provide:

```
score
+
dimensions
+
weights
+
contributions
+
matched skills
+
partial skills
+
missing requirements
+
evidence
+
confidence
+
rationale

```

This provides a stronger basis for evaluating explainable semantic skill-gap analysis.

* * * * *

155\. LIMITATIONS
=================

Phase 6 intentionally does not claim to solve:

```
career planning
candidate recommendations
job discovery
resume rewriting
real-time labor-market intelligence
automated application tracking
LLM-based career coaching

```

The implemented scope is limited to:

```
candidate-job scoring
skill-gap analysis
XAI

```

within the existing Resume + JD analytical pipeline.

* * * * *

156\. FUTURE EXTENSION BOUNDARY
===============================

Future phases may build on Phase 6 outputs.

Possible future consumers can use:

```
ScoringResult
SkillAnalysis
XAIResult

```

without modifying their underlying authority.

Future functionality must be introduced under an explicitly approved phase.

It must not silently expand Phase 6.

* * * * *

157\. PHASE 6 FREEZE RULE
=========================

Phase 6 is frozen.

No additional feature expansion should be introduced under Phase 6 unless:

```
a defect is discovered

```

or:

```
a contract violation is discovered

```

New capabilities must belong to a future phase.

* * * * *

158\. FINAL PHASE 6 STATUS
==========================

```
PHASE 6
Final Candidate-Job Scoring, Skill Gap Analysis & XAI

STATUS:
COMPLETE AND FROZEN

IMPLEMENTATION:
COMPLETE

INTEGRATION:
COMPLETE

TESTING:
COMPLETE

API VERIFICATION:
COMPLETE

REGRESSION VERIFICATION:
COMPLETE

DOCUMENTATION:
COMPLETE

SOURCE VALIDATION:
COMPLETE

TARGETED TESTS:
64 PASSED

FULL BACKEND TESTS:
281 PASSED

FAILURES:
0

ERRORS:
0

```

* * * * *

159\. FINAL CONCLUSION
======================

Phase 6 successfully extends SkillLens from Resume + JD semantic matching into a complete deterministic candidate-job analytical layer.

Phase 5 determines:

```
what matches

```

Phase 6 determines:

```
how those results contribute to candidate-job suitability

```

and:

```
why the resulting analytical conclusions were produced

```

The implementation preserves:

```
evidence
confidence
requirement linkage
required/preferred distinction
matching authority
deterministic scoring
transparent contributions
XAI traceability

```

The existing `ConcreteAnalysisOrchestrator` remains the sole workflow orchestrator.

No second orchestrator was introduced.

No duplicate matching engine was introduced.

No LLM was made responsible for deterministic scoring.

No arbitrary scoring penalties or bonuses were introduced.

UNKNOWN results are not treated as confirmed failures.

Similarity is not treated as confidence.

The implementation has been verified through dedicated Phase 6 testing, API testing, orchestrator testing, full backend regression testing, compile validation, and Git diff validation.

Final result:

```
64 targeted Phase 6 tests passed.
281 full backend tests passed.
7 dependency/deprecation warnings.
0 failures.
0 errors.

```

Therefore:

**PHASE 6 --- FINAL CANDIDATE-JOB SCORING, SKILL GAP ANALYSIS & XAI --- COMPLETE AND FROZEN.**

For the complete implementation record, refer to:

```
docs/PHASE_6.md

```

Future development proceeds under the next explicitly approved phase.
- deterministic candidate-job scoring
- requirement-linked skill-gap analysis
- transparent score contributions
- deterministic explainability (XAI)
- evidence and confidence preservation
- required/preferred requirement differentiation
- explicit handling of UNKNOWN alignment states

Phase 6 does not duplicate Phase 5 matching or requirement alignment.

## Architecture

Phase 6 extends the existing:

`ConcreteAnalysisOrchestrator`

No second analysis orchestrator was introduced.

The RESUME_JD flow is:

1. Resume profile construction
2. JD profile construction
3. Phase 5 skill extraction
4. Phase 5 skill matching
5. Phase 5 requirement alignment
6. Phase 6 skill-gap analysis
7. Phase 6 deterministic scoring
8. Phase 6 deterministic XAI
9. Canonical AnalysisResult

Resume-only analysis remains compatible and does not execute JD-dependent Phase 6 scoring/XAI.

## Skill Gap Analysis

Phase 6 preserves the authoritative Phase 5 requirement alignment status:

- `matched`
- `partial`
- `unmatched`
- `unknown`

Each requirement-linked gap preserves:

- requirement ID
- required/preferred classification
- target skill identity
- match status
- gap classification
- similarity when available
- rationale
- evidence
- confidence

UNKNOWN is not treated as unmatched and is not treated as a failure.

Phase 6 does not infer a missing skill merely from absence of evidence.

## Deterministic Scoring

The scoring model uses explicit configurable dimension weights:

| Dimension | Weight |
|---|---:|
| Required skills | 0.50 |
| Preferred skills | 0.15 |
| Experience | 0.15 |
| Education | 0.10 |
| Domain | 0.10 |

Total weight: `1.00`

Alignment values:

| Alignment | Internal value |
|---|---:|
| Matched | 1.0 |
| Partial | 0.5 |
| Unmatched | 0.0 |
| Unknown | excluded |

Scores are calculated internally on a normalized `0–1` scale and exposed as `0–100` scores.

When a dimension contains only UNKNOWN evidence, that dimension is unavailable rather than being treated as zero.

Available dimension weights are renormalized when necessary.

## Score Contributions

Phase 6 exposes deterministic contribution decomposition.

Each contribution records:

- contribution ID
- dimension
- source type
- source ID
- normalized score
- weight
- contribution value
- rationale
- requirement type when applicable

No arbitrary penalties or bonuses are introduced.

The contribution layer explains the existing scoring formula rather than introducing an independent scoring mechanism.

## Matching and Confidence Separation

Phase 6 preserves the distinction between:

- matching strength / similarity
- confidence

Similarity represents the strength of an existing Phase 5 match.

Confidence represents confidence in the underlying evidence or alignment.

Similarity is not silently converted into confidence.

## XAI

Phase 6 introduces a deterministic XAI layer.

XAI explains existing Phase 5 and Phase 6 outputs.

It does not:

- perform semantic matching
- perform requirement alignment
- recalculate matching
- recalculate scores
- modify scores
- generate recommendations
- introduce LLM-based decision making

XAI provides:

- overall explanation
- score explanation
- strengths
- weaknesses
- matched-skill explanations
- partial-match explanations
- missing-skill explanations
- evidence mapping
- aggregate confidence

Score explanations include the deterministic contribution rationale.

## Evidence Preservation

Evidence remains attached to the underlying result.

XAI preserves available evidence from:

- skill matches
- requirement alignments
- skill gaps
- resume skill evidence

This maintains traceability from the final explanation back to the underlying analysis result.

## Engine Versions

Phase 6 engines are versioned independently:

- `phase6-orchestrator-v1`
- `phase6-gap-analysis-v1`
- `phase6-scoring-v1`
- `phase6-xai-v1`

Phase 5 engine versions remain independently identifiable.

## Testing

Phase 6 dedicated verification includes:

- GapAnalyzer unit tests
- ScoringAnalyzer unit tests
- XAIAnalyzer unit tests
- orchestrator integration tests
- API integration tests

Final Phase 6 targeted verification:

**64 passed, 7 warnings**

Final backend regression suite:

**281 passed, 7 warnings**

No test failures were present.

The warnings are dependency deprecation warnings originating from Starlette/httpx, AnyIO, and SWIG dependencies.

## Regression Compatibility

Resume-only analysis remains supported.

For resume-only analysis:

- JD profile remains absent
- matching remains absent
- scoring remains absent
- XAI remains absent
- existing resume analysis behavior remains intact

For Resume + JD analysis:

- Phase 5 matching remains the source of matching evidence
- Phase 5 requirement alignment remains authoritative
- Phase 6 consumes those results
- scoring and XAI are attached to the canonical AnalysisResult

## Explicit Non-Goals

Phase 6 does not introduce:

- career intelligence
- recommendations
- resume rewriting
- LLM-based deterministic scoring
- Ollama
- job scraping
- recruiter functionality
- authentication changes
- job database
- application tracking
- report-generation redesign
- background workers
- Redis
- Celery
- microservices
- a second orchestrator
- SHAP/LIME solely for branding

## Completion Criteria

Phase 6 is complete because:

- deterministic scoring is implemented
- required/preferred weighting is explicit
- UNKNOWN handling is defined
- skill gaps are requirement-linked
- evidence and confidence are preserved
- score contributions are explainable
- XAI explains existing results
- Resume-only compatibility is preserved
- Resume + JD integration is complete
- engine versions are registered
- dedicated tests pass
- API tests pass
- full regression suite passes
- `git diff --check` passes

## Final Status

**PHASE 6 — COMPLETE AND FROZEN**

No additional Phase 6 feature expansion is required unless a defect or contract violation is discovered.

Future development proceeds under the next explicitly approved phase.
