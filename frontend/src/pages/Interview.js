import React, { useState, useEffect } from "react";
import { resumeAPI, interviewAPI } from "../services/api";

const CAT_COLORS = {
  technical: { bg:"#eef2ff", color:"#4f46e5" },
  behavioral: { bg:"#ecfdf5", color:"#059669" },
  "project-based": { bg:"#fffbeb", color:"#d97706" },
  hr: { bg:"#fdf4ff", color:"#9333ea" },
};

function QuestionCard({ q, index }) {
  const [open, setOpen] = useState(false);
  const cat = CAT_COLORS[q.category] || { bg:"#f3f4f6", color:"#374151" };
  const diffBadge = q.difficulty === "easy" ? "badge-green" : q.difficulty === "hard" ? "badge-red" : "badge-yellow";
  return (
    <div style={{ border:"1px solid #e5e7eb", borderRadius:10, overflow:"hidden", marginBottom:10 }}>
      <div onClick={() => setOpen(!open)}
        style={{ padding:"14px 16px", cursor:"pointer", background: open ? "#f9fafb" : "white",
          display:"flex", justifyContent:"space-between", alignItems:"flex-start", gap:12 }}>
        <div style={{ flex:1 }}>
          <div style={{ display:"flex", gap:6, marginBottom:6, flexWrap:"wrap" }}>
            <span style={{ fontSize:11, padding:"2px 8px", borderRadius:20, background:cat.bg, color:cat.color, fontWeight:500 }}>
              {q.category}
            </span>
            <span className={`badge ${diffBadge}`} style={{ fontSize:11 }}>{q.difficulty}</span>
          </div>
          <div style={{ fontWeight:500, fontSize:14, color:"#111827" }}>Q{index + 1}. {q.question}</div>
        </div>
        <span style={{ color:"#9ca3af", fontSize:18, flexShrink:0 }}>{open ? "▲" : "▼"}</span>
      </div>
      {open && (
        <div style={{ padding:"14px 16px", background:"#f9fafb", borderTop:"1px solid #e5e7eb" }}>
          <div style={{ fontSize:12, fontWeight:500, color:"#6b7280", marginBottom:6, textTransform:"uppercase", letterSpacing:"0.05em" }}>
            Model Answer
          </div>
          <p style={{ fontSize:14, color:"#374151", lineHeight:1.7 }}>{q.model_answer}</p>
        </div>
      )}
    </div>
  );
}

