import React, { useState, useEffect } from "react";
import { resumeAPI } from "../services/api";
import api from "../services/api";

const copilotAPI = {
  fetchJD: (url) => api.post("/api/copilot/fetch-jd", { url }),
  tailorResume: (data) => api.post("/api/copilot/tailor-resume", data),
  coverLetter: (data) => api.post("/api/copilot/cover-letter", data),
  scoreAnswer: (data) => api.post("/api/copilot/score-answer", data),
  roadmap: (data) => api.post("/api/copilot/roadmap", data),
};

const TABS = [
  { id: "tailor", label: "✂️ Tailor Resume" },
  { id: "cover", label: "📝 Cover Letter" },
  { id: "mock", label: "🎯 Mock Interview" },
  { id: "roadmap", label: "🗺️ Skill Roadmap" },
];

function TabBtn({ id, label, active, onClick }) {
  return (
    <button onClick={() => onClick(id)} style={{
      padding: "10px 18px", borderRadius: 8, border: "none", cursor: "pointer",
      fontSize: 13, fontWeight: 500, transition: "all 0.15s",
      background: active ? "#4f46e5" : "white",
      color: active ? "white" : "#6b7280",
      boxShadow: active ? "0 2px 8px rgba(79,70,229,0.3)" : "none",
    }}>{label}</button>
  );
}

function CopyBtn({ text }) {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  return (
    <button onClick={copy} style={{
      padding: "6px 14px", borderRadius: 6, border: "1px solid #d1d5db",
      background: copied ? "#ecfdf5" : "white", color: copied ? "#059669" : "#374151",
      fontSize: 12, cursor: "pointer", fontWeight: 500,
    }}>
      {copied ? "✓ Copied" : "Copy"}
    </button>
  );
}

