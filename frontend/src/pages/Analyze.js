import React, { useState, useEffect } from "react";
import { useSearchParams } from "react-router-dom";
import { resumeAPI, analyzeAPI } from "../services/api";

function ScoreBadge({ score }) {
  const cls = score >= 70 ? "score-high" : score >= 45 ? "score-mid" : "score-low";
  const label = score >= 70 ? "Strong" : score >= 45 ? "Moderate" : "Weak";
  return (
    <div style={{ textAlign: "center" }}>
      <div className={`score-circle ${cls}`}>
        <span>{score}</span>
        <span style={{ fontSize: 12, fontWeight: 400 }}>/100</span>
      </div>
      <div style={{ marginTop: 8, fontSize: 13, fontWeight: 500, color: score >= 70 ? "#059669" : score >= 45 ? "#d97706" : "#dc2626" }}>
        {label} Match
      </div>
    </div>
  );
}

function GapCard({ gap, index }) {
  const severityColor = { high: "#dc2626", medium: "#d97706", low: "#059669" };
  const sevBg = { high: "#fef2f2", medium: "#fffbeb", low: "#ecfdf5" };
  return (
    <div style={{ padding: 14, background: sevBg[gap.severity] || "#f9fafb", borderRadius: 8, marginBottom: 8, borderLeft: `3px solid ${severityColor[gap.severity] || "#6b7280"}` }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 4 }}>
        <div style={{ fontWeight: 500, fontSize: 14, color: "#111827", flex: 1, paddingRight: 8 }}>{gap.issue}</div>
        <span className={`badge badge-${gap.severity === "high" ? "red" : gap.severity === "medium" ? "yellow" : "green"}`} style={{ flexShrink: 0 }}>
          {gap.severity}
        </span>
      </div>
      <div style={{ fontSize: 13, color: "#4b5563" }}>💡 {gap.fix}</div>
    </div>
  );
}

