import { useState } from "react";

import "./styles.css";
import type {
  AnalysisResult,
  Recommendation,
  RoleFit,
} from "../types/analysis";

const API_BASE_URL = "http://127.0.0.1:8000";

function scoreLabel(score: number) {
  return `${score.toFixed(1)}%`;
}

function SkillList({
  title,
  skills,
  emptyMessage,
}: {
  title: string;
  skills: string[];
  emptyMessage: string;
}) {
  return (
    <section className="result-section">
      <h3>{title}</h3>

      {skills.length > 0 ? (
        <div className="tag-list">
          {skills.map((skill) => (
            <span className="skill-tag" key={skill}>
              {skill}
            </span>
          ))}
        </div>
      ) : (
        <p className="muted">{emptyMessage}</p>
      )}
    </section>
  );
}

function RoleFitList({ roles }: { roles: RoleFit[] }) {
  if (roles.length === 0) {
    return <p className="muted">No career suggestions were generated.</p>;
  }

  return (
    <div className="role-list">
      {roles.map((role) => (
        <article className="role-item" key={role.role}>
          <div className="role-heading">
            <strong>{role.role}</strong>
            <span>{scoreLabel(role.fit_score)}</span>
          </div>

          <div className="score-track">
            <div
              className="score-fill"
              style={{
                width: `${Math.max(0, Math.min(100, role.fit_score))}%`,
              }}
            />
          </div>

          {role.rationale && <p>{role.rationale}</p>}
        </article>
      ))}
    </div>
  );
}

function RecommendationList({
  recommendations,
}: {
  recommendations: Recommendation[];
}) {
  if (recommendations.length === 0) {
    return <p className="muted">No recommendations were generated.</p>;
  }

  return (
    <div className="recommendation-list">
      {recommendations.map((recommendation) => (
        <article
          className="recommendation-item"
          key={recommendation.recommendation_id}
        >
          <div className="recommendation-heading">
            <strong>{recommendation.title}</strong>
            <span className="small-label">
              {recommendation.priority}
            </span>
          </div>

          <p>{recommendation.rationale}</p>

          {recommendation.expected_impact && (
            <p>
              <strong>Expected impact:</strong>{" "}
              {recommendation.expected_impact}
            </p>
          )}
        </article>
      ))}
    </div>
  );
}

function AnalysisResults({ result }: { result: AnalysisResult }) {
  const scoring = result.scoring;
  const skillAnalysis = result.skill_analysis;
  const career = result.career_intelligence;

  return (
    <section className="results-panel">
      <div className="result-header">
        <div>
          <p className="eyebrow">ANALYSIS COMPLETE</p>
          <h2>Your SkillLens report</h2>
          <p className="muted">
            Review your current fit, skill gaps, and possible next steps.
          </p>
        </div>

        {scoring && (
          <div className="score-card">
            <span>Overall fit</span>
            <strong>{scoreLabel(scoring.overall_score)}</strong>
          </div>
        )}
      </div>

      {skillAnalysis && result.job_profile && (
        <div className="result-grid">
          <SkillList
            title="Matched skills"
            skills={skillAnalysis.matched_skills}
            emptyMessage="No direct skill matches were found."
          />

          <SkillList
            title="Missing skills"
            skills={skillAnalysis.missing_skills}
            emptyMessage="No missing skills were identified."
          />

          <SkillList
            title="Transferable skills"
            skills={skillAnalysis.transferable_skills}
            emptyMessage="No transferable skills were identified."
          />

          <SkillList
            title="Partial matches"
            skills={skillAnalysis.partial_matches}
            emptyMessage="No partial matches were identified."
          />
        </div>
      )}

      {career && (
        <section className="result-section">
          <h3>
            {result.job_profile
              ? "Career direction relative to this job"
              : "Suggested career directions"}
          </h3>

          {career.transition_analysis && (
            <p className="transition-summary">
              {career.transition_analysis}
            </p>
          )}

          <RoleFitList roles={career.role_fit} />
        </section>
      )}

      <section className="result-section">
        <h3>Recommendations</h3>
        <RecommendationList recommendations={result.recommendations} />
      </section>

      <details className="raw-response">
        <summary>View raw response</summary>
        <pre>{JSON.stringify(result, null, 2)}</pre>
      </details>
    </section>
  );
}

