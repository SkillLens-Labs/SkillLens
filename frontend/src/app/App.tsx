import { useEffect, useMemo, useState } from "react";
import "./styles.css";
import type {
  AnalysisResult,
  ATSIntelligenceResult,
  CareerIntelligence,
  Confidence,
  Evidence,
  JobProfile,
  JobRequirement,
  LanguageIssue,
  MatchingResult,
  Recommendation,
  ResumeLanguageQualityResult,
  ResumeQualityResult,
  ScoringResult,
  SkillGap,
  XAIResult,
} from "../types/analysis";

const API_BASE = "http://127.0.0.1:8000/api/v1";

type Page = "landing" | "input" | "analyzing" | "dashboard";

interface ApiError {
  code?: string;
  message?: string;
  details?: unknown;
  field?: string | null;
  request_id?: string;
}

/* =========================================================
   HELPERS
   ========================================================= */

function confidenceLabel(confidence?: Confidence | null): string {
  if (!confidence) return "Unknown";
  return `${confidence.level} (${Math.round(confidence.score * 100)}%)`;
}

function scoreLabel(score?: number | null): string {
  if (score === null || score === undefined) return "N/A";
  return `${score.toFixed(1)}/100`;
}

function pretty(value: string | undefined | null): string {
  if (!value) return "—";
  return value.replaceAll("_", " ");
}

/* =========================================================
   HEADER — two-item segmented nav with sliding indicator
   ========================================================= */

function Header({
  page,
  onNavigate,
  onNewAnalysis,
  analysisExists,
}: {
  page: Page;
  onNavigate: (page: Page) => void;
  onNewAnalysis: () => void;
  analysisExists: boolean;
}) {
  // Map the current page to a nav index.
  // "analyzing" keeps whatever the user was doing (defaults to dashboard).
  const activeIndex: 0 | 1 | 2 =
    page === "landing" ? 0 : page === "input" || page === "analyzing" ? 1 : 2; // "dashboard"

  const items: { id: Page; label: string }[] = [
    { id: "landing", label: "Home" },
    { id: "input", label: "Upload" },
    { id: "dashboard", label: "Dashboard" },
  ];

  return (
    <header className="topbar">
      <button
        type="button"
        className="topbar__brand"
        onClick={() => onNavigate("landing")}
        aria-label="SkillLens home"
      >
        <span className="brand-mark" aria-hidden="true">
          <img src="/logo.png" alt="" />
        </span>
        <span className="brand-block">
          <span className="brand">SKILLLENS</span>
          <span className="brand-subtitle">
            Explainable career intelligence
          </span>
        </span>
      </button>

      <nav
        className="segmented-nav"
        aria-label="Primary"
        data-active={activeIndex}
      >
        <span className="segmented-nav__thumb" aria-hidden="true" />

        {items.map((item) => (
          <button
            key={item.id}
            type="button"
            className={`segmented-nav__item ${
              activeIndex === items.indexOf(item) ? "is-active" : ""
            }`}
            onClick={() => onNavigate(item.id)}
          >
            {item.label}
          </button>
        ))}
      </nav>

      <div className="topbar__actions">
        <div className="header-status" title="Analysis engine ready">
          <span className="dot" aria-hidden="true" />
          <span className="status-text">
            Engine <strong>ready</strong>
          </span>
        </div>

        {analysisExists ? (
          <button
            type="button"
            className="secondary-button"
            onClick={onNewAnalysis}
          >
            New analysis
          </button>
        ) : (
          <button
            type="button"
            className="secondary-button"
            onClick={() => onNavigate("input")}
          >
            Get started
          </button>
        )}
      </div>
    </header>
  );
}

/* =========================================================
   PRIMITIVES (unchanged)
   ========================================================= */

function EvidenceList({ evidence }: { evidence?: Evidence[] }) {
  if (!evidence?.length) return <p className="muted">No evidence recorded.</p>;

  return (
    <details className="evidence-details">
      <summary>
        Evidence · {evidence.length} {evidence.length === 1 ? "item" : "items"}
      </summary>

      <div className="evidence-list">
        {evidence.map((item) => (
          <article className="evidence-item" key={item.evidence_id}>
            <div className="evidence-header">
              <strong>{pretty(item.source_type)}</strong>
              {item.section && (
                <span className="evidence-section">{pretty(item.section)}</span>
              )}
            </div>

            {item.text && <p>{item.text}</p>}

            <div className="evidence-meta">
              <span>Type: {pretty(item.evidence_type)}</span>
              {item.relevance != null && (
                <span>Relevance: {item.relevance.toFixed(2)}</span>
              )}
              {item.confidence != null && (
                <span>Confidence: {item.confidence.toFixed(2)}</span>
              )}
            </div>
          </article>
        ))}
      </div>
    </details>
  );
}

function TagList({
  items,
  empty = "None",
}: {
  items?: string[];
  empty?: string;
}) {
  if (!items?.length) return <span className="muted">{empty}</span>;

  return (
    <div className="tag-list">
      {items.map((item, index) => (
        <span className="skill-tag" key={`${item}-${index}`}>
          {item}
        </span>
      ))}
    </div>
  );
}

function ScoreCard({
  label,
  score,
  description,
}: {
  label: string;
  score?: number | null;
  description?: string;
}) {
  const fillPercent =
    score !== null && score !== undefined
      ? Math.max(0, Math.min(100, score))
      : 0;

  return (
    <article
      className="score-card"
      style={{ ["--score-fill" as string]: `${fillPercent}%` }}
    >
      <span className="eyebrow">{label}</span>
      <strong>{scoreLabel(score)}</strong>
      {description && <p>{description}</p>}
    </article>
  );
}

function Section({
  title,
  eyebrow,
  children,
}: {
  title: string;
  eyebrow?: string;
  children: React.ReactNode;
}) {
  return (
    <section className="result-section">
      {eyebrow && <span className="eyebrow">{eyebrow}</span>}
      <h2>{title}</h2>
      {children}
    </section>
  );
}

function DimensionTable({
  dimensions,
}: {
  dimensions: Array<{ dimension: string; score: number; weight: number }>;
}) {
  if (!dimensions.length) {
    return <p className="muted">No dimension scores available.</p>;
  }

  return (
    <div className="dimension-table">
      <div className="dimension-row dimension-header">
        <span>Dimension</span>
        <span>Score</span>
        <span>Weight</span>
      </div>

      {dimensions.map((dimension) => (
        <div
          className="dimension-row"
          key={dimension.dimension}
          style={{ ["--dim-fill" as string]: `${dimension.score}%` }}
        >
          <span>{pretty(dimension.dimension)}</span>
          <span className="dimension-score">{dimension.score.toFixed(1)}</span>
          <span className="dimension-weight">
            {(dimension.weight * 100).toFixed(0)}%
          </span>
        </div>
      ))}
    </div>
  );
}

function FindingList({
  findings,
}: {
  findings: Array<{
    finding_id?: string;
    category?: string;
    title: string;
    explanation: string;
    recommendation?: string | null;
    severity?: string;
    evidence?: Evidence[];
    confidence?: Confidence;
  }>;
}) {
  if (!findings.length) {
    return <p className="muted">No findings reported.</p>;
  }

  return (
    <div className="finding-list">
      {findings.map((finding, index) => (
        <article
          className="finding-card"
          key={finding.finding_id ?? `${finding.title}-${index}`}
        >
          <div className="finding-header">
            <strong>{finding.title}</strong>
            <div className="finding-badges">
              {finding.category && (
                <span className="category-pill">
                  {pretty(finding.category)}
                </span>
              )}
              {finding.severity && (
                <span
                  className={`severity severity-${finding.severity.toLowerCase()}`}
                >
                  {pretty(finding.severity)}
                </span>
              )}
            </div>
          </div>

          <p>{finding.explanation}</p>

          {finding.recommendation && (
            <p>
              <strong>Recommendation:</strong> {finding.recommendation}
            </p>
          )}

          {finding.confidence && (
            <p className="finding-confidence">
              <strong>Confidence:</strong> {confidenceLabel(finding.confidence)}
            </p>
          )}

          {finding.evidence && finding.evidence.length > 0 && (
            <EvidenceList evidence={finding.evidence} />
          )}
        </article>
      ))}
    </div>
  );
}

/* =========================================================
   DASHBOARD SECTIONS — unchanged from your version
   ========================================================= */

