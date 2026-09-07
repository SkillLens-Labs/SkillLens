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

export interface SkillMatch {
  resume_skill_id: string;
  job_skill_id: string;
  relationship: MatchRelationship;
  similarity: number;
  confidence: Confidence | null;
  evidence: Evidence[];
  rationale: string | null;
}

export interface SkillGap {
  gap_id: string;
  target_skill_id: string;
  target_skill_name: string;
  gap_type: string;
  severity: string | null;
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

export interface ScoringResult {
  overall_score: number;
  skill_score: number;
  required_skill_score: number;
  preferred_skill_score: number;
  experience_score: number;
  education_score: number;
  domain_score: number;
  dimension_scores: DimensionScore[];
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

export interface RoleFit {
  role: string;
  fit_score: number;
  rationale: string | null;
  confidence: Confidence | null;
}

export interface SkillPriority {
  skill_id: string;
  skill_name: string;
  priority: string;
  rationale: string | null;
}

export interface CareerIntelligence {
  inferred_profile: string | null;
  experience_level: string | null;
  primary_domains: string[];
  secondary_domains: string[];
  strengths: string[];
  career_signals: string[];
  potential_roles: string[];
  role_fit: RoleFit[];
  transition_analysis: string | null;
  skill_priorities: SkillPriority[];
  risks: string[];
  confidence: Confidence | null;
}

export type RecommendationType =
  | "learning"
  | "project"
  | "certification"
  | "resume"
  | "career";

export interface Recommendation {
  recommendation_id: string;
  type: RecommendationType;
  title: string;
  target_skill: string | null;
  priority: string;
  rationale: string;
  expected_impact: string | null;
  effort: string | null;
  evidence: Evidence[];
  related_gap_ids: string[];
  confidence: Confidence | null;
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
  scoring: ScoringResult | null;
  xai: XAIResult | null;
  career_intelligence: CareerIntelligence | null;
  recommendations: Recommendation[];
  metadata: AnalysisMetadata;
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
