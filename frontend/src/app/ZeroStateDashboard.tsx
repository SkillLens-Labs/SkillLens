import React, { useEffect, useRef, useState, useCallback } from "react";
import "./zero-dashboard.css";

function CountUp({ to, decimals = 0, suffix = "", duration = 1400 }: { to: number; decimals?: number; suffix?: string; duration?: number }) {
  const [value, setValue] = useState(0);
  const ref = useRef<HTMLSpanElement>(null);
  const started = useRef(false);

  useEffect(() => {
    const node = ref.current;
    if (!node) return;
    const io = new IntersectionObserver(
      (entries) => {
        if (!entries[0].isIntersecting || started.current) return;
        started.current = true;
        const t0 = performance.now();
        const tick = (t: number) => {
          const p = Math.min(1, (t - t0) / duration);
          const eased = 1 - Math.pow(1 - p, 3);
          setValue(to * eased);
          if (p < 1) requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
      },
      { threshold: 0.4 },
    );
    io.observe(node);
    return () => io.disconnect();
  }, [to, duration]);

  return (
    <span ref={ref} style={{ fontVariantNumeric: "tabular-nums" }}>
      {value.toFixed(decimals)}
      {suffix}
    </span>
  );
}

function Tilt({ children, className = "", strong = false }: { children: React.ReactNode; className?: string; strong?: boolean }) {
  const ref = useRef<HTMLDivElement>(null);

  const onMove = useCallback(
    (e: React.MouseEvent) => {
      const el = ref.current;
      if (!el) return;
      const r = el.getBoundingClientRect();
      const x = (e.clientX - r.left) / r.width - 0.5;
      const y = (e.clientY - r.top) / r.height - 0.5;
      const k = strong ? 5 : 2.5;
      el.style.transform = `perspective(1100px) rotateX(${(-y * k).toFixed(2)}deg) rotateY(${(x * k).toFixed(2)}deg)`;
      el.style.setProperty("--mx", `${(x * 100 + 50).toFixed(1)}%`);
      el.style.setProperty("--my", `${(y * 100 + 50).toFixed(1)}%`);
    },
    [strong],
  );

  const onLeave = useCallback(() => {
    const el = ref.current;
    if (!el) return;
    el.style.transform = "perspective(1100px) rotateX(0deg) rotateY(0deg)";
  }, []);

  return (
    <div ref={ref} className={className} onMouseMove={onMove} onMouseLeave={onLeave}>
      {children}
    </div>
  );
}

function Ring({ score, size = 96, color = "#1d2740", track = "rgba(11,17,32,0.08)", label }: { score: number; size?: number; color?: string; track?: string; label?: string }) {
  const r = (size - 10) / 2;
  const c = 2 * Math.PI * r;
  const dash = (score / 100) * c;
  return (
    <div className="sl-ring" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="sl-ring__svg">
        <circle cx={size / 2} cy={size / 2} r={r} stroke={track} strokeWidth="7" fill="none" />
        <circle
          cx={size / 2} cy={size / 2} r={r}
          stroke={color} strokeWidth="7" fill="none" strokeLinecap="round"
          strokeDasharray={`${dash} ${c}`}
          className="sl-ring__fill"
          style={{ ["--dash" as string]: `${dash}`, ["--c" as string]: `${c}` }}
        />
      </svg>
      <div className="sl-ring__center">
        <strong style={{ fontSize: size > 80 ? "1.05rem" : "0.85rem" }}>
          <CountUp to={score} decimals={1} />
        </strong>
        {label && <span>{label}</span>}
      </div>
    </div>
  );
}

function ZeroStateDashboard({ onStartAnalysis }: { onStartAnalysis: () => void }) {
  return (
    <div className="slz-page">
      <div className="slz-aurora" aria-hidden="true">
        <span className="slz-blob slz-blob--1" />
        <span className="slz-blob slz-blob--2" />
        <span className="slz-blob slz-blob--3" />
      </div>

      <main className="slz-shell">

        <section className="slz-hero">
          <div className="slz-hero__copy">
            <div className="slz-hero__badge">
              <span className="slz-pulse" />
              Analysis dashboard
              <span className="slz-sep">·</span>
              <em>no analysis yet</em>
            </div>

            <h1 className="slz-hero__title">
              See what a hiring team
              <br />
              <span className="slz-hero__accent">sees in your resume.</span>
            </h1>

            <p className="slz-hero__sub">
              Six engines score quality, ATS readability, career direction,
              language and job fit. Every claim is grounded in evidence from
              your own documents, so you can verify it rather than trust it.
            </p>

            <div className="slz-hero__cta">
              <button className="slz-btn slz-btn--primary" onClick={onStartAnalysis}>
                Run your first analysis
                <svg viewBox="0 0 24 24" fill="none">
                  <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </button>
              <span className="slz-hero__hint">
                <svg viewBox="0 0 24 24" fill="none">
                  <rect x="5" y="10" width="14" height="10" rx="2" stroke="currentColor" strokeWidth="1.7" />
                  <path d="M8 10V8a4 4 0 018 0v2" stroke="currentColor" strokeWidth="1.7" />
                </svg>
                5–10 seconds · nothing stored, ever
              </span>
            </div>

            <div className="slz-hero__stats">
              <div className="slz-stat">
                <strong><CountUp to={6} /></strong>
                <span>analysis modules</span>
              </div>
              <div className="slz-stat__divider" />
              <div className="slz-stat">
                <strong><CountUp to={100} suffix="%" /></strong>
                <span>evidence-backed</span>
              </div>
              <div className="slz-stat__divider" />
              <div className="slz-stat">
                <strong><CountUp to={0} /></strong>
                <span>data retained</span>
              </div>
            </div>
          </div>

          <div className="slz-hero__demo">
            <div className="slz-demo__frame">
              <div className="slz-browser">
                <div className="slz-browser__chrome">
                  <span className="slz-dot" style={{ background: "#ff5f57" }} />
                  <span className="slz-dot" style={{ background: "#febc2e" }} />
                  <span className="slz-dot" style={{ background: "#28c840" }} />
                  <span className="slz-url">
                    <svg viewBox="0 0 24 24" fill="none">
                      <rect x="5" y="10" width="14" height="10" rx="2" stroke="currentColor" strokeWidth="1.6" />
                      <path d="M8 10V8a4 4 0 018 0v2" stroke="currentColor" strokeWidth="1.6" />
                    </svg>
                    skilllens.app
                  </span>
                  <span className="slz-progress"><i /><i /><i /><i /></span>
                </div>

                <div className="slz-stage">
                  <div className="slz-scene slz-scene--home">
                    <div className="slz-w slz-w--xl" />
                    <div className="slz-w slz-w--l" />
                    <div className="slz-w slz-w--s" />
                    <div className="slz-wrow">
                      <span className="slz-pill slz-pill--dark" />
                      <span className="slz-pill slz-pill--ghost" />
                    </div>
                  </div>

                  <div className="slz-scene slz-scene--upload">
                    <div className="slz-upcard">
                      <div className="slz-uphead">
                        <span className="slz-uphead__t">Add documents</span>
                        <span className="slz-uphead__s">2 of 2 attached</span>
                      </div>
                      <div className="slz-drop">
                        <span className="slz-filerow slz-filerow--resume">
                          <i />
                          <span className="slz-filerow__txt" />
                          <b className="slz-filerow__ok">
                            <svg viewBox="0 0 24 24" fill="none">
                              <path d="M5 12.5l4.5 4.5L19 7.5" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                          </b>
                        </span>
                        <span className="slz-filerow slz-filerow--jd">
                          <i />
                          <span className="slz-filerow__txt" />
                          <b className="slz-filerow__ok">
                            <svg viewBox="0 0 24 24" fill="none">
                              <path d="M5 12.5l4.5 4.5L19 7.5" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                          </b>
                        </span>
                      </div>
                      <span className="slz-pill slz-pill--blue">Run SkillLens analysis</span>
                    </div>
                  </div>

                  <div className="slz-scene slz-scene--analyzing">
                    <div className="slz-scan">
                      <span className="slz-spin" />
                      <span className="slz-core" />
                    </div>
                    <div className="slz-pipeline">
                      <span>Parsing</span><span>Matching</span><span>Scoring</span><span>Explaining</span>
                    </div>
                  </div>

                  <div className="slz-scene slz-scene--dash">
                    <div className="slz-dashhead">
                      <span className="slz-dashtick">
                        <svg viewBox="0 0 24 24" fill="none">
                          <path d="M5 12.5l4.5 4.5L19 7.5" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                      </span>
                      <div>
                        <span className="slz-dashk">Assessment</span>
                        <strong>Strong fit</strong>
                      </div>
                      <span className="slz-dashscore">
                        <CountUp to={82.4} decimals={1} />
                        <small>/ 100</small>
                      </span>
                    </div>
                    <div className="slz-dashbars">
                      <div className="slz-dashbar"><span>Quality</span><i /><em>78.9</em></div>
                      <div className="slz-dashbar"><span>ATS</span><i /><em>92.7</em></div>
                      <div className="slz-dashbar"><span>JD fit</span><i /><em>94.0</em></div>
                    </div>
                  </div>

                  <div className="slz-cap slz-cap--1">Open SkillLens</div>
                  <div className="slz-cap slz-cap--2">Drop resume + job description</div>
                  <div className="slz-cap slz-cap--3">Analyzing documents</div>
                  <div className="slz-cap slz-cap--4">Evidence-backed report, ready</div>

                  <span className="slz-cursor">
                    <svg viewBox="0 0 24 24" fill="none">
                      <path d="M4.8 2.1 18.6 12.9l-6.2.5 3.2 6.9-2.9 1.3-3.2-6.9-4.3 4.5z" fill="#0a0f1e" stroke="#ffffff" strokeWidth="1.7" strokeLinejoin="round" />
                    </svg>
                  </span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="slz-report">
          <div className="slz-report__intro">
            <span className="slz-kicker">What lands in the dashboard</span>
            <h2>A report you can verify,<br />not a black box.</h2>
            <p>
              Every number links back to a line in your resume or the job
              description. Hover any card to feel the detail level.
            </p>
          </div>

          <div className="slz-report__grid">
            <Tilt className="slz-tile slz-tile--score" strong>
              <span className="slz-tile__k">Overall job fit</span>
              <Ring score={82.4} color="#1a7f4f" label="Strong fit" />
              <div className="slz-tile__segment">
                <span className="slz-seg" style={{ ["--seg" as string]: "62%", background: "#1a7f4f" }} />
                <span className="slz-seg" style={{ ["--seg" as string]: "24%", background: "#c98a1c" }} />
                <span className="slz-seg" style={{ ["--seg" as string]: "14%", background: "#c1301f" }} />
              </div>
              <div className="slz-tile__legend">
                <span><i style={{ background: "#1a7f4f" }} />matched</span>
                <span><i style={{ background: "#c98a1c" }} />partial</span>
                <span><i style={{ background: "#c1301f" }} />missing</span>
              </div>
            </Tilt>

            <Tilt className="slz-tile slz-tile--findings">
              <span className="slz-tile__k">Priority findings</span>
              <div className="slz-finding">
                <span className="slz-sev slz-sev--red">High</span>
                <div>
                  <strong>No quantified results in last role</strong>
                  <p>Two recent bullets describe impact without numbers. The JD emphasizes metrics, so this caps your score.</p>
                </div>
              </div>
              <div className="slz-finding">
                <span className="slz-sev slz-sev--amber">Medium</span>
                <div>
                  <strong>Kubernetes skill reads as adjacent</strong>
                  <p>Resume mentions deployments but never Kubernetes; the phrasing is 62% similar to the JD requirement.</p>
                </div>
              </div>
              <div className="slz-finding">
                <span className="slz-sev slz-sev--green">Low</span>
                <div>
                  <strong>Sections ordered correctly for ATS</strong>
                  <p>Header, experience and skills parse cleanly with no table-based columns.</p>
                </div>
              </div>
            </Tilt>

            <Tilt className="slz-tile slz-tile--evidence">
              <span className="slz-tile__k">Traceable evidence — example</span>
              <p className="slz-quote">
                “Led a 400-node DynamoDB migration across 12 regional clusters
                with zero-downtime replay, reducing p99 read latency by 38%.”
              </p>
              <div className="slz-slz-evidence">
                <span className="slz-src">Resume · Experience · L34</span>
                <span className="slz-similarity">↔ JD requirement 07 · 94% match</span>
              </div>
              <p className="slz-verdict">
                This line satisfies both the “DynamoDB at scale” requirement and
                partial “operational leadership” requirement.
              </p>
            </Tilt>

            <Tilt className="slz-tile slz-tile--actions">
              <span className="slz-tile__k">Action plan, ranked</span>
              <div className="slz-action">
                <span className="slz-action__rank">1</span>
                <div>
                  <strong>Quantify two achievements</strong>
                  <p>Impact · High &nbsp; Effort · Low</p>
                </div>
                <span className="slz-action__gain">+8.4</span>
              </div>
              <div className="slz-action">
                <span className="slz-action__rank">2</span>
                <div>
                  <strong>Frame deployments as Kubernetes work</strong>
                  <p>Impact · Medium &nbsp; Effort · Low</p>
                </div>
                <span className="slz-action__gain">+3.1</span>
              </div>
              <div className="slz-action">
                <span className="slz-action__rank">3</span>
                <div>
                  <strong>Add a CI/CD exposure bullet</strong>
                  <p>Impact · Medium &nbsp; Effort · Medium</p>
                </div>
                <span className="slz-action__gain">+2.2</span>
              </div>
            </Tilt>
          </div>
        </section>

        <section className="slz-steps">
          <div className="slz-step">
            <span className="slz-step__num">1</span>
            <div><h4>Upload your resume</h4><p>PDF or DOCX, up to 10 MB.</p></div>
          </div>
          <span className="slz-arrow" />
          <div className="slz-step">
            <span className="slz-step__num">2</span>
            <div><h4>Optionally add the JD</h4><p>Unlocks fit scoring and gaps.</p></div>
          </div>
          <span className="slz-arrow" />
          <div className="slz-step">
            <span className="slz-step__num">3</span>
            <div><h4>Verify the report</h4><p>Evidence for every score.</p></div>
          </div>
        </section>

        <section className="slz-close">
          <h2>Your first report is one file away.</h2>
          <button className="slz-btn slz-btn--primary slz-btn--lg" onClick={onStartAnalysis}>
            Run your first analysis
            <svg viewBox="0 0 24 24" fill="none">
              <path d="M5 12h14M13 6l6 6-6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </section>
      </main>
    </div>
  );
}

export default ZeroStateDashboard;