function ResumeOverview({ result }: { result: AnalysisResult }) {
  const resume = result.resume_profile;
  const contact = resume.contact;

  const profileLinks = [
    { label: "LinkedIn", value: contact?.linkedin },
    { label: "GitHub", value: contact?.github },
    { label: "Portfolio", value: contact?.portfolio },
  ].filter((link): link is { label: string; value: string } =>
    Boolean(link.value),
  );

  return (
    <Section title="Resume overview" eyebrow="Candidate">
      <div className="detail-grid">
        <div>
          <span className="label">Name</span>
          <strong>{contact?.name ?? "—"}</strong>
        </div>
        <div>
          <span className="label">Email</span>
          <strong>{contact?.email ?? "—"}</strong>
        </div>
        <div>
          <span className="label">Phone</span>
          <strong>{contact?.phone ?? "—"}</strong>
        </div>
        <div>
          <span className="label">Location</span>
          <strong>{contact?.location ?? "—"}</strong>
        </div>
        <div>
          <span className="label">Seniority</span>
          <strong>{resume.seniority ?? "—"}</strong>
        </div>
        <div>
          <span className="label">Experience</span>
          <strong>
            {resume.total_experience != null
              ? `${resume.total_experience} years`
              : "—"}
          </strong>
        </div>
      </div>

      {profileLinks.length > 0 && (
        <div className="subsection">
          <h3>Profile links</h3>
          <div className="tag-list">
            {profileLinks.map((link) => (
              <a
                className="tag"
                href={link.value}
                key={link.label}
                target="_blank"
                rel="noreferrer"
              >
                {link.label}
              </a>
            ))}
          </div>
        </div>
      )}

      <div className="subsection">
        <h3>Professional summary</h3>
        {resume.candidate_summary ? (
          <p>{resume.candidate_summary}</p>
        ) : (
          <p className="muted">No professional summary extracted.</p>
        )}
      </div>

      <div className="subsection">
        <h3>Skills</h3>
        <TagList items={resume.skills?.map((skill) => skill.display_name)} />
      </div>

      <div className="subsection">
        <h3>Education</h3>
        {resume.education?.length ? (
          <div className="education-list">
            {resume.education.map((education, index) => (
              <article className="education-card" key={`education-${index}`}>
                <div className="education-card-header">
                  <div>
                    <span className="label">Degree</span>
                    <strong>
                      {education.degree ?? "Degree not specified"}
                    </strong>
                  </div>
                  {education.start_date || education.end_date ? (
                    <span className="education-period">
                      {education.start_date ?? "—"} →{" "}
                      {education.end_date ?? "—"}
                    </span>
                  ) : null}
                </div>

                <div className="education-details">
                  <div>
                    <span className="label">Field of study</span>
                    <span>{education.field_of_study ?? "Not specified"}</span>
                  </div>
                  <div>
                    <span className="label">Institution</span>
                    <span>{education.institution ?? "Not specified"}</span>
                  </div>
                </div>

                {education.description && (
                  <p className="education-description">
                    {education.description}
                  </p>
                )}
              </article>
            ))}
          </div>
        ) : (
          <p className="muted">No education entries.</p>
        )}
      </div>

      <div className="subsection">
        <h3>Experience</h3>
        {resume.experience?.length ? (
          resume.experience.map((experience, index) => (
            <div className="compact-card" key={`experience-${index}`}>
              <strong>{experience.role ?? "Role not specified"}</strong>
              <span>{experience.company ?? "Company not specified"}</span>
              <span>
                {experience.start_date ?? "—"} → {experience.end_date ?? "—"}
              </span>
              {experience.description && <p>{experience.description}</p>}
            </div>
          ))
        ) : (
          <p className="muted">No experience entries.</p>
        )}
      </div>

      <div className="subsection">
        <h3>Projects</h3>
        {resume.projects?.length ? (
          <div className="project-list">
            {resume.projects.map((project, index) => (
              <article className="project-card" key={`project-${index}`}>
                <div className="project-card-header">
                  <strong>{project.name ?? "Unnamed project"}</strong>
                  {project.start_date || project.end_date ? (
                    <span className="project-period">
                      {project.start_date ?? "—"} → {project.end_date ?? "—"}
                    </span>
                  ) : null}
                </div>

                {project.description && (
                  <p className="project-description">{project.description}</p>
                )}

                {project.technologies?.length ? (
                  <div className="project-technologies">
                    <span className="label">Technologies</span>
                    <TagList items={project.technologies} />
                  </div>
                ) : (
                  <span className="muted">No technologies recorded.</span>
                )}
              </article>
            ))}
          </div>
        ) : (
          <p className="muted">No projects recorded.</p>
        )}
      </div>

      <div className="subsection">
        <h3>Certifications</h3>
        {resume.certifications?.length ? (
          resume.certifications.map((certification, index) => (
            <div className="compact-card" key={`certification-${index}`}>
              <strong>{certification.name ?? "Unnamed certification"}</strong>
              <span>{certification.issuer ?? "Issuer not specified"}</span>
            </div>
          ))
        ) : (
          <p className="muted">No certifications recorded.</p>
        )}
      </div>
    </Section>
  );
}

function QualitySection({ quality }: { quality?: ResumeQualityResult | null }) {
  if (!quality) return null;

  return (
    <Section title="Resume quality" eyebrow="Resume analysis">
      <div className="score-grid">
        <ScoreCard
          label="Overall quality"
          score={quality.overall_score}
          description={`Confidence: ${confidenceLabel(quality.confidence)}`}
        />
      </div>

      <DimensionTable dimensions={quality.dimension_scores} />

      <h3>Findings</h3>
      <FindingList findings={quality.findings} />

      {quality.warnings.length > 0 && (
        <div className="warning-box">
          <strong>Warnings</strong>
          <ul>
            {quality.warnings.map((warning, index) => (
              <li key={`${warning}-${index}`}>{warning}</li>
            ))}
          </ul>
        </div>
      )}
    </Section>
  );
}

function ATSSection({ ats }: { ats?: ATSIntelligenceResult | null }) {
  if (!ats) return null;

  return (
    <Section title="ATS intelligence" eyebrow="Machine readability">
      <div className="score-grid">
        <ScoreCard
          label="ATS score"
          score={ats.overall_score}
          description={`Confidence: ${confidenceLabel(ats.confidence)}`}
        />
      </div>

      <DimensionTable dimensions={ats.dimension_scores} />

      <h3>ATS findings</h3>
      <FindingList findings={ats.findings} />

      {ats.warnings.length > 0 && (
        <div className="warning-box">
          <strong>Warnings</strong>
          <ul>
            {ats.warnings.map((warning, index) => (
              <li key={`${warning}-${index}`}>{warning}</li>
            ))}
          </ul>
        </div>
      )}
    </Section>
  );
}

function LanguageSection({
  language,
}: {
  language?: ResumeLanguageQualityResult | null;
}) {
  if (!language) return null;

  return (
    <Section
      title="Language quality & AI-writing heuristic"
      eyebrow="Writing analysis"
    >
      <div className="score-grid">
        <ScoreCard
          label="Language quality"
          score={language.overall_score}
          description={`Confidence: ${confidenceLabel(language.confidence)}`}
        />
        <ScoreCard
          label="AI-style heuristic"
          score={language.authorship_heuristic.score}
          description={language.authorship_heuristic.level}
        />
      </div>

      <div className="disclaimer">
        <strong>Important:</strong> {language.authorship_heuristic.disclaimer}
      </div>

      {language.authorship_heuristic.signals.length > 0 && (
        <>
          <h3>Heuristic signals</h3>
          <ul>
            {language.authorship_heuristic.signals.map((signal, index) => (
              <li key={`${signal}-${index}`}>{signal}</li>
            ))}
          </ul>
        </>
      )}

      <h3>Language issues</h3>
      {language.issues.length ? (
        <div className="finding-list">
          {language.issues.map((issue: LanguageIssue) => (
            <article className="finding" key={issue.issue_id}>
              <div className="finding-header">
                <strong>{issue.title}</strong>
                <span className={`severity severity-${issue.severity}`}>
                  {issue.severity}
                </span>
              </div>
              <span className="finding-category">
                {pretty(issue.issue_type)} · {confidenceLabel(issue.confidence)}
              </span>
              <p>{issue.explanation}</p>
              {issue.original_text && (
                <p>
                  <strong>Original:</strong> {issue.original_text}
                </p>
              )}
              {issue.suggested_text && (
                <p>
                  <strong>Suggested:</strong> {issue.suggested_text}
                </p>
              )}
              {issue.recommendation && (
                <p>
                  <strong>Recommendation:</strong> {issue.recommendation}
                </p>
              )}
              <EvidenceList evidence={issue.evidence} />
            </article>
          ))}
        </div>
      ) : (
        <p className="muted">No language issues detected.</p>
      )}

      {language.warnings.length > 0 && (
        <div className="warning-box">
          <strong>Warnings</strong>
          <ul>
            {language.warnings.map((warning, index) => (
              <li key={`${warning}-${index}`}>{warning}</li>
            ))}
          </ul>
        </div>
      )}
    </Section>
  );
}

