export type AnalysisMode = "resume_only" | "resume_jd";

export type AnalysisStatus =
  | "pending"
  | "running"
  | "completed"
  | "failed";

export type ConfidenceLevel = "low" | "medium" | "high";

export interface Confidence {
  score: number;
  level: ConfidenceLevel;
  components: Record<string, number>;
  rationale: string | null;
}

export type EvidenceSourceType = "resume" | "job_description";

export interface Evidence {
  evidence_id: string;
  source_type: EvidenceSourceType;
  source_document_id: string;
  section: string | null;
  text: string;
  start_offset: number | null;
  end_offset: number | null;
  evidence_type: string;
  extractor: string | null;
  relevance: number | null;
  confidence: number | null;
}

export interface Skill {
  skill_id: string;
  canonical_name: string;
  display_name: string;
  category: string | null;
  subcategory: string | null;
  aliases: string[];
  proficiency: string | null;
  importance: string | null;
  evidence: Evidence[];
  confidence: Confidence | null;
  metadata: Record<string, unknown>;
}

export interface Education {
  institution: string | null;
  degree: string | null;
  field_of_study: string | null;
  start_date: string | null;
  end_date: string | null;
  description: string | null;
}

export interface Experience {
  company: string | null;
  role: string | null;
  location: string | null;
  start_date: string | null;
  end_date: string | null;
  description: string | null;
  skills: Skill[];
}

export interface Project {
  name: string;
  description: string | null;
  technologies: string[];
  start_date: string | null;
  end_date: string | null;
}

export interface Certification {
  name: string;
  issuer: string | null;
  issue_date: string | null;
  expiry_date: string | null;
  credential_id: string | null;
}

export interface Contact {
  name: string | null;
  email: string | null;
  phone: string | null;
  location: string | null;
  linkedin: string | null;
  github: string | null;
  portfolio: string | null;
}

export interface ResumeProfile {
  profile_id: string;
  document_id: string;
  candidate_summary: string | null;
  contact: Contact | null;
  education: Education[];
  experience: Experience[];
  projects: Project[];
  certifications: Certification[];
  skills: Skill[];
  skill_categories: string[];
  total_experience: number | null;
  seniority: string | null;
  domains: string[];
  metadata: Record<string, unknown>;
}

export interface ExperienceRequirements {
  minimum_years: number | null;
  maximum_years: number | null;
  description: string | null;
}

export interface EducationRequirements {
  degrees: string[];
  fields_of_study: string[];
  description: string | null;
}

export interface JobProfile {
  profile_id: string;
  document_id: string;
  job_title: string;
  company: string | null;
  summary: string | null;
  responsibilities: string[];
  required_skills: string[];
  preferred_skills: string[];
  technical_skills: string[];
  soft_skills: string[];
  domain_skills: string[];
  experience_requirements: ExperienceRequirements | null;
  education_requirements: EducationRequirements | null;
  seniority: string | null;
  metadata: Record<string, unknown>;
}

export type MatchRelationship =
  | "exact"
  | "strong_semantic"
  | "partial"
  | "related"
  | "unmatched";

export type JobRequirementType = "required" | "preferred";

export type JobRequirementCategory =
  | "skill"
  | "experience"
  | "education"
  | "certification";

export type RequirementMatchStatus =
  | "matched"
  | "partial"
  | "unmatched"
  | "unknown";

export interface JobRequirement {
  requirement_id: string;
  text: string;
  requirement_type: JobRequirementType;
  category: JobRequirementCategory;
  skill_id: string | null;
  canonical_name: string | null;
  evidence: Evidence[];
  confidence: Confidence | null;
  metadata: Record<string, unknown>;
}

export interface RequirementAlignment {
  requirement_id: string;
  status: RequirementMatchStatus;
  evidence: Evidence[];
  confidence: Confidence | null;
  rationale: string | null;
}

export interface SkillMatch {
  resume_skill_id: string;
  job_skill_id: string;
  relationship: MatchRelationship;
  similarity: number;
  confidence: Confidence | null;
  evidence: Evidence[];
  rationale: string | null;
}

