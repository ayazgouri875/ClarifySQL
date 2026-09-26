import React, { useState, useEffect } from "react";
import { Terminal, Database, HelpCircle, Zap, Shield, CheckCircle2, ArrowUpRight, Clock, Activity, Sparkles } from "lucide-react";
import api from "../services/api";
import { useAuth } from "../context/AuthContext";

export default function Dashboard({ onNavigateToQuery }) {
  const { user, activeConnection, connections } = useAuth();
  const [stats, setStats] = useState({
    total_queries: 0,
    successful_queries: 0,
    failed_queries: 0,
    clarified_queries: 0,
    avg_execution_time_ms: 0,
    connections_count: 0
  });
  const [recentQueries, setRecentQueries] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [statsData, historyData] = await Promise.all([
          api.history.getStats(),
          api.history.list({ limit: 5 })
        ]);
        setStats(statsData);
        setRecentQueries(historyData?.results || historyData || []);
      } catch (err) {
        console.error("Error loading dashboard data:", err);
      } finally {
        setLoading(false);
      }
    }
    loadDashboard();
  }, []);

  const sampleQuestions = [
    { text: "Who are our best customers recently?", category: "Ambiguity Demo", tag: "Metric & Time" },
    { text: "Show sales breakdown by category", category: "Analytics", tag: "Aggregation" },
    { text: "Which products generated the most revenue?", category: "Product Intel", tag: "Ranking" },
    { text: "Show recent large orders above $1,000", category: "Filters", tag: "Threshold" },
  ];

  const successRate = stats.total_queries > 0 
    ? Math.round((stats.successful_queries / stats.total_queries) * 100) 
    : 100;

  return (
    <div style={{ padding: "28px", display: "flex", flexDirection: "column", gap: "28px" }}>
      {/* Welcome banner */}
      <div
        className="glass-card"
        style={{
          padding: "28px 32px",
          background: "linear-gradient(135deg, rgba(99, 102, 241, 0.12) 0%, rgba(6, 182, 212, 0.08) 100%)",
          border: "1px solid rgba(99, 102, 241, 0.25)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: "20px"
        }}
      >
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "6px" }}>
            <span className="badge badge-success">
              <Sparkles size={12} />
              Enterprise AI Active
            </span>
            <span style={{ fontSize: "13px", color: "var(--text-muted)" }}>
              Workspace: <strong>{user?.organization_name || "Default"}</strong>
            </span>
          </div>
          <h2 style={{ fontSize: "24px", fontWeight: 800, color: "#FFF" }}>
            Hello, {user?.name || "Analyst"} 👋
          </h2>
          <p style={{ fontSize: "14px", color: "var(--text-muted)", marginTop: "4px", maxWidth: "600px" }}>
            QueryMind transforms natural language into secure, dialect-aware SQL with multi-turn ambiguity resolution and safe read-only execution.
          </p>
        </div>

        <button
          className="btn btn-primary"
          onClick={() => onNavigateToQuery()}
          style={{ padding: "12px 24px", fontSize: "14px" }}
        >
          <Terminal size={18} />
          Open Query Studio
        </button>
      </div>

      {/* KPI Metric Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "16px" }}>
        {/* Card 1 */}
        <div className="glass-card" style={{ padding: "20px" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", color: "var(--text-subtle)", marginBottom: "8px" }}>
            <span style={{ fontSize: "12px", fontWeight: 600, textTransform: "uppercase" }}>Total Queries</span>
            <Terminal size={18} color="var(--primary)" />
          </div>
          <div style={{ fontSize: "28px", fontWeight: 800, color: "#FFF" }}>
            {stats.total_queries}
          </div>
          <div style={{ fontSize: "12px", color: "#10B981", marginTop: "4px", display: "flex", alignItems: "center", gap: "4px" }}>
            <CheckCircle2 size={12} /> {successRate}% success rate
          </div>
        </div>

        {/* Card 2 */}
        <div className="glass-card" style={{ padding: "20px" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", color: "var(--text-subtle)", marginBottom: "8px" }}>
            <span style={{ fontSize: "12px", fontWeight: 600, textTransform: "uppercase" }}>Clarified Ambiguities</span>
            <HelpCircle size={18} color="#F59E0B" />
          </div>
          <div style={{ fontSize: "28px", fontWeight: 800, color: "#FFF" }}>
            {stats.clarified_queries}
          </div>
          <div style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "4px" }}>
            Resolved without hallucination
          </div>
        </div>

        {/* Card 3 */}
        <div className="glass-card" style={{ padding: "20px" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", color: "var(--text-subtle)", marginBottom: "8px" }}>
            <span style={{ fontSize: "12px", fontWeight: 600, textTransform: "uppercase" }}>Avg Execution Time</span>
            <Clock size={18} color="var(--accent-cyan)" />
          </div>
          <div style={{ fontSize: "28px", fontWeight: 800, color: "#FFF" }}>
            {stats.avg_execution_time_ms} <span style={{ fontSize: "14px", fontWeight: 500, color: "var(--text-muted)" }}>ms</span>
          </div>
          <div style={{ fontSize: "12px", color: "var(--accent-cyan)", marginTop: "4px" }}>
            High-speed read-only execution
          </div>
        </div>

        {/* Card 4 */}
        <div className="glass-card" style={{ padding: "20px" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", color: "var(--text-subtle)", marginBottom: "8px" }}>
            <span style={{ fontSize: "12px", fontWeight: 600, textTransform: "uppercase" }}>Databases Connected</span>
            <Database size={18} color="#A855F7" />
          </div>
          <div style={{ fontSize: "28px", fontWeight: 800, color: "#FFF" }}>
            {connections.length || stats.connections_count}
          </div>
          <div style={{ fontSize: "12px", color: "var(--text-muted)", marginTop: "4px" }}>
            Active: {activeConnection ? activeConnection.name : "None"}
          </div>
        </div>
      </div>

      {/* Suggested Queries Grid */}
      <div>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "16px" }}>
          <h3 style={{ fontSize: "16px", fontWeight: 700, color: "#FFF" }}>Quick Start Inquiries</h3>
          <span style={{ fontSize: "12px", color: "var(--text-subtle)" }}>Click any question to open in Query Studio</span>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "14px" }}>
          {sampleQuestions.map((q, idx) => (
            <div
              key={idx}
              className="glass-card"
              onClick={() => onNavigateToQuery(q.text)}
              style={{
                padding: "18px",
                cursor: "pointer",
                transition: "all 0.2s cubic-bezier(0.16, 1, 0.3, 1)",
                display: "flex",
                flexDirection: "column",
                justifyContent: "space-between",
                gap: "12px"
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = "translateY(-2px)";
                e.currentTarget.style.borderColor = "var(--border-active)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = "translateY(0)";
                e.currentTarget.style.borderColor = "var(--border-subtle)";
              }}
            >
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <span className="badge badge-neutral" style={{ fontSize: "10px" }}>{q.category}</span>
                <span style={{ fontSize: "11px", color: "var(--accent-cyan)", fontWeight: 600 }}>{q.tag}</span>
              </div>
              <div style={{ fontSize: "14px", fontWeight: 600, color: "#F1F5F9", lineHeight: 1.4 }}>
                "{q.text}"
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "4px", fontSize: "12px", color: "#818CF8", fontWeight: 600 }}>
                Query now <ArrowUpRight size={13} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Guardrails and Recent Activity */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(320px, 1fr))", gap: "20px" }}>
        {/* Security Guardrails Card */}
        <div className="glass-card" style={{ padding: "24px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "10px", marginBottom: "18px" }}>
            <div style={{ width: "36px", height: "36px", borderRadius: "10px", background: "rgba(16, 185, 129, 0.15)", display: "flex", alignItems: "center", justifyContent: "center", color: "#10B981" }}>
              <Shield size={20} />
            </div>
            <div>
              <h3 style={{ fontSize: "15px", fontWeight: 700, color: "#FFF" }}>Enterprise Security Guardrails</h3>
              <p style={{ fontSize: "12px", color: "var(--text-subtle)" }}>Enforced by AST validation on every execution</p>
            </div>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "10px", fontSize: "13px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", color: "#E2E8F0" }}>
              <CheckCircle2 size={16} color="#10B981" />
              <span>Strict Read-Only Enforcement (BLOCKS DROP, UPDATE, DELETE, INSERT)</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", color: "#E2E8F0" }}>
              <CheckCircle2 size={16} color="#10B981" />
              <span>Zero Stacked Queries (Prevents SQL Injection attacks)</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", color: "#E2E8F0" }}>
              <CheckCircle2 size={16} color="#10B981" />
              <span>Automatic Limit Protection (Guards memory with 1,000 row max ceiling)</span>
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: "10px", color: "#E2E8F0" }}>
              <CheckCircle2 size={16} color="#10B981" />
              <span>Multi-Tenant Isolation (Encrypted credentials via Fernet cipher)</span>
            </div>
          </div>
        </div>

        {/* Recent Queries */}
        <div className="glass-card" style={{ padding: "24px" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "18px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
              <div style={{ width: "36px", height: "36px", borderRadius: "10px", background: "rgba(99, 102, 241, 0.15)", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--primary)" }}>
                <Activity size={20} />
              </div>
              <div>
                <h3 style={{ fontSize: "15px", fontWeight: 700, color: "#FFF" }}>Recent Executions</h3>
                <p style={{ fontSize: "12px", color: "var(--text-subtle)" }}>Live query log</p>
              </div>
            </div>
          </div>

          {recentQueries.length === 0 ? (
            <div style={{ color: "var(--text-subtle)", fontSize: "13px", padding: "20px 0", textAlign: "center" }}>
              No queries recorded yet.
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
              {recentQueries.map((q) => (
                <div
                  key={q.id}
                  style={{
                    padding: "10px 12px",
                    background: "rgba(255, 255, 255, 0.02)",
                    borderRadius: "var(--radius-sm)",
                    border: "1px solid var(--border-subtle)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    gap: "10px"
                  }}
                >
                  <div style={{ minWidth: 0 }}>
                    <div style={{ fontSize: "13px", fontWeight: 600, color: "#FFF", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {q.natural_query}
                    </div>
                    <div style={{ fontSize: "11px", color: "var(--text-subtle)", marginTop: "2px" }}>
                      {q.connection_name} • {q.execution_time_ms} ms
                    </div>
                  </div>
                  <span className={`badge ${q.status === "success" ? "badge-success" : "badge-danger"}`}>
                    {q.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