function CareerSection({ career }: { career?: CareerIntelligence | null }) {
  if (!career) return null;

  return (
    <Section title="Career intelligence" eyebrow="Career fit">
      <div className="detail-grid">
        <div>
          <span className="label">Inferred profile</span>
          <strong>{career.inferred_profile ?? "—"}</strong>
        </div>
        <div>
          <span className="label">Experience level</span>
          <strong>{pretty(career.experience_level)}</strong>
        </div>
        <div>
          <span className="label">Seniority confidence</span>
          <strong>{confidenceLabel(career.seniority_confidence)}</strong>
        </div>
        <div>
          <span className="label">Overall confidence</span>
          <strong>{confidenceLabel(career.confidence)}</strong>
        </div>
      </div>

      <div className="subsection">
        <h3>Career domains</h3>
        <div className="career-domain-grid">
          <div>
            <span className="label">Primary</span>
            <TagList items={career.primary_domains} />
          </div>
          <div>
            <span className="label">Secondary</span>
            <TagList items={career.secondary_domains} />
          </div>
        </div>
      </div>

      <div className="subsection">
        <h3>Strengths</h3>
        <TagList items={career.strengths} />
      </div>
      <div className="subsection">
        <h3>Limitations</h3>
        <TagList items={career.limitations} />
      </div>
      <div className="subsection">
        <h3>Transferable skills</h3>
        <TagList items={career.transferable_skills} />
      </div>

      <div className="subsection">
        <h3>Recommended career paths</h3>
        {career.career_directions?.length ? (
          <div className="role-list">
            {career.career_directions.map((direction, index) => (
              <article
                className="role-card"
                key={`${direction.role}-${direction.direction}-${index}`}
              >
                <div className="finding-header">
                  <strong>{direction.role}</strong>
                  <span className="score-pill">
                    {scoreLabel(direction.fit_score)}
                  </span>
                </div>
                <span>{pretty(direction.direction)}</span>
                <p>{direction.rationale}</p>
                <div className="recommendation-meta">
                  <span>
                    Confidence: {confidenceLabel(direction.confidence)}
                  </span>
                </div>
                <EvidenceList evidence={direction.evidence} />
              </article>
            ))}
          </div>
        ) : (
          <p className="muted">No career directions.</p>
        )}
      </div>

      <div className="subsection">
        <h3>Career signals</h3>
        <TagList items={career.career_signals} />
      </div>

      {career.transition_analysis && (
        <div className="subsection">
          <h3>Transition analysis</h3>
          <p>{career.transition_analysis}</p>
        </div>
      )}

      <div className="subsection">
        <h3>Skill priorities</h3>
        {career.skill_priorities?.length ? (
          <div className="finding-list">
            {career.skill_priorities.map((priority) => (
              <article className="finding" key={priority.skill_id}>
                <div className="finding-header">
                  <strong>{priority.skill_name}</strong>
                  <span className="severity severity-medium">
                    {pretty(priority.priority)}
                  </span>
                </div>
                {priority.rationale && <p>{priority.rationale}</p>}
                <div className="recommendation-meta">
                  <span>Skill ID: {priority.skill_id}</span>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <p className="muted">No skill priorities.</p>
        )}
      </div>

      <div className="subsection">
        <h3>Risks</h3>
        <TagList items={career.risks} />
      </div>

      <div className="subsection">
        <h3>Seniority reasoning</h3>
        {career.seniority_rationale && <p>{career.seniority_rationale}</p>}
        <EvidenceList evidence={career.seniority_evidence} />
      </div>

      <div className="subsection">
        <h3>Career intelligence metadata</h3>
        <div className="detail-grid">
          <div>
            <span className="label">Taxonomy version</span>
            <strong>{career.taxonomy_version}</strong>
          </div>
          <div>
            <span className="label">Engine version</span>
            <strong>{career.engine_version}</strong>
          </div>
        </div>
      </div>
    </Section>
  );
}

function JobOverview({ job }: { job?: JobProfile | null }) {
  if (!job) return null;

  const requirements =
    (job.metadata?.requirements as JobRequirement[] | undefined) ?? [];

  const requiredRequirements = requirements.filter(
    (r) => r.requirement_type === "required",
  );
  const preferredRequirements = requirements.filter(
    (r) => r.requirement_type === "preferred",
  );

  return (
    <Section title="Job description" eyebrow="Target role">
      <div className="detail-grid">
        <div>
          <span className="label">Job title</span>
          <strong>{job.job_title}</strong>
        </div>
        <div>
          <span className="label">Company</span>
          <strong>{job.company ?? "—"}</strong>
        </div>
        <div>
          <span className="label">Seniority</span>
          <strong>{job.seniority ?? "—"}</strong>
        </div>
        <div>
          <span className="label">Minimum experience</span>
          <strong>
            {job.experience_requirements?.minimum_years !== null &&
            job.experience_requirements?.minimum_years !== undefined
              ? `${job.experience_requirements.minimum_years} years`
              : "—"}
          </strong>
        </div>
      </div>

      {job.summary && <p>{job.summary}</p>}

      <div className="subsection">
        <h3>Required requirements</h3>
        {requiredRequirements.length ? (
          <div className="finding-list">
            {requiredRequirements.map((requirement) => (
              <article className="finding" key={requirement.requirement_id}>
                <div className="finding-header">
                  <strong>{requirement.text}</strong>
                  <span className="severity severity-high">Required</span>
                </div>
                <div className="recommendation-meta">
                  <span>{pretty(requirement.category)}</span>
                  {requirement.canonical_name && (
                    <span>{requirement.canonical_name}</span>
                  )}
                  <span>
                    Confidence: {confidenceLabel(requirement.confidence)}
                  </span>
                </div>
                <EvidenceList evidence={requirement.evidence} />
              </article>
            ))}
          </div>
        ) : (
          <p className="muted">No required requirements extracted.</p>
        )}
      </div>

      <div className="subsection">
        <h3>Preferred requirements</h3>
        {preferredRequirements.length ? (
          <div className="finding-list">
            {preferredRequirements.map((requirement) => (
              <article className="finding" key={requirement.requirement_id}>
                <div className="finding-header">
                  <strong>{requirement.text}</strong>
                  <span className="severity severity-medium">Preferred</span>
                </div>
                <div className="recommendation-meta">
                  <span>{pretty(requirement.category)}</span>
                  {requirement.canonical_name && (
                    <span>{requirement.canonical_name}</span>
                  )}
                  <span>
                    Confidence: {confidenceLabel(requirement.confidence)}
                  </span>
                </div>
                <EvidenceList evidence={requirement.evidence} />
              </article>
            ))}
          </div>
        ) : (
          <p className="muted">No preferred requirements extracted.</p>
        )}
      </div>

      <div className="subsection">
        <h3>Technical skills</h3>
        <TagList items={job.technical_skills} />
      </div>
      <div className="subsection">
        <h3>Soft skills</h3>
        <TagList items={job.soft_skills} />
      </div>
      <div className="subsection">
        <h3>Domain skills</h3>
        <TagList items={job.domain_skills} />
      </div>

      {job.responsibilities?.length ? (
        <div className="subsection">
          <h3>Responsibilities</h3>
          <ul>
            {job.responsibilities.map((responsibility, index) => (
              <li key={`${responsibility}-${index}`}>{responsibility}</li>
            ))}
          </ul>
        </div>
      ) : null}
    </Section>
  );
}

function MatchingSection({
  matching,
  job,
}: {
  matching?: MatchingResult | null;
  job?: JobProfile | null;
}) {
  if (!matching) return null;

  const requirements =
    (job?.metadata?.requirements as JobRequirement[] | undefined) ?? [];

  const requirementById = new Map(
    requirements.map((r) => [r.requirement_id, r]),
  );

  const relationshipClass = (r: string): string => {
    switch (r) {
      case "exact":
      case "strong_semantic":
        return "info";
      case "partial":
      case "related":
        return "medium";
      case "unmatched":
        return "high";
      default:
        return "medium";
    }
  };

  const statusClass = (s: string): string => {
    switch (s) {
      case "matched":
        return "info";
      case "partial":
        return "medium";
      case "unmatched":
        return "high";
      default:
        return "medium";
    }
  };

  return (
    <Section title="Resume ↔ JD matching" eyebrow="Semantic matching">
      <div className="detail-grid">
        <div>
          <span className="label">Matching confidence</span>
          <strong>{confidenceLabel(matching.confidence)}</strong>
        </div>
        <div>
          <span className="label">Skill relationships</span>
          <strong>{matching.skill_matches.length}</strong>
        </div>
        <div>
          <span className="label">Requirement alignments</span>
          <strong>{matching.requirement_alignments.length}</strong>
        </div>
      </div>

      <div className="subsection">
        <h3>Skill matches</h3>
        {matching.skill_matches.length ? (
          <div className="finding-list">
            {matching.skill_matches.map((match, index) => (
              <article
                className="finding matching-item"
                key={`${match.resume_skill_id}-${match.job_skill_id}-${index}`}
              >
                <div className="finding-header">
                  <strong>{pretty(match.relationship)}</strong>
                  <div className="matching-badges">
                    <span
                      className={`severity severity-${relationshipClass(match.relationship)}`}
                    >
                      {pretty(match.relationship)}
                    </span>
                    <span className="score-pill">
                      {(match.similarity * 100).toFixed(1)}% similarity
                    </span>
                  </div>
                </div>

                <div className="matching-summary">
                  <span>Confidence: {confidenceLabel(match.confidence)}</span>
                </div>

                {match.rationale ? <p>{match.rationale}</p> : null}

                <details className="evidence-details">
                  <summary>Technical match details & evidence</summary>
                  <div className="detail-grid matching-technical-details">
                    <div>
                      <span className="label">Resume skill ID</span>
                      <strong>{match.resume_skill_id}</strong>
                    </div>
                    <div>
                      <span className="label">Job skill ID</span>
                      <strong>{match.job_skill_id}</strong>
                    </div>
                    <div>
                      <span className="label">Similarity</span>
                      <strong>{(match.similarity * 100).toFixed(1)}%</strong>
                    </div>
                    <div>
                      <span className="label">Confidence</span>
                      <strong>{confidenceLabel(match.confidence)}</strong>
                    </div>
                  </div>
                  <EvidenceList evidence={match.evidence} />
                </details>
              </article>
            ))}
          </div>
        ) : (
          <p className="muted">No skill matches.</p>
        )}
      </div>

      <div className="subsection">
        <h3>Requirement alignments</h3>
        {matching.requirement_alignments.length ? (
          <div className="finding-list">
            {matching.requirement_alignments.map((alignment) => {
              const requirement = requirementById.get(alignment.requirement_id);
              return (
                <article
                  className="finding matching-item"
                  key={alignment.requirement_id}
                >
                  <div className="finding-header">
                    <strong>
                      {requirement?.text ?? alignment.requirement_id}
                    </strong>
                    <span
                      className={`severity severity-${statusClass(alignment.status)}`}
                    >
                      {pretty(alignment.status)}
                    </span>
                  </div>

                  {requirement ? (
                    <div className="matching-meta-row">
                      <span className="matching-type">
                        {pretty(requirement.requirement_type)}
                      </span>
                      <span>Category: {pretty(requirement.category)}</span>
                      {requirement.canonical_name ? (
                        <span>Skill: {requirement.canonical_name}</span>
                      ) : null}
                      <span>
                        Confidence: {confidenceLabel(alignment.confidence)}
                      </span>
                    </div>
                  ) : null}

                  {alignment.rationale ? <p>{alignment.rationale}</p> : null}

                  <details className="evidence-details">
                    <summary>Requirement evidence & technical details</summary>
                    <div className="detail-grid matching-technical-details">
                      <div>
                        <span className="label">Requirement ID</span>
                        <strong>{alignment.requirement_id}</strong>
                      </div>
                      <div>
                        <span className="label">Alignment status</span>
                        <strong>{pretty(alignment.status)}</strong>
                      </div>
                      <div>
                        <span className="label">Alignment confidence</span>
                        <strong>{confidenceLabel(alignment.confidence)}</strong>
                      </div>
                      {requirement?.confidence ? (
                        <div>
                          <span className="label">Requirement confidence</span>
                          <strong>
                            {confidenceLabel(requirement.confidence)}
                          </strong>
                        </div>
                      ) : null}
                    </div>

                    <div className="matching-evidence-group">
                      <span className="label">Alignment evidence</span>
                      <EvidenceList evidence={alignment.evidence} />
                    </div>

                    {requirement?.evidence?.length ? (
                      <div className="matching-evidence-group">
                        <span className="label">JD requirement evidence</span>
                        <EvidenceList evidence={requirement.evidence} />
                      </div>
                    ) : null}
                  </details>
                </article>
              );
            })}
          </div>
        ) : (
          <p className="muted">No requirement alignments.</p>
        )}
      </div>
    </Section>
  );
}

function RequirementsSection({
  job,
  matching,
}: {
  job?: JobProfile | null;
  matching?: MatchingResult | null;
}) {
  if (!job) return null;

  const requirements =
    (job.metadata?.requirements as JobRequirement[] | undefined) ?? [];

  const alignmentById = new Map(
    (matching?.requirement_alignments ?? []).map((a) => [a.requirement_id, a]),
  );

  if (!requirements.length && !matching?.requirement_alignments.length) {
    return null;
  }

  return (
    <Section title="Requirement analysis" eyebrow="Required vs preferred">
      {requirements.length ? (
        <div className="finding-list">
          {requirements.map((requirement) => {
            const alignment = alignmentById.get(requirement.requirement_id);
            return (
              <article className="finding" key={requirement.requirement_id}>
                <div className="finding-header">
                  <strong>{requirement.text}</strong>
                  {alignment ? (
                    <span
                      className={`severity severity-${alignment.status === "matched" ? "info" : "medium"}`}
                    >
                      {pretty(alignment.status)}
                    </span>
                  ) : (
                    <span className="severity severity-medium">
                      Not evaluated
                    </span>
                  )}
                </div>

                <div className="detail-grid">
                  <div>
                    <span className="label">Type</span>
                    <strong>{pretty(requirement.requirement_type)}</strong>
                  </div>
                  <div>
                    <span className="label">Category</span>
                    <strong>{pretty(requirement.category)}</strong>
                  </div>
                  <div>
                    <span className="label">Skill</span>
                    <strong>{requirement.canonical_name ?? "—"}</strong>
                  </div>
                  <div>
                    <span className="label">Confidence</span>
                    <strong>{confidenceLabel(requirement.confidence)}</strong>
                  </div>
                </div>

                {alignment?.rationale ? (
                  <p>
                    <strong>Alignment:</strong> {alignment.rationale}
                  </p>
                ) : null}

                {alignment ? (
                  <p>
                    <strong>Alignment confidence:</strong>{" "}
                    {confidenceLabel(alignment.confidence)}
                  </p>
                ) : null}

                <EvidenceList evidence={requirement.evidence} />

                {alignment?.evidence?.length ? (
                  <>
                    <p className="muted">Alignment evidence</p>
                    <EvidenceList evidence={alignment.evidence} />
                  </>
                ) : null}
              </article>
            );
          })}
        </div>
      ) : (
        <p className="muted">
          Detailed requirement objects are not exposed in the JobProfile
          metadata. See requirement alignments above.
        </p>
      )}
    </Section>
  );
}

function GapsSection({ result }: { result: AnalysisResult }) {
  const analysis = result.skill_analysis;

  return (
    <Section title="Skills & gaps" eyebrow="Gap analysis">
      <div className="skill-stat-grid">
        <div>
          <strong>{analysis.matched_skills.length}</strong>
          <span>Matched</span>
        </div>
        <div>
          <strong>{analysis.partial_matches.length}</strong>
          <span>Partial</span>
        </div>
        <div>
          <strong>{analysis.missing_skills.length}</strong>
          <span>Missing</span>
        </div>
        <div>
          <strong>{analysis.transferable_skills.length}</strong>
          <span>Transferable</span>
        </div>
      </div>

      <div className="subsection">
        <h3>Matched skills</h3>
        <TagList items={analysis.matched_skills} />
      </div>
      <div className="subsection">
        <h3>Partial matches</h3>
        <TagList items={analysis.partial_matches} />
      </div>
      <div className="subsection">
        <h3>Missing skills</h3>
        <TagList items={analysis.missing_skills} />
      </div>
      <div className="subsection">
        <h3>Transferable skills</h3>
        <TagList items={analysis.transferable_skills} />
      </div>

      <div className="subsection">
        <h3>Detailed gaps</h3>
        {analysis.gaps.length ? (
          <div className="finding-list">
            {analysis.gaps.map((gap: SkillGap) => (
              <article className="finding" key={gap.gap_id}>
                <div className="finding-header">
                  <strong>{gap.target_skill_name}</strong>
                  <span className="severity severity-medium">
                    {pretty(gap.gap_type)}
                  </span>
                </div>

                <div className="detail-grid">
                  <div>
                    <span className="label">Requirement type</span>
                    <strong>{pretty(gap.requirement_type)}</strong>
                  </div>
                  <div>
                    <span className="label">Match status</span>
                    <strong>{pretty(gap.match_status)}</strong>
                  </div>
                  <div>
                    <span className="label">Severity</span>
                    <strong>{pretty(gap.severity)}</strong>
                  </div>
                  <div>
                    <span className="label">Confidence</span>
                    <strong>{confidenceLabel(gap.confidence)}</strong>
                  </div>
                  {gap.similarity !== null && gap.similarity !== undefined ? (
                    <div>
                      <span className="label">Similarity</span>
                      <strong>{(gap.similarity * 100).toFixed(1)}%</strong>
                    </div>
                  ) : null}
                  {gap.requirement_id ? (
                    <div>
                      <span className="label">Requirement ID</span>
                      <strong>{gap.requirement_id}</strong>
                    </div>
                  ) : null}
                </div>

                {gap.rationale ? <p>{gap.rationale}</p> : null}
                <EvidenceList evidence={gap.evidence} />
              </article>
            ))}
          </div>
        ) : (
          <p className="muted">No detailed gaps.</p>
        )}
      </div>
    </Section>
  );
}

function ScoringSection({ scoring }: { scoring?: ScoringResult | null }) {
  if (!scoring) return null;

  return (
    <Section title="Job fit scoring" eyebrow="Overall suitability">
      <div className="score-grid">
        <ScoreCard
          label="Overall score"
          score={scoring.overall_score}
          description={`Confidence: ${confidenceLabel(scoring.confidence)}`}
        />
      </div>

      {scoring.dimension_scores?.length ? (
        <DimensionTable dimensions={scoring.dimension_scores} />
      ) : null}

      <div className="subsection">
        <h3>Score contributions</h3>
        {scoring.contributions?.length ? (
          <div className="finding-list">
            {scoring.contributions.map((contribution) => (
              <article className="finding" key={contribution.contribution_id}>
                <div className="finding-header">
                  <strong>{pretty(contribution.dimension)}</strong>
                  <span className="score-pill">
                    {contribution.contribution >= 0 ? "+" : ""}
                    {contribution.contribution.toFixed(3)}
                  </span>
                </div>

                <div className="detail-grid">
                  <div>
                    <span className="label">Source</span>
                    <strong>{pretty(contribution.source_type)}</strong>
                  </div>
                  <div>
                    <span className="label">Score</span>
                    <strong>{contribution.score.toFixed(3)}</strong>
                  </div>
                  <div>
                    <span className="label">Weight</span>
                    <strong>{contribution.weight.toFixed(3)}</strong>
                  </div>
                  {contribution.requirement_type ? (
                    <div>
                      <span className="label">Requirement type</span>
                      <strong>{pretty(contribution.requirement_type)}</strong>
                    </div>
                  ) : null}
                </div>

                <p>{contribution.rationale}</p>
                <div className="muted">Source ID: {contribution.source_id}</div>
              </article>
            ))}
          </div>
        ) : (
          <p className="muted">No score contributions recorded.</p>
        )}
      </div>

      <h3>Penalties</h3>
      {scoring.penalties?.length ? (
        <div className="finding-list">
          {scoring.penalties.map((adjustment, index) => (
            <article className="finding" key={`penalty-${index}`}>
              <div className="finding-header">
                <strong>{adjustment.reason}</strong>
                <span className="score-pill">
                  {adjustment.value > 0 ? "+" : ""}
                  {adjustment.value.toFixed(2)}
                </span>
              </div>
            </article>
          ))}
        </div>
      ) : (
        <p className="muted">No penalties recorded.</p>
      )}

      <h3>Bonuses</h3>
      {scoring.bonuses?.length ? (
        <div className="finding-list">
          {scoring.bonuses.map((adjustment, index) => (
            <article className="finding" key={`bonus-${index}`}>
              <div className="finding-header">
                <strong>{adjustment.reason}</strong>
                <span className="score-pill">
                  {adjustment.value > 0 ? "+" : ""}
                  {adjustment.value.toFixed(2)}
                </span>
              </div>
            </article>
          ))}
        </div>
      ) : (
        <p className="muted">No bonuses recorded.</p>
      )}
    </Section>
  );
}

function XAISection({ xai }: { xai?: XAIResult | null }) {
  if (!xai) return null;

  return (
    <Section
      title="Explainability"
      eyebrow="Why the system reached these results"
    >
      <div className="detail-grid">
        <div>
          <span className="label">Confidence</span>
          <strong>{confidenceLabel(xai.confidence)}</strong>
        </div>
        <div>
          <span className="label">Evidence map entries</span>
          <strong>{xai.evidence_map.length}</strong>
        </div>
      </div>

      <div className="subsection">
        <h3>Overall explanation</h3>
        <p>{xai.overall_explanation}</p>
      </div>
      <div className="subsection">
        <h3>Score explanation</h3>
        <p>{xai.score_explanation}</p>
      </div>
      <div className="subsection">
        <h3>Strengths</h3>
        <TagList items={xai.strengths} />
      </div>
      <div className="subsection">
        <h3>Weaknesses</h3>
        <TagList items={xai.weaknesses} />
      </div>

      <div className="subsection">
        <h3>Matched skill explanations</h3>
        {xai.matched_skill_explanations.length ? (
          xai.matched_skill_explanations.map((item) => (
            <article className="compact-card" key={item.skill_id}>
              <strong>{item.skill_id}</strong>
              <p>{item.explanation}</p>
              <p>
                <strong>Confidence:</strong> {confidenceLabel(item.confidence)}
              </p>
              <EvidenceList evidence={item.evidence} />
            </article>
          ))
        ) : (
          <p className="muted">None.</p>
        )}
      </div>

      <div className="subsection">
        <h3>Partial-match explanations</h3>
        {xai.partial_match_explanations.length ? (
          xai.partial_match_explanations.map((item) => (
            <article className="compact-card" key={item.skill_id}>
              <strong>{item.skill_id}</strong>
              <p>{item.explanation}</p>
              <p>
                <strong>Confidence:</strong> {confidenceLabel(item.confidence)}
              </p>
              <EvidenceList evidence={item.evidence} />
            </article>
          ))
        ) : (
          <p className="muted">None.</p>
        )}
      </div>

      <div className="subsection">
        <h3>Missing skill explanations</h3>
        {xai.missing_skill_explanations.length ? (
          xai.missing_skill_explanations.map((item) => (
            <article className="compact-card" key={item.skill_id}>
              <strong>{item.skill_id}</strong>
              <p>{item.explanation}</p>
              <p>
                <strong>Confidence:</strong> {confidenceLabel(item.confidence)}
              </p>
              <EvidenceList evidence={item.evidence} />
            </article>
          ))
        ) : (
          <p className="muted">None.</p>
        )}
      </div>

      <div className="subsection">
        <h3>Evidence map</h3>
        {xai.evidence_map.length ? (
          <div className="finding-list">
            {xai.evidence_map.map((entry, index) => (
              <article
                className="finding"
                key={`${entry.result_type}-${entry.result_id}-${index}`}
              >
                <div className="finding-header">
                  <strong>{pretty(entry.result_type)}</strong>
                  <span className="score-pill">
                    {entry.evidence.length} evidence
                  </span>
                </div>
                <p>
                  <strong>Result ID:</strong> {entry.result_id}
                </p>
                <EvidenceList evidence={entry.evidence} />
              </article>
            ))}
          </div>
        ) : (
          <p className="muted">No evidence map entries.</p>
        )}
      </div>
    </Section>
  );
}

function RecommendationSection({
  recommendations,
}: {
  recommendations: Recommendation[];
}) {
  return (
    <Section title="Recommendations" eyebrow="Action plan">
      {recommendations.length ? (
        <div className="recommendation-list">
          {recommendations.map((recommendation) => (
            <article
              className="recommendation-card"
              key={recommendation.recommendation_id}
            >
              <div className="finding-header">
                <strong>{recommendation.title}</strong>
                <span
                  className={`severity severity-${recommendation.priority}`}
                >
                  {pretty(recommendation.priority)}
                </span>
              </div>

              <div className="recommendation-meta">
                <span>{pretty(recommendation.type)}</span>
                <span>Impact: {pretty(recommendation.expected_impact)}</span>
                <span>Effort: {pretty(recommendation.effort)}</span>
                {recommendation.priority_score !== undefined && (
                  <span>
                    Priority score: {recommendation.priority_score.toFixed(1)}
                  </span>
                )}
                {recommendation.impact_score !== undefined && (
                  <span>
                    Impact score: {recommendation.impact_score.toFixed(1)}
                  </span>
                )}
              </div>

              <p>{recommendation.rationale}</p>

              {recommendation.target_skill && (
                <p>
                  <strong>Target skill:</strong> {recommendation.target_skill}
                </p>
              )}

              {recommendation.related_gap_ids.length > 0 && (
                <p>
                  <strong>Related gaps:</strong>{" "}
                  {recommendation.related_gap_ids.join(", ")}
                </p>
              )}

              <p>
                <strong>Confidence:</strong>{" "}
                {confidenceLabel(recommendation.confidence)}
              </p>

              <EvidenceList evidence={recommendation.evidence} />
            </article>
          ))}
        </div>
      ) : (
        <p className="muted">No recommendations generated.</p>
      )}
    </Section>
  );
}

function PromptSection({ prompt }: { prompt?: string | null }) {
  const [copied, setCopied] = useState(false);

  if (!prompt) return null;

  async function copyPrompt() {
    try {
      await navigator.clipboard.writeText(prompt ?? "");
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1800);
    } catch {
      setCopied(false);
    }
  }

  return (
    <Section
      title="Resume improvement prompt"
      eyebrow="External GenAI workflow"
    >
      <div className="prompt-toolbar">
        <p>
          Copy this evidence-backed prompt into another GenAI tool to customize
          the resume without inventing facts.
        </p>
        <button type="button" onClick={copyPrompt}>
          {copied ? "Copied" : "Copy prompt"}
        </button>
      </div>
      <textarea className="prompt-output" readOnly value={prompt} />
    </Section>
  );
}

/* =========================================================
   DASHBOARD WITH RESULTS
   ========================================================= */

/* =========================================================
   ANALYSIS DASHBOARD — restructured
   Hero → Overview tiles → Tabbed sections
   ========================================================= */

type DashboardTab =
  | "resume"
  | "quality"
  | "ats"
  | "language"
  | "career"
  | "matching";

function AnalysisDashboard({
  result,
  onNewAnalysis,
}: {
  result: AnalysisResult;
  onNewAnalysis: () => void;
}) {
  const [tab, setTab] = useState<DashboardTab>("resume");

  const suitability = useMemo(() => {
    if (!result.scoring) return "Resume-only";
    const score = result.scoring.overall_score;
    if (score >= 75) return "Strong fit";
    if (score >= 55) return "Potential fit";
    if (score >= 35) return "Weak fit";
    return "Low fit";
  }, [result.scoring]);


  const tabs: { id: DashboardTab; label: string; count?: number }[] = [];

  if (result.resume_profile) {
    tabs.push({
      id: "resume",
      label: "Resume",
      count: result.resume_profile.skills?.length,
    });
  }
  if (result.resume_quality) {
    tabs.push({
      id: "quality",
      label: "Quality",
      count: result.resume_quality.findings.length,
    });
  }
  if (result.ats_intelligence) {
    tabs.push({
      id: "ats",
      label: "ATS",
      count: result.ats_intelligence.findings.length,
    });
  }
  if (result.language_quality) {
    tabs.push({
      id: "language",
      label: "Language",
      count: result.language_quality.issues.length,
    });
  }
  if (result.career_intelligence) {
    tabs.push({
      id: "career",
      label: "Career",
      count: result.career_intelligence.career_directions?.length,
    });
  }
  if (
    result.analysis_mode === "resume_jd" &&
    (result.matching || result.scoring)
  ) {
    tabs.push({
      id: "matching",
      label: "JD match",
      count: result.matching?.requirement_alignments.length,
    });
  }

  return (
    <div className="dash">
      <header className="dash-hero">
        <div className="dash-hero__main">
          <span className="dash-hero__eyebrow">
            <span className="dash-hero__dot" aria-hidden="true" />
            Analysis dashboard
          </span>

          <h1 className="dash-hero__title">
            {result.job_profile?.job_title ?? "Resume intelligence report"}
          </h1>

          <p className="dash-hero__sub">
            {result.analysis_mode === "resume_jd"
              ? "Resume and job description analysis"
              : "Resume-only career analysis"}
            {" · "}
            <span className="dash-hero__id">
              {result.analysis_id.slice(0, 8)}
            </span>
          </p>

          <div className="dash-hero__actions">
            <button
              type="button"
              className="primary-button"
              onClick={onNewAnalysis}
            >
              New analysis
            </button>
            <button
              type="button"
              className="ghost-button"
              onClick={() => {
                navigator.clipboard.writeText(result.analysis_id);
              }}
            >
              Copy ID
            </button>
          </div>
        </div>

        <div className="dash-status">
          <div className="dash-status__tick" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none">
              <path
                d="M5 12.5l4.5 4.5L19 7.5"
                stroke="currentColor"
                strokeWidth="2.4"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>

          <div className="dash-status__meta">
            <span className="dash-status__label">Assessment</span>
            <strong className="dash-status__value">{suitability}</strong>
            <span className="dash-status__sub">
              {result.scoring
                ? `${scoreLabel(result.scoring.overall_score)} overall`
                : "Resume-only · no JD"}
            </span>
          </div>
        </div>
      </header>

      <section className="dash-overview" aria-label="Score overview">
        {result.resume_quality && (
          <ScoreCard
            label="Resume quality"
            score={result.resume_quality.overall_score}
            description={`Confidence ${confidenceLabel(
              result.resume_quality.confidence,
            )}`}
          />
        )}
        {result.ats_intelligence && (
          <ScoreCard
            label="ATS readiness"
            score={result.ats_intelligence.overall_score}
            description={`Confidence ${confidenceLabel(
              result.ats_intelligence.confidence,
            )}`}
          />
        )}
        {result.language_quality && (
          <ScoreCard
            label="Language quality"
            score={result.language_quality.overall_score}
            description={
              result.language_quality.authorship_heuristic.level
            }
          />
        )}
      </section>

      <nav className="dash-tabs" aria-label="Report sections">
        {tabs.map((t) => (
          <button
            key={t.id}
            type="button"
            className={`dash-tab ${tab === t.id ? "is-active" : ""}`}
            onClick={() => setTab(t.id)}
          >
            <span className="dash-tab__label">{t.label}</span>
            {t.count != null && t.count > 0 && (
              <span className="dash-tab__count">{t.count}</span>
            )}
          </button>
        ))}
      </nav>

      <div className="dash-panel">
        {tab === "resume" && <ResumeOverview result={result} />}
        {tab === "quality" && (
          <QualitySection quality={result.resume_quality} />
        )}
        {tab === "ats" && (
          <ATSSection ats={result.ats_intelligence} />
        )}
        {tab === "language" && (
          <LanguageSection language={result.language_quality} />
        )}
        {tab === "career" && (
          <CareerSection career={result.career_intelligence} />
        )}
        {tab === "matching" && (
          <>
            <JobOverview job={result.job_profile} />
            <MatchingSection
              matching={result.matching}
              job={result.job_profile}
            />
            <RequirementsSection
              job={result.job_profile}
              matching={result.matching}
            />
            <GapsSection result={result} />
            <ScoringSection scoring={result.scoring} />
            <XAISection xai={result.xai} />
          </>
        )}
      </div>

      <section className="dash-secondary">
        <RecommendationSection recommendations={result.recommendations} />
        <PromptSection prompt={result.resume_improvement_prompt} />

        <Section title="Analysis metadata" eyebrow="Technical">
          <div className="detail-grid">
            <div>
              <span className="label">Analysis ID</span>
              <strong>{result.analysis_id}</strong>
            </div>
            <div>
              <span className="label">Mode</span>
              <strong>{pretty(result.analysis_mode)}</strong>
            </div>
            <div>
              <span className="label">Status</span>
              <strong>{pretty(result.status)}</strong>
            </div>
            <div>
              <span className="label">Schema</span>
              <strong>{result.schema_version}</strong>
            </div>
            <div>
              <span className="label">Processing time</span>
              <strong>
                {result.metadata.processing_time_ms != null
                  ? `${result.metadata.processing_time_ms} ms`
                  : "—"}
              </strong>
            </div>
            <div>
              <span className="label">Engine versions</span>
              <strong>
                {Object.keys(result.metadata.engine_versions).length}
              </strong>
            </div>
          </div>

          {result.metadata.warnings.length > 0 && (
            <div className="warning-box">
              <strong>Analysis warnings</strong>
              <ul>
                {result.metadata.warnings.map((w, i) => (
                  <li key={`${w}-${i}`}>{w}</li>
                ))}
              </ul>
            </div>
          )}

          <details>
            <summary>Open canonical JSON</summary>
            <pre className="json-output">
              {JSON.stringify(result, null, 2)}
            </pre>
          </details>
        </Section>
      </section>
    </div>
  );
}

/* =========================================================
   ZERO-STATE DASHBOARD (Home with no analysis)
   ========================================================= */

function ZeroStateDashboard({
  onStartAnalysis,
}: {
  onStartAnalysis: () => void;
}) {
  return (
    <div className="zero-state">
      <section className="zero-hero">
        <span className="eyebrow">Analysis dashboard</span>
        <h1>No analysis yet</h1>
        <p>
          Run your first analysis to unlock resume quality, ATS readiness,
          career direction, and job-fit scoring — all backed by evidence you can
          inspect.
        </p>

        <div className="zero-cta">
          <button
            type="button"
            className="primary-button"
            onClick={onStartAnalysis}
          >
            Run your first analysis
          </button>
        </div>
      </section>

      <section className="zero-modules" aria-label="What you'll get">
        <article className="zero-module">
          <span className="zero-module__index">01</span>
          <h3>Resume quality</h3>
          <p>Structure, clarity, and completeness scoring with findings.</p>
          <div className="zero-module__preview" aria-hidden="true">
            <span className="preview-bar" style={{ width: "62%" }} />
          </div>
        </article>

        <article className="zero-module">
          <span className="zero-module__index">02</span>
          <h3>ATS readiness</h3>
          <p>Machine-readability, keyword parsing, and format analysis.</p>
          <div className="zero-module__preview" aria-hidden="true">
            <span className="preview-bar" style={{ width: "84%" }} />
          </div>
        </article>

        <article className="zero-module">
          <span className="zero-module__index">03</span>
          <h3>Career intelligence</h3>
          <p>Direction, seniority, transferable strengths, and paths.</p>
          <div className="zero-module__preview" aria-hidden="true">
            <span className="preview-bar" style={{ width: "47%" }} />
          </div>
        </article>

        <article className="zero-module">
          <span className="zero-module__index">04</span>
          <h3>Skills & gaps</h3>
          <p>Matched, partial, missing, and transferable skills.</p>
          <div className="zero-module__preview" aria-hidden="true">
            <span className="preview-bar" style={{ width: "73%" }} />
          </div>
        </article>

        <article className="zero-module">
          <span className="zero-module__index">05</span>
          <h3>Explainability</h3>
          <p>Every score traceable to evidence in your resume and JD.</p>
          <div className="zero-module__preview" aria-hidden="true">
            <span className="preview-bar" style={{ width: "100%" }} />
          </div>
        </article>

        <article className="zero-module">
          <span className="zero-module__index">06</span>
          <h3>Recommendations</h3>
          <p>Prioritized actions ranked by impact and effort.</p>
          <div className="zero-module__preview" aria-hidden="true">
            <span className="preview-bar" style={{ width: "58%" }} />
          </div>
        </article>
      </section>

      <section className="zero-steps">
        <div className="zero-step">
          <span className="zero-step__num">1</span>
          <div>
            <h4>Upload your resume</h4>
            <p>PDF or DOCX, up to 10 MB.</p>
          </div>
        </div>
        <div className="zero-step">
          <span className="zero-step__num">2</span>
          <div>
            <h4>Add a job description (optional)</h4>
            <p>Unlock JD-specific matching, gaps, and fit scoring.</p>
          </div>
        </div>
        <div className="zero-step">
          <span className="zero-step__num">3</span>
          <div>
            <h4>Get the report</h4>
            <p>Evidence-backed findings and next actions in seconds.</p>
          </div>
        </div>
      </section>
    </div>
  );
}

/* =========================================================
   LANDING
   ========================================================= */

function LandingPage({ onStart }: { onStart: () => void }) {
  return (
    <div className="landing-grid">
      <section className="landing-copy">
        <span className="eyebrow">Explainable career intelligence</span>

        <h1>
          Understand what your resume says, where it fits,{" "}
          <em>and what to improve.</em>
        </h1>

        <p>
          SkillLens analyzes resume quality, ATS readiness, career direction,
          language quality, job alignment, skill gaps, recommendations and
          evidence-backed explanations.
        </p>
      </section>

      <div className="landing-cta">
        <button type="button" className="primary-button" onClick={onStart}>
          Analyze a resume
        </button>
        <button type="button" className="ghost-button" onClick={onStart}>
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <polygon points="5 3 19 12 5 21 5 3" />
          </svg>
          Watch demo
        </button>
      </div>

      <div className="landing-stats">
        <span className="stat">
          <strong>10k+</strong> resumes analyzed
        </span>
        <span className="sep" aria-hidden="true" />
        <span className="stat">
          <strong>98%</strong> parsing accuracy
        </span>
        <span className="sep" aria-hidden="true" />
        <span className="stat">
          <strong>6</strong> analysis modules
        </span>
        <span className="sep" aria-hidden="true" />
        <span className="stat">
          <strong>100%</strong> evidence-backed
        </span>
      </div>

      <div className="landing-preview" aria-hidden="true">
        <div className="landing-preview__chrome">
          <span className="dot red" />
          <span className="dot amber" />
          <span className="dot green" />
          <span className="url">skilllens.app / dashboard</span>
        </div>

        <div className="landing-preview__body">
          <div className="preview-card">
            <div className="k">Resume quality</div>
            <div className="v">78.9</div>
            <div className="bar">
              <i />
            </div>
            <div className="meta">Confidence · high</div>
          </div>
          <div className="preview-card">
            <div className="k">ATS readiness</div>
            <div className="v">92.7</div>
            <div className="bar">
              <i />
            </div>
            <div className="meta">Machine readable</div>
          </div>
          <div className="preview-card">
            <div className="k">JD fit</div>
            <div className="v">94.0</div>
            <div className="bar">
              <i />
            </div>
            <div className="meta">Semantic match</div>
          </div>
        </div>

        <span className="landing-preview__chip left">
          <span className="swatch" /> Strong fit · 82.4
        </span>
        <span className="landing-preview__chip right">
          <span className="swatch" /> 6 skill matches
        </span>
      </div>

      <section className="landing-map" aria-label="Analysis modules">
        <div className="map-node node-main" aria-hidden="true" />
        <div className="map-line" aria-hidden="true" />

        <div className="map-node">
          <span className="node-index">01</span>
          <strong>Quality</strong>
          <span>Resume structure, clarity & completeness.</span>
        </div>
        <div className="map-node">
          <span className="node-index">02</span>
          <strong>ATS</strong>
          <span>Machine-readability & format parsing.</span>
        </div>
        <div className="map-node">
          <span className="node-index">03</span>
          <strong>Career</strong>
          <span>Direction, seniority & transferable strengths.</span>
        </div>
        <div className="map-node">
          <span className="node-index">04</span>
          <strong>Skills</strong>
          <span>Matched, partial, missing & transferable.</span>
        </div>
        <div className="map-node">
          <span className="node-index">05</span>
          <strong>XAI</strong>
          <span>Evidence-backed explanations for every call.</span>
        </div>
        <div className="map-node">
          <span className="node-index">06</span>
          <strong>Actions</strong>
          <span>Prioritized improvements by impact & effort.</span>
        </div>
      </section>
    </div>
  );
}

/* =========================================================
   INPUT
   ========================================================= */

function InputPage({
  onSubmit,
  error,
}: {
  onSubmit: (resume: File | null, jd: File | null, jdText: string) => void;
  error: string | null;
}) {
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [jdFile, setJdFile] = useState<File | null>(null);
  const [jdText, setJdText] = useState("");

  const [resumeDragging, setResumeDragging] = useState(false);
  const [jdDragging, setJdDragging] = useState(false);

  const resumeInputValid = Boolean(resumeFile);
  const jdInputValid =
    !jdFile && !jdText.trim()
      ? true
      : Boolean(jdFile) !== Boolean(jdText.trim());
  const canSubmit = resumeInputValid && jdInputValid;

  function handleResumeFile(file: File | null) {
    setResumeFile(file);
  }

  function handleJdFile(file: File | null) {
    setJdFile(file);
    if (file) setJdText("");
  }

  function fileSizeLabel(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  return (
    <section className="upload-page">
      {/* ---------- Hero (now includes the CTA) ---------- */}
      <div className="upload-hero">
        <div className="upload-hero__top">
          <span className="eyebrow">Step 01 · Setup</span>
          <h1>Give SkillLens your resume.</h1>
        </div>

        <p>
          Upload a resume to unlock quality, ATS, language, career, and
          recommendation analysis. Add a job description to unlock JD-specific
          matching and fit scoring.
        </p>

        {/* Alerts sit inside the hero so they appear right under the CTA row */}
        {(!jdInputValid || error) && (
          <div className="upload-alerts upload-alerts--inline">
            {!jdInputValid && (
              <div className="warning-box">
                Provide the job description as either a file or pasted text —
                not both.
              </div>
            )}
            {error && <div className="error-box">{error}</div>}
          </div>
        )}

        {/* Primary CTA — always visible above the fold */}
        <div className="upload-cta upload-cta--hero">
          <button
            type="button"
            className="primary-button"
            disabled={!canSubmit}
            onClick={() => onSubmit(resumeFile, jdFile, jdText.trim())}
          >
            Run SkillLens analysis
          </button>
          <span className="upload-cta__hint">
            Takes about 5–10 seconds · Nothing is stored on our servers
          </span>
        </div>
      </div>

      {/* ---------- Two symmetrical cards ---------- */}
      <div className="upload-grid">
        {/* ---- Resume (required) ---- */}
        <section className="upload-card upload-card--required">
          <header className="upload-card__head">
            <div className="upload-card__title">
              <span className="upload-card__tag">Required</span>
              <h2>Resume</h2>
            </div>
            <span className="upload-card__index" aria-hidden="true">
              01
            </span>
          </header>

          <p className="upload-card__desc">
            PDF or DOCX · up to 10 MB. Text is extracted locally before it
            leaves your browser.
          </p>

          <label
            className={`upload-drop ${resumeDragging ? "is-dragging" : ""} ${
              resumeFile ? "has-file" : ""
            }`}
            onDragOver={(e) => {
              e.preventDefault();
              setResumeDragging(true);
            }}
            onDragLeave={() => setResumeDragging(false)}
            onDrop={(e) => {
              e.preventDefault();
              setResumeDragging(false);
              const file = e.dataTransfer.files?.[0] ?? null;
              if (file) handleResumeFile(file);
            }}
          >
            <input
              type="file"
              accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
              onChange={(e) => handleResumeFile(e.target.files?.[0] ?? null)}
            />

            <span className="upload-drop__icon" aria-hidden="true">
              {resumeFile ? (
                <svg viewBox="0 0 24 24">
                  <path d="M6 2h9l5 5v15H6z" />
                  <path d="M15 2v5h5" />
                  <path d="M9 13l2 2 4-4" />
                </svg>
              ) : (
                <svg viewBox="0 0 24 24">
                  <path d="M12 16V4" />
                  <path d="M7 9l5-5 5 5" />
                  <path d="M5 20h14" />
                </svg>
              )}
            </span>

            {resumeFile ? (
              <>
                <strong className="upload-drop__filename">
                  {resumeFile.name}
                </strong>
                <span className="upload-drop__meta">
                  {fileSizeLabel(resumeFile.size)} · Ready to analyze
                </span>
                <span className="upload-drop__action">Replace file</span>
              </>
            ) : (
              <>
                <strong className="upload-drop__title">
                  Drop your resume here
                </strong>
                <span className="upload-drop__meta">
                  or click to browse · PDF, DOCX
                </span>
                <span className="upload-drop__action">Choose file</span>
              </>
            )}
          </label>

          <div className="upload-card__foot">
            <span
              className={`upload-status ${resumeFile ? "is-ok" : "is-idle"}`}
            >
              <span className="upload-status__dot" aria-hidden="true" />
              {resumeFile ? "Ready" : "Waiting for file"}
            </span>
          </div>
        </section>

        {/* ---- JD (optional) ---- */}
        <section className="upload-card upload-card--optional">
          <header className="upload-card__head">
            <div className="upload-card__title">
              <span className="upload-card__tag upload-card__tag--optional">
                Optional
              </span>
              <h2>Job description</h2>
            </div>
            <span className="upload-card__index" aria-hidden="true">
              02
            </span>
          </header>

          <p className="upload-card__desc">
            Add a JD as a file or paste the text. Activates matching, gaps, and
            fit scoring.
          </p>

          {!jdFile && (
            <label
              className={`upload-drop upload-drop--compact ${
                jdDragging ? "is-dragging" : ""
              }`}
              onDragOver={(e) => {
                e.preventDefault();
                setJdDragging(true);
              }}
              onDragLeave={() => setJdDragging(false)}
              onDrop={(e) => {
                e.preventDefault();
                setJdDragging(false);
                const file = e.dataTransfer.files?.[0] ?? null;
                if (file) handleJdFile(file);
              }}
            >
              <input
                type="file"
                accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                onChange={(e) => handleJdFile(e.target.files?.[0] ?? null)}
              />

              <span className="upload-drop__icon" aria-hidden="true">
                <svg viewBox="0 0 24 24">
                  <path d="M12 16V4" />
                  <path d="M7 9l5-5 5 5" />
                  <path d="M5 20h14" />
                </svg>
              </span>

              <strong className="upload-drop__title">Drop JD file here</strong>
              <span className="upload-drop__meta">
                PDF, DOCX · or paste below
              </span>
            </label>
          )}

          {jdFile && (
            <div className="upload-file-chip">
              <span className="upload-file-chip__icon" aria-hidden="true">
                <svg viewBox="0 0 24 24">
                  <path d="M6 2h9l5 5v15H6z" />
                  <path d="M15 2v5h5" />
                </svg>
              </span>
              <div className="upload-file-chip__body">
                <strong>{jdFile.name}</strong>
                <span>{fileSizeLabel(jdFile.size)} · Attached</span>
              </div>
              <button
                type="button"
                className="upload-file-chip__remove"
                aria-label="Remove job description file"
                onClick={() => setJdFile(null)}
              >
                <svg viewBox="0 0 24 24">
                  <path d="M6 6l12 12M18 6L6 18" />
                </svg>
              </button>
            </div>
          )}

          <div className="upload-or">
            <span>OR paste text</span>
          </div>

          <textarea
            className="upload-textarea"
            value={jdText}
            onChange={(e) => {
              setJdText(e.target.value);
              if (e.target.value.trim()) setJdFile(null);
            }}
            placeholder="Paste the job description here…"
          />

          <div className="upload-card__foot">
            <span
              className={`upload-status ${
                jdFile || jdText.trim() ? "is-ok" : "is-idle"
              }`}
            >
              <span className="upload-status__dot" aria-hidden="true" />
              {jdFile
                ? "File attached"
                : jdText.trim()
                  ? `${jdText.trim().length} characters`
                  : "Optional · skip if not needed"}
            </span>
          </div>
        </section>
      </div>
    </section>
  );
}

/* =========================================================
   ANALYZING
   ========================================================= */

function AnalyzingPage() {
  return (
    <div className="analyzing-view">
      <div className="analysis-loader">
        <div className="loader-ring" />
        <span className="eyebrow">Analysis running</span>
        <h1>Reading your resume.</h1>
        <p>
          SkillLens is processing the document through the analysis pipeline.
          This may take a moment.
        </p>
      </div>
    </div>
  );
}

/* =========================================================
   API
   ========================================================= */

async function parseApiError(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as ApiError;
    if (payload.message) {
      return payload.code
        ? `${payload.code}: ${payload.message}`
        : payload.message;
    }
  } catch {
    // fall through
  }
  return `Request failed with HTTP ${response.status}.`;
}

async function runAnalysis(
  resume: File | null,
  jd: File | null,
  jdText: string,
): Promise<AnalysisResult> {
  const hasJd = Boolean(jd || jdText.trim());
  const form = new FormData();

  if (!resume) {
    throw new Error("A resume PDF or DOCX file is required.");
  }

  form.append("resume", resume);

  form.append(
    "options",
    JSON.stringify({
      include_career_intelligence: true,
      include_recommendations: true,
      include_xai: true,
    }),
  );

  form.append(
    "client_metadata",
    JSON.stringify({
      source: "skilllens-web",
      session_id: null,
      extra: { frontend_version: "phase9-temporary-ui-v3" },
    }),
  );

  let endpoint = `${API_BASE}/analyses/resume`;
  if (hasJd) {
    endpoint = `${API_BASE}/analyses/resume-jd`;
    if (jd) {
      form.append("job_description", jd);
    } else {
      form.append("job_description_text", jdText);
    }
  }

  const response = await fetch(endpoint, { method: "POST", body: form });

  if (!response.ok) {
    throw new Error(await parseApiError(response));
  }

  const payload = (await response.json()) as { data: AnalysisResult };
  if (!payload.data) {
    throw new Error("The API returned no AnalysisResult.");
  }
  return payload.data;
}

/* =========================================================
   APP
   ========================================================= */

function App() {
  const [page, setPage] = useState<Page>("landing");
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  }, [page]);

  function navigate(next: Page) {
    setError(null);
    setPage(next);
  }

  async function handleSubmit(
    resume: File | null,
    jd: File | null,
    jdText: string,
  ) {
    setError(null);
    setPage("analyzing");
    try {
      const result = await runAnalysis(resume, jd, jdText);
      setAnalysis(result);
      setPage("dashboard");
    } catch (caught) {
      const message =
        caught instanceof Error
          ? caught.message
          : "An unexpected analysis error occurred.";
      setError(message);
      setPage("input");
    }
  }

  function handleNewAnalysis() {
    setAnalysis(null);
    setError(null);
    setPage("input");
  }

  const analysisExists = Boolean(analysis);

  /* ---------- routing ---------- */

  let body: React.ReactNode = null;

  if (page === "landing") {
    body = <LandingPage onStart={() => navigate("input")} />;
  } else if (page === "input") {
    body = <InputPage onSubmit={handleSubmit} error={error} />;
  } else if (page === "analyzing") {
    body = <AnalyzingPage />;
  } else if (page === "dashboard") {
    body = analysis ? (
      <AnalysisDashboard result={analysis} onNewAnalysis={handleNewAnalysis} />
    ) : (
      <ZeroStateDashboard onStartAnalysis={() => navigate("input")} />
    );
  }

  return (
    <main className="app-shell">
      <Header
        page={page}
        onNavigate={navigate}
        onNewAnalysis={handleNewAnalysis}
        analysisExists={analysisExists}
      />
      <div className="app-content">{body}</div>
    </main>
  );
}

export default App;