export interface MatchingResult {
  skill_matches: SkillMatch[];
  requirement_alignments: RequirementAlignment[];
  confidence: Confidence | null;
  evidence: Evidence[];
  metadata: Record<string, unknown>;
}

export interface SkillGap {
  gap_id: string;
  requirement_id: string;
  requirement_type: string;
  target_skill_id: string;
  target_skill_name: string;
  match_status: string;
  gap_type: string;
  severity: string | null;
  similarity: number | null;
  rationale: string | null;
  evidence: Evidence[];
  confidence: Confidence | null;
}

export interface SkillAnalysis {
  extracted_skills: string[];
  matched_skills: string[];
  partial_matches: string[];
  missing_skills: string[];
  transferable_skills: string[];
  gaps: SkillGap[];
}

export interface DimensionScore {
  dimension: string;
  score: number;
  weight: number;
}

export interface ScoreAdjustment {
  reason: string;
  value: number;
}

export interface ScoreContribution {
  contribution_id: string;
  dimension: string;
  source_type: string;
  source_id: string;
  score: number;
  weight: number;
  contribution: number;
  rationale: string;
  requirement_type?: string | null;
}

export interface ScoringResult {
  overall_score: number;
  skill_score: number;
  required_skill_score: number;
  preferred_skill_score: number;
  experience_score: number;
  education_score: number;
  domain_score: number;
  dimension_scores: DimensionScore[];
  contributions: ScoreContribution[];
  weights: Record<string, number>;
  penalties: ScoreAdjustment[];
  bonuses: ScoreAdjustment[];
  confidence: Confidence | null;
}

export interface SkillExplanation {
  skill_id: string;
  explanation: string;
  evidence: Evidence[];
  confidence: Confidence | null;
}

export interface EvidenceMapEntry {
  result_type: string;
  result_id: string;
  evidence: Evidence[];
}

export interface XAIResult {
  overall_explanation: string | null;
  score_explanation: string | null;
  strengths: string[];
  weaknesses: string[];
  matched_skill_explanations: SkillExplanation[];
  missing_skill_explanations: SkillExplanation[];
  partial_match_explanations: SkillExplanation[];
  evidence_map: EvidenceMapEntry[];
  confidence: Confidence | null;
}

export type CareerSeniorityLevel =
  | "entry"
  | "junior"
  | "mid"
  | "senior"
  | "lead"
  | "unknown";

export type CareerDirection =
  | "primary"
  | "secondary"
  | "insufficient_evidence";

export interface RoleFit {
  role: string;
  fit_score: number;
  direction: CareerDirection;
  rationale: string;
  evidence: Evidence[];
  confidence: Confidence;
}

export interface CareerDirectionResult {
  role: string;
  direction: CareerDirection;
  fit_score: number;
  rationale: string;
  evidence: Evidence[];
  confidence: Confidence;
}

export interface SkillPriority {
  skill_id: string;
  skill_name: string;
  priority: string;
  rationale: string | null;
}

export interface CareerIntelligence {
  inferred_profile: string | null;
  experience_level: CareerSeniorityLevel;
  seniority_confidence: Confidence;
  seniority_evidence: Evidence[];
  seniority_rationale: string;
  primary_domains: string[];
  secondary_domains: string[];
  strengths: string[];
  limitations: string[];
  transferable_skills: string[];
  career_directions: CareerDirectionResult[];
  potential_roles: string[];
  role_fit: RoleFit[];
  career_signals: string[];
  transition_analysis: string | null;
  skill_priorities: SkillPriority[];
  risks: string[];
  confidence: Confidence;
  taxonomy_version: string;
  engine_version: string;
}

export type RecommendationType =
  | "learning"
  | "project"
  | "certification"
  | "resume"
  | "career"
  | "job_alignment";

export type RecommendationPriority =
  | "low"
  | "medium"
  | "high"
  | "critical";

export type RecommendationEffort = "low" | "medium" | "high";

export type RecommendationImpact = "low" | "medium" | "high";

