import { useRef, useState } from "react";
import type { AnalysisResult, Recommendation } from "../types/analysis";
import {
  Header,
  Section,
  ScoreCard,
  EvidenceList,
  scoreLabel,
  pretty,
  ResumeOverview,
  QualitySection,
  ATSSection,
  LanguageSection,
  CareerSection,
  JobOverview,
  MatchingSection,
  type Page,
} from "./App";
import "./styles.css";

const API_BASE = "http://127.0.0.1:8000/api/v1";

type Mode = "resume_only" | "resume_jd";
type DashTab = "overview" | "match" | "recommendations" | "prompt";

interface SubmitState {
  running: boolean;
  error: string | null;
}

/* ---------------- Landing ---------------- */

function Landing({ onGetStarted }: { onGetStarted: () => void }) {
  return (
    <main className="landing">
      <section className="hero">
        <span className="eyebrow">AI-powered resume & career intelligence</span>
        <h1>Understand exactly how your resume measures up</h1>
        <p>
          SkillLens reads your resume and a job description, matches your
          skills, explains every score, and tells you which certifications
          and courses close your gaps.
        </p>
        <button type="button" className="primary-button" onClick={onGetStarted}>
          Analyze my resume
        </button>
      </section>
    </main>
  );
}

/* ---------------- Input ---------------- */

function InputPage({
  mode,
  setMode,
  submit,
  state,
}: {
  mode: Mode;
  setMode: (mode: Mode) => void;
  submit: () => void;
  state: SubmitState;
}) {
  const resumeFileRef = useRef<HTMLInputElement>(null);
  const jdFileRef = useRef<HTMLInputElement>(null);
  const [resumeText, setResumeText] = useState("");
  const [jdText, setJdText] = useState("");

  return (
    <main className="input-page">
      <Section title="New analysis" eyebrow="Input">
        <div className="mode-toggle">
          <button
            type="button"
            className={mode === "resume_only" ? "chip chip-match" : "chip"}
            onClick={() => setMode("resume_only")}
          >
            Resume only
          </button>
          <button
            type="button"
            className={mode === "resume_jd" ? "chip chip-match" : "chip"}
            onClick={() => setMode("resume_jd")}
          >
            Resume + Job description
          </button>
        </div>

        <div className="subsection">
          <h3>Resume</h3>
          <input ref={resumeFileRef} type="file" accept=".pdf,.docx,.txt,.md" />
          <textarea
            placeholder="...or paste your resume text"
            value={resumeText}
            onChange={(event) => setResumeText(event.target.value)}
            rows={6}
          />
        </div>

        {mode === "resume_jd" && (
          <div className="subsection">
            <h3>Job description</h3>
            <input ref={jdFileRef} type="file" accept=".pdf,.docx,.txt,.md" />
            <textarea
              placeholder="...or paste the job description"
              value={jdText}
              onChange={(event) => setJdText(event.target.value)}
              rows={6}
            />
          </div>
        )}

        {state.error && <div className="warning-box">{state.error}</div>}

        <button
          type="button"
          className="primary-button"
          onClick={submit}
          disabled={state.running}
        >
          {state.running ? "Analyzing..." : "Run analysis"}
        </button>
      </Section>
    </main>
  );
}

/* ---------------- Dashboard pieces ---------------- */