export default function Analyze() {
  const [searchParams] = useSearchParams();
  const [resumes, setResumes] = useState([]);
  const [selectedResume, setSelectedResume] = useState(searchParams.get("resume_id") || "");
  const [jdText, setJdText] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("ats");

  useEffect(() => {
    resumeAPI.list().then((r) => {
      setResumes(r.data);
      if (!selectedResume && r.data.length > 0) setSelectedResume(String(r.data[0].id));
    });
  }, []);

  const runAnalysis = async () => {
    if (!selectedResume) { setError("Please select a resume first."); return; }
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await analyzeAPI.full({
        resume_id: parseInt(selectedResume),
        jd_text: jdText || null,
      });
      setResult(res.data);
      setActiveTab(jdText ? "ats" : "gaps");
    } catch (e) {
      setError(e.response?.data?.detail || "Analysis failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: "ats", label: "ATS Score", show: !!result?.ats?.score },
    { id: "gaps", label: "Gap Analysis" },
    { id: "roles", label: `Role Matches (${result?.matched_roles?.length || 0})` },
  ].filter(t => !t.show === false || t.id !== "ats" || result?.ats?.score);

  return (
    <div>
      <h1 className="page-title">AI Analysis</h1>
      <p className="page-subtitle">Get your ATS score, gap analysis, and matched roles in one click</p>

      <div className="card" style={{ marginBottom: 20 }}>
        <div className="grid-2" style={{ gap: 20 }}>
          <div>
            <label className="label">Select Resume</label>
            <select
              className="input"
              value={selectedResume}
              onChange={(e) => setSelectedResume(e.target.value)}
            >
              <option value="">Choose a resume...</option>
              {resumes.map((r) => (
                <option key={r.id} value={r.id}>{r.filename}</option>
              ))}
            </select>
            {resumes.length === 0 && (
              <p style={{ fontSize: 12, color: "#9ca3af", marginTop: 4 }}>
                No resumes found. Upload one from Dashboard first.
              </p>
            )}
          </div>
          <div>
            <label className="label">
              Job Description <span style={{ color: "#9ca3af", fontWeight: 400 }}>(optional — for ATS scoring)</span>
            </label>
            <textarea
              className="textarea"
              placeholder="Paste the job description here to get an ATS score against this specific role..."
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
              style={{ minHeight: 80 }}
            />
          </div>
        </div>

        {error && (
          <div style={{ margin: "12px 0", padding: 12, background: "#fef2f2", borderRadius: 8, color: "#dc2626", fontSize: 13 }}>
            {error}
          </div>
        )}

        <button
          className="btn btn-primary"
          onClick={runAnalysis}
          disabled={loading || !selectedResume}
          style={{ marginTop: 16, minWidth: 180, justifyContent: "center" }}
        >
          {loading ? (
            <><span className="spinner" /> Analyzing with AI...</>
          ) : (
            "◎ Run Full Analysis"
          )}
        </button>
        {loading && (
          <p style={{ fontSize: 12, color: "#6b7280", marginTop: 8 }}>
            This takes 15–30 seconds. AI is analyzing your resume...
          </p>
        )}
      </div>

      {result && (
        <div>
          <div style={{ display: "flex", gap: 4, marginBottom: 16, background: "white", padding: "6px", borderRadius: 10, boxShadow: "var(--shadow)", width: "fit-content" }}>
            {[
              { id: "ats", label: "ATS Score" },
              { id: "gaps", label: "Gap Analysis" },
              { id: "roles", label: `Role Matches (${result.matched_roles?.length || 0})` },
            ].map(tab => (
              <button key={tab.id} onClick={() => setActiveTab(tab.id)}
                style={{
                  padding: "8px 18px", borderRadius: 7, border: "none", cursor: "pointer",
                  fontSize: 13, fontWeight: 500,
                  background: activeTab === tab.id ? "#4f46e5" : "transparent",
                  color: activeTab === tab.id ? "white" : "#6b7280",
                  transition: "all 0.15s",
                }}>
                {tab.label}
              </button>
            ))}
          </div>

          {activeTab === "ats" && (
            <div className="card">
              {result.ats?.score ? (
                <div>
                  <div className="grid-2" style={{ alignItems: "start" }}>
                    <div>
                      <ScoreBadge score={result.ats.score} />
                      <p style={{ textAlign: "center", marginTop: 12, fontSize: 14, color: "#4b5563", padding: "0 20px" }}>
                        {result.ats.feedback}
                      </p>
                    </div>
                    <div>
                      {result.ats.matched_keywords?.length > 0 && (
                        <div style={{ marginBottom: 16 }}>
                          <div style={{ fontSize: 13, fontWeight: 500, color: "#059669", marginBottom: 6 }}>✓ Matched Keywords</div>
                          {result.ats.matched_keywords.map(k => <span key={k} className="pill">{k}</span>)}
                        </div>
                      )}
                      {result.ats.missing_keywords?.length > 0 && (
                        <div>
                          <div style={{ fontSize: 13, fontWeight: 500, color: "#dc2626", marginBottom: 6 }}>✗ Missing Keywords</div>
                          {result.ats.missing_keywords.map(k => <span key={k} className="pill" style={{ background: "#fef2f2", color: "#dc2626" }}>{k}</span>)}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ) : (
                <div style={{ textAlign: "center", padding: "2rem", color: "#6b7280" }}>
                  <div style={{ fontSize: 32, marginBottom: 8 }}>📋</div>
                  <p>No JD provided for ATS scoring.</p>
                  <p style={{ fontSize: 13, marginTop: 4 }}>Paste a job description above and re-run to get your ATS score.</p>
                </div>
              )}
            </div>
          )}

          {activeTab === "gaps" && (
            <div className="card">
              {result.gaps?.priority_fixes?.length > 0 && (
                <div style={{ marginBottom: 24, padding: 16, background: "#eef2ff", borderRadius: 10 }}>
                  <div style={{ fontWeight: 600, color: "#3730a3", marginBottom: 10 }}>🎯 Priority Fixes (Do These First)</div>
                  {result.gaps.priority_fixes.map((fix, i) => (
                    <div key={i} style={{ fontSize: 13, color: "#4338ca", marginBottom: 6, display: "flex", gap: 8, alignItems: "flex-start" }}>
                      <span style={{ fontWeight: 600, flexShrink: 0 }}>{i + 1}.</span>
                      <span>{fix}</span>
                    </div>
                  ))}
                </div>
              )}

              <div className="grid-3" style={{ alignItems: "start" }}>
                {[
                  { title: "Resume Gaps", key: "resume_gaps", icon: "📄" },
                  { title: "Profile Gaps", key: "profile_gaps", icon: "👤" },
                  { title: "Market Gaps", key: "market_gaps", icon: "📊" },
                ].map(({ title, key, icon }) => (
                  <div key={key}>
                    <div style={{ fontWeight: 600, fontSize: 14, marginBottom: 10, color: "#111827" }}>{icon} {title}</div>
                    {(result.gaps[key] || []).length === 0 ? (
                      <p style={{ fontSize: 13, color: "#9ca3af" }}>No gaps found</p>
                    ) : (
                      (result.gaps[key] || []).map((gap, i) => <GapCard key={i} gap={gap} index={i} />)
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === "roles" && (
            <div className="card">
              {result.matched_roles?.length === 0 ? (
                <div style={{ textAlign: "center", padding: "2rem", color: "#6b7280" }}>
                  <p>No jobs in database. Go to Dashboard and seed jobs first.</p>
                </div>
              ) : (
                <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                  <p style={{ fontSize: 13, color: "#6b7280", marginBottom: 4 }}>
                    Matched against <strong>{result.total_jobs_in_db}</strong> real fresher jobs in our database
                  </p>
                  {result.matched_roles.map((role, i) => (
                    <div key={i} style={{ padding: 16, background: "#f9fafb", borderRadius: 10, border: "1px solid #e5e7eb" }}>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                        <div>
                          <div style={{ fontWeight: 600, fontSize: 15 }}>{role.title}</div>
                          <div style={{ color: "#6b7280", fontSize: 13 }}>{role.company} · {role.location}</div>
                          {role.salary_range && <div style={{ fontSize: 12, color: "#4f46e5", marginTop: 2 }}>💰 {role.salary_range}</div>}
                        </div>
                        <div style={{ textAlign: "center", minWidth: 70 }}>
                          <div style={{
                            fontSize: 22, fontWeight: 700,
                            color: role.match_percentage >= 60 ? "#059669" : role.match_percentage >= 40 ? "#d97706" : "#dc2626"
                          }}>
                            {Math.min(100, role.match_percentage)}%
                          </div>
                          <div style={{ fontSize: 11, color: "#9ca3af" }}>match</div>
                        </div>
                      </div>
                      <div style={{ marginTop: 10, display: "flex", flexWrap: "wrap", gap: 4 }}>
                        {role.skills_matched?.map(s => <span key={s} className="pill" style={{ fontSize: 11 }}>{s}</span>)}
                        {role.skills_missing?.slice(0, 3).map(s => <span key={s} className="pill pill-gray" style={{ fontSize: 11 }}>+{s}</span>)}
                      </div>
                      {role.source_url && (
                        <a href={role.source_url} target="_blank" rel="noreferrer"
                          style={{ display: "inline-block", marginTop: 8, fontSize: 12, color: "#4f46e5" }}>
                          View job →
                        </a>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
