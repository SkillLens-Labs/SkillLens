import { useState } from "react";

import "./styles.css";

type AnalysisResult = {
  analysis_id: string;
  analysis_mode: string;
  status: string;
  matching?: {
    summary?: string;
  };
  scoring?: {
    overall_score?: number;
  };
};

export default function App() {
  const [resume, setResume] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState<File | null>(null);
  const [started, setStarted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<AnalysisResult | null>(null);

  async function analyzeDocuments() {
    if (!resume || !jobDescription) return;

    setLoading(true);
    setError("");
    setResult(null);

    const formData = new FormData();
    formData.append("resume", resume);
    formData.append("job_description", jobDescription);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/v1/analyses/resume-jd",
        {
          method: "POST",
          body: formData,
        },
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || `Analysis failed with HTTP ${response.status}`,
        );
      }

      setResult(data.data);
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
            <span>{jobDescription?.name ?? "Not selected"}</span>
          </div>

          <button
            className="primary-button"
            disabled={loading || !resume || !jobDescription}
            onClick={analyzeDocuments}
          >
            {loading ? "Analyzing..." : "Start analysis"}
          </button>

          {error && <p className="error-message">{error}</p>}

          {result && (
            <section className="result-card">
              <h2>Analysis completed</h2>

              <p>
                Status: <strong>{result.status ?? "completed"}</strong>
              </p>

              {result.scoring?.overall_score !== undefined && (
                <p>
                  Overall score:{" "}
                  <strong>{result.scoring.overall_score}</strong>
                </p>
              )}

              {result.matching?.summary && (
                <p>{result.matching.summary}</p>
              )}

              <details>
                <summary>View raw response</summary>
                <pre>{JSON.stringify(result, null, 2)}</pre>
              </details>
            </section>
          )}

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
              onChange={(event) =>
                setResume(event.target.files?.[0] ?? null)
              }
            />

            <span className="file-name">
              {resume ? resume.name : "Choose resume"}
            </span>
          </label>

          <label className="upload-card">
            <span className="upload-number">02</span>
            <span className="upload-title">Job description</span>
            <span className="upload-help">PDF or DOCX</span>

            <input
              type="file"
              accept=".pdf,.docx"
              onChange={(event) =>
                setJobDescription(event.target.files?.[0] ?? null)
              }
            />

            <span className="file-name">
              {jobDescription
                ? jobDescription.name
                : "Choose job description"}
            </span>
          </label>
        </div>

        <button
          className="primary-button"
          disabled={!resume || !jobDescription}
          onClick={() => setStarted(true)}
        >
          Continue to analysis
        </button>
      </section>
    </main>
  );
}