function VerdictBanner({ result }: { result: AnalysisResult }) {
  const jd = result.analysis_mode === "resume_jd";
  const analysis = result.skill_analysis;

  const actions = result.recommendations.slice(0, 3);
  const headline = jd
    ? `${analysis.matched_skills.length} skills matched, ${analysis.missing_skills.length} missing`
    : `Quality ${scoreLabel(result.resume_quality?.overall_score)} · ATS ${scoreLabel(result.ats_intelligence?.overall_score)}`;

  return (
    <div className="verdict-banner">
      <div>
        <span className="label">
          {jd ? "Overall match score" : "Overall readiness"}
        </span>
        <div className="verdict-score">
          {scoreLabel(jd ? result.scoring?.overall_score : result.resume_quality?.overall_score)}
        </div>
        <div>{headline}</div>
      </div>
      {actions.length > 0 && (
        <div>
          <span className="label">Top actions</span>
          <ul className="verdict-actions">
            {actions.map((rec) => (
              <li key={rec.recommendation_id}>{rec.title}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function SkillMatchTable({ result }: { result: AnalysisResult }) {
  const matches = result.matching?.skill_matches ?? [];
  if (!matches.length) return <p className="muted">No skill matches recorded.</p>;

  return (
    <table className="match-table">
      <thead>
        <tr>
          <th>Your skill</th>
          <th>Job skill</th>
          <th>Relationship</th>
          <th>Similarity</th>
        </tr>
      </thead>
      <tbody>
        {matches.map((match, index) => (
          <tr key={`${match.resume_skill_id}-${match.job_skill_id}-${index}`}>
            <td><strong>{match.resume_skill_name ?? match.resume_skill_id}</strong></td>
            <td>{match.job_skill_name ?? match.job_skill_id}</td>
            <td>{pretty(match.relationship)}</td>
            <td>
              <div
                className="similarity-bar"
                style={{ ["--sim" as string]: `${Math.round(match.similarity * 100)}%` }}
              >
                <span />
              </div>
              <span>{Math.round(match.similarity * 100)}%</span>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function GapSummary({ result }: { result: AnalysisResult }) {
  const analysis = result.skill_analysis;
  return (
    <div className="subsection">
      <h3>Skill outcome</h3>
      <div className="chip-row">
        {analysis.matched_skills.map((skill) => (
          <span className="chip chip-match" key={`m-${skill}`}>✓ {skill}</span>
        ))}
        {analysis.partial_matches.map((skill) => (
          <span className="chip chip-partial" key={`p-${skill}`}>~ {skill}</span>
        ))}
        {analysis.missing_skills.map((skill) => (
          <span className="chip chip-missing" key={`x-${skill}`}>✗ {skill}</span>
        ))}
      </div>
    </div>
  );
}

const TYPE_LABEL: Record<Recommendation["type"], string> = {
  learning: "Learning",
  project: "Project",
  certification: "Certification",
  resume: "Resume",
  career: "Career",
  job_alignment: "Alignment",
};

function RecommendationsSection({ result }: { result: AnalysisResult }) {
  const recs = result.recommendations;
  if (!recs.length) return <p className="muted">No recommendations generated.</p>;

  return (
    <Section title="Recommendations" eyebrow="What to do next">
      <div className="finding-list">
        {recs.map((rec) => (
          <article className="finding-card rec-card" key={rec.recommendation_id}>
            <div className="finding-header">
              <strong>{rec.title}</strong>
              <div className="finding-badges">
                <span className="type-pill">{TYPE_LABEL[rec.type]}</span>
                <span className={`severity severity-${rec.priority}`}>
                  {pretty(rec.priority)}
                </span>
              </div>
            </div>
            <p>{rec.rationale}</p>
            <div className="recommendation-meta">
              {rec.effort && <span>Effort: {pretty(rec.effort)}</span>}
              {rec.expected_impact && <span>Impact: {pretty(rec.expected_impact)}</span>}
              {rec.target_skill && <span>Skill: {rec.target_skill}</span>}
            </div>
            {rec.resources?.map((resource) => (
              <a
                className="resource-link"
                href={resource.url}
                target="_blank"
                rel="noreferrer"
                key={`${rec.recommendation_id}-${resource.title}`}
              >
                {resource.kind === "certification" ? "🎓" : "📘"}{" "}
                {resource.title} · {resource.provider} ({resource.level})
              </a>
            ))}
            {rec.evidence.length > 0 && <EvidenceList evidence={rec.evidence} />}
          </article>
        ))}
      </div>
    </Section>
  );
}

function PromptPanel({ result }: { result: AnalysisResult }) {
  const [copied, setCopied] = useState(false);
  const prompt = result.resume_improvement_prompt;

  if (!prompt) {
    return (
      <Section title="Improvement prompt" eyebrow="AI-ready briefing">
        <p className="muted">
          No improvement prompt was generated for this analysis.
        </p>
      </Section>
    );
  }

  return (
    <Section title="Improvement prompt" eyebrow="AI-ready briefing">
      <p>
        Copy this into any AI assistant to get a prioritized rewrite plan
        based on this exact analysis.
      </p>
      <div className="prompt-panel">
        <button
          type="button"
          className="secondary-button copy-button"
          onClick={() => {
            navigator.clipboard?.writeText(prompt).then(
              () => {
                setCopied(true);
                setTimeout(() => setCopied(false), 2000);
              },
              () => undefined,
            );
          }}
        >
          {copied ? "Copied" : "Copy"}
        </button>
        <pre>{prompt}</pre>
      </div>
    </Section>
  );
}

/* ---------------- Dashboard ---------------- */

function Dashboard({ result }: { result: AnalysisResult }) {
  const jd = result.analysis_mode === "resume_jd";
  const [tab, setTab] = useState<DashTab>("overview");
  const tabs: { id: DashTab; label: string }[] = [
    { id: "overview", label: "Resume analysis" },
    ...(jd ? ([{ id: "match", label: "Job & match" }] as const) : []),
    { id: "recommendations", label: `Recommendations (${result.recommendations.length})` },
    { id: "prompt", label: "Improvement prompt" },
  ];

  return (
    <main className="dashboard">
      <VerdictBanner result={result} />

      <nav className="tabs" aria-label="Result sections">
        {tabs.map((item) => (
          <button
            key={item.id}
            type="button"
            className={`tab ${tab === item.id ? "is-active" : ""}`}
            onClick={() => setTab(item.id)}
          >
            {item.label}
          </button>
        ))}
      </nav>

      {tab === "overview" && (
        <>
          <ResumeOverview result={result} />
          <QualitySection quality={result.resume_quality} />
          <ATSSection ats={result.ats_intelligence} />
          <LanguageSection language={result.language_quality} />
          <CareerSection career={result.career_intelligence} />
        </>
      )}

      {tab === "match" && jd && (
        <>
          <Section title="Match verdict" eyebrow="Skills">
            <div className="score-grid">
              <ScoreCard label="Overall" score={result.scoring?.overall_score} />
              <ScoreCard label="Skill score" score={result.scoring?.skill_score} />
              <ScoreCard
                label="Required skills"
                score={result.scoring?.required_skill_score}
              />
            </div>
            <GapSummary result={result} />
          </Section>
          <Section title="Skill matches" eyebrow="Side by side">
            <SkillMatchTable result={result} />
          </Section>
          <JobOverview job={result.job_profile} />
          <MatchingSection matching={result.matching} job={result.job_profile} />
        </>
      )}

      {tab === "recommendations" && <RecommendationsSection result={result} />}
      {tab === "prompt" && <PromptPanel result={result} />}
    </main>
  );
}

/* ---------------- App assembly ---------------- */

export default function SkillLensApp() {
  const [page, setPage] = useState<Page>("landing");
  const [mode, setMode] = useState<Mode>("resume_jd");
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [submit, setSubmit] = useState<SubmitState>({ running: false, error: null });
  const [submitted, setSubmitted] = useState(false);
  const inputRef = useRef<{
    resumeFile: File | null;
    resumeText: string;
    jdFile: File | null;
    jdText: string;
  } | null>(null);

  const analysisExists = result !== null || submitted;

  const runAnalysis = async () => {
    setSubmit({ running: true, error: null });
    setPage("analyzing");
    try {
      const payload = inputRef.current;
      if (!payload) throw new Error("No resume provided.");

      const form = new FormData();
      if (payload.resumeFile) form.append("resume", payload.resumeFile);
      else if (payload.resumeText.trim()) form.append("resume_text", payload.resumeText);
      else throw new Error("Provide a resume file or paste resume text.");

      if (mode === "resume_jd") {
        if (payload.jdFile) form.append("job_description", payload.jdFile);
        else if (payload.jdText.trim()) form.append("job_description_text", payload.jdText);
        else throw new Error("Provide a job description file or paste its text.");
      }

      const endpoint = mode === "resume_jd" ? "/analyses/resume-jd" : "/analyses/resume";
      const response = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        body: form,
      });

      if (!response.ok) {
        let message = `Analysis failed (${response.status}).`;
        try {
          const body = await response.json();
          if (body?.message) message = body.message;
          else if (body?.detail?.message) message = body.detail.message;
        } catch {
          /* keep default message */
        }
        throw new Error(message);
      }

      const body = await response.json();
      setResult(body.data as AnalysisResult);
      setSubmit({ running: false, error: null });
      setPage("dashboard");
    } catch (error) {
      setSubmit({ running: false, error: error instanceof Error ? error.message : "Unexpected error." });
      setPage("input");
    }
  };

  const handleInputSubmit = () => {
    // Gather the uncontrolled inputs from the DOM on submit.
    const inputs = document.querySelectorAll<HTMLInputElement>("input[type=file]");
    const areas = document.querySelectorAll<HTMLTextAreaElement>("textarea");
    const resumeFile = inputs[0]?.files?.[0] ?? null;
    const jdFile = mode === "resume_jd" ? (inputs[1]?.files?.[0] ?? null) : null;
    const resumeText = areas[0]?.value ?? "";
    const jdText = mode === "resume_jd" ? (areas[1]?.value ?? "") : "";
    inputRef.current = { resumeFile, resumeText, jdFile, jdText };
    setSubmitted(true);
    void runAnalysis();
  };

  return (
    <div className="app-shell">
      <Header page={page} onNavigate={(next) => setPage(next)} />
      {analysisExists && page !== "input" && (
        <div style={{ display: "flex", justifyContent: "flex-end", padding: "0 24px" }}>
          <button
            type="button"
            className="secondary-button"
            onClick={() => {
              setResult(null);
              setSubmitted(false);
              setPage("input");
            }}
          >
            New analysis
          </button>
        </div>
      )}

      {page === "landing" && <Landing onGetStarted={() => setPage("input")} />}
      {page === "input" && (
        <InputPage mode={mode} setMode={setMode} submit={handleInputSubmit} state={submit} />
      )}
      {page === "analyzing" && (
        <main className="analyzing">
          <p className="muted">Running the analysis pipeline...</p>
        </main>
      )}
      {page === "dashboard" && result && <Dashboard result={result} />}
    </div>
  );
}