export interface Recommendation {
  recommendation_id: string;
  type: RecommendationType;
  title: string;
  target_skill: string | null;
  priority: RecommendationPriority;
  rationale: string;
  expected_impact: RecommendationImpact | null;
  effort: RecommendationEffort | null;
  evidence: Evidence[];
  related_gap_ids: string[];
  confidence: Confidence | null;
  priority_score: number;
  impact_score: number;
  source_engine: string;
}

export type LanguageIssueType =
  | "spelling"
  | "grammar"
  | "wording"
  | "terminology"
  | "formatting";

export type LanguageIssueSeverity =
  | "info"
  | "low"
  | "medium"
  | "high";

export interface LanguageIssue {
  issue_id: string;
  issue_type: LanguageIssueType;
  severity: LanguageIssueSeverity;
  title: string;
  explanation: string;
  recommendation: string | null;
  original_text: string | null;
  suggested_text: string | null;
  evidence: Evidence[];
  confidence: Confidence;
}

export interface AIAuthorshipHeuristic {
  score: number;
  level: string;
  signals: string[];
  disclaimer: string;
}

export interface ResumeLanguageQualityResult {
  overall_score: number;
  issues: LanguageIssue[];
  confidence: Confidence;
  authorship_heuristic: AIAuthorshipHeuristic;
  warnings: string[];
}

export type ResumeQualitySeverity = "info" | "low" | "medium" | "high";

export type ResumeQualityDimension =
  | "structure"
  | "completeness"
  | "skills_presentation"
  | "experience"
  | "education"
  | "projects"
  | "content_quality"
  | "consistency";

export interface ResumeQualityFinding {
  finding_id: string;
  category: ResumeQualityDimension;
  severity: ResumeQualitySeverity;
  title: string;
  explanation: string;
  recommendation: string | null;
  evidence: Evidence[];
  confidence: Confidence;
}

export interface ResumeQualityDimensionScore {
  dimension: ResumeQualityDimension;
  score: number;
  weight: number;
}

export interface ResumeQualityResult {
  overall_score: number;
  dimension_scores: ResumeQualityDimensionScore[];
  findings: ResumeQualityFinding[];
  confidence: Confidence;
  warnings: string[];
}

export type ATSIntelligenceSeverity = "info" | "low" | "medium" | "high";

export type ATSIntelligenceDimension =
  | "machine_readability"
  | "section_detectability"
  | "text_extraction"
  | "heading_clarity"
  | "skill_detectability"
  | "contact_detectability"
  | "formatting_risk"
  | "content_redundancy"
  | "standard_information";

export interface ATSIntelligenceFinding {
  finding_id: string;
  category: ATSIntelligenceDimension;
  severity: ATSIntelligenceSeverity;
  title: string;
  explanation: string;
  recommendation: string | null;
  evidence: Evidence[];
  confidence: Confidence;
}

export interface ATSIntelligenceDimensionScore {
  dimension: ATSIntelligenceDimension;
  score: number;
  weight: number;
}

export interface ATSIntelligenceResult {
  overall_score: number;
  dimension_scores: ATSIntelligenceDimensionScore[];
  findings: ATSIntelligenceFinding[];
  confidence: Confidence;
  warnings: string[];
}

export interface AnalysisInput {
  resume_document_id: string;
  job_description_document_id: string | null;
}

export interface AnalysisMetadata {
  engine_versions: Record<string, string>;
  processing_time_ms: number | null;
  warnings: string[];
  extra: Record<string, unknown>;
}

export interface AnalysisResult {
  analysis_id: string;
  schema_version: string;
  analysis_mode: AnalysisMode;
  status: AnalysisStatus;
  created_at: string;
  input: AnalysisInput;
  resume_profile: ResumeProfile;
  job_profile: JobProfile | null;
  skill_analysis: SkillAnalysis;
  resume_quality: ResumeQualityResult | null;
  ats_intelligence: ATSIntelligenceResult | null;
  language_quality: ResumeLanguageQualityResult | null;
  resume_improvement_prompt: string | null;
  matching: MatchingResult | null;
  scoring: ScoringResult | null;
  xai: XAIResult | null;
  career_intelligence: CareerIntelligence | null;
  recommendations: Recommendation[];
  metadata: AnalysisMetadata;
}
