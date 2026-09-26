import React, { useState } from "react";
import { User, Lock, Mail, Building, ArrowRight, Sparkles, AlertCircle } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Signup({ onSwitchToLogin }) {
  const { signup } = useAuth();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [orgName, setOrgName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await signup(name, email, password, orgName || `${name}'s Org`);
    } catch (err) {
      setError(err.message || "Failed to register workspace.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "20px"
      }}
    >
      <div
        className="glass-card"
        style={{
          width: "100%",
          maxWidth: "460px",
          padding: "36px",
          background: "linear-gradient(180deg, #131B2E 0%, #0B111F 100%)",
          border: "1px solid rgba(99, 102, 241, 0.25)",
          boxShadow: "0 25px 60px -15px rgba(0, 0, 0, 0.7), 0 0 40px rgba(99, 102, 241, 0.15)"
        }}
      >
        {/* Brand */}
        <div style={{ textAlign: "center", marginBottom: "24px" }}>
          <div
            style={{
              width: "48px",
              height: "48px",
              margin: "0 auto 14px",
              borderRadius: "14px",
              background: "linear-gradient(135deg, #6366F1 0%, #06B6D4 100%)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              color: "#FFF",
              boxShadow: "0 0 20px rgba(99, 102, 241, 0.4)"
            }}
          >
            <Sparkles size={24} />
          </div>
          <h2 style={{ fontSize: "22px", fontWeight: 800, color: "#FFF", letterSpacing: "-0.02em" }}>
            Create Your Workspace
          </h2>
          <p style={{ fontSize: "13px", color: "var(--text-muted)", marginTop: "4px" }}>
            Get started with AI-powered Natural Language to SQL
          </p>
        </div>

        {error && (
          <div
            style={{
              padding: "10px 14px",
              background: "rgba(239, 68, 68, 0.12)",
              border: "1px solid rgba(239, 68, 68, 0.3)",
              borderRadius: "var(--radius-md)",
              color: "#F87171",
              fontSize: "13px",
              marginBottom: "18px",
              display: "flex",
              alignItems: "center",
              gap: "8px"
            }}
          >
            <AlertCircle size={16} />
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label className="input-label">Full Name</label>
            <div style={{ position: "relative" }}>
              <input
                type="text"
                className="input-field"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Jane Doe"
                style={{ paddingLeft: "38px" }}
              />
              <User
                size={16}
                style={{
                  position: "absolute",
                  left: "12px",
                  top: "50%",
                  transform: "translateY(-50%)",
                  color: "var(--text-subtle)"
                }}
              />
            </div>
          </div>

          <div className="input-group">
            <label className="input-label">Work Email</label>
            <div style={{ position: "relative" }}>
              <input
                type="email"
                className="input-field"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="jane@company.com"
                style={{ paddingLeft: "38px" }}
              />
              <Mail
                size={16}
                style={{
                  position: "absolute",
                  left: "12px",
                  top: "50%",
                  transform: "translateY(-50%)",
                  color: "var(--text-subtle)"
                }}
              />
            </div>
          </div>

          <div className="input-group">
            <label className="input-label">Organization Name</label>
            <div style={{ position: "relative" }}>
              <input
                type="text"
                className="input-field"
                value={orgName}
                onChange={(e) => setOrgName(e.target.value)}
                placeholder="Acme Analytics Inc."
                style={{ paddingLeft: "38px" }}
              />
              <Building
                size={16}
                style={{
                  position: "absolute",
                  left: "12px",
                  top: "50%",
                  transform: "translateY(-50%)",
                  color: "var(--text-subtle)"
                }}
              />
            </div>
          </div>

          <div className="input-group">
            <label className="input-label">Password</label>
            <div style={{ position: "relative" }}>
              <input
                type="password"
                className="input-field"
                required
                minLength={6}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Minimum 6 characters"
                style={{ paddingLeft: "38px" }}
              />
              <Lock
                size={16}
                style={{
                  position: "absolute",
                  left: "12px",
                  top: "50%",
                  transform: "translateY(-50%)",
                  color: "var(--text-subtle)"
                }}
              />
            </div>
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
            style={{ width: "100%", marginTop: "8px", padding: "12px" }}
          >
            {loading ? "Creating Workspace..." : "Get Started Now"}
            {!loading && <ArrowRight size={16} />}
          </button>
        </form>

        {/* Switch tab */}
        <div style={{ marginTop: "24px", textAlign: "center", fontSize: "13px", color: "var(--text-muted)" }}>
          Already have an account?{" "}
          <button
            onClick={onSwitchToLogin}
            style={{
              background: "none",
              border: "none",
              color: "var(--accent-cyan)",
              fontWeight: 600,
              cursor: "pointer",
              textDecoration: "underline"
            }}
          >
            Sign In
          </button>
        </div>
      </div>
    </div>
  );
}
