import React from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../App";

const NAV_ITEMS = [
  { path: "/", label: "Dashboard", icon: "⊞" },
  { path: "/analyze", label: "Analyze", icon: "◎" },
  { path: "/jobs", label: "Jobs", icon: "◈" },
  { path: "/interview", label: "Interview Prep", icon: "◆" },
];

export default function Navbar() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleLogout = () => { logout(); navigate("/login"); };

  return (
    <nav style={{
      background: "white",
      borderBottom: "1px solid #e5e7eb",
      padding: "0 24px",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      height: 60,
      position: "sticky",
      top: 0,
      zIndex: 100,
      boxShadow: "0 1px 3px rgba(0,0,0,0.05)",
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 32 }}>
        <Link to="/" style={{ textDecoration: "none" }}>
          <span style={{ fontSize: 18, fontWeight: 700, color: "#4f46e5" }}>
            JobLens <span style={{ color: "#1a1a2e" }}>AI</span>
          </span>
        </Link>
        <div style={{ display: "flex", gap: 4 }}>
          {NAV_ITEMS.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              style={{
                textDecoration: "none",
                padding: "6px 14px",
                borderRadius: 8,
                fontSize: 14,
                fontWeight: 500,
                color: location.pathname === item.path ? "#4f46e5" : "#6b7280",
                background: location.pathname === item.path ? "#eef2ff" : "transparent",
                display: "flex",
                alignItems: "center",
                gap: 6,
              }}
            >
              <span style={{ fontSize: 12 }}>{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </div>
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <span style={{ fontSize: 13, color: "#6b7280" }}>
          Hey, <strong style={{ color: "#374151" }}>{user?.name?.split(" ")[0]}</strong>
        </span>
        <button onClick={handleLogout} className="btn btn-outline" style={{ padding: "6px 14px", fontSize: 13 }}>
          Logout
        </button>
      </div>
    </nav>
  );
}
