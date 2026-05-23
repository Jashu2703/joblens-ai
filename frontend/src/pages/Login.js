import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { authAPI } from "../services/api";
import { useAuth } from "../App";

export default function Login() {
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handle = (e) => setForm({ ...form, [e.target.name]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const res = await authAPI.login(form);
      login(res.data.user, res.data.access_token);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed. Check your credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "linear-gradient(135deg, #667eea22 0%, #764ba222 100%)" }}>
      <div style={{ width: "100%", maxWidth: 420, padding: 16 }}>
        <div className="card" style={{ padding: "2rem" }}>
          <div style={{ textAlign: "center", marginBottom: "2rem" }}>
            <div style={{ fontSize: 32, marginBottom: 8 }}>◎</div>
            <h1 style={{ fontSize: 24, fontWeight: 700, color: "#1a1a2e" }}>JobLens AI</h1>
            <p style={{ color: "#6b7280", fontSize: 14, marginTop: 4 }}>Your job search intelligence platform</p>
          </div>
          <form onSubmit={submit}>
            <div style={{ marginBottom: 16 }}>
              <label className="label">Email</label>
              <input className="input" type="email" name="email" placeholder="you@email.com" value={form.email} onChange={handle} required />
            </div>
            <div style={{ marginBottom: 20 }}>
              <label className="label">Password</label>
              <input className="input" type="password" name="password" placeholder="••••••••" value={form.password} onChange={handle} required />
            </div>
            {error && <p className="error-msg" style={{ marginBottom: 12 }}>{error}</p>}
            <button className="btn btn-primary" type="submit" disabled={loading} style={{ width: "100%", justifyContent: "center" }}>
              {loading ? <span className="spinner" /> : "Sign In"}
            </button>
          </form>
          <p style={{ textAlign: "center", marginTop: 16, fontSize: 14, color: "#6b7280" }}>
            No account? <Link to="/register" style={{ color: "#4f46e5", fontWeight: 500 }}>Create one free</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
