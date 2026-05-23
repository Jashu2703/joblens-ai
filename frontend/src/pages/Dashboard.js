import React, { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useDropzone } from "react-dropzone";
import { resumeAPI, jobsAPI } from "../services/api";
import { useAuth } from "../App";

export default function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [resumes, setResumes] = useState([]);
  const [jobStats, setJobStats] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [error, setError] = useState("");
  const [seeding, setSeeding] = useState(false);

  const loadData = async () => {
    try {
      const [resumeRes, statsRes] = await Promise.all([resumeAPI.list(), jobsAPI.stats()]);
      setResumes(resumeRes.data);
      setJobStats(statsRes.data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => { loadData(); }, []);

  const onDrop = useCallback(async (files) => {
    if (!files.length) return;
    setUploading(true);
    setError("");
    setUploadResult(null);
    try {
      const res = await resumeAPI.upload(files[0]);
      setUploadResult(res.data);
      loadData();
    } catch (e) {
      setError(e.response?.data?.detail || "Upload failed. Try a PDF or DOCX file.");
    } finally {
      setUploading(false);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"], "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"] },
    maxFiles: 1,
    disabled: uploading,
  });

  const seedJobs = async () => {
    setSeeding(true);
    try {
      await jobsAPI.seedNow();
      await loadData();
    } catch (e) {
      console.error(e);
    } finally {
      setSeeding(false);
    }
  };

  const deleteResume = async (id) => {
    if (!window.confirm("Delete this resume?")) return;
    await resumeAPI.delete(id);
    loadData();
  };

  return (
    <div>
      <div style={{ marginBottom: 28 }}>
        <h1 className="page-title">Welcome back, {user?.name?.split(" ")[0]} 👋</h1>
        <p className="page-subtitle">Upload your resume and get AI-powered job search intelligence</p>
      </div>

      <div className="grid-3" style={{ marginBottom: 24 }}>
        <div className="card" style={{ textAlign: "center" }}>
          <div style={{ fontSize: 28, fontWeight: 700, color: "#4f46e5" }}>{resumes.length}</div>
          <div style={{ fontSize: 13, color: "#6b7280", marginTop: 4 }}>Resumes uploaded</div>
        </div>
        <div className="card" style={{ textAlign: "center" }}>
          <div style={{ fontSize: 28, fontWeight: 700, color: "#059669" }}>{jobStats?.total_jobs || 0}</div>
          <div style={{ fontSize: 13, color: "#6b7280", marginTop: 4 }}>Jobs in database</div>
        </div>
        <div className="card" style={{ textAlign: "center" }}>
          <div style={{ fontSize: 28, fontWeight: 700, color: "#d97706" }}>{jobStats?.internships || 0}</div>
          <div style={{ fontSize: 13, color: "#6b7280", marginTop: 4 }}>Internships available</div>
        </div>
      </div>

      {jobStats?.total_jobs === 0 && (
        <div className="card" style={{ marginBottom: 20, background: "#fffbeb", border: "1px solid #fcd34d" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div>
              <div style={{ fontWeight: 500, color: "#92400e" }}>Job database is empty</div>
              <div style={{ fontSize: 13, color: "#b45309", marginTop: 2 }}>Seed 15 curated fresher jobs to enable role matching</div>
            </div>
            <button className="btn btn-primary" onClick={seedJobs} disabled={seeding}>
              {seeding ? <span className="spinner" /> : "Seed Jobs Now"}
            </button>
          </div>
        </div>
      )}

      <div className="grid-2">
        <div>
          <div className="card">
            <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>Upload Resume</h2>
            <div
              {...getRootProps()}
              style={{
                border: `2px dashed ${isDragActive ? "#4f46e5" : "#d1d5db"}`,
                borderRadius: 10,
                padding: "2rem",
                textAlign: "center",
                cursor: uploading ? "not-allowed" : "pointer",
                background: isDragActive ? "#eef2ff" : "#f9fafb",
                transition: "all 0.2s",
              }}
            >
              <input {...getInputProps()} />
              {uploading ? (
                <div>
                  <div className="spinner" style={{ margin: "0 auto 12px" }} />
                  <p style={{ color: "#6b7280", fontSize: 14 }}>Parsing your resume...</p>
                </div>
              ) : (
                <div>
                  <div style={{ fontSize: 32, marginBottom: 8 }}>📄</div>
                  <p style={{ fontWeight: 500, color: "#374151", marginBottom: 4 }}>
                    {isDragActive ? "Drop it here!" : "Drop resume here or click to upload"}
                  </p>
                  <p style={{ fontSize: 12, color: "#9ca3af" }}>PDF or DOCX · Max 10MB</p>
                </div>
              )}
            </div>

            {error && (
              <div style={{ marginTop: 12, padding: 12, background: "#fef2f2", borderRadius: 8, color: "#dc2626", fontSize: 13 }}>
                {error}
              </div>
            )}

            {uploadResult && (
              <div style={{ marginTop: 12, padding: 12, background: "#ecfdf5", borderRadius: 8, border: "1px solid #6ee7b7" }}>
                <div style={{ fontWeight: 500, color: "#065f46", marginBottom: 8 }}>✓ Resume parsed successfully!</div>
                <div style={{ fontSize: 13, color: "#047857" }}>
                  <div>Skills found: <strong>{uploadResult.skills_found?.length || 0}</strong></div>
                  <div>Word count: <strong>{uploadResult.word_count}</strong></div>
                  {uploadResult.email && <div>Email: <strong>{uploadResult.email}</strong></div>}
                </div>
                {uploadResult.skills_found?.slice(0, 6).map(s => (
                  <span key={s} className="pill" style={{ marginTop: 8 }}>{s}</span>
                ))}
                <button
                  className="btn btn-primary"
                  style={{ marginTop: 12, width: "100%", justifyContent: "center" }}
                  onClick={() => navigate("/analyze")}
                >
                  Analyze this resume →
                </button>
              </div>
            )}
          </div>
        </div>

        <div>
          <div className="card">
            <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 16 }}>Your Resumes</h2>
            {resumes.length === 0 ? (
              <div style={{ textAlign: "center", padding: "2rem", color: "#9ca3af" }}>
                <div style={{ fontSize: 32, marginBottom: 8 }}>📋</div>
                <p style={{ fontSize: 14 }}>No resumes yet. Upload your first one.</p>
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                {resumes.map((r) => (
                  <div key={r.id} style={{
                    padding: "12px 14px",
                    background: "#f9fafb",
                    borderRadius: 8,
                    border: "1px solid #e5e7eb",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "flex-start",
                  }}>
                    <div>
                      <div style={{ fontWeight: 500, fontSize: 14 }}>📄 {r.filename}</div>
                      <div style={{ fontSize: 12, color: "#6b7280", marginTop: 3 }}>
                        {r.skills?.slice(0, 3).join(", ")} · {r.word_count} words
                      </div>
                    </div>
                    <div style={{ display: "flex", gap: 6 }}>
                      <button className="btn btn-outline" style={{ padding: "4px 10px", fontSize: 12 }}
                        onClick={() => navigate(`/analyze?resume_id=${r.id}`)}>
                        Analyze
                      </button>
                      <button style={{ background: "none", border: "none", cursor: "pointer", color: "#dc2626", fontSize: 14 }}
                        onClick={() => deleteResume(r.id)}>✕</button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="card" style={{ marginTop: 16 }}>
            <h2 style={{ fontSize: 16, fontWeight: 600, marginBottom: 12 }}>Quick Actions</h2>
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              <button className="btn btn-outline" style={{ justifyContent: "flex-start" }} onClick={() => navigate("/analyze")}>
                ◎ Run Full Analysis
              </button>
              <button className="btn btn-outline" style={{ justifyContent: "flex-start" }} onClick={() => navigate("/jobs")}>
                ◈ Browse Job Matches
              </button>
              <button className="btn btn-outline" style={{ justifyContent: "flex-start" }} onClick={() => navigate("/interview")}>
                ◆ Practice Interview Prep
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
