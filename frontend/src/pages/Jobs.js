import React, { useState, useEffect } from "react";
import { jobsAPI } from "../services/api";

export default function Jobs() {
  const [jobs, setJobs] = useState([]);
  const [total, setTotal] = useState(0);
  const [search, setSearch] = useState("");
  const [jobType, setJobType] = useState("");
  const [loading, setLoading] = useState(false);
  const [seeding, setSeeding] = useState(false);
  const [stats, setStats] = useState(null);

  const loadJobs = async () => {
    setLoading(true);
    try {
      const res = await jobsAPI.list({ search, job_type: jobType, limit: 30 });
      setJobs(res.data.jobs);
      setTotal(res.data.total);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const loadStats = async () => {
    try { const res = await jobsAPI.stats(); setStats(res.data); } catch (e) {}
  };

  useEffect(() => { loadJobs(); loadStats(); }, []);
  useEffect(() => { const t = setTimeout(loadJobs, 400); return () => clearTimeout(t); }, [search, jobType]);

  const seedNow = async () => {
    setSeeding(true);
    try { await jobsAPI.seedNow(); await loadJobs(); await loadStats(); }
    catch (e) { console.error(e); }
    finally { setSeeding(false); }
  };

  return (
    <div>
      <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start", marginBottom:24 }}>
        <div>
          <h1 className="page-title">Job Database</h1>
          <p className="page-subtitle">{total} curated fresher AI/ML/Python jobs in India</p>
        </div>
        <button className="btn btn-primary" onClick={seedNow} disabled={seeding}>
          {seeding ? <><span className="spinner"/> Seeding...</> : "↻ Refresh Jobs"}
        </button>
      </div>

      {stats && (
        <div className="grid-3" style={{ marginBottom:20 }}>
          {[
            { val: stats.total_jobs, label: "Total Jobs", color: "#4f46e5" },
            { val: stats.full_time, label: "Full-time", color: "#059669" },
            { val: stats.internships, label: "Internships", color: "#d97706" },
          ].map(({ val, label, color }) => (
            <div key={label} className="card" style={{ textAlign:"center" }}>
              <div style={{ fontSize:26, fontWeight:700, color }}>{val}</div>
              <div style={{ fontSize:13, color:"#6b7280" }}>{label}</div>
            </div>
          ))}
        </div>
      )}

      <div className="card" style={{ marginBottom:20 }}>
        <div style={{ display:"flex", gap:12 }}>
          <input className="input" placeholder="Search by title, company, or skill..." value={search}
            onChange={(e) => setSearch(e.target.value)} style={{ flex:1 }} />
          <select className="input" style={{ width:160 }} value={jobType} onChange={(e) => setJobType(e.target.value)}>
            <option value="">All types</option>
            <option value="full-time">Full-time</option>
            <option value="internship">Internship</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign:"center", padding:"3rem" }}>
          <div className="spinner" style={{ margin:"0 auto 12px" }}/>
          <p style={{ color:"#6b7280", fontSize:14 }}>Loading jobs...</p>
        </div>
      ) : jobs.length === 0 ? (
        <div className="card" style={{ textAlign:"center", padding:"3rem" }}>
          <div style={{ fontSize:40, marginBottom:12 }}>🔍</div>
          <p style={{ fontWeight:500, marginBottom:8 }}>No jobs found</p>
          <p style={{ fontSize:14, color:"#6b7280", marginBottom:16 }}>
            {total === 0 ? "Database is empty — seed jobs to get started." : "Try a different search."}
          </p>
          {total === 0 && (
            <button className="btn btn-primary" onClick={seedNow} disabled={seeding}>
              {seeding ? "Seeding..." : "Seed 15 Curated Jobs Now"}
            </button>
          )}
        </div>
      ) : (
        <div style={{ display:"flex", flexDirection:"column", gap:12 }}>
          {jobs.map((job) => (
            <div key={job.id} className="card" style={{ padding:"16px 20px" }}>
              <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start" }}>
                <div style={{ flex:1 }}>
                  <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:4 }}>
                    <span style={{ fontWeight:600, fontSize:15 }}>{job.title}</span>
                    <span className={`badge ${job.job_type === "internship" ? "badge-blue" : "badge-green"}`}>{job.job_type}</span>
                  </div>
                  <div style={{ fontSize:13, color:"#6b7280" }}>
                    🏢 {job.company} &nbsp;·&nbsp; 📍 {job.location || "India"}
                    {job.experience_required && <>&nbsp;·&nbsp; ⏱ {job.experience_required}</>}
                  </div>
                  {job.salary_range && (
                    <div style={{ fontSize:13, color:"#4f46e5", fontWeight:500, marginTop:4 }}>💰 {job.salary_range}</div>
                  )}
                  <div style={{ marginTop:10, display:"flex", flexWrap:"wrap", gap:4 }}>
                    {(job.skills_required || []).slice(0, 6).map((s) => (
                      <span key={s} className="pill" style={{ fontSize:11 }}>{s}</span>
                    ))}
                    {(job.skills_required || []).length > 6 && (
                      <span className="pill pill-gray" style={{ fontSize:11 }}>+{job.skills_required.length - 6} more</span>
                    )}
                  </div>
                </div>
                {job.source_url && (
                  <a href={job.source_url} target="_blank" rel="noreferrer"
                    className="btn btn-outline" style={{ marginLeft:16, padding:"6px 14px", fontSize:12, flexShrink:0 }}>
                    Apply →
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
