import React, { useState } from "react";
import { Lock, Mail, ArrowRight, Sparkles, AlertCircle } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function Login({ onSwitchToSignup }) {
  const { login } = useAuth();
  const [email, setEmail] = useState("demo@example.com");
  const [password, setPassword] = useState("Password123!");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(email, password);
    } catch (err) {
      setError(err.message || "Failed to authenticate.");
    } finally {
      setLoading(false);
    }
  };

  const handleDemoFill = () => {
    setEmail("demo@example.com");
    setPassword("Password123!");
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
          maxWidth: "440px",
          padding: "36px",
          background: "linear-gradient(180deg, #131B2E 0%, #0B111F 100%)",
          border: "1px solid rgba(99, 102, 241, 0.25)",
          boxShadow: "0 25px 60px -15px rgba(0, 0, 0, 0.7), 0 0 40px rgba(99, 102, 241, 0.15)"
        }}
      >
        {/* Brand */}
        <div style={{ textAlign: "center", marginBottom: "28px" }}>
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
            Welcome to Text2SQL
          </h2>
          <p style={{ fontSize: "13px", color: "var(--text-muted)", marginTop: "4px" }}>
            Enterprise Natural Language SQL Intelligence
          </p>
        </div>

        {/* Demo fast-fill pill */}
        <div
          onClick={handleDemoFill}
          style={{
            padding: "8px 12px",
            background: "rgba(99, 102, 241, 0.1)",
            border: "1px dashed rgba(99, 102, 241, 0.4)",
            borderRadius: "var(--radius-md)",
            fontSize: "12px",
            color: "#A5B4FC",
            textAlign: "center",
            cursor: "pointer",
            marginBottom: "20px",
            transition: "all 0.15s ease"
          }}
          onMouseEnter={(e) => (e.currentTarget.style.background = "rgba(99, 102, 241, 0.2)")}
          onMouseLeave={(e) => (e.currentTarget.style.background = "rgba(99, 102, 241, 0.1)")}
        >
          💡 Click to use <strong>Demo Workspace</strong> credentials
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
            <label className="input-label">Work Email</label>
            <div style={{ position: "relative" }}>
              <input
                type="email"
                className="input-field"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@company.com"
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
            <label className="input-label">Password</label>
            <div style={{ position: "relative" }}>
              <input
                type="password"
                className="input-field"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
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
            {loading ? "Authenticating..." : "Sign In to Workspace"}
            {!loading && <ArrowRight size={16} />}
          </button>
        </form>

        {/* Switch tab */}
        <div style={{ marginTop: "24px", textAlign: "center", fontSize: "13px", color: "var(--text-muted)" }}>
          Don't have a workspace?{" "}
          <button
            onClick={onSwitchToSignup}
            style={{
              background: "none",
              border: "none",
              color: "var(--accent-cyan)",
              fontWeight: 600,
              cursor: "pointer",
              textDecoration: "underline"
            }}
          >
            Create New Workspace
          </button>
        </div>
      </div>
    </div>
  );
}