export default function App() {
  const [resume, setResume] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState<File | null>(null);
  const [jobDescriptionText, setJobDescriptionText] = useState("");
  const [started, setStarted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<AnalysisResult | null>(null);

  async function analyzeDocuments() {
    if (!resume) {
      setError("Please select a resume file.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    const formData = new FormData();
    formData.append("resume", resume);

    if (jobDescription) {
      formData.append("job_description", jobDescription);
    } else if (jobDescriptionText.trim()) {
      formData.append("job_description_text", jobDescriptionText.trim());
    }

    try {
      const endpoint =
        jobDescription || jobDescriptionText.trim()
          ? `${API_BASE_URL}/api/v1/analyses/resume-jd`
          : `${API_BASE_URL}/api/v1/analyses/resume`;

      const response = await fetch(endpoint, {
        method: "POST",
        body: formData,
      });

      const responseText = await response.text();

      let data: { detail?: string; data?: AnalysisResult };

      try {
        data = JSON.parse(responseText);
      } catch {
        data = { detail: responseText };
      }

      if (!response.ok) {
        throw new Error(
          data.detail || `Analysis failed with HTTP ${response.status}`,
        );
      }

      setResult(data.data ?? null);
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Unable to connect to the backend.",
      );
    } finally {
      setLoading(false);
    }
  }

  if (started) {
    return (
      <main className="app-shell">
        <section className="panel">
          <p className="eyebrow">SKILLLENS</p>
          <h1>Ready to analyze</h1>

          <p className="muted">
            Your documents are selected. Start the backend analysis when ready.
          </p>

          <div className="file-summary">
            <strong>Resume</strong>
            <span>{resume?.name ?? "Not selected"}</span>
          </div>

          <div className="file-summary">
            <strong>Job description</strong>
            <span>
              {jobDescription
                ? `Selected file: ${jobDescription.name}`
                : jobDescriptionText.trim()
                  ? "Job description text entered"
                  : "No job description selected"}
            </span>
          </div>

          <button
            className="primary-button"
            disabled={loading || !resume}
            onClick={analyzeDocuments}
          >
            {loading ? "Analyzing..." : "Start analysis"}
          </button>

          {error && <p className="error-message">{error}</p>}

          {result && <AnalysisResults result={result} />}

          <button
            className="secondary-button"
            disabled={loading}
            onClick={() => {
              setStarted(false);
              setResult(null);
              setError("");
            }}
          >
            Back to uploads
          </button>
        </section>
      </main>
    );
  }

  return (
    <main className="app-shell">
      <section className="hero">
        <p className="eyebrow">SKILLLENS</p>

        <h1>
          Understand your fit.
          <br />
          Close your skill gaps.
        </h1>

        <p className="intro">
          Upload your resume and a job description to explore your strengths,
          missing skills, and next career steps.
        </p>

        <div className="upload-grid">
          <label className="upload-card">
            <span className="upload-number">01</span>
            <span className="upload-title">Resume</span>
            <span className="upload-help">PDF or DOCX</span>

            <input
              type="file"
              accept=".pdf,.docx"
              onChange={(event) => setResume(event.target.files?.[0] ?? null)}
            />

            <span className="file-name">
              {resume ? resume.name : "Choose resume"}
            </span>
          </label>

          <div className="upload-card">
            <span className="upload-number">02</span>
            <span className="upload-title">Job description</span>
            <span className="upload-help">PDF, DOCX, or pasted text</span>

            <input
              type="file"
              accept=".pdf,.docx"
              onChange={(event) =>
                setJobDescription(event.target.files?.[0] ?? null)
              }
            />

            <span className="file-name">
              {jobDescription ? jobDescription.name : "Choose job description"}
            </span>

            <div className="field">
              <label htmlFor="job-description-text">
                Or paste job description text
              </label>

              <textarea
                id="job-description-text"
                value={jobDescriptionText}
                onChange={(event) => setJobDescriptionText(event.target.value)}
                placeholder="Paste the job description here..."
                rows={10}
              />
            </div>
          </div>
        </div>

        <button
          type="button"
          disabled={!resume}
          onClick={() => setStarted(true)}
        >
          Continue to analysis
        </button>
      </section>
    </main>
  );
}