export default function Interview() {
  const [resumes, setResumes] = useState([]);
  const [selectedResume, setSelectedResume] = useState("");
  const [roleTitle, setRoleTitle] = useState("AI/ML Engineer");
  const [questions, setQuestions] = useState([]);
  const [tips, setTips] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState("prep");
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    resumeAPI.list().then((r) => {
      setResumes(r.data);
      if (r.data.length > 0) setSelectedResume(String(r.data[0].id));
    });
    interviewAPI.tips().then((r) => setTips(r.data)).catch(() => {});
  }, []);

  const generate = async () => {
    if (!selectedResume) { setError("Select a resume first."); return; }
    setLoading(true); setError("");
    try {
      const res = await interviewAPI.generate({ resume_id: parseInt(selectedResume), role_title: roleTitle });
      setQuestions(res.data.questions);
      setActiveTab("questions");
    } catch (e) { setError(e.response?.data?.detail || "Failed to generate questions."); }
    finally { setLoading(false); }
  };

  const filtered = filter === "all" ? questions : questions.filter((q) => q.category === filter);
  const categories = ["all", ...new Set(questions.map((q) => q.category))];

  const TABS = [
    { id:"prep", label:"Generate Questions" },
    { id:"questions", label:`Questions (${questions.length})` },
    { id:"tips", label:"Interview Tips" },
  ];

  return (
    <div>
      <h1 className="page-title">Interview Prep</h1>
      <p className="page-subtitle">AI-generated questions tailored to your resume and target role</p>

      <div style={{ display:"flex", gap:4, marginBottom:20, background:"white", padding:"6px", borderRadius:10, boxShadow:"var(--shadow)", width:"fit-content" }}>
        {TABS.map(tab => (
          <button key={tab.id} onClick={() => setActiveTab(tab.id)}
            style={{ padding:"8px 18px", borderRadius:7, border:"none", cursor:"pointer", fontSize:13, fontWeight:500,
              background: activeTab === tab.id ? "#4f46e5" : "transparent",
              color: activeTab === tab.id ? "white" : "#6b7280", transition:"all 0.15s" }}>
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === "prep" && (
        <div className="card" style={{ maxWidth:600 }}>
          <h2 style={{ fontSize:16, fontWeight:600, marginBottom:16 }}>Generate Personalized Questions</h2>
          <div style={{ marginBottom:16 }}>
            <label className="label">Select Resume</label>
            <select className="input" value={selectedResume} onChange={(e) => setSelectedResume(e.target.value)}>
              <option value="">Choose a resume...</option>
              {resumes.map((r) => <option key={r.id} value={r.id}>{r.filename}</option>)}
            </select>
          </div>
          <div style={{ marginBottom:20 }}>
            <label className="label">Target Role</label>
            <input className="input" value={roleTitle} onChange={(e) => setRoleTitle(e.target.value)}
              placeholder="e.g. AI Engineer, Python Developer, Data Scientist" />
          </div>
          {error && <p className="error-msg" style={{ marginBottom:12 }}>{error}</p>}
          <button className="btn btn-primary" onClick={generate} disabled={loading || !selectedResume}
            style={{ justifyContent:"center", minWidth:200 }}>
            {loading ? <><span className="spinner"/> Generating...</> : "◆ Generate 10 Questions"}
          </button>
          <div style={{ marginTop:24, padding:16, background:"#f9fafb", borderRadius:10 }}>
            <div style={{ fontWeight:500, fontSize:13, marginBottom:8 }}>💡 How to use</div>
            <div style={{ fontSize:13, color:"#4b5563", lineHeight:1.8 }}>
              1. Generate questions for your target role<br/>
              2. Click each question to reveal model answer<br/>
              3. Practice out loud — aim for 90 seconds max<br/>
              4. Re-generate with different roles
            </div>
          </div>
        </div>
      )}

      {activeTab === "questions" && (
        <div>
          {questions.length === 0 ? (
            <div className="card" style={{ textAlign:"center", padding:"3rem" }}>
              <p style={{ color:"#6b7280" }}>No questions yet. Go to Generate tab first.</p>
            </div>
          ) : (
            <div>
              <div style={{ display:"flex", gap:6, marginBottom:16, flexWrap:"wrap" }}>
                {categories.map((cat) => (
                  <button key={cat} onClick={() => setFilter(cat)}
                    style={{ padding:"6px 14px", borderRadius:20, border:"1px solid", fontSize:12, cursor:"pointer",
                      borderColor: filter === cat ? "#4f46e5" : "#d1d5db",
                      background: filter === cat ? "#4f46e5" : "white",
                      color: filter === cat ? "white" : "#374151", fontWeight:500 }}>
                    {cat === "all" ? `All (${questions.length})` : cat}
                  </button>
                ))}
              </div>
              {filtered.map((q, i) => <QuestionCard key={i} q={q} index={questions.indexOf(q)} />)}
            </div>
          )}
        </div>
      )}

      {activeTab === "tips" && tips && (
        <div style={{ display:"flex", flexDirection:"column", gap:16 }}>
          {tips.rounds?.map((round) => (
            <div key={round.round} className="card">
              <div style={{ fontWeight:600, fontSize:15, marginBottom:4 }}>{round.round}</div>
              <div style={{ fontSize:13, color:"#6b7280", marginBottom:8 }}>Expect: {round.what_to_expect}</div>
              <div style={{ fontSize:13, color:"#374151", padding:10, background:"#eef2ff", borderRadius:8 }}>
                💡 {round.prep}
              </div>
            </div>
          ))}
          <div className="card">
            <div style={{ fontWeight:600, fontSize:15, marginBottom:12 }}>❌ Common Mistakes</div>
            {tips.common_mistakes?.map((m, i) => (
              <div key={i} style={{ fontSize:13, color:"#374151", marginBottom:8, display:"flex", gap:8 }}>
                <span style={{ color:"#dc2626", flexShrink:0 }}>✗</span> {m}
              </div>
            ))}
          </div>
          <div className="card">
            <div style={{ fontWeight:600, fontSize:15, marginBottom:12 }}>✅ Power Phrases That Impress</div>
            {tips.power_phrases?.map((p, i) => (
              <div key={i} style={{ fontSize:13, color:"#374151", marginBottom:10, padding:12,
                background:"#ecfdf5", borderRadius:8, borderLeft:"3px solid #059669" }}>
                "{p}"
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