export default function Copilot() {
  const [activeTab, setActiveTab] = useState("tailor");
  const [resumes, setResumes] = useState([]);
  const [selectedResume, setSelectedResume] = useState("");
  const [jdText, setJdText] = useState("");
  const [jdUrl, setJdUrl] = useState("");
  const [jobTitle, setJobTitle] = useState("");
  const [company, setCompany] = useState("");
  const [loading, setLoading] = useState(false);
  const [fetchingJD, setFetchingJD] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  // Mock interview state
  const [question, setQuestion] = useState("Walk me through your RAG pipeline architecture.");
  const [answer, setAnswer] = useState("");
  const [mockResult, setMockResult] = useState(null);

  // Roadmap state
  const [targetRole, setTargetRole] = useState("AI/ML Engineer");
  const [roadmapResult, setRoadmapResult] = useState(null);

  useEffect(() => {
    resumeAPI.list().then((r) => {
      setResumes(r.data);
      if (r.data.length > 0) setSelectedResume(String(r.data[0].id));
    });
  }, []);

  const fetchJD = async () => {
    if (!jdUrl) return;
    setFetchingJD(true);
    try {
      const res = await copilotAPI.fetchJD(jdUrl);
      setJdText(res.data.jd_text);
    } catch (e) {
      setError("Could not fetch JD from URL. Please paste it manually.");
    } finally {
      setFetchingJD(false);
    }
  };

  const runTailor = async () => {
    if (!selectedResume || !jdText) { setError("Select a resume and provide JD."); return; }
    setLoading(true); setError(""); setResult(null);
    try {
      const res = await copilotAPI.tailorResume({
        resume_id: parseInt(selectedResume), jd_text: jdText,
        job_title: jobTitle || "the role", company_name: company || "the company"
      });
      setResult(res.data);
    } catch (e) { setError(e.response?.data?.detail || "Failed. Try again."); }
    finally { setLoading(false); }
  };

  const runCoverLetter = async () => {
    if (!selectedResume || !jdText) { setError("Select a resume and provide JD."); return; }
    setLoading(true); setError(""); setResult(null);
    try {
      const res = await copilotAPI.coverLetter({
        resume_id: parseInt(selectedResume), jd_text: jdText,
        job_title: jobTitle || "the role", company_name: company || "the company"
      });
      setResult(res.data);
    } catch (e) { setError(e.response?.data?.detail || "Failed. Try again."); }
    finally { setLoading(false); }
  };

  const runMock = async () => {
    if (!answer) { setError("Type your answer first."); return; }
    setLoading(true); setError(""); setMockResult(null);
    try {
      const res = await copilotAPI.scoreAnswer({ question, answer, role_title: targetRole });
      setMockResult(res.data);
    } catch (e) { setError(e.response?.data?.detail || "Failed. Try again."); }
    finally { setLoading(false); }
  };

  const runRoadmap = async () => {
    if (!selectedResume) { setError("Select a resume first."); return; }
    setLoading(true); setError(""); setRoadmapResult(null);
    try {
      const res = await copilotAPI.roadmap({ resume_id: parseInt(selectedResume), target_role: targetRole });
      setRoadmapResult(res.data);
    } catch (e) { setError(e.response?.data?.detail || "Failed. Try again."); }
    finally { setLoading(false); }
  };

  const JDInput = () => (
    <div style={{ marginBottom: 16 }}>
      <label className="label">Job Description</label>
      <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
        <input className="input" placeholder="Paste job URL to auto-fetch..." value={jdUrl}
          onChange={(e) => setJdUrl(e.target.value)} style={{ flex: 1 }} />
        <button className="btn btn-outline" onClick={fetchJD} disabled={fetchingJD || !jdUrl}
          style={{ whiteSpace: "nowrap" }}>
          {fetchingJD ? <span className="spinner" /> : "Auto-fetch"}
        </button>
      </div>
      <textarea className="textarea" placeholder="...or paste job description here"
        value={jdText} onChange={(e) => setJdText(e.target.value)} style={{ minHeight: 100 }} />
    </div>
  );

  const JobFields = () => (
    <div className="grid-2" style={{ marginBottom: 16 }}>
      <div>
        <label className="label">Job Title</label>
        <input className="input" placeholder="e.g. AI Engineer" value={jobTitle} onChange={(e) => setJobTitle(e.target.value)} />
      </div>
      <div>
        <label className="label">Company Name</label>
        <input className="input" placeholder="e.g. Zoho" value={company} onChange={(e) => setCompany(e.target.value)} />
      </div>
    </div>
  );

  const scoreColor = (s) => s >= 8 ? "#059669" : s >= 5 ? "#d97706" : "#dc2626";
  const scoreBg = (s) => s >= 8 ? "#ecfdf5" : s >= 5 ? "#fffbeb" : "#fef2f2";

  return (
    <div>
      <h1 className="page-title">AI Job Copilot</h1>
      <p className="page-subtitle">Tailor your resume, generate cover letters, practice interviews, and plan your career</p>

      <div style={{ display: "flex", gap: 6, marginBottom: 24, flexWrap: "wrap" }}>
        {TABS.map(t => <TabBtn key={t.id} id={t.id} label={t.label} active={activeTab === t.id} onClick={(id) => { setActiveTab(id); setResult(null); setError(""); }} />)}
      </div>

      {/* Resume selector */}
      {activeTab !== "mock" && (
        <div className="card" style={{ marginBottom: 16 }}>
          <label className="label">Select Resume</label>
          <select className="input" value={selectedResume} onChange={(e) => setSelectedResume(e.target.value)} style={{ maxWidth: 400 }}>
            <option value="">Choose a resume...</option>
            {resumes.map((r) => <option key={r.id} value={r.id}>{r.filename}</option>)}
          </select>
        </div>
      )}

      {/* TAILOR RESUME */}
      {activeTab === "tailor" && (
        <div className="card">
          <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>Tailor Resume to Job</h2>
          <JobFields />
          <JDInput />
          {error && <p className="error-msg" style={{ marginBottom: 12 }}>{error}</p>}
          <button className="btn btn-primary" onClick={runTailor} disabled={loading || !selectedResume || !jdText}>
            {loading ? <><span className="spinner" /> Tailoring...</> : "✂️ Tailor My Resume"}
          </button>

          {result && (
            <div style={{ marginTop: 24 }}>
              {result.tailored_summary && (
                <div style={{ marginBottom: 20, padding: 16, background: "#eef2ff", borderRadius: 10 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                    <div style={{ fontWeight: 600, color: "#3730a3" }}>✨ Tailored Summary</div>
                    <CopyBtn text={result.tailored_summary} />
                  </div>
                  <p style={{ fontSize: 14, color: "#374151", lineHeight: 1.7 }}>{result.tailored_summary}</p>
                </div>
              )}

              {result.tailored_bullets?.length > 0 && (
                <div style={{ marginBottom: 20 }}>
                  <div style={{ fontWeight: 600, marginBottom: 12, fontSize: 15 }}>📝 Rewritten Bullet Points</div>
                  {result.tailored_bullets.map((b, i) => (
                    <div key={i} style={{ marginBottom: 12, padding: 14, background: "#f9fafb", borderRadius: 10, border: "1px solid #e5e7eb" }}>
                      <div style={{ fontSize: 12, fontWeight: 500, color: "#6b7280", marginBottom: 8 }}>{b.section}</div>
                      <div style={{ fontSize: 13, color: "#dc2626", marginBottom: 6, textDecoration: "line-through" }}>{b.original}</div>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 8 }}>
                        <div style={{ fontSize: 13, color: "#059669", fontWeight: 500, flex: 1 }}>→ {b.tailored}</div>
                        <CopyBtn text={b.tailored} />
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {result.keywords_added?.length > 0 && (
                <div>
                  <div style={{ fontWeight: 600, marginBottom: 8, fontSize: 14 }}>🔑 Keywords Added</div>
                  {result.keywords_added.map(k => <span key={k} className="pill">{k}</span>)}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* COVER LETTER */}
      {activeTab === "cover" && (
        <div className="card">
          <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>Generate Cover Letter</h2>
          <JobFields />
          <JDInput />
          {error && <p className="error-msg" style={{ marginBottom: 12 }}>{error}</p>}
          <button className="btn btn-primary" onClick={runCoverLetter} disabled={loading || !selectedResume || !jdText}>
            {loading ? <><span className="spinner" /> Writing...</> : "📝 Generate Cover Letter"}
          </button>

          {result && (
            <div style={{ marginTop: 24 }}>
              <div style={{ marginBottom: 16, padding: 12, background: "#f9fafb", borderRadius: 8, border: "1px solid #e5e7eb" }}>
                <div style={{ fontSize: 12, color: "#6b7280", marginBottom: 4 }}>Email Subject</div>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div style={{ fontWeight: 500, fontSize: 14 }}>{result.subject_line}</div>
                  <CopyBtn text={result.subject_line} />
                </div>
              </div>
              <div style={{ padding: 20, background: "#f9fafb", borderRadius: 10, border: "1px solid #e5e7eb" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
                  <div style={{ fontWeight: 600 }}>Cover Letter</div>
                  <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                    <span style={{ fontSize: 12, color: "#9ca3af" }}>{result.word_count} words</span>
                    <CopyBtn text={result.cover_letter} />
                  </div>
                </div>
                <pre style={{ whiteSpace: "pre-wrap", fontSize: 14, color: "#374151", lineHeight: 1.8, fontFamily: "inherit" }}>
                  {result.cover_letter}
                </pre>
              </div>
            </div>
          )}
        </div>
      )}

      {/* MOCK INTERVIEW */}
      {activeTab === "mock" && (
        <div className="card">
          <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>Mock Interview Scorer</h2>
          <div style={{ marginBottom: 16 }}>
            <label className="label">Target Role</label>
            <input className="input" value={targetRole} onChange={(e) => setTargetRole(e.target.value)} style={{ maxWidth: 300 }} />
          </div>
          <div style={{ marginBottom: 16 }}>
            <label className="label">Question</label>
            <textarea className="textarea" value={question} onChange={(e) => setQuestion(e.target.value)} style={{ minHeight: 60 }} />
          </div>
          <div style={{ marginBottom: 16 }}>
            <label className="label">Your Answer</label>
            <textarea className="textarea" placeholder="Type your answer here as you would say it in an interview..."
              value={answer} onChange={(e) => setAnswer(e.target.value)} style={{ minHeight: 120 }} />
          </div>
          {error && <p className="error-msg" style={{ marginBottom: 12 }}>{error}</p>}
          <button className="btn btn-primary" onClick={runMock} disabled={loading || !answer}>
            {loading ? <><span className="spinner" /> Scoring...</> : "🎯 Score My Answer"}
          </button>

          {mockResult && (
            <div style={{ marginTop: 24 }}>
              <div style={{ display: "flex", gap: 16, alignItems: "center", marginBottom: 20 }}>
                <div style={{ width: 80, height: 80, borderRadius: "50%", background: scoreBg(mockResult.score),
                  display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
                  <div style={{ fontSize: 28, fontWeight: 700, color: scoreColor(mockResult.score) }}>{mockResult.score}</div>
                  <div style={{ fontSize: 11, color: scoreColor(mockResult.score) }}>/10</div>
                </div>
                <div>
                  <div style={{ fontSize: 18, fontWeight: 600, color: scoreColor(mockResult.score) }}>{mockResult.verdict}</div>
                  <div style={{ fontSize: 13, color: "#6b7280", marginTop: 2 }}>Interview answer score</div>
                </div>
              </div>

              <div className="grid-2" style={{ marginBottom: 16 }}>
                <div style={{ padding: 14, background: "#ecfdf5", borderRadius: 10 }}>
                  <div style={{ fontWeight: 500, color: "#065f46", marginBottom: 8 }}>✓ Strengths</div>
                  {mockResult.strengths?.map((s, i) => <div key={i} style={{ fontSize: 13, color: "#374151", marginBottom: 4 }}>• {s}</div>)}
                </div>
                <div style={{ padding: 14, background: "#fef2f2", borderRadius: 10 }}>
                  <div style={{ fontWeight: 500, color: "#991b1b", marginBottom: 8 }}>↑ Improve</div>
                  {mockResult.improvements?.map((s, i) => <div key={i} style={{ fontSize: 13, color: "#374151", marginBottom: 4 }}>• {s}</div>)}
                </div>
              </div>

              <div style={{ padding: 14, background: "#eef2ff", borderRadius: 10, marginBottom: 12 }}>
                <div style={{ fontWeight: 500, color: "#3730a3", marginBottom: 6 }}>💡 Ideal Answer Should Include</div>
                <p style={{ fontSize: 13, color: "#374151" }}>{mockResult.ideal_answer_hints}</p>
              </div>

              {mockResult.follow_up_question && (
                <div style={{ padding: 14, background: "#fffbeb", borderRadius: 10, border: "1px solid #fcd34d" }}>
                  <div style={{ fontWeight: 500, color: "#92400e", marginBottom: 6 }}>⚡ Likely Follow-up Question</div>
                  <p style={{ fontSize: 14, color: "#374151", fontStyle: "italic" }}>"{mockResult.follow_up_question}"</p>
                  <button className="btn btn-outline" style={{ marginTop: 10, fontSize: 12 }}
                    onClick={() => { setQuestion(mockResult.follow_up_question); setAnswer(""); setMockResult(null); }}>
                    Answer this question →
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* ROADMAP */}
      {activeTab === "roadmap" && (
        <div className="card">
          <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>Skill Gap Roadmap</h2>
          <div style={{ marginBottom: 16 }}>
            <label className="label">Target Role</label>
            <input className="input" value={targetRole} onChange={(e) => setTargetRole(e.target.value)} style={{ maxWidth: 300 }} />
          </div>
          {error && <p className="error-msg" style={{ marginBottom: 12 }}>{error}</p>}
          <button className="btn btn-primary" onClick={runRoadmap} disabled={loading || !selectedResume}>
            {loading ? <><span className="spinner" /> Generating roadmap...</> : "🗺️ Generate My Roadmap"}
          </button>

          {roadmapResult && (
            <div style={{ marginTop: 24 }}>
              <div className="grid-3" style={{ marginBottom: 20 }}>
                <div style={{ padding: 16, background: "#f9fafb", borderRadius: 10, textAlign: "center" }}>
                  <div style={{ fontSize: 28, fontWeight: 700, color: scoreColor(roadmapResult.gap_score) }}>{roadmapResult.gap_score}/10</div>
                  <div style={{ fontSize: 12, color: "#6b7280" }}>Readiness Score</div>
                </div>
                <div style={{ padding: 16, background: "#f9fafb", borderRadius: 10, textAlign: "center" }}>
                  <div style={{ fontSize: 28, fontWeight: 700, color: "#4f46e5" }}>{roadmapResult.weeks_to_ready}w</div>
                  <div style={{ fontSize: 12, color: "#6b7280" }}>Weeks to Ready</div>
                </div>
                <div style={{ padding: 16, background: "#f9fafb", borderRadius: 10, textAlign: "center" }}>
                  <div style={{ fontSize: 14, fontWeight: 500, color: "#374151" }}>{roadmapResult.target_role}</div>
                  <div style={{ fontSize: 12, color: "#6b7280" }}>Target Role</div>
                </div>
              </div>

              <div className="grid-2" style={{ marginBottom: 20 }}>
                <div style={{ padding: 14, background: "#ecfdf5", borderRadius: 10 }}>
                  <div style={{ fontWeight: 500, color: "#065f46", marginBottom: 8 }}>✓ You Already Have</div>
                  {roadmapResult.green_flags?.map((g, i) => <div key={i} style={{ fontSize: 13, color: "#374151", marginBottom: 4 }}>• {g}</div>)}
                </div>
                <div style={{ padding: 14, background: "#fef2f2", borderRadius: 10 }}>
                  <div style={{ fontWeight: 500, color: "#991b1b", marginBottom: 8 }}>⚠️ Watch Out For</div>
                  {roadmapResult.red_flags?.map((r, i) => <div key={i} style={{ fontSize: 13, color: "#374151", marginBottom: 4 }}>• {r}</div>)}
                </div>
              </div>

              {roadmapResult.must_build && (
                <div style={{ padding: 14, background: "#eef2ff", borderRadius: 10, marginBottom: 20 }}>
                  <div style={{ fontWeight: 500, color: "#3730a3", marginBottom: 4 }}>🏗️ Must Build This Project</div>
                  <p style={{ fontSize: 14, color: "#374151" }}>{roadmapResult.must_build}</p>
                </div>
              )}

              <div>
                <div style={{ fontWeight: 600, marginBottom: 12 }}>📅 Week-by-Week Plan</div>
                {roadmapResult.roadmap?.map((week, i) => (
                  <div key={i} style={{ marginBottom: 12, padding: 14, background: "#f9fafb", borderRadius: 10, border: "1px solid #e5e7eb" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                      <span style={{ fontWeight: 500, fontSize: 14 }}>{week.week}</span>
                      <span className="badge badge-blue" style={{ fontSize: 11 }}>{week.focus}</span>
                    </div>
                    {week.tasks?.map((t, j) => <div key={j} style={{ fontSize: 13, color: "#374151", marginBottom: 3 }}>• {t}</div>)}
                    {week.resources?.length > 0 && (
                      <div style={{ marginTop: 6 }}>
                        {week.resources.map((r, j) => <span key={j} style={{ fontSize: 11, color: "#6b7280", marginRight: 8 }}>📚 {r}</span>)}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
